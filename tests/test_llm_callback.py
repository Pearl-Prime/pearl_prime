"""
Tests for EI V2 LLM callback protocols, cost guard, and safety classifier LLM path.
"""
from __future__ import annotations

from typing import Optional

import pytest

from phoenix_v4.quality.ei_v2.llm_callback import (
    LLMBudgetExceeded,
    LLMClassifyCallback,
    LLMJsonCallback,
    LLMTextCallback,
    cost_guarded,
    reset_chapter_budget,
)
from phoenix_v4.quality.ei_v2.safety_classifier import SAFETY_LLM_CATEGORIES, classify_safety

from tests.test_ei_v2 import SAMPLE_STORY_SAFE


class _MockTextCb:
    def __call__(self, prompt: str, text: str) -> float:
        return 0.82


class _MockJsonCb:
    def __call__(self, text: str, aspect: str, question: str) -> dict:
        return {"score": 0.7, "reasoning": "ok"}


class _MockClassifyCb:
    def __call__(self, text: str, categories: list[str]) -> dict:
        return {"category": "promotional", "confidence": 0.85, "flags": []}


def test_llm_text_callback_protocol_mock():
    cb = _MockTextCb()
    assert isinstance(cb, LLMTextCallback)
    assert cb("p", "t") == 0.82


def test_llm_json_callback_protocol_mock():
    cb = _MockJsonCb()
    assert isinstance(cb, LLMJsonCallback)
    d = cb("hello", "cohesion", "question?")
    assert d["score"] == 0.7
    assert "reasoning" in d


def test_llm_classify_callback_protocol_mock():
    cb = _MockClassifyCb()
    assert isinstance(cb, LLMClassifyCallback)
    d = cb("x", ["a", "b"])
    assert d["category"] == "promotional"


def test_cost_guarded_tracks_book_and_chapter_calls():
    tracker: dict = {}
    inner_calls: list[int] = []

    def inner(x: int) -> int:
        inner_calls.append(x)
        return x * 2

    wrapped = cost_guarded(inner, max_calls_per_book=3, max_calls_per_chapter=2, budget_tracker=tracker)
    assert wrapped(1) == 2
    assert wrapped(2) == 4
    assert tracker["book_calls"] == 2
    assert tracker["chapter_calls"] == 2
    inner_calls.clear()

    reset_chapter_budget(tracker)
    assert tracker["chapter_calls"] == 0
    assert wrapped(3) == 6
    assert tracker["book_calls"] == 3
    assert tracker["chapter_calls"] == 1


def test_cost_guarded_returns_none_when_exhausted():
    tracker = {"book_calls": 5, "chapter_calls": 0}

    def inner() -> str:
        return "ok"

    wrapped = cost_guarded(inner, max_calls_per_book=5, max_calls_per_chapter=10, budget_tracker=tracker)
    assert wrapped() is None
    assert tracker["book_calls"] == 5


def test_cost_guarded_raises_when_configured():
    tracker: dict = {}

    def inner() -> str:
        return "ok"

    wrapped = cost_guarded(
        inner,
        max_calls_per_book=1,
        max_calls_per_chapter=10,
        budget_tracker=tracker,
        raise_on_exhaust=True,
    )
    assert wrapped() == "ok"
    with pytest.raises(LLMBudgetExceeded):
        wrapped()


def test_cost_guarded_chapter_limit():
    tracker: dict = {}

    def inner() -> int:
        return 1

    wrapped = cost_guarded(inner, max_calls_per_book=100, max_calls_per_chapter=2, budget_tracker=tracker)
    assert wrapped() == 1
    assert wrapped() == 1
    assert wrapped() is None
    assert tracker["book_calls"] == 2
    assert tracker["chapter_calls"] == 2


def test_safety_classifier_llm_path_merges_with_mock():
    cfg = {"mode": "llm"}

    def mock_llm(text: str, categories: list[str]) -> dict:
        assert isinstance(categories, list)
        assert categories == SAFETY_LLM_CATEGORIES
        return {"category": "medical_claims", "confidence": 0.95, "flags": ["llm_flag"]}

    base = classify_safety(SAMPLE_STORY_SAFE, cfg={**cfg, "mode": "heuristic_plus"})
    merged = classify_safety(SAMPLE_STORY_SAFE, cfg=cfg, call_llm_fn=mock_llm)

    assert merged["categories"]["medical_claims"]["score"] > base["categories"]["medical_claims"]["score"]
    assert merged["risk_score"] >= base["risk_score"]
    assert "llm_flag" in merged["reason_codes"]


def test_safety_classifier_llm_fallback_when_callback_returns_none():
    cfg = {"mode": "llm"}

    def mock_llm(text: str, categories: list[str]) -> Optional[dict]:
        return None

    a = classify_safety(SAMPLE_STORY_SAFE, cfg={**cfg, "mode": "heuristic_plus"})
    b = classify_safety(SAMPLE_STORY_SAFE, cfg=cfg, call_llm_fn=mock_llm)
    assert b["risk_score"] == a["risk_score"]
    assert b["categories"] == a["categories"]
    assert b["reason_codes"] == a["reason_codes"]
    assert b["mode"] == "llm"


def test_safety_classifier_llm_fallback_when_callback_raises():
    cfg = {"mode": "llm"}

    def mock_llm(text: str, categories: list[str]) -> dict:
        raise RuntimeError("network")

    a = classify_safety(SAMPLE_STORY_SAFE, cfg={**cfg, "mode": "heuristic_plus"})
    b = classify_safety(SAMPLE_STORY_SAFE, cfg=cfg, call_llm_fn=mock_llm)
    assert b["risk_score"] == a["risk_score"]
    assert b["categories"] == a["categories"]
    assert b["reason_codes"] == a["reason_codes"]
    assert b["mode"] == "llm"


def test_safety_classifier_heuristic_plus_no_llm_invocation():
    from unittest.mock import Mock

    cfg = {"mode": "heuristic_plus"}
    m = Mock(return_value={"category": "medical_claims", "confidence": 1.0, "flags": []})
    out = classify_safety(SAMPLE_STORY_SAFE, cfg=cfg, call_llm_fn=m)
    m.assert_not_called()
    assert out["mode"] == "heuristic_plus"


def test_safety_classifier_llm_low_confidence_averages():
    cfg = {"mode": "llm"}
    base = classify_safety(SAMPLE_STORY_SAFE, cfg={**cfg, "mode": "heuristic_plus"})
    h = base["categories"]["medical_claims"]["score"]

    def mock_llm(text: str, categories: list[str]) -> dict:
        return {"category": "medical_claims", "confidence": 0.4, "flags": []}

    merged = classify_safety(SAMPLE_STORY_SAFE, cfg=cfg, call_llm_fn=mock_llm)
    expected = round((h + 0.4) / 2.0, 3)
    assert merged["categories"]["medical_claims"]["score"] == expected


def test_safety_classifier_llm_determinism_with_mock():
    cfg = {"mode": "llm"}

    def mock_llm(text: str, categories: list[str]) -> dict:
        return {"category": "pathologizing", "confidence": 0.85, "flags": []}

    r1 = classify_safety(SAMPLE_STORY_SAFE, cfg=cfg, call_llm_fn=mock_llm)
    r2 = classify_safety(SAMPLE_STORY_SAFE, cfg=cfg, call_llm_fn=mock_llm)
    assert r1 == r2


def test_safety_classifier_llm_with_cost_guard_none_fallback_matches_heuristic():
    cfg = {"mode": "llm"}
    tracker = {"book_calls": 10_000, "chapter_calls": 0}

    def raw_llm(text: str, categories: list[str]) -> dict:
        return {"category": "medical_claims", "confidence": 1.0, "flags": []}

    wrapped = cost_guarded(raw_llm, max_calls_per_book=10_000, max_calls_per_chapter=10, budget_tracker=tracker)
    heuristic_only = classify_safety(SAMPLE_STORY_SAFE, cfg={**cfg, "mode": "heuristic_plus"})
    with_guard = classify_safety(SAMPLE_STORY_SAFE, cfg=cfg, call_llm_fn=wrapped)
    assert with_guard["risk_score"] == heuristic_only["risk_score"]
    assert with_guard["categories"] == heuristic_only["categories"]
    assert with_guard["reason_codes"] == heuristic_only["reason_codes"]
    assert with_guard["mode"] == "llm"
