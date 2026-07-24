"""Mood-register → Storyblocks Audio query + licensed bed resolution (Lane 04).

Search is free (no MAU). HD confirm_selection meters the shared MAU ledger.
Bank path: artifacts/storyblocks_licensed/{work_unit_id}/audio/{asset_id}.{ext}
Does not touch assets/music_bank/ (narration/audiobook bank — separate).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import yaml

from scripts.storyblocks.api_client import StoryblocksAPIClient
from scripts.storyblocks.license_store import LicenseStore, default_license_store

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_QUERY_MAP = REPO_ROOT / "config" / "social" / "mood_register_audio_query_map.yaml"

MOOD_REGISTERS = (
    "tense_anxious",
    "heavy_low",
    "grounding_somatic",
    "empowering_courage",
)


def load_mood_audio_query_map(path: Path | None = None) -> dict[str, Any]:
    p = path or Path(os.environ.get("STORYBLOCKS_MOOD_AUDIO_MAP", str(DEFAULT_QUERY_MAP)))
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "mood_register_audio" not in data:
        raise ValueError(f"invalid mood audio query map: {p}")
    return data


def query_params_for_mood(
    mood_register: str,
    *,
    map_data: dict[str, Any] | None = None,
    page: int = 1,
    results_per_page: int = 25,
) -> dict[str, Any]:
    """Compile Storyblocks /api/v2/audio/search params for a mood_register cluster."""
    data = map_data or load_mood_audio_query_map()
    block = (data.get("mood_register_audio") or {}).get(mood_register)
    if not isinstance(block, dict):
        raise KeyError(f"mood_register not in query map: {mood_register!r}")
    keywords = block.get("keywords") or []
    if isinstance(keywords, list):
        keywords_s = ",".join(str(k) for k in keywords)
    else:
        keywords_s = str(keywords)
    filtered = block.get("filtered_keywords") or []
    if isinstance(filtered, list):
        filtered_s = ",".join(str(k) for k in filtered)
    else:
        filtered_s = str(filtered) if filtered else ""
    params: dict[str, Any] = {
        "keywords": keywords_s,
        "content_type": block.get("content_type") or data.get("content_type_default") or "music",
        "has_vocals": "false" if block.get("has_vocals") is False else (
            "true" if block.get("has_vocals") is True else None
        ),
        "extended": data.get("extended_default")
        or "moods,genres,bpm,keywords,instruments,pro,publisher",
        "page": page,
        "results_per_page": results_per_page,
        "safe_search": "true",
    }
    if block.get("min_bpm") is not None:
        params["min_bpm"] = int(block["min_bpm"])
    if block.get("max_bpm") is not None:
        params["max_bpm"] = int(block["max_bpm"])
    if filtered_s:
        params["filtered_keywords"] = filtered_s
    # Drop Nones so HMAC request stays clean
    return {k: v for k, v in params.items() if v is not None}


def search_audio_for_mood(
    client: StoryblocksAPIClient,
    mood_register: str,
    *,
    brand_id: str,
    locale: str,
    work_unit_id: str,
    map_data: dict[str, Any] | None = None,
    page: int = 1,
    results_per_page: int = 25,
) -> dict[str, Any]:
    """Search Storyblocks Audio for a mood cluster — does NOT touch MAU."""
    compiled = query_params_for_mood(
        mood_register, map_data=map_data, page=page, results_per_page=results_per_page
    )
    return client.search_audio(
        compiled["keywords"],
        brand_id=brand_id,
        locale=locale,
        work_unit_id=work_unit_id,
        content_type=str(compiled.get("content_type", "music")),
        min_bpm=compiled.get("min_bpm"),
        max_bpm=compiled.get("max_bpm"),
        has_vocals=(
            False
            if compiled.get("has_vocals") == "false"
            else True
            if compiled.get("has_vocals") == "true"
            else None
        ),
        filtered_keywords=compiled.get("filtered_keywords"),
        extended=str(compiled.get("extended", "")),
        page=page,
        results_per_page=results_per_page,
    )


def resolve_licensed_audio_bed(
    mood_register: str,
    work_unit_id: str | None,
    *,
    license_store: LicenseStore | None = None,
) -> Path | None:
    """
    Return a licensed Storyblocks audio path for this mood/work unit when present.

    Resolution order:
      1. STORYBLOCKS_AUDIO_BED_PATH env override (tests / operator pin)
      2. work-unit audio/ dir: *.license.json with metadata.mood_register match
      3. work-unit audio/ dir: any existing audio file (single-smoke convenience)
    """
    override = os.environ.get("STORYBLOCKS_AUDIO_BED_PATH", "").strip()
    if override:
        p = Path(override)
        if p.is_file():
            return p
        logger.warning("STORYBLOCKS_AUDIO_BED_PATH set but missing: %s", override)
        return None
    if not work_unit_id:
        return None
    store = license_store or default_license_store
    audio_dir = store.work_unit_dir(work_unit_id) / "audio"
    if not audio_dir.is_dir():
        return None

    mood_hit: Path | None = None
    any_hit: Path | None = None
    for side in sorted(audio_dir.glob("*.license.json")):
        try:
            import json

            data = json.loads(side.read_text(encoding="utf-8"))
        except Exception:
            continue
        local = data.get("local_uri")
        if not local:
            continue
        path = Path(local)
        if not path.is_file():
            continue
        meta = data.get("metadata") or {}
        if meta.get("mood_register") == mood_register:
            mood_hit = path
            break
        if any_hit is None:
            any_hit = path
    if mood_hit is not None:
        return mood_hit
    # Prefer mood-tagged; else first licensed audio under the work unit (pilot smoke).
    return any_hit
