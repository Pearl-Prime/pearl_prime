"""
Pytest wrapper for the Flagship CH1 golden parity gate.

Makes scripts/ci/check_flagship_book_parity.py runnable in the normal
pytest battery. Includes a mutation smoke test proving the gate catches drift.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_SCRIPT = REPO_ROOT / "scripts/ci/check_flagship_book_parity.py"
CANONICAL_SNAPSHOT = REPO_ROOT / "artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt"
METADATA_PATH = REPO_ROOT / "artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1_METADATA.json"


def _run_gate(*extra: str) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(GATE_SCRIPT), *extra],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    return result.returncode, result.stdout, result.stderr


def test_gate_script_exists() -> None:
    assert GATE_SCRIPT.exists()


def test_canonical_snapshot_exists() -> None:
    assert CANONICAL_SNAPSHOT.exists()
    assert METADATA_PATH.exists()


def test_parity_gate_passes_on_canonical_state() -> None:
    exit_code, stdout, stderr = _run_gate()
    assert exit_code == 0, f"parity gate failed:\nstdout={stdout}\nstderr={stderr}"


def test_parity_gate_fails_on_deliberately_broken_snapshot(tmp_path: Path) -> None:
    original = CANONICAL_SNAPSHOT.read_text(encoding="utf-8")
    broken = original.replace("protective alarm", "BROKEN protective alarm", 1)
    broken_path = tmp_path / "broken_ch1.txt"
    broken_path.write_text(broken, encoding="utf-8")
    exit_code, stdout, stderr = _run_gate("--ch1-from-file", str(broken_path))
    assert exit_code != 0, "parity gate did not detect deliberately broken CH1"
    combined = stdout + stderr
    assert "restore via `git checkout" in combined
