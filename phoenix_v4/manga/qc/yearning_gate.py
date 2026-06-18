"""MANGA.YEARNING.PACING gate — shojo/josei/romance pacing check.

Checks that longing/romance-engine chapters do NOT resolve emotional tension
prematurely. The grammar of yearning requires deferred resolution:
proximity without contact, dialogue that almost says everything, beats of
waiting and restraint that build unbearable tension before any release.

Violations: a chapter in a longing/romance-engine profile that resolves
too quickly — confession completed, reunion completed, emotional arc closed
within a chapter that should sustain yearning.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

from phoenix_v4.manga.series.profile_loader import MangaProfile

# Gate applies to these emotional engines
_YEARNING_ENGINES = frozenset(["longing", "tenderness"])
# Also applies to romance genre regardless of engine
_YEARNING_GENRES = frozenset(["romance", "shojo_romance"])
# Also applies when hook family is almost-resolution type
_YEARNING_HOOKS = frozenset(["almost_confession", "confession_almost_happened"])

# Resolution signals: chapter closes the loop too early
_RESOLUTION_PATTERNS = [
    r"\bi love you\b",
    r"\bshe confessed\b", r"\bhe confessed\b",
    r"\bshe said it\b", r"\bhe said it\b",
    r"\bfinally said\b",
    r"\bkissed\b",
    r"\bthey kissed\b",
    r"\bthey held each other\b",
    r"\btogether at last\b",
    r"\bwe can finally\b",
    r"\bit's over now\b",
    r"\beverything was resolved\b",
    r"\bshe accepted\b", r"\bhe accepted\b",
    r"\bhe agreed\b", r"\bshe agreed\b",
]

_RESOLUTION_RE = re.compile("|".join(_RESOLUTION_PATTERNS), re.IGNORECASE)

# Yearning-sustain signals: tension maintained, not resolved
_SUSTAIN_SIGNALS = [
    "almost", "nearly", "stopped herself", "stopped himself",
    "looked away", "couldn't", "didn't say", "bit her lip", "bit his lip",
    "silence fell", "said nothing", "turned away", "walked away",
    "left before", "paused", "the distance between", "not yet",
    "still waiting", "almost touched", "held back",
]


def _applies_to_profile(profile: MangaProfile) -> bool:
    return (
        profile.emotional_engine in _YEARNING_ENGINES
        or profile.genre_family in _YEARNING_GENRES
        or profile.chapter_hook_family in _YEARNING_HOOKS
    )


def check_yearning_pacing(
    chapter_script: Mapping[str, Any],
    profile: MangaProfile,
) -> dict[str, Any] | None:
    """MANGA.YEARNING.PACING: ensure longing/romance chapters sustain tension, not resolve it."""
    if not _applies_to_profile(profile):
        return None

    resolution_count = 0
    sustain_count = 0
    total_panels = 0

    from phoenix_v4.manga.qc._script_shape import iter_panels

    def _dialogue_str(items: Any) -> str:
        if not isinstance(items, list):
            return str(items or "")
        out: list[str] = []
        for d in items:
            if isinstance(d, dict):
                out.append(str(d.get("text") or ""))
            elif d is not None:
                out.append(str(d))
        return " ".join(out)

    for panel in iter_panels(chapter_script):
        total_panels += 1
        narration = str(panel.get("narration") or "")
        caption = str(panel.get("caption") or "")
        dialogue = _dialogue_str(panel.get("dialogue"))
        description = str(panel.get("panel_description") or panel.get("description") or panel.get("action") or "")

        full_text = f"{narration} {caption} {dialogue}"
        all_text = f"{description} {full_text}".lower()

        if _RESOLUTION_RE.search(full_text):
            resolution_count += 1

        if any(sig in all_text for sig in _SUSTAIN_SIGNALS):
            sustain_count += 1

    if total_panels == 0:
        return None

    if resolution_count == 0:
        return None  # no premature resolution detected — gate passes

    resolution_ratio = resolution_count / total_panels
    # Threshold: >15% of panels contain resolution language in a yearning-engine chapter
    if resolution_ratio <= 0.15:
        return None

    return {
        "issue_code": "PREMATURE_RESOLUTION_IN_YEARNING_CHAPTER",
        "gate_id": "MANGA.YEARNING.PACING",
        "severity": "MAJOR",
        "stage_owner": "chapter_qc",
        "description": (
            f"{resolution_count}/{total_panels} panels ({resolution_ratio:.0%}) contain "
            f"resolution language in a {profile.emotional_engine}/{profile.genre_family} chapter. "
            f"Yearning grammar requires deferred resolution. "
            f"Sustain signals found in only {sustain_count} panels. "
            f"Remove or defer confessions/closures; extend the almost-moment."
        ),
    }
