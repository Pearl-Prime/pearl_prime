from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_CONTENT_BANKS_DIR = REPO_ROOT / "config" / "content_banks"

REQUIRED_VARIANT_KEYS = frozenset(
    {
        "variant_id",
        "slot_type",
        "body",
        "topic_allowlist",
        "topic_blocklist",
        "persona_allowlist",
        "frame_allowlist",
        "frame_blocklist",
        "runtime_allowlist",
        "band",
        "intensity",
        "mechanism_depth",
        "ontgp_move",
        "ei_v2_targets",
        "collision_family",
        "signature_phrases",
        "forbidden_terms",
    }
)


class ContentBankSchemaError(ValueError):
    pass


def _norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _validate_variant(rec: dict[str, Any], *, source: str) -> None:
    missing = REQUIRED_VARIANT_KEYS - set(rec.keys())
    if missing:
        raise ContentBankSchemaError(f"{source}: variant {rec.get('variant_id')!r} missing keys {sorted(missing)}")
    if not str(rec.get("variant_id") or "").strip():
        raise ContentBankSchemaError(f"{source}: empty variant_id")
    if not str(rec.get("body") or "").strip():
        raise ContentBankSchemaError(f"{source}: empty body for {rec.get('variant_id')!r}")
    for k in (
        "topic_allowlist",
        "topic_blocklist",
        "persona_allowlist",
        "frame_allowlist",
        "frame_blocklist",
        "runtime_allowlist",
        "signature_phrases",
        "forbidden_terms",
    ):
        v = rec.get(k)
        if v is None or not isinstance(v, list):
            raise ContentBankSchemaError(f"{source}: {rec.get('variant_id')!r} {k} must be a list")
    if not isinstance(rec.get("ei_v2_targets"), dict):
        raise ContentBankSchemaError(f"{source}: {rec.get('variant_id')!r} ei_v2_targets must be a dict")


@dataclass
class ContentBankRegistry:
    """All variant banks under config/content_banks plus doctrine quarantine payloads."""

    banks: Dict[str, List[dict[str, Any]]] = field(default_factory=dict)
    quarantine_entries: List[dict[str, Any]] = field(default_factory=list)
    secular_replacements: List[dict[str, Any]] = field(default_factory=list)
    source_checksum: str = ""

    def variants_for_stems(self, stems: List[str]) -> List[dict[str, Any]]:
        out: List[dict[str, Any]] = []
        for stem in stems:
            out.extend(self.banks.get(stem, []))
        return out

    def locale_np_keys(self) -> set[str]:
        cached = getattr(self, "_locale_np_keys_cache", None)
        if cached is not None:
            return cached
        keys = {
            str(r.get("locale_var_key") or "")
            for r in self.banks.get("global_locale_np_bank", [])
        }
        keys.discard("")
        self._locale_np_keys_cache = keys
        return keys


_REGISTRY_CACHE: Optional[ContentBankRegistry] = None


def _dir_checksum(paths: List[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths, key=lambda x: str(x)):
        if p.is_file():
            h.update(p.name.encode())
            h.update(str(p.stat().st_mtime_ns).encode())
    return h.hexdigest()[:16]


def _load_registry_from_dir(root: Path) -> ContentBankRegistry:
    if yaml is None:
        raise ContentBankSchemaError("PyYAML is required to load content banks")
    if not root.is_dir():
        raise ContentBankSchemaError(f"Content banks directory missing: {root}")

    banks: Dict[str, List[dict[str, Any]]] = {}
    quarantine_entries: List[dict[str, Any]] = []
    secular_replacements: List[dict[str, Any]] = []
    yaml_files = sorted(root.glob("*.yaml"))

    for path in yaml_files:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        stem = path.stem
        if "quarantine_entries" in data:
            qe = data.get("quarantine_entries") or []
            sr = data.get("secular_replacements") or []
            if not isinstance(qe, list) or not isinstance(sr, list):
                raise ContentBankSchemaError(f"{path}: quarantine_entries/secular_replacements must be lists")
            quarantine_entries.extend(qe)
            secular_replacements.extend(sr)
            continue
        # Skip non-bank config files that live in the same directory
        # (loc_var_render.yaml uses fallbacks/rotations; selected_mechanism_resolver.yaml
        # uses a top-level `resolver:` mapping — neither are variant banks).
        if (
            "fallbacks" in data
            or "rotations" in data
            or "mechanisms" in data
            or "resolver" in data
        ):
            continue
        variants = data.get("variants")
        if not isinstance(variants, list):
            merged: List[dict[str, Any]] = []
            for _k, v in data.items():
                if not isinstance(v, list) or not v:
                    continue
                if not isinstance(v[0], dict):
                    continue
                if "variant_id" not in v[0]:
                    continue
                merged.extend(v)
            variants = merged
        if not isinstance(variants, list) or not variants:
            raise ContentBankSchemaError(f"{path}: expected variants list or bank sections of variant records")
        cleaned: List[dict[str, Any]] = []
        for i, rec in enumerate(variants):
            if not isinstance(rec, dict):
                raise ContentBankSchemaError(f"{path}: variants[{i}] must be a mapping")
            _validate_variant(rec, source=str(path))
            cleaned.append(rec)
        banks[stem] = cleaned

    return ContentBankRegistry(
        banks=banks,
        quarantine_entries=quarantine_entries,
        secular_replacements=secular_replacements,
        source_checksum=_dir_checksum(yaml_files),
    )


def load_content_bank_registry(
    *,
    banks_dir: Optional[Path] = None,
    force_reload: bool = False,
) -> ContentBankRegistry:
    """
    Load YAML banks from ``config/content_banks`` by default.
    When ``banks_dir`` is set, load from that directory only and do not use the process-wide cache
    (used by tests and enrichment fallbacks that need an isolated registry).
    """
    if banks_dir is not None:
        return _load_registry_from_dir(Path(banks_dir))

    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is not None and not force_reload:
        return _REGISTRY_CACHE
    reg = _load_registry_from_dir(_CONTENT_BANKS_DIR)
    _REGISTRY_CACHE = reg
    return reg


def get_content_bank_registry(*, force_reload: bool = False) -> ContentBankRegistry:
    return load_content_bank_registry(force_reload=force_reload)


def registry_fingerprint() -> str:
    return load_content_bank_registry().source_checksum
