from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Candidate:
    teacher_id: str
    topic: str
    persona: str
    topic_score: float
    persona_score: float
    series_ids: tuple[str, ...]


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def _score_lookup(score_rows: dict[str, Any], key: str, field: str) -> dict[str, float]:
    section = score_rows.get(key) or {}
    values = section.get(field) or {}
    return {str(k): float(v) for k, v in values.items()}


def load_inputs(repo_root: Path) -> dict[str, Any]:
    catalog_dir = repo_root / "config" / "catalog_planning"
    recommender_dir = repo_root / "config" / "recommender"

    topics = list((_load_yaml(catalog_dir / "canonical_topics.yaml").get("topics") or []))
    personas = list((_load_yaml(catalog_dir / "canonical_personas.yaml").get("personas") or []))
    teacher_scores = _load_yaml(catalog_dir / "teacher_topic_persona_scores.yaml")
    series_templates = _load_yaml(catalog_dir / "series_templates.yaml").get("series") or {}
    topic_mapping = _load_yaml(recommender_dir / "topic_mapping.yaml").get("topic_series_map") or {}

    return {
        "topics": [str(topic) for topic in topics],
        "personas": [str(persona) for persona in personas],
        "teachers": sorted((teacher_scores.get("teachers") or {}).keys()),
        "default_score": float(teacher_scores.get("default_score", 0.5)),
        "teacher_scores": teacher_scores.get("teachers") or {},
        "series_templates": series_templates,
        "topic_mapping": topic_mapping,
    }


def _series_ids_for_topic(
    topic: str,
    topic_mapping: dict[str, Any],
    series_templates: dict[str, Any],
) -> tuple[str, ...]:
    mapped = topic_mapping.get(topic) or {}
    series_ids = mapped.get("series_ids") or mapped.get("series") or []
    filtered = [series_id for series_id in series_ids if series_id in series_templates]
    return tuple(filtered)


def generate_candidates(repo_root: Path) -> tuple[list[Candidate], dict[str, Any]]:
    inputs = load_inputs(repo_root)
    teacher_scores = inputs["teacher_scores"]
    default_score = inputs["default_score"]
    topic_mapping = inputs["topic_mapping"]
    series_templates = inputs["series_templates"]

    candidates: list[Candidate] = []
    for teacher_id in inputs["teachers"]:
        topic_scores = _score_lookup(teacher_scores, teacher_id, "topic_scores")
        persona_scores = _score_lookup(teacher_scores, teacher_id, "persona_scores")
        for topic in inputs["topics"]:
            topic_score = topic_scores.get(topic, default_score)
            series_ids = _series_ids_for_topic(topic, topic_mapping, series_templates)
            for persona in inputs["personas"]:
                persona_score = persona_scores.get(persona, default_score)
                candidates.append(
                    Candidate(
                        teacher_id=str(teacher_id),
                        topic=topic,
                        persona=persona,
                        topic_score=float(topic_score),
                        persona_score=float(persona_score),
                        series_ids=series_ids,
                    )
                )

    return candidates, inputs
