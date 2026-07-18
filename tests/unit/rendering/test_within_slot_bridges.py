"""
OPD-109 Phase 1 — within-slot bridge generator + cap reductions.

Defect ref: docs/diagnostics/OPD-109_RENDERING_LAYER_DIAGNOSIS_2026-05-18.md
Operator ref: artifacts/qa/BLIND_10_VERDICT_2026-05-18.md Book 3

These tests cover:
    1. A slot with 5 atoms produces output with 4 bridges interleaved.
    2. A slot with 1 atom produces no bridges (no-op).
    3. Bridge families load correctly from YAML.
    4. Deterministic: same (chapter_index, slot_type, atom_pair_index)
       always returns the same bridge.
    5. Backward compat: `_dedupe_paragraphs` without `bridge_fn` produces
       identical output to before.
    6. Empty / unknown slot type falls back to default family or returns "".
"""
from __future__ import annotations

import pytest

from phoenix_v4.rendering import chapter_composer as cc
from phoenix_v4.rendering import golden_chapter_synthesis as gcs


@pytest.fixture(autouse=True)
def _enable_within_slot_bridges_for_unit_tests(monkeypatch):
    """Bridge machinery tests exercise the template path; production default is OFF."""
    monkeypatch.setattr(cc, "within_slot_bridges_enabled", lambda: True)


# ---------------------------------------------------------------------------
# Test 3: bridge families load correctly from YAML
# ---------------------------------------------------------------------------

def test_within_slot_bridge_families_yaml_loads() -> None:
    payload = cc._load_within_slot_bridge_families()
    assert isinstance(payload, dict)
    assert "slot_families" in payload
    families = payload["slot_families"]
    assert isinstance(families, dict)
    # All eight required slot types from OPD-109 prompt should be present.
    for slot_type in (
        "STORY",
        "REFLECTION",
        "EXERCISE",
        "INTEGRATION",
        "TEACHER_DOCTRINE",
        "SCENE",
        "COMPRESSION",
        "HOOK",
    ):
        assert slot_type in families, f"missing slot family: {slot_type}"
        family = families[slot_type]
        assert isinstance(family, dict) and family
        # Each shape has at least one text entry with a non-empty 'text' field.
        for shape, entries in family.items():
            assert isinstance(entries, list) and entries
            for entry in entries:
                assert isinstance(entry, dict)
                assert str(entry.get("text") or "").strip()


# ---------------------------------------------------------------------------
# Test 4: deterministic with fixed (chapter, slot, atom_pair_index)
# ---------------------------------------------------------------------------

def test_bridge_within_slot_is_deterministic() -> None:
    a = cc._bridge_within_slot(
        prev_atom="The body tightened before the mind caught up.",
        next_atom="Across town, another body did the same thing.",
        slot_type="STORY",
        atom_pair_index=0,
        chapter_index=0,
    )
    b = cc._bridge_within_slot(
        prev_atom="The body tightened before the mind caught up.",
        next_atom="Across town, another body did the same thing.",
        slot_type="STORY",
        atom_pair_index=0,
        chapter_index=0,
    )
    assert a == b
    assert a, "deterministic bridge should return a non-empty string for STORY"


def test_bridge_within_slot_varies_with_atom_pair_index() -> None:
    """Adjacent atom pairs should rotate through shape buckets so the
    chapter does not see the same shape repeated back-to-back."""
    seen_shapes: list[str] = []
    for i in range(4):
        text = cc._bridge_within_slot(
            prev_atom=f"prev {i}",
            next_atom=f"next {i}",
            slot_type="STORY",
            atom_pair_index=i,
            chapter_index=2,
        )
        assert text, f"empty bridge at index {i}"
        seen_shapes.append(text)
    # We expect at least 2 distinct bridge sentences across 4 indices.
    assert len(set(seen_shapes)) >= 2


# ---------------------------------------------------------------------------
# Test 6: unknown slot type falls back gracefully
# ---------------------------------------------------------------------------

def test_bridge_within_slot_unknown_falls_back_to_default() -> None:
    text = cc._bridge_within_slot(
        prev_atom="some prev atom",
        next_atom="some next atom",
        slot_type="THIS_IS_NOT_A_REAL_SLOT_TYPE",
        atom_pair_index=0,
        chapter_index=0,
    )
    # default_family is defined in the YAML; should produce a non-empty bridge.
    assert text, "default_family fallback should produce a non-empty bridge"


# ---------------------------------------------------------------------------
# Test 1: 5 atoms in a slot → 4 bridges interleaved
# ---------------------------------------------------------------------------

def _bridge_fn_for_slot(slot_type: str, chapter_index: int):
    """Build a bridge_fn closure (mirrors what build_virtual_slot_streams does)."""

    def _fn(prev: str, nxt: str, idx: int) -> str:
        return cc._bridge_within_slot(
            prev_atom=prev,
            next_atom=nxt,
            slot_type=slot_type,
            atom_pair_index=idx,
            chapter_index=chapter_index,
        )

    return _fn


def test_dedupe_paragraphs_interleaves_bridges_for_5_atoms() -> None:
    atoms = [
        "First, the body tightens before the mind has a story to attach to it. The chest goes thin, the jaw locks, the shoulders rise.",
        "Then, an old prediction fires: this will go badly. The prediction arrives before any evidence has been weighed.",
        "The system narrows. Attention shrinks to the threat. Everything else falls away from view.",
        "Behavior becomes either freeze, or rehearse. Freeze keeps the body still; rehearse keeps the mind looping.",
        "Eventually, the moment passes. The body unwinds in its own time, no faster than that.",
    ]
    bridge_fn = _bridge_fn_for_slot("STORY", chapter_index=0)
    out = gcs._dedupe_paragraphs(atoms, bridge_fn=bridge_fn)
    paragraphs = [p.strip() for p in out.split("\n\n") if p.strip()]
    # 5 atoms + 4 bridges = 9 paragraphs
    assert len(paragraphs) == 9, f"expected 9 paragraphs, got {len(paragraphs)}: {paragraphs}"
    # Even indices (0,2,4,6,8) are atoms, odd indices (1,3,5,7) are bridges.
    for atom_idx, original in zip([0, 2, 4, 6, 8], atoms):
        assert original.strip() == paragraphs[atom_idx], (
            f"atom position {atom_idx} should match original atom: "
            f"got {paragraphs[atom_idx][:80]!r}, expected {original[:80]!r}"
        )
    # Every bridge slot must be non-empty.
    for bridge_idx in (1, 3, 5, 7):
        assert paragraphs[bridge_idx], f"bridge at index {bridge_idx} is empty"


# ---------------------------------------------------------------------------
# Test 2: 1 atom → no bridges (no-op)
# ---------------------------------------------------------------------------

def test_dedupe_paragraphs_no_bridge_for_single_atom() -> None:
    atoms = [
        "Only one atom in this slot — nothing to bridge to.",
    ]
    bridge_fn = _bridge_fn_for_slot("STORY", chapter_index=0)
    out = gcs._dedupe_paragraphs(atoms, bridge_fn=bridge_fn)
    paragraphs = [p.strip() for p in out.split("\n\n") if p.strip()]
    assert len(paragraphs) == 1
    assert paragraphs[0] == atoms[0]


# ---------------------------------------------------------------------------
# Test 5: backward compatibility — no bridge_fn → bare-join output unchanged
# ---------------------------------------------------------------------------

def test_dedupe_paragraphs_without_bridge_fn_is_backward_compat() -> None:
    """Callers that don't pass bridge_fn must get the legacy bare-join output."""
    atoms = [
        "Body tightens before the story arrives. The signal is older than the words.",
        "Then a prediction lands: this will go badly. The prediction arrives before evidence.",
        "Attention narrows. Everything outside the threat dims down for a moment.",
    ]
    out_legacy = gcs._dedupe_paragraphs(atoms)
    out_with_none = gcs._dedupe_paragraphs(atoms, bridge_fn=None)
    assert out_legacy == out_with_none
    paragraphs = [p.strip() for p in out_legacy.split("\n\n") if p.strip()]
    # 3 atoms, no bridges
    assert len(paragraphs) == 3


def test_first_or_join_without_bridge_fn_is_backward_compat() -> None:
    atoms = [
        "Body tightens before the story arrives. The signal is older than the words.",
        "Then a prediction lands: this will go badly. The prediction arrives before evidence.",
    ]
    out_legacy = gcs._first_or_join(atoms)
    out_with_none = gcs._first_or_join(atoms, bridge_fn=None)
    assert out_legacy == out_with_none


# ---------------------------------------------------------------------------
# Test: bridge_fn that raises is treated as no-op (defensive)
# ---------------------------------------------------------------------------

def test_dedupe_paragraphs_bridge_fn_exception_safe() -> None:
    """If bridge_fn raises, the atom-join should still succeed without bridges."""
    atoms = [
        "First atom with enough body to survive the min-length filter.",
        "Second atom with enough body to survive the min-length filter.",
    ]

    def _broken(prev: str, nxt: str, idx: int) -> str:  # pragma: no cover - error path
        raise RuntimeError("bridge generator broke")

    out = gcs._dedupe_paragraphs(atoms, bridge_fn=_broken)
    paragraphs = [p.strip() for p in out.split("\n\n") if p.strip()]
    # Still get both atoms; bridge swallowed.
    assert len(paragraphs) == 2


# ---------------------------------------------------------------------------
# Test: cap reductions on _max_extra_chunks_for_format (OPD-109 Phase 1)
# ---------------------------------------------------------------------------

def test_max_extra_chunks_cap_reductions() -> None:
    """OPD-109 Phase 1 caps:
        - extended_book_2h: was 5 → 4
        - deep_book_4h:     was 7 → 5
        - deep_book_6h:     was 18 (cap 24) → 8 (cap 12)
        - hard cap min(24, ...) → min(12, ...)
    """
    from phoenix_v4.planning.enrichment_select import _max_extra_chunks_for_format

    # extended_book_2h base 4
    assert _max_extra_chunks_for_format("extended_book_2h", 320) == 4
    # deep_book_4h base 5
    assert _max_extra_chunks_for_format("deep_book_4h", 320) == 5
    # deep_book_6h base 8 (was 18); hard cap at 12 (was 24)
    assert _max_extra_chunks_for_format("deep_book_6h", 320) == 8
    # Large slot_target_words → still bounded by hard cap of 12 (was 24)
    assert _max_extra_chunks_for_format("deep_book_6h", 5000) == 12
    # Other formats unchanged
    assert _max_extra_chunks_for_format("standard_book", 320) == 3
    assert _max_extra_chunks_for_format("micro_book_15", 320) == 0
    assert _max_extra_chunks_for_format("short_book_30", 320) == 1


def test_within_slot_bridge_destack_skips_adjacent_injects():
    from phoenix_v4.rendering.register_output_strengthen import (
        destack_adjacent_inject_paragraphs,
    )

    bridge = "The mechanism behind this pattern is small and stubborn."
    dep = "An ordinary pace is a sustainable pace."
    body = f"{bridge}\n\n{dep}\n\n{'Narrative paragraph content here.' * 3}"
    out = destack_adjacent_inject_paragraphs(f"Chapter 1\n\n{body}")
    assert bridge in out
    assert dep not in out
