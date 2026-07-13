from __future__ import annotations

from phoenix_v4.planning.enhancement_contract_v21_runtime import (
    build_optional_accent_budget,
    validate_contract_rows,
    validate_optional_accent_budget,
)


def _budget_with_actual(*, assigned: int, chapters: list[int], per_chapter: dict[str, int]):
    budget = build_optional_accent_budget(chapter_count=12, max_accents_per_chapter=2)
    budget["actual"] = {
        "assigned_total_optional_accents": assigned,
        "optional_assignment_counts": {"QUOTE": assigned},
        "chapters_with_optional_accents": chapters,
        "optional_accent_chapter_count": len(chapters),
        "accent_free_chapter_count": 12 - len(chapters),
        "per_chapter_optional_counts": per_chapter,
    }
    return budget


def test_optional_budget_retains_memo_priors_and_scaled_limits() -> None:
    budget = build_optional_accent_budget(chapter_count=12, max_accents_per_chapter=2)

    assert budget["prior_source"] == "ENHANCEMENT_CONTRACT_V2_WORKING_PRIORS_2026-07-13"
    assert budget["memo_target_accent_chapters"] == {"min": 5, "max": 7}
    assert budget["memo_hard_max_accent_chapters"] == 8
    assert budget["memo_target_total_accents"] == {"min": 7, "max": 9}
    assert budget["memo_hard_max_total_accents"] == 10
    assert budget["target_accent_chapters"] == {"min": 5, "max": 7}
    assert budget["hard_max_total_accents"] == 10


def test_optional_budget_hard_fails_ceiling_violations() -> None:
    budget = _budget_with_actual(
        assigned=11,
        chapters=[1, 2, 3, 4, 5, 6, 7, 8, 9],
        per_chapter={"1": 3, "2": 1, "3": 1, "4": 1, "5": 1, "6": 1, "7": 1, "8": 1, "9": 1},
    )

    result = validate_optional_accent_budget(budget, chapter_count=12)

    assert result["status"] == "FAIL"
    codes = {row["code"] for row in result["hard_failures"]}
    assert "hard_max_total_optional_accents_exceeded" in codes
    assert "hard_max_optional_accent_chapters_exceeded" in codes
    assert "max_optional_accents_per_chapter_exceeded" in codes
    assert "accent_free_minimum_not_met" in codes


def test_supported_underfill_is_advisory_not_hard_fail() -> None:
    budget = _budget_with_actual(
        assigned=6,
        chapters=[1, 3, 5, 7, 9],
        per_chapter={"1": 2, "3": 1, "5": 1, "7": 1, "9": 1},
    )

    result = validate_optional_accent_budget(budget, chapter_count=12)

    assert result["status"] == "PASS"
    assert {row["code"] for row in result["warnings"]} == {"supported_budget_underfill"}


def test_external_story_requires_function_source_citation_and_truth_metadata() -> None:
    good = {
        "chapter": 2,
        "class": "EXTERNAL_STORY",
        "accent_id": "ext_good",
        "story_function": "recognition",
        "truth_metadata": {
            "source": "lawful source",
            "citation": "Lawful Source, 2026",
            "truth_status": "verified",
        },
    }
    bad = {"chapter": 3, "class": "EXTERNAL_STORY", "accent_id": "ext_bad"}

    result = validate_contract_rows(
        accent_rows=[good, bad],
        core_surface_rows=[],
        chapter_count=12,
    )

    codes = {row["code"] for row in result["hard_failures"]}
    assert "external_story_missing_function" in codes
    assert "external_story_missing_source" in codes
    assert "external_story_missing_citation" in codes
    assert "external_story_missing_truth_status" in codes


def test_cited_evidence_requires_citation_and_verification_metadata() -> None:
    result = validate_contract_rows(
        accent_rows=[
            {
                "chapter": 4,
                "class": "CITED_EVIDENCE",
                "accent_id": "ev_bad",
                "selected_body_excerpt": "Evidence-like sentence without metadata.",
                "truth_metadata": {},
            }
        ],
        core_surface_rows=[],
        chapter_count=12,
    )

    codes = {row["code"] for row in result["hard_failures"]}
    assert "cited_evidence_missing_citation" in codes
    assert "cited_evidence_missing_verification" in codes


def test_callback_return_requires_prior_plant_and_semantic_development() -> None:
    result = validate_contract_rows(
        accent_rows=[],
        core_surface_rows=[
            {
                "chapter": 4,
                "slot_type": "ANGLE_CALLBACK",
                "callback_role": "return",
                "plant_id": "alarm",
                "return_function": "angle_callback",
                "semantic_development": "",
                "final_order_index": 2,
            }
        ],
        chapter_count=12,
    )

    codes = {row["code"] for row in result["hard_failures"]}
    assert "callback_return_without_prior_plant" in codes
    assert "callback_return_without_semantic_development" in codes


def test_valid_callback_return_passes_when_prior_plant_exists() -> None:
    result = validate_contract_rows(
        accent_rows=[],
        core_surface_rows=[
            {
                "chapter": 1,
                "slot_type": "ANGLE_DEFINITION",
                "callback_role": "plant",
                "plant_id": "alarm",
                "final_order_index": 1,
            },
            {
                "chapter": 4,
                "slot_type": "ANGLE_CALLBACK",
                "callback_role": "return",
                "plant_id": "alarm",
                "return_function": "angle_callback",
                "semantic_development": "later_chapter_reactivation",
                "final_order_index": 2,
            },
        ],
        chapter_count=12,
    )

    assert result["status"] == "PASS"


def test_parable_must_use_story_like_container() -> None:
    result = validate_contract_rows(
        accent_rows=[
            {
                "chapter": 5,
                "class": "AUTHOR_COMMENTARY",
                "accent_id": "bad_parable",
                "keys": {"story_type": "parable"},
            }
        ],
        core_surface_rows=[],
        chapter_count=12,
    )

    assert {row["code"] for row in result["hard_failures"]} == {"invalid_parable_container"}
