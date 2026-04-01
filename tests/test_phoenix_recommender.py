from __future__ import annotations

import json
from pathlib import Path

from phoenix_recommender.candidate_generator import Candidate
from phoenix_recommender.cli import build_ranked_recommendations, main
from phoenix_recommender.scoring_model import ScoringWeights, score_candidate


def test_score_candidate_rewards_stronger_fit() -> None:
    strong = Candidate(
        teacher_id="ahjan",
        topic="anxiety",
        persona="gen_z_professionals",
        topic_score=0.9,
        persona_score=0.85,
        series_ids=("social_anxiety_arc", "panic_response_arc"),
    )
    weak = Candidate(
        teacher_id="maat",
        topic="burnout",
        persona="working_parents",
        topic_score=0.5,
        persona_score=0.5,
        series_ids=(),
    )

    weights = ScoringWeights()
    assert score_candidate(strong, weights) > score_candidate(weak, weights)


def test_cli_writes_ranked_and_summary(tmp_path: Path) -> None:
    out_dir = tmp_path / "recommendations"

    exit_code = main(["--out-dir", str(out_dir)])
    assert exit_code == 0

    ranked_path = out_dir / "ranked.json"
    summary_path = out_dir / "summary.md"
    assert ranked_path.exists()
    assert summary_path.exists()

    data = json.loads(ranked_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["counts"]["selected"] > 0
    assert data["recommendations"]
    scores = [row["score"] for row in data["recommendations"]]
    assert scores == sorted(scores, reverse=True)
    assert any("teacher_id" in row for row in data["recommendations"])


def test_build_ranked_recommendations_returns_expected_shape() -> None:
    ranked, inputs = build_ranked_recommendations()
    assert ranked
    assert inputs["topics"]
    assert inputs["personas"]
    assert inputs["teachers"]
    first = ranked[0]
    assert {"teacher_id", "topic", "persona", "score", "series_summary"} <= set(first)
