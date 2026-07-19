#!/usr/bin/env python3
"""Build shortform beat caption packs from SOURCE_OF_TRUTH evergreen atoms.

On-screen lines prefer voice-bank speakable_text (TTS prep output) when a
MANIFEST hit exists, so burnt-in captions match CosyVoice MP3s. Falls back to
raw evergreen text only on bank miss. Never uses thin storyboard placeholders.
Durations scale with word count so captions are readable.
"""
from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
EVERGREEN = REPO / "SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl"
DEFAULT_VOICE_BANK = REPO / "artifacts/social_media_voice_bank_2026-07-19/MANIFEST.tsv"

# Beat role -> evergreen family (assembly shape for shortform teaching)
ROLE_FAMILY = {
    "hook": "HOOK_COVER",
    "recognition": "PROBLEM_AGITATION",
    "mechanism": "MECHANISM_EXPLAINER",
    "practice": "TOOL_STEP",
    "payoff": "SAVEABLE_PAYOFF",
}

# Preferred atom picks (topic, persona, family, variant_index)
DEFAULT_PICKS = {
    "anxiety": {
        "persona": "healthcare_rns",
        "variants": {
            "HOOK_COVER": 2,
            "PROBLEM_AGITATION": 2,
            "MECHANISM_EXPLAINER": 2,
            "TOOL_STEP": 1,
            "SAVEABLE_PAYOFF": 2,
        },
    },
    "burnout": {
        "persona": "corporate_managers",
        "variants": {
            "HOOK_COVER": 2,
            "PROBLEM_AGITATION": 2,
            "MECHANISM_EXPLAINER": 2,
            "TOOL_STEP": 1,
            "SAVEABLE_PAYOFF": 2,
        },
    },
    "overthinking": {
        "persona": "gen_z_professionals",
        "variants": {
            "HOOK_COVER": 3,
            "PROBLEM_AGITATION": 2,
            "MECHANISM_EXPLAINER": 1,
            "TOOL_STEP": 1,
            "SAVEABLE_PAYOFF": 2,
        },
    },
}

# Kinetic needs shorter lines — punch cuts faithful to evergreen atoms
KINETIC_SHORT = {
    "anxiety": {
        "hook": "If tight chest is familiar — this pattern needs a better reset.",
        "recognition": "Outrunning anxiety makes the loop more expensive.",
        "mechanism": "The body gets safety before the mind can believe it.",
        "practice": "Feet on the floor. Widen your gaze. Name five ordinary things.",
        "payoff": "Signal. Reset. Next action.",
    },
    "burnout": {
        "hook": "If raised shoulders are familiar — this burnout pattern needs a better reset.",
        "recognition": "Outrunning burnout makes the loop more expensive.",
        "mechanism": "A tired nervous system stops treating pressure like a performance tool.",
        "practice": "Close the loop. Lower your jaw. Three slow double-inhale sighs.",
        "payoff": "Rest is a recovery input — not a reward for perfect output.",
    },
    "overthinking": {
        "hook": "The hidden cost of overthinking is constant safety scanning.",
        "recognition": "Outrunning overthinking makes the loop more expensive.",
        "mechanism": "Your threat scanner treats uncertainty like danger.",
        "practice": "Write one fact, one fear, one next action in ten minutes.",
        "payoff": "Anxious thoughts are proposals — not instructions.",
    },
}


def load_evergreen() -> list[dict]:
    return [json.loads(l) for l in EVERGREEN.read_text().splitlines() if l.strip()]


def pick_atom(rows: list[dict], topic: str, persona: str, family: str, variant: int) -> dict:
    for r in rows:
        if (
            r.get("topic") == topic
            and r.get("persona") == persona
            and r.get("atom_family") == family
            and int(r.get("variant_index") or 0) == variant
        ):
            return r
    # fallback: shortest in family
    cands = [
        r
        for r in rows
        if r.get("topic") == topic and r.get("persona") == persona and r.get("atom_family") == family
    ]
    if not cands:
        raise KeyError(f"no evergreen {topic}/{persona}/{family}")
    return sorted(cands, key=lambda r: r.get("char_count", 999))[0]


def reading_duration_s(text: str, *, wpm: float = 150.0, min_s: float = 3.0, max_s: float = 10.0) -> float:
    words = max(1, len(text.split()))
    # slightly slower than speech for reading on phone
    secs = (words / wpm) * 60.0 + 0.8  # breathe after
    return round(min(max_s, max(min_s, secs)), 2)


def wrap_onscreen(text: str, width: int = 28, max_lines: int = 4) -> str:
    lines = textwrap.wrap(text, width=width)[:max_lines]
    return "\n".join(lines)


def _speakable_for_atom(atom_id: str, raw_text: str, bank_index) -> tuple[str, str]:
    """Return (caption_source_text, source_label)."""
    if bank_index is None:
        return raw_text, "ssot_text"
    try:
        hit = bank_index.resolve(atom_id, require_audio=False)
        return hit.speakable_text, "voice_bank_speakable"
    except Exception:
        return raw_text, "ssot_text_bank_miss"


def build_pack(
    topic: str = "anxiety",
    *,
    style: str = "broll",
    voice_bank: Path | None = DEFAULT_VOICE_BANK,
) -> dict:
    rows = load_evergreen()
    cfg = DEFAULT_PICKS[topic]
    persona = cfg["persona"]
    bank_index = None
    if voice_bank is not None and Path(voice_bank).is_file():
        from scripts.social_media.voice_bank_lookup import load_index

        bank_index = load_index(Path(voice_bank), allow_r2_download=False)
    beats = []
    t = 0.0
    roles = ["hook", "recognition", "mechanism", "practice", "payoff"]
    for role in roles:
        fam = ROLE_FAMILY[role]
        atom = pick_atom(rows, topic, persona, fam, cfg["variants"][fam])
        raw = atom["text"].strip()
        full, src = _speakable_for_atom(atom["atom_id"], raw, bank_index)
        if style == "kinetic" and topic in KINETIC_SHORT and src.startswith("ssot"):
            # Kinetic punch lines only when bank speakable unavailable
            on_screen = KINETIC_SHORT[topic][role]
            # kinetic: still paced for reading short lines, with hold
            dur = reading_duration_s(on_screen, wpm=120.0, min_s=3.5, max_s=7.5)
            if role == "hook":
                dur = max(dur, 4.0)
            if role == "payoff":
                dur = max(dur, 4.5)
        elif style == "kinetic" and topic in KINETIC_SHORT and src == "voice_bank_speakable":
            # Prefer speakable (matches audio); wrap for kinetic line length
            on_screen = wrap_onscreen(full, width=28, max_lines=3)
            dur = reading_duration_s(full, wpm=120.0, min_s=3.5, max_s=7.5)
            if role == "hook":
                dur = max(dur, 4.0)
            if role == "payoff":
                dur = max(dur, 4.5)
        else:
            on_screen = wrap_onscreen(full, width=26 if style == "broll" else 28, max_lines=4)
            # broll/metaphor: reading pace; hook a bit punchier min
            mins = {"hook": 3.5, "recognition": 4.5, "mechanism": 6.0, "practice": 6.5, "payoff": 4.5}
            maxs = {"hook": 6.0, "recognition": 8.0, "mechanism": 10.0, "practice": 10.0, "payoff": 7.0}
            dur = reading_duration_s(
                full, wpm=140.0, min_s=mins[role], max_s=maxs[role]
            )
        beats.append(
            {
                "role": role,
                "family": fam,
                "atom_id": atom["atom_id"],
                "persona": persona,
                "full_text": full,
                "ssot_text": raw,
                "caption_source": src,
                "on_screen": on_screen,
                "start": round(t, 2),
                "end": round(t + dur, 2),
                "duration_s": dur,
                "word_count": atom.get("word_count"),
            }
        )
        t += dur
    return {
        "topic": topic,
        "style": style,
        "source": "SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl",
        "voice_bank_manifest": str(voice_bank) if voice_bank else None,
        "total_duration_s": round(t, 2),
        "beats": beats,
    }


if __name__ == "__main__":
    for style in ("kinetic", "broll", "metaphor"):
        pack = build_pack("anxiety", style=style)
        out = (
            REPO
            / "artifacts/qa/social_finish_20260718/lane03_research_complete/variants"
            / f"_caption_pack_anxiety_{style}.json"
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(pack, indent=2), encoding="utf-8")
        print(style, "total", pack["total_duration_s"], "s")
        for b in pack["beats"]:
            print(f"  {b['role']:12} {b['duration_s']:5}s  {b['on_screen'][:60]!r}  ← {b['atom_id']}")
