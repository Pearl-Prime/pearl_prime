#!/usr/bin/env python3
"""
Stage 17 — Analytics Ingestor: distribution_manifest + optional analytics_data -> analytics_feedback.json.
VCE §10.5–§10.6: retention stubs, hook ranking, A/B variables for shot planner feedback.
Usage: python scripts/video/run_analytics_ingestor.py <distribution_manifest.json> -o analytics_feedback.json [--analytics analytics_data.json]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import config_snapshot_hash, load_json, should_skip_output, write_atomically


def run_analytics(dist: dict, analytics: dict | None) -> dict:
    analytics = analytics or {}
    retention_curve = analytics.get("retention_curve") or [
        {"t_s": 3, "pct": 0.92},
        {"t_s": 15, "pct": 0.78},
        {"t_s": 30, "pct": 0.65},
        {"t_s": 60, "pct": 0.55},
    ]
    hook_rank = analytics.get("hook_effectiveness") or [
        {"hook_type": dist.get("hook_type", "light_reveal"), "score": 0.71, "sample_n": 120},
    ]
    completion = analytics.get("completion_rate") or 0.62
    ab_vars = {
        "thumbnail_variant": dist.get("thumbnail_variant", "A"),
        "hook_type": dist.get("hook_type"),
        "pacing_variant": dist.get("pacing_variant", "standard"),
        "music_mood": dist.get("music_mood"),
        "color_grade_preset": dist.get("color_grade_preset", "neutral"),
    }
    shot_planner_hints = {
        "suggested_pacing_tweak": "slightly_longer_resolve" if retention_curve and retention_curve[-1]["pct"] < 0.5 else "hold",
        "hook_type_rank": hook_rank,
        "drop_off_seconds": [r["t_s"] for r in retention_curve if r["pct"] < 0.6],
    }
    return {
        "video_id": dist.get("video_id"),
        "plan_id": dist.get("plan_id"),
        "config_hash": config_snapshot_hash(),
        "retention_curve_stub": retention_curve,
        "hook_effectiveness_ranking": hook_rank,
        "completion_rate_tracking": completion,
        "ab_test_variables": ab_vars,
        "shot_planner_feedback": shot_planner_hints,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="VCE Stage 17 — Analytics ingestor (stubs)")
    ap.add_argument("distribution_manifest")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--analytics", default=None, help="Optional analytics_data.json")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    dpath = Path(args.distribution_manifest)
    if not dpath.exists():
        print(f"Error: not found: {dpath}", file=sys.stderr)
        return 1
    dist = load_json(dpath)
    extra = load_json(Path(args.analytics)) if args.analytics and Path(args.analytics).exists() else None
    out = Path(args.out)
    h = config_snapshot_hash()
    if should_skip_output(out, ["plan_id", "shot_planner_feedback", "config_hash"], args.force, h):
        print(f"Skip (exists): {out}")
        return 0
    doc = run_analytics(dist, extra)
    write_atomically(out, doc)
    print(f"Wrote analytics_feedback to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
