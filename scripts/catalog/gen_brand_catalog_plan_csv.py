#!/usr/bin/env python3
"""Generate Waystream-style 800-row catalog plan CSV for a brand archetype.

Expands persona × topic × engine grid (plus optional __1hr variants) to hit --target rows.
Uses naming engine for title/subtitle; resolves pen-name bylines from brand assignments.

  PYTHONPATH=. python3 scripts/catalog/gen_brand_catalog_plan_csv.py \\
    --brand stillness_press --target 800 --dry-run

  PYTHONPATH=. python3 scripts/catalog/gen_brand_catalog_plan_csv.py \\
    --brand stillness_press --target 800 \\
    --out artifacts/catalog/stillness_press_800_catalog_plan.csv
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

import yaml

from phoenix_v4.naming import cli as naming
from phoenix_v4.planning.author_brand_resolver import resolve_author_from_brand
from scripts.catalog.gen_plan_skeletons import ASSIGN, ENGINE_ORDER, INTENTS
from scripts.catalog.locale_paths import normalize_lane_id
from scripts.catalog.market_topic_fit import topics_for_generation

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "config/brand_management/global_brand_registry_unified.yaml"
PERSONAS = ROOT / "config/catalog_planning/canonical_personas.yaml"
TOPICS = ROOT / "config/catalog_planning/canonical_topics.yaml"
ARCS = ROOT / "config/source_of_truth/master_arcs"

# Waystream flagship grid (10 × 15) — proven to yield 800 with 7 engines + 1hr mix
WAYSTREAM_TOPICS = [
    "anxiety", "boundaries", "burnout", "compassion_fatigue", "courage",
    "depression", "financial_anxiety", "financial_stress", "grief",
    "imposter_syndrome", "overthinking", "self_worth", "sleep_anxiety",
    "social_anxiety", "somatic_healing",
]


def _h(s: str) -> int:
    return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16)


_BRAND_REC_CACHE: dict[str, dict] = {}
_AUTHOR_CACHE: dict[tuple[str, str, str], str] = {}


def _brand_rec(brand: str, lane_id: str) -> dict:
    key = (brand, lane_id)
    if key in _BRAND_REC_CACHE:
        return _BRAND_REC_CACHE[key]
    reg = yaml.safe_load(REG.read_text())["brands"]
    for rec in reg.values():
        if rec.get("brand_archetype_id") == brand and rec.get("lane_id") == lane_id:
            _BRAND_REC_CACHE[key] = rec
            return rec
    raise SystemExit(f"brand '{brand}' not found in registry ({lane_id} lane)")


def _canonical_personas() -> list[str]:
    data = yaml.safe_load(PERSONAS.read_text())
    return [p if isinstance(p, str) else p.get("id", "") for p in (data.get("personas") or [])]


_ENGINE_BY_TOPIC: dict[str, list[str]] | None = None


def _engine_index() -> dict[str, list[str]]:
    global _ENGINE_BY_TOPIC
    if _ENGINE_BY_TOPIC is not None:
        return _ENGINE_BY_TOPIC
    by_topic: dict[str, list[str]] = {}
    for p in ARCS.glob("*.yaml"):
        parts = p.stem.split("__")
        if len(parts) < 4:
            continue
        topic, engine = parts[-3], parts[-2]
        by_topic.setdefault(topic, [])
        if engine not in by_topic[topic]:
            by_topic[topic].append(engine)
    _ENGINE_BY_TOPIC = by_topic
    return by_topic


def _engines_for_topic(topic: str) -> list[str]:
    found = _engine_index().get(topic, [])
    if found:
        return [e for e in ENGINE_ORDER if e in found] + [e for e in found if e not in ENGINE_ORDER]
    return list(ENGINE_ORDER)


def _author_display(brand: str, topic: str, persona: str) -> str:
    key = (brand, topic, persona)
    if key in _AUTHOR_CACHE:
        return _AUTHOR_CACHE[key]
    slug = resolve_author_from_brand(
        brand_id=brand, topic_id=topic, persona_id=persona, assignments_path=ASSIGN
    )
    display = slug.replace("_", " ").title() if slug else ""
    _AUTHOR_CACHE[key] = display
    return display


def _expand_grid(rec: dict, target: int, *, lane_id: str) -> tuple[list[str], list[str]]:
    personas = list(rec.get("primary_personas") or [])
    topics = list(rec.get("primary_topics") or [])
    # Expand to Waystream-scale grid when target exceeds registry footprint
    canon_p = _canonical_personas()
    fit_topics = topics_for_generation(lane_id, WAYSTREAM_TOPICS)
    if target > len(personas) * len(topics) * 5:
        personas = canon_p if len(fit_topics) < len(WAYSTREAM_TOPICS) else canon_p[:10]
        topics = fit_topics
    return personas, topics


def _title_subtitle(
    brand: str, topic: str, persona: str, engine: str, book_id: str, installment: int, *, use_naming: bool
) -> tuple[str, str]:
    series_base = "__".join(book_id.replace("__1hr", "").split("__")[:4])
    if use_naming:
        intent = INTENTS[(installment - 1) % len(INTENTS)]
        try:
            nm = naming.run(topic, persona, series_base, intent, brand, "", str(_h(book_id)), installment)
            return (nm.get("title") or "").strip(), (nm.get("subtitle") or "").strip()
        except Exception:
            pass
    topic_l = topic.replace("_", " ").title()
    persona_l = persona.replace("_", " ").title()
    engine_l = engine.replace("_", " ").title()
    return f"{topic_l}: {engine_l}", f"A guide for {persona_l}"


def generate_rows(
    brand: str,
    target: int,
    *,
    lane_id: str = "en_US",
    one_hr_ratio: float = 0.44,
    use_naming: bool = False,
) -> list[dict]:
    rec = _brand_rec(brand, lane_id)
    teacher = rec.get("teacher_id") or "default_teacher"
    personas, topics = _expand_grid(rec, target, lane_id=lane_id)
    rows: list[dict] = []
    seen: set[str] = set()

    def _fill(one_hr_ratio: float) -> None:
        nonlocal rows, seen
        for persona in personas:
            for topic in topics:
                engines = _engines_for_topic(topic)
                series_base = f"{brand}__{teacher}__{persona}__{topic}"
                installment = len(rows)
                for engine in engines:
                    for suffix, is_1hr in (("", False), ("__1hr", True)):
                        book_id = f"{series_base}__{engine}{suffix}"
                        if book_id in seen:
                            continue
                        if is_1hr and (_h(book_id) % 100) > int(one_hr_ratio * 100):
                            continue
                        seen.add(book_id)
                        installment += 1
                        title, subtitle = _title_subtitle(
                            brand, topic, persona, engine, book_id, installment, use_naming=use_naming
                        )
                        rows.append({
                            "book_id": book_id,
                            "title": title,
                            "subtitle": subtitle,
                            "author": _author_display(brand, topic, persona),
                            "installment": installment,
                            "topic": topic,
                            "engine": engine,
                            "persona": persona,
                            "cluster": "",
                        })
                        if len(rows) >= target:
                            return

    _fill(one_hr_ratio)
    if len(rows) < target and len(topics) < len(WAYSTREAM_TOPICS):
        _fill(1.0)
    return rows[:target]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True)
    ap.add_argument("--locale", default="en_US", help="Registry lane_id (e.g. de_DE, ja_JP)")
    ap.add_argument("--target", type=int, default=800)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--use-naming-engine", action="store_true", help="Slow: call phoenix_v4.naming per row")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    lane_id = normalize_lane_id(args.locale)
    rows = generate_rows(args.brand, args.target, lane_id=lane_id, use_naming=args.use_naming_engine)
    print(f"{args.brand}: generated {len(rows)} catalog rows (target {args.target})")
    if rows:
        print(f"  sample: {rows[0]['book_id']}")
        print(f"  personas: {len({r['persona'] for r in rows})}, topics: {len({r['topic'] for r in rows})}")
        print(f"  1hr variants: {sum(1 for r in rows if r['book_id'].endswith('__1hr'))}")

    if args.dry_run or not args.out:
        if len(rows) < args.target:
            print(f"  WARNING: ceiling {len(rows)} < target {args.target} — expand personas/topics or add engines")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["book_id", "title", "subtitle", "author", "installment", "topic", "engine", "persona", "cluster"]
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
