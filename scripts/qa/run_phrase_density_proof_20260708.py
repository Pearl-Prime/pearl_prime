#!/usr/bin/env python3
"""Phrase-density proof harness — same cells/seed as cohesion_proof_20260708."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "artifacts" / "qa" / "phrase_density_proof_20260708"
SEED = "4242"
REFRAINS = [
    "Peel back the obvious. Something else lives one inch down.",
    "Rest at this stop. You do not have to march past it.",
]

CELLS = [
    {
        "key": "burnout_overwhelm__corporate_managers",
        "persona": "corporate_managers",
        "arc": "config/source_of_truth/master_arcs/corporate_managers__burnout__overwhelm__F006.yaml",
    },
    {
        "key": "burnout_grief__gen_z_professionals",
        "persona": "gen_z_professionals",
        "arc": "config/source_of_truth/master_arcs/gen_z_professionals__burnout__grief__F006.yaml",
    },
    {
        "key": "burnout_overwhelm__healthcare_rns",
        "persona": "healthcare_rns",
        "arc": "config/source_of_truth/master_arcs/healthcare_rns__burnout__overwhelm__F006.yaml",
    },
]


def top_phrase_violations(text: str, cap: int = 12, top_n: int = 10) -> list[dict]:
    from phoenix_v4.quality.book_quality_gate import _repeated_phrase_violations

    viols = _repeated_phrase_violations(text, cap=cap)
    viols.sort(key=lambda v: (-v["count"], -len(v["phrase"])))
    return viols[:top_n]


def run_cell(cell: dict) -> dict:
    render_dir = OUT_DIR / cell["key"]
    render_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "run_pipeline.py"),
        "--topic",
        "burnout",
        "--persona",
        cell["persona"],
        "--arc",
        str(REPO / cell["arc"]),
        "--pipeline-mode",
        "spine",
        "--quality-profile",
        "draft",
        "--seed",
        SEED,
        "--no-job-check",
        "--render-book",
        "--render-dir",
        str(render_dir),
    ]
    print(f"=== rendering {cell['key']} ===", flush=True)
    subprocess.run(cmd, cwd=REPO, check=True, env={**dict(__import__("os").environ), "PYTHONPATH": str(REPO)})

    book_txt = render_dir / "book.txt"
    text = book_txt.read_text(encoding="utf-8")
    (OUT_DIR / f"{cell['key']}.txt").write_text(text, encoding="utf-8")

    bq_path = render_dir / "book_quality_report.json"
    bq = json.loads(bq_path.read_text(encoding="utf-8")) if bq_path.exists() else {}

    viols = top_phrase_violations(text)
    return {
        "key": cell["key"],
        "book_quality_release_band": bq.get("release_band"),
        "repeated_phrase_violations_count": len(
            bq.get("metrics", {}).get("repeated_phrase_violations", viols)
        ),
        "top_repeated_phrase_violations": viols,
        "refrain_counts": {r: text.count(r) for r in REFRAINS},
        "book_quality_hold_reasons": bq.get("hold_reasons", []),
        "render_dir": str(render_dir),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = [run_cell(c) for c in CELLS]
    report = {"seed": SEED, "cells": {r["key"]: r for r in results}}
    (OUT_DIR / "PROOF_REPORT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
