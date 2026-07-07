#!/usr/bin/env python3
"""
M7 Wave A — allocation-derived manga series_plan emission for one locale.

Per docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md §7:
  Wave A (plans) runs the 2X.4 vehicle with M2 allocations for zero-plan locales.
  fr_FR is first; ≤180-file PRs per locale (split batches if count exceeds cap).

Unlike run_2x4_atomic_regen.py (global brand %-table only), this script blends
per-locale genre shares from config/manga/locale_genre_allocations.yaml with
each brand's strategic mix (70% locale × 30% brand) via locale_series_counts().

Requires format_routing.yaml entries for the target locale (see fr_FR template).

Usage:
    # Dry-run — counts only, no files written
    PYTHONPATH=. python3 scripts/manga/run_m7_wave_a.py --locale fr_FR --dry-run

    # Proof emit to artifacts (not production path)
    PYTHONPATH=. python3 scripts/manga/run_m7_wave_a.py --locale fr_FR \\
        --out-root artifacts/qa/manga_m7_wave_a_fr_FR_proof/series_plans

    # Production emit (operator PR — one locale per merge)
    PYTHONPATH=. python3 scripts/manga/run_m7_wave_a.py --locale fr_FR
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
ALLOCATIONS_PATH = REPO / "config" / "manga" / "locale_genre_allocations.yaml"
ROUTING_PATH = REPO / "config" / "manga" / "format_routing.yaml"
CANONICAL_BRANDS_PATH = REPO / "config" / "manga" / "canonical_brand_list.yaml"
OUTPUT_ROOT = REPO / "config" / "source_of_truth" / "manga_series_plans"
SCHEMA_PATH = REPO / "schemas" / "manga" / "series_plan.schema.json"

# Wave A zero-plan locales (5 existing + 9 zero = 14 registry; ko_KR has plans on hold).
WAVE_A_ZERO_PLAN_LOCALES = (
    "fr_FR", "de_DE", "es_ES", "es_US", "it_IT", "hu_HU", "zh_SG", "zh_HK", "pt_BR",
)

LOCALE_ORIGIN: dict[str, str] = {
    "en_US": "us", "ja_JP": "jp", "zh_TW": "tw", "zh_CN": "cn", "ko_KR": "kr",
    "es_US": "us", "es_ES": "es", "fr_FR": "fr", "de_DE": "de", "it_IT": "it",
    "hu_HU": "hu", "zh_SG": "sg", "zh_HK": "hk", "pt_BR": "br",
}

DISTRIBUTION_STATUS: dict[str, str] = {
    "en_US": "distributed",
    "ja_JP": "distributed",
    "zh_TW": "distributed",
    "zh_CN": "gray_zone_disclosed",
    "ko_KR": "hold_pending_market_clearance",
    "es_US": "distributed",
    "es_ES": "distributed",
    "fr_FR": "distributed",
    "de_DE": "distributed",
    "it_IT": "distributed",
    "hu_HU": "distributed",
    "zh_SG": "distributed",
    "zh_HK": "distributed",
    "pt_BR": "distributed",
}

BRAND_TEACHER_MAP: dict[str, str | None] = {
    "stillness_press": "ahjan",
    "digital_ground": "miki",
    "qi_foundation_cultivation": "master_feung",
    "warrior_calm_cultivation": "master_wu",
    "spiritual_ground_supernatural": "ra",
    "devotion_path_shonen": "ra",
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


def load_brand_manga_locales() -> dict[str, list[str] | None]:
    data = yaml.safe_load(CANONICAL_BRANDS_PATH.read_text(encoding="utf-8")) or {}
    out: dict[str, list[str] | None] = {}
    for brand_id, block in (data.get("brands") or {}).items():
        if isinstance(block, dict):
            out[str(brand_id)] = block.get("manga_locales")
    return out


def load_schema() -> dict[str, Any]:
    import json
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_plan(plan: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return []
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'.'.join(str(p) for p in e.path)}: {e.message}" for e in validator.iter_errors(plan)]


def emit_series_plan_yaml(
    *,
    brand_id: str,
    teacher_id: str | None,
    locale: str,
    genre: str,
    series_slug: str,
    routing: dict[str, Any],
) -> dict[str, Any]:
    locale_routing = routing["defaults_by_locale_genre"].get(locale, {})
    cell_routing = locale_routing.get(genre, {"master": "color_vertical_webtoon", "flatten": []})
    master_format = cell_routing.get("master", "color_vertical_webtoon")
    flatten = cell_routing.get("flatten", [])

    platforms_by_format = routing.get("target_platforms_by_locale_format", {}).get(locale, {})
    target_platforms = platforms_by_format.get(master_format, [])

    conn_by_format = routing.get("connector_lane_by_locale_format", {}).get(locale, {})
    connector_lane = conn_by_format.get(master_format, "print_only")

    panel_template = routing.get("panel_layout_template_by_format", {}).get(
        master_format,
        "config/manga/panel_layout_templates/vertical_scroll_webtoon.yaml",
    )

    pending_partners = routing.get("pending_partner_targets_by_locale", {}).get(locale, [])

    series_id = f"{brand_id}__{locale}__{genre}__{series_slug}"
    return {
        "series_plan_schema": "2.4.0",
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
        "title": "TBD",
        "localized_titles": {locale: "TBD"},
        "genre": genre,
        "demographic": "general",
        "locale_origin": LOCALE_ORIGIN.get(locale, locale.split("_")[0]),
        "distribution_status": DISTRIBUTION_STATUS.get(locale, "distributed"),
        "topic": "TBD",
        "manga_author": "TBD",
        "chapters_target": 14,
        "ai_disclosure_required": True,
    }


def write_plan(out_root: Path, plan: dict[str, Any]) -> Path:
    locale_dir = out_root / plan["locale"]
    locale_dir.mkdir(parents=True, exist_ok=True)
    out_path = locale_dir / f"{plan['series_id']}.yaml"
    header = (
        "# Auto-generated by scripts/manga/run_m7_wave_a.py — do not hand-edit.\n"
        f"# M7 Wave A — allocation-derived from {ALLOCATIONS_PATH.name}\n"
        "# Routing: config/manga/format_routing.yaml\n"
        "# Schema: schemas/manga/series_plan.schema.json (v2.0.0)\n\n"
    )
    out_path.write_text(
        header + yaml.safe_dump(plan, sort_keys=False, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument(
        "--locale",
        required=True,
        choices=WAVE_A_ZERO_PLAN_LOCALES,
        help="Target zero-plan locale for Wave A emission.",
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=OUTPUT_ROOT,
        help=f"Output root for series_plan YAMLs (default: {OUTPUT_ROOT.relative_to(REPO)}).",
    )
    parser.add_argument(
        "--allocations",
        type=Path,
        default=ALLOCATIONS_PATH,
        help="Path to locale_genre_allocations.yaml.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print counts only; do not write files.")
    parser.add_argument(
        "--max-files",
        type=int,
        default=0,
        help="Cap emitted files (0 = no cap). Use 180 for catalog scale-up doctrine batches.",
    )
    args = parser.parse_args(argv)

    locale = args.locale
    catalog_mod = load_module(CATALOG_GEN)
    routing = load_routing()

    if locale not in routing.get("defaults_by_locale_genre", {}):
        print(
            f"error: {locale} missing from format_routing.yaml defaults_by_locale_genre. "
            "Add routing before Wave A emit.",
            file=sys.stderr,
        )
        return 4

    alloc_all = catalog_mod.load_locale_allocations(args.allocations)
    locale_shares = alloc_all.get(locale)
    if not locale_shares:
        print(f"error: no allocation block for {locale} in {args.allocations}", file=sys.stderr)
        return 5

    portfolio_text = (REPO / "docs" / "GENRE_PORTFOLIO_PLAN.md").read_text(encoding="utf-8")
    brands = catalog_mod.parse_genre_portfolio(portfolio_text)
    if not brands:
        print("error: parsed 0 brands", file=sys.stderr)
        return 2

    canon_ids = list(yaml.safe_load(CANONICAL_BRANDS_PATH.read_text(encoding="utf-8")).get("brands", {}).keys())
    ok, issues = catalog_mod.validate_brand_allocations(brands, canonical_brand_ids=canon_ids)
    if not ok:
        for issue in issues:
            print(f"  {issue}", file=sys.stderr)
        return 3

    manga_locales = load_brand_manga_locales()
    schema = load_schema()

    total = 0
    skipped_brands: list[str] = []
    failed: list[tuple[str, list[str]]] = []
    genre_totals: dict[str, int] = {}

    for brand in brands:
        allowed = manga_locales.get(brand.brand_id)
        if allowed is not None and locale not in allowed:
            skipped_brands.append(brand.brand_id)
            continue

        counts = catalog_mod.locale_series_counts(brand, locale_shares)
        teacher_id = BRAND_TEACHER_MAP.get(brand.brand_id)

        for genre, count in counts.items():
            if count <= 0:
                continue
            genre_totals[genre] = genre_totals.get(genre, 0) + count
            for i in range(count):
                if args.max_files and total >= args.max_files:
                    break
                series_slug = f"series{i + 1:02d}"
                plan = emit_series_plan_yaml(
                    brand_id=brand.brand_id,
                    teacher_id=teacher_id,
                    locale=locale,
                    genre=genre,
                    series_slug=series_slug,
                    routing=routing,
                )
                errors = validate_plan(plan, schema)
                if errors:
                    failed.append((plan["series_id"], errors))
                    continue
                if args.dry_run:
                    print(f"[dry-run] {plan['series_id']} ({plan['master_format']})")
                else:
                    write_plan(args.out_root, plan)
                total += 1
            if args.max_files and total >= args.max_files:
                break
        if args.max_files and total >= args.max_files:
            break

    print()
    print(f"M7 Wave A — {locale}")
    print(f"  allocation-derived series: {total}")
    print(f"  brands skipped (manga_locales): {len(skipped_brands)}")
    if skipped_brands:
        print(f"    {', '.join(skipped_brands)}")
    top_genres = sorted(genre_totals.items(), key=lambda kv: -kv[1])[:5]
    print(f"  top genres: {', '.join(f'{g}={n}' for g, n in top_genres)}")

    if failed:
        print(f"  schema failures: {len(failed)}", file=sys.stderr)
        for sid, errs in failed[:5]:
            print(f"    {sid}: {errs[0]}", file=sys.stderr)
        return 1

    if not args.dry_run:
        print(f"  wrote to {args.out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
