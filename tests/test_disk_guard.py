"""Unit tests for scripts/git/disk_guard.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[1]
DISK_GUARD_PATH = REPO / "scripts" / "git" / "disk_guard.py"


def _load_disk_guard():
    spec = importlib.util.spec_from_file_location("disk_guard", DISK_GUARD_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _usage(free_gb: float) -> SimpleNamespace:
    free = int(free_gb * 1024**3)
    total = 1024**4
    return SimpleNamespace(free=free, total=total, used=total - free)


def test_passes_above_threshold(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    dg = _load_disk_guard()
    monkeypatch.setattr(dg.shutil, "disk_usage", lambda _p: _usage(25.0))
    monkeypatch.setattr(dg, "stale_claude_worktrees", lambda _r: [])

    ok, payload = dg.check_disk(tmp_path, min_gb=20.0)
    assert ok is True
    assert payload["free_gb"] == 25.0
    assert payload["status"] == "ok"


def test_fails_below_threshold(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    dg = _load_disk_guard()
    monkeypatch.setattr(dg.shutil, "disk_usage", lambda _p: _usage(10.0))
    monkeypatch.setattr(dg, "stale_claude_worktrees", lambda _r: [])

    ok, payload = dg.check_disk(tmp_path, min_gb=20.0, worktree_add=True)
    assert ok is False
    assert payload["status"] == "failed"
    assert payload["worktree_add_safe"] is True
    assert any("GIT_LFS_SKIP_SMUDGE" in line for line in payload["remediation"])


def test_cli_exits_nonzero_below_threshold(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    dg = _load_disk_guard()
    monkeypatch.setattr(dg.shutil, "disk_usage", lambda _p: _usage(5.0))
    monkeypatch.setattr(dg, "stale_claude_worktrees", lambda _r: [])

    assert dg.main(["--path", str(tmp_path), "--min-gb", "20"]) == 1


def test_cli_warn_only_exits_zero_below_threshold(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    dg = _load_disk_guard()
    monkeypatch.setattr(dg.shutil, "disk_usage", lambda _p: _usage(5.0))
    monkeypatch.setattr(dg, "stale_claude_worktrees", lambda _r: [])

    assert dg.main(["--path", str(tmp_path), "--min-gb", "20", "--warn-only"]) == 0


def test_stale_worktree_detection(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    dg = _load_disk_guard()
    orphan = tmp_path / ".claude" / "worktrees" / "aborted-checkout"
    orphan.mkdir(parents=True)
    monkeypatch.setattr(dg, "git_worktree_paths", lambda _r: set())

    stale = dg.stale_claude_worktrees(tmp_path)
    assert stale == [orphan]


def test_json_output_parses(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(DISK_GUARD_PATH),
            "--json",
            "--path",
            str(tmp_path),
            "--min-gb",
            "0.001",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["status"] == "ok"
    assert "free_gb" in data
