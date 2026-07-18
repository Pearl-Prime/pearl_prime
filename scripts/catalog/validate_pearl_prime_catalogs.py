#!/usr/bin/env python3
"""
Pearl Prime book script catalog validator.

Reads the 4 locale CSVs in artifacts/catalog/pearl_prime_book_script_catalogs/
and produces a bestseller-readiness report covering:

  - Structural integrity (column count, locked-field literals, schema match)
  - Blocked vs ready breakdown
  - Top 10 strongest entries per market (by composite score in notes)
  - Title duplication / saturation
  - Weak / placeholder titles
  - Cross-locale market-fit check (do JP/TW/CN have locale-native titles?)

Pure analysis — no LLM calls, no row mutation.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

CATALOG_DIR = Path("artifacts/catalog/pearl_prime_book_script_catalogs")
LOCALES = ["en_US", "ja_JP", "zh_TW", "zh_CN"]

EXPECTED_COLS = [
    "locale", "market", "brand", "brand_locale_name", "title", "subtitle",
    "topic", "persona", "teacher_id", "teacher_mode", "runtime_format",
    "duration_band", "section_plan_id", "variant_pool_size",
    "bestseller_overlay_ref", "selection_strategy", "pipeline_route",
    "readiness_status", "required_source_atoms", "required_registry_topic",
    "output_target_path", "notes", "blockers",
]

LOCKED_FIELDS = {
    "section_plan_id": "pearl_prime_12x10x5",
    "variant_pool_size": "5",
    "bestseller_overlay_ref": "docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md",
    "selection_strategy": "deterministic_by_seed",
    "pipeline_route": "scripts/run_pipeline.py --pipeline-mode spine",
    "runtime_format": "standard_book",
    "duration_band": "standard",
}

COMPOSITE_RE = re.compile(r"composite=([\d.]+)")


def load_rows(locale: str) -> list[dict]:
    path = CATALOG_DIR / f"{locale}_catalog.csv"
    with open(path, "r", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def composite_of(row: dict) -> float | None:
    m = COMPOSITE_RE.search(row.get("notes", "") or "")
    return float(m.group(1)) if m else None


def has_cjk(s: str) -> bool:
    return any(
        "぀" <= ch <= "ヿ"  # hiragana + katakana
        or "一" <= ch <= "鿿"  # CJK unified
        or "가" <= ch <= "힯"  # hangul
        for ch in s
    )


def report() -> dict:
    out: dict[str, Any] = {"locales": {}, "global": {}}

    all_rows_by_locale: dict[str, list[dict]] = {}
    for locale in LOCALES:
        rows = load_rows(locale)
        all_rows_by_locale[locale] = rows

    # ── Per-locale ────────────────────────────────────────────────────────
    for locale, rows in all_rows_by_locale.items():
        locale_report: dict[str, Any] = {}
        locale_report["row_count"] = len(rows)

        # Status breakdown
        status = Counter(r["readiness_status"] for r in rows)
        locale_report["status_breakdown"] = dict(status)

        # Structural integrity
        struct_violations = []
        column_check = "OK"
        if rows:
            actual_cols = list(rows[0].keys())
            if actual_cols != EXPECTED_COLS:
                column_check = f"MISMATCH: expected {EXPECTED_COLS}, got {actual_cols}"

        violation_count_per_field = Counter()
        for r in rows:
            for field, expected in LOCKED_FIELDS.items():
                if r.get(field, "") != expected:
                    violation_count_per_field[field] += 1
        locale_report["column_check"] = column_check
        locale_report["locked_field_violations"] = dict(violation_count_per_field)

        # Brand count
        brands = sorted({r["brand"] for r in rows})
        locale_report["unique_brand_count"] = len(brands)
        locale_report["brands"] = brands

        # Top 10 strongest by composite
        scored = [(r, c) for r in rows if (c := composite_of(r)) is not None]
        scored.sort(key=lambda x: -x[1])
        top10 = []
        for r, c in scored[:10]:
            top10.append({
                "composite": c,
                "brand": r["brand"],
                "topic": r["topic"],
                "persona": r["persona"],
                "teacher": r["teacher_id"],
                "title": r.get("title") or "(blank)",
                "subtitle": r.get("subtitle") or "(blank)",
                "status": r["readiness_status"],
            })
        locale_report["top_10_strongest"] = top10

        # Title duplication
        title_counts = Counter(r["title"] for r in rows if r.get("title"))
        locale_report["distinct_titles"] = len(title_counts)
        locale_report["most_duplicated_titles"] = title_counts.most_common(10)

        # Title × subtitle duplication
        ts_counts = Counter(
            (r.get("title", ""), r.get("subtitle", ""))
            for r in rows if r.get("title")
        )
        locale_report["distinct_title_subtitle_pairs"] = len(ts_counts)
        locale_report["most_duplicated_title_subtitle"] = [
            {"title": t, "subtitle": s, "count": n}
            for (t, s), n in ts_counts.most_common(5)
        ]

        # Weak / placeholder titles
        blank_title_rows = sum(1 for r in rows if not r.get("title"))
        locale_report["blank_title_rows"] = blank_title_rows

        # Market-fit: does this locale carry locale-native titles?
        ready_rows = [r for r in rows if r["readiness_status"] == "ready"
                      and r.get("title")]
        cjk_titles = sum(1 for r in ready_rows if has_cjk(r["title"] or ""))
        locale_report["ready_rows_with_titles"] = len(ready_rows)
        locale_report["ready_rows_with_cjk_titles"] = cjk_titles
        locale_report["sample_ready_titles"] = [
            r["title"] for r in ready_rows[:5]
        ]

        # Distinct (topic, persona, teacher) per brand — differentiation
        brand_distinct_combos: dict[str, int] = {}
        for b in brands:
            combos = {(r["topic"], r["persona"], r["teacher_id"])
                      for r in rows if r["brand"] == b}
            brand_distinct_combos[b] = len(combos)
        locale_report["brand_distinct_topic_persona_teacher"] = brand_distinct_combos

        out["locales"][locale] = locale_report

    # ── Cross-locale market-fit check ────────────────────────────────────
    # Three distinct readiness levels per locale:
    #   spine_ready   = readiness_status == "ready" (renderer can produce a manuscript)
    #   title_ready   = title is non-blank (catalog has listing metadata)
    #   listing_ready = spine_ready AND title_ready AND title is locale-fit
    en_titles = {
        r["title"] for r in all_rows_by_locale["en_US"]
        if r["readiness_status"] == "ready" and r.get("title")
    }
    cross_locale = {}
    for locale in LOCALES:
        rows = all_rows_by_locale[locale]
        spine_ready = [r for r in rows if r["readiness_status"] == "ready"]
        with_title = [r for r in spine_ready if r.get("title")]
        verbatim_en = sum(1 for r in with_title if r["title"] in en_titles)
        cjk = sum(1 for r in with_title if has_cjk(r["title"] or ""))
        is_english_locale = locale == "en_US"
        listing_ready = with_title if is_english_locale else [r for r in with_title if has_cjk(r["title"] or "")]
        cross_locale[locale] = {
            "spine_ready": len(spine_ready),
            "title_ready": len(with_title),
            "listing_ready": len(listing_ready),
            "titles_verbatim_english": verbatim_en,
            "titles_with_cjk_chars": cjk,
            "spine_ready_without_title": len(spine_ready) - len(with_title),
        }
    out["global"]["cross_locale_market_fit"] = cross_locale

    # Top-10 launch-ready globally (highest composite, ready status)
    all_ready_scored = []
    for locale, rows in all_rows_by_locale.items():
        for r in rows:
            if r["readiness_status"] != "ready":
                continue
            c = composite_of(r)
            if c is None or not r.get("title"):
                continue
            all_ready_scored.append((c, locale, r))
    all_ready_scored.sort(key=lambda x: -x[0])
    out["global"]["top_50_launch_ready"] = [
        {"composite": c, "locale": loc, "brand": r["brand"], "topic": r["topic"],
         "persona": r["persona"], "teacher": r["teacher_id"],
         "title": r["title"], "subtitle": r.get("subtitle", "")}
        for c, loc, r in all_ready_scored[:50]
    ]

    return out


if __name__ == "__main__":
    report_dict = report()
    out_path = CATALOG_DIR / "validation_report.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report_dict, fh, indent=2, ensure_ascii=False)
    print(f"Wrote {out_path}")

    # Print human-readable summary
    print("\n=== STRUCTURAL INTEGRITY ===")
    for loc, rep in report_dict["locales"].items():
        v = rep["locked_field_violations"]
        col = rep["column_check"]
        print(f"  {loc}: column_check={col}, "
              f"locked_field_violations={'OK (none)' if not v else v}")

    print("\n=== STATUS BREAKDOWN ===")
    for loc, rep in report_dict["locales"].items():
        print(f"  {loc}: {rep['status_breakdown']}")

    print("\n=== UNIQUE TITLES ===")
    for loc, rep in report_dict["locales"].items():
        print(f"  {loc}: {rep['distinct_titles']} distinct titles, "
              f"{rep['distinct_title_subtitle_pairs']} distinct title+subtitle pairs, "
              f"{rep['blank_title_rows']} rows with blank title")

    print("\n=== CROSS-LOCALE READINESS LADDER ===")
    print("  (spine_ready = renderer can produce manuscript;")
    print("   title_ready = catalog has any title text;")
    print("   listing_ready = spine_ready AND has locale-fit title)")
    for loc, info in report_dict["global"]["cross_locale_market_fit"].items():
        print(f"  {loc}: spine_ready={info['spine_ready']}, "
              f"title_ready={info['title_ready']}, "
              f"listing_ready={info['listing_ready']}, "
              f"verbatim_english={info['titles_verbatim_english']}, "
              f"cjk_titles={info['titles_with_cjk_chars']}")

    print("\n=== TOP 10 STRONGEST PER LOCALE ===")
    for loc, rep in report_dict["locales"].items():
        print(f"\n  {loc}:")
        for i, e in enumerate(rep["top_10_strongest"], 1):
            print(f"    {i:2}. [{e['composite']:.2f}] {e['brand']:<22} "
                  f"{e['topic']:<22} → \"{e['title']}\" :: {e['subtitle']}")
