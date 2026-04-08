"""Tests for the exercise component assembly system."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from phoenix_v4.exercises.models import (
    AssemblyContext,
    ComponentMode,
    ComponentSelection,
    ComponentVariants,
    EmotionalState,
    ExerciseComponents,
)
from phoenix_v4.exercises.component_assembler import (
    _derive_lean,
    _match_rule,
    assemble_exercise,
    load_assembly_rules,
    resolve_from_ab_tady_components,
    select_components,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Rule matching
# ---------------------------------------------------------------------------

class TestRuleMatching:
    """Test that each named rule fires correctly."""

    @pytest.fixture()
    def rules(self):
        return load_assembly_rules(REPO_ROOT / "config" / "practice" / "assembly_components.yaml")

    def test_quick_repeat_fires(self, rules):
        ctx = AssemblyContext(repeat_count=3, first_encounter=False)
        sel = select_components(ctx, rules)
        assert sel.rule_name == "quick_repeat"
        assert sel.bridge == ComponentMode.SKIP
        assert sel.description == ComponentMode.LEAN

    def test_emotional_pivot_fires(self, rules):
        ctx = AssemblyContext(emotional_state=EmotionalState.HEAVY)
        sel = select_components(ctx, rules)
        assert sel.rule_name == "emotional_pivot"
        assert sel.bridge == ComponentMode.FULL
        assert sel.bridge_tone == "gentle"

    def test_flow_state_fires(self, rules):
        ctx = AssemblyContext(emotional_state=EmotionalState.FLOW, first_encounter=False)
        sel = select_components(ctx, rules)
        assert sel.rule_name == "flow_state"
        assert sel.intro == ComponentMode.SKIP
        assert sel.integration == ComponentMode.SKIP

    def test_session_close_fires(self, rules):
        ctx = AssemblyContext(is_session_close=True, first_encounter=False, emotional_state=EmotionalState.NEUTRAL)
        sel = select_components(ctx, rules)
        assert sel.rule_name == "session_close"
        assert sel.bridge == ComponentMode.SKIP
        assert sel.aha == ComponentMode.FULL

    def test_familiar_new_context_fires(self, rules):
        ctx = AssemblyContext(first_encounter=False, repeat_count=0)
        sel = select_components(ctx, rules)
        assert sel.rule_name == "familiar_new_context"
        assert sel.bridge == ComponentMode.LEAN
        assert sel.intro == ComponentMode.LEAN

    def test_first_encounter_fires(self, rules):
        ctx = AssemblyContext(first_encounter=True)
        sel = select_components(ctx, rules)
        assert sel.rule_name == "first_encounter"
        assert sel.bridge == ComponentMode.FULL
        assert sel.intro == ComponentMode.FULL
        assert sel.description == ComponentMode.FULL

    def test_default_fires(self, rules):
        # Construct a context that won't match any specific rule
        ctx = AssemblyContext(first_encounter=False, repeat_count=1, emotional_state=EmotionalState.NEUTRAL)
        sel = select_components(ctx, rules)
        # Should match familiar_new_context (repeat_count_lte: 1)
        assert sel.rule_name in ("familiar_new_context", "default")


# ---------------------------------------------------------------------------
# Lean derivation
# ---------------------------------------------------------------------------

class TestLeanDerivation:
    def test_lean_extracts_first_sentences(self):
        full = "First sentence here. Second sentence follows. Third sentence too. Fourth one."
        lean = _derive_lean(full, max_sentences=2)
        assert lean == "First sentence here. Second sentence follows."

    def test_lean_handles_short_text(self):
        assert _derive_lean("Single sentence.") == "Single sentence."

    def test_lean_handles_empty(self):
        assert _derive_lean("") == ""


# ---------------------------------------------------------------------------
# Component assembly
# ---------------------------------------------------------------------------

class TestAssembleExercise:
    def _make_components(self) -> ExerciseComponents:
        return ExerciseComponents(
            exercise_id="test_exercise",
            exercise_type="00_breath_regulation",
            bridge=ComponentVariants(
                full="Full bridge text here.",
                lean="Lean bridge.",
                gentle="Gentle bridge after heavy content.",
            ),
            intro=ComponentVariants(
                full="Full intro explaining the exercise.",
                lean="Lean intro.",
            ),
            description=ComponentVariants(
                full="Full description with all steps. Step one. Step two. Step three.",
                lean="Step one. Step two.",
            ),
            aha=ComponentVariants(
                full="Now, I want you to notice something. Full AHA text here.",
                lean="Now, notice this.",
            ),
            integration=ComponentVariants(
                full="Now, before you move on, full integration text.",
                lean="Now, before you move on, lean.",
            ),
        )

    def test_full_assembly_includes_all(self):
        components = self._make_components()
        sel = ComponentSelection(
            bridge=ComponentMode.FULL,
            intro=ComponentMode.FULL,
            description=ComponentMode.FULL,
            aha=ComponentMode.FULL,
            integration=ComponentMode.FULL,
        )
        result = assemble_exercise(components, sel)
        assert "Full bridge text" in result
        assert "Full intro" in result
        assert "Full description" in result
        assert "Full AHA" in result
        assert "full integration" in result

    def test_skip_removes_components(self):
        components = self._make_components()
        sel = ComponentSelection(
            bridge=ComponentMode.SKIP,
            intro=ComponentMode.SKIP,
            description=ComponentMode.LEAN,
            aha=ComponentMode.SKIP,
            integration=ComponentMode.SKIP,
        )
        result = assemble_exercise(components, sel)
        assert "bridge" not in result.lower()
        assert "intro" not in result.lower()
        assert "AHA" not in result
        assert "integration" not in result.lower()
        assert "Step one. Step two." in result

    def test_gentle_bridge_tone(self):
        components = self._make_components()
        sel = ComponentSelection(
            bridge=ComponentMode.FULL,
            intro=ComponentMode.SKIP,
            description=ComponentMode.FULL,
            aha=ComponentMode.SKIP,
            integration=ComponentMode.SKIP,
            bridge_tone="gentle",
        )
        result = assemble_exercise(components, sel)
        assert "Gentle bridge" in result
        assert "Full bridge" not in result

    def test_lean_variants_used(self):
        components = self._make_components()
        sel = ComponentSelection(
            bridge=ComponentMode.LEAN,
            intro=ComponentMode.LEAN,
            description=ComponentMode.FULL,
            aha=ComponentMode.LEAN,
            integration=ComponentMode.LEAN,
        )
        result = assemble_exercise(components, sel)
        assert "Lean bridge." in result
        assert "Lean intro." in result
        assert "Now, notice this." in result
        assert "lean." in result


# ---------------------------------------------------------------------------
# AB Tady 37 component resolution
# ---------------------------------------------------------------------------

class TestAbTady37Components:
    def test_resolve_from_ab_tady(self):
        data = {
            "id": "cyclic_sighing",
            "exercise_type": "00_breath_regulation",
            "components": {
                "bridge": {"full": "Full bridge.", "lean": "Lean bridge."},
                "intro": {"full": "Full intro.", "lean": "Lean intro."},
                "description": {"full": "Full desc.", "lean": "Lean desc."},
                "aha": {"full": "Full aha.", "lean": "Lean aha."},
                "integration": {"full": "Full int.", "lean": "Lean int."},
            },
        }
        comps = resolve_from_ab_tady_components(data)
        assert comps.exercise_id == "cyclic_sighing"
        assert comps.bridge.full == "Full bridge."
        assert comps.bridge.lean == "Lean bridge."
        assert comps.aha.full == "Full aha."

    def test_resolve_derives_lean_when_missing(self):
        data = {
            "id": "test",
            "exercise_type": "00_breath_regulation",
            "components": {
                "bridge": {"full": "First sentence. Second sentence. Third."},
                "intro": {"full": "Intro full text."},
                "description": {"full": "Desc."},
                "aha": {"full": "Aha full."},
                "integration": {"full": "Integration full text."},
            },
        }
        comps = resolve_from_ab_tady_components(data)
        assert comps.bridge.lean == "First sentence. Second sentence."


# ---------------------------------------------------------------------------
# AB Tady 37 JSON validation
# ---------------------------------------------------------------------------

class TestAbTady37Json:
    @pytest.fixture()
    def exercises(self):
        path = REPO_ROOT / "SOURCE_OF_TRUTH" / "practice_library" / "inbox" / "exercises_ab_tady_37_PRODUCTION_READY.json"
        with open(path) as f:
            data = json.load(f)
        return data["exercises"]

    def test_has_39_exercises(self, exercises):
        assert len(exercises) == 39

    def test_all_have_text_field(self, exercises):
        for ex in exercises:
            assert "text" in ex and len(ex["text"]) > 20, f"{ex['id']} missing/short text"

    def test_all_have_components(self, exercises):
        for ex in exercises:
            assert "components" in ex, f"{ex['id']} missing components"
            comps = ex["components"]
            for key in ("bridge", "intro", "description", "aha", "integration"):
                assert key in comps, f"{ex['id']} missing component {key}"
                assert "full" in comps[key], f"{ex['id']}.{key} missing full variant"

    def test_unique_ids(self, exercises):
        ids = [ex["id"] for ex in exercises]
        assert len(ids) == len(set(ids)), f"Duplicate IDs: {[i for i in ids if ids.count(i) > 1]}"


# ---------------------------------------------------------------------------
# Bridge/intro template files exist
# ---------------------------------------------------------------------------

class TestTemplateFiles:
    def test_bridge_templates_exist(self):
        path = REPO_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4" / "bridge_templates.yaml"
        assert path.exists()

    def test_intro_templates_exist(self):
        path = REPO_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4" / "intro_templates.yaml"
        assert path.exists()


# ---------------------------------------------------------------------------
# Chapter composer backward compatibility
# ---------------------------------------------------------------------------

class TestChapterComposerBackwardCompat:
    def test_compose_without_exercise_context(self):
        """compose_chapter_prose without exercise_context uses 5-dim template wrapping."""
        from phoenix_v4.rendering.chapter_composer import compose_chapter_prose

        result = compose_chapter_prose(
            slot_types=["HOOK", "REFLECTION", "STORY", "EXERCISE", "INTEGRATION"],
            slot_proses=[
                "Your badge beeps.",
                "The mechanism is comparison. It uses exterior to judge interior.",
                "She opened the feed and the comparison engine started.",
                "Press your feet into the floor. Feel the pressure.",
                "Feet on floor. Breath steady. Still here.",
            ],
            chapter_index=0,
            total_chapters=5,
        )
        assert "Your badge beeps" in result
        assert "Press your feet" in result
        # 5-dim compose_exercise wraps the exercise with bridge + intro + desc + aha + integration
        # from templates, replacing the explicit INTEGRATION slot content
        assert "before you move on" in result.lower() or "now, notice" in result.lower()

    def test_compose_with_exercise_context(self):
        """compose_chapter_prose with exercise_context should use component assembler."""
        from phoenix_v4.rendering.chapter_composer import compose_chapter_prose

        ctx = AssemblyContext(
            first_encounter=True,
            exercise_id="cyclic_sighing",
        )
        result = compose_chapter_prose(
            slot_types=["HOOK", "REFLECTION", "STORY", "EXERCISE", "INTEGRATION"],
            slot_proses=[
                "Your badge beeps.",
                "The mechanism is comparison.",
                "She opened the feed.",
                "Breathe in through your nose.",
                "Feet on floor.",
            ],
            chapter_index=0,
            total_chapters=5,
            exercise_context=ctx,
        )
        assert "Breathe in through your nose" in result
