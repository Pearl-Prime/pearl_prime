"""Load authority YAMLs and page assets for manga distribution."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise RuntimeError("PyYAML required: pip install pyyaml") from exc

from phoenix_v4.manga.models.validation import repo_root

_PAGE_RE = re.compile(r"^page_(\d{3,4})\.png$", re.IGNORECASE)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_format_grammars(root: Path | None = None) -> dict[str, Any]:
    path = (root or repo_root()) / "config" / "manga" / "format_adaptation_grammars.yaml"
    data = _load_yaml(path)
    return data.get("formats") or {}


def load_brand_illustration_styles(root: Path | None = None) -> dict[str, Any]:
    path = (root or repo_root()) / "config" / "manga" / "brand_illustration_styles.yaml"
    data = _load_yaml(path)
    return data.get("brands") or {}


def load_style_archetypes(root: Path | None = None) -> dict[str, Any]:
    path = (root or repo_root()) / "config" / "manga" / "style_archetypes.yaml"
    data = _load_yaml(path)
    return data.get("archetypes") or data.get("style_archetypes") or {}


def default_episode_panel_count(root: Path | None = None) -> int:
    """Optimal panel count from Korea webtoon platform defaults."""
    path = (root or repo_root()) / "config" / "manga" / "korea_webtoon_config.yaml"
    data = _load_yaml(path)
    platforms = (
        ((data.get("webtoon_track") or {}).get("platforms")) or []
    )
    for plat in platforms:
        lengths = plat.get("episode_length_panels") or []
        if len(lengths) >= 2:
            return int(lengths[1])
    return 50


def grammar_for_format(formats: dict[str, Any], format_id: str) -> dict[str, Any]:
    block = formats.get(format_id)
    if not isinstance(block, dict):
        raise KeyError(f"Unknown format grammar: {format_id!r}")
    return block


def list_page_pngs(page_dir: Path) -> list[Path]:
    if not page_dir.is_dir():
        raise FileNotFoundError(f"page-dir not found: {page_dir}")
    pages: list[tuple[int, Path]] = []
    for p in sorted(page_dir.iterdir()):
        if not p.is_file():
            continue
        m = _PAGE_RE.match(p.name)
        if m:
            pages.append((int(m.group(1)), p))
    if not pages:
        raise FileNotFoundError(
            f"No page_###.png files in {page_dir} (expected e.g. page_001.png)"
        )
    return [p for _, p in sorted(pages)]


def publisher_label(brand_id: str) -> str:
    return brand_id.replace("_", " ").title()


def age_rating_for_market_demo(market_demo: str) -> str:
    demo = (market_demo or "").lower()
    if demo in ("shonen", "shojo", "kodomo"):
        return "Teen"
    if demo in ("seinen", "josei"):
        return "Teen+"
    return "Everyone"
