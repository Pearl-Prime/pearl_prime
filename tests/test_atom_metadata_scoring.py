"""
Tests for ACT-007: atom metadata tagging and enrichment scoring.

Covers:
- metadata_field_bonus applied when atom metadata matches chapter targets
- no crash when metadata fields absent
- collision_family dedup penalty for adjacent chapters
- _bestseller_metadata_score backward-compatibility
"""
from __future__ import annotations

import pytest

from phoenix_v4.planning.enrichment_select import (
    _collision_family_penalty,
    _metadata_field_bonus,
)
from phoenix_v4.planning.slot_resolver import _bestseller_metadata_score


# ---------------------------------------------------------------------------
# _metadata_field_bonus
# ---------------------------------------------------------------------------


def test_metadata_bonus_applied_when_matching():
    """Atom with matching reader_objection gets higher score than untagged atom."""
    ch_tgt = {
        "reader_objection": "already_tried",
        "proof_mode": "neuroscience",
        "tension_type": "curiosity_gap",
        "propulsion_type": "promise",
    }
    tagged_atom = {
        "reader_objection": "already_tried",
        "proof_mode": "neuroscience",
        "tension_type": "curiosity_gap",
        "propulsion_type": "promise",
        "shareability": 5,
    }
    untagged_atom: dict = {}

    tagged_score = _metadata_field_bonus(tagged_atom, ch_tgt)
    untagged_score = _metadata_field_bonus(untagged_atom, ch_tgt)

    assert tagged_score > untagged_score
    # Full match: 0.15 + 0.10 + 0.10 + 0.08 + 0.05 = 0.48
    assert abs(tagged_score - 0.48) < 1e-6


def test_reader_objection_bonus_only():
    """Only reader_objection matches → +0.15."""
    ch_tgt = {"reader_objection": "already_tried"}
    atom = {"reader_objection": "already_tried"}
    assert abs(_metadata_field_bonus(atom, ch_tgt) - 0.15) < 1e-6


def test_proof_mode_bonus_only():
    """Only proof_mode matches → +0.10."""
    ch_tgt = {"proof_mode": "neuroscience"}
    atom = {"proof_mode": "neuroscience"}
    assert abs(_metadata_field_bonus(atom, ch_tgt) - 0.10) < 1e-6


def test_shareability_bonus_threshold():
    """shareability >= 4 earns +0.05 unconditionally; shareability 3 does not."""
    atom_high = {"shareability": 4}
    atom_low = {"shareability": 3}
    # shareability bonus is unconditional — no chapter targets needed
    assert abs(_metadata_field_bonus(atom_high, {}) - 0.05) < 1e-6
    assert abs(_metadata_field_bonus(atom_high, None) - 0.05) < 1e-6  # type: ignore[arg-type]
    assert _metadata_field_bonus(atom_low, {}) == 0.0


def test_no_crash_when_metadata_absent():
    """Atom without metadata fields scores normally (no KeyError)."""
    ch_tgt = {
        "reader_objection": "already_tried",
        "proof_mode": "neuroscience",
        "tension_type": "curiosity_gap",
        "propulsion_type": "promise",
    }
    # Should not raise
    score = _metadata_field_bonus({}, ch_tgt)
    assert score == 0.0


def test_no_crash_when_targets_empty():
    """Empty chapter targets → only unconditional shareability bonus, no crash."""
    atom_with_share = {
        "reader_objection": "already_tried",
        "proof_mode": "neuroscience",
        "shareability": 5,
    }
    atom_no_share = {
        "reader_objection": "already_tried",
        "proof_mode": "neuroscience",
    }
    # shareability >= 4 earns +0.05 even with empty targets
    assert abs(_metadata_field_bonus(atom_with_share, {}) - 0.05) < 1e-6
    # no shareability → 0.0 bonus when targets empty
    assert _metadata_field_bonus(atom_no_share, {}) == 0.0
    assert _metadata_field_bonus(atom_no_share, None) == 0.0  # type: ignore[arg-type]


def test_case_insensitive_match():
    """Field matching is case-insensitive."""
    ch_tgt = {"reader_objection": "Already_Tried"}
    atom = {"reader_objection": "already_tried"}
    assert abs(_metadata_field_bonus(atom, ch_tgt) - 0.15) < 1e-6


# ---------------------------------------------------------------------------
# _collision_family_penalty
# ---------------------------------------------------------------------------


def test_collision_family_penalty_adjacent_chapters():
    """Same collision_family in adjacent chapters gets penalized."""
    atom = {"collision_family": "breathing_exercise"}
    recent_families = ["breathing_exercise", "thought_labeling"]

    penalty = _collision_family_penalty(atom, recent_families)
    assert abs(penalty - (-0.20)) < 1e-6


def test_no_penalty_when_different_family():
    """Different collision_family → no penalty."""
    atom = {"collision_family": "nervous_system_reset"}
    recent_families = ["breathing_exercise", "body_scan"]

    penalty = _collision_family_penalty(atom, recent_families)
    assert penalty == 0.0


def test_no_penalty_when_family_absent():
    """Atom with no collision_family → no penalty (graceful fallback)."""
    atom: dict = {}
    recent_families = ["breathing_exercise"]

    penalty = _collision_family_penalty(atom, recent_families)
    assert penalty == 0.0


def test_no_penalty_when_recent_empty():
    """Empty recent_families window → no penalty."""
    atom = {"collision_family": "breathing_exercise"}
    assert _collision_family_penalty(atom, []) == 0.0


def test_collision_family_penalty_is_additive():
    """Bonus + penalty combine correctly for net score."""
    ch_tgt = {"reader_objection": "already_tried"}
    atom = {"reader_objection": "already_tried", "collision_family": "breathing_exercise"}
    recent_families = ["breathing_exercise"]

    field_bonus = _metadata_field_bonus(atom, ch_tgt)
    cf_penalty = _collision_family_penalty(atom, recent_families)
    net = field_bonus + cf_penalty

    assert abs(field_bonus - 0.15) < 1e-6
    assert abs(cf_penalty - (-0.20)) < 1e-6
    assert abs(net - (-0.05)) < 1e-6


# ---------------------------------------------------------------------------
# _bestseller_metadata_score backward compatibility
# ---------------------------------------------------------------------------


def test_bestseller_score_still_works_no_new_fields():
    """_bestseller_metadata_score scores normally without the 6 new fields."""
    metadata = {
        "reader_objection": "already_tried",
        "proof_mode": "neuroscience",
    }
    target = {
        "reader_objection": "already_tried",
        "proof_mode": "neuroscience",
    }
    score = _bestseller_metadata_score(metadata, target)
    assert score > 0.0


def test_bestseller_score_zero_on_no_match():
    """_bestseller_metadata_score returns 0 when nothing matches."""
    metadata = {"reader_objection": "already_tried"}
    target = {"reader_objection": "not_that_bad"}
    score = _bestseller_metadata_score(metadata, target)
    assert score == 0.0


def test_bestseller_score_no_crash_empty_inputs():
    """_bestseller_metadata_score handles empty dicts gracefully."""
    assert _bestseller_metadata_score({}, {}) == 0.0
    assert _bestseller_metadata_score({}, {"reader_objection": "already_tried"}) == 0.0
    assert _bestseller_metadata_score({"reader_objection": "x"}, {}) == 0.0
