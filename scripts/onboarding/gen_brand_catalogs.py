#!/usr/bin/env python3
"""
Bridge: real book plans  →  Brand Director Operations catalog feed (per-brand static JSON).

Reads config/source_of_truth/book_plans_en_us/*.yaml (the real catalog plans) and emits one
JSON per brand under brand-wizard-app/public/brand_catalogs/<brand>.json. The dashboard
(brand_handoff_dashboard.html) fetches its own brand's file via ?brand=<id> -> base id, so
View Catalog + the weekly packet show the brand's ACTUAL titles/subtitles/taglines/keywords/
prices instead of placeholders. No live backend (same static-bridge pattern as
gen_brand_admin_brands.py / gen_setup_helper_brands.py).

Filename taxonomy: <brand>__<teacher>__<persona>__<topic>__<engine>.yaml
Plans are en_US only today, so this feeds the English (US) director view; JP/other lanes
keep their placeholder catalog until localized plans exist.

Run:  python3 scripts/onboarding/gen_brand_catalogs.py
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "config" / "source_of_truth" / "book_plans_en_us"
OUTDIR = REPO / "brand-wizard-app" / "public" / "brand_catalogs"


def book_from_plan(d: dict, stem: str) -> dict:
    parts = stem.split("__")  # brand, teacher, persona, topic, engine
    desc = d.get("description") or {}
    blurb = (desc.get("short_blurb") if isinstance(desc, dict) else "") or ""
    price = d.get("target_price") or {}
    kw = ((d.get("keywords") or {}).get("primary") or [])[:7]
    return {
        "title": (d.get("title") or "").strip(),
        "subtitle": (d.get("subtitle") or "").strip(),
        "desc": blurb.strip(),
        "angle": (d.get("cover_tagline") or "").strip(),       # the marketing hook
        "keywords": [str(k) for k in kw],
        "bisac": [str(c) for c in (d.get("bisac_codes") or [])][:3],
        "price": str(price.get("ebook_usd") or "4.99"),
        "audioPrice": str(price.get("audible_usd") or "9.99"),
        "persona": parts[2] if len(parts) > 2 else "",
        "topic": parts[3] if len(parts) > 3 else "",
        "engine": d.get("engine") or (parts[4] if len(parts) > 4 else ""),
    }


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"book plans dir not found: {SRC}")
    OUTDIR.mkdir(parents=True, exist_ok=True)
    by_brand: dict[str, list] = defaultdict(list)
    skipped = 0
    for f in sorted(SRC.glob("*.yaml")):
        try:
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except Exception:
            skipped += 1
            continue
        if not isinstance(d, dict) or not d.get("title"):
            skipped += 1
            continue
        brand = (d.get("author_positioning") or {}).get("brand") or f.name.split("__")[0]
        by_brand[brand].append(book_from_plan(d, f.stem))

    # Order by persona→topic→engine (NOT title): titles repeat across personas
    # (the subtitle carries the persona), so a title sort clusters duplicates into
    # one week. This interleaving keeps each weekly window varied + deterministic.
    for brand, books in sorted(by_brand.items()):
        books.sort(key=lambda b: (b["persona"], b["topic"], b["engine"], b["title"]))
        out = {"brand": brand, "count": len(books), "books": books}
        (OUTDIR / f"{brand}.json").write_text(
            json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"  {brand}: {len(books)} books -> brand_catalogs/{brand}.json")
    print(f"wrote {len(by_brand)} brand catalogs to {OUTDIR.relative_to(REPO)}"
          + (f" (skipped {skipped} unreadable/empty)" if skipped else ""))


main()
