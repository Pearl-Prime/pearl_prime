"""OPD-116/117 Phase B — chapter planner angle journey slot injection."""
from __future__ import annotations

from phoenix_v4.planning.chapter_planner import plan_chapters


def _base_slots(n: int) -> list[list[str]]:
    row = ["HOOK", "STORY", "REFLECTION", "INTEGRATION"]
    return [list(row) for _ in range(n)]


def test_long_form_with_angle_injects_definition_and_callbacks():
    slots = _base_slots(12)
    result = plan_chapters(
        slot_definitions=slots,
        chapter_count=12,
        selector_key_prefix="test:angle:on",
        angle_id="VERDICT",
        runtime_format="deep_book_6h",
    )
    assert result.slot_definitions[0][0] == "HOOK"
    assert "ANGLE_DEFINITION" in result.slot_definitions[0]
    assert result.angle_layer_by_chapter
    for ch_idx in range(1, 12):
        row = result.slot_definitions[ch_idx]
        assert row[0] == "HOOK"
        assert row[1] == "ANGLE_CALLBACK"
        assert ch_idx + 1 in result.angle_layer_by_chapter


def test_long_form_without_angle_unchanged():
    slots = _base_slots(8)
    result = plan_chapters(
        slot_definitions=slots,
        chapter_count=8,
        selector_key_prefix="test:angle:off",
        angle_id=None,
        runtime_format="deep_book_6h",
    )
    flat = [s for row in result.slot_definitions for s in row]
    assert "ANGLE_DEFINITION" not in flat
    assert "ANGLE_CALLBACK" not in flat
    assert not result.angle_layer_by_chapter


def test_micro_book_15_unchanged_with_angle():
    slots = _base_slots(5)
    result = plan_chapters(
        slot_definitions=slots,
        chapter_count=5,
        selector_key_prefix="test:micro",
        angle_id="VERDICT",
        runtime_format="micro_book_15",
    )
    flat = [s for row in result.slot_definitions for s in row]
    assert "ANGLE_DEFINITION" not in flat
    assert "ANGLE_CALLBACK" not in flat
    assert not result.angle_layer_by_chapter
