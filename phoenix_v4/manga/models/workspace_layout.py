"""Resolve chapter workspace root (flat vs ``chapters/<chapter_id>/``)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from phoenix_v4.manga.models import paths as manga_paths
from phoenix_v4.manga.models.validation import repo_root

DEFAULT_CHAPTERS_SUBDIR = "chapters"


def load_workspace_layout_config() -> dict[str, Any]:
    p = repo_root() / "config" / "manga" / "workspace_layout.yaml"
    if not p.is_file():
        return {"chapters_subdir": DEFAULT_CHAPTERS_SUBDIR}
    try:
        import yaml
    except ImportError:
        return {"chapters_subdir": DEFAULT_CHAPTERS_SUBDIR}
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return raw if isinstance(raw, dict) else {"chapters_subdir": DEFAULT_CHAPTERS_SUBDIR}


def chapters_subdir_name() -> str:
    cfg = load_workspace_layout_config()
    return str(cfg.get("chapters_subdir") or DEFAULT_CHAPTERS_SUBDIR)


def chapter_workspace_path(series_workspace: Path, chapter_id: str) -> Path:
    """``series_workspace / chapters / chapter_id`` (does not require dir to exist)."""
    return Path(series_workspace).resolve() / chapters_subdir_name() / chapter_id


def resolve_chapter_workspace(
    workspace: Path,
    *,
    chapter_id: str | None = None,
) -> Path:
    """If ``chapter_request.json`` exists at ``workspace``, return ``workspace``.

    Else if ``chapter_id`` is set, return ``workspace/chapters/<chapter_id>``.
    Raises ``FileNotFoundError`` if neither yields a chapter_request.
    """
    ws = Path(workspace).resolve()
    flat_cr = ws / manga_paths.CHAPTER_REQUEST
    if flat_cr.is_file():
        return ws
    if chapter_id:
        nested = chapter_workspace_path(ws, chapter_id)
        nested_cr = nested / manga_paths.CHAPTER_REQUEST
        if nested_cr.is_file():
            return nested
        # allow creating new chapter dir
        return nested
    raise FileNotFoundError(
        f"No {manga_paths.CHAPTER_REQUEST} at {flat_cr} "
        f"and no --chapter-id for nested layout under {ws / chapters_subdir_name()}"
    )
