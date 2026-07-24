#!/usr/bin/env python3
"""CI smoke: localization quality_contracts directory is present and non-empty (I031)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CONTRACTS = REPO / "config/localization/quality_contracts"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate-mode", choices=("fail", "warn"), default="fail")
    args = ap.parse_args()
    errors = []
    if not CONTRACTS.is_dir():
        errors.append(f"missing directory: {CONTRACTS.relative_to(REPO)}")
    else:
        files = [p for p in CONTRACTS.rglob("*") if p.is_file() and not p.name.startswith(".")]
        if not files:
            errors.append("quality_contracts directory is empty")
        readme = CONTRACTS / "README.md"
        if not readme.exists():
            errors.append("quality_contracts/README.md missing")
    if errors:
        msg = "localization quality contracts:\n" + "\n".join(f"  - {e}" for e in errors)
        if args.gate_mode == "warn":
            print(f"::warning::{msg}")
            return 0
        print(msg, file=sys.stderr)
        return 1
    n = len(list(CONTRACTS.rglob("*")))
    print(f"OK: quality_contracts present ({n} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
