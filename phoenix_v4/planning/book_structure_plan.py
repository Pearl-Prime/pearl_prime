"""Book-level deterministic planning contracts."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from phoenix_v4.planning.chapter_plan import ChapterPlan, PlanValidationError, validate_chapter_plan

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PLANS_ROOT = REPO_ROOT / "config" / "plans"
EI_V2_CONFIG = REPO_ROOT / "config" / "quality" / "ei_v2_config.yaml"
FORMAT_REGISTRY_PATH = REPO_ROOT / "config" / "format_selection" / "format_registry.yaml"


# Default chapter count when a runtime format is unknown to the registry.
# Post-AUTO-PLAN-SSOT-01-AMENDMENT (2026-05-06) backfill, every format the
# auto-plan path knows about has a registry entry; this fallback is a
# last-resort guard for runtime formats that are referenced before being
# declared.
_FORMAT_CHAPTER_COUNT_FALLBACK = 10


@lru_cache(maxsize=1)
def _load_format_registry() -> dict[str, Any]:
    """Read config/format_selection/format_registry.yaml once per process.

    Cached via lru_cache so the auto-plan hot path (called many times per
    pipeline run) doesn't re-parse the file. Tests that need to override
    can call _load_format_registry.cache_clear().
    """
    if yaml is None or not FORMAT_REGISTRY_PATH.exists():
        return {}
    try:
        return yaml.safe_load(FORMAT_REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def get_format_chapter_count(runtime_format: str) -> int:
    """Return chapter_count_default for `runtime_format` from the registry.

    Single source of truth per AUTO-PLAN-SSOT-01 + AUTO-PLAN-SSOT-01-AMENDMENT
    (`docs/PEARL_ARCHITECT_STATE.md`, 2026-05-06). Replaces the prior
    `FORMAT_CHAPTER_COUNTS` Python constant which had drifted from the
    registry on 16 of 20 formats. Falls back to
    `_FORMAT_CHAPTER_COUNT_FALLBACK` (10) only for formats the registry
    does not declare.
    """
    if not runtime_format:
        return _FORMAT_CHAPTER_COUNT_FALLBACK
    runtime_formats = _load_format_registry().get("runtime_formats") or {}
    spec = runtime_formats.get(runtime_format) or {}
    if isinstance(spec, dict):
        cc = spec.get("chapter_count_default")
        if isinstance(cc, int) and cc > 0:
            return cc
    return _FORMAT_CHAPTER_COUNT_FALLBACK

RUNTIME_ALIASES = {
    "standard_book": "deep_book_6h",
}

RUNTIME_TEMPLATES = {
    "short_book_30": {"tier": "short", "chapter_count": 6, "exercise_cap": 1},
    "standard_book": {"tier": "standard", "chapter_count": 12, "exercise_cap": 2},
    "deep_book_6h": {"tier": "standard", "chapter_count": 12, "exercise_cap": 2},
}


@dataclass(frozen=True)
class BookStructurePlan:
    plan_id: str
    persona_id: str
    topic_id: str
    teacher_id: str
    runtime_format_id: str
    engine_type: str
    chapter_count: int
    tier: str
    chapters: list[ChapterPlan]
    dominant_band_sequence: list[int]
    intensity_sequence: list[int]
    emotional_curve: list[int]
    cost_chapter_index: int
    reflection_strategy_rotation: list[str]
    motif: dict[str, Any]
    resolution_type: str
    word_budget_total: dict[str, Any]
    bestseller_structure_histogram: dict[str, int]
    teacher_anchor: dict[str, Any]
    arc_checkpoint_percent: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BookStructurePlan":
        root = data.get("book_structure_plan") if "book_structure_plan" in data else data
        if not isinstance(root, dict):
            raise PlanValidationError("book_structure_plan must be a mapping")
        values = dict(root)
        raw_chapters = values.get("chapters") or []
        values["chapters"] = [ChapterPlan.from_dict(ch) for ch in raw_chapters]
        values.setdefault("emotional_curve", values.get("intensity_sequence", []))
        values.setdefault("reflection_strategy_rotation", [])
        values.setdefault("motif", {})
        values.setdefault("word_budget_total", {})
        values.setdefault("bestseller_structure_histogram", {})
        values.setdefault("teacher_anchor", {})
        values.setdefault("arc_checkpoint_percent", {})
        missing = [name for name in cls.__dataclass_fields__ if name not in values]
        if missing:
            raise PlanValidationError(f"BookStructurePlan missing required fields: {', '.join(sorted(missing))}")
        return cls(**{name: values.get(name) for name in cls.__dataclass_fields__})


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanValidationError(message)


def get_runtime_template(runtime_id: str) -> dict[str, Any]:
    key = (runtime_id or "").strip()
    return dict(RUNTIME_TEMPLATES.get(key) or RUNTIME_TEMPLATES.get(RUNTIME_ALIASES.get(key, ""), {}))


def ensure_ei_v2_book_structure_enforcement(repo_root: Path = REPO_ROOT) -> None:
    """Persist the spec-required EI V2 book-structure enforcement switch."""
    if yaml is None:
        return
    path = repo_root / "config" / "quality" / "ei_v2_config.yaml"
    if not path.exists():
        return
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    block = data.setdefault("book_structure", {})
    if block.get("enforce_bestseller_beat_order") is True:
        return
    block["enforce_bestseller_beat_order"] = True
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def validate_book_arc(plan: BookStructurePlan) -> BookStructurePlan:
    _require(plan.chapter_count == len(plan.chapters), "chapter_count must match len(chapters)")
    _require(plan.chapter_count > 0, "book must have chapters")
    template = get_runtime_template(plan.runtime_format_id)
    if template:
        _require(plan.tier == template["tier"], f"runtime {plan.runtime_format_id} expects tier {template['tier']}")

    bands = [int(ch.band) for ch in plan.chapters]
    intensities = [int(ch.intensity) for ch in plan.chapters]
    _require(plan.dominant_band_sequence == bands, "dominant_band_sequence must match chapter bands")
    _require(plan.intensity_sequence == intensities, "intensity_sequence must match chapter intensities")
    for idx in range(1, len(bands)):
        _require(abs(bands[idx] - bands[idx - 1]) <= 2, "adjacent BAND step may not exceed 2")
    peak = max(bands)
    _require(bands[-1] < peak, "final chapter may not be the peak BAND")
    _require(0 <= int(plan.cost_chapter_index) < plan.chapter_count - 1, "cost_chapter_index must not be final")

    for idx in range(2, len(intensities)):
        window = intensities[idx - 2 : idx + 1]
        _require(window != [5, 5, 5], "macro cadence forbids three consecutive intensity 5 chapters")
    for idx, value in enumerate(intensities):
        if value >= 4:
            support_window = plan.chapters[idx + 1 : idx + 3]
            if support_window:
                _require(
                    any(ch.regulation_support in {"medium", "high"} for ch in support_window),
                    "intensity 4-5 must be followed by medium/high regulation within 2 chapters",
                )

    structures = [ch.bestseller_structure for ch in plan.chapters]
    for idx in range(2, len(structures)):
        _require(len(set(structures[idx - 2 : idx + 1])) > 1, "same bestseller_structure may not repeat 3 times")

    exercise_cap = int(template.get("exercise_cap", 99)) if template else 99
    for ch in plan.chapters:
        validate_chapter_plan(ch)
        exercises = sum(1 for slot in ch.slot_plans if str(slot.get("type") or slot.get("slot_type")).upper() == "EXERCISE")
        _require(exercises <= exercise_cap, "exercise slots exceed runtime cap")
    final = plan.chapters[-1]
    _require(bool(final.ending_contract), "final chapter requires ending_contract")
    return plan


def _emotional_job_for_chapter(ch_1indexed: int, total: int) -> str:
    """Phase-aware emotional job assignment (BSG-011 / ACT-011)."""
    pct = (ch_1indexed - 1) / max(total - 1, 1)
    if pct < 0.15:
        return "recognition"
    elif pct < 0.40:
        return "mechanism"
    elif pct < 0.55:
        return "deepening"
    elif pct < 0.70:
        return "reframe"
    elif pct < 0.88:
        return "practice"
    else:
        return "resolution"


def _band_for_chapter(ch_1indexed: int, total: int) -> int:
    """Smooth band arc: rises to peak at ~60%, resolves at end (peak-1).

    Rules enforced by validate_book_arc:
      - Adjacent bands may not differ by more than 2.
      - Final chapter band must be < peak.
    """
    pct = (ch_1indexed - 1) / max(total - 1, 1)
    if pct < 0.15:
        band = 1
    elif pct < 0.35:
        band = 2
    elif pct < 0.55:
        band = 3
    elif pct < 0.70:
        band = 4
    elif pct < 0.88:
        band = 3
    else:
        band = 2
    return band


def _intensity_for_chapter(ch_1indexed: int, total: int) -> int:
    """Smooth intensity arc: rises to 4 near the peak, no three 5s in a row."""
    pct = (ch_1indexed - 1) / max(total - 1, 1)
    if pct < 0.15:
        return 2
    elif pct < 0.35:
        return 3
    elif pct < 0.65:
        return 4
    elif pct < 0.88:
        return 3
    else:
        return 2


def _regulation_for_intensity(intensity: int) -> str:
    """Return regulation_support level appropriate for intensity."""
    if intensity >= 4:
        return "high"
    elif intensity == 3:
        return "medium"
    return "low"


# Canonical 7-engine map → chapter_thesis_bank.yaml engine columns.
# overwhelm/spiral/comparison now have their own baseline columns (no longer
# collapsed to "watcher"). somatic/cognitive aliases preserved for compat.
_ENGINE_TO_BANK_KEY: dict[str, str] = {
    "somatic": "watcher",
    "watcher": "watcher",
    "false": "false_alarm",
    "false_alarm": "false_alarm",
    "alarm": "false_alarm",
    "shame": "shame",
    "grief": "grief",
    "cognitive": "false_alarm",
    "overwhelm": "overwhelm",
    "spiral": "spiral",
    "comparison": "comparison",
}

# Map emotional_job → ALL of its chapter-intent facets. Listing every facet
# (not just 2) lets a 12-chapter book rotate across more distinct theses; the
# 2-cycle here was the within-book repetition source (audit Q1/D2).
JOB_TO_INTENT: dict[str, list[str]] = {
    "recognition": ["establish_mask", "expose_cost", "the_oldest_version"],
    "mechanism": ["destabilize_strategy", "reveal_hidden_belief", "what_you_protected"],
    "deepening": ["confrontation", "somatic_repair", "the_cost_named", "the_price_of_knowing"],
    "reframe": ["grounded_reframe", "embodied_identity", "the_body_after"],
    "practice": ["witness_without_fix", "moving_without_certainty"],
    "resolution": ["carrying_forward", "the_open_hand", "the_relational_truth"],
    "integration": ["the_new_self", "carrying_forward", "the_open_hand"],
}


def _bank_engine_key(engine_type: str) -> str:
    """Resolve an engine slug to its chapter_thesis_bank.yaml column.

    Matches the full slug first (e.g. "false_alarm", "overwhelm"), then the
    leading token (e.g. "somatic_first" → "somatic"). Unknown engines fall back
    to "watcher" only as a last resort for genuinely unrecognised slugs — the
    three previously-TBD canonical engines now resolve to their own columns.
    """
    key = (engine_type or "").lower().strip()
    if key in _ENGINE_TO_BANK_KEY:
        return _ENGINE_TO_BANK_KEY[key]
    head = key.split("_")[0]
    return _ENGINE_TO_BANK_KEY.get(head, "watcher")


def _get_thesis_from_bank(
    emotional_job: str,
    engine_type: str,
    chapter_number: int,
    topic_id: str,
    repo_root: Path,
) -> str:
    """Load chapter_thesis_bank.yaml and return the best-match thesis.

    Precedence: topics[topic_id][intent][engine] → intents[intent][engine].
    No silent watcher default — a missing engine yields an explicit
    topic/job descriptor so a book is never mislabelled as a watcher book.
    """
    bank_path = repo_root / "config" / "planning" / "chapter_thesis_bank.yaml"
    if yaml is None or not bank_path.exists():
        return (
            f"Understanding {emotional_job} is essential to resolving the core pattern "
            f"around {topic_id}."
        )
    data = yaml.safe_load(bank_path.read_text(encoding="utf-8")) or {}
    intents = data.get("intents") or {}
    topics = data.get("topics") or {}
    bank_engine = _bank_engine_key(engine_type)

    # Map emotional_job → chapter intent key. Each job lists ALL of its intent
    # facets so a 12-chapter book rotates across more theses than a 2-cycle
    # (within-book repetition is the JOB_TO_INTENT 2-cycle, per audit Q1/D2).
    candidates = JOB_TO_INTENT.get(emotional_job.lower(), ["establish_mask", "expose_cost"])
    intent_key = candidates[(chapter_number - 1) % len(candidates)]

    # Precedence: topic override → engine baseline. NO silent watcher default —
    # a missing engine returns an explicit descriptor so a book is never
    # mislabelled as a watcher book (audit Q1/D2).
    topic_block = ((topics.get(topic_id) or {}).get(intent_key)) or {}
    intent_block = intents.get(intent_key) or {}
    thesis = topic_block.get(bank_engine) or intent_block.get(bank_engine)
    if thesis:
        return thesis
    # Same engine, different facet within this job (still topic-aware).
    for alt_intent in candidates:
        alt_topic = ((topics.get(topic_id) or {}).get(alt_intent)) or {}
        alt_base = intents.get(alt_intent) or {}
        t = alt_topic.get(bank_engine) or alt_base.get(bank_engine)
        if t:
            return t
    # Explicit no-thesis signal (never a wrong-engine watcher line).
    return (
        f"This chapter addresses the {emotional_job} phase of transformation "
        f"around {topic_id} through the {bank_engine.replace('_', ' ')} pattern."
    )


def _build_slot_plans(
    persona_id: str,
    topic_id: str,
    runtime_format_id: str,
    teacher_id: str,
    emotional_job: str,
) -> tuple[list[str], list[dict[str, Any]]]:
    """Build a minimal valid slot_plans list covering all 5 ONTGP moves.

    validate_chapter_plan requires:
      - All 5 ONTGP moves present: orient, name, turn, give, pull
      - bestseller_beat_order == [s["type"] for s in slot_plans]
      - All slot types in VALID_SLOT_TYPES
      - persona_filter and topic_filter on every slot
    """
    # Standard 5-slot template covering all ONTGP moves
    slots: list[dict[str, Any]] = [
        {
            "type": "HOOK",
            "slot_type": "HOOK",
            "count": 1,
            "persona_filter": [persona_id],
            "topic_filter": [topic_id],
            "forbidden_tags": [],
            "ontgp_serves": ["orient"],
            "ei_v2_dimension_target": {},
            "runtime_format_id": runtime_format_id,
        },
        {
            "type": "SCENE",
            "slot_type": "SCENE",
            "count": 1,
            "persona_filter": [persona_id],
            "topic_filter": [topic_id],
            "forbidden_tags": [],
            "ontgp_serves": ["name"],
            "ei_v2_dimension_target": {},
            "runtime_format_id": runtime_format_id,
        },
        {
            "type": "STORY",
            "slot_type": "STORY",
            "count": 1,
            "persona_filter": [persona_id],
            "topic_filter": [topic_id],
            "forbidden_tags": [],
            "ontgp_serves": ["turn"],
            "ei_v2_dimension_target": {},
            "runtime_format_id": runtime_format_id,
        },
        {
            "type": "REFLECTION",
            "slot_type": "REFLECTION",
            "count": 1,
            "persona_filter": [persona_id],
            "topic_filter": [topic_id],
            "forbidden_tags": [],
            "ontgp_serves": ["give"],
            "ei_v2_dimension_target": {},
            "runtime_format_id": runtime_format_id,
        },
        {
            "type": "INTEGRATION",
            "slot_type": "INTEGRATION",
            "count": 1,
            "persona_filter": [persona_id],
            "topic_filter": [topic_id],
            "forbidden_tags": [],
            "ontgp_serves": ["pull"],
            "ei_v2_dimension_target": {},
            "runtime_format_id": runtime_format_id,
        },
    ]
    beat_order = [s["type"] for s in slots]
    return beat_order, slots


def _build_chapter_plan(
    idx: int,
    total: int,
    topic_id: str,
    persona_id: str,
    teacher_id: str,
    runtime_format_id: str,
    engine_type: str,
    bestseller_structure: str,
    repo_root: Path,
) -> ChapterPlan:
    """Build a single valid ChapterPlan for generate_book_plan."""
    ch_num = idx + 1
    emotional_job = _emotional_job_for_chapter(ch_num, total)
    band = _band_for_chapter(ch_num, total)
    intensity = _intensity_for_chapter(ch_num, total)
    regulation = _regulation_for_intensity(intensity)

    thesis = _get_thesis_from_bank(emotional_job, engine_type, ch_num, topic_id, repo_root)

    # intent maps to emotional job for readability
    INTENT_LABELS: dict[str, str] = {
        "recognition": "Name the pattern with precision",
        "mechanism": "Reveal the hidden mechanism",
        "deepening": "Deepen the exploration",
        "reframe": "Offer the reframe",
        "practice": "Build the practice",
        "resolution": "Land the resolution",
        "integration": "Integrate the arc",
    }
    chapter_intent = INTENT_LABELS.get(emotional_job, f"Chapter {ch_num} intent")

    beat_order, slot_plans = _build_slot_plans(
        persona_id, topic_id, runtime_format_id, teacher_id, emotional_job
    )

    is_final = idx == total - 1
    ending_contract: dict[str, Any] | None = None
    if is_final:
        ending_contract = {
            "type": "resolution",
            "closing_move": "open_hand",
            "thread_close": True,
        }

    # Band sequence for this chapter (single-chapter view)
    dominant_band_seq = [band]

    return ChapterPlan(
        chapter_index=idx,
        chapter_number=ch_num,
        title=f"Chapter {ch_num}: {chapter_intent}",
        runtime_format_id=runtime_format_id,
        persona_id=persona_id,
        topic_id=topic_id,
        teacher_id=teacher_id,
        engine_type=engine_type,
        chapter_intent=chapter_intent,
        chapter_thesis=thesis,
        thread_sentences=[],
        bestseller_structure=bestseller_structure,
        thread_type="quiet_orientation",
        band=band,
        emotional_role=emotional_job,
        emotional_temperature=emotional_job,
        dominant_band_sequence=dominant_band_seq,
        intensity=intensity,
        regulation_support=regulation,
        mechanism_depth_target=min(max(1, band - 1 + 1), 4),
        cost_intensity=intensity,
        identity_stage=ch_num,
        callback_ids=[],
        bestseller_beat_order=beat_order,
        slot_plans=slot_plans,
        word_budget={},
        tts_targets={},
        scene_plan={},
        safety_budget={},
        duration_fit={},
        frame_context={},
        ending_contract=ending_contract,
    )


def _fix_bestseller_repeats(structures: list[str]) -> list[str]:
    """Post-process structure list to eliminate any 3-in-a-row repeats.

    assign_bestseller_structures has a known edge case for some seed+count combos.
    We patch remaining repeats here by rotating to the next available structure.
    """
    from phoenix_v4.planning.chapter_plan import VALID_STRUCTURES

    all_structs = list(VALID_STRUCTURES)
    result = list(structures)
    # iterate until stable
    for _ in range(len(result)):
        changed = False
        for i in range(2, len(result)):
            window = result[i - 2 : i + 1]
            if len(set(window)) == 1:
                used_nearby = set(result[max(0, i - 2) : i + 1])
                for alt in all_structs:
                    if alt not in used_nearby:
                        result[i] = alt
                        changed = True
                        break
        if not changed:
            break
    return result


def generate_book_plan(
    topic_id: str,
    persona_id: str,
    runtime_format: str,
    engine_type: str,
    *,
    chapter_count: int | None = None,
    seed: str = "",
    teacher_id: str = "default_teacher",
    repo_root: Path = REPO_ROOT,
) -> "BookStructurePlan":
    """Auto-generate a valid BookStructurePlan from topic + persona + format + engine.

    Used when no pre-authored plan YAML exists for the combination.
    The generated plan follows all phase rules and produces a structure
    that passes validate_book_arc().

    ACT-011 / BSG-011.
    """
    from phoenix_v4.planning.chapter_planner import assign_bestseller_structures

    n_chapters = chapter_count or get_format_chapter_count(runtime_format)
    selector_key = seed or f"{topic_id}:{persona_id}:{runtime_format}"
    structures = assign_bestseller_structures(n_chapters, selector_key)

    # Normalize bestseller_structure names: "letter" → "the_letter" to match VALID_STRUCTURES
    STRUCTURE_NORMALIZE: dict[str, str] = {
        "letter": "the_letter",
    }
    structures = [STRUCTURE_NORMALIZE.get(s, s) for s in structures]
    # Fix any 3-in-a-row repeats from assign_bestseller_structures edge cases
    structures = _fix_bestseller_repeats(structures)

    chapters: list[ChapterPlan] = []
    for idx in range(n_chapters):
        ch = _build_chapter_plan(
            idx=idx,
            total=n_chapters,
            topic_id=topic_id,
            persona_id=persona_id,
            teacher_id=teacher_id,
            runtime_format_id=runtime_format,
            engine_type=engine_type,
            bestseller_structure=structures[idx],
            repo_root=repo_root,
        )
        chapters.append(ch)

    bands = [ch.band for ch in chapters]
    intensities = [ch.intensity for ch in chapters]

    # cost_chapter_index: chapter with highest intensity, not the final
    cost_idx = 0
    peak_intensity = 0
    for i, ch in enumerate(chapters[:-1]):  # exclude final
        if ch.intensity > peak_intensity:
            peak_intensity = ch.intensity
            cost_idx = i

    # Determine tier from runtime_format
    template = get_runtime_template(runtime_format)
    tier = template.get("tier", "standard") if template else "standard"

    # Bestseller structure histogram
    histogram: dict[str, int] = {}
    for ch in chapters:
        histogram[ch.bestseller_structure] = histogram.get(ch.bestseller_structure, 0) + 1

    plan = BookStructurePlan(
        plan_id=f"generated_{topic_id}_{persona_id}_{runtime_format}",
        topic_id=topic_id,
        persona_id=persona_id,
        teacher_id=teacher_id,
        runtime_format_id=runtime_format,
        engine_type=engine_type,
        chapter_count=n_chapters,
        tier=tier,
        chapters=chapters,
        dominant_band_sequence=bands,
        intensity_sequence=intensities,
        emotional_curve=intensities,
        cost_chapter_index=cost_idx,
        reflection_strategy_rotation=[],
        motif={},
        resolution_type="open_hand",
        word_budget_total={},
        bestseller_structure_histogram=histogram,
        teacher_anchor={},
        arc_checkpoint_percent={},
    )
    # Validate — raises PlanValidationError on failure
    validate_book_arc(plan)
    return plan


def _candidate_plan_paths(topic_id: str, persona_id: str, runtime_format_id: str, repo_root: Path) -> list[Path]:
    runtime = (runtime_format_id or "").strip()
    suffixes = [runtime]
    alias = RUNTIME_ALIASES.get(runtime)
    if alias:
        suffixes.append(alias)
    if runtime in {"short_book_30", "micro_book_15", "micro_book_20"}:
        suffixes.append("1h")
    if runtime in {"standard_book", "deep_book_6h", "extended_book_2h", "deep_book_4h"}:
        suffixes.append("6h")
    seen: set[str] = set()
    paths: list[Path] = []
    for suffix in suffixes:
        if not suffix or suffix in seen:
            continue
        seen.add(suffix)
        paths.append(repo_root / "config" / "plans" / f"{topic_id}_{persona_id}_{suffix}.yaml")
    return paths


def load_book_structure_plan(
    topic_id: str,
    persona_id: str,
    runtime_format_id: str,
    repo_root: Path = REPO_ROOT,
) -> BookStructurePlan:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load BookStructurePlan")
    ensure_ei_v2_book_structure_enforcement(repo_root)
    for path in _candidate_plan_paths(topic_id, persona_id, runtime_format_id, repo_root):
        if path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            plan = BookStructurePlan.from_dict(data)
            return validate_book_arc(plan)
    candidates = ", ".join(str(p) for p in _candidate_plan_paths(topic_id, persona_id, runtime_format_id, repo_root))
    raise FileNotFoundError(
        f"No deterministic BookStructurePlan for topic={topic_id!r}, persona={persona_id!r}, "
        f"runtime={runtime_format_id!r}. Expected one of: {candidates}"
    )
