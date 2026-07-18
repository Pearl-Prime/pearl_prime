#!/usr/bin/env python3
"""Read-only inputs + fail-closed join for the GHL YAML sub-account sync.

Authority:
  docs/specs/GHL_YAML_SUBACCOUNT_SYNC_V1_SPEC.md   (PR #5687)
  docs/ghl/GHL_YAML_SYNC_FIELD_MAP.md              (PR #5690)

This module NEVER calls the GoHighLevel API and NEVER writes to GHL. It joins
three read-only Phoenix inputs (brand wizard YAML, marketing registry, location
manifest) with an optional read-only current-state snapshot fixture, and emits a
desired-state diff whose default decision is ``blocked``.

Fail-closed contract: a target row is syncable only when exactly one active
wizard YAML, exactly one marketing registry row, and exactly one manifest row
resolve to the same brand_id + locale + GHL location_id. Anything else blocks.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

SCHEMA_VERSION = 1
FIELD_MAP_VERSION = "GHL_YAML_SUBACCOUNT_SYNC_V1"

DEFAULT_REGISTRY_PATH = REPO_ROOT / "config" / "marketing" / "brand_marketing_registry.yaml"
DEFAULT_MANIFEST_PATH = REPO_ROOT / "docs" / "handoffs" / "ghl_location_manifest.example.tsv"
DEFAULT_WIZARD_DIR = REPO_ROOT / "brand-wizard-app" / "brands"
QUIZ_SEGMENT_MAP_PATH = REPO_ROOT / "config" / "freebies" / "quiz_segment_map.yaml"
FUNNEL_CAPTURE_PATH = REPO_ROOT / "config" / "freebies" / "ghl_funnel_capture.yaml"
EMAIL_SLOT_RULES_PATH = REPO_ROOT / "config" / "marketing" / "ghl_email_slot_rules.yaml"

REDACTED = "<redacted>"

# ---------------------------------------------------------------------------
# Safety classes (mirror of docs/ghl/GHL_YAML_SYNC_FIELD_MAP.md "Safety Classes")
# ---------------------------------------------------------------------------

PHOENIX_MANAGED = "phoenix_managed"
MANUAL_GHL_ADMIN = "manual_ghl_admin"
OPERATOR_APPROVAL_REQUIRED = "operator_approval_required"
BLOCKED_CLASS = "blocked"
PHOENIX_ONLY = "phoenix_only"

SAFETY_CLASSES = (
    PHOENIX_MANAGED,
    MANUAL_GHL_ADMIN,
    OPERATOR_APPROVAL_REQUIRED,
    BLOCKED_CLASS,
    PHOENIX_ONLY,
)


@dataclass(frozen=True)
class FieldSpec:
    """One allowlisted GHL custom-value target from the merged field map."""

    name: str
    source_kind: str  # wizard | registry | manifest | engine
    source_key: str
    safety_class: str
    note: str = ""

    @property
    def live_write_allowed(self) -> bool:
        """V1 live-write eligibility. Dry-run always shows the diff regardless."""
        return self.safety_class == PHOENIX_MANAGED

    @property
    def requires_operator_approval(self) -> bool:
        return self.safety_class == OPERATOR_APPROVAL_REQUIRED


# Allowlist-only. Order mirrors docs/ghl/GHL_YAML_SYNC_FIELD_MAP.md.
FIELD_MAP: tuple[FieldSpec, ...] = (
    FieldSpec("phoenix_brand_id", "registry", "brand_id", PHOENIX_MANAGED, "Must match manifest row."),
    FieldSpec(
        "phoenix_brand_display_name",
        "registry",
        "display_name",
        OPERATOR_APPROVAL_REQUIRED,
        "Prefer registry display name when GHL pilot row already exists.",
    ),
    FieldSpec("phoenix_locale", "registry", "locale", PHOENIX_MANAGED, "V1 pilot is en_US."),
    FieldSpec("phoenix_feed_url", "manifest", "feed_url", PHOENIX_MANAGED, "Public stable URL only; no presigned URLs."),
    FieldSpec("phoenix_funnel_base_url", "manifest", "funnel_base_url", PHOENIX_MANAGED, "Public Cloudflare Pages URL."),
    FieldSpec("phoenix_shop_cta_style", "manifest", "shop_cta_style", MANUAL_GHL_ADMIN, "Dry-run only until operator approves."),
    FieldSpec("phoenix_rollout_phase", "registry", "rollout_phase", MANUAL_GHL_ADMIN, "Audit only, not automation switching in V1."),
    FieldSpec("phoenix_last_sync_sha", "engine", "sync_sha", PHOENIX_MANAGED, "Preferred one-field live pilot target."),
    FieldSpec("phoenix_last_sync_at", "engine", "sync_at", PHOENIX_MANAGED, "Low-risk audit target."),
    FieldSpec("phoenix_brand_tagline", "wizard", "wizard_core.tagline", OPERATOR_APPROVAL_REQUIRED, "Brand identity copy."),
    FieldSpec("phoenix_positioning_line", "wizard", "wizard_core.positioning_line", OPERATOR_APPROVAL_REQUIRED, "Brand identity copy."),
)

FIELD_MAP_BY_NAME = {f.name: f for f in FIELD_MAP}

# Preferred one-field live pilot order (field map "Pilot Field Set").
PILOT_FIELD_ORDER: tuple[str, ...] = ("phoenix_last_sync_sha", "phoenix_last_sync_at")

# Never a GHL custom value in V1. Guarded by tests.
NEVER_SYNC_KEYS: tuple[str, ...] = (
    "webhook_env",  # phoenix_only: env var NAME may live in manifests, URL value never syncs
    "webhook_url",
    "api_key",
    "apikey",
    "oauth_token",
    "access_token",
    "refresh_token",
    "private_integration_token",
    "billing",
    "users",
    "permissions",
    "phone_number",
    "sender_settings",
    "contacts",
    "email",
    "first_name",
    "last_name",
)

# Scale manifest columns (field map "Scale Manifest Columns").
SCALE_MANIFEST_COLUMNS: tuple[str, ...] = (
    "location_id",
    "location_name",
    "brand_id",
    "locale",
    "display_name",
    "feed_url",
    "funnel_base_url",
    "webhook_env",
    "shop_cta_style",
    "rollout_phase",
    "ghl_enabled",
    "phoenix_managed_custom_value_ids",
    "last_readback_at",
    "last_sync_sha",
    "rollback_note",
)

# ---------------------------------------------------------------------------
# Secret / signed-URL guard
# ---------------------------------------------------------------------------

_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"leadconnectorhq\.com/hooks", re.IGNORECASE),
    re.compile(r"hooks?\.(zapier|slack|make|integromat)\.com", re.IGNORECASE),
    re.compile(r"/services/[A-Za-z0-9_\-]{8,}"),
    re.compile(r"X-Amz-Signature=", re.IGNORECASE),
    re.compile(r"[?&](sig|signature|token|api_key|apikey|access_token|key)=", re.IGNORECASE),
    re.compile(r"\b(sk|pit|pk|rk)[-_][A-Za-z0-9]{12,}"),
    re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\."),  # JWT-ish
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{12,}", re.IGNORECASE),
)


def looks_secret(value: Any) -> bool:
    """True when a value looks like a webhook URL, signed URL, token, or key.

    Fail-closed guard: any matching value is blocked and redacted; it is never
    written to a diff, a packet, or a log.
    """
    if value is None:
        return False
    text = str(value)
    return any(p.search(text) for p in _SECRET_PATTERNS)


def redact(value: Any) -> Any:
    """Return the value, or ``<redacted>`` when it looks secret."""
    if value is None:
        return None
    return REDACTED if looks_secret(value) else value


def redact_location_id(location_id: str | None) -> str | None:
    """Stable, non-reversible token for a GHL location id (spec: hash/redaction)."""
    if not location_id:
        return None
    digest = hashlib.sha256(str(location_id).encode("utf-8")).hexdigest()[:12]
    return f"loc_sha256:{digest}"


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RegistryRow:
    brand_id: str
    locale: str
    display_name: str | None
    rollout_phase: str | None
    webhook_env: str | None
    ghl_enabled: bool
    funnel_path_prefix: str | None
    shop_base: str | None
    default_persona: str | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(frozen=True)
class Registry:
    path: Path
    defaults: dict[str, Any]
    rows: tuple[RegistryRow, ...]

    def ghl_enabled_rows(self) -> tuple[RegistryRow, ...]:
        return tuple(r for r in self.rows if r.ghl_enabled)


def load_registry(path: Path | None = None) -> Registry:
    p = Path(path or DEFAULT_REGISTRY_PATH)
    if not p.is_file():
        raise FileNotFoundError(f"marketing registry not found: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    defaults = data.get("defaults") or {}
    if not isinstance(defaults, dict):
        defaults = {}
    brands = data.get("brands") or {}
    if not isinstance(brands, dict):
        brands = {}
    rows: list[RegistryRow] = []
    for brand_id, body in brands.items():
        body = body if isinstance(body, dict) else {}
        rows.append(
            RegistryRow(
                brand_id=str(brand_id),
                locale=str(body.get("locale") or defaults.get("locale") or "en_US"),
                display_name=_str_or_none(body.get("display_name")),
                rollout_phase=_str_or_none(body.get("rollout_phase")),
                webhook_env=_str_or_none(body.get("webhook_env")),
                ghl_enabled=bool(body.get("ghl_enabled")),
                funnel_path_prefix=_str_or_none(body.get("funnel_path_prefix")),
                shop_base=_str_or_none(body.get("shop_base") or defaults.get("shop_base")),
                default_persona=_str_or_none(body.get("default_persona") or defaults.get("default_persona")),
                raw=body,
            )
        )
    return Registry(path=p, defaults=defaults, rows=tuple(sorted(rows, key=lambda r: r.brand_id)))


def _str_or_none(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


# ---------------------------------------------------------------------------
# Location manifest
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ManifestRow:
    row_id: int
    columns: dict[str, str]

    def get(self, key: str) -> str | None:
        return _str_or_none(self.columns.get(key))

    @property
    def brand_id(self) -> str | None:
        return self.get("brand_id")

    @property
    def locale(self) -> str | None:
        return self.get("locale")

    @property
    def location_id(self) -> str | None:
        return self.get("location_id")


@dataclass(frozen=True)
class Manifest:
    path: Path
    header: tuple[str, ...]
    rows: tuple[ManifestRow, ...]

    @property
    def missing_scale_columns(self) -> tuple[str, ...]:
        return tuple(c for c in SCALE_MANIFEST_COLUMNS if c not in self.header)

    def rows_for(self, brand_id: str, locale: str) -> tuple[ManifestRow, ...]:
        return tuple(r for r in self.rows if r.brand_id == brand_id and r.locale == locale)


def load_manifest(path: Path | None = None) -> Manifest:
    p = Path(path or DEFAULT_MANIFEST_PATH)
    if not p.is_file():
        raise FileNotFoundError(f"GHL location manifest not found: {p}")
    with p.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh, delimiter="\t")
        raw_rows = [r for r in reader if any((c or "").strip() for c in r)]
    if not raw_rows:
        return Manifest(path=p, header=(), rows=())
    header = tuple(h.strip() for h in raw_rows[0])
    rows: list[ManifestRow] = []
    for i, row in enumerate(raw_rows[1:], start=1):
        cols = {header[j]: (row[j].strip() if j < len(row) else "") for j in range(len(header))}
        rows.append(ManifestRow(row_id=i, columns=cols))
    return Manifest(path=p, header=header, rows=tuple(rows))


# ---------------------------------------------------------------------------
# Current-state snapshot (read-only fixture or redacted GET output)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Snapshot:
    path: Path | None
    locations: dict[str, dict[str, Any]]

    def location(self, location_id: str) -> dict[str, Any] | None:
        return self.locations.get(location_id)


def load_snapshot(path: Path | None) -> Snapshot | None:
    """Load a read-only current-state snapshot. ``None`` means no snapshot.

    Shape::

        {"schema_version": 1, "source": "fixture", "locations": {
            "<location_id>": {"name": "...", "custom_values": {
                "<name>": {"id": "cv_...", "value": "..."}}}}}
    """
    if path is None:
        return None
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"GHL snapshot fixture not found: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    locations = data.get("locations") or {}
    if not isinstance(locations, dict):
        locations = {}
    return Snapshot(path=p, locations=locations)


# ---------------------------------------------------------------------------
# Wizard YAML eligibility
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WizardYaml:
    brand_id: str
    path: Path
    exists: bool
    active: bool
    inactive_reason: str
    doc: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def repo_rel_path(self) -> str | None:
        if not self.exists:
            return None
        try:
            return str(self.path.relative_to(_repo_root_of(self.path)))
        except Exception:
            return str(self.path)


def _repo_root_of(p: Path) -> Path:
    for parent in p.resolve().parents:
        if (parent / ".git").exists() or (parent / "brand-wizard-app").is_dir():
            return parent
    return p.resolve().parent


def blob_sha_of(path: Path) -> str | None:
    """git blob SHA-1 of a file (provenance for the diff record)."""
    if not path.is_file():
        return None
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324 - git object id, not security


def wizard_yaml_paths(wizard_dir: Path | None = None) -> dict[str, Path]:
    d = Path(wizard_dir or DEFAULT_WIZARD_DIR)
    if not d.is_dir():
        return {}
    return {p.stem: p for p in sorted(d.glob("*.yaml")) if p.is_file()}


def resolve_wizard(brand_id: str, *, repo_root: Path, wizard_dir: Path | None = None) -> WizardYaml:
    """Resolve one brand's wizard YAML through scripts.brand.active_brand_classifier.

    Eligibility is re-derived from the live checkout per spec "Source Eligibility";
    the 37-brand universe is never assumed to have YAML files.
    """
    from scripts.brand.active_brand_classifier import ActiveBrandClassifier

    wdir = Path(wizard_dir or (Path(repo_root) / "brand-wizard-app" / "brands"))
    paths = wizard_yaml_paths(wdir)
    path = paths.get(brand_id)
    if path is None:
        return WizardYaml(brand_id, wdir / f"{brand_id}.yaml", False, False, "no brand_wizard YAML found")

    classifier = ActiveBrandClassifier(repo_root=Path(repo_root), wizard_yaml_dir=wdir)
    active = classifier.is_active(brand_id)
    reason = "" if active else (classifier.reason_for(brand_id) or "inactive")
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(doc, dict):
            doc = {}
    except (OSError, yaml.YAMLError):
        doc, active, reason = {}, False, "brand_wizard YAML unreadable or invalid YAML"
    return WizardYaml(brand_id, path, True, active, reason, doc)


def dotted_get(doc: dict[str, Any], dotted: str) -> Any:
    cur: Any = doc
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
