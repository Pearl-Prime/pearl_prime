"""
Pytest wrapper for scripts/ci/check_flagship_contract.py.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE_SCRIPT = REPO_ROOT / "scripts/ci/check_flagship_contract.py"


def _run_gate() -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(GATE_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    return result.returncode, result.stdout, result.stderr


def test_contract_gate_script_exists() -> None:
    assert GATE_SCRIPT.exists()


def test_contract_gate_passes_on_canonical_state() -> None:
    exit_code, stdout, stderr = _run_gate()
    assert exit_code == 0, f"contract gate failed:\nstdout={stdout}\nstderr={stderr}"
