"""MANGA.SILENCE.DENSITY and MANGA.GENRE.AUTHENTICITY pacing gates."""
from __future__ import annotations

from typing import Any, Mapping

from phoenix_v4.manga.series.profile_loader import MangaProfile


def check_silence_density(
    chapter_script: Mapping[str, Any],
    lettering: Mapping[str, Any],
    profile: MangaProfile,
) -> dict[str, Any] | None:
    """MANGA.SILENCE.DENSITY: actual silent_panel_ratio vs profile target ±0.15."""
    panels_total = 0
    panels_silent = 0

    # count from lettering spec if available
    for row in (lettering.get("lettering_panels") or []):
        panels_total += 1
        if row.get("silence_confirmed"):
            panels_silent += 1

    # fall back to counting from chapter script
    if panels_total == 0:
        for ch in (chapter_script.get("chapters") or []):
            for page in (ch.get("pages") or []):
                for panel in (page.get("panels") or []):
                    panels_total += 1
                    dialogue = panel.get("dialogue") or []
                    has_text = any(str(d).strip() for d in dialogue if d)
                    if not has_text:
                        panels_silent += 1

    if panels_total == 0:
        return None  # can't check

    actual_ratio = panels_silent / panels_total
    target = profile.silent_panel_ratio
    tolerance = 0.15

    if abs(actual_ratio - target) <= tolerance:
        return None  # passes

    return {
        "issue_code": "SILENCE_DENSITY_OUT_OF_RANGE",
        "gate_id": "MANGA.SILENCE.DENSITY",
        "severity": "MAJOR",
        "stage_owner": "chapter_qc",
        "description": (
            f"Silent panel ratio {actual_ratio:.2f} is outside target "
            f"{target:.2f} ± {tolerance:.2f} for {profile.visual_grammar} profile."
        ),
    }


def _count_words_in_panel(panel: Mapping[str, Any]) -> int:
    count = 0
    for d in (panel.get("dialogue") or []):
        count += len(str(d).split())
    count += len(str(panel.get("narration") or "").split())
    count += len(str(panel.get("caption") or "").split())
    return count


def check_genre_authenticity(
    chapter_script: Mapping[str, Any],
    profile: MangaProfile,
) -> dict[str, Any] | None:
    """MANGA.GENRE.AUTHENTICITY: words-per-page vs profile target ±30%."""
    total_words = 0
    total_pages = 0

    for ch in (chapter_script.get("chapters") or []):
        for page in (ch.get("pages") or []):
            total_pages += 1
            for panel in (page.get("panels") or []):
                total_words += _count_words_in_panel(panel)

    if total_pages == 0:
        return None

    actual_wpp = total_words / total_pages
    target = profile.words_per_page_target
    tolerance = target * 0.30

    if abs(actual_wpp - target) <= tolerance:
        return None  # passes

    return {
        "issue_code": "GENRE_AUTHENTICITY_PACING_MISMATCH",
        "gate_id": "MANGA.GENRE.AUTHENTICITY",
        "severity": "MAJOR",
        "stage_owner": "chapter_qc",
        "description": (
            f"Words per page {actual_wpp:.0f} is outside {profile.genre_family} target "
            f"{target} ± {tolerance:.0f} ({profile.market_demo} profile expects "
            f"{target} wpp)."
        ),
    }
