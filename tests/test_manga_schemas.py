"""Manga JSON Schemas — validation and fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from phoenix_v4.manga.models.leakage import assert_handoff_has_no_transmission_leakage
from phoenix_v4.manga.models.validation import (
    iter_instance_schema_stems,
    load_and_validate,
    validate_instance,
    validator_for,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "manga"
VALID = FIXTURES / "valid"
INVALID = FIXTURES / "invalid"

_ZERO_SHA = "0" * 64


def _minimal_payload(stem: str) -> dict:
    common = {"schema_version": "1.0.0", "artifact_type": stem}
    builders: dict[str, dict] = {
        "chapter_request": {
            **common,
            "artifact_type": "chapter_request",
            "series_id": "s",
            "chapter_id": "c",
        },
        "style_bible": {
            **common,
            "artifact_type": "style_bible",
            "style_bible_version": "1.0.0",
            "lexicons": {},
        },
        "lettering_style_bible": {
            **common,
            "artifact_type": "lettering_style_bible",
            "fonts": {},
        },
        "genre_blueprint": {
            **common,
            "artifact_type": "genre_blueprint",
            "genre_id": "shonen",
        },
        "story_architecture_internal": {
            **common,
            "artifact_type": "story_architecture_internal",
            "series_id": "s",
            "arc_id": "a",
            "chapters": [
                {
                    "chapter_number": 1,
                    "plot_beats": [
                        {"beat_index": 0, "beat_text": "x", "beat_type": "opening"}
                    ],
                }
            ],
            "transmission_audit": {},
            "constraint_checks": {},
        },
        "story_architecture_handoff": {
            **common,
            "artifact_type": "story_architecture_handoff",
            "series_id": "s",
            "arc_id": "a",
            "chapters": [
                {
                    "chapter_number": 1,
                    "plot_beats": [{"beat_index": 0, "beat_text": "x"}],
                }
            ],
        },
        "asset_registry": {
            **common,
            "artifact_type": "asset_registry",
            "assets": [{"asset_id": "a1"}],
        },
        "character_model_sheets": {
            **common,
            "artifact_type": "character_model_sheets",
            "characters": [{"character_id": "c1"}],
        },
        "motif_evolution_map": {
            **common,
            "artifact_type": "motif_evolution_map",
            "motifs": [],
        },
        "chapter_script_writer_handoff": {
            **common,
            "artifact_type": "chapter_script_writer_handoff",
            "series_id": "s",
            "chapter_id": "c1",
            "pages": [],
        },
        "chapter_script_internal_record": {
            **common,
            "artifact_type": "chapter_script_internal_record",
            "series_id": "s",
            "chapter_id": "c1",
            "pages": [{"panels": [{"carrier_beat": True}]}],
        },
        "panel_prompts": {
            **common,
            "artifact_type": "panel_prompts",
            "panels": [{"panel_id": "p1", "prompt": "test"}],
        },
        "panel_images_manifest": {
            **common,
            "artifact_type": "panel_images_manifest",
            "panels": [{"panel_id": "p1", "status": "pending"}],
        },
        "lettering_spec": {
            **common,
            "artifact_type": "lettering_spec",
            "lettering_panels": [{"panel_id": "p1", "silence_confirmed": True}],
        },
        "revision_queue": {
            **common,
            "artifact_type": "revision_queue",
            "chapter_clearance": "pass",
            "issues": [],
        },
        "series_memory": {
            **common,
            "artifact_type": "series_memory",
            "facts": [],
        },
        "series_memory_update": {
            **common,
            "artifact_type": "series_memory_update",
            "patches": [],
        },
        "series_memory_snapshot": {
            **common,
            "artifact_type": "series_memory_snapshot",
            "snapshot_of_series_memory_sha256": _ZERO_SHA,
            "facts": [],
        },
        "stage_manifest": {
            **common,
            "artifact_type": "stage_manifest",
            "stage_id": "chapter_writer",
            "stage_name": "Chapter Writer",
            "attempt": 1,
            "status": "passed",
        },
    }
    if stem not in builders:
        raise KeyError(stem)
    return builders[stem]


@pytest.mark.parametrize("stem", iter_instance_schema_stems())
def test_minimal_instance_validates(stem: str) -> None:
    validate_instance(_minimal_payload(stem), stem)


def test_valid_chapter_request_fixture() -> None:
    load_and_validate(VALID / "minimal_chapter_request.json", "chapter_request")


def test_valid_story_handoff_fixture() -> None:
    data = load_and_validate(
        VALID / "minimal_story_architecture_handoff.json",
        "story_architecture_handoff",
    )
    assert_handoff_has_no_transmission_leakage(data)


def test_invalid_chapter_request_rejected() -> None:
    import jsonschema

    raw = json.loads((INVALID / "chapter_request_missing_series.json").read_text(encoding="utf-8"))
    with pytest.raises(jsonschema.ValidationError):
        validate_instance(raw, "chapter_request")


def test_handoff_fixture_with_leakage_fails_policy() -> None:
    import jsonschema

    raw = json.loads(
        (INVALID / "story_handoff_with_leakage.json").read_text(encoding="utf-8")
    )
    validate_instance(raw, "story_architecture_handoff")
    with pytest.raises(AssertionError, match="Transmission leakage"):
        assert_handoff_has_no_transmission_leakage(raw)


def test_internal_record_may_contain_carrier_beat() -> None:
    data = _minimal_payload("chapter_script_internal_record")
    validate_instance(data, "chapter_script_internal_record")


@pytest.mark.parametrize("stem", iter_instance_schema_stems())
def test_validator_for_each_stem(stem: str) -> None:
    v = validator_for(stem)
    v.validate(_minimal_payload(stem))
