"""
Doctrine-per-chapter rotation for composite REFLECTION slots.

Authority: docs/doctrine_distribution_plan.md
Config: config/source_of_truth/doctrine_rotation.yaml
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ROTATION_CONFIG = REPO_ROOT / "config" / "source_of_truth" / "doctrine_rotation.yaml"

_REFLECTION_SLOT_TYPES = frozenset({"REFLECTION", "COMPOSITE_TEACHER_REFLECTION"})

_DOCTRINE_ID_RE = re.compile(
    r"^(COMPOSITE_DOCTRINE|REFLECTION)\s+v(\d{2})(?:_\w+)?$",
    re.IGNORECASE,
)


class DoctrineRotationError(Exception):
    """Fail-closed rotation violation (repeat, missing variant, dosage skip)."""


def normalize_doctrine_id(raw: str) -> str:
    """Canonicalize doctrine atom ids (strip suffix tags like _pure)."""
    text = (raw or "").strip()
    if not text:
        return ""
    m = _DOCTRINE_ID_RE.match(text)
    if not m:
        return text
    prefix = m.group(1).upper()
    if prefix == "REFLECTION":
        prefix = "COMPOSITE_DOCTRINE"
    return f"{prefix} v{m.group(2)}"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        import yaml
    except ImportError:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_doctrine_rotation_config(repo_root: Optional[Path] = None) -> dict[str, Any]:
    path = (repo_root or REPO_ROOT) / ROTATION_CONFIG.relative_to(REPO_ROOT)
    return _load_yaml(path)


def _dosage_profile_for_frame(book_frame: str, config: dict[str, Any]) -> dict[str, Any]:
    frame = (book_frame or "somatic_first").strip().lower()
    profiles = config.get("brand_dosage_profiles") or {}
    for _name, profile in profiles.items():
        if not isinstance(profile, dict):
            continue
        frames = [str(f).lower() for f in (profile.get("book_frames") or [])]
        if frame in frames:
            return profile
    return profiles.get("somatic_heavy") or {}


def chapter_gets_composite_reflection(
    chapter_number: int,
    book_frame: str,
    *,
    repo_root: Optional[Path] = None,
) -> bool:
    """Brand dosage gate — whether this chapter should receive rotated composite doctrine."""
    config = load_doctrine_rotation_config(repo_root)
    profile = _dosage_profile_for_frame(book_frame, config)
    allowed = profile.get("reflection_chapters") or list(range(1, 13))
    return int(chapter_number) in {int(c) for c in allowed}


def resolve_chapter_doctrine_id(
    topic_id: str,
    chapter_index0: int,
    *,
    spine_context: Optional[dict[str, Any]] = None,
    book_frame: str = "somatic_first",
    repo_root: Optional[Path] = None,
) -> Optional[str]:
    """
    Resolve the assigned doctrine variant for chapter N.

    Precedence: chapter_continuity_plan doctrine_id → topic_sequences.default_12.
    Returns None when brand dosage skips this chapter or no plan exists.
    """
    ch_num = chapter_index0 + 1
    if not chapter_gets_composite_reflection(ch_num, book_frame, repo_root=repo_root):
        return None

    ctx = spine_context or {}
    plan = ctx.get("chapter_continuity_plan")
    if isinstance(plan, list):
        entry = next((c for c in plan if int(c.get("chapter") or 0) == ch_num), None)
        if isinstance(entry, dict):
            raw = str(entry.get("doctrine_id") or "").strip()
            if raw:
                return normalize_doctrine_id(raw)

    topic = (topic_id or "").strip()
    config = load_doctrine_rotation_config(repo_root)
    sequences = (config.get("topic_sequences") or {}).get(topic) or {}
    default_12 = sequences.get("default_12") or []
    for row in default_12:
        if not isinstance(row, dict):
            continue
        if int(row.get("chapter") or 0) == ch_num:
            raw = str(row.get("doctrine_id") or "").strip()
            return normalize_doctrine_id(raw) if raw else None
    return None


def pick_doctrine_atom_by_id(
    pool: list[dict],
    doctrine_id: str,
    *,
    used_doctrine_ids: Optional[set[str]] = None,
    current_chapter_doctrine_id: Optional[str] = None,
) -> Optional[dict]:
    """
    Select the pool atom matching doctrine_id. Fail closed on a CROSS-chapter repeat.

    Design intent (docs/doctrine_distribution_plan.md rules 1–2): each chapter gets
    exactly ONE doctrine variant, SHARED across every REFLECTION slot in that chapter;
    "no repeats" is a CROSS-chapter guarantee only. Multi-REFLECTION templates
    (e.g. deep_book_6h with 2 REFLECTION slots/chapter) resolve the SAME per-chapter
    doctrine for each slot — that intra-chapter recurrence is expected and MUST NOT
    fail closed. Only a doctrine already assigned to a *prior* chapter is a violation.

    ``current_chapter_doctrine_id`` names the doctrine assigned to the chapter being
    filled; when ``target`` equals it, an entry already present in ``used_doctrine_ids``
    is an intra-chapter re-pick (allowed), not a cross-chapter repeat.
    """
    target = normalize_doctrine_id(doctrine_id)
    if not target:
        return None
    used = used_doctrine_ids or set()
    current = normalize_doctrine_id(current_chapter_doctrine_id or "")
    if target in used and target != current:
        logger.error("doctrine_rotation: repeat blocked — %s already assigned", target)
        raise DoctrineRotationError(f"doctrine repeat blocked: {target}")

    for atom in pool:
        aid = normalize_doctrine_id(str(atom.get("atom_id") or ""))
        if aid == target:
            return atom

    logger.error(
        "doctrine_rotation: variant missing from REFLECTION pool — %s (pool size %d)",
        target,
        len(pool),
    )
    return None


def is_reflection_rotation_slot(slot_type: str) -> bool:
    return (slot_type or "").strip().upper() in _REFLECTION_SLOT_TYPES
