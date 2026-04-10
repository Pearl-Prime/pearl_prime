"""Tests for phoenix_v4.planning.knob_apply (Knob Apply stage)."""
from __future__ import annotations

import copy
import json
from dataclasses import replace

from phoenix_v4.planning import knob_apply
from phoenix_v4.planning.knob_apply import (
    apply_knobs,
    load_knob_profile,
    load_runtime_format,
    load_spine,
    shaped_spine_to_jsonable,
    validate_shaped_spine,
)


def test_load_anxiety_spine():
    s = load_spine("anxiety")
    assert s.family_id == "anxiety"
    assert len(s.chapters) == 12
    assert s.chapters[0].number == 1
    assert "HOOK" in s.chapters[0].required_sections


def test_load_grief_spine():
    s = load_spine("grief")
    assert s.family_id == "grief"
    assert len(s.chapters) == 12


def test_load_burnout_spine():
    s = load_spine("burnout")
    assert s.family_id == "burnout"
    assert len(s.chapters) == 12
    ch4 = next(c for c in s.chapters if c.number == 4)
    assert "SOMATIC_INVENTORY" in [x.upper() for x in ch4.required_sections]


def test_load_knob_profile_anxiety():
    p = load_knob_profile("anxiety")
    assert p.topic == "anxiety"
    assert "story_density" in p.knob_defaults
    assert len(p.knob_defaults) >= 12
    assert p.hard_floors
    assert p.hard_ceilings


def test_load_knob_profile_grief():
    p = load_knob_profile("grief")
    assert p.knob_defaults["exercise_density"] == "low"
    assert p.phase_overrides["early_book"]["exercise_density"] == "none"


def test_load_runtime_format_standard():
    spec = load_runtime_format("standard_book")
    assert spec["word_range"] == [9000, 11000]
    assert spec["chapter_count_default"] == 12


def test_apply_knobs_anxiety_standard():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile, runtime_format="standard_book")
    assert len(shaped.chapters) == 12
    assert shaped.stage == "knob_apply"


def test_apply_knobs_grief_standard():
    spine = load_spine("grief")
    profile = load_knob_profile("grief")
    shaped = apply_knobs(spine, profile)
    assert len(shaped.chapters) == 12


def test_apply_knobs_burnout_standard():
    spine = load_spine("burnout")
    profile = load_knob_profile("burnout")
    shaped = apply_knobs(spine, profile)
    assert len(shaped.chapters) == 12


def test_chapter_count_preserved():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile)
    assert len(shaped.chapters) == len(spine.chapters)


def test_thesis_immutable():
    spine = load_spine("grief")
    profile = load_knob_profile("grief")
    shaped = apply_knobs(spine, profile)
    by_n = {c.number: c for c in spine.chapters}
    for ch in shaped.chapters:
        assert ch.thesis == by_n[ch.number].thesis


def test_role_immutable():
    spine = load_spine("burnout")
    profile = load_knob_profile("burnout")
    shaped = apply_knobs(spine, profile)
    by_n = {c.number: c for c in spine.chapters}
    for ch in shaped.chapters:
        assert ch.role == by_n[ch.number].role


def test_title_immutable():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile)
    by_n = {c.number: c for c in spine.chapters}
    for ch in shaped.chapters:
        assert ch.working_title == by_n[ch.number].working_title


def test_early_phase_chapters_1_to_4():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile)
    for ch in shaped.chapters:
        if ch.number <= 4:
            assert ch.phase == "early"


def test_mid_phase_chapters_5_to_8():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile)
    for ch in shaped.chapters:
        if 5 <= ch.number <= 8:
            assert ch.phase == "mid"


def test_late_phase_chapters_9_to_12_anxiety_grief():
    for topic in ("anxiety", "grief"):
        spine = load_spine(topic)
        profile = load_knob_profile(topic)
        shaped = apply_knobs(spine, profile)
        for ch in shaped.chapters:
            if ch.number >= 9:
                assert ch.phase == "late"


def test_burnout_ch9_mid_ch10_late():
    spine = load_spine("burnout")
    profile = load_knob_profile("burnout")
    shaped = apply_knobs(spine, profile)
    by_n = {c.number: c for c in shaped.chapters}
    assert by_n[9].phase == "mid"
    assert by_n[10].phase == "late"


def test_anxiety_exercise_ceiling_early():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile)
    for ch in shaped.chapters:
        if ch.number <= 4:
            ex = ch.knob_snapshot.get("exercise_density")
            assert ex in ("none", "low")


def test_grief_exercise_ceiling_through_ch8():
    spine = load_spine("grief")
    profile = load_knob_profile("grief")
    shaped = apply_knobs(spine, profile)
    for ch in shaped.chapters:
        if ch.number <= 8:
            ex = ch.knob_snapshot.get("exercise_density")
            assert ex in ("none", "low")


def test_emotional_temperature_floor_anxiety():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    profile = replace(
        profile,
        persona_overrides={"emotional_temperature": "clinical"},
    )
    shaped = apply_knobs(spine, profile)
    for ch in shaped.chapters:
        scale = knob_apply._SCALE_TEMP
        assert knob_apply._rank(scale, ch.knob_snapshot.get("emotional_temperature")) >= knob_apply._rank(
            scale, "warm"
        )


def test_spirituality_ceiling_financial_stress():
    spine = replace(load_spine("anxiety"), topic="financial_stress")
    profile = load_knob_profile("financial_stress")
    profile = replace(
        profile,
        platform_overrides={"spirituality_level": "high"},
    )
    shaped = apply_knobs(spine, profile)
    assert any(x.get("knob") == "spirituality_level" for x in shaped.knob_audit.ceilings_enforced)
    for ch in shaped.chapters:
        assert ch.knob_snapshot.get("spirituality_level") == "secular"


def test_anxiety_high_exercise_low_temp_blocked():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    hf = {k: v for k, v in profile.hard_floors.items() if k != "emotional_temperature"}
    profile = replace(
        profile,
        hard_floors=hf,
        platform_overrides={"exercise_density": "high", "emotional_temperature": "clinical"},
    )
    shaped = apply_knobs(spine, profile)
    ch2 = next(c for c in shaped.chapters if c.number == 2)
    assert ch2.knob_snapshot.get("exercise_density") == "none"
    assert any(
        r.get("reason") == "spine_sequencing_exercise_blocked"
        for r in shaped.knob_audit.dangerous_combos_resolved
    ) or any(r.get("knob") == "exercise_density" for r in shaped.knob_audit.dangerous_combos_resolved)


def test_mechanism_reflection_combo_resolved_anxiety_early():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    profile = replace(
        profile,
        platform_overrides={"mechanism_depth": "high", "reflection_depth": "high"},
    )
    shaped = apply_knobs(spine, profile)
    ch1 = next(c for c in shaped.chapters if c.number == 1)
    assert ch1.knob_snapshot.get("mechanism_depth") != "high"
    assert not any(
        r.get("matched") and r.get("still_matched_after_resolution")
        for r in shaped.knob_audit.dangerous_combos_checked
    )


def test_no_false_positive_on_safe_combo():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile)
    bad = [
        r
        for r in shaped.knob_audit.dangerous_combos_checked
        if r.get("matched") and r.get("still_matched_after_resolution")
    ]
    assert not bad


def test_standard_book_word_count():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile, runtime_format="standard_book")
    total = sum(c.target_word_count for c in shaped.chapters)
    assert 9000 <= total <= 11000


def test_micro_book_word_count():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile, runtime_format="micro_book_15")
    total = sum(c.target_word_count for c in shaped.chapters)
    assert 2500 <= total <= 3000


def test_deep_book_word_count():
    spine = load_spine("burnout")
    profile = load_knob_profile("burnout")
    shaped = apply_knobs(spine, profile, runtime_format="deep_book_4h")
    total = sum(c.target_word_count for c in shaped.chapters)
    assert 36000 <= total <= 44000


def test_valid_shaped_spine_passes():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile)
    assert validate_shaped_spine(shaped, spine, profile) == []


def test_modified_thesis_fails():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile)
    bad = copy.deepcopy(shaped)
    bad.chapters[0].thesis = "tampered"
    assert any("thesis_mutated" in v for v in validate_shaped_spine(bad, spine, profile))


def test_floor_violation_fails():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile)
    bad = copy.deepcopy(shaped)
    bad.chapters[3].knob_snapshot["story_density"] = "low"
    assert any("floor_violation" in v for v in validate_shaped_spine(bad, spine, profile))


def test_required_section_zeroed_fails():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile)
    bad = copy.deepcopy(shaped)
    bad.chapters[0].shaped_section_weights["HOOK"] = 0.0
    assert any("required_section_zeroed" in v for v in validate_shaped_spine(bad, spine, profile))


def test_audit_records_floor_enforcement():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    profile = replace(
        profile,
        persona_overrides={"story_density": "low"},
    )
    shaped = apply_knobs(spine, profile)
    assert any(x.get("knob") == "story_density" for x in shaped.knob_audit.floors_enforced)


def test_audit_records_combo_resolution():
    spine = load_spine("burnout")
    profile = load_knob_profile("burnout")
    profile = replace(
        profile,
        platform_overrides={"exercise_density": "high", "pacing_profile": "fast"},
    )
    shaped = apply_knobs(spine, profile)
    assert len(shaped.knob_audit.dangerous_combos_resolved) >= 1


def test_audit_records_platform_conflict():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile, platform_id="spotify")
    assert shaped.knob_audit.platform_conflicts_resolved


def test_shaped_profiles_differ_across_topics():
    out = []
    for topic in ("anxiety", "grief", "burnout"):
        spine = load_spine(topic)
        profile = load_knob_profile(topic)
        shaped = apply_knobs(spine, profile)
        mid = next(c for c in shaped.chapters if c.number == 6)
        out.append(
            (
                mid.knob_snapshot.get("exercise_density"),
                mid.knob_snapshot.get("narrative_structure"),
                mid.knob_snapshot.get("pacing_profile"),
            )
        )
    assert len(set(out)) == 3


def test_jsonable_roundtrip_keys():
    spine = load_spine("burnout")
    profile = load_knob_profile("burnout")
    shaped = apply_knobs(spine, profile)
    d = shaped_spine_to_jsonable(shaped)
    assert d["stage"] == "knob_apply"
    json.dumps(d)


def test_cli_three_topics_smoke():
    for topic in ["anxiety", "grief", "burnout"]:
        spine = load_spine(topic)
        knobs = load_knob_profile(topic)
        shaped = apply_knobs(spine, knobs, runtime_format="standard_book")
        total = sum(ch.target_word_count for ch in shaped.chapters)
        assert len(shaped.chapters) == 12
        assert 9000 <= total <= 11000
