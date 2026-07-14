#!/usr/bin/env python3
"""Generate a local Waystream freebie report from a completed tool payload."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
TEMPLATES = REPO / "config/freebies/freebie_report_templates.yaml"


def _load_templates() -> dict[str, Any]:
    return yaml.safe_load(TEMPLATES.read_text(encoding="utf-8")) or {}


def _coerce_answers(value: str | None) -> list[dict[str, Any]]:
    if not value:
        return []
    data = json.loads(value)
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        return [{"field": key, "value": val} for key, val in data.items()]
    return []


def build_report(slug: str, answers_json: str | None = None, score_band: str | None = None) -> dict[str, Any]:
    templates = _load_templates().get("reports") or {}
    spec = templates.get(slug)
    if not spec:
        raise KeyError(f"unknown freebie slug: {slug}")
    answers = _coerce_answers(answers_json)
    answered_fields = [str(item.get("field") or item.get("label") or f"answer_{idx}") for idx, item in enumerate(answers)]
    pattern = ", ".join(answered_fields[:4]) if answered_fields else "the completed tool state"
    report = {
        "report_id": spec["report_id"],
        "source_page_slug": slug,
        "topic": spec["topic"],
        "freebie_id": spec["freebie_id"],
        "title": spec["title"],
        "score_band": score_band or "not_scored",
        "summary": f"Your report reflects {pattern}. It is educational and reflective, not clinical advice.",
        "sections": {
            "completion_reflection": "You completed the tool and created a useful snapshot of the pattern.",
            "answer_pattern": f"The strongest available signal is {pattern}.",
            "somatic_signal": spec["benefits"]["somatic"],
            "nervous_system_cue": spec["benefits"]["nervous_system"],
            "psychological_reflection": spec["benefits"]["psychological"],
            "spiritual_question": spec["benefits"]["spiritual"],
            "next_week_reflective_forecast": spec["forecast"],
            "recommended_practice": spec["recommended_practice"],
        },
    }
    report["text"] = "\n\n".join(
        [
            report["title"],
            report["summary"],
            f"Next week reflection: {report['sections']['next_week_reflective_forecast']}",
            f"Practice: {report['sections']['recommended_practice']}",
        ]
    )
    report["html"] = (
        f"<h1>{html.escape(report['title'])}</h1>"
        f"<p>{html.escape(report['summary'])}</p>"
        f"<h2>Next week reflection</h2><p>{html.escape(report['sections']['next_week_reflective_forecast'])}</p>"
        f"<h2>Practice</h2><p>{html.escape(report['sections']['recommended_practice'])}</p>"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Waystream freebie report.")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--answers-json")
    parser.add_argument("--score-band")
    parser.add_argument("--out")
    args = parser.parse_args()
    report = build_report(args.slug, args.answers_json, args.score_band)
    body = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        out = Path(args.out)
        if not out.is_absolute():
            out = REPO / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
    else:
        print(body, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
