"""Tests for phoenix_v4.quality.bestseller_craft_gate (ONTGP heuristics)."""
from __future__ import annotations

import pytest

from phoenix_v4.quality.bestseller_craft_gate import (
    DIAGNOSTIC_QUESTIONS,
    CraftGateResult,
    evaluate_bestseller_craft,
)


@pytest.fixture
def chapter_well_crafted() -> str:
    """Strong orient, name, turn, give, pull signals (overlay §4); ~500 words golden fixture."""
    return """
Your throat closes before you name why. Three a.m. and the ceiling is the same gray sheet you have memorized.
You are awake in the small hours and your jaw is already busy. The room is quiet except the heat clicking on.

Maya stands in the hallway outside the conference room. She said less than she planned. Her hands stayed polite.
The real problem is not her volume at the table. What you call careful is actually disappeared, and her body knows it before she does.
Not a flaw in her character. A pattern that once kept her safe when speaking cost more than silence.

She rides the elevator down and watches the numbers fall. The fluorescent hum is steady. Her phone stays dark in her pocket.
The pattern is visible in how she rehearses apologies before anyone has asked for one. What you thought was politeness is a survival script.
Except the script no longer matches the room she is in. The problem is not her tone. What actually happens is her nervous system still acts as if the stakes are mortal.

But the cost is not the meeting. The cost is what you call yourself after you leave the room.
The problem is not that she is shy. What actually happens is her system rehearses danger before her mouth opens.
This is why the throat locks first. Not because she is broken. Never because she lacks courage — it is because the old math still runs.

Place your hand on your chest. Breathe in for four counts. Out for six. Right now.
Press gently and feel the warmth under your palm for ten seconds. Name one word for what the sternum is holding. Whisper it once.
The instruction is small on purpose. You can do it without a mat, without an app, without explaining yourself to anyone in the room.

Still here. The grip behind your sternum has a name now. Feet on the floor. Weight in the chair.
You feel the chair under you and the air on your face. The hallway memory is still in your jaw, but softer than it was.
What you have not yet asked is who taught you that silence was safety — and whether that teacher is still in the room when you walk into the kitchen tomorrow.
Which part of you still believes that disappearing is the same as being good?
""".strip()


@pytest.fixture
def chapter_bad_orient() -> str:
    """Abstract topic opener — fails Orient diagnostic.

    First ~150 words must stay in essay/topic mode so the orient window does not
    pick up second-person or imperative placement from later lines.
    """
    abstract_open = """
This chapter is about anxiety and how it affects daily life. Today we will explore several themes.
Throughout this chapter, the material addresses patterns and mechanisms at a conceptual level.
Let us discuss the framework before any application appears. The topic is important for many readers.
Anxiety is a response that researchers describe in aggregate. Burnout happens when expectations misalign.
Self-worth means different things depending on context. The section summarizes general principles first.
Later sections may offer exercises when the conceptual groundwork is complete. We will explore boundaries
between stress and disorder without naming individual moments. The narrative stays informational until
the midpoint. Mechanisms include cognitive appraisal and physiological arousal in broad terms.
The discussion proceeds through definitions, prevalence estimates, and theoretical models without
anchoring the listener in a room or on a clock face. In this chapter, the aim is orientation to the
literature rather than immersion in lived experience.
""".strip()
    tail = """
But the cost is not the meeting. The cost is what you call yourself after you leave the room.
Place your hand on your chest. Breathe in for four counts. Out for six. Right now.
What you have not yet asked is who taught you that silence was safety.
""".strip()
    assert len(abstract_open.split()) >= 150, "fixture must keep orient zone abstract-only"
    return f"{abstract_open}\n\n{tail}"


@pytest.fixture
def chapter_bad_pull() -> str:
    """Generic explore closer — fails Pull (overlay §7.2)."""
    return """
Your throat closes before you name why. Three a.m. and the ceiling is the same gray.

Not avoidance. A system that learned to protect you when speaking up cost more than silence.

But the cost is not the meeting. The cost is what you call yourself after you leave the room.

Place your hand on your chest. Breathe in for four counts. Out for six. Right now.

There is more to explore in the next chapter. We will continue this journey together.
""".strip()


@pytest.fixture
def chapter_vague_give() -> str:
    """Weak exercise block — WARN on give (between fail and pass thresholds)."""
    return """
Your throat closes before you name why. Three a.m. and the ceiling is the same gray.

Not avoidance. A system that learned to protect you when speaking up cost more than silence.

But the cost is not the meeting. The cost is what you call yourself after you leave the room.

Notice your breath. Try to stay with the sensation when you can. Maybe sit quietly if that works for you.

Still here. The grip behind your sternum has a name now. What you have not yet asked is who taught you that silence was safety — and whether that teacher is still in the room.
""".strip()


class TestBestsellerCraftGate:
    def test_well_crafted_passes(self, chapter_well_crafted: str):
        wc = len(chapter_well_crafted.split())
        assert 400 <= wc <= 650, f"golden chapter ~500 words, got {wc}"
        r = evaluate_bestseller_craft(chapter_well_crafted)
        assert isinstance(r, CraftGateResult)
        assert r.status == "PASS"
        for m, s in r.move_scores.items():
            assert s >= 0.4, (m, s)
        assert "orient_words" in r.metrics.get("zones", {})

    def test_bad_orient_fails(self, chapter_bad_orient: str):
        r = evaluate_bestseller_craft(chapter_bad_orient)
        assert r.status == "FAIL"
        assert r.move_scores["orient"] < 0.2
        assert any("abstract_topic" in i for i in r.issues)

    def test_bad_pull_fails_or_warns(self, chapter_bad_pull: str):
        r = evaluate_bestseller_craft(chapter_bad_pull)
        assert r.status == "FAIL"
        assert r.move_scores["pull"] < 0.2
        joined = " ".join(r.issues).lower()
        assert "generic_thread" in joined or "move_fail:pull" in joined

    def test_vague_give_warns(self, chapter_vague_give: str):
        r = evaluate_bestseller_craft(chapter_vague_give)
        assert r.status == "WARN"
        assert 0.2 <= r.move_scores["give"] < 0.4

    def test_deterministic_same_input(self, chapter_well_crafted: str):
        a = evaluate_bestseller_craft(chapter_well_crafted)
        b = evaluate_bestseller_craft(chapter_well_crafted)
        assert a.status == b.status
        assert a.move_scores == b.move_scores

    def test_empty_chapter_fails(self):
        r = evaluate_bestseller_craft("")
        assert r.status == "FAIL"
        assert r.move_scores["orient"] == 0.0

    def test_thresholds_configurable(self, chapter_vague_give: str):
        """Loosen warn band so marginal give passes overall."""
        r = evaluate_bestseller_craft(
            chapter_vague_give,
            thresholds={"fail_below": 0.15, "warn_below": 0.15},
        )
        assert r.status == "PASS"

    def test_llm_callback_contract_mock(self, chapter_well_crafted: str):
        calls: list[tuple[str, str, str]] = []

        def mock_llm(chapter_text: str, move_name: str, diagnostic_question: str) -> dict:
            calls.append((chapter_text, move_name, diagnostic_question))
            assert diagnostic_question == DIAGNOSTIC_QUESTIONS[move_name]
            assert chapter_text.strip() == chapter_well_crafted.strip()
            return {"score": 0.99, "reasoning": "mock"}

        r = evaluate_bestseller_craft(chapter_well_crafted, call_llm_json=mock_llm)
        assert len(calls) == 5
        assert {c[1] for c in calls} == {"orient", "name", "turn", "give", "pull"}
        assert r.metrics.get("llm_tier") == "callback_invoked"
        for m in ("orient", "name", "turn", "give", "pull"):
            assert r.move_scores[m] == 0.99

    def test_to_dict_roundtrip(self, chapter_well_crafted: str):
        r = evaluate_bestseller_craft(chapter_well_crafted)
        d = r.to_dict()
        assert d["status"] == r.status
        assert set(d["move_scores"].keys()) == {"orient", "name", "turn", "give", "pull"}
