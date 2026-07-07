"""Story architecture internal artifact — handoff produced via transmission."""

from __future__ import annotations

import hashlib
from typing import Any, Optional

# M4: mode vessels are loaded via the existing loader (call-reachability).
# Additive — no behavior change unless ``mode`` is set on the series.


# ── Beat templates per arc stage ────────────────────────────────────
# Each stage defines a pool of beat templates. A deterministic hash
# selects and fills them so the same series_id + arc_id always
# produces the same story, but different inputs produce different
# stories.

_BEAT_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "setup": [
        {"text": "Wide establishing shot of {setting}. Dawn light, stillness before the day.", "camera": "wide", "mood": "calm", "carrier": True},
        {"text": "{protagonist} appears in silhouette against {setting}. Their posture tells a story before any word is spoken.", "camera": "medium", "mood": "neutral", "carrier": False},
        {"text": "Close on {protagonist}'s hands — fidgeting, gripping, or still. The body knows what the mind hasn't admitted.", "camera": "close-up", "mood": "tense", "carrier": True},
        {"text": "{protagonist} walks through the familiar space. Everything looks the same. Something has shifted.", "camera": "medium", "mood": "neutral", "carrier": False},
        {"text": "A small detail catches {protagonist}'s eye — a crack in the wall, a wilting plant, a clock stopped at the wrong time.", "camera": "close-up", "mood": "neutral", "carrier": False},
        {"text": "{rival} enters the frame without warning. {protagonist} stiffens.", "camera": "over-shoulder", "mood": "tense", "carrier": False},
        {"text": "The first exchange. Words say one thing. Eyes say another. Neither acknowledges the gap.", "camera": "medium", "mood": "tense", "carrier": True},
        {"text": "{protagonist} alone again. They exhale. The room holds the echo.", "camera": "wide", "mood": "calm", "carrier": False},
        {"text": "A memory surfaces — not as flashback but as body sensation. {protagonist}'s shoulders rise.", "camera": "close-up", "mood": "dark", "carrier": True},
        {"text": "Night falls over {setting}. {protagonist} at the window. The reflection stares back.", "camera": "medium", "mood": "dark", "carrier": False},
        {"text": "SILENCE: The world breathes. No dialogue. No action. Just the space between heartbeats.", "camera": "wide", "mood": "calm", "carrier": True},
        {"text": "{protagonist} makes a small choice — turns left instead of right, picks up a forgotten object, opens a closed door.", "camera": "medium", "mood": "hopeful", "carrier": False},
    ],
    "rising": [
        {"text": "{protagonist} faces {rival} across a charged space. Neither moves first.", "camera": "wide", "mood": "tense", "carrier": False},
        {"text": "Close on {protagonist}'s face as realization hits — the pattern they've been blind to.", "camera": "close-up", "mood": "dark", "carrier": True},
        {"text": "{protagonist} tries the old response. It doesn't work anymore. The body rejects the habit.", "camera": "medium", "mood": "tense", "carrier": True},
        {"text": "A confrontation builds. {rival} pushes. {protagonist} almost breaks — then catches themselves.", "camera": "over-shoulder", "mood": "tense", "carrier": False},
        {"text": "{protagonist} alone, processing. The walls feel closer. Or maybe they always were this close.", "camera": "wide", "mood": "dark", "carrier": False},
        {"text": "An unexpected kindness from a stranger. {protagonist} doesn't know how to receive it.", "camera": "medium", "mood": "calm", "carrier": True},
        {"text": "{protagonist} speaks truth for the first time — halting, imperfect, real.", "camera": "close-up", "mood": "hopeful", "carrier": True},
        {"text": "The cost of the truth lands. Silence follows. Neither person looks away.", "camera": "medium", "mood": "tense", "carrier": False},
        {"text": "{protagonist} walks a new path. Each step deliberate. The ground feels different.", "camera": "wide", "mood": "neutral", "carrier": False},
        {"text": "SILENCE: A breath held and released. The world continues. Something has loosened.", "camera": "wide", "mood": "calm", "carrier": True},
        {"text": "{rival} shows a crack in their armor. For one panel, the shadow looks human.", "camera": "close-up", "mood": "neutral", "carrier": True},
        {"text": "{protagonist} returns to a familiar place but sees it differently. The change is internal.", "camera": "medium", "mood": "hopeful", "carrier": False},
    ],
    "climax": [
        {"text": "{protagonist} and {rival} face each other for the final time. This isn't about winning.", "camera": "wide", "mood": "tense", "carrier": False},
        {"text": "Everything {protagonist} has learned crystallizes in one moment. The body moves before the mind.", "camera": "close-up", "mood": "tense", "carrier": True},
        {"text": "{protagonist} chooses the harder path — not the dramatic one, but the honest one.", "camera": "medium", "mood": "hopeful", "carrier": True},
        {"text": "{rival} falters. Not defeated — seen. The shadow recognized is no longer a shadow.", "camera": "close-up", "mood": "neutral", "carrier": True},
        {"text": "The world holds still. What needed to happen has happened. What needed to break has broken.", "camera": "wide", "mood": "calm", "carrier": False},
        {"text": "SILENCE: The deepest pause. Three panels of nothing but breath and light.", "camera": "wide", "mood": "calm", "carrier": True},
        {"text": "{protagonist} stands in the aftermath. Changed not by victory but by surrender.", "camera": "medium", "mood": "hopeful", "carrier": False},
        {"text": "A hand extended — to {rival}, to self, to the reader. Integration, not triumph.", "camera": "close-up", "mood": "hopeful", "carrier": True},
        {"text": "{protagonist} speaks the last words of the arc. Quiet. Unforced. True.", "camera": "medium", "mood": "calm", "carrier": False},
        {"text": "{setting} at peace. The light has changed. Dawn or dusk — it doesn't matter. What matters is the stillness.", "camera": "wide", "mood": "calm", "carrier": False},
        {"text": "Final panel: {protagonist}'s eyes. Not resolved. Not healed. Awake.", "camera": "close-up", "mood": "hopeful", "carrier": True},
        {"text": "SILENCE: The story ends where the reader begins. No summary. No lesson. Just the echo.", "camera": "wide", "mood": "calm", "carrier": True},
    ],
}

_SETTINGS = {
    "shonen": ["the training grounds at dawn", "a crowded market street", "the rooftop overlooking the city"],
    "seinen": ["a dimly lit office after hours", "the rain-soaked alleyway", "a hospital corridor at 3 AM"],
    "iyashikei": ["a quiet mountain village", "the garden behind the old house", "the empty beach at low tide"],
}

_PROTAGONIST = {
    "shonen": "Kai", "seinen": "Ren", "iyashikei": "Hana",
}
_RIVAL = {
    "shonen": "Sora", "seinen": "The Director", "iyashikei": "the memory of Mother",
}


def _deterministic_int(seed: str, max_val: int) -> int:
    """Stable integer from a seed string."""
    return int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) % max_val


def _generate_default_chapters(
    series_id: str,
    arc_id: str,
    genre_id: str = "shonen",
) -> list[dict[str, Any]]:
    """Generate a full 3-chapter arc with 12-16 beats per chapter."""
    seed = f"{series_id}:{arc_id}:{genre_id}"
    settings = _SETTINGS.get(genre_id, _SETTINGS["shonen"])
    setting = settings[_deterministic_int(seed + ":setting", len(settings))]
    protag = _PROTAGONIST.get(genre_id, "Kai")
    rival = _RIVAL.get(genre_id, "Sora")

    stage_sequence = [
        ("setup", "Awakening", "Turn"),
        ("rising", "Struggle", "Escalation"),
        ("climax", "Resolution", "Echo"),
    ]
    chapters: list[dict[str, Any]] = []
    for ch_num, (stage, title, hook) in enumerate(stage_sequence, 1):
        templates = _BEAT_TEMPLATES[stage]
        beats: list[dict[str, Any]] = []
        for bi, tmpl in enumerate(templates):
            text = tmpl["text"].format(
                setting=setting, protagonist=protag, rival=rival,
            )
            beats.append({
                "beat_index": bi,
                "beat_text": text,
                "is_carrier_beat": tmpl["carrier"],
                "camera_hint": tmpl["camera"],
                "mood_hint": tmpl["mood"],
            })

        silence_count = sum(1 for b in beats if "SILENCE" in b["beat_text"])
        chapters.append({
            "chapter_number": ch_num,
            "chapter_title": title,
            "mini_arc_stage": stage,
            "plot_beats": beats,
            "chapter_end_hook": hook,
            "turning_point": f"ch{ch_num}_turn" if stage != "climax" else None,
            "silence_beats_allocated": silence_count,
            "villain_presence": "absent" if stage == "setup" else "present",
        })

    return chapters


# ── Strategy-driven chapter generation (rich engine) ─────────────────────────
# Maps a profile/genre id onto a story-strategy genre family that has an
# authored ``*_strategies.yaml`` under config/source_of_truth/manga_story_strategies/.
# The Devotion lane (genre_family supernatural_everyday / healing) resolves to the
# HEALING / iyashikei register — NOT shonen / battle.
_STRATEGY_GENRE_ALIASES: dict[str, str] = {
    "iyashikei": "iyashikei",
    "healing": "iyashikei",
    "healing_iyashikei": "iyashikei",
    "supernatural_everyday": "iyashikei",  # Devotion lane (supernatural-healing)
    "slice_of_life": "iyashikei",
    "shonen": "shonen",
    "shojo": "shojo",
    "shoujo": "shojo",
    "seinen": "seinen",
    "mecha": "mecha",
    "psychological_horror": "psychological_horror",
    "horror": "psychological_horror",
    "psych_horror": "psychological_horror",
    "dark_fantasy": "dark_fantasy",
    "isekai": "isekai",
    "psychological_thriller": "psychological_thriller",
    "psych_thriller": "psychological_thriller",
    "thriller": "psychological_thriller",
    "romance_josei_drama": "romance_josei_drama",
    "romance": "romance_josei_drama",
    "josei": "romance_josei_drama",
    "romance_drama": "romance_josei_drama",
    "sci_fi_cyberpunk": "sci_fi_cyberpunk",
    "scifi": "sci_fi_cyberpunk",
    "cyberpunk": "sci_fi_cyberpunk",
    "sci_fi": "sci_fi_cyberpunk",
    "action_battle": "action_battle",
    "battle": "action_battle",
    "action": "action_battle",
    "sports_competition": "sports_competition",
    "sports": "sports_competition",
    "supernatural_mystery": "supernatural_mystery",
    "mystery": "supernatural_mystery",
    "supernatural": "supernatural_mystery",
    "historical_period": "historical_period",
    "historical": "historical_period",
    "period": "historical_period",
    "workplace_drama": "workplace_drama",
    "workplace": "workplace_drama",
}

# Character-name pools per strategy genre. Healing register uses gentle,
# place-rooted names — never the legacy Kai/Ren/Hana battle defaults.
_STRATEGY_CHARACTERS: dict[str, dict[str, list[str]]] = {
    "iyashikei": {
        "protagonist": ["Asa", "Mira", "Yui", "Nao", "Sora"],
        "companion": ["the visitor", "the old keeper", "the child", "a stranger from the road", "Ren"],
        "setting": [
            "a quiet mountain village",
            "the garden behind the old house",
            "the empty beach at low tide",
            "a canal town at the turning of the season",
            "the tea house at the edge of the forest",
        ],
    },
    "mecha": {
        "protagonist": ["Rei", "Kade", "Ash", "Yuna", "Iko"],
        "companion": [
            "the hangar chief", "the old mechanic", "Master Wu",
            "the wing commander", "the deck engineer",
        ],
        "setting": [
            "the carrier hangar before a drop",
            "the cockpit on the launch rail",
            "the maintenance bay at night",
            "the drop-zone under a bruised sky",
            "the reactor deck between sorties",
        ],
    },
}


def _strategy_chapter_titles(genre: str) -> list[str]:
    """Deterministic fallback titles when a chapter's selected strategy carries
    no usable ``name`` (e.g. a malformed strategy file). The production path
    prefers the strategy-driven title from :func:`_chapter_title_from_strategy`."""
    if genre == "iyashikei":
        return ["First Light", "The Visitor", "One Degree Deeper"]
    return ["Awakening", "Struggle", "Resolution"]


def _title_case_label(raw: str) -> str:
    """'single_object_meditation' -> 'Single Object Meditation'."""
    words = [w for w in str(raw).replace("-", "_").split("_") if w]
    return " ".join(w[:1].upper() + w[1:] for w in words)


def _chapter_title_from_strategy(
    strategy: dict[str, Any],
    layer_1: Any,
    fallback: str,
) -> str:
    """Derive a per-chapter title from the SAME strategy data that drives the
    beats — so the title is strategy-selected, not a hard-coded constant.

    Each chapter re-selects a strategy (4 per family, e.g. iyashikei: "Seasonal
    Return", "The Visiting Presence", "The Open Hand", "The Quiet Crossing") plus
    a layer-1 plot variant (e.g. "grief_received", "single_object_meditation").
    The selected strategy ``name`` is the natural chapter title; when a distinct
    plot variant is present we append it as a subtitle so the three chapters read
    as distinct movements rather than repeating the strategy name. Falls back to
    *fallback* (a deterministic constant) when no usable name exists.
    """
    name = ""
    if isinstance(strategy, dict):
        name = str(strategy.get("name") or "").strip()
    if not name:
        return fallback

    variant = ""
    if isinstance(layer_1, dict):
        variant = str(layer_1.get("variant_label") or "").strip()
    # A bare "<family>_standard"/"_default" variant is the baseline — no subtitle.
    if variant and not any(
        variant.endswith(sfx) for sfx in ("_standard", "_default", "_base")
    ):
        return f"{name}: {_title_case_label(variant)}"
    return name


def _hook_from_pacing(layer_5: Any, chapter_idx: int, fallback: str) -> str:
    """Pull a per-chapter end hook from a selected layer_5 pacing skeleton."""
    if not isinstance(layer_5, dict):
        return fallback
    hooks = layer_5.get("end_of_chapter_hooks")
    if isinstance(hooks, dict) and hooks:
        vals = list(hooks.values())
        return str(vals[chapter_idx % len(vals)])
    return fallback


def _generate_strategy_chapters(
    series_id: str,
    arc_id: str,
    genre_id: str,
    topic: str = "",
) -> list[dict[str, Any]] | None:
    """Derive a 3-chapter arc from the rich manga_story_strategies for *genre_id*.

    Returns ``None`` when no strategy file exists for the (aliased) genre, so the
    caller can fall back to the deterministic ``_BEAT_TEMPLATES`` path. Each
    chapter re-selects a strategy + layer variants with a chapter-scoped seed, so
    the three chapters differ while staying deterministic for a given
    (series_id, arc_id, genre_id).
    """
    norm_genre = genre_id.lower().replace("-", "_").replace(" ", "_")
    strat_genre = _STRATEGY_GENRE_ALIASES.get(norm_genre)
    if not strat_genre:
        # Exact-name genres are self-describing: a {genre}_strategies.yaml makes
        # the genre valid without an explicit alias (scales to all genres).
        from phoenix_v4.manga.story_strategy_loader import strategy_bank_exists
        if strategy_bank_exists(norm_genre):
            strat_genre = norm_genre
    if not strat_genre:
        return None

    try:
        from phoenix_v4.manga.story_strategy_loader import (
            load_story_strategy,
            select_layer_variants,
        )
    except ImportError:
        return None

    # Confirm a strategy file actually exists for this genre (loader returns {} otherwise).
    probe = load_story_strategy(strat_genre, series_id=series_id, arc_id=arc_id)
    if not probe or not probe.get("strategy"):
        return None

    chars = _STRATEGY_CHARACTERS.get(strat_genre)
    if not chars:
        # Self-contained genre banks carry their own cast (character_pool).
        from phoenix_v4.manga.story_strategy_loader import load_character_pool
        chars = load_character_pool(strat_genre)
    name_seed = f"{series_id}:{arc_id}:{strat_genre}"
    protag_pool = chars.get("protagonist") or ["the protagonist"]
    comp_pool = chars.get("companion") or ["the visitor"]
    setting_pool = chars.get("setting") or ["the place"]
    protagonist = protag_pool[_deterministic_int(name_seed + ":protag", len(protag_pool))]
    companion = comp_pool[_deterministic_int(name_seed + ":comp", len(comp_pool))]
    setting = setting_pool[_deterministic_int(name_seed + ":setting", len(setting_pool))]

    titles = _strategy_chapter_titles(strat_genre)
    fallback_hooks = ["small_wonder_close", "loss_echo_close", "small_wonder_close"]

    # Topic embed: pin the device-strategy the genre maps this topic to (e.g.
    # mecha + burnout -> failing-chassis) for the CARRIER chapter, so the episode
    # opens on the right inner-state arc rather than a hash-random one.
    pinned_sid: str | None = None
    if topic:
        try:
            from phoenix_v4.manga.story_strategy_loader import resolve_topic_strategy
            pinned_sid = resolve_topic_strategy(strat_genre, topic)
        except Exception:
            pinned_sid = None

    chapters: list[dict[str, Any]] = []
    for ch_idx in range(3):
        ch_num = ch_idx + 1
        # Chapter-scoped arc so the three chapters select distinct strategies/variants.
        ch_arc = f"{arc_id}:ch{ch_num}"
        if pinned_sid and ch_idx == 0:
            sd = load_story_strategy(
                strat_genre, strategy_id=pinned_sid, series_id=series_id, arc_id=ch_arc
            )
        else:
            sd = load_story_strategy(strat_genre, series_id=series_id, arc_id=ch_arc)
        strategy = sd.get("strategy") or {}
        variants = select_layer_variants(sd, series_id=series_id, arc_id=ch_arc, genre=strat_genre)

        # Layer 1 plot skeleton — prefer the selected variant's beat list, else the
        # strategy's base layer_1_plot_skeleton.
        layer_1 = variants.get("layer_1")
        skeleton = None
        if isinstance(layer_1, dict) and layer_1.get("beats"):
            skeleton = layer_1
        if skeleton is None:
            skeleton = strategy.get("layer_1_plot_skeleton") or {}
        raw_beats = skeleton.get("beats") or []

        beats: list[dict[str, Any]] = []
        for bi, rb in enumerate(raw_beats):
            text = str(rb.get("text") or "").strip()
            text = (
                text.replace("{protagonist}", protagonist)
                .replace("{companion}", companion)
                .replace("{rival}", companion)  # healing register has no rival
                .replace("{setting}", setting)
            )
            # Collapse the YAML folded-scalar whitespace into clean prose.
            text = " ".join(text.split())
            beats.append({
                "beat_index": bi,
                "beat_text": text,
                "is_carrier_beat": bool(rb.get("is_carrier", False)),
                "camera_hint": str(rb.get("camera_hint") or "medium"),
                "mood_hint": str(rb.get("mood_hint") or "calm"),
            })

        if not beats:
            return None  # malformed strategy — fall back to defaults

        end_hook = _hook_from_pacing(
            variants.get("layer_5") or strategy.get("layer_5_pacing_skeleton"),
            ch_idx,
            fallback_hooks[ch_idx % len(fallback_hooks)],
        )

        chapter_title = _chapter_title_from_strategy(
            strategy, layer_1, titles[ch_idx % len(titles)]
        )

        chapters.append({
            "chapter_number": ch_num,
            "chapter_title": chapter_title,
            "mini_arc_stage": ["setup", "rising", "climax"][ch_idx],
            "plot_beats": beats,
            "chapter_end_hook": end_hook,
            "turning_point": f"ch{ch_num}_turn" if ch_idx < 2 else None,
            "silence_beats_allocated": sum(
                1 for b in beats if b["mood_hint"] in ("stillness", "calm")
            ),
            "villain_presence": "absent",  # healing register: no villain, ever
            "story_strategy_id": sd.get("strategy_id"),
            "story_strategy_genre": strat_genre,
        })

    return chapters


# genre_id / strategy aliases → vessel config keys in manga_mode_vessels.yaml
_VESSEL_GENRE_KEYS: dict[str, str] = {
    "iyashikei": "iyashikei",
    "healing": "iyashikei",
    "healing_iyashikei": "iyashikei",
    "supernatural_everyday": "iyashikei",
    "slice_of_life": "iyashikei",
    "dark_fantasy": "dark_fantasy",
    "mecha": "mecha",
    "supernatural_mystery": "supernatural_mystery",
    "psychological_thriller": "psychological_thriller",
    "psych_thriller": "psychological_thriller",
    "thriller": "psychological_thriller",
    "romance_josei_drama": "romance_josei_drama",
    "romance": "romance_josei_drama",
    "josei": "romance_josei_drama",
    "shojo": "romance_josei_drama",
    "shoujo": "romance_josei_drama",
    "workplace_drama": "workplace_drama",
    "workplace": "workplace_drama",
    "sci_fi_cyberpunk": "sci_fi_cyberpunk",
    "cyberpunk": "sci_fi_cyberpunk",
    "sci_fi": "sci_fi_cyberpunk",
    "psychological_horror": "psychological_horror",
    "horror": "psychological_horror",
    "psych_horror": "psychological_horror",
    "action_battle": "action_battle",
    "battle": "action_battle",
    "action": "action_battle",
    "shonen": "action_battle",
    "seinen": "psychological_thriller",
    "historical_period": "historical_period",
    "historical": "historical_period",
    "isekai": "isekai",
    "sports_competition": "sports_competition",
    "sports": "sports_competition",
    "school_coming_of_age": "school_coming_of_age",
    "school": "school_coming_of_age",
    "cultivation_martial": "cultivation_martial",
    "cultivation": "cultivation_martial",
}


def resolve_vessel_genre(genre_id: str) -> str:
    """Map a story-architect genre_id onto a manga_mode_vessels.yaml key."""
    key = (genre_id or "").strip().lower()
    return _VESSEL_GENRE_KEYS.get(key, key)


def _vessel_beat_keys(mode: str) -> tuple[str, str, str]:
    if mode == "music":
        return ("opening", "mid", "closing")
    return ("wound", "turn", "renewal")


def apply_mode_vessel(
    chapters: list[dict[str, Any]],
    *,
    genre_id: str,
    mode: str,
    repo_root: Optional[Any] = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Weave the genre-native mode vessel into chapter beats (M4).

    Calls ``phoenix_v4.manga.mode.vessels.load_vessel`` — the existing loader —
    so manga_mode_vessels.yaml gains call-reachability. Injects one carrier beat
    per chapter (wound/turn/renewal or opening/mid/closing) at beat_index 0 of
    chapters 1–3. Returns (chapters, vessel_meta).
    """
    from phoenix_v4.manga.mode.vessels import load_vessel
    from phoenix_v4.manga.mode.validator import ModeError, MODES

    mode_norm = str(mode).strip().lower()
    if mode_norm not in MODES:
        raise ModeError(f"mode must be one of {MODES}, got {mode!r}")

    vessel_genre = resolve_vessel_genre(genre_id)
    vessel = load_vessel(vessel_genre, mode_norm, repo_root=repo_root)
    beats_map = vessel.get("beats") or {}
    keys = _vessel_beat_keys(mode_norm)
    vessel_name = str(vessel.get("vessel") or "")
    vessel_desc = str(vessel.get("vessel_desc") or "")

    out: list[dict[str, Any]] = []
    for idx, ch in enumerate(chapters):
        ch2 = dict(ch)
        plot = [dict(b) for b in (ch.get("plot_beats") or [])]
        key = keys[min(idx, len(keys) - 1)]
        skeleton = str(beats_map.get(key) or "").strip()
        if skeleton:
            beat_text = (
                f"[mode:{mode_norm} vessel:{vessel_name} / {key}] {skeleton} "
                f"— apparatus: {vessel_desc}. Teacher/musician is NEVER named; "
                f"the vessel carries the mode diegetically."
            )
            injected = {
                "beat_index": 0,
                "beat_text": beat_text,
                "is_carrier_beat": True,
                "camera_hint": "medium",
                "mood_hint": "hopeful" if key in ("renewal", "closing", "turn", "mid") else "tense",
                "mode_vessel_beat": key,
            }
            # Re-index existing beats after the injection.
            rest = []
            for bi, b in enumerate(plot, start=1):
                b2 = dict(b)
                b2["beat_index"] = bi
                rest.append(b2)
            plot = [injected] + rest
        ch2["plot_beats"] = plot
        out.append(ch2)

    meta = {
        "mode": mode_norm,
        "vessel_genre": vessel_genre,
        "vessel": vessel_name,
        "vessel_desc": vessel_desc,
        "beats": {k: beats_map.get(k) for k in keys},
    }
    return out, meta


def build_story_architecture_internal(
    *,
    series_id: str,
    arc_id: str,
    schema_version: str = "1.0.0",
    chapters: list[dict[str, Any]] | None = None,
    genre_id: str = "shonen",
    topic: str = "",
    mode: Optional[str] = None,
    repo_root: Optional[Any] = None,
) -> dict[str, Any]:
    """Build ``story_architecture_internal`` with optional carrier metadata on beats.

    When *chapters* is ``None``, generates a full 3-chapter arc with 12 beats
    per chapter (36 panels total across ~9 pages), using *genre_id* to select
    setting, protagonist, and rival names.

    When *mode* is ``\"teacher\"`` or ``\"music\"``, the genre-native vessel from
    ``config/manga/manga_mode_vessels.yaml`` is woven into beats via
    ``load_vessel`` (M4). Legacy callers omit *mode* — behavior unchanged.

    Writer handoff strips beats to ``beat_index`` + ``beat_text`` only
    (see ``transmission.story_architecture_internal_to_handoff``).

    Generation strategy (when *chapters* is ``None``):
      1. Try the RICH engine — derive chapters from the authored
         ``config/source_of_truth/manga_story_strategies/{genre}_strategies.yaml``
         via ``story_strategy_loader`` (243+ combos per strategy).
      2. Validate against ``config/manga/story_engines.yaml`` for governed genres.
      3. Fall back to ``_BEAT_TEMPLATES`` ONLY for non-governed legacy genres
         (no strategy bank). Governed commercial shells hard-fail instead.
    """
    from phoenix_v4.manga.story_engine_loader import (
        StoryEngineError,
        is_engine_governed,
        resolve_engine_genre,
        validate_architect_chapters,
    )

    note = "chunk_b_deterministic"
    engine_genre = resolve_engine_genre(genre_id)
    if chapters is None:
        chapters = _generate_strategy_chapters(series_id, arc_id, genre_id, topic)
        if chapters is not None:
            note = "strategy_driven"
        elif is_engine_governed(genre_id):
            raise StoryEngineError(
                f"no strategy bank for governed genre {engine_genre!r} — "
                f"generic _BEAT_TEMPLATES fallback blocked"
            )
        else:
            chapters = _generate_default_chapters(series_id, arc_id, genre_id)

    if is_engine_governed(genre_id):
        validate_architect_chapters(chapters, genre_id)

    vessel_meta: dict[str, Any] | None = None
    mode_norm = (str(mode).strip().lower() if mode else "") or None
    if mode_norm:
        chapters, vessel_meta = apply_mode_vessel(
            chapters, genre_id=genre_id, mode=mode_norm, repo_root=repo_root,
        )
        note = f"{note}+mode_vessel"

    out: dict[str, Any] = {
        "schema_version": schema_version,
        "artifact_type": "story_architecture_internal",
        "series_id": series_id,
        "arc_id": arc_id,
        "chapters": chapters,
        "transmission_audit": {"note": note},
        "constraint_checks": {"passed": True},
    }
    if vessel_meta is not None:
        out["mode"] = vessel_meta["mode"]
        out["mode_vessel"] = vessel_meta
    if is_engine_governed(genre_id):
        out["story_engine_genre"] = engine_genre
        out["story_engine_governed"] = True
    return out
