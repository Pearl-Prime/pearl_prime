"""Shared chapter_script shape helpers for the bestseller QC gates.

The production ``chapter_script_writer_handoff`` schema is a TOP-LEVEL ``pages``
array (``pages[].panels[]`` — see schemas/manga/chapter_script_writer_handoff.schema.json
and writer_stub / writer output). Some early gate code assumed a ``chapters[]``
wrapper (``chapters[].pages[].panels[]``) that the real artifact never has, so
those gates silently no-opped on real chapters.

These helpers iterate BOTH shapes so the gates fire on the artifacts the
pipeline actually produces, while remaining backward-compatible with any
``chapters[]``-wrapped replay fixtures.
"""

from __future__ import annotations

from typing import Any, Iterator, Mapping


def iter_pages(chapter_script: Mapping[str, Any]) -> Iterator[dict[str, Any]]:
    """Yield page dicts from either the flat (``pages``) or wrapped (``chapters[].pages``) shape."""
    chapters = chapter_script.get("chapters")
    if isinstance(chapters, list) and chapters:
        for ch in chapters:
            if not isinstance(ch, dict):
                continue
            for page in ch.get("pages") or []:
                if isinstance(page, dict):
                    yield page
        return
    for page in chapter_script.get("pages") or []:
        if isinstance(page, dict):
            yield page


def iter_panels(chapter_script: Mapping[str, Any]) -> Iterator[dict[str, Any]]:
    """Yield panel dicts in document order from either chapter_script shape."""
    for page in iter_pages(chapter_script):
        for panel in page.get("panels") or []:
            if isinstance(panel, dict):
                yield panel


def last_page(chapter_script: Mapping[str, Any]) -> dict[str, Any] | None:
    pages = list(iter_pages(chapter_script))
    return pages[-1] if pages else None


def last_panel(chapter_script: Mapping[str, Any]) -> dict[str, Any] | None:
    panels = list(iter_panels(chapter_script))
    return panels[-1] if panels else None


def panel_text(panel: Mapping[str, Any]) -> str:
    """Concatenate every textual field of a panel (dialogue/narration/caption/action)."""
    parts: list[str] = []
    dialogue = panel.get("dialogue")
    if isinstance(dialogue, list):
        for d in dialogue:
            if isinstance(d, dict):
                parts.append(str(d.get("text") or ""))
            elif d is not None:
                parts.append(str(d))
    elif dialogue is not None:
        parts.append(str(dialogue))
    for key in ("narration", "caption", "action", "panel_description", "description"):
        v = panel.get(key)
        if v:
            parts.append(str(v))
    return " ".join(p for p in parts if p)


def reader_text(panel: Mapping[str, Any]) -> str:
    """Reader-facing text only: dialogue + narration + caption.

    Excludes art-direction fields (panel_description/description/action), which are
    NOT printed on the page. Use this for words-per-page pacing; use ``panel_text``
    for substance/labeling scans that should also see the art direction.
    """
    parts: list[str] = []
    dialogue = panel.get("dialogue")
    if isinstance(dialogue, list):
        for d in dialogue:
            if isinstance(d, dict):
                parts.append(str(d.get("text") or ""))
            elif d is not None:
                parts.append(str(d))
    elif dialogue is not None:
        parts.append(str(dialogue))
    for key in ("narration", "caption"):
        v = panel.get(key)
        if v:
            parts.append(str(v))
    return " ".join(p for p in parts if p)


def panel_has_text(panel: Mapping[str, Any]) -> bool:
    """True when the panel carries any dialogue/narration/caption (i.e. NOT silent)."""
    dialogue = panel.get("dialogue")
    if isinstance(dialogue, list):
        for d in dialogue:
            if isinstance(d, dict) and str(d.get("text") or "").strip():
                return True
            if not isinstance(d, dict) and d is not None and str(d).strip():
                return True
    elif dialogue is not None and str(dialogue).strip():
        return True
    for key in ("narration", "caption"):
        if str(panel.get(key) or "").strip():
            return True
    return False
