from __future__ import annotations

from phoenix_v4.planning.accent_planner import (
    accent_class_bucket,
    build_enhancement_contract_v21_summary,
    count_unit_for_surface,
)
from phoenix_v4.rendering.accent_renderer import insert_accent_beats_into_streams


def test_v21_summary_separates_proof_surfaces_from_optional_budget() -> None:
    summary = build_enhancement_contract_v21_summary(
        accent_budget={
            "QUOTE": 3,
            "ENCOURAGEMENT": 2,
            "REFLECTION_QUESTION": 3,
            "AUTHOR_COMMENTARY": 1,
            "WISDOM_ESSENCE": 1,
            "TROUBLESHOOTING": 1,
            "CITED_EVIDENCE": 1,
            "EXTERNAL_STORY": 2,
        },
        flat_rows=[
            {"chapter": 1, "class": "QUOTE"},
            {"chapter": 2, "class": "EXTERNAL_STORY"},
            {"chapter": 3, "class": "CITED_EVIDENCE"},
            {"chapter": 4, "class": "TROUBLESHOOTING"},
        ],
        chapter_count=12,
        story_mix_profile="intimate_voice",
        max_accents_per_chapter=2,
        persona_id="gen_z_professionals",
        topic_id="anxiety",
    )

    optional_actual = summary["optional_accent_budget"]["actual"]
    assert optional_actual["assigned_total_optional_accents"] == 1
    assert optional_actual["optional_assignment_counts"]["QUOTE"] == 1
    assert "EXTERNAL_STORY" not in optional_actual["optional_assignment_counts"]
    assert "CITED_EVIDENCE" not in optional_actual["optional_assignment_counts"]
    tracked = {row["surface"]: row for row in summary["tracked_surfaces"]}
    assert tracked["EXTERNAL_STORY"]["bucket"] == "proof_and_embodiment"
    assert tracked["CITED_EVIDENCE"]["bucket"] == "proof_and_embodiment"
    assert tracked["TROUBLESHOOTING"]["bucket"] == "chapter_engine"


def test_surface_bucket_and_count_unit_make_author_voice_distinction_explicit() -> None:
    assert accent_class_bucket("AUTHOR_DISCLOSURE") == "proof_and_embodiment"
    assert accent_class_bucket("AUTHOR_COMMENTARY") == "optional_accents"
    assert count_unit_for_surface("AUTHOR_DISCLOSURE") == "substantial_first_person_disclosure"
    assert count_unit_for_surface("AUTHOR_COMMENTARY") == "substantial_interpretive_commentary_block"


def test_accent_renderer_carries_v21_metadata_into_render_audit_rows() -> None:
    _, _, rendered = insert_accent_beats_into_streams(
        ["HOOK", "THREAD"],
        ["Hook body.", "Thread body."],
        [
            {
                "class": "ENCOURAGEMENT",
                "accent_id": "enc_01",
                "position": "before_THREAD",
                "keys": {
                    "surface_bucket": "optional_accents",
                    "count_unit": "substantial_encouragement_block",
                    "supply_provenance": "authored_bank",
                },
            }
        ],
        {"enc_01": "You are allowed to move one breath at a time."},
    )

    assert rendered[0]["surface_bucket"] == "optional_accents"
    assert rendered[0]["count_unit"] == "substantial_encouragement_block"
    assert rendered[0]["keys"]["supply_provenance"] == "authored_bank"
