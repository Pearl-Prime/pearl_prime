"""
BeatmapCompile stage — turns ShapedSpine into a concrete per-chapter slot plan.

Consumes output from phoenix_v4.planning.knob_apply only (no raw spine registry).
Chapter thesis, role, and working_title stay identical to the shaped spine.
"""
from __future__ import annotations

import logging
import warnings
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from phoenix_v4.planning.knob_apply import (
    REPO_ROOT,
    ShapedChapter,
    ShapedSpine,
    SpineChapter,
    load_spine,
)

logger = logging.getLogger(__name__)

# Alias spine section labels to canonical beat slots used in format_registry.
_SECTION_ALIASES = {
    "PRACTICE": "EXERCISE",
    "FORWARD": "INTEGRATION",
}

# Standard and deeper runtime formats use the full 10-slot somatic grid (V2 template 12×10).
SOMATIC_FULL_RUNTIME_FORMATS = frozenset(
    {"standard_book", "extended_book_2h", "deep_book_4h", "deep_book_6h"}
)

# Canonical slot types per V2 somatic section_01 … section_10.
SOMATIC_10_SLOT_GRID = [
    "HOOK",  # section_01
    "SCENE",  # section_02
    "REFLECTION",  # section_03
    "EXERCISE",  # section_04 — awareness phase
    "SCENE",  # section_05
    "TEACHER_DOCTRINE",  # section_06 — mechanism / teacher voice
    "REFLECTION",  # section_07
    "EXERCISE",  # section_08 — regulation phase
    "SCENE",  # section_09
    "INTEGRATION",  # section_10
]

# Parallel budget keys (non-uniform six-hour baseline; scaled per chapter target).
SOMATIC_BUDGET_KEYS = [
    "HOOK",
    "SCENE_A",
    "REFLECTION_A",
    "EXERCISE_A",
    "SCENE_B",
    "TEACHER_DOCTRINE",
    "REFLECTION_B",
    "EXERCISE_B",
    "SCENE_C",
    "INTEGRATION",
]

# Total baseline 4,520 words/chapter @ full scale (12 ch × ~4.5k ≈ six-hour book).
SOMATIC_WORD_BUDGET: Dict[str, int] = {
    "HOOK": 320,
    "SCENE_A": 520,
    "REFLECTION_A": 380,
    "EXERCISE_A": 560,
    "SCENE_B": 500,
    "TEACHER_DOCTRINE": 460,
    "REFLECTION_B": 380,
    "EXERCISE_B": 620,
    "SCENE_C": 460,
    "INTEGRATION": 320,
}

# Beatmap slot index 0..9 → V2 somatic section index 1..10.
SLOT_TO_SOMATIC_INDEX: Dict[int, int] = {
    0: 1,
    1: 2,
    2: 3,
    3: 4,
    4: 5,
    5: 6,
    6: 7,
    7: 8,
    8: 9,
    9: 10,
}


@dataclass
class BeatmapSlot:
    slot_type: str
    weight: float
    target_words: int
    somatic_section_index: int  # 1..10 for V2 somatic template; 0 = not used (short formats)
    atom_selection_criteria: Dict[str, Any]
    enrichment_hooks: List[str]
    emotional_temperature: str
    is_required: bool


@dataclass
class BeatmapChapter:
    number: int
    role: str
    working_title: str
    thesis: str
    phase: str
    target_word_count: int
    slots: List[BeatmapSlot]
    slot_definitions: List[str]


@dataclass
class Beatmap:
    schema_version: int
    stage: str
    topic: str
    family_id: str
    runtime_format: str
    total_target_words: int
    chapters: List[BeatmapChapter]
    compile_audit: Dict[str, Any]


def _load_yaml(path: Path) -> Any:
    if yaml is None:
        raise RuntimeError("PyYAML is required for beatmap_compile loaders")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_topic_engines(topic: str, repo_root: Optional[Path] = None) -> Dict[str, Any]:
    root = repo_root or REPO_ROOT
    path = root / "config" / "topic_engine_bindings.yaml"
    if not path.exists():
        return {"allowed_engines": [], "topic": topic}
    data = _load_yaml(path)
    block = data.get(topic)
    if not isinstance(block, dict):
        return {"allowed_engines": [], "topic": topic}
    out = dict(block)
    out["topic"] = topic
    return out


def load_format_spec(format_id: str, repo_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Runtime format block from format_registry.yaml plus canonical_slot_order derived
    from the first compatible structural format that declares slot_template (e.g. F006).
    """
    root = repo_root or REPO_ROOT
    path = root / "config" / "format_selection" / "format_registry.yaml"
    reg = _load_yaml(path)
    rt = (reg.get("runtime_formats") or {}).get(format_id)
    if not isinstance(rt, dict):
        raise KeyError(f"Unknown runtime format {format_id!r}")
    spec: Dict[str, Any] = dict(rt)
    compat = spec.get("compatible_structural_formats") or []
    structural = reg.get("structural_formats") or {}
    order: Optional[List[str]] = None
    for fid in compat:
        sf = structural.get(fid)
        if isinstance(sf, dict) and sf.get("slot_template"):
            order = [str(x) for x in sf["slot_template"]]
            break
    if order is None:
        default_slots = reg.get("default_slot_definitions") or []
        if default_slots and isinstance(default_slots[0], list):
            order = [str(x) for x in default_slots[0]]
    if order is None:
        order = ["HOOK", "SCENE", "STORY", "REFLECTION", "COMPRESSION", "EXERCISE", "INTEGRATION"]
    spec["canonical_slot_order"] = order
    return spec


def _normalize_slot(slot: str) -> str:
    u = slot.strip().upper()
    return _SECTION_ALIASES.get(u, u)


def _forbidden_slot_types(forbidden_moves: List[str]) -> Set[str]:
    """Heuristic mapping of spine forbidden_moves lines to canonical slot types."""
    out: Set[str] = set()
    for line in forbidden_moves:
        low = line.lower()
        introduces_practice = (
            "do not introduce" in low
            or "not introduce" in low
            or "don't introduce" in low
            or "no practice of any kind" in low
        ) and any(k in low for k in ("practice", "exercise", "technique", "somatic"))
        blocks_practice_here = (
            ("not yet" in low or "before chapter" in low)
            and ("practice" in low or "exercise" in low)
            and "frame" not in low
        )
        if introduces_practice or blocks_practice_here:
            out.add("EXERCISE")
        neg = "do not" in low or "no " in low or "not yet" in low
        if neg and ("compression" in low or "compress" in low) and "frame" not in low:
            out.add("COMPRESSION")
        if ("do not explain" in low or "not explain" in low) and "mechanism" in low:
            out.add("COMPRESSION")
    return out


def _slug_hooks(slug: str, slot_type: str) -> List[str]:
    """Map enrichment_priority slugs to semantic hook labels per slot."""
    s = slug.lower()
    hooks: List[str] = []
    if slot_type == "EXERCISE" and (
        "somatic" in s or "exercise" in s or "practice" in s or "tending" in s or "ritual" in s
    ):
        hooks.append("somatic_exercise")
    if slot_type == "STORY" and ("story" in s or "vivid" in s or "scene" in s):
        hooks.append("story_vividness")
    if slot_type in ("HOOK", "SCENE") and (
        "persona" in s or "open" in s or "alarm" in s or ("voice" in s and "teacher" not in s)
    ):
        hooks.append("persona_alarm_behavior")
    if slot_type in ("REFLECTION", "INTEGRATION", "TEACHER_DOCTRINE") and (
        "teacher" in s or "voice" in s or "integration" in s or "mechanism" in s
    ):
        hooks.append("teacher_voice")
    return hooks


def _enrichment_hooks_for_slot(slugs: List[str], slot_type: str) -> List[str]:
    acc: List[str] = []
    for sl in slugs:
        acc.extend(_slug_hooks(sl, slot_type))
    out: List[str] = []
    for h in acc:
        if h not in out:
            out.append(h)
    if slot_type == "EXERCISE" and not out:
        out.append("somatic_exercise")
    return out


def _slot_minimums() -> Dict[str, int]:
    return {
        "HOOK": 100,
        "EXERCISE": 80,
        "INTEGRATION": 60,
    }


def _default_min() -> int:
    return 50


def _scale_budget(base_budget: Dict[str, int], target_chapter_words: int) -> Dict[str, int]:
    total = sum(base_budget.values())
    if total <= 0:
        return {k: 0 for k in base_budget}
    scale = target_chapter_words / total
    return {k: int(v * scale) for k, v in base_budget.items()}


def _reconcile_somatic_row_targets(
    ordered: List[str],
    budget_keys: List[str],
    scaled: Dict[str, int],
    chapter_target: int,
) -> List[int]:
    """Enforce per-slot floors then snap the row sum to chapter_target."""
    mins = _slot_minimums()
    dmin = _default_min()
    out: List[int] = []
    for st, bk in zip(ordered, budget_keys):
        floor = mins.get(st, dmin)
        out.append(max(floor, int(scaled.get(bk, floor))))
    delta = chapter_target - sum(out)
    if delta == 0:
        return out
    if delta > 0:
        bump_order = sorted(range(len(out)), key=lambda j: -out[j])
        k = 0
        while delta > 0 and out:
            out[bump_order[k % len(out)]] += 1
            delta -= 1
            k += 1
        return out
    neg = -delta
    k = 0
    while neg > 0 and k < 100000:
        reducible = [
            j
            for j, st in enumerate(ordered)
            if out[j] > mins.get(st, dmin)
        ]
        if not reducible:
            break
        j = max(reducible, key=lambda idx: out[idx])
        out[j] -= 1
        neg -= 1
        k += 1
    return out


def _somatic_slot_weight(slot_type: str, wmap: Dict[str, float]) -> float:
    st = slot_type.strip().upper()
    if st == "TEACHER_DOCTRINE":
        return max(
            float(wmap.get("COMPRESSION", 0.0)),
            float(wmap.get("REFLECTION", 0.0)) * 0.55,
            0.35,
        )
    return float(wmap.get(st, 0.0))


def _somatic_slot_required(slot_type: str, req_set: Set[str]) -> bool:
    st = slot_type.strip().upper()
    if st == "TEACHER_DOCTRINE":
        return "COMPRESSION" in req_set or "REFLECTION" in req_set
    if st in ("SCENE", "STORY"):
        return "SCENE" in req_set or "STORY" in req_set
    return st in req_set


def resolve_slot_definitions(
    shaped_chapter: ShapedChapter,
    runtime_format: str,
    orig: SpineChapter,
) -> List[str]:
    """
    Ordered slot types for this chapter.

    Standard and deeper runtime formats use the fixed 10-slot somatic grid so every
    V2 somatic template section can be consumed. Short/micro formats are compiled via
    the legacy candidate + canonical_order path in compile_beatmap (this function is
    not used for those formats).
    """
    del shaped_chapter  # reserved for future per-chapter somatic tuning
    if runtime_format in SOMATIC_FULL_RUNTIME_FORMATS:
        return list(SOMATIC_10_SLOT_GRID)
    required = [_normalize_slot(s) for s in (orig.required_sections or [])]
    if required:
        return required
    return ["HOOK", "SCENE", "REFLECTION", "EXERCISE", "INTEGRATION"]


def _allocate_words(
    slot_types: List[str],
    weights: Dict[str, float],
    chapter_target: int,
    audit_min_overrides: List[Dict[str, Any]],
) -> Dict[str, int]:
    mins = _slot_minimums()
    dmin = _default_min()
    wsum = sum(max(weights.get(s, 0.0), 0.0) for s in slot_types)
    if wsum <= 0:
        wsum = 1.0
    proportional = {s: weights.get(s, 0.0) / wsum * chapter_target for s in slot_types}
    words = {s: max(proportional[s], float(mins.get(s, dmin))) for s in slot_types}
    total = sum(words.values())
    excess = total - chapter_target
    if excess > 1e-6:
        slack = {s: max(0.0, words[s] - float(mins.get(s, dmin))) for s in slot_types}
        flex = sum(slack.values())
        if flex > 1e-6:
            for s in slot_types:
                shave = excess * (slack[s] / flex)
                new_v = max(float(mins.get(s, dmin)), words[s] - shave)
                if new_v < words[s]:
                    words[s] = new_v
            total = sum(words.values())
            excess = total - chapter_target
        # integer flooring can still drift; nudge from largest flexible slots
    deficit = chapter_target - total
    if deficit > 1e-6:
        wflex = {s: max(weights.get(s, 0.0), 0.001) for s in slot_types}
        wf = sum(wflex.values())
        for s in slot_types:
            words[s] += deficit * (wflex[s] / wf)

    int_words: Dict[str, int] = {}
    for s in slot_types:
        int_words[s] = max(mins.get(s, dmin), int(round(words[s])))
    delta = chapter_target - sum(int_words.values())
    if delta != 0 and slot_types:
        key_fn = lambda st: int_words[st] - mins.get(st, dmin)
        order = sorted(slot_types, key=key_fn, reverse=True)
        i = 0
        while delta != 0 and order:
            st = order[i % len(order)]
            if delta > 0:
                int_words[st] += 1
                delta -= 1
            elif int_words[st] > mins.get(st, dmin):
                int_words[st] -= 1
                delta += 1
            i += 1
            if i > 10000:
                break

    for s in slot_types:
        m = mins.get(s, dmin)
        if int_words[s] > m and proportional[s] < m - 1e-6:
            audit_min_overrides.append(
                {
                    "slot": s,
                    "reason": "minimum_enforced",
                    "floor": m,
                    "proportional_share": round(proportional[s], 2),
                }
            )
    return int_words


def _merge_alias_weights(weights: Dict[str, float]) -> Dict[str, float]:
    out = dict(weights)
    for raw, canon in _SECTION_ALIASES.items():
        w = out.get(raw, 0.0) + out.get(canon, 0.0)
        if w > 0:
            out[canon] = max(out.get(canon, 0.0), w)
        out.pop(raw, None)
    return out


def compile_beatmap(
    shaped_spine: ShapedSpine,
    topic_engines: Dict[str, Any],
    format_spec: Dict[str, Any],
    repo_root: Optional[Path] = None,
) -> Beatmap:
    root = repo_root or REPO_ROOT
    if shaped_spine.stage != "knob_apply":
        warnings.warn(f"Unexpected shaped spine stage {shaped_spine.stage!r}; expected 'knob_apply'", stacklevel=2)

    spine = load_spine(shaped_spine.topic, root)
    by_num = {c.number: c for c in spine.chapters}

    canonical_order = list(format_spec.get("canonical_slot_order") or [])
    if not canonical_order:
        canonical_order = load_format_spec(shaped_spine.runtime_format, root)["canonical_slot_order"]

    allowed_engines = list(topic_engines.get("allowed_engines") or [])
    default_engine = allowed_engines[0] if allowed_engines else None

    wmin, wmax = format_spec["word_range"]
    mid_total = (float(wmin) + float(wmax)) / 2.0

    chapters_out: List[BeatmapChapter] = []
    sections_included = 0
    sections_excluded: List[Dict[str, Any]] = []
    forbidden_hits: List[Dict[str, Any]] = []
    all_min_overrides: List[Dict[str, Any]] = []

    for ch in shaped_spine.chapters:
        orig = by_num.get(ch.number)
        if not orig:
            raise ValueError(f"Missing spine chapter {ch.number} for topic {shaped_spine.topic!r}")

        wmap = _merge_alias_weights(dict(ch.shaped_section_weights))
        required = [_normalize_slot(s) for s in orig.required_sections]
        forbidden = _forbidden_slot_types(orig.forbidden_moves)

        for mv in forbidden:
            forbidden_hits.append({"chapter": ch.number, "slot": mv, "source": "forbidden_moves"})

        ch_target = ch.target_word_count

        if shaped_spine.runtime_format in SOMATIC_FULL_RUNTIME_FORMATS:
            for r in required:
                rw = wmap.get(r, 0.0)
                if rw <= 0.0:
                    msg = (
                        f"required section {r} has zero weight for chapter {ch.number}; "
                        "KnobApply should have caught this — bumping to 0.3 for BeatmapCompile"
                    )
                    logger.warning(msg)
                    warnings.warn(msg, stacklevel=2)
                    wmap[r] = 0.3
                    all_min_overrides.append(
                        {
                            "chapter": ch.number,
                            "slot": r,
                            "reason": "required_section_zero_weight_recovery",
                            "weight_applied": 0.3,
                        }
                    )

            ordered = resolve_slot_definitions(ch, shaped_spine.runtime_format, orig)
            scaled = _scale_budget(SOMATIC_WORD_BUDGET, ch_target)
            tw_list = _reconcile_somatic_row_targets(
                ordered, SOMATIC_BUDGET_KEYS, scaled, ch_target
            )
            req_set = set(required)
            slots_somatic: List[BeatmapSlot] = []
            for j, st in enumerate(ordered):
                crit: Dict[str, Any] = {
                    "topic": shaped_spine.topic,
                    "persona": None,
                    "engine": default_engine,
                    "slot_type": st,
                    "emotional_temperature": ch.emotional_temperature,
                    "phase": ch.phase,
                    "chapter_role": ch.role,
                    "runtime_format": shaped_spine.runtime_format,
                }
                hooks = _enrichment_hooks_for_slot(ch.enrichment_priority, st)
                if st == "TEACHER_DOCTRINE" and "teacher_voice" not in hooks:
                    hooks = list(hooks)
                    hooks.append("teacher_voice")
                slots_somatic.append(
                    BeatmapSlot(
                        slot_type=st,
                        weight=_somatic_slot_weight(st, wmap),
                        target_words=tw_list[j],
                        somatic_section_index=int(SLOT_TO_SOMATIC_INDEX.get(j, j + 1)),
                        atom_selection_criteria=crit,
                        enrichment_hooks=hooks,
                        emotional_temperature=ch.emotional_temperature,
                        is_required=_somatic_slot_required(st, req_set),
                    )
                )
                sections_included += 1

            chapters_out.append(
                BeatmapChapter(
                    number=ch.number,
                    role=ch.role,
                    working_title=ch.working_title,
                    thesis=ch.thesis,
                    phase=ch.phase,
                    target_word_count=ch_target,
                    slots=slots_somatic,
                    slot_definitions=[s.slot_type for s in slots_somatic],
                )
            )
            continue

        # Step 1: candidate inclusion by weight > 0
        candidates: Set[str] = set()
        for sec, wt in wmap.items():
            if wt > 0.0:
                norm = _normalize_slot(sec)
                candidates.add(norm)

        for r in required:
            rw = wmap.get(r, 0.0)
            if rw <= 0.0:
                msg = (
                    f"required section {r} has zero weight for chapter {ch.number}; "
                    "KnobApply should have caught this — bumping to 0.3 for BeatmapCompile"
                )
                logger.warning(msg)
                warnings.warn(msg, stacklevel=2)
                wmap[r] = 0.3
                candidates.add(r)
                all_min_overrides.append(
                    {
                        "chapter": ch.number,
                        "slot": r,
                        "reason": "required_section_zero_weight_recovery",
                        "weight_applied": 0.3,
                    }
                )

        # Forbidden overrides weights
        for ban in forbidden:
            if ban in candidates:
                sections_excluded.append(
                    {
                        "chapter": ch.number,
                        "slot": ban,
                        "reason": "forbidden_moves",
                    }
                )
                candidates.discard(ban)
            if ban in required:
                # Spine contradiction; prefer forbidden for slot list but flag
                sections_excluded.append(
                    {
                        "chapter": ch.number,
                        "slot": ban,
                        "reason": "forbidden_moves_overrides_required",
                    }
                )
                candidates.discard(ban)

        # COMPRESSION: respect compression_allowed
        if "COMPRESSION" in candidates and not ch.compression_allowed:
            sections_excluded.append(
                {"chapter": ch.number, "slot": "COMPRESSION", "reason": "compression_not_allowed"}
            )
            candidates.discard("COMPRESSION")

        # Order slots
        ordered = [s for s in canonical_order if s in candidates]
        if not ordered:
            raise ValueError(f"No slots compiled for chapter {ch.number} (topic {shaped_spine.topic})")

        # Word allocation
        min_audit_chunk: List[Dict[str, Any]] = []
        word_by_slot = _allocate_words(ordered, wmap, ch_target, min_audit_chunk)
        all_min_overrides.extend([{**x, "chapter": ch.number} for x in min_audit_chunk])

        slots: List[BeatmapSlot] = []
        req_set = set(required)
        for j, st in enumerate(ordered):
            crit: Dict[str, Any] = {
                "topic": shaped_spine.topic,
                "persona": None,
                "engine": default_engine,
                "slot_type": st,
                "emotional_temperature": ch.emotional_temperature,
                "phase": ch.phase,
                "chapter_role": ch.role,
                "runtime_format": shaped_spine.runtime_format,
            }
            hooks = _enrichment_hooks_for_slot(ch.enrichment_priority, st)
            slots.append(
                BeatmapSlot(
                    slot_type=st,
                    weight=float(wmap.get(st, 0.0)),
                    target_words=word_by_slot[st],
                    somatic_section_index=min(j + 1, 10),
                    atom_selection_criteria=crit,
                    enrichment_hooks=hooks,
                    emotional_temperature=ch.emotional_temperature,
                    is_required=st in req_set,
                )
            )
            sections_included += 1

        chapters_out.append(
            BeatmapChapter(
                number=ch.number,
                role=ch.role,
                working_title=ch.working_title,
                thesis=ch.thesis,
                phase=ch.phase,
                target_word_count=ch_target,
                slots=slots,
                slot_definitions=[s.slot_type for s in slots],
            )
        )

    total_words = sum(c.target_word_count for c in chapters_out)
    if total_words < 0.9 * mid_total or total_words > 1.1 * mid_total:
        raise ValueError(
            f"Beatmap total words {total_words} outside ±10% of runtime midpoint {mid_total} "
            f"for format {shaped_spine.runtime_format!r}"
        )

    audit = {
        "sections_included_total": sections_included,
        "sections_excluded_total": len(sections_excluded),
        "sections_excluded": sections_excluded,
        "word_budget_total": total_words,
        "forbidden_moves_applied": forbidden_hits,
        "minimum_word_overrides": all_min_overrides,
        "runtime_word_midpoint": mid_total,
        "somatic_ten_slot_grid": shaped_spine.runtime_format in SOMATIC_FULL_RUNTIME_FORMATS,
    }

    return Beatmap(
        schema_version=1,
        stage="beatmap_compile",
        topic=shaped_spine.topic,
        family_id=shaped_spine.family_id,
        runtime_format=shaped_spine.runtime_format,
        total_target_words=total_words,
        chapters=chapters_out,
        compile_audit=audit,
    )


def beatmap_to_jsonable(bm: Beatmap) -> Dict[str, Any]:
    return {
        "schema_version": bm.schema_version,
        "stage": bm.stage,
        "topic": bm.topic,
        "family_id": bm.family_id,
        "runtime_format": bm.runtime_format,
        "total_target_words": bm.total_target_words,
        "chapters": [
            {
                **{k: getattr(ch, k) for k in ("number", "role", "working_title", "thesis", "phase", "target_word_count", "slot_definitions")},
                "slots": [asdict(s) for s in ch.slots],
            }
            for ch in bm.chapters
        ],
        "compile_audit": bm.compile_audit,
    }
