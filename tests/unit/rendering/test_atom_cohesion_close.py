"""Atom cohesion close — adjacency selector + template cadence suppression."""

from __future__ import annotations

from phoenix_v4.planning.enrichment_select import (
    PersonaPoolRotationState,
    _collision_family_penalty,
    _pick_hook_index_unique,
    _pick_primary_index_unseen,
    _recent_collision_families,
)
from phoenix_v4.rendering.register_output_strengthen import (
    suppress_unbudgeted_template_cadence,
)


def test_collision_family_penalty_applies_on_recent_match() -> None:
    meta = {"collision_family": "permission_to_pause"}
    assert _collision_family_penalty(meta, ["permission_to_pause"]) == -0.20
    assert _collision_family_penalty(meta, ["other_family"]) == 0.0


def test_pick_primary_skips_recent_collision_family_when_alternative_exists() -> None:
    pool = [
        {
            "atom_id": "a1",
            "content": "First reflection body with enough words to pass the fuzzy dedup floor easily.",
            "metadata": {"collision_family": "repeat_me"},
        },
        {
            "atom_id": "a2",
            "content": "Second reflection body with different words so the selector can rotate cleanly.",
            "metadata": {"collision_family": "fresh_family"},
        },
    ]
    rot = PersonaPoolRotationState()
    idx = _pick_primary_index_unseen(
        rot,
        pool,
        "seed:ch2:REFLECTION",
        "persona",
        seen_bodies=set(),
        recent_families=["repeat_me"],
    )
    assert idx == 1


def test_pick_hook_prefers_non_recent_collision_family() -> None:
    pool = [
        {
            "atom_id": "h1",
            "content": "Hook one opens the chapter with a distinct corporate burnout scene.",
            "metadata": {"collision_family": "used_family"},
        },
        {
            "atom_id": "h2",
            "content": "Hook two opens differently so engine siblings do not restart the same way.",
            "metadata": {"collision_family": "new_family"},
        },
    ]
    rot = PersonaPoolRotationState()
    idx = _pick_hook_index_unique(
        rot,
        pool,
        "seed:ch3:HOOK",
        "persona",
        seen_bodies=set(),
        used_hooks=set(),
        recent_families=["used_family"],
    )
    assert idx == 1


def test_recent_collision_families_window() -> None:
    hist = [["a"], ["b", "c"], []]
    assert _recent_collision_families(hist, 2, window=2) == ["a", "b", "c"]
    assert _recent_collision_families(hist, 1, window=2) == ["a"]


def test_suppress_unbudgeted_template_cadence_drops_surplus_standalone() -> None:
    refrain = "Rest at this stop. You do not have to march past it."
    other = "A longer narrative paragraph that should remain even when cadence lines are trimmed."
    prose = (
        f"Chapter 1\n{refrain}\n\n{other}\n\n"
        f"Chapter 2\n{refrain}\n\n{other}"
    )
    out = suppress_unbudgeted_template_cadence(prose)
    assert out.count(refrain) == 1
    assert other in out


def test_suppress_keeps_embedded_refrain_in_long_paragraph() -> None:
    refrain = "Peel back the obvious. Something else lives one inch down."
    embedded = f"Start here. {refrain} Continue the story with more narrative detail."
    prose = f"Chapter 1\n{embedded}\n\nChapter 2\n{embedded}"
    out = suppress_unbudgeted_template_cadence(prose)
    assert out.count(refrain) == 2
