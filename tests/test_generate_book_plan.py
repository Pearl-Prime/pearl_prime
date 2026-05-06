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


# ---------------------------------------------------------------------------
# Compact runtime formats (PR-E follow-up to PR #856 + #858 smoke diagnosis)
# ---------------------------------------------------------------------------
# PR #856 declared compact_book_5ch_15min / 5ch_20min / 8ch_30min in
# config/format_selection/format_registry.yaml but did not register them in
# the auto-plan path. PR #858 smoke surfaced this as a 13-chapter render
# against an 8-chapter format declaration. These tests regression-guard the
# compact-format auto-plan wiring.
#
# Post-AUTO-PLAN-SSOT-01-AMENDMENT (2026-05-06) refactor: chapter_count is
# read from format_registry.yaml via get_format_chapter_count(); the prior
# FORMAT_CHAPTER_COUNTS dict is removed.

def test_compact_book_5ch_15min_chapter_count():
    """PR-E regression: compact_book_5ch_15min must auto-plan to exactly 5 chapters."""
    plan = generate_book_plan(
        "anxiety", "gen_z_professionals", "compact_book_5ch_15min", "somatic_first"
    )
    assert plan.chapter_count == 5, (
        f"compact_book_5ch_15min should auto-plan to 5 chapters, got {plan.chapter_count}"
    )
    validate_book_arc(plan)


def test_compact_book_5ch_20min_chapter_count():
    """PR-E regression: compact_book_5ch_20min must auto-plan to exactly 5 chapters."""
    plan = generate_book_plan(
        "anxiety", "gen_z_professionals", "compact_book_5ch_20min", "somatic_first"
    )
    assert plan.chapter_count == 5, (
        f"compact_book_5ch_20min should auto-plan to 5 chapters, got {plan.chapter_count}"
    )
    validate_book_arc(plan)


def test_compact_book_8ch_30min_chapter_count():
    """PR-E regression: compact_book_8ch_30min must auto-plan to exactly 8 chapters.

    This is the format that produced 13 chapters in PR #858's smoke run (under-cover
    of the auto-plan default fallback). Asserting 8 here closes that regression.
    """
    plan = generate_book_plan(
        "anxiety", "gen_z_professionals", "compact_book_8ch_30min", "somatic_first"
    )
    assert plan.chapter_count == 8, (
        f"compact_book_8ch_30min should auto-plan to 8 chapters, got {plan.chapter_count}"
    )
    validate_book_arc(plan)


def test_format_chapter_counts_compact_entries_present():
    """All three compact runtime formats must resolve via get_format_chapter_count.

    Post-AUTO-PLAN-SSOT-01-AMENDMENT: chapter_count is read from
    config/format_selection/format_registry.yaml via the registry-aware
    helper; FORMAT_CHAPTER_COUNTS dict no longer exists.
    """
    from phoenix_v4.planning.book_structure_plan import get_format_chapter_count

    expected = {
        "compact_book_5ch_15min": 5,
        "compact_book_5ch_20min": 5,
        "compact_book_8ch_30min": 8,
    }
    for fmt, expected_count in expected.items():
        actual = get_format_chapter_count(fmt)
        assert actual == expected_count, (
            f"get_format_chapter_count({fmt!r}) = {actual}, expected {expected_count}"
        )


def test_chapter_count_reads_from_registry_ssot():
    """Pin the SSoT contract: get_format_chapter_count reads from registry.

    Proves AUTO-PLAN-SSOT-01-AMENDMENT: editing format_registry.yaml's
    chapter_count_default flows through to the auto-plan path without
    touching book_structure_plan.py. The FORMAT_CHAPTER_COUNTS Python
    constant is genuinely gone, not just renamed.
    """
    import phoenix_v4.planning.book_structure_plan as bsp

    # No FORMAT_CHAPTER_COUNTS attribute on the module (constant removed).
    assert not hasattr(bsp, "FORMAT_CHAPTER_COUNTS"), (
        "FORMAT_CHAPTER_COUNTS should have been removed in the AUTO-PLAN-SSOT-01 refactor; "
        "the registry is now the single source of truth"
    )

    # Monkeypatch the registry loader to return a known dict; verify
    # get_format_chapter_count picks up the new value without code changes.
    bsp._load_format_registry.cache_clear()
    original_loader = bsp._load_format_registry
    try:
        bsp._load_format_registry = lambda: {
            "runtime_formats": {
                "synthetic_test_format": {"chapter_count_default": 42}
            }
        }
        assert bsp.get_format_chapter_count("synthetic_test_format") == 42, (
            "registry-driven lookup did not return the patched value; SSoT broken"
        )
    finally:
        bsp._load_format_registry = original_loader
        bsp._load_format_registry.cache_clear()
