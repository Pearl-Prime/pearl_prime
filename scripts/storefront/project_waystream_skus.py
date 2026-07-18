#!/usr/bin/env python3
"""Project Waystream Sanctuary EPUBs into the Pearl Prime storefront sample catalog.

Reads brand metadata (brand_catalogs/way_stream_sanctuary.json) and delivery
paths (brand_deliveries/way_stream_sanctuary.json after gen_brand_deliveries.py).
Writes storefront/public/app/sample_catalog.way_stream_sanctuary.en-US.json so
the static storefront (api.js sample fallback) lists every rendered EPUB.

Pure stdlib + PyYAML. No paid LLM APIs.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BRAND = "way_stream_sanctuary"
CATALOG = REPO / "brand-wizard-app/public/brand_catalogs/way_stream_sanctuary.json"
DELIVERIES = REPO / "brand-wizard-app/public/brand_deliveries/way_stream_sanctuary.json"
OUT = REPO / "storefront/public/app/sample_catalog.way_stream_sanctuary.en-US.json"
BRAND_ADMIN_BASE = "https://brand-admin-onboarding-bu2.pages.dev"
PRICE_CENTS = 499


def _parse_book_id(book_id: str) -> dict[str, str | None]:
    parts = book_id.split("__")
    out = {
        "teacher": None,
        "persona": None,
        "topic": None,
        "angle": None,
        "runtime_suffix": None,
    }
    if len(parts) < 5:
        return out
    out["teacher"] = parts[1]
    out["persona"] = parts[2]
    out["topic"] = parts[3]
    if parts[-1] == "1hr":
        out["runtime_suffix"] = "1hr"
        out["angle"] = parts[4] if len(parts) > 5 else parts[4]
    else:
        out["angle"] = parts[4]
    return out


def _sku_id(meta: dict) -> str:
    inner = "__".join(
        x
        for x in (
            meta["topic"],
            meta["persona"],
            meta["teacher"],
            meta["angle"],
            meta["runtime_suffix"],
        )
        if x
    )
    inner = re.sub(r"[^a-z0-9_]+", "_", inner.lower())
    return f"book_en_US_{BRAND}_{inner}"


def _delivery_index() -> dict[str, str]:
    """book_id (stem) -> public delivery URL path (no domain)."""
    if not DELIVERIES.is_file():
        return {}
    feed = json.loads(DELIVERIES.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for _week, plats in (feed.get("weeks") or {}).items():
        for _plat, files in plats.items():
            for entry in files or []:
                fname = entry.get("file") or ""
                if not fname.endswith(".epub"):
                    continue
                out[Path(fname).stem] = entry.get("url") or ""
    return out


def project(*, require_deliveries: bool = True) -> list[dict]:
    if not CATALOG.is_file():
        raise SystemExit(f"missing catalog: {CATALOG}")
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    books = cat.get("books") or []
    durls = _delivery_index()
    if require_deliveries and not durls:
        raise SystemExit(
            f"no delivery feed at {DELIVERIES.relative_to(REPO)} — run gen_brand_deliveries.py first"
        )

    rows: list[dict] = []
    for b in books:
        book_id = b.get("book_id") or b.get("file_stem") or ""
        if not book_id:
            continue
        if book_id not in durls:
            continue
        meta = _parse_book_id(book_id)
        sku_id = _sku_id(meta)
        rel = durls[book_id]
        if rel.startswith("http://") or rel.startswith("https://"):
            asset_url = rel
        else:
            asset_url = f"{BRAND_ADMIN_BASE}/{rel.lstrip('/')}" if rel else ""
        cover_rel = f"assets/covers/{BRAND}/{book_id}.png"
        rows.append(
            {
                "sku_id": sku_id,
                "locale": "en-US",
                "brand_id": BRAND,
                "product_type": "book",
                "sub_type": "one_hour_book" if meta["runtime_suffix"] == "1hr" else "standard_book",
                "topic": meta["topic"],
                "persona": meta["persona"],
                "series_id": None,
                "title": b.get("title") or book_id,
                "subtitle": b.get("subtitle") or "",
                "description": (b.get("desc") or "")[:500] or None,
                "cover_url": f"{BRAND_ADMIN_BASE}/{cover_rel}",
                "preview_url": None,
                "asset_url": asset_url,
                "price_cents": PRICE_CENTS,
                "currency": "USD",
                "status": "live",
                "bundle_id": None,
                "upstream_path": f"artifacts/weekly_packages/{BRAND}/",
                "created_at": 0,
                "updated_at": 0,
                "brand_label": "Waystream Sanctuary",
                "book_id": book_id,
            }
        )
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--allow-empty",
        action="store_true",
        help="write [] when deliveries feed is missing (for dry checks)",
    )
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument(
        "--allow-shrink",
        action="store_true",
        help="permit overwriting the catalog with fewer SKUs than it currently has",
    )
    args = ap.parse_args()
    try:
        rows = project(require_deliveries=not args.allow_empty)
    except SystemExit as exc:
        if args.allow_empty:
            rows = []
        else:
            raise exc
    # Shrink-guard: this is a FULL REGEN of the sample catalog, keyed on the books present
    # in the (just-regenerated) delivery feed. Running it after a partial local build silently
    # rewrites the tracked catalog down to that subset (153 -> 18 already happened once).
    # Refuse to overwrite a tracked catalog with fewer SKUs unless explicitly overridden;
    # only run the unguarded regen in the full-tree CI context.
    allow_shrink = args.allow_shrink or os.environ.get("WAYSTREAM_SKUS_ALLOW_SHRINK") == "1"
    if args.out.is_file() and not allow_shrink and not args.allow_empty:
        try:
            prev = json.loads(args.out.read_text(encoding="utf-8"))
            prev_count = len(prev) if isinstance(prev, list) else 0
        except (json.JSONDecodeError, OSError):
            prev_count = 0
        if len(rows) < prev_count:
            raise SystemExit(
                f"SHRINK-GUARD: {args.out.name} would drop from {prev_count} -> {len(rows)} SKUs. "
                f"This is a FULL REGEN keyed on the delivery feed — you are almost certainly "
                f"running it after a partial local build (build the full tree first, or run in "
                f"the full-tree CI context). To intentionally shrink, set "
                f"WAYSTREAM_SKUS_ALLOW_SHRINK=1.")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} waystream SKUs -> {args.out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
