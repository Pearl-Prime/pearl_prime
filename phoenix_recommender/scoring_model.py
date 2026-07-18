from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .candidate_generator import Candidate


@dataclass(frozen=True)
class ScoringWeights:
    topic_weight: float = 0.55
    persona_weight: float = 0.35
    series_bonus_weight: float = 0.03
    strong_fit_bonus: float = 0.05
    strong_fit_threshold: float = 0.7


@dataclass(frozen=True)
class RecommenderGates:
    min_score: float = 0.58
    max_recommendations: int = 25
    max_per_teacher: int = 8
    max_per_topic: int = 6
    max_per_persona: int = 6


def load_scoring_weights(raw: dict[str, Any]) -> ScoringWeights:
    return ScoringWeights(
        topic_weight=float(raw.get("topic_weight", 0.55)),
        persona_weight=float(raw.get("persona_weight", 0.35)),
        series_bonus_weight=float(raw.get("series_bonus_weight", 0.03)),
        strong_fit_bonus=float(raw.get("strong_fit_bonus", 0.05)),
        strong_fit_threshold=float(raw.get("strong_fit_threshold", 0.7)),
    )


def load_gates(raw: dict[str, Any]) -> RecommenderGates:
    return RecommenderGates(
        min_score=float(raw.get("min_score", 0.58)),
        max_recommendations=int(raw.get("max_recommendations", 25)),
        max_per_teacher=int(raw.get("max_per_teacher", 8)),
        max_per_topic=int(raw.get("max_per_topic", 6)),
        max_per_persona=int(raw.get("max_per_persona", 6)),
    )


def score_candidate(candidate: Candidate, weights: ScoringWeights) -> float:
    base = (candidate.topic_score * weights.topic_weight) + (candidate.persona_score * weights.persona_weight)
    score = base + (min(len(candidate.series_ids), 3) * weights.series_bonus_weight)
    if candidate.topic_score >= weights.strong_fit_threshold and candidate.persona_score >= weights.strong_fit_threshold:
        score += weights.strong_fit_bonus
    return round(min(score, 1.0), 4)
