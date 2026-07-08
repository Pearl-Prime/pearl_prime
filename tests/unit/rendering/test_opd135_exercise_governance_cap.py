"""OPD-135: exercise multiplicity is planner-owned; renderer must not silently drop.

PR #1275 five-part exercise assembly needs ≥2 EXERCISE slots on deep_book_6h /
arch-v2 practice chapters. The ceiling is resolved upstream in
``resolve_effective_max_exercises`` + ``cap_exercise_slots_in_row`` (beatmap).
The renderer records contract violations but never silently drops authored packets.
"""

from __future__ import annotations

from unittest.mock import patch

from phoenix_v4.planning.chapter_planner import (
    ChapterContract,
    cap_exercise_slots_in_row,
    resolve_effective_max_exercises,
)
from phoenix_v4.planning.enrichment_select import EnrichedBook, EnrichedChapter, EnrichedSlot
from phoenix_v4.rendering.chapter_composer import compose_from_enriched_book


def _exercise_slots(n: int) -> list[EnrichedSlot]:
    return [
        EnrichedSlot("EXERCISE", f"body line {i} " * 4, "t", f"id{i}", 20, 20, [])
        for i in range(n)
    ]


def _book(runtime_format: str, contracts_max: int, slot_count: int = 3, *, arch_v: int | None = None) -> tuple[EnrichedBook, list[ChapterContract]]:
    ch = EnrichedChapter(1, "r", "wt", "th", _exercise_slots(slot_count), 80, {})
    spine_ctx: dict = {}
    if arch_v is not None:
        spine_ctx["chapter_architecture_version"] = arch_v
    book = EnrichedBook(
        1,
        "enrichment_select",
        "anxiety",
        None,
        "gen_z_professionals",
        runtime_format,
        [ch],
        80,
        {},
        spine_context=spine_ctx,
    )
    contracts = [ChapterContract(0, "practice", "", [], "", ["EXERCISE"], contracts_max)]
    return book, contracts


def _run(book: EnrichedBook, contracts: list[ChapterContract], format_cap: int = 3) -> dict:
    gov: dict = {}
    with patch(
        "phoenix_v4.planning.chapter_planner.assign_chapter_purpose_contracts",
        return_value=contracts,
    ):
        with patch(
            "phoenix_v4.quality.ei_v2.config.load_ei_v2_config",
            return_value={
                "exercise_governance": {
                    "max_per_chapter_default": 2,
                    "override_per_format": {"deep_book_6h": format_cap},
                }
            },
        ):
            compose_from_enriched_book(book, governance_report=gov)
    return gov


def test_resolve_effective_max_lifts_deep_book_contract_one_to_two() -> None:
    assert resolve_effective_max_exercises(1, "deep_book_6h", format_cap=3) == 2


def test_resolve_effective_max_lifts_arch_v2_contract_one_to_two() -> None:
    assert resolve_effective_max_exercises(1, "standard_book", chapter_architecture_version=2) == 2


def test_resolve_effective_max_preserves_zero_exercise_contract() -> None:
    assert resolve_effective_max_exercises(0, "deep_book_6h") == 0


def test_resolve_effective_max_legacy_runtime_unchanged() -> None:
    assert resolve_effective_max_exercises(1, "standard_book") == 1


def test_cap_exercise_slots_in_row_keeps_first_n() -> None:
    row = ["HOOK", "EXERCISE", "STORY", "EXERCISE", "INTEGRATION"]
    assert cap_exercise_slots_in_row(row, 1) == ["HOOK", "EXERCISE", "STORY", "INTEGRATION"]


def test_renderer_does_not_drop_when_upstream_matches_contract() -> None:
    """When enrichment emits exactly contract-allowed EXERCISE slots, render keeps all."""
    book, contracts = _book("deep_book_6h", contracts_max=1, slot_count=2)
    gov = _run(book, contracts)
    assert not gov.get("exercise_slots_dropped")
    assert not gov.get("exercise_slot_contract_violations")


def test_renderer_records_violation_instead_of_dropping_excess() -> None:
    """Planner bug: too many EXERCISE slots must surface as violation, not silent drop."""
    book, contracts = _book("standard_book", contracts_max=1, slot_count=2)
    gov = _run(book, contracts)
    assert not gov.get("exercise_slots_dropped")
    assert len(gov.get("exercise_slot_contract_violations", [])) == 1


def test_deep_book_format_cap_remains_upper_bound() -> None:
    assert resolve_effective_max_exercises(3, "deep_book_6h", format_cap=3) == 3
