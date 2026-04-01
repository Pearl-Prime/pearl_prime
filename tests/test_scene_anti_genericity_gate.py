"""
Tests for scene anti-genericity gate (§8 overlay spec).

Covers:
  - Unique scenes pass
  - Colliding scenes fail
  - Static-only scenes flagged
  - Location repetition detected
  - Production vs draft mode behavior
"""
from __future__ import annotations

import pytest

from phoenix_v4.qa.scene_anti_genericity_gate import (
    ChapterDiagnostic,
    GateResult,
    SceneReport,
    check_scene_genericity,
    enforce_scene_gate,
    _extract_sensory_phrases,
    _find_collisions,
    _has_character_action,
    _find_repeated_locations,
    _ngrams,
    _jaccard,
)


# ---------------------------------------------------------------------------
# Fixtures: chapter texts
# ---------------------------------------------------------------------------

UNIQUE_CHAPTER_A = (
    "Your thumb hovers over the cracked phone screen. The oat-milk film on the "
    "cold mug has gone grey. Your left knee presses against the dented metal "
    "desk leg. You exhale and your shoulders drop two inches. The fluorescent "
    "hum is the only sound. Your fingers curl around the chipped ceramic edge."
)

UNIQUE_CHAPTER_B = (
    "The sticky leather of the steering wheel pulls at your palms. A bitter "
    "coffee ring stains the faded dashboard. Your jaw tightens as the sharp "
    "morning light hits the scratched windshield. You grip the rough gear shift "
    "and your wrist rotates slowly. The stale air sits heavy in your chest."
)

UNIQUE_CHAPTER_C = (
    "Your heel catches on the frayed doormat. The damp towel on the bathroom "
    "door smells of mildew. Your neck tilts forward under the dim hallway bulb. "
    "You reach for the cold metal railing. Your fingers find the smooth surface "
    "of the yellowed light switch. A soft click. Your hand drops."
)

COLLIDING_CHAPTER_1 = (
    "You sit at the kitchen counter. The coffee is cold. Your phone buzzes. "
    "The room is quiet. You feel overwhelmed. The light through the window "
    "falls on the counter. You stare at the screen. Nothing changes."
)

COLLIDING_CHAPTER_2 = (
    "You sit at the kitchen counter. The coffee is cold. Your phone buzzes. "
    "The room is quiet. You feel overwhelmed. The light through the window "
    "falls on the counter. You stare at the screen. Nothing changes at all."
)

STATIC_CHAPTER = (
    "The room is painted grey. A cold draft enters from somewhere. The sharp "
    "metallic smell of old pipes fills the dim corridor. The rough concrete "
    "floor stretches ahead. Silence. A damp stain spreads across the "
    "yellowed ceiling tiles. The fluorescent light flickers once."
)

ACTION_CHAPTER = (
    "The rough wooden railing meets your palm. A sharp splinter catches your "
    "thumb. You pull your hand back. Your fingers curl into your damp pocket. "
    "The cold air presses against your chest as you lean forward."
)

LOCATION_REPEAT_A = (
    "You sit in the kitchen. The sharp cold mug sits on the counter. "
    "Your thumb presses against the cracked ceramic. You exhale and "
    "your shoulders drop. The damp towel hangs nearby."
)

LOCATION_REPEAT_B = (
    "You stand in the kitchen. The bitter coffee smell fills the air. "
    "Your jaw clenches under the dim light. Your fingers grip the "
    "rough counter edge. A stale crumb falls."
)

LOCATION_REPEAT_C = (
    "You lean in the kitchen. The warm steam rises from the chipped bowl. "
    "Your neck tilts forward. Your hand rests on the sticky counter. "
    "The fluorescent tube hums above."
)


# ---------------------------------------------------------------------------
# Unit tests: helper functions
# ---------------------------------------------------------------------------

class TestNgrams:
    def test_basic(self):
        grams = _ngrams("the quick brown fox jumps")
        assert ("the", "quick", "brown", "fox") in grams
        assert ("quick", "brown", "fox", "jumps") in grams

    def test_short_text(self):
        assert _ngrams("one two three") == set()

    def test_empty(self):
        assert _ngrams("") == set()


class TestJaccard:
    def test_identical(self):
        s = {("a", "b", "c", "d")}
        assert _jaccard(s, s) == 1.0

    def test_disjoint(self):
        a = {("a", "b", "c", "d")}
        b = {("e", "f", "g", "h")}
        assert _jaccard(a, b) == 0.0

    def test_empty(self):
        assert _jaccard(set(), set()) == 0.0


class TestExtractSensoryPhrases:
    def test_finds_body_parts(self):
        phrases = _extract_sensory_phrases("Your thumb presses the cold mug")
        assert any("thumb" in p for p in phrases)

    def test_finds_adjective_combos(self):
        phrases = _extract_sensory_phrases("The rough surface and sharp edge")
        assert len(phrases) >= 2


class TestHasCharacterAction:
    def test_action_present(self):
        assert _has_character_action(
            "You grip the railing. Your fingers tighten."
        )

    def test_no_action(self):
        assert not _has_character_action(
            "The room is cold. A draft enters."
        )

    def test_verb_without_body(self):
        assert not _has_character_action(
            "The door swings open. The light flickers."
        )


class TestFindCollisions:
    def test_identical_chapters_collide(self):
        collisions = _find_collisions(
            [COLLIDING_CHAPTER_1, COLLIDING_CHAPTER_2],
            threshold=0.8,
        )
        assert len(collisions) >= 1
        assert collisions[0][2] > 0.8

    def test_unique_chapters_no_collision(self):
        collisions = _find_collisions(
            [UNIQUE_CHAPTER_A, UNIQUE_CHAPTER_B, UNIQUE_CHAPTER_C],
            threshold=0.8,
        )
        assert len(collisions) == 0


class TestFindRepeatedLocations:
    def test_detects_repetition(self):
        repeated = _find_repeated_locations(
            [LOCATION_REPEAT_A, LOCATION_REPEAT_B, LOCATION_REPEAT_C],
            threshold=0.5,
        )
        assert any("in the kitchen" in phrase for phrase in repeated)

    def test_no_repetition_unique_chapters(self):
        repeated = _find_repeated_locations(
            [UNIQUE_CHAPTER_A, UNIQUE_CHAPTER_B, UNIQUE_CHAPTER_C],
            threshold=0.5,
        )
        assert len(repeated) == 0 or all(
            len(indices) / 3 <= 0.5 for indices in repeated.values()
        )


# ---------------------------------------------------------------------------
# Integration tests: check_scene_genericity
# ---------------------------------------------------------------------------

class TestCheckSceneGenericity:
    def test_unique_scenes_pass(self):
        report = check_scene_genericity(
            [UNIQUE_CHAPTER_A, UNIQUE_CHAPTER_B, UNIQUE_CHAPTER_C]
        )
        assert report.status == "PASS"
        assert len(report.errors) == 0
        assert report.metrics["collision_count"] == 0

    def test_colliding_scenes_fail(self):
        report = check_scene_genericity(
            [COLLIDING_CHAPTER_1, COLLIDING_CHAPTER_2]
        )
        assert report.status == "FAIL"
        assert any("SCENE_COLLISION" in e for e in report.errors)
        assert report.metrics["collision_count"] >= 1

    def test_static_scene_flagged(self):
        report = check_scene_genericity([STATIC_CHAPTER])
        has_static_error = any("STATIC_SCENE" in e for e in report.errors)
        assert has_static_error

    def test_action_scene_not_flagged(self):
        report = check_scene_genericity([ACTION_CHAPTER])
        has_static_error = any("STATIC_SCENE" in e for e in report.errors)
        assert not has_static_error

    def test_location_repetition_detected(self):
        report = check_scene_genericity(
            [LOCATION_REPEAT_A, LOCATION_REPEAT_B, LOCATION_REPEAT_C]
        )
        assert any("LOCATION_REPETITION" in e for e in report.errors)
        assert report.metrics["repeated_location_count"] >= 1

    def test_empty_chapters_pass(self):
        report = check_scene_genericity([])
        assert report.status == "PASS"
        assert report.metrics["chapter_count"] == 0

    def test_per_chapter_diagnostics(self):
        report = check_scene_genericity(
            [UNIQUE_CHAPTER_A, UNIQUE_CHAPTER_B]
        )
        assert len(report.chapter_diagnostics) == 2
        for diag in report.chapter_diagnostics:
            assert isinstance(diag, ChapterDiagnostic)
            assert isinstance(diag.unique_details, int)
            assert isinstance(diag.has_action, bool)


# ---------------------------------------------------------------------------
# Integration tests: enforce_scene_gate
# ---------------------------------------------------------------------------

class TestEnforceSceneGate:
    def test_production_unique_pass(self):
        result = enforce_scene_gate(
            [UNIQUE_CHAPTER_A, UNIQUE_CHAPTER_B, UNIQUE_CHAPTER_C],
            mode="production",
        )
        assert result.status == "PASS"
        assert result.mode == "production"
        assert not result.blocking

    def test_production_collision_fails(self):
        result = enforce_scene_gate(
            [COLLIDING_CHAPTER_1, COLLIDING_CHAPTER_2],
            mode="production",
        )
        assert result.status == "FAIL"
        assert result.blocking
        assert any("SCENE_COLLISION" in e for e in result.report.errors)

    def test_production_location_repetition_fails(self):
        result = enforce_scene_gate(
            [LOCATION_REPEAT_A, LOCATION_REPEAT_B, LOCATION_REPEAT_C],
            mode="production",
        )
        assert result.status == "FAIL"
        assert result.blocking

    def test_draft_mode_never_blocks(self):
        result = enforce_scene_gate(
            [COLLIDING_CHAPTER_1, COLLIDING_CHAPTER_2],
            mode="draft",
        )
        assert result.status == "WARN"
        assert not result.blocking
        assert result.mode == "draft"
        assert len(result.report.errors) == 0
        assert len(result.report.warnings) > 0

    def test_draft_unique_pass(self):
        result = enforce_scene_gate(
            [UNIQUE_CHAPTER_A, UNIQUE_CHAPTER_B, UNIQUE_CHAPTER_C],
            mode="draft",
        )
        assert result.status == "PASS"
        assert not result.blocking

    def test_production_static_scene_warns_not_blocks(self):
        """Static scene alone should WARN, not FAIL in production (no collision)."""
        result = enforce_scene_gate(
            [STATIC_CHAPTER],
            mode="production",
        )
        assert not result.blocking
        assert result.status in ("WARN", "PASS")

    def test_gate_result_structure(self):
        result = enforce_scene_gate(
            [UNIQUE_CHAPTER_A],
            mode="production",
        )
        assert isinstance(result, GateResult)
        assert isinstance(result.report, SceneReport)
        assert result.report.metrics.get("chapter_count") == 1
