"""Coverage gate must block on teacher-voice slot deficits (INVARIANTS §9)."""
from __future__ import annotations

from phoenix_v4.teacher.coverage_gate import run_coverage_gate


def test_teacher_voice_slots_block_when_empty():
    book_spec = {
        "teacher_id": "nonexistent_teacher_xyz",
        "topic_id": "burnout",
        "persona_id": "gen_z_professionals",
    }
    format_plan = {
        "chapter_count": 12,
        "slot_definitions": [
            ["HOOK", "SCENE", "STORY", "REFLECTION", "COMPRESSION", "EXERCISE", "INTEGRATION"]
        ],
    }
    arc = {"emotional_curve": [3] * 12}
    passed, gap = run_coverage_gate(book_spec, format_plan, arc)
    assert passed is False
    assert gap is not None
    gaps = gap.get("gaps") or {}
    assert gaps.get("REFLECTION", {}).get("total_missing", 0) > 0
    assert gaps.get("COMPRESSION", {}).get("total_missing", 0) > 0


def test_persona_fallback_slots_do_not_alone_block():
    book_spec = {
        "teacher_id": "nonexistent_teacher_xyz",
        "topic_id": "burnout",
        "persona_id": "gen_z_professionals",
    }
    format_plan = {
        "chapter_count": 2,
        "slot_definitions": [["HOOK", "SCENE", "STORY"]],
    }
    arc = {"emotional_curve": [3, 3]}
    passed, gap = run_coverage_gate(book_spec, format_plan, arc)
    assert passed is True
    assert gap is not None
