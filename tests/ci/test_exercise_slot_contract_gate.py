"""CI gate: planner-owned EXERCISE slot contract."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_exercise_slot_contract_gate_passes() -> None:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts/ci/check_exercise_slot_contract.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
