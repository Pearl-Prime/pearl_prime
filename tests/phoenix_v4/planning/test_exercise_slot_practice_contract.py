"""EXERCISE-slot contract — practice-with-steps only, no teaching essays.

Pins the post-PR-#612 follow-up: the EXERCISE branch of enrichment_select must
filter teacher_atoms[EXERCISE] to instruction-with-steps content. kb_mine_v1
essay synthesis (e.g. "Bhakti Yoga is the practice of mindful awareness...",
"selfless giving teaches us to transcend the boundaries of the self...") lives
in approved_atoms/EXERCISE/ by directory name, but its CONTENT is a teaching
essay, not a practice with steps. The selection-site filter rejects essay-shaped
atoms; the pipeline falls through to practice_library.

Bug evidence: keen-sinoussi book.txt — chapter X EXERCISE slot rendered an essay
about Bhakti Yoga and selfless giving (grep "selfless giving|Bhakti|transcend"
matched 4 times in the rendered book).
"""
from __future__ import annotations

import pytest

from phoenix_v4.planning.enrichment_select import (
    _filter_practice_pool,
    _is_practice_atom,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

ESSAY_ATOM_BHAKTI = {
    "atom_id": "ahjan_EXERCISE_028_mined",
    "content": (
        "It is also akin to the reverence a spiritual seeker holds for an "
        "enlightened teacher, recognizing them as an embodiment of divine love "
        "and enlightenment. In Bhakti Yoga's teachings, genuine love is "
        "stripped of personal desires and attachments. Its potency resides in "
        "its capacity to elevate us beyond the confines of mundane existence."
    ),
    "metadata": {"synthesis_method": "kb_mine_v1"},
}

ESSAY_ATOM_SELFLESS = {
    "atom_id": "ahjan_EXERCISE_036_mined",
    "content": (
        "We come to understand that we are all interconnected. The practice of "
        "selfless giving encourages us to move beyond dualistic thinking and "
        "the limitations of opposites. It urges us to continue giving, even in "
        "the face of challenging circumstances, as a means to transcend the "
        "boundaries of the self."
    ),
    "metadata": {"synthesis_method": "kb_mine_v1"},
}

ESSAY_ATOM_TRANSCEND = {
    "atom_id": "ahjan_EXERCISE_999_essay",
    "content": (
        "Buddhism teaches the transient and dream-like nature of life. "
        "Spiritual literature, compassionate practices, and meditation help "
        "individuals raise their consciousness and gain a deeper understanding "
        "of universal truths."
    ),
    "metadata": {},
}

PRACTICE_ATOM_BREATH = {
    "atom_id": "ahjan_EXERCISE_practice_breath",
    "content": (
        "Sit comfortably and close your eyes. Place one hand on your chest "
        "and the other on your belly. Inhale slowly through your nose for a "
        "count of four. Hold for one. Exhale through your mouth for a count "
        "of six. Notice the rise and fall of your hand on the belly. Repeat "
        "five times."
    ),
    "metadata": {},
}

PRACTICE_ATOM_NUMBERED = {
    "atom_id": "ahjan_EXERCISE_practice_numbered",
    "content": (
        "Anchor yourself in this moment with the 5-4-3-2-1 sensory scan.\n"
        "1. Name five things you can see.\n"
        "2. Name four things you can feel against your skin.\n"
        "3. Name three sounds you can hear.\n"
        "4. Name two scents you notice.\n"
        "5. Name one taste in your mouth."
    ),
    "metadata": {},
}

PRACTICE_ATOM_META_TAGGED = {
    "atom_id": "ahjan_EXERCISE_practice_meta",
    "content": "Stand tall. Roll your shoulders back. Take three deep breaths.",
    "metadata": {"slot_type": "exercise"},
}


# ── _is_practice_atom unit tests ───────────────────────────────────────────

def test_essay_atom_bhakti_is_rejected():
    """The exact atom from the keen-sinoussi bug must be rejected."""
    assert _is_practice_atom(ESSAY_ATOM_BHAKTI) is False


def test_essay_atom_selfless_giving_is_rejected():
    """The 'selfless giving' essay atom must be rejected."""
    assert _is_practice_atom(ESSAY_ATOM_SELFLESS) is False


def test_essay_atom_transcendent_is_rejected():
    """Pure teaching prose about transcendence must be rejected."""
    assert _is_practice_atom(ESSAY_ATOM_TRANSCEND) is False


def test_practice_atom_breath_steps_is_accepted():
    """Imperative breath instruction must be accepted."""
    assert _is_practice_atom(PRACTICE_ATOM_BREATH) is True


def test_practice_atom_numbered_steps_is_accepted():
    """Numbered step list (1. 2. 3.) must be accepted."""
    assert _is_practice_atom(PRACTICE_ATOM_NUMBERED) is True


def test_practice_atom_meta_tagged_is_accepted():
    """Atom with metadata.slot_type=='exercise' must be accepted."""
    assert _is_practice_atom(PRACTICE_ATOM_META_TAGGED) is True


def test_empty_atom_is_rejected():
    assert _is_practice_atom({}) is False
    assert _is_practice_atom({"content": ""}) is False
    assert _is_practice_atom({"content": "   "}) is False


def test_non_dict_atom_is_rejected():
    assert _is_practice_atom(None) is False  # type: ignore[arg-type]
    assert _is_practice_atom("not a dict") is False  # type: ignore[arg-type]


# ── _filter_practice_pool integration tests ────────────────────────────────

def test_filter_strips_essay_atoms_keeps_practices():
    """The keen-sinoussi mixed pool must filter down to only practice atoms."""
    mixed_pool = [
        ESSAY_ATOM_BHAKTI,
        PRACTICE_ATOM_BREATH,
        ESSAY_ATOM_SELFLESS,
        PRACTICE_ATOM_NUMBERED,
        ESSAY_ATOM_TRANSCEND,
        PRACTICE_ATOM_META_TAGGED,
    ]
    filtered = _filter_practice_pool(mixed_pool)
    assert len(filtered) == 3
    atom_ids = {a["atom_id"] for a in filtered}
    assert atom_ids == {
        "ahjan_EXERCISE_practice_breath",
        "ahjan_EXERCISE_practice_numbered",
        "ahjan_EXERCISE_practice_meta",
    }


def test_filter_empty_pool_returns_empty():
    assert _filter_practice_pool([]) == []
    assert _filter_practice_pool(None) == []  # type: ignore[arg-type]


def test_filter_all_essay_pool_returns_empty():
    """If every atom is essay-shaped, pool becomes empty → triggers practice_library fallback."""
    essay_only_pool = [ESSAY_ATOM_BHAKTI, ESSAY_ATOM_SELFLESS, ESSAY_ATOM_TRANSCEND]
    assert _filter_practice_pool(essay_only_pool) == []


# ── Negative-content contract assertion ────────────────────────────────────

@pytest.mark.parametrize(
    "essay_atom",
    [ESSAY_ATOM_BHAKTI, ESSAY_ATOM_SELFLESS, ESSAY_ATOM_TRANSCEND],
)
def test_rendered_essay_atom_never_passes_filter(essay_atom):
    """The exact essay-leak strings from the audit must never pass.

    If filter accepts any of these, the EXERCISE slot would render teaching
    prose like 'Bhakti Yoga is the practice of mindful awareness...' or
    'selfless giving teaches us to transcend the boundaries of the self...'
    """
    body = essay_atom["content"].lower()
    leak_present = any(s in body for s in ("bhakti", "selfless giving", "transcend"))
    if leak_present:
        # Essay leak strings present, AND no practice-step marker → must reject.
        practice_markers_present = any(
            m in body
            for m in ("inhale", "exhale", "count to ", "place your hand", "notice your")
        )
        if not practice_markers_present:
            assert _is_practice_atom(essay_atom) is False, (
                f"Essay-leak atom {essay_atom['atom_id']} must not pass the "
                f"EXERCISE-slot practice filter (would render '{body[:60]}...' "
                f"into book.txt as if it were a practice)."
            )
