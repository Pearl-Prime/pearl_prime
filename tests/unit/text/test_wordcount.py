"""CJK-honest word counting for production book gates."""
from __future__ import annotations

from phoenix_v4.quality.register_gate import evaluate_register
from phoenix_v4.text.wordcount import count_words, has_cjk_script


def test_english_whitespace_count_unchanged() -> None:
    assert count_words("one two three four") == 4
    assert count_words("  spaced   words  ") == 2
    assert count_words("") == 0


def test_han_paragraph_is_not_one_word() -> None:
    para = "野心仍在。只是它的代價比過去高昂。"
    assert len(para.split()) == 1  # whitespace-blind baseline
    assert count_words(para) >= 4
    assert has_cjk_script(para)


def test_long_han_paragraph_well_above_f2d_floor() -> None:
    para = (
        "倦怠並非來自於工時長短。而是來自於每一小時都處於警戒狀態，"
        "包括那些什麼事都沒發生的時刻。"
    )
    assert count_words(para) >= 20


def test_mixed_latin_and_han_counts_both() -> None:
    text = "burnout 無關乎工時長短。"
    # one latin token + Han chars
    assert count_words(text) > len(text.split())


def test_register_f2d_does_not_flag_full_han_paragraph() -> None:
    body = (
        "Chapter 1\n\n"
        "The Alarm That Won't Stop Ringing\n\n"
        "野心仍在。只是它的代價比過去高昂。\n\n"
        "This is a longer English paragraph that ends properly and keeps the "
        "chapter body above structural noise floors for the register gate.\n"
    )
    result = evaluate_register(body)
    f2d = [
        f
        for f in result.findings
        if f.failure_id == "F2" and (f.evidence or {}).get("rule") == "F2.D_sub_4_word_paragraph"
    ]
    assert not f2d, f"F2.D false-failed on Han prose: {[f.summary for f in f2d]}"


def test_register_f2d_still_flags_english_sub4_orphan() -> None:
    body = (
        "Chapter 1\n\n"
        "Working Title Here\n\n"
        "Ahjan's the practice\n\n"
        "A full sentence that ends properly so the chapter is not empty.\n"
    )
    result = evaluate_register(body)
    assert any(
        f.failure_id == "F2" and (f.evidence or {}).get("rule") == "F2.D_sub_4_word_paragraph"
        for f in result.findings
    )
