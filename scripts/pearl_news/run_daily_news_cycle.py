#!/usr/bin/env python3
"""
Pearl News daily publishing cycle — runs 10 teachers × 1 article per cycle.

Morning cycle (6 AM Taiwan / 22:00 UTC prev day): 1 article per teacher = 10 articles
Evening cycle (6 PM Taiwan / 10:00 UTC):          1 article per teacher = 10 articles
Full cycle: both morning + evening = 20 articles

Teacher order is seeded by date so it rotates daily, preventing the same
teachers from always publishing first.

Rate limits:
  30s between WordPress publishes (don't hammer the API)
  5s  between LLM calls (Pearl Star Qwen for CJK)

Usage:
  PYTHONPATH=. python3 scripts/pearl_news/run_daily_news_cycle.py --cycle morning
  PYTHONPATH=. python3 scripts/pearl_news/run_daily_news_cycle.py --cycle evening
  PYTHONPATH=. python3 scripts/pearl_news/run_daily_news_cycle.py --cycle full
  PYTHONPATH=. python3 scripts/pearl_news/run_daily_news_cycle.py --cycle morning --dry-run

Required env vars:
  WORDPRESS_SITE_URL, WORDPRESS_USERNAME, WORDPRESS_APP_PASSWORD
  ANTHROPIC_API_KEY  (English articles via Claude)
  QWEN_BASE_URL      (CJK articles; default http://192.168.1.112:11434/v1)
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import subprocess
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger("pearl_news.daily_cycle")

# ---------------------------------------------------------------------------
# Teacher × language (matches TEACHER × LANGUAGE MATRIX in spec)
# ---------------------------------------------------------------------------
TEACHER_LANGUAGE: dict[str, str] = {
    "ahjan": "en",
    "sai_ma": "en",
    "ra": "en",
    "pamela_fellows": "en",
    "maat": "en",
    "junko": "ja",
    "miki": "ja",
    "joshin": "ja",
    "master_feung": "zh-cn",
    "master_wu": "zh-cn",
}

ALL_TEACHERS = list(TEACHER_LANGUAGE.keys())

# Rate limits
WP_PUBLISH_PAUSE = 30   # seconds between WordPress publishes
LLM_CALL_PAUSE = 5      # seconds between LLM calls (Pearl Star guard)

# ---------------------------------------------------------------------------
# Progress tracking
# ---------------------------------------------------------------------------
PROGRESS_PATH = Path("artifacts/pearl_news/daily_cycle_progress.json")
PUBLISH_LOG_PATH = Path("artifacts/pearl_news/publish_log.jsonl")


def _load_progress(cycle_key: str) -> dict:
    today = date.today().isoformat()
    if PROGRESS_PATH.exists():
        try:
            p = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
            if p.get("date") == today and p.get("cycle") == cycle_key:
                return p
        except Exception:
            pass
    return {
        "date": today,
        "cycle": cycle_key,
        "teachers_completed": [],
        "teachers_failed": [],
        "articles_published": 0,
        "articles_failed": 0,
    }


def _save_progress(progress: dict) -> None:
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_PATH.write_text(json.dumps(progress, indent=2, ensure_ascii=False), encoding="utf-8")


def _append_publish_log(entry: dict) -> None:
    PUBLISH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PUBLISH_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Teacher ordering: rotate daily using date-seeded shuffle
# ---------------------------------------------------------------------------
def _ordered_teachers() -> list[str]:
    """Return teachers in a date-seeded order so the rotation varies daily."""
    today_int = int(date.today().strftime("%Y%m%d"))
    rng = random.Random(today_int)
    teachers = ALL_TEACHERS.copy()
    rng.shuffle(teachers)
    return teachers


# ---------------------------------------------------------------------------
# Per-teacher article generation + publish
# ---------------------------------------------------------------------------
def _build_env(language: str) -> dict[str, str]:
    env = os.environ.copy()
    if language in ("ja", "zh-cn", "ko", "zh-tw", "zh-hk", "zh-sg"):
        if not env.get("QWEN_BASE_URL"):
            env["QWEN_BASE_URL"] = "http://192.168.1.112:11434/v1"
        if not env.get("QWEN_MODEL"):
            env["QWEN_MODEL"] = "qwen2.5:14b"
    return env


def run_teacher(
    teacher_id: str,
    cycle: str,
    out_dir: Path,
    dry_run: bool = False,
) -> dict:
    """
    Generate + publish 1 article for teacher_id.
    Returns a result dict suitable for logging.
    """
    language = TEACHER_LANGUAGE.get(teacher_id, "en")
    teacher_out = out_dir / teacher_id
    teacher_out.mkdir(parents=True, exist_ok=True)

    result = {
        "teacher": teacher_id,
        "language": language,
        "cycle": cycle,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "articles_published": 0,
        "articles_failed": 0,
        "error": None,
    }

    # --- Step 1: Generate article via pipeline ---
    cmd = [
        sys.executable, "-m", "pearl_news.pipeline.run_article_pipeline",
        "--language", language,
        "--out-dir", str(teacher_out),
        "--expand",
        "--validate",
        "--select-image",
        "--limit", "1",
    ]
    logger.info("[%s/%s] Running pipeline (lang=%s)", teacher_id, cycle, language)

    if dry_run:
        logger.info("[DRY-RUN] Would run pipeline: %s", " ".join(cmd))
        result["articles_published"] = 0
        return result

    env = _build_env(language)
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env)
    if proc.returncode != 0:
        result["error"] = f"Pipeline exited {proc.returncode}"
        result["articles_failed"] = 1
        logger.error("[%s] Pipeline failed (exit %d)", teacher_id, proc.returncode)
        return result

    # Brief pause after LLM call before publishing
    time.sleep(LLM_CALL_PAUSE)

    # --- Step 2: Publish generated articles ---
    articles = sorted(teacher_out.glob("article_*.json"))
    if not articles:
        result["error"] = "Pipeline produced no article JSON files"
        result["articles_failed"] = 1
        logger.warning("[%s] No articles generated", teacher_id)
        return result

    from pearl_news.publish.wordpress_client import post_article, WordPressPublishError

    for art_path in articles:
        try:
            data = json.loads(art_path.read_text(encoding="utf-8"))
            title = data.get("title") or data.get("headline", "")
            content = data.get("content") or data.get("body", "")
            if not title or not content:
                raise ValueError("Missing title or content")

            wp_result = post_article(
                title=title,
                content=content,
                status="publish",
                slug=data.get("slug"),
                author=data.get("author"),
                meta={
                    "pearl_news_layout": "sidebar",
                    "pearl_news_template": "sidebar",
                },
                featured_image=data.get("featured_image"),
                featured_image_url=data.get("featured_image_url"),
                featured_image_path=(
                    REPO_ROOT / data["featured_image_path"]
                    if data.get("featured_image_path") else None
                ),
            )
            wp_url = wp_result.get("link") or ""
            wp_post_id = wp_result.get("id")
            result["articles_published"] += 1

            log_entry = {
                "teacher": teacher_id,
                "language": language,
                "cycle": cycle,
                "title": title,
                "wp_url": wp_url,
                "wp_post_id": wp_post_id,
                "published_at": datetime.now(timezone.utc).isoformat(),
                "status": "publish",
            }
            _append_publish_log(log_entry)
            logger.info("[%s] Published: post_id=%s %s", teacher_id, wp_post_id, wp_url)

        except WordPressPublishError as e:
            result["articles_failed"] += 1
            result["error"] = str(e)
            log_entry = {
                "teacher": teacher_id,
                "language": language,
                "cycle": cycle,
                "title": data.get("title", ""),
                "published_at": datetime.now(timezone.utc).isoformat(),
                "status": "failed",
                "error": str(e),
            }
            _append_publish_log(log_entry)
            logger.error("[%s] WordPress publish error: %s", teacher_id, e)

        except Exception as e:
            result["articles_failed"] += 1
            result["error"] = str(e)
            logger.error("[%s] Unexpected error during publish: %s", teacher_id, e)

    return result


# ---------------------------------------------------------------------------
# Cycle runner
# ---------------------------------------------------------------------------
def run_cycle(cycle: str, dry_run: bool = False) -> dict:
    """
    Run one cycle (morning or evening). Returns summary dict.
    """
    today = date.today().isoformat()
    logger.info("=== Pearl News daily cycle: %s  date: %s ===", cycle, today)

    progress = _load_progress(cycle)
    already_done = set(progress.get("teachers_completed", []))
    if already_done:
        logger.info("Resuming: %d teachers already completed", len(already_done))

    teachers = _ordered_teachers()
    out_dir = Path(f"artifacts/pearl_news/published/{today}/{cycle}")
    out_dir.mkdir(parents=True, exist_ok=True)

    for teacher_id in teachers:
        if teacher_id in already_done:
            logger.info("[%s] Already completed in this cycle — skipping", teacher_id)
            continue

        logger.info("--- Starting teacher: %s ---", teacher_id)
        try:
            result = run_teacher(
                teacher_id=teacher_id,
                cycle=cycle,
                out_dir=out_dir,
                dry_run=dry_run,
            )
            if result.get("articles_failed", 0) > 0 or result.get("error"):
                progress["teachers_failed"].append(teacher_id)
                progress["articles_failed"] += result.get("articles_failed", 0)
                logger.warning("[%s] Failed: %s", teacher_id, result.get("error"))
            else:
                progress["teachers_completed"].append(teacher_id)
                progress["articles_published"] += result.get("articles_published", 0)

        except Exception as e:
            # Never stop the whole cycle — log and continue
            progress["teachers_failed"].append(teacher_id)
            progress["articles_failed"] += 1
            logger.error("[%s] Unhandled error: %s", teacher_id, e)

        _save_progress(progress)

        # Rate limit: pause between teachers to avoid hammering WordPress
        if teacher_id != teachers[-1]:
            logger.info("Pausing %ds before next teacher...", WP_PUBLISH_PAUSE)
            if not dry_run:
                time.sleep(WP_PUBLISH_PAUSE)

    _save_progress(progress)
    logger.info(
        "=== Cycle %s complete: published=%d failed=%d ===",
        cycle,
        progress["articles_published"],
        progress["articles_failed"],
    )
    return progress


def main() -> int:
    ap = argparse.ArgumentParser(description="Pearl News daily publishing cycle")
    ap.add_argument(
        "--cycle",
        choices=("morning", "evening", "full"),
        required=True,
        help="morning: run morning cycle; evening: evening cycle; full: both",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate + validate but do not publish; do not pause between teachers",
    )
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    if args.verbose:
        logging.getLogger("pearl_news").setLevel(logging.DEBUG)

    if args.cycle == "full":
        r_morning = run_cycle("morning", dry_run=args.dry_run)
        r_evening = run_cycle("evening", dry_run=args.dry_run)
        total_published = r_morning["articles_published"] + r_evening["articles_published"]
        total_failed = r_morning["articles_failed"] + r_evening["articles_failed"]
    else:
        r = run_cycle(args.cycle, dry_run=args.dry_run)
        total_published = r["articles_published"]
        total_failed = r["articles_failed"]

    logger.info(
        "Daily cycle done. Total published: %d  failed: %d",
        total_published, total_failed,
    )
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
