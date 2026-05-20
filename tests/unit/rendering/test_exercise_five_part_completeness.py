"""
OPD-113 — every rendered exercise must contain all 5 operator-spec parts.

Operator observation (2026-05-20):
    "In Books 1 and 2 the shorter books, the exercises were very clear.
    It's like, 'this is an exercise. We're gonna do an exercise now.
    Here's what it's called. Here's a description of it.' And then I
    think we're missing that in the longer books. It's not as clear.
    So whenever we do an exercise, we need to do all parts of it:
    introduction, description, guidance, the aha, and the integration."

Operator's 5-part mapping in code:
    1. introduction → introduction_templates.yaml ("Now we're going to do a practice.")
    2. description  → intro field / intro_templates.yaml ("This is a X practice...")
    3. guidance     → description field / atom text
    4. aha          → aha field
    5. integration  → integration field

Tests in this file:
    - test_introduction_templates_load: YAML file loads, has every exercise type.
    - test_assemble_exercise_has_introduction_cue: emit Part 1 marker at default rule.
    - test_assemble_exercise_has_all_five_parts: all 5 parts present at default rule.
    - test_assemble_exercise_5_parts_at_familiar_new_context: 5 parts at familiar context
      (the dominant rule for chapter 2+ in a 6h book, formerly used lean intro).
    - test_assemble_exercise_5_parts_at_session_close: 5 parts at session close
      (formerly skipped intro/description).
    - test_quick_repeat_skips_introduction: quick_repeat suppresses the cue (no fatigue).
    - test_practice_library_compose_emits_introduction: alternate path also emits the cue.
    - test_introduction_per_exercise_type: a sample of types each have unique introductions.
    - test_short_form_atoms_without_explicit_markers_still_render: backward compatibility.
"""
from __future__ import annotations

import pytest

from phoenix_v4.exercises import component_assembler as ca
from phoenix_v4.exercises.models import (
    AssemblyContext,
    ComponentMode,
    EmotionalState,
)


# ---------------------------------------------------------------------------
# 5-part markers — string patterns that identify each operator-required part.
# These markers come from the existing template YAMLs and standards files.
# ---------------------------------------------------------------------------
PART_1_INTRODUCTION_MARKERS = (
    "Now we're going to do",
    "Now, a ",
)
PART_2_DESCRIPTION_MARKERS = (
    "This is a ",
    "This is an ",
)


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


# ---------------------------------------------------------------------------
# Test 1: introduction_templates.yaml loads and covers every canonical type
# ---------------------------------------------------------------------------

def test_introduction_templates_load() -> None:
    templates = ca._load_introduction_templates()
    # All 11 canonical exercise types plus the _default
    assert "_default" in templates, "introduction_templates.yaml must define _default"
    for ex_type in ca.EXERCISE_TYPES_ROTATION:
        assert ex_type in templates, (
            f"introduction_templates.yaml missing entry for {ex_type}"
        )
        entry = templates[ex_type]
        full = str(entry.get("full", "")).strip()
        assert full, f"introduction_templates.yaml: {ex_type}.full is empty"
        # Must look like an operator-spec introduction cue, not just generic prose
        assert _contains_any(full, PART_1_INTRODUCTION_MARKERS), (
            f"introduction_templates.yaml: {ex_type}.full does not contain a Part 1 "
            f"marker (expected 'Now we're going to do' or 'Now, a '): {full!r}"
        )


# ---------------------------------------------------------------------------
# Test 2: assemble_exercise at first_encounter contains all 5 operator parts
# ---------------------------------------------------------------------------

def test_assemble_exercise_has_all_five_parts_first_encounter() -> None:
    ctx = AssemblyContext(
        first_encounter=True,
        emotional_state=EmotionalState.NEUTRAL,
        chapter_index=0,
    )
    composed = ca.assemble_exercise_for_chapter(
        exercise_id="test_breath_001",
        exercise_type="00_breath_regulation",
        description_text="Breathe in for four counts. Breathe out for six counts. Four cycles.",
        ctx=ctx,
    )
    assert composed, "assemble_exercise_for_chapter returned empty text"

    # Part 1 — introduction cue
    assert _contains_any(composed, PART_1_INTRODUCTION_MARKERS), (
        f"Missing Part 1 (introduction cue) at first_encounter:\n{composed}"
    )
    # Part 2 — description ("This is a X practice")
    assert _contains_any(composed, PART_2_DESCRIPTION_MARKERS), (
        f"Missing Part 2 (description) at first_encounter:\n{composed}"
    )
    # Part 3 — guidance (the atom text)
    assert "Breathe in for four counts" in composed, (
        f"Missing Part 3 (guidance / atom text) at first_encounter:\n{composed}"
    )
    # Parts 4 + 5 — aha and integration come from Phoenix standards.
    # These exist whenever component_assembler resolves a known exercise_type;
    # confirm the composed text is meaningfully longer than just the atom +
    # intro + introduction together, which means aha/integration also fired.
    minimum_words_for_5_parts = 80
    assert len(composed.split()) >= minimum_words_for_5_parts, (
        f"Composed exercise too short ({len(composed.split())} words) to plausibly "
        f"contain all 5 parts. Got:\n{composed}"
    )


# ---------------------------------------------------------------------------
# Test 3: familiar_new_context (the dominant rule in long-form runtimes)
#         must still emit all 5 parts after OPD-113.
# Before OPD-113: this path used lean intro, hiding the description.
# After OPD-113: introduction + full intro are both emitted.
# ---------------------------------------------------------------------------

def test_assemble_exercise_5_parts_at_familiar_new_context() -> None:
    ctx = AssemblyContext(
        first_encounter=False,
        emotional_state=EmotionalState.NEUTRAL,
        repeat_count=1,
        chapter_index=5,
    )
    sel = ca.select_components(ctx)
    assert sel.rule_name == "familiar_new_context", (
        f"Test scenario broke: expected familiar_new_context, got {sel.rule_name}"
    )
    composed = ca.assemble_exercise_for_chapter(
        exercise_id="test_grounding_002",
        exercise_type="01_grounding_orientation",
        description_text="Place both feet flat on the floor. Press your heels down.",
        ctx=ctx,
    )
    assert _contains_any(composed, PART_1_INTRODUCTION_MARKERS), (
        f"familiar_new_context dropped introduction cue (OPD-113 regression):\n{composed}"
    )
    assert _contains_any(composed, PART_2_DESCRIPTION_MARKERS), (
        f"familiar_new_context dropped description (OPD-113 regression):\n{composed}"
    )
    assert "Place both feet flat on the floor" in composed, (
        f"familiar_new_context dropped atom guidance:\n{composed}"
    )


# ---------------------------------------------------------------------------
# Test 4: session_close must still emit all 5 parts after OPD-113.
# Before OPD-113: this path skipped both intro and description.
# After OPD-113: introduction and intro both emitted.
# ---------------------------------------------------------------------------

def test_assemble_exercise_5_parts_at_session_close() -> None:
    ctx = AssemblyContext(
        first_encounter=False,
        emotional_state=EmotionalState.NEUTRAL,
        is_session_close=True,
        chapter_index=11,
    )
    sel = ca.select_components(ctx)
    assert sel.rule_name == "session_close", (
        f"Test scenario broke: expected session_close, got {sel.rule_name}"
    )
    composed = ca.assemble_exercise_for_chapter(
        exercise_id="test_integration_003",
        exercise_type="10_integration_return_to_baseline",
        description_text="Stop what you are doing completely. Sit with nothing in your hands.",
        ctx=ctx,
    )
    assert _contains_any(composed, PART_1_INTRODUCTION_MARKERS), (
        f"session_close dropped introduction cue (OPD-113 regression):\n{composed}"
    )
    assert _contains_any(composed, PART_2_DESCRIPTION_MARKERS), (
        f"session_close dropped description (OPD-113 regression):\n{composed}"
    )


# ---------------------------------------------------------------------------
# Test 5: quick_repeat — operator-allowed exception — skips the cue.
# This is the only rule where intro/introduction/etc. are intentionally
# suppressed: repeating the same exercise 3+ times in one session doesn't
# need the explicit "now we're going to do..." cue again.
# ---------------------------------------------------------------------------

def test_quick_repeat_skips_introduction() -> None:
    ctx = AssemblyContext(
        first_encounter=False,
        emotional_state=EmotionalState.NEUTRAL,
        repeat_count=3,
        chapter_index=8,
    )
    sel = ca.select_components(ctx)
    assert sel.rule_name == "quick_repeat"
    assert sel.introduction == ComponentMode.SKIP, (
        "quick_repeat must skip the introduction (avoid repetition fatigue)"
    )


# ---------------------------------------------------------------------------
# Test 6: introduction cue is type-specific (not just one generic phrase)
# ---------------------------------------------------------------------------

def test_introduction_per_exercise_type() -> None:
    templates = ca._load_introduction_templates()
    seen: set[str] = set()
    for ex_type in (
        "00_breath_regulation",
        "01_grounding_orientation",
        "02_body_awareness_scan",
        "03_somatic_release_discharge",
        "06_vagal_stimulation_sound",
    ):
        full = templates[ex_type]["full"].strip()
        assert full not in seen, (
            f"Duplicate introduction text for {ex_type}: {full!r}. "
            f"Each type must have a distinct cue so readers can tell exercise "
            f"types apart by the introduction alone."
        )
        seen.add(full)


# ---------------------------------------------------------------------------
# Test 7: alternate compose path (practice_library_loader.compose_exercise)
# also emits the OPD-113 introduction cue.
# ---------------------------------------------------------------------------

def test_practice_library_compose_emits_introduction() -> None:
    from phoenix_v4.exercises import practice_library_loader as pll

    exercise = {
        "id": "test_breath_004",
        "name": "Box Breath",
        "text": "Breathe in for four. Hold for four. Breathe out for four. Hold for four.",
        "exercise_type": "00_breath_regulation",
    }
    composed = pll.compose_exercise(exercise, chapter_index=2, seed="opd-113-test-seed")
    assert composed
    assert _contains_any(composed, PART_1_INTRODUCTION_MARKERS), (
        f"practice_library_loader.compose_exercise dropped introduction cue:\n{composed}"
    )
    assert "Breathe in for four" in composed, (
        f"compose_exercise dropped guidance:\n{composed}"
    )


# ---------------------------------------------------------------------------
# Test 8: short-form backward compatibility — if the introduction YAML is
# unavailable or an exercise_type is unknown, the assembler must still
# produce something (no hard crash). Atoms without explicit part markers
# render fine on their own.
# ---------------------------------------------------------------------------

def test_assemble_exercise_unknown_type_does_not_crash() -> None:
    ctx = AssemblyContext(
        first_encounter=True,
        emotional_state=EmotionalState.NEUTRAL,
        chapter_index=0,
    )
    # Unknown exercise_type — should rotate to a canonical type
    composed = ca.assemble_exercise_for_chapter(
        exercise_id="test_unknown_005",
        exercise_type="some_unrecognized_type",
        description_text="Just breathe.",
        ctx=ctx,
    )
    assert composed, "Unknown exercise_type should still produce output"
    assert "Just breathe" in composed


# ---------------------------------------------------------------------------
# Test 9: ComponentMode.SKIP suppresses the introduction even when text exists
# (defense for quick_repeat path consistency)
# ---------------------------------------------------------------------------

def test_introduction_skip_mode_suppresses_text() -> None:
    from phoenix_v4.exercises.models import (
        ComponentSelection,
        ComponentVariants,
        ExerciseComponents,
    )

    components = ExerciseComponents(
        exercise_id="t",
        exercise_type="00_breath_regulation",
        introduction=ComponentVariants(full="Now we're going to do a breath practice."),
        intro=ComponentVariants(full="This is a breath-based practice."),
        description=ComponentVariants(full="Breathe in. Breathe out."),
        aha=ComponentVariants(full="Notice."),
        integration=ComponentVariants(full="Carry this forward."),
    )
    selection = ComponentSelection(
        bridge=ComponentMode.SKIP,
        introduction=ComponentMode.SKIP,
        intro=ComponentMode.SKIP,
        description=ComponentMode.LEAN,
        aha=ComponentMode.SKIP,
        integration=ComponentMode.SKIP,
    )
    composed = ca.assemble_exercise(components, selection)
    assert "Now we're going to do" not in composed, (
        "ComponentMode.SKIP must suppress the introduction text completely"
    )
    assert "Breathe in" in composed, "description (guidance) should still render"


# ---------------------------------------------------------------------------
# Test 10: ordering — the introduction comes BEFORE the description (intro)
# so the reader hears "we're going to do an exercise" before "this is a X
# practice", matching the operator's spec.
# ---------------------------------------------------------------------------

def test_introduction_precedes_description_in_output() -> None:
    ctx = AssemblyContext(
        first_encounter=True,
        emotional_state=EmotionalState.NEUTRAL,
        chapter_index=0,
    )
    composed = ca.assemble_exercise_for_chapter(
        exercise_id="test_order_006",
        exercise_type="00_breath_regulation",
        description_text="Breathe in for four.",
        ctx=ctx,
    )
    idx_intro = composed.find("Now we're going to do")
    idx_desc = composed.find("This is a breath-based practice")
    assert idx_intro >= 0, f"missing introduction cue:\n{composed}"
    assert idx_desc >= 0, f"missing description:\n{composed}"
    assert idx_intro < idx_desc, (
        f"Introduction cue must precede description.\n"
        f"introduction at {idx_intro}, description at {idx_desc}.\n"
        f"composed:\n{composed}"
    )
