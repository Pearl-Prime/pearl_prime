"""
Combine exercise outcome tags, validate against thesis thresholds, prerequisites, redundancy.
"""
from __future__ import annotations

from typing import Dict, List, Mapping, Sequence, Tuple

from phoenix_v4.planning.exercise_registry_loader import ExerciseDefinition

_DIMS = ("awareness", "regulation", "integration")


def resolve_combined_outcome(
    exercise_ids: Sequence[str],
    registry: Mapping[str, ExerciseDefinition],
) -> Dict[str, float]:
    """
    Merge outcome_tags from each exercise into dimensional scores in [0, 1].

    Each exercise splits weight 1.0 across its outcome_tags; contributions sum per
    dimension and are capped at 1.0.
    """
    acc: Dict[str, float] = {d: 0.0 for d in _DIMS}
    for eid in exercise_ids:
        ex = registry.get(str(eid).strip())
        if not ex:
            continue
        tags = [t.lower() for t in ex.outcome_tags if t]
        if not tags:
            continue
        w = 1.0 / len(tags)
        for t in tags:
            if t in acc:
                acc[t] += w
    return {d: min(1.0, acc[d]) for d in _DIMS}


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
