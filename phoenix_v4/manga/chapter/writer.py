"""Chapter Writer — produces validated chapter_script writer handoff + internal record.

Chunk A: replay-backed generation only (see ReplayLLMClient). No live API in default paths.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from phoenix_v4.manga.llm.client import LLMClient
from phoenix_v4.manga.models.leakage import assert_handoff_has_no_transmission_leakage
from phoenix_v4.manga.models.validation import validate_instance

_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "chapter_writer_prompt.txt"

# Response envelope from the LLM (replay or future live adapter).
_PAIR_KEYS = ("chapter_script_writer_handoff", "chapter_script_internal_record")


def _load_prompt_template() -> str:
    if _PROMPT_FILE.is_file():
        return _PROMPT_FILE.read_text(encoding="utf-8")
    return (
        "Chapter Writer. Return JSON with keys chapter_script_writer_handoff and "
        "chapter_script_internal_record.\n"
        "series_id={series_id} chapter_id={chapter_id} chapter_number={chapter_number}\n"
        "{story_chapter_json}\n"
    )


def _story_chapter_excerpt(
    story_handoff: Mapping[str, Any], chapter_number: int
) -> str:
    for ch in story_handoff.get("chapters") or []:
        if int(ch.get("chapter_number", -1)) == int(chapter_number):
            return json.dumps(ch, indent=2)
    raise ValueError(f"No chapter {chapter_number} in story_architecture_handoff")


def _mode_vessel_prompt_block(
    story_handoff: Mapping[str, Any],
    *,
    mode: str | None = None,
    genre_id: str | None = None,
) -> str:
    """Append mode-vessel craft rules when mode is set (M4).

    Calls ``load_vessel`` so manga_mode_vessels.yaml is on a callable path from
    the chapter-writer prompt assembly. Empty string when mode is unset (legacy).
    """
    mode_norm = (mode or story_handoff.get("mode") or "").strip().lower()
    if mode_norm not in ("teacher", "music"):
        return ""
    genre = (
        genre_id
        or story_handoff.get("genre_id")
        or story_handoff.get("genre")
        or (story_handoff.get("mode_vessel") or {}).get("vessel_genre")
        or ""
    )
    if not genre:
        return ""
    from phoenix_v4.manga.mode.vessels import VesselError, load_vessel
    from phoenix_v4.manga.series.story_architect import resolve_vessel_genre

    try:
        vessel = load_vessel(resolve_vessel_genre(str(genre)), mode_norm)
    except (VesselError, Exception):
        return ""
    beats = vessel.get("beats") or {}
    beat_lines = "\n".join(f"  - {k}: {v}" for k, v in beats.items() if v)
    return (
        "\n\nMode vessel (M4 — diegetic apparatus; NEVER name the teacher/musician):\n"
        f"- mode: {mode_norm}\n"
        f"- vessel: {vessel.get('vessel')}\n"
        f"- vessel_desc: {vessel.get('vessel_desc')}\n"
        f"- beat skeleton:\n{beat_lines}\n"
        "Weave the vessel into panels as a genre-native presence. "
        "Teacher-mode: doctrine earned (wound→turn→renewal). "
        "Music-mode: motif felt (opening→mid→closing). "
        "The brand teacher or musician is NEVER named in-story.\n"
    )


def build_chapter_writer_prompt(
    story_handoff: Mapping[str, Any],
    *,
    chapter_number: int,
    series_id: str,
    chapter_id: str,
    mode: str | None = None,
    genre_id: str | None = None,
) -> str:
    """Deterministic prompt text for replay keys and future live backends.

    When *mode* is set (or present on the story handoff), appends the genre-native
    vessel block from ``manga_mode_vessels.yaml`` via ``load_vessel`` (M4).
    """
    tpl = _load_prompt_template()
    excerpt = _story_chapter_excerpt(story_handoff, chapter_number)
    base = tpl.format(
        series_id=series_id,
        chapter_id=chapter_id,
        chapter_number=chapter_number,
        story_chapter_json=excerpt,
    )
    return base + _mode_vessel_prompt_block(
        story_handoff, mode=mode, genre_id=genre_id,
    )


def _normalize_pair(
    writer_handoff: dict[str, Any],
    internal_record: dict[str, Any],
    *,
    schema_version: str,
    series_id: str,
    chapter_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    wh = dict(writer_handoff)
    ir = dict(internal_record)
    wh.setdefault("schema_version", schema_version)
    wh["artifact_type"] = "chapter_script_writer_handoff"
    wh["series_id"] = series_id
    wh["chapter_id"] = chapter_id
    ir.setdefault("schema_version", schema_version)
    ir["artifact_type"] = "chapter_script_internal_record"
    ir["series_id"] = series_id
    ir["chapter_id"] = chapter_id
    return wh, ir


def write_chapter_script_pair(
    client: LLMClient,
    story_handoff: Mapping[str, Any],
    *,
    chapter_number: int,
    series_id: str,
    chapter_id: str,
    schema_version: str = "1.0.0",
    prompt_version: str = "chunk_a_v1",
    debug_path: Path | None = None,
    schema_hint: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Call the LLM client (replay or future live), validate both artifacts, return pair.

    The client must return a JSON object with keys ``chapter_script_writer_handoff`` and
    ``chapter_script_internal_record`` (see replay fixtures).
    """
    prompt = build_chapter_writer_prompt(
        story_handoff,
        chapter_number=chapter_number,
        series_id=series_id,
        chapter_id=chapter_id,
        mode=story_handoff.get("mode"),
        genre_id=(
            story_handoff.get("genre_id")
            or story_handoff.get("genre")
            or (story_handoff.get("mode_vessel") or {}).get("vessel_genre")
        ),
    )
    hint = schema_hint if schema_hint is not None else {}
    raw = client.generate_json(
        prompt,
        hint,
        debug_path=debug_path,
        prompt_version=prompt_version,
    )
    if not isinstance(raw, dict):
        raise TypeError("LLM response must be a JSON object")
    missing = [k for k in _PAIR_KEYS if k not in raw]
    if missing:
        raise ValueError(f"LLM response missing keys: {missing}")
    wh, ir = _normalize_pair(
        raw["chapter_script_writer_handoff"],
        raw["chapter_script_internal_record"],
        schema_version=schema_version,
        series_id=series_id,
        chapter_id=chapter_id,
    )
    validate_instance(wh, "chapter_script_writer_handoff")
    validate_instance(ir, "chapter_script_internal_record")
    assert_handoff_has_no_transmission_leakage(wh)
    return wh, ir
