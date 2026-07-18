#!/usr/bin/env python3
"""
Canonical daily trend orchestrator: writes digest JSONL, trend_score JSON, and summary markdown
per docs/TREND_PIPELINE_TRUTH_AND_AUTOMATION_DEV_SPEC.md §4.

Tier rotation and Tier 4 weekday use config under config/trend_keywords/ (not prose docs).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.feeds.budget_guard import BudgetGuard
from scripts.feeds.check_trends import (
    get_serpapi_key,
    load_tier4_schedule,
    run_trend_check,
)
from scripts.feeds.score_trends import (
    build_trend_score,
    render_markdown_summary,
    write_trend_score,
)


def score_date_to_utc_datetime(score_date: str) -> datetime:
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", score_date):
        raise ValueError(f"score_date must be YYYY-MM-DD, got {score_date!r}")
    y, m, d = (int(score_date[0:4]), int(score_date[5:7]), int(score_date[8:10]))
    return datetime(y, m, d, 12, 0, 0, tzinfo=timezone.utc)


def google_trend_results_to_digest_rows(results: list[dict], score_date: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rec in results:
        pc = float(rec.get("pct_change_7d") or 0)
        if rec.get("spike"):
            direction = "spike"
        elif pc > 5:
            direction = "slight_uptick"
        elif pc < -5:
            direction = "downtick"
        else:
            direction = "stable"
        rows.append(
            {
                "source": "google_trends_serpapi",
                "topic": rec.get("keyword"),
                "google_trends_interest": rec.get("current_interest"),
                "trend_direction": direction,
                "period": "90d",
                "scraped_at": rec.get("checked_at"),
                "scrape_date": score_date,
                "tier": rec.get("tier"),
                "pct_change_7d": rec.get("pct_change_7d"),
            }
        )
    return rows


def run_daily_pipeline(
    score_date: str,
    *,
    feeds_dir: Path,
    dry_run: bool = False,
    skip_rss: bool = False,
    skip_trends: bool = False,
    skip_score: bool = False,
    quiet: bool = False,
    budget_guard: Optional[BudgetGuard] = None,
) -> dict[str, Any]:
    """
    Write canonical artifacts under ``feeds_dir``. Returns paths and metadata.

    When ``skip_score`` is True, only digest (and google jsonl when trends run) are written.
    """
    feeds_dir = Path(feeds_dir)
    digest_path = feeds_dir / f"daily_trend_digest_{score_date}.jsonl"
    gt_path = feeds_dir / f"google_trends_{score_date}.jsonl"
    score_path = feeds_dir / f"trend_score_{score_date}.json"
    summary_path = feeds_dir / f"daily_trend_summary_{score_date}.md"

    # Drop stale google_trends JSONL so score_trends never mixes another day's file.
    gt_path.unlink(missing_ok=True)

    digest_rows: list[dict[str, Any]] = []

    if skip_rss:
        digest_rows.append({"source": "rss", "status": "skipped", "reason": "--skip-rss"})
    else:
        digest_rows.append(
            {
                "source": "rss",
                "status": "skipped",
                "reason": "automated rss pull is not implemented in daily_scrape_runner (follow-up lane)",
            }
        )

    digest_rows.append(
        {
            "source": "exploding_topics",
            "status": "skipped",
            "reason": "exploding topics are not fetched by daily_scrape_runner; use manual or governed ingest",
        }
    )

    as_of = score_date_to_utc_datetime(score_date)

    if skip_trends:
        digest_rows.append(
            {
                "source": "google_trends_serpapi",
                "scrape_date": score_date,
                "status": "skipped",
                "reason": "--skip-trends",
            }
        )
    elif dry_run:
        sch = load_tier4_schedule()
        digest_rows.append(
            {
                "source": "google_trends_serpapi",
                "scrape_date": score_date,
                "status": "skipped",
                "reason": (
                    "dry-run: no SerpApi calls executed. "
                    f"Tier 4 check_day={sch['check_day']} from config/trend_keywords/tier4_emerging.yaml "
                    f"(tier 4 runs only on that weekday)"
                ),
            }
        )
        run_trend_check(as_of=as_of, dry_run=True, quiet=quiet)
    else:
        if not get_serpapi_key():
            digest_rows.append(
                {
                    "source": "google_trends_serpapi",
                    "scrape_date": score_date,
                    "status": "BLOCKED",
                    "note": "SERPAPI_KEY not configured in environment or .env",
                }
            )
        else:
            results = run_trend_check(as_of=as_of, dry_run=False, quiet=quiet)
            if results:
                feeds_dir.mkdir(parents=True, exist_ok=True)
                with open(gt_path, "w", encoding="utf-8") as f:
                    for r in results:
                        f.write(json.dumps(r, ensure_ascii=False) + "\n")
                digest_rows.extend(google_trend_results_to_digest_rows(results, score_date))
            else:
                digest_rows.append(
                    {
                        "source": "google_trends_serpapi",
                        "scrape_date": score_date,
                        "status": "BLOCKED",
                        "note": (
                            "No successful Google Trends fetches (budget exhausted, network errors, "
                            "or all batches failed)"
                        ),
                    }
                )

    feeds_dir.mkdir(parents=True, exist_ok=True)
    digest_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in digest_rows) + "\n",
        encoding="utf-8",
    )

    meta: dict[str, Any] = {
        "digest_path": digest_path,
        "google_trends_path": gt_path,
        "score_path": None,
        "summary_path": None,
        "tier4_schedule": load_tier4_schedule(),
    }

    if skip_score:
        return meta

    payload = build_trend_score(
        score_date,
        digest_path=digest_path,
        google_trends_path=gt_path,
        summary_path=summary_path,
        budget_guard=budget_guard or BudgetGuard(),
    )
    write_trend_score(score_path, payload)
    summary_path.write_text(render_markdown_summary(payload), encoding="utf-8")
    meta["score_path"] = score_path
    meta["summary_path"] = summary_path
    meta["score"] = payload
    return meta


def main() -> int:
    ap = argparse.ArgumentParser(description="Daily trend pipeline: digest + score + summary")
    ap.add_argument("--date", default=None, help="Run date YYYY-MM-DD (default: UTC today)")
    ap.add_argument(
        "--feeds-dir",
        default=None,
        help="Output directory (default: artifacts/feeds under repo root)",
    )
    ap.add_argument("--dry-run", action="store_true", help="No SerpApi calls; still writes artifacts")
    ap.add_argument("--skip-rss", action="store_true", help="Mark rss skipped in digest")
    ap.add_argument("--skip-trends", action="store_true", help="Skip Google Trends fetch")
    ap.add_argument("--skip-score", action="store_true", help="Skip trend_score.json and summary.md")
    args = ap.parse_args()

    score_date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    feeds_dir = Path(args.feeds_dir) if args.feeds_dir else REPO_ROOT / "artifacts" / "feeds"

    meta = run_daily_pipeline(
        score_date,
        feeds_dir=feeds_dir,
        dry_run=args.dry_run,
        skip_rss=args.skip_rss,
        skip_trends=args.skip_trends,
        skip_score=args.skip_score,
        quiet=False,
    )
    print(f"Wrote digest: {meta['digest_path']}")
    if meta.get("score_path"):
        print(f"Wrote score:   {meta['score_path']}")
        print(f"Wrote summary: {meta['summary_path']}")
    else:
        print("Skipped score + summary (--skip-score)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
