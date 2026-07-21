"""Tests for G-F1H — templated paragraph cluster HARD_FAIL escalation (>=6 chapters)."""
from __future__ import annotations

from scripts.ci.check_f1h_templated_cluster_hard import (
    G_F1H_CHAPTER_LIMIT,
    find_hard_fail_clusters,
)

TEMPLATE_PARA = (
    "You notice the tightness rise in your chest again today. It happens the "
    "same way every single time it arrives without warning at all."
)


def _book_with_template_in_chapters(n: int, *, unique_suffix_from: int = 0) -> str:
    parts = []
    for i in range(1, n + 1):
        filler = f" Chapter filler line unique to chapter {i} about the desk lamp."
        parts.append(f"Chapter {i}\n\n{TEMPLATE_PARA}{filler}\n")
    return "\n".join(parts)


def test_cluster_below_limit_is_not_hard_fail():
    assert G_F1H_CHAPTER_LIMIT == 6
    book = _book_with_template_in_chapters(5)
    hard = find_hard_fail_clusters(book)
    assert hard == [], f"expected no G-F1H hard-fail below {G_F1H_CHAPTER_LIMIT} chapters, got {hard}"


def test_cluster_at_limit_is_hard_fail():
    book = _book_with_template_in_chapters(6)
    hard = find_hard_fail_clusters(book)
    assert hard, "expected a G-F1H hard-fail cluster at exactly 6 chapters"
    assert hard[0]["chapter_count"] >= G_F1H_CHAPTER_LIMIT


def test_cluster_above_limit_is_hard_fail():
    book = _book_with_template_in_chapters(8)
    hard = find_hard_fail_clusters(book)
    assert hard, "expected a G-F1H hard-fail cluster above 6 chapters"
    assert hard[0]["chapter_count"] == 8


def test_no_repetition_no_hard_fail():
    parts = []
    for i in range(1, 9):
        parts.append(
            f"Chapter {i}\n\n"
            f"This chapter opens with a completely distinct scene about person {i} "
            f"doing something different in a different room entirely on day {i}.\n"
        )
    book = "\n".join(parts)
    hard = find_hard_fail_clusters(book)
    assert hard == []
