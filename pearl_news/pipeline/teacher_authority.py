"""
Pearl News teacher authority loader — single source of truth: Pearl_Prime.

Operator directive 2026-05-15: "yaml is doctrine authority not canonical-pack."
Operator directive 2026-05-17: "There should not be separate authors for Pearl
News. The authors should come from Pearl Prime."

Pearl_Prime owns `SOURCE_OF_TRUTH/teacher_banks/<id>/doctrine/doctrine.yaml`
and `signature_vibe.yaml`. Pearl News teacher_topic_packs (and the older
`TEACHER_PEDAGOGY` hardcoded dict in assemble_v52.py) carry their own cached
identity blocks that historically drifted from doctrine — display_name typos
("Joshin Sensei" → doctrine says "Joshin"), shortened tradition strings, etc.

This module is the canonicalization layer: at runtime, callers ask here for
a teacher's identity / voice / forbidden_claims, and we read Pearl_Prime's
doctrine + signature_vibe live. The 59 pack `identity:` blocks become inert
cache that we can prune later — but until then, runtime is doctrine-driven.

Usage:

    from pearl_news.pipeline.teacher_authority import load_teacher_authority

    auth = load_teacher_authority("ahjan", repo_root=Path("."))
    print(auth["display_name"])        # "Ahjan"
    print(auth["tradition"])           # full Pearl_Prime string
    print(auth["forbidden_claims"])    # doctrine-authoritative list
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


def _read_yaml(path: Path) -> dict[str, Any]:
    if yaml is None or not path.exists():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        logger.warning("teacher_authority: failed to parse %s: %s", path, exc)
        return {}


def _doctrine_path(repo_root: Path, teacher_id: str) -> Path:
    """Pearl_Prime canonical location. Falls back to flat-file variant for legacy banks."""
    nested = repo_root / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id / "doctrine" / "doctrine.yaml"
    if nested.exists():
        return nested
    return repo_root / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id / "doctrine.yaml"


def _signature_vibe_path(repo_root: Path, teacher_id: str) -> Path:
    return repo_root / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id / "doctrine" / "signature_vibe.yaml"


@lru_cache(maxsize=128)
def _load_authority_cached(teacher_id: str, repo_root_str: str) -> dict[str, Any]:
    """Cached load. The cache is per-process; tests should call cache_clear()."""
    repo_root = Path(repo_root_str)
    doctrine = _read_yaml(_doctrine_path(repo_root, teacher_id))
    vibe = _read_yaml(_signature_vibe_path(repo_root, teacher_id))

    if not doctrine:
        logger.warning("teacher_authority: no doctrine.yaml found for %s", teacher_id)
        return {"teacher_id": teacher_id, "_authority_status": "no_doctrine"}

    # Build the unified authority record. Doctrine is canonical for identity;
    # signature_vibe contributes voice-level constraints.
    display_name = (
        doctrine.get("display_name")
        or doctrine.get("teacher_display_name")
        or teacher_id.replace("_", " ").title()
    ).strip()

    # attribution_name: how the teacher is named in article bylines. Doctrine
    # may specify this explicitly (e.g., "Channeler Junko"); otherwise derive
    # from display_name. Pearl News earlier conventions like "Teacher Ahjan"
    # are kept as fallback only when doctrine is silent on attribution.
    attribution_name = (
        doctrine.get("attribution_name")
        or doctrine.get("byline_name")
        or display_name
    ).strip()

    tradition_long = (doctrine.get("tradition") or "").strip()
    tradition_short = (
        doctrine.get("tradition_short")
        or _derive_tradition_short(tradition_long)
    ).strip()

    record: dict[str, Any] = {
        "teacher_id": teacher_id,
        "display_name": display_name,
        "attribution_name": attribution_name,
        "tradition": tradition_long,
        "tradition_short": tradition_short,
        "primary_methods": doctrine.get("primary_methods", ""),
        "core_principles": doctrine.get("core_principles", ""),
        "tone_profile": doctrine.get("tone_profile", ""),
        "forbidden_claims": list(doctrine.get("forbidden_claims") or []),
        "prohibited_outcomes": list(doctrine.get("prohibited_outcomes") or []),
        "tone_boundaries": list(doctrine.get("tone_boundaries") or []),
        "glossary": list(doctrine.get("glossary") or []),
        "location": doctrine.get("location", ""),
        "sacred_site": doctrine.get("sacred_site", ""),
        # signature_vibe contributes prose-level constraints
        "voice_instruction": vibe.get("voice_instruction", ""),
        "sentence_constraints": vibe.get("sentence_constraints", {}),
        "vocabulary": vibe.get("vocabulary", {}),
        "_authority_status": "pearl_prime_doctrine",
        "_doctrine_path": str(_doctrine_path(repo_root, teacher_id).relative_to(repo_root)),
    }
    return record


def _derive_tradition_short(tradition_long: str) -> str:
    """When doctrine doesn't supply tradition_short, derive a 2-3 word slug from the long form."""
    if not tradition_long:
        return ""
    head = tradition_long.split(";")[0].strip()
    # Strip parenthetical detail
    paren = head.find("(")
    if paren != -1:
        head = head[:paren].strip()
    # Cap at ~4 words
    words = head.split()
    return " ".join(words[:4])


def load_teacher_authority(teacher_id: str, repo_root: Path) -> dict[str, Any]:
    """Public entrypoint. Returns the canonical Pearl_Prime authority record for one teacher."""
    return _load_authority_cached(teacher_id, str(repo_root.resolve()))


def apply_authority_to_pack(
    pack: dict[str, Any],
    teacher_id: str,
    repo_root: Path,
) -> dict[str, Any]:
    """
    Overlay Pearl_Prime's authority record on a loaded teacher_topic_pack dict.
    Doctrine wins on every identity field. Pack-specific keys outside the
    identity block (persona, topic_fit, voice-bearing sections) pass through.

    Returns a new dict; does not mutate the input.
    """
    auth = load_teacher_authority(teacher_id, repo_root)
    if auth.get("_authority_status") != "pearl_prime_doctrine":
        # Doctrine missing — keep the pack's identity as best-effort fallback
        return dict(pack)

    out = dict(pack)
    pack_identity = dict(pack.get("identity") or {})
    # Fields where doctrine is authoritative — overwrite pack values
    pack_identity["display_name"] = auth["display_name"]
    pack_identity["attribution_name"] = auth["attribution_name"]
    pack_identity["tradition"] = auth["tradition"]
    pack_identity["tradition_short"] = auth["tradition_short"]
    # Pack may carry pack-specific fields (teacher_years, affiliation_safe_line,
    # teacher_setting_options) — those stay.
    out["identity"] = pack_identity
    # Surface the authority record for downstream consumers (slot engine, etc.)
    out["_teacher_authority"] = auth
    return out


def list_pearl_prime_active_teachers(repo_root: Path) -> list[str]:
    """
    Pearl_Prime is the source of truth for who is an active teacher. Pearl News
    must intersect this with its own roster (pearl_news/config/teacher_news_roster.yaml)
    before publishing. Delegates to pearl_prime.teacher_system.
    """
    try:
        from pearl_prime.teacher_system import list_active_teacher_ids
        return list_active_teacher_ids(repo_root)
    except ImportError:
        logger.warning("pearl_prime.teacher_system not importable — returning empty active list")
        return []
