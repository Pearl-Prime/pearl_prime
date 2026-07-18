"""De-injection 2026-07-05: render-time glue families OFF by default on spine path."""
from __future__ import annotations

from phoenix_v4.exercises import component_assembler as ca
from phoenix_v4.rendering import chapter_composer as cc


def test_bridge_transition_families_disabled_by_default(monkeypatch):
    monkeypatch.delenv("PHOENIX_ENABLE_RENDER_GLUE", raising=False)
    monkeypatch.delenv("PHOENIX_BRIDGE_TRANSITION_FAMILIES", raising=False)
    cc._BRIDGE_TRANSITION_CACHE = None
    assert cc.bridge_transition_families_enabled() is False
    assert cc._bridge_after_opening("The point is x", emotional_job="recognition") == ""
    assert cc._select_bridge_candidate(
        bridge_type="after_opening",
        emotional_job="recognition",
        chapter_index=0,
        total_chapters=12,
        bridge_memory=cc.BridgeMemory(),
        context_text="x",
    ) is None


def test_mechanism_thesis_families_disabled_by_default(monkeypatch):
    monkeypatch.delenv("PHOENIX_ENABLE_RENDER_GLUE", raising=False)
    monkeypatch.delenv("PHOENIX_MECHANISM_THESIS_FAMILIES", raising=False)
    cc._MECHANISM_THESIS_CACHE = None
    assert cc.mechanism_thesis_families_enabled() is False
    assert cc._distill_mechanism("alarm fires", "The point is alarm", emotional_job="mechanism") == ""


def test_exercise_wrapper_families_disabled_by_default(monkeypatch):
    monkeypatch.delenv("PHOENIX_ENABLE_RENDER_GLUE", raising=False)
    monkeypatch.delenv("PHOENIX_EXERCISE_WRAPPER_FAMILIES", raising=False)
    cc._EXERCISE_WRAPPER_CACHE = None
    assert cc.exercise_wrapper_families_enabled() is False
    assert cc._exercise_setup_sentence("jaw tight", "story") == ""
    assert cc._fallback_takeaway("The point is x") == ""


def test_exercise_component_templates_disabled_by_default(monkeypatch):
    monkeypatch.delenv("PHOENIX_ENABLE_RENDER_GLUE", raising=False)
    monkeypatch.delenv("PHOENIX_EXERCISE_COMPONENT_TEMPLATES", raising=False)
    assert ca.exercise_component_templates_enabled() is False
    comps = ca.resolve_exercise_components(
        exercise_id="ex01",
        exercise_type="body_awareness",
        description_text="Notice your breath.",
        chapter_index=0,
    )
    assert not comps.bridge.full
    assert not comps.introduction.full
    assert not comps.intro.full
    assert comps.description.full == "Notice your breath."


def test_compose_chapter_prose_no_glue_phrases_by_default(monkeypatch):
    monkeypatch.delenv("PHOENIX_ENABLE_RENDER_GLUE", raising=False)
    monkeypatch.delenv("PHOENIX_BRIDGE_TRANSITION_FAMILIES", raising=False)
    monkeypatch.delenv("PHOENIX_MECHANISM_THESIS_FAMILIES", raising=False)
    monkeypatch.delenv("PHOENIX_EXERCISE_WRAPPER_FAMILIES", raising=False)
    monkeypatch.delenv("PHOENIX_EXERCISE_COMPONENT_TEMPLATES", raising=False)
    cc._BRIDGE_TRANSITION_CACHE = None
    cc._MECHANISM_THESIS_CACHE = None
    cc._EXERCISE_WRAPPER_CACHE = None
    out = cc.compose_chapter_prose(
        ["HOOK", "REFLECTION", "EXERCISE"],
        [
            "The inbox is still open.",
            "Financial stress has a specific physical signature.",
            "Notice one breath.",
        ],
        chapter_index=0,
        total_chapters=12,
        topic_id="financial_stress",
    )
    low = out.lower()
    assert "turn it into motion" not in low
    assert "now we're going to do a practice" not in low
    assert "remember this:" not in low
    assert "what remains is not more explanation" not in low
