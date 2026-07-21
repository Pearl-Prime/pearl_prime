#!/usr/bin/env python3
"""Report usage percent of catalog/planner knobs (gt30d keeper I007).

Sibling to build_pipeline_matrix.py — measurement only; does not mutate catalog.

Usage:
  PYTHONPATH=. python3 scripts/audit/catalog_knob_usage_analyzer.py
  PYTHONPATH=. python3 scripts/audit/catalog_knob_usage_analyzer.py --out artifacts/qa/knob_usage.tsv
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO = Path(__file__).resolve().parents[2]

# Knobs we care about for English catalog / planner cells
KNOB_KEYS = (
    "book_structure_id",
    "journey_shape_id",
    "motif_id",
    "section_reorder_mode",
    "reframe_profile_id",
    "angle_id",
    "arc_id",
    "runtime_format",
    "pipeline_mode",
    "quality_profile",
    "family_id",
    "engine",
)


def _walk(obj, counts: dict[str, Counter], seen_files: Counter) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in KNOB_KEYS and v is not None and v != "":
                counts[k][str(v)] += 1
                seen_files[k] += 1
            else:
                _walk(v, counts, seen_files)
    elif isinstance(obj, list):
        for item in obj:
            _walk(item, counts, seen_files)


def scan(roots: list[Path]) -> tuple[dict[str, Counter], Counter, int]:
    counts = {k: Counter() for k in KNOB_KEYS}
    file_hits: Counter = Counter()
    files = 0
    if yaml is None:
        return counts, file_hits, 0
    for root in roots:
        if not root.exists():
            continue
        paths = list(root.rglob("*.yaml")) if root.is_dir() else [root]
        for path in paths:
            if not path.is_file():
                continue
            files += 1
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except Exception:
                continue
            before = {k: sum(counts[k].values()) for k in KNOB_KEYS}
            _walk(data, counts, file_hits)
            # file_hits already incremented per key occurrence; OK for %
            _ = before
    return counts, file_hits, files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default="artifacts/qa/archived_session_audit_gt30d_20260722/catalog_knob_usage.tsv",
    )
    args = ap.parse_args()
    roots = [
        REPO / "config/catalog_planning",
        REPO / "config/spines",
        REPO / "config/source_of_truth/master_arcs",
    ]
    counts, file_hits, nfiles = scan(roots)
    out = REPO / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for knob in KNOB_KEYS:
        total = sum(counts[knob].values())
        if total == 0:
            rows.append((knob, "(none)", 0, 0.0, nfiles))
            continue
        for val, n in counts[knob].most_common():
            pct = 100.0 * n / total
            rows.append((knob, val, n, round(pct, 2), nfiles))
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["knob", "value", "count", "pct_of_knob", "yaml_files_scanned"])
        w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows from {nfiles} yaml files)")
    # stdout summary: top value per knob
    for knob in KNOB_KEYS:
        if counts[knob]:
            val, n = counts[knob].most_common(1)[0]
            total = sum(counts[knob].values())
            print(f"  {knob}: top={val!r} {n}/{total} ({100*n/total:.1f}%)")
        else:
            print(f"  {knob}: (no observations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
