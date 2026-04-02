"""Chapter Writer replay path — validated pair + leakage checks."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from phoenix_v4.manga.chapter.writer import write_chapter_script_pair
from phoenix_v4.manga.llm.client import ReplayLLMClient
from phoenix_v4.manga.models.validation import validate_instance

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "manga"
REPLAY = FIXTURES / "replay" / "chapter_script_pair_minimal.json"
VALID_STORY = FIXTURES / "valid" / "minimal_story_architecture_handoff.json"


def test_write_chapter_script_pair_replay_validates(tmp_path: Path) -> None:
    story = json.loads(VALID_STORY.read_text(encoding="utf-8"))
    client = ReplayLLMClient.from_json_file(REPLAY)
    wh, ir = write_chapter_script_pair(
        client,
        story,
        chapter_number=1,
        series_id="sample_series",
        chapter_id="ch01",
        debug_path=tmp_path / "writer_debug.json",
    )
    validate_instance(wh, "chapter_script_writer_handoff")
    validate_instance(ir, "chapter_script_internal_record")
    assert wh["chapter_id"] == "ch01"
    assert ir["pages"][0]["panels"][0].get("is_carrier_beat") is False


def test_write_chapter_script_pair_missing_keys_raises() -> None:
    story = json.loads(VALID_STORY.read_text(encoding="utf-8"))
    client = ReplayLLMClient({"chapter_script_writer_handoff": {}})
    with pytest.raises(ValueError, match="missing keys"):
        write_chapter_script_pair(
            client,
            story,
            chapter_number=1,
            series_id="sample_series",
            chapter_id="ch01",
        )


def test_write_chapter_script_pair_rejects_transmission_leakage_in_handoff() -> None:
    story = json.loads(VALID_STORY.read_text(encoding="utf-8"))
    raw = json.loads(REPLAY.read_text(encoding="utf-8"))
    bad = deepcopy(raw)
    bad["chapter_script_writer_handoff"]["pages"][0]["panels"][0][
        "is_carrier_beat"
    ] = True
    client = ReplayLLMClient(bad)
    with pytest.raises(AssertionError, match="Transmission leakage"):
        write_chapter_script_pair(
            client,
            story,
            chapter_number=1,
            series_id="sample_series",
            chapter_id="ch01",
        )


def test_build_prompt_requires_chapter_in_handoff() -> None:
    from phoenix_v4.manga.chapter.writer import build_chapter_writer_prompt

    story = json.loads(VALID_STORY.read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="No chapter 99"):
        build_chapter_writer_prompt(
            story, chapter_number=99, series_id="s", chapter_id="c"
        )
