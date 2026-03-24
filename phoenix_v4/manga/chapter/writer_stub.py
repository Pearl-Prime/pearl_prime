"""Deterministic chapter script stub — maps story handoff beats to minimal script panels (no LLM)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


def _find_chapter(
    handoff: Mapping[str, Any], chapter_number: int
) -> Mapping[str, Any] | None:
    for ch in handoff.get("chapters") or []:
        if int(ch.get("chapter_number", -1)) == chapter_number:
            return ch
    return None


def build_chapter_script_pair_from_handoff(
    handoff: Mapping[str, Any],
    *,
    chapter_number: int,
    series_id: str,
    chapter_id: str,
    schema_version: str = "1.0.0",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (writer_handoff_script, internal_record_script) minimal valid shapes."""
    ch = _find_chapter(handoff, chapter_number)
    if ch is None:
        raise ValueError(f"No chapter {chapter_number} in handoff")

    panels: list[dict[str, Any]] = []
    internal_panels: list[dict[str, Any]] = []
    for beat in ch.get("plot_beats") or []:
        pid = f"p_{chapter_number}_{beat['beat_index']}"
        base = {
            "panel_id": pid,
            "dialogue": [],
            "action": str(beat.get("beat_text", "")),
            "camera": "medium",
            "mood": "neutral",
        }
        panels.append(deepcopy(base))
        internal = deepcopy(base)
        internal["is_carrier_beat"] = False
        internal_panels.append(internal)

    page = {
        "page_number": 1,
        "page_type": "standard",
        "panels": panels,
    }
    page_i = {
        "page_number": 1,
        "page_type": "standard",
        "panels": internal_panels,
    }

    writer = {
        "schema_version": schema_version,
        "artifact_type": "chapter_script_writer_handoff",
        "series_id": series_id,
        "chapter_id": chapter_id,
        "pages": [page],
    }
    internal = {
        "schema_version": schema_version,
        "artifact_type": "chapter_script_internal_record",
        "series_id": series_id,
        "chapter_id": chapter_id,
        "pages": [page_i],
    }
    return writer, internal
