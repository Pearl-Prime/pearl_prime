#!/usr/bin/env python3
"""Hard gate: every store_series.id must map to exactly one distinct store_series.name.

KDP's and Google Play's series-linking both key series-page grouping on an exact-match
series-name string (see artifacts/research/SERIES_TITLES_SUBTITLES_PLATFORM_SEO_RESEARCH_2026-07-23.md
§2.1/§2.2). store_series.name on Waystream book plans has no canonical generator — every
value is hand/LLM-authored per book — so nothing has ever verified two books sharing a
store_series.id actually carry the identical name string until this gate.

WARN (non-blocking) on: plans with no store_series at all, and duplicate installment_number
values within one store_series.id. Neither is a hard failure — not every book needs a series,
and installment-number collisions are an editorial concern, not a storefront-breaking one.

  PYTHONPATH=. python3 scripts/ci/check_store_series_name_consistency.py
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
BRAND = "way_stream_sanctuary"
DEFAULT_PLANS_DIR = REPO / "config/source_of_truth/book_plans_en_us"


def _load_plans(plans_dir: Path) -> list[dict[str, Any]]:
    out = []
    for f in sorted(plans_dir.glob(f"{BRAND}__*.yaml")):
        data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict):
            data["_source_path"] = str(f)
            out.append(data)
    return out


def check_store_series_name_consistency(
    plans: list[dict[str, Any]],
) -> tuple[bool, list[str], list[str]]:
    """Return (ok, hard_failures, warnings) for the given loaded plan dicts.

    ``ok`` is False only when a store_series.id maps to more than one distinct name.
    """
    names_by_id: dict[str, set[str]] = defaultdict(set)
    paths_by_id: dict[str, list[str]] = defaultdict(list)
    installments_by_id: dict[str, list[int]] = defaultdict(list)
    no_series_count = 0

    for plan in plans:
        store_series = plan.get("store_series")
        if not isinstance(store_series, dict) or not store_series.get("id"):
            no_series_count += 1
            continue
        sid = str(store_series["id"])
        name = str(store_series.get("name") or "").strip()
        names_by_id[sid].add(name)
        paths_by_id[sid].append(plan.get("_source_path", ""))
        inst = plan.get("installment_number")
        if inst is not None:
            installments_by_id[sid].append(int(inst))

    hard_failures: list[str] = []
    for sid, names in sorted(names_by_id.items()):
        if len(names) > 1:
            hard_failures.append(
                f"store_series.id={sid!r} has {len(names)} distinct names: {sorted(names)} "
                f"across {paths_by_id[sid]}"
            )

    warnings: list[str] = []
    if no_series_count:
        warnings.append(f"{no_series_count} plan(s) have no store_series block")
    for sid, insts in sorted(installments_by_id.items()):
        dups = {n: c for n, c in Counter(insts).items() if c > 1}
        if dups:
            warnings.append(f"store_series.id={sid!r} has duplicate installment_number(s): {dups}")

    return (not hard_failures, hard_failures, warnings)


def main() -> int:
    ap = argparse.ArgumentParser(description="Check store_series.id -> name exact-match consistency")
    ap.add_argument("--plans-dir", type=Path, default=DEFAULT_PLANS_DIR)
    args = ap.parse_args()

    plans = _load_plans(args.plans_dir)
    ok, hard_failures, warnings = check_store_series_name_consistency(plans)

    for w in warnings:
        print(f"WARN: {w}")
    if not ok:
        for f in hard_failures:
            print(f"FAIL: {f}")
        print(f"STORE SERIES NAME CONSISTENCY GATE: {len(hard_failures)} violation(s) — blocking")
        return 1

    series_count = len({p["store_series"]["id"] for p in plans if isinstance(p.get("store_series"), dict) and p["store_series"].get("id")})
    print(f"OK store_series name consistency (series={series_count}, plans={len(plans)}, warnings={len(warnings)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
