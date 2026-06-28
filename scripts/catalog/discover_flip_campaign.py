#!/usr/bin/env python3
"""Discover en_US brands with skeleton plans ready to flip (arc+atoms present).

Emits JSON matrix for catalog-flip-campaign.yml:
  {"include": [{"brand": "...", "pending": N}, ...]}

  PYTHONPATH=. python3 scripts/catalog/discover_flip_campaign.py
  PYTHONPATH=. python3 scripts/catalog/discover_flip_campaign.py --json-only
  PYTHONPATH=. python3 scripts/catalog/discover_flip_campaign.py --brands warrior_calm
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
PLANS = REPO / "config/source_of_truth/book_plans_en_us"
ARCS = REPO / "config/source_of_truth/master_arcs"
ATOMS = REPO / "atoms"


def _load(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _arc_set() -> set[tuple[str, str, str]]:
    out: set[tuple[str, str, str]] = set()
    for p in ARCS.glob("*.yaml"):
        parts = p.stem.split("__")
        if len(parts) == 4:
            out.add((parts[0], parts[1], parts[2]))
    return out


def _parse_stem(stem: str) -> tuple[str, str, str, str, str] | None:
    is_1hr = stem.endswith("__1hr")
    s = stem[:-5] if is_1hr else stem
    parts = s.split("__")
    if len(parts) < 5:
        return None
    return parts[0], parts[1], parts[2], parts[3], parts[4]


def _flippable(plan: dict, arc_set: set[tuple[str, str, str]]) -> bool:
    if plan.get("_needs_authoring") is not True:
        return False
    bid = plan.get("book_id") or ""
    parsed = _parse_stem(bid)
    if not parsed:
        return False
    _brand, _teacher, persona, topic, engine = parsed
    if (persona, topic, engine) not in arc_set:
        return False
    p = ATOMS / persona / topic / engine / "CANONICAL.txt"
    return p.is_file() and p.stat().st_size > 100


def pending_by_brand(brand_filter: set[str] | None) -> dict[str, int]:
    arc_set = _arc_set()
    counts: Counter[str] = Counter()
    for f in PLANS.glob("*.yaml"):
        plan = _load(f)
        bid = plan.get("book_id") or f.stem
        brand = bid.split("__")[0]
        if brand_filter and brand not in brand_filter:
            continue
        if _flippable(plan, arc_set):
            counts[brand] += 1
    return dict(counts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brands", default="", help="Space-separated brand ids (default: all with pending)")
    ap.add_argument("--json-only", action="store_true")
    args = ap.parse_args()

    brand_filter = set(args.brands.split()) if args.brands.strip() else None
    counts = pending_by_brand(brand_filter)
    include = [{"brand": b, "pending": n} for b, n in sorted(counts.items(), key=lambda x: -x[1]) if n > 0]
    payload = {"include": include}

    if args.json_only:
        print(json.dumps(payload))
    else:
        total = sum(r["pending"] for r in include)
        print(f"brands: {len(include)} pending flips: {total}")
        for row in include[:20]:
            print(f"  {row['brand']}: {row['pending']}")
        if len(include) > 20:
            print(f"  ... +{len(include) - 20} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
