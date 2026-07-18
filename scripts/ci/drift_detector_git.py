#!/usr/bin/env python3
"""Shared git helpers for drift-detector CI scripts."""
from __future__ import annotations

import subprocess
from pathlib import Path


def repo_root_from_script(script_path: Path) -> Path:
    return script_path.resolve().parents[2]


def git_diff_name_status(base: str | None, head: str, repo_root: Path) -> list[tuple[str, str]]:
    """Return (status, path) pairs from git diff. status is A/M/D/R etc."""
    if base:
        cmd = ["git", "diff", "--name-status", f"{base}...{head}"]
    else:
        cmd = ["git", "diff", "--name-status", "HEAD"]
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    rows: list[tuple[str, str]] = []
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0]
        path = parts[-1]
        rows.append((status, path.replace("\\", "/")))
    return rows


def changed_paths(base: str | None, head: str, repo_root: Path) -> list[str]:
    return [path for _status, path in git_diff_name_status(base, head, repo_root)]


def added_paths(base: str | None, head: str, repo_root: Path) -> list[str]:
    added: list[str] = []
    for status, path in git_diff_name_status(base, head, repo_root):
        if status.startswith("A"):
            added.append(path)
    return added
