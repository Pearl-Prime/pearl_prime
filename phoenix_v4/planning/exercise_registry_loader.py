"""
Load canonical exercise YAML registries for journey planning (read-only configs).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from phoenix_v4.planning.registry_resolver import _load_yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class ExerciseDefinition:
    exercise_id: str
    type: str
    phase_fit: List[str]
    section_fit: List[int]
    effects: List[str]
    intensity: str
    prerequisites: List[str]
    compatible_with: List[str]
    outcome_tags: List[str]


def _as_str_list(val: Any) -> List[str]:
    if val is None:
        return []
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    return [str(val).strip()] if str(val).strip() else []


def _as_int_list(val: Any) -> List[int]:
    out: List[int] = []
    if val is None:
        return out
    if isinstance(val, list):
        for x in val:
            try:
                out.append(int(x))
            except (TypeError, ValueError):
                continue
    return out


def load_exercise_registry(
    path: Optional[Path] = None,
    repo_root: Optional[Path] = None,
) -> Dict[str, ExerciseDefinition]:
    root = repo_root or REPO_ROOT
    p = path or (root / "config" / "exercises" / "exercise_metadata_registry.yaml")
    if not p.exists():
        return {}
    data = _load_yaml(p) or {}
    exercises = data.get("exercises") or {}
    if not isinstance(exercises, dict):
        return {}
    out: Dict[str, ExerciseDefinition] = {}
    for eid, raw in exercises.items():
        if not isinstance(raw, dict):
            continue
        eid_s = str(eid).strip()
        if not eid_s:
            continue
        out[eid_s] = ExerciseDefinition(
            exercise_id=eid_s,
            type=str(raw.get("type") or "").strip(),
            phase_fit=_as_str_list(raw.get("phase_fit")),
            section_fit=_as_int_list(raw.get("section_fit")),
            effects=_as_str_list(raw.get("effects")),
            intensity=str(raw.get("intensity") or "").strip(),
            prerequisites=_as_str_list(raw.get("prerequisites")),
            compatible_with=_as_str_list(raw.get("compatible_with")),
            outcome_tags=_as_str_list(raw.get("outcome_tags")),
        )
    return out


def load_thesis_outcome_map(
    path: Optional[Path] = None,
    repo_root: Optional[Path] = None,
) -> Dict[str, Dict[str, float]]:
    root = repo_root or REPO_ROOT
    p = path or (root / "config" / "exercises" / "thesis_outcome_map.yaml")
    if not p.exists():
        return {}
    data = _load_yaml(p) or {}
    raw_map = data.get("thesis_outcomes") or {}
    if not isinstance(raw_map, dict):
        return {}
    out: Dict[str, Dict[str, float]] = {}
    for tid, dims in raw_map.items():
        if not isinstance(dims, dict):
            continue
        tkey = str(tid).strip()
        row: Dict[str, float] = {}
        for k in ("awareness", "regulation", "integration"):
            v = dims.get(k)
            if v is None:
                continue
            try:
                row[k] = float(v)
            except (TypeError, ValueError):
                continue
        if row:
            out[tkey] = row
    return out


def load_journey_templates(
    path: Optional[Path] = None,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    root = repo_root or REPO_ROOT
    p = path or (root / "config" / "exercises" / "journey_templates.yaml")
    if not p.exists():
        return {}
    data = _load_yaml(p) or {}
    templates = data.get("journey_templates") or {}
    if not isinstance(templates, dict):
        return {}
    return dict(templates)
