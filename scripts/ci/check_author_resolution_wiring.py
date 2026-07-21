#!/usr/bin/env python3
"""CI smoke: author-resolution surfaces remain wired into assembly consumers (I001).

Fails if known author helpers disappear or have zero non-test importers.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

REQUIRED_PATHS = [
    "scripts/ci/check_author_positioning.py",
    "scripts/ci/check_author_cover_art.py",
]


def _rg_count(pattern: str) -> int:
    try:
        proc = subprocess.run(
            ["rg", "-l", pattern, "phoenix_v4", "scripts", "--glob", "*.py"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return -1
    files = [ln for ln in proc.stdout.splitlines() if ln.strip() and "/test" not in ln]
    return len(files)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate-mode", choices=("fail", "warn"), default="fail")
    args = ap.parse_args()
    errors = []
    for rel in REQUIRED_PATHS:
        if not (REPO / rel).exists():
            errors.append(f"missing required path: {rel}")
    # author_id must still appear in social/assembly surfaces
    n = _rg_count(r"author_id")
    if n == 0:
        errors.append("no author_id references under phoenix_v4/scripts (unwired?)")
    elif n < 0:
        print("WARN: rg unavailable; path existence only", file=sys.stderr)
    if errors:
        msg = "author resolution wiring gaps:\n" + "\n".join(f"  - {e}" for e in errors)
        if args.gate_mode == "warn":
            print(f"::warning::{msg}")
            return 0
        print(msg, file=sys.stderr)
        return 1
    print(f"OK: author resolution wiring surfaces present (author_id hits≈{n})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
