"""Tests for spine enriched-book slot bridge injection."""

import pytest

from phoenix_v4.planning.enrichment_select import (
    EnrichedBook,
    EnrichedChapter,
    EnrichedSlot,
)
from phoenix_v4.rendering import chapter_composer as cc
from phoenix_v4.rendering.chapter_composer import (
    _inject_slot_bridges,
    compose_from_enriched_book,
)


@pytest.fixture(autouse=True)
def _enable_render_glue_for_slot_bridge_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """These tests exercise template slot bridges; production default is glue OFF."""
    monkeypatch.setenv("PHOENIX_ENABLE_RENDER_GLUE", "1")
    monkeypatch.setenv("PHOENIX_BRIDGE_TRANSITION_FAMILIES", "1")
    cc._BRIDGE_TRANSITION_CACHE = None


def _slot(st: str, content: str) -> EnrichedSlot:
    return EnrichedSlot(
        slot_type=st,
        content=content,
        source="test",
        source_id="x",
        target_words=100,
        actual_words=len(content.split()),
        enrichment_applied=[],
    )


def _book(ch_slots: list[EnrichedSlot], runtime_format: str = "standard_book") -> EnrichedBook:
    ch = EnrichedChapter(
        number=1,
        role="test",
        working_title="Alpha",
        thesis="",
        slots=ch_slots,
        total_words=0,
        source_breakdown={},
    )
    return EnrichedBook(
        schema_version=1,
        stage="test",
        topic="anxiety",
        teacher_id=None,
        persona_id="gen_z_professionals",
        runtime_format=runtime_format,
        chapters=[ch],
        total_words=0,
        enrichment_audit={},
    )


def test_bridge_between_scene_and_reflection_when_allowed() -> None:
    slots = [
        _slot("SCENE", "AAA_SCENE_BODY"),
        _slot(
            "REFLECTION",
            "The point is that the alarm fires on prediction, not evidence. Mechanism text here.",
        ),
    ]
    out = _inject_slot_bridges(slots, chapter_index=0, runtime_format="standard_book")
    assert "AAA_SCENE_BODY" in out
    assert "Mechanism text here." in out
    assert out.index("AAA_SCENE_BODY") < out.index("Mechanism text here.")
    parts = out.split("\n\n")
    assert len(parts) >= 2
    assert any("pause" in p.lower() or "inquiry" in p.lower() or "moment" in p.lower() for p in parts)


def test_no_bridge_when_prev_signals_exercise() -> None:
    slots = [
        _slot(
            "REFLECTION",
            "We close with a gentle step. Try this: breathe once and name the sensation.",
        ),
        _slot("EXERCISE", "BBB_EXERCISE_BODY"),
    ]
    out = _inject_slot_bridges(slots, chapter_index=0, runtime_format="standard_book")
    assert out == "We close with a gentle step. Try this: breathe once and name the sensation.\n\nBBB_EXERCISE_BODY"


def test_slot_order_unchanged_markers() -> None:
    slots = [
        _slot("SCENE", "MARK_A"),
        _slot("REFLECTION", "The point is that shame is a pattern. MARK_B"),
    ]
    out = _inject_slot_bridges(slots, chapter_index=0, runtime_format="standard_book")
    assert out.index("MARK_A") < out.index("MARK_B")


def test_micro_format_only_exercise_bridges() -> None:
    slots = [
        _slot("SCENE", "S_ONLY"),
        _slot("REFLECTION", "R_ONLY"),
        _slot("EXERCISE", "E_ONLY"),
    ]
    out = _inject_slot_bridges(slots, chapter_index=0, runtime_format="micro_book_15")
    assert "S_ONLY" in out
    assert "R_ONLY" in out
    assert "E_ONLY" in out
    assert out.index("S_ONLY") < out.index("R_ONLY") < out.index("E_ONLY")
    parts = [p.strip() for p in out.split("\n\n") if p.strip()]
    assert parts[0] == "S_ONLY"
    assert parts[1] == "R_ONLY"
    assert len(parts) >= 4
    assert parts[-1] == "E_ONLY"


def test_standard_book_story_to_reflection_bridge() -> None:
    slots = [
        _slot("STORY", "STORY_MARK"),
        _slot("REFLECTION", "The point is that overwhelm is a capacity signal. REF_MARK"),
    ]
    out = _inject_slot_bridges(slots, chapter_index=0, runtime_format="standard_book")
    assert out.index("STORY_MARK") < out.index("REF_MARK")
    mid = out[out.index("STORY_MARK") + len("STORY_MARK") : out.index("REF_MARK")]
    assert "mirror" in mid.lower() or "story" in mid.lower() or "pattern" in mid.lower()


def test_no_adjacent_duplicate_bridge_norm() -> None:
    slots = [
        _slot("SCENE", "S1"),
        _slot("REFLECTION", "The point is that the alarm fires on prediction. R1"),
        _slot("STORY", "ST1"),
        _slot("REFLECTION", "The point is that the alarm fires on prediction. R2"),
    ]
    out = _inject_slot_bridges(slots, chapter_index=0, runtime_format="standard_book")
    paras = [p.strip() for p in out.split("\n\n") if p.strip()]
    for a, b in zip(paras, paras[1:]):
        if a == b:
            raise AssertionError("adjacent duplicate paragraphs")


def test_compose_from_enriched_book_includes_chapter_header() -> None:
    book = _book(
        [
            _slot("HOOK", "HOOK_LINE"),
            _slot("REFLECTION", "The point is that rest is not earned — it is required. REF_LINE"),
        ],
        runtime_format="standard_book",
    )
    text = compose_from_enriched_book(book)
    assert "Chapter 1" in text
    assert "HOOK_LINE" in text
    assert "REF_LINE" in text
    assert text.index("HOOK_LINE") < text.index("REF_LINE")
