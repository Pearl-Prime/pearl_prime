"""Within-book chapter uniqueness — prose-first semantic dedup (shipped spine)."""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.quality.content_uniqueness_truth import split_shipped_book_chapters
from phoenix_v4.quality.ei_v2.semantic_dedup import (
    analyze_chapter_content_uniqueness,
    detect_semantic_duplicates,
)
from scripts.ci.run_ei_v2_rigorous_eval import evaluate_chapter

BURNOUT_BOOK = (
    Path(__file__).resolve().parents[1]
    / "artifacts/wave_proof/draft/burnout_overwhelm__corporate_managers/book.txt"
)

NEAR_DUPE = (
    "That morning the elevator doors closed and your badge cut into your palm. "
    "You kept performing while the room went quiet around you. "
) * 40

DIFFERENT = (
    "A recipe for chocolate cake involves cocoa, butter, eggs, and patience. "
    "The oven preheats while you sift flour under kitchen light. "
) * 40


@pytest.fixture
def burnout_chapters() -> list[str]:
    if not BURNOUT_BOOK.exists():
        pytest.skip(f"missing {BURNOUT_BOOK}")
    return split_shipped_book_chapters(BURNOUT_BOOK.read_text(encoding="utf-8"))


def test_shipped_burnout_chapters_score_above_legacy_floor(burnout_chapters: list[str]) -> None:
    scores = []
    for i, ch in enumerate(burnout_chapters):
        ev = evaluate_chapter(ch, i, {}, "corporate_managers", "burnout", burnout_chapters)
        scores.append(ev.content_uniqueness)
    avg = sum(scores) / len(scores)
    assert avg >= 0.55
    assert min(scores) >= 0.40
    assert len(set(round(s, 2) for s in scores)) > 1


def test_worst_pair_evidence_is_prose_not_beat_only(burnout_chapters: list[str]) -> None:
    result = analyze_chapter_content_uniqueness(
        burnout_chapters[0], 0, burnout_chapters, cfg={}
    )
    worst = result["worst_pair"]
    assert worst is not None
    assert result["max_ngram_overlap"] < 0.15
    assert worst["evidence"]["beat_similarity"] >= 0.6
    assert result["content_uniqueness"] > 0.5


def test_identical_chapters_still_fail_uniqueness() -> None:
    chapters = [NEAR_DUPE, NEAR_DUPE] + [DIFFERENT] * 4
    ev0 = evaluate_chapter(chapters[0], 0, {}, "p", "burnout", chapters)
    ev1 = evaluate_chapter(chapters[1], 1, {}, "p", "burnout", chapters)
    assert ev0.content_uniqueness < 0.2
    assert ev1.content_uniqueness < 0.2


def test_atom_pool_dedup_unchanged_for_near_duplicates() -> None:
    dupes = detect_semantic_duplicates([NEAR_DUPE, NEAR_DUPE[: len(NEAR_DUPE) // 2] + NEAR_DUPE], ["a", "b"])
    assert dupes
    assert dupes[0]["similarity"] >= 0.3
