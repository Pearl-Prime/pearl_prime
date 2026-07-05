"""Authored TRANSITION atoms — consumer for Part D (de-injection 2026-07-05).

When ``PHOENIX_ENABLE_RENDER_GLUE`` is off, ``chapter_composer`` emits authored
transition prose from ``atoms/{persona}/{topic}/TRANSITION/CANONICAL.txt`` instead
of template bridge families. Atoms may carry metadata::

    ## TRANSITION v01
    ---
    boundary: before_story
    engine: false_alarm
    ---
    Prose here.
    ---

``boundary`` ∈ {after_opening, before_story, before_exercise, before_integration}.
``engine`` is optional — when set, the atom is preferred for chapters on that engine.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Optional

from phoenix_v4.planning.registry_resolver import _load_persona_atoms

BOUNDARIES = frozenset(
    {"after_opening", "before_story", "before_exercise", "before_integration"}
)


def _deterministic_index(seed: str, pool_size: int) -> int:
    if pool_size <= 0:
        return 0
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % pool_size


def load_transition_pool(
    persona_id: str,
    topic_id: str,
    *,
    locale: Optional[str] = None,
    engine: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Return TRANSITION atoms from the persona/topic bank (may be empty)."""
    atoms = _load_persona_atoms(persona_id, topic_id, locale=locale, engine=engine)
    return list(atoms.get("TRANSITION") or [])


def select_authored_transition(
    boundary: str,
    *,
    persona_id: str,
    topic_id: str,
    engine_type: str = "",
    chapter_index: int = 0,
    book_seed: str = "",
    locale: Optional[str] = None,
    used_texts: Optional[set[str]] = None,
) -> str:
    """Pick one authored transition for ``boundary``; ``""`` when none available."""
    b = (boundary or "").strip().lower()
    if b not in BOUNDARIES:
        return ""
    pool = load_transition_pool(
        persona_id, topic_id, locale=locale, engine=(engine_type or None)
    )
    if not pool:
        return ""

    engine_key = (engine_type or "").strip().lower()
    candidates: list[dict[str, Any]] = []
    for atom in pool:
        meta = atom.get("metadata") if isinstance(atom.get("metadata"), dict) else {}
        atom_boundary = str(meta.get("boundary") or atom.get("boundary") or "").strip().lower()
        if atom_boundary and atom_boundary != b:
            continue
        atom_engine = str(meta.get("engine") or atom.get("engine") or "").strip().lower()
        content = str(atom.get("content") or "").strip()
        if not content:
            continue
        norm = " ".join(content.split()).lower()
        if used_texts and norm in used_texts:
            continue
        score = 0
        if atom_engine and engine_key and atom_engine == engine_key:
            score += 2
        elif not atom_engine:
            score += 1
        candidates.append({"atom": atom, "content": content, "score": score, "norm": norm})

    if not candidates:
        return ""

    candidates.sort(
        key=lambda c: (
            -c["score"],
            str(c["atom"].get("atom_id") or ""),
        )
    )
    top_score = candidates[0]["score"]
    tier = [c for c in candidates if c["score"] == top_score]
    seed = f"{book_seed}|{topic_id}|{persona_id}|{b}|ch{chapter_index}|{engine_key}"
    picked = tier[_deterministic_index(seed, len(tier))]
    if used_texts is not None:
        used_texts.add(picked["norm"])
    return picked["content"]
