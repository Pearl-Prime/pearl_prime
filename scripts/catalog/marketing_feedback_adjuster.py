#!/usr/bin/env python3
"""
Phoenix Omega Marketing Feedback Adjuster
==========================================
Reads daily marketing signals and adjusts FUTURE weeks of the 12-month projection.

Adjustment rules:
  - format conversion_rate > 2× baseline → increase format share 5-10%
  - format conversion_rate < 0.5× baseline → decrease format share 3-5%
  - listener_growth > 10% → increase podcast share 3-5%
  - topic search_volume_change > 20% → tag next 4 standalones with that topic
  - Weekly cap: ±10% per format per adjustment
  - Monthly cap: ±15% from original annual target per format
  - All adjustments logged to artifacts/projections/adjustment_log.jsonl

Usage:
    python3 scripts/catalog/marketing_feedback_adjuster.py --date today
    python3 scripts/catalog/marketing_feedback_adjuster.py --date 2026-04-10 --dry-run
    python3 scripts/catalog/marketing_feedback_adjuster.py --date today --brand stillness_press --lane english_global
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
_CONFIG_ROOT = (_MAIN_REPO if not (REPO_ROOT / "config" / "brand_management").exists()
                and (_MAIN_REPO / "config" / "brand_management").exists() else REPO_ROOT)

SIGNALS_PATH = REPO_ROOT / "artifacts" / "catalog" / "marketing_signals.jsonl"
PROJECTIONS_DIR = REPO_ROOT / "artifacts" / "projections"
ADJ_LOG_PATH = REPO_ROOT / "artifacts" / "projections" / "adjustment_log.jsonl"

# Baselines for signal interpretation
BASELINE_CONVERSION_RATE = 0.025  # from investor DD
BASELINE_LISTENER_GROWTH = 0.05


def _today_iso() -> str:
    return date.today().isoformat()


def _current_week_num() -> int:
    return date.today().isocalendar()[1]


def _week_num_from_str(week_str: str) -> int:
    """Parse '2026-W15' → 15."""
    return int(week_str.split("W")[1])


def load_signals(signal_date: str) -> list[dict]:
    """Load all signals for a given date from marketing_signals.jsonl."""
    if not SIGNALS_PATH.exists():
        return []
    signals = []
    with open(SIGNALS_PATH, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if record.get("date") == signal_date:
                    signals.append(record)
            except json.JSONDecodeError:
                continue
    return signals


def load_projection(brand_id: str, lane: str, year: int) -> dict | None:
    """Load an existing projection JSON."""
    path = PROJECTIONS_DIR / f"{brand_id}_{lane}_{year}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_projection(brand_id: str, lane: str, year: int, projection: dict) -> None:
    """Save adjusted projection back to disk."""
    path = PROJECTIONS_DIR / f"{brand_id}_{lane}_{year}.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(projection, fh, indent=2)


def log_adjustment(entry: dict, dry_run: bool = False) -> None:
    """Append adjustment to adjustment_log.jsonl."""
    if dry_run:
        return
    ADJ_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ADJ_LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def compute_adjustments(signals: list[dict]) -> list[dict]:
    """
    Convert raw signals → adjustment directives.
    Returns list of {market, format, direction, pct_shift, reason}.
    """
    adjustments = []
    for sig in signals:
        sig_type = sig.get("signal")
        market = sig.get("market", "english_global")

        if sig_type == "format_performance":
            fmt = sig.get("format")
            metric = sig.get("metric")
            value = float(sig.get("value", 0))
            note = sig.get("note", "")

            if metric == "conversion_rate":
                ratio = value / BASELINE_CONVERSION_RATE
                if ratio >= 2.0:
                    shift = min(0.10, 0.05 + (ratio - 2.0) * 0.025)  # 5-10%
                    adjustments.append({
                        "market": market, "format": fmt,
                        "direction": "increase", "pct_shift": shift,
                        "reason": f"conversion_rate {value:.3f} is {ratio:.1f}× baseline ({BASELINE_CONVERSION_RATE}). Note: {note}",
                    })
                elif ratio <= 0.5:
                    shift = min(0.05, 0.03 + (0.5 - ratio) * 0.04)  # 3-5%
                    adjustments.append({
                        "market": market, "format": fmt,
                        "direction": "decrease", "pct_shift": shift,
                        "reason": f"conversion_rate {value:.3f} is {ratio:.1f}× baseline. Note: {note}",
                    })

            elif metric == "listener_growth":
                if value > BASELINE_LISTENER_GROWTH:
                    shift = min(0.05, 0.03 + (value - BASELINE_LISTENER_GROWTH) * 0.5)
                    adjustments.append({
                        "market": market, "format": "podcast_episodes",
                        "direction": "increase", "pct_shift": shift,
                        "reason": f"listener_growth {value:.1%} above baseline {BASELINE_LISTENER_GROWTH:.1%}. Note: {note}",
                    })

        elif sig_type == "topic_demand":
            topic = sig.get("topic")
            metric = sig.get("metric")
            value = float(sig.get("value", 0))
            note = sig.get("note", "")

            if metric == "search_volume_change" and value >= 0.20:
                adjustments.append({
                    "market": market, "format": "standalone_books",
                    "direction": "topic_shift", "topic": topic,
                    "slots": 4,
                    "reason": f"topic '{topic}' search volume +{value:.0%}. Note: {note}",
                })

    return adjustments


def apply_adjustments(
    projection: dict,
    adjustments: list[dict],
    signal_date: str,
    dry_run: bool = False,
) -> tuple[dict, list[dict]]:
    """
    Apply adjustments to all FUTURE weeks of projection.
    Returns (modified_projection, log_entries).
    """
    today_week = _current_week_num()
    year = projection.get("year", 2026)
    original_format_mix = projection.get("format_mix", {})
    annual_target = projection.get("annual_target", 780)
    log_entries = []

    for adj in adjustments:
        market = adj["market"]
        lane = projection.get("lane", "")
        # Only apply if market matches lane (rough check)
        if market not in lane and market != "english_global" and lane != "english_global":
            # Market/lane mismatch — skip
            continue

        fmt = adj.get("format")
        direction = adj["direction"]

        if direction == "topic_shift":
            # Mark next 4 standalone slots with topic preference
            slots_tagged = 0
            for w in projection["weeks"]:
                week_num = _week_num_from_str(w["week"])
                if week_num <= today_week:
                    continue
                if slots_tagged >= adj.get("slots", 4):
                    break
                if not w.get("locked"):
                    w.setdefault("topic_hints", [])
                    w["topic_hints"].append(adj.get("topic"))
                    slots_tagged += 1

            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "signal_date": signal_date,
                "brand_id": projection.get("brand_id"),
                "lane": lane,
                "adjustment_type": "topic_shift",
                "topic": adj.get("topic"),
                "slots_tagged": slots_tagged,
                "reason": adj["reason"],
                "provenance": "MARKETING_SIGNAL",
            }
            log_entries.append(entry)
            if dry_run:
                print(f"    [DRY RUN] topic_shift '{adj.get('topic')}' → {slots_tagged} future standalone slots")
            continue

        # Compute original weekly target for this format
        original_pct = original_format_mix.get(fmt, 0)
        original_weekly_target = annual_target * original_pct / 52

        # Apply to future unlocked weeks
        weeks_adjusted = 0
        for w in projection["weeks"]:
            week_num = _week_num_from_str(w["week"])
            if week_num <= today_week:
                continue
            if w.get("locked"):
                continue
            if fmt not in w["planned"]:
                continue

            current_qty = w["planned"][fmt]
            pct_shift = adj["pct_shift"]

            if direction == "increase":
                delta = round(current_qty * pct_shift)
                new_qty = current_qty + delta
            else:
                delta = round(current_qty * pct_shift)
                new_qty = max(0, current_qty - delta)

            # Weekly cap: ±10% of current quantity
            max_delta = round(current_qty * 0.10)
            actual_delta = min(abs(new_qty - current_qty), max_delta)
            if direction == "increase":
                new_qty = current_qty + actual_delta
            else:
                new_qty = max(0, current_qty - actual_delta)

            # Monthly cap: no format's annual share shifts >15% from original
            # Estimate: if we changed every remaining week, would we exceed 15%?
            remaining_weeks = 52 - today_week
            if remaining_weeks > 0:
                projected_annual_change_pct = abs(new_qty - current_qty) * remaining_weeks / (original_weekly_target * 52 + 1)
                if projected_annual_change_pct > 0.15:
                    # Scale back adjustment to stay within 15% annual cap
                    allowed_delta = round(original_weekly_target * 52 * 0.15 / remaining_weeks)
                    if direction == "increase":
                        new_qty = current_qty + allowed_delta
                    else:
                        new_qty = max(0, current_qty - allowed_delta)

            w["planned"][fmt] = max(0, new_qty)
            weeks_adjusted += 1

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signal_date": signal_date,
            "brand_id": projection.get("brand_id"),
            "lane": lane,
            "adjustment_type": direction,
            "format": fmt,
            "pct_shift": adj["pct_shift"],
            "weeks_adjusted": weeks_adjusted,
            "reason": adj["reason"],
            "weekly_cap_applied": True,
            "monthly_cap_applied": True,
            "provenance": "MARKETING_SIGNAL",
        }
        log_entries.append(entry)
        if dry_run:
            print(f"    [DRY RUN] {direction} '{fmt}' by {adj['pct_shift']:.1%} across {weeks_adjusted} future weeks")

    return projection, log_entries


def find_all_projections(year: int) -> list[tuple[str, str]]:
    """Find all brand/lane projection files for a given year."""
    pairs = []
    if not PROJECTIONS_DIR.exists():
        return pairs
    for path in PROJECTIONS_DIR.glob(f"*_{year}.json"):
        name = path.stem  # e.g. stillness_press_english_global_2026
        # Split on _{year} to get brand_lane
        brand_lane = name[: -len(f"_{year}")]
        # We need to split brand_id from lane — lanes are known
        known_lanes = [
            "english_global", "dach", "france", "spain", "italy",
            "latam", "brazil", "japan", "korea", "taiwan", "china", "hungary",
        ]
        lane = None
        brand_id = None
        for kl in known_lanes:
            if brand_lane.endswith(f"_{kl}"):
                lane = kl
                brand_id = brand_lane[: -len(f"_{kl}")]
                break
        if brand_id and lane:
            pairs.append((brand_id, lane))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phoenix Omega Marketing Feedback Adjuster — daily signal → projection replan"
    )
    parser.add_argument("--date", default="today", help="Signal date to process (YYYY-MM-DD or 'today')")
    parser.add_argument("--brand", help="Limit to this brand_id")
    parser.add_argument("--lane", help="Limit to this lane")
    parser.add_argument("--year", type=int, default=2026, help="Projection year")
    parser.add_argument("--dry-run", action="store_true", help="Show adjustments without saving")
    args = parser.parse_args()

    signal_date = _today_iso() if args.date == "today" else args.date
    print(f"Processing marketing signals for date: {signal_date}")

    signals = load_signals(signal_date)
    if not signals:
        print(f"  No signals found for {signal_date} in {SIGNALS_PATH}")
        sys.exit(0)
    print(f"  Found {len(signals)} signal(s)")

    adjustments = compute_adjustments(signals)
    if not adjustments:
        print("  No actionable adjustments derived from signals")
        sys.exit(0)
    print(f"  Derived {len(adjustments)} adjustment directive(s)")

    if args.brand and args.lane:
        pairs = [(args.brand, args.lane)]
    else:
        pairs = find_all_projections(args.year)
        if not pairs:
            print(f"  No projection files found in {PROJECTIONS_DIR} for year {args.year}")
            sys.exit(0)

    for brand_id, lane in pairs:
        projection = load_projection(brand_id, lane, args.year)
        if not projection:
            print(f"  Skipping {brand_id}/{lane}: no projection file")
            continue

        print(f"  Adjusting {brand_id}/{lane}:")
        updated_projection, log_entries = apply_adjustments(projection, adjustments, signal_date, args.dry_run)

        if not args.dry_run:
            save_projection(brand_id, lane, args.year, updated_projection)
            for entry in log_entries:
                log_adjustment(entry, dry_run=False)
            print(f"    Saved {len(log_entries)} adjustment(s)")

    if args.dry_run:
        print("\n[DRY RUN] No files written.")
    else:
        print(f"\nAdjustment log: {ADJ_LOG_PATH}")


if __name__ == "__main__":
    main()
