"""Tests for the TEACHER_DOCTRINE entry in ``_TEACHER_TYPE_MAP``.

Before this fix the lookup chain for ``sec_type == "TEACHER_DOCTRINE"`` was::

    _TEACHER_TYPE_MAP["TEACHER_DOCTRINE"] == ["COMPRESSION", "REFLECTION", "TEACHING"]

so atoms an operator placed under
``SOURCE_OF_TRUTH/teacher_banks/<teacher>/approved_atoms/TEACHER_DOCTRINE/``
were never resolved by ``registry_resolver.resolve_book`` /
``enrichment_select._pick_teacher_pool``. Pearl_Writer #4 worked around the
bug in PR #1230 by dual-locating the new ahjan doctrine atoms in both
``TEACHER_DOCTRINE/`` (operator-canonical) and ``COMPRESSION/`` (where the
resolver actually looked).

The fix inserts ``"TEACHER_DOCTRINE"`` as the FIRST directory in the chain::

    _TEACHER_TYPE_MAP["TEACHER_DOCTRINE"] ==
        ["TEACHER_DOCTRINE", "COMPRESSION", "REFLECTION", "TEACHING"]

The fix is additive — teachers without a ``TEACHER_DOCTRINE/`` directory on
disk still resolve via the legacy ``COMPRESSION → REFLECTION → TEACHING``
fallback. Teachers that DO have a ``TEACHER_DOCTRINE/`` directory now have
those atoms reach the slot.
"""
from __future__ import annotations

from typing import Dict, List

import pytest

from phoenix_v4.planning import registry_resolver as rr
from phoenix_v4.planning.registry_resolver import (
    _TEACHER_TYPE_MAP,
    resolve_book,
)


# ---------------------------------------------------------------------------
# Fixtures — synthetic teacher_atoms shaped like the on-disk loader output.
# ---------------------------------------------------------------------------


def _atom(atom_id: str, body: str) -> dict:
    """Match the shape ``_load_teacher_atoms`` returns per atom."""
    return {"atom_id": atom_id, "content": body, "metadata": {}}


_DOCTRINE_ATOM = _atom(
    "fake_TEACHER_DOCTRINE_001",
    "From the TEACHER_DOCTRINE directory — canonical doctrine slot.",
)
_COMPRESSION_ATOM = _atom(
    "fake_COMPRESSION_001",
    "From the COMPRESSION directory — legacy compressed-doctrine fallback.",
)
_REFLECTION_ATOM = _atom(
    "fake_REFLECTION_001",
    "From the REFLECTION directory — secondary fallback.",
)
_TEACHING_ATOM = _atom(
    "fake_TEACHING_001",
    "From the TEACHING directory — tertiary backward-compat fallback.",
)


def _make_registry() -> dict:
    """Single-chapter, single-section TEACHER_DOCTRINE registry."""
    return {
        "topic": "fixture_topic",
        "sections": {
            "chapter_01": {
                "chapter": 1,
                "title": "Fixture Chapter",
                "sections": {
                    "section_01": {
                        "section_id": "ch01_sec01",
                        "type": "TEACHER_DOCTRINE",
                        "purpose": "test doctrine resolution",
                        "variants": [
                            {
                                "variant_id": "ch01_sec01_registry_v1",
                                "content": "Registry variant (should be overlaid).",
                            }
                        ],
                    }
                },
            }
        },
    }


# ---------------------------------------------------------------------------
# Test 1 — TEACHER_DOCTRINE/ wins when populated.
# ---------------------------------------------------------------------------


def test_doctrine_dir_resolves_first_when_populated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Teacher with TEACHER_DOCTRINE/ atoms: resolver picks from there FIRST."""
    fake_atoms: Dict[str, List[dict]] = {
        "TEACHER_DOCTRINE": [_DOCTRINE_ATOM],
        # COMPRESSION/REFLECTION/TEACHING populated too — must NOT be picked.
        "COMPRESSION": [_COMPRESSION_ATOM],
        "REFLECTION": [_REFLECTION_ATOM],
        "TEACHING": [_TEACHING_ATOM],
    }
    monkeypatch.setattr(rr, "_load_teacher_atoms", lambda teacher_id: fake_atoms)

    book = resolve_book(_make_registry(), seed="seed_doctrine_wins", teacher_id="fake_teacher")

    assert book.chapter_count == 1
    sec = book.chapters[0].sections[0]
    assert sec.variant_id == "fake_TEACHER_DOCTRINE_001", (
        f"Expected TEACHER_DOCTRINE/ atom to win; got {sec.variant_id!r}"
    )
    assert sec.content == _DOCTRINE_ATOM["content"]


# ---------------------------------------------------------------------------
# Test 2 — Backward-compat: COMPRESSION/ still resolves when TEACHER_DOCTRINE/
# is absent (the pre-fix behavior, preserved).
# ---------------------------------------------------------------------------


def test_compression_fallback_when_no_doctrine_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    """Teacher without TEACHER_DOCTRINE/ atoms still resolves via COMPRESSION/."""
    fake_atoms: Dict[str, List[dict]] = {
        # No "TEACHER_DOCTRINE" key — simulating teacher banks for adi_da,
        # joshin, junko, etc. that don't yet have an explicit doctrine dir.
        "COMPRESSION": [_COMPRESSION_ATOM],
        "REFLECTION": [_REFLECTION_ATOM],
        "TEACHING": [_TEACHING_ATOM],
    }
    monkeypatch.setattr(rr, "_load_teacher_atoms", lambda teacher_id: fake_atoms)

    book = resolve_book(_make_registry(), seed="seed_legacy_compat", teacher_id="fake_teacher")

    sec = book.chapters[0].sections[0]
    assert sec.variant_id == "fake_COMPRESSION_001", (
        f"Expected COMPRESSION/ fallback when no TEACHER_DOCTRINE/; got {sec.variant_id!r}"
    )
    assert sec.content == _COMPRESSION_ATOM["content"]


# ---------------------------------------------------------------------------
# Test 3 — Strict lookup-chain order:
#   TEACHER_DOCTRINE → COMPRESSION → REFLECTION → TEACHING
# ---------------------------------------------------------------------------


def test_lookup_chain_order_is_canonical() -> None:
    """The TEACHER_DOCTRINE chain must be exactly the canonical order."""
    assert _TEACHER_TYPE_MAP["TEACHER_DOCTRINE"] == [
        "TEACHER_DOCTRINE",
        "COMPRESSION",
        "REFLECTION",
        "TEACHING",
    ]


def test_chain_order_walked_in_sequence(monkeypatch: pytest.MonkeyPatch) -> None:
    """Drive the chain end-to-end: each successive dir becomes the winner only
    after every earlier dir is empty."""

    # (atoms_dict, expected_winner_variant_id)
    cases: List[tuple[Dict[str, List[dict]], str]] = [
        # All four populated → TEACHER_DOCTRINE wins.
        (
            {
                "TEACHER_DOCTRINE": [_DOCTRINE_ATOM],
                "COMPRESSION": [_COMPRESSION_ATOM],
                "REFLECTION": [_REFLECTION_ATOM],
                "TEACHING": [_TEACHING_ATOM],
            },
            "fake_TEACHER_DOCTRINE_001",
        ),
        # No TEACHER_DOCTRINE → COMPRESSION wins.
        (
            {
                "COMPRESSION": [_COMPRESSION_ATOM],
                "REFLECTION": [_REFLECTION_ATOM],
                "TEACHING": [_TEACHING_ATOM],
            },
            "fake_COMPRESSION_001",
        ),
        # No TEACHER_DOCTRINE, no COMPRESSION → REFLECTION wins.
        (
            {
                "REFLECTION": [_REFLECTION_ATOM],
                "TEACHING": [_TEACHING_ATOM],
            },
            "fake_REFLECTION_001",
        ),
        # Only TEACHING populated → TEACHING wins (final backward-compat slot).
        (
            {"TEACHING": [_TEACHING_ATOM]},
            "fake_TEACHING_001",
        ),
    ]

    for atoms_dict, expected_id in cases:
        monkeypatch.setattr(rr, "_load_teacher_atoms", lambda teacher_id, a=atoms_dict: a)
        book = resolve_book(
            _make_registry(),
            seed=f"seed_chain_{expected_id}",
            teacher_id="fake_teacher",
        )
        sec = book.chapters[0].sections[0]
        assert sec.variant_id == expected_id, (
            f"Chain order broken: pools={list(atoms_dict.keys())} "
            f"expected={expected_id} got={sec.variant_id}"
        )


# ---------------------------------------------------------------------------
# Test 4 — Empty pool at a layer is skipped (zero-length list != absent key).
# ---------------------------------------------------------------------------


def test_empty_pool_falls_through(monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty-list pool at one layer must not short-circuit the chain."""
    fake_atoms: Dict[str, List[dict]] = {
        "TEACHER_DOCTRINE": [],  # explicitly empty
        "COMPRESSION": [_COMPRESSION_ATOM],
    }
    monkeypatch.setattr(rr, "_load_teacher_atoms", lambda teacher_id: fake_atoms)

    book = resolve_book(_make_registry(), seed="seed_empty_skip", teacher_id="fake_teacher")
    sec = book.chapters[0].sections[0]
    assert sec.variant_id == "fake_COMPRESSION_001"
