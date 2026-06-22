#!/usr/bin/env python3
"""Regenerate way_stream_sanctuary titles + engine-bearing subtitles (800/800 unique).

Dry-run proves achievability before --apply mutates plans.

  PYTHONPATH=. python3 scripts/catalog/waystream_subtitle_regen.py --dry-run
  PYTHONPATH=. python3 scripts/catalog/waystream_subtitle_regen.py --apply
  PYTHONPATH=. python3 scripts/catalog/waystream_subtitle_regen.py --apply --batch a
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
PLANS = REPO / "config/source_of_truth/book_plans_en_us"
BRAND = "way_stream_sanctuary"
ENGINE_ANGLES = REPO / "config/catalog_planning/engine_title_angles.yaml"
PATTERNS = REPO / "omega/title_entropy/subtitle_patterns.yaml"
PERSONA_FLAVOR = REPO / "config/catalog_planning/persona_subtitle_modifiers.yaml"
ARTIFACT = REPO / "artifacts/waystream/subtitle_regen_dryrun.json"

SUBTITLE_IDS = [
    "engine_persona_hook",
    "engine_voice",
    "engine_topic_persona",
    "engine_field_guide",
    "engine_reset",
    "engine_hook",
    "generation_voice",
    "profession_specific",
    "identity_shift",
]

TOPIC_DISPLAY = {
    "sleep_anxiety": "Sleep Anxiety",
    "social_anxiety": "Social Anxiety",
    "financial_anxiety": "Financial Anxiety",
    "financial_stress": "Financial Stress",
    "imposter_syndrome": "Imposter Syndrome",
    "self_worth": "Self-Worth",
    "somatic_healing": "Somatic Healing",
    "compassion_fatigue": "Compassion Fatigue",
}


def _seed(s: str) -> int:
    return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)


def _load_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _parse_stem(stem: str) -> dict:
    parts = stem.split("__")
    persona = parts[2] if len(parts) > 2 else ""
    topic = parts[3] if len(parts) > 3 else ""
    engine_part = parts[4] if len(parts) > 4 else ""
    is_1hr = stem.endswith("__1hr") or engine_part.endswith("1hr")
    engine = engine_part.replace("__1hr", "").replace("1hr", "")
    return {"persona": persona, "topic": topic, "engine": engine, "is_1hr": is_1hr}


def _persona_desc(persona_id: str, flavor: dict) -> str:
    mods = flavor.get("persona_subtitle_modifiers") or flavor
    entry = mods.get(persona_id) or mods.get("_default") or {}
    sig = (entry.get("signal") or "").strip()
    if sig:
        return sig.lstrip("— ").strip()
    return persona_id.replace("_", " ").title()


def _topic_keyword(topic: str) -> str:
    return TOPIC_DISPLAY.get(topic, topic.replace("_", " ").title())


def _engine_phrases(engine: str, angles: dict, variant: int) -> tuple[str, str]:
    card = (angles.get("engine_angles") or {}).get(engine) or {}
    pool = [card.get("subtitle_hook") or ""] + list(card.get("alt_phrases") or [])
    pool = [p for p in pool if p]
    if not pool:
        pool = [engine.replace("_", " ").title()]
    hook = pool[variant % len(pool)]
    short_pool = [card.get("primary_phrase") or ""] + list(card.get("alt_phrases") or [])
    short_pool = [p for p in short_pool if p]
    short = short_pool[(variant // max(len(pool), 1)) % len(short_pool)]
    return hook, short


def _fill_template(text: str, *, primary: str, persona: str, hook: str, short: str, fmt: str) -> str:
    return (
        text.replace("{PrimaryKeyword}", primary)
        .replace("{PersonaDescription}", persona)
        .replace("{EngineSubtitleHook}", hook)
        .replace("{EngineShortPhrase}", short)
        .replace("{FormatUnit}", fmt)
        .replace("{EngineAngle}", short)
    )


def _subtitle_templates(patterns: dict) -> dict[str, str]:
    raw = patterns.get("subtitle_templates") or {}
    out = {}
    for k, v in raw.items():
        if isinstance(v, dict):
            out[k] = v.get("text") or ""
        else:
            out[k] = str(v)
    return out


def generate_subtitle(
    book_id: str,
    persona: str,
    topic: str,
    engine: str,
    is_1hr: bool,
    templates: dict[str, str],
    angles: dict,
    flavor: dict,
    used: set[str],
) -> str:
    primary = _topic_keyword(topic)
    persona_desc = _persona_desc(persona, flavor)
    fmt = "One-Hour" if is_1hr else "Practical"
    base_seed = _seed(book_id)

    for attempt in range(120):
        tid = SUBTITLE_IDS[(base_seed + attempt) % len(SUBTITLE_IDS)]
        tpl = templates.get(tid) or templates.get("engine_hook") or "{EngineSubtitleHook} for {PersonaDescription}"
        hook, short = _engine_phrases(engine, angles, (base_seed + attempt) // len(SUBTITLE_IDS))
        sub = _fill_template(tpl, primary=primary, persona=persona_desc, hook=hook, short=short, fmt=fmt)
        sub = re.sub(r"\s+", " ", sub).strip(" ,:;—-–")
        if sub and sub not in used:
            return sub
    # Last resort: append engine disambiguator (still readable)
    hook, short = _engine_phrases(engine, angles, base_seed % 7)
    sub = f"{hook} — {primary} for {persona_desc} ({short})"
    n = 1
    while sub in used:
        sub = f"{hook} — {primary} for {persona_desc} ({short}, {n})"
        n += 1
    return sub


def _score_title(title: str, subtitle: str, persona: str, topic: str, engine: str) -> float:
    """Waystream scorer: persona-scenario in title +0.20, reduced keyword bonus, generic metaphor -0.15."""
    score = 0.0
    tl, sl = title.lower(), subtitle.lower()
    primary = _topic_keyword(topic).lower()
    persona_words = persona.replace("_", " ").lower().split()

    if primary in sl:
        score += 0.25  # reduced from 0.50 primary-in-title stacking
    if primary in tl:
        score += 0.15
    if any(w in tl for w in persona_words if len(w) > 3):
        score += 0.20  # persona_scenario_in_title
    if engine.replace("_", " ") in tl or any(w in tl for w in engine.split("_")):
        score += 0.10
    # generic topic-only metaphor penalty
    if tl.startswith(primary) and ":" not in title:
        score -= 0.15
    if len(title) > 90:
        score -= 0.20
    return score


def generate_title(
    book_id: str,
    persona: str,
    topic: str,
    engine: str,
    store_series_id: str,
    used_titles: set[str],
    skeleton_used: set[tuple[str, str]],
) -> str:
    from phoenix_v4.naming.generator import generate_candidates

    series_id = store_series_id or f"{BRAND}__{persona}__{topic}"
    _, candidates = generate_candidates(
        topic_id=topic,
        persona_id=persona,
        series_id=series_id,
        angle_id=engine,
        brand_id=BRAND,
        seed=book_id,
        installment_number=(_seed(book_id) % 7) + 1,
    )
    ranked = sorted(
        candidates,
        key=lambda c: _score_title(c.get("title") or "", c.get("subtitle") or "", persona, topic, engine),
        reverse=True,
    )
    sk = (topic, engine)
    for c in ranked:
        t = (c.get("title") or "").strip()
        if not t or t in used_titles:
            continue
        # skeleton cap: max 1 per (topic, engine) for series_metaphor/topic_metaphor skeleton
        tpl = c.get("template_used") or ""
        if tpl in ("series_metaphor", "topic_metaphor") and sk in skeleton_used:
            continue
        if tpl in ("series_metaphor", "topic_metaphor"):
            skeleton_used.add(sk)
        return t
    for c in ranked:
        t = (c.get("title") or "").strip()
        if t and t not in used_titles:
            return t
    base = ranked[0].get("title") if ranked else _topic_keyword(topic)
    n = 1
    t = base
    while t in used_titles:
        t = f"{base} ({n})"
        n += 1
    return t


def load_plans(batch: str | None = None) -> list[tuple[Path, dict]]:
    files = sorted(PLANS.glob(f"{BRAND}__*.yaml"))
    if batch == "a":
        files = files[: len(files) // 2 + len(files) % 2]
    elif batch == "b":
        files = files[len(files) // 2 + len(files) % 2 :]
    out = []
    for f in files:
        d = _load_yaml(f)
        if d.get("_needs_authoring") is False and d.get("book_id"):
            out.append((f, d))
    return out


def run(dry_run: bool, batch: str | None) -> int:
    patterns = _load_yaml(PATTERNS)
    angles = _load_yaml(ENGINE_ANGLES)
    flavor = _load_yaml(PERSONA_FLAVOR) if PERSONA_FLAVOR.exists() else {}
    templates = _subtitle_templates(patterns)

    plans = load_plans(batch)
    if not plans:
        print("no authored plans found", file=sys.stderr)
        return 1

    used_subs: set[str] = set()
    used_titles: set[str] = set()
    skeleton_used: set[tuple[str, str]] = set()
    updates: list[dict] = []

    for path, plan in plans:
        stem = path.stem
        meta = _parse_stem(stem)
        bid = plan["book_id"]
        ss = plan.get("store_series") or {}
        series_id = ss.get("id") or ""

        new_sub = generate_subtitle(
            bid, meta["persona"], meta["topic"], meta["engine"], meta["is_1hr"],
            templates, angles, flavor, used_subs,
        )
        used_subs.add(new_sub)

        new_title = generate_title(
            bid, meta["persona"], meta["topic"], meta["engine"], series_id,
            used_titles, skeleton_used,
        )
        used_titles.add(new_title)

        updates.append({
            "book_id": bid,
            "path": str(path.relative_to(REPO)),
            "old_title": plan.get("title"),
            "new_title": new_title,
            "old_subtitle": plan.get("subtitle"),
            "new_subtitle": new_sub,
        })

    titles = [u["new_title"] for u in updates]
    subs = [u["new_subtitle"] for u in updates]
    pairs = [(u["new_title"], u["new_subtitle"]) for u in updates]
    dup_t = {t: c for t, c in Counter(titles).items() if c > 1}
    dup_s = {t: c for t, c in Counter(subs).items() if c > 1}
    dup_p = {p: c for p, c in Counter(pairs).items() if c > 1}

    report = {
        "batch": batch or "all",
        "count": len(updates),
        "distinct_titles": len(set(titles)),
        "distinct_subtitles": len(set(subs)),
        "distinct_pairs": len(set(pairs)),
        "dup_titles": dup_t,
        "dup_subtitles": dup_s,
        "dup_pairs": dup_p,
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    ok = not dup_t and not dup_s and not dup_p and len(set(subs)) == len(updates)
    print(
        f"{'DRY-RUN' if dry_run else 'APPLY'}: books={len(updates)} "
        f"titles={len(set(titles))} subs={len(set(subs))} pairs={len(set(pairs))} "
        f"{'OK' if ok else 'FAIL'}"
    )
    if dup_s:
        top = sorted(dup_s.items(), key=lambda x: -x[1])[:5]
        for s, n in top:
            print(f"  dup sub x{n}: {s[:70]}...")
    if not ok:
        return 1

    if dry_run:
        print(f"artifact: {ARTIFACT}")
        return 0

    for u in updates:
        p = REPO / u["path"]
        d = _load_yaml(p)
        d["title"] = u["new_title"]
        d["subtitle"] = u["new_subtitle"]
        p.write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"applied {len(updates)} plan updates")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--batch", choices=["a", "b"], default=None)
    args = ap.parse_args()
    if not args.dry_run and not args.apply:
        ap.error("specify --dry-run or --apply")
    sys.exit(run(dry_run=args.dry_run, batch=args.batch))


if __name__ == "__main__":
    main()
