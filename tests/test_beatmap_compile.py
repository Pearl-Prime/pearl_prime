"""Tests for phoenix_v4.planning.beatmap_compile (BeatmapCompile stage)."""
from __future__ import annotations

import copy
import hashlib

import pytest

from phoenix_v4.planning.beatmap_compile import (
    Beatmap,
    beatmap_to_jsonable,
    compile_beatmap,
    load_format_spec,
    load_topic_engines,
)
from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine


@pytest.fixture
def fmt_std():
    return load_format_spec("standard_book")


def _chain(topic: str, fmt_std):
    spine = load_spine(topic)
    prof = load_knob_profile(topic)
    shaped = apply_knobs(spine, prof, runtime_format="standard_book")
    engines = load_topic_engines(topic)
    return compile_beatmap(shaped, engines, fmt_std)


# --- Group 1: basic ---


def test_compile_anxiety_standard(fmt_std):
    bm = _chain("anxiety", fmt_std)
    assert isinstance(bm, Beatmap)
    assert bm.stage == "beatmap_compile"
    assert len(bm.chapters) == 12
    assert bm.topic == "anxiety"


def test_compile_grief_standard(fmt_std):
    bm = _chain("grief", fmt_std)
    assert len(bm.chapters) == 12


def test_compile_burnout_standard(fmt_std):
    bm = _chain("burnout", fmt_std)
    assert len(bm.chapters) == 12


def test_all_chapters_have_slots(fmt_std):
    from phoenix_v4.planning.chapter_planner import (
        assign_chapter_purpose_contracts,
        resolve_effective_max_exercises,
    )

    somatic_exercise_slots = 2
    for topic in ("anxiety", "grief", "burnout"):
        bm = _chain(topic, fmt_std)
        contracts = assign_chapter_purpose_contracts(len(bm.chapters), "standard_book")
        for ch, contract in zip(bm.chapters, contracts):
            effective_max = resolve_effective_max_exercises(
                contract.max_exercises,
                "standard_book",
            )
            expected_slots = 10 - (somatic_exercise_slots - effective_max)
            assert len(ch.slots) == expected_slots


def test_slot_definitions_match_slots(fmt_std):
    bm = _chain("anxiety", fmt_std)
    for ch in bm.chapters:
        assert ch.slot_definitions == [s.slot_type for s in ch.slots]


# --- Group 2: inclusion / exclusion ---


def test_exercise_excluded_when_weight_zero(fmt_std):
    """Purpose contract max_exercises=0 removes EXERCISE slots upstream for recognition ch1."""
    from phoenix_v4.planning.chapter_planner import assign_chapter_purpose_contracts

    bm = _chain("anxiety", fmt_std)
    ch1 = bm.chapters[0]
    contracts = assign_chapter_purpose_contracts(len(bm.chapters), "standard_book")
    assert contracts[0].max_exercises == 0
    assert ch1.slot_definitions.count("EXERCISE") == 0


def test_required_section_survives_zero_weight(fmt_std, recwarn):
    spine = load_spine("anxiety")
    shaped = apply_knobs(spine, load_knob_profile("anxiety"))
    bad = copy.deepcopy(shaped)
    bad.chapters[0].shaped_section_weights["HOOK"] = 0.0
    bm = compile_beatmap(bad, load_topic_engines("anxiety"), fmt_std)
    ch1 = bm.chapters[0]
    assert "HOOK" in ch1.slot_definitions
    hook_slot = next(s for s in ch1.slots if s.slot_type == "HOOK")
    assert hook_slot.weight >= 0.29
    assert any(
        x.get("reason") == "required_section_zero_weight_recovery"
        for x in bm.compile_audit.get("minimum_word_overrides", [])
    )


def test_forbidden_move_excludes_section():
    """Legacy beatmap path (non-somatic formats) still drops forbidden slots."""
    fmt_short = load_format_spec("short_book_30")
    # Source the spine WITH the runtime_format so the shaped/tampered spine matches the
    # subsetted chapter count that compile_beatmap re-loads (PR #1610 wired the re-load;
    # PR #1612 gave short_book_30 a compact_chapter_subset → 8 chapters). Mirrors the real
    # pipeline (scripts/run_pipeline.py, scripts/pilot/run_spine_pipeline.py).
    spine = load_spine("anxiety", runtime_format="short_book_30")
    shaped = apply_knobs(spine, load_knob_profile("anxiety"), runtime_format="short_book_30")
    tampered = copy.deepcopy(shaped)
    tampered.chapters[0].shaped_section_weights["EXERCISE"] = 0.95
    bm = compile_beatmap(tampered, load_topic_engines("anxiety"), fmt_short)
    ch1 = bm.chapters[0]
    assert "EXERCISE" not in ch1.slot_definitions
    assert any(
        x.get("reason") == "forbidden_moves" and x.get("chapter") == 1
        for x in bm.compile_audit["sections_excluded"]
    )


# --- Group 3: word budgets ---


def test_word_budget_non_uniform_somatic(fmt_std):
    """Somatic grid uses scaled non-uniform baselines (second exercise > first)."""
    shaped = apply_knobs(load_spine("anxiety"), load_knob_profile("anxiety"))
    bm = compile_beatmap(shaped, load_topic_engines("anxiety"), fmt_std)
    ch6 = next(c for c in bm.chapters if c.number == 6)
    ex_a = ch6.slots[3]
    ex_b = ch6.slots[7]
    assert ex_a.slot_type == "EXERCISE"
    assert ex_b.slot_type == "EXERCISE"
    assert ex_b.target_words >= ex_a.target_words


def test_hook_minimum_100_words(fmt_std):
    bm = _chain("anxiety", fmt_std)
    for ch in bm.chapters:
        hook = next((s for s in ch.slots if s.slot_type == "HOOK"), None)
        if hook:
            assert hook.target_words >= 100


def test_exercise_minimum_80_words(fmt_std):
    bm = _chain("grief", fmt_std)
    ch9 = next(c for c in bm.chapters if c.number == 9)
    ex = next(s for s in ch9.slots if s.slot_type == "EXERCISE")
    assert ex.target_words >= 80


def test_total_words_within_format_range(fmt_std):
    spec = load_format_spec("standard_book")
    lo, hi = spec["word_range"]
    for topic in ("anxiety", "grief", "burnout"):
        bm = _chain(topic, fmt_std)
        assert lo <= bm.total_target_words <= hi


# --- Group 4: ordering ---


def test_somatic_ten_slot_grid_order(fmt_std):
    from phoenix_v4.planning.beatmap_compile import SOMATIC_10_SLOT_GRID

    bm = _chain("anxiety", fmt_std)
    for ch in bm.chapters:
        assert [s.slot_type for s in ch.slots] == SOMATIC_10_SLOT_GRID


def test_somatic_section_indices(fmt_std):
    bm = _chain("anxiety", fmt_std)
    for ch in bm.chapters:
        for i, s in enumerate(ch.slots):
            assert s.somatic_section_index == i + 1


def test_no_random_ordering(fmt_std):
    bm1 = _chain("burnout", fmt_std)
    bm2 = _chain("burnout", fmt_std)
    d1 = beatmap_to_jsonable(bm1)
    d2 = beatmap_to_jsonable(bm2)
    h1 = hashlib.sha256(repr(d1).encode()).hexdigest()
    h2 = hashlib.sha256(repr(d2).encode()).hexdigest()
    assert h1 == h2


# --- Group 5: enrichment hooks ---


def test_enrichment_hooks_mapped_to_slots(fmt_std):
    bm = _chain("anxiety", fmt_std)
    assert any(len(s.enrichment_hooks) > 0 for ch in bm.chapters for s in ch.slots)


def test_teacher_voice_on_reflection(fmt_std):
    bm = _chain("grief", fmt_std)
    found = False
    for ch in bm.chapters:
        ref = next((s for s in ch.slots if s.slot_type == "REFLECTION"), None)
        if ref and "teacher_voice" in ref.enrichment_hooks:
            found = True
            break
    assert found


def test_exercise_enrichment_on_exercise(fmt_std):
    bm = _chain("grief", fmt_std)
    ch9 = next(c for c in bm.chapters if c.number == 9)
    ex = next(s for s in ch9.slots if s.slot_type == "EXERCISE")
    assert "somatic_exercise" in ex.enrichment_hooks


# --- Group 6: audit ---


def test_audit_records_exclusions(fmt_std):
    bm = _chain("anxiety", fmt_std)
    assert bm.compile_audit.get("somatic_ten_slot_grid") is True
    assert isinstance(bm.compile_audit["sections_excluded"], list)


def test_audit_records_minimum_overrides(fmt_std):
    spine = load_spine("anxiety")
    shaped = apply_knobs(spine, load_knob_profile("anxiety"))
    bad = copy.deepcopy(shaped)
    bad.chapters[0].shaped_section_weights["HOOK"] = 0.0
    bm = compile_beatmap(bad, load_topic_engines("anxiety"), fmt_std)
    assert len(bm.compile_audit["minimum_word_overrides"]) >= 1


def test_audit_total_words_accurate(fmt_std):
    bm = _chain("anxiety", fmt_std)
    assert bm.total_target_words == sum(ch.target_word_count for ch in bm.chapters)


# --- Group 7: end-to-end ---


def test_anxiety_full_pipeline(fmt_std):
    spine = load_spine("anxiety")
    shaped = apply_knobs(spine, load_knob_profile("anxiety"), runtime_format="standard_book")
    bm = compile_beatmap(shaped, load_topic_engines("anxiety"), fmt_std)
    assert len(bm.chapters) == 12


def test_grief_full_pipeline(fmt_std):
    spine = load_spine("grief")
    shaped = apply_knobs(spine, load_knob_profile("grief"))
    bm = compile_beatmap(shaped, load_topic_engines("grief"), fmt_std)
    assert bm.family_id == "grief"


def test_burnout_full_pipeline(fmt_std):
    spine = load_spine("burnout")
    shaped = apply_knobs(spine, load_knob_profile("burnout"))
    bm = compile_beatmap(shaped, load_topic_engines("burnout"), fmt_std)
    assert bm.runtime_format == "standard_book"


def test_output_chapters_match_input(fmt_std):
    spine = load_spine("burnout")
    shaped = apply_knobs(spine, load_knob_profile("burnout"))
    bm = compile_beatmap(shaped, load_topic_engines("burnout"), fmt_std)
    by_n = {c.number: c for c in spine.chapters}
    for ch in bm.chapters:
        o = by_n[ch.number]
        assert ch.role == o.role
        assert ch.working_title == o.working_title
        assert ch.thesis == o.thesis


def test_topics_produce_distinct_beatmaps(fmt_std):
    topics = ("anxiety", "grief", "burnout")
    bms = [_chain(t, fmt_std) for t in topics]
    assert len({bm.topic for bm in bms}) == 3
    for bm in bms:
        assert sum(len(ch.slots) for ch in bm.chapters) == 120
        assert sum(1 for ch in bm.chapters for s in ch.slots if s.slot_type == "EXERCISE") == 24


def test_load_topic_engines_includes_allowed_engines():
    eng = load_topic_engines("anxiety")
    assert "false_alarm" in eng.get("allowed_engines", [])


def test_load_format_spec_has_canonical_order():
    spec = load_format_spec("standard_book")
    assert spec["canonical_slot_order"][0] == "HOOK"
    assert "COMPRESSION" in spec["canonical_slot_order"]


def test_compression_slot_suppressed_when_not_allowed(fmt_std):
    shaped = apply_knobs(load_spine("anxiety"), load_knob_profile("anxiety"))
    for ch in shaped.chapters:
        assert not ch.compression_allowed or ch.knob_snapshot.get("compression", "none") != "none"
    bm = compile_beatmap(shaped, load_topic_engines("anxiety"), fmt_std)
    assert all("COMPRESSION" not in c.slot_definitions for c in bm.chapters)


def test_integration_minimum_60_words(fmt_std):
    bm = _chain("anxiety", fmt_std)
    for ch in bm.chapters:
        intr = next((s for s in ch.slots if s.slot_type == "INTEGRATION"), None)
        if intr:
            assert intr.target_words >= 60


def test_jsonable_roundtrip_keys(fmt_std):
    bm = _chain("burnout", fmt_std)
    d = beatmap_to_jsonable(bm)
    assert d["stage"] == "beatmap_compile"
    assert len(d["chapters"]) == 12
