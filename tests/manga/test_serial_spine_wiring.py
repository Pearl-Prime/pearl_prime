"""Tests for serial spine loader + story_architect/writer wiring."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from phoenix_v4.manga.chapter.writer import build_chapter_writer_prompt
from phoenix_v4.manga.models.validation import validate_instance
from phoenix_v4.manga.serial.spine_loader import (
    audit_adopted_series,
    build_episode_architect_input,
    build_serial_context,
    is_series_adopted,
    load_continuity_state,
    load_serial_spine,
    serial_prompt_block,
    validate_continuity_state,
    validate_serial_spine,
)
from phoenix_v4.manga.series.story_architect import build_story_architecture_internal
from phoenix_v4.manga.transmission import story_architecture_internal_to_handoff

REPO_ROOT = Path(__file__).resolve().parents[2]

ROMANCE_SID = "heart_balance_shojo__en_US__romance_josei_drama__series01"
HISTORICAL_SID = "legacy_builder_memoir__en_US__historical_period__series01"
CULTIVATION_SID = "devotion_path_shonen__en_US__cultivation_martial__series01"
DARK_FANTASY_SID = "stillness_press__en_US__dark_fantasy__series02"
ACTION_BATTLE_SID = "stillness_press__en_US__action_battle__series01"
PSYCH_THRILLER_SID = "stillness_press__en_US__psychological_thriller__series01"

EXEMPLARS = (ROMANCE_SID, HISTORICAL_SID, CULTIVATION_SID, DARK_FANTASY_SID)
CONTINUITY_SEED_LANES = (ACTION_BATTLE_SID, PSYCH_THRILLER_SID)


@pytest.mark.parametrize("series_id", EXEMPLARS)
def test_exemplar_adopted_and_spine_valid(series_id):
    assert is_series_adopted(series_id, REPO_ROOT)
    spine = load_serial_spine(series_id, repo_root=REPO_ROOT)
    assert spine is not None
    assert not validate_serial_spine(spine)


@pytest.mark.parametrize("series_id", EXEMPLARS)
def test_serial_context_has_engine_and_hooks(series_id):
    ctx = build_serial_context(series_id, chapter_number=2, repo_root=REPO_ROOT)
    assert ctx is not None
    assert ctx.get("serial_engine")
    assert ctx.get("long_arc_spine")
    assert ctx.get("settled_state")
    assert ctx.get("unresolved_hooks")
    assert ctx.get("episode_mandate", {}).get("must_rebreak")


def test_architect_includes_serial_context_for_romance():
    internal = build_story_architecture_internal(
        series_id=ROMANCE_SID,
        arc_id="arc_v1",
        genre_id="romance_josei_drama",
        topic="self_worth",
        mode="music",
        chapter_number=2,
        repo_root=REPO_ROOT,
    )
    assert "serial_context" in internal
    assert internal["serial_context"]["serial_engine"] == "delay_gaze_proximity_confession"
    assert "+serial_spine" in internal["transmission_audit"]["note"]
    ch2 = internal["chapters"][1]
    assert ch2["plot_beats"][0].get("serial_carrier_beat") is True
    assert "re-break" in ch2["plot_beats"][0]["beat_text"].lower()

    handoff = story_architecture_internal_to_handoff(internal)
    assert handoff.get("serial_context") is not None


def test_ep_002_architect_input_carries_rival_for_cultivation():
    payload = build_episode_architect_input(
        CULTIVATION_SID, chapter_number=2, repo_root=REPO_ROOT,
    )
    assert payload["artifact_type"] == "serial_episode_architect_input"
    assert payload["chapter_id"] == "ep_002"
    rivals = payload["carries_forward"]["rival_state"]
    assert any(r.get("rival_id") == "wei_long" for r in rivals)
    mandate = payload["episode_mandate"]
    assert "wei_long" in json.dumps(mandate).lower()
    assert mandate.get("must_rebreak")


def test_writer_prompt_includes_serial_mandate():
    internal = build_story_architecture_internal(
        series_id=DARK_FANTASY_SID,
        arc_id="arc_v1",
        genre_id="dark_fantasy",
        mode="teacher",
        chapter_number=2,
        repo_root=REPO_ROOT,
    )
    handoff = story_architecture_internal_to_handoff(internal)
    prompt = build_chapter_writer_prompt(
        handoff,
        chapter_number=2,
        series_id=DARK_FANTASY_SID,
        chapter_id="ep_002",
        mode="teacher",
        genre_id="dark_fantasy",
    )
    assert "Serial spine" in prompt
    assert "iron_wardens" in prompt.lower() or "Iron Warden" in prompt
    assert "must_rebreak" in prompt.lower() or "re-break" in prompt.lower()


def test_audit_adopted_series_all_pass():
    rows = audit_adopted_series(REPO_ROOT)
    assert len(rows) >= 4
    assert all(r["status"] == "PASS" for r in rows)


def test_serial_prompt_block_non_empty():
    ctx = build_serial_context(ROMANCE_SID, chapter_number=2, repo_root=REPO_ROOT)
    block = serial_prompt_block(ctx, chapter_number=2)
    assert "premiere_clock" in block or "window_seat" in block


@pytest.mark.parametrize("series_id", CONTINUITY_SEED_LANES)
def test_continuity_seed_validates_loader_and_schema(series_id):
    state = load_continuity_state(series_id, repo_root=REPO_ROOT)
    assert state is not None
    assert not validate_continuity_state(state)
    validate_instance(state, "series_continuity_state")
    mandate = state.get("next_episode_mandate") or {}
    assert mandate.get("episode_id") == "ep_002"
    assert mandate.get("must_rebreak")
    assert mandate.get("must_plant")
    assert mandate.get("forbidden")
