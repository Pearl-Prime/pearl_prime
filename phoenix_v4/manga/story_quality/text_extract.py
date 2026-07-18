"""Deterministic text extraction for story excellence realization.

Extends ``phoenix_v4.manga.qc._script_shape`` page/panel iteration and mirrors
the multi-schema panel text rules from ``check_manga_story_authored``.
"""

from __future__ import annotations

from typing import Any, Iterator, Mapping

from phoenix_v4.manga.qc._script_shape import iter_pages, iter_panels


def _locale_values(v: Any) -> str:
    if isinstance(v, dict):
        return " ".join(str(x) for x in v.values() if x)
    return str(v or "")


def panel_text_parts(panel: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Return (relative_path_suffix, text) pairs for a panel."""
    parts: list[tuple[str, str]] = []
    for key in (
        "scene",
        "action",
        "narration",
        "caption",
        "sfx",
        "visual_description",
        "panel_description",
        "description",
        "prompt",
    ):
        v = panel.get(key)
        if v:
            parts.append((key, str(v)))
    for key in ("narrator_caption_by_locale", "sfx_by_locale", "text_by_locale"):
        flat = _locale_values(panel.get(key))
        if flat.strip():
            parts.append((key, flat))
    dialogue = panel.get("dialogue")
    if isinstance(dialogue, list):
        for i, d in enumerate(dialogue):
            if isinstance(d, dict):
                t = str(d.get("text") or "")
                if not t.strip():
                    t = _locale_values(d.get("text_by_locale"))
                if t.strip():
                    parts.append((f"dialogue[{i}].text", t))
            elif d is not None and str(d).strip():
                parts.append((f"dialogue[{i}]", str(d)))
    elif dialogue is not None and str(dialogue).strip():
        parts.append(("dialogue", str(dialogue)))
    for i, line in enumerate(panel.get("dialogue_lines") or []):
        if not isinstance(line, dict):
            continue
        t = str(line.get("text") or "")
        if not t.strip():
            t = _locale_values(line.get("text_by_locale"))
        if t.strip():
            parts.append((f"dialogue_lines[{i}].text", t))
    return [(p, t) for p, t in parts if t and str(t).strip()]


def panel_reader_and_action_text(panel: Mapping[str, Any]) -> str:
    return " ".join(t for _, t in panel_text_parts(panel))


def iter_page_panel_texts(
    chapter_script: Mapping[str, Any],
) -> Iterator[tuple[int, int, str, str]]:
    """Yield (page_idx, panel_idx, json_path, text) in document order."""
    for page_idx, page in enumerate(iter_pages(chapter_script)):
        panels = page.get("panels") or []
        for panel_idx, panel in enumerate(panels):
            if not isinstance(panel, dict):
                continue
            for suffix, text in panel_text_parts(panel):
                path = f"pages[{page_idx}].panels[{panel_idx}].{suffix}"
                yield page_idx, panel_idx, path, text


def opening_pages_text(
    chapter_script: Mapping[str, Any],
    *,
    max_pages: int = 2,
) -> tuple[str, list[dict[str, Any]]]:
    """Concatenate text from the first ``max_pages`` pages with evidence rows."""
    blob_parts: list[str] = []
    evidence: list[dict[str, Any]] = []
    for page_idx, panel_idx, path, text in iter_page_panel_texts(chapter_script):
        if page_idx >= max_pages:
            break
        blob_parts.append(text)
        evidence.append(
            {
                "path": path,
                "text": text[:240],
                "page_idx": page_idx,
                "panel_idx": panel_idx,
            }
        )
    return " ".join(blob_parts), evidence


def full_script_text(chapter_script: Mapping[str, Any]) -> str:
    return " ".join(t for *_, t in iter_page_panel_texts(chapter_script))


def metadata_only_blob(writer_handoff: Mapping[str, Any]) -> str:
    """Title/caption/prompt metadata that must NOT count as realization."""
    parts: list[str] = []
    for key in (
        "title",
        "chapter_title",
        "series_id",
        "chapter_id",
        "logline",
        "synopsis",
        "prompt",
        "chapter_end_hook",
    ):
        if writer_handoff.get(key):
            parts.append(str(writer_handoff[key]))
    mrc = writer_handoff.get("modern_reader_context")
    if isinstance(mrc, dict):
        parts.append(str(mrc.get("craft_directive") or ""))
        cat = mrc.get("catalyst") or {}
        if isinstance(cat, dict):
            parts.append(str(cat.get("logline") or ""))
            parts.append(str(cat.get("genre_transmutation") or ""))
    return " ".join(parts)


__all__ = [
    "full_script_text",
    "iter_page_panel_texts",
    "iter_pages",
    "iter_panels",
    "metadata_only_blob",
    "opening_pages_text",
    "panel_reader_and_action_text",
    "panel_text_parts",
]
