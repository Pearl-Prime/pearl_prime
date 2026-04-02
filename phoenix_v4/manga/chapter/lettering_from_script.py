"""Derive ``lettering_spec`` from chapter_script writer handoff."""

from __future__ import annotations

from typing import Any, Mapping

from phoenix_v4.manga.chapter.visual_from_script import iter_panels_from_chapter_script


def _panel_has_dialogue_text(panel: Mapping[str, Any]) -> bool:
    dialogue = panel.get("dialogue")
    if not isinstance(dialogue, list):
        return False
    for x in dialogue:
        if isinstance(x, str) and x.strip():
            return True
        if x is not None and not isinstance(x, str) and str(x).strip():
            return True
    return False


def build_lettering_spec_from_chapter_script(
    chapter_script: Mapping[str, Any],
    *,
    schema_version: str = "1.0.0",
) -> dict[str, Any]:
    """``silence_confirmed`` is True when the panel has no dialogue lines with text."""
    lettering_panels: list[dict[str, Any]] = []
    for panel in iter_panels_from_chapter_script(chapter_script):
        pid = panel.get("panel_id")
        if not pid or not str(pid).strip():
            raise ValueError("Every panel must have a non-empty panel_id")
        has_dlg = _panel_has_dialogue_text(panel)
        entry: dict[str, Any] = {"panel_id": str(pid)}
        entry["silence_confirmed"] = not has_dlg
        lettering_panels.append(entry)
    return {
        "schema_version": schema_version,
        "artifact_type": "lettering_spec",
        "lettering_panels": lettering_panels,
    }
