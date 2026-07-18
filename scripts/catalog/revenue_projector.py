#!/usr/bin/env python3
"""
Phoenix Omega Revenue Projector
================================
Generates 12-month revenue forecast from 52-week projection plans.

Inputs:
    artifacts/projections/{brand}_{lane}_{year}.json (per-brand plans)
    config/catalog/annual_projection_targets.yaml (ASP, conversion rate)

Outputs:
    artifacts/projections/revenue_forecast_{year}.json
    artifacts/projections/revenue_forecast_{year}.md

Usage:
    python3 scripts/catalog/revenue_projector.py --year 2026
    python3 scripts/catalog/revenue_projector.py --year 2026 --format md
    python3 scripts/catalog/revenue_projector.py --year 2026 --brand stillness_press --lane english_global
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
_CONFIG_ROOT = (_MAIN_REPO if not (REPO_ROOT / "config" / "brand_management").exists()
                and (_MAIN_REPO / "config" / "brand_management").exists() else REPO_ROOT)

PROJECTIONS_DIR = REPO_ROOT / "artifacts" / "projections"

# Format revenue share weights (some formats monetize better per title)
FORMAT_REVENUE_WEIGHTS = {
    "series_books": 1.20,        # Series readers buy more installments
    "standalone_books": 1.00,    # Baseline
    "micro_books": 0.40,         # $0.99 price point
    "manga_chapters": 0.60,      # Serialized — per-chapter revenue lower
    "podcast_episodes": 0.20,    # Primarily listener-supported / Patreon
    "format_variations": 0.80,   # Same content, different format — some cannibalization
    "video_audiobooks": 0.15,    # YouTube revenue per unit (ad-based, low)
}

# Market revenue multipliers (from growth_engine_config.yaml market data)
MARKET_MULTIPLIERS = {
    "english_global": 1.00,
    "dach": 0.75,
    "france": 0.65,
    "spain": 0.55,
    "italy": 0.50,
    "latam": 0.45,
    "brazil": 0.45,
    "japan": 0.70,
    "korea": 0.60,
    "taiwan": 0.55,
    "china": 0.40,
    "hungary": 0.20,
}

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

KNOWN_LANES = [
    "english_global", "dach", "france", "spain", "italy",
    "latam", "brazil", "japan", "korea", "taiwan", "china", "hungary",
]


def _try_load_yaml(path: Path) -> dict:
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:
        return {}


def load_marketing_assumptions() -> dict:
    """Load lower-avg marketing assumptions (single source of truth).

    See config/marketing/marketing_assumptions.yaml. Authority:
    docs/FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md G5.
    """
    for root in [REPO_ROOT, _CONFIG_ROOT]:
        p = root / "config/marketing/marketing_assumptions.yaml"
        if p.exists():
            return _try_load_yaml(p)
    return {}


def load_targets() -> dict:
    """Load annual projection targets, backstopped by lower-avg marketing assumptions.

    Order of precedence for `conversion_rate` / `blended_asp` defaults when
    `annual_projection_targets.yaml` is missing or incomplete:
      1. config/catalog/annual_projection_targets.yaml (per-lane / global)
      2. config/marketing/marketing_assumptions.yaml (lower-avg defaults)
      3. hard-coded fallback (lower-avg conservative)
    """
    targets: dict = {}
    for root in [REPO_ROOT, _CONFIG_ROOT]:
        p = root / "config/catalog/annual_projection_targets.yaml"
        if p.exists():
            targets = _try_load_yaml(p)
            break

    # Backstop missing global_defaults from marketing_assumptions.yaml.
    if not targets.get("global_defaults", {}).get("conversion_rate"):
        ma = load_marketing_assumptions()
        # Use email_to_purchase as the primary funnel-stage conversion baseline
        # (lower-avg 1.5%); fallback to visitor_to_freebie (2.5%) if missing.
        cr = (ma.get("conversion_rates", {}) or {}).get("email_to_purchase")
        if cr is None:
            cr = (ma.get("conversion_rates", {}) or {}).get("visitor_to_freebie", 0.025)
        targets.setdefault("global_defaults", {})
        targets["global_defaults"].setdefault("blended_asp", 6.25)
        targets["global_defaults"].setdefault("conversion_rate", cr)

    return targets or {"global_defaults": {"blended_asp": 6.25, "conversion_rate": 0.025}}


def week_to_month(week_num: int, year: int = 2026) -> int:
    """Approximate week → month (1-12). Weeks 1-4=Jan, 5-8=Feb, etc."""
    month = min(12, max(1, (week_num - 1) * 12 // 52 + 1))
    return month


def compute_week_revenue(week: dict, blended_asp: float, conversion_rate: float, market_mult: float) -> tuple[float, float, float]:
    """Compute low/mid/high revenue for a single week."""
    planned = week.get("planned", {})
    weighted_titles = 0.0
    for fmt, qty in planned.items():
        weight = FORMAT_REVENUE_WEIGHTS.get(fmt, 1.0)
        weighted_titles += qty * weight

    # Revenue = titles × ASP × conversion × market_mult
    mid = weighted_titles * blended_asp * conversion_rate * market_mult
    low = mid * 0.6   # conservative scenario
    high = mid * 1.6  # optimistic scenario (viral, promo lift)

    return low, mid, high


def find_all_projections(year: int, brand_filter: str | None = None, lane_filter: str | None = None) -> list[Path]:
    """Find projection JSON files."""
    paths = []
    if not PROJECTIONS_DIR.exists():
        return paths
    for path in sorted(PROJECTIONS_DIR.glob(f"*_{year}.json")):
        if path.name.startswith("revenue_forecast"):
            continue
        stem = path.stem
        # Check filters
        if brand_filter and not stem.startswith(brand_filter):
            continue
        if lane_filter:
            found_lane = any(stem.endswith(f"_{kl}") for kl in [lane_filter])
            if not found_lane:
                continue
        paths.append(path)
    return paths


def project_revenue(year: int, brand_filter: str | None = None, lane_filter: str | None = None) -> dict:
    """Aggregate revenue projections across all brand/lane plans."""
    targets = load_targets()
    global_defaults = targets.get("global_defaults", {})
    blended_asp = float(global_defaults.get("blended_asp", 6.25))
    conversion_rate = float(global_defaults.get("conversion_rate", 0.025))

    # Per-lane ASP overrides possible in future
    lane_targets = targets.get("lanes", {})

    proj_paths = find_all_projections(year, brand_filter, lane_filter)
    if not proj_paths:
        raise FileNotFoundError(f"No projection files found in {PROJECTIONS_DIR} for year {year}. Run projection_planner.py first.")

    # Accumulators
    monthly_low = [0.0] * 12
    monthly_mid = [0.0] * 12
    monthly_high = [0.0] * 12
    monthly_titles = [0] * 12

    by_lane: dict[str, dict] = {}
    by_format: dict[str, dict] = {}
    total_titles = 0
    brands_processed = []

    for path in proj_paths:
        with open(path, "r", encoding="utf-8") as fh:
            proj = json.load(fh)

        brand_id = proj.get("brand_id", "unknown")
        lane = proj.get("lane", "english_global")
        market_mult = MARKET_MULTIPLIERS.get(lane, 0.50)

        # Lane-specific ASP override
        lane_asp = float(lane_targets.get(lane, {}).get("blended_asp", blended_asp))
        lane_conv = float(lane_targets.get(lane, {}).get("conversion_rate", conversion_rate))

        brand_total_mid = 0.0
        brand_total_titles = 0

        for week in proj.get("weeks", []):
            week_num = int(week["week"].split("W")[1])
            month_idx = week_to_month(week_num, year) - 1

            low, mid, high = compute_week_revenue(week, lane_asp, lane_conv, market_mult)
            monthly_low[month_idx] += low
            monthly_mid[month_idx] += mid
            monthly_high[month_idx] += high

            planned = week.get("planned", {})
            week_titles = sum(planned.values())
            monthly_titles[month_idx] += week_titles
            total_titles += week_titles
            brand_total_mid += mid
            brand_total_titles += week_titles

            # Aggregate by format
            for fmt, qty in planned.items():
                if fmt not in by_format:
                    by_format[fmt] = {"count": 0, "revenue_mid": 0.0}
                weight = FORMAT_REVENUE_WEIGHTS.get(fmt, 1.0)
                by_format[fmt]["count"] += qty
                by_format[fmt]["revenue_mid"] += qty * weight * lane_asp * lane_conv * market_mult

        # Aggregate by lane
        if lane not in by_lane:
            by_lane[lane] = {"titles": 0, "revenue_mid": 0.0, "brands": []}
        by_lane[lane]["titles"] += brand_total_titles
        by_lane[lane]["revenue_mid"] += brand_total_mid
        by_lane[lane]["brands"].append(brand_id)
        brands_processed.append(brand_id)

    total_mid = sum(monthly_mid)
    total_low = sum(monthly_low)
    total_high = sum(monthly_high)

    # Compute format revenue percentages
    total_format_rev = sum(v["revenue_mid"] for v in by_format.values()) or 1
    for fmt in by_format:
        by_format[fmt]["revenue_pct"] = round(by_format[fmt]["revenue_mid"] / total_format_rev, 4)

    monthly_breakdown = []
    for i, name in enumerate(MONTH_NAMES):
        monthly_breakdown.append({
            "month": name,
            "month_num": i + 1,
            "titles_published": monthly_titles[i],
            "revenue_low": round(monthly_low[i], 2),
            "revenue_mid": round(monthly_mid[i], 2),
            "revenue_high": round(monthly_high[i], 2),
        })

    forecast = {
        "schema_version": 1,
        "year": year,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provenance": "PROJECTION — based on planned catalog + blended ASP + assumed conversion rate. Not REPO-BACKED revenue.",
        "brands_included": len(set(brands_processed)),
        "total_titles_projected": total_titles,
        "total_projected_revenue_low": round(total_low, 2),
        "total_projected_revenue_mid": round(total_mid, 2),
        "total_projected_revenue_high": round(total_high, 2),
        "blended_asp": blended_asp,
        "baseline_conversion_rate": conversion_rate,
        "monthly": monthly_breakdown,
        "by_lane": {
            lane: {
                "titles": data["titles"],
                "revenue_mid": round(data["revenue_mid"], 2),
                "brands_count": len(set(data["brands"])),
                "market_multiplier": MARKET_MULTIPLIERS.get(lane, 0.5),
            }
            for lane, data in sorted(by_lane.items(), key=lambda x: -x[1]["revenue_mid"])
        },
        "by_format": {
            fmt: {
                "count": data["count"],
                "revenue_pct": data["revenue_pct"],
                "revenue_weight": FORMAT_REVENUE_WEIGHTS.get(fmt, 1.0),
            }
            for fmt, data in sorted(by_format.items(), key=lambda x: -x[1]["revenue_mid"])
        },
    }

    return forecast


def format_md(forecast: dict) -> str:
    """Render forecast as markdown."""
    lines = [
        f"# Revenue Forecast {forecast['year']}",
        "",
        f"> **{forecast['provenance']}**",
        "",
        f"Generated: {forecast['generated_at']}  ",
        f"Brands included: {forecast['brands_included']}  ",
        f"Total titles projected: {forecast['total_titles_projected']:,}  ",
        f"Blended ASP: ${forecast['blended_asp']:.2f} | Conversion rate: {forecast['baseline_conversion_rate']:.1%}",
        "",
        "## Annual Revenue Summary",
        "",
        f"| Scenario | Revenue |",
        f"|----------|---------|",
        f"| **Low** (conservative) | ${forecast['total_projected_revenue_low']:,.0f} |",
        f"| **Mid** (expected) | ${forecast['total_projected_revenue_mid']:,.0f} |",
        f"| **High** (optimistic) | ${forecast['total_projected_revenue_high']:,.0f} |",
        "",
        "## Monthly Breakdown",
        "",
        "| Month | Titles | Low | Mid | High |",
        "|-------|--------|-----|-----|------|",
    ]
    for m in forecast["monthly"]:
        lines.append(
            f"| {m['month']} | {m['titles_published']:,} | ${m['revenue_low']:,.0f} | ${m['revenue_mid']:,.0f} | ${m['revenue_high']:,.0f} |"
        )

    lines += [
        "",
        "## Revenue by Lane (Market)",
        "",
        "| Lane | Brands | Titles | Revenue (Mid) | Market Mult |",
        "|------|--------|--------|---------------|-------------|",
    ]
    for lane, data in forecast["by_lane"].items():
        lines.append(
            f"| {lane} | {data['brands_count']} | {data['titles']:,} | ${data['revenue_mid']:,.0f} | {data['market_multiplier']:.2f}× |"
        )

    lines += [
        "",
        "## Revenue by Format",
        "",
        "| Format | Titles | Revenue Share | Revenue Weight |",
        "|--------|--------|---------------|----------------|",
    ]
    for fmt, data in forecast["by_format"].items():
        lines.append(
            f"| {fmt} | {data['count']:,} | {data['revenue_pct']:.1%} | {data['revenue_weight']:.2f}× |"
        )

    lines += [
        "",
        "---",
        "*PROJECTION — not audited revenue. Based on: planned catalog titles × blended ASP × assumed conversion rate × market multiplier.*",
        "*Actual revenue will vary based on platform distribution, marketing spend, and organic discovery.*",
    ]

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Phoenix Omega Revenue Projector — plan → monthly/quarterly forecast")
    parser.add_argument("--year", type=int, default=2026, help="Projection year")
    parser.add_argument("--format", choices=["json", "md", "both"], default="both", help="Output format")
    parser.add_argument("--brand", help="Limit to this brand_id")
    parser.add_argument("--lane", help="Limit to this lane")
    args = parser.parse_args()

    print(f"Generating revenue forecast for {args.year}...")
    forecast = project_revenue(args.year, args.brand, args.lane)

    PROJECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = PROJECTIONS_DIR / f"revenue_forecast_{args.year}.json"
    md_path = PROJECTIONS_DIR / f"revenue_forecast_{args.year}.md"

    if args.format in ("json", "both"):
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(forecast, fh, indent=2)
        print(f"  Wrote {json_path.relative_to(REPO_ROOT)}")

    if args.format in ("md", "both"):
        md_content = format_md(forecast)
        with open(md_path, "w", encoding="utf-8") as fh:
            fh.write(md_content)
        print(f"  Wrote {md_path.relative_to(REPO_ROOT)}")

    # Print summary
    print(f"\n{'='*50}")
    print(f"Revenue Forecast {args.year}")
    print(f"{'='*50}")
    print(f"Brands: {forecast['brands_included']}  |  Titles: {forecast['total_titles_projected']:,}")
    print(f"Low:   ${forecast['total_projected_revenue_low']:>10,.0f}")
    print(f"Mid:   ${forecast['total_projected_revenue_mid']:>10,.0f}")
    print(f"High:  ${forecast['total_projected_revenue_high']:>10,.0f}")


if __name__ == "__main__":
    main()
