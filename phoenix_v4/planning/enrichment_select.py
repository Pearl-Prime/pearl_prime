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

Depth pass (apply_depth_pass): after select_enrichment, fills thin chapters using
config/depth/depth_module_map.yaml — existing content only, no LLM generation.
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
    _load_yaml,
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
    exercise_phase: Optional[str] = None
    journey_exercise_id: Optional[str] = None


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
                "exercise_journey": ch.exercise_journey,
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
                content = canonical.read_text(encoding="utf-8").strip()
                if content and len(content.split()) > 20:
                    return content
        topic_dir = repo_root / "atoms" / persona_id / topic
        if topic_dir.exists():
            for engine_dir in sorted(topic_dir.iterdir()):
                if not engine_dir.is_dir():
                    continue
                if engine_dir.name.isupper():
                    continue
                canonical = engine_dir / "CANONICAL.txt"
                if canonical.exists():
                    content = canonical.read_text(encoding="utf-8").strip()
                    if content and len(content.split()) > 20:
                        return content
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


def apply_depth_pass(
    enriched_book: EnrichedBook,
    depth_map: Dict[str, Any],
    repo_root: Optional[Path] = None,
) -> EnrichedBook:
    """
    Fill thin chapters/slots by requesting depth modules from the depth_module_map.

    Runs AFTER select_enrichment(). Adds content where chapters are under their
    target word count (sum of slot target_words).
    """
    root = repo_root or REPO_ROOT
    topic = enriched_book.topic
    modules = depth_map.get("depth_modules") or {}
    topic_overrides = (depth_map.get("topic_overrides") or {}).get(topic, {})
    tid = enriched_book.teacher_id
    persona_id = enriched_book.persona_id
    chapter_count = len(enriched_book.chapters)

    enriched_book.enrichment_audit.setdefault("depth_modules_added", [])

    for chapter in enriched_book.chapters:
        target_words = sum(s.target_words for s in chapter.slots)
        actual_words = chapter.total_words
        deficit = target_words - actual_words
        if deficit <= 100:
            continue

        phase = _chapter_phase(chapter.number, chapter_count)
        priority_key = f"depth_priority_{phase}"
        priority_list = list(topic_overrides.get(priority_key) or [])
        if not priority_list:
            priority_list = list(DEFAULT_DEPTH_PRIORITY)

        for module_name in priority_list:
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

            for source in module.get("sources", []):
                if not isinstance(source, dict):
                    continue
                content = _load_depth_content(
                    source=source,
                    topic=topic,
                    teacher_id=tid,
                    persona_id=persona_id,
                    chapter_number=chapter.number,
                    seed=f"depth:{topic}:{chapter.number}:{module_name}",
                    repo_root=root,
                )
                if not content:
                    continue
                word_list = content.split()
                if len(word_list) <= 20:
                    continue

                max_chunk = min(deficit, upper_cap)
                trimmed = _truncate_to_word_budget(content, max_chunk)
                added_w = len(trimmed.split())
                if added_w <= 0:
                    continue

                depth_slot = EnrichedSlot(
                    slot_type=f"DEPTH_{module_name.upper()}",
                    content=trimmed,
                    source=f"depth_module:{module_name}:{source.get('type')}",
                    source_id=f"depth_{module_name}_{chapter.number}",
                    target_words=max_chunk,
                    actual_words=added_w,
                    enrichment_applied=[module_name],
                )
                chapter.slots.append(depth_slot)
                chapter.total_words += added_w
                deficit -= added_w

                enriched_book.enrichment_audit["depth_modules_added"].append(
                    {
                        "chapter": chapter.number,
                        "module": module_name,
                        "source_type": source.get("type"),
                        "words_added": added_w,
                        "remaining_deficit": max(0, deficit),
                    }
                )

                if deficit <= 100:
                    break

            if deficit <= 100:
                break

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
