"""Book-wide flagship chapter shape gate — mutation proofs (red-then-reverted)."""
from __future__ import annotations

import pytest

from phoenix_v4.planning.chapter_object_continuity import (
    filter_persona_pool_one_character,
    forbidden_characters_in_text,
)
from scripts.ci.check_flagship_chapter_shape import assert_flagship_chapter_shape


def _sample_ch3() -> str:
    return (
        "Priya opens the doc again. The alarm is still ringing.\n\n"
        "[Angle journey — layer 2 callback placeholder.]\n\n"
        "Earlier I said the alarm is not broken.\n\n"
        "Just thirty seconds.\n\n"
        "Notice the space that breath moves through.\n\n"
        "Priya closes the laptop."
    )


def _sample_ch4_full_exercise() -> str:
    return (
        "Priya sits with the thread still open.\n\n"
        "Earlier I said the alarm has a shape.\n\n"
        "Just thirty seconds.\n\n"
        "This is Breath and Space. Not to empty your mind.\n\n"
        "Notice the space that breath moves through.\n\n"
        "Now, notice if your breathing changed. Or not. Both are fine.\n\n"
        "Before you move on, one breath is a whole meditation.\n\n"
        "Priya exhales."
    )


def test_mutation_placeholder_in_ch3_fails_gate() -> None:
    with pytest.raises(AssertionError, match="placeholder"):
        assert_flagship_chapter_shape(_sample_ch3(), chapter_number=3)


def test_mutation_body_only_exercise_in_ch4_fails_gate() -> None:
    thin = (
        "Priya sits.\n\n"
        "Just thirty seconds.\n\n"
        "Notice the space that breath moves through.\n\n"
        "Priya exhales."
    )
    with pytest.raises(AssertionError, match="5-layer|thin"):
        assert_flagship_chapter_shape(thin, chapter_number=4)


def test_mutation_second_named_character_in_ch2_fails_gate() -> None:
    text = "Priya waits. Jordan sends another ping. Priya breathes."
    with pytest.raises(AssertionError, match="Jordan"):
        assert_flagship_chapter_shape(text, chapter_number=2)


def test_ch4_full_exercise_passes_gate() -> None:
    assert_flagship_chapter_shape(_sample_ch4_full_exercise(), chapter_number=4)


def test_persona_pool_filters_forbidden_character() -> None:
    pool = [
        {"atom_id": "good", "content": "Priya waits for the reply."},
        {"atom_id": "bad", "content": "Jordan presents the quarterly findings."},
    ]
    filtered = filter_persona_pool_one_character(pool, "Priya")
    assert len(filtered) == 1
    assert filtered[0]["atom_id"] == "good"
    assert forbidden_characters_in_text("Jordan waits.", "Priya") == ["Jordan"]
