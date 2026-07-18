"""Deterministic chapter script stub — maps story handoff beats to multi-page panels (no LLM).

Produces proper manga page layout: 4 panels per page, varied camera/mood,
dialogue on non-silent panels, splash pages for chapter openers, silent
pages for breath beats.
"""

from __future__ import annotations

import hashlib
from copy import deepcopy
from typing import Any, Mapping

PANELS_PER_PAGE = 4


def _find_chapter(
    handoff: Mapping[str, Any], chapter_number: int
) -> Mapping[str, Any] | None:
    for ch in handoff.get("chapters") or []:
        if int(ch.get("chapter_number", -1)) == chapter_number:
            return ch
    return None


def _det_choice(seed: str, options: list[str]) -> str:
    idx = int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) % len(options)
    return options[idx]


_CAMERAS = ["close-up", "medium", "wide", "over-shoulder", "low-angle", "high-angle"]
_MOODS = ["neutral", "tense", "calm", "dark", "hopeful"]

# Dialogue templates keyed by mood — gives panels real speech
_DIALOGUE_TEMPLATES: dict[str, list[list[dict[str, str]]]] = {
    "tense": [
        [{"character": "protagonist", "text": "...I wasn't expecting that."}],
        [{"character": "protagonist", "text": "Don't."}, {"character": "rival", "text": "You know I'm right."}],
        [{"character": "rival", "text": "You're doing it again."}],
    ],
    "calm": [
        [{"character": "protagonist", "text": "It's quieter than I remember."}],
        [{"character": "protagonist", "text": "Maybe that's enough for today."}],
        [],  # some calm panels are wordless
    ],
    "dark": [
        [{"character": "protagonist", "text": "I can't keep pretending this is fine."}],
        [{"character": "rival", "text": "You never could."}],
        [],
    ],
    "hopeful": [
        [{"character": "protagonist", "text": "Okay. Let's try again."}],
        [{"character": "protagonist", "text": "Something shifted. I felt it."}],
        [{"character": "protagonist", "text": "Not fixed. But... different."}],
    ],
    "neutral": [
        [],  # neutral panels are often silent or action-only
        [{"character": "protagonist", "text": "Hmm."}],
        [],
    ],
}


def build_chapter_script_pair_from_handoff(
    handoff: Mapping[str, Any],
    *,
    chapter_number: int,
    series_id: str,
    chapter_id: str,
    schema_version: str = "1.0.0",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (writer_handoff_script, internal_record_script) with multi-page layout."""
    ch = _find_chapter(handoff, chapter_number)
    if ch is None:
        raise ValueError(f"No chapter {chapter_number} in handoff")

    beats = ch.get("plot_beats") or []
    all_panels: list[dict[str, Any]] = []
    all_internal: list[dict[str, Any]] = []

    for beat in beats:
        bi = beat["beat_index"]
        pid = f"p_{chapter_number}_{bi}"
        beat_text = str(beat.get("beat_text", ""))
        is_silence = "SILENCE" in beat_text.upper()

        # Use hints from story architect if available, else derive deterministically
        seed = f"{series_id}:{chapter_id}:{bi}"
        camera = beat.get("camera_hint") or _det_choice(seed + ":cam", _CAMERAS)
        mood = beat.get("mood_hint") or _det_choice(seed + ":mood", _MOODS)

        if is_silence:
            camera = "wide"
            mood = "calm"

        # Build dialogue for non-silent panels
        dialogue: list[dict[str, str]] = []
        if not is_silence:
            templates = _DIALOGUE_TEMPLATES.get(mood, _DIALOGUE_TEMPLATES["neutral"])
            chosen = templates[int(hashlib.sha256(seed.encode()).hexdigest()[:4], 16) % len(templates)]
            dialogue = [deepcopy(d) for d in chosen]

        base: dict[str, Any] = {
            "panel_id": pid,
            "dialogue": dialogue,
            "action": beat_text,
            "camera": camera,
            "mood": mood,
        }
        if is_silence:
            base["panel_type"] = "silent"

        all_panels.append(base)

        internal = deepcopy(base)
        internal["is_carrier_beat"] = bool(beat.get("is_carrier_beat", False))
        all_internal.append(internal)

    # ── Distribute panels across pages ──
    pages: list[dict[str, Any]] = []
    pages_internal: list[dict[str, Any]] = []

    for page_idx in range(0, len(all_panels), PANELS_PER_PAGE):
        page_num = (page_idx // PANELS_PER_PAGE) + 1
        chunk = all_panels[page_idx : page_idx + PANELS_PER_PAGE]
        chunk_i = all_internal[page_idx : page_idx + PANELS_PER_PAGE]

        # Determine page type
        is_first_page = page_num == 1
        has_silence = any(p.get("panel_type") == "silent" for p in chunk)
        all_silent = all(p.get("panel_type") == "silent" for p in chunk)

        if all_silent:
            page_type = "silent"
        elif is_first_page:
            page_type = "splash"
        else:
            page_type = "standard"

        pages.append({
            "page_number": page_num,
            "page_type": page_type,
            "panels": chunk,
        })
        pages_internal.append({
            "page_number": page_num,
            "page_type": page_type,
            "panels": chunk_i,
        })

    writer = {
        "schema_version": schema_version,
        "artifact_type": "chapter_script_writer_handoff",
        "series_id": series_id,
        "chapter_id": chapter_id,
        "pages": pages,
    }
    internal_doc = {
        "schema_version": schema_version,
        "artifact_type": "chapter_script_internal_record",
        "series_id": series_id,
        "chapter_id": chapter_id,
        "pages": pages_internal,
    }
    # Propagate declared genre from story handoff so GENRE_ENGINE can evaluate
    # without CI/test-side mutation of the emitted script.
    declared = (
        handoff.get("genre_id")
        or handoff.get("genre")
        or (handoff.get("mode_vessel") or {}).get("vessel_genre")
    )
    if declared:
        writer["genre_id"] = str(declared)
        writer["genre"] = str(declared)
        internal_doc["genre_id"] = str(declared)
        internal_doc["genre"] = str(declared)
    mode = handoff.get("mode")
    if mode:
        writer["mode"] = mode
        internal_doc["mode"] = mode
    return writer, internal_doc
