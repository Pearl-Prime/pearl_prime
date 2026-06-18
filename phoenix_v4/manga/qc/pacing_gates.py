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

    # fall back to counting from chapter script (handles both shapes)
    if panels_total == 0:
        from phoenix_v4.manga.qc._script_shape import iter_panels, panel_has_text
        for panel in iter_panels(chapter_script):
            panels_total += 1
            if not panel_has_text(panel):
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
    # Words-per-page counts READER-FACING text only (dialogue/narration/caption),
    # not art-direction (panel_description/action) which is never printed on the page.
    from phoenix_v4.manga.qc._script_shape import reader_text
    return len(reader_text(panel).split())


def _wpp_band(profile: MangaProfile) -> tuple[float, float, str]:
    """Resolve the acceptable words-per-page band for a profile.

    Honors an explicit ``pacing.words_per_page_band: [min, max]`` (e.g. the
    iyashikei craft band [18, 45], whose natural variance is too wide for a fixed
    tolerance). Falls back to ``words_per_page_target`` ± 30%.
    """
    raw = getattr(profile, "_raw", {}) or {}
    pacing = raw.get("pacing") or {}
    band = pacing.get("words_per_page_band") or raw.get("words_per_page_band")
    if isinstance(band, (list, tuple)) and len(band) == 2:
        try:
            lo, hi = float(band[0]), float(band[1])
            if lo <= hi:
                return lo, hi, f"band [{lo:.0f}, {hi:.0f}]"
        except (TypeError, ValueError):
            pass
    target = profile.words_per_page_target
    tol = target * 0.30
    return target - tol, target + tol, f"{target} ± {tol:.0f}"


def check_genre_authenticity(
    chapter_script: Mapping[str, Any],
    profile: MangaProfile,
) -> dict[str, Any] | None:
    """MANGA.GENRE.AUTHENTICITY: words-per-page vs the profile's acceptable band."""
    from phoenix_v4.manga.qc._script_shape import iter_pages

    total_words = 0
    total_pages = 0
    for page in iter_pages(chapter_script):
        total_pages += 1
        for panel in (page.get("panels") or []):
            total_words += _count_words_in_panel(panel)

    if total_pages == 0:
        return None

    actual_wpp = total_words / total_pages
    lo, hi, band_desc = _wpp_band(profile)

    if lo <= actual_wpp <= hi:
        return None  # passes

    return {
        "issue_code": "GENRE_AUTHENTICITY_PACING_MISMATCH",
        "gate_id": "MANGA.GENRE.AUTHENTICITY",
        "severity": "MAJOR",
        "stage_owner": "chapter_qc",
        "description": (
            f"Words per page {actual_wpp:.0f} is outside {profile.genre_family} "
            f"{band_desc} ({profile.market_demo} profile)."
        ),
    }
