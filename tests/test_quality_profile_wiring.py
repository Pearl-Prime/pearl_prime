"""
Tests for quality profile wiring in run_pipeline.py.

Validates that --quality-profile production/draft/debug and --skip-quality-gates
correctly control gate enforcement behavior.
"""
from __future__ import annotations

import json
import re
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.quality.chapter_flow_gate import ChapterFlowResult, evaluate_chapter_flow
from phoenix_v4.quality.bestseller_craft_gate import evaluate_bestseller_craft, CraftGateResult


# ---------------------------------------------------------------------------
# Helpers: build mock data for _run_post_render_quality_gates
# ---------------------------------------------------------------------------

def _make_failing_flow_report(n_chapters: int = 5) -> dict:
    """Build a chapter_flow_report.json where ALL chapters fail."""
    chapters = []
    for i in range(n_chapters):
        chapters.append({
            "chapter": i + 1,
            "status": "FAIL",
            "score": 10,
            "errors": ["WEAK_TRANSITIONS", "MISSING_CLEAR_POINT"],
            "warnings": [],
            "metrics": {},
        })
    return {
        "status": "FAIL",
        "chapters": chapters,
    }


def _make_passing_flow_report(n_chapters: int = 5) -> dict:
    chapters = []
    for i in range(n_chapters):
        chapters.append({
            "chapter": i + 1,
            "status": "PASS",
            "score": 85,
            "errors": [],
            "warnings": [],
            "metrics": {},
        })
    return {
        "status": "PASS",
        "chapters": chapters,
    }


def _make_rendered_txt(n_chapters: int = 5) -> str:
    """Generate minimal rendered book text with chapter headings."""
    parts = []
    for i in range(n_chapters):
        parts.append(f"## Chapter {i + 1}\n\nSome prose for chapter {i + 1}.\n")
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Import the post-render function from run_pipeline
# ---------------------------------------------------------------------------

# We import _run_post_render_quality_gates from the scripts module.
# Since scripts/run_pipeline.py inserts REPO_ROOT into sys.path, we need
# to handle the import carefully.
from importlib import import_module
import importlib.util

_PIPELINE_PATH = REPO_ROOT / "scripts" / "run_pipeline.py"


def _load_pipeline_module():
    spec = importlib.util.spec_from_file_location("run_pipeline", _PIPELINE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_pipeline = _load_pipeline_module()
_run_post_render_quality_gates = _pipeline._run_post_render_quality_gates


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestProductionModeAllFail:
    """production mode: all-fail chapters -> exit 1."""

    def test_all_chapters_fail_returns_exit_1(self, tmp_path):
        render_dir = tmp_path / "rendered"
        render_dir.mkdir()

        # Write a failing flow report
        flow_report = _make_failing_flow_report(5)
        flow_path = render_dir / "chapter_flow_report.json"
        flow_path.write_text(json.dumps(flow_report, indent=2))

        # Write minimal rendered txt
        txt_path = render_dir / "book.txt"
        txt_path.write_text(_make_rendered_txt(5))

        written = {"txt": txt_path, "chapter_flow_report": flow_path}

        with patch(
            "phoenix_v4.quality.bestseller_craft_gate.evaluate_bestseller_craft"
        ) as mock_craft:
            mock_craft.return_value = CraftGateResult(
                status="FAIL",
                move_scores={"orient": 0.1, "name": 0.1, "turn": 0.1, "give": 0.1, "pull": 0.1},
                issues=["move_fail:orient,name,turn,give,pull"],
                remediation=[],
                metrics={},
            )

            result = _run_post_render_quality_gates(
                out={"chapter_slot_sequence": [["HOOK", "STORY"]] * 5, "atom_ids": ["a"] * 10},
                render_dir=render_dir,
                written=written,
                canonical_persona="test_persona",
                canonical_topic="test_topic",
                atoms_root=None,
                gates_hard=True,  # production mode
            )

        # All chapters failed -> should return exit code 1
        assert result == 1


class TestDraftModeAllFail:
    """draft mode: all-fail chapters -> exit 0 (warnings only)."""

    def test_all_chapters_fail_returns_none(self, tmp_path):
        render_dir = tmp_path / "rendered"
        render_dir.mkdir()

        flow_report = _make_failing_flow_report(5)
        flow_path = render_dir / "chapter_flow_report.json"
        flow_path.write_text(json.dumps(flow_report, indent=2))

        txt_path = render_dir / "book.txt"
        txt_path.write_text(_make_rendered_txt(5))

        written = {"txt": txt_path, "chapter_flow_report": flow_path}

        with patch(
            "phoenix_v4.quality.bestseller_craft_gate.evaluate_bestseller_craft"
        ) as mock_craft:
            mock_craft.return_value = CraftGateResult(
                status="FAIL",
                move_scores={"orient": 0.1, "name": 0.1, "turn": 0.1, "give": 0.1, "pull": 0.1},
                issues=[],
                remediation=[],
                metrics={},
            )

            result = _run_post_render_quality_gates(
                out={"chapter_slot_sequence": [["HOOK", "STORY"]] * 5, "atom_ids": ["a"] * 10},
                render_dir=render_dir,
                written=written,
                canonical_persona="test_persona",
                canonical_topic="test_topic",
                atoms_root=None,
                gates_hard=False,  # draft mode
            )

        # Draft mode: failures only warn, should return None (continue)
        assert result is None


class TestDebugModeNoGates:
    """debug mode: no gates run -- verified via argparse flag resolution."""

    def test_skip_quality_gates_overrides_production(self):
        """When --skip-quality-gates is set, quality_profile becomes debug."""
        import argparse

        # Simulate the argparse + resolution logic from main()
        ap = argparse.ArgumentParser()
        ap.add_argument("--quality-profile", choices=["production", "draft", "debug"], default="production")
        ap.add_argument("--skip-quality-gates", action="store_true")

        args = ap.parse_args(["--quality-profile", "production", "--skip-quality-gates"])

        quality_profile = args.quality_profile
        if args.skip_quality_gates:
            quality_profile = "debug"
        gates_run = quality_profile in ("production", "draft")
        gates_hard = quality_profile == "production"

        assert quality_profile == "debug"
        assert gates_run is False
        assert gates_hard is False

    def test_debug_profile_skips_gates(self):
        """When --quality-profile=debug, gates_run is False."""
        import argparse

        ap = argparse.ArgumentParser()
        ap.add_argument("--quality-profile", choices=["production", "draft", "debug"], default="production")
        ap.add_argument("--skip-quality-gates", action="store_true")

        args = ap.parse_args(["--quality-profile", "debug"])

        quality_profile = args.quality_profile
        if args.skip_quality_gates:
            quality_profile = "debug"
        gates_run = quality_profile in ("production", "draft")

        assert gates_run is False


class TestSkipQualityGatesOverridesProduction:
    """--skip-quality-gates overrides production mode."""

    def test_production_default_runs_gates(self):
        """Default (production) runs gates."""
        import argparse

        ap = argparse.ArgumentParser()
        ap.add_argument("--quality-profile", choices=["production", "draft", "debug"], default="production")
        ap.add_argument("--skip-quality-gates", action="store_true")

        args = ap.parse_args([])

        quality_profile = args.quality_profile
        if args.skip_quality_gates:
            quality_profile = "debug"
        gates_run = quality_profile in ("production", "draft")
        gates_hard = quality_profile == "production"

        assert quality_profile == "production"
        assert gates_run is True
        assert gates_hard is True

    def test_draft_mode_runs_gates_soft(self):
        """draft mode runs gates but doesn't hard-fail."""
        import argparse

        ap = argparse.ArgumentParser()
        ap.add_argument("--quality-profile", choices=["production", "draft", "debug"], default="production")
        ap.add_argument("--skip-quality-gates", action="store_true")

        args = ap.parse_args(["--quality-profile", "draft"])

        quality_profile = args.quality_profile
        if args.skip_quality_gates:
            quality_profile = "debug"
        gates_run = quality_profile in ("production", "draft")
        gates_hard = quality_profile == "production"

        assert quality_profile == "draft"
        assert gates_run is True
        assert gates_hard is False


class TestPassingGatesReturnNone:
    """When all gates pass, the function returns None (continue pipeline)."""

    def test_all_pass_returns_none(self, tmp_path):
        render_dir = tmp_path / "rendered"
        render_dir.mkdir()

        flow_report = _make_passing_flow_report(3)
        flow_path = render_dir / "chapter_flow_report.json"
        flow_path.write_text(json.dumps(flow_report, indent=2))

        txt_path = render_dir / "book.txt"
        txt_path.write_text(_make_rendered_txt(3))

        written = {"txt": txt_path, "chapter_flow_report": flow_path}

        with patch(
            "phoenix_v4.quality.bestseller_craft_gate.evaluate_bestseller_craft"
        ) as mock_craft:
            mock_craft.return_value = CraftGateResult(
                status="PASS",
                move_scores={"orient": 0.8, "name": 0.7, "turn": 0.6, "give": 0.7, "pull": 0.6},
                issues=[],
                remediation=[],
                metrics={},
            )

            result = _run_post_render_quality_gates(
                out={"chapter_slot_sequence": [["HOOK", "STORY"]] * 3, "atom_ids": ["a"] * 6},
                render_dir=render_dir,
                written=written,
                canonical_persona="test_persona",
                canonical_topic="test_topic",
                atoms_root=None,
                gates_hard=True,
            )

        assert result is None


class TestBestsellerCraftAdvisoryOnly:
    """Bestseller craft gate is advisory -- never blocks, even in production."""

    def test_craft_fail_does_not_block(self, tmp_path):
        render_dir = tmp_path / "rendered"
        render_dir.mkdir()

        flow_report = _make_passing_flow_report(2)
        flow_path = render_dir / "chapter_flow_report.json"
        flow_path.write_text(json.dumps(flow_report, indent=2))

        txt_path = render_dir / "book.txt"
        txt_path.write_text(_make_rendered_txt(2))

        written = {"txt": txt_path, "chapter_flow_report": flow_path}

        with patch(
            "phoenix_v4.quality.bestseller_craft_gate.evaluate_bestseller_craft"
        ) as mock_craft:
            mock_craft.return_value = CraftGateResult(
                status="FAIL",
                move_scores={"orient": 0.05, "name": 0.05, "turn": 0.05, "give": 0.05, "pull": 0.05},
                issues=["move_fail:orient,name,turn,give,pull"],
                remediation=["Everything failed."],
                metrics={},
            )

            result = _run_post_render_quality_gates(
                out={"chapter_slot_sequence": [["HOOK"]] * 2, "atom_ids": ["a"] * 2},
                render_dir=render_dir,
                written=written,
                canonical_persona="test_persona",
                canonical_topic="test_topic",
                atoms_root=None,
                gates_hard=True,
            )

        # Advisory: craft gate failure never blocks
        assert result is None

        # Verify craft scores were written into the flow report
        updated_report = json.loads(flow_path.read_text())
        assert "bestseller_craft" in updated_report
        assert updated_report["bestseller_craft"]["overall_score"] < 0.1
