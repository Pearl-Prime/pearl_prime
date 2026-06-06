"""Deterministic heading-variant selector for Pearl News articles.

Reads pearl_news/config/heading_variants.yaml and picks a stable variant per
article based on a blake2b hash of (post_slug | axis). Stable across
re-publishes (same slug + axis -> same variant).

Wired into pearl_news/pipeline/assemble_v52.py: when assembling an article,
the felt_experience and teacher_sees section headers consult this module
instead of using a single fixed string per locale.

Falls back to the legacy fixed string if the variant pool is missing or
malformed. Defense-in-depth so a malformed config never breaks publishing.

Authority: docs/PEARL_NEWS_WRITER_SPEC.md §14.
"""
from __future__ import annotations

import hashlib
import logging
import pathlib
from functools import lru_cache
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

_CONFIG_PATH = pathlib.Path(__file__).resolve().parents[1] / "config" / "heading_variants.yaml"

_AXIS_GEN_Z = "gen_z_impact"
_AXIS_TEACHER = "teacher_sees"


@lru_cache(maxsize=1)
def _load_config() -> dict:
    if not _CONFIG_PATH.exists():
        logger.warning("heading_variants.yaml missing at %s; falling back to fixed strings", _CONFIG_PATH)
        return {}
    try:
        return yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8")) or {}
    except Exception as e:
        logger.warning("heading_variants.yaml failed to parse (%s); falling back", e)
        return {}


def _hash_index(post_slug: str, axis: str, pool_size: int) -> int:
    """blake2b(slug|axis) mod pool_size — stable across re-publishes."""
    if pool_size <= 0:
        return 0
    key = f"{post_slug}|{axis}".encode("utf-8")
    digest = hashlib.blake2b(key, digest_size=4).hexdigest()
    return int(digest, 16) % pool_size


def pick_gen_z_heading(topic: str, locale: str, post_slug: str, fallback: str) -> str:
    """Pick a Gen Z impact heading variant for (topic, locale)."""
    cfg = _load_config()
    pool = ((cfg.get(_AXIS_GEN_Z) or {}).get(topic) or {}).get(locale)
    if not pool or not isinstance(pool, list):
        logger.debug("gen_z pool missing for topic=%s locale=%s; using fallback", topic, locale)
        return fallback
    idx = _hash_index(post_slug, _AXIS_GEN_Z, len(pool))
    return pool[idx]


def pick_teacher_sees_heading(teacher_id: str, post_slug: str, fallback: str) -> str:
    """Pick a teacher-insight heading variant for the given teacher.

    The variant is always in the teacher's primary locale (recorded in the
    config), since each Pearl News teacher publishes only in one locale.
    """
    cfg = _load_config()
    entry = (cfg.get(_AXIS_TEACHER) or {}).get(teacher_id)
    if not entry or not isinstance(entry, dict):
        logger.debug("teacher_sees pool missing for teacher=%s; using fallback", teacher_id)
        return fallback
    pool = entry.get("variants")
    if not pool or not isinstance(pool, list):
        return fallback
    idx = _hash_index(post_slug, _AXIS_TEACHER, len(pool))
    return pool[idx]


def pool_sizes() -> dict:
    """Diagnostic: counts of variants per (axis, dimension). Used by tests + audit reports."""
    cfg = _load_config()
    out: dict = {"gen_z_impact": {}, "teacher_sees": {}}
    for topic, locales in (cfg.get(_AXIS_GEN_Z) or {}).items():
        out["gen_z_impact"][topic] = {loc: len(v) for loc, v in (locales or {}).items()}
    for teacher_id, entry in (cfg.get(_AXIS_TEACHER) or {}).items():
        out["teacher_sees"][teacher_id] = len((entry or {}).get("variants") or [])
    return out


def reset_cache() -> None:
    """Test hook: clears the LRU cache so a hot reload works in unit tests."""
    _load_config.cache_clear()
