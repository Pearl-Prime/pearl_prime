"""Tests for register-output craft strengthen passes."""

from phoenix_v4.rendering.register_output_strengthen import (
    break_pedagogical_cadence_repetition,
    cap_prescribed_action_density,
    dedupe_register_f1_paragraphs,
    ensure_book_terminal_integrity,
    ensure_dwell_beats,
    ensure_unique_chapter_closings,
    repair_f13_dwell_contract,
    verify_f7_exercise_preservation,
    _DEPRESCRIBE_ALTERNATIVES,
)
from phoenix_v4.quality.register_gate import (
    _detect_f4_closing_line_repeats,
    _detect_f13_dwell_starvation,
    _detect_f6_cadence_repetition,
    _detect_f1_templated_paragraphs,
    _f13_is_insight,
    _is_prescribed_action,
    _split_chapters,
)


def test_ensure_book_terminal_integrity_truncates_mid_sentence():
    prose = "Chapter 1\n\nFirst paragraph ends well.\n\nThis breath practice starts"
    fixed = ensure_book_terminal_integrity(prose)
    assert fixed.endswith(".")
    assert "starts" not in fixed.split()[-3:]


def test_ensure_dwell_beats_is_noop():
    body = (
        "The mechanism is simple. Which means the body moves first. "
        "The cost is already on the table."
    )
    chapter = f"Chapter 2\n\n{body}"
    out = ensure_dwell_beats(chapter, seed="test")
    assert out == chapter


def test_break_pedagogical_cadence_clears_f6():
    # Four identical cadence windows (8,10,12,9 word sentences ×3) trip F6.
    sent_a = "one two three four five six seven eight."
    sent_b = "one two three four five six seven eight nine ten."
    sent_c = "one two three four five six seven eight nine ten eleven twelve."
    sent_d = "one two three four five six seven eight nine."
    block = " ".join([sent_a, sent_b, sent_c, sent_d])
    chapter = f"Chapter 1\n\n{block}\n\n{block}\n\n{block}"
    assert _detect_f6_cadence_repetition(_split_chapters(chapter))
    fixed = break_pedagogical_cadence_repetition(chapter, seed="test")
    assert not _detect_f6_cadence_repetition(_split_chapters(fixed))


def test_cap_prescribed_action_density():
    paras = []
    for i in range(5):
        paras.append(f"Notice your breath for five seconds. Step {i + 1}. Hold.")
    body = "\n\n".join(paras)
    chapter = f"Chapter 1\n\n{body}"
    out = cap_prescribed_action_density(chapter, max_per_chapter=2)
    ch_text = out.split("Chapter 1", 1)[1]
    count = sum(1 for p in ch_text.split("\n\n") if _is_prescribed_action(p))
    assert count <= 2


def test_deprescribe_alternatives_are_f7_safe():
    assert _DEPRESCRIBE_ALTERNATIVES
    for line in _DEPRESCRIBE_ALTERNATIVES:
        assert not _is_prescribed_action(line), line
        assert not _f13_is_insight(line), line


def test_repair_f13_dwell_contract_is_noop():
    body = (
        "The mechanism is simple. Which means the body moves first. "
        "The cost is already on the table."
    )
    chapter = f"Chapter 3\n\n{body}"
    out = repair_f13_dwell_contract(chapter, seed="test")
    assert out == chapter


def test_verify_f7_exercise_preservation_zero_contract():
    chapter = "Chapter 1\n\nNotice your breath for five seconds. Step one."
    gov = {
        "exercise_slots_dropped": [
            {"chapter": 1, "contract_max_exercises": 0},
        ]
    }
    violations = verify_f7_exercise_preservation(chapter, governance_report=gov)
    assert violations
    assert any("contract_max_exercises=0" in v for v in violations)


def test_verify_f7_exercise_preservation_stripped_exercise():
    chapter = "Chapter 2\n\nPlain narrative without prescribed steps."
    gov = {
        "exercise_slots_dropped": [
            {"chapter": 2, "contract_max_exercises": 1},
        ]
    }
    violations = verify_f7_exercise_preservation(chapter, governance_report=gov)
    assert any("below contract_max_exercises" in v for v in violations)


def test_dedupe_register_f1_paragraphs():
    para = (
        "One two three four five six. "
        "Seven eight nine ten eleven twelve. "
        "Thirteen fourteen fifteen sixteen."
    )
    ch1 = f"Chapter 1\n\n{para}\n\nTail sentence here."
    ch2 = f"Chapter 2\n\n{para}\n\nDifferent tail."
    book = f"{ch1}\n\n{ch2}"
    assert _detect_f1_templated_paragraphs(_split_chapters(book))
    out, notes = dedupe_register_f1_paragraphs(book)
    assert not _detect_f1_templated_paragraphs(_split_chapters(out))
    assert notes


def test_ensure_unique_chapter_closings():
    line = "Of course the alarm kept running — the system was doing its job."
    book = (
        f"Chapter 1\n\nBody one.\n\n{line}\n\n"
        f"Chapter 2\n\nBody two.\n\n{line}"
    )
    assert _detect_f4_closing_line_repeats(_split_chapters(book))
    out = ensure_unique_chapter_closings(book, seed="test")
    assert not _detect_f4_closing_line_repeats(_split_chapters(out))
