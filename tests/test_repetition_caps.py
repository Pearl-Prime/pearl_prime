"""Tests for repetition caps (Bestseller Overlay §9).

Verifies reframe diversity ceiling and bestseller structure run cap.
"""
from __future__ import annotations

import pytest

from phoenix_v4.qa.validate_reframe_diversity import (
    MAX_SAME_REFRAME_LINE_PER_BOOK,
    validate_reframe_diversity,
)
from phoenix_v4.planning.chapter_planner import (
    BESTSELLER_STRUCTURES,
    MAX_BESTSELLER_RUN,
    assign_bestseller_structures,
)


class TestReframeDiversityCeiling:
    """No single reframe line may repeat more than MAX times per book."""

    def test_above_ceiling_fails(self):
        repeated_text = "This is the moment everything changes."
        plan = {
            "reframe_injections": [
                {"text": repeated_text} for _ in range(MAX_SAME_REFRAME_LINE_PER_BOOK + 1)
            ]
        }
        result = validate_reframe_diversity(plan)
        assert result.valid is False
        assert any("repeated" in e.lower() or "diversity" in e.lower() for e in result.errors)

    def test_at_ceiling_passes(self):
        repeated_text = "This is the moment everything changes."
        plan = {
            "reframe_injections": [
                {"text": repeated_text} for _ in range(MAX_SAME_REFRAME_LINE_PER_BOOK)
            ]
        }
        result = validate_reframe_diversity(plan)
        assert result.valid is True

    def test_below_ceiling_passes(self):
        plan = {
            "reframe_injections": [
                {"text": "Line one."},
                {"text": "Line two."},
                {"text": "Line one."},
            ]
        }
        result = validate_reframe_diversity(plan)
        assert result.valid is True

    def test_empty_injections_passes(self):
        result = validate_reframe_diversity({"reframe_injections": []})
        assert result.valid is True

    def test_no_injections_key_passes(self):
        result = validate_reframe_diversity({})
        assert result.valid is True


class TestBestsellerStructureRunCap:
    """No structure may appear more than MAX_BESTSELLER_RUN (3) in a row."""

    def test_no_more_than_3_in_a_row_20_chapters(self):
        structures = assign_bestseller_structures(20, "test_seed_alpha")
        for i in range(len(structures) - MAX_BESTSELLER_RUN):
            window = structures[i : i + MAX_BESTSELLER_RUN + 1]
            assert len(set(window)) > 1, (
                f"Structure '{window[0]}' repeated {MAX_BESTSELLER_RUN + 1} times "
                f"starting at chapter {i + 1}"
            )

    def test_no_more_than_3_in_a_row_50_chapters(self):
        structures = assign_bestseller_structures(50, "test_seed_beta")
        for i in range(len(structures) - MAX_BESTSELLER_RUN):
            window = structures[i : i + MAX_BESTSELLER_RUN + 1]
            assert len(set(window)) > 1

    def test_all_12_structures_represented_in_large_book(self):
        structures = assign_bestseller_structures(100, "test_seed_gamma")
        used = set(structures)
        # With 100 chapters, all 12 structures should appear
        assert len(used) == len(BESTSELLER_STRUCTURES), (
            f"Missing structures: {set(BESTSELLER_STRUCTURES) - used}"
        )

    def test_correct_count(self):
        n = 15
        structures = assign_bestseller_structures(n, "test_seed_delta")
        assert len(structures) == n


class TestBestsellerDeterminism:
    """Same seed produces identical structure assignments."""

    def test_deterministic(self):
        a = assign_bestseller_structures(20, "determinism_test")
        b = assign_bestseller_structures(20, "determinism_test")
        assert a == b

    def test_different_seeds_differ(self):
        a = assign_bestseller_structures(20, "seed_one")
        b = assign_bestseller_structures(20, "seed_two")
        # With 20 chapters and different seeds, output should differ
        assert a != b
