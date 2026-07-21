"""Adjacency selector — opening-mode penalties after doctrine/reflection slots."""

from __future__ import annotations

from phoenix_v4.planning.adjacency_selector import (
    ADJACENCY_PENALTY_JOLT,
    ADJACENCY_BONUS_SOFT,
    adjacency_opening_penalty,
    adjacency_penalty_for_atom,
    is_adjacency_selector_active,
    resolve_opening_mode,
)
from phoenix_v4.planning.enrichment_select import (
    PersonaPoolRotationState,
    _pick_primary_index_unseen,
)


def test_is_adjacency_selector_active_off_for_twelve_shape() -> None:
    assert is_adjacency_selector_active({"twelve_shape_continuity": True}) is False
    assert is_adjacency_selector_active({"chapter_continuity_plan": [{"chapter": 1}]}) is False


def test_is_adjacency_selector_active_off_for_story_picks() -> None:
    assert is_adjacency_selector_active(
        {"chapters": [{"story_picks": {"turning_point": "v03"}}]}
    ) is False


def test_is_adjacency_selector_active_on_for_catalog() -> None:
    assert is_adjacency_selector_active({}) is True
    assert is_adjacency_selector_active({"persona_id": "corporate_managers"}) is True


def test_adjacency_penalizes_named_character_cold_open_after_reflection() -> None:
    assert adjacency_opening_penalty("REFLECTION", "named_character_scene_cold_open") == ADJACENCY_PENALTY_JOLT
    assert adjacency_opening_penalty("TEACHER_DOCTRINE", "named_character_scene_cold_open") == ADJACENCY_PENALTY_JOLT


def test_adjacency_no_penalty_without_doctrine_prior() -> None:
    assert adjacency_opening_penalty("STORY", "named_character_scene_cold_open") == 0.0
    assert adjacency_opening_penalty("HOOK", "named_character_scene_cold_open") == 0.0


def test_adjacency_bonus_soft_opening_after_doctrine() -> None:
    assert adjacency_opening_penalty("REFLECTION", "second_person_direct") == ADJACENCY_BONUS_SOFT
    assert adjacency_opening_penalty("COMPRESSION", "continuation_cue") == ADJACENCY_BONUS_SOFT


def test_resolve_opening_mode_heuristic_named_character() -> None:
    atom = {"content": "Elena sits at her desk and cannot focus on the quarterly review."}
    assert resolve_opening_mode(atom, slot_type="STORY") == "named_character_scene_cold_open"


def test_resolve_opening_mode_metadata_override() -> None:
    atom = {
        "content": "Elena sits at her desk.",
        "metadata": {"opening_mode": "second_person_direct"},
    }
    assert resolve_opening_mode(atom) == "second_person_direct"


def test_pick_primary_skips_jolt_story_after_reflection() -> None:
    pool = [
        {
            "atom_id": "STORY v01",
            "content": "Yuki opens the expense portal and her whole body becomes a held breath.",
            "metadata": {"opening_mode": "named_character_scene_cold_open"},
        },
        {
            "atom_id": "STORY v02",
            "content": "You notice the tension in your shoulders before the meeting even starts.",
            "metadata": {"opening_mode": "second_person_direct"},
        },
    ]
    rot = PersonaPoolRotationState()
    idx = _pick_primary_index_unseen(
        rot,
        pool,
        "seed:ch1:STORY",
        "persona",
        seen_bodies=set(),
        prior_slot_type="REFLECTION",
        adjacency_active=True,
        persona_id="corporate_managers",
        topic_id="burnout",
        candidate_slot_type="STORY",
    )
    assert idx == 1


def test_pick_primary_unchanged_when_adjacency_off() -> None:
    pool = [
        {
            "atom_id": "STORY v01",
            "content": "Yuki opens the expense portal and her whole body becomes a held breath.",
            "metadata": {"opening_mode": "named_character_scene_cold_open"},
        },
        {
            "atom_id": "STORY v02",
            "content": "You notice the tension in your shoulders before the meeting even starts.",
            "metadata": {"opening_mode": "second_person_direct"},
        },
    ]
    rot = PersonaPoolRotationState()
    idx_on = _pick_primary_index_unseen(
        rot,
        pool,
        "seed:flagship:STORY",
        "persona",
        seen_bodies=set(),
        prior_slot_type="REFLECTION",
        adjacency_active=False,
        candidate_slot_type="STORY",
    )
    idx_baseline = rot.pick_index(pool, "seed:flagship:STORY")
    assert idx_on == idx_baseline


def test_adjacency_penalty_for_atom_uses_heuristic() -> None:
    atom = {"content": "Sana sits down to write the retention analysis at nine sharp."}
    pen = adjacency_penalty_for_atom("REFLECTION", atom, slot_type="STORY")
    assert pen == ADJACENCY_PENALTY_JOLT
