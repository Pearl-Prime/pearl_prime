#!/usr/bin/env python3
"""
score_external_text.py — Score a raw text file against the Phoenix gate stack.

Wraps raw chapter text in the minimal structure the heuristic gates expect,
runs the deterministic (zero-API) gate stack, dumps a scores JSON.

Usage:
  PYTHONPATH=. python3 scripts/analysis/score_external_text.py \
      --input path/to/chapter.txt \
      --output path/to/scores.json \
      [--gates chapter_flow,bestseller_craft,memorable_lines]
      [--runtime-format standard_book]

Exit: 0 PASS, 1 FAIL/WARN (see scores.json for detail).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

SUPPORTED_GATES = ["chapter_flow", "bestseller_craft", "memorable_lines"]


def _split_chapters(text: str) -> list[str]:
    """Split text on 'Chapter N' headings; if none, treat as single chapter."""
    parts = re.split(r"\n?Chapter\s+\d+[^\n]*\n", text, flags=re.I)
    chapters = [p.strip() for p in parts if p.strip()]
    return chapters if chapters else [text.strip()]


def score_text(
    text: str,
    gates: list[str],
    runtime_format: str = "standard_book",
) -> dict:
    results: dict = {"runtime_format": runtime_format, "chapters": [], "summary": {}}
    chapters = _split_chapters(text)
    results["num_chapters"] = len(chapters)

    ontgp_scores: list[float] = []
    flow_scores: list[float] = []
    memorable_counts: list[int] = []

    for i, chap in enumerate(chapters):
        chap_result: dict = {"chapter_index": i, "word_count": len(chap.split())}

        if "chapter_flow" in gates:
            from phoenix_v4.quality.chapter_flow_gate import (
                evaluate_chapter_flow,
                flow_profile_for_runtime_format,
            )
            profile = flow_profile_for_runtime_format(runtime_format)
            fr = evaluate_chapter_flow(chap, flow_profile=profile)
            chap_result["chapter_flow"] = {
                "status": fr.status,
                "score": fr.score,
                "errors": fr.errors,
                "warnings": fr.warnings,
            }
            flow_scores.append(float(fr.score))

        if "bestseller_craft" in gates:
            from phoenix_v4.quality.bestseller_craft_gate import evaluate_bestseller_craft
            cr = evaluate_bestseller_craft(chap)
            ms = cr.move_scores or {}
            ontgp = sum(ms.values()) / len(ms) if ms else 0.0
            chap_result["bestseller_craft"] = {
                "status": cr.status,
                "ontgp": round(ontgp, 3),
                "move_scores": {k: round(v, 3) for k, v in ms.items()},
                "issues": cr.issues[:10],
            }
            ontgp_scores.append(ontgp)

        if "memorable_lines" in gates:
            from phoenix_v4.quality.memorable_line_detector import detect_lines
            ml = detect_lines(f"chapter_{i}", [chap])
            quotable = [
                ln["text"]
                for ln in ml.get("candidates", [])
                if ln.get("score", 0) >= 4.0
            ]
            chap_result["memorable_lines"] = {
                "quotable_count": len(quotable),
                "lines": quotable[:5],
            }
            memorable_counts.append(len(quotable))

        results["chapters"].append(chap_result)

    if ontgp_scores:
        results["summary"]["ontgp_mean"] = round(sum(ontgp_scores) / len(ontgp_scores), 3)
        results["summary"]["ontgp_min"] = round(min(ontgp_scores), 3)
        results["summary"]["ontgp_max"] = round(max(ontgp_scores), 3)
    if flow_scores:
        results["summary"]["flow_mean"] = round(sum(flow_scores) / len(flow_scores), 1)
    if memorable_counts:
        results["summary"]["memorable_total"] = sum(memorable_counts)
        results["summary"]["chapters_with_quotables"] = sum(
            1 for c in memorable_counts if c >= 2
        )

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to raw text file")
    parser.add_argument("--output", required=True, help="Path to write scores JSON")
    parser.add_argument(
        "--gates",
        default="chapter_flow,bestseller_craft,memorable_lines",
        help="Comma-separated gates to run (default: all)",
    )
    parser.add_argument(
        "--runtime-format",
        default="standard_book",
        help="Pipeline runtime format ID for thresholds (default: standard_book)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        return 1

    text = input_path.read_text(encoding="utf-8")
    gates = [g.strip() for g in args.gates.split(",") if g.strip()]

    unknown = [g for g in gates if g not in SUPPORTED_GATES]
    if unknown:
        print(f"ERROR: unknown gates: {unknown}. Supported: {SUPPORTED_GATES}", file=sys.stderr)
        return 1

    results = score_text(text, gates, runtime_format=args.runtime_format)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Scores written: {output_path}")

    summary = results.get("summary", {})
    print(f"  ONTGP mean:    {summary.get('ontgp_mean', 'n/a')}")
    print(f"  Flow mean:     {summary.get('flow_mean', 'n/a')}")
    print(f"  Memorable:     {summary.get('memorable_total', 'n/a')} lines across {results['num_chapters']} chapters")

    fail = any(
        ch.get("chapter_flow", {}).get("status") == "FAIL"
        or ch.get("bestseller_craft", {}).get("status") == "FAIL"
        for ch in results["chapters"]
    )
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
