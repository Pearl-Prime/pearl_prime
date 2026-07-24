"""Regression tests: locale-aware EXERCISE practice-shape classification.

Background (zh-TW first-book blocker, 2026-07-23 — see
``artifacts/qa/zhtw_first_book_20260723/TRACE_SUMMARY.md`` and
``artifacts/qa/zhtw_first_book_20260723/build_attempt5_postfix_confirm.log``):

``enrichment_select._is_practice_atom`` classifies whether an EXERCISE atom is
practice-shaped ("instruction with steps") vs. an essay that was mistakenly
filed under an ``EXERCISE/`` directory. Absent explicit metadata, the only
positive-evidence signal was a tuple of ~44 English substrings
(``_PRACTICE_STEP_MARKERS``) plus a numbered-step regex. A faithfully
translated (zh-TW, ja-JP, ...) EXERCISE atom can never contain an English
substring, so every translated EXERCISE atom was misclassified as "not
practice-shaped," production builds fell through to the shared English
``practice_library`` for every EXERCISE slot in every non-English locale, and
the ``EXERCISE-BANK-RESOLUTION-01`` production gate
(``scripts/run_pipeline.py::_check_exercise_strict_canonical_gate``) fired for
a reason unrelated to real per-cell coverage.

The fix lives in ``registry_resolver._stamp_locale_exercise_metadata``: a
translated EXERCISE atom is stamped ``metadata["slot_type"] = "exercise"``
**only** when the English atom sharing its exact ``atom_id`` in the base
``CANONICAL.txt`` (same directory, no ``locales/`` suffix) already
independently passes the same shape check used for English content. This is
a structural (atom_id + directory-convention), not language-based, signal,
and it deliberately does NOT trust the ``EXERCISE/`` directory blindly:
essay-shaped atoms placed there (the ``ahjan_EXERCISE_064_mined`` /
"keen-sinoussi" incident — see ``enrichment_select._is_practice_atom``
docstring) must keep failing in every locale, exactly as they do in English
today, or the gate's actual purpose (catching genuinely thin/wrong EXERCISE
coverage) would be silently defeated.

Two things are pinned down here:
  (a) a real, well-formed translated EXERCISE atom is now correctly
      classified as practice-shaped (unblocks the gate for the reason it was
      previously mis-firing);
  (b) a genuinely essay-shaped EXERCISE atom (and its translation) is STILL
      correctly rejected — the gate's real protection is not weakened.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import phoenix_v4.planning.registry_resolver as rr
from phoenix_v4.planning.enrichment_select import _filter_practice_pool, _is_practice_atom


# ---------------------------------------------------------------------------
# Fixtures: English base bank with one practice-shaped and one essay-shaped
# atom, mirroring the real gen_z_professionals/overthinking/EXERCISE shape
# (three "## EXERCISE vNN" blocks, only one of which is practice-shaped).
# ---------------------------------------------------------------------------

CANONICAL_EN_EXERCISE = """## EXERCISE v01
---

---
Stop. Your mind is spinning into the future.
Name three things you can see right now.
Feel the ground beneath your feet.
---
## EXERCISE v02
---

---
Overthinking is the mind's attempt to control an uncertain future through
endless simulation. This essay explores why the nervous system defaults to
rumination and what that reveals about the illusion of control.
---
"""

# Faithful, atom_id-matched zh-TW translation of the SAME two blocks. v01 is
# a real translation of the practice script; v02 is a real translation of the
# essay (structurally must stay rejected in every locale).
CANONICAL_ZH_TW_EXERCISE = """## EXERCISE v01
---

---
停下來。你的思緒正飛向未來。
說出三件你現在看得見的東西。
感受腳下的地面。
---
## EXERCISE v02
---

---
過度思考是心智試圖透過無止盡的模擬來掌控不確定未來的方式。這篇文章探討
神經系統為何預設進入反芻思考模式，以及這揭示了關於掌控幻覺的什麼道理。
---
"""

# A zh-TW variant with an orphan atom_id (no English counterpart at all) —
# must fail safe (stay unstamped, stay rejected).
CANONICAL_ZH_TW_ORPHAN = """## EXERCISE v99
---

---
這是一個沒有對應英文原子的翻譯內容，不應該被標記為練習內容。
---
"""


def _seed_exercise_bank(
    atoms_root: Path,
    persona: str,
    topic: str,
    en_body: str,
    locale_bodies: dict[str, str] | None = None,
) -> None:
    slot_dir = atoms_root / persona / topic / "EXERCISE"
    slot_dir.mkdir(parents=True, exist_ok=True)
    (slot_dir / "CANONICAL.txt").write_text(en_body, encoding="utf-8")
    for locale, body in (locale_bodies or {}).items():
        locale_dir = slot_dir / "locales" / locale
        locale_dir.mkdir(parents=True, exist_ok=True)
        (locale_dir / "CANONICAL.txt").write_text(body, encoding="utf-8")


@pytest.fixture
def isolated_atoms_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(rr, "ATOMS_ROOT", tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# (a) Real, well-formed translated EXERCISE atom is now correctly classified.
# ---------------------------------------------------------------------------

def test_zhtw_practice_shaped_exercise_atom_is_classified_as_practice(
    isolated_atoms_root: Path,
) -> None:
    _seed_exercise_bank(
        isolated_atoms_root,
        "gen_z_professionals",
        "overthinking",
        CANONICAL_EN_EXERCISE,
        locale_bodies={"zh-TW": CANONICAL_ZH_TW_EXERCISE},
    )

    atoms = rr._load_persona_atoms(
        "gen_z_professionals", "overthinking", locale="zh-TW"
    )
    exercise_pool = atoms.get("EXERCISE", [])
    by_id = {a["atom_id"]: a for a in exercise_pool}
    assert "EXERCISE v01" in by_id, "zh-TW EXERCISE pool must load both atoms"

    v01 = by_id["EXERCISE v01"]
    assert v01["metadata"].get("slot_type") == "exercise", (
        "practice-shaped v01 should inherit slot_type=exercise from its "
        "English counterpart's shape check"
    )
    assert _is_practice_atom(v01) is True, (
        "zh-TW EXERCISE v01 (translation of a practice-shaped English atom) "
        "must classify as practice-shaped"
    )

    filtered = _filter_practice_pool(exercise_pool)
    filtered_ids = {a["atom_id"] for a in filtered}
    assert "EXERCISE v01" in filtered_ids, (
        "_filter_practice_pool must keep the practice-shaped zh-TW atom — this "
        "is what unblocks EXERCISE-BANK-RESOLUTION-01 for real translated content"
    )


# ---------------------------------------------------------------------------
# (b) Genuinely essay-shaped content (English AND its translation) is STILL
# correctly rejected — the gate's real protection is not weakened.
# ---------------------------------------------------------------------------

def test_zhtw_essay_shaped_exercise_atom_stays_rejected(
    isolated_atoms_root: Path,
) -> None:
    _seed_exercise_bank(
        isolated_atoms_root,
        "gen_z_professionals",
        "overthinking",
        CANONICAL_EN_EXERCISE,
        locale_bodies={"zh-TW": CANONICAL_ZH_TW_EXERCISE},
    )

    atoms = rr._load_persona_atoms(
        "gen_z_professionals", "overthinking", locale="zh-TW"
    )
    exercise_pool = atoms.get("EXERCISE", [])
    by_id = {a["atom_id"]: a for a in exercise_pool}

    v02 = by_id["EXERCISE v02"]
    assert "slot_type" not in v02["metadata"], (
        "essay-shaped v02's English counterpart fails the shape check, so the "
        "zh-TW translation must NOT be stamped practice-shaped — directory "
        "location alone (EXERCISE/) must never be trusted blindly"
    )
    assert _is_practice_atom(v02) is False, (
        "zh-TW EXERCISE v02 (translation of an essay) must still be rejected — "
        "this is the exact regression the classifier exists to prevent "
        "(ahjan_EXERCISE_064_mined / keen-sinoussi incident)"
    )

    filtered = _filter_practice_pool(exercise_pool)
    filtered_ids = {a["atom_id"] for a in filtered}
    assert "EXERCISE v02" not in filtered_ids


def test_english_base_exercise_shape_check_is_unaffected(
    isolated_atoms_root: Path,
) -> None:
    """en-US / default locale never touches the stamping branch (canonical ==
    base_canonical), so English classification behaves exactly as before."""
    _seed_exercise_bank(
        isolated_atoms_root,
        "gen_z_professionals",
        "overthinking",
        CANONICAL_EN_EXERCISE,
        locale_bodies={"zh-TW": CANONICAL_ZH_TW_EXERCISE},
    )

    for loc in (None, "en-US"):
        atoms = rr._load_persona_atoms(
            "gen_z_professionals", "overthinking", locale=loc
        )
        exercise_pool = atoms.get("EXERCISE", [])
        by_id = {a["atom_id"]: a for a in exercise_pool}
        assert by_id["EXERCISE v01"]["metadata"] == {}
        assert by_id["EXERCISE v02"]["metadata"] == {}
        assert _is_practice_atom(by_id["EXERCISE v01"]) is True
        assert _is_practice_atom(by_id["EXERCISE v02"]) is False


def test_zhtw_orphan_atom_id_with_no_english_counterpart_fails_safe(
    isolated_atoms_root: Path,
) -> None:
    """A translated atom whose atom_id has no English counterpart at all
    (translator added/renamed an atom_id) must NOT be stamped — fail safe,
    not fail open."""
    _seed_exercise_bank(
        isolated_atoms_root,
        "gen_z_professionals",
        "overthinking",
        CANONICAL_EN_EXERCISE,
        locale_bodies={"zh-TW": CANONICAL_ZH_TW_ORPHAN},
    )

    atoms = rr._load_persona_atoms(
        "gen_z_professionals", "overthinking", locale="zh-TW"
    )
    exercise_pool = atoms.get("EXERCISE", [])
    assert len(exercise_pool) == 1
    orphan = exercise_pool[0]
    assert orphan["atom_id"] == "EXERCISE v99"
    assert "slot_type" not in orphan["metadata"]
    assert _is_practice_atom(orphan) is False


# ---------------------------------------------------------------------------
# (c) Gate-relevant: genuine English fallback (no zh-TW EXERCISE bank at all)
# must still resolve as real English content, not silently vanish or get a
# false practice-shape stamp it didn't earn.
# ---------------------------------------------------------------------------

def test_missing_zhtw_bank_falls_back_to_english_and_is_still_classified_correctly(
    isolated_atoms_root: Path,
) -> None:
    """No zh-TW EXERCISE bank exists on disk for this cell at all -> the loader
    falls back to the base English file (existing, unrelated behavior; this
    is the case phoenix_v4/rendering/locale_fallback_report.py is responsible
    for flagging as an honesty violation). Confirm the practice/essay
    classification of that (English) fallback content is exactly what English
    would produce — no locale-stamping logic misfires on it."""
    _seed_exercise_bank(
        isolated_atoms_root,
        "gen_z_professionals",
        "overthinking",
        CANONICAL_EN_EXERCISE,
        locale_bodies=None,  # no zh-TW variant on disk
    )

    atoms = rr._load_persona_atoms(
        "gen_z_professionals", "overthinking", locale="zh-TW"
    )
    exercise_pool = atoms.get("EXERCISE", [])
    by_id = {a["atom_id"]: a for a in exercise_pool}
    # Fell back to English content verbatim.
    assert "spinning into the future" in by_id["EXERCISE v01"]["content"]
    # Classification matches plain English behavior (untouched by the
    # locale-stamping branch, since canonical == base_canonical here).
    assert _is_practice_atom(by_id["EXERCISE v01"]) is True
    assert _is_practice_atom(by_id["EXERCISE v02"]) is False


def test_stamp_locale_exercise_metadata_respects_explicit_translator_metadata(
    isolated_atoms_root: Path,
) -> None:
    """If a translated atom already explicitly declares its own slot_type
    (authored front-matter), the inferred stamp must not override it."""
    en_body = CANONICAL_EN_EXERCISE  # v02 is essay-shaped in English
    zh_body = """## EXERCISE v02
---
slot_type: exercise
---
過度思考是心智試圖透過無止盡的模擬來掌控不確定未來的方式。
---
"""
    _seed_exercise_bank(
        isolated_atoms_root,
        "gen_z_professionals",
        "overthinking",
        en_body,
        locale_bodies={"zh-TW": zh_body},
    )
    atoms = rr._load_persona_atoms(
        "gen_z_professionals", "overthinking", locale="zh-TW"
    )
    exercise_pool = atoms.get("EXERCISE", [])
    by_id = {a["atom_id"]: a for a in exercise_pool}
    # Explicit operator/translator metadata is honored even though the
    # English v02 counterpart itself is essay-shaped.
    assert by_id["EXERCISE v02"]["metadata"].get("slot_type") == "exercise"
    assert _is_practice_atom(by_id["EXERCISE v02"]) is True
