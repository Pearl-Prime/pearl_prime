"""Chapter-level deterministic book planning primitives."""
from __future__ import annotations

from dataclasses import MISSING, dataclass
from typing import Any


VALID_SLOT_TYPES = {
    "HOOK",
    "SCENE",
    "STORY",
    "PIVOT",
    "REFLECTION",
    "EXERCISE",
    "TAKEAWAY",
    "INTEGRATION",
    "THREAD",
    "PERMISSION",
    "TEACHER_DOCTRINE",
}

VALID_STRUCTURES = {
    "promise_engine",
    "gladwell_spiral",
    "van_der_kolk",
    "atomic",
    "brene_brown",
    "myth_killer",
    "case_file",
    "permission_slip",
    "zoom_lens",
    "contrast_engine",
    "ancestor",
    "the_letter",
}

VALID_THREAD_TYPES = {
    "quiet_orientation",
    "sharp_question",
    "unresolved_tension",
    "micro_action_prompt",
    "vulnerability_prompt",
    "release_statement",
    "proof_in_motion",
    "both_micro_macro",
    "gentle_unresolved",
    "before_after_bridge",
    "lineage_thread",
    "contrast_carries",
}

VALID_ONTGP_MOVES = {"orient", "name", "turn", "give", "pull"}
STEALTH_TERMS = {"miracle", "cure", "guaranteed", "diagnose", "dsm", "clinical_dsm"}


class PlanValidationError(ValueError):
    """Raised when a deterministic book plan violates a hard contract."""


@dataclass(frozen=True)
class ChapterPlan:
    chapter_index: int
    chapter_number: int
    title: str
    runtime_format_id: str
    persona_id: str
    topic_id: str
    teacher_id: str
    engine_type: str
    chapter_intent: str
    chapter_thesis: str
    thread_sentences: list[str]
    bestseller_structure: str
    thread_type: str
    band: int
    emotional_role: str
    emotional_temperature: str
    dominant_band_sequence: list[int]
    intensity: int
    regulation_support: str
    mechanism_depth_target: int
    cost_intensity: int
    identity_stage: int
    callback_ids: list[str]
    bestseller_beat_order: list[str]
    slot_plans: list[dict[str, Any]]
    word_budget: dict[str, Any]
    tts_targets: dict[str, Any]
    scene_plan: dict[str, Any]
    safety_budget: dict[str, Any]
    duration_fit: dict[str, Any]
    frame_context: dict[str, Any]
    ending_contract: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChapterPlan":
        required = {
            f.name
            for f in cls.__dataclass_fields__.values()
            if f.default is MISSING and f.default_factory is MISSING
        }
        values = dict(data)
        values.setdefault("chapter_number", int(values.get("chapter_index", 0)) + 1)
        values.setdefault("thread_sentences", [])
        values.setdefault("dominant_band_sequence", [])
        values.setdefault("callback_ids", [])
        values.setdefault("bestseller_beat_order", [])
        values.setdefault("slot_plans", [])
        values.setdefault("word_budget", {})
        values.setdefault("tts_targets", {})
        values.setdefault("scene_plan", {})
        values.setdefault("safety_budget", {})
        values.setdefault("duration_fit", {})
        values.setdefault("frame_context", {})
        values.setdefault("ending_contract", None)
        missing = [name for name in required if name not in values]
        if missing:
            raise PlanValidationError(f"ChapterPlan missing required fields: {', '.join(sorted(missing))}")
        return cls(**{name: values.get(name) for name in cls.__dataclass_fields__})


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanValidationError(message)


def validate_chapter_plan(plan: ChapterPlan) -> ChapterPlan:
    _require(plan.chapter_index >= 0, "chapter_index must be >= 0")
    _require(plan.chapter_number == plan.chapter_index + 1, "chapter_number must equal chapter_index + 1")
    _require(bool(plan.title.strip()), "title is required")
    _require(bool(plan.persona_id.strip()), "persona_id is required")
    _require(bool(plan.topic_id.strip()), "topic_id is required")
    _require(bool(plan.chapter_intent.strip()), "chapter_intent is required")
    _require(bool(plan.chapter_thesis.strip()), "chapter_thesis is required")
    _require(plan.bestseller_structure in VALID_STRUCTURES, f"unknown bestseller_structure: {plan.bestseller_structure}")
    _require(plan.thread_type in VALID_THREAD_TYPES, f"unknown thread_type: {plan.thread_type}")
    _require(1 <= int(plan.band) <= 5, "band must be 1..5")
    _require(1 <= int(plan.intensity) <= 5, "intensity must be 1..5")
    _require(1 <= int(plan.mechanism_depth_target) <= 4, "mechanism_depth_target must be 1..4")
    _require(plan.slot_plans, "slot_plans are required")

    beat_order = [str(x).upper() for x in plan.bestseller_beat_order]
    slot_types = [str(s.get("type") or s.get("slot_type") or "").upper() for s in plan.slot_plans]
    _require(all(st in VALID_SLOT_TYPES for st in slot_types), "slot_plans contain unknown slot type")
    _require(beat_order == slot_types, "bestseller_beat_order must match slot_plans type order")

    moves: set[str] = set()
    forbidden: set[str] = set()
    for slot in plan.slot_plans:
        slot_moves = {str(m).strip().lower() for m in slot.get("ontgp_serves") or []}
        _require(slot_moves <= VALID_ONTGP_MOVES, "slot_plans contain unknown ONTGP move")
        moves.update(slot_moves)
        forbidden.update(str(t).strip().lower() for t in slot.get("forbidden_tags") or [])
        _require(slot.get("persona_filter") not in (None, []), "slot persona_filter is required")
        _require(slot.get("topic_filter") not in (None, []), "slot topic_filter is required")
    _require(moves == VALID_ONTGP_MOVES, "every chapter must cover all five ONTGP moves")
    _require(not (forbidden & STEALTH_TERMS - {"clinical_dsm"}), "stealth or miracle terms are forbidden in slot tags")

    cap = plan.scene_plan.get("scene_anchor_cap")
    if cap is not None:
        _require(int(cap) >= 1, "scene_anchor_cap must be >= 1")
    return plan


def render_atom_slot_spec(plan: ChapterPlan) -> list[dict[str, Any]]:
    """Return the authoritative atom selection spec for a chapter."""
    validate_chapter_plan(plan)
    rendered: list[dict[str, Any]] = []
    for slot in plan.slot_plans:
        item = dict(slot)
        item["type"] = str(item.get("type") or item.get("slot_type")).upper()
        item.setdefault("slot_type", item["type"])
        item.setdefault("count", 1)
        item.setdefault("persona_filter", [plan.persona_id])
        item.setdefault("topic_filter", [plan.topic_id])
        item.setdefault("forbidden_tags", [])
        item.setdefault("ontgp_serves", [])
        item.setdefault("ei_v2_dimension_target", {})
        item.setdefault("runtime_format_id", plan.runtime_format_id)
        item.setdefault("chapter_index", plan.chapter_index)
        item.setdefault("chapter_thesis", plan.chapter_thesis)
        rendered.append(item)
    return rendered
