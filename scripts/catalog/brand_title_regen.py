#!/usr/bin/env python3
"""Regenerate book-plan titles + subtitles for any brand (Formula 4 contract).

Generalizes the Waystream regen path: distinct titles/subs/pairs, hook-first
titles, persona-in-subtitle, Formula-4 validator pass on every row.

  PYTHONPATH=. python3 scripts/catalog/brand_title_regen.py --brand adhd_forge --dry-run
  PYTHONPATH=. python3 scripts/catalog/brand_title_regen.py --brand stabilizer --apply --batch a
  PYTHONPATH=. python3 scripts/catalog/brand_title_regen.py --brand way_stream_sanctuary --apply --authored-only
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
ENGINE_ANGLES = REPO / "config/catalog_planning/engine_title_angles.yaml"
PATTERNS = REPO / "omega/title_entropy/subtitle_patterns.yaml"
PERSONA_FLAVOR = REPO / "omega/title_entropy/persona_title_flavor.yaml"

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
    "overthinking": "Overthinking",
    "anxiety": "Anxiety",
    "burnout": "Burnout",
    "grief": "Grief",
    "boundaries": "Boundaries",
    "depression": "Depression",
    "courage": "Courage",
    "adhd_focus": "ADHD Focus",
    "focus": "Focus",
}


@dataclass
class RegenConfig:
    brand_id: str
    locale_dir: str = "en_us"
    authored_only: bool = False

    @property
    def plans_dir(self) -> Path:
        return REPO / f"config/source_of_truth/book_plans_{self.locale_dir}"

    @property
    def artifact_path(self) -> Path:
        return REPO / f"artifacts/naming/{self.brand_id}/title_regen_report.json"

    @property
    def analysis_path(self) -> Path:
        return REPO / f"artifacts/naming/{self.brand_id}/title_format_analysis.json"


_CFG: RegenConfig | None = None


def _cfg() -> RegenConfig:
    if _CFG is None:
        raise RuntimeError("RegenConfig not initialized")
    return _CFG


def _seed(s: str) -> int:
    return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)


def _load_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _fast_read_plan(path: Path, *, authored_only: bool) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if authored_only and not re.search(r"^_needs_authoring:\s*false\s*$", text, re.M | re.I):
        return None

    def _field(name: str) -> str:
        m = re.search(rf"^{name}:\s*(.+)$", text, re.M)
        return (m.group(1).strip().strip('"\'') if m else "")

    book_id = _field("book_id") or path.stem
    series_id = ""
    m_ss = re.search(r"^store_series:\s*\n(?:  .+\n)*?  id:\s*(.+)$", text, re.M)
    if m_ss:
        series_id = m_ss.group(1).strip().strip('"\'')

    return {
        "book_id": book_id,
        "title": _field("title"),
        "subtitle": _field("subtitle"),
        "store_series": {"id": series_id} if series_id else {},
    }


def _parse_stem(stem: str) -> dict:
    parts = stem.split("__")
    persona = parts[2] if len(parts) > 2 else ""
    topic = parts[3] if len(parts) > 3 else ""
    engine_part = parts[4] if len(parts) > 4 else ""
    is_1hr = stem.endswith("__1hr") or engine_part.endswith("1hr")
    engine = engine_part.replace("__1hr", "").replace("1hr", "")
    return {"persona": persona, "topic": topic, "engine": engine, "is_1hr": is_1hr}


def _persona_desc(persona_id: str, flavor: dict) -> str:
    personas = flavor.get("personas") or flavor.get("persona_subtitle_modifiers") or flavor
    entry = personas.get(persona_id) or personas.get("_default") or personas.get("default") or {}
    role = (entry.get("persona_role") or entry.get("signal") or "").strip()
    if role:
        return role.lstrip("— ").strip()
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


def _validate_pair(title: str, subtitle: str, topic: str, persona: str, flavor: dict) -> tuple[bool, str]:
    from phoenix_v4.naming.validator import validate_formula4

    primary = _topic_keyword(topic)
    persona_desc = _persona_desc(persona, flavor)
    return validate_formula4(title, subtitle, primary, persona_desc, persona)


def _fit_formula4_budget(
    title: str,
    subtitle: str,
    topic: str,
    persona: str,
    engine: str,
    flavor: dict,
    angles: dict,
    variant: int,
) -> tuple[str, str]:
    from phoenix_v4.naming.validator import validate_formula4

    primary = _topic_keyword(topic)
    persona_desc = _persona_desc(persona, flavor)
    ok, _ = validate_formula4(title, subtitle, primary, persona_desc, persona)
    if ok:
        return title, subtitle

    _, short = _engine_phrases(engine, angles, variant)
    compact_subs = [
        f"A Field Guide to {primary} for {persona_desc}",
        f"Practical {primary} Tools for {persona_desc}",
        f"{short} — for {persona_desc}",
        f"A Guide to {primary} for {persona_desc}",
    ]
    for sub in compact_subs:
        sub = re.sub(r"\s+", " ", sub).strip()
        ok, _ = validate_formula4(title, sub, primary, persona_desc, persona)
        if ok:
            return title, sub

    words = subtitle.split()
    while len(words) > 6:
        words = words[:-1]
        sub = " ".join(words).strip(" ,:;—-–")
        ok, _ = validate_formula4(title, sub, primary, persona_desc, persona)
        if ok:
            return title, sub

    return title, compact_subs[0]


def _persona_fallback_subtitle(topic: str, persona: str, engine: str, flavor: dict, angles: dict, variant: int) -> str:
    primary = _topic_keyword(topic)
    persona_desc = _persona_desc(persona, flavor)
    _, short = _engine_phrases(engine, angles, variant)
    candidates = [
        f"A Practical Field Guide to {primary} for {persona_desc} Navigating {short}",
        f"Real Tools for {primary} — Written for {persona_desc} Who Need a Reset",
        f"How {persona_desc} Can Work Through {primary} Without Burning Out Again",
        f"A Clear Path Through {primary} — A Guide for {persona_desc}",
    ]
    return candidates[variant % len(candidates)]


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

    for attempt in range(40):
        tid = SUBTITLE_IDS[(base_seed + attempt) % len(SUBTITLE_IDS)]
        tpl = templates.get(tid) or templates.get("engine_hook") or "{EngineSubtitleHook} for {PersonaDescription}"
        hook, short = _engine_phrases(engine, angles, (base_seed + attempt) // len(SUBTITLE_IDS))
        sub = _fill_template(tpl, primary=primary, persona=persona_desc, hook=hook, short=short, fmt=fmt)
        sub = re.sub(r"\s+", " ", sub).strip(" ,:;—-–")
        ok, _ = _validate_pair("Hook Placeholder: " + primary, sub, topic, persona, flavor)
        if sub and sub not in used and ok:
            return sub

    for attempt in range(40):
        sub = _persona_fallback_subtitle(topic, persona, engine, flavor, angles, base_seed + attempt)
        sub = re.sub(r"\s+", " ", sub).strip()
        ok, _ = _validate_pair("Hook Placeholder: " + primary, sub, topic, persona, flavor)
        if sub not in used and ok:
            return sub

    sub = _persona_fallback_subtitle(topic, persona, engine, flavor, angles, base_seed)
    n = 1
    while sub in used:
        sub = f"{sub} — edition {n}"
        n += 1
    return sub


def _score_title(title: str, subtitle: str, persona: str, topic: str, engine: str, flavor: dict) -> float:
    score = 0.0
    tl, sl = title.lower(), subtitle.lower()
    primary = _topic_keyword(topic).lower()
    ok, _ = _validate_pair(title, subtitle, topic, persona, flavor)
    score += 2.0 if ok else -1.5

    if ":" in title:
        pre, _, post = title.partition(":")
        pre_l, post_l = pre.lower(), post.lower()
        if primary not in pre_l and primary in post_l:
            score += 1.0
        if primary in pre_l:
            score -= 2.0

    persona_tokens = _persona_desc(persona, flavor).lower().split()
    if any(w in sl for w in persona_tokens if len(w) > 3):
        score += 0.3

    if engine.replace("_", " ") in tl:
        score += 0.05
    if len(title) > 90:
        score -= 0.20
    return score


def _fallback_titles(engine: str, topic: str, series_title: str, angles: dict, variant: int) -> list[str]:
    primary = _topic_keyword(topic)
    _, short = _engine_phrases(engine, angles, variant)
    card = (angles.get("engine_angles") or {}).get(engine) or {}
    hooks = list(dict.fromkeys(
        [card.get("primary_phrase") or ""]
        + list(card.get("alt_phrases") or [])
        + [short, series_title]
    ))
    hooks = [h for h in hooks if h and primary.lower() not in h.lower()]
    out: list[str] = []
    seen: set[str] = set()
    for h in hooks:
        for t in (
            f"{h}: A Guide to {primary}",
            f"{series_title}: {primary} and {short}",
            f"{h}: When {primary} Takes Over",
            f"{series_title}: {primary}",
            f"{h}: {primary}",
        ):
            if t not in seen:
                seen.add(t)
                out.append(t)
    return out


def generate_title(
    book_id: str,
    brand_id: str,
    persona: str,
    topic: str,
    engine: str,
    store_series_id: str,
    subtitle: str,
    used_titles: set[str],
    skeleton_used: set[tuple[str, str]],
    flavor: dict,
    angles: dict,
) -> str:
    from phoenix_v4.naming import keyword_bank
    from phoenix_v4.naming.generator import generate_candidates

    series_id = store_series_id or f"{brand_id}__{persona}__{topic}"
    keywords = keyword_bank.get_keywords(series_id, engine, topic, engine_id=engine)
    series_title = keywords.get("series_title") or _topic_keyword(topic)
    base_seed = _seed(book_id)

    for variant in range(48):
        for t in _fallback_titles(engine, topic, series_title, angles, base_seed + variant):
            if t in used_titles:
                continue
            ok, _ = _validate_pair(t, subtitle, topic, persona, flavor)
            if ok:
                return t

    _, candidates = generate_candidates(
        topic_id=topic,
        persona_id=persona,
        series_id=series_id,
        angle_id=engine,
        brand_id=brand_id,
        seed=f"{book_id}|f4",
        installment_number=(base_seed % 7) + 1,
    )
    ranked = sorted(
        candidates,
        key=lambda c: _score_title(
            c.get("title") or "", subtitle, persona, topic, engine, flavor,
        ),
        reverse=True,
    )
    sk = (topic, engine)
    for c in ranked:
        t = (c.get("title") or "").strip()
        if not t or t in used_titles:
            continue
        ok, _ = _validate_pair(t, subtitle, topic, persona, flavor)
        if not ok:
            continue
        tpl = c.get("template_used") or ""
        if tpl in ("series_metaphor", "formula4_series") and sk in skeleton_used:
            continue
        if tpl in ("series_metaphor", "formula4_series"):
            skeleton_used.add(sk)
        return t

    t = f"The Turning Point: A Guide to {_topic_keyword(topic)}"
    n = 1
    while t in used_titles:
        t = f"The Turning Point: {_topic_keyword(topic)} ({n})"
        n += 1
    return t


def load_plans(cfg: RegenConfig, batch: str | None = None) -> list[tuple[Path, dict]]:
    files = sorted(cfg.plans_dir.glob(f"{cfg.brand_id}__*.yaml"))
    if batch == "a":
        files = files[: len(files) // 2 + len(files) % 2]
    elif batch == "b":
        files = files[len(files) // 2 + len(files) % 2 :]
    out = []
    for f in files:
        d = _fast_read_plan(f, authored_only=cfg.authored_only)
        if d:
            out.append((f, d))
    return out


def _seed_used_from_sibling_batch(cfg: RegenConfig, batch: str | None) -> tuple[set[str], set[str], set[tuple[str, str]]]:
    """When applying batch b, reserve titles/subs already written by batch a."""
    if batch != "b":
        return set(), set(), set()
    all_files = sorted(cfg.plans_dir.glob(f"{cfg.brand_id}__*.yaml"))
    split = len(all_files) // 2 + len(all_files) % 2
    used_titles: set[str] = set()
    used_subs: set[str] = set()
    for f in all_files[:split]:
        d = _fast_read_plan(f, authored_only=cfg.authored_only)
        if not d:
            continue
        used_titles.add((d.get("title") or "").strip())
        used_subs.add((d.get("subtitle") or "").strip())
    return used_titles, used_subs, set()


def _split_colon(title: str) -> tuple[str, str]:
    if ":" not in title:
        return title.strip(), ""
    pre, _, post = title.partition(":")
    return pre.strip(), post.strip()


def analyze_patterns(plans: list[tuple[Path, dict]], flavor: dict) -> dict:
    n = len(plans)
    keyword_first = hook_first = persona_in_sub = echoes = over_budget = 0

    for path, plan in plans:
        title = (plan.get("title") or "").strip()
        subtitle = (plan.get("subtitle") or "").strip()
        meta = _parse_stem(path.stem)
        primary = _topic_keyword(meta["topic"]).lower()
        pre, post = _split_colon(title)
        pre_l = pre.lower()

        if primary and primary in pre_l:
            keyword_first += 1
        if primary and primary not in pre_l and (primary in post.lower() or primary in subtitle.lower()):
            hook_first += 1

        persona_desc = _persona_desc(meta["persona"], flavor).lower()
        persona_tokens = [w for w in persona_desc.split() if len(w) > 2]
        persona_id_tokens = [w for w in meta["persona"].replace("_", " ").lower().split() if len(w) > 2]
        check_tokens = list(dict.fromkeys(persona_tokens + persona_id_tokens))
        if check_tokens and any(tok in subtitle.lower() for tok in check_tokens):
            persona_in_sub += 1

        from phoenix_v4.naming.validator import _subtitle_echoes_title
        if _subtitle_echoes_title(title, subtitle):
            echoes += 1
        if len(f"{title} {subtitle}".strip()) > 120:
            over_budget += 1

    return {
        "count": n,
        "keyword_first_inverted_pct": round(100 * keyword_first / max(n, 1), 1),
        "hook_first_pct": round(100 * hook_first / max(n, 1), 1),
        "persona_in_subtitle_pct": round(100 * persona_in_sub / max(n, 1), 1),
        "subtitle_echo_pct": round(100 * echoes / max(n, 1), 1),
        "over_budget_pct": round(100 * over_budget / max(n, 1), 1),
    }


def run_regen(
    cfg: RegenConfig,
    *,
    dry_run: bool,
    batch: str | None,
    analyze_only: bool = False,
) -> int:
    global _CFG
    _CFG = cfg

    patterns = _load_yaml(PATTERNS)
    angles = _load_yaml(ENGINE_ANGLES)
    flavor = _load_yaml(PERSONA_FLAVOR) if PERSONA_FLAVOR.exists() else {}

    plans = load_plans(cfg, batch)
    if not plans:
        print(f"no plans found for brand={cfg.brand_id} in {cfg.plans_dir}", file=sys.stderr)
        return 1

    before = analyze_patterns(plans, flavor)
    cfg.analysis_path.parent.mkdir(parents=True, exist_ok=True)
    if analyze_only:
        cfg.analysis_path.write_text(json.dumps({"before": before, "brand": cfg.brand_id}, indent=2), encoding="utf-8")
        print(json.dumps({"brand": cfg.brand_id, **before}, indent=2))
        return 0

    templates = _subtitle_templates(patterns)
    used_titles, used_subs, skeleton_used = _seed_used_from_sibling_batch(cfg, batch)
    if not skeleton_used:
        skeleton_used = set()
    updates: list[dict] = []

    for path, plan in plans:
        meta = _parse_stem(path.stem)
        bid = plan["book_id"]
        ss = plan.get("store_series") or {}
        series_id = ss.get("id") or ""

        new_sub = generate_subtitle(
            bid, meta["persona"], meta["topic"], meta["engine"], meta["is_1hr"],
            templates, angles, flavor, used_subs,
        )
        new_title = generate_title(
            bid, cfg.brand_id, meta["persona"], meta["topic"], meta["engine"], series_id,
            new_sub, used_titles, skeleton_used, flavor, angles,
        )
        new_title, new_sub = _fit_formula4_budget(
            new_title, new_sub, meta["topic"], meta["persona"], meta["engine"],
            flavor, angles, _seed(bid),
        )
        n = 1
        while new_sub in used_subs:
            persona_desc = _persona_desc(meta["persona"], flavor)
            new_sub = f"A Guide to {_topic_keyword(meta['topic'])} for {persona_desc} ({n})"
            n += 1
        used_subs.add(new_sub)
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

    after_plans = [(REPO / u["path"], {"title": u["new_title"], "subtitle": u["new_subtitle"]}) for u in updates]
    after = analyze_patterns(after_plans, flavor)

    formula4_pass = sum(
        1 for u in updates
        if _validate_pair(
            u["new_title"], u["new_subtitle"],
            _parse_stem(Path(u["path"]).stem)["topic"],
            _parse_stem(Path(u["path"]).stem)["persona"],
            flavor,
        )[0]
    )

    report = {
        "brand": cfg.brand_id,
        "locale_dir": cfg.locale_dir,
        "authored_only": cfg.authored_only,
        "batch": batch or "all",
        "count": len(updates),
        "distinct_titles": len(set(titles)),
        "distinct_subtitles": len(set(subs)),
        "distinct_pairs": len(set(pairs)),
        "dup_titles": dup_t,
        "dup_subtitles": dup_s,
        "dup_pairs": dup_p,
        "pattern_before": before,
        "pattern_after": after,
        "formula4_pass": formula4_pass,
        "formula4_pass_pct": round(100 * formula4_pass / max(len(updates), 1), 1),
        "samples": updates[:10],
    }
    cfg.artifact_path.parent.mkdir(parents=True, exist_ok=True)
    cfg.artifact_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    cfg.analysis_path.write_text(json.dumps({"before": before, "after": after}, indent=2), encoding="utf-8")

    ok = (
        not dup_t and not dup_s and not dup_p
        and len(set(subs)) == len(updates)
        and formula4_pass == len(updates)
    )
    print(
        f"{'DRY-RUN' if dry_run else 'APPLY'} brand={cfg.brand_id}: books={len(updates)} "
        f"titles={len(set(titles))} subs={len(set(subs))} pairs={len(set(pairs))} "
        f"formula4={formula4_pass}/{len(updates)} "
        f"hook_first {before['hook_first_pct']}%→{after['hook_first_pct']}% "
        f"persona {before['persona_in_subtitle_pct']}%→{after['persona_in_subtitle_pct']}% "
        f"echo {before['subtitle_echo_pct']}%→{after['subtitle_echo_pct']}% "
        f"{'OK' if ok else 'FAIL'}"
    )
    if not ok:
        return 1

    if dry_run:
        print(f"artifact: {cfg.artifact_path}")
        return 0

    for u in updates:
        p = REPO / u["path"]
        d = _load_yaml(p)
        d["title"] = u["new_title"]
        d["subtitle"] = u["new_subtitle"]
        p.write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"applied {len(updates)} plan updates for {cfg.brand_id}")
    return 0


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Formula-4 title+subtitle regen for any brand")
    ap.add_argument("--brand", required=True, help="brand_id (e.g. adhd_forge, stabilizer)")
    ap.add_argument("--locale-dir", default="en_us", help="book_plans subdir suffix (default en_us)")
    ap.add_argument("--authored-only", action="store_true", help="skip _needs_authoring:true skeletons")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--analyze", action="store_true", help="Pattern analysis on current plans only")
    ap.add_argument("--batch", choices=["a", "b"], default=None)
    args = ap.parse_args(argv)

    cfg = RegenConfig(
        brand_id=args.brand,
        locale_dir=args.locale_dir,
        authored_only=args.authored_only,
    )
    if args.analyze:
        sys.exit(run_regen(cfg, dry_run=True, batch=args.batch, analyze_only=True))
    if not args.dry_run and not args.apply:
        ap.error("specify --dry-run, --apply, or --analyze")
    sys.exit(run_regen(cfg, dry_run=args.dry_run, batch=args.batch))


if __name__ == "__main__":
    main()
