from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .candidate_generator import generate_candidates
from .recommendation_report import write_outputs
from .scoring_model import RecommenderGates, ScoringWeights, load_gates, load_scoring_weights, score_candidate


REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_recommender_config(repo_root: Path) -> tuple[ScoringWeights, RecommenderGates, dict[str, Any]]:
    import yaml

    config_dir = repo_root / "config" / "recommender"
    weights = yaml.safe_load((config_dir / "scoring_weights.yaml").read_text(encoding="utf-8")) or {}
    constraints = yaml.safe_load((config_dir / "constraints.yaml").read_text(encoding="utf-8")) or {}
    gates = yaml.safe_load((config_dir / "hard_gates.yaml").read_text(encoding="utf-8")) or {}
    merged_gates = {**constraints, **gates}
    return load_scoring_weights(weights), load_gates(merged_gates), merged_gates


def _select_ranked(
    scored: list[dict[str, Any]],
    gates: RecommenderGates,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    teacher_counts: dict[str, int] = {}
    topic_counts: dict[str, int] = {}
    persona_counts: dict[str, int] = {}

    for row in scored:
        if row["score"] < gates.min_score:
            continue
        teacher_id = row["teacher_id"]
        topic = row["topic"]
        persona = row["persona"]
        if teacher_counts.get(teacher_id, 0) >= gates.max_per_teacher:
            continue
        if topic_counts.get(topic, 0) >= gates.max_per_topic:
            continue
        if persona_counts.get(persona, 0) >= gates.max_per_persona:
            continue

        teacher_counts[teacher_id] = teacher_counts.get(teacher_id, 0) + 1
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
        persona_counts[persona] = persona_counts.get(persona, 0) + 1
        selected.append(row)
        if len(selected) >= gates.max_recommendations:
            break

    return selected


def build_ranked_recommendations(repo_root: Path = REPO_ROOT) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidates, inputs = generate_candidates(repo_root)
    weights, gates, gate_config = _load_recommender_config(repo_root)

    scored: list[dict[str, Any]] = []
    for candidate in candidates:
        score = score_candidate(candidate, weights)
        scored.append(
            {
                "teacher_id": candidate.teacher_id,
                "topic": candidate.topic,
                "persona": candidate.persona,
                "topic_score": candidate.topic_score,
                "persona_score": candidate.persona_score,
                "series_ids": list(candidate.series_ids),
                "series_summary": ", ".join(candidate.series_ids) if candidate.series_ids else "none",
                "score": score,
            }
        )

    scored.sort(
        key=lambda row: (
            -row["score"],
            -row["topic_score"],
            -row["persona_score"],
            row["teacher_id"],
            row["topic"],
            row["persona"],
        )
    )
    ranked = _select_ranked(scored, gates)
    inputs["gates"] = gate_config
    return ranked, inputs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build Phase 1 Phoenix Recommender artifacts")
    ap.add_argument("--out-dir", default=str(REPO_ROOT / "artifacts" / "recommendations"))
    args = ap.parse_args(argv)

    ranked, inputs = build_ranked_recommendations(REPO_ROOT)
    out_dir = Path(args.out_dir)
    json_path, md_path = write_outputs(out_dir, REPO_ROOT, ranked, inputs)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0
