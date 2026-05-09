"""
Music-mode-only catalog branch (MUSIC-MODE-BRAND-INTEGRATION-V1-01 §4).

When a brand is indexed in ``config/music/music_brand_registry.yaml``, catalog slices
must be 100% music-mode: no teacher-mode BookSpecs and no composite pipeline rows.
Path X brands (``config/manga/canonical_brand_list.yaml``) keep standard planner behavior.
"""
from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, TypeVar

try:
    import yaml
except ImportError:
    yaml = None

_LOG = logging.getLogger(__name__)

T = TypeVar("T")


class CatalogBranch(str, Enum):
    """Planner branch for ``CatalogPlanner.generate_for_brand``."""

    MUSIC_ONLY = "music_only"
    STANDARD = "standard"


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def music_brand_registry_path(repo_root: Path) -> Path:
    return repo_root / "config" / "music" / "music_brand_registry.yaml"


def canonical_brand_list_path(repo_root: Path) -> Path:
    return repo_root / "config" / "manga" / "canonical_brand_list.yaml"


def _load_yaml_dict(path: Path) -> dict[str, Any]:
    if yaml is None or not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def load_music_brand_ids(repo_root: Path) -> set[str]:
    """Return ``brand_id`` values listed under ``music_brands``."""
    data = _load_yaml_dict(music_brand_registry_path(repo_root))
    out: set[str] = set()
    for row in data.get("music_brands") or []:
        if isinstance(row, dict) and row.get("brand_id"):
            out.add(str(row["brand_id"]))
    return out


def load_path_x_brand_ids(repo_root: Path) -> set[str]:
    """Return keys under ``brands`` in Path X canonical list."""
    data = _load_yaml_dict(canonical_brand_list_path(repo_root))
    brands = data.get("brands") or {}
    if not isinstance(brands, dict):
        return set()
    return {str(k) for k in brands.keys()}


def resolve_catalog_branch(brand_id: str, *, repo_root: Path | None = None) -> CatalogBranch:
    """
    Decide whether ``generate_for_brand`` applies the music-only filter.

    Precedence: music registry wins. If ``brand_id`` is present in both registries
    (anti-drift violation), log a warning and still return ``MUSIC_ONLY``.
    """
    root = repo_root or _repo_root_from_here()
    music = load_music_brand_ids(root)
    path_x = load_path_x_brand_ids(root)
    if brand_id not in music:
        return CatalogBranch.STANDARD
    if brand_id in path_x:
        _LOG.warning(
            "catalog music branch: brand_id=%r appears in both music_brand_registry.yaml and "
            "canonical_brand_list.yaml (sets should be disjoint per MUSIC-MODE-BRAND-INTEGRATION-V1-01). "
            "Applying music_mode precedence: 100%% music-mode filter.",
            brand_id,
        )
    return CatalogBranch.MUSIC_ONLY


def filter_to_music_mode_book_specs(specs: list[T]) -> list[T]:
    """
    Keep BookSpecs that are safe for a music-mode-only catalog slice (§4).

    Drops ``teacher_mode`` rows and rows explicitly tagged as composite or
    teacher_mode via optional ``catalog_pipeline_mode`` on the spec object.
    """
    out: list[T] = []
    for spec in specs:
        if bool(getattr(spec, "teacher_mode", False)):
            continue
        mode = getattr(spec, "catalog_pipeline_mode", None)
        if isinstance(mode, str) and mode.lower() in ("composite", "teacher_mode"):
            continue
        out.append(spec)
    return out


def filter_catalog_entry_dicts_music_mode(entries: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter planner/CSV-style dict rows to music-mode-only (optional ``teacher_mode`` / pipeline mode keys)."""
    out: list[dict[str, Any]] = []
    for row in entries:
        raw_tm = row.get("teacher_mode")
        if isinstance(raw_tm, bool) and raw_tm:
            continue
        if isinstance(raw_tm, str) and raw_tm.strip().lower() in ("true", "1", "yes"):
            continue
        mode = (row.get("catalog_pipeline_mode") or row.get("pipeline_mode") or "")
        if isinstance(mode, str) and mode.lower() in ("composite", "teacher_mode"):
            continue
        out.append(row)
    return out
