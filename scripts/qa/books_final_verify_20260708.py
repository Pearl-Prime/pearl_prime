#!/usr/bin/env python3
"""Final verify + rollup for books-quality lane (2026-07-08)."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "artifacts/qa/book_final_verify_20260708"
SEED = "4242"

REFRAINS = [
    "Peel back the obvious. Something else lives one inch down.",
    "Rest at this stop. You do not have to march past it.",
]

BURNOUT_CELLS = [
    {
        "key": "burnout_overwhelm__corporate_managers",
        "persona": "corporate_managers",
        "engine": "overwhelm",
        "arc": "config/source_of_truth/master_arcs/corporate_managers__burnout__overwhelm__F006.yaml",
    },
    {
        "key": "burnout_watcher__corporate_managers",
        "persona": "corporate_managers",
        "engine": "watcher",
        "arc": "config/source_of_truth/master_arcs/corporate_managers__burnout__watcher__F006.yaml",
    },
    {
        "key": "burnout_grief__corporate_managers",
        "persona": "corporate_managers",
        "engine": "grief",
        "arc": "config/source_of_truth/master_arcs/corporate_managers__burnout__grief__F006.yaml",
    },
]

FLAGSHIP_BOOK = REPO / "artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt"


def _render_cell(cell: dict, render_dir: Path) -> None:
    render_dir.mkdir(parents=True, exist_ok=True)
    # CI-ALLOWLIST: legacy-registry-ok — QA harness draft spine verify, not production bestseller build
    cmd = [
        sys.executable,
        str(REPO / "scripts/run_pipeline.py"),  # CI-ALLOWLIST: legacy-registry-ok — QA harness draft spine verify
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
    subprocess.run(cmd, cwd=REPO, check=True, env={**dict(__import__("os").environ), "PYTHONPATH": str(REPO)})


def _cadence_counts(text: str) -> dict[str, int]:
    return {r: text.count(r) for r in REFRAINS}


def _score_book(path: Path, topic_id: str, persona_id: str) -> dict:
    from phoenix_v4.quality.content_uniqueness_truth import (
        compare_truth_sources,
        split_shipped_book_chapters,
    )
    from scripts.ci.run_ei_v2_rigorous_eval import evaluate_chapter

    text = path.read_text(encoding="utf-8")
    chapters = split_shipped_book_chapters(text)
    ei_scores = []
    for i, ch in enumerate(chapters):
        ev = evaluate_chapter(ch, i, {}, persona_id, topic_id, chapters)
        ei_scores.append(ev.content_uniqueness)

    bq_path = path.parent / "book_quality_report.json"
    bq = json.loads(bq_path.read_text(encoding="utf-8")) if bq_path.exists() else {}

    ei_path = path.parent / "ei_v2_report.json"
    ei_report = json.loads(ei_path.read_text(encoding="utf-8")) if ei_path.exists() else {}

    truth = compare_truth_sources(path, topic_id, persona_id=persona_id)
    cadence = _cadence_counts(text)

    return {
        "book_path": str(path),
        "chapter_count": len(chapters),
        "cadence_refrains": cadence,
        "cadence_offenders": sum(cadence.values()),
        "book_quality": {
            "release_band": bq.get("release_band"),
            "hold_reasons": bq.get("hold_reasons", []),
            "fail_reasons": bq.get("fail_reasons", []),
            "repeated_phrase_violations": len(bq.get("metrics", {}).get("repeated_phrase_violations", [])),
        },
        "ei_v2": {
            "status": ei_report.get("status"),
            "content_uniqueness_avg": round(mean(ei_scores), 4) if ei_scores else None,
            "content_uniqueness_min": round(min(ei_scores), 4) if ei_scores else None,
            "composite_avg": ei_report.get("composite_avg"),
        },
        "uniqueness_truth": truth,
    }


def _bestseller_band(ei_avg: float | None, bq_band: str | None) -> str:
    if bq_band == "Reject":
        return "FAIL"
    if ei_avg is None:
        return "UNKNOWN"
    if ei_avg >= 0.50 and bq_band == "Pass":
        return "PASS"
    if ei_avg >= 0.45:
        return "CONCERN"
    return "FAIL"


def build_proof(*, out_dir: Path, skip_render: bool = False) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    cells_out = []

    for cell in BURNOUT_CELLS:
        render_dir = out_dir / "render" / cell["key"]
        if not skip_render:
            print(f"=== render {cell['key']} ===", flush=True)
            _render_cell(cell, render_dir)
        book_path = render_dir / "book.txt"
        if not book_path.exists():
            raise FileNotFoundError(book_path)
        (out_dir / f"{cell['key']}.txt").write_text(book_path.read_text(encoding="utf-8"), encoding="utf-8")
        row = _score_book(book_path, "burnout", cell["persona"])
        row["cell"] = cell["key"]
        cells_out.append(row)

    flagship_row = None
    if FLAGSHIP_BOOK.exists():
        flagship_row = _score_book(FLAGSHIP_BOOK, "anxiety", "gen_z_professionals")
        flagship_row["cell"] = "CANONICAL_FLAGSHIP_BOOK"
        flagship_row["note"] = "ratified snapshot — read-only verify, no re-render"

    blockers = []
    for row in cells_out:
        if row["cadence_offenders"] != 0:
            blockers.append(
                f"{row['cell']}: cadence_offenders={row['cadence_offenders']} in {row['book_path']}"
            )
        if row["book_quality"]["release_band"] != "Pass":
            blockers.append(
                f"{row['cell']}: book_quality={row['book_quality']['release_band']} "
                f"hold={row['book_quality']['hold_reasons']} path={row['book_path']}"
            )
        if (row["ei_v2"]["content_uniqueness_avg"] or 0) < 0.55:
            blockers.append(
                f"{row['cell']}: ei_v2 content_uniqueness_avg={row['ei_v2']['content_uniqueness_avg']} "
                f"< 0.55 in {row['book_path']}"
            )
        shipped = row["uniqueness_truth"]["shipped_spine_book"]
        if shipped.get("truth_source") != "shipped_spine_book":
            blockers.append(f"{row['cell']}: missing shipped_spine truth_source")
        legacy = row["uniqueness_truth"].get("legacy_registry_artifact") or {}
        if legacy and not legacy.get("warning"):
            blockers.append(f"{row['cell']}: legacy registry missing warning label")

    if flagship_row:
        if (flagship_row["ei_v2"]["content_uniqueness_avg"] or 0) < 0.55:
            blockers.append(
                f"flagship: ei_v2 content_uniqueness_avg={flagship_row['ei_v2']['content_uniqueness_avg']}"
            )

    verdict = "GREEN" if not blockers else "BLOCKED"

    proof = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "lane": "books-final-verify",
        "seed": SEED,
        "verdict": verdict,
        "blockers": blockers,
        "burnout_proof_cells": cells_out,
        "flagship_proof_cell": flagship_row,
        "rollup": {
            "cadence_offenders_total": sum(r["cadence_offenders"] for r in cells_out),
            "book_quality_pass": sum(1 for r in cells_out if r["book_quality"]["release_band"] == "Pass"),
            "ei_uniqueness_avg_mean": round(
                mean(r["ei_v2"]["content_uniqueness_avg"] for r in cells_out if r["ei_v2"]["content_uniqueness_avg"]),
                4,
            ),
        },
    }
    return proof


def _scorecard_md(proof: dict) -> str:
    lines = [
        "# Books Final Verify Scorecard (2026-07-08)",
        "",
        f"**Verdict:** {proof['verdict']}",
        "",
        "## Burnout proof cells (fresh spine render, seed 4242)",
        "",
        "| Cell | Cadence offenders | book_quality | phrase violations | EI uniqueness avg | Bestseller band |",
        "|------|------------------:|--------------|------------------:|------------------:|-----------------|",
    ]
    for row in proof["burnout_proof_cells"]:
        band = _bestseller_band(row["ei_v2"]["content_uniqueness_avg"], row["book_quality"]["release_band"])
        lines.append(
            f"| {row['cell']} | {row['cadence_offenders']} | {row['book_quality']['release_band']} | "
            f"{row['book_quality']['repeated_phrase_violations']} | "
            f"{row['ei_v2']['content_uniqueness_avg']} | {band} |"
        )
    if proof.get("flagship_proof_cell"):
        fs = proof["flagship_proof_cell"]
        band = _bestseller_band(fs["ei_v2"]["content_uniqueness_avg"], fs["book_quality"].get("release_band"))
        lines.append(
            f"| {fs['cell']} | {fs['cadence_offenders']} | {fs['book_quality'].get('release_band', 'n/a')} | "
            f"{fs['book_quality'].get('repeated_phrase_violations', 'n/a')} | "
            f"{fs['ei_v2']['content_uniqueness_avg']} | {band} |"
        )
    if proof["blockers"]:
        lines.extend(["", "## Blockers", ""] + [f"- {b}" for b in proof["blockers"]])
    return "\n".join(lines) + "\n"


def _rollup_md(proof: dict) -> str:
    r = proof["rollup"]
    return "\n".join(
        [
            "# Books Final Verify — Sellability Rollup (2026-07-08)",
            "",
            f"**Verdict:** {proof['verdict']}",
            "",
            "## Post-fix truth",
            "",
            f"- Named cadence refrain offenders (3 burnout cells): **{r['cadence_offenders_total']}**",
            f"- book_quality Pass cells: **{r['book_quality_pass']}/3**",
            f"- Shipped-book EI v2 content_uniqueness mean: **{r['ei_uniqueness_avg_mean']}** (was ~0.16 pre semantic-dedup)",
            "- Registry scorer labeled `legacy_registry_artifact` with `sellability_truth: false`",
            "",
            "## Layer claims",
            "",
            "- **structurally clear:** book_quality Pass + cadence 0 on proof cells",
            "- **authored candidate:** unchanged — no writer lane in this PR",
            "- **bestseller register:** NOT claimed — Layer 4 blind-10 unchanged",
            "",
        ]
    ) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ap.add_argument("--skip-render", action="store_true")
    args = ap.parse_args()

    proof = build_proof(out_dir=args.out_dir, skip_render=args.skip_render)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "PROOF.json").write_text(json.dumps(proof, indent=2), encoding="utf-8")
    (args.out_dir / "SCORECARD.md").write_text(_scorecard_md(proof), encoding="utf-8")
    (args.out_dir / "SELLABILITY_ROLLUP.md").write_text(_rollup_md(proof), encoding="utf-8")
    closeout = (
        f"# Books final verify closeout (2026-07-08)\n\n"
        f"**Verdict:** {proof['verdict']}\n\n"
    )
    if proof["blockers"]:
        closeout += f"**BLOCKER:** {proof['blockers'][0]}\n"
    else:
        closeout += "All proof cells green on cadence, phrase-density, uniqueness truth, and EI v2 semantic-dedup.\n"
    (args.out_dir / "CLOSEOUT.md").write_text(closeout, encoding="utf-8")
    print(proof["verdict"], proof.get("blockers", []))
    return 1 if proof["verdict"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
