"""story_picks: explicit twelve-shape story pinning (pool-size drift guard)."""
from __future__ import annotations

from pathlib import Path

from phoenix_v4.planning.chapter_object_continuity import load_chapter_continuity_plan
from phoenix_v4.planning.story_planner import (
    SCENE_SECTION_INDICES,
    build_story_schedule,
    find_atom_by_variant,
    normalize_story_pick_variant,
)

REPO = Path(__file__).resolve().parents[3]

_CH1_EXPECTED = {
    "recognition": "v03",
    "mechanism_proof": "v05",
    "turning_point": "v08",
}
_CH2_EXPECTED = {
    "recognition": "v18",
    "mechanism_proof": "v22",
    "turning_point": "v18",
}
_SEED = "flagship_phase2_layer6"


def _variants_for_chapter(schedule, ch: int) -> dict[str, str]:
    out: dict[str, str] = {}
    for (chapter, sec_idx), slot in schedule.assignments.items():
        if chapter != ch:
            continue
        assert sec_idx in SCENE_SECTION_INDICES
        out[slot.arc_position] = slot.source.rsplit(":", 1)[-1]
    return out


def test_normalize_story_pick_variant() -> None:
    assert normalize_story_pick_variant("v03") == "v03"
    assert normalize_story_pick_variant("story v03") == "v03"
    assert normalize_story_pick_variant("") == ""


def test_flagship_plan_has_story_picks_ch1_ch2() -> None:
    plan = load_chapter_continuity_plan("gen_z_professionals", "anxiety")
    ch1 = next(c for c in plan if int(c["chapter"]) == 1)
    ch2 = next(c for c in plan if int(c["chapter"]) == 2)
    assert ch1.get("story_picks") == _CH1_EXPECTED
    assert ch2.get("story_picks") == _CH2_EXPECTED


def test_story_picks_pin_ch1_ch2_selections() -> None:
    sched = build_story_schedule(
        "gen_z_professionals",
        "anxiety",
        _SEED,
        REPO,
    )
    assert _variants_for_chapter(sched, 1) == _CH1_EXPECTED
    assert _variants_for_chapter(sched, 2) == _CH2_EXPECTED


def test_story_picks_immune_to_pool_size_drift() -> None:
    """Adding a decoy story atom must not shift pinned ch1/ch2 selections."""
    from phoenix_v4.planning.story_planner import (
        AtomFile,
        _build_schedule_from_continuity_plan,
        _load_all_atoms,
    )

    plan = load_chapter_continuity_plan("gen_z_professionals", "anxiety")
    baseline_atoms = _load_all_atoms("gen_z_professionals", "anxiety", REPO)
    decoy = AtomFile(
        path=Path("/decoy/recognition/v99.txt"),
        arc_position="recognition",
        engine="overwhelm",
        variant="v99",
        character=None,
        word_count=40,
        text=(
            "The room held its breath while the cursor blinked on an empty draft. "
            "Nothing urgent had happened yet, but the body already knew the shape "
            "of the next hour. A notification chimed once and went quiet again."
        ),
    )
    polluted_atoms = baseline_atoms + [decoy]

    baseline = _build_schedule_from_continuity_plan(baseline_atoms, _SEED, plan)
    with_decoy = _build_schedule_from_continuity_plan(polluted_atoms, _SEED, plan)
    assert _variants_for_chapter(baseline, 1) == _CH1_EXPECTED
    assert _variants_for_chapter(with_decoy, 1) == _CH1_EXPECTED
    assert _variants_for_chapter(baseline, 2) == _CH2_EXPECTED
    assert _variants_for_chapter(with_decoy, 2) == _CH2_EXPECTED


def test_find_atom_by_variant_resolves_pinned_file() -> None:
    from phoenix_v4.planning.story_planner import _load_all_atoms

    atoms = _load_all_atoms("gen_z_professionals", "anxiety", REPO)
    atom = find_atom_by_variant(atoms, "recognition", "v03")
    assert atom is not None
    assert atom.variant == "v03"
    assert atom.arc_position == "recognition"
