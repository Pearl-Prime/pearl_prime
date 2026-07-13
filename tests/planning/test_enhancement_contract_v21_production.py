from __future__ import annotations

from types import SimpleNamespace

from phoenix_v4.planning.accent_planner import enrichment_contract_v1_enabled
from phoenix_v4.qa import book_outline
from phoenix_v4.qa import enhancement_contract
from scripts.ci.check_enhancement_contract_v21 import check_payload


def _chapter(*, hooks=(), slots=("ANGLE_DEFINITION",), accents=()):
    slot_rows = [
        SimpleNamespace(
            slot_type=slot,
            enrichment_applied=list(hooks),
            source_id="angle:test",
            atom_id="",
            variant_id="",
            source="",
            content="body",
            journey_exercise_id=None,
        )
        for slot in slots
    ]
    chapter = SimpleNamespace(
        number=1,
        slots=slot_rows,
        source_breakdown={},
        exercise_journey={},
    )
    accent_rows = [{"class": value, "accent_id": value.lower()} for value in accents]
    return chapter, accent_rows


def test_production_activation_is_doctrine_based():
    assert enrichment_contract_v1_enabled(
        {"quality_profile": "production", "runtime_format": "extended_book_2h"}
    )
    assert not enrichment_contract_v1_enabled(
        {"quality_profile": "draft", "runtime_format": "extended_book_2h"}
    )


def test_angle_definition_does_not_invent_analogy_metaphor_or_parable():
    chapter, accents = _chapter()
    groups = book_outline._chapter_v21_groups(chapter, accents)
    families = book_outline._enrichment_families(chapter, accents)
    qa_groups = enhancement_contract._chapter_v21_groups(chapter, accents)
    assert "ANALOGY" not in groups["cohesion_and_craft"]
    assert "METAPHOR" not in groups["cohesion_and_craft"]
    assert "ANALOGY" not in qa_groups["cohesion_and_craft"]
    assert "METAPHOR" not in qa_groups["cohesion_and_craft"]
    assert families["analogy"] is False
    assert families["metaphor"] is False
    assert families["parable_or_external_story"] is False


def test_explicit_trace_evidence_is_reported():
    chapter, accents = _chapter(
        hooks=("analogy", "metaphor", "parable"),
        slots=("STORY",),
        accents=("EXTERNAL_STORY",),
    )
    groups = book_outline._chapter_v21_groups(chapter, accents)
    families = book_outline._enrichment_families(chapter, accents)
    assert {"ANALOGY", "METAPHOR"} <= set(groups["cohesion_and_craft"])
    assert families["parable_or_external_story"] is True


def test_over_budget_production_payload_fails():
    payload = {
        "status": "PASS",
        "enhancement_contract_v21": {
            "optional_accent_budget": {
                "hard_max_total_accents": 10,
                "hard_max_accent_chapters": 8,
                "max_accents_per_chapter": 2,
                "accent_free_chapters_minimum": 4,
                "actual": {
                    "assigned_total_optional_accents": 11,
                    "optional_accent_chapter_count": 9,
                    "accent_free_chapter_count": 3,
                    "per_chapter_optional_counts": {"1": 3},
                },
            }
        },
        "validation": {"v21_integrity": {"status": "PASS"}},
    }
    errors = check_payload(payload, production=True)
    assert "hard_max_total_accents_exceeded" in errors
    assert "hard_max_accent_chapters_exceeded" in errors
    assert "accent_free_chapters_minimum_not_met" in errors


def test_valid_sparse_payload_passes():
    payload = {
        "status": "PASS",
        "enhancement_contract_v21": {
            "optional_accent_budget": {
                "hard_max_total_accents": 10,
                "hard_max_accent_chapters": 8,
                "max_accents_per_chapter": 2,
                "accent_free_chapters_minimum": 4,
                "actual": {
                    "assigned_total_optional_accents": 8,
                    "optional_accent_chapter_count": 6,
                    "accent_free_chapter_count": 6,
                    "per_chapter_optional_counts": {"1": 1, "3": 2},
                },
            }
        },
        "validation": {"v21_integrity": {"status": "PASS"}},
    }
    assert not check_payload(payload, production=True)
