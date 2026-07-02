"""Q-TEACHERMODE-BYLINE-01 — teacher-mode books byline a PEN-NAME, never a teacher.

Ratified default (OPD-20260701-001): every teacher-mode EPUB's primary creator
(dc:creator role=aut) is a brand pen-name; the teacher is credited SEPARATELY
("Teaching by <teacher>" + dc:contributor role=oth). A teacher display name from
config/teachers/teacher_registry.yaml must NEVER appear as an EPUB primary author
— same class as the Sai-Maa rule.

These tests are the research's proposed CI guard (BOOK_COVER_UNIFIED_RESEARCH
§identity-bug) expressed as a unit test. They assert, for every entry in
TEACHER_BOOKS:
  1. the resolved primary author is a real registry pen-name for that book's brand;
  2. NO teacher display-name is ever the resolved primary author;
  3. the teacher still appears as the separate teaching-by credit.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.release.build_epub import (  # noqa: E402
    TEACHER_BOOKS,
    TeacherBylineError,
    _brand_author_pool_ids,
    _brand_for_teacher,
    _brand_topic_affinities,
    _load_yaml,
    _pen_name_pool_for_brand,
    _teacher_topic_band,
    _teacher_display_name,
    _topic_fit_pool,
    resolve_teacher_byline,
)

_TEACHER_REGISTRY_PATH = REPO_ROOT / "config" / "teachers" / "teacher_registry.yaml"


def _all_teacher_display_names() -> set[str]:
    """Every display_name / formal_name in teacher_registry.yaml — the banned set."""
    reg = _load_yaml(_TEACHER_REGISTRY_PATH)
    names: set[str] = set()
    for meta in (reg.get("teachers") or {}).values():
        if not isinstance(meta, dict):
            continue
        for key in ("display_name", "formal_name"):
            val = (meta.get(key) or "").strip()
            if val:
                names.add(val)
    return names


BANNED_TEACHER_NAMES = _all_teacher_display_names()


def _resolvable_books() -> list[dict]:
    """TEACHER_BOOKS whose brand currently has a pen-name pool (skip un-provisioned)."""
    out = []
    for book in TEACHER_BOOKS:
        try:
            brand = _brand_for_teacher(book["teacher"])
            if _pen_name_pool_for_brand(brand):
                out.append(book)
        except TeacherBylineError:
            pass
    return out


def test_teacher_registry_names_present():
    """Sanity: the banned set is non-empty (guards a broken registry path)."""
    assert BANNED_TEACHER_NAMES, "teacher_registry.yaml yielded no teacher names"
    # Spot-check the canonical teacher-mode-only identities.
    assert "Ahjan" in BANNED_TEACHER_NAMES
    assert "Sai Maa" in BANNED_TEACHER_NAMES


@pytest.mark.parametrize("book", _resolvable_books(), ids=lambda b: b["id"])
def test_primary_author_is_pen_name_never_teacher(book):
    pen_author, teacher_display = resolve_teacher_byline(book)

    # (1) resolved author is a real pen-name from the brand's pool
    brand = _brand_for_teacher(book["teacher"])
    pool = _pen_name_pool_for_brand(brand)
    assert pen_author in pool, f"{book['id']}: author '{pen_author}' not in {brand} pool"

    # (2) NO teacher display-name is ever the primary author
    assert pen_author not in BANNED_TEACHER_NAMES, (
        f"{book['id']}: teacher name '{pen_author}' leaked into dc:creator"
    )

    # (3) the teacher is still credited separately
    assert teacher_display == _teacher_display_name(book["teacher"])
    assert teacher_display in BANNED_TEACHER_NAMES, (
        f"{book['id']}: teaching-by credit '{teacher_display}' is not a known teacher"
    )
    assert teacher_display != pen_author


def test_selection_is_deterministic():
    """Same book_id → same pen-name across calls (stable byline)."""
    for book in _resolvable_books():
        a1, _ = resolve_teacher_byline(book)
        a2, _ = resolve_teacher_byline(book)
        assert a1 == a2, f"{book['id']}: byline not deterministic ({a1} != {a2})"


def test_no_teacher_name_in_manifest_author_field():
    """The manifest must not carry an ``author`` key at all (only ``teacher``)."""
    for book in TEACHER_BOOKS:
        assert "author" not in book, (
            f"{book['id']}: manifest still has an 'author' key — should be 'teacher'"
        )
        assert book.get("teacher"), f"{book['id']}: missing 'teacher' key"


def test_missing_pool_raises_not_teacher_fallback():
    """A brand with no pen-name pool RAISES — never falls back to the teacher name."""
    fake = {"id": "nobody_x", "teacher": "__no_such_teacher__",
            "title": "x", "subtitle": "y", "topic": "anxiety", "lang": "en"}
    with pytest.raises(TeacherBylineError):
        resolve_teacher_byline(fake)


# ─── Q-BYLINE-POOL-SOURCE-01 — pool-source reconciliation + topic-fit ─────
#
# The 13 teacher-mode books split into two sets on origin/main:
#   * RESOLVABLE — the teacher's brand has an authored pen-name pool (SSOT =
#     config/brand_author_assignments.yaml, mapped to display names via the
#     roster). Only the fully-expanded teacher brands qualify today.
#   * ESCALATED — the brand is a roster SKELETON (no authored authors anywhere)
#     or the teacher has no brand mapping at all (adi_da, joshin). Provisioning
#     these means AUTHORING new pen-name identities, which is out of scope and
#     explicitly forbidden — so these RAISE TeacherBylineError by design. They
#     are tracked here as the known gap, NOT as a test failure.

# Teachers whose brand has NO authored pool on origin/main (documented gap).
# adi_da / joshin: no brand mapping at all. The rest: roster skeleton brands.
ESCALATED_TEACHERS = {
    "adi_da", "joshin",            # no brand mapping in the roster
    "miyuki", "maat", "master_feung", "master_sha", "master_wu",
    "miki", "omote", "ra", "sai_ma",  # roster skeleton brands (author_count, no authors)
}


def _partition_books() -> tuple[list[dict], list[dict]]:
    """Split TEACHER_BOOKS into (resolvable, escalated) by real pool presence."""
    resolvable, escalated = [], []
    for book in TEACHER_BOOKS:
        try:
            brand = _brand_for_teacher(book["teacher"])
            if _pen_name_pool_for_brand(brand):
                resolvable.append(book)
                continue
        except TeacherBylineError:
            pass
        escalated.append(book)
    return resolvable, escalated


RESOLVABLE_BOOKS, ESCALATED_BOOKS = _partition_books()


def test_every_teacher_book_resolves_or_is_escalated():
    """No teacher book is in an undefined state: each either resolves to a real
    pen-name byline or is on the explicit escalation (un-provisioned) list."""
    for book in TEACHER_BOOKS:
        if book["teacher"] in ESCALATED_TEACHERS:
            # Escalated: must RAISE (never silently ship a teacher name).
            with pytest.raises(TeacherBylineError):
                resolve_teacher_byline(book)
        else:
            pen, _teacher = resolve_teacher_byline(book)
            assert pen and pen not in BANNED_TEACHER_NAMES, (
                f"{book['id']}: expected a pen-name byline, got '{pen}'"
            )


def test_resolvable_set_is_nonempty():
    """The SSOT rewiring must actually resolve at least the provisioned brands —
    guards against a regression that empties every pool (e.g. wrong SSOT path)."""
    assert RESOLVABLE_BOOKS, (
        "no teacher book resolves — brand_author_assignments.yaml pools not read?"
    )


def test_ssot_pools_read_from_brand_author_assignments():
    """The provisioned teacher brands resolve to their assignments-SSOT pools
    (author_ids mapped to display names), not just the 1 brand author_registry
    carried. This is the core Q-BYLINE-POOL-SOURCE-01 fix."""
    for brand, expected_min in [
        ("stillness_press", 12),
        ("clear_seeing_books", 6),
        ("felt_sense_publishing", 8),
    ]:
        ids = _brand_author_pool_ids(brand)
        assert len(ids) >= expected_min, f"{brand}: {len(ids)} pool ids < {expected_min}"
        pool = _pen_name_pool_for_brand(brand)
        assert len(pool) >= expected_min, f"{brand}: {len(pool)} display names"
        # every resolved name is a real display name, none is a raw author_id
        assert all(" " in name for name in pool), (
            f"{brand}: pool has un-mapped author_ids: {pool}"
        )


@pytest.mark.parametrize("book", RESOLVABLE_BOOKS, ids=lambda b: b["id"])
def test_chosen_author_is_topic_eligible(book):
    """The resolved byline is drawn from the topic-eligible set for the book's
    topic (band-gated over the assignments' affinity rows), not an arbitrary
    pool member — i.e. topic-fit actually constrains the choice."""
    pen, _teacher = resolve_teacher_byline(book)
    brand = _brand_for_teacher(book["teacher"])
    eligible, _band = _topic_fit_pool(book, brand)
    assert pen in eligible, (
        f"{book['id']}: byline '{pen}' not in topic-eligible set {eligible}"
    )


def test_topic_band_gating_uses_score_bands():
    """The band gate matches PEN_NAME_AUTHOR_SYSTEM.md §6 thresholds via the
    teacher topic scores (strong ≥0.7). Spot-check a known strong pairing."""
    # ahjan scores anxiety at 0.9 → strong band.
    assert _teacher_topic_band("ahjan", "anxiety") == "strong"
    # joshin is unscored → None (must not crash the gate).
    assert _teacher_topic_band("joshin", "anxiety") is None


def test_anti_dup_brand_books_spread_across_pool():
    """A brand with >=2 books yields >=2 DISTINCT bylines (anti-dup), for both
    varied-topic and same-topic book sets. Never collapses to one author."""
    # Varied topics across one brand's pool.
    varied = [
        {"id": f"antidup_v_{i}", "teacher": "ahjan", "topic": t}
        for i, t in enumerate(
            ["anxiety", "burnout", "grief", "overthinking", "boundaries", "depression"]
        )
    ]
    got_varied = {resolve_teacher_byline(b)[0] for b in varied}
    assert len(got_varied) >= 2, f"varied-topic collapsed to {got_varied}"

    # Same topic, many books — the eligible-set spread must still distribute.
    same = [
        {"id": f"antidup_s_{i}", "teacher": "ahjan", "topic": "anxiety"}
        for i in range(8)
    ]
    got_same = {resolve_teacher_byline(b)[0] for b in same}
    assert len(got_same) >= 2, f"same-topic collapsed to a single byline: {got_same}"


def test_selection_deterministic_and_no_teacher_leak_resolvable():
    """Resolvable books: same book_id → same byline; byline is never a teacher."""
    for book in RESOLVABLE_BOOKS:
        a1, t1 = resolve_teacher_byline(book)
        a2, t2 = resolve_teacher_byline(book)
        assert a1 == a2, f"{book['id']}: non-deterministic ({a1} != {a2})"
        assert a1 not in BANNED_TEACHER_NAMES, f"{book['id']}: teacher '{a1}' as byline"
        assert t1 in BANNED_TEACHER_NAMES, f"{book['id']}: teaching-by '{t1}' unknown"


def test_escalated_books_raise_never_fallback_to_teacher():
    """Every escalated book RAISES rather than falling back to the teacher name.
    This is the anti-leak invariant for un-provisioned brands."""
    assert ESCALATED_BOOKS, "expected some un-provisioned teacher brands to escalate"
    for book in ESCALATED_BOOKS:
        with pytest.raises(TeacherBylineError):
            resolve_teacher_byline(book)
