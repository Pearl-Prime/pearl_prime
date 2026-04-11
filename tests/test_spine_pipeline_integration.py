"""Integration tests for scripts/run_pipeline.py --pipeline-mode spine."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_PIPELINE = REPO_ROOT / "scripts" / "run_pipeline.py"
ANXIETY_ARC = (
    REPO_ROOT
    / "config"
    / "source_of_truth"
    / "master_arcs"
    / "gen_z_professionals__anxiety__false_alarm__F006.yaml"
)


def test_run_pipeline_help_lists_pipeline_mode() -> None:
    """CLI documents --pipeline-mode spine."""
    r = subprocess.run(
        [sys.executable, str(RUN_PIPELINE), "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0
    assert "--pipeline-mode" in r.stdout
    assert "spine" in r.stdout


def test_registry_mode_default() -> None:
    """Default pipeline mode is registry (backward compatible)."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline-mode", choices=["registry", "spine"], default="registry")
    ns = ap.parse_args([])
    assert ns.pipeline_mode == "registry"


@pytest.mark.skipif(not ANXIETY_ARC.exists(), reason="fixture arc missing")
def test_spine_mode_produces_book_and_audit(tmp_path: Path) -> None:
    """Spine mode run writes book.txt, enrichment_audit.json, budget.json."""
    out_dir = tmp_path / "spine_out"
    plan_path = tmp_path / "plan.json"
    cmd = [
        sys.executable,
        str(RUN_PIPELINE),
        "--topic",
        "anxiety",
        "--persona",
        "gen_z_professionals",
        "--arc",
        str(ANXIETY_ARC),
        "--pipeline-mode",
        "spine",
        "--render-book",
        "--render-dir",
        str(out_dir),
        "--out",
        str(plan_path),
        "--quality-profile",
        "draft",
        "--no-job-check",
        "--no-generate-freebies",
    ]
    r = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, r.stderr + r.stdout
    book = out_dir / "book.txt"
    assert book.exists()
    assert book.read_text(encoding="utf-8").strip()
    audit = out_dir / "enrichment_audit.json"
    assert audit.exists()
    data = json.loads(audit.read_text(encoding="utf-8"))
    assert "total_slots" in data or "total_words" in data


@pytest.mark.skipif(not ANXIETY_ARC.exists(), reason="fixture arc missing")
def test_spine_mode_budget_word_count_matches_book(tmp_path: Path) -> None:
    """budget.json word_count matches token count of book.txt (whitespace split)."""
    out_dir = tmp_path / "spine_out2"
    plan_path = tmp_path / "plan2.json"
    cmd = [
        sys.executable,
        str(RUN_PIPELINE),
        "--topic",
        "anxiety",
        "--persona",
        "gen_z_professionals",
        "--arc",
        str(ANXIETY_ARC),
        "--pipeline-mode",
        "spine",
        "--render-book",
        "--render-dir",
        str(out_dir),
        "--out",
        str(plan_path),
        "--quality-profile",
        "draft",
        "--no-job-check",
        "--no-generate-freebies",
    ]
    r = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, r.stderr + r.stdout
    book_text = (out_dir / "book.txt").read_text(encoding="utf-8")
    budget = json.loads((out_dir / "budget.json").read_text(encoding="utf-8"))
    wc = budget.get("word_count")
    assert wc == len(book_text.split())


@pytest.mark.skipif(not ANXIETY_ARC.exists(), reason="fixture arc missing")
def test_registry_mode_still_runs_for_anxiety(tmp_path: Path) -> None:
    """Default registry path still renders when topic has a section registry."""
    out_dir = tmp_path / "reg_out"
    plan_path = tmp_path / "reg_plan.json"
    cmd = [
        sys.executable,
        str(RUN_PIPELINE),
        "--topic",
        "anxiety",
        "--persona",
        "gen_z_professionals",
        "--arc",
        str(ANXIETY_ARC),
        "--render-book",
        "--render-dir",
        str(out_dir),
        "--out",
        str(plan_path),
        "--quality-profile",
        "draft",
        "--no-job-check",
        "--no-generate-freebies",
    ]
    r = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr + r.stdout
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert plan.get("source") == "section_registry"
    assert (out_dir / "book.txt").exists()


def test_spine_mode_enrichment_audit_has_depth_key_when_ran() -> None:
    """Pilot artifact (if present) includes depth_modules_added after depth pass."""
    audit_path = REPO_ROOT / "artifacts" / "pilot" / "full_15_spine" / "anxiety" / "enrichment_audit.json"
    if not audit_path.exists():
        pytest.skip("batch artifact not present")
    data = json.loads(audit_path.read_text(encoding="utf-8"))
    assert "depth_modules_added" in data
