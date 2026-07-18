#!/usr/bin/env python3
"""ITE CI: Composite score validation (T-19).
Authority: specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md §12.3, §17.1
Input: --chapter-dir containing ite_report.json
Exit 1 if ITE_score < 0.50."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WEIGHTS = {
    "vt_parasympathetic": 0.30,
    "vt_processing": 0.25,
    "vt_somatic": 0.25,
    "vt_stealth": 0.20,
}
PASS_THRESHOLD = 0.50


def compute_composite(dimensions: dict) -> float:
    score = 0.0
    for dim, weight in WEIGHTS.items():
        score += dimensions.get(dim, 0.0) * weight
    return round(score, 4)


def main() -> int:
    ap = argparse.ArgumentParser(description="ITE composite score check")
    ap.add_argument("--chapter-dir", required=True, help="Chapter output directory")
    args = ap.parse_args()

    report_path = Path(args.chapter_dir) / "ite_report.json"
    if not report_path.exists():
        print("No ite_report.json found; skipping composite check")
        return 0

    report = json.loads(report_path.read_text(encoding="utf-8"))
    dimensions = report.get("dimensions", {})
    ite_score = report.get("ite_score")

    if ite_score is None:
        ite_score = compute_composite(dimensions)

    passed = ite_score >= PASS_THRESHOLD
    result = {
        "gate": "ite_composite",
        "ite_score": ite_score,
        "dimensions": dimensions,
        "threshold": PASS_THRESHOLD,
        "pass": passed,
    }
    print(json.dumps(result, indent=2))

    if not passed:
        print(
            f"T-19 FAIL: ITE_score {ite_score:.3f} < {PASS_THRESHOLD}",
            file=sys.stderr,
        )
        return 1

    print(f"T-19 PASS: ITE_score {ite_score:.3f} >= {PASS_THRESHOLD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
