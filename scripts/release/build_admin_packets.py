#!/usr/bin/env python3
"""
Platform Delivery Bundle Builder
==================================
Builds weekly platform-specific download packets for brand admins.
Per brand, per platform: metadata CSV + upload instructions.

Output structure:
    artifacts/release/<YEAR>-W<WW>/<brand_id>/
        google_play/
            metadata.csv
            upload_instructions.md
        amazon_kdp/
            metadata.csv
            upload_instructions.md
        rakuten_kobo/          # Japan market only
            metadata.csv
            upload_instructions.md
        packet_summary.json

Usage:
    python3 scripts/release/build_admin_packets.py --brand stillness_press --week current
    python3 scripts/release/build_admin_packets.py --all --week current
    python3 scripts/release/build_admin_packets.py --market japan --week 2026-W17
    python3 scripts/release/build_admin_packets.py --brand stillness_press --week current --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
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
# Platform caps
# ---------------------------------------------------------------------------
PLATFORM_WEEKLY_CAPS: dict[str, int] = {
    "google_play": 15,
    "amazon_kdp": 10,
    "rakuten_kobo": 5,
    "apple_books": 10,
    "audible": 5,
    "findaway": 20,
}

# Market → platforms with Kobo
KOBO_MARKETS = {"japan", "taiwan", "korea", "singapore", "hong_kong"}

# Market → locale
MARKET_TO_LOCALE: dict[str, str] = {
    "us": "en_US",
    "japan": "ja_JP",
    "korea": "ko_KR",
    "germany": "de_DE",
    "france": "fr_FR",
    "taiwan": "zh_TW",
    "china": "zh_CN",
    "hong_kong": "zh_HK",
    "spain": "es_ES",
    "latam": "es_US",
    "brazil": "pt_BR",
    "italy": "it_IT",
    "singapore": "zh_SG",
    "hungary": "hu_HU",
}

# ---------------------------------------------------------------------------
# Week resolution
# ---------------------------------------------------------------------------

def _current_week_label() -> str:
    today = datetime.now(tz=timezone.utc)
    return f"{today.year}-W{today.isocalendar()[1]:02d}"


def _parse_week(week_str: str) -> str:
    if week_str.lower() == "current":
        return _current_week_label()
    if week_str.lower() == "next":
        today = datetime.now(tz=timezone.utc)
        next_week = today + timedelta(weeks=1)
        return f"{next_week.year}-W{next_week.isocalendar()[1]:02d}"
    # Accept YYYY-WWW format
    if "W" in week_str.upper():
        return week_str.upper().replace("w", "W")
    raise ValueError(f"Cannot parse week '{week_str}'. Use 'current', 'next', or 'YYYY-WNN'.")

# ---------------------------------------------------------------------------
# Catalog loader
# ---------------------------------------------------------------------------

def _load_catalog(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        return []
    with open(csv_path, "r", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _catalog_path() -> Path:
    for base in [_WORKTREE, _REPO_ROOT]:
        p = base / "artifacts/catalog/full_catalog.csv"
        if p.exists():
            return p
    return _REPO_ROOT / "artifacts/catalog/full_catalog.csv"


# ---------------------------------------------------------------------------
# Registry loaders
# ---------------------------------------------------------------------------

def _load_market_registry() -> dict:
    for base in [_WORKTREE, _REPO_ROOT]:
        p = base / "config/catalog/market_catalog_registry.yaml"
        if p.exists() and _HAS_YAML:
            with open(p, "r", encoding="utf-8") as fh:
                return yaml.safe_load(fh) or {}
    return {}


def _all_brand_ids() -> list[str]:
    """Return deduplicated list of brand IDs from the registry."""
    registry = _load_market_registry()
    brand_set: set[str] = set()
    for market in registry.get("markets", {}).values():
        for b in market.get("brands", []):
            if isinstance(b, str):
                brand_set.add(b)
    # Fallback: known teacher brands
    if not brand_set:
        brand_set = {
            "stillness_press", "cognitive_clarity", "somatic_wisdom", "qi_foundation",
            "digital_ground", "heart_balance", "relational_calm", "warrior_calm",
            "sleep_restoration", "body_memory", "solar_return", "devotion_path",
        }
    return sorted(brand_set)


def _brands_for_market(market_id: str) -> list[str]:
    registry = _load_market_registry()
    markets = registry.get("markets", {})
    m = markets.get(market_id.lower(), {})
    brands = [b for b in m.get("brands", []) if isinstance(b, str)]
    if not brands:
        brands = _all_brand_ids()
    return brands


# ---------------------------------------------------------------------------
# Platform selection
# ---------------------------------------------------------------------------

def _platforms_for_brand(brand_id: str, market_id: Optional[str] = None) -> list[str]:
    """Return the platforms to generate packets for."""
    platforms = ["google_play", "amazon_kdp", "apple_books"]
    # Add Kobo for Japan/APAC markets
    if market_id and market_id.lower() in KOBO_MARKETS:
        platforms.append("rakuten_kobo")
    elif any(token in brand_id for token in ["_tw", "_cn", "_hk", "_sg", "_jp"]):
        platforms.append("rakuten_kobo")
    return platforms


# ---------------------------------------------------------------------------
# Metadata CSV generation
# ---------------------------------------------------------------------------
METADATA_FIELDS = [
    "isbn", "title", "subtitle", "author", "description",
    "category", "bisac_code", "language", "price_usd",
    "keywords", "series_name", "series_position",
]


def _stub_entry(brand_id: str, i: int, week: str, platform: str) -> dict:
    """Generate a stub metadata row for brands without a real catalog."""
    return {
        "isbn": f"979-8-{brand_id[:8].replace('_', '')}-{i:04d}-0",
        "title": f"[{brand_id} title {i} — {week}]",
        "subtitle": f"A {platform}-ready placeholder",
        "author": brand_id.replace("_", " ").title(),
        "description": f"Catalog entry for {brand_id}, week {week}. Replace with generated content.",
        "category": "Self-Help / Mindfulness",
        "bisac_code": "SEL031000",
        "language": "en",
        "price_usd": "9.99",
        "keywords": f"{brand_id}, mindfulness, wellbeing",
        "series_name": "",
        "series_position": str(i),
    }


def _catalog_to_metadata(entry: dict) -> dict:
    return {
        "isbn": entry.get("catalog_id", ""),
        "title": entry.get("title", ""),
        "subtitle": entry.get("subtitle", ""),
        "author": entry.get("teacher_id", entry.get("brand_id", "")),
        "description": entry.get("description", ""),
        "category": "Self-Help / Mindfulness",
        "bisac_code": "SEL031000",
        "language": "en",
        "price_usd": entry.get("price_usd", "9.99"),
        "keywords": entry.get("keywords", ""),
        "series_name": entry.get("series_id", ""),
        "series_position": entry.get("series_position", ""),
    }


# ---------------------------------------------------------------------------
# Upload instructions
# ---------------------------------------------------------------------------

_INSTRUCTIONS: dict[str, str] = {
    "google_play": """\
# Google Play Books — Upload Instructions

1. Go to https://play.google.com/books/publish/ and sign in to your brand account.
2. Click **Add book** → **Upload files** → select each EPUB file.
3. In the metadata form, copy values from `metadata.csv` for this packet.
4. Set **Price** to the value in the `price_usd` column (convert to local currency if needed).
5. Set **Language** and **Category** from the CSV.
6. Add **Keywords** exactly as listed — do not reorder.
7. Submit for review. Approval typically takes 24–72 hours.

Weekly cap for this brand: {cap} titles/week. Do not exceed this limit.
""",

    "amazon_kdp": """\
# Amazon KDP — Upload Instructions

1. Sign in at https://kdp.amazon.com/ with your brand publisher account.
2. Click **+ Kindle eBook** for each title.
3. Fill in Title, Subtitle, Author, and Description from `metadata.csv`.
4. Set **BISAC category** using the `bisac_code` column.
5. Upload the EPUB/MOBI content file from the `files/` subfolder (if present).
6. Set price from `price_usd`. KDP converts to local currency automatically.
7. Enroll in KDP Select only if brand strategy permits (check brand_teacher_matrix).
8. Publish. Live in 24–48 hours.

Weekly cap for this brand: {cap} titles/week.
""",

    "rakuten_kobo": """\
# Rakuten Kobo — Upload Instructions (Japan/APAC)

1. Sign in at https://www.kobo.com/writinglife with your publisher account.
2. Click **Add a Book** for each title.
3. Copy metadata from `metadata.csv` — Japanese/Traditional Chinese titles take priority
   where available in the `title` column.
4. Select **Primary Language** from the `language` column.
5. Set price in JPY/TWD/HKD as appropriate; use `price_usd` as the USD baseline.
6. Upload EPUB from `files/` subfolder if present.
7. Submit. Kobo Japan review takes 3–5 business days.

Weekly cap for this brand: {cap} titles/week.
""",

    "apple_books": """\
# Apple Books — Upload Instructions

1. Use Apple Books Connect at https://itunesconnect.apple.com/ (Books section).
2. For each title: click **+** → **New Book**.
3. Fill in all required fields from `metadata.csv`.
4. Upload the EPUB file from `files/` if present.
5. Set territory pricing from `price_usd` baseline.
6. Submit for review. Apple review takes 2–7 business days.

Weekly cap for this brand: {cap} titles/week.
""",
}


def _write_instructions(out_dir: Path, platform: str) -> None:
    cap = PLATFORM_WEEKLY_CAPS.get(platform, 10)
    template = _INSTRUCTIONS.get(platform, f"# {platform.title()} upload instructions\n\nSee platform docs.\n")
    content = template.format(cap=cap)
    (out_dir / "upload_instructions.md").write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Packet builder
# ---------------------------------------------------------------------------

def build_packet(
    brand_id: str,
    week: str,
    catalog_entries: list[dict],
    market_id: Optional[str],
    out_base: Path,
    dry_run: bool = False,
) -> dict:
    platforms = _platforms_for_brand(brand_id, market_id)
    brand_dir = out_base / week / brand_id
    packet_summary: dict = {
        "brand": brand_id,
        "week": week,
        "market": market_id,
        "platforms": platforms,
        "book_count": 0,
        "status": "OK",
        "platform_packets": {},
    }

    # Filter entries for this brand
    brand_entries = [e for e in catalog_entries if e.get("brand_id", "").lower() == brand_id.lower()]

    # If no real catalog entries, generate stubs so admin UI can still render
    use_stubs = len(brand_entries) == 0

    for platform in platforms:
        cap = PLATFORM_WEEKLY_CAPS.get(platform, 10)
        plat_entries = brand_entries[:cap]

        if use_stubs:
            plat_entries = [_stub_entry(brand_id, i + 1, week, platform) for i in range(3)]
            rows = plat_entries
        else:
            rows = [_catalog_to_metadata(e) for e in plat_entries]

        if dry_run:
            print(f"  [DRY-RUN] {brand_id}/{platform}: {len(rows)} rows (cap={cap})")
            packet_summary["platform_packets"][platform] = {"row_count": len(rows), "dry_run": True}
            continue

        plat_dir = brand_dir / platform
        plat_dir.mkdir(parents=True, exist_ok=True)

        # Write metadata.csv
        with open(plat_dir / "metadata.csv", "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=METADATA_FIELDS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

        # Write upload_instructions.md
        _write_instructions(plat_dir, platform)

        packet_summary["platform_packets"][platform] = {
            "row_count": len(rows),
            "cap": cap,
            "metadata_csv": str(plat_dir / "metadata.csv"),
        }

    if not use_stubs:
        packet_summary["book_count"] = len(brand_entries)
    else:
        packet_summary["book_count"] = 0
        packet_summary["status"] = "STUB — no catalog entries found; placeholder packet generated"

    if not dry_run:
        brand_dir.mkdir(parents=True, exist_ok=True)
        (brand_dir / "packet_summary.json").write_text(
            json.dumps(packet_summary, indent=2), encoding="utf-8"
        )

    return packet_summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Platform Delivery Bundle Builder")
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--brand", type=str, help="Single brand ID")
    scope.add_argument("--all", action="store_true", help="All brands")
    scope.add_argument("--market", type=str, help="All brands in a market (e.g. japan)")
    parser.add_argument("--week", type=str, default="current",
                        help="Week label: 'current', 'next', or 'YYYY-WNN' (default: current)")
    parser.add_argument("--output-base", type=str, default="artifacts/release",
                        help="Base output directory (relative to repo root)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be written without creating files")
    args = parser.parse_args()

    week = _parse_week(args.week)
    print(f"Building admin packets — week {week}")
    if args.dry_run:
        print("[DRY-RUN] — no files will be written")

    # Resolve output base
    for base in [_WORKTREE, _REPO_ROOT]:
        out_base = base / args.output_base
        if out_base.parent.exists():
            break

    # Load catalog
    cat_path = _catalog_path()
    catalog = _load_catalog(cat_path)
    print(f"Catalog: {len(catalog)} entries from {cat_path}")

    # Determine brands to process
    market_id: Optional[str] = None
    if args.brand:
        brands = [args.brand]
    elif args.market:
        market_id = args.market.lower()
        brands = _brands_for_market(market_id)
        print(f"Market '{market_id}': {len(brands)} brands")
    else:
        brands = _all_brand_ids()
        print(f"All brands: {len(brands)}")

    summaries: list[dict] = []
    for brand_id in brands:
        print(f"  Building: {brand_id}")
        summary = build_packet(
            brand_id=brand_id,
            week=week,
            catalog_entries=catalog,
            market_id=market_id,
            out_base=out_base,
            dry_run=args.dry_run,
        )
        summaries.append(summary)

    print(f"\nDone. {len(summaries)} brand packet(s) for week {week}.")
    if not args.dry_run:
        out_dir = out_base / week
        print(f"Output: {out_dir}/")


if __name__ == "__main__":
    main()
