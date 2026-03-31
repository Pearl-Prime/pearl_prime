#!/usr/bin/env python3
"""
Per-locale (persona, topic, engine) coverage.
Authority: PEARL_PRIME_100_PERCENT_DEV_PLAN §5.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser(description="Translation coverage per locale")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--locales", type=str, default=None, help="Comma-separated locales (default: from config)")
    args = ap.parse_args()

    locales = (args.locales or "en-US").split(",")
    report = {"locales": locales, "by_locale": {}}
    for loc in locales:
        atoms_root = REPO_ROOT / "atoms" if loc == "en-US" else REPO_ROOT / "atoms" / loc
        if not atoms_root.exists():
            report["by_locale"][loc] = {"persona_topic_count": 0, "has_atoms": False}
            continue
        count = sum(1 for _ in atoms_root.rglob("CANONICAL.txt"))
        report["by_locale"][loc] = {"persona_topic_count": count, "has_atoms": count > 0}

    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    for loc, data in report["by_locale"].items():
        print(f"  {loc}: {data['persona_topic_count']} CANONICAL.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
