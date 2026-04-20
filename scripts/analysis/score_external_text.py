#!/usr/bin/env python3
"""Score a single chapter-sized text through deterministic Phoenix quality gates.

Wraps plain UTF-8 prose as a one-chapter book where needed (book_quality_gate),
runs museum detectors on a minimal book dict, and writes JSON suitable for
benchmark aggregation. No network calls; optional LLM hooks are never passed.

Usage:
  PYTHONPATH=. python3 scripts/analysis/score_external_text.py \\
    --input path/to/chapter.txt \\
    --output artifacts/research/bestseller_benchmark/scores/foo.json \\
    --persona gen_z_professionals \\
    --gates all
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]

_DEFAULT_GATES = (
    "chapter_flow",
    "bestseller_craft",
    "ei_v2",
    "editorial",
    "memorable_lines",
    "transformation_arc",
    "book_quality_gate",
    "regression_museum",
)


def _load_bestseller_craft_thresholds() -> dict:
    try:
        import yaml as _yaml_mod
    except ImportError:
        return {}
    cfg_path = REPO_ROOT / "config" / "quality" / "bestseller_craft_gate.yaml"
    if not cfg_path.exists():
        return {}
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = _yaml_mod.safe_load(f) or {}
        craft = data.get("bestseller_craft", {})
        out: dict = {}
        for key in (
            "fail_below",
            "warn_below",
            "orient_word_span",
            "pull_word_span",
            "name_start_frac",
            "name_end_frac",
            "turn_start_frac",
            "turn_end_frac",
            "give_start_frac",
        ):
            if key in craft:
                out[key] = craft[key]
        return out
    except Exception:
        return {}


def _book_dict_for_museum(chapter_text: str, *, persona: str) -> dict:
    return {
        "persona": persona,
        "chapters": [
            {
                "index": 1,
                "text": chapter_text,
                "exercise_atom_ids": [],
            }
        ],
    }


def _violations_payload(violations: list) -> list[dict[str, Any]]:
    out = []
    for v in violations:
        out.append(
            {
                "failure_class": v.failure_class,
                "severity": v.severity,
                "location": v.location,
                "evidence": (v.evidence or "")[:800],
                "description": v.description,
            }
        )
    return out


def _museum_summary(result: dict) -> dict[str, Any]:
    violations = result.get("violations") or []
    classes = sorted({v.failure_class for v in violations})
    return {
        "blocked": bool(result.get("blocked")),
        "warned": bool(result.get("warned")),
        "summary": result.get("summary", ""),
        "failure_classes": classes,
        "violation_count": len(violations),
    }


def _craft_composite(move_scores: dict[str, float]) -> float:
    if not move_scores:
        return 0.0
    vals = [float(v) for v in move_scores.values()]
    return round(sum(vals) / max(1, len(vals)), 4)


def _parse_gates_arg(raw: str) -> List[str]:
    s = (raw or "").strip().lower()
    if s in ("", "all", "*"):
        return list(_DEFAULT_GATES)
    gates = [g.strip() for g in raw.split(",") if g.strip()]
    unknown = [g for g in gates if g not in _DEFAULT_GATES]
    if unknown:
        raise SystemExit(f"Unknown gates: {unknown}. Allowed: {', '.join(_DEFAULT_GATES)}")
    return gates


def score_chapter_text(
    chapter_text: str,
    *,
    persona: str,
    gates: List[str],
    source_label: str = "",
) -> dict[str, Any]:
    text = (chapter_text or "").strip()
    wc = len(text.split())
    out: dict[str, Any] = {
        "source_label": source_label,
        "persona": persona,
        "word_count": wc,
        "gates_requested": gates,
    }

    if "chapter_flow" in gates:
        from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow

        cf = evaluate_chapter_flow(text, flow_profile="standard")
        out["chapter_flow"] = {
            "status": cf.status,
            "score": cf.score,
            "errors": cf.errors,
            "warnings": cf.warnings,
            "metrics": cf.metrics,
        }

    if "bestseller_craft" in gates:
        from phoenix_v4.quality.bestseller_craft_gate import evaluate_bestseller_craft

        thr = _load_bestseller_craft_thresholds()
        craft = evaluate_bestseller_craft(text, thresholds=thr if thr else None)
        out["bestseller_craft"] = {
            "status": craft.status,
            "move_scores": craft.move_scores,
            "ontgp_composite": _craft_composite(craft.move_scores),
            "issues": craft.issues,
            "remediation": craft.remediation,
            "metrics": craft.metrics,
        }

    if "memorable_lines" in gates:
        from phoenix_v4.quality.memorable_line_gate import evaluate_memorable_lines

        ml = evaluate_memorable_lines(text)
        out["memorable_lines"] = {
            "status": ml.status,
            "memorable_line_count": ml.memorable_line_count,
            "issues": ml.issues,
            "metrics": ml.metrics,
        }

    if "transformation_arc" in gates:
        from phoenix_v4.quality.transformation_heatmap import compute_signals, ending_check

        sigs = compute_signals([text])
        end = ending_check(sigs, last_n=2)
        out["transformation_arc"] = {
            "chapter_signals": [asdict(s) for s in sigs],
            "ending_check": end,
            "note_single_chapter": (
                "Single-chapter sample: ending_check uses only this chapter; "
                "identity_shift in final chapter is often absent by construction."
            ),
        }

    if "editorial" in gates:
        from phoenix_v4.qa.editorial_report import generate_editorial_report

        ed = generate_editorial_report(text, [text])
        out["editorial"] = ed.to_dict()

    if "book_quality_gate" in gates:
        from phoenix_v4.quality.book_quality_gate import evaluate_book_quality

        wrapped = f"Chapter 1\n\n{text}" if not re.match(r"(?m)^Chapter\s+1\s*$", text) else text
        bq = evaluate_book_quality(wrapped, runtime_format_id="")
        out["book_quality_gate"] = bq.to_dict()

    if "ei_v2" in gates:
        from phoenix_v4.quality.ei_v2.safety_classifier import classify_safety
        from phoenix_v4.quality.ei_v2.tts_readability import score_tts_readability

        safety = classify_safety(text, cfg={"mode": "heuristic_plus"})
        tts = score_tts_readability(text)
        out["ei_v2"] = {
            "mode": "heuristic_plus_safety_plus_tts_readability",
            "safety": safety,
            "tts_readability": tts,
        }

    if "regression_museum" in gates:
        from phoenix_v4.quality.regression_museum import run_museum_gates

        book = _book_dict_for_museum(text, persona=persona)
        mres = run_museum_gates(book, persona=persona)
        out["regression_museum"] = {
            "summary": _museum_summary(mres),
            "violations": _violations_payload(mres["violations"]),
        }

    return out


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, help="UTF-8 chapter text file")
    p.add_argument("--output", required=True, help="Write JSON scores here")
    p.add_argument("--persona", default="gen_z_professionals")
    p.add_argument("--gates", default="all", help=f"Comma list or 'all' ({', '.join(_DEFAULT_GATES)})")
    p.add_argument("--label", default="", help="Optional string stored in JSON")
    args = p.parse_args(argv)

    path = Path(args.input)
    if not path.is_file():
        print(f"INPUT_NOT_FOUND: {path}", file=sys.stderr)
        return 2

    raw = path.read_text(encoding="utf-8", errors="replace")
    gates = _parse_gates_arg(args.gates)
    label = args.label or path.stem
    payload = score_chapter_text(raw, persona=args.persona, gates=gates, source_label=label)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
