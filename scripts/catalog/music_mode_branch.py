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


def load_music_brand_rows(repo_root: Path) -> dict[str, dict[str, Any]]:
    """Return ``brand_id -> registry row`` for entries under ``music_brands``."""
    data = _load_yaml_dict(music_brand_registry_path(repo_root))
    out: dict[str, dict[str, Any]] = {}
    for row in data.get("music_brands") or []:
        if isinstance(row, dict) and row.get("brand_id"):
            out[str(row["brand_id"])] = row
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


_DEFAULT_MUSIC_MODE_WITH_CONSENT = "with-lyrics"
_DEFAULT_MUSIC_MODE_NO_CONSENT = "no-lyrics"


def _survey_song_consent(repo_root: Path, survey_yaml_pointer: Any) -> bool | None:
    """
    Read ``output_preferences_with_lyrics.companion_ai_song_consent`` from the survey YAML
    pointed to by a registry row's ``survey_yaml_pointer``.

    Returns ``None`` (caller defaults to with-lyrics, per spec §4) when the pointer is
    missing, the file doesn't exist, or the field isn't a bool.
    """
    pointer = str(survey_yaml_pointer or "").strip()
    if not pointer:
        return None
    survey = _load_yaml_dict(repo_root / pointer)
    prefs = survey.get("output_preferences_with_lyrics")
    if not isinstance(prefs, dict):
        return None
    consent = prefs.get("companion_ai_song_consent")
    return consent if isinstance(consent, bool) else None


def resolve_music_args_for_brand(
    brand_id: str, *, repo_root: Path | None = None
) -> tuple[str, str] | None:
    """
    Auto-resolve ``(music_mode, musician_id)`` for a registered, active music brand.

    Returns ``None`` when ``brand_id`` is not present in
    ``config/music/music_brand_registry.yaml``, or is present but not ``status: active``
    (inactive brands stay represented per registry Q4 but must never auto-trigger a
    music-mode render), or has no usable ``musician_handle``.

    V1 variant policy (spec §4): default ``"with-lyrics"`` unless the entry's pointed
    survey YAML explicitly sets
    ``output_preferences_with_lyrics.companion_ai_song_consent: false``.
    """
    root = repo_root or _repo_root_from_here()
    row = load_music_brand_rows(root).get(brand_id)
    if row is None or str(row.get("status", "")).strip().lower() != "active":
        return None
    musician_id = str(row.get("musician_handle") or "").strip()
    if not musician_id:
        return None
    consent = _survey_song_consent(root, row.get("survey_yaml_pointer"))
    music_mode = (
        _DEFAULT_MUSIC_MODE_NO_CONSENT if consent is False else _DEFAULT_MUSIC_MODE_WITH_CONSENT
    )
    return music_mode, musician_id


def apply_auto_detected_music_args(
    brand_id: str,
    *,
    explicit_music_mode: str | None,
    explicit_musician_id: str | None,
    repo_root: Path | None = None,
) -> tuple[str, str | None]:
    """
    Resolve the effective ``(music_mode, musician_id)`` pair for a pipeline dispatch.

    Explicit operator-passed values ALWAYS win and are never overridden. Each field is
    auto-filled independently, and only when the operator did not pass it (falsy check:
    ``music_mode`` missing/``"none"``, ``musician_id`` missing/blank). A ``brand_id`` that
    is not a registered active music brand (e.g. a Path X brand) is a pure no-op: the
    explicit values (or the CLI's ``"none"``/``None`` defaults) pass through unchanged.
    """
    resolved_music_mode = (explicit_music_mode or "none").strip() or "none"
    resolved_musician_id = (explicit_musician_id or "").strip() or None

    needs_music_mode = resolved_music_mode == "none"
    needs_musician_id = resolved_musician_id is None
    if not needs_music_mode and not needs_musician_id:
        return resolved_music_mode, resolved_musician_id

    auto = resolve_music_args_for_brand(brand_id, repo_root=repo_root)
    if auto is None:
        return resolved_music_mode, resolved_musician_id

    auto_music_mode, auto_musician_id = auto
    if needs_music_mode:
        resolved_music_mode = auto_music_mode
    if needs_musician_id:
        resolved_musician_id = auto_musician_id
    return resolved_music_mode, resolved_musician_id


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
