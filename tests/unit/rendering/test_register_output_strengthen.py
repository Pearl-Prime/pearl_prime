"""Tests for register-output craft strengthen passes."""

from phoenix_v4.rendering.register_output_strengthen import (
    break_pedagogical_cadence_repetition,
    cap_prescribed_action_density,
    dedupe_register_f1_paragraphs,
    ensure_book_terminal_integrity,
    ensure_dwell_beats,
    ensure_unique_chapter_closings,
)
from phoenix_v4.quality.register_gate import (
    _detect_f4_closing_line_repeats,
    _detect_f13_dwell_starvation,
    _detect_f6_cadence_repetition,
    _detect_f1_templated_paragraphs,
    _is_prescribed_action,
    _split_chapters,
)


def test_ensure_book_terminal_integrity_truncates_mid_sentence():
    prose = "Chapter 1\n\nFirst paragraph ends well.\n\nThis breath practice starts"
    fixed = ensure_book_terminal_integrity(prose)
    assert fixed.endswith(".")
    assert "starts" not in fixed.split()[-3:]


def test_ensure_dwell_beats_breaks_insight_run():
    body = (
        "The mechanism is simple. Which means the body moves first. "
        "The cost is already on the table."
    )
    chapter = f"Chapter 2\n\n{body}"
    out = ensure_dwell_beats(chapter, seed="test")
    f13 = _detect_f13_dwell_starvation(_split_chapters(out))
    assert not f13


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
