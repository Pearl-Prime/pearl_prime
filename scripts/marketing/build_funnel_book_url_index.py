#!/usr/bin/env python3
"""Build config/marketing/funnel_book_url_index.json from catalog CSVs (fast)."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STOREFRONT_BASE = "pearlprime.shop"
DEFAULT_TEACHER_PRIORITY = ("ahjan", "omote", "joshin")

BOOK_CATALOGS = {
    "en_US": "artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv",
    "ja_JP": "artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv",
    "zh_CN": "artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv",
    "zh_TW": "artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv",
}


def _load_yaml_topics() -> set[str]:
    import yaml

    data = yaml.safe_load((REPO_ROOT / "config/funnel/freebie_to_book_map.yaml").read_text(encoding="utf-8"))
    return set((data.get("topics") or {}).keys())


def _pick_teacher(rows: list[dict]) -> dict:
    by_teacher = {r["teacher_id"]: r for r in rows}
    for tid in DEFAULT_TEACHER_PRIORITY:
        if tid in by_teacher:
            return by_teacher[tid]
    return sorted(rows, key=lambda r: r["teacher_id"])[0]


def _inner_key(topic: str, persona: str, teacher_id: str) -> str:
    return f"{topic}_{persona}_{teacher_id}"


def _book_url(locale: str, brand: str, inner_key: str, product_type: str) -> str:
    url_locale = locale.replace("_", "-")
    return f"https://{STOREFRONT_BASE}/{url_locale}/{product_type}/{brand}/{inner_key}"


def _merge_brand_catalog_urls(
    loc_topics: dict,
    *,
    brand_id: str,
    locale: str,
    funnel_topics: set[str],
    landing_base: str = "https://brand-admin-onboarding-bu2.pages.dev",
) -> None:
    """Add topic×persona URLs from brand-wizard catalog JSON (e.g. way_stream_sanctuary)."""
    catalog_path = REPO_ROOT / f"brand-wizard-app/public/brand_catalogs/{brand_id}.json"
    if not catalog_path.exists():
        return
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    books = data.get("books") or []
    seen: set[tuple[str, str]] = set()
    for book in books:
        book_id = str(book.get("book_id") or book.get("file_stem") or "")
        if not book_id or book_id.endswith("__1hr"):
            continue
        parts = book_id.split("__")
        if len(parts) < 5:
            continue
        persona = parts[2]
        topic = parts[3]
        if topic not in funnel_topics:
            continue
        key = (topic, persona)
        if key in seen:
            continue
        seen.add(key)
        entry = {
            "brand_id": brand_id,
            "teacher_id": parts[1] if parts[1] != "default_teacher" else "",
            "inner_key": book_id,
            "title": str(book.get("title") or ""),
            "book_url": f"{landing_base.rstrip('/')}/download/{book_id}",
            "audiobook_url": None,
            "sku_id": book_id,
        }
        loc_topics.setdefault(topic, {}).setdefault(persona, {})[brand_id] = entry


def build_index(locales: list[str] | None = None) -> dict:
    funnel_topics = _load_yaml_topics()
    locales_out: dict = {}
    target_locales = locales or list(BOOK_CATALOGS.keys())

    for loc in target_locales:
        rel = BOOK_CATALOGS.get(loc)
        if not rel:
            continue
        path = REPO_ROOT / rel
        if not path.exists():
            print(f"WARN: missing {path}", file=sys.stderr)
            continue

        buckets: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                topic = row.get("topic") or ""
                if topic not in funnel_topics:
                    continue
                persona = row.get("persona") or ""
                brand = row.get("brand") or ""
                teacher = row.get("teacher_id") or ""
                if not all([topic, persona, brand, teacher]):
                    continue
                buckets[(topic, persona, brand)].append(row)

        loc_topics: dict = {}
        for (topic, persona, brand), rows in sorted(buckets.items()):
            chosen = _pick_teacher(rows)
            teacher = chosen["teacher_id"]
            ik = _inner_key(topic, persona, teacher)
            entry = {
                "brand_id": brand,
                "teacher_id": teacher,
                "inner_key": ik,
                "title": chosen.get("title") or "",
                "book_url": _book_url(loc, brand, ik, "book"),
                "audiobook_url": _book_url(loc, brand, ik, "audiobook"),
                "sku_id": f"book_{loc}_{brand}_{ik}",
            }
            loc_topics.setdefault(topic, {}).setdefault(persona, {})[brand] = entry

        if loc == "en_US":
            _merge_brand_catalog_urls(
                loc_topics,
                brand_id="way_stream_sanctuary",
                locale=loc,
                funnel_topics=funnel_topics,
            )

        locales_out[loc] = loc_topics

    return {
        "schema_version": 1,
        "last_updated": dt.date.today().isoformat(),
        "funnel_topics": sorted(funnel_topics),
        "storefront_base_url": STOREFRONT_BASE,
        "locales": locales_out,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "config/marketing/funnel_book_url_index.json")
    ap.add_argument("--locale", action="append", dest="locales", help="Locale(s) to include")
    ap.add_argument("--all-locales", action="store_true", help="Include all catalog locales (large)")
    ap.add_argument("--check", action="store_true", help="Exit 1 if --out would change")
    args = ap.parse_args()

    locales = args.locales
    if args.all_locales:
        locales = list(BOOK_CATALOGS.keys())
    elif not locales:
        locales = ["en_US"]

    doc = build_index(locales)
    out = args.out
    payload = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"

    if args.check and out.exists():
        existing = out.read_text(encoding="utf-8")
        if existing != payload:
            print(f"STALE: {out} — run build_funnel_book_url_index.py", file=sys.stderr)
            return 1
        print(f"OK: {out} up to date")
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(payload, encoding="utf-8")
    n = sum(
        len(brands)
        for loc in doc["locales"].values()
        for personas in loc.values()
        for brands in personas.values()
    )
    print(f"OK: wrote {out} ({n} topic×persona cells)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
