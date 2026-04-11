"""Tests for phoenix_v4.planning.exercise_journey_planner."""
from __future__ import annotations

import pytest

from phoenix_v4.planning.exercise_journey_planner import (
    plan_exercise_journey,
    resolve_thesis_id,
)
from phoenix_v4.planning.exercise_registry_loader import (
    load_exercise_registry,
    load_journey_templates,
    load_thesis_outcome_map,
)


@pytest.fixture
def ctx():
    return {
        "exercises": load_exercise_registry(),
        "thesis": load_thesis_outcome_map(),
        "templates": load_journey_templates(),
    }


def test_resolve_thesis_id_deterministic():
    assert resolve_thesis_id("anxiety", 1, "s") == resolve_thesis_id("anxiety", 1, "s")
    assert resolve_thesis_id("anxiety", 1, "s") != resolve_thesis_id("anxiety", 2, "s")


def test_short_book_one_phase(ctx):
    j = plan_exercise_journey(
        1,
        "anxiety_spike",
        "short_book",
        seed="t1",
        exercise_registry=ctx["exercises"],
        thesis_outcomes=ctx["thesis"],
        journey_templates=ctx["templates"],
    )
    assert j.journey_type == "1_step"
    assert len(j.phases) == 1
    assert j.phases[0].name == "awareness"


def test_standard_book_two_phases(ctx):
    j = plan_exercise_journey(
        2,
        "emotional_overwhelm",
        "standard_book",
        seed="t2",
        exercise_registry=ctx["exercises"],
        thesis_outcomes=ctx["thesis"],
        journey_templates=ctx["templates"],
    )
    assert j.journey_type == "2_step"
    assert [p.name for p in j.phases] == ["awareness", "regulation"]
    assert j.phases[0].target_section == 4
    assert j.phases[1].target_section == 8


def test_deep_book_three_phases_ordered(ctx):
    j = plan_exercise_journey(
        3,
        "burnout_pattern",
        "deep_book_6h",
        seed="t3",
        exercise_registry=ctx["exercises"],
        thesis_outcomes=ctx["thesis"],
        journey_templates=ctx["templates"],
    )
    assert j.journey_type == "3_step"
    assert [p.name for p in j.phases] == ["awareness", "regulation", "integration"]
    assert [p.target_section for p in j.phases] == [4, 8, 10]


def test_deterministic_same_inputs(ctx):
    a = plan_exercise_journey(
        5,
        "anxiety_spike",
        "standard_book",
        seed="fixed",
        exercise_registry=ctx["exercises"],
        thesis_outcomes=ctx["thesis"],
        journey_templates=ctx["templates"],
    )
    b = plan_exercise_journey(
        5,
        "anxiety_spike",
        "standard_book",
        seed="fixed",
        exercise_registry=ctx["exercises"],
        thesis_outcomes=ctx["thesis"],
        journey_templates=ctx["templates"],
    )
    assert [p.exercise_id for p in a.phases] == [p.exercise_id for p in b.phases]


def test_different_chapters_different_exercises(ctx):
    ids_ch1 = [
        p.exercise_id
        for p in plan_exercise_journey(
            1,
            "anxiety_spike",
            "standard_book",
            seed="vary",
            exercise_registry=ctx["exercises"],
            thesis_outcomes=ctx["thesis"],
            journey_templates=ctx["templates"],
        ).phases
    ]
    ids_ch2 = [
        p.exercise_id
        for p in plan_exercise_journey(
            2,
            "anxiety_spike",
            "standard_book",
            seed="vary",
            exercise_registry=ctx["exercises"],
            thesis_outcomes=ctx["thesis"],
            journey_templates=ctx["templates"],
        ).phases
    ]
    assert ids_ch1 != ids_ch2


def test_nine_plans_meaningfully_diverse(ctx):
    """3 topics × 3 chapters → 9 journeys; not identical; thesis ids vary by topic/chapter."""
    topics = ("anxiety", "grief", "burnout")
    sigs = set()
    thesis_keys: set[str] = set()
    exercises = load_exercise_registry()
    thesis = load_thesis_outcome_map()
    templates = load_journey_templates()
    for topic in topics:
        for ch in (1, 2, 3):
            tid = resolve_thesis_id(topic, ch, "ninepack")
            thesis_keys.add(tid)
            j = plan_exercise_journey(
                ch,
                tid,
                "standard_book",
                seed=f"{topic}:nine:{ch}",
                exercise_registry=exercises,
                thesis_outcomes=thesis,
                journey_templates=templates,
            )
            sigs.add((topic, ch, tuple((p.name, p.exercise_id) for p in j.phases)))
    assert len(sigs) == 9
    assert len(thesis_keys) >= 3
    assert len({t[2] for t in sigs}) >= 3


def test_breath_anchor_only_after_sensation_tracking(ctx):
    """breath_anchor_v1 must not appear unless awareness phase used sensation_tracking."""
    exercises = load_exercise_registry()
    thesis = load_thesis_outcome_map()
    templates = load_journey_templates()
    for ch in range(1, 40):
        j = plan_exercise_journey(
            ch,
            "anxiety_spike",
            "standard_book",
            seed="probe",
            exercise_registry=exercises,
            thesis_outcomes=thesis,
            journey_templates=templates,
        )
        if len(j.phases) < 2:
            continue
        aw, reg = j.phases[0].exercise_id, j.phases[1].exercise_id
        if reg == "breath_anchor_v1":
            assert aw == "sensation_tracking_v1"
        if aw == "body_scan_v1":
            assert reg != "breath_anchor_v1"


def test_template_id_stable_per_chapter(ctx):
    exercises = load_exercise_registry()
    thesis = load_thesis_outcome_map()
    templates = load_journey_templates()
    j1 = plan_exercise_journey(
        4,
        "anxiety_spike",
        "deep_book_6h",
        seed="tpl",
        exercise_registry=exercises,
        thesis_outcomes=thesis,
        journey_templates=templates,
    )
    j2 = plan_exercise_journey(
        4,
        "anxiety_spike",
        "deep_book_6h",
        seed="tpl",
        exercise_registry=exercises,
        thesis_outcomes=thesis,
        journey_templates=templates,
    )
    assert j1.template_id == j2.template_id


def test_outcome_flags_populated(ctx):
    exercises = load_exercise_registry()
    thesis = load_thesis_outcome_map()
    templates = load_journey_templates()
    j = plan_exercise_journey(
        1,
        "neck_up_problem",
        "short_book",
        seed="o",
        exercise_registry=exercises,
        thesis_outcomes=thesis,
        journey_templates=templates,
    )
    assert isinstance(j.outcome_ok, bool)
    assert "awareness" in j.expected_outcome
