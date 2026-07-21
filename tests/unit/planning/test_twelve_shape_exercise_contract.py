"""Twelve-shape beatmap must honor purpose-contract exercise caps."""
from __future__ import annotations

from phoenix_v4.planning.beatmap_compile import (
    compile_beatmap,
    load_format_spec,
    load_topic_engines,
    resolve_twelve_shape_slot_grid,
)
from phoenix_v4.planning.chapter_planner import assign_chapter_purpose_contracts
from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine


def test_twelve_shape_grid_includes_exercise_before_cap() -> None:
    grid = resolve_twelve_shape_slot_grid("gen_z_professionals", "anxiety")
    assert grid is not None
    assert grid.count("EXERCISE") == 1


def test_twelve_shape_ch1_keeps_single_exercise_when_contract_allows_it() -> None:
    """Extended-book flagship chapter 1 keeps its single planned exercise slot."""
    fmt = load_format_spec("extended_book_2h")
    spine = load_spine("anxiety", runtime_format="extended_book_2h")
    shaped = apply_knobs(
        spine,
        load_knob_profile("anxiety"),
        runtime_format="extended_book_2h",
    )
    bm = compile_beatmap(
        shaped,
        load_topic_engines("anxiety"),
        fmt,
        persona_id="gen_z_professionals",
    )
    contracts = assign_chapter_purpose_contracts(len(bm.chapters), "extended_book_2h")
    assert contracts[0].max_exercises == 1
    ch1 = bm.chapters[0]
    assert ch1.slot_definitions.count("EXERCISE") == 1, (
        f"ch1 lost its planned EXERCISE slot: {ch1.slot_definitions}"
    )
