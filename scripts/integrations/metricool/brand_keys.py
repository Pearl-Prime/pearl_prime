"""Canonical brand-key derivation for Metricool brand map (SSOT merge source).

Union of:
- ``config/brand_registry.yaml`` brand keys
- ``config/catalog_planning/brand_archetype_registry.yaml`` brand_id values
- ``config/brand_management/global_brand_registry_unified.yaml`` archetype ids
  (including inactive/thin lists)
- CLI alias ``waystream_sanctuary`` → registry ``way_stream_sanctuary``
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]

BRAND_REGISTRY_PATH = REPO_ROOT / "config" / "brand_registry.yaml"
ARCHETYPE_REGISTRY_PATH = (
    REPO_ROOT / "config" / "catalog_planning" / "brand_archetype_registry.yaml"
)
UNIFIED_REGISTRY_PATH = (
    REPO_ROOT / "config" / "brand_management" / "global_brand_registry_unified.yaml"
)

# CLI / Metricool map alias → registry archetype id
KNOWN_ALIASES: dict[str, str] = {
    "waystream_sanctuary": "way_stream_sanctuary",
}

REQUIRED_CLI_KEYS = frozenset({"waystream_sanctuary"})


def _load_yaml(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Missing registry: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def collect_canonical_brand_keys(
    *,
    brand_registry_path: Path = BRAND_REGISTRY_PATH,
    archetype_registry_path: Path = ARCHETYPE_REGISTRY_PATH,
    unified_registry_path: Path = UNIFIED_REGISTRY_PATH,
) -> set[str]:
    """Return the set of brand keys the Metricool map must cover."""
    keys: set[str] = set()

    brand_reg = _load_yaml(brand_registry_path)
    brands = (brand_reg or {}).get("brands") or {}
    if isinstance(brands, dict):
        keys.update(str(k) for k in brands.keys())

    arch = _load_yaml(archetype_registry_path)
    for entry in (arch or {}).get("brand_archetypes") or []:
        if isinstance(entry, dict) and entry.get("brand_id"):
            keys.add(str(entry["brand_id"]))

    uni = _load_yaml(unified_registry_path)
    if isinstance(uni, dict):
        for name in uni.get("inactive_archetypes") or []:
            keys.add(str(name))
        for name in uni.get("thin_archetypes_topics_from_manga_only") or []:
            keys.add(str(name))
        for row in (uni.get("brands") or {}).values():
            if isinstance(row, dict) and row.get("brand_archetype_id"):
                keys.add(str(row["brand_archetype_id"]))

    keys.update(KNOWN_ALIASES.keys())
    keys.update(KNOWN_ALIASES.values())
    return keys


def alias_target(brand_key: str) -> str | None:
    """Return registry archetype for a known CLI alias, else None."""
    return KNOWN_ALIASES.get(brand_key)
