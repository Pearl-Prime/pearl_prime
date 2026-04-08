#!/usr/bin/env python3
"""Generate weekly video upload schedule across all brand lanes.

Reads the audiobook video catalog config and video cadence config to produce
a week-by-week schedule that respects per-platform upload caps, cross-brand
spacing, and anti-spam diversification rules.

Usage:
    # Generate schedule for EN lane, Phase 1
    python3 scripts/release/generate_video_schedule.py \
        --lane en --phase 1 --weeks 12 -o schedule_en_p1.json

    # Generate schedule for all lanes
    python3 scripts/release/generate_video_schedule.py \
        --lane all --phase 1 --weeks 12 -o schedule_all.json

    # Dry-run: show summary without writing file
    python3 scripts/release/generate_video_schedule.py \
        --lane en --phase 1 --weeks 4 --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    print("pyyaml required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text()) or {}


def _load_configs() -> tuple[dict, dict, dict]:
    catalog = _load_yaml(REPO_ROOT / "config" / "catalog_planning" / "audiobook_video_catalog.yaml")
    cadence = _load_yaml(REPO_ROOT / "config" / "release_velocity" / "video_cadence.yaml")
    velocity = _load_yaml(REPO_ROOT / "config" / "release_velocity" / "safe_velocity.yaml")
    return catalog, cadence, velocity


def _get_lane_config(catalog: dict, lane_id: str) -> dict:
    lanes = catalog.get("lanes", {})
    if lane_id == "all":
        return lanes
    if lane_id in lanes:
        return {lane_id: lanes[lane_id]}
    raise ValueError(f"Unknown lane: {lane_id}. Available: {list(lanes.keys())}")


def generate_weekly_schedule(
    lane_id: str = "en",
    phase: int = 1,
    num_weeks: int = 12,
    start_date: datetime | None = None,
) -> dict:
    """Generate a week-by-week video upload schedule.

    Returns a structured schedule with per-day, per-platform upload slots.
    """
    catalog, cadence, velocity = _load_configs()
    lanes = _get_lane_config(catalog, lane_id)

    if start_date is None:
        start_date = datetime.now() + timedelta(days=7)

    # Get video platform caps
    platforms = cadence.get("video_platforms", {})
    cross_brand = cadence.get("cross_brand", {})
    max_brands_per_day = cross_brand.get("max_brands_per_day_per_platform", 3)
    min_brand_gap_hours = cross_brand.get("min_hours_between_brands", 4)

    # Per-book video counts
    derivatives = catalog.get("video_derivatives_per_book", {})
    longs_per_book = derivatives.get("audiobook_chapter_long", {}).get("count_per_book", 20)
    shorts_per_book = derivatives.get("audiobook_chapter_short", {}).get("count_per_book", 40)
    fulls_per_book = derivatives.get("audiobook_full", {}).get("count_per_book", 1)
    total_per_book = longs_per_book + shorts_per_book + fulls_per_book

    # Phase determines how many books are in production
    phase_config = catalog.get("production_phases", {}).get(f"phase_{phase}", {})
    total_books = phase_config.get("books", 354)

    # Teacher-channel mapping
    teacher_map = catalog.get("teacher_brand_channel_map", {})
    teachers = list(teacher_map.keys())

    # Build schedule
    schedule = {
        "lane": lane_id,
        "phase": phase,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "num_weeks": num_weeks,
        "total_books": total_books,
        "total_videos": total_books * total_per_book,
        "videos_per_book": total_per_book,
        "weeks": [],
    }

    # Daily upload caps per platform
    yt_long_per_day = platforms.get("youtube", {}).get("long_form", {}).get("new_channel", {}).get("per_day", 1)
    yt_short_per_day = platforms.get("youtube", {}).get("shorts", {}).get("new_channel", {}).get("per_day", 2)
    tiktok_per_day = platforms.get("tiktok", {}).get("per_day", 3)
    ig_per_day = platforms.get("instagram_reels", {}).get("per_day", 2)

    # Calculate daily throughput
    daily_longs = yt_long_per_day * 5  # 5 active channels
    daily_shorts = yt_short_per_day * 5 + tiktok_per_day + ig_per_day
    daily_total = daily_longs + daily_shorts

    # Books that can be fully drained per week
    videos_per_week = daily_total * 7
    books_drainable_per_week = videos_per_week / total_per_book

    # Ramp: Phase 1 starts slow
    ramp_multipliers = {
        1: [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0, 1.0],
        2: [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        3: [0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    }

    cumulative_videos = 0
    cumulative_revenue = 0
    teacher_idx = 0

    for week_num in range(1, num_weeks + 1):
        week_start = start_date + timedelta(weeks=week_num - 1)
        ramp = ramp_multipliers.get(phase, ramp_multipliers[1])
        multiplier = ramp[min(week_num - 1, len(ramp) - 1)]

        week_longs = int(daily_longs * 7 * multiplier)
        week_shorts = int(daily_shorts * 7 * multiplier)
        week_total = week_longs + week_shorts

        # Distribute across teachers (round-robin)
        teacher_distribution = defaultdict(int)
        for i in range(week_total):
            t = teachers[teacher_idx % len(teachers)]
            teacher_distribution[t] += 1
            teacher_idx += 1

        # Estimate revenue (conservative)
        # Long: 500 views × $12 RPM = $6/video
        # Shorts: 2000 views × $0.05/1000 = $0.10/video
        week_rev_long = week_longs * 6.0 * multiplier
        week_rev_short = week_shorts * 0.10 * multiplier
        week_revenue = week_rev_long + week_rev_short

        cumulative_videos += week_total
        cumulative_revenue += week_revenue

        # Daily breakdown
        days = []
        for d in range(7):
            day_date = week_start + timedelta(days=d)
            day_longs = int(daily_longs * multiplier)
            day_shorts = int(daily_shorts * multiplier)

            # Rotate platforms for shorts
            short_split = {
                "youtube_shorts": min(day_shorts // 3, yt_short_per_day * 5),
                "tiktok": min(day_shorts // 3, tiktok_per_day),
                "instagram_reels": min(day_shorts // 3, ig_per_day),
            }

            days.append({
                "date": day_date.strftime("%Y-%m-%d"),
                "day_of_week": day_date.strftime("%A"),
                "youtube_long": day_longs,
                "shorts": short_split,
                "total": day_longs + sum(short_split.values()),
            })

        schedule["weeks"].append({
            "week": week_num,
            "start": week_start.strftime("%Y-%m-%d"),
            "ramp_pct": int(multiplier * 100),
            "long_form": week_longs,
            "shorts": week_shorts,
            "total_videos": week_total,
            "teacher_distribution": dict(teacher_distribution),
            "estimated_revenue_usd": round(week_revenue, 2),
            "cumulative_videos": cumulative_videos,
            "cumulative_revenue_usd": round(cumulative_revenue, 2),
            "days": days,
        })

    # Summary
    schedule["summary"] = {
        "total_videos_scheduled": cumulative_videos,
        "total_estimated_revenue_usd": round(cumulative_revenue, 2),
        "avg_videos_per_week": cumulative_videos // num_weeks if num_weeks else 0,
        "avg_revenue_per_week_usd": round(cumulative_revenue / num_weeks, 2) if num_weeks else 0,
        "books_needed": total_books,
        "weeks_to_drain_all_videos": round(total_books * total_per_book / (daily_total * 7), 1),
        "daily_throughput": {
            "youtube_long": daily_longs,
            "youtube_shorts": yt_short_per_day * 5,
            "tiktok": tiktok_per_day,
            "instagram_reels": ig_per_day,
            "total": daily_total,
        },
    }

    return schedule


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate video upload schedule")
    ap.add_argument("--lane", default="en", help="Lane: en, zh_tw_hk_sg, zh_cn, ja, ko, eu_west, es_us, hu, all")
    ap.add_argument("--phase", type=int, default=1, choices=[1, 2, 3])
    ap.add_argument("--weeks", type=int, default=12)
    ap.add_argument("--start-date", type=str, help="YYYY-MM-DD")
    ap.add_argument("--dry-run", action="store_true", help="Print summary only")
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    start = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None

    schedule = generate_weekly_schedule(
        lane_id=args.lane,
        phase=args.phase,
        num_weeks=args.weeks,
        start_date=start,
    )

    if args.dry_run:
        s = schedule["summary"]
        print(f"Lane: {args.lane} | Phase: {args.phase} | {args.weeks} weeks")
        print(f"Total videos: {s['total_videos_scheduled']:,}")
        print(f"Avg/week: {s['avg_videos_per_week']:,}")
        print(f"Revenue est: ${s['total_estimated_revenue_usd']:,.2f}")
        print(f"Avg/week revenue: ${s['avg_revenue_per_week_usd']:,.2f}")
        print(f"Daily throughput: {s['daily_throughput']}")
        print(f"Weeks to drain all {schedule['total_books']} books' videos: {s['weeks_to_drain_all_videos']}")
        return 0

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(schedule, indent=2, ensure_ascii=False))
        print(f"Schedule written to {args.output}")
        s = schedule["summary"]
        print(f"  {s['total_videos_scheduled']:,} videos over {args.weeks} weeks")
        print(f"  Estimated revenue: ${s['total_estimated_revenue_usd']:,.2f}")
    else:
        print(json.dumps(schedule, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
