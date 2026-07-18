#!/usr/bin/env python3
"""Delete locale book/series plans for market-suppressed topics.

Governance-safe: default --max-files 50 (mass_deletion gate). For hu_HU the
fan-out should prefer generation-time topic fit; this script cleans orphans.

  PYTHONPATH=. python3 scripts/catalog/prune_suppressed_locale_plans.py --locale hu_HU --dry-run
  PYTHONPATH=. python3 scripts/catalog/prune_suppressed_locale_plans.py --locale hu_HU --list-out /tmp/prune.txt
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.catalog.locale_paths import normalize_lane_id, plan_dirs
from scripts.catalog.market_topic_fit import suppress_topics_for_lane

ROOT = Path(__file__).resolve().parents[2]


def _topic_from_stem(stem: str) -> str:
    parts = stem.replace("__1hr", "").split("__")
    return parts[3] if len(parts) > 3 else ""


def collect_suppressed_paths(lane_id: str) -> list[Path]:
    lane_id = normalize_lane_id(lane_id)
    suppressed = suppress_topics_for_lane(lane_id)
    if not suppressed:
        raise SystemExit(f"no suppress list for {lane_id}")
    book_dir, series_dir = plan_dirs(ROOT, lane_id)
    out: list[Path] = []
    for d in (book_dir, series_dir):
        if not d.is_dir():
            continue
        for f in d.glob("*.yaml"):
            if _topic_from_stem(f.stem) in suppressed:
                out.append(f)
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--locale", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--list-out", type=Path, default=None)
    ap.add_argument("--max-files", type=int, default=50, help="Max deletions per invocation (governance gate)")
    args = ap.parse_args()

    paths = collect_suppressed_paths(args.locale)
    batch = paths[: args.max_files]
    print(f"{args.locale}: suppressed_total={len(paths)} batch={len(batch)}")
    if args.list_out:
        args.list_out.parent.mkdir(parents=True, exist_ok=True)
        args.list_out.write_text("\n".join(str(p.relative_to(ROOT)) for p in batch) + "\n", encoding="utf-8")
        print(f"Wrote {args.list_out}")

    if args.dry_run:
        for p in batch[:10]:
            print(f"  would delete {p.relative_to(ROOT)}")
        if len(batch) > 10:
            print(f"  ... +{len(batch) - 10} more in batch")
        return 0

    for p in batch:
        p.unlink()
    print(f"Deleted {len(batch)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
