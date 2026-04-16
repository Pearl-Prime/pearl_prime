"""Tests for generate_book_plan() — ACT-011 / BSG-011."""
from __future__ import annotations

import pytest

from phoenix_v4.planning.book_structure_plan import generate_book_plan, validate_book_arc
from phoenix_v4.planning.chapter_plan import PlanValidationError


def test_generate_plan_passes_validation_for_all_formats():
    formats = [
        "pocket_guide",
        "standard_book",
        "extended_book_2h",
        "micro_book_15",
        "protocol_library",
    ]
    for fmt in formats:
        plan = generate_book_plan("anxiety", "gen_z_professionals", fmt, "somatic_first")
        # validate_book_arc raises on failure; if no exception, validation passed
        validate_book_arc(plan)
        print(f"{fmt}: {plan.chapter_count} chapters OK")


def test_generated_plan_chapter_count_matches_format():
    plan = generate_book_plan("anxiety", "gen_z_professionals", "pocket_guide", "somatic_first")
    assert 5 <= plan.chapter_count <= 8, (
        f"pocket_guide should have 5-8 chapters, got {plan.chapter_count}"
    )


def test_generated_plan_has_thesis_for_all_chapters():
    plan = generate_book_plan("burnout", "corporate_leaders", "standard_book", "somatic_first")
    for ch in plan.chapters:
        thesis = getattr(ch, "chapter_thesis", None) or getattr(ch, "thesis", None) or ""
        assert thesis.strip(), f"Chapter {getattr(ch, 'number', ch.chapter_number)} missing thesis"


def test_generated_plan_has_bestseller_structures():
    plan = generate_book_plan("anxiety", "gen_z_professionals", "standard_book", "somatic_first")
    for ch in plan.chapters:
        struct = getattr(ch, "bestseller_structure", None) or ""
        assert struct, "Chapter missing bestseller_structure"


def test_generated_plan_plan_id_format():
    plan = generate_book_plan("stress", "millennials", "micro_book_15", "grief")
    assert plan.plan_id.startswith("generated_")
    assert "stress" in plan.plan_id
    assert "millennials" in plan.plan_id
    assert "micro_book_15" in plan.plan_id


def test_generated_plan_no_three_consecutive_structures():
    plan = generate_book_plan("anxiety", "gen_z_professionals", "extended_book_2h", "somatic_first")
    structures = [ch.bestseller_structure for ch in plan.chapters]
    for i in range(2, len(structures)):
        window = structures[i - 2 : i + 1]
        assert len(set(window)) > 1, (
            f"3-in-a-row bestseller_structure at chapters {i-2}..{i}: {window}"
        )


def test_generated_plan_final_chapter_has_ending_contract():
    plan = generate_book_plan("anxiety", "gen_z_professionals", "standard_book", "somatic_first")
    final = plan.chapters[-1]
    assert final.ending_contract, "Final chapter must have ending_contract"


def test_generated_plan_band_arc_valid():
    """Final band must be less than the peak band."""
    plan = generate_book_plan("anxiety", "gen_z_professionals", "standard_book", "somatic_first")
    bands = [ch.band for ch in plan.chapters]
    peak = max(bands)
    assert bands[-1] < peak, (
        f"Final chapter band {bands[-1]} must be < peak {peak}"
    )


def test_generated_plan_deep_book_6h():
    """Deep book with 20 chapters should still pass validation."""
    plan = generate_book_plan("trauma", "therapists", "deep_book_6h", "grief")
    validate_book_arc(plan)
    assert plan.chapter_count == 20


def test_generated_plan_custom_chapter_count():
    plan = generate_book_plan(
        "relationships",
        "young_adults",
        "standard_book",
        "shame",
        chapter_count=7,
    )
    assert plan.chapter_count == 7
    validate_book_arc(plan)
