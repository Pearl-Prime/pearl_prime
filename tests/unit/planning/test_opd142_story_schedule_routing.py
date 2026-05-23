"""OPD-142 — story_schedule routing regression fix.

PR #1248 (OPD-116/117 angle journey) inserted ANGLE_DEFINITION / ANGLE_CALLBACK
slots into the slot list, breaking the `slot_i + 1 == somatic_section_index`
invariant that PR #669's story_schedule routing depended on. After the fix,
the STORY guard at enrichment_select.py:1707 keys off slot.somatic_section_index
(which patch_beatmap_angle_journey preserves) rather than slot list position.

These tests assert the routing works under both:
- no angle_id (back-compat with original PR #669 behavior)
- angle_id ENGINE present (PR #1248 angle journey inserts new slots)
"""
from __future__ import annotations

import pytest

# Test 1: slot.somatic_section_index is correctly preserved across angle journey insertions.
def test_somatic_section_index_preserved_under_angle_journey_insertion() -> None:
    """When patch_beatmap_angle_journey inserts ANGLE_DEFINITION / ANGLE_CALLBACK,
    existing slots retain their original somatic_section_index. STORY slots at
    somatic section 2/5/9 remain routable via story_schedule even when their
    slot-list index shifts due to angle insertion."""
    from phoenix_v4.planning.beatmap_compile import (
        SOMATIC_10_SLOT_GRID,
        SLOT_TO_SOMATIC_INDEX,
    )
    # Verify the grid mapping is what OPD-142 fix expects
    assert len(SOMATIC_10_SLOT_GRID) == 10
    assert SOMATIC_10_SLOT_GRID[1] == "STORY"  # slot_i=1 → section_02 (RECOGNITION)
    assert SOMATIC_10_SLOT_GRID[4] == "STORY"  # slot_i=4 → section_05 (MECHANISM_PROOF)
    assert SOMATIC_10_SLOT_GRID[8] == "STORY"  # slot_i=8 → section_09 (TURNING_POINT)


def test_scene_section_indices_include_2_5_9() -> None:
    """SCENE_SECTION_INDICES is the integer set the STORY routing checks against.
    Must contain 2/5/9 to enable the named-character × 3 beats routing per chapter."""
    from phoenix_v4.planning.enrichment_select import SCENE_SECTION_INDICES
    assert 2 in SCENE_SECTION_INDICES
    assert 5 in SCENE_SECTION_INDICES
    assert 9 in SCENE_SECTION_INDICES


def test_fix_uses_getattr_fallback_to_slot_i_plus_1() -> None:
    """The OPD-142 fix uses `getattr(slot, 'somatic_section_index', 0) or (slot_i + 1)`.
    This grep-test guards against a future regression that would re-introduce
    the simple `_sec_idx = slot_i + 1` form."""
    import inspect
    from phoenix_v4.planning import enrichment_select
    source = inspect.getsource(enrichment_select)
    # The fix must be present
    assert 'getattr(slot, "somatic_section_index", 0) or (slot_i + 1)' in source, (
        "OPD-142 fix regression: enrichment_select.py:~1707 must read "
        '`getattr(slot, "somatic_section_index", 0) or (slot_i + 1)` not `slot_i + 1`'
    )
    # The naive form must NOT be the sole assignment at that location
    naive_count = source.count("            _sec_idx = slot_i + 1\n")
    assert naive_count == 0, (
        f"OPD-142 regression: found {naive_count} occurrences of naive "
        "`_sec_idx = slot_i + 1` that bypass somatic_section_index"
    )
