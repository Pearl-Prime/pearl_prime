from phoenix_v4.planning.assembly_compiler import _resolved_story_band


def test_resolved_story_band_uses_required_band_for_universal_story() -> None:
    out = _resolved_story_band(
        aid="story_1",
        chapter_idx=2,
        band_by_id={"story_1": 2},
        universal_story_ids={"story_1"},
        required_band_by_chapter={2: 5},
    )
    assert out == 5


def test_resolved_story_band_falls_back_to_atom_band_when_not_universal() -> None:
    out = _resolved_story_band(
        aid="story_2",
        chapter_idx=0,
        band_by_id={"story_2": 4},
        universal_story_ids=set(),
        required_band_by_chapter={0: 1},
    )
    assert out == 4
