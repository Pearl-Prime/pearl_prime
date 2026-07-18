"""Phase 1 de-injection tests — master switch, TRANSITION consumer, identity, HOOK dedup."""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.exercises import component_assembler as ca
from phoenix_v4.planning import enrichment_select as es
from phoenix_v4.planning import transition_atoms as ta
from phoenix_v4.planning.book_identity_contract import (
    banned_phrase_penalty,
    load_book_identity_contract,
)
from phoenix_v4.rendering import chapter_composer as cc
from phoenix_v4.rendering.render_glue import render_glue_enabled


def test_render_glue_disabled_by_default(monkeypatch):
    monkeypatch.delenv("PHOENIX_ENABLE_RENDER_GLUE", raising=False)
    assert render_glue_enabled() is False
    assert cc.render_glue_enabled() is False
    assert cc.bridge_transition_families_enabled() is False


def test_render_glue_master_enables_families(monkeypatch):
    monkeypatch.setenv("PHOENIX_ENABLE_RENDER_GLUE", "1")
    monkeypatch.setenv("PHOENIX_BRIDGE_TRANSITION_FAMILIES", "1")
    cc._BRIDGE_TRANSITION_CACHE = None
    assert cc.bridge_transition_families_enabled() is True


def test_authored_transition_empty_pool(monkeypatch):
    monkeypatch.delenv("PHOENIX_ENABLE_RENDER_GLUE", raising=False)
    out = cc._authored_transition(
        "before_story",
        topic_id="anxiety",
        persona_id="gen_z_professionals",
        chapter_index=0,
        book_seed="test",
    )
    assert out == ""


def test_select_authored_transition_with_metadata(tmp_path, monkeypatch):
    atoms = tmp_path / "atoms" / "p1" / "topic1" / "TRANSITION"
    atoms.mkdir(parents=True)
    atoms.joinpath("CANONICAL.txt").write_text(
        "## TRANSITION v01\n"
        "---\n"
        "boundary: before_story\n"
        "---\n"
        "The story ahead lands the pattern in a body you can recognize.\n"
        "---\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(ta, "load_transition_pool", lambda *a, **k: [
        {
            "atom_id": "TRANSITION v01",
            "content": "The story ahead lands the pattern in a body you can recognize.",
            "metadata": {"boundary": "before_story"},
        }
    ])
    picked = ta.select_authored_transition(
        "before_story",
        persona_id="p1",
        topic_id="topic1",
        chapter_index=0,
        book_seed="seed",
    )
    assert "story ahead" in picked


def test_identity_contract_banned_penalty():
    contract = load_book_identity_contract("financial_stress")
    assert contract is not None
    assert banned_phrase_penalty("numbers and nerves in the chest", contract) >= 3.0
    assert banned_phrase_penalty("the pile is heavy", contract) == 0.0


def test_hook_dedup_never_reuses_body():
    rotation = es.PersonaPoolRotationState()
    pool = [
        {"atom_id": "HOOK v01", "content": "First hook line."},
        {"atom_id": "HOOK v02", "content": "Second hook line."},
    ]
    used: set[str] = set()
    i1 = es._pick_hook_index_unique(
        rotation, pool, "seed:1", "persona", None, used
    )
    used.add(es._norm_ws(pool[i1]["content"]))
    i2 = es._pick_hook_index_unique(
        rotation, pool, "seed:2", "persona", None, used
    )
    assert pool[i1]["content"] != pool[i2]["content"]


def test_compose_emits_authored_transition_when_present(monkeypatch):
    monkeypatch.delenv("PHOENIX_ENABLE_RENDER_GLUE", raising=False)
    cc._BRIDGE_TRANSITION_CACHE = None
    monkeypatch.setattr(
        cc,
        "_authored_transition",
        lambda boundary, **kw: "Authored bridge line." if boundary == "before_story" else "",
    )
    out = cc.compose_chapter_prose(
        ["HOOK", "REFLECTION", "STORY"],
        ["Hook.", "Teaching.", "Story body."],
        chapter_index=0,
        total_chapters=12,
        topic_id="anxiety",
        persona_id="gen_z_professionals",
    )
    assert "Authored bridge line." in out
