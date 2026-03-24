"""Smoke tests for scripts/git/push_guard.py (local git state may skip)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_push_guard_json_parses_and_exits_zero_or_one() -> None:
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "git" / "push_guard.py"), "--json"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert proc.stdout.strip()
    data = json.loads(proc.stdout)
    assert "status" in data
    assert data["status"] in ("ok", "failed", "skipped")
    assert proc.returncode in (0, 1)
