"""
OPD-109 Phase 3 — persona pool rotation selector tests.

Defect ref: ws_opd109_phase3_selector_dedup_fix_20260519
Validation: 96 SCENE-class slots in deep_book_6h picked only 3-5 unique atoms
            out of a 57-atom pool. Selector was hash-only (no book-level
            rotation), and the within-slot expansion path read `persona_expand_pool`
            from a stale `None` declaration so the expansion never fired for
            persona content.

Fix (this commit): `PersonaPoolRotationState` ranks pool indices by book-level
usage (lowest first) with deterministic SHA tiebreak. Wired through:
    1. `select_enrichment` (primary persona pick),
    2. `_expand_atom_pool_blocks` (within-slot expansion),
    3. EXERCISE persona-pool fallthrough (OPD-107 follow-up).

These tests cover:
    1. Pool utilization: 96 slot picks across a 57-atom pool → 50%+ unique.
       In practice rotation gets near 100% (all 57 atoms touched, max use ~3-4).
    2. Slot expansion utilization: 96 slots × 1 primary + 3 expansion atoms
       = 384 picks → all 57 atoms touched, max use ≤ 8.
    3. Seed-determinism: same seed + same atom pool produces identical pick
       sequence so re-renders reproduce the same book.
    4. Hash-anchor tiebreak: when no atom has been used yet, the rotation
       state defers to the existing `_deterministic_index(seed_key, n)`.
"""
from __future__ import annotations

from collections import Counter

import pytest

from phoenix_v4.planning.enrichment_select import (
    PersonaPoolRotationState,
    _expand_atom_pool_blocks,
)
from phoenix_v4.planning.registry_resolver import _deterministic_index


def _build_pool(n: int) -> list[dict]:
    """Make a pool of n distinct atom dicts with unique 11+-word content bodies."""
    return [
        {
            "atom_id": f"atom_{i:03d}",
            "content": (
                f"This is atom variant number {i} lorem ipsum dolor sit amet "
                f"consectetur adipiscing elit sed do eiusmod tempor."
            ),
        }
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# Test 1: primary-pick rotation reaches >50% utilization across 96 slots.
# ---------------------------------------------------------------------------


def test_primary_pick_rotation_uses_more_than_50pct_of_pool() -> None:
    """Confirms the OPD-109 Phase 3 fix raises pool utilization above 50%."""
    state = PersonaPoolRotationState()
    pool = _build_pool(57)  # matches gen_z_professionals/anxiety SCENE pool size

    counts: Counter[str] = Counter()
    for slot_n in range(96):  # 96 SCENE-class slots in deep_book_6h
        seed_key = f"seed1:topic:anxiety:ch{slot_n // 8 + 1}:slot:{slot_n % 8}:SCENE"
        idx = state.pick_index(pool, seed_key)
        aid = pool[idx]["atom_id"]
        state.register(aid)
        counts[aid] += 1

    unique_used = len(counts)
    assert unique_used >= 29, (  # 50% of 57 = 28.5 → 29
        f"Pool utilization regressed: {unique_used}/57 atoms used (want >= 29)"
    )
    # Sanity: rotation should also flatten the histogram. With 96 picks and 57
    # atoms, perfect distribution is ~1.7 uses/atom. Cap at 3 (rotation tiebreak
    # plus picked-first-twice atoms during the first sweep through the pool).
    most_used = counts.most_common(1)[0][1]
    assert most_used <= 3, (
        f"Top atom used {most_used} times; rotation should cap below 4 across 96 picks."
    )


# ---------------------------------------------------------------------------
# Test 2: expansion-pool rotation across 96 slots + 3 extras each.
# ---------------------------------------------------------------------------


def test_expansion_pool_rotation_full_pool_coverage() -> None:
    """With expansion-rotation, 96 slots × 4 atoms (1 primary + 3 extras) must
    exercise the full 57-atom pool and cap any single atom at <= 8 uses.
    """
    state = PersonaPoolRotationState()
    pool = _build_pool(57)

    content_to_aid = {atom["content"]: atom["atom_id"] for atom in pool}
    counts: Counter[str] = Counter()

    for slot_n in range(96):
        seed_key = f"seed1:topic:anxiety:ch{slot_n // 8 + 1}:slot:{slot_n % 8}:STORY"
        primary_idx = state.pick_index(pool, seed_key)
        primary_aid = pool[primary_idx]["atom_id"]
        state.register(primary_aid)
        counts[primary_aid] += 1

        extras = _expand_atom_pool_blocks(
            pool,
            primary_idx,
            seed_key,
            "persona_x",
            goal_extra_words=400,
            max_chunks=3,
            rotation_state=state,
        )
        for content in extras:
            aid = content_to_aid.get(content.strip())
            if aid is not None:
                counts[aid] += 1

    unique = len(counts)
    assert unique == 57, (
        f"Expansion failed to use full pool: {unique}/57 atoms used."
    )
    most_used = counts.most_common(1)[0][1]
    assert most_used <= 8, (
        f"Top atom used {most_used} times; rotation should cap at 8 across 96×4=384 picks."
    )


# ---------------------------------------------------------------------------
# Test 3: seed-determinism (re-runs at same seed produce same picks).
# ---------------------------------------------------------------------------


def test_rotation_state_is_seed_deterministic() -> None:
    """Two independent rotation states given the same seed_key sequence pick
    the same atom IDs in the same order. Critical for re-render reproducibility.
    """
    pool = _build_pool(57)
    seq_a: list[int] = []
    seq_b: list[int] = []

    state_a = PersonaPoolRotationState()
    state_b = PersonaPoolRotationState()

    for slot_n in range(40):
        seed_key = f"seed1:slot:{slot_n}"
        ia = state_a.pick_index(pool, seed_key)
        state_a.register(pool[ia]["atom_id"])
        seq_a.append(ia)

        ib = state_b.pick_index(pool, seed_key)
        state_b.register(pool[ib]["atom_id"])
        seq_b.append(ib)

    assert seq_a == seq_b, (
        "Rotation state is non-deterministic: same seed_key sequence produced "
        f"different picks.\n  A: {seq_a[:10]}...\n  B: {seq_b[:10]}..."
    )


# ---------------------------------------------------------------------------
# Test 4: empty rotation state defers to hash-anchor.
# ---------------------------------------------------------------------------


def test_empty_rotation_defers_to_hash_anchor() -> None:
    """First pick on a fresh rotation state must match the legacy
    `_deterministic_index` result, so existing callers see no behavior change
    on the first call.
    """
    pool = _build_pool(57)
    state = PersonaPoolRotationState()
    seed_key = "seed1:topic:anxiety:ch1:slot:0:HOOK:persona"

    rotation_pick = state.pick_index(pool, seed_key)
    legacy_pick = _deterministic_index(seed_key, len(pool))

    assert rotation_pick == legacy_pick, (
        f"Empty rotation state diverged from hash anchor: "
        f"rotation_pick={rotation_pick} vs legacy_pick={legacy_pick}"
    )


# ---------------------------------------------------------------------------
# Test 5: pre-fix histogram simulation (regression smoke).
# ---------------------------------------------------------------------------


def test_expansion_without_rotation_state_legacy_behavior() -> None:
    """When `rotation_state=None`, `_expand_atom_pool_blocks` falls back to
    SHA-only ordering. This protects existing callers that have not been
    updated to thread the rotation state through.
    """
    pool = _build_pool(20)
    extras_a = _expand_atom_pool_blocks(
        pool, primary_idx=5, seed_key="seedA", label="persona_x",
        goal_extra_words=200, max_chunks=4, rotation_state=None,
    )
    extras_b = _expand_atom_pool_blocks(
        pool, primary_idx=5, seed_key="seedA", label="persona_x",
        goal_extra_words=200, max_chunks=4, rotation_state=None,
    )
    assert extras_a == extras_b, (
        "Legacy (no rotation_state) path must be deterministic."
    )
    assert len(extras_a) > 0, "Expansion should return non-empty extras."
