"""Per-chapter EXERCISE caps (config + ChapterContract)."""

from __future__ import annotations

from unittest.mock import patch

from phoenix_v4.planning.chapter_planner import ChapterContract
from phoenix_v4.planning.enrichment_select import EnrichedBook, EnrichedChapter, EnrichedSlot
from phoenix_v4.rendering.chapter_composer import compose_from_enriched_book


def _four_exercise_slots() -> list[EnrichedSlot]:
    return [
        EnrichedSlot("EXERCISE", f"body line {i} " * 4, "t", f"id{i}", 20, 20, [])
        for i in range(4)
    ]


def test_four_exercise_slots_two_kept_default() -> None:
    ch = EnrichedChapter(1, "r", "wt", "th", _four_exercise_slots(), 80, {})
    book = EnrichedBook(
        1,
        "enrichment_select",
        "anxiety",
        None,
        "gen_z_professionals",
        "standard_book",
        [ch],
        80,
        {},
    )
    fixed = [ChapterContract(0, "practice", "", [], "", ["EXERCISE"], 4)]
    gov: dict = {}
    with patch("phoenix_v4.planning.chapter_planner.assign_chapter_purpose_contracts", return_value=fixed):
        with patch(
            "phoenix_v4.quality.ei_v2.config.load_ei_v2_config",
            return_value={"exercise_governance": {"max_per_chapter_default": 2, "override_per_format": {}}},
        ):
            compose_from_enriched_book(book, governance_report=gov)
    assert len(gov.get("exercise_slots_dropped", [])) == 2


def test_one_exercise_unchanged() -> None:
    slots = _four_exercise_slots()[:1]
    ch = EnrichedChapter(1, "r", "wt", "th", slots, 20, {})
    book = EnrichedBook(
        1,
        "enrichment_select",
        "anxiety",
        None,
        "gen_z_professionals",
        "standard_book",
        [ch],
        20,
        {},
    )
    fixed = [ChapterContract(0, "practice", "", [], "", ["EXERCISE"], 4)]
    gov: dict = {}
    with patch("phoenix_v4.planning.chapter_planner.assign_chapter_purpose_contracts", return_value=fixed):
        compose_from_enriched_book(book, governance_report=gov)
    assert not gov.get("exercise_slots_dropped")


def test_micro_book_15_max_one() -> None:
    ch = EnrichedChapter(1, "r", "wt", "th", _four_exercise_slots(), 80, {})
    book = EnrichedBook(
        1,
        "enrichment_select",
        "anxiety",
        None,
        "gen_z_professionals",
        "micro_book_15",
        [ch],
        80,
        {},
    )
    fixed = [ChapterContract(0, "practice", "", [], "", ["EXERCISE"], 4)]
    gov: dict = {}
    with patch("phoenix_v4.planning.chapter_planner.assign_chapter_purpose_contracts", return_value=fixed):
        compose_from_enriched_book(book, governance_report=gov)
    assert len(gov.get("exercise_slots_dropped", [])) == 3


def test_contract_max_one_overrides_default() -> None:
    ch = EnrichedChapter(1, "r", "wt", "th", _four_exercise_slots(), 80, {})
    book = EnrichedBook(
        1,
        "enrichment_select",
        "anxiety",
        None,
        "gen_z_professionals",
        "standard_book",
        [ch],
        80,
        {},
    )
    fixed = [ChapterContract(0, "practice", "", [], "", ["EXERCISE"], 1)]
    gov: dict = {}
    with patch("phoenix_v4.planning.chapter_planner.assign_chapter_purpose_contracts", return_value=fixed):
        with patch(
            "phoenix_v4.quality.ei_v2.config.load_ei_v2_config",
            return_value={"exercise_governance": {"max_per_chapter_default": 2, "override_per_format": {}}},
        ):
            compose_from_enriched_book(book, governance_report=gov)
    assert len(gov.get("exercise_slots_dropped", [])) == 3
