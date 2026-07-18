"""
Integration tests for ACT-008: EMA learner production wiring.

Tests that:
1. Engagement-correlated accepted books shift the learner weights toward engagement-
   adjacent dimensions (rerank) after 20 feedback records.
2. Learner does not crash and does not write params when feedback is insufficient.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.quality.ei_v2.learner import (
    DEFAULT_COMPOSITE_WEIGHTS,
    FeedbackRecord,
    LearnedParams,
    learn_from_feedback,
    load_learned_params,
    log_feedback,
    save_learned_params,
)


def _minimal_record(**overrides) -> FeedbackRecord:
    base = dict(
        timestamp="2026-04-17T00:00:00Z",
        slot="EDITORIAL",
        chapter_index=0,
        persona_id="editor",
        topic_id="topic_01",
        v1_chosen_id="atom_v1",
        v2_chosen_id="atom_v2",
        hybrid_chosen_id="atom_v2",
        override_applied=False,
        accepted=True,
        v1_score=0.5,
        v2_score=0.7,
        margin_delta=0.0,
        dimension_scores={},
    )
    base.update(overrides)
    return FeedbackRecord(**base)


def _write_feedback(path: Path, records: list[FeedbackRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    for r in records:
        log_feedback(r, path=path)


# ---------------------------------------------------------------------------
# Test 1: EMA weights shift toward accepted-book dimensions
# ---------------------------------------------------------------------------

def test_ema_weights_shift_toward_accepted_books(tmp_path: Path) -> None:
    """
    Write 20 feedback records where `rerank` strongly correlates with acceptance:
    accepted=True records have high rerank (0.95), rejected have low rerank (0.1).
    After learning, the `rerank` composite weight should be higher than the default.

    This exercises the production feedback loop path used by run_ema_learner.py.
    """
    fb = tmp_path / "learner_feedback.jsonl"
    params_path = tmp_path / "learned_params.json"

    # Start from defaults
    save_learned_params(LearnedParams(), params_path)
    default_rerank_weight = DEFAULT_COMPOSITE_WEIGHTS["rerank"]

    records: list[FeedbackRecord] = []

    # 15 accepted with high rerank, low other dims
    for i in range(15):
        records.append(
            _minimal_record(
                accepted=True,
                margin_delta=1.5,
                dimension_scores={
                    "rerank": 0.95,
                    "domain": 0.30,
                    "safety": 0.30,
                    "tts": 0.30,
                    "emotion_arc": 0.30,
                },
            )
        )

    # 5 rejected with low rerank — these have no dimension_scores (accepted=False
    # records are ignored by EMA weight computation, only override_applied matters)
    for i in range(5):
        records.append(
            _minimal_record(
                accepted=False,
                margin_delta=-0.5,
                dimension_scores={
                    "rerank": 0.10,
                    "domain": 0.20,
                    "safety": 0.20,
                    "tts": 0.20,
                    "emotion_arc": 0.20,
                },
            )
        )

    _write_feedback(fb, records)

    cfg = {"learner": {"ema_alpha": 0.15, "min_observations": 10, "learning_window": 200}}
    updated = learn_from_feedback(fb, params_path, cfg=cfg)

    rerank_weight = updated.composite_weights["rerank"]

    # The rerank weight should increase because accepted books have high rerank scores
    assert rerank_weight > default_rerank_weight, (
        f"Expected rerank weight > {default_rerank_weight:.4f} after 15 high-rerank accepted books, "
        f"got {rerank_weight:.4f}"
    )

    # Weights must sum to 1.0
    total = sum(updated.composite_weights.values())
    assert abs(total - 1.0) < 1e-9, f"Weights do not sum to 1.0: {total}"

    # Params file must exist after successful learn
    assert params_path.exists(), "learned_params.json was not written"

    # total_observations should reflect full record count
    assert updated.total_observations == len(records)


# ---------------------------------------------------------------------------
# Test 2: No crash and no write when feedback is insufficient
# ---------------------------------------------------------------------------

def test_learner_no_crash_when_insufficient_records(tmp_path: Path) -> None:
    """
    Empty feedback file -> learner returns defaults unchanged, no params file written.
    This exercises the fail-safe path required by production safety.
    """
    fb = tmp_path / "learner_feedback.jsonl"
    params_path = tmp_path / "learned_params.json"

    # Feedback file exists but is empty
    fb.parent.mkdir(parents=True, exist_ok=True)
    fb.write_text("", encoding="utf-8")

    # No params file pre-exists
    assert not params_path.exists()

    cfg = {"learner": {"min_observations": 10}}
    result = learn_from_feedback(fb, params_path, cfg=cfg)

    # Should not crash; returns current params (defaults when file absent)
    assert result is not None
    assert isinstance(result, LearnedParams)

    # Params file should NOT be written (insufficient observations)
    assert not params_path.exists(), (
        "learned_params.json should not be written when records < min_observations"
    )

    # Returned params should be defaults
    assert result.override_margin == pytest.approx(0.12)
    assert result.total_observations == 0


def test_learner_no_crash_with_nonexistent_feedback_file(tmp_path: Path) -> None:
    """
    Feedback file does not exist -> graceful return with no write.
    """
    fb = tmp_path / "nonexistent.jsonl"
    params_path = tmp_path / "learned_params.json"

    assert not fb.exists()
    assert not params_path.exists()

    result = learn_from_feedback(fb, params_path, cfg={"learner": {"min_observations": 10}})

    assert result is not None
    assert not params_path.exists(), "No params should be written for empty/missing feedback"
