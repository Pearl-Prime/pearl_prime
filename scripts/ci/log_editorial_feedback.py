#!/usr/bin/env python3
"""
Log editorial feedback for EMA learner consumption.

Usage:
  python3 scripts/ci/log_editorial_feedback.py --grade 7.5 --notes "ch6-8 repetitive"
  python3 scripts/ci/log_editorial_feedback.py --plan artifacts/out.plan.json --grade 8.2
  python3 scripts/ci/log_editorial_feedback.py --grade 7.0 \
    --scores rerank=0.82,domain=0.75,safety=0.91,tts=0.88,emotion_arc=0.79
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running from repo root without install
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import yaml

from phoenix_v4.quality.ei_v2.learner import FeedbackRecord, log_feedback


def _load_config() -> dict:
    cfg_path = Path(__file__).resolve().parents[2] / "config" / "quality" / "ei_v2_config.yaml"
    with open(cfg_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _feedback_log_path(cfg: dict) -> Path:
    learner_cfg = cfg.get("learner") or {}
    raw = learner_cfg.get("feedback_path", "artifacts/ei_v2/learner_feedback.jsonl")
    p = Path(raw)
    if not p.is_absolute():
        p = Path(__file__).resolve().parents[2] / p
    return p


def _extract_scores_from_plan(plan_path: Path) -> dict[str, float]:
    """Try to extract EI V2 dimension scores from a plan JSON file."""
    try:
        data = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    # Try common keys where ei_v2_report might live
    for key in ("ei_v2_report", "ei_v2_scores", "composite_scores", "scores"):
        if isinstance(data.get(key), dict):
            raw = data[key]
            result: dict[str, float] = {}
            for k, v in raw.items():
                try:
                    result[str(k)] = float(v)
                except (TypeError, ValueError):
                    continue
            if result:
                return result

    # Try nested under chapters[0] or quality_report
    for subkey in ("quality_report", "pipeline_report"):
        sub = data.get(subkey)
        if isinstance(sub, dict):
            for key in ("ei_v2_report", "composite_scores", "scores"):
                if isinstance(sub.get(key), dict):
                    raw = sub[key]
                    result = {}
                    for k, v in raw.items():
                        try:
                            result[str(k)] = float(v)
                        except (TypeError, ValueError):
                            continue
                    if result:
                        return result
    return {}


def _parse_scores(raw: str) -> dict[str, float]:
    """Parse 'key=val,key=val' string into float dict."""
    result: dict[str, float] = {}
    for item in raw.split(","):
        item = item.strip()
        if "=" not in item:
            continue
        k, _, v = item.partition("=")
        try:
            result[k.strip()] = float(v.strip())
        except ValueError:
            print(f"Warning: could not parse score '{item}', skipping", file=sys.stderr)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Log editorial feedback for EMA learner")
    parser.add_argument("--grade", type=float, required=True, help="Editorial grade (0-10)")
    parser.add_argument("--notes", type=str, default="", help="Free-text editorial notes")
    parser.add_argument(
        "--plan", type=Path, default=None,
        help="Path to plan JSON; dimension scores will be extracted if present",
    )
    parser.add_argument(
        "--scores", type=str, default="",
        help="Dimension scores as key=val,key=val (e.g. rerank=0.82,domain=0.75,...)",
    )
    parser.add_argument(
        "--slot", type=str, default="EDITORIAL",
        help="Slot label (default: EDITORIAL)",
    )
    parser.add_argument(
        "--persona-id", type=str, default="editorial",
        help="Persona ID for this feedback record",
    )
    parser.add_argument(
        "--topic-id", type=str, default="",
        help="Topic ID for this feedback record",
    )
    args = parser.parse_args()

    cfg = _load_config()
    feedback_path = _feedback_log_path(cfg)

    # Build dimension scores: --plan first, then --scores overrides
    dimension_scores: dict[str, float] = {}
    if args.plan is not None:
        dimension_scores.update(_extract_scores_from_plan(args.plan))
    if args.scores:
        dimension_scores.update(_parse_scores(args.scores))

    accepted = args.grade >= 7.0
    margin_delta = args.grade - 7.0

    record = FeedbackRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        slot=args.slot,
        chapter_index=0,
        persona_id=args.persona_id,
        topic_id=args.topic_id or "",
        v1_chosen_id="",
        v2_chosen_id="",
        hybrid_chosen_id="",
        override_applied=False,
        accepted=accepted,
        v1_score=0.0,
        v2_score=0.0,
        margin_delta=margin_delta,
        dimension_scores=dimension_scores,
    )

    log_feedback(record, feedback_path)

    notes_suffix = f" notes='{args.notes}'" if args.notes else ""
    print(
        f"Logged feedback: grade={args.grade} accepted={accepted}{notes_suffix} "
        f"to {feedback_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
