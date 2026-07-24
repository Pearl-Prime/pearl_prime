from __future__ import annotations

import logging

import yaml

from phoenix_v4.content_banks.loader import REQUIRED_VARIANT_KEYS, load_content_bank_registry
from phoenix_v4.planning.enrichment_select import (
    PersonaPoolRotationState,
    _try_registry_variant,
    _try_persona_content,
    _try_teacher_content,
)
from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow


def _atoms(count: int, slot_type: str) -> dict[str, list[dict]]:
    return {
        slot_type: [
            {"atom_id": f"reflection_{i}", "content": f"Distinct reflection body number {i}."}
            for i in range(count)
        ]
    }


def test_teacher_and_persona_pickers_rotate_before_reusing() -> None:
    for picker, slot_type in (
        (_try_teacher_content, "TEACHER_DOCTRINE"),
        (_try_persona_content, "HOOK"),
    ):
        rotation = PersonaPoolRotationState()
        seen: set[str] = set()
        picked = []
        for i in range(6):
            hit = picker(
                _atoms(6, slot_type),
                slot_type,
                f"chapter-{i}",
                rotation_state=rotation,
                seen_bodies=seen,
            )
            assert hit is not None
            picked.append(hit[1])
        assert len(set(picked)) == 6


def _valid_variant(variant_id: str) -> dict:
    rec = {key: [] for key in REQUIRED_VARIANT_KEYS}
    rec.update(
        {
            "variant_id": variant_id,
            "slot_type": "SCENE",
            "body": "A valid scene body.",
            "band": "recognition",
            "intensity": "medium",
            "mechanism_depth": "surface",
            "ontgp_move": "orient",
            "collision_family": "test",
            "ei_v2_targets": {},
        }
    )
    return rec


def test_content_bank_loader_skips_bad_file_and_keeps_valid_bank(tmp_path, caplog) -> None:
    (tmp_path / "valid.yaml").write_text(
        yaml.safe_dump({"variants": [_valid_variant("valid_001")]}), encoding="utf-8"
    )
    (tmp_path / "malformed.yaml").write_text(
        yaml.safe_dump({"variants": [{"variant_id": "bad_001", "body": "Old schema"}]}),
        encoding="utf-8",
    )

    with caplog.at_level(logging.WARNING):
        registry = load_content_bank_registry(banks_dir=tmp_path)

    assert [v["variant_id"] for v in registry.banks["valid"]] == ["valid_001"]
    assert "malformed" not in registry.banks
    assert "Skipping malformed content bank" in caplog.text


def test_registry_variant_removes_only_book_wide_exact_paragraph_restamps() -> None:
    repeated = "This shared reflection is long enough to represent an authored paragraph."
    reg_lists = {
        "REFLECTION": [
            {
                "variants": [
                    {"variant_id": "v1", "content": f"A unique governing lead.\n\n{repeated}"}
                ]
            },
            {
                "variants": [
                    {"variant_id": "v2", "content": f"A different governing lead.\n\n{repeated}"}
                ]
            },
        ]
    }
    counters = {"REFLECTION": 0}
    seen: set[str] = set()

    first = _try_registry_variant(reg_lists, "REFLECTION", counters, "seed", seen)
    second = _try_registry_variant(reg_lists, "REFLECTION", counters, "seed", seen)

    assert first is not None and repeated in first[0]
    assert second is not None and "A different governing lead." in second[0]
    assert repeated not in second[0]


def test_mechanism_contrast_counts_as_thesis_without_generic_false_positive() -> None:
    chapter = """
First, notice the alarm before you argue with it. Then, let your feet meet the floor.
None of this is metaphor. It is a budget, and every predicted disaster is a withdrawal.
Your hands shaking before a presentation is mobilization, not malfunction.
For example, name three things you can see. Because your body predicts danger, it mobilizes.
Next, breathe out slowly. Finally, choose one small action and write it down.
"""
    result = evaluate_chapter_flow(chapter)
    assert result.metrics["thesis_hits"] >= 1
    assert "MISSING_CLEAR_POINT" not in result.errors

    thesis_free = """
First, the room was quiet. Then, a phone rang. For example, someone crossed the hall.
Next, the light changed. Finally, she opened a notebook and wrote three words.
Because the meeting was near, she took one breath and waited.
"""
    result = evaluate_chapter_flow(thesis_free)
    assert result.metrics["thesis_hits"] == 0
    assert "MISSING_CLEAR_POINT" in result.errors
