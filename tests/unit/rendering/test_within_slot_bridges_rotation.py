"""
OPD-109 Phase 1.1 — within-slot bridge rotation tests.

Defect ref: docs/diagnostics/OPD-109_RENDERING_LAYER_DIAGNOSIS_2026-05-18.md
Validation: artifacts/pearl_prime/deep_book_6h/...POST_MERGE_VALIDATION_2026-05-19/
            book_quality_report.json showed 54-59 occurrences of single bridge
            templates (vs. book-wide cap of 12).

Fix: variants expanded ~3x per shape, rotation state added in
`chapter_composer._bridge_within_slot` so the renderer prefers variants not
yet used in the book and never reuses a variant within a single chapter.

These tests cover:
    1. Per-book load spread: across 12 chapters of mock bridge calls, no
       single variant is used more than ceil(total_uses / N_variants) + 1.
    2. Per-chapter no-reuse: a 5-atom slot (4 bridges) inside one chapter
       uses 4 DIFFERENT bridge variants.
    3. Seed-determinism: same rotation state + same coordinates → same text.
    4. Book-wide cap simulation: a realistic 12-chapter render with the
       OPD-109 caps (depth_rounds=2, max_extra=8) produces NO bridge phrase
       appearing > 12 times.
"""
from __future__ import annotations

import math
from collections import Counter

import pytest

from phoenix_v4.rendering import chapter_composer as cc


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_state() -> cc.WithinSlotRotationState:
    """Return a brand-new rotation state (no leakage between tests)."""
    return cc.WithinSlotRotationState()


def _variants_in_shape(slot_type: str, shape: str) -> int:
    """Count variants in one shape bucket (for the per-book spread test)."""
    payload = cc._load_within_slot_bridge_families()
    families = payload.get("slot_families") or {}
    family = families.get(slot_type.upper()) or {}
    entries = family.get(shape) or []
    return len(entries)


def _total_variants_in_family(slot_type: str) -> int:
    """Count variants across all shapes in one slot family."""
    payload = cc._load_within_slot_bridge_families()
    family = (payload.get("slot_families") or {}).get(slot_type.upper()) or {}
    return sum(len(entries) for entries in family.values() if isinstance(entries, list))


# ---------------------------------------------------------------------------
# Test 1: across 12 chapters, no single bridge variant is used more than
# ceil(total_uses / N_variants_in_family) + 1 times.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("slot_type", ["STORY", "REFLECTION", "EXERCISE", "SCENE"])
def test_book_wide_load_spread_across_12_chapters(slot_type: str) -> None:
    """Simulate 12 chapters, each with 6 atom-pairs in the same slot type.

    Total uses = 72. With rotation state preferring least-used variants,
    no single variant should be used more than ceil(72 / N_variants) + 1.
    """
    state = _fresh_state()
    n_chapters = 12
    pairs_per_chapter = 6  # realistic for deep_book_6h after OPD-109 caps
    total_uses = n_chapters * pairs_per_chapter
    n_variants = _total_variants_in_family(slot_type)
    assert n_variants >= 8, (
        f"{slot_type} has only {n_variants} variants — expansion target was >=8"
    )
    cap = math.ceil(total_uses / n_variants) + 1

    picks: Counter[str] = Counter()
    for ch in range(n_chapters):
        for pair_idx in range(pairs_per_chapter):
            text = cc._bridge_within_slot(
                prev_atom=f"prev ch{ch} pair{pair_idx}",
                next_atom=f"next ch{ch} pair{pair_idx}",
                slot_type=slot_type,
                atom_pair_index=pair_idx,
                chapter_index=ch,
                rotation_state=state,
            )
            assert text, f"empty bridge at ch{ch} pair{pair_idx}"
            picks[text] += 1

    top_text, top_count = picks.most_common(1)[0]
    assert top_count <= cap, (
        f"{slot_type}: top variant {top_text!r} used {top_count} times "
        f"(cap={cap} = ceil({total_uses}/{n_variants})+1). "
        f"Distribution: {dict(picks.most_common(5))}"
    )


# ---------------------------------------------------------------------------
# Test 2: within one chapter, a 5-atom slot uses 4 DIFFERENT bridges
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("slot_type", ["STORY", "REFLECTION", "EXERCISE", "SCENE"])
def test_within_one_chapter_5_atoms_yields_4_distinct_bridges(slot_type: str) -> None:
    """A 5-atom slot generates 4 bridges. With rotation state, all 4 must
    be different (no variant is reused inside a single chapter)."""
    state = _fresh_state()
    texts: list[str] = []
    for pair_idx in range(4):  # 5 atoms -> 4 bridges
        text = cc._bridge_within_slot(
            prev_atom=f"atom {pair_idx}",
            next_atom=f"atom {pair_idx + 1}",
            slot_type=slot_type,
            atom_pair_index=pair_idx,
            chapter_index=3,  # arbitrary fixed chapter
            rotation_state=state,
        )
        assert text, f"empty bridge at pair_idx={pair_idx}"
        texts.append(text)
    assert len(set(texts)) == 4, (
        f"{slot_type}: expected 4 distinct bridges within one chapter, got "
        f"{len(set(texts))}: {texts}"
    )


# ---------------------------------------------------------------------------
# Test 3: seed-deterministic — same seed produces same selection
# ---------------------------------------------------------------------------

def test_rotation_state_is_seed_deterministic() -> None:
    """Two independent runs with fresh rotation state and identical
    (chapter_index, slot_type, atom_pair_index) sequences must yield
    identical output."""
    seqs: list[list[str]] = []
    for _ in range(2):
        state = _fresh_state()
        run: list[str] = []
        for ch in range(4):
            for pair_idx in range(5):
                text = cc._bridge_within_slot(
                    prev_atom=f"prev ch{ch} pair{pair_idx}",
                    next_atom=f"next ch{ch} pair{pair_idx}",
                    slot_type="STORY",
                    atom_pair_index=pair_idx,
                    chapter_index=ch,
                    rotation_state=state,
                )
                run.append(text)
        seqs.append(run)
    assert seqs[0] == seqs[1], (
        "rotation should be seed-deterministic; two fresh runs diverged"
    )


def test_legacy_path_without_rotation_state_still_deterministic() -> None:
    """Backward-compat: calls that do not pass rotation_state (and where no
    TLS state is set) must still return the same value for the same input."""
    # Ensure no TLS state contaminates this test.
    cc._WITHIN_SLOT_ROTATION_TLS = None
    a = cc._bridge_within_slot(
        prev_atom="p", next_atom="n",
        slot_type="STORY", atom_pair_index=2, chapter_index=1,
    )
    b = cc._bridge_within_slot(
        prev_atom="p", next_atom="n",
        slot_type="STORY", atom_pair_index=2, chapter_index=1,
    )
    assert a == b and a, "legacy seed-only path should be stable and non-empty"


# ---------------------------------------------------------------------------
# Test 4: book-wide cap simulation — given the OPD-109 caps (depth_rounds=2,
# max_extra=8), the resulting render should have NO bridge phrase appearing > 12 times.
# ---------------------------------------------------------------------------

def test_book_wide_cap_simulation_no_phrase_exceeds_12() -> None:
    """Simulate a 12-chapter deep_book_6h render that exercises all eight
    slot families. With the OPD-109 Phase 1 caps in place each chapter now
    stacks at most ~8 atoms per slot. We approximate that with 6 atom-pairs
    per slot type (a comfortable upper bound for what the renderer actually
    emits after the cap reductions). The book-wide cap on repeated phrases
    is 12; the rotation state must spread bridges enough that no single
    template phrase reaches 13."""
    state = _fresh_state()
    slot_types = [
        "STORY",
        "REFLECTION",
        "EXERCISE",
        "INTEGRATION",
        "TEACHER_DOCTRINE",
        "SCENE",
        "COMPRESSION",
        "HOOK",
    ]
    pairs_per_chapter_per_slot = 6
    n_chapters = 12

    picks: Counter[str] = Counter()
    for ch in range(n_chapters):
        for st in slot_types:
            for pair_idx in range(pairs_per_chapter_per_slot):
                text = cc._bridge_within_slot(
                    prev_atom=f"p ch{ch} {st} {pair_idx}",
                    next_atom=f"n ch{ch} {st} {pair_idx}",
                    slot_type=st,
                    atom_pair_index=pair_idx,
                    chapter_index=ch,
                    rotation_state=state,
                )
                assert text, f"empty bridge at ch{ch} {st} {pair_idx}"
                picks[text] += 1

    over_cap = [(t, c) for t, c in picks.items() if c > 12]
    assert not over_cap, (
        f"OPD-109 Phase 1.1 acceptance failure: {len(over_cap)} bridge "
        f"variants exceeded the book-wide cap of 12. "
        f"Worst offenders: {sorted(over_cap, key=lambda x: -x[1])[:5]}"
    )


# ---------------------------------------------------------------------------
# Sanity tests for the rotation state object itself
# ---------------------------------------------------------------------------

def test_rotation_state_register_increments_book_and_chapter() -> None:
    state = _fresh_state()
    state.register(0, "hello")
    state.register(0, "hello")
    state.register(1, "hello")
    assert state.book_count("hello") == 3
    assert state.chapter_has_used(0, "hello")
    assert state.chapter_has_used(1, "hello")
    assert not state.chapter_has_used(2, "hello")


def test_rotation_state_explicit_param_wins_over_tls() -> None:
    """If a caller passes rotation_state explicitly, the module-level TLS
    is NOT consulted. This protects test isolation and per-job state."""
    cc._WITHIN_SLOT_ROTATION_TLS = cc.WithinSlotRotationState()
    cc._WITHIN_SLOT_ROTATION_TLS.book_usage["should not matter"] = 99

    explicit = cc.WithinSlotRotationState()
    text = cc._bridge_within_slot(
        prev_atom="p", next_atom="n",
        slot_type="STORY", atom_pair_index=0, chapter_index=0,
        rotation_state=explicit,
    )
    # The picked text should be registered in `explicit`, not the TLS state.
    assert explicit.book_count(text) == 1
    assert cc._WITHIN_SLOT_ROTATION_TLS.book_count(text) == 0
    # Cleanup.
    cc._WITHIN_SLOT_ROTATION_TLS = None
