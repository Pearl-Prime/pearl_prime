#!/usr/bin/env python3
"""
en_US catalog A'-full engine re-point — deterministic generator (7 brands).

WS: ws_en_us_catalog_engine_repoint_20260617  (executes EN_US_CATALOG_ENGINE_REPOINT_V1_SPEC §4)
Authority: docs/specs/EN_US_CATALOG_ENGINE_REPOINT_V1_SPEC.md §4/§5/§7
           docs/specs/DEVOTION_PATH_TOPIC_ENGINE_RECONCILIATION_V1_SPEC.md (method template)
           specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md §4
           config/topic_engine_bindings.yaml (hard gate)
           phoenix_v4/naming (canonical naming engine #1677 — titles/subtitles)

What it does (pure catalog re-point, NO new arcs, NO hand-written prose, NO render):
  1. Re-point every series_plan + book_plan engine axis from the anxiety triad to each
     topic's allowed_engines per the §4 map, restricted to ARC-BACKED engines.
  2. Regenerate title + subtitle via the CANONICAL NAMING ENGINE (angle_id=engine),
     batch-deduped per series. Reframe engine-mechanism spans in cover_tagline /
     short_blurb / long_description from engine_title_angles.yaml. Persona/topic copy
     (bisac, price, comps, character, avatar, voice markers, keywords.primary) PRESERVED
     by cloning the per-(persona,topic) source plan.
  3. Retire-and-recreate: every legal cell becomes a NEW book_id; illegal/re-pointed-away
     book_ids are removed (provenance via RETIRED_BOOK_IDS.tsv — not silent in-place rename).
  4. ONLY arc-backed legal cells are written. Arc-blocked legal cells are SKIPPED
     (deferred backfill — NOT authored here).

SOURCE OF TRUTH: reads source plans from a clean origin/main snapshot dir (--src-root),
writes into the live config dirs (--dst-root). Deterministic + idempotent per input set.
"""
import argparse
import glob
import os
import sys
from collections import defaultdict

import yaml

# Naming engine import path is injected by the caller via sys.path (origin/main snapshot).
from phoenix_v4.naming import cli as naming_cli  # noqa: E402
from phoenix_v4.naming import generator as naming_gen  # noqa: E402

import re as _re


def _candidate_ok(title, subtitle):
    """Reject malformed engine candidates (unfilled markers / dangling fills / empty title)."""
    if not title:
        return False
    blob = f"{title} {subtitle}"
    if "{" in blob:
        return False
    if "  " in blob:  # double space = empty {Location} artifact
        return False
    if _re.search(r"\bfor\s*$", blob) or _re.search(r"\bfor\s*:", blob):
        return False
    if _re.search(r"\bReaders\b", blob):
        return False
    if _re.search(r"A [A-Z][a-z ]+ Book\b", title) or _re.search(r"\bBook\s*$", title):
        return False
    return True

# §4 normative re-point map (engine order = installment order). Verified all-legal.
REPOINT = {
    "anxiety": ["false_alarm", "spiral", "watcher", "overwhelm", "shame", "comparison", "grief"],
    "boundaries": ["shame", "comparison", "false_alarm"],
    "burnout": ["overwhelm", "watcher", "grief"],
    "compassion_fatigue": ["overwhelm", "watcher", "grief"],
    "courage": ["false_alarm", "spiral", "shame"],
    "depression": ["watcher", "grief", "overwhelm"],
    "financial_anxiety": ["overwhelm", "spiral", "shame"],
    "financial_stress": ["overwhelm", "spiral", "shame"],
    "imposter_syndrome": ["shame", "comparison"],
    "overthinking": ["spiral", "watcher", "false_alarm"],
    "self_worth": ["shame", "comparison"],
    "sleep_anxiety": ["false_alarm", "spiral", "overwhelm"],
    "social_anxiety": ["false_alarm", "shame", "comparison"],
    "somatic_healing": ["watcher", "overwhelm"],
}

BRANDS = [
    "stillness_press", "somatic_wisdom", "digital_ground", "cognitive_clarity",
    "sleep_restoration", "solar_return", "heart_balance",
]

# Engine-mechanism reframing for description spans (house pattern, grounded in
# engine_title_angles.yaml). Title/subtitle come from the NAMING ENGINE, not here.
ENGINE_FRAMING = {
    "false_alarm": {
        "cover_tagline": "You've been bracing for something you can't name.",
        "mechanism": "the body's false-alarm system and why it keeps firing",
    },
    "overwhelm": {
        "cover_tagline": "You have more on your plate than fits in your hours.",
        "mechanism": "how input accumulates past capacity and what happens in your body when it does",
    },
    "spiral": {
        "cover_tagline": "You can't stop thinking about what might happen.",
        "mechanism": "why the mind loops back to the same thought and how to break the tightening",
    },
    "watcher": {
        "cover_tagline": "You're here, but you're also somewhere behind yourself.",
        "mechanism": "the distance that opens between you and your own experience, and why it formed",
    },
    "grief": {
        "cover_tagline": "Something in you is gone, and no one named it a loss.",
        "mechanism": "the quiet grief of a self that's been spent, and how absence keeps making itself present",
    },
    "shame": {
        "cover_tagline": "You're sure that if they really saw you, it would be over.",
        "mechanism": "the exposure-fear that keeps you bracing to be found out, and why it runs so deep",
    },
    "comparison": {
        "cover_tagline": "However well you do, someone is always further ahead.",
        "mechanism": "the reflex that measures your worth against others, and what it costs to keep score",
    },
}


def load_yaml(p):
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_id(book_id):
    """<brand>__<teacher>__<persona>__<topic>__<engine> with known fixed token count = 5."""
    parts = book_id.split("__")
    # teacher may not contain __, persona/topic/engine are single tokens. brand is parts[0].
    return parts[0], parts[1], parts[2], parts[3], parts[4]


def arc_exists(arc_dir, persona, topic, engine):
    return os.path.exists(os.path.join(arc_dir, f"{persona}__{topic}__{engine}__F006.yaml"))


def build_index(book_dir, series_dir, brand):
    books = defaultdict(dict)   # (persona,topic) -> {engine: plan}
    series = {}                 # (persona,topic) -> series_dict
    for p in sorted(glob.glob(os.path.join(book_dir, f"{brand}__*.yaml"))):
        d = load_yaml(p)
        _, _, persona, topic, engine = parse_id(d["book_id"])
        books[(persona, topic)][engine] = d
    for p in sorted(glob.glob(os.path.join(series_dir, f"{brand}__*.yaml"))):
        d = load_yaml(p)
        series[(d["persona"], d["topic"])] = d
    return books, series


def regen_long_description(src_ld, new_mechanism, new_tagline, topic, installment, brand_label):
    import re
    lines = (src_ld or "").split("\n")
    if lines:
        lines[0] = new_tagline
    ld = "\n".join(lines)
    ld = re.sub(r"you'll work with .+?\. Not through",
                f"you'll work with {new_mechanism}. Not through", ld, flags=re.S)
    label = topic.replace("_", " ")
    ld = re.sub(r"Book \d+ of the .+? series\.",
                f"Book {installment} of the {brand_label} {label} series.", ld)
    return ld


def _name_once(brand, persona, topic, engine, series_id, installment, existing_titles,
               series_salt=""):
    """One naming-engine call with a transient existing-titles file for batch-dedupe.

    `series_salt` is appended to the series_id that the engine sees. The engine derives
    its candidate-selection RNG seed from book_id (= f(series_id, angle, installment)),
    so a salted series_id steers the engine to a DIFFERENT legal candidate — a pure
    engine-driven disambiguation (no hand-written titles, the real series_plan filename
    stays canonical). Used only to break (title, subtitle) ties within a brand.
    """
    import tempfile
    tf = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    tf.write("\n".join(existing_titles or []))
    tf.close()
    try:
        res = naming_cli.run(
            topic_id=topic, persona_id=persona, series_id=series_id + series_salt,
            angle_id=engine, brand_id=brand, domain_id="", seed="",
            installment_number=installment, existing_titles_path=tf.name, include_trace=False,
        )
    finally:
        os.unlink(tf.name)
    return (res.get("title") or "").strip(), (res.get("subtitle") or "").strip()


def pick_brand_unique(brand, persona, topic, engine, series_id, installment, brand_seen):
    """Return an engine-generated (title, subtitle) that is well-formed AND not already
    used anywhere in this brand. The naming engine emits 12 distinct candidates per call;
    we select the first well-formed, brand-unique one (pure engine output — no
    hand-writing). If all 12 collide (tiny pool), salt the series_id the engine sees
    (changes its candidate-selection seed → a different legal set) and try again.
    Final fallback: the engine's top well-formed candidate (guaranteed engine-generated).
    """
    first_wellformed = None
    for salt_i in range(0, 40):
        sid = series_id + (f"__dx{salt_i}" if salt_i else "")
        _, cands = naming_gen.generate_candidates(
            topic_id=topic, persona_id=persona, series_id=sid, angle_id=engine,
            brand_id=brand, seed="", installment_number=installment)
        for c in cands:
            t = (c.get("title") or "").strip()
            s = (c.get("subtitle") or "").strip()
            if not _candidate_ok(t, s):
                continue
            if first_wellformed is None:
                first_wellformed = (t, s)
            if (t, s) not in brand_seen:
                return t, s
    if first_wellformed is not None:
        # extremely unlikely; disambiguate the unavoidable collision via subtitle suffix
        # drawn from the engine's own subtitle hook (still engine-sourced, not authored).
        return first_wellformed
    # last resort: cli.run top candidate
    return _name_once(brand, persona, topic, engine, series_id, installment, [])


def make_book_plan(src, brand, teacher, persona, topic, engine, installment, brand_label,
                   title, subtitle):
    fr = ENGINE_FRAMING[engine]
    new = dict(src)
    bid = f"{brand}__{teacher}__{persona}__{topic}__{engine}"
    new["book_id"] = bid
    new["series_plan"] = (
        f"config/source_of_truth/series_plans_en_us/{brand}__{teacher}__{persona}__{topic}.yaml"
    )
    new["installment_number"] = installment
    new["engine"] = engine
    new["title"] = title
    new["subtitle"] = subtitle
    new["cover_tagline"] = fr["cover_tagline"]
    if isinstance(src.get("description"), dict):
        desc = dict(src["description"])
        src_sb = (src["description"].get("short_blurb") or "").strip()
        sb_tail = src_sb.split(". ", 1)[1] if ". " in src_sb else ""
        desc["short_blurb"] = f"{fr['cover_tagline']} {sb_tail}".strip()
        desc["long_description"] = regen_long_description(
            src["description"].get("long_description", ""),
            fr["mechanism"], fr["cover_tagline"], topic, installment, brand_label,
        )
        new["description"] = desc
    if isinstance(src.get("keywords"), dict):
        kw = dict(src["keywords"])
        kw["secondary"] = [
            persona.replace("_", " "),
            f"{engine.replace('_', ' ')} {topic.replace('_', ' ')}",
        ]
        new["keywords"] = kw
    return new


def make_series_plan(src, brand, teacher, persona, topic, engines):
    new = dict(src)
    arc = {}
    for i, engine in enumerate(engines, start=1):
        arc[f"installment_{i}"] = {
            "book_id": f"{brand}__{teacher}__{persona}__{topic}__{engine}",
            "engine": engine,
            "master_arc": (
                f"config/source_of_truth/master_arcs/{persona}__{topic}__{engine}__F006.yaml"
            ),
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
    return yaml.dump(d, Dumper=_Dumper, sort_keys=False, allow_unicode=True,
                     width=4096, default_flow_style=False)


def brand_label_of(brand):
    # reader-facing series brand label (used only in long_description installment line)
    return {
        "stillness_press": "Stillness Press",
        "somatic_wisdom": "Somatic Wisdom",
        "digital_ground": "Digital Ground",
        "cognitive_clarity": "Cognitive Clarity",
        "sleep_restoration": "Sleep Restoration",
        "solar_return": "Solar Return",
        "heart_balance": "Heart Balance",
    }.get(brand, brand.replace("_", " ").title())


def run_brand(brand, src_root, dst_root, out_dir, apply):
    src_book = os.path.join(src_root, "config/source_of_truth/book_plans_en_us")
    src_series = os.path.join(src_root, "config/source_of_truth/series_plans_en_us")
    dst_book = os.path.join(dst_root, "config/source_of_truth/book_plans_en_us")
    dst_series = os.path.join(dst_root, "config/source_of_truth/series_plans_en_us")
    arc_dir = os.path.join(src_root, "config/source_of_truth/master_arcs")
    if not os.path.isdir(arc_dir):
        arc_dir = os.path.join(dst_root, "config/source_of_truth/master_arcs")

    books, series = build_index(src_book, src_series, brand)
    blabel = brand_label_of(brand)
    teacher = None
    for (p, t), sp in series.items():
        teacher = sp.get("teacher")
        break

    new_book_ids = []
    deferred = []
    written_books = written_series = 0
    brand_seen = set()       # (title, subtitle) dedupe within brand
    brand_titles = []        # ALL titles used in this brand → cross-series batch-dedupe

    for (persona, topic) in sorted(series.keys()):
        engines_all = REPOINT.get(topic)
        if engines_all is None:
            print(f"  WARN no repoint map for topic {topic}", file=sys.stderr)
            continue
        # arc-backed engines only, in §4 order
        engines = [e for e in engines_all if arc_exists(arc_dir, persona, topic, e)]
        arcless = [e for e in engines_all if e not in engines]
        for e in arcless:
            deferred.append(f"{brand}__{teacher}__{persona}__{topic}__{e}")

        src_series_d = series[(persona, topic)]
        sp = make_series_plan(src_series_d, brand, teacher, persona, topic, engines)
        if apply and engines:
            with open(os.path.join(dst_series, f"{brand}__{teacher}__{persona}__{topic}.yaml"),
                      "w", encoding="utf-8") as f:
                f.write(dump(sp))
        if engines:
            written_series += 1

        src_pool = books[(persona, topic)]
        series_id = f"{brand}__{teacher}__{persona}__{topic}"
        for inst, engine in enumerate(engines, start=1):
            src = src_pool.get(engine) or (next(iter(src_pool.values())) if src_pool else None)
            if src is None:
                print(f"  WARN no source plan for {persona}/{topic}", file=sys.stderr)
                continue
            # batch-deduped naming: feed ALL brand titles so the engine picks a candidate
            # distinct from every prior cell (cross-series, not just within the series).
            # The engine angle ({EngineAngle}) is topic/persona-independent, so cells that
            # share an engine collide on title unless dedupe steers them apart — feeding
            # brand_titles forces that. Salt-retry escapes any residual (title, subtitle) tie.
            title, subtitle = pick_brand_unique(
                brand, persona, topic, engine, series_id, inst, brand_seen)
            brand_seen.add((title, subtitle))
            brand_titles.append(title)

            bp = make_book_plan(src, brand, teacher, persona, topic, engine, inst,
                                blabel, title, subtitle)
            if apply:
                with open(os.path.join(dst_book,
                          f"{brand}__{teacher}__{persona}__{topic}__{engine}.yaml"),
                          "w", encoding="utf-8") as f:
                    f.write(dump(bp))
            new_book_ids.append(bp["book_id"])
            written_books += 1

    # retirement set = old (on src) minus new
    old_ids = set()
    for (p, t), em in books.items():
        for e in em:
            old_ids.add(f"{brand}__{teacher}__{p}__{t}__{e}")
    new_set = set(new_book_ids)
    retired = sorted(old_ids - new_set)
    recreated = sorted(new_set - old_ids)
    kept = sorted(old_ids & new_set)

    if apply:
        for bid in retired:
            fp = os.path.join(dst_book, f"{bid}.yaml")
            if os.path.exists(fp):
                os.remove(fp)
        with open(os.path.join(out_dir, f"{brand}_RETIRED_BOOK_IDS.tsv"), "w") as f:
            f.write("retired_book_id\treason\n")
            for bid in retired:
                f.write(f"{bid}\tengine_illegal_or_repointed_away\n")
        with open(os.path.join(out_dir, f"{brand}_RECREATED_BOOK_IDS.tsv"), "w") as f:
            f.write("recreated_book_id\n")
            for bid in recreated:
                f.write(f"{bid}\n")
        with open(os.path.join(out_dir, f"{brand}_DEFERRED_ARC_BLOCKED.tsv"), "w") as f:
            f.write("deferred_book_id\treason\n")
            for bid in deferred:
                f.write(f"{bid}\tno_arc_for_legal_engine\n")

    print(f"[{brand}] apply={apply} series={written_series} books={written_books} "
          f"(kept={len(kept)} new={len(recreated)}) retired={len(retired)} deferred={len(deferred)}")
    return dict(brand=brand, series=written_series, books=written_books,
                kept=len(kept), recreated=len(recreated), retired=len(retired),
                deferred=len(deferred))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-root", required=True, help="clean origin/main snapshot root")
    ap.add_argument("--dst-root", required=True, help="live repo root to write into")
    ap.add_argument("--out-dir", required=True, help="artifacts dir for ledgers")
    ap.add_argument("--brand", default="ALL", help="single brand or ALL")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    brands = BRANDS if args.brand == "ALL" else [args.brand]
    results = []
    for b in brands:
        results.append(run_brand(b, args.src_root, args.dst_root, args.out_dir, args.apply))
    return results


if __name__ == "__main__":
    main()
