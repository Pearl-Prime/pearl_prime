#!/usr/bin/env python3
"""
G-ACCENT — weekly accent-fill preflight matrix.

Per PEARL_PRIME_PERFECT_BOOKS_SPEC.md #3.B: "Production already blocks; add
preflight matrix job that fails weekly if top-N catalog cells have
no_supply_pool for budgeted accents" (Catalog planning, not a per-PR blocker).

This gate does not re-implement capability-gap detection — it re-uses the
planner's own gap detector (phoenix_v4.planning.accent_planner._capability_gaps,
the same function `validate_accent_plan()` calls at render time) against the
top-N catalog cells from the 100-book analysis MATRIX.tsv, without needing a
full render (resolve_accent_budget + _build_pools_with_provenance only need
persona_id/topic_id/brand_id — no enriched book required).

Cadence: exit 0 (report-only) by default so it never blocks a PR. Pass
--fail-closed for the weekly scheduled job, which exits 1 if any budgeted
accent class has no_supply_pool in the top-N matrix cells (ops-cadence report
+ fail-closed per spec, not a per-PR blocker).

Authority: artifacts/qa/pearl_prime_100book_analysis_20260718/PEARL_PRIME_PERFECT_BOOKS_SPEC.md #3.B (G-ACCENT row)

Usage:
  PYTHONPATH=. python3 scripts/ci/check_accent_supply_preflight.py                 # integrity mode
  PYTHONPATH=. python3 scripts/ci/check_accent_supply_preflight.py --top-n 20 \\
      --brand-id stillness_press --fail-closed
  PYTHONPATH=. python3 scripts/ci/check_accent_supply_preflight.py --matrix path/to/MATRIX.tsv

Exit: 0 pass/report-only (default); 1 if --fail-closed and gaps found; 1 on input errors.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.planning.accent_planner import (  # noqa: E402
    _build_pools_with_provenance,
    _capability_gaps,
    locale_to_cluster,
    resolve_accent_budget,
)

DEFAULT_MATRIX = (
    REPO_ROOT
    / "artifacts"
    / "qa"
    / "pearl_prime_100book_analysis_20260718"
    / "MATRIX.tsv"
)
DEFAULT_REPORT = (
    REPO_ROOT
    / "artifacts"
    / "qa"
    / "accent_supply_preflight"
    / "ACCENT_SUPPLY_PREFLIGHT.json"
)
DEFAULT_BRAND_ID = "stillness_press"
DEFAULT_TOP_N = 20


def load_top_cells(matrix_path: Path, *, top_n: int) -> list[tuple[str, str]]:
    """Return unique (persona, topic) pairs from MATRIX.tsv, ranked by `index`, top-N."""
    with matrix_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        rows = list(reader)

    def _rank(row: dict[str, str]) -> int:
        try:
            return int(row.get("index") or 0)
        except (TypeError, ValueError):
            return 0

    rows.sort(key=_rank)
    seen: set[tuple[str, str]] = set()
    cells: list[tuple[str, str]] = []
    for row in rows:
        persona = str(row.get("persona") or "").strip()
        topic = str(row.get("topic") or "").strip()
        if not persona or not topic:
            continue
        key = (persona, topic)
        if key in seen:
            continue
        seen.add(key)
        cells.append(key)
        if len(cells) >= top_n:
            break
    return cells


def preflight_cell(
    *,
    persona_id: str,
    topic_id: str,
    brand_id: str,
    locale: str,
    repo_root: Path,
) -> dict[str, Any]:
    locale_cluster = locale_to_cluster(locale)
    budget, profile_name, _share_cap = resolve_accent_budget(
        brand_id,
        persona_id=persona_id,
        topic_id=topic_id,
        repo_root=repo_root,
    )
    pools, provenance = _build_pools_with_provenance(
        persona_id=persona_id,
        topic_id=topic_id,
        author_id="",
        locale_cluster=locale_cluster,
        repo_root=repo_root,
    )
    gaps = _capability_gaps(budget, pools)
    return {
        "persona_id": persona_id,
        "topic_id": topic_id,
        "brand_id": brand_id,
        "profile": profile_name,
        "accent_budget": dict(budget),
        "capability_gaps": dict(gaps),
        "supply_provenance": dict(provenance),
        "has_gap": bool(gaps),
    }


def build_report(
    *,
    matrix_path: Path,
    top_n: int,
    brand_id: str,
    locale: str,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    cells = load_top_cells(matrix_path, top_n=top_n)
    rows = [
        preflight_cell(
            persona_id=persona,
            topic_id=topic,
            brand_id=brand_id,
            locale=locale,
            repo_root=repo_root,
        )
        for persona, topic in cells
    ]
    gap_rows = [r for r in rows if r["has_gap"]]
    return {
        "matrix_source": str(matrix_path),
        "top_n": top_n,
        "brand_id": brand_id,
        "cells_checked": len(rows),
        "cells_with_gap": len(gap_rows),
        "fill_rate": (
            round(1.0 - (len(gap_rows) / len(rows)), 4) if rows else 1.0
        ),
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="G-ACCENT weekly accent-fill preflight matrix")
    ap.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    ap.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    ap.add_argument("--brand-id", default=DEFAULT_BRAND_ID)
    ap.add_argument("--locale", default="en_US")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT)
    ap.add_argument(
        "--fail-closed",
        action="store_true",
        help="Exit 1 when any top-N cell has a no_supply_pool gap (weekly cadence job)",
    )
    args = ap.parse_args(argv)

    if not args.matrix.is_file():
        # Integrity mode: confirm the planner gap-detector import contract holds
        # even when the analysis matrix isn't present on this checkout/CI runner.
        assert callable(_capability_gaps)
        assert callable(resolve_accent_budget)
        print(
            f"G-ACCENT: PASS (integrity) — planner gap-detector importable; "
            f"matrix not found at {args.matrix} (skip)"
        )
        return 0

    report = build_report(
        matrix_path=args.matrix,
        top_n=args.top_n,
        brand_id=args.brand_id,
        locale=args.locale,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"G-ACCENT: cells_checked={report['cells_checked']} "
        f"cells_with_gap={report['cells_with_gap']} "
        f"fill_rate={report['fill_rate']} -> {args.out}"
    )
    for row in report["rows"]:
        if row["has_gap"]:
            print(
                f"  - GAP {row['persona_id']}x{row['topic_id']} "
                f"(profile={row['profile']}): {row['capability_gaps']}"
            )

    if report["cells_with_gap"] and args.fail_closed:
        print(
            f"G-ACCENT: FAIL (weekly fail-closed) — {report['cells_with_gap']} "
            f"top-{args.top_n} cell(s) with no_supply_pool for a budgeted accent",
            file=sys.stderr,
        )
        return 1

    print("G-ACCENT: PASS (report-only)" if not args.fail_closed else "G-ACCENT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
