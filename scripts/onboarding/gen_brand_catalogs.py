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
import argparse
import json
from collections import defaultdict, Counter
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "config" / "source_of_truth" / "book_plans_en_us"
OUTDIR = REPO / "brand-wizard-app" / "public" / "brand_catalogs"


def humanize(s) -> str:
    return " ".join(w.capitalize() for w in str(s or "").split("_")) if s else ""


def book_from_plan(d: dict, stem: str) -> dict:
    parts = stem.split("__")  # brand, teacher, persona, topic, engine
    desc = d.get("description") or {}
    blurb = (desc.get("short_blurb") if isinstance(desc, dict) else "") or ""
    long_desc = (desc.get("long_description") if isinstance(desc, dict) else "") or blurb
    price = d.get("target_price") or {}
    kw = ((d.get("keywords") or {}).get("primary") or [])[:7]
    ap = d.get("author_positioning") or {}
    brand_prefix = stem.split("__")[0]
    book_id = (d.get("book_id") or stem).strip()
    return {
        "book_id": book_id,
        "file_stem": book_id,
        "title": (d.get("title") or "").strip(),
        "subtitle": (d.get("subtitle") or "").strip(),
        "desc": blurb.strip(),                                  # short blurb (list/cover)
        "long_desc": long_desc.strip(),                         # full store description
        "angle": (d.get("cover_tagline") or "").strip(),        # the marketing hook
        "cover": f"assets/covers/{brand_prefix}/{book_id}.png",
        "author": humanize(ap.get("byline_author")),            # public byline = pen name (matches cover; never the teacher / Sai Maa)
        "keywords": [str(k) for k in kw],
        "bisac": [str(c) for c in (d.get("bisac_codes") or [])][:3],
        "price": str(price.get("ebook_usd") or "4.99"),
        "audioPrice": str(price.get("audible_usd") or "9.99"),
        "paperbackPrice": str(price.get("paperback_usd") or ""),
        "isbn": str(d.get("isbn") or "").strip(),               # real ISBN if assigned (else blank → PENDING)
        "persona": parts[2] if len(parts) > 2 else "",
        "topic": parts[3] if len(parts) > 3 else "",
        "engine": d.get("engine") or (parts[4] if len(parts) > 4 else ""),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", default=None, help="only (re)generate this brand's catalog JSON")
    args = ap.parse_args()
    if not SRC.exists():
        raise SystemExit(f"book plans dir not found: {SRC}")
    OUTDIR.mkdir(parents=True, exist_ok=True)
    by_brand: dict[str, list] = defaultdict(list)
    skipped = 0
    glob_pat = f"{args.brand}__*.yaml" if args.brand else "*.yaml"
    for f in sorted(SRC.glob(glob_pat)):
        try:
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except Exception:
            skipped += 1
            continue
        if not isinstance(d, dict) or not d.get("title"):
            skipped += 1
            continue
        if d.get("_needs_authoring") is not False:
            skipped += 1  # authored-only: skip skeletons (true) + legacy orphans (field absent)
            continue
        brand = (d.get("author_positioning") or {}).get("brand") or f.name.split("__")[0]
        by_brand[brand].append(book_from_plan(d, f.stem))

    # Order by persona→topic→engine (NOT title): titles repeat across personas
    # (the subtitle carries the persona), so a title sort clusters duplicates into
    # one week. This interleaving keeps each weekly window varied + deterministic.
    for brand, books in sorted(by_brand.items()):
        titles = [b["title"] for b in books]
        subtitles = [b["subtitle"] for b in books]
        dup_t = {t: c for t, c in Counter(titles).items() if c > 1}
        dup_s = {t: c for t, c in Counter(subtitles).items() if c > 1}
        if brand == "way_stream_sanctuary" and (dup_t or dup_s):
            raise SystemExit(
                f"UNIQUENESS GUARD {brand}: duplicate titles={dup_t or 0} subtitles={dup_s or 0}"
            )
        books.sort(key=lambda b: (b["persona"], b["topic"], b["engine"], b["title"]))
        out = {"brand": brand, "count": len(books), "books": books}
        (OUTDIR / f"{brand}.json").write_text(
            json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"  {brand}: {len(books)} books -> brand_catalogs/{brand}.json")
    print(f"wrote {len(by_brand)} brand catalogs to {OUTDIR.relative_to(REPO)}"
          + (f" (skipped {skipped} unreadable/empty)" if skipped else ""))


main()
