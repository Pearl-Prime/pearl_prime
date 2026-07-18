#!/usr/bin/env python3
"""
Active / inactive brand classification from brand_wizard YAML SSOT.

Cap: WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 (Q4 = brand_wizard_yaml as SSOT for
active/inactive). Music-mode extension is gated on MUSIC-MODE-BRAND-INTEGRATION-V1-01;
when ``config/music/music_brand_registry.yaml`` is absent, music IDs are deferred
(empty) and ``music_registry_deferred`` is True.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

# Canonical on-disk layout for exported / checked-in wizard bundles (Phase 1).
# The SPA under ``brand-wizard-app/`` generates YAML; committed SSOT lives here.
DEFAULT_WIZARD_YAML_DIR = REPO_ROOT / "brand-wizard-app" / "brands"

CANONICAL_BRAND_LIST = REPO_ROOT / "config" / "manga" / "canonical_brand_list.yaml"
BRAND_REGISTRY = REPO_ROOT / "config" / "brand_registry.yaml"
MUSIC_BRAND_REGISTRY = REPO_ROOT / "config" / "music" / "music_brand_registry.yaml"

# Minimum fields for a brand_wizard bundle to count as "active" for catalog gates.
REQUIRED_WIZARD_FIELDS: tuple[str, ...] = (
    "schema_version",
    "brand_id",
    "display_name",
    "wizard_core",
)

# When ``wizard_core`` is present it must be a mapping with these keys (non-empty str values).
REQUIRED_WIZARD_CORE_KEYS: tuple[str, ...] = ("tagline", "positioning_line")


@dataclass(frozen=True)
class BrandWizardStatus:
    brand_id: str
    active: bool
    reason: str


def _load_brands_section(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    brands = data.get("brands")
    if not isinstance(brands, dict):
        return {}
    return {str(k): v for k, v in brands.items()}


def _collect_registry_brand_ids(repo_root: Path) -> list[str]:
    ids: set[str] = set()
    ids.update(_load_brands_section(repo_root / "config" / "manga" / "canonical_brand_list.yaml"))
    ids.update(_load_brands_section(repo_root / "config" / "brand_registry.yaml"))
    return sorted(ids)


def _music_brand_ids(repo_root: Path) -> tuple[list[str], bool]:
    path = repo_root / "config" / "music" / "music_brand_registry.yaml"
    if not path.is_file():
        return [], True
    return sorted(_load_brands_section(path)), False


def _wizard_yaml_paths(wizard_dir: Path) -> dict[str, Path]:
    if not wizard_dir.is_dir():
        return {}
    out: dict[str, Path] = {}
    for p in sorted(wizard_dir.glob("*.yaml")):
        if p.is_file():
            out[p.stem] = p
    return out


def _missing_required_fields(doc: dict[str, object]) -> list[str]:
    missing: list[str] = []
    for key in REQUIRED_WIZARD_FIELDS:
        if key not in doc or doc[key] in (None, ""):
            missing.append(key)
            continue
        if key == "wizard_core":
            core = doc.get("wizard_core")
            if not isinstance(core, dict):
                missing.append("wizard_core")
                continue
            for sub in REQUIRED_WIZARD_CORE_KEYS:
                val = core.get(sub)
                if val is None or (isinstance(val, str) and not val.strip()):
                    missing.append(f"wizard_core.{sub}")
    return missing


def _evaluate_yaml(path: Path, expected_brand_id: str) -> tuple[bool, str]:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return False, "brand_wizard YAML unreadable or invalid YAML"
    if not isinstance(raw, dict):
        return False, "brand_wizard YAML root must be a mapping"
    bid = raw.get("brand_id")
    if bid is not None and str(bid) != str(expected_brand_id):
        return False, f"brand_id mismatch (file {expected_brand_id}.yaml vs brand_id={bid!r})"
    missing = _missing_required_fields(raw)
    if missing:
        return False, f"missing required field: {missing[0]}"
    return True, ""


class ActiveBrandClassifier:
    """Load registries + brand_wizard YAML directory; produce activation snapshot."""

    __slots__ = ("repo_root", "wizard_yaml_dir", "_music_ids", "_music_deferred")

    def __init__(
        self,
        repo_root: Path | None = None,
        wizard_yaml_dir: Path | None = None,
    ) -> None:
        self.repo_root = (repo_root or REPO_ROOT).resolve()
        self.wizard_yaml_dir = (wizard_yaml_dir or (self.repo_root / "brand-wizard-app" / "brands")).resolve()
        self._music_ids, self._music_deferred = _music_brand_ids(self.repo_root)

    @property
    def music_registry_deferred(self) -> bool:
        """True when ``config/music/music_brand_registry.yaml`` is absent (cap not landed)."""
        return self._music_deferred

    def music_brand_ids(self) -> list[str]:
        """Brand IDs owned by the music registry (empty when deferred)."""
        return list(self._music_ids)

    def brand_universe(self) -> list[str]:
        """Union of manga canonical, book registry, and music registry brand IDs."""
        base = _collect_registry_brand_ids(self.repo_root)
        return sorted(set(base) | set(self._music_ids))

    def snapshot(self) -> dict[str, BrandWizardStatus]:
        """brand_id -> status (active + empty reason, or inactive + reason)."""
        paths = _wizard_yaml_paths(self.wizard_yaml_dir)
        out: dict[str, BrandWizardStatus] = {}
        for bid in self.brand_universe():
            path = paths.get(bid)
            if path is None:
                out[bid] = BrandWizardStatus(bid, False, "no brand_wizard YAML found")
                continue
            ok, reason = _evaluate_yaml(path, bid)
            if ok:
                out[bid] = BrandWizardStatus(bid, True, "")
            else:
                out[bid] = BrandWizardStatus(bid, False, reason or "inactive")
        return out

    def is_active(self, brand_id: str) -> bool:
        st = self.snapshot().get(brand_id)
        return bool(st and st.active)

    def list_active(self) -> list[str]:
        snap = self.snapshot()
        return sorted(bid for bid, st in snap.items() if st.active)

    def list_inactive(self) -> list[str]:
        snap = self.snapshot()
        return sorted(bid for bid, st in snap.items() if not st.active)

    def reason_for(self, brand_id: str) -> str:
        st = self.snapshot().get(brand_id)
        if st is None:
            return "brand_id not in classifier universe"
        return st.reason


_default: ActiveBrandClassifier | None = None


def default_classifier() -> ActiveBrandClassifier:
    global _default
    if _default is None:
        _default = ActiveBrandClassifier()
    return _default


def reset_default_classifier() -> None:
    """Test hook: clear memoized default instance."""
    global _default
    _default = None


def activation_snapshot(classifier: ActiveBrandClassifier | None = None) -> dict[str, BrandWizardStatus]:
    c = classifier or default_classifier()
    return c.snapshot()


def is_active(brand_id: str, *, classifier: ActiveBrandClassifier | None = None) -> bool:
    return (classifier or default_classifier()).is_active(brand_id)


def list_active(*, classifier: ActiveBrandClassifier | None = None) -> list[str]:
    return (classifier or default_classifier()).list_active()


def list_inactive(*, classifier: ActiveBrandClassifier | None = None) -> list[str]:
    return (classifier or default_classifier()).list_inactive()


def reason_for(brand_id: str, *, classifier: ActiveBrandClassifier | None = None) -> str:
    return (classifier or default_classifier()).reason_for(brand_id)


def manga_canonical_brand_ids(repo_root: Path | None = None) -> list[str]:
    root = (repo_root or REPO_ROOT).resolve()
    return sorted(_load_brands_section(root / "config" / "manga" / "canonical_brand_list.yaml"))


def summarize_manga_slice(classifier: ActiveBrandClassifier | None = None) -> tuple[int, int, int]:
    """Returns (active_count, inactive_count, total) for the 37-brand manga canonical slice only."""
    c = classifier or default_classifier()
    snap = c.snapshot()
    manga_ids = manga_canonical_brand_ids(c.repo_root)
    active = sum(1 for b in manga_ids if snap.get(b) and snap[b].active)
    return active, len(manga_ids) - active, len(manga_ids)
