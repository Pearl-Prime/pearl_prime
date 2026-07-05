#!/usr/bin/env python3
"""Disk space guard for agent dispatch and worktree creation.

Cheap preflight: one ``shutil.disk_usage`` call on the hot path. Stale
``.claude/worktrees`` orphan detection runs only for human-facing reports
(``--report-stale``, remediation output, ``--json``).

Exit codes: 0 pass (or warn-only trip), 1 below threshold, 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

DEFAULT_MIN_GB = 20.0
GB = 1024**3

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]


def repo_root(start: Path | None = None) -> Path:
    if start is not None:
        return start.resolve()
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        return Path(proc.stdout.strip()).resolve()
    return REPO_ROOT


def free_gb(path: Path) -> float:
    usage = shutil.disk_usage(path)
    return usage.free / GB


def git_worktree_paths(root: Path) -> set[Path]:
    proc = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=root,
    )
    if proc.returncode != 0:
        return set()
    registered: set[Path] = set()
    for line in proc.stdout.splitlines():
        if line.startswith("worktree "):
            registered.add(Path(line.split(" ", 1)[1]).resolve())
    return registered


def claude_worktrees_dir(root: Path) -> Path:
    return root / ".claude" / "worktrees"


def stale_claude_worktrees(root: Path) -> list[Path]:
    """Dirs under .claude/worktrees not referenced by ``git worktree list``."""
    wt_dir = claude_worktrees_dir(root)
    if not wt_dir.is_dir():
        return []
    registered = git_worktree_paths(root)
    orphans: list[Path] = []
    for entry in sorted(wt_dir.iterdir()):
        if not entry.is_dir():
            continue
        try:
            resolved = entry.resolve()
        except OSError:
            resolved = entry
        if resolved not in registered:
            orphans.append(entry)
    return orphans


def remediation_lines(root: Path, *, worktree_add: bool) -> list[str]:
    lines = [
        "Remediation (report-only — never auto-deleted):",
        "  1. git worktree prune",
        "  2. git lfs prune",
    ]
    orphans = stale_claude_worktrees(root)
    if orphans:
        lines.append("  3. Stale .claude/worktrees orphans (prune candidates):")
        for path in orphans:
            lines.append(f"       {path}")
        lines.append("     Inspect sizes: du -sh .claude/worktrees/*")
        lines.append(
            "     Remove safely: git worktree remove --force <path>  (human/agent decision)"
        )
    else:
        lines.append("  3. Inspect checkout disk: du -sh .claude/worktrees/*")
    if worktree_add:
        lines.extend(
            [
                "",
                "Before git worktree add:",
                "  GIT_LFS_SKIP_SMUDGE=1 git worktree add --no-checkout ... origin/main",
                "  git sparse-checkout init --cone && git sparse-checkout set <dirs>",
            ]
        )
    return lines


def check_disk(
    root: Path,
    *,
    min_gb: float,
    worktree_add: bool = False,
    report_stale: bool = False,
) -> tuple[bool, dict[str, Any]]:
    free = free_gb(root)
    ok = free >= min_gb
    payload: dict[str, Any] = {
        "status": "ok" if ok else "failed",
        "free_gb": round(free, 2),
        "min_gb": min_gb,
        "repo_root": str(root),
        "worktree_add_safe": worktree_add,
    }
    if report_stale or not ok:
        payload["stale_claude_worktrees"] = [str(p) for p in stale_claude_worktrees(root)]
    payload["remediation"] = remediation_lines(root, worktree_add=worktree_add)
    return ok, payload


def emit_human(payload: dict[str, Any], *, warn_only: bool) -> None:
    free = payload["free_gb"]
    min_gb = payload["min_gb"]
    print(f"Disk: {free:.2f} GB free (threshold {min_gb:.1f} GB)")
    if payload["status"] == "ok":
        print("Disk guard OK.")
        return
    prefix = "WARNING" if warn_only else "FAILED"
    print(f"{prefix}: below disk threshold ({free:.2f} GB < {min_gb:.1f} GB)", file=sys.stderr)
    for line in payload.get("remediation", []):
        print(line, file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Refuse dispatch/worktree add when free disk is below threshold.",
    )
    parser.add_argument(
        "--min-gb",
        type=float,
        default=float(os.environ.get("DISK_GUARD_MIN_GB", DEFAULT_MIN_GB)),
        help=f"Minimum free GB required (default: {DEFAULT_MIN_GB})",
    )
    parser.add_argument(
        "--path",
        default=None,
        help="Path for disk_usage (default: git repo root)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON on stdout",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Print warning below threshold but exit 0 (preflight soft-warn)",
    )
    parser.add_argument(
        "--worktree-add-safe",
        action="store_true",
        help="Hard block git worktree add below threshold; remind LFS-skip + sparse-checkout",
    )
    parser.add_argument(
        "--report-stale",
        action="store_true",
        help="Include stale .claude/worktrees orphan paths in output",
    )
    args = parser.parse_args(argv)

    if args.min_gb <= 0:
        print("Invalid --min-gb: must be positive", file=sys.stderr)
        return 2

    root = repo_root(Path(args.path) if args.path else None)
    ok, payload = check_disk(
        root,
        min_gb=args.min_gb,
        worktree_add=args.worktree_add_safe,
        report_stale=args.report_stale or args.worktree_add_safe,
    )

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        emit_human(payload, warn_only=args.warn_only)

    if ok:
        return 0
    if args.warn_only:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
