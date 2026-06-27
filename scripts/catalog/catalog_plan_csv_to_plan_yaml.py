#!/usr/bin/env python3
"""Import Waystream-style catalog plan CSV → book_plans_<locale> + series_plans_<locale> YAML.

CSV columns (header required):
  book_id, title, subtitle, author, installment, topic, engine, persona, cluster

Provenance: mirrors artifacts/waystream/waystream_800book_catalog_plan.csv → YAML path used
for the 800-book Waystream flagship (see project_all_catalogs_program memory).

  PYTHONPATH=. python3 scripts/catalog/catalog_plan_csv_to_plan_yaml.py \\
    --csv artifacts/waystream/waystream_800book_catalog_plan.csv --dry-run --limit 10

  PYTHONPATH=. python3 scripts/catalog/catalog_plan_csv_to_plan_yaml.py \\
    --csv artifacts/catalog/stillness_press_800_catalog_plan.csv --brand stillness_press
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

import yaml

from scripts.catalog.gen_plan_skeletons import ASSIGN, topic_bisac
from scripts.catalog.locale_paths import normalize_lane_id, plan_dirs
from phoenix_v4.planning.author_brand_resolver import resolve_author_from_brand

ROOT = Path(__file__).resolve().parents[2]
ARCS = ROOT / "config/source_of_truth/master_arcs"
REG = ROOT / "config/brand_management/global_brand_registry_unified.yaml"


def _load_brand_teacher(brand_archetype: str, lane_id: str) -> str:
    reg = yaml.safe_load(REG.read_text())["brands"]
    for rec in reg.values():
        if rec.get("brand_archetype_id") == brand_archetype and rec.get("lane_id") == lane_id:
            return rec.get("teacher_id") or "house"
    return "default_teacher"


def _parse_book_id(book_id: str) -> dict:
    """Parse brand__teacher__persona__topic__engine[__1hr] ids."""
    is_1hr = book_id.endswith("__1hr")
    stem = book_id[:-5] if is_1hr else book_id
    parts = stem.split("__")
    if len(parts) < 5:
        raise ValueError(f"book_id needs ≥5 segments: {book_id}")
    brand, teacher, persona, topic = parts[0], parts[1], parts[2], parts[3]
    engine = parts[4]
    return {
        "brand": brand,
        "teacher": teacher,
        "persona": persona,
        "topic": topic,
        "engine": engine,
        "is_1hr": is_1hr,
        "series_id": f"{brand}__{teacher}__{persona}__{topic}",
    }


def _master_arc(persona: str, topic: str, engine: str) -> tuple[str | None, str]:
    """Return (relative master_arc path, structural_format_id)."""
    for fmt in ("F006", "F005", "F004", "F003"):
        p = ARCS / f"{persona}__{topic}__{engine}__{fmt}.yaml"
        if p.exists():
            return str(p.relative_to(ROOT)), fmt
    return None, "F006"


def _duration(is_1hr: bool) -> tuple[str, str]:
    if is_1hr:
        return "one_hour_book", "one_hour_book"
    return "standard_book_60min", "standard_book_60min"


def _author_slug(display_name: str) -> str:
  """Map CSV display author to pen-name slug when possible."""
  if not display_name or not display_name.strip():
    return ""
  return display_name.strip().lower().replace(" ", "_")


def _rows_from_csv(csv_path: Path, brand_filter: str | None) -> list[dict]:
    rows = []
    with csv_path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if brand_filter:
                parsed = _parse_book_id(row["book_id"])
                if parsed["brand"] != brand_filter:
                    continue
            rows.append(row)
    return rows


def _group_series(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        parsed = _parse_book_id(row["book_id"])
        grouped[parsed["series_id"]].append(row)
    for sid in grouped:
        grouped[sid].sort(key=lambda r: (int(r.get("installment") or 0), r["book_id"]))
    return grouped


def _build_series_plan(
    series_id: str,
    book_rows: list[dict],
    *,
    plan_source: str,
    teacher_raw: str | None,
    lane_id: str,
) -> dict:
    first = _parse_book_id(book_rows[0]["book_id"])
    brand, persona, topic = first["brand"], first["persona"], first["topic"]
    teacher_yaml = None if teacher_raw in (None, "house", "default_teacher") else teacher_raw
    byline = _author_slug(book_rows[0].get("author", "")) or resolve_author_from_brand(
        brand_id=brand, topic_id=topic, persona_id=persona, assignments_path=ASSIGN
    )
    arc: dict = {}
    for i, row in enumerate(book_rows, start=1):
        p = _parse_book_id(row["book_id"])
        arc_path, _fmt = _master_arc(p["persona"], p["topic"], p["engine"])
        dur, _ = _duration(p["is_1hr"])
        entry = {
            "book_id": row["book_id"],
            "engine": p["engine"],
            "duration": dur,
        }
        if arc_path:
            entry["master_arc"] = arc_path
        arc[f"installment_{i}"] = entry
    return {
        "series_plan_schema": "1.0.0",
        "created_at": str(date.today()),
        "locale": lane_id,
        "book_id_prefix": series_id,
        "brand": brand,
        "teacher": teacher_yaml,
        "persona": persona,
        "topic": topic,
        "arc": arc,
        "reader_promise_family": "",
        "bestseller_hook_family": "",
        "emotional_engine": f"{topic}_recognition",
        "comp_series": [],
        "platform_strategy": {
            "primary": ["kdp_ebook", "audible"],
            "secondary": ["apple_books", "google_play", "spotify_audiobooks"],
            "launch_platform": "kdp_ebook",
            "cadence": {"release_spacing_days": 14, "max_books_per_brand_per_month": 2},
        },
        "reader_avatar": {"age": "", "where_they_are": "", "what_they_need": "", "what_they_avoid": ""},
        "series_voice_markers": {
            "register": "",
            "sentence_rhythm": "",
            "metaphor_family": "",
            "second_person_default": True,
        },
        "plan_source_path": plan_source,
        "_needs_authoring": True,
    }


def _build_book_plan(
    row: dict,
    series_rel: str,
    *,
    plan_source: str,
    teacher_raw: str | None,
) -> dict:
    p = _parse_book_id(row["book_id"])
    dur, runtime = _duration(p["is_1hr"])
    _, fmt = _master_arc(p["persona"], p["topic"], p["engine"])
    byline = _author_slug(row.get("author", "")) or resolve_author_from_brand(
        brand_id=p["brand"], topic_id=p["topic"], persona_id=p["persona"], assignments_path=ASSIGN
    )
    teacher_yaml = None if teacher_raw in (None, "house", "default_teacher") else teacher_raw
    return {
        "book_plan_schema": "1.0.0",
        "created_at": str(date.today()),
        "book_id": row["book_id"],
        "series_plan": series_rel,
        "installment_number": int(row.get("installment") or 1),
        "engine": p["engine"],
        "duration": dur,
        "runtime_format_id": runtime,
        "structural_format_id": fmt,
        "target_word_range": [9000, 12000],
        "target_audio_minutes": 70 if not p["is_1hr"] else 60,
        "title": (row.get("title") or "").strip(),
        "subtitle": (row.get("subtitle") or "").strip(),
        "cover_tagline": "",
        "description": {"short_blurb": "", "long_description": ""},
        "keywords": {"primary": [], "secondary": []},
        "bisac_codes": topic_bisac(p["topic"]),
        "target_price": {"ebook_usd": 4.99, "audible_usd": 9.99, "paperback_usd": 12.99},
        "author_positioning": {
            "teacher": teacher_yaml,
            "brand": p["brand"],
            "byline_author": byline,
        },
        "comp_titles": [],
        "plan_source_path": plan_source,
        "_needs_authoring": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Catalog plan CSV → book/series plan YAML (Waystream pattern)")
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--brand", help="Only import rows for this brand archetype id")
    ap.add_argument("--locale", default="en_US", help="Registry lane_id (e.g. de_DE, ja_JP)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="Overwrite existing YAML files")
    ap.add_argument("--limit", type=int, default=0, help="Max book rows to process")
    ap.add_argument("--out-books", type=Path, default=None)
    ap.add_argument("--out-series", type=Path, default=None)
    args = ap.parse_args()
    lane_id = normalize_lane_id(args.locale)
    default_books, default_series = plan_dirs(ROOT, lane_id)
    if args.out_books is None:
        args.out_books = default_books
    if args.out_series is None:
        args.out_series = default_series

    plan_source = str(args.csv.relative_to(ROOT)) if args.csv.is_relative_to(ROOT) else str(args.csv)
    rows = _rows_from_csv(args.csv, args.brand)
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        print("No rows to import.")
        return 1

    grouped = _group_series(rows)
    n_series = n_books = n_skip = 0
    sample_book = sample_series = ""

    for series_id, book_rows in sorted(grouped.items()):
        teacher_raw = _parse_book_id(book_rows[0]["book_id"])["teacher"]
        series_path = args.out_series / f"{series_id}.yaml"
        try:
            series_rel = str(series_path.relative_to(ROOT))
        except ValueError:
            series_rel = str(series_path)
        if series_path.exists() and not args.force:
            pass  # still emit books; series no-clobber unless force
        else:
            sp = _build_series_plan(
                series_id, book_rows, plan_source=plan_source, teacher_raw=teacher_raw, lane_id=lane_id
            )
            if not args.dry_run:
                args.out_series.mkdir(parents=True, exist_ok=True)
                series_path.write_text(yaml.safe_dump(sp, sort_keys=False, allow_unicode=True))
            n_series += 1
            if not sample_series:
                sample_series = series_id

        for row in book_rows:
            book_path = args.out_books / f"{row['book_id']}.yaml"
            if book_path.exists() and not args.force:
                n_skip += 1
                continue
            bp = _build_book_plan(row, series_rel, plan_source=plan_source, teacher_raw=teacher_raw)
            if not args.dry_run:
                args.out_books.mkdir(parents=True, exist_ok=True)
                book_path.write_text(yaml.safe_dump(bp, sort_keys=False, allow_unicode=True))
            n_books += 1
            if not sample_book:
                sample_book = row["book_id"]

    mode = "(dry-run) would write" if args.dry_run else "wrote"
    print(f"{mode} {n_series} series + {n_books} book plans (skipped {n_skip} existing)")
    if sample_book:
        print(f"sample book: {sample_book}")
    if sample_series:
        print(f"sample series: {sample_series}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
