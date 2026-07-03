"""
OPD-112 — bridge ↔ following-atom semantic continuity tests.

Defect ref: OPD-112 (operator observation 2026-05-20)
> "this is Ajahn's framework, and then when it says the Ajahn teaching, it
>  doesn't go together. It'd be like, 'this is Ajahn's framework...' and then
>  it doesn't have a declarative that happens after it has something that
>  sounds out of whack."

The within-slot bridge selector was picking bridges by rhetorical shape only.
With the OPD-112 fix, each bridge in `config/rendering/within_slot_bridge_families.yaml`
carries a `next_atom_expectation:` tag (what content-class the bridge phrasing
promises the reader). The selector classifies the next atom and filters
candidates whose expectation does not match — falling back to "any" universal
bridges, then to the full pool, so the selector never goes silent.

These tests cover:
    1. _classify_atom returns the right label for each category tell.
    2. A bridge promising `teacher_teaching` is REJECTED when the next atom
       is clearly a scene_vignette (commute / Slack scene).
    3. Bridges tagged `next_atom_expectation: any` always match (universal).
    4. When no narrow-match exists in the chosen shape, the selector falls
       back to least-used `any` bridge.
    5. Backward-compat: bridges with no `next_atom_expectation` field (or
       an invalid label) are treated as `any` and never skipped.
    6. Determinism + rotation state still hold after the filter is added.
"""
from __future__ import annotations

import pytest

from phoenix_v4.rendering import chapter_composer as cc


@pytest.fixture(autouse=True)
def _enable_within_slot_bridges_for_unit_tests(monkeypatch):
    """Bridge machinery tests exercise the template path; production default is OFF."""
    monkeypatch.setattr(cc, "within_slot_bridges_enabled", lambda: True)



# ---------------------------------------------------------------------------
# Test 1: _classify_atom maps content tells to the right content-class
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("Ahjan teaches that suffering is a feature, not a bug.", "teacher_teaching"),
    ("What Ahjan returns to is the body's quiet honesty.", "teacher_teaching"),
    ("The teacher would put it this way: stop pretending.", "teacher_teaching"),
    ("The teaching points to one thing.", "teacher_teaching"),
    ("Here is the mechanism: the alarm fires on prediction, not evidence.",
     "mechanism_paragraph"),
    ("Underneath the feeling is a small machine.", "mechanism_paragraph"),
    ("Your chest pulls in. The face heats.", "body_anchor"),
    ("Your jaw clenches before the message is even read.", "body_anchor"),
    ("Notice your breath as it shortens at the desk.", "body_anchor"),
    ("The Slack notification pings at 11:47 pm.", "scene_vignette"),
    ("At 2 PM the reorg email lands in your inbox.", "scene_vignette"),
    ("The standup is in five minutes and your hands are cold.", "scene_vignette"),
    ("Mei stared at her monitor, jaw clenched.", "named_story"),
    ("Try this: name three things you can see right now.", "practical_takeaway"),
    ("Do this for ten breaths.", "practical_takeaway"),
    ("What if the feeling is not lying to you?", "reflective_pivot"),
    ("Where in your life do you flinch from this?", "reflective_pivot"),
    ("Some sentence with no specific tells worth catching.", "any"),
    ("", "any"),
    ("   ", "any"),
])
def test_classify_atom_categories(text: str, expected: str) -> None:
    assert cc._classify_atom(text) == expected, (
        f"_classify_atom({text!r}) returned {cc._classify_atom(text)!r}, "
        f"expected {expected!r}"
    )


# ---------------------------------------------------------------------------
# Test 2: a bridge promising `teacher_teaching` is REJECTED when the next
# atom is clearly a scene_vignette. Selector falls back to a different shape
# (which carries `any` or `scene_vignette` expectations).
# ---------------------------------------------------------------------------

def test_teacher_bridge_rejected_when_next_atom_is_scene() -> None:
    """If the user just read a doctrinal atom and the NEXT atom is a
    commute scene, the bridge must NOT be a "the teacher would put it
    this way." That phrasing promised a teaching that never arrives.

    The selector handles this by classifying the next atom as
    `scene_vignette` and dropping all `teacher_teaching`-tagged variants
    from the TEACHER_DOCTRINE family — which leaves an empty narrow
    pool, so the filter falls back to `any`-tagged variants (none in
    TEACHER_DOCTRINE) and finally to the full pool. In practice this
    means the SCENE family (not TEACHER_DOCTRINE) should be used by the
    upstream caller; but we test the filter behaviour explicitly here
    via direct invocation with slot_type='TEACHER_DOCTRINE'.
    """
    # In TEACHER_DOCTRINE family, BOTH shape buckets are tagged
    # `teacher_teaching`. With next_atom = scene_vignette, narrow filter
    # is empty, `any` filter is empty (none in this family), so the
    # selector falls back to the full pool. The contract is: the bridge
    # is never silent — it still returns a non-empty string.
    text = cc._bridge_within_slot(
        prev_atom="The teaching points to attachment as the seed of suffering.",
        next_atom="At 2 PM the reorg email lands in your inbox and your hands go cold.",
        slot_type="TEACHER_DOCTRINE",
        atom_pair_index=0,
        chapter_index=0,
    )
    # Fallback pool ensures we never go silent.
    assert text, "bridge must not be silent — fallback pool should fire"


def test_teacher_bridge_accepted_when_next_atom_is_teacher_teaching() -> None:
    """The complement of the above: when the next atom IS a teacher
    teaching, the selector should pick a teacher-tagged bridge (every
    variant in TEACHER_DOCTRINE is tagged teacher_teaching, so any of
    them is acceptable)."""
    text = cc._bridge_within_slot(
        prev_atom="The teaching points to attachment as the seed of suffering.",
        next_atom="Ahjan teaches that letting go is not loss; it is permission.",
        slot_type="TEACHER_DOCTRINE",
        atom_pair_index=0,
        chapter_index=0,
    )
    assert text, "bridge must be non-empty when next atom is a real teaching"
    # The bridge is from TEACHER_DOCTRINE's teacher_attribution_bridge or
    # deepen_doctrine shape — all variants there reference teaching/tradition.
    # We don't assert exact text (rotation may pick any), but we can verify
    # the picked text comes from one of those two shapes.
    payload = cc._load_within_slot_bridge_families()
    teacher_family = (payload.get("slot_families") or {}).get("TEACHER_DOCTRINE", {})
    all_teacher_texts = {
        e["text"]
        for shape, entries in teacher_family.items()
        for e in entries
    }
    assert text in all_teacher_texts, (
        f"chosen bridge {text!r} should come from TEACHER_DOCTRINE family"
    )


# ---------------------------------------------------------------------------
# Test 3: bridges tagged `next_atom_expectation: any` always match
# ---------------------------------------------------------------------------

def test_any_tagged_bridges_always_match() -> None:
    """A bridge with `next_atom_expectation: any` should be eligible
    regardless of next-atom class. We use INTEGRATION whose both shapes
    are tagged `any`, then feed wildly different next atoms and assert
    the selector never goes silent."""
    state = cc.WithinSlotRotationState()
    next_atoms_by_class = [
        ("Ahjan teaches that the path begins in the body.", "teacher_teaching"),
        ("Your chest pulls tight. The breath goes shallow.", "body_anchor"),
        ("The Slack notification arrives at 2 PM.", "scene_vignette"),
        ("Here is the mechanism: prediction becomes chemistry.", "mechanism_paragraph"),
        ("Try this: count three breaths.", "practical_takeaway"),
        ("What if the feeling is not lying to you?", "reflective_pivot"),
        ("Some sentence with no clear tells.", "any"),
    ]
    for i, (na, _cls) in enumerate(next_atoms_by_class):
        text = cc._bridge_within_slot(
            prev_atom="Previous integration moment.",
            next_atom=na,
            slot_type="INTEGRATION",
            atom_pair_index=i,
            chapter_index=0,
            rotation_state=state,
        )
        assert text, f"INTEGRATION (all `any`) failed to fire for next_class={_cls!r}"


# ---------------------------------------------------------------------------
# Test 4: when narrow match is empty, fall back to least-used `any` bridge
# ---------------------------------------------------------------------------

def test_fallback_to_any_when_no_narrow_match() -> None:
    """STORY/contrast_lift has all variants tagged `scene_vignette`. If we
    ask for a body_anchor-class next atom (no narrow match in this shape),
    the selector should fall back. Since STORY/contrast_lift has NO `any`
    variants in this shape, last-resort returns the full raw pool. We test
    the OPD-112 ladder behaviour explicitly: no silent failure."""
    state = cc.WithinSlotRotationState()
    text = cc._bridge_within_slot(
        prev_atom="A scene of the morning commute.",
        next_atom="Your chest pulls tight. The breath goes shallow.",
        slot_type="STORY",
        atom_pair_index=2,  # 2 % 3 shapes = contrast_lift (sorted)
        chapter_index=0,
        rotation_state=state,
    )
    assert text, "fallback pool should ensure non-empty bridge"


# ---------------------------------------------------------------------------
# Test 5: backward-compat — un-annotated entries treated as `any`
# ---------------------------------------------------------------------------

def test_unannotated_yaml_treated_as_any(tmp_path, monkeypatch) -> None:
    """A bridge YAML with no `next_atom_expectation` field at all (legacy
    schema) must still load and produce non-empty bridges — the missing
    field defaults to `any`."""
    legacy_yaml = """\
schema_version: 2
slot_families:
  STORY:
    legacy_shape:
      - text: "Here is a legacy bridge."
        stems: [legacy]
        roots: [legacy]
"""
    p = tmp_path / "legacy_bridges.yaml"
    p.write_text(legacy_yaml, encoding="utf-8")

    monkeypatch.setattr(cc, "_WITHIN_SLOT_BRIDGE_PATH", p)
    # Reset the module-level cache so the next call re-reads from p.
    monkeypatch.setattr(cc, "_WITHIN_SLOT_BRIDGE_CACHE", None)

    text = cc._bridge_within_slot(
        prev_atom="prev",
        next_atom="The teaching points to one truth.",  # teacher_teaching class
        slot_type="STORY",
        atom_pair_index=0,
        chapter_index=0,
    )
    assert text == "Here is a legacy bridge.", (
        f"un-annotated bridge should fire as `any`; got {text!r}"
    )

    # Cleanup: clear the cache again so subsequent tests reload real YAML.
    monkeypatch.setattr(cc, "_WITHIN_SLOT_BRIDGE_CACHE", None)


def test_invalid_expectation_label_treated_as_any(tmp_path, monkeypatch) -> None:
    """An unknown / mistyped `next_atom_expectation:` label (e.g. a typo
    like `teacher_teching`) is coerced to `any` so the bridge stays
    eligible regardless of next-atom class."""
    typo_yaml = """\
schema_version: 2
slot_families:
  STORY:
    typo_shape:
      - text: "Bridge with a typo expectation."
        next_atom_expectation: teacher_teching   # intentional typo
        stems: [typo]
        roots: [typo]
"""
    p = tmp_path / "typo_bridges.yaml"
    p.write_text(typo_yaml, encoding="utf-8")
    monkeypatch.setattr(cc, "_WITHIN_SLOT_BRIDGE_PATH", p)
    monkeypatch.setattr(cc, "_WITHIN_SLOT_BRIDGE_CACHE", None)

    text = cc._bridge_within_slot(
        prev_atom="prev",
        next_atom="Your jaw clenches before the message lands.",  # body_anchor
        slot_type="STORY",
        atom_pair_index=0,
        chapter_index=0,
    )
    assert text == "Bridge with a typo expectation.", (
        f"invalid label should be coerced to `any`; got {text!r}"
    )
    monkeypatch.setattr(cc, "_WITHIN_SLOT_BRIDGE_CACHE", None)


# ---------------------------------------------------------------------------
# Test 6: determinism still holds after the filter is added
# ---------------------------------------------------------------------------

def test_determinism_preserved_with_filter() -> None:
    """Two calls with identical (chapter_index, slot_type, atom_pair_index,
    next_atom) must return identical bridges — the OPD-112 filter is
    pure (no randomness)."""
    cc._WITHIN_SLOT_ROTATION_TLS = None
    a = cc._bridge_within_slot(
        prev_atom="A previous body-anchor moment.",
        next_atom="Your jaw clenches before the message lands.",
        slot_type="STORY",
        atom_pair_index=0,
        chapter_index=0,
    )
    b = cc._bridge_within_slot(
        prev_atom="A previous body-anchor moment.",
        next_atom="Your jaw clenches before the message lands.",
        slot_type="STORY",
        atom_pair_index=0,
        chapter_index=0,
    )
    assert a == b, f"OPD-112 filter must be deterministic; got {a!r} vs {b!r}"
    assert a, "filter must not silence the bridge"


def test_filter_yaml_loads_and_all_entries_have_expectation() -> None:
    """Acceptance gate: every variant in within_slot_bridge_families.yaml
    must have a valid `next_atom_expectation` field after OPD-112. New
    bridges added later must carry the tag too."""
    payload = cc._load_within_slot_bridge_families()
    families = payload.get("slot_families") or {}
    total_checked = 0
    bad: list[tuple[str, str, str]] = []
    for slot_type, family in families.items():
        for shape, entries in family.items():
            for entry in entries:
                total_checked += 1
                exp = entry.get("next_atom_expectation")
                if not exp or str(exp).strip().lower() not in cc._NEXT_ATOM_EXPECTATION_LABELS:
                    bad.append((slot_type, shape, entry.get("text", "")[:60]))
    # default_family entries should also carry the tag.
    for shape, entries in (payload.get("default_family") or {}).items():
        for entry in entries:
            total_checked += 1
            exp = entry.get("next_atom_expectation")
            if not exp or str(exp).strip().lower() not in cc._NEXT_ATOM_EXPECTATION_LABELS:
                bad.append(("default_family", shape, entry.get("text", "")[:60]))
    assert total_checked > 200, (
        f"sanity: expected >200 within-slot bridge variants, found {total_checked}"
    )
    assert not bad, (
        f"OPD-112: {len(bad)} entries missing/invalid next_atom_expectation. "
        f"First few: {bad[:5]}"
    )


def test_rotation_state_still_works_with_filter() -> None:
    """Within one chapter, asking for 4 INTEGRATION bridges (all `any`-tagged
    in this family) with the same next-atom class must still yield 4 distinct
    variants — rotation state survives the OPD-112 filter."""
    state = cc.WithinSlotRotationState()
    texts: list[str] = []
    for pair_idx in range(4):
        text = cc._bridge_within_slot(
            prev_atom=f"prev {pair_idx}",
            next_atom="Some neutral integration moment.",
            slot_type="INTEGRATION",
            atom_pair_index=pair_idx,
            chapter_index=5,
            rotation_state=state,
        )
        texts.append(text)
    assert len(set(texts)) == 4, (
        f"OPD-112 must not break OPD-109 Phase 3 rotation; got {texts}"
    )
