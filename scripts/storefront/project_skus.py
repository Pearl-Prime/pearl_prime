#!/usr/bin/env python3
"""Project the Pearl Prime catalog into storefront SKU rows + a D1 seed.

The D1 `sku` table is a PROJECTION CACHE of the catalog CSVs, not a source of
truth (spec §7.5 anti-drift #2). This is the projector named in
docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md §7.1 (previously MISSING).

Spine = config/storefront/sku_url_map.yaml (emitted by
scripts/marketing/generate_sku_url_map.py): it already carries the
content-deterministic sku_id / canonical_url / inner_key for every SKU (§2.5).
We JOIN that spine to the source catalog rows to recover
title/subtitle/topic/persona/teacher_id/output_target_path, then add the
storefront-only fields (price_cents, currency, cover_url, preview_url,
asset_url, status). Reusing the spine's sku_id means this projector cannot
drift from generate_sku_url_map.py.

Outputs:
  --out-sql   D1 seed (apply AFTER 0001_init.sql): INSERT OR REPLACE into `sku`
              + INSERT into `sku_search`. Idempotent on `sku`.
  --out-json  optional catalog feed (frontend / local dev fallback)

Pricing = Q-PRP-PRICE-01 launch defaults (book $4.99 / audiobook $9.99 /
manga $1.99), per-locale price book below — no live FX. Refine later via a
price-book config without touching this projector.

Pure stdlib + PyYAML. No paid LLM APIs.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import json
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
SKU_MAP = REPO / "config/storefront/sku_url_map.yaml"
BOOK_CSV = REPO / "artifacts/catalog/pearl_prime_book_script_catalogs/{loc}_catalog.csv"
MANGA_CSV = REPO / "artifacts/catalog/manga/{loc}_manga_catalog.csv"
MANGA_JA_SSOT = REPO / "artifacts/catalog/manga/ssot_rollup/ja_JP_manga_catalog_ssot.csv"

# storefront locale (hyphen) -> (csv token, currency, zero-decimal currency?)
LOCALES = {
    "en-US": ("en_US", "USD", False),
    "ja-JP": ("ja_JP", "JPY", True),
    "zh-TW": ("zh_TW", "TWD", False),
    "zh-CN": ("zh_CN", "CNY", False),
    "ko-KR": ("ko_KR", "KRW", True),
}

# Q-PRP-PRICE-01 launch defaults, each in the currency's smallest unit.
# JPY/KRW are zero-decimal. Phase A = USD + JPY; the rest are Phase-B
# placeholders refined when those locales launch.
PRICE_BOOK = {
    "USD": {"book": 499, "audiobook": 999, "manga": 199},
    "JPY": {"book": 750, "audiobook": 1500, "manga": 300},
    "TWD": {"book": 150, "audiobook": 300, "manga": 60},
    "CNY": {"book": 3500, "audiobook": 6900, "manga": 1500},
    "KRW": {"book": 6500, "audiobook": 13000, "manga": 2500},
}
ASSET_EXT = {"book": "epub", "audiobook": "m4b", "manga": "pdf"}
PREVIEW_EXT = {"book": "epub", "audiobook": "mp3", "manga": "png"}

SKU_COLS = [
    "sku_id", "locale", "brand_id", "product_type", "sub_type", "topic", "persona",
    "series_id", "title", "subtitle", "description", "cover_url", "preview_url",
    "asset_url", "price_cents", "currency", "status", "bundle_id", "upstream_path",
    "created_at", "updated_at",
]
SEARCH_COLS = [
    "sku_id", "title", "subtitle", "brand_id", "topic", "persona",
    "series_title", "archetype", "description",
]
INT_COLS = {"price_cents", "created_at", "updated_at"}


def _load_yaml(path: Path):
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    return yaml.load(path.read_text(encoding="utf-8"), Loader=loader)


def _csv(loc):
    return LOCALES[loc][0]


def load_book_index(loc):
    """(brand, inner_key) -> catalog row, for the book/audiobook join."""
    path = Path(str(BOOK_CSV).format(loc=_csv(loc)))
    idx = {}
    if not path.exists():
        return idx
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            inner = f"{row['topic']}_{row['persona']}_{row['teacher_id']}"
            idx[(row["brand"], inner)] = row
    return idx


def load_manga_index(loc):
    """(brand, series_id) -> manga catalog row."""
    path = MANGA_JA_SSOT if loc == "ja-JP" else Path(str(MANGA_CSV).format(loc=_csv(loc)))
    idx = {}
    if not path.exists():
        return idx
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            brand = row.get("brand") or row.get("brand_id") or ""
            sid = row.get("series_id") or ""
            if sid:
                idx[(brand, sid)] = row
    return idx


def status_from(readiness):
    r = (readiness or "").strip().lower()
    return "draft" if r.startswith("blocked") else "active"


def sql_val(v, col):
    if col in INT_COLS:
        return str(int(v))
    if v is None or v == "":
        return "NULL"
    return "'" + str(v).replace("'", "''") + "'"


def build_rows(entries, locales, product_types, ts):
    book_idx = {loc: load_book_index(loc) for loc in locales}
    manga_idx = {loc: load_manga_index(loc) for loc in locales}
    rows, misses, by = [], 0, {}

    for e in entries:
        loc, pt = e["locale"], e["product_type"]
        if loc not in locales or pt not in product_types:
            continue
        brand, inner = e["brand_id"], e["inner_key"]
        cur = LOCALES[loc][1]
        sku = {c: None for c in SKU_COLS}
        sku.update(
            sku_id=e["sku_id"], locale=loc, brand_id=brand, product_type=pt,
            cover_url=f"covers/{loc}/{brand}/{inner}.jpg",
            preview_url=f"previews/{e['sku_id']}.{PREVIEW_EXT.get(pt, 'bin')}",
            asset_url=f"assets/{e['sku_id']}.{ASSET_EXT.get(pt, 'bin')}",
            price_cents=PRICE_BOOK[cur][pt], currency=cur, status="draft",
            created_at=ts, updated_at=ts,
        )
        sku["series_title"] = None  # search-only column
        sku["archetype"] = None     # search-only column
        sku["brand_label"] = None   # localized display name (JSON feed only, not the D1 sku table)

        if pt in ("book", "audiobook"):
            row = book_idx[loc].get((brand, inner))
            if not row:
                misses += 1
                continue
            sku.update(
                topic=row.get("topic"), persona=row.get("persona"),
                title=row.get("title"), subtitle=row.get("subtitle"),
                upstream_path=row.get("output_target_path"),
                status=status_from(row.get("readiness_status")),
                archetype=row.get("brand_locale_name"),
                brand_label=row.get("brand_locale_name"),
            )
        elif pt == "manga":
            row = manga_idx[loc].get((brand, inner))
            if not row:
                misses += 1
                continue
            title = row.get("localized_title") or row.get("series_title") or row.get("title")
            if not title:  # en_US manga titles not yet synthesized -> derived working title (NOT NULL)
                base = inner[len(brand) + 1:] if inner.startswith(brand + "_") else inner
                title = " ".join(w.capitalize() for w in base.split("_")) or inner
            sku.update(
                series_id=inner, title=title, series_title=title,
                subtitle=row.get("genre"),
                upstream_path=row.get("output_target_path"),
                status=status_from(row.get("readiness_status")),
                brand_label=row.get("brand_locale_name"),
            )
        else:
            misses += 1
            continue

        rows.append(sku)
        by[(loc, pt)] = by.get((loc, pt), 0) + 1
    return rows, misses, by


def emit_sql(rows, out: Path):
    lines = [
        "-- Pearl Prime storefront SKU seed — generated by scripts/storefront/project_skus.py",
        "-- Apply AFTER storefront/migrations/0001_init.sql. Idempotent on `sku`.",
        "PRAGMA foreign_keys = OFF;",
        "DELETE FROM sku_search;",
        "BEGIN TRANSACTION;",
    ]
    for s in rows:
        vals = ", ".join(sql_val(s.get(c), c) for c in SKU_COLS)
        lines.append(f"INSERT OR REPLACE INTO sku ({', '.join(SKU_COLS)}) VALUES ({vals});")
    for s in rows:
        vals = ", ".join(sql_val(s.get(c), c) for c in SEARCH_COLS)
        lines.append(f"INSERT INTO sku_search ({', '.join(SEARCH_COLS)}) VALUES ({vals});")
    lines.append("COMMIT;")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def emit_json(rows, out: Path):
    cols = SKU_COLS + ["brand_label"]
    feed = [{c: s.get(c) for c in cols} for s in rows]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(feed, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Project catalog -> storefront SKU rows + D1 seed.")
    ap.add_argument("--locales", default="en-US",
                    help="comma list in hyphen form (en-US,ja-JP) or 'all'")
    ap.add_argument("--product-types", default="book,audiobook,manga")
    ap.add_argument("--out-sql", default="storefront/seeds/skus.sql")
    ap.add_argument("--out-json", default=None)
    ap.add_argument("--sample", type=int, default=0,
                    help="emit only ~N rows via stride sampling (brand-diverse dev fixture); 0 = all")
    args = ap.parse_args(argv)

    locales = (list(LOCALES) if args.locales == "all"
               else [x.strip().replace("_", "-") for x in args.locales.split(",") if x.strip()])
    for loc in locales:
        if loc not in LOCALES:
            ap.error(f"unknown locale {loc!r}; choices: {', '.join(LOCALES)} or 'all'")
    pts = [p.strip() for p in args.product_types.split(",") if p.strip()]

    doc = _load_yaml(SKU_MAP)
    entries = doc.get("url_map", [])
    try:
        ts = calendar.timegm(time.strptime(str(doc.get("last_updated", "")), "%Y-%m-%d"))
    except ValueError:
        ts = 0

    rows, misses, by = build_rows(entries, locales, pts, ts)
    if args.sample and len(rows) > args.sample:
        stride = max(1, len(rows) // args.sample)
        rows = rows[::stride][:args.sample]
        by = {}
        for s in rows:
            by[(s["locale"], s["product_type"])] = by.get((s["locale"], s["product_type"]), 0) + 1
    emit_sql(rows, Path(args.out_sql))
    if args.out_json:
        emit_json(rows, Path(args.out_json))

    print(f"spine entries: {len(entries)}")
    print(f"SKUs projected: {len(rows)}  (unmatched spine entries skipped: {misses})")
    for k in sorted(by):
        print(f"  {k[0]:6} {k[1]:9}: {by[k]}")
    active = sum(1 for s in rows if s["status"] == "active")
    print(f"status: active={active} draft={len(rows) - active}")
    print(f"seed SQL  -> {args.out_sql}")
    if args.out_json:
        print(f"json feed -> {args.out_json}")
    if rows:
        s = rows[0]
        print(f"sample: {s['sku_id']} | {s['title']!r} | {s['price_cents']} {s['currency']} | {s['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
