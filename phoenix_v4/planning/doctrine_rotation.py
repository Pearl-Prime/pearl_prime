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


def spacing_window(pool_size: int, chapter_count: int) -> int:
    """Bounded-reuse spacing window = ``min(pool_size, chapter_count)`` (>= 1).

    A doctrine may not repeat within this many chapters. When the lesson library
    grows past the chapter count the window widens to the full pool size, so the
    rule auto-tightens back toward strict no-repeat with no code change.
    """
    ps = max(1, int(pool_size or 1))
    cc = max(1, int(chapter_count or ps))
    return min(ps, cc)


def _distinct_pool_ids(pool: list[dict]) -> set[str]:
    return {
        normalize_doctrine_id(str(a.get("atom_id") or ""))
        for a in pool
        if normalize_doctrine_id(str(a.get("atom_id") or ""))
    }


def _least_recently_used_atom(
    pool: list[dict], recent: list[str]
) -> Optional[dict]:
    """Fail-safe pick: the pool atom used longest ago (never-used first).

    Deterministic — ties break on pool order — so re-renders at the same seed
    reproduce. Returns ``None`` only when the pool is empty.
    """
    best: Optional[dict] = None
    best_key: Optional[tuple[int, int]] = None
    for pos, atom in enumerate(pool):
        aid = normalize_doctrine_id(str(atom.get("atom_id") or ""))
        last_used = -1  # never used → most preferred
        for i, rid in enumerate(recent):
            if rid == aid:
                last_used = i
        key = (last_used, pos)
        if best_key is None or key < best_key:
            best_key = key
            best = atom
    return best


def pick_doctrine_atom_by_id(
    pool: list[dict],
    doctrine_id: str,
    *,
    used_doctrine_ids: Optional[set[str]] = None,
    current_chapter_doctrine_id: Optional[str] = None,
    recent_doctrine_ids: Optional[list[str]] = None,
    chapter_count: Optional[int] = None,
) -> Optional[dict]:
    """
    Select the pool atom for ``doctrine_id`` under BOUNDED-REUSE spacing.

    Design intent (docs/doctrine_distribution_plan.md rules 1–2, bounded-reuse
    revision): each chapter gets exactly ONE doctrine variant, SHARED across every
    REFLECTION slot in that chapter. A variant MAY repeat across chapters, but not
    within a spacing window of ``min(pool_size, chapter_count)`` chapters, and never
    in two adjacent chapters. This lets a small lesson library (e.g. 5 anxiety
    variants) still cover all 12 chapters with spaced reuse; when the library grows
    past the chapter count the window widens back toward strict no-repeat.

    ``recent_doctrine_ids`` is the ORDERED list of doctrines assigned to PRIOR
    chapters (oldest→newest) — spacing needs recency, which the legacy unordered
    ``used_doctrine_ids`` set cannot express (it is honored as a conservative
    fallback: every entry counts as recent).

    ``current_chapter_doctrine_id`` names this chapter's single doctrine; a
    ``target`` equal to it is an intra-chapter re-pick (multi-REFLECTION templates
    resolve the same doctrine for each slot) and is always allowed.

    Fail-safe: when the assigned doctrine cannot be honored at the required spacing
    (too close a repeat) or is missing from the pool, degrade to the least-recently
    -used pool atom. Never raises; returns ``None`` only when the pool is empty.
    """
    if not pool:
        return None

    target = normalize_doctrine_id(doctrine_id)
    current = normalize_doctrine_id(current_chapter_doctrine_id or "")

    recent = [normalize_doctrine_id(x) for x in (recent_doctrine_ids or []) if x]
    if not recent and used_doctrine_ids:
        # Legacy unordered set — treat every prior id as "recent" (conservative).
        recent = [normalize_doctrine_id(x) for x in used_doctrine_ids if x]

    def _find(tid: str) -> Optional[dict]:
        for atom in pool:
            if normalize_doctrine_id(str(atom.get("atom_id") or "")) == tid:
                return atom
        return None

    if not target:
        return _least_recently_used_atom(pool, recent)

    # Intra-chapter re-pick: same doctrine shared across a chapter's slots (rule 1).
    if target == current:
        hit = _find(target)
        return hit if hit is not None else _least_recently_used_atom(pool, recent)

    window = spacing_window(
        len(_distinct_pool_ids(pool)),
        chapter_count if chapter_count is not None else len(recent) + 1,
    )
    # Blocked: target used within the last (window-1) chapters, or in the adjacent one.
    blocked = set(recent[-(window - 1):]) if window > 1 else set()
    if recent:
        blocked.add(recent[-1])

    hit = _find(target)
    if hit is not None and target not in blocked:
        return hit

    # Fail-safe: assigned doctrine unusable — degrade to least-recently-used rather
    # than dropping the slot (silent gap) or raising (the pre-#4673 crash).
    if hit is None:
        logger.warning(
            "doctrine_rotation: assigned %s missing from pool (size %d) — LRU fallback",
            target,
            len(pool),
        )
    else:
        logger.info(
            "doctrine_rotation: assigned %s repeats within window %d — LRU fallback",
            target,
            window,
        )
    return _least_recently_used_atom(pool, recent)


def is_reflection_rotation_slot(slot_type: str) -> bool:
    return (slot_type or "").strip().upper() in _REFLECTION_SLOT_TYPES
