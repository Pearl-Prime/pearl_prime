"""
Part 3.1 slot resolver: deterministic selection per slot, no reuse in-book.
Selector hash algorithm: SHA256(selector_key) -> first 16 bytes big-endian int -> modulo len(available).
Do not substitute Python's built-in hash() (salted per process, non-deterministic).
Teacher Mode: when teacher_mode=True and no candidates, raise TeacherCoverageError (do not return None).
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from phoenix_v4.planning.pool_index import AtomEntry, PoolIndex


@dataclass
class ResolverContext:
    persona_id: str
    topic_id: str
    slot_definitions: list[list[str]]
    used_atom_ids: set[str]
    pool_index: "PoolIndex"
    selector_key_prefix: str
    # Arc-First: required BAND per chapter for STORY slots (chapter_idx -> 1-5). None = no filter.
    required_band_by_chapter: Optional[dict[int, int]] = None
    # Repetition decay: semantic_family single-use per book (no two atoms from same family).
    used_semantic_families: Optional[set[str]] = None
    # Angle Integration (V4.7): chapter 1 framing bias. Optional dict with framing_mode, etc.
    angle_context: Optional[dict] = None
    # Intro/ending variation: final chapter INTEGRATION ranking by ending_style. Optional dict with final_chapter_index, integration_ending_style_id.
    ending_context: Optional[dict] = None
    # Teacher Mode: when True, raise on no candidates; return (atom_id, atom_source).
    teacher_mode: bool = False
    # Required slot counts (for EXERCISE fallback merge). teacher_exercise_fallback from config.
    required_slots_by_type: Optional[dict[str, int]] = None
    teacher_exercise_fallback: bool = False
    # Thesis-aware ranking (V4.8): per-chapter thesis text for biasing REFLECTION/STORY atom selection.
    # Keys are 1-based chapter numbers (same as arc chapter_thesis / CompiledBook.chapter_thesis).
    # Atoms with metadata keywords matching the thesis rank higher.
    chapter_thesis: Optional[dict[int, str]] = None


def _selector_index(selector_key: str, available_count: int) -> int:
    """
    Deterministic index into available list. Mandatory algorithm:
    - SHA256 over selector_key (UTF-8 bytes)
    - First 16 bytes of digest as big-endian int
    - modulo len(available)
    Do not use Python's built-in hash() (salted per run).
    """
    if available_count <= 0:
        return 0
    digest = hashlib.sha256(selector_key.encode("utf-8")).digest()
    # First 16 bytes (or full 32) as big-endian integer
    n = int.from_bytes(digest[:16], "big")
    return n % available_count


_THESIS_STOPWORDS = frozenset({
    "the", "is", "that", "this", "and", "but", "not", "you", "your", "are",
    "was", "were", "been", "being", "have", "has", "had", "does", "did",
    "will", "would", "could", "should", "can", "may", "might", "shall",
    "with", "for", "from", "into", "about", "than", "then", "when", "where",
    "what", "which", "who", "how", "its", "our", "their", "there", "here",
    "just", "also", "very", "more", "most", "some", "any", "all", "each",
    "every", "both", "few", "many", "much", "such", "own", "same", "other",
    "only", "over", "after", "before", "between", "because", "while",
    "point", "thing", "things", "like", "even",
})

_WORD_RE = re.compile(r"[a-z]{4,}")


def _thesis_keyword_overlap(thesis: str, metadata: dict) -> float:
    """Score 0.0-1.0: how well an atom's metadata aligns with the chapter thesis."""
    if not thesis:
        return 0.0
    thesis_words = set(_WORD_RE.findall(thesis.lower())) - _THESIS_STOPWORDS
    if not thesis_words:
        return 0.0
    # Gather searchable text from metadata
    meta_text_parts = []
    for key in ("description", "summary", "keywords", "semantic_family", "theme", "topic"):
        val = metadata.get(key)
        if isinstance(val, str):
            meta_text_parts.append(val.lower())
        elif isinstance(val, list):
            meta_text_parts.extend(str(v).lower() for v in val)
    meta_text = " ".join(meta_text_parts)
    meta_words = set(_WORD_RE.findall(meta_text)) - _THESIS_STOPWORDS
    if not meta_words:
        return 0.0
    overlap = thesis_words & meta_words
    return len(overlap) / len(thesis_words)


def resolve_slot(
    slot_type: str,
    chapter_idx: int,
    slot_idx: int,
    context: ResolverContext,
) -> Optional[Tuple[str, Optional[str]]]:
    """
    Return (atom_id, atom_source) for this slot from the pool, or None if pool empty or all used (and not teacher_mode).
    Teacher Mode: when teacher_mode and no candidates, raise TeacherCoverageError.
    No reuse: only atoms not in context.used_atom_ids are considered.
    Repetition decay: atoms with metadata.semantic_family already used are excluded.
    Determinism: selector_key = prefix + slot_type + ch:slot; SHA256 then modulo.
    """
    required_count = context.required_slots_by_type.get(slot_type) if context.required_slots_by_type else None
    teacher_exercise_fallback = context.teacher_exercise_fallback if slot_type == "EXERCISE" else False
    pool = context.pool_index.get_pool(
        slot_type,
        context.persona_id,
        context.topic_id,
        None,
        required_count=required_count,
        teacher_exercise_fallback=teacher_exercise_fallback,
    )
    available = [e for e in pool if e.atom_id not in context.used_atom_ids]
    # Repetition decay: exclude atoms whose semantic_family was already used this book
    if context.used_semantic_families is not None:
        available = [
            e for e in available
            if (e.metadata or {}).get("semantic_family") not in context.used_semantic_families
        ]
    # Arc-First: filter STORY by required BAND for this chapter when arc is set
    if slot_type == "STORY" and context.required_band_by_chapter is not None:
        ch_band = context.required_band_by_chapter.get(chapter_idx)
        if ch_band is not None:
            available = [
                e for e in available
                if (e.metadata or {}).get("band") == ch_band
                or bool((e.metadata or {}).get("band_universal"))
            ]
    if not available:
        if context.teacher_mode:
            from phoenix_v4.teacher.coverage_gate import TeacherCoverageError
            raise TeacherCoverageError(
                f"No teacher atoms for slot {slot_type} at chapter {chapter_idx} slot {slot_idx}. "
                "Coverage gate should have caught this; resolver must not return None in teacher mode."
            )
        return None
    # Angle Integration (V4.7): chapter 1 framing bias — rank by angle_bias.score_atom then atom_id; deterministic pick
    if chapter_idx == 0 and context.angle_context:
        from phoenix_v4.planning.angle_bias import score_atom
        def _key(e: "AtomEntry") -> tuple:
            return (-score_atom(e.metadata, slot_type, context.angle_context), e.atom_id)
        available.sort(key=_key)
    # Intro/ending variation: final chapter INTEGRATION — soft bias by ending_style
    elif (
        slot_type == "INTEGRATION"
        and context.ending_context
        and chapter_idx == context.ending_context.get("final_chapter_index")
    ):
        ending_style_id = (context.ending_context.get("integration_ending_style_id") or "").strip()
        if ending_style_id:
            from phoenix_v4.planning.angle_bias import score_ending_atom
            def _key_end(e: "AtomEntry") -> tuple:
                return (-score_ending_atom(e.metadata, ending_style_id), e.atom_id)
            available.sort(key=_key_end)
        else:
            available.sort(key=lambda e: e.atom_id)
    # Thesis-aware ranking (V4.8): bias REFLECTION and STORY atoms toward chapter thesis.
    # Keys follow arc/plan convention: 1-based chapter index (same as CompiledBook.chapter_thesis).
    elif (
        slot_type in ("REFLECTION", "STORY", "HOOK", "SCENE")
        and context.chapter_thesis
    ):
        th_map = context.chapter_thesis
        thesis_key = chapter_idx + 1
        ch_thesis = th_map.get(thesis_key)
        if ch_thesis is None:
            ch_thesis = th_map.get(str(thesis_key))
        if ch_thesis and str(ch_thesis).strip():
            thesis_text = str(ch_thesis).strip()

            def _key_thesis(e: "AtomEntry") -> tuple:
                score = _thesis_keyword_overlap(thesis_text, e.metadata or {})
                return (-score, e.atom_id)  # Higher overlap first, then deterministic tiebreak

            available.sort(key=_key_thesis)
        else:
            available.sort(key=lambda e: e.atom_id)
    else:
        # Lexicographic sort by atom_id (raw UTF-8; no Unicode normalization)
        available.sort(key=lambda e: e.atom_id)
    selector_key = f"{context.selector_key_prefix}:{slot_type}:ch{chapter_idx:02d}:s{slot_idx:02d}"
    idx = _selector_index(selector_key, len(available))
    chosen = available[idx]
    # Track semantic_family for repetition decay (single-use per book)
    fam = (chosen.metadata or {}).get("semantic_family")
    if fam is not None and context.used_semantic_families is not None:
        context.used_semantic_families.add(str(fam))
    atom_source = getattr(chosen, "atom_source", None)
    return (chosen.atom_id, atom_source)
