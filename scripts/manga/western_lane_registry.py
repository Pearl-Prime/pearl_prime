"""Load western illustrated self-help pilot registry configs (Phase A).

Runtime consumer for:
  - config/manga/us_illustrated_pilot_cells.yaml
  - config/manga/western_cartoon_styles.yaml

Phase B wires Pearl Star illustration dispatch against western_cartoon_styles.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
PILOT_REGISTRY_PATH = REPO / "config" / "manga" / "us_illustrated_pilot_cells.yaml"
STYLES_PATH = REPO / "config" / "manga" / "western_cartoon_styles.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_pilot_registry() -> dict[str, Any]:
    return _load_yaml(PILOT_REGISTRY_PATH)


def load_western_cartoon_styles() -> dict[str, Any]:
    return _load_yaml(STYLES_PATH)


def pilot_cells() -> list[dict[str, Any]]:
    return list(load_pilot_registry().get("pilot_cells") or [])


def brand_style(brand_id: str) -> dict[str, Any] | None:
    brands = (load_western_cartoon_styles().get("brands") or {})
    entry = brands.get(brand_id)
    return dict(entry) if isinstance(entry, dict) else None
