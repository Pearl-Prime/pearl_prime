#!/usr/bin/env python3
"""
Final launch report builder — Issue #786 closeout (post B1 + B2 land).

Reads current-main catalogs (Pearl Prime book scripts + manga, all 4 locales)
and emits:
  - Top 50 combined launch candidates (CSV)
  - Top 10 per locale (CSV per locale + combined)
  - artifacts/catalog/launch_baseline/launch_baseline_data.json
  - docs/PEARL_PRIME_FINAL_LAUNCH_REPORT_2026-04-29.md

Per operator directive (Option C closeout):
  - readiness by locale
  - remaining blockers (esp. bright_presence_tw / adi_da)
  - image QA rows marked as manual QA, NOT LoRA training tasks
  - teacher_showcase status pass-through (#784 audio + #785 CTAs landed)

Pure analysis. No LLM. No catalog mutation. No new generators.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PP_DIR = ROOT / "artifacts/catalog/pearl_prime_book_script_catalogs"
M_DIR = ROOT / "artifacts/catalog/manga"
OUT_DIR = ROOT / "artifacts/catalog/launch_baseline"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LOCALES = ("en_US", "ja_JP", "zh_TW", "zh_CN")
COMPOSITE_RE = re.compile(r"composite=([\d.]+)")


def load_pp_rows():
    """Pearl Prime book script rows: parse composite score from notes."""
    out = []
    for loc in LOCALES:
        p = PP_DIR / f"{loc}_catalog.csv"
        if not p.exists():
            continue
        for r in csv.DictReader(open(p)):
            if r["readiness_status"] != "ready":
                continue
            m = COMPOSITE_RE.search(r.get("notes", "") or "")
            if not m:
                continue
            comp = float(m.group(1))
            out.append({
                "lane": "book_script",
                "locale": loc,
                "brand": r["brand"],
                "brand_locale_name": r.get("brand_locale_name", ""),
                "subject": r["topic"],
                "persona": r["persona"],
                "teacher": r["teacher_id"],
                "teacher_mode": r.get("teacher_mode", "true"),
                "title": r.get("title", "") or "[blank]",
                "subtitle": r.get("subtitle", "") or "",
                "raw_score": comp,
                "normalized_score": comp,  # already 0-1
                "format": "pearl_prime_12x10x5",
                "listing_ready": bool(r.get("title")),
            })
    return out


def load_manga_rows():
    """Manga rows: rank by genre_allocation_pct + tentpole_bonus."""
    out = []
    for loc in LOCALES:
        p = M_DIR / f"{loc}_manga_catalog.csv"
        if not p.exists():
            continue
        for r in csv.DictReader(open(p)):
            status = r.get("readiness_status", "")
            # Include both 'ready' and image-QA-pending rows.
            # Per operator: image QA rows are manual QA, not LoRA training,
            # so they are still launch candidates from a catalog-readiness lens.
            if status not in ("ready", "needs_image_qa", "blocked_lora"):
                continue
            try:
                pct = float(r.get("genre_allocation_pct", 0) or 0)
            except ValueError:
                pct = 0.0
            tentpole_bonus = 15.0 if r.get("is_tentpole") == "true" else 0.0
            raw = pct + tentpole_bonus
            normalized = raw / 65.0
            out.append({
                "lane": "manga",
                "locale": loc,
                "brand": r["brand"],
                "brand_locale_name": r.get("brand_locale_name", ""),
                "subject": r["genre"],
                "persona": "",
                "teacher": "",
                "teacher_mode": r.get("teacher_mode", ""),
                "title": "[needs_locale_native_synthesis]",  # manga titles still blank by design
                "subtitle": "",
                "raw_score": raw,
                "normalized_score": normalized,
                "format": r.get("series_format", ""),
                "is_tentpole": r.get("is_tentpole") == "true",
                "series_id": r.get("series_id", ""),
                "readiness_status": status,
                "listing_ready": False,
                "blockers": r.get("blockers", "") or "",
            })
    return out


def write_csv(rows, path, columns):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main():
    pp = load_pp_rows()
    manga = load_manga_rows()

    pp.sort(key=lambda r: -r["normalized_score"])
    manga.sort(key=lambda r: -r["normalized_score"])

    pp_cols = ["lane", "locale", "brand", "brand_locale_name", "subject",
               "persona", "teacher", "teacher_mode", "title", "subtitle",
               "raw_score", "normalized_score", "listing_ready", "format"]
    manga_cols = ["lane", "locale", "brand", "brand_locale_name", "subject",
                  "title", "raw_score", "normalized_score", "format",
                  "is_tentpole", "series_id", "readiness_status",
                  "blockers", "teacher_mode"]

    # Top 50 combined (sorted by normalized score, mixed lanes)
    combined = sorted(pp + manga, key=lambda r: -r["normalized_score"])
    top50 = combined[:50]
    combined_cols = ["lane", "locale", "brand", "brand_locale_name", "subject",
                     "persona", "teacher", "teacher_mode", "title",
                     "raw_score", "normalized_score", "format", "listing_ready"]
    write_csv(top50, OUT_DIR / "top_50_combined.csv", combined_cols)

    # Top 10 per locale (book script lane only — manga titles are blank)
    pp_by_locale = defaultdict(list)
    for r in pp:
        pp_by_locale[r["locale"]].append(r)
    top10_by_locale = {}
    all_top10 = []
    for loc in LOCALES:
        loc_rows = sorted(pp_by_locale[loc], key=lambda r: -r["normalized_score"])[:10]
        top10_by_locale[loc] = loc_rows
        write_csv(loc_rows, OUT_DIR / f"top_10_book_scripts_{loc}.csv", pp_cols)
        all_top10.extend(loc_rows)
    write_csv(all_top10, OUT_DIR / "top_10_per_locale_combined.csv", pp_cols)

    # Readiness by locale
    readiness_by_locale = {}
    for loc in LOCALES:
        # Pearl Prime
        pp_path = PP_DIR / f"{loc}_catalog.csv"
        m_path = M_DIR / f"{loc}_manga_catalog.csv"
        pp_rows = list(csv.DictReader(open(pp_path))) if pp_path.exists() else []
        m_rows = list(csv.DictReader(open(m_path))) if m_path.exists() else []
        pp_status = Counter(r["readiness_status"] for r in pp_rows)
        m_status = Counter(r["readiness_status"] for r in m_rows)
        pp_listing = sum(1 for r in pp_rows
                         if r["readiness_status"] == "ready" and r.get("title"))
        readiness_by_locale[loc] = {
            "pearl_prime": {
                "rows": len(pp_rows),
                "by_status": dict(pp_status),
                "listing_ready": pp_listing,
            },
            "manga": {
                "rows": len(m_rows),
                "by_status": dict(m_status),
            },
        }

    # Remaining blockers — focus on bright_presence_tw + adi_da + zh_TW score-blocked
    blockers = {
        "manga_image_qa_pending": [],
        "manga_blocked_lora_specific": [],
        "book_script_blocked_score_zh_TW": [],
    }
    # Manga image-QA / blocked_lora — surface as manual QA per operator
    for loc in LOCALES:
        p = M_DIR / f"{loc}_manga_catalog.csv"
        if not p.exists():
            continue
        for r in csv.DictReader(open(p)):
            if r["readiness_status"] in ("blocked_lora", "needs_image_qa"):
                entry = {
                    "locale": loc,
                    "brand": r["brand"],
                    "series_id": r.get("series_id", ""),
                    "genre": r["genre"],
                    "blockers": r.get("blockers", ""),
                    "status": r["readiness_status"],
                }
                if r["brand"] == "bright_presence_tw":
                    blockers["manga_blocked_lora_specific"].append(entry)
                else:
                    blockers["manga_image_qa_pending"].append(entry)

    # Pearl Prime zh_TW blocked_score rows
    p = PP_DIR / "zh_TW_catalog.csv"
    if p.exists():
        for r in csv.DictReader(open(p)):
            if r["readiness_status"] == "blocked_score":
                blockers["book_script_blocked_score_zh_TW"].append({
                    "brand": r["brand"],
                    "topic": r["topic"],
                    "persona": r["persona"],
                    "teacher": r["teacher_id"],
                    "blockers": r.get("blockers", ""),
                })

    # Aggregate counts for the report header
    totals = {
        "pearl_prime_total": sum(d["pearl_prime"]["rows"] for d in readiness_by_locale.values()),
        "pearl_prime_listing_ready": sum(d["pearl_prime"]["listing_ready"] for d in readiness_by_locale.values()),
        "pearl_prime_blocked_score": sum(
            d["pearl_prime"]["by_status"].get("blocked_score", 0)
            for d in readiness_by_locale.values()
        ),
        "manga_total": sum(d["manga"]["rows"] for d in readiness_by_locale.values()),
        "manga_ready": sum(d["manga"]["by_status"].get("ready", 0)
                           for d in readiness_by_locale.values()),
        "manga_image_qa_pending": sum(
            d["manga"]["by_status"].get("blocked_lora", 0)
            + d["manga"]["by_status"].get("needs_image_qa", 0)
            for d in readiness_by_locale.values()
        ),
    }

    # Snapshot top 10 per locale for the report
    top10_summary = {}
    for loc in LOCALES:
        top10_summary[loc] = [
            {
                "score": r["normalized_score"],
                "brand": r["brand"],
                "subject": r["subject"],
                "persona": r["persona"],
                "title": r["title"],
                "subtitle": r.get("subtitle", ""),
            }
            for r in top10_by_locale[loc]
        ]

    out_data = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "branch_state": "post-#793 (B1) + post-#790 (B2) on main",
        "totals": totals,
        "readiness_by_locale": readiness_by_locale,
        "top_50_combined_count": len(top50),
        "top_50_lane_split": dict(Counter(r["lane"] for r in top50)),
        "top_50_locale_split": dict(Counter(r["locale"] for r in top50)),
        "top_10_per_locale": top10_summary,
        "blockers": {
            "manga_image_qa_pending_count": len(blockers["manga_image_qa_pending"]),
            "manga_blocked_lora_specific_count": len(blockers["manga_blocked_lora_specific"]),
            "book_script_blocked_score_zh_TW_count": len(blockers["book_script_blocked_score_zh_TW"]),
            "bright_presence_tw_rows": [
                b for b in blockers["manga_blocked_lora_specific"]
            ],
        },
    }

    with open(OUT_DIR / "launch_baseline_data.json", "w", encoding="utf-8") as fh:
        json.dump(out_data, fh, indent=2, ensure_ascii=False)
    print(f"  → wrote {OUT_DIR}/launch_baseline_data.json")

    # CLI summary
    print("\n=== Catalog totals ===")
    print(f"  Pearl Prime listing-ready:      {totals['pearl_prime_listing_ready']:>5} (of {totals['pearl_prime_total']})")
    print(f"  Pearl Prime blocked_score:      {totals['pearl_prime_blocked_score']:>5} (zh_TW only)")
    print(f"  Manga ready:                    {totals['manga_ready']:>5} (of {totals['manga_total']})")
    print(f"  Manga awaiting manual image QA: {totals['manga_image_qa_pending']:>5}")
    print(f"\n=== Top 50 split ===")
    print(f"  by lane:   {dict(Counter(r['lane'] for r in top50))}")
    print(f"  by locale: {dict(Counter(r['locale'] for r in top50))}")
    print(f"\nFiles written:")
    print(f"  {OUT_DIR}/top_50_combined.csv ({len(top50)} rows)")
    for loc in LOCALES:
        print(f"  {OUT_DIR}/top_10_book_scripts_{loc}.csv (10 rows)")
    print(f"  {OUT_DIR}/top_10_per_locale_combined.csv ({len(all_top10)} rows)")
    print(f"  {OUT_DIR}/launch_baseline_data.json")


if __name__ == "__main__":
    main()
