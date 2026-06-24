#!/usr/bin/env python3
"""Post-batch Waystream handoff: cadence → deliveries → storefront → verify.

Run after batch_waystream_epubs.py completes (778 ok + 22 atom-gap fails is expected):

  PYTHONPATH=. python3 scripts/release/finish_waystream_handoff.py

Steps:
  1. Inventory audit
  2. Cadence reslice if W26 amazon_kdp exceeds cap
  3. dedupe-w26 (remove post-reslice duplicates)
  4. gen_brand_deliveries → brand_handoff_dashboard.html real files
  5. project_waystream_skus → storefront sample catalog
  6. verify_resync (metadata parity gate)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BRAND_DIR = REPO / "artifacts/weekly_packages/way_stream_sanctuary"
FROM_WEEK = "2026-W26"
PLATFORM = "amazon_kdp"


def _run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd), flush=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    return subprocess.run(cmd, cwd=str(REPO), check=check, env=env)


def _w26_count() -> int:
    kdp = BRAND_DIR / FROM_WEEK / PLATFORM
    if not kdp.is_dir():
        return 0
    return len(list(kdp.glob("*.epub")))


def _cap_max() -> int:
    import yaml

    safe = yaml.safe_load(
        (REPO / "config/release_velocity/safe_velocity.yaml").read_text(encoding="utf-8")
    ) or {}
    per_week = ((safe.get("google_play_books") or {}).get("new_imprint") or {}).get("per_week")
    return int(per_week[1]) if per_week else 20


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-reslice", action="store_true")
    ap.add_argument("--skip-storefront", action="store_true")
    args = ap.parse_args()
    py = sys.executable

    _run([py, "scripts/release/waystream_epub_inventory.py", "audit"], check=True)

    n26 = _w26_count()
    cap = _cap_max()
    print(f"W26 {PLATFORM}: {n26} EPUBs (cap_max={cap})", flush=True)
    if not args.skip_reslice and n26 > cap:
        _run(
            [
                py,
                "scripts/release/cadence_reslice_deliveries.py",
                "--brand-dir",
                str(BRAND_DIR),
                "--from-week",
                FROM_WEEK,
                "--platform",
                PLATFORM,
                "--lane",
                "en",
            ],
            check=True,
        )
        _run([py, "scripts/release/waystream_epub_inventory.py", "dedupe-w26"], check=True)

    _run([py, "scripts/onboarding/gen_brand_deliveries.py"], check=True)
    _run([py, "scripts/release/upload_waystream_deliveries_r2.py"], check=True)

    if not args.skip_storefront:
        _run([py, "scripts/storefront/project_waystream_skus.py"], check=True)

    _run([py, "scripts/publish/waystream_covers/verify_resync.py"], check=True)
    _run([py, "scripts/release/waystream_epub_inventory.py", "manifest"], check=True)

    feed = REPO / "brand-wizard-app/public/brand_deliveries/way_stream_sanctuary.json"
    sku_out = REPO / "storefront/public/app/sample_catalog.way_stream_sanctuary.en-US.json"
    summary = {
        "brand_deliveries": feed.is_file(),
        "storefront_skus": sku_out.is_file(),
        "storefront_sku_count": len(json.loads(sku_out.read_text())) if sku_out.is_file() else 0,
    }
    print("handoff complete:", json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
