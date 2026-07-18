#!/usr/bin/env python3
"""
Phase 2X.4 atomic regeneration — spec-compliant per-brand × per-genre %.

Per specs/MANGA_CATALOG_RECONCILIATION_SPEC.md §6.1.A + D-20 AND the
operator-approved 2026-04-27 spec-compliance correction (Path A regen):
  - Schema 2.1.0 (23-entry genre enum, demographic + locale_origin +
    distribution_status, nullable teacher_id) — same as before.
  - **Distribution is now STRICT against GENRE_PORTFOLIO_PLAN.md.** Each
    brand's per-genre allocation is exactly the spec's % table — no
    uniform-1-per-genre fallback, no metadata bleed-through, no market-
    revenue tilt. Genres with 0% in a brand's spec table get NO series.
  - Result: total catalog ~272 series per locale (vs previous 282 per
    locale that smeared across all 15 genres uniformly).
  - One existing production series is preserved verbatim: stillness_press ×
    en_US × iyashikei × anxiety = "the_alarm_is_lying" (ep_001 rendered).

Run:
    # Smoke test — 3 flagship brands → /tmp/catalog_regen_smoke/
    PYTHONPATH=. python3 scripts/manga/run_2x4_atomic_regen.py \\
        --out-root /tmp/catalog_regen_smoke \\
        --brand stillness_press --brand cognitive_clarity --brand digital_ground

    # Full regen → /tmp staging dir
    PYTHONPATH=. python3 scripts/manga/run_2x4_atomic_regen.py \\
        --out-root /tmp/catalog_regen_full

    # Production regen to repo path (default)
    PYTHONPATH=. python3 scripts/manga/run_2x4_atomic_regen.py

Steps performed:
  1. Parse GENRE_PORTFOLIO_PLAN.md → 37 brand × per-genre %-tables
  2. Validate every canonical brand has %-table with 95-105% sum + ≥3 genres
     (STOP if any brand fails — surfaces brand IDs needing spec authoring)
  3. For each brand, distribute target_series across spec-listed genres via
     largest-remainder method (counts sum to target_series exactly)
  4. Load format_routing.yaml for per-locale-genre format defaults
  5. For each (brand, locale, genre) cell with count > 0, emit count YAMLs
  6. Preserve known production series: the_alarm_is_lying
  7. Write all YAMLs to <out-root>/{locale}/

This script does NOT delete stale YAMLs — that happens via `git rm` in the
PR commit. This script also does NOT regenerate book_plans (those are
derivative; landed by generate_book_plans_from_series.py per spec §7.7).
"""
from __future__ import annotations

import argparse
import importlib.util
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


def load_canonical_brand_ids() -> list[str]:
    """Read 37-brand canonical list. Used for spec-compliance validation."""
    path = REPO / "config" / "manga" / "canonical_brand_list.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(data.get("brands", {}).keys())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument(
        "--out-root",
        type=Path,
        default=OUTPUT_ROOT,
        help=(
            f"Root directory for emitted series_plan YAMLs (default: "
            f"{OUTPUT_ROOT.relative_to(REPO)}). Use /tmp/... for smoke or "
            f"staging runs."
        ),
    )
    parser.add_argument(
        "--brand",
        action="append",
        dest="brands_filter",
        default=None,
        help="Restrict regen to specific brand_id (repeat for multiple). Used for smoke tests.",
    )
    parser.add_argument(
        "--locale",
        action="append",
        dest="locales_filter",
        default=None,
        help="Restrict regen to specific locale (e.g. en_US). Used for smoke tests.",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip the spec-compliance validation (sums 95-105%%, ≥3 genres per brand).",
    )
    args = parser.parse_args(argv)

    out_root: Path = args.out_root

    # Load the catalog generator + compute brand allocations
    catalog_mod = load_module(CATALOG_GEN)
    portfolio_text = (REPO / "docs" / "GENRE_PORTFOLIO_PLAN.md").read_text(encoding="utf-8")

    brands = catalog_mod.parse_genre_portfolio(portfolio_text)

    if not brands:
        print("error: parsed 0 brands", file=sys.stderr)
        return 2

    # ── Spec-compliance validation ─────────────────────────────────────────
    # STOP and surface if any canonical brand lacks %-table or has malformed
    # entries. Operator directive: brands without spec coverage need spec
    # authoring before regen can run.
    if not args.skip_validation:
        canon = load_canonical_brand_ids()
        ok, issues = catalog_mod.validate_brand_allocations(brands, canonical_brand_ids=canon)
        if not ok:
            print("\nERROR: spec-compliance validation FAILED", file=sys.stderr)
            for issue in issues:
                print(f"  {issue}", file=sys.stderr)
            print(
                "\nResolve the above by editing docs/GENRE_PORTFOLIO_PLAN.md "
                "and re-running. Use --skip-validation to bypass (not "
                "recommended for production regen).",
                file=sys.stderr,
            )
            return 3
        print(f"validation OK: {len(brands)} brands, all %-tables 95-105%, ≥3 genres each")

    # ── Apply STRICT per-brand × per-genre %-allocation ───────────────────
    # Each brand gets exactly target_series across the genres listed in its
    # spec table. No uniform fallback. Genres at 0% in spec get 0 series.
    for brand in brands:
        brand.spread_counts = catalog_mod.distribute_strategic_strict(
            target_series=brand.target_series,
            strategic_alloc=brand.genre_pct,
        )

    # Apply filters (used for smoke tests)
    if args.brands_filter:
        brands = [b for b in brands if b.brand_id in args.brands_filter]
        if not brands:
            print(
                f"error: no brands matched filter {args.brands_filter}",
                file=sys.stderr,
            )
            return 2
    locales_to_emit = args.locales_filter or list(catalog_mod.VALID_LOCALES)

    routing = load_routing()

    total_emitted = 0
    by_locale_count: dict[str, int] = {lc: 0 for lc in locales_to_emit}
    by_brand_summary: list[tuple[str, str, int, int]] = []  # (brand, tier, target, total_emitted)

    for brand in brands:
        teacher_id = BRAND_TEACHER_MAP.get(brand.brand_id)
        brand_emitted = 0
        for locale in locales_to_emit:
            for genre, count in brand.spread_counts.items():
                if count <= 0:
                    continue
                # Note: distribute_strategic_strict only includes genres in
                # the spec table; no zero-keys to filter.
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

                    out_dir = out_root / locale
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_path = out_dir / f"{plan['series_id']}.yaml"

                    header = (
                        "# Auto-generated by scripts/manga/run_2x4_atomic_regen.py — do not hand-edit.\n"
                        "# Source: docs/GENRE_PORTFOLIO_PLAN.md (per-brand × per-genre %)\n"
                        "# Routing: config/manga/format_routing.yaml\n"
                        "# Schema: schemas/manga/series_plan.schema.json (v2.1.0)\n"
                        "# Per: specs/MANGA_CATALOG_RECONCILIATION_SPEC.md Phase 2X.4 atomic\n"
                        "# Distribution: distribute_strategic_strict (operator-approved 2026-04-27 Path A)\n"
                        "\n"
                    )
                    body = yaml.safe_dump(plan, sort_keys=False, allow_unicode=True, width=120)
                    out_path.write_text(header + body, encoding="utf-8")

                    total_emitted += 1
                    by_locale_count[locale] += 1
                    brand_emitted += 1
        by_brand_summary.append((brand.brand_id, brand.tier, brand.target_series, brand_emitted))

    print(f"\n2X.4 atomic regen complete (out-root: {out_root}):")
    print(f"  Total series_plan YAMLs emitted: {total_emitted}")
    print(f"  Brands processed: {len(brands)}")
    print(f"  Locales emitted: {len(locales_to_emit)}")
    for locale, n in by_locale_count.items():
        print(f"    {locale}: {n}")
    print()
    print(f"  Per-brand totals (target × locales = total emitted):")
    for bid, tier, target, emitted in by_brand_summary[:20]:
        expected = target * len(locales_to_emit)
        marker = "✓" if emitted == expected else "✗"
        print(f"    {marker} {bid:40s} {tier:9s} target={target:2d}  emitted={emitted:3d} (expected {expected})")
    if len(by_brand_summary) > 20:
        print(f"    ... ({len(by_brand_summary) - 20} more brands)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
