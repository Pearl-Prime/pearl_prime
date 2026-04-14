"""Chapter purpose contracts YAML + assign_chapter_purpose_contracts."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from phoenix_v4.planning.chapter_planner import (
    CHAPTER_PURPOSE_CONTRACTS_PATH,
    ChapterContract,
    assign_chapter_purpose_contracts,
)
from phoenix_v4.planning.enrichment_select import EnrichedBook, EnrichedChapter, EnrichedSlot
from phoenix_v4.rendering.chapter_composer import compose_from_enriched_book


def test_yaml_loads_without_error() -> None:
    assert CHAPTER_PURPOSE_CONTRACTS_PATH.exists()
    data = yaml.safe_load(CHAPTER_PURPOSE_CONTRACTS_PATH.read_text(encoding="utf-8"))
    assert data.get("version") == 1
    assert "arcs" in data


@pytest.mark.parametrize("n", [3, 5, 7, 10, 12, 16, 22])
def test_contract_list_length_matches_chapter_count(n: int) -> None:
    contracts = assign_chapter_purpose_contracts(n, "standard_book")
    assert len(contracts) == n
    assert all(isinstance(c, ChapterContract) for c in contracts)
    assert contracts[0].chapter_index == 0
    assert contracts[-1].chapter_index == n - 1


def test_assign_returns_chapter_contract_dataclasses() -> None:
    cc = assign_chapter_purpose_contracts(12, "standard_book")
    assert cc[0].emotional_job == "recognition"
    assert cc[0].max_exercises == 0
    assert cc[11].emotional_job == "resolution"
    assert cc[11].max_exercises == 0


def test_missing_yaml_graceful(tmp_path: Path) -> None:
    missing = tmp_path / "no_contracts.yaml"
    out = assign_chapter_purpose_contracts(3, None, policy_path=missing)
    assert len(out) == 3
    assert out[0].max_exercises == 2


def test_max_exercises_enforced_in_compose_from_enriched_book() -> None:
    slots = [
        EnrichedSlot("EXERCISE", "one two three four five six seven eight", "t", "a", 8, 8, []),
        EnrichedSlot("EXERCISE", "one two three four five six seven eight", "t", "b", 8, 8, []),
        EnrichedSlot("EXERCISE", "one two three four five six seven eight", "t", "c", 8, 8, []),
        EnrichedSlot("EXERCISE", "one two three four five six seven eight", "t", "d", 8, 8, []),
    ]
    ch = EnrichedChapter(1, "r", "wt", "th", slots, 32, {})
    book = EnrichedBook(
        1,
        "enrichment_select",
        "anxiety",
        None,
        "gen_z_professionals",
        "standard_book",
        [ch],
        32,
        {},
    )
    fixed = [
        ChapterContract(0, "practice", "", [], "", ["EXERCISE", "REFLECTION"], 2),
    ]
    gov: dict = {}
    with patch("phoenix_v4.planning.chapter_planner.assign_chapter_purpose_contracts", return_value=fixed):
        compose_from_enriched_book(book, governance_report=gov)
    dropped = gov.get("exercise_slots_dropped", [])
    assert len(dropped) == 2
