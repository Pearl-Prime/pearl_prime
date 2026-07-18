"""Tests for DupEval: structural duplication detection for pre-publish gate.

Covers: fingerprinting, similarity functions, CTSS/TSS/MSS scoring,
run_dupe_eval verdicts, wave density checks, and edge cases.
"""
from __future__ import annotations

import pytest

from phoenix_v4.qa.dupe_eval import (
    band_seq_from_plan,
    build_fingerprint,
    check_wave_density,
    ctss,
    exercise_chapters_from_plan,
    final_dup_score,
    jaccard,
    mss,
    run_dupe_eval,
    sim_band,
    slot_signature,
    tss,
)


# ── Helper builders ─────────────────────────────────────────────────


def _plan(
    *,
    arc_id: str = "arc_a",
    teacher_id: str = "",
    bands: list[int] | None = None,
    slots: list[list[str]] | None = None,
    atom_ids: list[str] | None = None,
    format_id: str = "F006",
    plan_hash: str = "h1",
    **extra: object,
) -> dict:
    bands = bands or [2, 3, 4, 3, 2]
    slots = slots or [
        ["HOOK", "STORY", "REFLECTION"],
        ["STORY", "EXERCISE", "INTEGRATION"],
        ["STORY", "REFLECTION", "INTEGRATION"],
        ["STORY", "REFLECTION", "EXERCISE"],
        ["STORY", "REFLECTION", "INTEGRATION"],
    ]
    flat_count = sum(len(r) for r in slots)
    atom_ids = atom_ids or [f"atom_{i}" for i in range(flat_count)]
    p: dict = {
        "arc_id": arc_id,
        "teacher_id": teacher_id,
        "dominant_band_sequence": bands,
        "chapter_slot_sequence": slots,
        "atom_ids": atom_ids,
        "format_id": format_id,
        "plan_hash": plan_hash,
    }
    p.update(extra)
    return p


def _fingerprint(**kwargs: object) -> dict:
    return build_fingerprint(_plan(**kwargs))


# ── band_seq_from_plan ──────────────────────────────────────────────


class TestBandSeq:
    def test_from_dominant_band_sequence(self) -> None:
        p = _plan(bands=[1, 2, 3])
        assert band_seq_from_plan(p) == "1-2-3"

    def test_none_bands_become_3(self) -> None:
        p: dict = {"dominant_band_sequence": [1, None, 3]}
        assert band_seq_from_plan(p) == "1-3-3"

    def test_empty_plan_returns_empty(self) -> None:
        assert band_seq_from_plan({}) == ""

    def test_priority_emotional_temperature_over_dominant(self) -> None:
        p: dict = {
            "emotional_temperature_sequence": [5, 4, 3],
            "dominant_band_sequence": [1, 1, 1],
        }
        assert band_seq_from_plan(p) == "5-4-3"


# ── exercise_chapters_from_plan ─────────────────────────────────────


class TestExerciseChapters:
    def test_from_chapter_slot_sequence(self) -> None:
        p = _plan(
            slots=[
                ["STORY", "REFLECTION"],
                ["STORY", "EXERCISE"],
                ["STORY", "REFLECTION"],
            ]
        )
        assert exercise_chapters_from_plan(p) == [2]

    def test_no_exercises(self) -> None:
        p = _plan(slots=[["STORY"], ["STORY"]])
        assert exercise_chapters_from_plan(p) == []


# ── slot_signature ──────────────────────────────────────────────────


class TestSlotSignature:
    def test_deterministic(self) -> None:
        p = _plan()
        assert slot_signature(p) == slot_signature(p)

    def test_different_layout_different_sig(self) -> None:
        p1 = _plan(slots=[["STORY", "REFLECTION"]])
        p2 = _plan(slots=[["REFLECTION", "STORY"]])
        assert slot_signature(p1) != slot_signature(p2)


# ── Similarity functions ────────────────────────────────────────────


class TestSimBand:
    def test_identical(self) -> None:
        assert sim_band("1-2-3", "1-2-3") == 1.0

    def test_completely_different(self) -> None:
        assert sim_band("1-1-1", "5-5-5") == 0.0

    def test_partial_match(self) -> None:
        assert sim_band("1-2-3", "1-2-5") == pytest.approx(2 / 3)

    def test_empty_returns_zero(self) -> None:
        assert sim_band("", "") == 0.0

    def test_different_lengths_uses_shorter(self) -> None:
        assert sim_band("1-2", "1-2-3") == 1.0


class TestJaccard:
    def test_identical(self) -> None:
        assert jaccard([1, 2, 3], [1, 2, 3]) == 1.0

    def test_disjoint(self) -> None:
        assert jaccard([1, 2], [3, 4]) == 0.0

    def test_both_empty(self) -> None:
        assert jaccard([], []) == 1.0

    def test_one_empty(self) -> None:
        assert jaccard([1], []) == 0.0


# ── CTSS / TSS / MSS ───────────────────────────────────────────────


class TestCTSS:
    def test_identical_plans_score_one(self) -> None:
        fp = _fingerprint()
        assert ctss(fp, fp) == pytest.approx(1.0)

    def test_completely_different_plans(self) -> None:
        fp1 = _fingerprint(arc_id="arc_a", bands=[1, 1], format_id="F006")
        fp2 = _fingerprint(arc_id="arc_b", bands=[5, 5], format_id="F010")
        score = ctss(fp1, fp2)
        assert score < 0.5


class TestTSS:
    def test_same_teacher_identical(self) -> None:
        fp = _fingerprint(teacher_id="teacher_x")
        fp["intro_style_ids"] = ["s1"]
        fp["outro_style_ids"] = ["o1"]
        fp["core_teachings_used"] = ["core:a"]
        assert tss(fp, fp) == pytest.approx(1.0)

    def test_different_teachers_zero(self) -> None:
        fp1 = _fingerprint(teacher_id="t1")
        fp2 = _fingerprint(teacher_id="t2")
        assert tss(fp1, fp2) == 0.0


class TestMSS:
    def test_identical_metadata(self) -> None:
        fp = _fingerprint()
        fp["title_style_id"] = "ts1"
        fp["subtitle_style_id"] = "ss1"
        assert mss(fp, fp) == 1.0

    def test_no_metadata_keys(self) -> None:
        fp1 = _fingerprint()
        fp2 = _fingerprint()
        assert mss(fp1, fp2) == 0.0


# ── final_dup_score ─────────────────────────────────────────────────


class TestFinalDupScore:
    def test_non_teacher_mode_uses_ctss_only(self) -> None:
        fp = _fingerprint()
        score = final_dup_score(fp, fp, teacher_mode=False)
        assert score == pytest.approx(ctss(fp, fp))

    def test_teacher_mode_blends_all_three(self) -> None:
        fp = _fingerprint(teacher_id="t1")
        fp["intro_style_ids"] = ["s1"]
        fp["outro_style_ids"] = ["o1"]
        fp["core_teachings_used"] = ["core:a"]
        fp["title_style_id"] = "ts1"
        score = final_dup_score(fp, fp, teacher_mode=True)
        # With identical fingerprints, should be 1.0
        assert score == pytest.approx(1.0)


# ── run_dupe_eval ───────────────────────────────────────────────────


class TestRunDupeEval:
    def test_empty_index_passes(self) -> None:
        verdict, score, row = run_dupe_eval(_plan(), index=[])
        assert verdict == "pass"
        assert score == 0.0
        assert row is None

    def test_identical_plan_blocks(self) -> None:
        p = _plan(teacher_id="t1", arc_id="arc_a")
        fp = build_fingerprint(p)
        verdict, score, _ = run_dupe_eval(p, index=[fp], teacher_mode=False)
        assert verdict == "block"
        assert score >= 0.75

    def test_different_plan_passes(self) -> None:
        p1 = _plan(arc_id="arc_a", bands=[1, 2, 3], format_id="F006")
        p2 = _plan(arc_id="arc_b", bands=[5, 4, 3], format_id="F010")
        fp2 = build_fingerprint(p2)
        verdict, score, _ = run_dupe_eval(p1, index=[fp2])
        assert verdict == "pass"

    def test_strat_rule_blocks_same_teacher_arc_band(self) -> None:
        p = _plan(teacher_id="t1", arc_id="arc_a", bands=[2, 3, 4])
        fp = build_fingerprint(p)
        verdict, _, _ = run_dupe_eval(p, index=[fp], teacher_mode=True)
        assert verdict == "block"


# ── check_wave_density ──────────────────────────────────────────────


class TestWaveDensity:
    def test_empty_rows_pass(self) -> None:
        errors, warnings = check_wave_density([])
        assert errors == []

    def test_diverse_wave_passes(self) -> None:
        rows = [
            {"arc_id": f"arc_{i}", "band_seq": f"{i}-{i+1}", "slot_sig": f"sig_{i}", "exercise_chapters": [i]}
            for i in range(10)
        ]
        errors, _ = check_wave_density(rows)
        assert errors == []

    def test_arc_concentration_fails(self) -> None:
        rows = [{"arc_id": "arc_same", "band_seq": f"{i}", "slot_sig": f"sig_{i}", "exercise_chapters": [i]} for i in range(10)]
        errors, _ = check_wave_density(rows)
        assert any("arc_id" in e for e in errors)

    def test_band_concentration_fails(self) -> None:
        rows = [{"arc_id": f"arc_{i}", "band_seq": "same", "slot_sig": f"sig_{i}", "exercise_chapters": [i]} for i in range(10)]
        errors, _ = check_wave_density(rows)
        assert any("band_seq" in e for e in errors)
