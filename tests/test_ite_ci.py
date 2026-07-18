"""Tests for ITE CI scripts and scorer.
Authority: specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md
Fixtures: tests/fixtures/ite/"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "ite"
SCRIPTS = REPO_ROOT / "scripts" / "ci"


def _run_ci(script: str, chapter_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), "--chapter-dir", str(chapter_dir)],
        capture_output=True, text=True, timeout=30, cwd=REPO_ROOT,
    )


def _make_chapter(tmp_path: Path, files: dict[str, str]) -> Path:
    """Copy fixture files into a temp chapter dir."""
    ch = tmp_path / "chapter"
    ch.mkdir()
    for dst_name, src_name in files.items():
        src = FIXTURES / src_name
        if src.exists():
            shutil.copy(src, ch / dst_name)
    return ch


# ── ite_gutter_check ──

class TestGutterCheck:
    def test_pass(self, tmp_path):
        ch = _make_chapter(tmp_path, {"panel_prompts.json": "panel_prompts_pass.json"})
        r = _run_ci("ite_gutter_check.py", ch)
        assert r.returncode == 0

    def test_fail_band4_and_consecutive(self, tmp_path):
        ch = _make_chapter(tmp_path, {"panel_prompts.json": "panel_prompts_fail_gutter.json"})
        r = _run_ci("ite_gutter_check.py", ch)
        assert r.returncode == 1
        assert "T-01 BLOCKER" in r.stderr or "T-02 BLOCKER" in r.stderr or "T-03 BLOCKER" in r.stderr


# ── ite_stealth_scan ──

class TestStealthScan:
    def test_pass(self, tmp_path):
        ch = _make_chapter(tmp_path, {"chapter_script.json": "chapter_script_pass.json"})
        r = _run_ci("ite_stealth_scan.py", ch)
        assert r.returncode == 0

    def test_fail_forbidden_terms(self, tmp_path):
        ch = _make_chapter(tmp_path, {"chapter_script.json": "chapter_script_fail.json"})
        r = _run_ci("ite_stealth_scan.py", ch)
        assert r.returncode == 1
        assert "T-04 BLOCKER" in r.stderr


# ── ite_color_arc ──

class TestColorArc:
    def test_pass(self, tmp_path):
        ch = _make_chapter(tmp_path, {"panel_prompts.json": "panel_prompts_pass.json"})
        r = _run_ci("ite_color_arc.py", ch)
        assert r.returncode == 0  # WARN only, never blocks


# ── ite_breath_check ──

class TestBreathCheck:
    def test_pass(self, tmp_path):
        ch = _make_chapter(tmp_path, {"panel_prompts.json": "panel_prompts_pass.json"})
        r = _run_ci("ite_breath_check.py", ch)
        assert r.returncode == 0

    def test_warn_no_breath(self, tmp_path):
        ch = _make_chapter(tmp_path, {"panel_prompts.json": "panel_prompts_fail_gutter.json"})
        r = _run_ci("ite_breath_check.py", ch)
        assert r.returncode == 0  # WARN only
        assert "T-07 WARN" in r.stdout


# ── ite_soundtrack ──

class TestSoundtrack:
    def test_pass(self, tmp_path):
        ch = _make_chapter(tmp_path, {"soundtrack_config.yaml": "soundtrack_config_pass.yaml"})
        r = _run_ci("ite_soundtrack.py", ch)
        assert r.returncode == 0

    def test_fail_lyrics_and_video(self, tmp_path):
        ch = _make_chapter(tmp_path, {"soundtrack_config.yaml": "soundtrack_config_fail.yaml"})
        r = _run_ci("ite_soundtrack.py", ch)
        assert r.returncode == 1
        assert "T-05 BLOCKER" in r.stderr or "T-06 BLOCKER" in r.stderr


# ── ite_composite ──

class TestComposite:
    def test_pass(self, tmp_path):
        ch = _make_chapter(tmp_path, {"ite_report.json": "ite_report_pass.json"})
        r = _run_ci("ite_composite.py", ch)
        assert r.returncode == 0

    def test_fail_low_score(self, tmp_path):
        ch = _make_chapter(tmp_path, {"ite_report.json": "ite_report_fail.json"})
        r = _run_ci("ite_composite.py", ch)
        assert r.returncode == 1
        assert "T-19 FAIL" in r.stderr


# ── ITE Scorer ──

class TestITEScorer:
    def test_stealth_clean(self):
        sys.path.insert(0, str(REPO_ROOT))
        from phoenix_v4.manga.qc.ite_scorer import score_stealth
        assert score_stealth("The river is quiet today.") == 1.0

    def test_stealth_violation(self):
        sys.path.insert(0, str(REPO_ROOT))
        from phoenix_v4.manga.qc.ite_scorer import score_stealth
        score = score_stealth("Try this mindfulness meditation for your wellness and mental health.")
        assert score < 0.5

    def test_composite(self):
        sys.path.insert(0, str(REPO_ROOT))
        from phoenix_v4.manga.qc.ite_scorer import ITEScores
        s = ITEScores(vt_parasympathetic=0.7, vt_processing=0.7, vt_somatic=0.7, vt_stealth=0.9)
        composite = s.compute_composite()
        expected = 0.7 * 0.30 + 0.7 * 0.25 + 0.7 * 0.25 + 0.9 * 0.20
        assert abs(composite - expected) < 0.01

    def test_score_chapter(self):
        sys.path.insert(0, str(REPO_ROOT))
        from phoenix_v4.manga.qc.ite_scorer import score_chapter
        panels = [
            {"chapter_pct": 70, "emotional_band": 1, "gutter_after": "processing",
             "size_pct": 45, "fractal_target": {"fd_range": [1.3, 1.5]},
             "color_temperature": {"temp_k": 6000, "saturation_pct": 45}},
            {"chapter_pct": 80, "emotional_band": 1, "gutter_after": "standard",
             "size_pct": 30, "color_temperature": {"temp_k": 6500, "saturation_pct": 40}},
        ]
        breath_seqs = [{"phase_panels": {"inhale": ["a"], "hold": ["b"], "exhale": ["c"]}}]
        scores = score_chapter(panels, breath_seqs, {"positive_model": {}, "transitional": {}}, {}, "The day was bright.")
        assert scores.ite_score > 0
        assert scores.vt_stealth == 1.0
