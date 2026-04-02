"""
BG-PR-02 / BG-PR-03 / BG-PR-04: dimension gate enforcement — selective block when
fail_mode is block; listen_experience runs only from dimension_gate_phase 3 onward.

No hybrid-module skip: dimension_gates is core EI v2.
"""
from __future__ import annotations

from phoenix_v4.quality.ei_v2.dimension_gates import gate_cohesion, gate_listen_experience, run_chapter_dimension_gates


def _passing_chapter_text() -> str:
    return (
        "That morning, Sarah opened her laptop at the kitchen table. "
        "Her jaw was tight. But then she noticed something. However, the catch was real. "
        "What comes next might surprise you. Her shoulders eased. Her breath slowed."
    )


def _listen_pass_chapter() -> str:
    return (
        "The morning light came through the kitchen window in a thin stripe.\n\n"
        "Sarah set her mug down and watched the steam rise. She counted three slow breaths "
        "before opening the laptop. Her shoulders eased when she named the fear.\n\n"
        "The room stayed quiet except for the fridge humming down the hall.\n\n"
        "She typed one honest sentence and paused. A short line can land harder than a long "
        "paragraph when the listener is tired and needs air.\n\n"
        "She saved the draft and stood to stretch. The day could wait while her jaw unclenched."
    )


def _listen_fail_wall_of_text() -> str:
    core = (
        "The organizational institutionalization demonstrates comprehensibility "
        "notwithstanding bureaucratic accountability for stakeholders everywhere today."
    )
    return (core + " ") * 18 + (
        " EXCEPTIONALEXCEPTIONAL bureaucratic ACCOUNTINGNUMBERS 1.2.3.4 here."
    )


def _listen_warn_borderline() -> str:
    return " ".join(
        [f"Sentence number {i} has exactly ten words for listener pacing today." for i in range(30)]
    )


class TestDimensionGateEnforcement:
    """Selective blocking per blocked_dimensions; telemetry phase marker."""

    def test_engagement_fail_blocks_when_dimension_blocked(self) -> None:
        text = "Too short."
        report = run_chapter_dimension_gates(
            text,
            [],
            chapter_index=0,
            dimension_gates_cfg={
                "enabled": True,
                "fail_mode": "block",
                "blocked_dimensions": ["engagement", "somatic_precision"],
                "dimension_gate_phase": 1,
            },
        )
        eng = next(g for g in report.gates if g.dimension == "engagement")
        assert eng.status == "FAIL"
        assert report.blocks_delivery is True
        d = report.to_dict()
        assert d["dimension_gate_phase"] == 1
        assert d["blocks_delivery"] is True
        assert d["fail_mode"] == "block"
        eg = next(x for x in d["gates"] if x["dimension"] == "engagement")
        assert eg["contributes_to_delivery_block"] is True
        assert eg["dimension_gate_phase"] == 1

    def test_engagement_fail_warn_only_when_not_in_blocked_dimensions(self) -> None:
        text = "Her shoulders were tight. Her breath quickened and her chest felt heavy."
        report = run_chapter_dimension_gates(
            text,
            [],
            chapter_index=0,
            dimension_gates_cfg={
                "enabled": True,
                "fail_mode": "block",
                "blocked_dimensions": ["somatic_precision"],
                "dimension_gate_phase": 1,
            },
        )
        eng = next(g for g in report.gates if g.dimension == "engagement")
        assert eng.status == "FAIL"
        som = next(g for g in report.gates if g.dimension == "somatic_precision")
        assert som.status == "PASS"
        assert report.blocks_delivery is False
        d = report.to_dict()
        eg = next(x for x in d["gates"] if x["dimension"] == "engagement")
        assert eg["contributes_to_delivery_block"] is False

    def test_missing_blocked_dimensions_never_blocks_backward_compat(self) -> None:
        text = "Too short."
        report = run_chapter_dimension_gates(
            text,
            [],
            chapter_index=0,
            dimension_gates_cfg={
                "enabled": True,
                "fail_mode": "block",
                "dimension_gate_phase": 1,
            },
        )
        assert report.blocks_delivery is False
        assert report.fail_mode == "block"
        assert report.blocked_dimensions == []

    def test_fail_mode_warn_never_blocks(self) -> None:
        text = "Too short."
        report = run_chapter_dimension_gates(
            text,
            [],
            chapter_index=0,
            dimension_gates_cfg={
                "enabled": True,
                "fail_mode": "warn",
                "blocked_dimensions": ["engagement", "somatic_precision"],
                "dimension_gate_phase": 1,
            },
        )
        assert report.blocks_delivery is False

    def test_passing_chapter_unchanged_no_block(self) -> None:
        text = _passing_chapter_text()
        report = run_chapter_dimension_gates(
            text,
            [],
            chapter_index=0,
            dimension_gates_cfg={
                "enabled": True,
                "fail_mode": "block",
                "blocked_dimensions": ["engagement", "somatic_precision"],
                "dimension_gate_phase": 1,
            },
        )
        assert report.blocks_delivery is False
        assert report.overall_status in ("PASS", "WARN")

    def test_somatic_fail_does_not_block_when_not_in_blocked_dimensions(self) -> None:
        text = (
            "Administrative concepts circulate without concrete reference points whatsoever. "
            "Policy frameworks determine outcomes systematically across every organizational layer. "
            "Theoretically speaking nothing concrete occurs in this paragraph deliberately so far."
        )
        report = run_chapter_dimension_gates(
            text,
            [],
            chapter_index=0,
            dimension_gates_cfg={
                "enabled": True,
                "fail_mode": "block",
                "blocked_dimensions": ["engagement"],
                "dimension_gate_phase": 1,
            },
        )
        som = next(g for g in report.gates if g.dimension == "somatic_precision")
        assert som.status in ("FAIL", "WARN")
        assert report.blocks_delivery is False

    def test_yaml_config_integration(self) -> None:
        from phoenix_v4.quality.ei_v2.config import invalidate_ei_v2_config_cache, load_ei_v2_config

        invalidate_ei_v2_config_cache()
        cfg = load_ei_v2_config()
        dg = cfg.get("dimension_gates") or {}
        assert "blocked_dimensions" in dg
        blocked_lower = [str(x).lower() for x in dg["blocked_dimensions"]]
        assert "engagement" in blocked_lower
        assert "uniqueness" in blocked_lower
        assert "cohesion" in blocked_lower
        assert "listen_experience" in blocked_lower
        assert dg.get("dimension_gate_phase") == 3
        report = run_chapter_dimension_gates(
            "Too short.",
            [],
            0,
            dimension_gates_cfg=dg,
        )
        assert report.dimension_gate_phase == 3
        assert isinstance(report.blocks_delivery, bool)
        assert any(g.dimension == "listen_experience" for g in report.gates)

    def test_gate_cohesion_related_prior_passes(self) -> None:
        prior = (
            "The quarterly planning retreat forced difficult conversations about leadership trust. "
            "Teams surfaced budgeting fears before lunch that Thursday afternoon together."
        )
        current = (
            "Building on that pattern we mapped earlier, the leadership team narrowed scope for Q3. "
            "They repeated trust exercises with smaller groups after that difficult morning session ended."
        )
        cohesion_cfg = {"min_cross_chapter_refs": 1, "pass_threshold": 0.40, "warn_threshold": 0.25}
        r = gate_cohesion(current, [prior], 1, cohesion_cfg)
        assert r.dimension == "cohesion"
        assert r.status == "PASS"

    def test_gate_cohesion_unrelated_prior_fails(self) -> None:
        prior = "Cats prefer warm windowsills during afternoon naps beside the garden wall outside."
        current = (
            "Tax regulations for fiscal year reporting require extensive documentation from all departments. "
            "Compliance officers review submissions carefully before approving revised corporate filings only. "
            "Organizations must retain detailed records throughout the statutory period without any exception stated."
        )
        cohesion_cfg = {"min_cross_chapter_refs": 1, "pass_threshold": 0.40, "warn_threshold": 0.25}
        r = gate_cohesion(current, [prior], 1, cohesion_cfg)
        assert r.dimension == "cohesion"
        assert r.status == "FAIL"

    def test_uniqueness_fail_blocks_when_dimension_blocked(self) -> None:
        long_dup = (
            "That morning, Sarah opened her laptop at the kitchen table with careful attention. "
            "Her jaw was tight and her shoulders carried the weight of unfinished decisions. "
            "But then she noticed something shifting in how she breathed before the meeting started. "
            "However, the catch was real and the pattern repeated whenever pressure arrived unexpectedly. "
            "What comes next might surprise anyone listening to this story unfold slowly across hours. "
            "Her shoulders eased slightly when she named the fear aloud in the quiet room alone."
        )
        report = run_chapter_dimension_gates(
            long_dup,
            [long_dup],
            chapter_index=1,
            dimension_gates_cfg={
                "enabled": True,
                "fail_mode": "block",
                "blocked_dimensions": ["uniqueness"],
                "dimension_gate_phase": 2,
            },
        )
        u = next(g for g in report.gates if g.dimension == "uniqueness")
        assert u.status == "FAIL"
        assert report.blocks_delivery is True
        d = report.to_dict()
        ug = next(x for x in d["gates"] if x["dimension"] == "uniqueness")
        assert ug["contributes_to_delivery_block"] is True

    def test_cohesion_fail_blocks_when_dimension_blocked(self) -> None:
        prior = "Cats prefer warm windowsills during afternoon naps beside the garden wall outside."
        current = (
            "Tax regulations for fiscal year reporting require extensive documentation from all departments. "
            "Her shoulders stayed tight while compliance officers reviewed worksheets and filings carefully. "
            "She noticed her breath shortening as the statutory deadline approached without mercy or relief. "
            "Auditors emphasize accuracy across schedules and evidence packets before final approval each year."
        )
        report = run_chapter_dimension_gates(
            current,
            [prior],
            chapter_index=1,
            dimension_gates_cfg={
                "enabled": True,
                "fail_mode": "block",
                "blocked_dimensions": ["cohesion"],
                "dimension_gate_phase": 2,
                "cohesion": {
                    "min_cross_chapter_refs": 1,
                    "pass_threshold": 0.40,
                    "warn_threshold": 0.25,
                },
            },
        )
        c = next(g for g in report.gates if g.dimension == "cohesion")
        assert c.status == "FAIL"
        assert report.blocks_delivery is True
        d = report.to_dict()
        cg = next(x for x in d["gates"] if x["dimension"] == "cohesion")
        assert cg["contributes_to_delivery_block"] is True


class TestListenExperienceDimensionGate:
    """BG-PR-04 listen_experience gate."""

    def test_listen_experience_pass_well_paced_chapter(self) -> None:
        text = _listen_pass_chapter()
        r = gate_listen_experience(
            text,
            {"pass_threshold": 0.5, "warn_threshold": 0.3},
        )
        assert r.dimension == "listen_experience"
        assert r.status == "PASS"
        assert r.score >= 0.5

    def test_listen_experience_fail_wall_of_text(self) -> None:
        text = _listen_fail_wall_of_text()
        r = gate_listen_experience(
            text,
            {"pass_threshold": 0.5, "warn_threshold": 0.3},
        )
        assert r.status == "FAIL"
        assert r.score < 0.3

    def test_listen_experience_warn_borderline(self) -> None:
        text = _listen_warn_borderline()
        r = gate_listen_experience(
            text,
            {"pass_threshold": 0.5, "warn_threshold": 0.3},
        )
        assert r.status == "WARN"
        assert 0.3 <= r.score < 0.5

    def test_phase_gating_listen_skipped_below_phase_3(self) -> None:
        text = _listen_pass_chapter()
        r2 = run_chapter_dimension_gates(
            text,
            [],
            0,
            dimension_gates_cfg={
                "fail_mode": "warn",
                "dimension_gate_phase": 2,
                "blocked_dimensions": [],
            },
        )
        names_2 = {g.dimension for g in r2.gates}
        assert "listen_experience" not in names_2

        r3 = run_chapter_dimension_gates(
            text,
            [],
            0,
            dimension_gates_cfg={
                "fail_mode": "warn",
                "dimension_gate_phase": 3,
                "blocked_dimensions": [],
            },
        )
        names_3 = {g.dimension for g in r3.gates}
        assert "listen_experience" in names_3

    def test_listen_fail_blocks_when_blocked_dimension_phase_3(self) -> None:
        text = _listen_fail_wall_of_text()
        report = run_chapter_dimension_gates(
            text,
            [],
            0,
            dimension_gates_cfg={
                "fail_mode": "block",
                "blocked_dimensions": ["listen_experience"],
                "dimension_gate_phase": 3,
                "listen_experience": {"pass_threshold": 0.5, "warn_threshold": 0.3},
            },
        )
        le = next(g for g in report.gates if g.dimension == "listen_experience")
        assert le.status == "FAIL"
        assert report.blocks_delivery is True
        row = next(x for x in report.to_dict()["gates"] if x["dimension"] == "listen_experience")
        assert row["contributes_to_delivery_block"] is True

    def test_listen_experience_deterministic(self) -> None:
        text = _listen_pass_chapter()
        cfg = {"pass_threshold": 0.5, "warn_threshold": 0.3}
        a = gate_listen_experience(text, cfg)
        b = gate_listen_experience(text, cfg)
        assert a.status == b.status
        assert a.score == b.score
        assert a.issues == b.issues
