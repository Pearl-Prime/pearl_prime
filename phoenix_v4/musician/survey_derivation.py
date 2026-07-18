"""Derive musician bank YAML fragments from a structured survey response (V1)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


def load_survey(path: Path) -> dict[str, Any]:
    if yaml is None or not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def survey_to_profile_dict(survey: dict[str, Any], musician_id: str) -> dict[str, Any]:
    """Return fields for ``profile.yaml``."""
    ident = survey.get("identity") or {}
    themes_block = survey.get("themes") or {}
    healing = survey.get("healing_intent") or {}
    voice = survey.get("voice_craft") or {}
    primary = themes_block.get("primary_themes") or []
    if not isinstance(primary, list):
        primary = [str(primary)]
    return {
        "musician_id": musician_id,
        "display_name": str(ident.get("display_name") or musician_id),
        "years_active": ident.get("years_active"),
        "primary_genre": str(ident.get("primary_genre") or ""),
        "secondary_genres": ident.get("secondary_genres") or [],
        "primary_instruments": ident.get("primary_instruments") or [],
        "creative_phases": ident.get("creative_phases") or [],
        "themes": primary,
        "listener_hope_one": str(themes_block.get("listener_hope_one") or ""),
        "healing_intent_summary": str(healing.get("what_helps_heal") or ""),
        "touchstones": (survey.get("material_for_reflection") or {}).get("touchstone_tracks") or [],
        "synthetic": bool(survey.get("synthetic")),
    }


def survey_to_themes_yaml(survey: dict[str, Any]) -> dict[str, Any]:
    tb = survey.get("themes") or {}
    return {
        "primary_themes": tb.get("primary_themes") or [],
        "avoided_themes": tb.get("avoided_themes") or [],
        "listener_hope_one": tb.get("listener_hope_one"),
    }


def survey_to_voice_yaml(survey: dict[str, Any]) -> dict[str, Any]:
    vc = survey.get("voice_craft") or {}
    return {
        "voice_person": vc.get("voice_person"),
        "register": vc.get("register"),
        "pacing": vc.get("pacing"),
        "signature_devices": vc.get("signature_devices") or [],
    }


def write_bank_from_survey(
    survey_path: Path,
    musician_id: str,
    dest_dir: Path,
) -> None:
    """Write profile.yaml, themes.yaml, voice_profile.yaml under ``dest_dir``."""
    if yaml is None:
        raise RuntimeError("PyYAML required")
    survey = load_survey(survey_path)
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / "profile.yaml").write_text(
        yaml.safe_dump(survey_to_profile_dict(survey, musician_id), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    (dest_dir / "themes.yaml").write_text(
        yaml.safe_dump(survey_to_themes_yaml(survey), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    (dest_dir / "voice_profile.yaml").write_text(
        yaml.safe_dump(survey_to_voice_yaml(survey), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
