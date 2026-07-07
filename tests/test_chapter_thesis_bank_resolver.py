"""Tests for chapter_thesis_bank topic→engine baseline resolution (Q1 census lane)."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from phoenix_v4.planning.book_structure_plan import _get_thesis_from_bank
from phoenix_v4.rendering import chapter_composer as cc

REPO = Path(__file__).resolve().parents[1]
BANK_PATH = REPO / "config" / "planning" / "chapter_thesis_bank.yaml"


@pytest.fixture(autouse=True)
def _clear_thesis_caches() -> None:
    cc._CHAPTER_THESIS_BANK_CACHE = None
    cc._CHAPTER_THESIS_TOPICS_CACHE = None
    yield
    cc._CHAPTER_THESIS_BANK_CACHE = None
    cc._CHAPTER_THESIS_TOPICS_CACHE = None


def _baseline(intent: str, engine: str) -> str:
    data = yaml.safe_load(BANK_PATH.read_text(encoding="utf-8")) or {}
    return str((data.get("intents") or {}).get(intent, {}).get(engine, ""))


def _overlay(topic: str, intent: str, engine: str) -> str:
    data = yaml.safe_load(BANK_PATH.read_text(encoding="utf-8")) or {}
    return str(((data.get("topics") or {}).get(topic) or {}).get(intent, {}).get(engine, ""))


def test_topic_override_precedes_engine_baseline_book_structure_plan() -> None:
    topic, intent, engine = "burnout", "establish_mask", "comparison"
    overlay = _overlay(topic, intent, engine)
    baseline = _baseline(intent, engine)
    assert overlay and baseline and overlay != baseline
    resolved = _get_thesis_from_bank("recognition", engine, 1, topic, REPO)
    assert resolved == overlay


def test_unauthored_topic_falls_back_to_baseline() -> None:
    topic, intent, engine = "adhd_focus", "establish_mask", "comparison"
    baseline = _baseline(intent, engine)
    resolved = _get_thesis_from_bank("recognition", engine, 1, topic, REPO)
    assert resolved == baseline


def test_chapter_composer_derive_thesis_topic_first() -> None:
    topic, intent, engine = "anxiety", "grounded_reframe", "comparison"
    overlay = _overlay(topic, intent, engine)
    thesis = cc._derive_thesis(
        "reflection seed",
        chapter_intent=intent,
        engine_type=engine,
        topic_id=topic,
    )
    assert thesis == overlay


def test_same_engine_different_topics_diverge() -> None:
    engine = "comparison"
    intent = "expose_cost"
    burnout = cc._derive_thesis(
        "",
        chapter_intent=intent,
        engine_type=engine,
        topic_id="burnout",
    )
    anxiety = cc._derive_thesis(
        "",
        chapter_intent=intent,
        engine_type=engine,
        topic_id="anxiety",
    )
    boundaries = cc._derive_thesis(
        "",
        chapter_intent=intent,
        engine_type=engine,
        topic_id="boundaries",
    )
    assert burnout != anxiety != boundaries
    assert burnout == _overlay("burnout", intent, engine)
    assert anxiety == _overlay("anxiety", intent, engine)


def test_spiral_overwhelm_comparison_baseline_intact_for_unauthored_topic() -> None:
    for engine in ("spiral", "overwhelm", "comparison"):
        baseline = _baseline("establish_mask", engine)
        resolved = _get_thesis_from_bank("recognition", engine, 1, "financial_stress", REPO)
        assert resolved == baseline
