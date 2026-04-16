"""Exercise fallback filter tests — Sanskrit/yoga frame mismatch exclusion.

Tests that:
  1. Exercises with Sanskrit/yoga/spiritual content are excluded from selection.
  2. Secular replacements are selected when Sanskrit exercises are present.
  3. No Sanskrit/spiritual language appears in a rendered test chapter exercise slot.
"""
from __future__ import annotations

import json
import logging
from unittest.mock import patch

import pytest

from phoenix_v4.exercises.practice_library_loader import (
    _exercise_has_frame_mismatch,
    _filter_frame_mismatch,
    _FRAME_MISMATCH_TERMS,
    get_exercise_for_chapter,
)


# ── Helpers ─────────────────────────────────────────────────────────────────

def _make_exercise(
    id: str,
    name: str,
    text: str = "",
    tags: list[str] | None = None,
    components: dict | None = None,
) -> dict:
    return {
        "id": id,
        "name": name,
        "exercise_type": "00_breath_regulation",
        "duration_seconds": 120,
        "difficulty": "beginner",
        "tags": tags or [],
        "text": text,
        "components": components or {},
    }


SANSKRIT_EXERCISE = _make_exercise(
    id="test_sanskrit_01",
    name="Three-Part Breath",
    text=(
        "This is three-part breath or Dirga Pranayama. You breathe into three zones: "
        "belly, ribs, upper chest."
    ),
    tags=["breath", "awareness", "belly"],
)

YOGA_EXERCISE = _make_exercise(
    id="test_yoga_01",
    name="Liberation Laughter",
    text=(
        "Force a laugh. Now, before you move on, laughter yoga groups exist for a reason. "
        "You do not need a group."
    ),
    tags=["laughter", "release"],
)

SECULAR_EXERCISE_A = _make_exercise(
    id="test_secular_01",
    name="Four-Seven-Eight Breath",
    text=(
        "Breathe in for four counts. Hold for seven. Exhale for eight. Repeat four times. "
        "Your nervous system responds to extended exhale by activating the vagal brake."
    ),
    tags=["breath", "vagal", "regulation"],
)

SECULAR_EXERCISE_B = _make_exercise(
    id="test_secular_02",
    name="5-4-3-2-1 Grounding",
    text=(
        "Name five things you can see. Four you can touch. Three you can hear. "
        "Two you can smell. One you can taste. This anchors the nervous system in present sensory data."
    ),
    tags=["grounding", "sensory", "orientation"],
)


# ── Unit tests: _exercise_has_frame_mismatch ─────────────────────────────────

def test_sanskrit_exercise_detected_as_frame_mismatch():
    """Exercise containing 'Pranayama' / 'Dirga' is flagged as frame_mismatch."""
    assert _exercise_has_frame_mismatch(SANSKRIT_EXERCISE) is True


def test_yoga_exercise_detected_as_frame_mismatch():
    """Exercise containing 'laughter yoga' is flagged as frame_mismatch."""
    assert _exercise_has_frame_mismatch(YOGA_EXERCISE) is True


def test_secular_exercise_not_flagged():
    """A secular somatic exercise is not flagged as frame_mismatch."""
    assert _exercise_has_frame_mismatch(SECULAR_EXERCISE_A) is False


def test_secular_grounding_exercise_not_flagged():
    assert _exercise_has_frame_mismatch(SECULAR_EXERCISE_B) is False


def test_frame_mismatch_case_insensitive():
    """Detection is case-insensitive (e.g. 'PRANAYAMA' still matches)."""
    ex = _make_exercise("ci_test", "Test", text="This is PRANAYAMA breathing.")
    assert _exercise_has_frame_mismatch(ex) is True


def test_frame_mismatch_in_tags():
    """Mismatch terms in tags are also caught."""
    ex = _make_exercise("tag_test", "Chakra Flow", tags=["chakra", "energy"])
    assert _exercise_has_frame_mismatch(ex) is True


def test_frame_mismatch_in_components():
    """Mismatch terms embedded in components dict are caught."""
    ex = _make_exercise(
        "comp_test",
        "Awakening",
        components={"intro": {"full": "This draws on kundalini tradition."}},
    )
    assert _exercise_has_frame_mismatch(ex) is True


def test_frame_mismatch_logs_debug(caplog):
    """Flagged exercises log at DEBUG with label names."""
    with caplog.at_level(logging.DEBUG, logger="phoenix_v4.exercises.practice_library_loader"):
        _exercise_has_frame_mismatch(SANSKRIT_EXERCISE)
    assert "frame_mismatch_spiritual" in caplog.text or "frame_mismatch_sanskrit" in caplog.text


# ── Unit tests: _filter_frame_mismatch ───────────────────────────────────────

def test_filter_removes_sanskrit_exercises():
    """_filter_frame_mismatch removes Sanskrit exercises from the pool."""
    pool = [SANSKRIT_EXERCISE, SECULAR_EXERCISE_A, YOGA_EXERCISE, SECULAR_EXERCISE_B]
    result = _filter_frame_mismatch(pool)
    ids = {ex["id"] for ex in result}
    assert "test_sanskrit_01" not in ids
    assert "test_yoga_01" not in ids
    assert "test_secular_01" in ids
    assert "test_secular_02" in ids


def test_filter_returns_empty_if_all_flagged():
    """_filter_frame_mismatch returns empty list when all exercises are flagged."""
    pool = [SANSKRIT_EXERCISE, YOGA_EXERCISE]
    result = _filter_frame_mismatch(pool)
    assert result == []


def test_filter_prefers_secular_somatic_content():
    """When Sanskrit exercises are present, filter selects only secular alternatives."""
    pool = [SANSKRIT_EXERCISE, SECULAR_EXERCISE_A]
    result = _filter_frame_mismatch(pool)
    assert len(result) == 1
    assert result[0]["id"] == "test_secular_01"


# ── Integration test: get_exercise_for_chapter ───────────────────────────────

def test_exercise_fallback_filters_sanskrit_yoga_content():
    """get_exercise_for_chapter excludes Sanskrit/yoga exercises when secular
    alternatives are available in the library."""
    mock_library = {
        "00_breath_regulation": [SANSKRIT_EXERCISE, SECULAR_EXERCISE_A],
    }
    with patch(
        "phoenix_v4.exercises.practice_library_loader.load_practice_library",
        return_value=mock_library,
    ):
        result = get_exercise_for_chapter(
            chapter_index=7,
            topic_id="anxiety",
            persona_id="gen_z_professionals",
            seed="test_seed_phase2",
        )
    assert result is not None
    text_lower = result.lower()
    for term in _FRAME_MISMATCH_TERMS:
        assert term not in text_lower, (
            f"Sanskrit/spiritual term {term!r} found in rendered exercise output"
        )


def test_exercise_fallback_prefers_secular_somatic_content():
    """get_exercise_for_chapter selects a secular exercise over a Sanskrit one."""
    mock_library = {
        "00_breath_regulation": [SANSKRIT_EXERCISE, YOGA_EXERCISE, SECULAR_EXERCISE_A],
    }
    with patch(
        "phoenix_v4.exercises.practice_library_loader.load_practice_library",
        return_value=mock_library,
    ):
        result = get_exercise_for_chapter(
            chapter_index=3,
            topic_id="anxiety",
            persona_id="gen_z_professionals",
            seed="test_seed_secular_pref",
        )
    assert result is not None
    # The selected exercise should not contain any frame-mismatch terms
    for term in _FRAME_MISMATCH_TERMS:
        assert term not in result.lower()


def test_spine_render_excludes_spiritual_exercise_language():
    """When the exercise pool contains only Sanskrit exercises, the fallback
    warning is logged and the pool is used in full (no crash) — but in normal
    conditions (secular exercises available) the output is clean."""
    mock_library = {
        "00_breath_regulation": [SECULAR_EXERCISE_A, SECULAR_EXERCISE_B],
        "01_grounding_orientation": [SECULAR_EXERCISE_B],
    }
    with patch(
        "phoenix_v4.exercises.practice_library_loader.load_practice_library",
        return_value=mock_library,
    ):
        for ch_idx in range(12):
            result = get_exercise_for_chapter(
                chapter_index=ch_idx,
                topic_id="anxiety",
                persona_id="gen_z_professionals",
                seed=f"test_seed_spine_ch{ch_idx}",
            )
            if result:
                for term in _FRAME_MISMATCH_TERMS:
                    assert term not in result.lower(), (
                        f"ch{ch_idx}: spiritual term {term!r} in rendered output"
                    )


def test_exercise_filter_logs_mismatch_when_all_flagged(caplog):
    """When all exercises are flagged, a warning is logged and execution continues."""
    mock_library = {
        "00_breath_regulation": [SANSKRIT_EXERCISE, YOGA_EXERCISE],
    }
    with caplog.at_level(logging.WARNING, logger="phoenix_v4.exercises.practice_library_loader"):
        with patch(
            "phoenix_v4.exercises.practice_library_loader.load_practice_library",
            return_value=mock_library,
        ):
            result = get_exercise_for_chapter(
                chapter_index=5,
                topic_id="anxiety",
                persona_id="gen_z_professionals",
                seed="test_seed_all_flagged",
            )
    assert "EXERCISE FRAME FILTER" in caplog.text
    # Returns something even when all flagged (uses full pool as fallback)
    assert result is not None
