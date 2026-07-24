#!/usr/bin/env python3
"""Renumber installment_number within each store_series.id to remove duplicates.

Waystream series intentionally bundle multiple internal topic-threads under one
reader-facing store_series (e.g. "Worth & Limits — for Managers" spans boundaries +
imposter_syndrome + self_worth). Each thread was numbered independently (1..N per
topic), which collides once the storefront series page displays every book in the
series together — scripts/ci/check_store_series_name_consistency.py WARNs on this.

This script renumbers each series' books sequentially (1..N) in a stable order —
sorted by (original installment_number, topic, engine) — so relative thread order
is preserved and the result is deterministic/idempotent. Only the
``installment_number:`` line is touched (surgical line-replace, not a full YAML
round-trip) so nothing else in a plan file changes.

  PYTHONPATH=. python3 scripts/catalog/fix_store_series_installment_numbers.py --dry-run
  PYTHONPATH=. python3 scripts/catalog/fix_store_series_installment_numbers.py --apply
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
BRAND = "way_stream_sanctuary"
DEFAULT_PLANS_DIR = REPO / "config/source_of_truth/book_plans_en_us"

_INSTALLMENT_LINE_RE = re.compile(r"^installment_number:\s*\d+\s*$", re.M)


def _topic_from_filename(path: Path) -> str:
    # way_stream_sanctuary__default_teacher__<persona>__<topic>__<engine>[__1hr].yaml
    parts = path.stem.split("__")
    return parts[3] if len(parts) > 3 else ""


def _load_plans(plans_dir: Path) -> list[dict[str, Any]]:
    out = []
    for f in sorted(plans_dir.glob(f"{BRAND}__*.yaml")):
        data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict):
            data["_source_path"] = f
            out.append(data)
    return out


def compute_renumber_plan(plans: list[dict[str, Any]]) -> dict[Path, tuple[int, int]]:
    """Return {path: (old_installment_number, new_installment_number)} for every
    book whose installment_number changes. Books already correctly numbered are
    omitted so the diff only touches what actually needs fixing."""
    by_series: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for plan in plans:
        store_series = plan.get("store_series")
        if not isinstance(store_series, dict) or not store_series.get("id"):
            continue
        by_series[store_series["id"]].append(plan)

    changes: dict[Path, tuple[int, int]] = {}
    for sid, group in by_series.items():
        counts: dict[int, int] = defaultdict(int)
        for p in group:
            inst = p.get("installment_number")
            if inst is not None:
                counts[int(inst)] += 1
        if not any(c > 1 for c in counts.values()):
            continue  # this series has no collision — leave it alone entirely

        ordered = sorted(
            group,
            key=lambda p: (
                int(p.get("installment_number") or 0),
                _topic_from_filename(p["_source_path"]),
                str(p.get("engine") or ""),
                p["_source_path"].name,
            ),
        )
        for new_num, plan in enumerate(ordered, start=1):
            old_num = int(plan.get("installment_number") or 0)
            if old_num != new_num:
                changes[plan["_source_path"]] = (old_num, new_num)
    return changes


def apply_changes(changes: dict[Path, tuple[int, int]]) -> None:
    for path, (_old, new_num) in changes.items():
        text = path.read_text(encoding="utf-8")
        new_text, n = _INSTALLMENT_LINE_RE.subn(f"installment_number: {new_num}", text, count=1)
        if n != 1:
            raise RuntimeError(f"could not find installment_number line in {path}")
        path.write_text(new_text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Renumber colliding installment_number within Waystream store_series")
    ap.add_argument("--plans-dir", type=Path, default=DEFAULT_PLANS_DIR)
    ap.add_argument("--apply", action="store_true", help="write changes (default is dry-run)")
    args = ap.parse_args()

    plans = _load_plans(args.plans_dir)
    changes = compute_renumber_plan(plans)

    for path, (old, new) in sorted(changes.items()):
        print(f"{'APPLY' if args.apply else 'WOULD CHANGE'}: {path.name}: installment_number {old} -> {new}")

    print(f"\n{len(changes)} file(s) {'changed' if args.apply else 'would change'} "
          f"across {len({p.get('store_series', {}).get('id') for p in plans if isinstance(p.get('store_series'), dict)})} series")

    if args.apply:
        apply_changes(changes)
        print("Applied.")
    else:
        print("Dry-run only — pass --apply to write changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
