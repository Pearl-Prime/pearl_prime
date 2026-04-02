"""
Integration tests for the complete book QA pipeline.

Validates end-to-end wiring of:
1. Bestseller craft gate (ONTGP per-chapter prose quality)
2. Book pass gate (structural/narrative progression)
3. Creative quality gate v1 (arc motion, transformation, specificity, ending, rhythm)
4. Bestseller editor report (aggregation of all gates)
5. Config loading from config/quality/bestseller_craft_gate.yaml
6. EI v2 dimension gates integration status
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.quality.bestseller_craft_gate import (
    CraftGateResult,
    evaluate_bestseller_craft,
)
from phoenix_v4.qa.book_pass_gate import (
    BookPassDetails,
    get_chapter_tier,
    get_tier_thresholds,
    validate_book_pass,
)


# ── Fixtures ──


WELL_CRAFTED_CHAPTER = """
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


ABSTRACT_CHAPTER = """
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
There is more to explore in the next chapter. We will continue this journey together.
""".strip()


def _make_plan_and_prose(n_chapters: int, good: bool = True) -> tuple[dict, dict, dict]:
    """Build a minimal plan, atom_metadata, and prose_map for n_chapters."""
    chapter_slot_sequence = []
    atom_ids = []
    prose_map: dict[str, str] = {}
    atom_meta: dict[str, dict] = {}

    story_stages = ["pre_awareness", "destabilization", "experimentation",
                    "experimentation", "self_claim", "self_claim"]

    varied_claims = [
        "The point is your alarm is active before language catches up.",
        "Here is what is happening: prediction loops amplify uncertainty.",
        "What this means is the mechanism adds false urgency to uncertainty.",
        "This is not failure; it is pattern recognition under stress and cost prediction.",
        "Which means you can choose a smaller entry and keep moving.",
        "The point is not zero fear but steady forward agency.",
    ]

    for ch in range(n_chapters):
        slots = ["STORY", "REFLECTION", "INTEGRATION"]
        if ch % 2 == 1:
            slots.insert(2, "EXERCISE")
        chapter_slot_sequence.append(slots)

        for si, slot_type in enumerate(slots):
            aid = f"{slot_type.lower()}_{ch}_{si}"
            atom_ids.append(aid)
            stage_idx = min(ch, len(story_stages) - 1)
            atom_meta[aid] = {
                "identity_stage": story_stages[stage_idx],
                "mechanism_depth": min(ch + 1, 4),
                "cost_intensity": min(ch + 1, 4),
            }
            if good:
                if slot_type == "STORY":
                    prose_map[aid] = f"Story chapter {ch + 1}. Concrete scene with stakes."
                elif slot_type == "REFLECTION":
                    prose_map[aid] = varied_claims[ch % len(varied_claims)] + " This chapter gives one clear frame."
                elif slot_type == "EXERCISE":
                    prose_map[aid] = "Practice this now. Exhale once and choose one small next step."
                elif slot_type == "INTEGRATION":
                    if ch == n_chapters - 1:
                        prose_map[aid] = (
                            "This is not about eliminating alarm but building choice under load. "
                            "From now on, choose one next step and practice it daily."
                        )
                    else:
                        prose_map[aid] = "Integration line that lands the chapter."
            else:
                prose_map[aid] = "Generic filler text with no specific craft signals."

    # Emotional curve: rise-peak-dip-resolve pattern that satisfies macro cadence.
    # Macro cadence requires: every intensity 4/5 followed within 2 chapters by regulation;
    # at least one relief in second half; last chapter must be <= 3 (no regulation needed after it).
    # Pattern for 6 chapters: [2, 3, 4, 3, 4, 2] — peak, relief, peak, final relief.
    if n_chapters <= 4:
        band_seq = [2, 3, 3, 2][:n_chapters]
    elif n_chapters <= 6:
        band_seq = [2, 3, 4, 3, 4, 2][:n_chapters]
    else:
        # General pattern: ramp up, peak at midpoint, alternate high/relief, end low
        band_seq = []
        for i in range(n_chapters):
            if i < n_chapters // 3:
                band_seq.append(min(i + 2, 4))
            elif i < 2 * n_chapters // 3:
                band_seq.append(4 if i % 2 == 0 else 2)
            elif i == n_chapters - 1:
                band_seq.append(2)  # final chapter always low for macro cadence
            else:
                band_seq.append(3 if i % 2 == 0 else 2)
    emotional_curve = list(band_seq)

    plan = {
        "chapter_slot_sequence": chapter_slot_sequence,
        "atom_ids": atom_ids,
        "dominant_band_sequence": band_seq,
        "emotional_curve": emotional_curve,
        "exercise_chapters": [i for i in range(n_chapters) if i % 2 == 1],
    }
    return plan, atom_meta, prose_map


# ── Test: Craft gate config file exists ──


class TestCraftGateConfig:
    def test_config_file_exists(self):
        cfg_path = REPO_ROOT / "config" / "quality" / "bestseller_craft_gate.yaml"
        assert cfg_path.exists(), f"Missing config: {cfg_path}"

    def test_config_has_required_keys(self):
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")
        cfg_path = REPO_ROOT / "config" / "quality" / "bestseller_craft_gate.yaml"
        with open(cfg_path) as f:
            data = yaml.safe_load(f)
        craft = data.get("bestseller_craft", {})
        assert "fail_below" in craft
        assert "warn_below" in craft
        assert "orient_word_span" in craft
        assert "enforcement" in craft

    def test_config_thresholds_are_sane(self):
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")
        cfg_path = REPO_ROOT / "config" / "quality" / "bestseller_craft_gate.yaml"
        with open(cfg_path) as f:
            data = yaml.safe_load(f)
        craft = data.get("bestseller_craft", {})
        assert 0.0 < craft["fail_below"] < craft["warn_below"] < 1.0


# ── Test: Craft gate + Book pass gate work on same fixture ──


class TestCraftAndBookPassCombined:
    def test_well_crafted_chapter_passes_craft_gate(self):
        result = evaluate_bestseller_craft(WELL_CRAFTED_CHAPTER)
        assert result.status == "PASS"
        for move, score in result.move_scores.items():
            assert score >= 0.4, f"{move} scored {score}, expected >= 0.4"

    def test_abstract_chapter_fails_craft_gate(self):
        result = evaluate_bestseller_craft(ABSTRACT_CHAPTER)
        assert result.status in ("FAIL", "WARN")
        assert result.move_scores["orient"] < 0.3

    def test_book_pass_gate_varied_plan_passes(self):
        plan, meta, prose = _make_plan_and_prose(6, good=True)
        result = validate_book_pass(plan, meta, prose_map=prose)
        assert result.valid is True, f"Expected pass, errors: {result.errors}"

    def test_book_pass_gate_tier_alignment(self):
        """Verify tier thresholds load correctly for different chapter counts."""
        micro = get_tier_thresholds(4)
        standard = get_tier_thresholds(10)
        deep = get_tier_thresholds(20)
        assert micro["min_distinct_bands"] < standard["min_distinct_bands"]
        assert deep["min_bestseller_structures_distinct"] > standard["min_bestseller_structures_distinct"]


# ── Test: Bestseller editor report includes craft gate ──


class TestEditorReportCraftGateWiring:
    def test_editor_report_includes_craft_gate_field(self, tmp_path: Path):
        """build_bestseller_editor_report should include craft_gate and craft_gate_status."""
        from phoenix_v4.qa.bestseller_editor import build_bestseller_editor_report

        # Write minimal chapter_flow_report.json and budget.json
        (tmp_path / "chapter_flow_report.json").write_text(
            json.dumps({
                "chapter_count": 1,
                "status": "PASS",
                "chapters": [{"chapter": 1, "status": "PASS", "score": 100, "errors": []}],
                "dimension_gates_status": "SKIP",
                "dimension_gates_blocks_delivery": False,
            }),
            encoding="utf-8",
        )
        (tmp_path / "budget.json").write_text(json.dumps({}), encoding="utf-8")

        plan = {"plan_hash": "test", "atom_ids": [], "chapter_slot_sequence": []}
        report = build_bestseller_editor_report(plan, tmp_path)

        assert "craft_gate" in report, "craft_gate missing from editor report"
        assert "craft_gate_status" in report, "craft_gate_status missing from editor report"
        assert report["craft_gate_status"] in ("PASS", "WARN", "FAIL", "SKIP")

    def test_craft_gate_directly_fails_abstract_text(self):
        """The ONTGP craft gate should FAIL or WARN on abstract-only prose."""
        result = evaluate_bestseller_craft(ABSTRACT_CHAPTER)
        assert result.status in ("FAIL", "WARN")
        # Orient should be low for abstract opener
        assert result.move_scores["orient"] < 0.3

    def test_craft_gate_status_included_in_overall_status_computation(self):
        """Verify _summarize_status correctly propagates craft gate FAIL."""
        from phoenix_v4.qa.bestseller_editor import _summarize_status
        # If craft_status is FAIL, overall must be FAIL
        assert _summarize_status("PASS", "PASS", "PASS", "PASS", "PASS", "PASS", "FAIL") == "FAIL"
        # If craft_status is WARN, overall must be at least WARN
        assert _summarize_status("PASS", "PASS", "PASS", "PASS", "PASS", "PASS", "WARN") == "WARN"


# ── Test: All quality configs present ──


class TestQualityConfigCompleteness:
    """Verify all quality gate config files exist."""

    EXPECTED_CONFIGS = [
        "config/quality/book_pass_gate_thresholds.yaml",
        "config/quality/ei_v2_config.yaml",
        "config/quality/bestseller_craft_gate.yaml",
        "config/creative_quality_v1.yaml",
    ]

    @pytest.mark.parametrize("config_path", EXPECTED_CONFIGS)
    def test_config_exists(self, config_path: str):
        full_path = REPO_ROOT / config_path
        assert full_path.exists(), f"Missing quality config: {full_path}"

    def test_ei_v2_dimension_gates_configured(self):
        """EI v2 config should have dimension_gates with at least 3 blocked dimensions."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")
        cfg_path = REPO_ROOT / "config" / "quality" / "ei_v2_config.yaml"
        with open(cfg_path) as f:
            data = yaml.safe_load(f)
        dg = data.get("dimension_gates", {})
        assert dg.get("enabled") is True
        blocked = dg.get("blocked_dimensions", [])
        assert len(blocked) >= 3, f"Expected at least 3 blocked dimensions, got {blocked}"


# ── Test: Craft gate deterministic ──


class TestCraftGateDeterminism:
    def test_same_input_same_output(self):
        a = evaluate_bestseller_craft(WELL_CRAFTED_CHAPTER)
        b = evaluate_bestseller_craft(WELL_CRAFTED_CHAPTER)
        assert a.status == b.status
        assert a.move_scores == b.move_scores
        assert a.issues == b.issues

    def test_empty_input_fails_cleanly(self):
        result = evaluate_bestseller_craft("")
        assert result.status == "FAIL"
        assert "empty_chapter" in result.issues

    def test_short_input_produces_low_scores(self):
        result = evaluate_bestseller_craft("One short sentence.")
        assert result.status == "FAIL"
        assert all(s < 0.3 for s in result.move_scores.values())
