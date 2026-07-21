from __future__ import annotations

from phoenix_v4.planning.book_structure_plan import generate_book_plan
from phoenix_v4.planning.chapter_contract import (
    build_chapter_contracts,
    validate_chapter_contract_packet,
)


def test_chapter_contracts_derive_from_current_generated_plan_without_release_auth():
    plan = generate_book_plan(
        topic_id="burnout",
        persona_id="corporate_managers",
        runtime_format="standard_book",
        engine_type="overwhelm",
        chapter_count=6,
    )

    packet = build_chapter_contracts(plan)
    errors = validate_chapter_contract_packet(packet)

    assert not errors
    assert packet["chapter_count"] == 6
    first = packet["contracts"][0]
    assert first["chapter_identity"]["topic_id"] == "burnout"
    assert first["reader_state_entry"]
    assert first["same_person_story_requirement"]["required"] is True
    assert first["acceptance_profile"]["production_public_release_authorized"] is False


def test_chapter_contract_preserves_chapter_one_thesis_from_plan():
    plan = generate_book_plan(
        topic_id="anxiety",
        persona_id="corporate_managers",
        runtime_format="standard_book",
        engine_type="comparison",
        chapter_count=6,
    )

    before = plan.chapters[0].chapter_thesis
    packet = build_chapter_contracts(plan)

    assert packet["contracts"][0]["thesis"] == before
