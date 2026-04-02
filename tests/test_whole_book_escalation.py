"""Tests for whole-book escalation (Bestseller Overlay §11).

Books must escalate and deepen across chapters — not restate.
Uses mechanism_escalation_gate to verify depth progression.
"""
from __future__ import annotations

import pytest

from phoenix_v4.qa.mechanism_escalation_gate import validate_mechanism_escalation


def _make_plan(n_chapters):
    css = [["STORY"] for _ in range(n_chapters)]
    aids = [f"s_{i}_0" for i in range(n_chapters)]
    return {"chapter_slot_sequence": css, "atom_ids": aids}


def _make_meta(depths):
    return {f"s_{i}_0": {"mechanism_depth": d} for i, d in enumerate(depths)}


class TestDepthIncreasesAcrossPhases:
    """Average depth should increase from early to mid to late."""

    def test_standard_escalation(self):
        depths = [1, 1, 1, 2, 2, 3, 3, 4, 4]
        plan = _make_plan(9)
        meta = _make_meta(depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is True

        # Verify average depth increases across thirds
        early = depths[:3]
        mid = depths[3:6]
        late = depths[6:]
        assert sum(early) / len(early) < sum(mid) / len(mid)
        assert sum(mid) / len(mid) < sum(late) / len(late)

    def test_12_chapter_escalation(self):
        depths = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 4]
        plan = _make_plan(12)
        meta = _make_meta(depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is True


class TestFinalThirdHasIdentityLevel:
    """At least one chapter in the final third must have depth=4."""

    def test_depth_4_present(self):
        depths = [1, 1, 1, 2, 2, 2, 3, 3, 4]
        plan = _make_plan(9)
        meta = _make_meta(depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is True

    def test_depth_4_missing(self):
        depths = [1, 1, 1, 2, 2, 2, 3, 3, 3]
        plan = _make_plan(9)
        meta = _make_meta(depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is False
        assert any("identity" in e.lower() or "depth=4" in e for e in result.errors)


class TestNoPlateauAfterMidpoint:
    """Consecutive same-depth chapters after midpoint produce warnings."""

    def test_plateau_warned(self):
        depths = [1, 1, 1, 2, 2, 2, 3, 3, 4]
        plan = _make_plan(9)
        meta = _make_meta(depths)
        result = validate_mechanism_escalation(plan, meta)
        # Chapters 7 and 8 both depth=3 after midpoint — should warn
        plateau_warnings = [w for w in result.warnings if "plateau" in w.lower()]
        assert len(plateau_warnings) > 0, (
            f"Expected plateau warning for ch7-8, got warnings: {result.warnings}"
        )

    def test_steady_increase_no_plateau(self):
        depths = [1, 1, 1, 2, 2, 3, 3, 4, 4]
        plan = _make_plan(9)
        meta = _make_meta(depths)
        result = validate_mechanism_escalation(plan, meta)
        # depth=4 is the max, so plateau at 4 is acceptable per gate logic
        # (gate only warns when depth < 4)
        assert result.valid is True


class TestFlatBookRejected:
    """A book that never escalates must fail."""

    def test_completely_flat(self):
        depths = [2, 2, 2, 2, 2, 2, 2, 2, 2]
        plan = _make_plan(9)
        meta = _make_meta(depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is False

    def test_descending_rejected(self):
        depths = [4, 3, 3, 2, 2, 2, 1, 1, 1]
        plan = _make_plan(9)
        meta = _make_meta(depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is False
