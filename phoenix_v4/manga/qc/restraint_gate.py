"""MANGA.RESTRAINT.EXPOSITION gate — female-reader grammar check.

Checks ratio of show (gesture/expression/silence/action) vs tell
(narration/internal monologue/explicit emotional labeling) in
romance and josei/shojo chapters. High narration-to-action ratio
is a grammar violation for these market segments.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

from phoenix_v4.manga.series.profile_loader import MangaProfile

# Applies only to these demographics/genres
_APPLIES_TO_DEMOS = frozenset(["josei", "shojo"])
_APPLIES_TO_GENRES = frozenset(["romance"])

# Narration-heavy signals: explicit emotional labeling in narration/caption
_EXPOSITION_PATTERNS = [
    r"\bshe felt\b", r"\bhe felt\b", r"\bshe was\b sad\b", r"\bhe was\b sad\b",
    r"\bshe realized\b", r"\bhe realized\b",
    r"\bshe thought\b", r"\bhe thought\b",
    r"\bshe knew\b", r"\bhe knew\b",
    r"\bin that moment\b",
    r"\bher heart\b", r"\bhis heart\b",
    r"\bshe loved\b", r"\bhe loved\b",
    r"\bshe couldn't deny\b", r"\bhe couldn't deny\b",
    r"\bshe wanted\b", r"\bhe wanted\b",
    r"\bher feelings\b", r"\bhis feelings\b",
    r"\bshe was afraid\b", r"\bhe was afraid\b",
]

_EXPOSITION_RE = re.compile("|".join(_EXPOSITION_PATTERNS), re.IGNORECASE)

# Show signals: gesture/action/expression beats in panel descriptions
_SHOW_SIGNALS = [
    "looks away", "turned away", "looked down", "bit her lip", "bit his lip",
    "clenched", "exhaled", "paused", "stepped back", "trembled",
    "silence", "silent panel", "no dialogue", "hands shook",
    "gripped", "smiled", "flinched", "froze", "blinked",
    "opened her mouth", "opened his mouth", "said nothing",
]


def _applies_to_profile(profile: MangaProfile) -> bool:
    return profile.market_demo in _APPLIES_TO_DEMOS or profile.genre_family in _APPLIES_TO_GENRES


def check_restraint_over_exposition(
    chapter_script: Mapping[str, Any],
    profile: MangaProfile,
) -> dict[str, Any] | None:
    """MANGA.RESTRAINT.EXPOSITION: check show vs tell ratio for josei/shojo/romance."""
    if not _applies_to_profile(profile):
        return None

    exposition_count = 0
    show_count = 0
    total_panels = 0

    from phoenix_v4.manga.qc._script_shape import iter_panels
    for panel in iter_panels(chapter_script):
        total_panels += 1
        narration = str(panel.get("narration") or "")
        caption = str(panel.get("caption") or "")
        description = str(panel.get("panel_description") or panel.get("description") or panel.get("action") or "")

        # Count exposition signals in narration/caption
        tell_text = f"{narration} {caption}"
        if _EXPOSITION_RE.search(tell_text):
            exposition_count += 1

        # Count show signals in panel description + all text
        full_text = f"{description} {narration} {caption}".lower()
        if any(sig in full_text for sig in _SHOW_SIGNALS):
            show_count += 1

    if total_panels == 0:
        return None

    if exposition_count == 0:
        return None  # no exposition — gate passes

    exposition_ratio = exposition_count / total_panels
    # Threshold: >25% of panels have explicit emotional exposition → flag
    if exposition_ratio <= 0.25:
        return None  # passes

    return {
        "issue_code": "OVER_EXPOSITION_IN_EMOTIONAL_CHAPTER",
        "gate_id": "MANGA.RESTRAINT.EXPOSITION",
        "severity": "MAJOR",
        "stage_owner": "chapter_qc",
        "description": (
            f"{exposition_count}/{total_panels} panels ({exposition_ratio:.0%}) contain "
            f"explicit emotional narration. For {profile.market_demo}/{profile.genre_family}, "
            f"emotional moments should be shown (gesture/silence/action), not labeled. "
            f"Show signals found in {show_count} panels."
        ),
    }
