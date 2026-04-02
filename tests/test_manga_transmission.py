"""Transmission Splitter — internal → handoff."""

from __future__ import annotations

import json
from pathlib import Path

from phoenix_v4.manga.models.validation import load_and_validate, validate_instance
from phoenix_v4.manga.models.leakage import assert_handoff_has_no_transmission_leakage
from phoenix_v4.manga.transmission import story_architecture_internal_to_handoff

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "manga" / "valid"


def test_split_matches_fixture_and_validates() -> None:
    internal = json.loads(
        (FIXTURES / "story_architecture_internal_sample.json").read_text(encoding="utf-8")
    )
    validate_instance(internal, "story_architecture_internal")
    handoff = story_architecture_internal_to_handoff(internal)
    validate_instance(handoff, "story_architecture_handoff")
    assert handoff["artifact_type"] == "story_architecture_handoff"
    assert "transmission_audit" not in handoff
    assert "constraint_checks" not in handoff
    beat = handoff["chapters"][0]["plot_beats"][0]
    assert set(beat.keys()) <= {"beat_index", "beat_text"}
    assert_handoff_has_no_transmission_leakage(handoff)


def test_roundtrip_beats_only_strip_metadata() -> None:
    internal = {
        "schema_version": "1.0.0",
        "artifact_type": "story_architecture_internal",
        "series_id": "s",
        "arc_id": "a",
        "chapters": [
            {
                "chapter_number": 2,
                "chapter_title": "T",
                "plot_beats": [
                    {
                        "beat_index": 0,
                        "beat_type": "action",
                        "beat_text": "Hello",
                        "carrier_beat": {"atom_id": "x"},
                    }
                ],
                "chapter_end_hook": "h",
                "turning_point": None,
            }
        ],
        "transmission_audit": {},
        "constraint_checks": {},
    }
    h = story_architecture_internal_to_handoff(internal)
    assert h["chapters"][0]["plot_beats"][0] == {"beat_index": 0, "beat_text": "Hello"}
