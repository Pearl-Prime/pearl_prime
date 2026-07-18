"""Import dry-run must never claim production atoms."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "teacher_onboarding" / "import_dry_run.py"
FIXTURE = (
    ROOT
    / "artifacts"
    / "qa"
    / "oldchats7_finish_20260718"
    / "lane08"
    / "fixtures"
    / "sample_submission.json"
)


def test_import_dry_run_fixture():
    assert SCRIPT.is_file()
    assert FIXTURE.is_file()
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--submission", str(FIXTURE)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["schema_version"] == "teacher_bank_import_scaffold_v1"
    assert data["production_atoms_created"] is False
    assert data["lifecycle_status"] == "imported"
    assert data["teacher_id"] == "lane08_fixture_teacher"
    assert "doctrine" in data["candidate_paths"]


def test_refuses_source_of_truth_write(tmp_path):
    bad = tmp_path / "SOURCE_OF_TRUTH" / "x"
    bad.mkdir(parents=True)
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--submission",
            str(FIXTURE),
            "--write-scaffold",
            str(bad),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 4
