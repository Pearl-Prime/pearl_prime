#!/usr/bin/env python3
"""Waystream wrapper — delegates to brand_title_regen (Formula 4 contract).

  PYTHONPATH=. python3 scripts/catalog/waystream_subtitle_regen.py --dry-run
  PYTHONPATH=. python3 scripts/catalog/waystream_subtitle_regen.py --apply
"""
from __future__ import annotations

import argparse
import sys

from scripts.catalog.brand_title_regen import RegenConfig, run_regen


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--batch", choices=["a", "b"], default=None)
    args = ap.parse_args()

    cfg = RegenConfig(
        brand_id="way_stream_sanctuary",
        locale_dir="en_us",
        authored_only=True,
    )
    if args.analyze:
        sys.exit(run_regen(cfg, dry_run=True, batch=args.batch, analyze_only=True))
    if not args.dry_run and not args.apply:
        ap.error("specify --dry-run, --apply, or --analyze")
    sys.exit(run_regen(cfg, dry_run=args.dry_run, batch=args.batch))


if __name__ == "__main__":
    main()
