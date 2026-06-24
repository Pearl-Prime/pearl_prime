#!/usr/bin/env python3
"""Build marketing feeds for all GHL-enabled brands in brand_marketing_registry.yaml."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.marketing.brand_profile import list_brands  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Matrix-build GHL marketing feeds")
    ap.add_argument("--locale", default="en_US")
    ap.add_argument("--rollout-phase", default=None, help="e.g. pilot")
    ap.add_argument("--brand-id", action="append", dest="brand_ids", help="Limit to brand(s)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--publish", action="store_true", help="Run publish_marketing_feed_r2.py after each build")
    args = ap.parse_args()

    brand_ids = args.brand_ids or list_brands(
        ghl_enabled_only=True,
        rollout_phase=args.rollout_phase,
    )
    if not brand_ids:
        print("No brands matched", file=sys.stderr)
        return 1

    failures: list[str] = []
    for brand_id in brand_ids:
        cmd = [
            sys.executable,
            str(REPO_ROOT / "scripts/marketing/build_marketing_feed.py"),
            "--brand-id",
            brand_id,
            "--locale",
            args.locale,
        ]
        print(f"=== {brand_id} ===")
        if args.dry_run:
            print(" ".join(cmd))
            continue
        rc = subprocess.call(cmd, cwd=REPO_ROOT)
        if rc != 0:
            failures.append(brand_id)
            continue
        if args.publish:
            pub = [
                sys.executable,
                str(REPO_ROOT / "scripts/marketing/publish_marketing_feed_r2.py"),
                "--brand-id",
                brand_id,
                "--locale",
                args.locale,
            ]
            if subprocess.call(pub, cwd=REPO_ROOT) != 0:
                failures.append(f"{brand_id}:publish")

    if failures:
        print(f"FAILED: {', '.join(failures)}", file=sys.stderr)
        return 1
    print(f"OK: {len(brand_ids)} brand(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
