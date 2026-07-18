#!/usr/bin/env python3
"""
Catalog Spam Gate — standalone CI runner.

Checks for Google Play Books compliance issues:
  GAP 1: Subtitle duplication
  GAP 2: Search keyword concentration
  GAP 3: Invisible script diversity
  GAP 4: Brand × topic × persona combo cap
  GAP 5: Author/narrator diversity
  Part 6: Health claims + disclaimer check

Authority: GOOGLE_PLAY_SPAM_FREE_AUDIT_2026_03_18.md

Usage:
  python scripts/ci/check_catalog_spam.py --plans-dir artifacts/full_catalog/candidates_compiled
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List


def main() -> int:
    ap = argparse.ArgumentParser(description="Catalog spam gates (Google Play compliance)")
    ap.add_argument("--plans-dir", required=True, help="Directory of compiled plan JSON files")
    args = ap.parse_args()

    # Load plans
    plans: List[Dict[str, Any]] = []
    for fn in sorted(os.listdir(args.plans_dir)):
        if fn.endswith(".json"):
            with open(os.path.join(args.plans_dir, fn), "r", encoding="utf-8") as f:
                plans.append(json.load(f))

    if not plans:
        print("CATALOG SPAM: no plans found", file=sys.stderr)
        return 1

    # Import gates
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from phoenix_v4.qa.catalog_spam_gates import run_all_catalog_spam_gates

    failures, warnings = run_all_catalog_spam_gates(plans)

    if failures:
        print(f"CATALOG SPAM: FAIL ({len(failures)} issues)")
        for f in failures:
            print(f"  FAIL: {f}")
    if warnings:
        print(f"CATALOG SPAM: WARNINGS ({len(warnings)})")
        for w in warnings[:20]:
            print(f"  WARN: {w}")
        if len(warnings) > 20:
            print(f"  ... and {len(warnings) - 20} more")
    if not failures:
        print(f"CATALOG SPAM: PASS ({len(plans)} plans checked, {len(warnings)} warnings)")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
