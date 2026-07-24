#!/usr/bin/env python3
"""CI smoke: anti-reinvention / subsystem authority surfaces exist (I047)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REQUIRED = [
    "artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv",
    "docs/agent_brief.txt",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate-mode", choices=("fail", "warn"), default="fail")
    args = ap.parse_args()
    errors = []
    for rel in REQUIRED:
        p = REPO / rel
        if not p.exists():
            errors.append(f"missing: {rel}")
        elif p.stat().st_size < 50:
            errors.append(f"too small / empty: {rel}")
    # Authority map should have a header + rows
    auth = REPO / REQUIRED[0]
    if auth.exists():
        lines = [ln for ln in auth.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]
        if len(lines) < 2:
            errors.append("SUBSYSTEM_AUTHORITY_MAP.tsv has no data rows")
    if errors:
        msg = "anti-reinvention surfaces:\n" + "\n".join(f"  - {e}" for e in errors)
        if args.gate_mode == "warn":
            print(f"::warning::{msg}")
            return 0
        print(msg, file=sys.stderr)
        return 1
    print("OK: anti-reinvention / authority surfaces present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
