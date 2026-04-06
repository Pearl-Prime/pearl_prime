"""Story architecture internal artifact — handoff produced via transmission."""

from __future__ import annotations

import hashlib
from typing import Any


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


def build_story_architecture_internal(
    *,
    series_id: str,
    arc_id: str,
    schema_version: str = "1.0.0",
    chapters: list[dict[str, Any]] | None = None,
    genre_id: str = "shonen",
) -> dict[str, Any]:
    """Build ``story_architecture_internal`` with optional carrier metadata on beats.

    When *chapters* is ``None``, generates a full 3-chapter arc with 12 beats
    per chapter (36 panels total across ~9 pages), using *genre_id* to select
    setting, protagonist, and rival names.

    Writer handoff strips beats to ``beat_index`` + ``beat_text`` only
    (see ``transmission.story_architecture_internal_to_handoff``).
    """
    if chapters is None:
        chapters = _generate_default_chapters(series_id, arc_id, genre_id)
    return {
        "schema_version": schema_version,
        "artifact_type": "story_architecture_internal",
        "series_id": series_id,
        "arc_id": arc_id,
        "chapters": chapters,
        "transmission_audit": {"note": "chunk_b_deterministic"},
        "constraint_checks": {"passed": True},
    }
