"""Story architecture internal artifact — handoff produced via transmission."""

from __future__ import annotations

from typing import Any


def build_story_architecture_internal(
    *,
    series_id: str,
    arc_id: str,
    schema_version: str = "1.0.0",
    chapters: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build ``story_architecture_internal`` with optional carrier metadata on beats.

    Writer handoff strips beats to ``beat_index`` + ``beat_text`` only
    (see ``transmission.story_architecture_internal_to_handoff``).
    """
    if chapters is None:
        chapters = [
            {
                "chapter_number": 1,
                "chapter_title": "Open",
                "mini_arc_stage": "setup",
                "plot_beats": [
                    {
                        "beat_index": 0,
                        "beat_text": "Establish the street.",
                        "is_carrier_beat": True,
                    },
                    {
                        "beat_index": 1,
                        "beat_text": "First dialogue beat.",
                        "is_carrier_beat": False,
                    },
                ],
                "chapter_end_hook": "Turn",
                "turning_point": None,
                "silence_beats_allocated": 1,
                "villain_presence": "absent",
            }
        ]
    return {
        "schema_version": schema_version,
        "artifact_type": "story_architecture_internal",
        "series_id": series_id,
        "arc_id": arc_id,
        "chapters": chapters,
        "transmission_audit": {"note": "chunk_b_deterministic"},
        "constraint_checks": {"passed": True},
    }
