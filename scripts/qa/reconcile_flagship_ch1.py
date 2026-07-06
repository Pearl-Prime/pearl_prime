#!/usr/bin/env python3
"""Reconcile production CH1 schedule/render against approved 12-shape manifest.

Usage:
  PYTHONPATH=. python3 scripts/qa/reconcile_flagship_ch1.py \\
    --schedule artifacts/qa/flagship_divergence_phase1_20260706/render/selected_content_variants.json \\
    --render artifacts/qa/flagship_divergence_phase1_20260706/render/book.txt \\
    --out artifacts/qa/flagship_divergence_phase1_20260706
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
APPROVED_MANIFEST = (
    REPO_ROOT / "artifacts/qa/ch1_12shape_preview_v4_20260705/manifest.json"
)
APPROVED_CH1 = (
    REPO_ROOT / "artifacts/qa/ch1_12shape_preview_v4_20260705/complete_ch1.txt"
)

_REFINED_SLOTS = [
    "HOOK",
    "ANGLE_DEFINITION",
    "SCENE",
    "STORY",
    "PIVOT",
    "REFLECTION",
    "EXERCISE",
    "STORY",
    "STORY",
    "TAKEAWAY",
    "INTEGRATION",
    "THREAD",
]


def _load_manifest() -> dict:
    return json.loads(APPROVED_MANIFEST.read_text(encoding="utf-8"))


def reconcile_schedule(schedule_path: Path) -> dict:
    data = json.loads(schedule_path.read_text(encoding="utf-8"))
    manifest = _load_manifest()
    expected = manifest["beats"]
    ch1 = next(c for c in data["chapters"] if c["number"] == 1)
    actual_slots = [s["slot_type"] for s in ch1["slots"]]
    actual_atoms = [s.get("atom_id") or "" for s in ch1["slots"]]

    matched = 0
    details: list[dict] = []
    for i, exp in enumerate(expected):
        exp_slot = exp["slot"]
        exp_atom = exp["atom_id"]
        act_slot = actual_slots[i] if i < len(actual_slots) else ""
        act_atom = actual_atoms[i] if i < len(actual_atoms) else ""
        ok = act_slot == exp_slot
        if ok and exp_slot == "STORY":
            ok = "story_plan" in act_atom or exp_atom.split(":")[-1] in act_atom
        elif ok and exp_atom:
            ok = exp_atom in act_atom or act_atom in exp_atom
        if ok:
            matched += 1
        details.append(
            {
                "index": i + 1,
                "expected_slot": exp_slot,
                "expected_atom": exp_atom,
                "actual_slot": act_slot,
                "actual_atom": act_atom,
                "match": ok,
            }
        )
    return {
        "beats_restored": matched,
        "beats_total": len(expected),
        "slot_sequence": actual_slots,
        "expected_sequence": _REFINED_SLOTS,
        "details": details,
    }


def extract_ch1(render_path: Path) -> str:
    text = render_path.read_text(encoding="utf-8")
    m = re.search(r"Chapter 1\b.*?\n\n(.*?)(?=\n\nChapter 2\b|\Z)", text, re.S)
    body = m.group(1).strip() if m else text.strip()
    if body.startswith("##"):
        body = body.split("\n\n", 1)[-1].strip()
    return body


def reconcile_render(render_path: Path) -> dict:
    approved = APPROVED_CH1.read_text(encoding="utf-8").strip()
    actual = extract_ch1(render_path)
    approved_norm = re.sub(r"\s+", " ", approved).strip()
    actual_norm = re.sub(r"\s+", " ", actual).strip()
    clean = approved_norm == actual_norm
    return {
        "clean_diff": clean,
        "approved_words": len(approved.split()),
        "actual_words": len(actual.split()),
        "approved_preview": approved[:200],
        "actual_preview": actual[:200],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--render", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    sched = reconcile_schedule(args.schedule)
    print(
        f"beats_restored={sched['beats_restored']}/{sched['beats_total']} "
        f"slots={sched['slot_sequence']}"
    )
    for d in sched["details"]:
        if not d["match"]:
            print(
                f"  MISS #{d['index']}: want {d['expected_slot']} {d['expected_atom']} "
                f"got {d['actual_slot']} {d['actual_atom']}"
            )

    report = {"schedule": sched}
    if args.render and args.render.exists():
        render_report = reconcile_render(args.render)
        report["render"] = render_report
        print(f"clean_diff={render_report['clean_diff']}")

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        out_path = args.out / "ch1_reconcile_report.json"
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"wrote {out_path}")

    return 0 if sched["beats_restored"] == sched["beats_total"] else 1


if __name__ == "__main__":
    sys.exit(main())
