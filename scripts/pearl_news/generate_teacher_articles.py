#!/usr/bin/env python3
"""
Generate and publish Pearl News articles for a single teacher in their native language.

TEACHER × LANGUAGE MATRIX (from PEARL_NEWS_WRITER_SPEC.md / teacher_news_roster.yaml):
  English:  ahjan, sai_ma, ra, pamela_fellows, maat
  Japanese: junko, miki, joshin
  Chinese:  master_feung, master_wu

LLM ROUTING (from expansion_routing.py):
  English articles → Claude (via ANTHROPIC_API_KEY)
  Japanese/Chinese → Qwen on Pearl Star (192.168.1.112:11434)

Usage:
  PYTHONPATH=. python3 scripts/pearl_news/generate_teacher_articles.py \\
    --teacher ahjan --count 2 --publish --out-dir artifacts/pearl_news/published/

  # Dry run (generate + validate, no publish):
  PYTHONPATH=. python3 scripts/pearl_news/generate_teacher_articles.py \\
    --teacher junko --count 1 --dry-run

Required env vars:
  WORDPRESS_SITE_URL, WORDPRESS_USERNAME, WORDPRESS_APP_PASSWORD
  ANTHROPIC_API_KEY  (English articles via Claude)
  QWEN_BASE_URL      (CJK articles; default: http://192.168.1.112:11434/v1)
"""
from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger("pearl_news.teacher_gen")

# ---------------------------------------------------------------------------
# Teacher → language mapping (authoritative; matches TEACHER × LANGUAGE MATRIX)
# region_fit alone is ambiguous (ahjan has japan but publishes in English).
# ---------------------------------------------------------------------------
TEACHER_LANGUAGE: dict[str, str] = {
    # English teachers
    "ahjan": "en",
    "sai_ma": "en",
    "ra": "en",
    "pamela_fellows": "en",
    "maat": "en",
    # Japanese teachers
    "junko": "ja",
    "miki": "ja",
    "joshin": "ja",
    # Chinese teachers
    "master_feung": "zh-cn",
    "master_wu": "zh-cn",
}

ALL_TEACHERS = list(TEACHER_LANGUAGE.keys())


def _language_for_teacher(teacher_id: str) -> str:
    """
    Return language code for teacher. Uses TEACHER_LANGUAGE map first;
    falls back to region_fit from teacher_news_roster.yaml for unknown teachers.
    """
    if teacher_id in TEACHER_LANGUAGE:
        return TEACHER_LANGUAGE[teacher_id]
    # Fallback: read roster and check region_fit priority
    try:
        import yaml
        roster_path = REPO_ROOT / "pearl_news" / "config" / "teacher_news_roster.yaml"
        if roster_path.exists():
            with open(roster_path, encoding="utf-8") as f:
                roster = yaml.safe_load(f) or {}
            teacher = (roster.get("teachers") or {}).get(teacher_id, {})
            region_fit = teacher.get("region_fit") or []
            if "japan" in region_fit:
                return "ja"
            if "china" in region_fit:
                return "zh-cn"
    except Exception:
        pass
    return "en"


def run_pipeline(
    teacher_id: str,
    language: str,
    count: int,
    out_dir: Path,
    dry_run: bool = False,
) -> list[Path]:
    """
    Run pearl_news.pipeline.run_article_pipeline for one teacher + language.
    Returns list of article JSON paths written to out_dir.
    """
    teacher_out = out_dir / teacher_id
    teacher_out.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "pearl_news.pipeline.run_article_pipeline",
        "--language", language,
        "--out-dir", str(teacher_out),
        "--expand",
        "--validate",
        "--select-image",
        "--limit", str(count),
    ]
    logger.info("Running pipeline: teacher=%s lang=%s count=%d", teacher_id, language, count)
    logger.info("CMD: %s", " ".join(cmd))

    env = _build_env(language)

    if dry_run:
        logger.info("[DRY-RUN] Would run: %s", " ".join(cmd))
        return []

    result = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Pipeline exited {result.returncode} for teacher={teacher_id} lang={language}"
        )

    # Collect generated article JSONs (exclude manifest files)
    articles = sorted(
        p for p in teacher_out.glob("article_*.json")
    )
    logger.info("Pipeline produced %d article files for %s", len(articles), teacher_id)
    return articles


def _build_env(language: str) -> dict[str, str]:
    """Build subprocess env with correct LLM routing env vars."""
    import os
    env = os.environ.copy()
    # For CJK, ensure QWEN_BASE_URL and QWEN_MODEL are set with defaults
    if language in ("ja", "zh-cn", "ko", "zh-tw", "zh-hk", "zh-sg"):
        if not env.get("QWEN_BASE_URL"):
            env["QWEN_BASE_URL"] = "http://192.168.1.112:11434/v1"
        if not env.get("QWEN_MODEL"):
            env["QWEN_MODEL"] = "qwen2.5:14b"
    return env


def publish_article(
    article_path: Path,
    teacher_id: str,
    status: str = "publish",
    dry_run: bool = False,
) -> dict:
    """
    Read article JSON, set publish status, post to WordPress.
    Returns result dict: {teacher, language, title, wp_url, wp_post_id, published_at, status}
    """
    data = json.loads(article_path.read_text(encoding="utf-8"))
    title = data.get("title") or data.get("headline", "")
    content = data.get("content") or data.get("body", "")
    slug = data.get("slug")
    author = data.get("author")
    language = data.get("language", "en")
    featured_image = data.get("featured_image")
    featured_image_url = data.get("featured_image_url")
    featured_image_path = data.get("featured_image_path")
    if featured_image_path:
        featured_image_path = REPO_ROOT / featured_image_path

    if not title or not content:
        raise ValueError(f"Article {article_path} missing title or content")

    log_entry = {
        "teacher": teacher_id,
        "language": language,
        "title": title,
        "article_path": str(article_path),
        "wp_url": None,
        "wp_post_id": None,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
    }

    if dry_run:
        logger.info("[DRY-RUN] Would publish: %s — %s", teacher_id, title[:60])
        log_entry["status"] = "dry_run"
        return log_entry

    from pearl_news.publish.wordpress_client import post_article, WordPressPublishError
    try:
        result = post_article(
            title=title,
            content=content,
            status=status,
            slug=slug,
            author=author,
            featured_image=featured_image,
            featured_image_url=featured_image_url,
            featured_image_path=featured_image_path,
        )
        wp_url = result.get("link") or result.get("guid", {}).get("rendered", "")
        wp_post_id = result.get("id")
        log_entry.update({
            "wp_url": wp_url,
            "wp_post_id": wp_post_id,
            "status": status,
        })
        logger.info(
            "Published [%s/%s]: post_id=%s url=%s",
            teacher_id, language, wp_post_id, wp_url,
        )
    except WordPressPublishError as e:
        log_entry["status"] = "failed"
        log_entry["error"] = str(e)
        logger.error("WordPress publish failed for %s: %s", teacher_id, e)
        raise

    return log_entry


def append_publish_log(entry: dict, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate and publish Pearl News articles for one teacher")
    ap.add_argument("--teacher", required=True, choices=ALL_TEACHERS + ["all"],
                    help="Teacher ID (from teacher_news_roster.yaml)")
    ap.add_argument("--count", type=int, default=2,
                    help="Number of articles to generate (default: 2)")
    ap.add_argument("--publish", action="store_true",
                    help="Publish to WordPress (status=publish). Without this, articles are generated but not posted.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Generate + validate but do not publish")
    ap.add_argument("--status", choices=("draft", "publish"), default="publish",
                    help="WordPress post status when --publish is set (default: publish)")
    ap.add_argument("--out-dir", type=Path,
                    default=Path("artifacts/pearl_news/published"),
                    help="Output directory for generated article JSONs")
    ap.add_argument("--log", type=Path,
                    default=Path("artifacts/pearl_news/publish_log.jsonl"),
                    help="Append-only publish log path")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    if args.verbose:
        logging.getLogger("pearl_news").setLevel(logging.DEBUG)

    if args.dry_run:
        logger.info("[DRY-RUN MODE] No articles will be published.")

    teachers = ALL_TEACHERS if args.teacher == "all" else [args.teacher]
    failed = 0

    for teacher_id in teachers:
        language = _language_for_teacher(teacher_id)
        logger.info("=== Teacher: %s  Language: %s ===", teacher_id, language)

        try:
            articles = run_pipeline(
                teacher_id=teacher_id,
                language=language,
                count=args.count,
                out_dir=args.out_dir,
                dry_run=args.dry_run,
            )
        except Exception as e:
            logger.error("Pipeline failed for %s: %s", teacher_id, e)
            failed += 1
            continue

        if not (args.publish or not args.dry_run):
            logger.info("Skipping publish (--publish not set and not dry-run)")
            continue

        for art_path in articles:
            try:
                entry = publish_article(
                    article_path=art_path,
                    teacher_id=teacher_id,
                    status=args.status if args.publish else "draft",
                    dry_run=args.dry_run,
                )
                append_publish_log(entry, args.log)
            except Exception as e:
                failed += 1
                entry = {
                    "teacher": teacher_id,
                    "language": language,
                    "title": "",
                    "article_path": str(art_path),
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "status": "failed",
                    "error": str(e),
                }
                append_publish_log(entry, args.log)

    if failed:
        logger.warning("Completed with %d failure(s)", failed)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
