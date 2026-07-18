#!/usr/bin/env python3
"""Pearl_News reader-signal ingest (Phase 1).

This module reads aggregated reader signals (poll votes + take submissions)
and emits per-article engagement scores that EI v2 can consume in its
article-quality composite.

Schema of an incoming signal (POSTed by the assemble_v52.py frontend to
/wp-json/pearl-news/v1/signal, OR mailed via the mailto fallback):

    {
      "kind":       "poll_vote" | "take",
      "article_id": "<slug or feed_item id>",
      "value":      "<poll option text>",       # for poll_vote
      "text":       "<reader's take text>",     # for take
      "ts":         "<ISO 8601 timestamp>",
      "ip":         "<optional, hashed>",
      "ua":         "<optional, hashed>",
    }

Storage location (Phase 1, before the WP endpoint lands):
  artifacts/pearl_news/reader_signals/<YYYY-MM-DD>.jsonl
  — one signal per line; append-only; one file per UTC day.

Output (Phase 1):
  artifacts/pearl_news/reader_signals/_engagement_scores.json
  — dict[article_id] → {
      "poll_response_rate": float,    # poll votes / impressions (proxy: 1.0 if any vote)
      "take_submission_count": int,   # raw count of takes received
      "dominant_poll_value": str,     # most-voted option
      "last_signal_ts": str,          # ISO 8601
    }

EI v2 hook (Phase 2 — TODO):
  pearl_news/pipeline/ei_article_scorer.py.score_engagement() reads the
  output above when present, factors poll/take signals into the engagement
  composite. Until that wire-up lands, this script's output is informational
  only.

Usage:
    python3 -m pearl_news.pipeline.reader_signal_ingest \
        --signals-dir artifacts/pearl_news/reader_signals \
        --out         artifacts/pearl_news/reader_signals/_engagement_scores.json
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_signals(signals_dir: Path) -> list[dict[str, Any]]:
    """Walk the daily JSONL files; return every well-formed signal."""
    signals: list[dict[str, Any]] = []
    if not signals_dir.exists():
        logger.info("signals dir not yet created: %s", signals_dir)
        return signals
    for jsonl in sorted(signals_dir.glob("*.jsonl")):
        with jsonl.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    sig = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning("bad JSONL line in %s — skipping", jsonl.name)
                    continue
                if not isinstance(sig, dict) or "kind" not in sig or "article_id" not in sig:
                    continue
                signals.append(sig)
    return signals


def aggregate(signals: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Group signals by article_id; emit per-article engagement summary."""
    per_article: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "poll_votes": Counter(),
        "take_count": 0,
        "last_signal_ts": "",
    })

    for sig in signals:
        aid = sig["article_id"]
        acc = per_article[aid]
        ts = sig.get("ts", "")
        if ts > acc["last_signal_ts"]:
            acc["last_signal_ts"] = ts

        if sig["kind"] == "poll_vote" and sig.get("value"):
            acc["poll_votes"][sig["value"]] += 1
        elif sig["kind"] == "take" and sig.get("text"):
            acc["take_count"] += 1

    # Project into the schema EI v2 consumes
    scores: dict[str, dict[str, Any]] = {}
    for aid, acc in per_article.items():
        total_poll = sum(acc["poll_votes"].values())
        dominant = acc["poll_votes"].most_common(1)
        scores[aid] = {
            "poll_response_rate": 1.0 if total_poll > 0 else 0.0,  # impressions TBD
            "poll_total_votes":   total_poll,
            "dominant_poll_value": dominant[0][0] if dominant else "",
            "poll_distribution":  dict(acc["poll_votes"]),
            "take_submission_count": acc["take_count"],
            "last_signal_ts":     acc["last_signal_ts"],
        }
    return scores


def engagement_score_for(article_id: str, scores: dict[str, dict[str, Any]]) -> float:
    """Single-number engagement boost for EI v2. Range: 0.0–1.0.

    Heuristic (Phase 1 — operator-tunable later):
      - 0.0 if no signals
      - 0.5 baseline if at least one poll vote received
      - +0.1 per take submission, capped at +0.3
      - +0.1 if dominant_poll_value exists (i.e. at least 1 vote)
    """
    a = scores.get(article_id)
    if not a:
        return 0.0
    score = 0.0
    if a.get("poll_total_votes", 0) > 0:
        score += 0.5 + 0.1  # base + dominant marker
    score += min(0.3, 0.1 * a.get("take_submission_count", 0))
    return min(1.0, round(score, 3))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--signals-dir", default="artifacts/pearl_news/reader_signals",
                    help="Directory with daily JSONL signal files.")
    ap.add_argument("--out", default="artifacts/pearl_news/reader_signals/_engagement_scores.json",
                    help="Output path for aggregated engagement scores.")
    ap.add_argument("--json", action="store_true", help="Print scores to stdout as JSON.")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

    signals_dir = Path(args.signals_dir)
    signals = load_signals(signals_dir)
    logger.info("loaded %d reader signals from %s", len(signals), signals_dir)

    scores = aggregate(signals)
    logger.info("aggregated into %d article-engagement records", len(scores))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(scores, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("wrote %s", out_path)

    if args.json:
        print(json.dumps(scores, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
