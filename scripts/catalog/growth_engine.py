#!/usr/bin/env python3
"""
Growth Engine — VIABLE → STRONG promotion based on sales signals.

Reads sales data (initially from manual CSV), scores titles, and promotes
VIABLE configs to STRONG when they hit thresholds. Feeds updated priorities
back into the weekly production queue.

Usage:
    # Score titles from sales CSV
    python scripts/catalog/growth_engine.py --sales-csv artifacts/catalog/sales_data.csv

    # Dry run (show promotions without writing)
    python scripts/catalog/growth_engine.py --sales-csv artifacts/catalog/sales_data.csv --dry-run

    # Show current tier distribution
    python scripts/catalog/growth_engine.py --status

    # Export updated priority tiers
    python scripts/catalog/growth_engine.py --sales-csv artifacts/catalog/sales_data.csv \
        --output artifacts/catalog/priority_tiers.json
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger("growth_engine")

try:
    import yaml
except ImportError:
    yaml = None


def _load_yaml(path: Path) -> Any:
    if yaml is not None:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    raise ImportError(f"PyYAML required to load {path.name}")


# ─── CONFIGURATION ─────────────────────────────────────────────────────────

DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "catalog" / "growth_engine_config.yaml"
DEFAULT_TIERS_PATH = REPO_ROOT / "artifacts" / "catalog" / "priority_tiers.json"
DEFAULT_HISTORY_PATH = REPO_ROOT / "artifacts" / "catalog" / "production_history.jsonl"


@dataclass
class GrowthConfig:
    """Growth engine thresholds and weights."""
    # Promotion thresholds (VIABLE → STRONG)
    promotion_units_per_month: int = 50
    promotion_revenue_per_month: float = 100.0
    promotion_min_reviews: int = 3
    promotion_min_rating: float = 3.5

    # Demotion settings
    demotion_grace_period_weeks: int = 12
    demotion_min_sales: int = 1  # min sales in grace period to keep VIABLE

    # Scoring weights (sum to 1.0)
    weight_units: float = 0.30
    weight_revenue: float = 0.25
    weight_reviews: float = 0.15
    weight_rating: float = 0.10
    weight_read_through: float = 0.10
    weight_rank: float = 0.10

    # Market adjustments (multiply thresholds for non-US markets)
    market_multipliers: dict[str, float] = field(default_factory=lambda: {
        "en_US": 1.0,
        "ja_JP": 0.7,
        "ko_KR": 0.5,
        "de_DE": 0.6,
        "fr_FR": 0.5,
        "es_US": 0.4,
        "es_ES": 0.4,
        "zh_TW": 0.35,
        "zh_CN": 0.25,
        "zh_HK": 0.3,
        "zh_SG": 0.3,
        "it_IT": 0.35,
        "hu_HU": 0.2,
    })

    @classmethod
    def from_yaml(cls, path: Path) -> GrowthConfig:
        if not path.exists():
            logger.warning("Config not found: %s — using defaults", path)
            return cls()
        data = _load_yaml(path)
        return cls(
            promotion_units_per_month=data.get("promotion_units_per_month", cls.promotion_units_per_month),
            promotion_revenue_per_month=data.get("promotion_revenue_per_month", cls.promotion_revenue_per_month),
            promotion_min_reviews=data.get("promotion_min_reviews", cls.promotion_min_reviews),
            promotion_min_rating=data.get("promotion_min_rating", cls.promotion_min_rating),
            demotion_grace_period_weeks=data.get("demotion_grace_period_weeks", cls.demotion_grace_period_weeks),
            demotion_min_sales=data.get("demotion_min_sales", cls.demotion_min_sales),
            weight_units=data.get("weight_units", cls.weight_units),
            weight_revenue=data.get("weight_revenue", cls.weight_revenue),
            weight_reviews=data.get("weight_reviews", cls.weight_reviews),
            weight_rating=data.get("weight_rating", cls.weight_rating),
            weight_read_through=data.get("weight_read_through", cls.weight_read_through),
            weight_rank=data.get("weight_rank", cls.weight_rank),
            market_multipliers=data.get("market_multipliers", cls().market_multipliers),
        )


# ─── SALES DATA ────────────────────────────────────────────────────────────

@dataclass
class TitleSales:
    """Sales data for a single title configuration."""
    config_key: str  # topic_persona_engine_format
    brand: str
    lane: str
    topic: str
    persona: str
    engine: str
    book_format: str
    units_sold: int = 0
    revenue: float = 0.0
    reviews: int = 0
    avg_rating: float = 0.0
    read_through_rate: float = 0.0  # series completion rate (0-1)
    kdp_rank: int = 0  # lower is better
    first_published: str = ""
    weeks_live: int = 0
    current_tier: str = "VIABLE"


def load_sales_csv(path: Path) -> list[TitleSales]:
    """Load sales data from CSV."""
    if not path.exists():
        raise FileNotFoundError(f"Sales CSV not found: {path}")

    titles: list[TitleSales] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            titles.append(TitleSales(
                config_key=row.get("config_key", f"{row.get('topic', '')}_{row.get('persona', '')}_{row.get('engine', '')}_{row.get('format', '')}"),
                brand=row.get("brand", ""),
                lane=row.get("lane", "en_US"),
                topic=row.get("topic", ""),
                persona=row.get("persona", ""),
                engine=row.get("engine", ""),
                book_format=row.get("format", "standard"),
                units_sold=int(row.get("units_sold", 0)),
                revenue=float(row.get("revenue", 0.0)),
                reviews=int(row.get("reviews", 0)),
                avg_rating=float(row.get("avg_rating", 0.0)),
                read_through_rate=float(row.get("read_through_rate", 0.0)),
                kdp_rank=int(row.get("kdp_rank", 0)),
                first_published=row.get("first_published", ""),
                weeks_live=int(row.get("weeks_live", 0)),
                current_tier=row.get("current_tier", "VIABLE"),
            ))

    return titles


# ─── SCORING ───────────────────────────────────────────────────────────────

def score_title(title: TitleSales, config: GrowthConfig) -> float:
    """
    Score a title from 0-100 based on weighted performance metrics.
    Higher = better performing.
    """
    market_mult = config.market_multipliers.get(title.lane, 0.5)

    # Normalize each signal to 0-1 range
    # Units: compare against market-adjusted threshold
    units_target = config.promotion_units_per_month * market_mult
    units_score = min(1.0, title.units_sold / max(units_target, 1))

    # Revenue: compare against market-adjusted threshold
    rev_target = config.promotion_revenue_per_month * market_mult
    rev_score = min(1.0, title.revenue / max(rev_target, 1))

    # Reviews: 0-1 based on min reviews threshold
    review_score = min(1.0, title.reviews / max(config.promotion_min_reviews, 1))

    # Rating: 0-1 where 5.0 = perfect
    rating_score = min(1.0, title.avg_rating / 5.0) if title.avg_rating > 0 else 0

    # Read-through: already 0-1
    rt_score = title.read_through_rate

    # Rank: inverse — lower rank is better. Top 100k = 1.0, above 1M = 0
    if title.kdp_rank > 0:
        rank_score = max(0, min(1.0, 1.0 - (title.kdp_rank / 1_000_000)))
    else:
        rank_score = 0

    weighted = (
        config.weight_units * units_score
        + config.weight_revenue * rev_score
        + config.weight_reviews * review_score
        + config.weight_rating * rating_score
        + config.weight_read_through * rt_score
        + config.weight_rank * rank_score
    )

    return round(weighted * 100, 1)


# ─── ENGINE ────────────────────────────────────────────────────────────────

@dataclass
class PromotionResult:
    promoted: list[str] = field(default_factory=list)  # VIABLE → STRONG
    demoted: list[str] = field(default_factory=list)   # VIABLE → DEPRIORITIZED
    unchanged: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    tier_map: dict[str, str] = field(default_factory=dict)


def run_growth_engine(
    titles: list[TitleSales],
    config: GrowthConfig,
) -> PromotionResult:
    """
    Score all titles and determine promotions/demotions.
    """
    result = PromotionResult()

    for title in titles:
        score = score_title(title, config)
        result.scores[title.config_key] = score

        market_mult = config.market_multipliers.get(title.lane, 0.5)
        promo_units = config.promotion_units_per_month * market_mult
        promo_rev = config.promotion_revenue_per_month * market_mult

        if title.current_tier == "VIABLE":
            # Check for promotion
            if (
                title.units_sold >= promo_units
                and title.revenue >= promo_rev
                and title.reviews >= config.promotion_min_reviews
            ):
                result.promoted.append(title.config_key)
                result.tier_map[title.config_key] = "STRONG"
                logger.info(
                    "PROMOTE %s: %d units, $%.2f rev, %d reviews (score=%.1f)",
                    title.config_key, title.units_sold, title.revenue,
                    title.reviews, score,
                )

            # Check for demotion
            elif (
                title.weeks_live >= config.demotion_grace_period_weeks
                and title.units_sold < config.demotion_min_sales
            ):
                result.demoted.append(title.config_key)
                result.tier_map[title.config_key] = "DEPRIORITIZED"
                logger.info(
                    "DEMOTE %s: %d units in %d weeks (score=%.1f)",
                    title.config_key, title.units_sold, title.weeks_live, score,
                )
            else:
                result.unchanged.append(title.config_key)
                result.tier_map[title.config_key] = "VIABLE"

        elif title.current_tier == "STRONG":
            # STRONG stays STRONG unless manually killed
            result.unchanged.append(title.config_key)
            result.tier_map[title.config_key] = "STRONG"

        else:
            result.unchanged.append(title.config_key)
            result.tier_map[title.config_key] = title.current_tier

    return result


# ─── OUTPUT ────────────────────────────────────────────────────────────────

def write_priority_tiers(result: PromotionResult, output_path: Path) -> None:
    """Write updated priority tiers to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "promoted": len(result.promoted),
            "demoted": len(result.demoted),
            "unchanged": len(result.unchanged),
            "total": len(result.tier_map),
        },
        "promotions": result.promoted,
        "demotions": result.demoted,
        "scores": result.scores,
        "tiers": result.tier_map,
    }

    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info("Priority tiers written to %s", output_path)


def write_sales_template(output_path: Path) -> None:
    """Write a blank sales data CSV template."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    headers = [
        "config_key", "brand", "lane", "topic", "persona", "engine", "format",
        "units_sold", "revenue", "reviews", "avg_rating", "read_through_rate",
        "kdp_rank", "first_published", "weeks_live", "current_tier",
    ]

    # Write header + 3 example rows
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow([
            "anxiety_corporate_managers_spiral_standard",
            "stabilizer_en_us", "en_US", "anxiety", "corporate_managers",
            "spiral", "standard", "67", "264.33", "5", "4.2", "0.45",
            "285000", "2026-01-15", "12", "VIABLE",
        ])
        writer.writerow([
            "burnout_tech_finance_burnout_overwhelm_micro",
            "stabilizer_en_us", "en_US", "burnout", "tech_finance_burnout",
            "overwhelm", "micro_book_15", "23", "22.77", "1", "3.8", "0",
            "890000", "2026-03-01", "5", "VIABLE",
        ])
        writer.writerow([
            "self_worth_millennial_women_professionals_shame_standard",
            "phoenix_mind_en_us", "en_US", "self_worth", "millennial_women_professionals",
            "shame", "standard", "142", "565.58", "12", "4.6", "0.62",
            "95000", "2025-11-01", "22", "STRONG",
        ])

    logger.info("Sales data template written to %s", output_path)


# ─── CLI ──────────────────────────────────────────────────────────────────

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    parser = argparse.ArgumentParser(description="Phoenix Omega Growth Engine")
    parser.add_argument("--sales-csv", type=Path, help="Path to sales data CSV")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_TIERS_PATH)
    parser.add_argument("--dry-run", action="store_true", help="Show promotions without writing")
    parser.add_argument("--status", action="store_true", help="Show current tier distribution")
    parser.add_argument(
        "--create-template", action="store_true",
        help="Create a blank sales data CSV template",
    )
    parser.add_argument(
        "--create-config", action="store_true",
        help="Create default growth engine config YAML",
    )

    args = parser.parse_args()

    config = GrowthConfig.from_yaml(args.config)

    if args.create_template:
        template_path = REPO_ROOT / "artifacts" / "catalog" / "sales_data_template.csv"
        write_sales_template(template_path)
        print(f"Template created: {template_path}")
        return

    if args.create_config:
        write_default_config(args.config, config)
        return

    if args.status:
        if args.output.exists():
            data = json.loads(args.output.read_text())
            print("=== CURRENT PRIORITY TIERS ===")
            print(json.dumps(data.get("summary", {}), indent=2))
            tiers = data.get("tiers", {})
            by_tier: dict[str, int] = {}
            for _, tier in tiers.items():
                by_tier[tier] = by_tier.get(tier, 0) + 1
            for tier, count in sorted(by_tier.items()):
                print(f"  {tier}: {count}")
        else:
            print("No priority tiers file found. Run with --sales-csv first.")
        return

    if not args.sales_csv:
        parser.error("--sales-csv is required (or use --create-template to get started)")

    titles = load_sales_csv(args.sales_csv)
    logger.info("Loaded %d titles from %s", len(titles), args.sales_csv)

    result = run_growth_engine(titles, config)

    print("\n=== GROWTH ENGINE RESULTS ===")
    print(f"Promoted (VIABLE → STRONG): {len(result.promoted)}")
    for key in result.promoted:
        print(f"  + {key} (score={result.scores.get(key, 0):.1f})")

    print(f"\nDemoted (VIABLE → DEPRIORITIZED): {len(result.demoted)}")
    for key in result.demoted:
        print(f"  - {key} (score={result.scores.get(key, 0):.1f})")

    print(f"\nUnchanged: {len(result.unchanged)}")

    if not args.dry_run:
        write_priority_tiers(result, args.output)
        print(f"\nTiers written to: {args.output}")
    else:
        print("\n(dry run — no files written)")


def write_default_config(path: Path, config: GrowthConfig) -> None:
    """Write default growth engine config as YAML."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Growth Engine Configuration",
        "# Authority: Pearl_PM + EI v2",
        "",
        "# ── Promotion Thresholds (VIABLE → STRONG) ──────────────────────",
        f"promotion_units_per_month: {config.promotion_units_per_month}",
        f"promotion_revenue_per_month: {config.promotion_revenue_per_month}",
        f"promotion_min_reviews: {config.promotion_min_reviews}",
        f"promotion_min_rating: {config.promotion_min_rating}",
        "",
        "# ── Demotion Settings ────────────────────────────────────────────",
        f"demotion_grace_period_weeks: {config.demotion_grace_period_weeks}",
        f"demotion_min_sales: {config.demotion_min_sales}",
        "",
        "# ── Scoring Weights (sum to 1.0) ────────────────────────────────",
        f"weight_units: {config.weight_units}",
        f"weight_revenue: {config.weight_revenue}",
        f"weight_reviews: {config.weight_reviews}",
        f"weight_rating: {config.weight_rating}",
        f"weight_read_through: {config.weight_read_through}",
        f"weight_rank: {config.weight_rank}",
        "",
        "# ── Market Adjustments (multiply thresholds for non-US markets) ──",
        "market_multipliers:",
    ]
    for market, mult in sorted(config.market_multipliers.items()):
        lines.append(f"  {market}: {mult}")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Default config written to %s", path)
    print(f"Config written: {path}")


if __name__ == "__main__":
    main()
