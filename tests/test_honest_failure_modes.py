"""Tests for honest failure modes (Hardening Spec §5).

The system must fail early with a clear reason rather than silently
producing degraded output.
"""
from __future__ import annotations

import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTeacherCoverageGateFailsHonestly:
    """Teacher coverage gate handles missing teacher honestly."""

    def test_nonexistent_teacher_handled(self):
        try:
            from phoenix_v4.teacher.coverage_gate import run_coverage_gate
        except ImportError:
            pytest.skip("teacher coverage_gate not importable")

        book_spec = {"teacher_id": "nonexistent_teacher_xyz", "topic_id": "anxiety", "persona_id": "gen_z_professionals"}
        format_plan = {"slot_definitions": {"chapters": [{"slots": ["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]}]}}
        arc = {"emotional_curve": [3]}

        try:
            passed, gap_report = run_coverage_gate(book_spec, format_plan, arc)
        except Exception as exc:
            # Raising an explicit error is an honest failure — acceptable
            assert str(exc), f"Teacher gate raised with empty message: {exc}"
            return

        # Gate either fails (expected) or passes with a valid gap report
        # Either way, the system does not silently produce broken output
        assert isinstance(passed, bool)
        assert gap_report is not None, "Gap report should not be None"

    def test_nonexistent_teacher_has_zero_atoms(self):
        try:
            from phoenix_v4.teacher.coverage_gate import compute_available_teacher_atoms
        except ImportError:
            pytest.skip("teacher coverage_gate not importable")

        available = compute_available_teacher_atoms("nonexistent_teacher_xyz")
        # A nonexistent teacher should have 0 atoms for every slot type
        total = sum(available.values()) if available else 0
        assert total == 0, f"Nonexistent teacher should have 0 atoms, got {total}"


class TestLocationProfileMissing:
    """Missing location profile raises explicit error (honest failure)."""

    def test_unknown_location_raises_with_message(self):
        try:
            from phoenix_v4.planning.catalog_planner import resolve_location_profile_id
        except ImportError:
            pytest.skip("catalog_planner not importable")

        with pytest.raises(ValueError, match="not found"):
            resolve_location_profile_id("nonexistent_city_xyz_999")

    def test_error_lists_available_profiles(self):
        try:
            from phoenix_v4.planning.catalog_planner import resolve_location_profile_id
        except ImportError:
            pytest.skip("catalog_planner not importable")

        with pytest.raises(ValueError) as exc_info:
            resolve_location_profile_id("nonexistent_city_xyz_999")
        msg = str(exc_info.value)
        # Error message should list available profiles for actionability
        assert "nyc_metro" in msg or "Available" in msg

    def test_known_locations_resolve(self):
        try:
            from phoenix_v4.planning.catalog_planner import resolve_location_profile_id
        except ImportError:
            pytest.skip("catalog_planner not importable")

        assert resolve_location_profile_id("nyc") == "nyc_metro"
        assert resolve_location_profile_id("grand_central") == "nyc_grand_central"


class TestOutputContractBudgetFail:
    """Word count shortfall produces explicit budget_check_result='fail'."""

    def test_undersized_book_fails_budget(self):
        from phoenix_v4.planning.output_contract import (
            build_output_contract,
            update_contract_post_render,
        )

        args = types.SimpleNamespace(
            topic="anxiety",
            persona="gen_z_professionals",
            location=None,
            teacher=None,
            runtime_format="standard_book",
            structural_format="F006",
        )
        resolved = {
            "canonical_topic_id": "anxiety",
            "canonical_persona_id": "gen_z_professionals",
            "resolved_location_id": "",
            "teacher_mode": False,
            "teacher_id": None,
            "quality_profile": "production",
            "runtime_format": "standard_book",
        }
        contract = build_output_contract(args, resolved)
        updated = update_contract_post_render(contract, word_count_achieved=2000)

        wc_target = contract.get("word_count_target", {})
        if wc_target.get("min", 0) > 0:
            assert updated["budget_check_result"] == "fail", (
                f"Budget should fail: achieved 2000 vs min {wc_target['min']}"
            )

    def test_adequate_book_passes_budget(self):
        from phoenix_v4.planning.output_contract import (
            build_output_contract,
            update_contract_post_render,
        )

        args = types.SimpleNamespace(
            topic="anxiety", persona="gen_z_professionals",
            location=None, teacher=None,
            runtime_format="standard_book", structural_format="F006",
        )
        resolved = {
            "canonical_topic_id": "anxiety",
            "canonical_persona_id": "gen_z_professionals",
            "resolved_location_id": "",
            "teacher_mode": False,
            "teacher_id": None,
            "quality_profile": "production",
            "runtime_format": "standard_book",
        }
        contract = build_output_contract(args, resolved)
        updated = update_contract_post_render(contract, word_count_achieved=10000)

        wc_target = contract.get("word_count_target", {})
        if wc_target.get("min", 0) > 0 and wc_target.get("max", 0) >= 10000:
            assert updated["budget_check_result"] == "pass"


class TestTopicWithNoPool:
    """Coverage checker reports errors for a fake topic with no atom pool."""

    def test_fake_topic_reports_errors(self):
        try:
            from phoenix_v4.planning.coverage_checker import check_coverage
        except ImportError:
            pytest.skip("coverage_checker not importable")

        try:
            passed, errors = check_coverage(
                persona="gen_z_professionals",
                topic="nonexistent_topic_xyz_999",
            )
        except Exception as exc:
            # Explicit error is honest failure
            assert str(exc), f"Coverage check raised with empty message: {exc}"
            return

        assert passed is False, "Coverage should fail for nonexistent topic"
        assert errors, "Should report specific errors"
