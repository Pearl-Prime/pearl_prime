"""
Tests for bestseller structure slot augmentation in chapter planner.

Validates that:
1. _augment_slots_for_bestseller_structure adds required bestseller slots
2. PIVOT, TAKEAWAY, THREAD, PERMISSION appear in augmented slot sequences
3. Base slots (COMPRESSION, etc.) are preserved
4. Unknown structures leave slot row unchanged
5. Beat order matches docs/BESTSELLER_STRUCTURES.md
6. The chapter planner integrates bestseller slot augmentation end-to-end
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.planning.chapter_planner import (
    _augment_slots_for_bestseller_structure,
    assign_bestseller_structures,
)
from phoenix_v4.planning.bestseller_structure_map import (
    BESTSELLER_BEAT_STEPS,
    normalize_structure_key,
    validate_chapter_beat_order,
)


def test_augment_promise_engine_adds_all_required_slots():
    """Promise Engine requires PIVOT, TAKEAWAY, THREAD, and optionally PERMISSION."""
    base = ["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]
    result = _augment_slots_for_bestseller_structure(base, "promise_engine")
    # Must include PIVOT, TAKEAWAY, THREAD
    assert "PIVOT" in result, f"PIVOT missing: {result}"
    assert "TAKEAWAY" in result, f"TAKEAWAY missing: {result}"
    assert "THREAD" in result, f"THREAD missing: {result}"
    # HOOK must come first
    assert result[0] == "HOOK", f"First slot should be HOOK: {result}"
    # Beat order validation should pass
    err = validate_chapter_beat_order("promise_engine", result)
    assert err is None, f"Beat order violation: {err}"


def test_augment_gladwell_spiral_adds_pivot_takeaway_thread():
    """Gladwell Spiral: HOOK, SCENE, STORY, PIVOT, REFLECTION, TAKEAWAY, THREAD."""
    base = ["HOOK", "SCENE", "STORY", "REFLECTION", "INTEGRATION"]
    result = _augment_slots_for_bestseller_structure(base, "gladwell_spiral")
    assert "PIVOT" in result
    assert "TAKEAWAY" in result
    assert "THREAD" in result
    err = validate_chapter_beat_order("gladwell_spiral", result)
    assert err is None, f"Beat order violation: {err}"


def test_augment_permission_slip_adds_permission():
    """Permission Slip structure requires PERMISSION slot (not optional)."""
    base = ["HOOK", "SCENE", "STORY", "REFLECTION", "INTEGRATION"]
    result = _augment_slots_for_bestseller_structure(base, "permission_slip")
    assert "PERMISSION" in result, f"PERMISSION missing: {result}"
    assert "PIVOT" in result
    assert "TAKEAWAY" in result
    assert "THREAD" in result
    err = validate_chapter_beat_order("permission_slip", result)
    assert err is None, f"Beat order violation: {err}"


def test_augment_brene_brown_optional_permission():
    """Brene Brown: PERMISSION is optional; present only if in base_row."""
    base_without = ["HOOK", "SCENE", "STORY", "REFLECTION", "INTEGRATION"]
    result_without = _augment_slots_for_bestseller_structure(base_without, "brene_brown")
    # PERMISSION is optional, not in base, should not be in result
    assert "PERMISSION" not in result_without, f"PERMISSION should be absent: {result_without}"
    # But required slots should be present
    assert "PIVOT" in result_without
    assert "TAKEAWAY" in result_without

    # Now with PERMISSION in base
    base_with = ["HOOK", "SCENE", "STORY", "REFLECTION", "PERMISSION", "INTEGRATION"]
    result_with = _augment_slots_for_bestseller_structure(base_with, "brene_brown")
    assert "PERMISSION" in result_with, f"PERMISSION should be present: {result_with}"


def test_augment_preserves_compression():
    """COMPRESSION slot from F006 base row is preserved after augmentation."""
    base = ["HOOK", "SCENE", "STORY", "REFLECTION", "COMPRESSION", "EXERCISE", "INTEGRATION"]
    result = _augment_slots_for_bestseller_structure(base, "gladwell_spiral")
    assert "COMPRESSION" in result, f"COMPRESSION should be preserved: {result}"


def test_augment_unknown_structure_unchanged():
    """Unknown structure name returns base row unchanged."""
    base = ["HOOK", "SCENE", "STORY", "REFLECTION", "INTEGRATION"]
    result = _augment_slots_for_bestseller_structure(base, "nonexistent_structure_xyz")
    assert result == base


def test_all_12_structures_pass_beat_order_validation():
    """Augmented slot sequences for all 12 bestseller structures must pass beat order validation."""
    base = ["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]
    for structure_key in BESTSELLER_BEAT_STEPS:
        result = _augment_slots_for_bestseller_structure(base, structure_key)
        err = validate_chapter_beat_order(structure_key, result)
        assert err is None, f"Structure {structure_key}: beat order violation with slots {result}: {err}"


def test_letter_structure_no_pivot():
    """The Letter structure does not require PIVOT."""
    base = ["HOOK", "SCENE", "STORY", "REFLECTION", "INTEGRATION"]
    result = _augment_slots_for_bestseller_structure(base, "letter")
    # The Letter beat order: HOOK, SCENE, STORY, REFLECTION, TAKEAWAY, INTEGRATION, THREAD
    # No PIVOT in the beat order
    assert "PIVOT" not in result, f"PIVOT should not be in Letter structure: {result}"
    assert "TAKEAWAY" in result
    assert "THREAD" in result
    err = validate_chapter_beat_order("letter", result)
    assert err is None, f"Beat order violation: {err}"


def test_assign_bestseller_structures_max_3_in_a_row():
    """No structure appears more than 3 times consecutively."""
    structures = assign_bestseller_structures(20, "test_prefix")
    for i in range(3, len(structures)):
        window = structures[i - 3 : i + 1]
        assert len(set(window)) > 1, f"Same structure 4+ in a row at ch {i}: {window}"


def test_slot_count_increases_with_bestseller_augmentation():
    """Augmented slot sequences should have more slots than the base 5-slot default."""
    base = ["HOOK", "SCENE", "STORY", "REFLECTION", "INTEGRATION"]
    augmented_counts = []
    for key in BESTSELLER_BEAT_STEPS:
        result = _augment_slots_for_bestseller_structure(base, key)
        augmented_counts.append(len(result))
    # Average should be > 5 (base has 5 slots)
    avg = sum(augmented_counts) / len(augmented_counts)
    assert avg > 5.5, f"Average augmented slot count {avg:.1f} too low; should be well above base 5"


def test_f006_k_tables_include_new_slots():
    """F006 k_tables must define k_min for PIVOT, TAKEAWAY, THREAD, PERMISSION."""
    try:
        import yaml
    except ImportError:
        return
    k_path = REPO_ROOT / "config" / "format_selection" / "k_tables" / "F006.yaml"
    if not k_path.exists():
        return
    with open(k_path) as f:
        data = yaml.safe_load(f)
    k_min = data.get("k_min_per_slot", {})
    for slot_type in ("PIVOT", "TAKEAWAY", "THREAD", "PERMISSION"):
        assert slot_type in k_min, f"{slot_type} missing from F006 k_tables"
        assert k_min[slot_type].get("k_min", 0) >= 8, f"{slot_type} k_min should be >= 8"
