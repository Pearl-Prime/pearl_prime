"""Tests for OPD-107: EXERCISE-slot persona-pool fallthrough.

Before OPD-107 (PR #612 contract): the EXERCISE branch in
`phoenix_v4/planning/enrichment_select.py` hard-coded
``teacher -> practice_library -> FAIL``. Persona atoms were never consulted, even
though many personas now ship a curated practice-shaped EXERCISE bank in
``atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt``.

OPD-107 adds an ``elif persona_atoms:`` branch between the teacher attempt and
the practice_library fallback. The new branch routes persona EXERCISE atoms
through the **same** ``_filter_practice_pool`` shape gate the teacher pool
uses -- so PR #612's guarantee (no essay-shaped atom can ever render as
EXERCISE) is preserved.

Reference: ``docs/diagnostics/OPD-107_PRACTICE_SHAPE_FILTER_2026-05-18.md``.
"""
from __future__ import annotations

from typing import Dict, List

import pytest

from phoenix_v4.planning import enrichment_select as es
from phoenix_v4.planning.beatmap_compile import (
    compile_beatmap,
    load_format_spec,
    load_topic_engines,
)
from phoenix_v4.planning.enrichment_select import (
    EnrichmentRequest,
    select_enrichment,
)
from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


# A few practice-shaped persona EXERCISE atoms. Each trips one of the
# _PRACTICE_STEP_MARKERS (place your feet / breathe in / count to).
_PRACTICE_PERSONA_EXERCISE_ATOMS: List[dict] = [
    {
        "atom_id": "persona_ex_practice_001",
        "content": (
            "Sit back from your screen. Place both feet flat on the floor. "
            "Feel your heels make contact. Breathe in for four counts. "
            "Hold for four counts. Breathe out for four counts."
        ),
        "metadata": {},
    },
    {
        "atom_id": "persona_ex_practice_002",
        "content": (
            "Place one hand on your belly. Place the other on your chest. "
            "Breathe in slowly. Count five breaths. Then remove your hands."
        ),
        "metadata": {},
    },
    {
        "atom_id": "persona_ex_practice_003",
        "content": (
            "Close your eyes. Notice the scalp. Breathe once. Move to the jaw. "
            "Let it go slack. Move to the shoulders. Drop your shoulders. "
            "Breathe out. Open your eyes."
        ),
        "metadata": {},
    },
    {
        "atom_id": "persona_ex_practice_004",
        "content": (
            "Breathe in for four counts. Breathe out for eight counts. "
            "Six complete cycles. Notice where in the body the exhale releases last."
        ),
        "metadata": {},
    },
]


# Essay-shaped persona EXERCISE atoms. No imperative step markers -- these
# should be REJECTED by _filter_practice_pool exactly as the teacher essays are.
_ESSAY_PERSONA_EXERCISE_ATOMS: List[dict] = [
    {
        "atom_id": "persona_ex_essay_001",
        "content": (
            "Bhakti Yoga is the way of mindful awareness. "
            "Through cultivation we recognize the ordinary boundaries of the self."
        ),
        "metadata": {},
    },
    {
        "atom_id": "persona_ex_essay_002",
        "content": (
            "Buddha's dialogue with Emperor Wu illustrates this point when he "
            "identified himself as not what one might assume."
        ),
        "metadata": {},
    },
    {
        "atom_id": "persona_ex_essay_003",
        "content": (
            "Transformative impact on self and society. Practicing karma yoga "
            "shifts one's perspective on duty and selflessness."
        ),
        "metadata": {},
    },
]


# Practice-shaped teacher EXERCISE atoms (e.g. ahjan v01 style).
_PRACTICE_TEACHER_EXERCISE_ATOMS: List[dict] = [
    {
        "atom_id": "teacher_ex_practice_001",
        "content": (
            "Place your hand on your chest. Breathe in for four counts. "
            "Notice the rise. Breathe out for four counts. Repeat five times."
        ),
        "metadata": {"slot_type": "exercise"},
    },
    {
        "atom_id": "teacher_ex_practice_002",
        "content": (
            "Sit comfortably. Close your eyes. Count to ten breaths. "
            "Notice your breath. Then open your eyes."
        ),
        "metadata": {"slot_type": "exercise"},
    },
    {
        "atom_id": "teacher_ex_practice_003",
        "content": (
            "Place both feet flat. Press your heels down. Breathe in. "
            "Step 1: inhale slowly. Step 2: exhale slowly."
        ),
        "metadata": {"slot_type": "exercise"},
    },
]


def _wrap_persona_bank_with_exercise_override(
    real_bank: Dict[str, List[dict]],
    exercise_atoms: List[dict],
) -> Dict[str, List[dict]]:
    """Take the real persona bank, replace the EXERCISE list. Keep all other
    slot types untouched (so the rest of select_enrichment can complete and so
    SPEC-739-THRESHOLD-01 still passes on those types).

    If the caller passes an empty list (the "no persona EXERCISE atoms" case)
    we remove the EXERCISE key entirely; otherwise SPEC-739-THRESHOLD-01 would
    fail the run with "EXERCISE has 0 variant(s), need >= 3". If the caller
    passes 1-2 atoms we pad with practice-shaped placeholders so the threshold
    is met, but the test still verifies which atom got selected by id.
    """
    out: Dict[str, List[dict]] = {k: list(v) for k, v in (real_bank or {}).items()}
    if len(exercise_atoms) == 0:
        out.pop("EXERCISE", None)
    else:
        out["EXERCISE"] = list(exercise_atoms)
        while len(out["EXERCISE"]) < 3:
            i = len(out["EXERCISE"])
            out["EXERCISE"].append(
                {
                    "atom_id": f"persona_ex_padding_{i:03d}",
                    "content": (
                        "Place both feet flat on the floor. Breathe in for four "
                        "counts. Breathe out for four counts. Repeat three times."
                    ),
                    "metadata": {"slot_type": "exercise"},
                }
            )
    return out


def _wrap_teacher_bank_with_exercise_override(
    real_bank: Dict[str, List[dict]],
    exercise_atoms: List[dict],
) -> Dict[str, List[dict]]:
    """Override only the EXERCISE list of the teacher bank, leaving all other
    slot types untouched (teacher pool isn't gated by SPEC-739)."""
    out: Dict[str, List[dict]] = {k: list(v) for k, v in (real_bank or {}).items()}
    out["EXERCISE"] = list(exercise_atoms)
    return out


def _build_request(seed: str = "opd107_test") -> EnrichmentRequest:
    topic = "anxiety"
    fmt = load_format_spec("standard_book")
    spine = load_spine(topic)
    shaped = apply_knobs(spine, load_knob_profile(topic), runtime_format="standard_book")
    bm = compile_beatmap(shaped, load_topic_engines(topic), fmt)
    return EnrichmentRequest(
        beatmap=bm,
        teacher_id="ahjan",
        persona_id="gen_z_professionals",
        topic_id=topic,
        seed=seed,
    )


def _exercise_slot_sources(book) -> List[str]:
    """Return the ``source`` field of every EXERCISE slot across the book."""
    out: List[str] = []
    for ch in book.chapters:
        for slot in ch.slots:
            if slot.slot_type == "EXERCISE":
                out.append(slot.source or "")
    return out


def _exercise_slot_contents(book) -> List[str]:
    out: List[str] = []
    for ch in book.chapters:
        for slot in ch.slots:
            if slot.slot_type == "EXERCISE":
                out.append(slot.content or "")
    return out


@pytest.fixture
def patch_atom_loaders(monkeypatch):
    """Factory: wrap _load_teacher_atoms + _load_persona_atoms on the module,
    overriding ONLY the EXERCISE slot of each. All other slot types keep their
    real production atoms so the rest of select_enrichment can complete.

    Also stubs _try_practice_library to return a sentinel so we can detect
    when the practice_library fallback fires (the LAST resort in the EXERCISE
    branch).

    Twelve_shape continuity is disabled so OPD-107 persona fallthrough is
    exercised (flagship gen_z×anxiety binds plan exercises when active).
    """
    monkeypatch.setattr(
        es,
        "_load_runtime_word_bounds",
        lambda _rf, _root: (0, 10_000_000),
    )

    monkeypatch.setattr(
        es,
        "is_twelve_shape_continuity_active",
        lambda *args, **kwargs: False,
    )

    real_load_teacher = es._load_teacher_atoms
    real_load_persona = es._load_persona_atoms

    def _patcher(
        teacher_exercise: List[dict],
        persona_exercise: List[dict],
        practice_library_text: str = "PRACTICE_LIBRARY_FALLBACK_SENTINEL",
    ):
        def fake_load_teacher(tid):
            real = real_load_teacher(tid) or {}
            return _wrap_teacher_bank_with_exercise_override(real, teacher_exercise)

        # engine= added by #1701 (engine-aware atom routing): mirror the real
        # _load_persona_atoms(persona_id, topic_id, locale=None, engine=None)
        # signature and forward engine through so the EXERCISE-override wrapper
        # sits on top of the same engine-aware base pool production loads.
        def fake_load_persona(pid, topic, locale=None, engine=None):
            real = real_load_persona(pid, topic, locale=locale, engine=engine) or {}
            return _wrap_persona_bank_with_exercise_override(real, persona_exercise)

        def fake_practice_library(chapter_index, topic_id, persona_id, seed, locale=None):  # noqa: ARG001
            return (practice_library_text, "practice_library")

        monkeypatch.setattr(es, "_load_teacher_atoms", fake_load_teacher)
        monkeypatch.setattr(es, "_load_persona_atoms", fake_load_persona)
        monkeypatch.setattr(es, "_try_practice_library", fake_practice_library)

    return _patcher


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_persona_atoms_selected_when_teacher_pool_returns_zero(patch_atom_loaders):
    """OPD-107 fix: with empty teacher EXERCISE pool but practice-shaped persona
    atoms available, the persona atom is selected (not library_34)."""
    patch_atom_loaders(
        teacher_exercise=[],
        persona_exercise=_PRACTICE_PERSONA_EXERCISE_ATOMS,
    )
    book = select_enrichment(_build_request())

    sources = _exercise_slot_sources(book)
    contents = _exercise_slot_contents(book)
    assert sources, "beatmap had no EXERCISE slots -- test setup is wrong"

    # Every EXERCISE slot should come from persona_atom, not practice_library.
    assert all(s == "persona_atom" for s in sources), (
        f"expected persona_atom source for every EXERCISE slot, got: {sources!r}"
    )
    assert not any("practice_library" in s for s in sources), (
        f"practice_library fallback fired when persona pool was healthy: {sources!r}"
    )
    # The content should be one of our practice-shaped atoms, not the sentinel
    # returned by _try_practice_library.
    assert not any("PRACTICE_LIBRARY_FALLBACK_SENTINEL" in c for c in contents), (
        "EXERCISE slot content contains practice_library sentinel"
    )
    practice_atom_bodies = {a["content"] for a in _PRACTICE_PERSONA_EXERCISE_ATOMS}
    matched = any(any(body in c for body in practice_atom_bodies) for c in contents)
    assert matched, (
        "no EXERCISE slot contains text from the practice-shaped persona pool"
    )

    audit = book.enrichment_audit
    assert audit["slots_from_practice_library"] == 0, audit
    assert audit["slots_from_persona"] >= len(sources), audit


def test_teacher_pool_still_wins_when_practice_shaped(patch_atom_loaders):
    """Regression: when teacher EXERCISE pool has practice-shaped atoms, the
    teacher precedence from PR #612 is preserved -- persona pool is not
    consulted even if non-empty."""
    patch_atom_loaders(
        teacher_exercise=_PRACTICE_TEACHER_EXERCISE_ATOMS,
        persona_exercise=_PRACTICE_PERSONA_EXERCISE_ATOMS,
    )
    book = select_enrichment(_build_request())

    sources = _exercise_slot_sources(book)
    contents = _exercise_slot_contents(book)
    assert sources

    # Every EXERCISE slot should come from teacher_atom (with optional
    # teacher_wrapper transformation).
    assert all(s == "teacher_atom" for s in sources), (
        f"expected teacher_atom source for every EXERCISE slot, got: {sources!r}"
    )
    # And no slot should be sourced from persona -- teacher precedence holds.
    assert not any(s == "persona_atom" for s in sources), sources
    # And content should not contain practice_library sentinel.
    assert not any("PRACTICE_LIBRARY_FALLBACK_SENTINEL" in c for c in contents), (
        "practice_library sentinel appeared when teacher had valid atoms"
    )

    audit = book.enrichment_audit
    assert audit["slots_from_practice_library"] == 0, audit
    assert audit["slots_from_teacher"] >= len(sources), audit


def test_practice_library_fallback_when_both_pools_empty(patch_atom_loaders):
    """Regression: when BOTH teacher and persona EXERCISE pools are empty,
    the practice_library fallback still fires -- pre-OPD-107 behavior
    preserved."""
    patch_atom_loaders(
        teacher_exercise=[],
        persona_exercise=[],
    )
    book = select_enrichment(_build_request())

    sources = _exercise_slot_sources(book)
    contents = _exercise_slot_contents(book)
    assert sources

    # Without any usable atoms the practice_library sentinel must surface.
    assert all(s == "practice_library" for s in sources), (
        f"expected practice_library source for every EXERCISE slot, got: {sources!r}"
    )
    assert all("PRACTICE_LIBRARY_FALLBACK_SENTINEL" in c for c in contents), (
        "expected practice_library sentinel content"
    )

    audit = book.enrichment_audit
    assert audit["slots_from_practice_library"] >= len(sources), audit


def test_persona_essay_atoms_still_rejected_by_shape_filter(patch_atom_loaders):
    """OPD-107 preserves PR #612's guarantee: blog-essay persona atoms must
    NOT enter an EXERCISE slot. With only essay-shaped persona atoms and an
    empty teacher pool, we must fall through to practice_library (not render
    the essays as exercises)."""
    patch_atom_loaders(
        teacher_exercise=[],
        persona_exercise=_ESSAY_PERSONA_EXERCISE_ATOMS,
    )
    book = select_enrichment(_build_request())

    sources = _exercise_slot_sources(book)
    contents = _exercise_slot_contents(book)
    assert sources

    # The essay-shaped persona atoms must have been rejected by
    # _filter_practice_pool; the practice_library fallback should win.
    assert all(s == "practice_library" for s in sources), (
        f"essay-shaped persona atoms leaked into EXERCISE slots: {sources!r}"
    )
    assert not any(s == "persona_atom" for s in sources), sources
    # And critically, none of the essay text should be visible in any
    # EXERCISE slot content.
    essay_bodies = {a["content"] for a in _ESSAY_PERSONA_EXERCISE_ATOMS}
    for c in contents:
        for body in essay_bodies:
            assert body not in c, (
                f"essay body leaked into EXERCISE slot content: {body[:60]!r}"
            )

    audit = book.enrichment_audit
    assert audit["slots_from_practice_library"] >= 1, audit
