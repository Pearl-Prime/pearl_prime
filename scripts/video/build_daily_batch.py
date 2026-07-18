#!/usr/bin/env python3
"""
Build Daily Batch — select videos from the publish queue for today's daily publishing run.

Reads the publish queue (artifacts/video/publish_queue/), applies cross-dedup,
content-mix targets, day-of-week multipliers, and per-channel caps, then writes
a daily_batch manifest that run_upload.py consumes.

Usage:
  # Preview what would be selected (dry run):
  python scripts/video/build_daily_batch.py --dry-run

  # Build batch for a specific brand:
  python scripts/video/build_daily_batch.py --brand stillness_press

  # Build batch for all brands:
  python scripts/video/build_daily_batch.py

  # Build batch for a specific date (backfill):
  python scripts/video/build_daily_batch.py --date 2026-04-01
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import load_yaml, write_atomically

logger = logging.getLogger(__name__)


def load_schedule_config() -> dict:
    """Load daily_publish_schedule.yaml."""
    return load_yaml("config/video/daily_publish_schedule.yaml")


def load_channel_registry() -> dict:
    """Load channel_registry.yaml channels."""
    reg = load_yaml("config/video/channel_registry.yaml")
    return reg.get("channels", {})


def load_dedup_config() -> dict:
    """Load cross_video_dedup.yaml."""
    return load_yaml("config/video/cross_video_dedup.yaml")


def discover_queue_items(queue_dir: Path, brand_filter: str | None = None) -> list[dict]:
    """Scan publish queue for ready-to-publish video manifests."""
    items: list[dict] = []
    if not queue_dir.exists():
        return items
    for manifest_path in sorted(queue_dir.glob("*/distribution_manifest.json")):
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            # Filter by brand if specified
            if brand_filter and data.get("brand_id") != brand_filter:
                continue
            data["_manifest_path"] = str(manifest_path)
            data["_queue_dir"] = str(manifest_path.parent)
            items.append(data)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Skipping %s: %s", manifest_path, exc)
    return items


def check_dedup(
    selected: list[dict],
    candidate: dict,
    dedup_cfg: dict,
) -> bool:
    """Return True if candidate passes cross-video dedup checks against already-selected items."""
    max_shared = dedup_cfg.get("max_shared_primary_assets_per_window", 1)
    candidate_assets = set(candidate.get("primary_asset_ids", []))
    if not candidate_assets:
        return True

    for item in selected:
        item_assets = set(item.get("primary_asset_ids", []))
        shared = candidate_assets & item_assets
        if len(shared) > max_shared:
            logger.debug(
                "Dedup blocked: %s shares %d assets with %s",
                candidate.get("video_id"),
                len(shared),
                item.get("video_id"),
            )
            return False
    return True


def score_candidate(candidate: dict, schedule_cfg: dict, day_name: str) -> float:
    """Score a candidate video for batch inclusion priority."""
    priority = schedule_cfg.get("priority", {})
    engagement_w = priority.get("engagement_score_weight", 0.4)
    recency_w = priority.get("recency_weight", 0.3)
    diversity_w = priority.get("diversity_weight", 0.3)

    # Engagement score (from analytics feedback, 0-1)
    engagement = float(candidate.get("engagement_score", 0.5))

    # Recency score (newer = higher, based on created_at)
    recency = 0.5  # default mid-score
    created = candidate.get("created_at", "")
    if created:
        try:
            created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            age_hours = (datetime.now(timezone.utc) - created_dt).total_seconds() / 3600
            recency = max(0.0, min(1.0, 1.0 - (age_hours / (14 * 24))))  # 14-day decay
        except (ValueError, TypeError):
            pass

    # Diversity placeholder (penalize same content_type clustering)
    diversity = 0.5

    base_score = (engagement * engagement_w) + (recency * recency_w) + (diversity * diversity_w)

    # Day-of-week multiplier
    dow_mults = schedule_cfg.get("day_of_week_multipliers", {})
    dow_mult = dow_mults.get(day_name.lower(), 1.0)

    return base_score * dow_mult


def build_batch(
    brand: str | None,
    target_date: datetime,
    dry_run: bool = False,
) -> dict:
    """Build a daily batch manifest for the given brand(s) and date."""
    schedule_cfg = load_schedule_config()
    channels = load_channel_registry()
    dedup_cfg = load_dedup_config()

    queue_dir = REPO_ROOT / (schedule_cfg.get("queue", {}).get("ready_dir", "artifacts/video/publish_queue"))
    batch_limits = schedule_cfg.get("batch_limits", {})
    max_per_channel = batch_limits.get("max_videos_per_channel_per_day", 3)
    max_per_brand = batch_limits.get("max_videos_per_brand_per_day", 9)

    day_name = target_date.strftime("%A")

    # Discover queue items
    items = discover_queue_items(queue_dir, brand_filter=brand)
    logger.info("Found %d items in publish queue (brand=%s)", len(items), brand or "all")

    # Score and sort
    for item in items:
        item["_score"] = score_candidate(item, schedule_cfg, day_name)
    items.sort(key=lambda x: x["_score"], reverse=True)

    # Select with constraints
    selected: list[dict] = []
    channel_counts: dict[str, int] = {}
    brand_counts: dict[str, int] = {}

    for item in items:
        vid_brand = item.get("brand_id", "unknown")
        vid_channel = item.get("channel_id", "unknown")

        # Per-channel cap
        if channel_counts.get(vid_channel, 0) >= max_per_channel:
            continue
        # Per-brand cap
        if brand_counts.get(vid_brand, 0) >= max_per_brand:
            continue
        # Cross-dedup
        if not check_dedup(selected, item, dedup_cfg):
            continue

        selected.append(item)
        channel_counts[vid_channel] = channel_counts.get(vid_channel, 0) + 1
        brand_counts[vid_brand] = brand_counts.get(vid_brand, 0) + 1

    # Build output manifest
    batch_id = f"batch-{target_date.strftime('%Y%m%d')}"
    if brand:
        batch_id += f"-{brand}"

    batch_entries = []
    for item in selected:
        entry = {
            "video_id": item.get("video_id"),
            "channel_id": item.get("channel_id"),
            "brand_id": item.get("brand_id"),
            "content_type": item.get("content_type"),
            "title": item.get("title"),
            "platforms": item.get("platforms", []),
            "video_provenance_path": item.get("video_provenance_path"),
            "queue_dir": item.get("_queue_dir"),
            "score": round(item.get("_score", 0), 4),
        }
        batch_entries.append(entry)

    manifest = {
        "batch_id": batch_id,
        "date": target_date.strftime("%Y-%m-%d"),
        "day_of_week": day_name,
        "brand_filter": brand,
        "total_selected": len(selected),
        "channel_counts": channel_counts,
        "brand_counts": brand_counts,
        "entries": batch_entries,
        "dry_run": dry_run,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    if not dry_run:
        out_dir = REPO_ROOT / "artifacts" / "video" / "daily_batches"
        out_path = out_dir / f"{batch_id}.json"
        write_atomically(out_path, manifest)
        logger.info("Wrote batch manifest: %s (%d videos)", out_path, len(selected))
    else:
        logger.info("[DRY RUN] Would select %d videos for %s", len(selected), batch_id)

    return manifest


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    ap = argparse.ArgumentParser(description="Build daily video publishing batch")
    ap.add_argument("--brand", default=None, help="Brand filter (stillness_press, cognitive_clarity, …)")
    ap.add_argument("--date", default=None, help="Target date YYYY-MM-DD (default: today UTC)")
    ap.add_argument("--dry-run", action="store_true", help="Preview selection without writing manifest")
    ap.add_argument("-o", "--output", default=None, help="Override output path for batch manifest")
    args = ap.parse_args()

    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        target_date = datetime.now(timezone.utc)

    manifest = build_batch(
        brand=args.brand,
        target_date=target_date,
        dry_run=args.dry_run,
    )

    if args.output and not args.dry_run:
        write_atomically(Path(args.output), manifest)
        logger.info("Wrote to override path: %s", args.output)

    # Print summary to stdout
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
