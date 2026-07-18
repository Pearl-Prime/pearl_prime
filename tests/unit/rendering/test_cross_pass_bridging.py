"""
OPD-109 Phase 4 — cross-pass atom-stacking bridge fix.

Operator observation 2026-05-19 (production-profile 6h render, Book 3):
    "right away in i notice that it goes scene, scene, scene, scene, scene.
    just strange. hook, scene, story. scene, scene, scene is weird. jumping
    around too much"

Root cause: the depth pass in
``phoenix_v4/planning/enrichment_select.py::apply_depth_pass`` runs 3 times
for ``deep_book_6h`` (passes p1r0, p2r0, p1r1). Each pass appends fresh
``DEPTH_STORY_SCENE`` and ``DEPTH_RECOGNITION_DEPTH`` slots — 9 of each
type in Chapter 1 alone. ``_bucket_slots`` collects every ``DEPTH_*``
slot into either ``_depth_story`` or ``_depth_mech`` depending on the
sub-type, and prior code joined the vanilla ``b["STORY"]`` /
``b["REFLECTION"]`` result with the depth-stream result using a bare
``"\\n\\n".join(...)`` — leaving the vanilla→depth boundary unbridged
and producing the operator's "vignette wall" symptom in Ch1.

This module verifies the Phase 4 fix:

    1. Aggregated REFLECTION + _depth_mech (cross-stream boundary) gets
       a bridge between the vanilla and depth streams.
    2. Aggregated STORY + _depth_story (cross-stream boundary) gets a
       bridge between the vanilla and depth streams.
    3. When a depth pass runs 3 times and each pass appends 3 atoms to
       the same slot type (the operator's exact 3-pass shape), the final
       output has bridges between EVERY adjacent atom pair (8 bridges for
       9 atoms), with all bridges distinct within the chapter.
    4. Rotation state across passes: the same bridge variant is not picked
       twice in the same chapter, even when called repeatedly with growing
       atom_pair_index values that mimic a 3-pass depth append.
    5. Backward compat: bare-join behavior is preserved when no bridge_fn
       is supplied.

Defect refs:
    docs/diagnostics/OPD-109_RENDERING_LAYER_DIAGNOSIS_2026-05-18.md
    artifacts/qa/BLIND_10_VERDICT_2026-05-18.md (Book 3)
"""
from __future__ import annotations

import pytest

from phoenix_v4.rendering import chapter_composer as cc


@pytest.fixture(autouse=True)
def _enable_within_slot_bridges_for_unit_tests(monkeypatch):
    """Bridge machinery tests exercise the template path; production default is OFF."""
    monkeypatch.setattr(cc, "within_slot_bridges_enabled", lambda: True)

from phoenix_v4.rendering import golden_chapter_synthesis as gcs


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


# ---------------------------------------------------------------------------
# Test 1 — 3 depth passes × 3 atoms = 9 atoms across the depth stream
# produce 8 bridges interleaved between every adjacent atom pair.
# ---------------------------------------------------------------------------

def test_depth_pass_9_atoms_yield_8_bridges_when_aggregated() -> None:
    """The operator's exact failure shape: depth pass runs 3 times, each
    pass appends 3 DEPTH_STORY_SCENE slots. When the bucketed
    ``_depth_story`` list (9 entries) is routed through
    ``_dedupe_paragraphs`` with the STORY bridge_fn, every adjacent
    atom pair has a bridge between it — 8 bridges for 9 atoms.
    """
    pass1_atoms = [
        "Pass-one atom A1 — a sensory beat that fills out the body-first "
        "vignette with enough words to clear the short-block dedup floor.",
        "Pass-one atom A2 — another concrete moment that lands in a "
        "different room with the same alarm chemistry running.",
        "Pass-one atom A3 — a third beat completes the first depth-round "
        "append before the next pass adds to the same slot.",
    ]
    pass2_atoms = [
        "Pass-two atom B1 — the depth pass re-enters and appends a fresh "
        "beat to the same chapter slot, now in pass 2 round 0.",
        "Pass-two atom B2 — another body-first vignette, distinct from the "
        "first round's atoms so the dedup gate keeps both.",
        "Pass-two atom B3 — a third beat finishes pass two before pass one "
        "round one starts adding its three atoms.",
    ]
    pass3_atoms = [
        "Pass-three atom C1 — pass one round one appends now, after pass "
        "two finished, all three atoms entering the same DEPTH_STORY pool.",
        "Pass-three atom C2 — another distinct vignette that fills out "
        "the budget without colliding with prior dedup prefixes.",
        "Pass-three atom C3 — the final beat of the three-pass append "
        "sequence, demonstrating cross-pass aggregation.",
    ]
    all_atoms = pass1_atoms + pass2_atoms + pass3_atoms  # 9 atoms total
    bridge_fn = _bridge_fn_for_slot("STORY", chapter_index=0)
    out = gcs._dedupe_paragraphs(all_atoms, bridge_fn=bridge_fn)
    paragraphs = [p.strip() for p in out.split("\n\n") if p.strip()]
    # 9 atoms + 8 bridges = 17 paragraphs.
    assert len(paragraphs) == 17, (
        f"expected 17 paragraphs (9 atoms + 8 bridges), got {len(paragraphs)}"
    )
    # Even indices are atoms; odd indices are bridges.
    for atom_idx, original in zip(range(0, 17, 2), all_atoms):
        assert paragraphs[atom_idx] == original, (
            f"atom at position {atom_idx} mismatched"
        )
    # All 8 bridges are non-empty.
    bridges = [paragraphs[i] for i in range(1, 17, 2)]
    for b in bridges:
        assert b, "bridge slot was empty"


# ---------------------------------------------------------------------------
# Test 2 — REFLECTION + _depth_mech aggregation places a bridge at the
# vanilla/depth boundary, matching how build_virtual_slot_streams aggregates.
# ---------------------------------------------------------------------------

def test_aggregated_reflection_and_depth_mech_bridges_across_streams() -> None:
    """build_virtual_slot_streams aggregates REFLECTION + _depth_mech into a
    single bridge-aware stream so a transition appears between the vanilla
    reflection block and the depth-pass mechanism block. Prior code joined
    the two streams with bare ``\\n\\n``, leaving the boundary unbridged.
    """
    vanilla_reflection = (
        "The body responds to prediction with the same chemistry it uses for "
        "actual danger. Knowing that does not stop the chemistry — it makes "
        "the chemistry legible."
    )
    depth_mech_1 = (
        "Underneath the feeling is a simple mechanism: the alarm treats "
        "uncertainty like danger. That is why ordinary moments can feel "
        "heavy before anything has actually gone wrong."
    )
    depth_mech_2 = (
        "What drives this is an old threat model running in modern rooms. "
        "The system was built for physical danger; now it fires inside "
        "offices, apartments, and group chats."
    )
    aggregated = [vanilla_reflection, depth_mech_1, depth_mech_2]
    bridge_fn = _bridge_fn_for_slot("REFLECTION", chapter_index=0)
    out = gcs._first_or_join(aggregated, chapter_index=0, bridge_fn=bridge_fn)
    paragraphs = [p.strip() for p in out.split("\n\n") if p.strip()]
    # 3 atoms + 2 bridges = 5 paragraphs.
    assert len(paragraphs) == 5, (
        f"expected 5 paragraphs, got {len(paragraphs)}: {paragraphs}"
    )
    assert paragraphs[0] == vanilla_reflection
    assert paragraphs[2] == depth_mech_1
    assert paragraphs[4] == depth_mech_2
    # Boundary bridge between vanilla and depth must be non-empty.
    assert paragraphs[1], "vanilla→depth boundary bridge missing"
    # Bridge between two depth atoms must be non-empty.
    assert paragraphs[3], "depth→depth boundary bridge missing"


def test_aggregated_story_and_depth_story_bridges_across_streams() -> None:
    """Same aggregation guarantee for the STORY + _depth_story merge."""
    vanilla_story = (
        "At 4:02 p.m., you read the message a fourth time. Your hand is "
        "warmer than it should be. The reply window in your head has been "
        "open for nineteen minutes."
    )
    depth_story_1 = (
        "On the elevator, your watch is at 96 bpm. The other people in the "
        "car cannot see the number, but you know it is in the room."
    )
    depth_story_2 = (
        "Wednesday at 9:14 a.m., you check the calendar and your jaw tightens "
        "at the same moment, before any sentence about the day has formed."
    )
    aggregated = [vanilla_story, depth_story_1, depth_story_2]
    bridge_fn = _bridge_fn_for_slot("STORY", chapter_index=3)
    out = gcs._first_or_join(aggregated, chapter_index=3, bridge_fn=bridge_fn)
    paragraphs = [p.strip() for p in out.split("\n\n") if p.strip()]
    assert len(paragraphs) == 5, (
        f"expected 5 paragraphs, got {len(paragraphs)}: {paragraphs}"
    )
    assert paragraphs[0] == vanilla_story
    assert paragraphs[2] == depth_story_1
    assert paragraphs[4] == depth_story_2
    assert paragraphs[1], "vanilla→depth boundary bridge missing"
    assert paragraphs[3], "depth→depth boundary bridge missing"


# ---------------------------------------------------------------------------
# Test 3 — rotation state across passes: bridges do not repeat within a
# chapter, even when called multiple times with growing atom_pair_index.
# ---------------------------------------------------------------------------

def test_rotation_state_persists_across_passes() -> None:
    """Simulate three depth passes each appending atoms to the same chapter
    slot. After all three passes, all bridges in the chapter should be
    distinct (the rotation state keeps per-chapter no-reuse semantics).
    """
    chapter_index = 0
    # Use the per-render TLS rotation state path so the bridge generator
    # tracks chapter-level reuse across calls.
    state = cc.WithinSlotRotationState()
    bridges: list[str] = []
    # 3 passes, each with 3 new atoms appended → 8 bridge call boundaries.
    base_atoms = [
        f"Pass {p} atom {a} — a concrete sensory beat that runs to about "
        f"twenty-five words so it survives the _dedupe_paragraphs short-block "
        f"filter."
        for p in (1, 2, 3)
        for a in (1, 2, 3)
    ]
    for i in range(1, len(base_atoms)):
        text = cc._bridge_within_slot(
            prev_atom=base_atoms[i - 1],
            next_atom=base_atoms[i],
            slot_type="STORY",
            atom_pair_index=i - 1,
            chapter_index=chapter_index,
            rotation_state=state,
        )
        assert text, f"bridge at pair {i} should be non-empty"
        bridges.append(text)
    # All bridges within the chapter must be distinct.
    assert len(bridges) == len(set(bridges)), (
        f"bridges repeated within a chapter: "
        f"{[(b, bridges.count(b)) for b in set(bridges) if bridges.count(b) > 1]}"
    )


# ---------------------------------------------------------------------------
# Test 4 — backward compatibility: bare-join behavior is preserved when no
# bridge_fn is supplied (every existing caller stays green).
# ---------------------------------------------------------------------------

def test_first_or_join_single_atom_no_bridge_fn_is_backward_compat() -> None:
    """Single-block path with no bridge_fn returns the block unchanged."""
    atom = (
        "One atom of body-first prose. The chest tightens, the jaw locks, "
        "the breath rises. The mind has not yet supplied a story."
    )
    out = gcs._first_or_join([atom])
    assert out == atom


def test_aggregated_no_bridge_fn_is_backward_compat() -> None:
    """Multi-block path with no bridge_fn produces the legacy bare-join."""
    atoms = [
        "Body tightens before the story arrives. The signal is older than the words.",
        "Then a prediction lands: this will go badly. The prediction arrives before evidence.",
    ]
    out_legacy = gcs._first_or_join(atoms)
    out_with_none = gcs._first_or_join(atoms, bridge_fn=None)
    assert out_legacy == out_with_none


# ---------------------------------------------------------------------------
# Test 5 — bridges are deterministic across re-renders with the same input
# (same chapter index + same slot type + same atom_pair_index).
# ---------------------------------------------------------------------------

def test_cross_pass_bridges_are_deterministic() -> None:
    atoms = [
        "Atom one — twenty-five words minimum so this paragraph survives the "
        "short-block filter inside _dedupe_paragraphs.",
        "Atom two — same length floor so the dedup gate does not drop the "
        "block before any bridge can be inserted between it and atom one.",
        "Atom three — another sensory beat that lands cleanly without "
        "tripping the prefix or suffix dedup keys.",
    ]
    bridge_fn_a = _bridge_fn_for_slot("STORY", chapter_index=0)
    bridge_fn_b = _bridge_fn_for_slot("STORY", chapter_index=0)
    out_a = gcs._first_or_join(atoms, chapter_index=0, bridge_fn=bridge_fn_a)
    out_b = gcs._first_or_join(atoms, chapter_index=0, bridge_fn=bridge_fn_b)
    assert out_a == out_b
    # The output has 3 atoms + 2 bridges = 5 paragraphs.
    paragraphs = [p.strip() for p in out_a.split("\n\n") if p.strip()]
    assert len(paragraphs) == 5
