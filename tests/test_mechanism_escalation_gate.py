"""Tests for mechanism escalation gate (Dev Spec §2.2).

Validates that mechanism_depth increases across the arc: early >= 1,
mid >= 2, late >= 3, final third has at least one depth=4.
"""
from __future__ import annotations

import pytest

from phoenix_v4.qa.mechanism_escalation_gate import validate_mechanism_escalation


def _make_plan(chapter_count: int, story_atoms_per_chapter: int = 1):
    """Build a minimal plan dict with chapter_slot_sequence and atom_ids."""
    css = [["STORY"] * story_atoms_per_chapter for _ in range(chapter_count)]
    atom_ids = [f"story_{ch}_{s}" for ch in range(chapter_count) for s in range(story_atoms_per_chapter)]
    return {"chapter_slot_sequence": css, "atom_ids": atom_ids}


def _make_metadata(depths: list[int], atoms_per_chapter: int = 1):
    """Build atom_metadata mapping atom IDs to mechanism_depth values."""
    meta = {}
    for ch, d in enumerate(depths):
        for s in range(atoms_per_chapter):
            meta[f"story_{ch}_{s}"] = {"mechanism_depth": d}
    return meta


class TestEscalatingBookPasses:
    """A properly escalating 9-chapter book passes the gate."""

    def test_valid_escalation(self):
        depths = [1, 1, 1, 2, 2, 2, 3, 3, 4]
        plan = _make_plan(9)
        meta = _make_metadata(depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is True, f"Expected valid, got errors: {result.errors}"

    def test_aggressive_escalation(self):
        depths = [2, 2, 2, 3, 3, 3, 4, 4, 4]
        plan = _make_plan(9)
        meta = _make_metadata(depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is True


class TestFlatBookFails:
    """A flat book (all depth=1) fails the gate."""

    def test_all_depth_one(self):
        depths = [1, 1, 1, 1, 1, 1, 1, 1, 1]
        plan = _make_plan(9)
        meta = _make_metadata(depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is False
        assert any("mechanism_depth" in e for e in result.errors)

    def test_all_depth_two(self):
        """depth=2 everywhere still fails late-stage (needs 3+) and identity (needs 4)."""
        depths = [2, 2, 2, 2, 2, 2, 2, 2, 2]
        plan = _make_plan(9)
        meta = _make_metadata(depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is False


class TestNoIdentityInFinalThirdFails:
    """Missing depth=4 in final third is an error."""

    def test_max_depth_three(self):
        depths = [1, 1, 1, 2, 2, 2, 3, 3, 3]
        plan = _make_plan(9)
        meta = _make_metadata(depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is False
        assert any("identity" in e.lower() or "depth=4" in e for e in result.errors)


class TestLateStageRegressionFails:
    """Depth decrease in late stage is an error."""

    def test_regression_detected(self):
        depths = [1, 1, 1, 2, 2, 3, 3, 4, 2]
        plan = _make_plan(9)
        meta = _make_metadata(depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is False
        assert any("regression" in e.lower() or "decreased" in e.lower() for e in result.errors)


class TestEmptyBookSkipped:
    """Zero-chapter book passes with a warning."""

    def test_no_chapters(self):
        plan = _make_plan(0)
        result = validate_mechanism_escalation(plan, {})
        assert result.valid is True
        assert len(result.warnings) > 0


class TestSmallBooks:
    """Edge case: very small books (3 chapters)."""

    def test_three_chapter_escalation(self):
        depths = [1, 2, 4]
        plan = _make_plan(3)
        meta = _make_metadata(depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is True

    def test_three_chapter_flat(self):
        depths = [1, 1, 1]
        plan = _make_plan(3)
        meta = _make_metadata(depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is False
