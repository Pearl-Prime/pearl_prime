"""
Keyword bank for naming engine.
Sources:
  - config/catalog_planning/series_templates.yaml (series → search_keywords)
  - config/catalog_planning/engine_title_angles.yaml (engine_id → human-readable phrases)
Read-only; no writes. Authority: SYSTEMS_DOCUMENTATION §29.2, EXPERIENCE_LAYER_ANTI_SPAM_SPEC §16.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_CATALOG = REPO_ROOT / "config" / "catalog_planning"
SERIES_TEMPLATES_PATH = CONFIG_CATALOG / "series_templates.yaml"
ENGINE_ANGLES_PATH = CONFIG_CATALOG / "engine_title_angles.yaml"

_CACHE: dict[str, Any] | None = None
_ENGINE_CACHE: dict[str, Any] | None = None


def _load_series_templates() -> dict[str, Any]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not SERIES_TEMPLATES_PATH.exists() or yaml is None:
        _CACHE = {"series": {}}
        return _CACHE
    with open(SERIES_TEMPLATES_PATH) as f:
        data = yaml.safe_load(f) or {}
    _CACHE = data
    return _CACHE


def _load_engine_angles() -> dict[str, Any]:
    global _ENGINE_CACHE
    if _ENGINE_CACHE is not None:
        return _ENGINE_CACHE
    if not ENGINE_ANGLES_PATH.exists() or yaml is None:
        _ENGINE_CACHE = {}
        return _ENGINE_CACHE
    with open(ENGINE_ANGLES_PATH) as f:
        data = yaml.safe_load(f) or {}
    _ENGINE_CACHE = data.get("engine_angles", {})
    return _ENGINE_CACHE


def load_series_templates() -> dict[str, Any]:
    """Load series templates YAML. Returns dict with 'series' key."""
    return _load_series_templates()


def get_engine_angle_phrase(engine_id: str, seed_int: int = 0) -> str:
    """
    Get human-readable angle phrase for an engine.
    Uses primary_phrase by default; rotates through alt_phrases based on seed.
    NEVER returns the raw engine_id — always returns a reader-facing phrase.
    """
    angles = _load_engine_angles()
    cfg = angles.get(engine_id)
    if not cfg:
        # Fallback: convert engine_id to title case phrase (better than raw)
        return engine_id.replace("_", " ").title()
    alt = cfg.get("alt_phrases", [])
    if alt and seed_int > 0:
        return alt[seed_int % len(alt)]
    return cfg.get("primary_phrase", engine_id.replace("_", " ").title())


def get_engine_subtitle_hook(engine_id: str) -> str:
    """Get the engine-specific subtitle hook clause."""
    angles = _load_engine_angles()
    cfg = angles.get(engine_id, {})
    return cfg.get("subtitle_hook", "")


def get_engine_angle_pool(engine_id: str) -> list[str]:
    """Return the full reader-facing angle pool for an engine:
    [primary_phrase, *alt_phrases]. Used by the generator to rotate creative
    titles deterministically per book seed instead of always using the single
    primary_phrase. Returns [] if the engine has no configured angle entry."""
    angles = _load_engine_angles()
    cfg = angles.get(engine_id)
    if not cfg:
        return []
    pool: list[str] = []
    primary = cfg.get("primary_phrase")
    if primary:
        pool.append(primary)
    for alt in (cfg.get("alt_phrases") or []):
        if alt and alt not in pool:
            pool.append(alt)
    return pool


def get_keywords(
    series_id: str,
    angle_id: str,
    topic_id: str | None = None,
    engine_id: str | None = None,
) -> dict[str, Any]:
    """
    Primary: first search_keyword + angle as natural phrase.
    Secondary: remaining search_keywords from series.

    Resolution order for angle phrase:
      1. engine_title_angles.yaml (if engine_id matches → human-readable phrase)
      2. Series angle slug (if series_id found and angle is a series angle)
      3. Topic slug as phrase (if angle is "{topic_id}_general")
      4. NEVER raw engine_id like "false_alarm" or "spiral"
    """
    data = load_series_templates()

    # Try series_id first, then topic_id as series fallback
    series_cfg = (data.get("series") or {}).get(series_id)
    if not series_cfg and topic_id:
        series_cfg = (data.get("series") or {}).get(topic_id)

    # Resolve angle phrase — engine_title_angles takes priority
    engine_angles = _load_engine_angles()
    if angle_id in engine_angles:
        angle_phrase = engine_angles[angle_id].get("primary_phrase", angle_id.replace("_", " "))
    elif topic_id and angle_id == f"{topic_id}_general":
        angle_phrase = topic_id.replace("_", " ")
    else:
        # Check if angle_id is actually an engine_id (common in full catalog generation)
        if angle_id in engine_angles:
            angle_phrase = engine_angles[angle_id].get("primary_phrase", angle_id.replace("_", " "))
        else:
            angle_phrase = angle_id.replace("_", " ")

    # Topic-true keyword fallback: when no series entry resolves, use the TOPIC
    # (not the engine angle) so {PrimaryKeyword} names the book's actual subject.
    # Using the engine angle here is what made titles/subtitles wear another
    # topic's phrasing (a Boundaries book reading "When Your Mind Screams Danger").
    topic_kw = (topic_id or "").replace("_", " ").strip()

    if not series_cfg:
        return {"primary": topic_kw or angle_phrase, "secondary": [], "engine_angle": angle_phrase, "series_title": ""}

    series_title = series_cfg.get("series_title") or ""
    search_keywords = list(series_cfg.get("search_keywords") or [])
    if not search_keywords:
        return {"primary": topic_kw or angle_phrase, "secondary": [], "engine_angle": angle_phrase, "series_title": series_title}

    primary = f"{search_keywords[0]}".strip()
    secondary = search_keywords[1:] if len(search_keywords) > 1 else []
    return {"primary": primary, "secondary": secondary, "engine_angle": angle_phrase, "series_title": series_title}
