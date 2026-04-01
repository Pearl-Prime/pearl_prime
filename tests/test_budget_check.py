"""Tests for phoenix_v4.planning.budget_check — pre-render word-budget gate."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.planning.budget_check import check_word_budget, BudgetResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_plan(chapter_slot_sequence: list[list[str]], atom_ids: list[str]) -> dict:
    return {
        "chapter_slot_sequence": chapter_slot_sequence,
        "atom_ids": atom_ids,
    }


def _make_prose_map(atom_ids: list[str], words_per_atom: int) -> dict[str, str]:
    """Generate a prose map with *words_per_atom* words per atom."""
    return {aid: " ".join(["word"] * words_per_atom) for aid in atom_ids}


def _format_config(word_min: int, word_max: int) -> dict:
    return {"word_range": [word_min, word_max]}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSufficientBudget:
    """Atom pool meets the word target."""

    def test_sufficient_returns_pass(self):
        slots = [["HOOK", "SCENE", "STORY"], ["HOOK", "SCENE", "STORY"]]
        aids = ["a1", "a2", "a3", "a4", "a5", "a6"]
        # 6 atoms * 200 words = 1200; target 1000-1500
        prose = _make_prose_map(aids, 200)
        fmt = _format_config(1000, 1500)

        result = check_word_budget(_make_plan(slots, aids), fmt, prose_map=prose)

        assert isinstance(result, BudgetResult)
        assert result.sufficient is True
        assert result.estimated_words == 1200
        assert result.target_min == 1000
        assert result.target_max == 1500
        assert "PASS" in result.message

    def test_per_chapter_estimates_sum(self):
        slots = [["HOOK", "SCENE"], ["HOOK", "SCENE"]]
        aids = ["a1", "a2", "a3", "a4"]
        prose = _make_prose_map(aids, 100)
        fmt = _format_config(200, 600)

        result = check_word_budget(_make_plan(slots, aids), fmt, prose_map=prose)

        ch_total = sum(c.estimated_words for c in result.per_chapter_estimates)
        assert ch_total == result.estimated_words
        assert len(result.per_chapter_estimates) == 2


class TestInsufficientBudget:
    """Atom pool does NOT meet the word target."""

    def test_insufficient_returns_fail(self):
        slots = [["HOOK", "STORY"], ["HOOK", "STORY"]]
        aids = ["a1", "a2", "a3", "a4"]
        # 4 atoms * 50 words = 200; target 9000-11000
        prose = _make_prose_map(aids, 50)
        fmt = _format_config(9000, 11000)

        result = check_word_budget(_make_plan(slots, aids), fmt, prose_map=prose)

        assert result.sufficient is False
        assert result.estimated_words == 200
        assert "FAIL" in result.message
        assert "8800 words short" in result.message

    def test_shortfall_per_chapter_accurate(self):
        slots = [["HOOK", "STORY", "REFLECTION"], ["HOOK", "STORY", "REFLECTION"]]
        aids = ["a1", "a2", "a3", "a4", "a5", "a6"]
        # ch0: a1=10w, a2=10w, a3=10w = 30 words; target_min per ch = 500
        prose = {aid: " ".join(["w"] * 10) for aid in aids}
        fmt = _format_config(1000, 1500)

        result = check_word_budget(_make_plan(slots, aids), fmt, prose_map=prose)

        assert result.sufficient is False
        for ce in result.per_chapter_estimates:
            assert ce.target_min == 500  # 1000 / 2 chapters
            assert ce.shortfall == 500 - 30  # 470


class TestPerChapterBreakdown:
    """Per-chapter estimates are correct and independent."""

    def test_uneven_chapters(self):
        # Chapter 0 has 2 slots, chapter 1 has 1 slot
        slots = [["HOOK", "STORY"], ["HOOK"]]
        aids = ["a1", "a2", "a3"]
        prose = {"a1": "one two three", "a2": "four five six seven eight", "a3": "nine"}
        fmt = _format_config(6, 10)

        result = check_word_budget(_make_plan(slots, aids), fmt, prose_map=prose)

        assert len(result.per_chapter_estimates) == 2
        ch0 = result.per_chapter_estimates[0]
        ch1 = result.per_chapter_estimates[1]
        assert ch0.estimated_words == 3 + 5  # "one two three" + "four five six seven eight"
        assert ch1.estimated_words == 1  # "nine"
        assert ch0.slot_count == 2
        assert ch1.slot_count == 1

    def test_missing_prose_treated_as_zero(self):
        slots = [["HOOK", "STORY"]]
        aids = ["a1", "a2"]
        prose = {"a1": "hello world"}  # a2 missing
        fmt = _format_config(10, 20)

        result = check_word_budget(_make_plan(slots, aids), fmt, prose_map=prose)

        assert result.estimated_words == 2  # only "hello world"


class TestSkipBudgetCheck:
    """The --skip-budget-check flag should bypass the check entirely.

    This is tested at the pipeline integration level; here we verify that
    the budget_check module itself is purely callable — there is no
    internal skip mechanism, the flag is honoured by run_pipeline.py.
    """

    def test_budget_check_always_returns_result(self):
        """Even on empty plans the function returns a valid BudgetResult."""
        result = check_word_budget(
            _make_plan([], []),
            _format_config(9000, 11000),
            prose_map={},
        )
        assert isinstance(result, BudgetResult)
        assert result.estimated_words == 0
        assert result.sufficient is False


class TestEdgeCases:

    def test_zero_target_always_sufficient(self):
        result = check_word_budget(
            _make_plan([["HOOK"]], ["a1"]),
            _format_config(0, 0),
            prose_map={"a1": "word"},
        )
        assert result.sufficient is True

    def test_empty_plan(self):
        result = check_word_budget(
            _make_plan([], []),
            _format_config(0, 0),
            prose_map={},
        )
        assert result.sufficient is True
        assert result.estimated_words == 0
        assert len(result.per_chapter_estimates) == 0
