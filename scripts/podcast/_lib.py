from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Deterministic ElevenLabs ID for "Rachel" (canonical in narrator_voice_assignments header).
_FALLBACK_ELEVENLABS_RACHEL = "21m00Tcm4TlvDq8ikWAM"

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

def load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None or not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def norm_locale(loc: str) -> str:
    """brand_registry uses en_US; TTS uses en-US."""
    if "_" in loc and "-" not in loc:
        p = loc.split("_", 1)
        return f"{p[0]}-{p[1]}"
    return loc


def load_video_plan(book_dir: Path) -> dict[str, Any]:
    plans = list(book_dir.glob("video_plan.json"))
    if not plans:
        raise FileNotFoundError(f"No video_plan.json under {book_dir}")
    return json.loads(plans[0].read_text(encoding="utf-8"))


def atoms_by_type(plan: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for seg in plan.get("narration_segments") or []:
        t = (seg.get("type") or "").upper()
        out[t] = (seg.get("text") or "").strip()
    return out


def cjk_locale(locale: str) -> bool:
    loc = norm_locale(locale)
    return loc.split("-", 1)[0].lower() in {"ja", "ko", "zh"} or loc in {
        "ja-JP",
        "ko-KR",
        "zh-CN",
        "zh-TW",
        "zh-HK",
        "zh-SG",
    }


def resolve_voice_config(teacher_id: str, brand_id: str, locale: str) -> dict[str, Any]:
    """Resolve narrator stack from locale_voice_routing; optional full narrator YAML via env."""
    loc = norm_locale(locale)
    routing = load_yaml(REPO_ROOT / "config" / "tts" / "locale_voice_routing.yaml")
    key = f"{teacher_id}__{brand_id}"
    voice_row: dict[str, Any] | None = None
    if os.environ.get("PHOENIX_LOAD_NARRATOR_ASSIGNMENTS", "").strip() == "1":
        assign = load_yaml(REPO_ROOT / "config" / "tts" / "narrator_voice_assignments.yaml")
        entry = (assign.get("authors") or {}).get(key)
        if entry:
            voices = entry.get("voices") or {}
            voice_row = voices.get("audiobook") or voices.get("youtube") or next(
                iter(voices.values()), None
            )
    en_eu = (routing.get("en_eu_locales") or {}).get(loc, {})
    cjk = (routing.get("cjk_locales") or {}).get(loc, {})
    edge_default = (
        (cjk.get("edge_tts_default") if cjk else None)
        or (en_eu.get("edge_tts_default") if en_eu else None)
        or "en-US-JennyNeural"
    )
    el_cfg = (routing.get("provider_config") or {}).get("elevenlabs") or {}
    model = el_cfg.get("model") or "eleven_multilingual_v2"

    if voice_row:
        provider = (voice_row.get("provider") or "edge_tts").lower()
        voice_id = voice_row.get("voice_id") or voice_row.get("reference_id") or ""
        edge_fb = voice_row.get("edge_fallback") or edge_default
        if provider == "elevenlabs" and voice_id and not re.match(r"^[a-zA-Z0-9]{20,}$", voice_id):
            cat = (
                load_yaml(REPO_ROOT / "config" / "tts" / "narrator_voice_assignments.yaml").get(
                    "elevenlabs_voice_catalog"
                )
                or {}
            )
            voice_id = str(cat.get(voice_id, voice_id))
        return {
            "provider": provider,
            "voice_id": voice_id,
            "reference_id": voice_row.get("reference_id") or "",
            "model": model,
            "edge_fallback": edge_fb,
            "locale": loc,
        }

    if cjk_locale(loc):
        return {
            "provider": "cosyvoice2",
            "voice_id": "",
            "reference_id": "english_female",
            "model": model,
            "edge_fallback": edge_default,
            "locale": loc,
        }
    # EN primary markets → ElevenLabs; other EU/LATAM locales → Edge default voice for that locale.
    if loc.lower() in ("en-us", "en-gb"):
        return {
            "provider": "elevenlabs",
            "voice_id": _FALLBACK_ELEVENLABS_RACHEL,
            "reference_id": "",
            "model": model,
            "edge_fallback": edge_default,
            "locale": loc,
        }
    return {
        "provider": "edge_tts",
        "voice_id": "",
        "reference_id": "",
        "model": model,
        "edge_fallback": edge_default,
        "locale": loc,
    }


def segment_music_profile(segment: str, topic: str) -> tuple[str, str]:
    """Return (music_role, mood_hint) for select_track topic/mood scoring."""
    _ = topic
    if segment == "scene_setting":
        return "grounding", "calm"
    if segment == "story":
        return "contemplative", "calm"
    if segment == "guided_practice":
        return "breath", "calm"
    if segment == "integration":
        return "grounding", "calm"
    return "stillness", "calm"


def format_structure(fmt: str) -> dict[str, Any]:
    pf = load_yaml(REPO_ROOT / "config" / "podcast" / "podcast_format.yaml")
    structures = (pf.get("episode_structure") or {}).get(fmt) or {}
    if not structures:
        raise ValueError(f"Unknown podcast format {fmt!r} in podcast_format.yaml")
    return structures


def episode_id_for(
    teacher_id: str,
    topic: str,
    locale: str,
    week: str,
    fmt: str,
    series_slug: str,
) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", f"{teacher_id}_{topic}_{series_slug}_{locale}_{week}_{fmt}")
    return safe.strip("_")


def stable_guid(episode_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"phoenix-omega:podcast:{episode_id}"))


def brand_podcast_pilot_brand() -> str | None:
    plans = load_yaml(REPO_ROOT / "config" / "podcast" / "brand_podcast_plans.yaml")
    pilot = plans.get("pilot") or {}
    return pilot.get("brand")


def brand_has_podcast(brand_id: str) -> bool:
    """True if brand is podcast-pilot anchor or listed under optional production_brands."""
    plans = load_yaml(REPO_ROOT / "config" / "podcast" / "brand_podcast_plans.yaml")
    if brand_podcast_pilot_brand() == brand_id:
        return True
    if brand_id in (plans.get("production_brands") or []):
        return True
    return False


def podcast_locale_for_brand(brand_id: str, lane_locale: str) -> str:
    """Pilot brand uses es-US (es_latam) per brand_podcast_plans; else lane locale."""
    plans = load_yaml(REPO_ROOT / "config" / "podcast" / "brand_podcast_plans.yaml")
    if brand_podcast_pilot_brand() == brand_id:
        m = plans.get("markets") or {}
        es = m.get("es_latam") or {}
        return es.get("locale") or "es-US"
    return norm_locale(lane_locale)
