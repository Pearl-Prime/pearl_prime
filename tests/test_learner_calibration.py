"""
Tests for EI V2 learner calibration: learn_from_feedback, calibration_report.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.quality.ei_v2.learner import (
    DEFAULT_COMPOSITE_WEIGHTS,
    FeedbackRecord,
    LearnedParams,
    calibration_report,
    learn_from_feedback,
    load_learned_params,
    log_feedback,
    save_learned_params,
)


def _write_feedback(path: Path, records: list[FeedbackRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    for r in records:
        log_feedback(r, path=path)


def _minimal_record(**overrides) -> FeedbackRecord:
    base = dict(
        timestamp="2026-03-30T12:00:00Z",
        slot="STORY",
        chapter_index=0,
        persona_id="p",
        topic_id="t",
        v1_chosen_id="a",
        v2_chosen_id="b",
        hybrid_chosen_id="a",
        override_applied=False,
    )
    base.update(overrides)
    return FeedbackRecord(**base)


def test_learn_from_feedback_insufficient_observations_unchanged(tmp_path: Path) -> None:
    fb = tmp_path / "fb.jsonl"
    params_path = tmp_path / "params.json"
    save_learned_params(LearnedParams(override_margin=0.18), params_path)
    recs = [_minimal_record(accepted=True, dimension_scores={"rerank": 0.9}) for _ in range(9)]
    _write_feedback(fb, recs)
    before = load_learned_params(params_path)
    out = learn_from_feedback(fb, params_path, cfg={"learner": {"min_observations": 10}})
    after = load_learned_params(params_path)
    assert out.override_margin == before.override_margin
    assert out.composite_weights == before.composite_weights
    assert after.override_margin == before.override_margin


def test_learn_from_feedback_updates_weights_with_sufficient_records(tmp_path: Path) -> None:
    fb = tmp_path / "fb.jsonl"
    params_path = tmp_path / "params.json"
    # Defaults on disk
    save_learned_params(LearnedParams(), params_path)
    scores = {"rerank": 0.8, "domain": 0.8, "safety": 0.8, "tts": 0.8, "emotion_arc": 0.8}
    recs = [_minimal_record(accepted=True, dimension_scores=dict(scores)) for _ in range(10)]
    _write_feedback(fb, recs)
    learn_from_feedback(fb, params_path, cfg={"learner": {"ema_alpha": 0.15, "min_observations": 10}})
    updated = load_learned_params(params_path)
    assert updated.composite_weights != DEFAULT_COMPOSITE_WEIGHTS.copy()
    s = sum(updated.composite_weights.values())
    assert s == pytest.approx(1.0)


def test_ema_math_exact_normalized_weights(tmp_path: Path) -> None:
    """Known averages and alpha -> predictable post-normalization weights."""
    alpha = 0.15
    fb = tmp_path / "fb.jsonl"
    params_path = tmp_path / "params.json"
    save_learned_params(LearnedParams(), params_path)
    scores = {"rerank": 0.4, "domain": 0.4, "safety": 0.4, "tts": 0.4, "emotion_arc": 0.4}
    recs = [_minimal_record(accepted=True, dimension_scores=dict(scores)) for _ in range(10)]
    _write_feedback(fb, recs)
    learn_from_feedback(
        fb,
        params_path,
        cfg={"learner": {"ema_alpha": alpha, "min_observations": 10, "learning_window": 200}},
    )
    updated = load_learned_params(params_path)
    raw = {}
    for dim, cur in DEFAULT_COMPOSITE_WEIGHTS.items():
        raw[dim] = alpha * 0.4 + (1.0 - alpha) * cur
    t = sum(raw.values())
    expected = {k: raw[k] / t for k in raw}
    for dim in DEFAULT_COMPOSITE_WEIGHTS:
        assert updated.composite_weights[dim] == pytest.approx(expected[dim], rel=1e-12, abs=1e-12)


def test_weights_sum_to_one_after_update(tmp_path: Path) -> None:
    fb = tmp_path / "fb.jsonl"
    params_path = tmp_path / "params.json"
    save_learned_params(LearnedParams(), params_path)
    recs = []
    for i in range(10):
        recs.append(
            _minimal_record(
                accepted=True,
                dimension_scores={
                    "rerank": 0.1 + i * 0.01,
                    "domain": 0.5,
                    "safety": 0.6,
                    "tts": 0.7,
                    "emotion_arc": 0.55,
                },
            )
        )
    _write_feedback(fb, recs)
    learn_from_feedback(fb, params_path, cfg={"learner": {"min_observations": 10}})
    w = load_learned_params(params_path).composite_weights
    assert sum(w.values()) == pytest.approx(1.0)


def test_override_margin_clamped_high(tmp_path: Path) -> None:
    fb = tmp_path / "fb.jsonl"
    params_path = tmp_path / "params.json"
    save_learned_params(LearnedParams(override_margin=0.12), params_path)
    recs = [
        _minimal_record(accepted=False, override_applied=True, margin_delta=0.99) for _ in range(10)
    ]
    _write_feedback(fb, recs)
    learn_from_feedback(fb, params_path, cfg={"learner": {"ema_alpha": 1.0, "min_observations": 10}})
    assert load_learned_params(params_path).override_margin == pytest.approx(0.30)


def test_override_margin_clamped_low(tmp_path: Path) -> None:
    fb = tmp_path / "fb.jsonl"
    params_path = tmp_path / "params.json"
    save_learned_params(LearnedParams(override_margin=0.12), params_path)
    recs = [
        _minimal_record(accepted=False, override_applied=True, margin_delta=-0.5) for _ in range(10)
    ]
    _write_feedback(fb, recs)
    learn_from_feedback(fb, params_path, cfg={"learner": {"ema_alpha": 1.0, "min_observations": 10}})
    assert load_learned_params(params_path).override_margin == pytest.approx(0.05)


def test_calibration_report_diffs() -> None:
    prev = LearnedParams(
        override_margin=0.12,
        composite_weights={k: v for k, v in DEFAULT_COMPOSITE_WEIGHTS.items()},
    )
    cur = LearnedParams(
        override_margin=0.15,
        composite_weights={k: (v + 0.01 if k == "rerank" else v) for k, v in DEFAULT_COMPOSITE_WEIGHTS.items()},
    )
    # renormalize cur for realism
    t = sum(cur.composite_weights.values())
    cur = LearnedParams(
        override_margin=0.15,
        composite_weights={k: cur.composite_weights[k] / t for k in cur.composite_weights},
    )
    rep = calibration_report(cur, prev)
    assert rep["override_margin"]["previous"] == pytest.approx(0.12)
    assert rep["override_margin"]["current"] == pytest.approx(0.15)
    assert rep["override_margin"]["delta"] == pytest.approx(0.03)
    assert "rerank" in rep["composite_weights"]
    assert rep["composite_weights"]["rerank"]["delta"] != 0.0


def test_determinism_same_feedback_same_params(tmp_path: Path) -> None:
    fb = tmp_path / "fb.jsonl"
    p1 = tmp_path / "p1.json"
    p2 = tmp_path / "p2.json"
    scores = {"rerank": 0.55, "domain": 0.62, "safety": 0.71, "tts": 0.49, "emotion_arc": 0.58}
    recs = [
        _minimal_record(
            accepted=i % 2 == 0,
            override_applied=i % 3 == 0,
            margin_delta=0.1 + i * 0.01,
            dimension_scores=dict(scores),
        )
        for i in range(12)
    ]
    _write_feedback(fb, recs)
    save_learned_params(LearnedParams(), p1)
    save_learned_params(LearnedParams(), p2)
    cfg = {"learner": {"ema_alpha": 0.15, "min_observations": 10}}
    a = learn_from_feedback(fb, p1, cfg=cfg)
    save_learned_params(LearnedParams(), p2)
    b = learn_from_feedback(fb, p2, cfg=cfg)
    assert a.to_dict() == b.to_dict()


def test_saved_params_roundtrip_load_learned_params(tmp_path: Path) -> None:
    fb = tmp_path / "fb.jsonl"
    params_path = tmp_path / "out.json"
    save_learned_params(LearnedParams(), params_path)
    recs = [
        _minimal_record(
            accepted=True,
            override_applied=True,
            margin_delta=0.14,
            dimension_scores={"rerank": 0.7, "domain": 0.65, "safety": 0.8, "tts": 0.5, "emotion_arc": 0.6},
        )
        for _ in range(10)
    ]
    _write_feedback(fb, recs)
    learned = learn_from_feedback(fb, params_path, cfg={"learner": {"min_observations": 10}})
    again = load_learned_params(params_path)
    assert again.to_dict() == learned.to_dict()


def test_learning_window_truncates_to_recent(tmp_path: Path) -> None:
    """Last window rows only: first record differs; if window=3, first should not affect result."""
    fb = tmp_path / "fb.jsonl"
    params_path = tmp_path / "params.json"
    save_learned_params(LearnedParams(), params_path)
    recs = []
    recs.append(
        _minimal_record(
            timestamp="2026-03-30T09:00:00Z",
            accepted=True,
            dimension_scores={"rerank": 0.99, "domain": 0.2, "safety": 0.2, "tts": 0.2, "emotion_arc": 0.2},
        )
    )
    for _ in range(9):
        recs.append(
            _minimal_record(
                accepted=True,
                dimension_scores={"rerank": 0.1, "domain": 0.25, "safety": 0.2, "tts": 0.1, "emotion_arc": 0.1},
            )
        )
    _write_feedback(fb, recs)
    learn_from_feedback(
        fb,
        params_path,
        cfg={"learner": {"min_observations": 10, "learning_window": 3, "ema_alpha": 1.0}},
    )
    w3 = load_learned_params(params_path).composite_weights.copy()

    save_learned_params(LearnedParams(), params_path)
    _write_feedback(fb, recs)
    learn_from_feedback(
        fb,
        params_path,
        cfg={"learner": {"min_observations": 10, "learning_window": 200, "ema_alpha": 1.0}},
    )
    w_all = load_learned_params(params_path).composite_weights.copy()
    assert w3 != w_all
