"""Tests for the per-character panel seed (manga cross-panel consistency).

Covers the lane-C fix: render_v5_episode.py replaces blind per-panel index-jitter
seeding (which lets the SAME character drift panel-to-panel) with an opt-in
per-character seed derived from the on-frame character_id — mirroring the
reference-sheet formula so panels seed-lock to a character's reference sheet.

INTERIM consistency win; composes with (does not replace) the deferred PuLID
pathway. These are pure-function tests — no ComfyUI, no GPU, deterministic.
"""
from __future__ import annotations

import pytest

# render_v5_episode → render_v4_episode → validate_layer imports numpy at module
# load; skip the whole module when numpy is absent (e.g. the Core-tests env) so
# collection doesn't hard-error. The seed logic itself needs no numpy.
pytest.importorskip("numpy")  # skip entire module if numpy not in test env

from scripts.manga.render_v5_episode import (
    DEFAULT_SEED_BASE,
    _resolve_archetype_subject_state,
    compute_panel_seed,
)
from scripts.manga.character_individuation.reference_sheet_generator import (
    DEFAULT_SEED_BASE as REF_SHEET_SEED_BASE,
)


def _character_panel(character_id: str = "mira_aoki", on_frame: bool = True) -> dict:
    """A panel payload shaped like a real continuity_state YAML (ep001_017)."""
    return {
        "panel_id": "ep001_017",
        "archetype": "chest_breath_micro",
        "character_state": {
            character_id: {
                "pose_id": "chest_breath_micro",
                "emotional": "anxious",
            }
        },
        "relational_field": {
            "active_entities": [
                {"id": character_id, "on_frame": on_frame, "role": "subject"}
            ]
        },
    }


CHAR_ARCH_CTX = {"subject_type": "character_single"}
ENV_ARCH_CTX = {"subject_type": None}


# ── audit assertion: the panel payload carries a per-panel character_id ───────

def test_panel_payload_carries_character_id():
    """AUDIT: the on-frame character_id is resolvable from the panel payload.

    This is the precondition for per-character seeding — it confirms no upstream
    schema change (continuity_state_generator) is needed.
    """
    cid, cstate = _resolve_archetype_subject_state(
        _character_panel("mira_aoki"), CHAR_ARCH_CTX
    )
    assert cid == "mira_aoki"
    assert cstate is not None


# ── the seed formula matches the reference-sheet generator ───────────────────

def test_per_character_seed_matches_reference_sheet_formula():
    """Panel seed for a character == reference-sheet seed for that character.

    reference_sheet_generator.py:251 uses DEFAULT_SEED_BASE + sum(ord(c) ...).
    Panels must seed-lock to the same value so a character matches its sheet.
    """
    character_id = "mira_aoki"
    expected = REF_SHEET_SEED_BASE + sum(ord(c) for c in character_id)
    got = compute_panel_seed(
        REF_SHEET_SEED_BASE, panel_index=17, character_id=character_id,
        seed_by_character=True,
    )
    assert got == expected


# ── the core bug fix: same character → same seed across panels ───────────────

def test_same_character_same_seed_across_panels():
    """THE FIX: one character resolves to one seed regardless of panel index."""
    seed_p1 = compute_panel_seed(DEFAULT_SEED_BASE, 1, "mira_aoki", True)
    seed_p9 = compute_panel_seed(DEFAULT_SEED_BASE, 9, "mira_aoki", True)
    seed_p42 = compute_panel_seed(DEFAULT_SEED_BASE, 42, "mira_aoki", True)
    assert seed_p1 == seed_p9 == seed_p42


def test_different_characters_get_different_seeds():
    """Distinct characters must not collide onto the same seed."""
    a = compute_panel_seed(DEFAULT_SEED_BASE, 1, "mira_aoki", True)
    b = compute_panel_seed(DEFAULT_SEED_BASE, 1, "kenji_tanaka", True)
    assert a != b


# ── the legacy default is preserved (index jitter when flag is off) ──────────

def test_index_jitter_is_the_default():
    """With seed_by_character=False the legacy index-jitter formula is unchanged."""
    assert compute_panel_seed(42, 1, "mira_aoki", False) == 42 + 1 * 1009
    assert compute_panel_seed(42, 5, "mira_aoki", False) == 42 + 5 * 1009


def test_index_jitter_varies_per_panel():
    """Legacy mode: each panel gets a distinct seed."""
    seeds = {compute_panel_seed(42, i, "mira_aoki", False) for i in range(1, 6)}
    assert len(seeds) == 5


# ── fallback: panels with no on-frame character still get a deterministic seed ─

def test_environmental_panel_falls_back_to_index_jitter():
    """A scene-only (subject_type=None) panel has no character → index jitter."""
    cid, _ = _resolve_archetype_subject_state(_character_panel(), ENV_ARCH_CTX)
    assert cid is None
    seed = compute_panel_seed(DEFAULT_SEED_BASE, 3, cid, True)
    assert seed == DEFAULT_SEED_BASE + 3 * 1009


def test_off_frame_character_falls_back_to_index_jitter():
    """An off-frame character isn't rendered → no per-character seed → jitter."""
    cid, _ = _resolve_archetype_subject_state(
        _character_panel("mira_aoki", on_frame=False), CHAR_ARCH_CTX
    )
    assert cid is None
    seed = compute_panel_seed(DEFAULT_SEED_BASE, 7, cid, True)
    assert seed == DEFAULT_SEED_BASE + 7 * 1009


def test_none_character_with_flag_off_is_still_index_jitter():
    """Defensive: flag off + no character == plain jitter (no crash on None)."""
    assert compute_panel_seed(42, 2, None, False) == 42 + 2 * 1009
