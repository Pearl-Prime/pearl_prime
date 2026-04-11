"""
Plan multi-phase exercise journeys aligned with chapter thesis and runtime profile.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from phoenix_v4.planning.exercise_registry_loader import ExerciseDefinition
from phoenix_v4.planning.outcome_resolver import (
    check_prerequisites,
    check_redundancy,
    resolve_combined_outcome,
    validate_required_outcome,
)
from phoenix_v4.planning.registry_resolver import _deterministic_index

# Deterministic thesis rotation per topic (chapter index picks slot).
TOPIC_THESIS_ROTATION: Dict[str, List[str]] = {
    "anxiety": ["anxiety_spike", "emotional_overwhelm", "unnamed_feeling"],
    "grief": ["emotional_overwhelm", "nothing_worked_yet", "unnamed_feeling"],
    "burnout": ["burnout_pattern", "emotional_overwhelm", "nothing_worked_yet"],
}

DEFAULT_THESIS_CYCLE = [
    "anxiety_spike",
    "unnamed_feeling",
    "nothing_worked_yet",
    "emotional_overwhelm",
    "burnout_pattern",
    "neck_up_problem",
]

AWARENESS_POOL = ("body_scan_v1", "sensation_tracking_v1")
REGULATION_POOL = ("extended_exhale_v2", "breath_anchor_v1")
INTEGRATION_POOL = ("sensation_hold_v1", "grounding_anchor_v1")

JOURNEY_INTROS = {
    "awareness": "First, we're going to help your body notice what it's been holding.",
    "regulation": "Now that you can feel it, we're going to help your system soften.",
    "integration": "Now we're going to let this settle into something you can carry.",
}


@dataclass
class JourneyPhase:
    name: str
    target_section: int
    exercise_id: str
    intro: str


@dataclass
class ExerciseJourney:
    journey_type: str
    phases: List[JourneyPhase]
    expected_outcome: Dict[str, float]
    aligned_with_thesis: str
    template_id: str
    outcome_ok: bool
    outcome_violations: List[str] = field(default_factory=list)
    prerequisite_violations: List[str] = field(default_factory=list)
    redundancy_warnings: List[str] = field(default_factory=list)


def resolve_thesis_id(topic_id: str, chapter_index: int, seed: str) -> str:
    """Stable thesis_outcome_map key for this chapter."""
    topic = (topic_id or "").strip().lower()
    pool = TOPIC_THESIS_ROTATION.get(topic, DEFAULT_THESIS_CYCLE)
    idx = _deterministic_index(f"{seed}:thesis:{topic}:ch{chapter_index}", len(pool))
    return pool[idx]


def _runtime_to_steps(runtime_profile: str) -> int:
    r = (runtime_profile or "").strip().lower()
    if r in ("short_book", "1_step", "short"):
        return 1
    if r in ("deep_book_6h", "3_step", "deep_book", "deep"):
        return 3
    return 2


def _pick_from_pool(
    pool: Sequence[str],
    phase: str,
    seed: str,
    chapter_index: int,
) -> str:
    idx = _deterministic_index(f"{seed}:journey:{phase}:ch{chapter_index}", len(pool))
    return pool[idx]


def _fix_prerequisite_pair(
    awareness_id: str,
    regulation_id: str,
) -> Tuple[str, str]:
    """Ensure breath_anchor / sensation_hold prerequisites when possible."""
    reg = regulation_id
    if reg == "breath_anchor_v1" and awareness_id != "sensation_tracking_v1":
        reg = "extended_exhale_v2"
    return awareness_id, reg


def _fix_integration_prereq(awareness_id: str, integration_id: str) -> str:
    if integration_id == "sensation_hold_v1" and awareness_id != "sensation_tracking_v1":
        return "grounding_anchor_v1"
    return integration_id


def _select_template_id(templates: Mapping[str, Any], seed: str, chapter_index: int) -> str:
    keys = sorted(templates.keys())
    if not keys:
        return "classic_somatic_entry"
    idx = _deterministic_index(f"{seed}:template:ch{chapter_index}", len(keys))
    return keys[idx]


def _sections_for_steps(steps: int, template_phases: Mapping[str, Any]) -> Dict[str, int]:
    """Map phase name -> target section using template when available."""
    out: Dict[str, int] = {}
    order = ["awareness", "regulation", "integration"]
    for name in order[:steps]:
        block = template_phases.get(name) if isinstance(template_phases, dict) else None
        if isinstance(block, dict) and block.get("target_section") is not None:
            try:
                out[name] = int(block["target_section"])
                continue
            except (TypeError, ValueError):
                pass
        # Fallback 4 / 8 / 10
        defaults = {"awareness": 4, "regulation": 8, "integration": 10}
        out[name] = defaults[name]
    return out


def plan_exercise_journey(
    chapter_index: int,
    thesis_id: str,
    runtime_profile: str,
    *,
    seed: str = "journey",
    exercise_registry: Mapping[str, ExerciseDefinition],
    thesis_outcomes: Mapping[str, Dict[str, float]],
    journey_templates: Optional[Mapping[str, Any]] = None,
) -> ExerciseJourney:
    """
    Build a 1-, 2-, or 3-phase journey (sections 4 / 4+8 / 4+8+10) with deterministic variety.
    """
    journey_templates = journey_templates or {}
    steps = _runtime_to_steps(runtime_profile)
    tpl_key = _select_template_id(journey_templates, seed, chapter_index)
    tpl_root = journey_templates.get(tpl_key) or {}
    phase_tpl = tpl_root.get("phases") if isinstance(tpl_root, dict) else {}
    if not isinstance(phase_tpl, dict):
        phase_tpl = {}
    section_by_phase = _sections_for_steps(steps, phase_tpl)

    phases: List[JourneyPhase] = []
    exercise_ids: List[str] = []

    aw = _pick_from_pool(AWARENESS_POOL, "awareness", seed, chapter_index)
    reg = _pick_from_pool(REGULATION_POOL, "regulation", seed, chapter_index)
    aw, reg = _fix_prerequisite_pair(aw, reg)
    inte = _pick_from_pool(INTEGRATION_POOL, "integration", seed, chapter_index)
    inte = _fix_integration_prereq(aw, inte)

    if steps >= 1:
        sec = section_by_phase["awareness"]
        phases.append(
            JourneyPhase(
                name="awareness",
                target_section=sec,
                exercise_id=aw,
                intro=JOURNEY_INTROS["awareness"],
            )
        )
        exercise_ids.append(aw)
    if steps >= 2:
        sec = section_by_phase["regulation"]
        phases.append(
            JourneyPhase(
                name="regulation",
                target_section=sec,
                exercise_id=reg,
                intro=JOURNEY_INTROS["regulation"],
            )
        )
        exercise_ids.append(reg)
    if steps >= 3:
        sec = section_by_phase["integration"]
        phases.append(
            JourneyPhase(
                name="integration",
                target_section=sec,
                exercise_id=inte,
                intro=JOURNEY_INTROS["integration"],
            )
        )
        exercise_ids.append(inte)

    expected = resolve_combined_outcome(exercise_ids, exercise_registry)
    required = dict(thesis_outcomes.get(thesis_id, {}))
    outcome_ok, outcome_violations = validate_required_outcome(required, expected)
    pre_violations = check_prerequisites(exercise_ids, exercise_registry)
    red_warnings = check_redundancy(exercise_ids, exercise_registry)

    jt = f"{steps}_step"
    return ExerciseJourney(
        journey_type=jt,
        phases=phases,
        expected_outcome=expected,
        aligned_with_thesis=thesis_id,
        template_id=tpl_key,
        outcome_ok=outcome_ok,
        outcome_violations=outcome_violations,
        prerequisite_violations=pre_violations,
        redundancy_warnings=red_warnings,
    )
