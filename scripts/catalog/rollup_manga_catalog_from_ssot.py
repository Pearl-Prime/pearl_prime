#!/usr/bin/env python3
"""
Manga Catalog Rollup — from the live SSOT (not the un-reconciled allocation matrix).
====================================================================================

Reads the live source-of-truth series plans at
``config/source_of_truth/manga_series_plans/<locale>/*.yaml`` (the 270/locale
set landed by the catalog reconciliation, specs/MANGA_CATALOG_RECONCILIATION_SPEC.md
Phase 2X.4, EXECUTED 2026-05) and rolls them up into a single human-readable view:

  - a flat catalog CSV (one row per series)
  - a machine-readable JSON summary (counts + title-fill status)
  - a grouped Markdown doc (per tier → brand → series)

This is a READ-ONLY reporter: it materializes a view of what already exists. It
does NOT generate, mutate, or delete any series/book plans, makes no LLM calls,
and renders nothing.

Why not reuse scripts/catalog/generate_manga_catalog.py?
  That generator materializes from config/manga/brand_genre_allocation.yaml — the
  *un-reconciled* allocation matrix the reconciliation spec explicitly left
  un-touched — and leaves series_title blank by policy. Its output (the stale
  artifacts/catalog/manga/ja_JP_manga_catalog.csv, 167 rows, old `healing` genre)
  predates and does NOT match the 270-series SSOT. This reporter reads the SSOT
  directly so the rollup reflects the live catalog.

Title state: as of the reconciliation, title/topic/manga_author are `TBD` across
the SSOT (synthesis is a separate, pending step — "Phase 2"). This reporter
surfaces that fill-state; it does not synthesize titles.

Usage:
  python3 scripts/catalog/rollup_manga_catalog_from_ssot.py --locale ja_JP
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import yaml

# ── Path resolution (matches sibling catalog scripts) ───────────────────────
REPO_ROOT = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
if not (REPO_ROOT / "config" / "manga").exists() and (_MAIN_REPO / "config" / "manga").exists():
    ROOT = _MAIN_REPO
else:
    ROOT = REPO_ROOT

SERIES_PLANS_ROOT = ROOT / "config" / "source_of_truth" / "manga_series_plans"
BOOK_PLANS_ROOT = ROOT / "config" / "source_of_truth" / "manga_book_plans"
CANONICAL_BRANDS = ROOT / "config" / "manga" / "canonical_brand_list.yaml"
SPEC_REF = "specs/MANGA_CATALOG_RECONCILIATION_SPEC.md"

TIER_ORDER = {"flagship": 0, "core": 1, "niche": 2}
TBD = "TBD"


def _load_yaml(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _series_index(series_id: str) -> str:
    """Trailing seriesNN token → 'NN' (e.g. ...__series03 → '03')."""
    tail = series_id.split("__")[-1]
    return tail.replace("series", "") if tail.startswith("series") else tail


def _is_filled(value: Any) -> bool:
    return bool(value) and str(value).strip().upper() != TBD


def load_brands() -> dict[str, dict]:
    data = _load_yaml(CANONICAL_BRANDS) or {}
    return data.get("brands", {})


def collect_series(locale: str, brands: dict[str, dict]) -> list[dict]:
    locale_dir = SERIES_PLANS_ROOT / locale
    if not locale_dir.is_dir():
        raise SystemExit(f"No series plans for locale {locale!r} at {locale_dir}")

    rows: list[dict] = []
    for path in sorted(locale_dir.glob("*.yaml")):
        sp = _load_yaml(path) or {}
        brand_id = sp.get("brand_id", "")
        binfo = brands.get(brand_id, {})
        series_id = sp.get("series_id", path.stem)
        localized = sp.get("localized_titles") or {}
        title = sp.get("title")
        rows.append(
            {
                "locale": sp.get("locale", locale),
                "tier": binfo.get("tier", ""),
                "brand_id": brand_id,
                "demographic": sp.get("demographic", binfo.get("demographic", "")),
                "genre": sp.get("genre", ""),
                "series_id": series_id,
                "series_index": _series_index(series_id),
                "title": title or "",
                "title_status": "filled" if _is_filled(title) else "TBD",
                "localized_title": localized.get(locale, "") or "",
                "topic": sp.get("topic", ""),
                "teacher_id": sp.get("teacher_id", ""),
                "manga_author": sp.get("manga_author", ""),
                "format": sp.get("format", ""),
                "master_format": sp.get("master_format", ""),
                "distribution_status": sp.get("distribution_status", ""),
                "locale_origin": sp.get("locale_origin", ""),
                "chapters_target": sp.get("chapters_target", ""),
                "ai_disclosure_required": sp.get("ai_disclosure_required", ""),
                "brand_primary_topic": binfo.get("primary_topic", ""),
                "brand_secondary_topics": "|".join(binfo.get("secondary_topics", []) or []),
                "target_platforms": "|".join(sp.get("target_platforms", []) or []),
                "_source": str(path.relative_to(ROOT)),
            }
        )
    return rows


CSV_COLUMNS = [
    "locale", "tier", "brand_id", "demographic", "genre", "series_id", "series_index",
    "title", "title_status", "localized_title", "topic", "teacher_id", "manga_author",
    "format", "master_format", "distribution_status", "locale_origin", "chapters_target",
    "ai_disclosure_required", "brand_primary_topic", "brand_secondary_topics",
    "target_platforms",
]


def _sort_key(r: dict) -> tuple:
    return (TIER_ORDER.get(r["tier"], 9), r["brand_id"], r["genre"], r["series_index"])


def write_csv(rows: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in sorted(rows, key=_sort_key):
            w.writerow(r)


def build_summary(locale: str, rows: list[dict], brands: dict[str, dict]) -> dict:
    by_brand = Counter(r["brand_id"] for r in rows)
    by_genre = Counter(r["genre"] for r in rows)
    by_tier = Counter(r["tier"] for r in rows)
    titled = sum(1 for r in rows if r["title_status"] == "filled")
    teacher_anchored = sum(
        1 for r in rows if r["teacher_id"] and r["teacher_id"] not in ("", "default_teacher")
    )
    book_plan_count = 0
    if BOOK_PLANS_ROOT.is_dir():
        book_plan_count = sum(
            1 for p in BOOK_PLANS_ROOT.glob(f"*__{locale}__*/*.yaml")
        )
    return {
        "locale": locale,
        "generated": date.today().isoformat(),
        "source": f"config/source_of_truth/manga_series_plans/{locale}/",
        "reconciliation_spec": SPEC_REF,
        "brands": len(by_brand),
        "canonical_brands": len(brands),
        "series_total": len(rows),
        "book_plan_installments": book_plan_count,
        "genres": len(by_genre),
        "title_fill": {"filled": titled, "tbd": len(rows) - titled},
        "topic_fill": {
            "filled": sum(1 for r in rows if _is_filled(r["topic"])),
            "tbd": sum(1 for r in rows if not _is_filled(r["topic"])),
        },
        "author_fill": {
            "filled": sum(1 for r in rows if _is_filled(r["manga_author"])),
            "tbd": sum(1 for r in rows if not _is_filled(r["manga_author"])),
        },
        "teacher_anchored": teacher_anchored,
        "by_tier": dict(by_tier),
        "by_genre": dict(by_genre.most_common()),
        "by_brand": dict(by_brand.most_common()),
    }


def write_json(summary: dict, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


LOCALE_LABEL = {
    "ja_JP": "ja_JP (Japan)", "en_US": "en_US (United States)",
    "zh_TW": "zh_TW (Taiwan)", "zh_CN": "zh_CN (China)", "ko_KR": "ko_KR (Korea)",
}


def _md_val(v: str) -> str:
    return f"_{TBD}_" if not _is_filled(v) else str(v)


def write_markdown(locale: str, rows: list[dict], summary: dict,
                   brands: dict[str, dict], out: Path) -> None:
    L: list[str] = []
    label = LOCALE_LABEL.get(locale, locale)
    L.append(f"# Manga Full Catalog Plan — {label}")
    L.append("")
    L.append("> **Auto-generated** by `scripts/catalog/rollup_manga_catalog_from_ssot.py` from the live")
    L.append(f"> SSOT (`config/source_of_truth/manga_series_plans/{locale}/`). Do not hand-edit — re-run the script.")
    L.append(f"> Reconciliation authority: `{SPEC_REF}` (Status: ✅ EXECUTED).")
    L.append(f"> Generated: {summary['generated']}")
    L.append("")
    L.append("## Summary")
    L.append("")
    tf = summary["title_fill"]
    L.append(f"- **Brands:** {summary['brands']} / {summary['canonical_brands']} canonical")
    L.append(f"- **Series:** {summary['series_total']}  ·  **Genres:** {summary['genres']}  ·  "
             f"**Book-plan installments:** {summary['book_plan_installments']:,}")
    L.append(f"- **Title synthesis:** {tf['filled']} / {summary['series_total']} titled "
             f"(**{tf['tbd']} `TBD`**) — Phase 2 (title/topic/author synthesis) pending")
    L.append(f"- **Teacher-anchored series:** {summary['teacher_anchored']} / {summary['series_total']}")
    L.append("")
    L.append("### Series by tier")
    L.append("")
    L.append("| tier | series |")
    L.append("|---|---|")
    for tier in ("flagship", "core", "niche"):
        if tier in summary["by_tier"]:
            L.append(f"| {tier} | {summary['by_tier'][tier]} |")
    L.append("")
    L.append("### Series by genre")
    L.append("")
    L.append("| genre | series |")
    L.append("|---|---|")
    for genre, n in summary["by_genre"].items():
        L.append(f"| {genre} | {n} |")
    L.append("")

    # Group rows by tier → brand
    by_brand_rows: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_brand_rows[r["brand_id"]].append(r)

    brand_order = sorted(
        by_brand_rows.keys(),
        key=lambda b: (TIER_ORDER.get(brands.get(b, {}).get("tier", ""), 9), b),
    )

    current_tier = None
    for brand_id in brand_order:
        binfo = brands.get(brand_id, {})
        tier = binfo.get("tier", "")
        if tier != current_tier:
            current_tier = tier
            L.append("")
            L.append(f"## {tier.capitalize()} brands")
        brand_rows = sorted(by_brand_rows[brand_id], key=_sort_key)
        notes = binfo.get("notes", "")
        demo = binfo.get("demographic", "")
        L.append("")
        L.append(f"### {brand_id} — {demo}" + (f" · {notes}" if notes else ""))
        prim = binfo.get("primary_topic", "")
        sec = ", ".join(binfo.get("secondary_topics", []) or [])
        L.append(f"*primary:* `{prim}`  ·  *secondary:* {sec}  ·  *series:* {len(brand_rows)}")
        L.append("")
        L.append("| # | genre | series_id | title | topic | teacher |")
        L.append("|---|---|---|---|---|---|")
        for r in brand_rows:
            L.append(
                f"| {r['series_index']} | {r['genre']} | `{r['series_id']}` | "
                f"{_md_val(r['title'])} | {_md_val(r['topic'])} | {r['teacher_id'] or '—'} |"
            )
    L.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--locale", default="ja_JP", help="Locale to roll up (default: ja_JP)")
    ap.add_argument("--out-dir", default="artifacts/catalog/manga/ssot_rollup",
                    help="Directory for CSV + JSON summary")
    ap.add_argument("--docs-dir", default="docs/manga",
                    help="Directory for the human-readable Markdown doc")
    args = ap.parse_args()

    locale = args.locale
    brands = load_brands()
    rows = collect_series(locale, brands)
    summary = build_summary(locale, rows, brands)

    out_dir = ROOT / args.out_dir
    docs_dir = ROOT / args.docs_dir
    csv_path = out_dir / f"{locale}_manga_catalog_ssot.csv"
    json_path = out_dir / f"{locale}_manga_catalog_ssot.summary.json"
    md_path = docs_dir / f"MANGA_FULL_CATALOG_PLAN_{locale}.md"

    write_csv(rows, csv_path)
    write_json(summary, json_path)
    write_markdown(locale, rows, summary, brands, md_path)

    print(f"[{locale}] series={summary['series_total']} brands={summary['brands']} "
          f"genres={summary['genres']} titled={summary['title_fill']['filled']} "
          f"tbd={summary['title_fill']['tbd']} book_plans={summary['book_plan_installments']}")
    print(f"  CSV : {csv_path.relative_to(ROOT)}")
    print(f"  JSON: {json_path.relative_to(ROOT)}")
    print(f"  DOC : {md_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
