"""OPD-143 — distinguish arc-positions across 3 STORY slots per chapter.

After OPD-142 restored story_schedule routing via `slot.somatic_section_index`,
a second-order bug surfaced: in `patch_beatmap_angle_journey` (angle_journey.py:200)
the existing slots were indexed into a `dict[slot_type → BeatmapSlot]` and then
re-emitted for every occurrence of that slot_type in the angle-journey row.

Because SOMATIC_10_SLOT_GRID has three STORY entries (sec 2/5/9), two REFLECTION
entries (sec 3/7), and two EXERCISE entries (sec 4/8), the dict collapsed each
repeating type onto its LAST occurrence. The result: all three STORY slots in
every chapter pointed at the SAME BeatmapSlot instance — the one whose
`somatic_section_index` was 9. Downstream, `_story_schedule.get(chapter, 9)`
returned the `turning_point` atom three times in a row, regardless of section.

The fix replaces the dict with a per-type FIFO queue so each occurrence of a
repeating slot_type consumes a distinct original BeatmapSlot in order.

These tests assert post-patch invariants:
- For each chapter, the three STORY slots are three DISTINCT objects
- Their somatic_section_index values are exactly {2, 5, 9}
- Same distinctness holds for REFLECTION (2 slots, indices {3, 7}) and EXERCISE
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class _StubSlot:
    """Mirror of beatmap_compile.BeatmapSlot for unit-level patch testing."""
    slot_type: str
    weight: float = 1.0
    target_words: int = 400
    somatic_section_index: int = 0
    atom_selection_criteria: Dict[str, Any] = field(default_factory=dict)
    enrichment_hooks: List[str] = field(default_factory=list)
    emotional_temperature: str = "warm"
    is_required: bool = True


@dataclass
class _StubChapter:
    number: int
    slots: List[_StubSlot]
    slot_definitions: List[str] = field(default_factory=list)


@dataclass
class _StubBeatmap:
    chapters: List[_StubChapter]
    runtime_format: str = "deep_book_6h"


def _build_somatic_chapter(number: int) -> _StubChapter:
    """Construct a chapter with SOMATIC_10_SLOT_GRID slots, somatic_section_index 1..10."""
    from phoenix_v4.planning.beatmap_compile import SOMATIC_10_SLOT_GRID

    slots: List[_StubSlot] = []
    for j, st in enumerate(SOMATIC_10_SLOT_GRID):
        slots.append(_StubSlot(slot_type=st, somatic_section_index=j + 1))
    return _StubChapter(number=number, slots=slots, slot_definitions=list(SOMATIC_10_SLOT_GRID))


def test_three_story_slots_are_distinct_after_angle_patch() -> None:
    """After patch_beatmap_angle_journey, Ch1's 3 STORY slots must be 3 distinct
    BeatmapSlot objects with somatic_section_index {2, 5, 9} — not 3 aliases to
    the section-9 slot (the original OPD-143 bug)."""
    from phoenix_v4.planning.angle_journey import patch_beatmap_angle_journey

    bm = _StubBeatmap(chapters=[_build_somatic_chapter(n) for n in (1, 2)])
    patch_beatmap_angle_journey(bm, angle_id="ENGINE")

    for ch in bm.chapters:
        story_slots = [s for s in ch.slots if s.slot_type == "STORY"]
        assert len(story_slots) == 3, (
            f"Ch{ch.number}: expected 3 STORY slots after angle patch, got {len(story_slots)}"
        )
        ids = {id(s) for s in story_slots}
        assert len(ids) == 3, (
            f"Ch{ch.number}: 3 STORY slots collapsed onto {len(ids)} distinct object(s); "
            "patch_beatmap_angle_journey is aliasing repeating slot_types"
        )
        sec_indices = sorted(s.somatic_section_index for s in story_slots)
        assert sec_indices == [2, 5, 9], (
            f"Ch{ch.number}: STORY somatic_section_index values {sec_indices}, expected [2,5,9]"
        )


def test_repeating_slot_types_consumed_in_order() -> None:
    """REFLECTION (sec 3/7) and EXERCISE (sec 4/8) also repeat in SOMATIC_10_SLOT_GRID.
    The FIFO consumption order must preserve their original somatic_section_index."""
    from phoenix_v4.planning.angle_journey import patch_beatmap_angle_journey

    bm = _StubBeatmap(chapters=[_build_somatic_chapter(2)])
    patch_beatmap_angle_journey(bm, angle_id="ENGINE")

    ch = bm.chapters[0]
    refl = [s for s in ch.slots if s.slot_type == "REFLECTION"]
    exer = [s for s in ch.slots if s.slot_type == "EXERCISE"]
    assert sorted(s.somatic_section_index for s in refl) == [3, 7]
    assert sorted(s.somatic_section_index for s in exer) == [4, 8]
    # And the slot list must encounter them in increasing sec order
    refl_in_order = [s.somatic_section_index for s in ch.slots if s.slot_type == "REFLECTION"]
    exer_in_order = [s.somatic_section_index for s in ch.slots if s.slot_type == "EXERCISE"]
    assert refl_in_order == [3, 7]
    assert exer_in_order == [4, 8]


def test_angle_callback_inserted_without_collapsing_other_slots() -> None:
    """Ch2 receives ANGLE_CALLBACK after HOOK. The injection must not alias any of
    the existing repeating STORY/REFLECTION/EXERCISE slots."""
    from phoenix_v4.planning.angle_journey import (
        ANGLE_CALLBACK_SLOT,
        patch_beatmap_angle_journey,
    )

    bm = _StubBeatmap(chapters=[_build_somatic_chapter(n) for n in (1, 2)])
    patch_beatmap_angle_journey(bm, angle_id="ENGINE")

    ch2 = bm.chapters[1]
    # Ch2 should have ANGLE_CALLBACK inserted; verify all repeating types still distinct
    types = [s.slot_type for s in ch2.slots]
    assert ANGLE_CALLBACK_SLOT in types
    for repeat_type in ("STORY", "REFLECTION", "EXERCISE"):
        slots = [s for s in ch2.slots if s.slot_type == repeat_type]
        ids = {id(s) for s in slots}
        assert len(ids) == len(slots), (
            f"Ch2 {repeat_type}: {len(slots)} slots but only {len(ids)} unique objects"
        )
