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
    _brand_for_teacher,
    _load_yaml,
    _pen_name_pool_for_brand,
    _teacher_display_name,
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
