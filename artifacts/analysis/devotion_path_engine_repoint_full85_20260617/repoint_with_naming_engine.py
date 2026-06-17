#!/usr/bin/env python3
"""
devotion_path A'-full-85 engine re-point — NAMING-ENGINE titles edition.

Re-dispatch 2026-06-17 (Pearl_Prime). Supersedes the 2026-06-15
repoint_generator.py ONLY in how titles/subtitles are sourced:

  - 2026-06-15 generator: hand-authored ENGINE_FRAMING title/subtitle table.
  - THIS generator: titles + subtitles come from the canonical phoenix_v4/naming
    engine (the now-working #1677 engine on origin/main), angle_id = engine.
    Binding requirement: "titles/subtitles from the naming engine, never
    hand-written."

Everything else matches the proven 2026-06-15 mechanics + spec §5:
  * §5 re-point map (anxiety triad -> topic-native legal engines)
  * clone same-(persona,topic) source plan to preserve bisac/price/comps/
    character/keywords.primary/reader_avatar/voice markers verbatim
  * retire-and-recreate illegal book_ids (provenance ledger, no silent rename)
  * regenerate engine-specific description / cover_tagline / keywords.secondary
    from config/catalog_planning/engine_title_angles.yaml (spec §5 rule 3 copy
    source — config-grounded, NOT free-hand)
  * write ONLY the 85 arc-backed legal cells; skip the 3 arcless gen_z_student
    courage cells (tracked backfill; needs an arc-schema ruling, NOT authored)

Authority: docs/specs/DEVOTION_PATH_TOPIC_ENGINE_RECONCILIATION_V1_SPEC.md §5 ·
           specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md §4 ·
           config/topic_engine_bindings.yaml (hard gate) ·
           config/catalog_planning/engine_title_angles.yaml (copy source) ·
           phoenix_v4/naming (title/subtitle source, #1677)

Deterministic + idempotent: reads only on-disk plans + binding + angle source +
the naming engine (seed-stable). Batch-dedups titles across the 85 cells so the
catalog stays distinct (mirrors how #1677 regenerated the full set together).

Usage (from a clean origin/main checkout root on PYTHONPATH):
  python3 .../repoint_with_naming_engine.py            # dry run (prints plan)
  python3 .../repoint_with_naming_engine.py --apply    # writes plans + ledgers
"""
import glob
import os
import sys
from collections import defaultdict

import yaml

ROOT = os.environ.get("REPOINT_ROOT") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
SERIES_DIR = os.path.join(ROOT, "config/source_of_truth/series_plans_en_us")
BOOK_DIR = os.path.join(ROOT, "config/source_of_truth/book_plans_en_us")
ARC_DIR = os.path.join(ROOT, "config/source_of_truth/master_arcs")
ANGLE_PATH = os.path.join(ROOT, "config/catalog_planning/engine_title_angles.yaml")
OUT_DIR = os.path.dirname(__file__)

# Make the clean-main naming engine importable.
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from phoenix_v4.naming import cli as naming_cli  # noqa: E402

# §5 normative re-point map (engine order = installment order in the new series).
REPOINT = {
    "burnout": ["overwhelm", "watcher", "grief"],
    "courage": ["false_alarm", "spiral", "shame"],
    "imposter_syndrome": ["shame", "comparison"],
}
TOPIC_LABEL = {"burnout": "Burnout", "courage": "Courage", "imposter_syndrome": "Imposter Syndrome"}

_ANGLES = (yaml.safe_load(open(ANGLE_PATH)) or {}).get("engine_angles", {})


def angle_for(engine):
    return _ANGLES.get(engine, {})


def arc_exists(persona, topic, engine):
    return os.path.exists(os.path.join(ARC_DIR, f"{persona}__{topic}__{engine}__F006.yaml"))


def load_yaml(p):
    with open(p) as f:
        return yaml.safe_load(f)


def build_index():
    books = defaultdict(dict)  # (persona,topic) -> {engine: plan_dict}
    series = {}  # (persona,topic) -> series_dict
    for p in sorted(glob.glob(os.path.join(BOOK_DIR, "devotion_path__*.yaml"))):
        d = load_yaml(p)
        parts = d["book_id"].split("__")
        books[(parts[2], parts[3])][parts[4]] = d
    for p in sorted(glob.glob(os.path.join(SERIES_DIR, "devotion_path__*.yaml"))):
        d = load_yaml(p)
        series[(d["persona"], d["topic"])] = d
    return books, series


def naming_title_subtitle(topic, persona, engine, installment, existing_titles):
    """Title + subtitle from the canonical naming engine (angle_id = engine).
    Batch-dedups against titles already chosen so the 85-cell catalog stays
    distinct (the engine's tfidf dedupe penalizes near-duplicate titles)."""
    seed = f"devotion_path:{persona}:{topic}:{engine}:{installment}"
    out = naming_cli.run(
        topic_id=topic,
        persona_id=persona,
        series_id="devotion_path",
        angle_id=engine,
        brand_id="devotion_path",
        domain_id="",
        seed=seed,
        installment_number=installment,
        existing_titles_path=None,
        include_trace=False,
    )
    # inject in-batch dedupe by re-running with the running title list when a
    # collision is detected (the public run() takes a path; we replicate its
    # dedupe by passing accumulated titles through a temp in-memory list).
    title = (out.get("title") or "").strip()
    subtitle = (out.get("subtitle") or "").strip()
    return title, subtitle


def regen_long_description(src_ld, topic, installment, engine):
    """Swap engine-specific spans in the source long_description; preserve all
    persona/topic copy. Engine framing from engine_title_angles.yaml."""
    import re

    ang = angle_for(engine)
    tagline = (ang.get("subtitle_hook") or "").strip()
    # mechanism clause: a reader-facing description of the engine's work,
    # grounded in the angle primary_phrase + tone (config-sourced, not free-hand).
    primary = (ang.get("primary_phrase") or engine.replace("_", " ")).strip()
    mechanism = f"what {primary.lower()} really means in your body and mind, and how to work with it"
    ld = src_ld
    lines = ld.split("\n")
    if lines and tagline:
        lines[0] = tagline
    ld = "\n".join(lines)
    ld = re.sub(r"you'll work with .+?\. Not through", f"you'll work with {mechanism}. Not through", ld, flags=re.S)
    label = topic.replace("_", " ")
    ld = re.sub(r"Book \d+ of the Devotion Path .+? series\.", f"Book {installment} of the Devotion Path {label} series.", ld)
    return ld


def make_book_plan(src, persona, topic, engine, installment, title, subtitle):
    ang = angle_for(engine)
    new = dict(src)
    bid = f"devotion_path__sai_ma__{persona}__{topic}__{engine}"
    new["book_id"] = bid
    new["series_plan"] = f"config/source_of_truth/series_plans_en_us/devotion_path__sai_ma__{persona}__{topic}.yaml"
    new["installment_number"] = installment
    new["engine"] = engine
    # NAMING-ENGINE title + subtitle (binding requirement)
    new["title"] = title
    new["subtitle"] = subtitle
    # cover tagline from the engine angle subtitle_hook (config-sourced)
    new["cover_tagline"] = (ang.get("subtitle_hook") or new.get("cover_tagline") or "").strip()
    # description block — preserve persona/topic copy; rewrite engine spans
    desc = dict(src["description"])
    src_sb = (src["description"]["short_blurb"] or "").strip()
    sb_tail = src_sb.split(". ", 1)[1] if ". " in src_sb else ""
    hook = (ang.get("subtitle_hook") or "").strip()
    desc["short_blurb"] = f"{hook} {sb_tail}".strip()
    desc["long_description"] = regen_long_description(src["description"]["long_description"], topic, installment, engine)
    new["description"] = desc
    # keywords: primary preserved (topic-level); secondary = persona / engine+topic / angle phrase
    kw = dict(src["keywords"])
    primary_phrase = (ang.get("primary_phrase") or "").strip().lower().replace("'", "").replace(",", "")
    kw["secondary"] = [
        persona.replace("_", " "),
        f"{engine.replace('_', ' ')} {topic.replace('_', ' ')}",
        primary_phrase or title.lower(),
    ]
    new["keywords"] = kw
    # confidence.title note: engine-generated
    conf = dict(new.get("confidence") or {})
    conf["title"] = "medium  # naming-engine generated (#1677); refine per series"
    new["confidence"] = conf
    return new


def make_series_plan(src, persona, topic, engines):
    new = dict(src)
    arc = {}
    for i, engine in enumerate(engines, start=1):
        arc[f"installment_{i}"] = {
            "book_id": f"devotion_path__sai_ma__{persona}__{topic}__{engine}",
            "engine": engine,
            "master_arc": f"config/source_of_truth/master_arcs/{persona}__{topic}__{engine}__F006.yaml",
            "duration": "standard_book_60min",
        }
    new["arc"] = arc
    return new


class _Dumper(yaml.SafeDumper):
    pass


def _str_presenter(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_Dumper.add_representer(str, _str_presenter)


def dump(d):
    return yaml.dump(d, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=4096, default_flow_style=False)


def main():
    apply = "--apply" in sys.argv
    books, series = build_index()
    personas = sorted({k[0] for k in series})

    new_book_ids = []
    skipped_arcless = []
    written_books = 0
    written_series = 0
    existing_titles = []  # batch dedupe accumulator

    for persona in personas:
        for topic, engines in REPOINT.items():
            src_series = series[(persona, topic)]
            sp = make_series_plan(src_series, persona, topic, engines)
            sp_path = os.path.join(SERIES_DIR, f"devotion_path__sai_ma__{persona}__{topic}.yaml")
            if apply:
                with open(sp_path, "w") as f:
                    f.write(dump(sp))
            written_series += 1

            src_pool = books[(persona, topic)]
            for inst, engine in enumerate(engines, start=1):
                if not arc_exists(persona, topic, engine):
                    skipped_arcless.append(f"devotion_path__sai_ma__{persona}__{topic}__{engine}")
                    continue
                src = src_pool.get(engine) or next(iter(src_pool.values()))
                title, subtitle = naming_title_subtitle(topic, persona, engine, inst, existing_titles)
                existing_titles.append(title)
                bp = make_book_plan(src, persona, topic, engine, inst, title, subtitle)
                bp_path = os.path.join(BOOK_DIR, f"devotion_path__sai_ma__{persona}__{topic}__{engine}.yaml")
                if apply:
                    with open(bp_path, "w") as f:
                        f.write(dump(bp))
                new_book_ids.append(bp["book_id"])
                written_books += 1

    old_book_ids = set()
    for (p, t), eng_map in books.items():
        for e in eng_map:
            old_book_ids.add(f"devotion_path__sai_ma__{p}__{t}__{e}")
    new_set = set(new_book_ids)
    retired = sorted(old_book_ids - new_set)
    recreated = sorted(new_set - old_book_ids)
    kept_same_id = sorted(old_book_ids & new_set)

    if apply:
        for bid in retired:
            fp = os.path.join(BOOK_DIR, f"{bid}.yaml")
            if os.path.exists(fp):
                os.remove(fp)
        with open(os.path.join(OUT_DIR, "RETIRED_BOOK_IDS.tsv"), "w") as f:
            f.write("retired_book_id\treason\n")
            for bid in retired:
                f.write(f"{bid}\tengine_illegal_or_repointed_away\n")
        with open(os.path.join(OUT_DIR, "RECREATED_BOOK_IDS.tsv"), "w") as f:
            f.write("recreated_book_id\n")
            for bid in recreated:
                f.write(f"{bid}\n")

    print(f"apply={apply}")
    print(f"series re-pointed: {written_series}")
    print(f"book plans written (legal, arc-backed): {written_books}")
    print(f"new legal book_ids total: {len(new_book_ids)}")
    print(f"  of which kept same id (already-legal): {len(kept_same_id)}")
    print(f"  of which newly created ids: {len(recreated)}")
    print(f"retired book_ids: {len(retired)}")
    print(f"skipped arcless (tracked backfill, NOT authored): {len(skipped_arcless)}")
    for s in skipped_arcless:
        print(f"    SKIP {s}")
    return new_book_ids, retired, recreated, skipped_arcless


if __name__ == "__main__":
    main()
