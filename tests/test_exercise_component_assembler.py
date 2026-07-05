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
    _sentences,
    assemble_exercise,
    assemble_exercise_for_chapter,
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
        # Operator directive (2026-05-29): lean is disabled. quick_repeat used
        # to skip every wrapper and lean the description; it now renders the
        # full 5-part structure so a repeated exercise is never truncated.
        assert sel.bridge == ComponentMode.FULL
        assert sel.introduction == ComponentMode.FULL
        assert sel.intro == ComponentMode.FULL
        assert sel.description == ComponentMode.FULL
        assert sel.aha == ComponentMode.FULL
        assert sel.integration == ComponentMode.FULL

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
        # Operator directive (2026-05-29): lean is disabled — the bridge now
        # resolves to FULL (was LEAN).
        assert sel.bridge == ComponentMode.FULL
        # OPD-113: intro changed from LEAN to FULL so the named description
        # ("This is a X practice...") is always visible in long-form runtimes.
        assert sel.intro == ComponentMode.FULL
        # OPD-113: introduction (Part 1 cue) is always emitted for non-repeat paths.
        assert sel.introduction == ComponentMode.FULL

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
    """Operator directive (2026-05-29): lean derivation is disabled — every
    helper that used to truncate now returns the full text verbatim so no
    STORY or EXERCISE is ever shortened."""

    def test_lean_returns_full_text_unchanged(self):
        full = "First sentence here. Second sentence follows. Third sentence too. Fourth one."
        # Even with max_sentences=2, lean is a no-op and returns the full text.
        assert _derive_lean(full, max_sentences=2) == full

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
            introduction=ComponentMode.SKIP,
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
        # Operator directive (2026-05-29): LEAN is a no-op → the description
        # renders in FULL (all steps), never truncated to the lean variant.
        assert "Full description with all steps. Step one. Step two. Step three." in result

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

    def test_lean_mode_renders_full(self):
        """Operator directive (2026-05-29): LEAN is a no-op — every component
        requested in LEAN mode renders its FULL variant, never the lean one."""
        components = self._make_components()
        sel = ComponentSelection(
            bridge=ComponentMode.LEAN,
            introduction=ComponentMode.SKIP,
            intro=ComponentMode.LEAN,
            description=ComponentMode.FULL,
            aha=ComponentMode.LEAN,
            integration=ComponentMode.LEAN,
        )
        result = assemble_exercise(components, sel)
        # FULL variants are emitted even though LEAN was requested.
        assert "Full bridge text here." in result
        assert "Full intro explaining the exercise." in result
        assert "Full AHA text here." in result
        assert "full integration text." in result
        # The lean strings must NOT appear.
        assert "Lean bridge." not in result
        assert "Lean intro." not in result


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

    def test_resolve_lean_equals_full_when_missing(self):
        # Operator directive (2026-05-29): lean derivation is disabled, so when
        # no explicit lean variant is provided the derived lean equals the full
        # text verbatim (no truncation).
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
        assert comps.bridge.lean == "First sentence. Second sentence. Third."


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
    def test_compose_without_exercise_context(self, monkeypatch: pytest.MonkeyPatch):
        """compose_chapter_prose without exercise_context uses 5-dim template wrapping."""
        monkeypatch.setenv("PHOENIX_ENABLE_RENDER_GLUE", "1")
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
        # Assembler + Phoenix standards (aha/integration) or legacy template wrap
        rl = result.lower()
        assert (
            "before you move on" in rl
            or "now, notice" in rl
            or "now, take a moment" in rl
            or "now, pause" in rl
            or "now, reflect" in rl
        )

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


# ---------------------------------------------------------------------------
# Operator directive (2026-05-29): EXERCISE never leans on any path
# ---------------------------------------------------------------------------

class TestExerciseNeverLeans:
    """The legacy registry render path supplies a book-global repeat_count, so
    from the 3rd exercise-bearing chapter onward `quick_repeat` used to fire and
    collapse the exercise to its first 3 setup sentences. Operator directive:
    every exercise renders FULL on every path. These tests use the real
    gen_z_professionals × anxiety box-breathing atom (EXERCISE v01, 13 authored
    guidance sentences) to prove the lean is gone.
    """

    # EXERCISE v01 — box breathing — the exact atom from the D1 investigation.
    BOX_BREATHING = (
        "Sit back from your screen. Place both feet flat on the floor. "
        "Feel your heels make contact. Breathe in for four counts. "
        "Hold for four counts. Breathe out for four counts. "
        "Hold for four counts. That is one cycle. Do not rush the holds. "
        "Keep the counts even. Complete four cycles. On the fourth exhale, "
        "let your shoulders drop before you breathe in again. "
        "Return to the screen after the fourth cycle."
    )

    # The atom guidance is 13 sentences; lean (the old defect) kept only 3.
    FULL_SENTENCE_COUNT = 13
    OLD_LEAN_SENTENCE_COUNT = 3

    def _assemble_legacy_repeat(self, repeat_count: int) -> str:
        """Assemble the box-breathing exercise via the legacy path with a
        book-global repeat_count (chapter 3+ on the registry render path)."""
        ctx = AssemblyContext(
            first_encounter=False,        # chapter-0-only is True; ch3+ is False
            repeat_count=repeat_count,    # legacy book-global count → quick_repeat used to fire
            chapter_index=3,
            exercise_id="gen_z_professionals_anxiety_box_breathing",
        )
        return assemble_exercise_for_chapter(
            exercise_id=ctx.exercise_id,
            exercise_type="00_breath_regulation",
            description_text=self.BOX_BREATHING,
            ctx=ctx,
        )

    def test_legacy_repeat_exercise_renders_full_not_lean(self):
        """repeat_count>=2 on the legacy path → quick_repeat fires, but the
        exercise renders FULL: all 13 guidance sentences are present, including
        the breathing pattern, cycle count, body cue and exit cue that the old
        lean (first 3 sentences) dropped."""
        # Confirm the rule that fires is still quick_repeat (so we are exercising
        # the exact code path that used to truncate).
        rules = load_assembly_rules(
            REPO_ROOT / "config" / "practice" / "assembly_components.yaml"
        )
        sel = select_components(
            AssemblyContext(repeat_count=3, first_encounter=False), rules
        )
        assert sel.rule_name == "quick_repeat"

        assembled = self._assemble_legacy_repeat(repeat_count=3)

        # The full atom text is present verbatim — nothing truncated.
        assert self.BOX_BREATHING in assembled

        # Sentence count of the guidance >= the atom's full count (NOT 3).
        # Count only the box-breathing portion to avoid wrapper sentences
        # inflating the number; the key is it is far more than the old lean of 3.
        guidance_sentences = _sentences(self.BOX_BREATHING)
        assert len(guidance_sentences) == self.FULL_SENTENCE_COUNT
        assembled_sentences = _sentences(assembled)
        assert len(assembled_sentences) >= self.FULL_SENTENCE_COUNT
        assert len(assembled_sentences) > self.OLD_LEAN_SENTENCE_COUNT

        # The breathing mechanics, cycle count, body cue and exit cue — all the
        # content the old lean discarded — must be present.
        for must_have in (
            "Breathe in for four counts.",
            "Hold for four counts.",
            "Breathe out for four counts.",
            "Complete four cycles.",
            "let your shoulders drop",
            "Return to the screen after the fourth cycle.",
        ):
            assert must_have in assembled, f"missing leaned-away content: {must_have!r}"

    def test_same_technique_repeat_also_full(self):
        """Because lean is disabled, even a same-technique repeat at a higher
        repeat_count renders full (the rule's anti-repetition truncation no
        longer applies)."""
        first = self._assemble_legacy_repeat(repeat_count=2)
        later = self._assemble_legacy_repeat(repeat_count=5)
        for assembled in (first, later):
            assert self.BOX_BREATHING in assembled
            assert len(_sentences(assembled)) >= self.FULL_SENTENCE_COUNT
        # The two repeats carry the same full guidance — no progressive thinning.
        assert self.BOX_BREATHING in first and self.BOX_BREATHING in later
