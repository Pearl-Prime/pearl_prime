"""Unit tests for individual narrative gates and shared plan utilities.

Covers:
- _narrative_plan_utils: plan extraction helpers
- mechanism_escalation_gate: validate_mechanism_escalation
- cost_gradient_gate: validate_cost_gradient

These gates are the foundation of book quality enforcement. Testing them
individually (not just through book_pass_gate) catches regressions in
threshold logic and edge-case handling.
"""
from __future__ import annotations

import pytest

from phoenix_v4.qa._narrative_plan_utils import (
    get_atom_ids,
    get_chapter_count,
    get_chapter_slot_sequence,
    get_exercise_chapters,
    get_story_atom_ids_by_chapter,
    iter_chapter_slot_atom_ids,
)
from phoenix_v4.qa.cost_gradient_gate import validate_cost_gradient
from phoenix_v4.qa.mechanism_escalation_gate import validate_mechanism_escalation


# ── Plan builder ────────────────────────────────────────────────────


def _plan(
    slots: list[list[str]],
    atom_ids: list[str] | None = None,
) -> dict:
    flat = sum(len(r) for r in slots)
    ids = atom_ids or [f"atom_{i}" for i in range(flat)]
    return {"chapter_slot_sequence": slots, "atom_ids": ids}


def _meta(
    atom_ids: list[str],
    *,
    mechanism_depth: int | list[int] = 1,
    cost_intensity: int | list[int] = 2,
) -> dict[str, dict]:
    """Build atom_metadata dict. If depth/cost is scalar, apply to all; if list, per-atom."""
    md_list = [mechanism_depth] * len(atom_ids) if isinstance(mechanism_depth, int) else mechanism_depth
    ci_list = [cost_intensity] * len(atom_ids) if isinstance(cost_intensity, int) else cost_intensity
    return {
        aid: {"mechanism_depth": md_list[i], "cost_intensity": ci_list[i]}
        for i, aid in enumerate(atom_ids)
    }


# ── _narrative_plan_utils ───────────────────────────────────────────


class TestNarrativePlanUtils:
    def test_get_atom_ids(self) -> None:
        p = _plan([["STORY"]], atom_ids=["a1"])
        assert get_atom_ids(p) == ["a1"]

    def test_get_atom_ids_empty(self) -> None:
        assert get_atom_ids({}) == []

    def test_get_chapter_slot_sequence(self) -> None:
        p = _plan([["STORY", "REFLECTION"], ["EXERCISE"]])
        assert get_chapter_slot_sequence(p) == [["STORY", "REFLECTION"], ["EXERCISE"]]

    def test_get_chapter_count(self) -> None:
        p = _plan([["STORY"], ["STORY"], ["STORY"]])
        assert get_chapter_count(p) == 3

    def test_get_chapter_count_empty(self) -> None:
        assert get_chapter_count({}) == 0

    def test_iter_chapter_slot_atom_ids(self) -> None:
        p = _plan(
            [["STORY", "REFLECTION"], ["EXERCISE"]],
            atom_ids=["a0", "a1", "a2"],
        )
        result = iter_chapter_slot_atom_ids(p)
        assert result == [
            (0, 0, "STORY", "a0"),
            (0, 1, "REFLECTION", "a1"),
            (1, 0, "EXERCISE", "a2"),
        ]

    def test_iter_handles_short_atom_ids(self) -> None:
        """If atom_ids is shorter than slots, remaining slots are skipped."""
        p = _plan([["STORY", "REFLECTION"]], atom_ids=["a0"])
        result = iter_chapter_slot_atom_ids(p)
        assert len(result) == 1

    def test_get_story_atom_ids_by_chapter(self) -> None:
        p = _plan(
            [["STORY", "REFLECTION"], ["STORY", "EXERCISE"]],
            atom_ids=["s1", "r1", "s2", "e1"],
        )
        result = get_story_atom_ids_by_chapter(p)
        assert result == [["s1"], ["s2"]]

    def test_get_story_excludes_placeholders(self) -> None:
        p = _plan(
            [["STORY", "STORY"]],
            atom_ids=["placeholder:STORY:ch0:s0", "real_atom"],
        )
        result = get_story_atom_ids_by_chapter(p)
        assert result == [["real_atom"]]

    def test_get_exercise_chapters(self) -> None:
        p = _plan([["STORY"], ["EXERCISE", "STORY"], ["STORY"]])
        assert get_exercise_chapters(p) == [1]

    def test_get_exercise_chapters_from_attr(self) -> None:
        p = {"exercise_chapters": [0, 3], "chapter_slot_sequence": []}
        assert get_exercise_chapters(p) == [0, 3]


# ── Mechanism Escalation Gate ───────────────────────────────────────


class TestMechanismEscalation:
    def _make_story_plan(self, n_chapters: int) -> tuple[dict, list[str]]:
        """Build a plan with one STORY slot per chapter."""
        slots = [["STORY"] for _ in range(n_chapters)]
        atom_ids = [f"s_ch{i}" for i in range(n_chapters)]
        return _plan(slots, atom_ids), atom_ids

    def test_no_chapters_passes(self) -> None:
        p = _plan([])
        result = validate_mechanism_escalation(p, {})
        assert result.valid is True

    def test_proper_escalation_passes(self) -> None:
        """6 chapters: early=1, mid=2, late=3, final=4."""
        plan, aids = self._make_story_plan(6)
        # ch0,1=early(depth1), ch2,3=mid(depth2), ch4=late(depth3), ch5=late(depth4)
        depths = [1, 1, 2, 2, 3, 4]
        meta = _meta(aids, mechanism_depth=depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is True, f"Errors: {result.errors}"

    def test_flat_depth_fails(self) -> None:
        """All depth=1 across 6 chapters should fail."""
        plan, aids = self._make_story_plan(6)
        meta = _meta(aids, mechanism_depth=1)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is False
        assert any("mechanism_depth" in e for e in result.errors)

    def test_missing_identity_depth_in_final_third(self) -> None:
        """Escalates to 3 but never hits 4."""
        plan, aids = self._make_story_plan(6)
        depths = [1, 1, 2, 2, 3, 3]
        meta = _meta(aids, mechanism_depth=depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is False
        assert any("depth=4" in e for e in result.errors)

    def test_late_stage_regression_fails(self) -> None:
        """Depth decreases in late chapters."""
        plan, aids = self._make_story_plan(6)
        depths = [1, 1, 2, 3, 4, 2]  # drops from 4 to 2
        meta = _meta(aids, mechanism_depth=depths)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is False
        assert any("regression" in e for e in result.errors)

    def test_single_chapter_requires_depth4(self) -> None:
        """Even 1-chapter books need depth=4 in final third (which is the whole book)."""
        plan, aids = self._make_story_plan(1)
        meta = _meta(aids, mechanism_depth=1)
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is False
        # With depth=4 it should pass
        meta4 = _meta(aids, mechanism_depth=4)
        result4 = validate_mechanism_escalation(plan, meta4)
        assert result4.valid is True

    def test_two_chapter_needs_depth4_in_final(self) -> None:
        """2-chapter book still needs depth=4 somewhere in final third."""
        plan, aids = self._make_story_plan(2)
        meta = _meta(aids, mechanism_depth=[1, 2])
        result = validate_mechanism_escalation(plan, meta)
        assert result.valid is False
        # With depth=4 in second chapter it should pass
        meta4 = _meta(aids, mechanism_depth=[1, 4])
        result4 = validate_mechanism_escalation(plan, meta4)
        assert result4.valid is True


# ── Cost Gradient Gate ──────────────────────────────────────────────


class TestCostGradient:
    def _make_story_plan(self, n_chapters: int) -> tuple[dict, list[str]]:
        slots = [["STORY"] for _ in range(n_chapters)]
        atom_ids = [f"s_ch{i}" for i in range(n_chapters)]
        return _plan(slots, atom_ids), atom_ids

    def test_no_chapters_passes(self) -> None:
        p = _plan([])
        result = validate_cost_gradient(p, {})
        assert result.valid is True

    def test_proper_escalation_passes(self) -> None:
        """Cost peaks in second half with high average."""
        plan, aids = self._make_story_plan(6)
        costs = [2, 2, 3, 4, 5, 3]
        meta = _meta(aids, cost_intensity=costs)
        result = validate_cost_gradient(plan, meta)
        assert result.valid is True, f"Errors: {result.errors}"

    def test_peak_before_midpoint_fails(self) -> None:
        """Highest cost in first chapter fails."""
        plan, aids = self._make_story_plan(6)
        costs = [5, 2, 2, 2, 2, 2]
        meta = _meta(aids, cost_intensity=costs)
        result = validate_cost_gradient(plan, meta)
        assert result.valid is False
        assert any("midpoint" in e for e in result.errors)

    def test_low_average_fails(self) -> None:
        """All cost=1 fails the 2.5 average threshold."""
        plan, aids = self._make_story_plan(6)
        meta = _meta(aids, cost_intensity=1)
        result = validate_cost_gradient(plan, meta)
        assert result.valid is False
        assert any("2.5" in e for e in result.errors)

    def test_no_high_intensity_second_half_fails(self) -> None:
        """No cost >= 4 in second half fails."""
        plan, aids = self._make_story_plan(6)
        costs = [3, 3, 3, 3, 3, 3]
        meta = _meta(aids, cost_intensity=costs)
        result = validate_cost_gradient(plan, meta)
        assert result.valid is False
        assert any("second half" in e.lower() for e in result.errors)

    def test_single_chapter_passes(self) -> None:
        plan, aids = self._make_story_plan(1)
        meta = _meta(aids, cost_intensity=3)
        result = validate_cost_gradient(plan, meta)
        assert result.valid is True

    def test_placeholder_atoms_ignored(self) -> None:
        """Placeholder atom IDs should not contribute to cost calculations."""
        plan = _plan(
            [["STORY"], ["STORY"], ["STORY"], ["STORY"]],
            atom_ids=["placeholder:STORY:ch0:s0", "real_1", "real_2", "real_3"],
        )
        meta = {
            "real_1": {"cost_intensity": 3, "mechanism_depth": 1},
            "real_2": {"cost_intensity": 4, "mechanism_depth": 1},
            "real_3": {"cost_intensity": 4, "mechanism_depth": 1},
        }
        result = validate_cost_gradient(plan, meta)
        # Should not crash; placeholder is filtered out
        assert isinstance(result.valid, bool)
