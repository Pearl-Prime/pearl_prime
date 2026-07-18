#!/usr/bin/env python3
"""
Phoenix Omega Projection Planner
==================================
Generates 52-week organic production plans per brand/lane from annual targets.

Usage:
    python3 scripts/catalog/projection_planner.py --brand stillness_press --lane english_global --year 2026
    python3 scripts/catalog/projection_planner.py --all-brands --year 2026
    python3 scripts/catalog/projection_planner.py --all-brands --year 2026 --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
_CONFIG_ROOT = _MAIN_REPO if not (REPO_ROOT / "config" / "brand_management").exists() and (_MAIN_REPO / "config" / "brand_management").exists() else REPO_ROOT

try:
    import yaml
except ImportError:
    yaml = None


def _load_yaml(path: Path) -> Any:
    if yaml is not None:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    raise ImportError(f"PyYAML required. pip install pyyaml")


def load_annual_targets() -> dict:
    for root in [REPO_ROOT, _CONFIG_ROOT]:
        p = root / "config/catalog/annual_projection_targets.yaml"
        if p.exists():
            return _load_yaml(p)
    raise FileNotFoundError("annual_projection_targets.yaml not found")


def load_brand_registry() -> dict:
    for root in [REPO_ROOT, _CONFIG_ROOT]:
        p = root / "config/brand_management/global_brand_registry.yaml"
        if p.exists():
            return _load_yaml(p)
    raise FileNotFoundError("global_brand_registry.yaml not found")


def week_to_quarter(week_num: int) -> str:
    """Map week number (1-52) to Q1/Q2/Q3/Q4."""
    if week_num <= 13:
        return "Q1"
    elif week_num <= 26:
        return "Q2"
    elif week_num <= 39:
        return "Q3"
    else:
        return "Q4"


def plan_annual_schedule(
    brand_id: str,
    lane: str,
    year: int,
    targets: dict,
    seed: int | None = None,
) -> dict:
    """Generate 52-week organic production plan for one brand/lane."""
    if seed is None:
        seed = int(hashlib.sha256(f"{brand_id}:{lane}:{year}".encode()).hexdigest(), 16) % (2**31)
    rng = random.Random(seed)

    global_defaults = targets.get("global_defaults", {})
    lane_config = targets.get("lanes", {}).get(lane, {})

    # Merge lane overrides onto global defaults
    format_mix = {**global_defaults.get("format_mix", {}), **lane_config.get("format_mix", {})}
    seasonal_weights = lane_config.get("seasonal_weights", {"Q1": 1.0, "Q2": 1.0, "Q3": 1.0, "Q4": 1.0})
    annual_target = global_defaults.get("annual_titles_per_brand", 780)
    annual_series = global_defaults.get("annual_series_per_brand", 12)
    max_series_length = global_defaults.get("max_series_length", 8)

    # Base weekly allocation per format (floating point)
    base_per_week = {fmt: annual_target * pct / 52 for fmt, pct in format_mix.items()}

    weeks = []
    for week_num in range(1, 53):
        quarter = week_to_quarter(week_num)
        seasonal_factor = seasonal_weights.get(quarter, 1.0)

        week_plan = {}
        for fmt, base in base_per_week.items():
            # Smooth sine wave variation (organic cadence) + gaussian noise
            # Phase offset per format so they don't all peak/valley together
            fmt_phase = int(hashlib.sha256(fmt.encode()).hexdigest(), 16) % 100 / 100.0
            sine_wave = 1.0 + 0.15 * math.sin(2 * math.pi * (week_num / 52 + fmt_phase))
            noise = rng.gauss(1.0, 0.10)
            noise = max(0.70, min(1.30, noise))  # clamp to ±30%

            quantity = max(0, round(base * seasonal_factor * sine_wave * noise))
            week_plan[fmt] = quantity

        weeks.append({
            "week": f"{year}-W{week_num:02d}",
            "brand_id": brand_id,
            "lane": lane,
            "quarter": quarter,
            "seasonal_factor": seasonal_factor,
            "planned": week_plan,
            "locked": False,
        })

    # Ensure no two adjacent weeks have identical format counts
    for i in range(1, len(weeks)):
        prev = weeks[i - 1]["planned"]
        curr = weeks[i]["planned"]
        if curr == prev:
            # Bump one format by 1 to break the tie
            fmt_to_bump = list(curr.keys())[week_num % len(curr)]
            weeks[i]["planned"][fmt_to_bump] = max(0, curr[fmt_to_bump] + rng.choice([-1, 1]))

    # Normalize: ensure 52-week totals match annual target per format ±5%
    _normalize_to_annual(weeks, annual_target, format_mix)

    # Plan series arcs: cluster installments organically
    series_plan = _plan_series_arcs(brand_id, lane, year, annual_series, max_series_length, rng)

    return {
        "schema_version": 1,
        "brand_id": brand_id,
        "lane": lane,
        "year": year,
        "annual_target": annual_target,
        "format_mix": format_mix,
        "seasonal_weights": seasonal_weights,
        "seed": seed,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provenance": "PROJECTION — based on annual targets + organic distribution algorithm",
        "series_plan": series_plan,
        "weeks": weeks,
    }


def _normalize_to_annual(weeks: list[dict], annual_target: int, format_mix: dict) -> None:
    """Adjust weekly quantities so 52-week sums match annual targets ±5%."""
    # Sum current planned quantities per format
    fmt_totals: dict[str, int] = {}
    for w in weeks:
        for fmt, qty in w["planned"].items():
            fmt_totals[fmt] = fmt_totals.get(fmt, 0) + qty

    # Target per format
    fmt_targets = {fmt: annual_target * pct for fmt, pct in format_mix.items()}

    # Scale each format proportionally
    for fmt, target in fmt_targets.items():
        actual = fmt_totals.get(fmt, 0)
        if actual == 0:
            continue
        scale = target / actual
        if 0.95 <= scale <= 1.05:
            continue  # already within ±5%
        running = 0.0
        for w in weeks:
            if fmt not in w["planned"]:
                continue
            exact = w["planned"][fmt] * scale
            rounded = round(exact)
            w["planned"][fmt] = max(0, rounded)
            running += rounded


def _plan_series_arcs(
    brand_id: str, lane: str, year: int, annual_series: int, max_series_length: int, rng: random.Random
) -> list[dict]:
    """Plan series launch and cadence across 52 weeks."""
    arcs = []
    week_cursor = 1

    for series_num in range(1, annual_series + 1):
        if week_cursor > 52:
            break

        # Each series: 2-3 installments in launch week, then 1/week for 4-6 weeks, pause
        launch_burst = rng.randint(2, 3)
        run_weeks = min(rng.randint(4, 6), max_series_length - launch_burst)
        total_installments = launch_burst + run_weeks

        arc = {
            "series_id": f"{brand_id}_{lane}_{year}_s{series_num:02d}",
            "launch_week": f"{year}-W{week_cursor:02d}",
            "installments": total_installments,
            "launch_burst": launch_burst,
            "run_weeks": run_weeks,
        }
        arcs.append(arc)

        # Advance cursor: launch week + run_weeks + 2-week gap before next series
        gap = rng.randint(2, 4)
        week_cursor += 1 + run_weeks + gap

    return arcs


def generate_and_save(brand_id: str, lane: str, year: int, targets: dict, dry_run: bool = False, output_dir: Path | None = None) -> dict:
    """Generate plan and optionally save to disk."""
    plan = plan_annual_schedule(brand_id, lane, year, targets)

    if output_dir is None:
        output_dir = REPO_ROOT / "artifacts" / "projections"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{brand_id}_{lane}_{year}.json"

    if not dry_run:
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(plan, fh, indent=2)
        print(f"  Wrote {output_path.relative_to(REPO_ROOT)}")
    else:
        # Compute totals for display
        totals: dict[str, int] = {}
        for w in plan["weeks"]:
            for fmt, qty in w["planned"].items():
                totals[fmt] = totals.get(fmt, 0) + qty
        grand_total = sum(totals.values())
        print(f"  [DRY RUN] {brand_id}/{lane}/{year}: {grand_total} titles across 52 weeks")
        for fmt, qty in sorted(totals.items()):
            pct = qty / grand_total * 100 if grand_total else 0
            print(f"    {fmt:25s} {qty:4d}  ({pct:.1f}%)")

    return plan


def get_all_brands_and_lanes(brand_registry: dict) -> list[tuple[str, str]]:
    """Extract all brand_id/lane pairs from brand registry."""
    pairs = []
    brands = brand_registry.get("brands", {})
    for brand_id, brand_data in brands.items():
        lanes = brand_data.get("lanes", [])
        if isinstance(lanes, list):
            for lane in lanes:
                pairs.append((brand_id, lane))
        elif isinstance(lanes, dict):
            for lane in lanes.keys():
                pairs.append((brand_id, lane))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description="Phoenix Omega Projection Planner — organic 52-week plan generator")
    parser.add_argument("--brand", help="Brand ID to plan (e.g. stillness_press)")
    parser.add_argument("--lane", help="Lane to plan (e.g. english_global)")
    parser.add_argument("--year", type=int, default=2026, help="Projection year (default: 2026)")
    parser.add_argument("--all-brands", action="store_true", help="Plan all brands × all lanes")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated without writing")
    parser.add_argument("--output-dir", help="Override output directory (default: artifacts/projections/)")
    args = parser.parse_args()

    targets = load_annual_targets()
    output_dir = Path(args.output_dir) if args.output_dir else None

    if args.all_brands:
        try:
            brand_registry = load_brand_registry()
            pairs = get_all_brands_and_lanes(brand_registry)
        except FileNotFoundError:
            print("WARNING: brand registry not found; using config lanes list only", file=sys.stderr)
            pairs = []

        if not pairs:
            # Fallback: generate for all configured lanes with placeholder brand
            lanes = list(targets.get("lanes", {}).keys())
            print(f"No brand registry found; generating plans for {len(lanes)} lanes with 'placeholder' brand")
            for lane in lanes:
                generate_and_save("placeholder", lane, args.year, targets, args.dry_run, output_dir)
        else:
            print(f"Generating plans for {len(pairs)} brand/lane pairs...")
            for brand_id, lane in pairs:
                if lane not in targets.get("lanes", {}):
                    continue  # skip lanes not in projection config
                generate_and_save(brand_id, lane, args.year, targets, args.dry_run, output_dir)
        print("Done.")

    elif args.brand and args.lane:
        generate_and_save(args.brand, args.lane, args.year, targets, args.dry_run, output_dir)

    elif args.brand or args.lane:
        parser.error("Specify both --brand and --lane, or use --all-brands")

    else:
        parser.error("Specify --brand + --lane, or use --all-brands")


if __name__ == "__main__":
    main()
