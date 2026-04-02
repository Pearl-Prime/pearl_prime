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


def test_cover_art_dry_run_with_qc() -> None:
    r = _run_script(
        ["scripts/generate_author_cover_art_flux.py", "--dry-run", "--authors", "ahjan"],
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "prompt QC" in r.stdout


def test_bank_build_dry_run_with_qc() -> None:
    r = _run_script(
        ["scripts/video/run_flux_bank_build.py", "--dry-run", "--limit", "2"],
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "prompt QC" in r.stdout


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


def test_skip_qc_flag_in_help() -> None:
    for args in (
        ["scripts/generate_author_cover_art_flux.py", "--help"],
        ["scripts/video/run_flux_bank_build.py", "--help"],
        ["scripts/onboard_author.py", "create-pic", "--help"],
    ):
        r = _run_script(args)
        assert r.returncode == 0
        assert "skip-qc" in r.stdout.lower()
