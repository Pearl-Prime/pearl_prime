#!/usr/bin/env python3
"""
Manga Catalog Builder
======================
Generates a manga-specific catalog CSV from:
  - config/manga/character_brand_registry.yaml  (all 12 brands, characters)
  - config/manga/manga_brand_series_plan.yaml   (series targets, genres)
  - config/catalog/market_catalog_registry.yaml (which markets get manga)
  - config/manga/japan_dual_track_config.yaml   (Japan pipeline)
  - config/manga/korea_webtoon_config.yaml      (Korea webtoon pipeline)

Output: artifacts/catalog/manga_catalog.csv
Each row = one manga series plan (not individual chapters).

Usage:
    python3 scripts/manga/build_manga_catalog.py --all
    python3 scripts/manga/build_manga_catalog.py --market japan
    python3 scripts/manga/build_manga_catalog.py --brand stillness_press
    python3 scripts/manga/build_manga_catalog.py --all --dry-run
    python3 scripts/manga/build_manga_catalog.py --all --output artifacts/catalog/manga_catalog.csv
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_WORKTREE = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
_REPO_ROOT = _MAIN_REPO if _MAIN_REPO.exists() else _WORKTREE
sys.path.insert(0, str(_REPO_ROOT))

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# ---------------------------------------------------------------------------
# Markets that support manga content
# ---------------------------------------------------------------------------
MANGA_MARKETS: dict[str, list[str]] = {
    "us":         ["webtoon_canvas", "google_play", "amazon_kdp"],
    "japan":      ["manga_app_partners", "physical_doujin", "booth_pm", "amazon_jp", "rakuten_kobo"],
    "korea":      ["kakao_page", "naver_webtoon", "ridi"],
    "taiwan":     ["google_play", "apple_books_tw"],
    "china":      ["bilibili_comics", "weread"],
    "hong_kong":  ["google_play", "apple_books_hk"],
    "singapore":  ["google_play", "apple_books"],
    "germany":    ["google_play"],
    "france":     ["google_play"],
}

MANGA_LOCALE_MAP: dict[str, str] = {
    "us": "en_US",
    "japan": "ja_JP",
    "korea": "ko_KR",
    "taiwan": "zh_TW",
    "china": "zh_CN",
    "hong_kong": "zh_HK",
    "singapore": "zh_SG",
    "germany": "de_DE",
    "france": "fr_FR",
}

# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    if not _HAS_YAML:
        raise ImportError("PyYAML required: pip install pyyaml")
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _find(filename: str) -> Optional[Path]:
    for base in [_WORKTREE, _REPO_ROOT]:
        p = base / filename
        if p.exists():
            return p
    return None


def _load(filename: str) -> dict:
    p = _find(filename)
    return _load_yaml(p) if p else {}


# ---------------------------------------------------------------------------
# Catalog row builder
# ---------------------------------------------------------------------------
MANGA_CATALOG_FIELDS = [
    "manga_catalog_id",
    "brand_id",
    "teacher_id",
    "series_slug",
    "genre",
    "market_id",
    "locale",
    "platform",
    "track_type",           # manga_partnership | webtoon_vertical | digital_publishing
    "active_series_target",
    "chapters_per_month",
    "volumes_per_year",
    "topic_allocation",     # JSON list
    "protagonist_id",
    "protagonist_name",
    "teacher_character_id",
    "teacher_display_name",
    "supporting_cast_count",
    "backgrounds_per_chapter",
    "character_views_total",
    "style_archetype",
    "market_variant_name",
    "status",               # planned | active | stub
    "priority",             # WAVE_1 | WAVE_2 | WAVE_3
]


def _make_id(brand_id: str, market_id: str, series_idx: int) -> str:
    raw = f"MANGA-{brand_id}-{market_id}-{series_idx:02d}"
    h = hashlib.md5(raw.encode()).hexdigest()[:8].upper()
    return f"MNG-{h}"


def _topic_list(plan_entry: dict) -> str:
    topo = plan_entry.get("topic_allocation", {})
    if isinstance(topo, dict):
        return json.dumps(list(topo.keys()))
    return json.dumps([])


def build_rows(
    brand_id: str,
    char_reg: dict,
    series_plan: dict,
    market_registry: dict,
    filter_market: Optional[str] = None,
) -> list[dict]:
    rows: list[dict] = []
    reg_entry = char_reg.get("brands", {}).get(brand_id, {})
    plan_entry = series_plan.get("brands", {}).get(brand_id, {})
    global_defaults = series_plan.get("global_defaults", {})

    genre = reg_entry.get("genre") or plan_entry.get("genre", "unknown")
    teacher_id = reg_entry.get("teacher_id") or plan_entry.get("teacher", "unknown")
    style_archetype = reg_entry.get("style_archetype", "")
    tc = reg_entry.get("teacher_character", {})
    teacher_char_id = tc.get("character_id", "")
    teacher_display = tc.get("display_name", teacher_id)
    supporting_cast_count = len(reg_entry.get("supporting_cast", []))
    asset_notes = reg_entry.get("asset_notes", {})
    bg_per_chapter = asset_notes.get("backgrounds_per_chapter", 7)
    char_views = asset_notes.get("character_views_needed", [])
    char_views_total = sum(
        int(v.split("_")[-1]) if v.split("_")[-1].isdigit() else 1
        for v in char_views
    ) * (1 + supporting_cast_count)

    active_series = plan_entry.get("active_series_target",
                                   global_defaults.get("active_series_target", 3))
    chapters_per_month = plan_entry.get("chapters_per_series_per_month",
                                        global_defaults.get("chapters_per_series_per_month", 2))
    volumes_per_year = plan_entry.get("volumes_per_year_target",
                                      global_defaults.get("volumes_per_year_target", 6))
    topic_alloc = _topic_list(plan_entry)

    # Determine which markets this brand serves with manga
    brand_markets = list(MANGA_MARKETS.keys())
    # bright_presence_tw is Taiwan only
    if brand_id == "bright_presence_tw":
        brand_markets = ["taiwan"]

    for market_id in brand_markets:
        if filter_market and market_id != filter_market.lower():
            continue

        locale = MANGA_LOCALE_MAP.get(market_id, "en_US")
        platforms = MANGA_MARKETS.get(market_id, [])
        market_variants = reg_entry.get("market_variants", {})
        mv = market_variants.get(locale, market_variants.get(market_id, {}))
        market_variant_name = mv.get("teacher_display_name", teacher_display)

        # Track type
        if market_id == "japan":
            track_types = ["manga_partnership", "digital_publishing"]
        elif market_id == "korea":
            track_types = ["webtoon_vertical", "digital_publishing"]
        else:
            track_types = ["digital_publishing"]

        # Priority tier
        if market_id in ("us", "japan"):
            priority = "WAVE_1"
        elif market_id in ("korea", "taiwan", "china"):
            priority = "WAVE_2"
        else:
            priority = "WAVE_3"

        # Status: already-dashboarded brands are active, rest planned
        active_brands = {"stillness_press", "cognitive_clarity", "digital_ground"}
        status = "active" if brand_id in active_brands else "planned"

        # One row per series slot × primary platform
        primary_platform = platforms[0] if platforms else "tbd"
        for track_type in track_types:
            for series_idx in range(1, active_series + 1):
                row = {
                    "manga_catalog_id": _make_id(brand_id, market_id, series_idx),
                    "brand_id": brand_id,
                    "teacher_id": teacher_id,
                    "series_slug": f"{brand_id}-{genre}-s{series_idx:02d}",
                    "genre": genre,
                    "market_id": market_id,
                    "locale": locale,
                    "platform": primary_platform,
                    "track_type": track_type,
                    "active_series_target": active_series,
                    "chapters_per_month": chapters_per_month,
                    "volumes_per_year": volumes_per_year,
                    "topic_allocation": topic_alloc,
                    "protagonist_id": reg_entry.get("supporting_cast", [{}])[0].get(
                        "character_id", f"{brand_id}_protagonist"
                    ),
                    "protagonist_name": reg_entry.get("supporting_cast", [{}])[0].get(
                        "display_name", "TBD"
                    ),
                    "teacher_character_id": teacher_char_id,
                    "teacher_display_name": market_variant_name,
                    "supporting_cast_count": supporting_cast_count,
                    "backgrounds_per_chapter": bg_per_chapter,
                    "character_views_total": char_views_total,
                    "style_archetype": style_archetype,
                    "market_variant_name": market_variant_name,
                    "status": status,
                    "priority": priority,
                }
                rows.append(row)

    return rows


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Manga Catalog Builder")
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--all", action="store_true", help="All brands × all manga markets")
    scope.add_argument("--market", type=str, help="Filter by market (e.g. japan, korea)")
    scope.add_argument("--brand", type=str, help="Filter by brand ID")
    parser.add_argument("--output", type=str,
                        default="artifacts/catalog/manga_catalog.csv",
                        help="Output CSV path (relative to repo root)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print plan without writing files")
    args = parser.parse_args()

    char_reg = _load("config/manga/character_brand_registry.yaml")
    series_plan = _load("config/manga/manga_brand_series_plan.yaml")
    market_registry = _load("config/catalog/market_catalog_registry.yaml")

    brand_ids = list(char_reg.get("brands", {}).keys())
    if args.brand:
        if args.brand not in brand_ids:
            print(f"Brand '{args.brand}' not found in character_brand_registry.")
            sys.exit(1)
        brand_ids = [args.brand]

    filter_market = args.market if args.market else None

    all_rows: list[dict] = []
    for bid in brand_ids:
        rows = build_rows(bid, char_reg, series_plan, market_registry,
                          filter_market=filter_market)
        all_rows.extend(rows)

    # Stats
    by_market: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_track: dict[str, int] = {}
    for r in all_rows:
        by_market[r["market_id"]] = by_market.get(r["market_id"], 0) + 1
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        by_track[r["track_type"]] = by_track.get(r["track_type"], 0) + 1

    scope_desc = f"market={args.market}" if args.market else (f"brand={args.brand}" if args.brand else "all")
    print(f"Manga Catalog Builder — scope: {scope_desc}")
    print(f"  Rows generated: {len(all_rows)}")
    print(f"  By market: {dict(sorted(by_market.items()))}")
    print(f"  By status: {by_status}")
    print(f"  By track:  {by_track}")

    if args.dry_run:
        print(f"\n[DRY-RUN] Would write {len(all_rows)} rows to {args.output}")
        return

    for base in [_WORKTREE, _REPO_ROOT]:
        out_path = base / args.output
        if out_path.parent.exists():
            break
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=MANGA_CATALOG_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\nWrote {len(all_rows)} rows → {out_path}")


if __name__ == "__main__":
    main()
