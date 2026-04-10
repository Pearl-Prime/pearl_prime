"""
EnrichmentSelect — fills Beatmap slots with prose using the registry_resolver waterfall.

Priority (aligned with phoenix_v4.planning.registry_resolver.resolve_book):
  1. Teacher atoms (approved_atoms/{SLOT_TYPE}/) when teacher_id is set and
     slot type is in the teacher-overlay set (see registry_resolver).
  2. Persona atoms (HOOK, SCENE, STORY) from atoms/{persona}/{topic}/.
  3. For EXERCISE only: practice library before registry variant.
  4. Registry variant from registry/{topic}.yaml (nth section of that type per chapter).
  5. Empty: visible CONTENT GAP marker + ERROR log.

Practice library: logs WARNING via get_exercise_for_chapter when used.
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from phoenix_v4.planning.beatmap_compile import Beatmap, BeatmapChapter, BeatmapSlot
from phoenix_v4.planning.registry_resolver import (
    _TEACHER_TYPE_MAP,
    _TEACHER_OVERLAY_TYPES,
    _PERSONA_OVERLAY_TYPES,
    _deterministic_index,
    _load_persona_atoms,
    _load_teacher_atoms,
    load_registry,
)

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class EnrichmentRequest:
    beatmap: Beatmap
    teacher_id: Optional[str]
    persona_id: str
    topic_id: str
    seed: str


@dataclass
class EnrichedSlot:
    slot_type: str
    content: str
    source: str
    source_id: str
    target_words: int
    actual_words: int
    enrichment_applied: List[str]


@dataclass
class EnrichedChapter:
    number: int
    role: str
    working_title: str
    thesis: str
    slots: List[EnrichedSlot]
    total_words: int
    source_breakdown: Dict[str, int]


@dataclass
class EnrichedBook:
    schema_version: int
    stage: str
    topic: str
    teacher_id: Optional[str]
    persona_id: str
    runtime_format: str
    chapters: List[EnrichedChapter]
    total_words: int
    enrichment_audit: Dict[str, Any]


def _norm_teacher_id(teacher_id: Optional[str]) -> Optional[str]:
    if not teacher_id:
        return None
    t = teacher_id.strip()
    return t.lower() if t else None


def _chapter_key(chapter_num: int) -> str:
    return f"chapter_{chapter_num:02d}"


def _registry_type_lists(ch_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    sections = ch_data.get("sections") or {}
    by_type: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    if not isinstance(sections, dict):
        return by_type
    for sec_key in sorted(sections.keys()):
        sec_data = sections[sec_key]
        if not isinstance(sec_data, dict):
            continue
        st = str(sec_data.get("type") or "REFLECTION").strip().upper()
        by_type[st].append(sec_data)
    return by_type


def _pick_teacher_pool(teacher_atoms: Dict[str, List[dict]], slot_type: str) -> List[dict]:
    st = slot_type.strip().upper()
    if st not in _TEACHER_OVERLAY_TYPES:
        return []
    for dir_name in _TEACHER_TYPE_MAP.get(st, [st]):
        pool = teacher_atoms.get(dir_name, [])
        if pool:
            return pool
    return []


def _try_teacher_content(
    teacher_atoms: Dict[str, List[dict]],
    slot_type: str,
    seed_key: str,
) -> Optional[Tuple[str, str]]:
    pool = _pick_teacher_pool(teacher_atoms, slot_type)
    if not pool:
        return None
    idx = _deterministic_index(f"{seed_key}:teacher", len(pool))
    atom = pool[idx]
    content = str(atom.get("content") or "").strip()
    if not content:
        return None
    aid = str(atom.get("atom_id") or f"auto_{idx}")
    return content, aid


def _try_persona_content(
    persona_atoms: Dict[str, List[dict]],
    slot_type: str,
    seed_key: str,
) -> Optional[Tuple[str, str]]:
    st = slot_type.strip().upper()
    if st not in _PERSONA_OVERLAY_TYPES:
        return None
    pool = persona_atoms.get(st, [])
    if not pool:
        return None
    idx = _deterministic_index(f"{seed_key}:persona", len(pool))
    atom = pool[idx]
    content = str(atom.get("content") or "").strip()
    if not content:
        return None
    return content, str(atom.get("atom_id") or f"persona_{idx}")


def _try_practice_library(
    chapter_index: int,
    topic_id: str,
    persona_id: str,
    seed: str,
) -> Optional[Tuple[str, str]]:
    try:
        from phoenix_v4.exercises.practice_library_loader import get_exercise_for_chapter

        composed = get_exercise_for_chapter(
            chapter_index=chapter_index,
            topic_id=topic_id,
            persona_id=persona_id or "",
            seed=seed,
        )
        if composed and composed.strip():
            return composed.strip(), "practice_library"
    except Exception as e:
        logger.warning("Practice library failed: %s", e)
    return None


def _try_registry_variant(
    reg_lists: Dict[str, List[Dict[str, Any]]],
    slot_type: str,
    reg_counters: Dict[str, int],
    seed_key: str,
) -> Optional[Tuple[str, str]]:
    st = slot_type.strip().upper()
    lst = reg_lists.get(st, [])
    idx = reg_counters[st]
    reg_counters[st] += 1
    if idx >= len(lst):
        return None
    sec_data = lst[idx]
    variants = sec_data.get("variants") or []
    if not variants:
        return None
    v_idx = _deterministic_index(f"{seed_key}:registry", len(variants))
    var = variants[v_idx]
    content = str(var.get("content") or "").strip()
    vid = str(var.get("variant_id") or f"v{v_idx}")
    if not content:
        return None
    return content, vid


def select_enrichment(
    request: EnrichmentRequest,
    repo_root: Optional[Path] = None,
) -> EnrichedBook:
    root = repo_root or REPO_ROOT
    topic = request.topic_id
    bm = request.beatmap
    seed = request.seed
    persona_id = request.persona_id
    tid = _norm_teacher_id(request.teacher_id)

    reg = load_registry(topic)
    sections_root = reg.get("sections") or {}
    teacher_atoms: Dict[str, List[dict]] = _load_teacher_atoms(tid) if tid else {}
    persona_atoms: Dict[str, List[dict]] = (
        _load_persona_atoms(persona_id, topic) if persona_id else {}
    )

    audit_counts = {
        "total_slots": 0,
        "slots_from_teacher": 0,
        "slots_from_persona": 0,
        "slots_from_registry": 0,
        "slots_from_practice_library": 0,
        "practice_library_warnings": 0,
        "slots_empty": 0,
    }
    total_target_words = 0
    gap_details: List[Dict[str, Any]] = []

    enriched_chapters: List[EnrichedChapter] = []

    for bm_ch in bm.chapters:
        ch_key = _chapter_key(bm_ch.number)
        ch_data = sections_root.get(ch_key)
        if not isinstance(ch_data, dict):
            ch_data = {}
        reg_lists = _registry_type_lists(ch_data)
        reg_counters: Dict[str, int] = defaultdict(int)

        chapter_index0 = bm_ch.number - 1
        slots_out: List[EnrichedSlot] = []
        ch_breakdown: Dict[str, int] = defaultdict(int)
        ch_words = 0

        for slot_i, slot in enumerate(bm_ch.slots):
            audit_counts["total_slots"] += 1
            total_target_words += slot.target_words
            stype = slot.slot_type.strip().upper()
            seed_key = f"{seed}:topic:{topic}:ch{bm_ch.number}:slot:{slot_i}:{stype}"

            content: str = ""
            source: str = ""
            source_id: str = ""
            hooks_fired: List[str] = []

            # 1) Teacher
            if tid and teacher_atoms:
                t_hit = _try_teacher_content(teacher_atoms, stype, seed_key)
                if t_hit:
                    content, source_id = t_hit
                    source = "teacher_atom"
                    audit_counts["slots_from_teacher"] += 1

            # 2) Persona
            if not content and persona_atoms:
                p_hit = _try_persona_content(persona_atoms, stype, seed_key)
                if p_hit:
                    content, source_id = p_hit
                    source = "persona_atom"
                    audit_counts["slots_from_persona"] += 1

            # 3) EXERCISE — practice library before registry (matches registry_resolver)
            if not content and stype == "EXERCISE":
                pl = _try_practice_library(chapter_index0, topic, persona_id, seed)
                if pl:
                    content, source_id = pl
                    source = "practice_library"
                    audit_counts["slots_from_practice_library"] += 1
                    audit_counts["practice_library_warnings"] += 1

            # 4) Registry
            if not content:
                r_hit = _try_registry_variant(reg_lists, stype, reg_counters, seed_key)
                if r_hit:
                    content, source_id = r_hit
                    source = "registry"
                    audit_counts["slots_from_registry"] += 1

            # 5) Gap
            if not content:
                audit_counts["slots_empty"] += 1
                gap_msg = f"[CONTENT GAP: {stype} for {topic} ch{bm_ch.number}]"
                logger.error("Enrichment gap: %s (slot %d)", gap_msg, slot_i)
                gap_details.append(
                    {"chapter": bm_ch.number, "slot_index": slot_i, "slot_type": stype}
                )
                content = gap_msg
                source = "gap"
                source_id = "gap"

            actual_w = len(content.split())
            ch_words += actual_w
            ch_breakdown[source] += 1

            if content and not content.startswith("[CONTENT GAP:") and slot.enrichment_hooks:
                hooks_fired = list(slot.enrichment_hooks)

            slots_out.append(
                EnrichedSlot(
                    slot_type=stype,
                    content=content,
                    source=source,
                    source_id=source_id,
                    target_words=slot.target_words,
                    actual_words=actual_w,
                    enrichment_applied=hooks_fired,
                )
            )

        enriched_chapters.append(
            EnrichedChapter(
                number=bm_ch.number,
                role=bm_ch.role,
                working_title=bm_ch.working_title,
                thesis=bm_ch.thesis,
                slots=slots_out,
                total_words=ch_words,
                source_breakdown=dict(ch_breakdown),
            )
        )

    total_words = sum(ch.total_words for ch in enriched_chapters)
    enrichment_audit: Dict[str, Any] = {
        **audit_counts,
        "total_words": total_words,
        "total_target_words": total_target_words,
        "gap_details": gap_details,
        "persona_id": persona_id,
        "teacher_id": tid or "",
    }

    return EnrichedBook(
        schema_version=1,
        stage="enrichment_select",
        topic=topic,
        teacher_id=tid,
        persona_id=persona_id,
        runtime_format=bm.runtime_format,
        chapters=enriched_chapters,
        total_words=total_words,
        enrichment_audit=enrichment_audit,
    )


def enriched_book_to_jsonable(book: EnrichedBook) -> Dict[str, Any]:
    return {
        "schema_version": book.schema_version,
        "stage": book.stage,
        "topic": book.topic,
        "teacher_id": book.teacher_id,
        "persona_id": book.persona_id,
        "runtime_format": book.runtime_format,
        "total_words": book.total_words,
        "enrichment_audit": book.enrichment_audit,
        "chapters": [
            {
                "number": ch.number,
                "role": ch.role,
                "working_title": ch.working_title,
                "thesis": ch.thesis,
                "total_words": ch.total_words,
                "source_breakdown": ch.source_breakdown,
                "slots": [asdict(s) for s in ch.slots],
            }
            for ch in book.chapters
        ],
    }


def dump_enriched_book_json(book: EnrichedBook, indent: int = 2) -> str:
    return json.dumps(enriched_book_to_jsonable(book), indent=indent, ensure_ascii=False)


def budget_from_enriched(book: EnrichedBook) -> Dict[str, Any]:
    return {
        "total_words": book.total_words,
        "chapter_count": len(book.chapters),
        "chapters": [
            {
                "chapter": ch.number,
                "working_title": ch.working_title,
                "words": ch.total_words,
                "slots": [
                    {
                        "type": s.slot_type,
                        "target_words": s.target_words,
                        "actual_words": s.actual_words,
                        "source": s.source,
                    }
                    for s in ch.slots
                ],
            }
            for ch in book.chapters
        ],
    }
