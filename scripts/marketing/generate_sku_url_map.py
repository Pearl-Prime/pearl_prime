#!/usr/bin/env python3
"""generate_sku_url_map.py — hand-curation generator for `config/storefront/sku_url_map.yaml`.

Per PEARL_PRIME_STOREFRONT_V1_SPEC.md §AMENDMENT-2026-06-04.3 §14 + §2.5:

    sku_id        = <product_type>_<locale>_<brand_id>_<inner_key>
    canonical_url = https://pearlprime.shop/<locale>/<product_type>/<brand_id>/<inner_key>

    inner_key (book)      = <topic>_<persona>_<teacher_id>
    inner_key (audiobook) = same as parent book's inner_key
    inner_key (manga)     = <series_id>

This script is a DETERMINISTIC HAND-CURATION substitute that runs BEFORE
Pearl_Int's CF wiring ws lands the catalog projector. It writes the same
schema that the catalog projector will eventually produce.

Source files:
- artifacts/catalog/pearl_prime_book_script_catalogs/{en_US,ja_JP,zh_CN,zh_TW}_catalog.csv (book + audiobook SKUs)
- artifacts/catalog/manga/{en_US,ja_JP,zh_CN,zh_TW}_manga_catalog.csv (manga SKUs)

Usage:
    python3 scripts/marketing/generate_sku_url_map.py \
        --out config/storefront/sku_url_map.yaml
"""

from __future__ import annotations

import argparse
import csv
import datetime
import pathlib
import sys
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
STOREFRONT_BASE_URL = "pearlprime.shop"

BOOK_CATALOGS = [
    "artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv",
    "artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv",
    "artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv",
    "artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv",
]

MANGA_CATALOGS = [
    "artifacts/catalog/manga/en_US_manga_catalog.csv",
    "artifacts/catalog/manga/ja_JP_manga_catalog.csv",
    "artifacts/catalog/manga/zh_CN_manga_catalog.csv",
    "artifacts/catalog/manga/zh_TW_manga_catalog.csv",
]


def _norm_locale(loc: str) -> str:
    """Normalize CSV-flavored locale tag (en_US) to URL-flavored tag (en-US)."""
    return loc.replace("_", "-")


def _book_inner_key(topic: str, persona: str, teacher_id: str) -> str:
    return f"{topic}_{persona}_{teacher_id}"


def _build_book_entries() -> list[dict]:
    entries: list[dict] = []
    for rel in BOOK_CATALOGS:
        path = REPO_ROOT / rel
        if not path.exists():
            print(f"WARN: missing catalog: {path}", file=sys.stderr)
            continue
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_locale = row["locale"]
                url_locale = _norm_locale(csv_locale)
                brand_id = row["brand"]
                inner_key = _book_inner_key(
                    row["topic"], row["persona"], row["teacher_id"]
                )
                # Emit BOOK SKU
                entries.append(
                    {
                        "locale": url_locale,
                        "product_type": "book",
                        "brand_id": brand_id,
                        "inner_key": inner_key,
                        "canonical_url": f"https://{STOREFRONT_BASE_URL}/{url_locale}/book/{brand_id}/{inner_key}",
                        "sku_id": f"book_{csv_locale}_{brand_id}_{inner_key}",
                        "source_csv": rel,
                    }
                )
                # Emit AUDIOBOOK SKU (per §2.5 — shares parent book's inner_key)
                entries.append(
                    {
                        "locale": url_locale,
                        "product_type": "audiobook",
                        "brand_id": brand_id,
                        "inner_key": inner_key,
                        "canonical_url": f"https://{STOREFRONT_BASE_URL}/{url_locale}/audiobook/{brand_id}/{inner_key}",
                        "sku_id": f"audiobook_{csv_locale}_{brand_id}_{inner_key}",
                        "source_csv": rel,
                    }
                )
    return entries


def _build_manga_entries() -> list[dict]:
    entries: list[dict] = []
    for rel in MANGA_CATALOGS:
        path = REPO_ROOT / rel
        if not path.exists():
            print(f"WARN: missing manga catalog: {path}", file=sys.stderr)
            continue
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_locale = row["locale"]
                url_locale = _norm_locale(csv_locale)
                brand_id = row["brand"]
                inner_key = row["series_id"]
                entries.append(
                    {
                        "locale": url_locale,
                        "product_type": "manga",
                        "brand_id": brand_id,
                        "inner_key": inner_key,
                        "canonical_url": f"https://{STOREFRONT_BASE_URL}/{url_locale}/manga/{brand_id}/{inner_key}",
                        "sku_id": f"manga_{csv_locale}_{brand_id}_{inner_key}",
                        "source_csv": rel,
                    }
                )
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default="config/storefront/sku_url_map.yaml",
        help="Output YAML path (relative to repo root).",
    )
    args = parser.parse_args()

    out_path = REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    entries = _build_book_entries() + _build_manga_entries()
    # Deterministic ordering: by (sku_id) — stable across runs.
    entries.sort(key=lambda e: e["sku_id"])

    today = datetime.date.today().isoformat()
    header = (
        "# config/storefront/sku_url_map.yaml\n"
        "# Hand-curated 2026-06-06 from artifacts/catalog/ CSVs (book + manga); will\n"
        "# be regenerated by Pearl_Int's catalog projector once that ws lands.\n"
        "# Identity per PEARL_PRIME_STOREFRONT_V1_SPEC.md §2.5 + §AMENDMENT-2026-06-04.3 §14.\n"
        "#\n"
        "# Source CSVs:\n"
        "#   - artifacts/catalog/pearl_prime_book_script_catalogs/{en_US,ja_JP,zh_CN,zh_TW}_catalog.csv\n"
        "#   - artifacts/catalog/manga/{en_US,ja_JP,zh_CN,zh_TW}_manga_catalog.csv\n"
        "#\n"
        "# Each book SKU emits BOTH a book row AND an audiobook row (audiobook shares\n"
        "# the parent book's inner_key per §2.5).\n"
        "#\n"
        "# Regenerate via:\n"
        "#   python3 scripts/marketing/generate_sku_url_map.py --out config/storefront/sku_url_map.yaml\n"
    )

    doc = {
        "schema_version": 1,
        "last_updated": today,
        "storefront_base_url": STOREFRONT_BASE_URL,
        "url_map": entries,
    }

    with open(out_path, "w") as f:
        f.write(header)
        yaml.safe_dump(doc, f, sort_keys=False, default_flow_style=False, allow_unicode=True, width=4096)

    print(f"OK: wrote {out_path}")
    print(f"     {len(entries)} SKU rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
