"""F3+F4: five-part exercise assembly (Holistic v2 Phase B)."""
from __future__ import annotations

import pytest

from phoenix_v4.exercises.component_assembler import assemble_exercise_for_chapter
from phoenix_v4.exercises.models import AssemblyContext, EmotionalState
from phoenix_v4.rendering.golden_chapter_synthesis import _bucket_slots
from phoenix_v4.planning.enrichment_select import EnrichedSlot


@pytest.fixture(autouse=True)
def _enable_exercise_component_templates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PHOENIX_ENABLE_RENDER_GLUE", "1")


def test_assemble_exercise_includes_all_five_parts():
    ctx = AssemblyContext(
        chapter_index=0,
        emotional_state=EmotionalState.NEUTRAL,
        first_encounter=True,
    )
    guidance = (
        "Sit comfortably. Notice your breath for thirty seconds. "
        "Let the shoulders drop without forcing them."
    )
    out = assemble_exercise_for_chapter(
        exercise_id="test_ex",
        exercise_type="00_breath_regulation",
        description_text=guidance,
        ctx=ctx,
    )
    assert "Now we're going to do" in out
    assert "This is a" in out or "breath" in out.lower()
    assert guidance in out
    assert "Now, I want you to" in out
    assert "Before you return" in out


def test_depth_practice_scaffold_routes_to_exercise_bucket():
    raw = "Sit quietly. Notice the breath. Do not fix anything."
    def _slot(st: str) -> EnrichedSlot:
        return EnrichedSlot(
            slot_type=st,
            content=raw,
            source="test",
            source_id="t1",
            target_words=100,
            actual_words=len(raw.split()),
            enrichment_applied=[],
        )

    slots = [_slot("EXERCISE"), _slot("DEPTH_PRACTICE_SCAFFOLD")]
    b = _bucket_slots(slots)
    assert len(b["EXERCISE"]) >= 2
    assert not any("practice" in x.lower() for x in b["_depth_mech"])
