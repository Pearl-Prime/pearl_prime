"""Tests for attach_exercise_journeys in enrichment_select."""
from __future__ import annotations

from phoenix_v4.planning.enrichment_select import (
    EnrichedBook,
    EnrichedChapter,
    EnrichedSlot,
    attach_exercise_journeys,
)


def _ten_slot_chapter() -> EnrichedChapter:
    slots: list[EnrichedSlot] = []
    for i in range(10):
        sec = i + 1
        st = "EXERCISE" if sec in (4, 8) else "HOOK"
        slots.append(
            EnrichedSlot(
                slot_type=st,
                content="c",
                source="registry",
                source_id="id",
                target_words=100,
                actual_words=1,
                enrichment_applied=[],
            )
        )
    return EnrichedChapter(
        number=1,
        role="r",
        working_title="w",
        thesis="t",
        slots=slots,
        total_words=10,
        source_breakdown={},
        exercise_journey=None,
    )


def test_attach_disabled_returns_same_audit_len():
    ch = _ten_slot_chapter()
    book = EnrichedBook(
        schema_version=1,
        stage="enrichment_select",
        topic="anxiety",
        teacher_id=None,
        persona_id="gen_z_professionals",
        runtime_format="standard_book",
        chapters=[ch],
        total_words=10,
        enrichment_audit={},
    )
    out = attach_exercise_journeys(book, seed="s", enabled=False)
    assert "exercise_journeys" not in out.enrichment_audit


def test_attach_sets_journey_and_phases_on_exercise_slots():
    ch = _ten_slot_chapter()
    book = EnrichedBook(
        schema_version=1,
        stage="enrichment_select",
        topic="anxiety",
        teacher_id=None,
        persona_id="gen_z_professionals",
        runtime_format="standard_book",
        chapters=[ch],
        total_words=10,
        enrichment_audit={},
    )
    out = attach_exercise_journeys(book, seed="attach_test", enabled=True)
    assert out.chapters[0].exercise_journey
    assert out.chapters[0].exercise_journey["journey_type"] == "2_step"
    tagged = [s for s in out.chapters[0].slots if s.exercise_phase]
    assert len(tagged) == 2
    phases = {s.exercise_phase for s in tagged}
    assert phases == {"awareness", "regulation"}
