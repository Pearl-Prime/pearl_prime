"""Style-id resolution authority chain (Wave-2 Item 4).

Every chapter render used to hard-default ``style_id="dark_psychological"``
regardless of genre (see ``scripts/manga/run_chapter_production.py``,
``run_chapter_visual.py``, ``run_manga_chapter.py`` — all three previously
carried ``ap.add_argument("--style-id", default="dark_psychological")``).
That meant a healing/iyashikei chapter with no explicit ``--style-id`` still
rendered in the dark-psychological register (thick ink, heavy shadows) —
the same "wrong tradition" failure class documented in
``phoenix_v4/manga/genre_tradition.py``.

This module resolves a style archetype id (a key into
``config/manga/style_archetypes.yaml``) through an explicit, documented
authority chain, highest priority first:

    1. explicit_override   — an operator-passed ``--style-id`` flag value.
    2. script_style         — a ``style_id`` embedded in the chapter_script
                               JSON itself (``chapter_script["style_id"]``).
    3. request_style        — a per-request style hint (e.g. from a job
                               payload / API call), distinct from the CLI
                               script's own default.
    4. teacher_archetype     — a per-teacher style association, when the
                               teacher has one configured (fail-open: no
                               registry entry today for most teachers).
    5. profile_grammar       — a format-adaptation-grammar style hint
                               (``config/manga/format_adaptation_grammars.yaml``
                               per format_id). No format currently declares a
                               ``style_id`` field, so this layer is a
                               documented no-op until one does — fail-open.
    6. genre_family_signal   — derive a style from the chapter's genre via
                               ``GENRE_STYLE_MAP`` below (best-effort,
                               editorially curated mapping from genre id to
                               style archetype).
    7. fallback              — ``grounded_realism`` when nothing above
                               resolves (source tag ``narrow_fallback``).

Every layer is optional/fail-open: a missing or unresolvable signal simply
falls through to the next layer. The function never raises for a missing
signal — only for a genuinely malformed ``style_archetypes.yaml`` if one
insists on validating against it (not done here; this module only computes
the *id*, callers still validate it against style_archetypes.yaml as before).
"""
from __future__ import annotations

from typing import Any, Mapping

# Terminal, guaranteed-present fallback archetype (config/manga/style_archetypes.yaml).
FALLBACK_STYLE_ID = "grounded_realism"

# Best-effort genre-family → style-archetype signal (layer 6). Curated from the
# genre ids in config/manga/canonical_genre_list.yaml + the wave-2 additions in
# config/manga/drawing_tradition_per_genre.yaml, mapped onto the archetype ids
# declared in config/manga/style_archetypes.yaml. Unmapped genres fall through
# to the narrow fallback (layer 7) rather than guessing.
GENRE_STYLE_MAP: dict[str, str] = {
    "healing": "cozy_iyashikei",
    "psychological_horror": "dark_psychological",
    "horror": "dark_psychological",
    "dark_fantasy": "dark_psychological",
    "mecha": "power_progression",
    "battle": "power_progression",
    "battle_internal": "power_progression",
    "sports": "power_progression",
    "romance": "webtoon_vertical_romance",
    "slice_of_life": "cozy_iyashikei",
    "supernatural_everyday": "cozy_iyashikei",
    "school": "cozy_iyashikei",
    "family": "cozy_iyashikei",
    "comedy": "comedic_deformation",
    "food": "sensory_closeup",
    "essay": "symbolic_reflection",
    "memoir": "symbolic_reflection",
    "social_issue": "grounded_realism",
    "graphic_medicine": "grounded_realism",
    "workplace": "grounded_realism",
    "procedural": "grounded_realism",
    "mystery": "grounded_realism",
    "historical": "ornate_fantasy",
    "cultivation": "ornate_fantasy",
    "fantasy_adventure": "ornate_fantasy",
    "sci_fi_cyberpunk": "hyper_clean_cinematic",
}

# Per-teacher style association (layer 4). Empty today — fail-open by design;
# populate as teacher-specific style conventions are established.
TEACHER_STYLE_MAP: dict[str, str] = {}


def _clean(value: Any) -> str | None:
    if isinstance(value, str):
        v = value.strip()
        if v:
            return v
    return None


def _normalize_genre(genre_id: Any) -> str | None:
    v = _clean(genre_id)
    if v is None:
        return None
    return v.lower().replace("-", "_").replace(" ", "_")


def resolve_style_id(
    *,
    explicit_override: str | None = None,
    chapter_script: Mapping[str, Any] | None = None,
    request_style: str | None = None,
    teacher_id: str | None = None,
    format_id: str | None = None,
    genre_id: str | None = None,
    format_grammars: Mapping[str, Any] | None = None,
) -> tuple[str, str]:
    """Resolve a style archetype id, returning ``(style_id, source)``.

    ``source`` names which authority-chain layer produced the value:
    ``explicit_override`` / ``script_style`` / ``request_style`` /
    ``teacher_archetype`` / ``profile_grammar`` / ``genre_family_signal`` /
    ``narrow_fallback``.

    Parameters mirror the chain layers 1-6; every one is optional. When
    ``genre_id`` is not given but ``chapter_script`` is, the genre is read
    from ``chapter_script.get("genre")`` (falls back to ``genre_id`` key too).
    """
    # 1. explicit_override — the operator-passed flag, when non-empty.
    v = _clean(explicit_override)
    if v is not None:
        return v, "explicit_override"

    # 2. script_style — embedded directly in the chapter_script JSON.
    if chapter_script is not None:
        v = _clean(chapter_script.get("style_id"))
        if v is not None:
            return v, "script_style"

    # 3. request_style — a request-level hint distinct from the CLI default.
    v = _clean(request_style)
    if v is not None:
        return v, "request_style"

    # 4. teacher_archetype — per-teacher style association, if configured.
    teacher_key = _clean(teacher_id)
    if teacher_key is not None:
        mapped = TEACHER_STYLE_MAP.get(teacher_key.lower())
        if mapped:
            return mapped, "teacher_archetype"

    # 5. profile_grammar — format-adaptation-grammar style hint (no-op today).
    fmt_key = _clean(format_id)
    if fmt_key is not None:
        grammars = format_grammars
        if grammars is None:
            grammars = _load_format_grammars()
        fmt_block = (grammars or {}).get("formats", {}).get(fmt_key) if isinstance(grammars, dict) else None
        if isinstance(fmt_block, dict):
            mapped = _clean(fmt_block.get("style_id"))
            if mapped is not None:
                return mapped, "profile_grammar"

    # 6. genre_family_signal — best-effort genre → archetype mapping.
    resolved_genre = _normalize_genre(genre_id)
    if resolved_genre is None and chapter_script is not None:
        resolved_genre = _normalize_genre(
            chapter_script.get("genre") or chapter_script.get("genre_id")
        )
    if resolved_genre is not None:
        mapped = GENRE_STYLE_MAP.get(resolved_genre)
        if mapped:
            return mapped, "genre_family_signal"

    # 7. fallback — grounded_realism, always present.
    return FALLBACK_STYLE_ID, "narrow_fallback"


def _load_format_grammars() -> dict[str, Any]:
    """Load config/manga/format_adaptation_grammars.yaml (fail-open)."""
    try:
        import yaml
        from pathlib import Path

        # phoenix_v4/manga/style_resolution.py -> parents[2] is the repo root.
        repo_root = Path(__file__).resolve().parents[2]
        path = repo_root / "config" / "manga" / "format_adaptation_grammars.yaml"
        data = yaml.safe_load(path.read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}
