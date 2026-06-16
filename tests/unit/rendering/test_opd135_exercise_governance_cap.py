"""OPD-135: exercise governance cap must allow ≥2 EXERCISE slots per chapter
under deep_book_6h / chapter_architecture_version=2.

PR #1275 wired the 5-part exercise assembly (intro + description + guidance +
aha + integration) and depends on multiple EXERCISE slots per chapter to drive
Part 4 (aha) and Part 5 (integration) coverage. The legacy governance cap
clamped to `contract.max_exercises`, which is 0/1 for most chapters in the
deep_book purpose-contract arc — dropping the second EXERCISE slot before it
could render. These tests pin the surgical lift to `max(contract, 2)` for
deep_book_6h and arch v2 while preserving the recognition / resolution
chapters' zero-exercise intent.
"""

from __future__ import annotations

from unittest.mock import patch

from phoenix_v4.planning.chapter_planner import ChapterContract
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


def test_deep_book_6h_lifts_contract_max_one_to_two() -> None:
    """deep_book_6h chapter with contract.max_exercises=1 + 2 EXERCISE slots
    used to drop the second slot; OPD-135 keeps both."""
    book, contracts = _book("deep_book_6h", contracts_max=1, slot_count=2)
    gov = _run(book, contracts)
    assert not gov.get("exercise_slots_dropped"), (
        f"deep_book_6h must keep ≥2 EXERCISE slots when contract caps at 1; "
        f"dropped={gov.get('exercise_slots_dropped')}"
    )


def test_arch_v2_lifts_contract_max_one_to_two() -> None:
    """chapter_architecture_version=2 also lifts the floor to 2."""
    book, contracts = _book("standard_book", contracts_max=1, slot_count=2, arch_v=2)
    gov = _run(book, contracts)
    assert not gov.get("exercise_slots_dropped"), (
        f"arch v2 must keep ≥2 EXERCISE slots when contract caps at 1; "
        f"dropped={gov.get('exercise_slots_dropped')}"
    )


def test_deep_book_6h_preserves_zero_exercise_contract() -> None:
    """Recognition / resolution chapters have contract.max_exercises=0 — the
    OPD-135 floor MUST NOT lift them. The first 'exercise-free' intent stays."""
    book, contracts = _book("deep_book_6h", contracts_max=0, slot_count=2)
    gov = _run(book, contracts)
    assert len(gov.get("exercise_slots_dropped", [])) == 2, (
        f"deep_book_6h must still drop EXERCISE slots when contract is 0; "
        f"dropped={gov.get('exercise_slots_dropped')}"
    )


def test_legacy_runtime_unchanged_when_contract_max_one() -> None:
    """short_book / standard_book under arch v1 keep the legacy contract cap
    (no surprise lift for established runtimes)."""
    book, contracts = _book("standard_book", contracts_max=1, slot_count=2)
    gov = _run(book, contracts)
    assert len(gov.get("exercise_slots_dropped", [])) == 1, (
        f"legacy runtime must still cap at contract.max_exercises=1; "
        f"dropped={gov.get('exercise_slots_dropped')}"
    )


def test_deep_book_6h_format_cap_remains_upper_bound() -> None:
    """OPD-135 floor lifts the *floor* of the contract cap, but format_cap is
    the absolute upper bound. With contract=3 + format_cap=3 + 4 slots, the
    4th must still drop."""
    book, contracts = _book("deep_book_6h", contracts_max=3, slot_count=4)
    gov = _run(book, contracts, format_cap=3)
    assert len(gov.get("exercise_slots_dropped", [])) == 1, (
        f"format_cap=3 must still drop the 4th slot; "
        f"dropped={gov.get('exercise_slots_dropped')}"
    )


def test_deep_book_6h_contract_two_unchanged() -> None:
    """When contract.max_exercises is already 2, the floor is a no-op."""
    book, contracts = _book("deep_book_6h", contracts_max=2, slot_count=2)
    gov = _run(book, contracts)
    assert not gov.get("exercise_slots_dropped"), (
        f"contract=2 + 2 slots should keep both; "
        f"dropped={gov.get('exercise_slots_dropped')}"
    )
