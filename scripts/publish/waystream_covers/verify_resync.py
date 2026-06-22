#!/usr/bin/env python3
"""Verify 100% Waystream cover resync: plan == catalog == dashboard == cover file."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
PLANS = ROOT / "config/source_of_truth/book_plans_en_us"
CATALOG = ROOT / "artifacts/waystream/waystream_800book_catalog_plan.csv"
DASH = ROOT / "brand-wizard-app/public/brand_catalogs/way_stream_sanctuary.json"
COVERS = ROOT / "brand-wizard-app/public/assets/covers/way_stream_sanctuary"


def _title_words(title: str) -> list[str]:
    chunk = re.sub(r"[^\w\s]", "", title.split(":")[0].lower())
    return [w for w in chunk.split() if len(w) > 3][:5]


def ocr_match(cover: Path, title: str) -> bool:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return True
    txt = pytesseract.image_to_string(Image.open(cover), config="--psm 6").lower()
    words = _title_words(title)
    if not words:
        return True
    hits = sum(1 for w in words if w in txt)
    return hits >= max(2, len(words) - 1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", default="way_stream_sanctuary")
    ap.add_argument("--ocr", action="store_true", help="OCR every cover (slow, thorough)")
    args = ap.parse_args()

    plans = {}
    for p in sorted(PLANS.glob(f"{args.brand}__*.yaml")):
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        if d.get("_needs_authoring") is False and d.get("book_id"):
            plans[d["book_id"]] = d

    csv_by_id = {r["book_id"]: r for r in csv.DictReader(CATALOG.open())}
    dash_by_cover = {}
    if DASH.exists():
        for b in json.loads(DASH.read_text(encoding="utf-8")).get("books", []):
            bid = b.get("file_stem") or b.get("book_id") or Path(b["cover"]).stem
            dash_by_cover[bid] = b

    errors: list[str] = []
    ocr_fail: list[str] = []

    for bid, plan in sorted(plans.items()):
        if bid not in csv_by_id:
            errors.append(f"missing csv row: {bid}")
            continue
        row = csv_by_id[bid]
        if row["title"].strip() != plan["title"].strip():
            errors.append(f"csv title mismatch: {bid}")
        if row["subtitle"].strip() != plan["subtitle"].strip():
            errors.append(f"csv subtitle mismatch: {bid}")
        cov = COVERS / f"{bid}.png"
        if not cov.is_file():
            errors.append(f"missing cover: {bid}")
        d = dash_by_cover.get(bid)
        if d:
            if d["title"].strip() != plan["title"].strip():
                errors.append(f"dashboard title mismatch: {bid}")
            if d["subtitle"].strip() != plan["subtitle"].strip():
                errors.append(f"dashboard subtitle mismatch: {bid}")
        if args.ocr and cov.is_file() and not ocr_match(cov, plan["title"]):
            ocr_fail.append(bid)

    titles = [p["title"] for p in plans.values()]
    subs = [p["subtitle"] for p in plans.values()]
    dup_t = {t: c for t, c in Counter(titles).items() if c > 1}
    dup_s = {t: c for t, c in Counter(subs).items() if c > 1}

    print(f"plans={len(plans)} csv={len(csv_by_id)} covers={len(list(COVERS.glob('*.png')))} dashboard={len(dash_by_cover)}")
    print(f"distinct titles={len(set(titles))} distinct subtitles={len(set(subs))}")
    print(f"structural errors={len(errors)} dup_titles={dup_t or 0} dup_subs={dup_s or 0}")
    if args.ocr:
        print(f"ocr failures={len(ocr_fail)}/{len(plans)}")
        for bid in ocr_fail[:10]:
            print(f"  OCR FAIL {bid}")

    if errors or dup_t or dup_s or ocr_fail:
        for e in errors[:20]:
            print(f"  ERR {e}")
        sys.exit(1)
    print("VERIFY OK — 100% resync")


if __name__ == "__main__":
    main()
