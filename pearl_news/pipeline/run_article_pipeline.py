#!/usr/bin/env python3
"""
Pearl News — full pipeline: feeds → ingest → classify → template select → assemble → quality gates → QC.
Output: final article drafts (title, content, metadata) to --out-dir; build manifests for audit.

v2 additions:
  --language    Generate articles in a specific language (en / zh-cn / ja). Default: en.
                Use multiple runs or --language all for 3-language output per story.
  --expand      LLM expansion (now injects teacher, research, language, audience into prompt).
  --validate    Run hard post-expansion validation gates (teacher, youth anchor, SDG, sections).
  --select-image Run rule-based featured image selection (image_catalog.yaml).

Usage:
  # Single language (default English)
  python -m pearl_news.pipeline.run_article_pipeline --feeds pearl_news/config/feeds.yaml --out-dir artifacts/pearl_news/drafts/en --expand --validate --select-image

  # Japanese
  python -m pearl_news.pipeline.run_article_pipeline --language ja --out-dir artifacts/pearl_news/drafts/ja --expand --validate

  # Simplified Chinese
  python -m pearl_news.pipeline.run_article_pipeline --language zh-cn --out-dir artifacts/pearl_news/drafts/zh-cn --expand --validate

  # No LLM (fast draft only)
  python -m pearl_news.pipeline.run_article_pipeline --out-dir artifacts/pearl_news/drafts --limit 10
"""
from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

from pearl_news.pipeline.feed_ingest import ingest_feeds
from pearl_news.pipeline.topic_sdg_classifier import classify_sdgs
from pearl_news.pipeline.template_selector import select_templates
from pearl_news.pipeline.article_assembler import assemble_articles
from pearl_news.pipeline.expansion_routing import run_routed_expansion
from pearl_news.pipeline.ei_article_scorer import run_ei_article_scoring
from pearl_news.pipeline.quality_gates import run_quality_gates
from pearl_news.pipeline.qc_checklist import run_qc_checklist
from pearl_news.pipeline.teacher_resolver import resolve_teacher
from pearl_news.pipeline.article_validator import run_validation
from pearl_news.pipeline.image_selector import run_image_selection
from pearl_news.pipeline.assemble_v52 import assemble_v52

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supported languages
# ---------------------------------------------------------------------------
SUPPORTED_LANGUAGES = {"en", "ja", "zh-cn", "ko", "zh-tw", "zh-hk", "zh-sg"}
LANGUAGE_LABELS = {
    "en": "English",
    "ja": "Japanese",
    "zh-cn": "Simplified Chinese",
    "ko": "Korean",
    "zh-tw": "Traditional Chinese (Taiwan)",
    "zh-hk": "Cantonese / Hong Kong",
    "zh-sg": "Singaporean Mandarin",
}


def _build_manifest_item(item: dict[str, Any]) -> dict[str, Any]:
    """One entry for build manifest (audit trail)."""
    teacher = item.get("_teacher_resolved") or {}
    validation = item.get("_validation") or {}
    return {
        "article_id": item.get("id", ""),
        "language": item.get("language", "en"),
        "feed_item": {
            "id": item.get("id", ""),
            "url": item.get("url", ""),
            "title": item.get("article_title") or item.get("title", ""),
            "published": item.get("pub_date", ""),
        },
        "template_id": item.get("template_id", ""),
        "atom_ids_used": {
            "news_event": [item.get("id", "")],
            "youth_impact": [],
            "teacher_quotes_practices": [teacher.get("teacher_id")] if teacher.get("teacher_id") else [],
            "sdg_refs": [item.get("primary_sdg", "")],
        },
        "teacher_used": {
            "teacher_id": teacher.get("teacher_id"),
            "display_name": teacher.get("display_name"),
            "tradition": teacher.get("tradition"),
        },
        "expansion": {
            "ran": item.get("_expansion_failed") is not None or bool(item.get("content")),
            "failed": item.get("_expansion_failed", False),
            "retries": item.get("_expansion_retries", 0),
        },
        "validation": {
            "passed": validation.get("passed"),
            "failed_gates": validation.get("failed_gates", []),
            "gate_count": validation.get("gate_count"),
            "passed_count": validation.get("passed_count"),
        },
        "model_used": item.get("_expansion_provider") or "qwen",
        "ei_composite": item.get("_ei_composite"),
        "ei_flags": item.get("_ei_flags") or [],
        "prompt_version": "expansion_system_v2",
        "qc_results": item.get("qc_results") or {},
        "signatures": {
            "headline_sig": item.get("headline_sig", ""),
            "lede_sig": item.get("lede_sig", ""),
            "teacher_sig": teacher.get("teacher_id", ""),
            "sdg_sig": item.get("primary_sdg", ""),
        },
        "built_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Pearl News: feeds → draft articles")
    ap.add_argument(
        "--feeds",
        default=None,
        help="Path to feeds.yaml (default: pearl_news/config/feeds.yaml)",
    )
    ap.add_argument(
        "--out-dir",
        default=None,
        help="Output directory for drafts (default: artifacts/pearl_news/drafts/<language>)",
    )
    ap.add_argument(
        "--language",
        default="en",
        choices=sorted(SUPPORTED_LANGUAGES) + ["all"],
        help="Article language: en, ja, zh-cn, ko, zh-tw, zh-hk, zh-sg, or all",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max number of feed items to process (across all feeds)",
    )
    ap.add_argument(
        "--per-feed-limit",
        type=int,
        default=None,
        help="Max items per feed (before global --limit)",
    )
    ap.add_argument(
        "--no-filter-qc",
        action="store_true",
        help="Output all articles (including QC-failed); default is only QC-passed",
    )
    ap.add_argument(
        "--expand",
        action="store_true",
        help="Run LLM expansion (v2: injects teacher, research excerpt, language, audience)",
    )
    ap.add_argument(
        "--validate",
        action="store_true",
        help="Run hard post-expansion validation gates (teacher, youth anchor, SDG, sections)",
    )
    ap.add_argument(
        "--select-image",
        action="store_true",
        help="Run rule-based featured image selection using image_catalog.yaml",
    )
    ap.add_argument(
        "--v52",
        action="store_true",
        help="Render articles using v5.2 interactive layout (exercise, sidebar, poll, co-creation)",
    )
    ap.add_argument(
        "--topic",
        default=None,
        help=(
            "Constrain output to a single topic (e.g. climate, mental_health). "
            "Feed items not matching this topic after classification are discarded. "
            "Required by the daily cycle to enforce INV-1/INV-4."
        ),
    )
    ap.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose logging",
    )
    args = ap.parse_args()

    if args.verbose:
        logging.getLogger("pearl_news").setLevel(logging.DEBUG)

    root = Path(__file__).resolve().parent.parent
    feeds_path = Path(args.feeds) if args.feeds else root / "config" / "feeds.yaml"

    if not feeds_path.exists():
        logger.error("Feeds config not found: %s", feeds_path)
        return 1

    # If --language all, run pipeline once per language and report
    if args.language == "all":
        results = {}
        for lang in sorted(SUPPORTED_LANGUAGES):
            logger.info("=== Running pipeline for language: %s ===", lang)
            lang_args_list = [
                f"--language={lang}",
                f"--out-dir=artifacts/pearl_news/drafts/{lang}",
            ]
            if args.feeds:
                lang_args_list.append(f"--feeds={args.feeds}")
            if args.limit:
                lang_args_list.append(f"--limit={args.limit}")
            if args.expand:
                lang_args_list.append("--expand")
            if args.validate:
                lang_args_list.append("--validate")
            if args.select_image:
                lang_args_list.append("--select-image")
            if args.verbose:
                lang_args_list.append("--verbose")
            if args.no_filter_qc:
                lang_args_list.append("--no-filter-qc")
            if args.v52:
                lang_args_list.append("--v52")
            import sys
            old_argv = sys.argv
            sys.argv = ["run_article_pipeline"] + lang_args_list
            exit_code = main()
            sys.argv = old_argv
            results[lang] = exit_code
        failed = [lang for lang, code in results.items() if code != 0]
        if failed:
            logger.error("Pipeline failed for languages: %s", failed)
            return 1
        logger.info("All-language pipeline complete: %s", results)
        return 0

    language = args.language.lower()
    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        out_dir = Path(f"artifacts/pearl_news/drafts/{language}")

    out_dir.mkdir(parents=True, exist_ok=True)
    config_root = root / "config"
    atoms_root = root / "atoms" / "teacher_quotes_practices"

    logger.info(
        "Pipeline start: language=%s out_dir=%s expand=%s validate=%s",
        language, out_dir, args.expand, args.validate,
    )

    # Step 1: Ingest
    try:
        items = ingest_feeds(feeds_path, limit=args.limit, per_feed_limit=args.per_feed_limit)
    except Exception as e:
        logger.exception("Feed ingest failed: %s", e)
        return 1
    logger.info("Ingested %d items", len(items))

    if not items:
        logger.warning("No items to process; writing empty manifest.")
        manifest = {
            "build_date": datetime.now(timezone.utc).isoformat(),
            "language": language,
            "feeds_path": str(feeds_path),
            "item_count": 0,
            "articles_count": 0,
            "items": [],
            "build_manifests": [],
        }
        (out_dir / "ingest_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return 0

    # Attach language to each item (used by assembler, resolver, expansion)
    for item in items:
        item["language"] = language

    # Step 2: Classify (topic + SDG)
    items = classify_sdgs(items)

    # Step 2a: Topic filter — enforce INV-1/INV-4 when --topic is specified.
    # The caller (run_daily_news_cycle.py) is responsible for assigning each teacher
    # a unique topic before calling this pipeline. This flag makes the pipeline
    # honour that assignment by discarding feed items that don't match.
    if args.topic:
        before = len(items)
        matched = [i for i in items if (i.get("topic") or "").lower() == args.topic.lower()]
        if matched:
            items = matched[:1]
            logger.info(
                "Topic filter '%s': %d → %d items", args.topic, before, len(items)
            )
        else:
            # Fallback: no feed items classified under the assigned topic today.
            # Use 'general' items so the teacher can still publish. The article
            # will carry the assigned topic as metadata for INV-1/INV-4 tracking.
            general_items = [i for i in items if (i.get("topic") or "").lower() == "general"]
            if general_items:
                logger.warning(
                    "Topic filter '%s': 0 matches — falling back to %d 'general' items.",
                    args.topic, len(general_items),
                )
                for gi in general_items:
                    gi["topic"] = args.topic  # tag with assigned topic for INV-4
                items = general_items[:1]
            else:
                logger.warning(
                    "No items matched topic='%s' and no 'general' fallback available. "
                    "Check feed coverage or topic name.",
                    args.topic,
                )
                (out_dir / "ingest_manifest.json").write_text(
                    json.dumps(
                        {
                            "build_date": datetime.now(timezone.utc).isoformat(),
                            "language": language,
                            "topic_filter": args.topic,
                            "item_count": 0,
                            "articles_output": 0,
                            "items": [],
                        },
                        indent=2,
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                return 0

    # Step 3: Select template
    items = select_templates(items)
    # Step 4: Assemble (structural draft from template + atoms/placeholders)
    items = assemble_articles(items)

    # Step 4a (NEW): Resolve named teacher per article
    for item in items:
        teacher = resolve_teacher(item, config_root=config_root, atoms_root=atoms_root)
        item["_teacher_resolved"] = teacher

    # Step 4b: LLM expansion with language-based routing (CJK6 → Qwen, EN → Claude)
    llm_yaml: dict = {}
    if yaml and (config_root / "llm_expansion.yaml").exists():
        with open(config_root / "llm_expansion.yaml", "r", encoding="utf-8") as _lf:
            llm_yaml = yaml.safe_load(_lf) or {}

    if args.expand:
        fr = ((llm_yaml.get("routing") or {}).get("fallback") or {})
        max_exp_retries = int(fr.get("max_retries") or 1)
        items = run_routed_expansion(items, config_root=config_root, max_retries=max_exp_retries)

    # Step 4b2: EI v2 article scoring (before hard validation)
    if args.expand and llm_yaml.get("ei_scoring", {}).get("enabled"):
        items = run_ei_article_scoring(items, pearl_cfg=llm_yaml)

    # Step 4c: Post-expansion validation gates
    if args.validate and args.expand:
        items = run_validation(items)
        n_failed = sum(1 for i in items if i.get("_validation_failed"))
        if n_failed:
            logger.warning(
                "%d articles failed validation gates and need manual review", n_failed
            )

    # Step 4d (NEW): Rule-based featured image selection
    if args.select_image:
        items = run_image_selection(items, config_root=config_root)

    # Step 5: Quality gates (sets qc_results, qc_passed on each)
    items = run_quality_gates(items)
    # Step 6: QC checklist (optionally filter to passed only)
    articles_to_output = run_qc_checklist(items, filter_to_passed=not args.no_filter_qc)

    # Ingest manifest
    build_date = datetime.now(timezone.utc).isoformat()
    ingest_manifest = {
        "build_date": build_date,
        "language": language,
        "feeds_path": str(feeds_path),
        "limit": args.limit,
        "per_feed_limit": args.per_feed_limit,
        "item_count": len(items),
        "articles_passed_qc": sum(1 for i in items if i.get("qc_passed")),
        "articles_validation_failed": sum(1 for i in items if i.get("_validation_failed")),
        "articles_output": len(articles_to_output),
        "items": [
            {
                "id": i.get("id"),
                "title": i.get("title"),
                "topic": i.get("topic"),
                "language": i.get("language"),
                "qc_passed": i.get("qc_passed"),
                "validation_passed": (i.get("_validation") or {}).get("passed"),
                "teacher": (i.get("_teacher_resolved") or {}).get("display_name"),
            }
            for i in items
        ],
    }
    (out_dir / "ingest_manifest.json").write_text(
        json.dumps(ingest_manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("Wrote %s", out_dir / "ingest_manifest.json")

    # Author rotation
    author_ids = [1]
    if yaml and config_root.exists():
        aw_path = config_root / "wordpress_authors.yaml"
        if aw_path.exists():
            with open(aw_path, "r", encoding="utf-8") as f:
                aw = yaml.safe_load(f) or {}
            author_ids = list(aw.get("author_ids") or [1])

    # Build manifests + article JSON output
    build_manifests = []
    for i, item in enumerate(articles_to_output):
        article_id = item.get("id", "")
        lang_suffix = f"_{language}" if language != "en" else ""
        output_filename = f"article_{article_id}{lang_suffix}.json"

        author_id = author_ids[i % len(author_ids)] if author_ids else None
        template_id = item.get("template_id") or "hard_news_spiritual_response"

        # Featured image: prefer catalog selection, then feed image, then old placeholder logic
        featured_image_data = item.get("_featured_image")
        featured_image = None
        featured_image_url = None
        featured_image_path = None

        if featured_image_data:
            if featured_image_data.get("url"):
                featured_image_url = featured_image_data["url"]
                featured_image = {
                    "url": featured_image_data["url"],
                    "alt_text": featured_image_data.get("alt_text", ""),
                    "caption": featured_image_data.get("caption", ""),
                }
            elif featured_image_data.get("path"):
                featured_image_path = featured_image_data["path"]
        else:
            # Legacy fallback: feed image or site.yaml placeholder
            feed_images = item.get("images") or []
            if feed_images and isinstance(feed_images[0], dict) and feed_images[0].get("url"):
                featured_image = feed_images[0]

        teacher = item.get("_teacher_resolved") or {}
        validation = item.get("_validation") or {}

        teacher_id_val = teacher.get("teacher_id")
        teacher_name = teacher.get("display_name") or "a teacher from the United Spiritual Leaders Forum"
        teacher_tradition = teacher.get("tradition") or "interfaith"
        teacher_attribution = teacher.get("attribution") or ""
        pub_date_display = (item.get("pub_date") or "")[:10]

        if args.v52:
            # v5.2 interactive layout: exercise sidebar, poll, co-creation, full design system
            v52_meta = {
                "teacher": teacher_id_val or "maat",
                "topic": item.get("topic", "general"),
                "sdg": item.get("primary_sdg", "3"),
                "template": template_id,
                "date": pub_date_display,
                "news_event": item.get("title", ""),
                "hero_image_url": featured_image_url or "",
            }
            article_content = assemble_v52(item, v52_meta, standalone=False)
        else:
            # INV-5: inject byline block at the top of article content
            # INV-6: sidebar block (embedded in content for WordPress post body)
            topic_label = (item.get("topic") or "").replace("_", " ").title()
            attribution_block = (
                '<p class="pn-sidebar-attribution">' + teacher_attribution + "</p>"
                if teacher_attribution else ""
            )
            byline_html = (
                f'<div class="pn-byline">'
                f'<span class="pn-byline-name">{teacher_name}</span>'
                f' | <span class="pn-byline-tradition">{teacher_tradition}</span>'
                f' | <span class="pn-byline-lang">{language.upper()}</span>'
                f' | <time class="pn-byline-date">{pub_date_display}</time>'
                f'</div>'
            )
            sidebar_html = (
                '<aside class="pn-sidebar" data-teacher="' + (teacher_id_val or "") + '">'
                '<section class="pn-sidebar-teacher">'
                '<h3 class="pn-sidebar-teacher-name">' + teacher_name + "</h3>"
                '<p class="pn-sidebar-tradition">' + teacher_tradition + "</p>"
                '<p class="pn-sidebar-lang">Writing in: ' + language.upper() + "</p>"
                + attribution_block
                + "</section>"
                '<section class="pn-sidebar-topic">'
                '<p class="pn-sidebar-topic-label">Topic: ' + topic_label + "</p>"
                "</section>"
                '<section class="pn-sidebar-cta">'
                "<p class=\"pn-sidebar-cta-text\">Follow this teacher's perspective on Pearl News</p>"
                "</section>"
                "</aside>"
            )
            raw_content = item.get("content", "")
            article_content = byline_html + "\n" + raw_content + "\n" + sidebar_html

        article_payload = {
            "title": item.get("article_title") or item.get("title", ""),
            "content": article_content,
            "teacher_id": teacher_id_val,
            "slug": article_id + lang_suffix,
            "author": author_id,
            "article_type": template_id,
            "language": language,
            "topic": item.get("topic", ""),
            "teacher_id": teacher_id_val,
            "primary_sdg": item.get("primary_sdg", ""),
            "un_body": item.get("un_body", ""),
            "url": item.get("url", ""),
            "pub_date": item.get("pub_date", ""),
            "source_feed_id": item.get("source_feed_id", ""),
            "qc_passed": item.get("qc_passed", False),
            "qc_results": item.get("qc_results", {}),
            "teacher_used": {
                "teacher_id": teacher_id_val,
                "display_name": teacher_name,
                "tradition": teacher_tradition,
            },
            "sidebar": {
                "teacher_name": teacher_name,
                "teacher_tradition": teacher_tradition,
                "teacher_language": language,
                "topic": item.get("topic", ""),
            },
            "validation": {
                "passed": validation.get("passed"),
                "failed_gates": validation.get("failed_gates", []),
            },
            "ei_composite": item.get("_ei_composite"),
            "ei_scores": item.get("_ei_scores"),
            "ei_flags": item.get("_ei_flags") or [],
            "needs_manual_review": item.get("_needs_manual_review", False),
            "sidebar": {
                "teacher_name": teacher_name,
                "teacher_tradition": teacher_tradition,
                "teacher_language": language,
                "topic": item.get("topic", ""),
            },
        }
        if featured_image:
            article_payload["featured_image"] = featured_image
        if featured_image_url:
            article_payload["featured_image_url"] = featured_image_url
        if featured_image_path:
            article_payload["featured_image_path"] = featured_image_path

        (out_dir / output_filename).write_text(
            json.dumps(article_payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        build_manifests.append(_build_manifest_item(item))

    (out_dir / "build_manifests.json").write_text(
        json.dumps(build_manifests, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info(
        "Wrote %d article drafts (%s) and build_manifests.json",
        len(articles_to_output), language,
    )

    # Editorial review queue: articles that need human follow-up
    needs_review = [
        {
            "article_id": item.get("id"),
            "language": language,
            "title": item.get("article_title") or item.get("title"),
            "topic": item.get("topic"),
            "failed_gates": (item.get("_validation") or {}).get("failed_gates", []),
            "expansion_failed": item.get("_expansion_failed", False),
            "ei_flags": item.get("_ei_flags") or [],
            "ei_composite": item.get("_ei_composite"),
            "queued_at": build_date,
        }
        for item in items
        if item.get("_needs_manual_review")
    ]
    if needs_review:
        review_queue_path = out_dir / "editorial_review_queue.json"
        review_queue_path.write_text(
            json.dumps(needs_review, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        logger.warning(
            "%d articles flagged for editorial review → %s", len(needs_review), review_queue_path
        )

    logger.info(
        "Pipeline complete [%s]: %d items → %d articles (%d need review)",
        language, len(items), len(articles_to_output), len(needs_review),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
