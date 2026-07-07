"""Transmission Splitter — story_architecture_internal → story_architecture_handoff (pure).

Per MANGA_STORY_ARCHITECT_SPEC §5 (Fix 1): strip carrier metadata and system-only blocks
so Chapter Writer sees plot beats only.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


def _strip_beat_for_handoff(beat: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "beat_index": int(beat["beat_index"]),
        "beat_text": str(beat.get("beat_text", "")),
    }


def _strip_chapter_for_handoff(chapter: Mapping[str, Any]) -> dict[str, Any]:
    beats = chapter.get("plot_beats") or []
    out: dict[str, Any] = {
        "chapter_number": int(chapter["chapter_number"]),
        "plot_beats": [_strip_beat_for_handoff(b) for b in beats],
    }
    if "chapter_title" in chapter:
        out["chapter_title"] = chapter["chapter_title"]
    if "chapter_end_hook" in chapter:
        out["chapter_end_hook"] = chapter["chapter_end_hook"]
    if "turning_point" in chapter:
        out["turning_point"] = chapter["turning_point"]
    return out


def story_architecture_internal_to_handoff(internal: Mapping[str, Any]) -> dict[str, Any]:
    """Return a new dict: writer-facing story_architecture_handoff (validated separately)."""
    if internal.get("artifact_type") != "story_architecture_internal":
        raise ValueError(
            "Expected artifact_type story_architecture_internal, got "
            f"{internal.get('artifact_type')!r}"
        )
    out: dict[str, Any] = {}
    for key in (
        "schema_version",
        "spec_version",
        "generator_version",
        "prompt_id",
        "prompt_version",
        "created_at",
        "provenance",
        "series_id",
        "arc_id",
    ):
        if key in internal:
            out[key] = deepcopy(internal[key])
    out["artifact_type"] = "story_architecture_handoff"
    out["chapters"] = [
        _strip_chapter_for_handoff(ch) for ch in (internal.get("chapters") or [])
    ]
    if internal.get("serial_context") is not None:
        out["serial_context"] = deepcopy(internal["serial_context"])
    if internal.get("mode") is not None:
        out["mode"] = internal["mode"]
    if internal.get("mode_vessel") is not None:
        out["mode_vessel"] = deepcopy(internal["mode_vessel"])
    return out
