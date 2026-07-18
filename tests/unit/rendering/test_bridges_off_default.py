"""Restore workstream #2: within-slot bridges OFF by default; G1 deprescribe OFF."""
from __future__ import annotations

from phoenix_v4.rendering import chapter_composer as cc
from phoenix_v4.rendering.register_output_strengthen import spine_deprescribe_inject_enabled


def test_within_slot_bridges_disabled_by_default():
    assert cc.within_slot_bridges_enabled() is False


def test_bridge_within_slot_returns_empty_when_disabled():
    text = cc._bridge_within_slot(
        prev_atom="The body tightened before the mind caught up.",
        next_atom="Across town, another body did the same thing.",
        slot_type="STORY",
        atom_pair_index=0,
        chapter_index=0,
    )
    assert text == ""


def test_bridge_within_slot_can_be_forced_on_for_ab():
    text = cc._bridge_within_slot(
        prev_atom="The body tightened before the mind caught up.",
        next_atom="Across town, another body did the same thing.",
        slot_type="STORY",
        atom_pair_index=0,
        chapter_index=0,
        enabled=True,
    )
    assert text


def test_g1_residual_deprescribe_absorbed_off_by_default(monkeypatch):
    monkeypatch.delenv("PHOENIX_SPINE_DEPRESCRIBE", raising=False)
    assert spine_deprescribe_inject_enabled() is False
