"""
Adjacency-aware opening-mode penalties for enrichment_select persona picks.

Chunk-2 (cohesion_chunk_2_adjacency_selector): when the immediately-preceding slot
was REFLECTION or doctrine-class, penalize ``named_character_scene_cold_open`` STORY
(and similar) atoms that audit TSV flags as high-jolt after teaching prose.

Input index: ``artifacts/analysis/ATOM_PLANNER_FULL_AUDIT_2026-07-08.tsv`` (heuristic —
spot-check, do not trust blind). Heuristic fallback when a row is missing.

Flagship-OFF: gated by ``is_adjacency_selector_active`` — twelve_shape / story_picks
selection is byte-untouched (mirrors #5162 before_story wiring).
"""
from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_TSV = REPO_ROOT / "artifacts" / "analysis" / "ATOM_PLANNER_FULL_AUDIT_2026-07-08.tsv"

# Prior slot types whose exit is teaching/doctrine prose — cold scene open is jarring.
_DOCTRINE_EXIT_SLOTS = frozenset({
    "REFLECTION",
    "TEACHER_DOCTRINE",
    "COMPOSITE_TEACHER_DOCTRINE",
    "COMPOSITE_TEACHER_REFLECTION",
    "TEACHER_DOCTRINE",
    "COMPRESSION",
})

# Audit TSV opening_mode value for the #1 jolt vector after doctrine (CLASS-E handoff).
_JOLT_OPENING_MODE = "named_character_scene_cold_open"

# Opening modes that soften the REFLECTION/doctrine -> STORY seam (audit heuristic).
_SOFT_AFTER_DOCTRINE = frozenset({
    "second_person_direct",
    "continuation_cue",
    "neutral_declarative",
    "abstract_generalization",
    "teaching_frame",
    "exercise_or_somatic_directive",
})

ADJACENCY_PENALTY_JOLT = -0.35
ADJACENCY_BONUS_SOFT = 0.10

_NAMED_CHARACTER_SCENE_RE = re.compile(
    r"^[A-Z][a-z]{2,15}\s+(sits|opens|arrives|stares|notices|walks|stands|leans|"
    r"reaches|picks|checks|scrolls|types|clicks|dials|answers|hangs|waits|"
    r"freezes|hesitates|pauses|wakes|lies|stays|holds|drops|pulls|pushes)\b"
)


def is_adjacency_selector_active(spine_context: Optional[dict[str, Any]]) -> bool:
    """True when adjacency penalties may apply (non-flagship catalog path).

    Mirrors #5162: twelve_shape / story_picks flagship selection stays byte-neutral.
    """
    if not spine_context:
        return True
    if spine_context.get("twelve_shape_continuity"):
        return False
    if spine_context.get("chapter_continuity_plan"):
        return False
    # Explicit story_picks on any chapter → flagship-shaped plan; leave picks alone.
    ch_entries = spine_context.get("chapters") or []
    for entry in ch_entries:
        if isinstance(entry, dict) and entry.get("story_picks"):
            return False
    plan = spine_context.get("book_plan") or {}
    if isinstance(plan, dict):
        for entry in plan.get("chapters") or []:
            if isinstance(entry, dict) and entry.get("story_picks"):
                return False
    return True


@lru_cache(maxsize=1)
def _load_opening_mode_index() -> Dict[tuple[str, str, str, str], str]:
    """Build (persona, topic, slot, atom_id) -> opening_mode from audit TSV."""
    index: Dict[tuple[str, str, str, str], str] = {}
    if not AUDIT_TSV.exists():
        return index
    with AUDIT_TSV.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            persona = str(row.get("persona") or "").strip()
            topic = str(row.get("topic") or "").strip()
            slot = str(row.get("slot") or "").strip().upper()
            atom_id = str(row.get("atom_id") or "").strip()
            mode = str(row.get("opening_mode") or "").strip()
            if persona and topic and slot and atom_id and mode:
                index[(persona, topic, slot, atom_id)] = mode
    return index


def resolve_opening_mode(
    atom: Dict[str, Any],
    *,
    persona_id: str = "",
    topic_id: str = "",
    slot_type: str = "",
) -> str:
    """Resolve opening_mode for a candidate atom (TSV first, heuristic fallback)."""
    meta = atom.get("metadata") if isinstance(atom.get("metadata"), dict) else {}
    if meta.get("opening_mode"):
        return str(meta["opening_mode"]).strip()

    atom_id = str(atom.get("atom_id") or "").strip()
    if persona_id and topic_id and slot_type and atom_id:
        key = (persona_id, topic_id, slot_type.strip().upper(), atom_id)
        hit = _load_opening_mode_index().get(key)
        if hit:
            return hit

    content = str(atom.get("content") or "").strip()
    if not content:
        return ""
    first = content.split("\n", 1)[0].strip()
    if _NAMED_CHARACTER_SCENE_RE.match(first):
        return _JOLT_OPENING_MODE
    if first.lower().startswith(("you ", "your ")):
        return "second_person_direct"
    if first.lower().startswith(("now ", "so ", "and so ", "when you")):
        return "continuation_cue"
    return "scene_or_narrative_open"


def adjacency_opening_penalty(
    prior_slot_type: str,
    candidate_opening_mode: str,
) -> float:
    """Additive penalty/bonus for candidate opening_mode given the prior slot type.

    Returns 0.0 when adjacency does not apply (no doctrine exit, empty mode).
  Skips when prior is not doctrine-class; penalizes jolt modes; rewards soft modes.
    """
    prior = (prior_slot_type or "").strip().upper()
    mode = (candidate_opening_mode or "").strip()
    if not prior or not mode:
        return 0.0
    if prior not in _DOCTRINE_EXIT_SLOTS:
        return 0.0
    if mode == _JOLT_OPENING_MODE:
        return ADJACENCY_PENALTY_JOLT
    if mode in _SOFT_AFTER_DOCTRINE:
        return ADJACENCY_BONUS_SOFT
    return 0.0


def adjacency_penalty_for_atom(
    prior_slot_type: str,
    atom: Dict[str, Any],
    *,
    persona_id: str = "",
    topic_id: str = "",
    slot_type: str = "",
) -> float:
    """Convenience: resolve opening_mode then score adjacency."""
    mode = resolve_opening_mode(
        atom,
        persona_id=persona_id,
        topic_id=topic_id,
        slot_type=slot_type,
    )
    return adjacency_opening_penalty(prior_slot_type, mode)
