"""
Deterministic title + subtitle candidate generation. Exactly 12 candidates, seeded shuffle.
Authority: SYSTEMS_DOCUMENTATION §29.2.5.

Subtitle strategy (2026-03-19):
  - Per-brand subtitle_strategy: none_pct / short_pct / long_pct weights.
  - Per-brand content_mix: persona_direct / topic_direct / metaphor / location weights.
  - Subtitle templates tagged with {length: short|long, content: persona_direct|topic_direct|metaphor|location}.
  - Generator picks subtitle mode per candidate based on brand weights, then selects
    template from the matching length pool, biased by content_mix weights.
"""
from __future__ import annotations

import hashlib
import random
from typing import Any

from . import keyword_bank
from ._config import (
    load_location_phrases,
    load_persona_flavor,
    load_recognition_lexemes,
    load_subtitle_patterns,
)


def book_id_from_spec(
    series_id: str,
    angle_id: str,
    installment_number: int,
) -> str:
    """Produce stable book_id e.g. bk_social_anx_work_003."""
    def series_abbrev(s: str) -> str:
        parts = (s or "").replace("-", "_").split("_")[:2]
        out = []
        for p in parts:
            if not p:
                continue
            out.append("anx" if p == "anxiety" else (p if len(p) <= 6 else p[:4]))
        return "_".join(out) if out else (s[:6] if s else "bk")
    def angle_abbrev(s: str) -> str:
        parts = (s or "").replace("-", "_").split("_")
        return parts[-1] if parts else (s[:4] if s else "gen")
    ser = series_abbrev(series_id or "bk")
    ang = angle_abbrev(angle_id or "gen")
    inst = max(1, int(installment_number) if installment_number is not None else 1)
    return f"bk_{ser}_{ang}_{inst:03d}"


def _seed_int(book_id: str, persona_id: str, angle_id: str, brand_id: str) -> int:
    seed_str = f"{book_id}{persona_id}{angle_id}{brand_id}"
    seed_bytes = hashlib.sha256(seed_str.encode()).digest()
    return int.from_bytes(seed_bytes[:4], "big")


def _pick_seeded(seq: list[str], rng: random.Random, n: int = 1) -> list[str]:
    if not seq or n <= 0:
        return []
    if n >= len(seq):
        return list(seq)
    indices = rng.sample(range(len(seq)), n)
    return [seq[i] for i in indices]


def _parse_subtitle_templates(raw: dict) -> dict[str, dict]:
    """Normalize subtitle_templates: accept both old string format and new dict format."""
    out = {}
    for k, v in (raw or {}).items():
        if isinstance(v, dict):
            out[k] = v
        elif isinstance(v, str):
            # Legacy string format — classify heuristically
            length = "short" if len(v.split()) < 8 else "long"
            content = "topic_direct"
            vl = v.lower()
            if "{personadescription}" in vl:
                content = "persona_direct"
            elif "{location}" in vl:
                content = "location"
            elif any(w in vl for w in ["gentle", "stillness", "broken", "knows", "path", "proven"]):
                content = "metaphor"
            out[k] = {"text": v, "length": length, "content": content}
    return out


def _select_subtitle_mode(rng: random.Random, strategy: dict) -> str:
    """Roll seeded random to select none/short/long based on brand weights.
    Used only when no series-level mode is set."""
    none_pct = float(strategy.get("none_pct", 0.10))
    short_pct = float(strategy.get("short_pct", 0.25))
    roll = rng.random()
    if roll < none_pct:
        return "none"
    elif roll < none_pct + short_pct:
        return "short"
    else:
        return "long"


def _series_subtitle_mode(series_id: str, brand_id: str, strategy: dict) -> str:
    """Determine subtitle mode for an entire series. Deterministic by series_id + brand_id
    so all books in the same series get the same treatment. First checks
    series_templates.yaml for explicit series_subtitle_mode, then falls back to
    a deterministic pick from brand strategy weights."""
    # Check series config for explicit mode
    try:
        from pathlib import Path
        repo = Path(__file__).resolve().parent.parent.parent
        stpl = repo / "config" / "catalog_planning" / "series_templates.yaml"
        if stpl.exists():
            import yaml
            with open(stpl, encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            entry = (cfg.get("series") or {}).get(series_id) or {}
            explicit = entry.get("series_subtitle_mode")
            if explicit in ("none", "short", "long"):
                return explicit
    except Exception:
        pass
    # Deterministic fallback: hash series_id+brand_id to pick mode
    # Same series always gets same mode regardless of installment number
    digest = hashlib.sha256(f"series_mode|{series_id}|{brand_id}".encode()).digest()
    roll = (int.from_bytes(digest[:4], "big") % 1000) / 1000.0
    none_pct = float(strategy.get("none_pct", 0.10))
    short_pct = float(strategy.get("short_pct", 0.25))
    if roll < none_pct:
        return "none"
    elif roll < none_pct + short_pct:
        return "short"
    else:
        return "long"


def _weighted_pick(templates: list[tuple[str, dict]], content_mix: dict, rng: random.Random) -> tuple[str, dict] | None:
    """Pick a subtitle template weighted by content_mix preference."""
    if not templates:
        return None
    weights = []
    for tid, tinfo in templates:
        tag = tinfo.get("content", "metaphor")
        w = float(content_mix.get(tag, 0.25))
        weights.append(max(w, 0.01))  # floor to avoid zero
    total = sum(weights)
    probs = [w / total for w in weights]
    r = rng.random()
    cumul = 0.0
    for i, p in enumerate(probs):
        cumul += p
        if r <= cumul:
            return templates[i]
    return templates[-1]


def _dedup_subtitle_vs_title(title: str, subtitle: str) -> str:
    """Remove exact repeated multi-word phrases from subtitle that already appear in title.
    Per deep research: Amazon ignores redundant keywords and may flag as stuffing.
    Keeps short function words. Only strips phrases of 2+ content words."""
    if not subtitle or not title:
        return subtitle
    title_lower = title.lower()
    # Extract content words from title (skip short function words)
    stop = {"a", "an", "the", "to", "for", "and", "or", "in", "of", "is", "on", "by", "at", "how", "who", "what", "that", "your", "you", "do", "not"}
    title_words = set(w.lower() for w in title.split() if len(w) > 2 and w.lower() not in stop)
    if not title_words:
        return subtitle
    # Check if PrimaryKeyword phrase from title appears in subtitle
    # e.g. title="Anxiety Relief: A Clear Path" → remove "Anxiety Relief" from subtitle
    # Work at phrase level: find 2+ word sequences from title in subtitle
    result = subtitle
    title_tokens = title.lower().split()
    for window in range(min(4, len(title_tokens)), 1, -1):
        for start in range(len(title_tokens) - window + 1):
            phrase = " ".join(title_tokens[start:start + window])
            phrase_words = set(phrase.split()) - stop
            if len(phrase_words) >= 2 and phrase in result.lower():
                # Remove the phrase (case-insensitive)
                import re
                result = re.sub(re.escape(phrase), "", result, flags=re.IGNORECASE).strip()
                # Clean up double spaces and leading/trailing punctuation
                result = re.sub(r"\s+", " ", result).strip(" ,:;—-–")
    return result


def generate_candidates(
    topic_id: str,
    persona_id: str,
    series_id: str,
    angle_id: str,
    brand_id: str,
    seed: str,
    installment_number: int = 1,
    location: str = "",
) -> tuple[str, list[dict[str, Any]]]:
    """
    Returns (book_id, list of 12 candidate dicts).
    Each candidate: title, subtitle, subtitle_mode (none/short/long),
    content_tag, template_used, candidate_id, intent.
    """
    bid = book_id_from_spec(series_id, angle_id, installment_number)
    seed_int = _seed_int(bid, persona_id, angle_id, brand_id)
    rng = random.Random(seed_int)

    keywords = keyword_bank.get_keywords(series_id, angle_id, topic_id, engine_id=angle_id)
    primary = (keywords.get("primary") or topic_id.replace("_", " ")).title()
    # Curated reader-facing series title (e.g. "The Alarm Is Lying"); falls back to
    # the topic keyword so {SeriesTitle} is always topic-true, never an engine angle.
    series_title_val = keywords.get("series_title") or primary
    secondary = keywords.get("secondary") or []
    engine_angle = keywords.get("engine_angle") or angle_id.replace("_", " ").title()
    # Rotate the engine angle deterministically across the {primary_phrase, *alt_phrases}
    # pool keyed by this book's seed, so creative ({EngineAngle}) titles vary per book
    # instead of every book on an engine collapsing to the single primary_phrase.
    # Falls back to the resolved engine_angle when no angle pool exists.
    angle_pool = keyword_bank.get_engine_angle_pool(angle_id) if hasattr(keyword_bank, "get_engine_angle_pool") else []
    if angle_pool:
        engine_angle = angle_pool[seed_int % len(angle_pool)]
    scenario_phrase = engine_angle

    # Engine subtitle hook from engine_title_angles.yaml
    engine_subtitle_hook = keyword_bank.get_engine_subtitle_hook(angle_id)

    patterns = load_subtitle_patterns()
    title_tpl = (patterns.get("title_templates") or {}).copy()
    raw_subtitle_tpl = (patterns.get("subtitle_templates") or {}).copy()
    subtitle_tpl = _parse_subtitle_templates(raw_subtitle_tpl)

    brand_prefs = (patterns.get("brand_template_preferences") or {}).get(brand_id) or \
                  (patterns.get("brand_template_preferences") or {}).get("default") or {}
    preferred_title = list(brand_prefs.get("title") or ["scenario_direct"])
    preferred_sub = list(brand_prefs.get("subtitle") or ["micro_promise"])
    subtitle_strategy = brand_prefs.get("subtitle_strategy") or {"none_pct": 0.10, "short_pct": 0.25, "long_pct": 0.65}
    content_mix = brand_prefs.get("content_mix") or {"persona_direct": 0.20, "topic_direct": 0.40, "metaphor": 0.30, "location": 0.10}

    micro_promises_cfg = patterns.get("micro_promises") or {}
    micro_list = micro_promises_cfg.get(brand_id) or micro_promises_cfg.get("default") or [
        "How to Stop Freezing and Speak Up with Confidence"
    ]

    flavor = load_persona_flavor()
    personas_cfg = flavor.get("personas") or {}
    persona_cfg = personas_cfg.get(persona_id) or personas_cfg.get("default") or {}
    persona_desc = persona_cfg.get("persona_role") or persona_id.replace("_", " ").title()
    title_tone = persona_cfg.get("title_tone") or "Readers"

    lex = load_recognition_lexemes()
    distress_verbs = list(lex.get("distress_verbs") or ["freeze", "panic", "overthink"])
    outcome_phrases = list(lex.get("outcome_phrases") or ["speak up", "feel confident", "find calm"])
    rng.shuffle(distress_verbs)
    rng.shuffle(outcome_phrases)
    dv = (distress_verbs[0] or "freeze").lower()
    distress_verb = dv.title()
    distress_verb_ing = (dv + "ing") if not dv.endswith("e") else (dv.rstrip("e") + "ing")
    distress_verb_ing = distress_verb_ing.title()
    outcome_verb = (outcome_phrases[0] or "feel confident").title()
    action1 = (outcome_phrases[1 % len(outcome_phrases)] or "speak up").title()
    action2 = (outcome_phrases[2 % len(outcome_phrases)] or "stop worrying").title()
    action3 = (outcome_phrases[3 % len(outcome_phrases)] or "find calm").title()
    promise_clause = rng.choice(micro_list) if micro_list else "How to Find Calm and Show Up"
    loc = location or ""

    # Pre-load location phrases early so we can resolve city_name for {Location}
    loc_phrases: dict = {}
    loc_title_colors: list = []
    loc_subtitle_scenes: list = []
    loc_transit: list = []
    loc_neighborhoods: list = []
    loc_city_name = loc  # fallback to raw key
    if loc:
        all_loc = load_location_phrases()
        loc_key = loc.lower().replace(" ", "_").replace("-", "_")
        loc_phrases = all_loc.get(loc_key) or {}
        loc_city_name = loc_phrases.get("city_name") or loc.replace("_", " ").title()
        loc_title_colors = list(loc_phrases.get("title_color") or [])
        loc_subtitle_scenes = list(loc_phrases.get("subtitle_scene") or [])
        loc_transit = list(loc_phrases.get("transit_hooks") or [])
        loc_neighborhoods = list(loc_phrases.get("neighborhood_hooks") or [])
        if loc_title_colors:
            rng.shuffle(loc_title_colors)
        if loc_subtitle_scenes:
            rng.shuffle(loc_subtitle_scenes)

    n_sessions = 8
    format_unit = "sessions"

    def fill(s: str) -> str:
        return (s or "") \
            .replace("{PrimaryKeyword}", primary) \
            .replace("{SeriesTitle}", series_title_val) \
            .replace("{ScenarioPhrase}", scenario_phrase) \
            .replace("{EngineAngle}", engine_angle) \
            .replace("{EngineSubtitleHook}", engine_subtitle_hook or f"A Deeper Look at {engine_angle}") \
            .replace("{PersonaDescription}", persona_desc) \
            .replace("{PromiseClause}", promise_clause) \
            .replace("{DistressVerb}", distress_verb) \
            .replace("{DistressVerbIng}", distress_verb_ing) \
            .replace("{OutcomeVerb}", outcome_verb) \
            .replace("{Action1}", action1) \
            .replace("{Action2}", action2) \
            .replace("{Action3}", action3) \
            .replace("{N}", str(n_sessions)) \
            .replace("{FormatUnit}", format_unit) \
            .replace("{Location}", loc_city_name)

    # ── Location-aware phrases (inject into template pools) ──
    if loc:
        # Inject location subtitle_scenes as additional long subtitle templates.
        # These have city-SPECIFIC details (neighborhoods, transit, streets).
        for i, sc in enumerate(loc_subtitle_scenes[:6]):
            subtitle_tpl[f"loc_scene_{i}"] = {"text": sc, "length": "long", "content": "location"}
        # Title_colors go in as alternate title templates (mood/vibe, not specifics)
        for i, tc in enumerate(loc_title_colors[:3]):
            title_tpl[f"loc_color_{i}"] = tc

    # Split subtitle pool by length
    short_pool = [(k, v) for k, v in subtitle_tpl.items() if v.get("length") == "short"]
    long_pool = [(k, v) for k, v in subtitle_tpl.items() if v.get("length") == "long"]

    # Preferred subtitle IDs (subset for tier ordering)
    preferred_sub_set = set(preferred_sub)
    pref_short = [(k, v) for k, v in short_pool if k in preferred_sub_set]
    pref_long = [(k, v) for k, v in long_pool if k in preferred_sub_set]

    # Build title template tiers
    title_names = list(title_tpl.keys())
    preferred_title_set = set(preferred_title)

    # ── Series-level subtitle mode ──
    # All books in the same series use the SAME subtitle mode for cohesion.
    # This is what makes a series feel like a series on the shelf.
    # Mode varies ACROSS series (brand strategy) but is CONSISTENT within one.
    series_mode = _series_subtitle_mode(series_id, brand_id, subtitle_strategy)

    # For short mode, determine colon-join vs split ONCE for the series too.
    short_in_title_pct = float(subtitle_strategy.get("short_in_title_pct", 0.60))
    series_short_joined = False
    if series_mode == "short":
        # Deterministic by series — same series always gets same join/split treatment
        join_digest = hashlib.sha256(f"short_join|{series_id}|{brand_id}".encode()).digest()
        series_short_joined = (int.from_bytes(join_digest[:4], "big") % 100) / 100.0 < short_in_title_pct

    # Generate 12 candidates — all use the same series_mode for the primary candidate.
    # Candidates 1-8 use series_mode (cohesive). Candidates 9-12 use alternate modes
    # (so editorial can see what other treatments look like if they want to override).
    seen = set()
    seen_subtitles = set()  # Prevent duplicate subtitle TEXT within candidates
    candidates = []

    for attempt in range(80):
        if len(candidates) >= 12:
            break

        # Pick title template: brand-preferred first.
        # The brand's declared `title:` list is authoritative — falling back to
        # the full template set let keyword-in-title skeletons (e.g.
        # "{PrimaryKeyword} for {PersonaDescription}") leak in and, because the
        # scorer rewards primary-in-title (0.50) over primary-in-subtitle (0.30),
        # those outscored the brand's creative/emotional titles. Per
        # persona_in_titles_strategy_research.md the keyword belongs in the
        # SUBTITLE and the title stays creative, so draw the fallback from the
        # brand's preferred titles plus any location-injected title colors.
        if attempt < len(preferred_title) * 4:
            tn = preferred_title[attempt % len(preferred_title)]
        else:
            fallback_titles = list(preferred_title) + [k for k in title_names if k.startswith("loc_color_")]
            tn = rng.choice(fallback_titles or title_names)

        t_tpl = title_tpl.get(tn, "{PrimaryKeyword}")
        title_text = fill(t_tpl)

        # First 8 candidates: series mode. Last 4: alternate modes for editorial.
        if len(candidates) < 8:
            mode = series_mode
        else:
            mode = _select_subtitle_mode(rng, subtitle_strategy)

        if mode == "none":
            subtitle_text = ""
            content_tag = "none"
            sub_template = "none"
        elif mode == "short":
            pool = pref_short if (pref_short and attempt < 6) else (short_pool if short_pool else long_pool)
            pick = _weighted_pick(pool, content_mix, rng)
            if pick:
                sub_template, sub_info = pick
                subtitle_text = fill(sub_info.get("text", ""))
                content_tag = sub_info.get("content", "metaphor")
                # Enforce unique subtitle text within this candidate set
                if subtitle_text in seen_subtitles:
                    # Try another template
                    remaining = [(k, v) for k, v in (short_pool if short_pool else long_pool) if fill(v.get("text", "")) not in seen_subtitles]
                    if remaining:
                        pick2 = _weighted_pick(remaining, content_mix, rng)
                        if pick2:
                            sub_template, sub_info = pick2
                            subtitle_text = fill(sub_info.get("text", ""))
                            content_tag = sub_info.get("content", "metaphor")
            else:
                subtitle_text = ""
                content_tag = "none"
                sub_template = "none"
        else:  # long
            pool = pref_long if (pref_long and attempt < 6) else (long_pool if long_pool else short_pool)
            pick = _weighted_pick(pool, content_mix, rng)
            if pick:
                sub_template, sub_info = pick
                subtitle_text = fill(sub_info.get("text", ""))
                content_tag = sub_info.get("content", "metaphor")
                if subtitle_text in seen_subtitles:
                    remaining = [(k, v) for k, v in (long_pool if long_pool else short_pool) if fill(v.get("text", "")) not in seen_subtitles]
                    if remaining:
                        pick2 = _weighted_pick(remaining, content_mix, rng)
                        if pick2:
                            sub_template, sub_info = pick2
                            subtitle_text = fill(sub_info.get("text", ""))
                            content_tag = sub_info.get("content", "metaphor")
            else:
                subtitle_text = ""
                content_tag = "none"
                sub_template = "none"

        # Deep research fix: strip keyword phrases from subtitle that repeat title words.
        # Amazon ignores redundant keywords and may flag as "keyword stuffing".
        if subtitle_text and title_text:
            subtitle_text = _dedup_subtitle_vs_title(title_text, subtitle_text)

        # Format display: colon-join for short mode uses series-level decision
        if mode == "short" and subtitle_text:
            if series_short_joined and ":" not in title_text:
                display_title = f"{title_text}: {subtitle_text}"
                display_subtitle = ""
            else:
                display_title = title_text
                display_subtitle = subtitle_text
        elif mode == "none":
            display_title = title_text
            display_subtitle = ""
        else:
            display_title = title_text
            display_subtitle = subtitle_text

        key = (display_title, display_subtitle)
        if key in seen:
            continue
        seen.add(key)
        if subtitle_text:
            seen_subtitles.add(subtitle_text)

        candidates.append({
            "title": display_title,
            "subtitle": display_subtitle,
            "subtitle_mode": mode,
            "series_mode": series_mode,
            "content_tag": content_tag,
            "template_used": tn,
            "subtitle_template": sub_template if mode != "none" else "none",
            "template_id": f"T{len(candidates)+1:03d}",
            "candidate_id": f"cand_{len(candidates)+1:03d}",
            "intent": "scenario_specific",
        })

    # ── Location enforcement ──
    # HARD RULE: If --location is set, candidate #1 MUST have a city-SPECIFIC
    # reference in the title or subtitle. "Specific" means transit lines, neighborhoods,
    # streets, cultural touchstones — NOT generic mood phrases like "The City That
    # Keeps You Up" which could be any city.
    #
    # Strategy: engine_angle stays as title (series identity), subtitle_scene provides
    # the unmistakable city grounding (Bushwick, the 6 train, Houston Street, etc).
    # This gives both: book identity + location specificity.
    if loc and loc_subtitle_scenes:
        # Pick a scene for this installment — deterministic and unique per installment.
        # Assign each installment a unique scene using modular indexing on a
        # stable sort. Sort scenes deterministically first, then offset by
        # installment number so no two installments in the same series collide.
        _sorted_scenes = sorted(loc_subtitle_scenes)
        scene_idx = (installment_number - 1) % len(_sorted_scenes)
        loc_scene = _sorted_scenes[scene_idx]
        # Build the location-grounded primary candidate
        loc_primary = {
            "title": engine_angle,
            "subtitle": loc_scene,
            "subtitle_mode": "long",
            "series_mode": series_mode,
            "content_tag": "location",
            "template_used": "metaphor_title",
            "subtitle_template": "loc_scene_enforced",
            "template_id": "T000",
            "candidate_id": "cand_000",
            "intent": "location_grounded",
        }
        # Insert as #1, push everything else down
        candidates.insert(0, loc_primary)

    return bid, candidates[:12]
