"""
EnrichmentSelect — fills Beatmap slots with prose using the registry_resolver waterfall.

Priority (aligned with phoenix_v4.planning.registry_resolver.resolve_book):
  1. Teacher atoms (approved_atoms/{SLOT_TYPE}/) when teacher_id is set and
     slot type is in the teacher-overlay set (see registry_resolver).
  2. Persona atoms (HOOK, SCENE, STORY) from atoms/{persona}/{topic}/.
  3. For EXERCISE only: practice library before registry variant.
  4. Registry variant from registry/{topic}.yaml (nth section of that type per chapter).
  5. Content bank fallbacks from config/content_banks/*.yaml (slot-type mapped bridges).
  6. Empty: visible CONTENT GAP marker + ERROR log (or EnrichmentGapError when publishable_book).

Practice library: logs WARNING via get_exercise_for_chapter when used.

Depth pass (apply_depth_pass): after select_enrichment, fills thin chapters using
config/depth/depth_module_map.yaml — existing content only, no LLM generation.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from phoenix_v4.planning.beatmap_compile import Beatmap, BeatmapChapter, BeatmapSlot
from phoenix_v4.planning.selection_allowlist import atom_passes_book_governance
from phoenix_v4.planning.slot_resolver import _bestseller_metadata_score
from phoenix_v4.planning.registry_resolver import (
    _TEACHER_TYPE_MAP,
    _TEACHER_OVERLAY_TYPES,
    _PERSONA_OVERLAY_TYPES,
    _deterministic_index,
    _load_persona_atoms,
    _load_teacher_atoms,
    _load_yaml,
    load_registry,
)

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Registry beatmap slot type → content-bank slot_type values (enrichment_slot_fallback_bank.yaml).
_ENRICH_BANK_SLOT_TYPES: Dict[str, Tuple[str, ...]] = {
    "HOOK": ("FALLBACK_PROSE",),
    "SCENE": ("FALLBACK_PROSE",),
    "REFLECTION": ("MECHANISM_BRIDGE",),
    "PIVOT": ("FLOW_GLUE",),
    "INTEGRATION": ("INTEGRATION_LAND", "FLOW_GLUE"),
    "THREAD": ("CHAPTER_PROPULSION",),
    "TAKEAWAY": ("TAKEAWAY_PULL",),
    "COMPRESSION": ("DOCTRINE_SECULAR_BRIDGE", "MECHANISM_BRIDGE"),
    "TEACHER_DOCTRINE": ("DOCTRINE_SECULAR_BRIDGE", "MECHANISM_BRIDGE"),
}


class EnrichmentGapError(RuntimeError):
    """Publishable-book runs must not ship visible [CONTENT GAP: ...] markers."""


def _try_content_bank_fallback(
    *,
    reg: Any,
    slot_type: str,
    seed_key: str,
    topic: str,
    persona_id: str,
    frame: str,
    runtime_format: str,
    chapter_index0: int,
    seed: str,
    chapter_targets: Dict[str, Any],
) -> Optional[Tuple[str, str, str, Dict[str, Any]]]:
    """Return (content, source, source_id, score_meta) or None."""
    from phoenix_v4.content_banks.selector import FragmentContext, _collect_candidates

    st = slot_type.strip().upper()
    aliases = _ENRICH_BANK_SLOT_TYPES.get(st, ())
    if not aliases:
        return None
    stems = list(reg.banks.keys())
    if not stems:
        return None
    ctx = FragmentContext(
        topic_id=topic,
        persona_id=persona_id,
        frame=frame,
        runtime_format_id=runtime_format,
        chapter_index=chapter_index0,
        book_seed=seed,
        slot_key=seed_key,
    )
    pool: List[dict[str, Any]] = []
    for alias in aliases:
        pool.extend(_collect_candidates(reg, stems, alias, ctx))
    if not pool:
        return None
    pool.sort(key=lambda r: str(r.get("variant_id") or ""))
    scored = sorted(
        pool,
        key=lambda r: (
            -_bestseller_metadata_score(r, chapter_targets),
            str(r.get("variant_id") or ""),
        ),
    )
    digest = hashlib.sha256(seed_key.encode("utf-8")).digest()
    idx = int.from_bytes(digest[:8], "big") % len(scored)
    picked = scored[idx]
    body = str(picked.get("body") or "").strip()
    if len(body.split()) < 11:
        return None
    vid = str(picked.get("variant_id") or "")
    bscore = _bestseller_metadata_score(picked, chapter_targets)
    return (
        body,
        "content_bank",
        vid,
        {"bestseller_target_score": bscore, "content_bank_variant_id": vid},
    )

def _load_runtime_word_bounds(
    runtime_format: str,
    repo_root: Path,
) -> Optional[Tuple[int, int]]:
    """Return (min_words, max_words) from config/format_selection/format_registry.yaml."""
    rf = (runtime_format or "").strip()
    if not rf:
        return None
    path = repo_root / "config" / "format_selection" / "format_registry.yaml"
    if not path.exists():
        return None
    data = _load_yaml(path)
    block = (data.get("runtime_formats") or {}).get(rf)
    if not isinstance(block, dict):
        return None
    wr = block.get("word_range")
    if not isinstance(wr, (list, tuple)) or len(wr) < 2:
        return None
    try:
        lo = int(wr[0])
        hi = int(wr[1])
    except (TypeError, ValueError):
        return None
    if hi <= 0:
        return None
    return lo, hi


@dataclass
class EnrichmentRequest:
    beatmap: Beatmap
    teacher_id: Optional[str]
    persona_id: str
    topic_id: str
    seed: str
    spine_context: Optional[Dict[str, Any]] = None
    publishable_book: bool = False
    content_banks_dir: Optional[Path] = None


@dataclass
class EnrichedSlot:
    slot_type: str
    content: str
    source: str
    source_id: str
    target_words: int
    actual_words: int
    enrichment_applied: List[str]
    exercise_phase: Optional[str] = None
    journey_exercise_id: Optional[str] = None
    variant_id: str = ""
    atom_id: str = ""
    match_scores: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnrichedChapter:
    number: int
    role: str
    working_title: str
    thesis: str
    slots: List[EnrichedSlot]
    total_words: int
    source_breakdown: Dict[str, int]
    exercise_journey: Optional[Dict[str, Any]] = None


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
    spine_context: Dict[str, Any] = field(default_factory=dict)


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
    *,
    topic_id: str = "",
    persona_id: str = "",
    book_frame: str = "somatic_first",
) -> Optional[Tuple[str, str, int, Dict[str, Any]]]:
    pool = _pick_teacher_pool(teacher_atoms, slot_type)
    pool = [
        a
        for a in pool
        if atom_passes_book_governance(
            a.get("metadata"),
            topic_id=topic_id,
            persona_id=persona_id,
            book_frame=book_frame,
        )
    ]
    if not pool:
        return None
    idx = _deterministic_index(f"{seed_key}:teacher", len(pool))
    atom = pool[idx]
    content = str(atom.get("content") or "").strip()
    if not content:
        return None
    aid = str(atom.get("atom_id") or f"auto_{idx}")
    meta = dict(atom.get("metadata") or {})
    return content, aid, idx, meta


def _try_persona_content(
    persona_atoms: Dict[str, List[dict]],
    slot_type: str,
    seed_key: str,
    *,
    topic_id: str = "",
    persona_id: str = "",
    book_frame: str = "somatic_first",
) -> Optional[Tuple[str, str, int, Dict[str, Any]]]:
    st = slot_type.strip().upper()
    if st not in _PERSONA_OVERLAY_TYPES:
        return None
    pool = [
        a
        for a in (persona_atoms.get(st, []))
        if atom_passes_book_governance(
            a.get("metadata"),
            topic_id=topic_id,
            persona_id=persona_id,
            book_frame=book_frame,
        )
    ]
    if not pool:
        return None
    idx = _deterministic_index(f"{seed_key}:persona", len(pool))
    atom = pool[idx]
    content = str(atom.get("content") or "").strip()
    if not content:
        return None
    meta = dict(atom.get("metadata") or {})
    return content, str(atom.get("atom_id") or f"persona_{idx}"), idx, meta


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


def _norm_ws(text: str) -> str:
    return " ".join((text or "").split())


def _wc(text: str) -> int:
    return len((text or "").split())


def _personas_with_topic(topic: str, repo_root: Path) -> List[str]:
    atoms_root = repo_root / "atoms"
    if not atoms_root.is_dir():
        return []
    out: List[str] = []
    for p in sorted(atoms_root.iterdir()):
        if p.is_dir() and (p / topic).is_dir():
            out.append(p.name)
    return out


def _merged_persona_atoms_deep_6h(
    primary_persona: str,
    topic: str,
    repo_root: Path,
) -> Dict[str, List[dict]]:
    """
    HOOK / SCENE / STORY pools for deep_book_6h: primary persona first, then other personas
    for the same topic (deduped by normalized body).
    """
    ids = _personas_with_topic(topic, repo_root)
    if primary_persona in ids:
        ordered = [primary_persona] + [x for x in ids if x != primary_persona]
    else:
        ordered = [primary_persona] + ids

    merged: Dict[str, List[dict]] = {}
    for st in _PERSONA_OVERLAY_TYPES:
        seen: set[str] = set()
        acc: List[dict] = []
        for pid in ordered:
            for atom in _load_persona_atoms(pid, topic).get(st, []):
                txt = str(atom.get("content") or "").strip()
                n = _norm_ws(txt)
                if not n or n in seen:
                    continue
                seen.add(n)
                aid = str(atom.get("atom_id") or f"{pid}_{len(acc)}")
                acc.append({"atom_id": aid, "content": txt})
        if acc:
            merged[st] = acc
    return merged


def _max_extra_chunks_for_format(runtime_format: str, slot_target_words: int) -> int:
    """Cap additional registry/persona/teacher variants per slot (format + beatmap slot target)."""
    rf = (runtime_format or "").strip()
    tw = max(0, int(slot_target_words or 0))
    if rf in ("micro_book_15", "micro_book_20"):
        base = 0
    elif rf == "short_book_30":
        base = 1
    elif rf == "standard_book":
        base = 3
    elif rf == "extended_book_2h":
        base = 5
    elif rf == "deep_book_4h":
        base = 7
    elif rf == "deep_book_6h":
        base = 18
    else:
        base = 3
    extra = max(0, tw - 320) // 160
    return min(24, base + extra)


def _extra_registry_variant_bodies(
    sec_data: Dict[str, Any],
    primary_v_idx: int,
    seed_key: str,
    goal_extra_words: int,
    max_chunks: int,
) -> List[str]:
    variants = sec_data.get("variants") or []
    if not variants or goal_extra_words <= 0 or max_chunks <= 0:
        return []
    indices = [i for i in range(len(variants)) if i != primary_v_idx]
    if not indices:
        return []
    indices.sort(
        key=lambda i: hashlib.sha256(f"{seed_key}:rv:{i}".encode("utf-8")).hexdigest()
    )
    primary_norm = ""
    if 0 <= primary_v_idx < len(variants):
        pv = variants[primary_v_idx]
        if isinstance(pv, dict):
            primary_norm = _norm_ws(str(pv.get("content") or ""))
    out: List[str] = []
    seen: set[str] = set()
    running = 0
    for i in indices:
        if running >= goal_extra_words or len(out) >= max_chunks:
            break
        v = variants[i]
        if not isinstance(v, dict):
            continue
        txt = str(v.get("content") or "").strip()
        if _wc(txt) < 11:
            continue
        norm = _norm_ws(txt)
        if not norm or norm == primary_norm or norm in seen:
            continue
        seen.add(norm)
        out.append(txt)
        running += _wc(txt)
    return out


def _expand_atom_pool_blocks(
    pool: List[dict],
    primary_idx: int,
    seed_key: str,
    label: str,
    goal_extra_words: int,
    max_chunks: int,
) -> List[str]:
    if len(pool) <= 1 or goal_extra_words <= 0 or max_chunks <= 0:
        return []
    order = [i for i in range(len(pool)) if i != primary_idx]
    order.sort(
        key=lambda i: hashlib.sha256(f"{seed_key}:{label}:{i}".encode("utf-8")).hexdigest()
    )
    primary = pool[primary_idx]
    primary_norm = _norm_ws(str(primary.get("content") or ""))
    out: List[str] = []
    seen: set[str] = {primary_norm} if primary_norm else set()
    running = 0
    for i in order:
        if running >= goal_extra_words or len(out) >= max_chunks:
            break
        atom = pool[i]
        txt = str(atom.get("content") or "").strip()
        if _wc(txt) < 11:
            continue
        norm = _norm_ws(txt)
        if not norm or norm in seen:
            continue
        seen.add(norm)
        out.append(txt)
        running += _wc(txt)
    return out


def _slot_spec_for(
    context: Dict[str, Any],
    chapter_number: int,
    slot_index: int,
) -> Dict[str, Any]:
    specs = (context or {}).get("atom_slot_specs") or {}
    chapter_specs = specs.get(str(chapter_number)) or specs.get(chapter_number) or []
    if isinstance(chapter_specs, list) and 0 <= slot_index < len(chapter_specs):
        item = chapter_specs[slot_index]
        return item if isinstance(item, dict) else {}
    return {}


def _atom_allowed_by_slot_spec(atom: dict, slot_spec: Dict[str, Any]) -> bool:
    """Apply deterministic persona/topic/forbidden tag filters when metadata exists."""
    if not slot_spec:
        return True
    metadata = atom.get("metadata") if isinstance(atom.get("metadata"), dict) else {}
    tags = {
        str(t).strip().lower()
        for t in (
            atom.get("tags")
            or metadata.get("tags")
            or metadata.get("topic_tags")
            or []
        )
    }
    forbidden = {str(t).strip().lower() for t in slot_spec.get("forbidden_tags") or []}
    if tags and forbidden and tags & forbidden:
        return False
    text = str(atom.get("content") or "").lower()
    for bad in forbidden:
        if bad and bad not in {"clinical_dsm"} and bad.replace("_", " ") in text:
            return False
    personas = {str(p).strip() for p in slot_spec.get("persona_filter") or []}
    atom_persona = str(atom.get("persona_id") or metadata.get("persona_id") or "").strip()
    if atom_persona and personas and atom_persona not in personas:
        return False
    topics = {str(t).strip() for t in slot_spec.get("topic_filter") or []}
    atom_topic = str(atom.get("topic_id") or metadata.get("topic_id") or "").strip()
    if atom_topic and topics and atom_topic not in topics:
        return False
    return True


def _filtered_pool(pool: List[dict], slot_spec: Dict[str, Any]) -> List[dict]:
    if not slot_spec:
        return pool
    return [atom for atom in pool if _atom_allowed_by_slot_spec(atom, slot_spec)]


def _try_registry_variant(
    reg_lists: Dict[str, List[Dict[str, Any]]],
    slot_type: str,
    reg_counters: Dict[str, int],
    seed_key: str,
) -> Optional[Tuple[str, str, Dict[str, Any], int]]:
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
    return content, vid, sec_data, v_idx


def _peek_registry_variant(
    reg_lists: Dict[str, List[Dict[str, Any]]],
    slot_type: str,
    reg_counters: Dict[str, int],
    seed_key: str,
) -> Optional[Tuple[str, str]]:
    """Same as _try_registry_variant but does not advance reg_counters."""
    st = slot_type.strip().upper()
    lst = reg_lists.get(st, [])
    idx = reg_counters[st]
    if idx >= len(lst):
        return None
    sec_data = lst[idx]
    variants = sec_data.get("variants") or []
    if not variants:
        return None
    v_idx = _deterministic_index(f"{seed_key}:registry", len(variants))
    var = variants[v_idx]
    content = str(var.get("content") or "").strip()
    if not content:
        return None
    vid = str(var.get("variant_id") or f"v{v_idx}")
    return content, vid


def peek_registry_content_for_beatmap_slot(
    *,
    beatmap: Beatmap,
    chapter_number: int,
    slot_index: int,
    topic_id: str,
    teacher_id: Optional[str],
    persona_id: str,
    seed: str,
    repo_root: Optional[Path] = None,
) -> str:
    """
    Registry variant text that would apply at this beatmap slot if teacher/persona/practice
    did not consume the slot — counters match select_enrichment() for prior slots.
    Used to stack teacher (or persona) overlay with registry baseline without double-consuming.
    """
    topic = topic_id
    tid = _norm_teacher_id(teacher_id)
    bm_ch = next((c for c in beatmap.chapters if c.number == chapter_number), None)
    if bm_ch is None or slot_index < 0 or slot_index >= len(bm_ch.slots):
        return ""

    reg = load_registry(topic)
    sections_root = reg.get("sections") or {}
    ch_key = _chapter_key(chapter_number)
    ch_data = sections_root.get(ch_key)
    if not isinstance(ch_data, dict):
        ch_data = {}
    reg_lists = _registry_type_lists(ch_data)
    reg_counters: Dict[str, int] = defaultdict(int)

    root = repo_root or REPO_ROOT
    teacher_atoms: Dict[str, List[dict]] = _load_teacher_atoms(tid) if tid else {}
    pid = (persona_id or "").strip()
    rf = (beatmap.runtime_format or "").strip()
    if rf == "deep_book_6h" and pid:
        persona_atoms = _merged_persona_atoms_deep_6h(pid, topic, root)
    elif pid:
        persona_atoms = _load_persona_atoms(pid, topic)
    else:
        persona_atoms = {}
    chapter_index0 = chapter_number - 1

    for slot_i in range(slot_index):
        slot = bm_ch.slots[slot_i]
        stype = slot.slot_type.strip().upper()
        seed_key = f"{seed}:topic:{topic}:ch{bm_ch.number}:slot:{slot_i}:{stype}"
        content: Optional[str] = None

        if tid and teacher_atoms:
            t_hit = _try_teacher_content(
                teacher_atoms,
                stype,
                seed_key,
                topic_id=topic,
                persona_id=persona_id,
                book_frame="somatic_first",
            )
            if t_hit:
                content = t_hit[0]

        if not content and persona_atoms:
            p_hit = _try_persona_content(
                persona_atoms,
                stype,
                seed_key,
                topic_id=topic,
                persona_id=persona_id,
                book_frame="somatic_first",
            )
            if p_hit:
                content = p_hit[0]

        if not content and stype == "EXERCISE":
            pl = _try_practice_library(chapter_index0, topic, persona_id, seed)
            if pl:
                content = pl[0]

        if not content:
            r_hit = _try_registry_variant(reg_lists, stype, reg_counters, seed_key)
            if r_hit:
                content = r_hit[0]

    stype = bm_ch.slots[slot_index].slot_type.strip().upper()
    seed_key = f"{seed}:topic:{topic}:ch{bm_ch.number}:slot:{slot_index}:{stype}"
    peek = _peek_registry_variant(reg_lists, stype, reg_counters, seed_key)
    return peek[0] if peek else ""


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
    pid = (persona_id or "").strip()
    rf_bm = (bm.runtime_format or "").strip()
    if rf_bm == "deep_book_6h" and pid:
        persona_atoms = _merged_persona_atoms_deep_6h(pid, topic, root)
    elif pid:
        persona_atoms = _load_persona_atoms(pid, topic)
    else:
        persona_atoms = {}

    from phoenix_v4.content_banks.loader import load_content_bank_registry

    try:
        cb_reg = load_content_bank_registry(banks_dir=request.content_banks_dir)
    except Exception as e:
        logger.warning("Content bank registry unavailable: %s", e)
        cb_reg = None

    _spine = request.spine_context or {}
    _frame = str(_spine.get("book_frame") or _spine.get("frame") or "somatic_first").strip()
    _sel_targets = list(_spine.get("chapter_selector_targets") or [])

    format_bounds = _load_runtime_word_bounds(bm.runtime_format, root)
    format_wmax: Optional[int] = format_bounds[1] if format_bounds else None

    audit_counts = {
        "total_slots": 0,
        "slots_from_teacher": 0,
        "slots_from_persona": 0,
        "slots_from_registry": 0,
        "slots_from_practice_library": 0,
        "practice_library_warnings": 0,
        "slots_empty": 0,
        "slots_format_scaled": 0,
        "format_word_cap_max": format_wmax,
        "slots_from_content_bank": 0,
    }
    total_target_words = 0
    gap_details: List[Dict[str, Any]] = []

    enriched_chapters: List[EnrichedChapter] = []
    plan_context = dict(request.spine_context or {})

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
            slot_spec = _slot_spec_for(plan_context, bm_ch.number, slot_i)
            ch_tgt = (
                _sel_targets[chapter_index0] if chapter_index0 < len(_sel_targets) else {}
            )

            content: str = ""
            source: str = ""
            source_id: str = ""
            variant_id = ""
            atom_id = ""
            match_scores: Dict[str, Any] = {}
            hooks_fired: List[str] = []
            reg_sec_meta: Optional[Tuple[Dict[str, Any], int]] = None
            persona_expand_pool: Optional[List[dict]] = None
            persona_primary_idx: Optional[int] = None
            teacher_expand_pool: Optional[List[dict]] = None
            teacher_primary_idx: Optional[int] = None

            # 1) Teacher
            if tid and teacher_atoms:
                teacher_atoms_for_slot = dict(teacher_atoms)
                for _k, _pool in list(teacher_atoms_for_slot.items()):
                    teacher_atoms_for_slot[_k] = _filtered_pool(_pool, slot_spec)
                t_hit = _try_teacher_content(
                    teacher_atoms_for_slot,
                    stype,
                    seed_key,
                    topic_id=topic,
                    persona_id=persona_id,
                    book_frame=_frame,
                )
                if t_hit:
                    content, source_id, teacher_primary_idx, t_meta = t_hit
                    source = "teacher_atom"
                    _raw_tp = _pick_teacher_pool(teacher_atoms_for_slot, stype)
                    teacher_expand_pool = [
                        a
                        for a in _raw_tp
                        if atom_passes_book_governance(
                            a.get("metadata"),
                            topic_id=topic,
                            persona_id=persona_id,
                            book_frame=_frame,
                        )
                    ]
                    audit_counts["slots_from_teacher"] += 1
                    atom_id = source_id
                    match_scores["bestseller_target_score"] = _bestseller_metadata_score(
                        t_meta, ch_tgt
                    )

            # 2) Persona
            if not content and persona_atoms:
                persona_pool = _filtered_pool(persona_atoms.get(stype, []), slot_spec)
                persona_atoms_for_slot = dict(persona_atoms)
                persona_atoms_for_slot[stype] = persona_pool
                p_hit = _try_persona_content(
                    persona_atoms_for_slot,
                    stype,
                    seed_key,
                    topic_id=topic,
                    persona_id=persona_id,
                    book_frame=_frame,
                )
                if p_hit:
                    content, source_id, persona_primary_idx, p_meta = p_hit
                    source = "persona_atom"
                    persona_expand_pool = [
                        a
                        for a in persona_pool
                        if atom_passes_book_governance(
                            a.get("metadata"),
                            topic_id=topic,
                            persona_id=persona_id,
                            book_frame=_frame,
                        )
                    ]
                    audit_counts["slots_from_persona"] += 1
                    atom_id = source_id
                    match_scores["bestseller_target_score"] = _bestseller_metadata_score(
                        p_meta, ch_tgt
                    )

            # 3) EXERCISE — practice library before registry (matches registry_resolver)
            if not content and stype == "EXERCISE":
                pl = _try_practice_library(chapter_index0, topic, persona_id, seed)
                if pl:
                    content, source_id = pl
                    source = "practice_library"
                    audit_counts["slots_from_practice_library"] += 1
                    audit_counts["practice_library_warnings"] += 1
                    match_scores["source"] = "practice_library"

            # 4) Registry
            if not content:
                r_hit = _try_registry_variant(reg_lists, stype, reg_counters, seed_key)
                if r_hit:
                    content, source_id, _sec_d, _v_i = r_hit
                    reg_sec_meta = (_sec_d, _v_i)
                    source = "registry"
                    audit_counts["slots_from_registry"] += 1
                    variant_id = source_id
                    vars_ = _sec_d.get("variants") or []
                    var_rec: Dict[str, Any] = {}
                    if 0 <= _v_i < len(vars_) and isinstance(vars_[_v_i], dict):
                        var_rec = vars_[_v_i]
                    match_scores["bestseller_target_score"] = _bestseller_metadata_score(
                        var_rec, ch_tgt
                    )

            # 5) Content bank (bridges / fallbacks)
            if not content and cb_reg is not None:
                b_hit = _try_content_bank_fallback(
                    reg=cb_reg,
                    slot_type=stype,
                    seed_key=seed_key,
                    topic=topic,
                    persona_id=persona_id,
                    frame=_frame,
                    runtime_format=rf_bm,
                    chapter_index0=chapter_index0,
                    seed=seed,
                    chapter_targets=ch_tgt,
                )
                if b_hit:
                    content, source, source_id, extra_scores = b_hit
                    variant_id = str(extra_scores.get("content_bank_variant_id") or source_id)
                    match_scores.update(extra_scores)
                    audit_counts["slots_from_content_bank"] += 1

            # 6) Gap
            if not content:
                if request.publishable_book:
                    raise EnrichmentGapError(
                        f"No enrichable content for slot {stype} "
                        f"(topic={topic} chapter={bm_ch.number} slot_index={slot_i})"
                    )
                audit_counts["slots_empty"] += 1
                gap_msg = f"[CONTENT GAP: {stype} for {topic} ch{bm_ch.number}]"
                logger.error(
                    "Enrichment gap: %s (slot %d) — PRODUCTION WILL FAIL. "
                    "Add atoms or content bank entries for topic=%s slot_type=%s.",
                    gap_msg, slot_i, topic, stype
                )
                gap_details.append(
                    {"chapter": bm_ch.number, "slot_index": slot_i, "slot_type": stype}
                )
                content = gap_msg
                source = "gap"
                source_id = "gap"

            if content and not content.startswith("[CONTENT GAP:"):
                book_words_prior = (
                    sum(c.total_words for c in enriched_chapters) + ch_words
                )
                tw_tgt = slot.target_words
                max_x = _max_extra_chunks_for_format(bm.runtime_format, tw_tgt)
                base_wc = _wc(content)
                if format_wmax is not None:
                    room_book = max(0, format_wmax - book_words_prior)
                    if base_wc > room_book:
                        content = _truncate_to_word_budget(content, room_book)
                        base_wc = _wc(content)
                shortfall = max(0, tw_tgt - base_wc)
                extra_bodies: List[str] = []
                if max_x > 0 and shortfall >= 100:
                    goal = min(shortfall, tw_tgt)
                    if format_wmax is not None:
                        room_after_base = max(0, format_wmax - book_words_prior - base_wc)
                        goal = min(goal, room_after_base)
                    if goal < 100:
                        goal = 0
                    if source == "registry" and reg_sec_meta is not None and goal >= 100:
                        sd, vi = reg_sec_meta
                        extra_bodies = _extra_registry_variant_bodies(
                            sd, vi, seed_key, goal, max_x
                        )
                    elif (
                        goal >= 100
                        and source == "persona_atom"
                        and persona_expand_pool
                        and persona_primary_idx is not None
                        and len(persona_expand_pool) > 1
                    ):
                        extra_bodies = _expand_atom_pool_blocks(
                            persona_expand_pool,
                            persona_primary_idx,
                            seed_key,
                            "persona_x",
                            goal,
                            max_x,
                        )
                    elif (
                        goal >= 100
                        and source == "teacher_atom"
                        and teacher_expand_pool
                        and teacher_primary_idx is not None
                        and len(teacher_expand_pool) > 1
                    ):
                        extra_bodies = _expand_atom_pool_blocks(
                            teacher_expand_pool,
                            teacher_primary_idx,
                            seed_key,
                            "teacher_x",
                            goal,
                            max_x,
                        )
                if extra_bodies:
                    content = "\n\n".join([content] + extra_bodies)
                    nx = len(extra_bodies)
                    audit_counts["slots_format_scaled"] += 1
                    if source == "registry":
                        source_id = f"{source_id}+v{nx}"
                    else:
                        source_id = f"{source_id}+stack{nx}"

                if format_wmax is not None:
                    room_slot = max(0, format_wmax - book_words_prior)
                    if _wc(content) > room_slot:
                        content = _truncate_to_word_budget(content, room_slot)

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
                    variant_id=variant_id,
                    atom_id=atom_id,
                    match_scores=dict(match_scores),
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
                exercise_journey=None,
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
        spine_context=dict(request.spine_context or {}),
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
        "spine_context": dict(book.spine_context or {}),
        "chapters": [
            {
                "number": ch.number,
                "role": ch.role,
                "working_title": ch.working_title,
                "thesis": ch.thesis,
                "total_words": ch.total_words,
                "source_breakdown": ch.source_breakdown,
                "slots": [asdict(s) for s in ch.slots],
                "exercise_journey": ch.exercise_journey,
            }
            for ch in book.chapters
        ],
    }


def dump_enriched_book_json(book: EnrichedBook, indent: int = 2) -> str:
    return json.dumps(enriched_book_to_jsonable(book), indent=indent, ensure_ascii=False)


def selected_content_variants_artifact(book: EnrichedBook) -> Dict[str, Any]:
    """Render artifact: variant_id / atom_id / match_scores per enriched slot."""
    return {
        "schema_version": 1,
        "stage": "selected_content_variants",
        "topic": book.topic,
        "persona_id": book.persona_id,
        "teacher_id": book.teacher_id or "",
        "runtime_format": book.runtime_format,
        "chapters": [
            {
                "number": ch.number,
                "slots": [
                    {
                        "slot_type": s.slot_type,
                        "variant_id": s.variant_id,
                        "atom_id": s.atom_id,
                        "source": s.source,
                        "source_id": s.source_id,
                        "target_words": s.target_words,
                        "actual_words": s.actual_words,
                        "enrichment_applied": list(s.enrichment_applied or []),
                        "exercise_phase": s.exercise_phase,
                        "journey_exercise_id": s.journey_exercise_id,
                        "match_scores": dict(s.match_scores or {}),
                    }
                    for s in ch.slots
                ],
            }
            for ch in book.chapters
        ],
    }


def write_selected_content_variants_json(book: EnrichedBook, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(selected_content_variants_artifact(book), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


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


DEFAULT_DEPTH_PRIORITY: List[str] = [
    "recognition_depth",
    "mechanism_depth",
    "story_scene",
    "consequence_exposure",
    "somatic_detail",
    "practice_scaffold",
    "bridge_transition",
    "integration_landing",
]

# Per-chapter depth budget reservation constants
MIN_DEPTH_WORDS_PER_CHAPTER = 180
TARGET_DEPTH_WORDS_PER_CHAPTER = 300
MAX_DEPTH_WORDS_PER_CHAPTER = 600


def _chapter_phase(chapter_number: int, chapter_count: int) -> str:
    """early / mid / late per docs/DEPTH_MODULE_PROTOCOL.md."""
    if chapter_count <= 0:
        return "late"
    early_end = (chapter_count + 2) // 3  # ceil(n/3)
    mid_end = (2 * chapter_count) // 3  # floor(2n/3)
    if chapter_number <= early_end:
        return "early"
    if chapter_number <= mid_end:
        return "mid"
    return "late"


def _module_banned(
    module_name: str,
    chapter_number: int,
    phase: str,
    topic_overrides: Dict[str, Any],
) -> bool:
    banned_early = topic_overrides.get("banned_early") or []
    if phase == "early" and module_name in banned_early:
        return True
    banned_chapters = topic_overrides.get("banned_chapters") or {}
    if isinstance(banned_chapters, dict):
        ch_list = banned_chapters.get(module_name) or []
        if chapter_number in ch_list:
            return True
    return False


def _chapter_affinity_ok(affinity: Any, chapter_number: int) -> bool:
    if affinity is None or affinity == "all":
        return True
    if isinstance(affinity, list):
        return chapter_number in affinity
    return False


def _truncate_to_word_budget(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).strip()


def _phoenix_standard_text_candidates(data: Dict[str, Any]) -> List[str]:
    """Collect prose-sized strings from phoenix standard YAML (flat or nested)."""
    out: List[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if str(k).startswith("#"):
                    continue
                walk(v)
        elif isinstance(node, str):
            t = node.strip()
            if t and len(t.split()) > 20:
                out.append(t)

    walk(data)
    return out


def _collect_bridge_template_strings(tpl_root: Any) -> List[str]:
    strings: List[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, str):
            t = node.strip()
            if t and len(t.split()) > 5:
                strings.append(t)

    walk(tpl_root)
    return strings


def _extract_prose_from_canonical(raw: str) -> str:
    """
    Extract only prose text from a CANONICAL.txt file.

    CANONICAL.txt uses atom blocks of the form::

        ## TYPE vNN
        ---
        metadata: value
        ---
        Prose text here.
        ---

    This function strips all ``## TYPE vNN`` headers and metadata blocks,
    returning only the concatenated prose bodies.  The raw text is safe to
    pass to ``_truncate_to_word_budget`` after this call.
    """
    # Split on atom header lines (## WORD vNN …)
    header_re = re.compile(r"^##\s+\S+\s+v\d+", re.MULTILINE)
    blocks = header_re.split(raw)
    prose_parts: List[str] = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # Each block: [metadata section between first and second ---] [prose]
        # Split on bare --- lines
        segments = re.split(r"(?m)^---\s*$", block)
        # segments[0]: empty or leftover header text
        # segments[1]: metadata key: value lines
        # segments[2]: prose text
        # segments[3+]: may contain sub-blocks (some files have multiple --- prose pairs)
        # Collect all segments that look like prose (not YAML key: value lines)
        for seg in segments[2:]:
            text = seg.strip()
            if not text:
                continue
            # Skip segments that are purely YAML metadata
            lines = text.splitlines()
            metadata_only = all(
                re.match(r"^[A-Z_]+\s*:", l.strip()) or not l.strip()
                for l in lines
            )
            if metadata_only:
                continue
            prose_parts.append(text)
    return "\n\n".join(prose_parts)


def _select_prose_chunk(content: str, seed: str, min_words: int = 21) -> Optional[str]:
    """
    Select a coherent prose chunk from extracted CANONICAL text.

    Splits on paragraph breaks so the returned text starts at a paragraph
    boundary (not mid-sentence).  Uses ``seed`` to pick a deterministic
    starting paragraph so different call-sites (chapters) get different
    passages from the same file.

    Returns None if no adequate prose is available.
    """
    if not content:
        return None
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", content) if p.strip()]
    # Keep only substantial paragraphs
    paras = [p for p in paragraphs if len(p.split()) >= min_words]
    if not paras:
        return None
    # Pick a starting paragraph deterministically
    start_idx = _deterministic_index(f"{seed}:pa_para", len(paras))
    # Collect from start_idx, wrapping around, until we have ≥ 150 words
    collected: List[str] = []
    target = 150
    for i in range(len(paras)):
        para = paras[(start_idx + i) % len(paras)]
        collected.append(para)
        if sum(len(p.split()) for p in collected) >= target:
            break
    return "\n\n".join(collected) if collected else None


def _load_depth_content(
    source: Dict[str, Any],
    topic: str,
    teacher_id: Optional[str],
    persona_id: str,
    chapter_number: int,
    seed: str,
    repo_root: Path,
) -> Optional[str]:
    """
    Load actual content for a depth module from a specific source.
    Returns the prose text, or None if not available.
    """
    source_type = source.get("type")
    persona_id = (persona_id or "").strip()

    if source_type == "teacher_atom":
        if not teacher_id:
            return None
        slot_types = source.get("slot_types", [])
        for slot_type in slot_types:
            atom_dir = (
                repo_root
                / "SOURCE_OF_TRUTH"
                / "teacher_banks"
                / teacher_id
                / "approved_atoms"
                / slot_type
            )
            if not atom_dir.exists():
                continue
            atoms = sorted(atom_dir.glob("*.yaml"))
            if not atoms:
                continue
            idx = _deterministic_index(f"{seed}:teacher:{slot_type}", len(atoms))
            atom_data = _load_yaml(atoms[idx])
            content = str(atom_data.get("body") or atom_data.get("content") or "").strip()
            if content and len(content.split()) > 20:
                return content
        return None

    if source_type == "persona_atom":
        slot_types = source.get("slot_types", [])
        for slot_type in slot_types:
            canonical = repo_root / "atoms" / persona_id / topic / slot_type / "CANONICAL.txt"
            if canonical.exists():
                raw = canonical.read_text(encoding="utf-8")
                content = _extract_prose_from_canonical(raw)
                chunk = _select_prose_chunk(content, seed)
                if chunk:
                    return chunk
        topic_dir = repo_root / "atoms" / persona_id / topic
        if topic_dir.exists():
            for engine_dir in sorted(topic_dir.iterdir()):
                if not engine_dir.is_dir():
                    continue
                if engine_dir.name.isupper():
                    continue
                canonical = engine_dir / "CANONICAL.txt"
                if canonical.exists():
                    raw = canonical.read_text(encoding="utf-8")
                    content = _extract_prose_from_canonical(raw)
                    chunk = _select_prose_chunk(content, seed)
                    if chunk:
                        return chunk
        return None

    if source_type == "registry_variant":
        section_types = source.get("section_types", [])
        variant_preference = source.get("variant_preference", ["F2", "F3", "F4"])
        registry_path = repo_root / "registry" / f"{topic}.yaml"
        if not registry_path.exists():
            return None
        registry = _load_yaml(registry_path)
        sections = registry.get("sections", {})
        ch_key = f"chapter_{chapter_number:02d}"
        ch_data = sections.get(ch_key, {})
        inner = ch_data.get("sections", {})
        if not isinstance(inner, dict):
            return None
        for _sec_key, sec_data in inner.items():
            if not isinstance(sec_data, dict):
                continue
            if sec_data.get("type") not in section_types:
                continue
            variants = sec_data.get("variants", [])
            for pref in variant_preference:
                pref_l = pref.lower()
                for v in variants:
                    if not isinstance(v, dict):
                        continue
                    fam = str(v.get("variant_family", "")).lower()
                    vid = str(v.get("variant_id", "")).lower()
                    if pref_l in fam or pref_l in vid:
                        content = str(v.get("content") or "").strip()
                        if content and len(content.split()) > 20:
                            return content
        return None

    if source_type == "component_template":
        rel = source.get("source_path", "config/pearl_practice/component_templates.yaml")
        templates_path = repo_root / rel
        if not templates_path.exists():
            return None
        templates = _load_yaml(templates_path)
        pool = source.get("pool", "bridge")
        items = templates.get(pool, [])
        if not items:
            return None
        idx = _deterministic_index(f"{seed}:template:{pool}", len(items))
        item = items[idx]
        if isinstance(item, str):
            return item.strip()
        if isinstance(item, dict):
            return str(item.get("text") or item.get("content") or "").strip() or None
        return None

    if source_type == "phoenix_standard":
        rel = source.get("source_path", "")
        path = repo_root / rel if rel else Path()
        if not path.exists():
            return None
        data = _load_yaml(path)
        blocks = _phoenix_standard_text_candidates(data)
        if not blocks:
            return None
        idx = _deterministic_index(f"{seed}:phoenix", len(blocks))
        return blocks[idx]

    if source_type == "exercise_atom":
        rel = source.get("source_path", "")
        path = repo_root / rel if rel else Path()
        if not path.exists():
            return None
        atoms = sorted(path.glob("*.yaml"))
        if not atoms:
            return None
        idx = _deterministic_index(f"{seed}:exercise", len(atoms))
        atom_data = _load_yaml(atoms[idx])
        return str(atom_data.get("body") or atom_data.get("content") or "").strip() or None

    if source_type == "practice_library":
        try:
            from phoenix_v4.exercises.practice_library_loader import get_exercise_for_chapter

            composed = get_exercise_for_chapter(
                chapter_index=chapter_number - 1,
                topic_id=topic,
                persona_id=persona_id,
                seed=seed,
            )
            if composed and composed.strip() and len(composed.split()) > 20:
                return composed.strip()
        except Exception as e:  # pragma: no cover
            logger.warning("Depth practice_library load failed: %s", e)
        return None

    if source_type == "exercise_bridge":
        rel = source.get("source_path", "SOURCE_OF_TRUTH/exercises_v4/bridge_templates.yaml")
        path = repo_root / rel
        if not path.exists():
            return None
        data = _load_yaml(path)
        tpl_root = data.get("templates") or {}
        strings = _collect_bridge_template_strings(tpl_root)
        long_strings = [s for s in strings if len(s.split()) > 20]
        pool = long_strings or strings
        if not pool:
            return None
        idx = _deterministic_index(f"{seed}:exercise_bridge", len(pool))
        return pool[idx]

    return None


def _fill_chapter_depth(
    chapter: EnrichedChapter,
    enriched_book: EnrichedBook,
    modules: Dict[str, Any],
    topic_overrides: Dict[str, Any],
    topic: str,
    tid: Optional[str],
    persona_id: str,
    chapter_count: int,
    rf: str,
    root: Path,
    max_words_to_add: int,
    book_budget_remaining: Optional[int],
    depth_round: int,
    pass_label: str,
    audit_list: List[Dict[str, Any]],
    deficit_floor: int,
) -> int:
    """
    Attempt to fill one chapter with depth content up to max_words_to_add.
    Returns total words added.
    """
    phase = _chapter_phase(chapter.number, chapter_count)
    priority_key = f"depth_priority_{phase}"
    priority_list = list(topic_overrides.get(priority_key) or [])
    if not priority_list:
        priority_list = list(DEFAULT_DEPTH_PRIORITY)

    words_added_total = 0
    remaining_allowance = max_words_to_add

    for module_name in priority_list:
        if remaining_allowance <= deficit_floor:
            break
        if _module_banned(module_name, chapter.number, phase, topic_overrides):
            continue
        module = modules.get(module_name)
        if not module:
            continue
        if not _chapter_affinity_ok(module.get("chapter_affinity"), chapter.number):
            continue
        restriction = module.get("topic_restriction")
        if restriction and topic not in restriction:
            continue

        tw_bounds = module.get("target_words_per_chapter") or [200, 400]
        upper_cap = int(tw_bounds[1]) if len(tw_bounds) > 1 else 400
        if rf == "deep_book_6h":
            upper_cap = min(1400, max(upper_cap, int(round(upper_cap * 2.4))))

        for source in module.get("sources", []):
            if not isinstance(source, dict):
                continue
            content = _load_depth_content(
                source=source,
                topic=topic,
                teacher_id=tid,
                persona_id=persona_id,
                chapter_number=chapter.number,
                seed=f"depth:{topic}:{chapter.number}:{module_name}:r{depth_round}:{pass_label}",
                repo_root=root,
            )
            if not content:
                continue
            word_list = content.split()
            if len(word_list) <= 20:
                continue

            max_chunk = min(remaining_allowance, upper_cap)
            if book_budget_remaining is not None:
                if book_budget_remaining - words_added_total <= 0:
                    return words_added_total
                max_chunk = min(max_chunk, book_budget_remaining - words_added_total)

            trimmed = _truncate_to_word_budget(content, max_chunk)
            added_w = len(trimmed.split())
            if added_w <= 0:
                continue

            depth_slot = EnrichedSlot(
                slot_type=f"DEPTH_{module_name.upper()}",
                content=trimmed,
                source=f"depth_module:{module_name}:{source.get('type')}",
                source_id=f"depth_{module_name}_{chapter.number}_{pass_label}",
                target_words=max_chunk,
                actual_words=added_w,
                enrichment_applied=[module_name],
            )
            chapter.slots.append(depth_slot)
            chapter.total_words += added_w
            words_added_total += added_w
            remaining_allowance -= added_w

            audit_list.append({
                "chapter": chapter.number,
                "module": module_name,
                "source_type": source.get("type"),
                "words_added": added_w,
                "remaining_deficit": max(0, remaining_allowance),
                "depth_round": depth_round,
                "pass": pass_label,
            })

            if remaining_allowance <= deficit_floor:
                break

        if remaining_allowance <= deficit_floor:
            break

    return words_added_total


def apply_depth_pass(
    enriched_book: EnrichedBook,
    depth_map: Dict[str, Any],
    repo_root: Optional[Path] = None,
) -> EnrichedBook:
    """
    Fill thin chapters/slots by requesting depth modules from the depth_module_map.

    Runs AFTER select_enrichment(). Uses two-pass per-chapter budget reservation
    to prevent early chapters from starving late chapters (chapters 9–12).

    Pass 1 (Reservation): Each chapter gets up to MIN_DEPTH_WORDS_PER_CHAPTER (180w)
    before any chapter gets priority fill. Early chapters cannot consume late chapters'
    reserved budget.

    Pass 2 (Priority fill): Remaining budget distributed by priority — late chapters
    first, then by deficit size.
    """
    root = repo_root or REPO_ROOT
    topic = enriched_book.topic
    modules = depth_map.get("depth_modules") or {}
    topic_overrides = (depth_map.get("topic_overrides") or {}).get(topic, {})
    tid = enriched_book.teacher_id
    persona_id = enriched_book.persona_id
    chapter_count = len(enriched_book.chapters)
    rf = (enriched_book.runtime_format or "").strip()
    _bounds = _load_runtime_word_bounds(rf, root)
    book_wmax: Optional[int] = _bounds[1] if _bounds else None
    deficit_floor = 55 if rf == "deep_book_6h" else 100
    depth_rounds = 3 if rf == "deep_book_6h" else 1

    enriched_book.enrichment_audit.setdefault("depth_modules_added", [])

    # Format-aware per-chapter depth budget caps.
    # Short formats (short_book_30: 7500w) keep the conservative defaults.
    # Large formats (deep_book_6h: 65000w) need proportionally larger caps.
    if book_wmax is not None and chapter_count > 0:
        fair_share = book_wmax // chapter_count
        min_depth_per_ch = max(MIN_DEPTH_WORDS_PER_CHAPTER, fair_share // 4)
        target_depth_per_ch = max(TARGET_DEPTH_WORDS_PER_CHAPTER, fair_share // 2)
        max_depth_per_ch = max(MAX_DEPTH_WORDS_PER_CHAPTER, fair_share)
    else:
        min_depth_per_ch = MIN_DEPTH_WORDS_PER_CHAPTER
        target_depth_per_ch = TARGET_DEPTH_WORDS_PER_CHAPTER
        max_depth_per_ch = MAX_DEPTH_WORDS_PER_CHAPTER

    # Per-chapter tracking for audit telemetry
    pre_depth_words: Dict[int, int] = {ch.number: ch.total_words for ch in enriched_book.chapters}
    depth_words_added_by_chapter: Dict[int, int] = {ch.number: 0 for ch in enriched_book.chapters}
    depth_budget_starvation: List[Dict[str, Any]] = []
    audit_list: List[Dict[str, Any]] = enriched_book.enrichment_audit["depth_modules_added"]

    for _depth_round in range(depth_rounds):

        # ── Pass 1: Reservation ─────────────────────────────────────────────
        # Each chapter gets up to MIN_DEPTH_WORDS_PER_CHAPTER from a shared
        # reservation pool. No chapter may consume another chapter's reserved share.
        #
        # Reservation pool = MIN × n_chapters (≤ 85% of book_wmax for safety).
        reservation_pool = min_depth_per_ch * chapter_count
        if book_wmax is not None:
            reservation_pool = min(reservation_pool, int(book_wmax * 0.85))

        reservation_used = 0

        for ch_idx, chapter in enumerate(enriched_book.chapters):
            # Guard the reservation budget for remaining chapters:
            # chapters after this one each need at least MIN.
            remaining_after_count = chapter_count - ch_idx - 1
            protected_for_later = remaining_after_count * min_depth_per_ch
            available_reservation = reservation_pool - reservation_used - protected_for_later
            available_reservation = max(0, min(available_reservation, min_depth_per_ch))

            if available_reservation <= deficit_floor:
                # Reservation pool cannot serve this chapter
                if depth_words_added_by_chapter[chapter.number] < min_depth_per_ch:
                    depth_budget_starvation.append({
                        "chapter": chapter.number,
                        "reserved_min_met": False,
                        "reason": "reservation_pool_exhausted",
                        "depth_round": _depth_round,
                    })
                continue

            # Only add depth if chapter actually needs it
            target_words = sum(s.target_words for s in chapter.slots)
            deficit = target_words - chapter.total_words
            if deficit <= deficit_floor:
                continue

            # How much can still be added this round (respect MAX cap)?
            already_added = depth_words_added_by_chapter[chapter.number]
            room_in_cap = max(0, max_depth_per_ch - already_added)
            want = min(available_reservation, deficit, room_in_cap)
            if want <= deficit_floor:
                continue

            # Compute global book budget remaining
            book_room: Optional[int] = None
            if book_wmax is not None:
                current_book = sum(ch.total_words for ch in enriched_book.chapters)
                book_room = book_wmax - current_book
                if book_room <= 0:
                    break

            added = _fill_chapter_depth(
                chapter=chapter,
                enriched_book=enriched_book,
                modules=modules,
                topic_overrides=topic_overrides,
                topic=topic,
                tid=tid,
                persona_id=persona_id,
                chapter_count=chapter_count,
                rf=rf,
                root=root,
                max_words_to_add=want,
                book_budget_remaining=book_room,
                depth_round=_depth_round,
                pass_label=f"p1r{_depth_round}",
                audit_list=audit_list,
                deficit_floor=deficit_floor,
            )
            reservation_used += added
            depth_words_added_by_chapter[chapter.number] += added

            if added == 0:
                # No eligible candidates found despite budget being available
                depth_budget_starvation.append({
                    "chapter": chapter.number,
                    "reserved_min_met": False,
                    "reason": "no_eligible_depth_candidates",
                    "depth_round": _depth_round,
                })

        # ── Pass 2: Priority fill ───────────────────────────────────────────
        # Distribute remaining budget. Late chapters (7–12) come first,
        # then by highest deficit.
        pass2_order = sorted(
            enriched_book.chapters,
            key=lambda ch: (
                0 if ch.number >= 7 else 1,          # late chapters first
                -(sum(s.target_words for s in ch.slots) - ch.total_words),  # largest deficit first
            ),
        )

        for chapter in pass2_order:
            if book_wmax is not None:
                current_book = sum(ch.total_words for ch in enriched_book.chapters)
                book_room = book_wmax - current_book
                if book_room <= 0:
                    break
            else:
                book_room = None

            target_words = sum(s.target_words for s in chapter.slots)
            deficit = target_words - chapter.total_words
            if deficit <= deficit_floor:
                continue

            already_added = depth_words_added_by_chapter[chapter.number]
            room_in_cap = max(0, max_depth_per_ch - already_added)
            # Target up to TARGET per chapter, max up to MAX
            want = min(deficit, room_in_cap, target_depth_per_ch)
            if want <= deficit_floor:
                continue

            if book_room is not None:
                want = min(want, book_room)
            if want <= deficit_floor:
                continue

            added = _fill_chapter_depth(
                chapter=chapter,
                enriched_book=enriched_book,
                modules=modules,
                topic_overrides=topic_overrides,
                topic=topic,
                tid=tid,
                persona_id=persona_id,
                chapter_count=chapter_count,
                rf=rf,
                root=root,
                max_words_to_add=want,
                book_budget_remaining=book_room,
                depth_round=_depth_round,
                pass_label=f"p2r{_depth_round}",
                audit_list=audit_list,
                deficit_floor=deficit_floor,
            )
            depth_words_added_by_chapter[chapter.number] += added

    # ── Audit telemetry ─────────────────────────────────────────────────────
    depth_budget_by_chapter: List[Dict[str, Any]] = []
    for chapter in enriched_book.chapters:
        added = depth_words_added_by_chapter.get(chapter.number, 0)
        starved = any(
            s["chapter"] == chapter.number and not s["reserved_min_met"]
            for s in depth_budget_starvation
        )
        depth_budget_by_chapter.append({
            "chapter": chapter.number,
            "pre_depth_words": pre_depth_words.get(chapter.number, 0),
            "depth_words_added": added,
            "post_depth_words": chapter.total_words,
            "reserved_min_met": added >= min_depth_per_ch and not starved,
        })

    enriched_book.enrichment_audit["depth_budget_policy"] = {
        "mode": "per_chapter_reservation",
        "book_wmax": book_wmax,
        "reserved_min_per_chapter": min_depth_per_ch,
        "target_per_chapter": target_depth_per_ch,
        "max_per_chapter": max_depth_per_ch,
    }
    enriched_book.enrichment_audit["depth_budget_by_chapter"] = depth_budget_by_chapter
    enriched_book.enrichment_audit["depth_budget_starvation"] = depth_budget_starvation

    enriched_book.total_words = sum(ch.total_words for ch in enriched_book.chapters)
    enriched_book.enrichment_audit["total_words"] = enriched_book.total_words
    return enriched_book


def attach_exercise_journeys(
    enriched_book: EnrichedBook,
    *,
    seed: str,
    enabled: bool = True,
    repo_root: Optional[Path] = None,
) -> EnrichedBook:
    """
    After enrichment + depth pass: attach per-chapter exercise journeys to chapters and
    EXERCISE slots at template sections (4 / 8 / 10). Logs warnings when thesis outcome
    validation fails, prerequisites fail, or redundancy is detected.
    """
    if not enabled:
        return enriched_book

    from phoenix_v4.planning.exercise_journey_planner import (
        plan_exercise_journey,
        resolve_thesis_id,
    )
    from phoenix_v4.planning.exercise_registry_loader import (
        load_exercise_registry,
        load_journey_templates,
        load_thesis_outcome_map,
    )

    root = repo_root or REPO_ROOT
    exercises = load_exercise_registry(repo_root=root)
    thesis_outcomes = load_thesis_outcome_map(repo_root=root)
    templates = load_journey_templates(repo_root=root)

    ej_audit: List[Dict[str, Any]] = []
    topic = enriched_book.topic
    runtime = enriched_book.runtime_format or "standard_book"

    for chapter in enriched_book.chapters:
        thesis_id = resolve_thesis_id(topic, chapter.number, seed)
        journey = plan_exercise_journey(
            chapter.number,
            thesis_id,
            runtime,
            seed=seed,
            exercise_registry=exercises,
            thesis_outcomes=thesis_outcomes,
            journey_templates=templates,
        )

        if not journey.outcome_ok:
            logger.warning(
                "Exercise journey outcome mismatch ch=%s thesis=%s violations=%s",
                chapter.number,
                thesis_id,
                journey.outcome_violations,
            )
        if journey.prerequisite_violations:
            logger.warning(
                "Exercise journey prerequisites ch=%s violations=%s",
                chapter.number,
                journey.prerequisite_violations,
            )
        if journey.redundancy_warnings:
            logger.warning(
                "Exercise journey redundancy ch=%s warnings=%s",
                chapter.number,
                journey.redundancy_warnings,
            )

        chapter.exercise_journey = {
            "journey_type": journey.journey_type,
            "template_id": journey.template_id,
            "aligned_with_thesis": journey.aligned_with_thesis,
            "expected_outcome": journey.expected_outcome,
            "outcome_ok": journey.outcome_ok,
            "outcome_violations": list(journey.outcome_violations),
            "prerequisite_violations": list(journey.prerequisite_violations),
            "redundancy_warnings": list(journey.redundancy_warnings),
            "phases": [
                {
                    "name": p.name,
                    "target_section": p.target_section,
                    "exercise_id": p.exercise_id,
                    "intro": p.intro,
                }
                for p in journey.phases
            ],
        }

        used_sections: Dict[int, str] = {}
        for phase in journey.phases:
            sec = int(phase.target_section)
            for si, slot in enumerate(chapter.slots):
                if si + 1 != sec:
                    continue
                if slot.slot_type.strip().upper() != "EXERCISE":
                    continue
                if sec in used_sections:
                    continue
                slot.exercise_phase = phase.name
                slot.journey_exercise_id = phase.exercise_id
                used_sections[sec] = phase.exercise_id
                break

        ej_audit.append(
            {
                "chapter": chapter.number,
                "thesis_id": thesis_id,
                "journey_type": journey.journey_type,
                "exercise_ids": [p.exercise_id for p in journey.phases],
            }
        )

    enriched_book.enrichment_audit["exercise_journeys"] = ej_audit
    return enriched_book
