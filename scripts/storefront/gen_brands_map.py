#!/usr/bin/env python3
"""Emit a small brand_id -> localized display-label map for the storefront chip
rail and cards (storefront/public/app/brands.json).

Source = each locale's book catalog CSV (`brand`, `brand_locale_name`). The D1
`sku` table intentionally does not store the brand label, and the catalog API
returns only `sku` columns, so the frontend localizes brand names from this tiny
static map (works in both the D1 path and the sample fallback). Regenerate when
brands or locale names change. Pure stdlib.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BOOK = REPO / "artifacts/catalog/pearl_prime_book_script_catalogs/{loc}_catalog.csv"
LOCALES = {"en-US": "en_US", "ja-JP": "ja_JP", "zh-TW": "zh_TW", "zh-CN": "zh_CN"}
OUT = REPO / "storefront/public/app/brands.json"


def main():
    out = {}
    for hyphen, us in LOCALES.items():
        path = Path(str(BOOK).format(loc=us))
        if not path.exists():
            continue
        labels = {}
        with path.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                brand = (row.get("brand") or "").strip()
                label = (row.get("brand_locale_name") or "").strip()
                if brand and label and brand not in labels:
                    labels[brand] = label
        if labels:
            out[hyphen] = labels
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"brands.json -> {OUT}: {sum(len(v) for v in out.values())} labels across {list(out)}")


if __name__ == "__main__":
    main()
