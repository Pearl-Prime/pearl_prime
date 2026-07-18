#!/usr/bin/env python3
"""Block oversized pushes: commit count, file count, and blob sizes.

Defaults match skills/pearl-github/references/git_system.md.
Compares HEAD to a base ref (default origin/main).

Exit codes: 0 pass or skip (cannot determine base), 1 violation, 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Any


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as e:
        raise SystemExit(f"Invalid integer for {name}: {raw!r}") from e


def _float_env(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return float(raw)
    except ValueError as e:
        raise SystemExit(f"Invalid float for {name}: {raw!r}") from e


def _git_ok(args: list[str]) -> bool:
    return subprocess.run(["git", *args], capture_output=True).returncode == 0


def resolve_base_ref(explicit: str | None) -> str | None:
    if explicit:
        return explicit if _git_ok(["rev-parse", "--verify", explicit]) else None
    for ref in ("origin/main", "origin/master", "main"):
        if _git_ok(["rev-parse", "--verify", ref]):
            return ref
    return None


def _git_out(args: list[str]) -> str:
    p = subprocess.run(["git", *args], capture_output=True, text=True)
    if p.returncode != 0:
        return ""
    return p.stdout.strip()


def commit_count_ahead(base: str, head: str = "HEAD") -> int:
    out = _git_out(["rev-list", "--count", f"{base}..{head}"])
    if not out.isdigit():
        return 0
    return int(out)


def changed_paths(base: str, head: str = "HEAD") -> list[str]:
    # Three-dot symmetric diff: changes on head since merge-base with base.
    raw = _git_out(["diff", "--name-only", f"{base}...{head}"])
    if not raw:
        return []
    return sorted(set(raw.splitlines()))


def blob_size_bytes(ref_path: str) -> int | None:
    """Size of object at `ref:path` (e.g. HEAD:foo/bar)."""
    p = subprocess.run(
        ["git", "cat-file", "-s", ref_path],
        capture_output=True,
        text=True,
    )
    if p.returncode != 0:
        return None
    try:
        return int(p.stdout.strip())
    except ValueError:
        return None


def size_stats(base: str, head: str = "HEAD") -> tuple[int, int]:
    """Return (total_bytes, max_single_bytes) for paths differing in base...head."""
    paths = changed_paths(base, head)
    total = 0
    largest = 0
    for path in paths:
        sz = blob_size_bytes(f"{head}:{path}")
        if sz is None:
            continue
        total += sz
        if sz > largest:
            largest = sz
    return total, largest


def run_check(
    base: str,
    *,
    head: str = "HEAD",
    max_commits: int,
    max_files: int,
    max_total_mb: float,
    max_single_file_mb: float,
) -> tuple[bool, dict[str, Any]]:
    commits = commit_count_ahead(base, head)
    paths = changed_paths(base, head)
    n_files = len(paths)
    total_b, largest_b = size_stats(base, head)
    total_mb = total_b / (1024 * 1024)
    largest_single_mb = largest_b / (1024 * 1024)

    limits = {
        "max_commits": max_commits,
        "max_files": max_files,
        "max_total_mb": max_total_mb,
        "max_single_mb": max_single_file_mb,
    }
    stats = {
        "base": base,
        "head": head,
        "commits_ahead": commits,
        "files_changed": n_files,
        "total_mb": round(total_mb, 4),
        "max_single_file_mb": round(largest_single_mb, 4),
        "limits": limits,
    }

    violations: list[str] = []
    if commits > max_commits:
        violations.append(
            f"Too many commits ahead of {base}: {commits} > {max_commits}"
        )
    if n_files > max_files:
        violations.append(
            f"Too many files changed vs {base}: {n_files} > {max_files}"
        )
    if total_mb > max_total_mb:
        violations.append(
            f"Total changed blob size too large: {total_mb:.2f} MB > {max_total_mb} MB"
        )
    if largest_single_mb > max_single_file_mb:
        violations.append(
            f"Largest single file too large: {largest_single_mb:.2f} MB > {max_single_file_mb} MB"
        )

    stats["violations"] = violations
    ok = len(violations) == 0
    stats["status"] = "ok" if ok else "failed"
    return ok, stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Enforce push size limits vs a base ref.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON on stdout",
    )
    parser.add_argument(
        "--base",
        default=os.environ.get("PUSH_GUARD_BASE"),
        help="Base ref (default: origin/main or first available)",
    )
    args = parser.parse_args(argv)

    max_commits = _int_env("PUSH_GUARD_MAX_COMMITS", 30)
    max_files = _int_env("PUSH_GUARD_MAX_FILES", 300)
    max_total_mb = _float_env("PUSH_GUARD_MAX_TOTAL_MB", 25.0)
    max_single_mb = _float_env("PUSH_GUARD_MAX_SINGLE_MB", 8.0)

    base = resolve_base_ref(args.base)
    if base is None:
        payload = {
            "status": "skipped",
            "reason": "no suitable base ref (set PUSH_GUARD_BASE or fetch origin)",
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print("SKIP: no base ref (origin/main / origin/master / main)", file=sys.stderr)
        return 0

    ok, stats = run_check(
        base,
        max_commits=max_commits,
        max_files=max_files,
        max_total_mb=max_total_mb,
        max_single_file_mb=max_single_mb,
    )

    if args.json:
        print(json.dumps(stats, indent=2))
    elif not ok:
        for v in stats.get("violations", []):
            print(v, file=sys.stderr)
        print(
            f"Push-guard: FAILED (base={base}, commits={stats['commits_ahead']}, "
            f"files={stats['files_changed']})",
            file=sys.stderr,
        )

    if ok and not args.json:
        print("Push-guard OK.")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
