#!/usr/bin/env python3
"""Generate detailed-plan SKELETONS for a brand's arc-backed (buildable) cells.

For each arc-backed (persona, topic) of a brand: emit a series_plan + per-installment
book_plan with all STRUCTURAL fields filled — arc refs, engine, installment, duration,
format, resolved pen-name byline author, and naming-engine title+subtitle — and PROSE
fields left empty with `_needs_authoring: true`, for Pearl_Writer/Pearl_Editor (Claude
subagents) to author. Schema mirrors the existing en_US prose plans.

  PYTHONPATH=. python3 scripts/catalog/gen_plan_skeletons.py --brand night_reset --dry-run
  PYTHONPATH=. python3 scripts/catalog/gen_plan_skeletons.py --brand night_reset --limit-series 1
"""
from __future__ import annotations
import argparse
import hashlib
from collections import defaultdict
from pathlib import Path

import yaml

from phoenix_v4.planning.author_brand_resolver import resolve_author_from_brand
from phoenix_v4.naming import cli as naming

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "config/brand_management/global_brand_registry_unified.yaml"
ARCS = ROOT / "config/source_of_truth/master_arcs"
SERIES_DIR = ROOT / "config/source_of_truth/series_plans_en_us"
BOOK_DIR = ROOT / "config/source_of_truth/book_plans_en_us"
_GEN_ASSIGN = ROOT / "config/brand_author_assignments_generated.yaml"
ASSIGN = _GEN_ASSIGN if _GEN_ASSIGN.exists() else None

ENGINE_ORDER = ["false_alarm", "overwhelm", "spiral", "shame", "grief", "comparison", "watcher"]
INTENTS = ["scenario_specific", "solution_seeking", "identity_based", "crisis", "informational"]


# Topic -> default BISAC codes. Anxiety-family topics lead with SEL036000 (SELF-HELP /
# Anxieties & Phobias) and never SEL045000 (SELF-HELP / Journaling), which is a format
# shelf not a topic shelf. Mirrors the corpus-correct anxiety triple (+ SEL024000
# Stress Management, SEL031000 Personal Growth). Pearl_Writer/Pearl_Editor inherit this
# floor during authoring and may refine; unmapped topics stay empty for the author layer.
_ANXIETY_FAMILY = {"anxiety", "sleep_anxiety", "social_anxiety", "financial_anxiety", "overthinking"}
_TOPIC_BISAC = {t: ["SEL036000", "SEL024000", "SEL031000"] for t in _ANXIETY_FAMILY}


def topic_bisac(topic: str) -> list:
    """Deterministic BISAC floor for a topic (empty list if unmapped)."""
    return list(_TOPIC_BISAC.get(topic, []))


def _h(s: str) -> int:
    return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16)


def arc_index():
    idx = defaultdict(dict)   # (persona, topic) -> {engine: (path, fmt)}
    for p in sorted(ARCS.glob("*.yaml")):
        parts = p.stem.split("__")
        if len(parts) != 4:
            continue
        persona, topic, engine, fmt = parts
        idx[(persona, topic)][engine] = (p, fmt)
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True)
    ap.add_argument("--limit-series", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="overwrite existing plan files (default: skip authored ones)")
    args = ap.parse_args()

    reg = yaml.safe_load(REG.read_text())["brands"]
    rec = next((r for _b, r in reg.items() if r.get("brand_archetype_id") == args.brand), None)
    if not rec:
        print(f"brand '{args.brand}' not in registry")
        return
    teacher = rec.get("teacher_id") or "house"
    topics = rec.get("primary_topics") or []
    personas = rec.get("primary_personas") or []
    idx = arc_index()

    cells = [(ps, tp) for ps in personas for tp in topics if (ps, tp) in idx]
    if args.limit_series:
        cells = cells[:args.limit_series]
    print(f"{args.brand}: teacher={teacher} personas={len(personas)} topics={len(topics)} -> {len(cells)} buildable series")

    n_series = n_books = 0
    for persona, topic in cells:
        engmap = idx[(persona, topic)]
        engines = [e for e in ENGINE_ORDER if e in engmap] + [e for e in engmap if e not in ENGINE_ORDER]
        series_id = f"{args.brand}__{teacher}__{persona}__{topic}"
        if (SERIES_DIR / f"{series_id}.yaml").exists() and not args.force:
            continue  # no-clobber: never overwrite an existing/authored plan
        author = resolve_author_from_brand(brand_id=args.brand, topic_id=topic, persona_id=persona, assignments_path=ASSIGN)
        arc, books = {}, []
        for i, engine in enumerate(engines, start=1):
            apath, fmt = engmap[engine]
            book_id = f"{series_id}__{engine}"
            arc[f"installment_{i}"] = {"book_id": book_id, "engine": engine,
                                       "master_arc": str(apath.relative_to(ROOT)), "duration": "standard_book_60min"}
            intent = INTENTS[(i - 1) % len(INTENTS)]
            try:
                nm = naming.run(topic, persona, series_id, intent, args.brand, "", str(_h(book_id)), i)
                title, subtitle = (nm.get("title") or "").strip(), (nm.get("subtitle") or "").strip()
            except Exception:
                title, subtitle = "", ""
            books.append((i, engine, book_id, fmt, title, subtitle))

        series_path = SERIES_DIR / f"{series_id}.yaml"
        sp = {
            "series_plan_schema": "1.0.0", "locale": "en_US", "book_id_prefix": series_id,
            "brand": args.brand, "teacher": (None if teacher == "house" else teacher),
            "persona": persona, "topic": topic, "byline_author": author,
            "arc": arc,
            "reader_promise_family": "", "bestseller_hook_family": "", "emotional_engine": f"{topic}_recognition",
            "comp_series": [],
            "platform_strategy": {"primary": ["kdp_ebook", "audible"],
                                  "secondary": ["apple_books", "google_play", "spotify_audiobooks"],
                                  "launch_platform": "kdp_ebook",
                                  "cadence": {"release_spacing_days": 14, "max_books_per_brand_per_month": 2}},
            "reader_avatar": {"age": "", "where_they_are": "", "what_they_need": "", "what_they_avoid": ""},
            "series_voice_markers": {"register": "", "sentence_rhythm": "", "metaphor_family": "", "second_person_default": True},
            "_needs_authoring": True,
        }
        if not args.dry_run:
            SERIES_DIR.mkdir(parents=True, exist_ok=True)
            series_path.write_text(yaml.safe_dump(sp, sort_keys=False, allow_unicode=True))
        n_series += 1

        for i, engine, book_id, fmt, title, subtitle in books:
            bp = {
                "book_plan_schema": "1.0.0", "book_id": book_id,
                "series_plan": str(series_path.relative_to(ROOT)),
                "installment_number": i, "engine": engine, "duration": "standard_book_60min",
                "runtime_format_id": "standard_book_60min", "structural_format_id": fmt,
                "target_word_range": [9000, 12000], "target_audio_minutes": 70,
                "title": title, "subtitle": subtitle, "cover_tagline": "",
                "description": {"short_blurb": "", "long_description": ""},
                "keywords": {"primary": [], "secondary": []},
                "bisac_codes": topic_bisac(topic),
                "target_price": {"ebook_usd": 4.99, "audible_usd": 9.99, "paperback_usd": 12.99},
                "author_positioning": {"teacher": (None if teacher == "house" else teacher),
                                       "brand": args.brand, "byline_author": author},
                "comp_titles": [],
                "_needs_authoring": True,
            }
            if not args.dry_run:
                BOOK_DIR.mkdir(parents=True, exist_ok=True)
                (BOOK_DIR / f"{book_id}.yaml").write_text(yaml.safe_dump(bp, sort_keys=False, allow_unicode=True))
            n_books += 1

    print(f"{'(dry-run) would write' if args.dry_run else 'wrote'} {n_series} series + {n_books} book skeletons")
    if cells:
        ps, tp = cells[0]
        print(f"sample series: {args.brand}__{teacher}__{ps}__{tp} (author={resolve_author_from_brand(brand_id=args.brand, topic_id=tp, persona_id=ps, assignments_path=ASSIGN)})")


if __name__ == "__main__":
    main()
