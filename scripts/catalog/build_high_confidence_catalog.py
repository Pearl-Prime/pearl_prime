#!/usr/bin/env python3
"""
Worldwide high-confidence allocation catalog builder (Pearl Prime Path X).

**V1.0 / unset:** emits the historical **12-brand** footprint — allocation
cells tagged ``V1.0_matrix_confirmed`` in the PR #1037 TSV (**96** rows:
12 × 4 locales × 2 surfaces).

**V1.1:** emits the ratified **37-brand** expansion — **all** rows from the
same TSV (**296** rows), per AMENDMENT-2026-05-11-V1-1-37-BRAND-ACTIVATION.

Does not call LLMs or touch image pipelines.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.catalog.v1_1_brand_allocation_loader import (  # noqa: E402
    AllocationPlan,
    default_allocation_tsv_path,
    filter_v1_0_cells,
    load_v1_1_brand_allocation_plan,
    summarize_by_locale,
)

OUTPUT_COLUMNS = [
    "brand_id",
    "locale",
    "surface",
    "series_count",
    "episodes_per_series",
    "priority_phase",
    "target_phase",
    "content_units",
]


def _normalize_target_phase(raw: str | None) -> str:
    if raw is None or not str(raw).strip():
        return "V1.0"
    return str(raw).strip()


def select_plan_for_target_phase(
    full_plan: AllocationPlan,
    target_phase: str,
) -> AllocationPlan:
    if target_phase == "V1.1":
        return dict(full_plan)
    return filter_v1_0_cells(full_plan)


def allocation_rows_to_dicts(
    plan: AllocationPlan,
    target_phase: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for (brand_id, locale, surface), cell in sorted(plan.items()):
        sc = int(cell["series_count"])
        ep = int(cell["episodes_per_series"])
        rows.append(
            {
                "brand_id": brand_id,
                "locale": locale,
                "surface": surface,
                "series_count": sc,
                "episodes_per_series": ep,
                "priority_phase": cell["priority_phase"],
                "target_phase": target_phase,
                "content_units": sc * ep,
            }
        )
    return rows


def write_allocation_catalog_tsv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def build_catalog(
    *,
    target_phase: str,
    allocation_tsv: Path,
    output_tsv: Path,
    write_summary_json: Path | None = None,
) -> dict[str, Any]:
    full = load_v1_1_brand_allocation_plan(allocation_tsv)
    selected = select_plan_for_target_phase(full, target_phase)
    rows = allocation_rows_to_dicts(selected, target_phase)
    write_allocation_catalog_tsv(rows, output_tsv)

    by_locale = summarize_by_locale(selected)
    brand_ids = {b for (b, _l, _s) in selected}
    summary: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target_phase": target_phase,
        "allocation_source": str(allocation_tsv),
        "row_count": len(rows),
        "distinct_brands": len(brand_ids),
        "rows_by_locale": by_locale,
        "priority_phase_counts": dict(Counter(c["priority_phase"] for c in selected.values())),
    }
    if write_summary_json:
        write_summary_json.parent.mkdir(parents=True, exist_ok=True)
        with open(write_summary_json, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2, ensure_ascii=False)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Path X allocation catalog rows from PR #1037 TSV."
    )
    parser.add_argument(
        "--target-phase",
        default="V1.0",
        help='Catalog phase gate: "V1.0" (12-brand matrix cells), "V1.1" (all 37 brands).',
    )
    parser.add_argument(
        "--allocation-tsv",
        type=Path,
        default=None,
        help="Override path to worldwide_catalog_37_brand_allocation_plan TSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output TSV path (default under artifacts/catalog/).",
    )
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=None,
        help="Optional JSON summary path.",
    )
    args = parser.parse_args()

    root = _REPO_ROOT
    tsv = args.allocation_tsv or default_allocation_tsv_path(root)
    phase = _normalize_target_phase(args.target_phase)
    safe = phase.replace(".", "_")
    out = args.output or (
        root / "artifacts" / "catalog" / f"path_x_allocation_catalog_{safe}.tsv"
    )
    summary_path = args.summary_json or (
        root / "artifacts" / "catalog" / f"path_x_allocation_catalog_{safe}_summary.json"
    )

    s = build_catalog(
        target_phase=phase,
        allocation_tsv=tsv,
        output_tsv=out,
        write_summary_json=summary_path,
    )
    print(json.dumps({"output": str(out), "summary": s}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
