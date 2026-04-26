#!/usr/bin/env python3
"""
Phase 2X.4 atomic regeneration.

Per specs/MANGA_CATALOG_RECONCILIATION_SPEC.md §6.1.A + D-20:
  - Schema flip already applied (series_plan_schema 2.1.0 with 23-entry
    genre enum, demographic + locale_origin + distribution_status fields,
    nullable teacher_id).
  - This script generates the new ~1,410 slug-only series_plan YAMLs.
  - Title is "TBD" per operator path-d directive (titles authored separately).
  - One existing series is preserved verbatim: stillness_press × en_US ×
    iyashikei × anxiety = "the_alarm_is_lying" (production-active ep_001).

Run: PYTHONPATH=. python3 scripts/manga/run_2x4_atomic_regen.py

Steps performed:
  1. Read strategic plans + apply revenue-weighted distribution
  2. Load format_routing.yaml for per-locale-genre format defaults
  3. For each (brand, locale, genre) cell with count > 0, emit count YAMLs
  4. Preserve 1 known production series: the_alarm_is_lying
  5. Write all YAMLs to config/source_of_truth/manga_series_plans/{locale}/

This script does NOT delete stale YAMLs — that happens via `git rm` in the
PR commit. This script also does NOT regenerate book_plans (those are
derivative; will land in a follow-up 2X.4b PR per spec §7.7).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
CATALOG_GEN = REPO / "scripts" / "manga" / "generate_catalog_plan_from_strategic.py"
ROUTING_PATH = REPO / "config" / "manga" / "format_routing.yaml"
OUTPUT_ROOT = REPO / "config" / "source_of_truth" / "manga_series_plans"

# Per-locale defaults
LOCALE_ORIGIN_DEFAULT = {
    "en_US": "us",
    "ja_JP": "jp",
    "zh_TW": "tw",
    "zh_CN": "cn",
    "ko_KR": "kr",
}

DISTRIBUTION_STATUS = {
    "en_US": "distributed",
    "ja_JP": "distributed",
    "zh_TW": "distributed",
    "zh_CN": "gray_zone_disclosed",       # per spec D-19
    "ko_KR": "hold_pending_market_clearance",  # per spec D-18
}

# Demographic default = general (caller picks specific demographic when
# authoring titles in 2X.4b)
DEMOGRAPHIC_DEFAULT = "general"

# Brands with strong teacher anchor → preserved teacher_id; rest → null
BRAND_TEACHER_MAP = {
    "stillness_press": "ahjan",
    "cognitive_clarity": None,    # 13-year-old AI cog psychology brand; no specific teacher
    "digital_ground": "miki",
    "qi_foundation_cultivation": "master_feung",
    "warrior_calm_cultivation": "master_wu",
    "spiritual_ground_supernatural": "ra",
    "devotion_path_shonen": "ra",
    "stoic_edge_battle": None,
    "legacy_builder_memoir": None,
    "bio_flow_healing": None,
    "longevity_lab_healing": None,
    # Default for unmapped brands → null
}

# Preservation overrides — keep these existing series_id slugs verbatim
# instead of using auto-numbered slugs. Maps (brand, locale, genre) →
# {explicit_series_slug: full_existing_series_id_to_preserve_or_path}
# Each cell can preserve at most as many series as count for that cell.
PRESERVE_BRAND_LOCALE_GENRE = {
    # (brand, locale, genre): list of series_id suffixes to use
    ("stillness_press", "en_US", "iyashikei"): ["the_alarm_is_lying"],
}


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("catalog_gen", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["catalog_gen"] = mod
    spec.loader.exec_module(mod)
    return mod


def load_routing() -> dict[str, Any]:
    with open(ROUTING_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def emit_series_plan_yaml(
    brand_id: str,
    teacher_id: str | None,
    locale: str,
    genre: str,
    series_slug: str,
    routing: dict[str, Any],
) -> dict[str, Any]:
    """Build the series_plan dict for one cell."""
    series_id = f"{brand_id}__{locale}__{genre}__{series_slug}"

    # Look up format for this (locale, genre)
    locale_routing = routing["defaults_by_locale_genre"].get(locale, {})
    cell_routing = locale_routing.get(genre, {"master": "color_vertical_webtoon", "flatten": []})
    master_format = cell_routing.get("master", "color_vertical_webtoon")
    flatten = cell_routing.get("flatten", [])

    # Look up target_platforms
    platforms_by_format = routing.get("target_platforms_by_locale_format", {}).get(locale, {})
    target_platforms = platforms_by_format.get(master_format, [])

    # Look up connector_lane
    conn_by_format = routing.get("connector_lane_by_locale_format", {}).get(locale, {})
    connector_lane = conn_by_format.get(master_format, "print_only")

    # Look up panel_layout_template
    panel_template = routing.get("panel_layout_template_by_format", {}).get(
        master_format,
        "config/manga/panel_layout_templates/vertical_scroll_webtoon.yaml",
    )

    pending_partners = routing.get("pending_partner_targets_by_locale", {}).get(locale, [])

    plan = {
        "series_plan_schema": "2.1.0",
        "series_id": series_id,
        "brand_id": brand_id,
        "teacher_id": teacher_id,
        "locale": locale,
        "default_locale": locale,
        "format": master_format,
        "master_format": master_format,
        "flatten_exports": flatten,
        "connector_lane": connector_lane,
        "panel_layout_template": panel_template,
        "target_platforms": target_platforms,
        "pending_partner_targets": pending_partners,
        "title": "TBD",  # Per operator path-d directive; authored separately in 2X.4b
        "localized_titles": {locale: "TBD"},
        "genre": genre,
        "demographic": DEMOGRAPHIC_DEFAULT,
        "locale_origin": LOCALE_ORIGIN_DEFAULT[locale],
        "distribution_status": DISTRIBUTION_STATUS[locale],
        "topic": "TBD",
        "manga_author": "TBD",
        "chapters_target": 14,
        "ai_disclosure_required": True,
    }
    return plan


def main() -> int:
    # Load the catalog generator + compute brand allocations
    catalog_mod = load_module(CATALOG_GEN)
    portfolio_text = (REPO / "docs" / "GENRE_PORTFOLIO_PLAN.md").read_text(encoding="utf-8")
    cjk_text = (REPO / "docs" / "CJK_CATALOG_PLAN.md").read_text(encoding="utf-8")

    brands = catalog_mod.parse_genre_portfolio(portfolio_text)
    locales = catalog_mod.parse_locale_formats(cjk_text)

    if not brands:
        print("error: parsed 0 brands", file=sys.stderr)
        return 2

    # Apply brand-metadata-weighted distribution (same as preview)
    for brand in brands:
        affinity = catalog_mod.compute_metadata_affinity(brand.description, brand.brand_id)
        brand.spread_counts = catalog_mod.distribute_with_spread(
            target_series=brand.target_series,
            strategic_alloc=brand.genre_pct,
            metadata_affinity=affinity,
            tier=brand.tier,
        )

    routing = load_routing()

    total_emitted = 0
    by_locale_count: dict[str, int] = {lc: 0 for lc in catalog_mod.VALID_LOCALES}

    for brand in brands:
        teacher_id = BRAND_TEACHER_MAP.get(brand.brand_id)
        for locale in catalog_mod.VALID_LOCALES:
            for genre in catalog_mod.VALID_GENRES:
                count = brand.spread_counts.get(genre, 0)
                if count <= 0:
                    continue
                preserve = PRESERVE_BRAND_LOCALE_GENRE.get((brand.brand_id, locale, genre), [])
                for i in range(count):
                    if i < len(preserve):
                        series_slug = preserve[i]
                    else:
                        series_slug = f"series{i+1:02d}"

                    plan = emit_series_plan_yaml(
                        brand_id=brand.brand_id,
                        teacher_id=teacher_id,
                        locale=locale,
                        genre=genre,
                        series_slug=series_slug,
                        routing=routing,
                    )

                    # Special: preserve the_alarm_is_lying's actual title
                    if series_slug == "the_alarm_is_lying":
                        plan["title"] = "The Alarm Is Lying"
                        plan["localized_titles"] = {locale: "The Alarm Is Lying"}
                        plan["topic"] = "anxiety"
                        plan["manga_author"] = "Hana Tidecalm"
                        plan["style"] = "cozy_iyashikei"

                    # Validate against schema in dry-run mode
                    # (full validation happens in pytest, not in regen script)

                    out_dir = OUTPUT_ROOT / locale
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_path = out_dir / f"{plan['series_id']}.yaml"

                    header = (
                        "# Auto-generated by scripts/manga/run_2x4_atomic_regen.py — do not hand-edit.\n"
                        "# Source: docs/GENRE_PORTFOLIO_PLAN.md + docs/CJK_CATALOG_PLAN.md + docs/US_CATALOG_PLAN.md\n"
                        "# Routing: config/manga/format_routing.yaml\n"
                        "# Schema: schemas/manga/series_plan.schema.json (v2.1.0)\n"
                        "# Per: specs/MANGA_CATALOG_RECONCILIATION_SPEC.md Phase 2X.4 atomic\n"
                        "\n"
                    )
                    body = yaml.safe_dump(plan, sort_keys=False, allow_unicode=True, width=120)
                    out_path.write_text(header + body, encoding="utf-8")

                    total_emitted += 1
                    by_locale_count[locale] += 1

    print(f"\n2X.4 atomic regen complete:")
    print(f"  Total series_plan YAMLs emitted: {total_emitted}")
    for locale, n in by_locale_count.items():
        print(f"    {locale}: {n}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
