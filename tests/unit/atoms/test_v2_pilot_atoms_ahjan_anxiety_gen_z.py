"""
Pearl_Editor v2 pilot atom tests — TEACHER_DOCTRINE_INTRO + PERMISSION_GRANT.

Verifies the Holistic Chapter Architecture v2 pilot atoms for
ahjan × gen_z_professionals × anxiety:

- TEACHER_DOCTRINE_INTRO atom (per spec §2.4):
  - File exists at expected path
  - Parses via the existing CANONICAL.txt parser
  - Body word count in [800, 1200]
  - Flesch-Kincaid grade ≤ 8.5
  - No F2 broken-slot fragments

- PERMISSION_GRANT atom (per spec §2.5):
  - File exists at expected path
  - Parses via the existing CANONICAL.txt parser
  - Body word count in [250, 400]
  - ≥ 5 "allowed to" sentences
  - Flesch-Kincaid grade ≤ 8.5
  - No F2 broken-slot fragments

Authority:
- docs/specs/PEARL_PRIME_HOLISTIC_CHAPTER_ARCHITECTURE_SPEC.md §2.4, §2.5
- artifacts/pipeline_examples/miki/book_miki_imposter_syndrome_15min.txt (reference model)
- SOURCE_OF_TRUTH/teacher_banks/ahjan/doctrine/doctrine.yaml (teacher identity)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from phoenix_v4.planning.registry_resolver import _parse_canonical_txt
from phoenix_v4.quality.register_gate import _detect_f2_broken_fragments

REPO_ROOT = Path(__file__).resolve().parents[3]
PERSONA = "gen_z_professionals"
TOPIC = "anxiety"
TEACHER_ID = "ahjan"

TEACHER_DOCTRINE_INTRO_PATH = (
    REPO_ROOT
    / "atoms"
    / PERSONA
    / TOPIC
    / "TEACHER_DOCTRINE_INTRO"
    / TEACHER_ID
    / "CANONICAL.txt"
)
PERMISSION_GRANT_PATH = (
    REPO_ROOT / "atoms" / PERSONA / TOPIC / "PERMISSION_GRANT" / "CANONICAL.txt"
)

# Per spec §2.4: 4–6 paragraphs, 800–1,200 words.
DOCTRINE_INTRO_MIN_WORDS = 800
DOCTRINE_INTRO_MAX_WORDS = 1200
DOCTRINE_INTRO_MIN_PARAGRAPHS = 4
DOCTRINE_INTRO_MAX_PARAGRAPHS = 6

# Per spec §2.5: 5–8 "allowed to" sentences. Caller spec extends the body
# to 250–400 words with framing + integration before/after the list.
PERMISSION_GRANT_MIN_WORDS = 250
PERMISSION_GRANT_MAX_WORDS = 400
PERMISSION_GRANT_MIN_ALLOWED_SENTENCES = 5
PERMISSION_GRANT_MAX_ALLOWED_SENTENCES = 8

# OPD-100 reading-level cap.
READING_LEVEL_MAX_FK = 8.5


# ─────────────────────────────────────────────────────────────────────────────
# Flesch–Kincaid grade — local implementation (no external dependency)
# ─────────────────────────────────────────────────────────────────────────────


def _count_syllables(word: str) -> int:
    """Approximate syllable count for an English word.

    Standard Flesch heuristic: count vowel groups, drop silent trailing 'e',
    add a syllable for -le after a consonant. Clamps to >= 1.
    """
    cleaned = re.sub(r"[^a-z]", "", word.lower())
    if not cleaned:
        return 0
    if len(cleaned) <= 3:
        return 1
    vowels = "aeiouy"
    count = 0
    prev_was_vowel = False
    for ch in cleaned:
        is_vowel = ch in vowels
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel
    if cleaned.endswith("e") and count > 1:
        count -= 1
    if (
        cleaned.endswith("le")
        and len(cleaned) > 2
        and cleaned[-3] not in vowels
    ):
        count += 1
    return max(1, count)


def _flesch_kincaid_grade(text: str) -> float:
    """Flesch–Kincaid Grade Level.

    Formula:  0.39 * (words / sentences)
            + 11.8 * (syllables / words)
            - 15.59
    """
    text_clean = re.sub(r"\.\.\.", " ", text)
    text_clean = re.sub(r"\s+", " ", text_clean)
    sentences = [s for s in re.split(r"[.!?]+", text_clean) if s.strip()]
    words = re.findall(r"\b[a-zA-Z]+\b", text_clean)
    if not sentences or not words:
        return 0.0
    syllables = sum(_count_syllables(w) for w in words)
    return (
        0.39 * (len(words) / len(sentences))
        + 11.8 * (syllables / len(words))
        - 15.59
    )


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _atom_body(path: Path) -> str:
    """Return the parsed body of the first block in a CANONICAL.txt atom file."""
    blocks = _parse_canonical_txt(path, slot_type=path.parent.name.upper())
    if not blocks:
        return ""
    return blocks[0]["content"]


def _paragraph_count(body: str) -> int:
    return len([p for p in body.split("\n\n") if p.strip()])


def _word_count(body: str) -> int:
    return len(body.split())


# ─────────────────────────────────────────────────────────────────────────────
# TEACHER_DOCTRINE_INTRO tests (spec §2.4)
# ─────────────────────────────────────────────────────────────────────────────


def test_teacher_doctrine_intro_file_exists() -> None:
    assert TEACHER_DOCTRINE_INTRO_PATH.exists(), (
        f"TEACHER_DOCTRINE_INTRO atom missing at {TEACHER_DOCTRINE_INTRO_PATH}"
    )


def test_teacher_doctrine_intro_parses_via_canonical_parser() -> None:
    blocks = _parse_canonical_txt(
        TEACHER_DOCTRINE_INTRO_PATH, slot_type="TEACHER_DOCTRINE_INTRO"
    )
    assert blocks, (
        "TEACHER_DOCTRINE_INTRO did not yield any blocks via canonical parser"
    )
    assert blocks[0]["atom_id"].startswith("TEACHER_DOCTRINE_INTRO"), (
        f"unexpected atom_id: {blocks[0]['atom_id']!r}"
    )


def test_teacher_doctrine_intro_word_count_in_range() -> None:
    body = _atom_body(TEACHER_DOCTRINE_INTRO_PATH)
    wc = _word_count(body)
    assert DOCTRINE_INTRO_MIN_WORDS <= wc <= DOCTRINE_INTRO_MAX_WORDS, (
        f"TEACHER_DOCTRINE_INTRO word count {wc} outside "
        f"[{DOCTRINE_INTRO_MIN_WORDS}, {DOCTRINE_INTRO_MAX_WORDS}]"
    )


def test_teacher_doctrine_intro_paragraph_count_in_range() -> None:
    body = _atom_body(TEACHER_DOCTRINE_INTRO_PATH)
    pc = _paragraph_count(body)
    assert (
        DOCTRINE_INTRO_MIN_PARAGRAPHS <= pc <= DOCTRINE_INTRO_MAX_PARAGRAPHS
    ), (
        f"TEACHER_DOCTRINE_INTRO paragraph count {pc} outside "
        f"[{DOCTRINE_INTRO_MIN_PARAGRAPHS}, {DOCTRINE_INTRO_MAX_PARAGRAPHS}]"
    )


def test_teacher_doctrine_intro_reading_level_under_cap() -> None:
    body = _atom_body(TEACHER_DOCTRINE_INTRO_PATH)
    fk = _flesch_kincaid_grade(body)
    assert fk <= READING_LEVEL_MAX_FK, (
        f"TEACHER_DOCTRINE_INTRO Flesch-Kincaid grade {fk:.2f} exceeds {READING_LEVEL_MAX_FK}"
    )


def test_teacher_doctrine_intro_no_f2_fragments() -> None:
    text = TEACHER_DOCTRINE_INTRO_PATH.read_text(encoding="utf-8")
    findings = _detect_f2_broken_fragments([(1, text)])
    assert not findings, (
        "TEACHER_DOCTRINE_INTRO has F2 broken-slot fragments: "
        + "; ".join(f"{f.failure_id}: {f.summary}" for f in findings)
    )


def test_teacher_doctrine_intro_names_ahjan_signature_concepts() -> None:
    """Both signature concepts must be present (Pearl_Editor scoping):
    bracing as suffering + noticing without correction.
    """
    body = _atom_body(TEACHER_DOCTRINE_INTRO_PATH).lower()
    assert "bracing as suffering" in body, (
        "TEACHER_DOCTRINE_INTRO missing 'bracing as suffering' concept"
    )
    assert "noticing without correction" in body, (
        "TEACHER_DOCTRINE_INTRO missing 'noticing without correction' concept"
    )


def test_teacher_doctrine_intro_references_thai_forest_lineage() -> None:
    """The intro must name the specific tradition (Thai Forest Theravada),
    not generic 'Buddhist' or 'contemplative'.
    """
    body = _atom_body(TEACHER_DOCTRINE_INTRO_PATH).lower()
    assert "thai forest" in body, (
        "TEACHER_DOCTRINE_INTRO must name 'Thai Forest' tradition explicitly"
    )
    assert "theravada" in body, (
        "TEACHER_DOCTRINE_INTRO must name 'Theravada' explicitly"
    )


# ─────────────────────────────────────────────────────────────────────────────
# PERMISSION_GRANT tests (spec §2.5)
# ─────────────────────────────────────────────────────────────────────────────


def test_permission_grant_file_exists() -> None:
    assert PERMISSION_GRANT_PATH.exists(), (
        f"PERMISSION_GRANT atom missing at {PERMISSION_GRANT_PATH}"
    )


def test_permission_grant_parses_via_canonical_parser() -> None:
    blocks = _parse_canonical_txt(
        PERMISSION_GRANT_PATH, slot_type="PERMISSION_GRANT"
    )
    assert blocks, "PERMISSION_GRANT did not yield any blocks via canonical parser"
    assert blocks[0]["atom_id"].startswith("PERMISSION_GRANT"), (
        f"unexpected atom_id: {blocks[0]['atom_id']!r}"
    )


def test_permission_grant_word_count_in_range() -> None:
    body = _atom_body(PERMISSION_GRANT_PATH)
    wc = _word_count(body)
    assert PERMISSION_GRANT_MIN_WORDS <= wc <= PERMISSION_GRANT_MAX_WORDS, (
        f"PERMISSION_GRANT word count {wc} outside "
        f"[{PERMISSION_GRANT_MIN_WORDS}, {PERMISSION_GRANT_MAX_WORDS}]"
    )


def test_permission_grant_has_allowed_to_sentences() -> None:
    body = _atom_body(PERMISSION_GRANT_PATH)
    matches = re.findall(
        r"(?:You|The reader) (?:are|is) allowed to[^.!?]*[.!?]",
        body,
    )
    n = len(matches)
    assert (
        PERMISSION_GRANT_MIN_ALLOWED_SENTENCES
        <= n
        <= PERMISSION_GRANT_MAX_ALLOWED_SENTENCES
    ), (
        f"PERMISSION_GRANT 'allowed to' sentence count {n} outside "
        f"[{PERMISSION_GRANT_MIN_ALLOWED_SENTENCES}, "
        f"{PERMISSION_GRANT_MAX_ALLOWED_SENTENCES}]"
    )


def test_permission_grant_reading_level_under_cap() -> None:
    body = _atom_body(PERMISSION_GRANT_PATH)
    fk = _flesch_kincaid_grade(body)
    assert fk <= READING_LEVEL_MAX_FK, (
        f"PERMISSION_GRANT Flesch-Kincaid grade {fk:.2f} exceeds {READING_LEVEL_MAX_FK}"
    )


def test_permission_grant_no_f2_fragments() -> None:
    text = PERMISSION_GRANT_PATH.read_text(encoding="utf-8")
    findings = _detect_f2_broken_fragments([(1, text)])
    assert not findings, (
        "PERMISSION_GRANT has F2 broken-slot fragments: "
        + "; ".join(f"{f.failure_id}: {f.summary}" for f in findings)
    )


def test_permission_grant_each_sentence_stands_alone() -> None:
    """Each 'allowed to' sentence should be a complete, mantra-quotable
    statement — not a fragment. Each must end with a terminal punctuation
    mark and contain at least 4 words after 'allowed to'.
    """
    body = _atom_body(PERMISSION_GRANT_PATH)
    matches = re.findall(
        r"(?:You|The reader) (?:are|is) allowed to[^.!?]*[.!?]",
        body,
    )
    for sent in matches:
        tail = sent.split("allowed to", 1)[1].rstrip(".!?").strip()
        words_after = tail.split()
        assert len(words_after) >= 2, (
            f"PERMISSION_GRANT line too thin to stand alone: {sent!r}"
        )


@pytest.mark.parametrize(
    "expected_substring",
    [
        # The user-specified anxiety-aligned permissions per Pearl_Editor brief.
        # Each must appear verbatim in the atom body.
        "not be fine",
        "feel the doubt",
        "need people",
        "succeed without feeling ready",
        "receive good things",
        "rest before you have earned it",
    ],
)
def test_permission_grant_covers_canary_permission(
    expected_substring: str,
) -> None:
    body = _atom_body(PERMISSION_GRANT_PATH).lower()
    assert expected_substring in body, (
        f"PERMISSION_GRANT missing canary permission substring: {expected_substring!r}"
    )
