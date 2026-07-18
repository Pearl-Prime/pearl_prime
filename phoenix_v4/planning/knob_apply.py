"""
Knob Apply stage — shapes a SelectedSpine using a KnobProfile (standalone module).

Authority: docs/KNOB_APPLY_STAGE_CONTRACT.md (merge priority and immutables).

Loaders search, in order:
  1) {repo_root}/config/spines|knobs
  2) {repo_root}/tests/fixtures/knob_apply
"""
from __future__ import annotations

import hashlib
import re
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

FIXTURES_ROOT = REPO_ROOT / "tests" / "fixtures" / "knob_apply"

_SCALE_EXERCISE = ["none", "low", "medium", "high"]
_SCALE_STORY = ["low", "medium", "high"]
_SCALE_MECHANISM = ["none", "light", "medium", "high"]
_SCALE_REFLECTION = ["light", "medium", "high"]
_SCALE_PACING = ["slow", "measured", "fast"]
_SCALE_TEMP = ["clinical", "neutral", "warm"]
_SCALE_SPIRITUALITY = ["secular", "secular_to_moderate", "moderate", "high"]
_SCALE_COMPRESSION = ["none", "light", "moderate", "heavy"]
_SCALE_PRACTICAL = ["contemplative", "contemplative_first", "balanced", "practical"]

_SCALES: Dict[str, List[str]] = {
    "exercise_density": _SCALE_EXERCISE,
    "story_density": _SCALE_STORY,
    "mechanism_depth": _SCALE_MECHANISM,
    "reflection_depth": _SCALE_REFLECTION,
    "pacing_profile": _SCALE_PACING,
    "emotional_temperature": _SCALE_TEMP,
    "spirituality_level": _SCALE_SPIRITUALITY,
    "compression": _SCALE_COMPRESSION,
    "practical_vs_contemplative": _SCALE_PRACTICAL,
}

_DENSITY_WEIGHT = {
    "none": 0.0,
    "low": 0.3,
    "medium": 0.6,
    "high": 0.9,
    "very_high": 1.0,
    "light": 0.45,
}


def _rank(scale: List[str], value: Optional[str]) -> int:
    if value is None or value not in scale:
        return -1
    return scale.index(value)


def _clamp_knob(
    name: str,
    value: Optional[str],
    floor_val: Optional[str],
    ceiling_val: Optional[str],
) -> Tuple[Optional[str], bool, bool]:
    scale = _SCALES.get(name)
    if scale is None:
        return value, False, False
    if value is None:
        if floor_val and floor_val in scale:
            return floor_val, True, False
        return value, False, False
    v = value
    floor_hit = ceiling_hit = False
    if floor_val and floor_val in scale:
        if _rank(scale, v) < _rank(scale, floor_val):
            v = floor_val
            floor_hit = True
    if ceiling_val and ceiling_val in scale:
        if _rank(scale, v) > _rank(scale, ceiling_val):
            v = ceiling_val
            ceiling_hit = True
    return v, floor_hit, ceiling_hit


def _merge_knob_dict(base: Dict[str, str], overlay: Optional[Dict[str, str]]) -> None:
    if not overlay:
        return
    for k, v in overlay.items():
        if v is not None and v != "":
            base[str(k)] = str(v)


def _yaml_phase_and_display(topic: str, chapter_num: int) -> Tuple[str, str]:
    if topic == "burnout":
        if chapter_num <= 4:
            return "early", "early_book"
        if chapter_num <= 9:
            return "mid", "mid_book"
        return "late", "late_book"
    if chapter_num <= 4:
        return "early", "early_book"
    if chapter_num <= 8:
        return "mid", "mid_book"
    return "late", "late_book"


def _spine_blocks_exercise(topic: str, chapter_num: int) -> bool:
    if topic == "anxiety":
        return chapter_num < 5
    if topic == "grief":
        return chapter_num < 9
    if topic == "burnout":
        return chapter_num < 10
    if topic == "financial_stress":
        return chapter_num <= 7
    return False


def _resolve_path(repo_root: Path, candidates: List[Path]) -> Path:
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(f"No file found in candidates: {candidates}")


def _load_yaml(path: Path) -> Any:
    if yaml is None:
        raise RuntimeError("PyYAML is required for knob_apply loaders")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@dataclass
class SpineChapter:
    number: int
    role: str
    working_title: str
    thesis: str
    emotional_job: str
    practical_job: str
    what_changes: str
    required_sections: List[str]
    forbidden_moves: List[str]
    recommended_enrichments: List[str]


@dataclass
class SelectedSpine:
    schema_version: int
    topic: str
    family_id: str
    primary_mechanism: str
    allowed_engines: List[str]
    reader_starting_state: str
    reader_ending_state: str
    chapters: List[SpineChapter]
    sequencing_rules: Dict[str, Any]
    tone_and_pacing: Dict[str, Any]


@dataclass
class KnobProfile:
    topic: str
    source: str
    knob_defaults: Dict[str, str]
    hard_floors: Dict[str, str]
    hard_ceilings: Dict[str, str]
    phase_overrides: Dict[str, Dict[str, str]]
    dangerous_combinations: List[Dict[str, Any]]
    persona_overrides: Optional[Dict[str, str]]
    platform_overrides: Optional[Dict[str, str]]


@dataclass
class ShapedChapter:
    number: int
    role: str
    working_title: str
    thesis: str
    emotional_job: str
    practical_job: str
    shaped_section_weights: Dict[str, float]
    emotional_temperature: str
    pacing: str
    target_word_count: int
    phase: str
    compression_allowed: bool
    enrichment_priority: List[str]
    knob_snapshot: Dict[str, str] = field(default_factory=dict)


@dataclass
class KnobAudit:
    knobs_applied: Dict[str, str]
    floors_enforced: List[Dict[str, Any]]
    ceilings_enforced: List[Dict[str, Any]]
    dangerous_combos_checked: List[Dict[str, Any]]
    dangerous_combos_resolved: List[Dict[str, Any]]
    platform_conflicts_resolved: List[Dict[str, Any]]


@dataclass
class ShapedSpine:
    schema_version: int
    stage: str
    topic: str
    family_id: str
    runtime_format: str
    chapters: List[ShapedChapter]
    knob_audit: KnobAudit


def _load_compact_chapter_subset(runtime_format: str, repo_root: Path) -> Optional[List[int]]:
    """Read `compact_chapter_subset` from format_registry.yaml for a runtime format.

    Returns the 1-based original-spine indices to keep, or None if the format
    declares no subset (i.e., uses the full spine). Used by load_spine to
    compress the topic spine for compact runtime formats per PR-G design
    (P1 — format-spec-declared subset patterns).
    """
    if not runtime_format:
        return None
    registry_path = repo_root / "config" / "format_selection" / "format_registry.yaml"
    if not registry_path.exists() or yaml is None:
        return None
    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return None
    formats = data.get("runtime_formats") or data.get("formats") or {}
    spec = formats.get(runtime_format) or {}
    subset = spec.get("compact_chapter_subset")
    if not isinstance(subset, list):
        return None
    return [int(n) for n in subset if isinstance(n, (int, float))]


def load_spine(
    topic: str,
    repo_root: Optional[Path] = None,
    runtime_format: Optional[str] = None,
) -> SelectedSpine:
    """Load a topic spine, optionally compressed for a compact runtime format.

    For compact runtime formats (declared via `compact_chapter_subset` in
    config/format_selection/format_registry.yaml), the returned spine contains
    only the subsetted chapters, **renumbered 1..N**. The renumbering is
    intentional: downstream code (e.g., enrichment_select._chapter_phase,
    story_planner.DEFAULT_PHASE_CHAPTERS) computes phase boundaries assuming
    contiguous 1..N chapter numbering. Original chapter numbers are preserved
    in the format spec's `compact_chapter_subset` field for traceability.

    For non-compact formats (or when runtime_format is None / lacks a subset
    declaration), behavior is unchanged: full topic spine, original numbers.

    Args:
        topic: topic id (e.g., "anxiety")
        repo_root: repo root path (default REPO_ROOT)
        runtime_format: runtime format id (e.g., "compact_book_8ch_30min").
            When this format declares `compact_chapter_subset`, the spine is
            compressed accordingly.
    """
    root = repo_root or REPO_ROOT
    path = _resolve_path(
        root,
        [
            root / "config" / "spines" / f"{topic}_spine.yaml",
            FIXTURES_ROOT / "spines" / f"{topic}_spine.yaml",
        ],
    )
    data = _load_yaml(path)
    chapters_raw = data.get("chapters") or {}
    chap_list: List[SpineChapter] = []
    for _key, ch in sorted(chapters_raw.items(), key=lambda kv: kv[1].get("number", 0)):
        if not isinstance(ch, dict):
            continue
        wt = ch.get("working_title") or ch.get("title") or ""
        wc = ch.get("what_changes")
        if isinstance(wc, dict):
            wc_str = "\n".join(f"{k}: {v}" for k, v in wc.items())
        else:
            wc_str = str(wc or "")
        chap_list.append(
            SpineChapter(
                number=int(ch["number"]),
                role=str(ch.get("role") or ""),
                working_title=str(wt),
                thesis=str(ch.get("thesis") or ""),
                emotional_job=str(ch.get("emotional_job") or ""),
                practical_job=str(ch.get("practical_job") or ""),
                what_changes=wc_str,
                required_sections=[str(s) for s in (ch.get("required_sections") or [])],
                forbidden_moves=[str(s) for s in (ch.get("forbidden_moves") or [])],
                recommended_enrichments=[str(s) for s in (ch.get("recommended_enrichments") or [])],
            )
        )
    chap_list.sort(key=lambda c: c.number)

    # Apply compact-format chapter subset if declared (PR-G).
    subset = _load_compact_chapter_subset(runtime_format or "", root)
    if subset:
        original_by_number = {c.number: c for c in chap_list}
        kept: List[SpineChapter] = []
        for new_idx, orig_num in enumerate(subset, start=1):
            orig = original_by_number.get(int(orig_num))
            if not orig:
                # Subset declares an index that doesn't exist in the spine — skip.
                # This should never happen if format_registry is correct; surfaced
                # via test_compact_subset_validates_indices.
                continue
            # Rebuild the chapter with renumbered position. Field order matches
            # SpineChapter dataclass definition (number first).
            kept.append(
                SpineChapter(
                    number=new_idx,
                    role=orig.role,
                    working_title=orig.working_title,
                    thesis=orig.thesis,
                    emotional_job=orig.emotional_job,
                    practical_job=orig.practical_job,
                    what_changes=orig.what_changes,
                    required_sections=list(orig.required_sections),
                    forbidden_moves=list(orig.forbidden_moves),
                    recommended_enrichments=list(orig.recommended_enrichments),
                )
            )
        if not kept:
            raise ValueError(
                f"compact_chapter_subset for {runtime_format!r} produced empty spine; "
                f"check that subset indices exist in {topic}_spine.yaml"
            )
        chap_list = kept

    seq = data.get("sequencing_rules") or {}
    seq = seq if isinstance(seq, dict) else {}
    tone = data.get("tone_and_pacing") or {}
    tone = tone if isinstance(tone, dict) else {}
    return SelectedSpine(
        schema_version=1,
        topic=topic,
        family_id=str(data.get("family_id") or topic),
        primary_mechanism=str(data.get("primary_mechanism") or ""),
        allowed_engines=[str(e) for e in (data.get("allowed_engines") or [])],
        reader_starting_state=str(data.get("reader_starting_state") or ""),
        reader_ending_state=str(data.get("reader_ending_state") or ""),
        chapters=chap_list,
        sequencing_rules=seq,
        tone_and_pacing=tone,
    )


def load_knob_profile(topic: str, repo_root: Optional[Path] = None) -> KnobProfile:
    root = repo_root or REPO_ROOT
    path = _resolve_path(
        root,
        [
            root / "config" / "knobs" / "topic_knob_profiles.yaml",
            FIXTURES_ROOT / "topic_knob_profiles.yaml",
        ],
    )
    data = _load_yaml(path)
    topics = data.get("topics") or {}
    if topic not in topics:
        raise KeyError(f"Unknown topic {topic!r} in topic_knob_profiles.yaml")
    t = topics[topic]
    phase_raw = t.get("phase_overrides") or {}
    phase: Dict[str, Dict[str, str]] = {}
    if isinstance(phase_raw, dict):
        for pk, pv in phase_raw.items():
            if isinstance(pv, dict):
                phase[str(pk)] = {str(k): str(v) for k, v in pv.items()}
    dangerous = list(t.get("dangerous_combinations") or [])
    try:
        src_rel = str(path.relative_to(root))
    except ValueError:
        src_rel = str(path)
    return KnobProfile(
        topic=topic,
        source=src_rel,
        knob_defaults={str(k): str(v) for k, v in (t.get("knob_defaults") or {}).items()},
        hard_floors={str(k): str(v) for k, v in (t.get("hard_floors") or {}).items()},
        hard_ceilings={str(k): str(v) for k, v in (t.get("hard_ceilings") or {}).items()},
        phase_overrides=phase,
        dangerous_combinations=dangerous,
        persona_overrides=None,
        platform_overrides=None,
    )


def load_runtime_format(format_id: str, repo_root: Optional[Path] = None) -> Dict[str, Any]:
    root = repo_root or REPO_ROOT
    path = root / "config" / "format_selection" / "format_registry.yaml"
    data = _load_yaml(path)
    rt = (data.get("runtime_formats") or {}).get(format_id)
    if not isinstance(rt, dict):
        raise KeyError(f"Unknown runtime format {format_id!r}")
    return dict(rt)


def _knob_tags(state: Dict[str, str]) -> List[str]:
    tags: List[str] = []
    ex = state.get("exercise_density")
    if ex:
        tags.append(f"exercise_density_{ex}")
    if state.get("emotional_temperature") == "clinical":
        tags.append("emotional_temperature_clinical")
    md = state.get("mechanism_depth")
    if md == "high":
        tags.append("mechanism_depth_high")
    rd = state.get("reflection_depth")
    if rd == "high":
        tags.append("reflection_depth_high")
    comp = state.get("compression")
    if comp == "heavy":
        tags.append("compression_heavy")
    if comp == "light":
        tags.append("compression_light")
    if comp == "moderate":
        tags.append("compression_moderate")
    if state.get("story_density") == "low":
        tags.append("story_density_low")
    if state.get("spirituality_level") == "high":
        tags.append("spirituality_level_high")
    if state.get("spirituality_level") in (None, "", "none"):
        tags.append("spirituality_level_none")
    if state.get("pacing_profile") == "fast":
        tags.append("pacing_profile_fast")
    ns = state.get("narrative_structure")
    if ns:
        tags.append(f"narrative_structure_{ns}")
    pvc = state.get("practical_vs_contemplative")
    if pvc == "practical":
        tags.append("practical_vs_contemplative_practical")
    if state.get("exercise_density") == "medium":
        tags.append("exercise_density_medium")
    return tags


def _chapter_in_range(chapter_num: int, spec: str) -> bool:
    s = spec.strip().lower().replace(" ", "")
    if s == "all":
        return True
    m = re.match(r"ch(\d+)-(\d+)", s)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return a <= chapter_num <= b
    m = re.match(r"ch(\d+)", s)
    if m:
        return chapter_num == int(m.group(1))
    return False


def _combo_tags_applicable(knob_tags: List[str], declared: List[str], chapter_num: int) -> bool:
    needed = [t for t in declared if not t.startswith("chapter_range_")]
    if not needed:
        return False
    return all(t in knob_tags for t in needed)


def _reduce_aggressive_for_resolution(
    state: Dict[str, str],
    matched_decl: List[str],
    floors: Dict[str, str],
) -> Optional[Tuple[str, str, str]]:
    priority = [
        "exercise_density",
        "emotional_temperature",
        "mechanism_depth",
        "reflection_depth",
        "compression",
        "pacing_profile",
        "spirituality_level",
        "practical_vs_contemplative",
    ]
    for knob in priority:
        scale = _SCALES.get(knob)
        if not scale:
            continue
        if not any(tg.startswith(f"{knob}_") for tg in matched_decl):
            continue
        cur = state.get(knob)
        if cur is None or cur not in scale:
            continue
        fl = floors.get(knob)
        if fl and fl in scale:
            target_idx = _rank(scale, fl)
        else:
            target_idx = max(0, _rank(scale, cur) - 1)
        new_val = scale[target_idx] if target_idx >= 0 else scale[0]
        if new_val != cur:
            return knob, cur, new_val
    return None


def _density_weight(val: Optional[str]) -> float:
    if val is None:
        return 0.6
    return float(_DENSITY_WEIGHT.get(val, 0.6))


def _build_section_weights(state: Dict[str, str], required: List[str]) -> Dict[str, float]:
    story_w = _density_weight(state.get("story_density"))
    ref_w = _density_weight(state.get("reflection_depth"))
    ex_w = _density_weight(state.get("exercise_density"))
    mech_w = _density_weight(state.get("mechanism_depth"))
    weights: Dict[str, float] = {}
    for t in (
        "HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION",
        "COMPRESSION", "PIVOT", "TAKEAWAY", "THREAD", "PERMISSION", "SOMATIC_INVENTORY",
    ):
        weights[t] = 0.0
    weights["HOOK"] = 1.0
    weights["INTEGRATION"] = 0.5
    for sec in required:
        u = sec.upper()
        if u == "HOOK":
            weights[u] = 1.0
        elif u in ("SCENE", "STORY"):
            weights[u] = story_w
        elif u == "REFLECTION":
            weights[u] = ref_w
        elif u == "EXERCISE":
            weights[u] = ex_w
        elif u == "INTEGRATION":
            weights[u] = max(0.5, _density_weight(state.get("exercise_density")) * 0.5 + 0.25)
        elif u == "COMPRESSION":
            weights[u] = mech_w
        elif u == "SOMATIC_INVENTORY":
            weights[u] = max(mech_w, story_w * 0.8)
        else:
            weights[u] = max(0.3, story_w * 0.5)
    if state.get("exercise_density") == "none":
        weights["EXERCISE"] = 0.0
    return weights


def _enrichment_slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    return s[:48] or "enrichment"


def _enrichment_priority(rec_lines: List[str]) -> List[str]:
    out: List[str] = []
    for line in rec_lines:
        sl = _enrichment_slug(line[:80])
        if sl not in out:
            out.append(sl)
    return out[:12]


def _platform_narrative_conflict(
    platform_id: Optional[str],
    narrative_structure: str,
    repo_root: Path,
    audit: List[Dict[str, Any]],
) -> None:
    if not platform_id:
        return
    try:
        path = repo_root / "config" / "catalog_planning" / "platform_knob_tuning.yaml"
        data = _load_yaml(path)
        prof = (data.get("platform_profiles") or {}).get(platform_id)
        if not prof:
            return
        preferred = prof.get("preferred_structures") or []
        if not preferred:
            return
        if narrative_structure and narrative_structure not in preferred:
            audit.append(
                {
                    "platform_id": platform_id,
                    "issue": "narrative_structure not in platform preferred_structures",
                    "preferred": list(preferred),
                    "selected": narrative_structure,
                    "resolution": "knob_profile_narrative_structure_retained",
                }
            )
    except Exception:
        return


def apply_knobs(
    spine: SelectedSpine,
    knob_profile: KnobProfile,
    runtime_format: str = "standard_book",
    persona_id: Optional[str] = None,
    platform_id: Optional[str] = None,
    repo_root: Optional[Path] = None,
) -> ShapedSpine:
    root = repo_root or REPO_ROOT
    format_spec = load_runtime_format(runtime_format, root)
    w0, w1 = format_spec["word_range"]
    total_target = (float(w0) + float(w1)) / 2.0
    chapter_count = len(spine.chapters)
    if chapter_count == 0:
        raise ValueError("Spine has no chapters")
    per_chapter = int(round(total_target / chapter_count))

    floors_audit: List[Dict[str, Any]] = []
    ceilings_audit: List[Dict[str, Any]] = []
    combo_checked: List[Dict[str, Any]] = []
    combo_resolved: List[Dict[str, Any]] = []
    platform_audit: List[Dict[str, Any]] = []

    topic = spine.topic
    shaped_chapters: List[ShapedChapter] = []

    for ch in spine.chapters:
        display_ph, yaml_ph = _yaml_phase_and_display(topic, ch.number)
        state: Dict[str, str] = deepcopy(knob_profile.knob_defaults)
        phase_ov = knob_profile.phase_overrides.get(yaml_ph) or {}
        _merge_knob_dict(state, phase_ov)
        _merge_knob_dict(state, knob_profile.persona_overrides)
        _merge_knob_dict(state, knob_profile.platform_overrides)

        if _spine_blocks_exercise(topic, ch.number):
            if state.get("exercise_density") not in ("none",):
                combo_resolved.append(
                    {
                        "chapter": ch.number,
                        "reason": "spine_sequencing_exercise_blocked",
                        "before": state.get("exercise_density"),
                        "after": "none",
                    }
                )
            state["exercise_density"] = "none"

        if topic == "anxiety" and ch.number <= 2:
            scale = _SCALE_MECHANISM
            if state.get("mechanism_depth") in scale and _rank(scale, state["mechanism_depth"]) > _rank(
                scale, "light"
            ):
                before = state["mechanism_depth"]
                state["mechanism_depth"] = "light"
                combo_resolved.append(
                    {
                        "chapter": ch.number,
                        "reason": "spine_forbidden_moves_mechanism_cap_early",
                        "before": before,
                        "after": "light",
                    }
                )

        for knob_name, floor_v in knob_profile.hard_floors.items():
            before = state.get(knob_name)
            nv, fh, _ = _clamp_knob(knob_name, before, floor_v, None)
            if fh and nv != before:
                state[knob_name] = nv  # type: ignore
                floors_audit.append(
                    {
                        "chapter": ch.number,
                        "knob": knob_name,
                        "floor": floor_v,
                        "before": before,
                        "after": nv,
                    }
                )
            elif nv != before and nv is not None:
                state[knob_name] = nv

        for knob_name, ceil_v in knob_profile.hard_ceilings.items():
            before = state.get(knob_name)
            nv, _, chit = _clamp_knob(knob_name, before, None, ceil_v)
            if chit and nv != before:
                state[knob_name] = nv  # type: ignore
                ceilings_audit.append(
                    {
                        "chapter": ch.number,
                        "knob": knob_name,
                        "ceiling": ceil_v,
                        "before": before,
                        "after": nv,
                    }
                )
            elif nv != before and nv is not None:
                state[knob_name] = nv

        if _spine_blocks_exercise(topic, ch.number):
            state["exercise_density"] = "none"

        tags = _knob_tags(state)
        for idx, combo in enumerate(knob_profile.dangerous_combinations):
            cr = str(combo.get("chapter_range") or "all")
            if not _chapter_in_range(ch.number, cr):
                combo_checked.append(
                    {
                        "chapter": ch.number,
                        "rule_index": idx,
                        "matched": False,
                        "pattern": combo.get("knobs"),
                        "chapter_range": cr,
                        "resolution": None,
                        "still_matched_after_resolution": False,
                    }
                )
                continue
            decl = [str(x) for x in (combo.get("knobs") or [])]
            decl_clean = [t for t in decl if not t.startswith("chapter_range_")]
            initial_matched = _combo_tags_applicable(tags, decl_clean, ch.number)
            resolutions: List[str] = []
            if initial_matched:
                guard = 0
                while _combo_tags_applicable(_knob_tags(state), decl_clean, ch.number) and guard < 8:
                    redux = _reduce_aggressive_for_resolution(state, decl_clean, knob_profile.hard_floors)
                    if redux:
                        k0, before, after = redux
                        state[k0] = after
                        resolutions.append(f"{k0}:{before}→{after}")
                        combo_resolved.append(
                            {
                                "chapter": ch.number,
                                "rule_index": idx,
                                "knob": k0,
                                "before": before,
                                "after": after,
                            }
                        )
                    elif (
                        "emotional_temperature_clinical" in decl_clean
                        and state.get("emotional_temperature") == "clinical"
                    ):
                        before = state["emotional_temperature"]
                        after = knob_profile.hard_floors.get("emotional_temperature", "warm")
                        state["emotional_temperature"] = after
                        resolutions.append(f"emotional_temperature:{before}→{after}")
                        combo_resolved.append(
                            {
                                "chapter": ch.number,
                                "rule_index": idx,
                                "knob": "emotional_temperature",
                                "before": before,
                                "after": after,
                            }
                        )
                    else:
                        break
                    guard += 1
            final_matched = _combo_tags_applicable(_knob_tags(state), decl_clean, ch.number)
            combo_checked.append(
                {
                    "chapter": ch.number,
                    "rule_index": idx,
                    "matched": initial_matched,
                    "still_matched_after_resolution": final_matched,
                    "pattern": decl,
                    "chapter_range": cr,
                    "resolution": ";".join(resolutions) if resolutions else None,
                }
            )
            tags = _knob_tags(state)

        weights = _build_section_weights(state, ch.required_sections)
        if state.get("exercise_density") == "none":
            weights["EXERCISE"] = 0.0

        cv = (state.get("compression") or "none").strip()
        comp_allowed = cv not in ("", "none")

        shaped_chapters.append(
            ShapedChapter(
                number=ch.number,
                role=ch.role,
                working_title=ch.working_title,
                thesis=ch.thesis,
                emotional_job=ch.emotional_job,
                practical_job=ch.practical_job,
                shaped_section_weights=weights,
                emotional_temperature=state.get("emotional_temperature") or "warm",
                pacing=state.get("pacing_profile") or "measured",
                target_word_count=per_chapter,
                phase=display_ph,
                compression_allowed=comp_allowed,
                enrichment_priority=_enrichment_priority(ch.recommended_enrichments),
                knob_snapshot=dict(state),
            )
        )

    _platform_narrative_conflict(
        platform_id,
        knob_profile.knob_defaults.get("narrative_structure", ""),
        root,
        platform_audit,
    )

    audit = KnobAudit(
        knobs_applied={
            "topic": topic,
            "runtime_format": runtime_format,
            "persona_id": persona_id or "",
            "platform_id": platform_id or "",
            "total_word_target": str(int(total_target)),
        },
        floors_enforced=floors_audit,
        ceilings_enforced=ceilings_audit,
        dangerous_combos_checked=combo_checked,
        dangerous_combos_resolved=combo_resolved,
        platform_conflicts_resolved=platform_audit,
    )

    shaped = ShapedSpine(
        schema_version=1,
        stage="knob_apply",
        topic=topic,
        family_id=spine.family_id,
        runtime_format=runtime_format,
        chapters=shaped_chapters,
        knob_audit=audit,
    )
    violations = validate_shaped_spine(shaped, spine, knob_profile)
    if violations:
        raise ValueError("ShapedSpine validation failed:\n" + "\n".join(violations))
    return shaped


def validate_shaped_spine(
    shaped: ShapedSpine,
    original_spine: SelectedSpine,
    knob_profile: KnobProfile,
) -> List[str]:
    violations: List[str] = []
    if len(shaped.chapters) != len(original_spine.chapters):
        violations.append("chapter_count_mismatch")
    oc = {c.number: c for c in original_spine.chapters}
    for ch in shaped.chapters:
        o = oc.get(ch.number)
        if not o:
            violations.append(f"missing_original_chapter_{ch.number}")
            continue
        if ch.thesis != o.thesis:
            violations.append(f"thesis_mutated_ch{ch.number}")
        if ch.role != o.role:
            violations.append(f"role_mutated_ch{ch.number}")
        if ch.working_title != o.working_title:
            violations.append(f"working_title_mutated_ch{ch.number}")
        if not ch.phase:
            violations.append(f"empty_phase_ch{ch.number}")
        for _k, w in ch.shaped_section_weights.items():
            if w < 0 or w > 1.0:
                violations.append(f"weight_out_of_range_ch{ch.number}_{_k}")
        for sec in o.required_sections:
            u = sec.upper()
            wgt = ch.shaped_section_weights.get(u, 0.0)
            if wgt <= 0.0:
                violations.append(f"required_section_zeroed_ch{ch.number}_{u}")

        snap = ch.knob_snapshot
        for knob, floor_v in knob_profile.hard_floors.items():
            scale = _SCALES.get(knob)
            cur = snap.get(knob)
            if scale and cur and floor_v in scale and _rank(scale, cur) < _rank(scale, floor_v):
                violations.append(f"floor_violation_ch{ch.number}_{knob}")
        for knob, ceil_v in knob_profile.hard_ceilings.items():
            scale = _SCALES.get(knob)
            cur = snap.get(knob)
            if scale and cur and ceil_v in scale and _rank(scale, cur) > _rank(scale, ceil_v):
                violations.append(f"ceiling_violation_ch{ch.number}_{knob}")

    for row in shaped.knob_audit.dangerous_combos_checked:
        if row.get("matched") and row.get("still_matched_after_resolution"):
            violations.append(
                f"dangerous_combo_unresolved_ch{row.get('chapter')}_rule{row.get('rule_index')}"
            )

    wmin, wmax = load_runtime_format(shaped.runtime_format)["word_range"]
    total = sum(c.target_word_count for c in shaped.chapters)
    mid = (wmin + wmax) / 2
    if total < 0.9 * mid or total > 1.1 * mid:
        violations.append(f"word_count_out_of_range_total_{total}_expected_{mid}")

    order_new = [c.number for c in shaped.chapters]
    order_old = [c.number for c in original_spine.chapters]
    if order_new != order_old:
        violations.append("chapter_order_changed")

    return violations


def shaped_spine_to_jsonable(shaped: ShapedSpine) -> Dict[str, Any]:
    return {
        "schema_version": shaped.schema_version,
        "stage": shaped.stage,
        "topic": shaped.topic,
        "family_id": shaped.family_id,
        "runtime_format": shaped.runtime_format,
        "chapters": [asdict(c) for c in shaped.chapters],
        "knob_audit": asdict(shaped.knob_audit),
    }


def spine_content_sha256(topic: str, repo_root: Optional[Path] = None) -> str:
    root = repo_root or REPO_ROOT
    path = _resolve_path(
        root,
        [
            root / "config" / "spines" / f"{topic}_spine.yaml",
            FIXTURES_ROOT / "spines" / f"{topic}_spine.yaml",
        ],
    )
    return hashlib.sha256(path.read_bytes()).hexdigest()



