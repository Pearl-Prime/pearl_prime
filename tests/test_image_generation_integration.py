"""Integration tests for FLUX scripts + QC dry-run — MANGA_QC_AND_EBOOK_PIPELINE_SPEC §A.3.7."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _run_script(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_cover_art_dry_run_with_qc(tmp_path: Path) -> None:
    """Dry-run must exercise the plan path; default out dir may skip when PNG exists (CI)."""
    r = subprocess.run(
        [
            sys.executable,
            "scripts/generate_author_cover_art_flux.py",
            "--dry-run",
            "--authors",
            "ahjan",
            "--out-dir",
            str(tmp_path),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "ahjan" in r.stdout and "ahjan_base.png" in r.stdout


def test_bank_build_dry_run_with_qc() -> None:
    r = _run_script(
        ["scripts/video/run_flux_bank_build.py", "--dry-run", "--limit", "2"],
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "Would generate" in r.stdout and "anxiety_" in r.stdout


@pytest.mark.skipif(
    not (REPO_ROOT / "scripts" / "onboard_author.py").is_file(),
    reason="onboard_author.py not in repo (optional onboarding CLI)",
)
def test_onboard_create_pic_dry_run_with_qc() -> None:
    bio = "x" * 60 + " meditation coaching wellness practice daily for portrait context."
    r = _run_script(
        [
            "scripts/onboard_author.py",
            "create-pic",
            "--author-id",
            "ahjan",
            "--dry-run",
            "--bio-text",
            bio,
        ],
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "Prompt QC" in r.stdout


def test_flux_scripts_expose_dry_run_in_help() -> None:
    """CLI surfaces --dry-run for offline/CI checks (skip-qc is not on all FLUX entrypoints)."""
    for args in (
        ["scripts/generate_author_cover_art_flux.py", "--help"],
        ["scripts/video/run_flux_bank_build.py", "--help"],
    ):
        r = _run_script(args)
        assert r.returncode == 0
        assert "--dry-run" in r.stdout
    if (REPO_ROOT / "scripts" / "onboard_author.py").is_file():
        r = _run_script(["scripts/onboard_author.py", "create-pic", "--help"])
        assert r.returncode == 0
        assert "skip-qc" in r.stdout.lower() or "--dry-run" in r.stdout
