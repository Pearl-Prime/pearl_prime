#!/usr/bin/env python3
"""
ML Editorial — Market router: quality + fit + variant signals -> positioning/distribution.
Writes market_actions.jsonl.
See docs/ML_EDITORIAL_MARKET_LOOP_SPEC.md
Usage:
  python scripts/ml_editorial/run_market_router.py
  python scripts/ml_editorial/run_market_router.py --section-scores artifacts/ml_editorial/section_scores.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(REPO_ROOT)
import sys
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.planning.catalog_planner import load_structured_trend_score, trend_heat_for_topic_id


def load_config() -> dict:
    path = REPO_ROOT / "config" / "ml_editorial" / "ml_editorial_config.yaml"
    if not path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(path.read_text()) or {}
    except Exception:
        return {}


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def run_market_router(
    artifacts_dir: Path,
    out_path: Path,
    config: dict,
    *,
    trend_score_path: Optional[Path] = None,
) -> int:
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    router_cfg = config.get("market_router") or {}
    default_priority = router_cfg.get("default_priority", "medium")
    heat_threshold = float(router_cfg.get("trend_heat_priority_threshold") or 60)
    channels = router_cfg.get("distribution_channels_default", ["google_play", "findaway"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    trend_payload = load_structured_trend_score(trend_score_path) if trend_score_path else None
    section_scores = load_jsonl(artifacts_dir / "section_scores.jsonl")
    reader_fit = load_jsonl(artifacts_dir / "reader_fit_scores.jsonl")
    variant_rankings = load_jsonl(artifacts_dir / "variant_rankings.jsonl")
    book_ids = set()
    for r in section_scores:
        book_ids.add(r.get("book_id"))
    for r in reader_fit:
        book_ids.add(r.get("book_id"))
    for r in variant_rankings:
        book_ids.add(r.get("book_id"))
    if not book_ids and (artifacts_dir / "section_scores.jsonl").exists():
        for r in section_scores:
            book_ids.add(r.get("book_id"))
    count = 0
    for book_id in book_ids:
        if not book_id:
            continue
        fit_rows = [x for x in reader_fit if x.get("book_id") == book_id]
        segment = ""
        if fit_rows:
            segment = f"{fit_rows[0].get('persona_id', '')}/{fit_rows[0].get('topic_id', '')}/{fit_rows[0].get('locale', 'en')}"
        priority = default_priority
        rationale = "Quality and reader-fit signals aggregated."
        if section_scores:
            weak_books = [s for s in section_scores if s.get("book_id") == book_id and (s.get("weak_flags") or [])]
            if weak_books:
                priority = "low"
                rationale = "Weak sections detected; recommend revise before push."
        topic_slug = ""
        if fit_rows:
            topic_slug = str(fit_rows[0].get("topic_id") or "")
        heat: Optional[float] = None
        trend_boost = False
        if trend_payload is not None and topic_slug:
            heat = trend_heat_for_topic_id(topic_slug, trend_payload)
        if heat is not None and heat >= heat_threshold and priority != "low":
            priority = "high"
            trend_boost = True
            rationale = (
                f"{rationale} Priority elevated using structured trend_score "
                f"(trend_heat_score={heat:.2f})."
            )
        rec = {
            "book_id": book_id,
            "recommended_segment": segment or "general",
            "positioning_angle": "self-help / therapeutic audiobook",
            "distribution_channels": channels,
            "priority": priority,
            "rationale": rationale,
            "ts": ts,
        }
        if heat is not None:
            rec["trend_heat_score"] = heat
        if trend_boost:
            rec["trend_priority_boost"] = True
        with out_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        count += 1
    if count == 0:
        with out_path.open("a", encoding="utf-8") as f:
            f.write("")
    print(f"Market router: {count} rows -> {out_path}")
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description="ML Editorial market router")
    ap.add_argument("--artifacts-dir", default=None, help="artifacts/ml_editorial dir")
    ap.add_argument("--out", default=None, help="Output JSONL path")
    ap.add_argument(
        "--trend-score",
        default=None,
        help="Path to structured trend_score_YYYY-MM-DD.json (from daily trend pipeline); optional",
    )
    args = ap.parse_args()
    config = load_config()
    paths = config.get("paths") or {}
    out_dir = Path(paths.get("output_dir") or "artifacts/ml_editorial")
    artifacts_dir = Path(args.artifacts_dir) if args.artifacts_dir else REPO_ROOT / out_dir
    out_path = Path(args.out) if args.out else REPO_ROOT / out_dir / "market_actions.jsonl"
    trend_path = Path(args.trend_score) if args.trend_score else None
    run_market_router(artifacts_dir, out_path, config, trend_score_path=trend_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
