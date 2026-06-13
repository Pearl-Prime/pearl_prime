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
    # bestseller-chord-audit-2026-05-17 Axis 4: raised ceiling 13000→18000 so
    # 12-chapter arcs don't truncate ch 11-12 content to 0 in
    # phoenix_v4/planning/enrichment_select.py:1228 format_wmax cap. PR #1152.
    # DURATION-DERIVATION-01 (#1550): ceiling raised 18000→22000 (cap_word_target=22000);
    # advertised audiobook_minutes re-derived 55→147. OPD-20260611-062 / OPD-20260613-001.
    assert spec["word_range"] == [9000, 22000]
    # AUTO-PLAN-SSOT-01-AMENDMENT (2026-05-06) Group B ruling: standard_book
    # chapter_count_default reconciled from 12 (registry pre-amendment) to 10
    # (Python ACT-011/BSG-011 deliberate runtime value, preserved as the
    # behavior-preserving choice). See docs/PEARL_ARCHITECT_STATE.md.
    assert spec["chapter_count_default"] == 10


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
    # bestseller-chord-audit-2026-05-17 Axis 4 (PR #1152): word_range raised to
    # [9000, 18000] to accommodate 12-chapter arcs without truncating ch 11-12.
    assert 9000 <= total <= 18000


def test_micro_book_word_count():
    spine = load_spine("anxiety")
    profile = load_knob_profile("anxiety")
    shaped = apply_knobs(spine, profile, runtime_format="micro_book_15")
    total = sum(c.target_word_count for c in shaped.chapters)
    assert 2500 <= total <= 4500


def test_deep_book_word_count():
    spine = load_spine("burnout")
    profile = load_knob_profile("burnout")
    shaped = apply_knobs(spine, profile, runtime_format="deep_book_4h")
    total = sum(c.target_word_count for c in shaped.chapters)
    assert 20000 <= total <= 40000


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
        # bestseller-chord-audit-2026-05-17 Axis 4 (PR #1152): raised ceiling 13000→18000.
        assert 9000 <= total <= 18000



# ---------------------------------------------------------------------------
# Compact-format spine subset (PR-G)
# ---------------------------------------------------------------------------
# Compact runtime formats declare `compact_chapter_subset` in
# config/format_selection/format_registry.yaml. When load_spine is called with
# such a runtime_format, it returns a subsetted spine renumbered 1..N. These
# tests pin the contract that smoke-verification confirmed in PR-G.

def test_load_spine_compact_8ch_30min_subsets_to_8():
    """compact_book_8ch_30min must produce an 8-chapter spine."""
    s = load_spine("anxiety", runtime_format="compact_book_8ch_30min")
    assert len(s.chapters) == 8, (
        f"compact_book_8ch_30min should yield 8 chapters, got {len(s.chapters)}"
    )


def test_load_spine_compact_5ch_15min_subsets_to_5():
    """compact_book_5ch_15min must produce a 5-chapter spine."""
    s = load_spine("anxiety", runtime_format="compact_book_5ch_15min")
    assert len(s.chapters) == 5


def test_load_spine_compact_5ch_20min_subsets_to_5():
    """compact_book_5ch_20min must produce a 5-chapter spine."""
    s = load_spine("anxiety", runtime_format="compact_book_5ch_20min")
    assert len(s.chapters) == 5


def test_load_spine_compact_chapters_renumbered_to_1_through_n():
    """Subsetted chapters MUST be renumbered 1..N for downstream phase mapping.

    enrichment_select._chapter_phase computes phase boundaries assuming
    contiguous chapter_number 1..chapter_count. If we returned original
    spine numbers (e.g. [1,3,4,6,7,9,10,12]), phase boundaries would
    miscompute and chapters 6/7/9 would land in HOPE instead of HELP/HEALING.
    """
    s8 = load_spine("anxiety", runtime_format="compact_book_8ch_30min")
    assert [c.number for c in s8.chapters] == [1, 2, 3, 4, 5, 6, 7, 8]

    s5 = load_spine("anxiety", runtime_format="compact_book_5ch_15min")
    assert [c.number for c in s5.chapters] == [1, 2, 3, 4, 5]


def test_load_spine_compact_preserves_role_semantics():
    """Subset must keep the four narrative phases represented + closer.

    Default subsets per format_registry.yaml:
      8ch: [1, 3, 4, 6, 7, 9, 10, 12]  (recognition, pattern_mapping, mechanism,
                                        destabilization, practical_interruption,
                                        somatic_legitimacy, reframe, integration)
      5ch: [1, 4, 7, 10, 12]            (recognition, mechanism,
                                         practical_interruption, reframe,
                                         integration)
    Closer (integration, original ch12) MUST be present in both — without it the
    book has no resolution chapter and ending_contract gates fail.
    """
    s8 = load_spine("anxiety", runtime_format="compact_book_8ch_30min")
    roles8 = [c.role for c in s8.chapters]
    assert "recognition" in roles8, "8ch subset missing recognition (HARDSHIP)"
    assert "mechanism" in roles8, "8ch subset missing mechanism (HELP)"
    assert "practical_interruption" in roles8, "8ch subset missing practical_interruption (HEALING)"
    assert "integration" in roles8, "8ch subset missing integration (closer/HOPE)"
    # Verify integration is the LAST chapter (closer position)
    assert s8.chapters[-1].role == "integration", (
        "integration must be the final chapter of compact subsets"
    )

    s5 = load_spine("anxiety", runtime_format="compact_book_5ch_15min")
    roles5 = [c.role for c in s5.chapters]
    assert "recognition" in roles5
    assert "mechanism" in roles5
    assert "practical_interruption" in roles5
    assert "integration" in roles5
    assert s5.chapters[-1].role == "integration"


def test_load_spine_no_runtime_format_returns_full_spine():
    """Backward-compat: load_spine with no runtime_format returns the full 12-chapter spine."""
    s = load_spine("anxiety")
    assert len(s.chapters) == 12
    s_explicit = load_spine("anxiety", runtime_format=None)
    assert len(s_explicit.chapters) == 12


def test_load_spine_non_compact_format_returns_full_spine():
    """Non-compact runtime formats (no compact_chapter_subset declared) return full spine."""
    s = load_spine("anxiety", runtime_format="standard_book")
    assert len(s.chapters) == 12
    s_micro = load_spine("anxiety", runtime_format="micro_book_15")
    assert len(s_micro.chapters) == 12  # micro_book_15 has no subset declaration


def test_apply_knobs_on_compact_spine_validates_clean():
    """apply_knobs against a compact-subsetted spine must validate cleanly.

    The validate_shaped_spine check `len(shaped.chapters) != len(original.chapters)`
    correctly compares against the (already-subsetted) spine passed in, so
    the chapter_count_mismatch violation does NOT fire for compact runs.
    """
    spine = load_spine("anxiety", runtime_format="compact_book_8ch_30min")
    knobs = load_knob_profile("anxiety")
    shaped = apply_knobs(
        spine, knobs, runtime_format="compact_book_8ch_30min"
    )
    assert len(shaped.chapters) == 8
    violations = validate_shaped_spine(shaped, spine, knobs)
    # Word range may flag depending on tuning; the critical assertion is no
    # chapter_count_mismatch / chapter_order_changed / role_mutated violations
    blocking = [v for v in violations if any(
        s in v for s in ("chapter_count_mismatch", "chapter_order_changed",
                         "role_mutated", "thesis_mutated", "missing_original_chapter")
    )]
    assert blocking == [], (
        f"unexpected blocking violations on compact spine: {blocking}"
    )
