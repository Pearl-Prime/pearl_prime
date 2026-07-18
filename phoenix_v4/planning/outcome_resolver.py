"""
Combine exercise outcome tags, validate against thesis thresholds, prerequisites, redundancy.
"""
from __future__ import annotations

from typing import Dict, List, Mapping, Sequence, Tuple

from phoenix_v4.planning.exercise_registry_loader import ExerciseDefinition

_DIMS = ("awareness", "regulation", "integration")


def _exercise_scores(ex: ExerciseDefinition) -> Dict[str, float]:
    """Per-dimension delivery magnitudes for one exercise.

    Prefers explicit ``outcome_scores`` (authored per-dimension magnitudes). Falls
    back to the legacy equal-weight split over ``outcome_tags`` only when no
    explicit scores are present, preserving backward compatibility for any
    registry entry that has not been migrated.
    """
    explicit = getattr(ex, "outcome_scores", None) or {}
    if explicit:
        return {d: float(explicit.get(d, 0.0)) for d in _DIMS}
    tags = [t.lower() for t in ex.outcome_tags if t]
    if not tags:
        return {d: 0.0 for d in _DIMS}
    w = 1.0 / len(tags)
    return {d: (w if d in tags else 0.0) for d in _DIMS}


def resolve_combined_outcome(
    exercise_ids: Sequence[str],
    registry: Mapping[str, ExerciseDefinition],
) -> Dict[str, float]:
    """
    Merge each exercise's per-dimension delivery into combined scores in [0, 1].

    Dimensions combine with a saturating "probabilistic OR" ``1 - prod(1 - s)``:
    multiple exercises contributing to a dimension reinforce it without ever
    exceeding 1.0, and a single strong exercise is preserved at its own value
    (unlike the old equal-split, which structurally capped each dimension at 0.5
    and made the thesis thresholds unsatisfiable in 2-step journeys).
    """
    remaining: Dict[str, float] = {d: 1.0 for d in _DIMS}
    for eid in exercise_ids:
        ex = registry.get(str(eid).strip())
        if not ex:
            continue
        scores = _exercise_scores(ex)
        for d in _DIMS:
            s = max(0.0, min(1.0, scores.get(d, 0.0)))
            remaining[d] *= (1.0 - s)
    return {d: round(min(1.0, 1.0 - remaining[d]), 6) for d in _DIMS}


def validate_required_outcome(
    required: Mapping[str, float],
    actual: Mapping[str, float],
    *,
    epsilon: float = 1e-6,
) -> Tuple[bool, List[str]]:
    """Return (passed, violation messages) if actual[d] < required[d] for any dimension."""
    violations: List[str] = []
    for dim, need in required.items():
        if dim not in _DIMS:
            continue
        try:
            n = float(need)
        except (TypeError, ValueError):
            violations.append(f"{dim}: invalid_required_threshold")
            continue
        got = float(actual.get(dim, 0.0))
        if got + epsilon < n:
            violations.append(f"{dim}: need>={n:.3f} got={got:.3f}")
    return (not violations, violations)


def check_prerequisites(
    ordered_exercise_ids: Sequence[str],
    registry: Mapping[str, ExerciseDefinition],
) -> List[str]:
    """
    Each exercise's prerequisites must appear earlier in ordered_exercise_ids.
    Also enforces phase order: no regulation-tagged-only exercise before any awareness tag.
    """
    violations: List[str] = []
    seen = set()
    for eid in ordered_exercise_ids:
        eid = str(eid).strip()
        ex = registry.get(eid)
        if not ex:
            violations.append(f"missing_definition:{eid}")
            seen.add(eid)
            continue
        for pre in ex.prerequisites:
            pre = str(pre).strip()
            if pre and pre not in seen:
                violations.append(f"prerequisite_not_met:{eid} requires {pre} before it")
        seen.add(eid)

    # Sequence awareness → regulation → integration: first regulation-only exercise
    # must not appear before first awareness-tagged exercise.
    def _tags(eid: str) -> List[str]:
        ex = registry.get(eid)
        return [t.lower() for t in (ex.outcome_tags if ex else [])]

    first_aware_idx: int | None = None
    for i, eid in enumerate(ordered_exercise_ids):
        if "awareness" in _tags(str(eid).strip()):
            first_aware_idx = i
            break
    for i, eid in enumerate(ordered_exercise_ids):
        tags = set(_tags(str(eid).strip()))
        if "regulation" in tags and "awareness" not in tags:
            if first_aware_idx is None or i < first_aware_idx:
                violations.append(f"regulation_before_awareness:{eid}")
    return violations


def check_redundancy(
    exercise_ids: Sequence[str],
    registry: Mapping[str, ExerciseDefinition],
) -> List[str]:
    """Flag two breath-type exercises in the same journey."""
    types: List[str] = []
    for eid in exercise_ids:
        ex = registry.get(str(eid).strip())
        if ex and ex.type:
            types.append(ex.type.lower())
    breath_hits = [i for i, t in enumerate(types) if t == "breath"]
    if len(breath_hits) >= 2:
        return ["redundant_breath_exercises:" + ",".join(str(i) for i in breath_hits)]
    return []
