"""Manga JSON Schemas — validation and fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from phoenix_v4.manga.models.leakage import assert_handoff_has_no_transmission_leakage
from phoenix_v4.manga.models.validation import (
    iter_instance_schema_stems,
    load_and_validate,
    validate_instance,
    validator_for,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "manga"
VALID = FIXTURES / "valid"
INVALID = FIXTURES / "invalid"

_ZERO_SHA = "0" * 64


def _minimal_payload(stem: str) -> dict:
    common = {"schema_version": "1.0.0", "artifact_type": stem}
    builders: dict[str, dict] = {
        "anchor_panels": {
            **common,
            "artifact_type": "anchor_panels",
            "series_id": "s",
            "anchor_panels": [
                {
                    "anchor_panel_id": "ap1",
                    "category": "dialogue_standard",
                    "reference_image_id": "ref1",
                    "measured_parameters": {
                        "contrast_ratio": 0.5,
                        "linework_weight_px": 2.0,
                        "shadow_coverage_pct": 0.3,
                        "highlight_coverage_pct": 0.2,
                    },
                }
            ],
        },
        "chapter_request": {
            **common,
            "artifact_type": "chapter_request",
            "series_id": "s",
            "chapter_id": "c",
        },
        "style_bible": {
            **common,
            "artifact_type": "style_bible",
            "style_bible_version": "1.0.0",
            "lexicons": {},
        },
        "lettering_style_bible": {
            **common,
            "artifact_type": "lettering_style_bible",
            "fonts": {},
        },
        "genre_blueprint": {
            **common,
            "artifact_type": "genre_blueprint",
            "genre_id": "shonen",
        },
        "story_architecture_internal": {
            **common,
            "artifact_type": "story_architecture_internal",
            "series_id": "s",
            "arc_id": "a",
            "chapters": [
                {
                    "chapter_number": 1,
                    "plot_beats": [
                        {"beat_index": 0, "beat_text": "x", "beat_type": "opening"}
                    ],
                }
            ],
            "transmission_audit": {},
            "constraint_checks": {},
        },
        "story_architecture_handoff": {
            **common,
            "artifact_type": "story_architecture_handoff",
            "series_id": "s",
            "arc_id": "a",
            "chapters": [
                {
                    "chapter_number": 1,
                    "plot_beats": [{"beat_index": 0, "beat_text": "x"}],
                }
            ],
        },
        "asset_registry": {
            **common,
            "artifact_type": "asset_registry",
            "assets": [{"asset_id": "a1"}],
        },
        "character_model_sheets": {
            **common,
            "artifact_type": "character_model_sheets",
            "characters": [{"character_id": "c1"}],
        },
        "motif_evolution_map": {
            **common,
            "artifact_type": "motif_evolution_map",
            "motifs": [],
        },
        "chapter_script_writer_handoff": {
            **common,
            "artifact_type": "chapter_script_writer_handoff",
            "series_id": "s",
            "chapter_id": "c1",
            "pages": [],
        },
        "chapter_script_internal_record": {
            **common,
            "artifact_type": "chapter_script_internal_record",
            "series_id": "s",
            "chapter_id": "c1",
            "pages": [{"panels": [{"carrier_beat": True}]}],
        },
        "panel_prompts": {
            **common,
            "artifact_type": "panel_prompts",
            "panels": [{"panel_id": "p1", "prompt": "test"}],
        },
        "panel_images_manifest": {
            **common,
            "artifact_type": "panel_images_manifest",
            "panels": [{"panel_id": "p1", "status": "pending"}],
        },
        "lettering_spec": {
            **common,
            "artifact_type": "lettering_spec",
            "lettering_panels": [{"panel_id": "p1", "silence_confirmed": True}],
        },
        "revision_queue": {
            **common,
            "artifact_type": "revision_queue",
            "chapter_clearance": "pass",
            "issues": [],
        },
        "series_continuity_state": {
            **common,
            "artifact_type": "series_continuity_state",
            "series_id": "s",
            "last_episode_id": "ep_001",
            "volume_arc_position": {
                "volume": 1,
                "chapter_in_volume": 1,
                "volume_title": "v1",
            },
            "settled_state": "ok",
            "rival_state": [{"rival_id": "r1", "state": "idle"}],
            "motif_state": {},
            "active_pressures": [],
            "set_pieces_fired": [],
            "unresolved_hooks": [],
        },
        "series_memory": {
            **common,
            "artifact_type": "series_memory",
            "facts": [],
        },
        "series_memory_update": {
            **common,
            "artifact_type": "series_memory_update",
            "patches": [],
        },
        "series_memory_snapshot": {
            **common,
            "artifact_type": "series_memory_snapshot",
            "snapshot_of_series_memory_sha256": _ZERO_SHA,
            "facts": [],
        },
        "structural_bundle": {
            "schema_version": "1.0.0",
            "bundle_id": "sb1",
            "structural_template_id": "seated_table_scene",
            "canvas": {"width": 1080, "height": 1920},
            "nodes": [
                {
                    "node_id": "surface_1",
                    "category": "support_surface",
                    "support_polygon_pct": [[0.1, 0.8], [0.9, 0.8], [0.9, 0.95]],
                },
                {
                    "node_id": "char_1",
                    "category": "character",
                    "contact_point_pct": [0.5, 0.8],
                },
            ],
            "edges": [
                {
                    "edge_id": "edge_1",
                    "relation": "seated_on",
                    "from_node": "char_1",
                    "to_node": "surface_1",
                },
            ],
        },
        "structural_plan": {
            "schema_version": "1.0.0",
            "envelope_id": "sp1",
            "plan_hash": "abcdef0123456789",
            "transform_model": "structural_mvp_v1",
            "plan_body": {
                "panel_id": "p1",
                "canvas": {"width": 1080, "height": 1920},
                "resolved_placements": [
                    {
                        "node_id": "char_1",
                        "transform": {
                            "tx_pct": 0.5,
                            "ty_pct": 0.8,
                            "uniform_scale": 1.0,
                            "rotation_deg": 0.0,
                        },
                    },
                ],
                "support_graph": {
                    "nodes": ["surface_1", "char_1"],
                    "edges": ["edge_1"],
                },
            },
        },
        "stage_manifest": {
            **common,
            "artifact_type": "stage_manifest",
            "stage_id": "chapter_writer",
            "stage_name": "Chapter Writer",
            "attempt": 1,
            "status": "passed",
        },
        "ite_qc_report": {
            "schema_version": "1.0.0",
            "artifact_type": "ite_qc_report",
            "ITE_score": 0.65,
            "gates": [
                {"id": "T-01", "level": "BLOCKER", "passed": True, "detail": "ok"},
            ],
            "blocker_fail_count": 0,
            "warn_fail_count": 0,
            "passed": True,
            "fractal_blocker": False,
        },
        "ite_color_arc": {
            "schema_version": "1.0.0",
            "artifact_type": "ite_color_arc",
            "genre": "shonen",
            "panels": [
                {
                    "panel_id": "p1",
                    "chapter_position_pct": 0.0,
                    "color_temp_target": 3200.0,
                    "ffmpeg_colorbalance": {"rs": 0.05, "gs": 0.01, "bs": -0.03},
                },
            ],
        },
        "series_plan": {
            "series_plan_schema": "1.0.0",
            "artifact_type": "series_plan",
            "series_id": "stillness_press__ahjan__gen_z__anxiety",
            "brand_id": "stillness_press",
            "teacher_id": "ahjan",
            "locale": "en_US",
            "format": "color_vertical_webtoon",
            "panel_layout_template": "config/manga/panel_layout_templates/vertical_scroll_webtoon.yaml",
            "target_platforms": ["webtoon_canvas"],
        },
        "book_plan": {
            "book_plan_schema": "1.0.0",
            "artifact_type": "book_plan",
            "book_id": "ep_001",
            "series_id": "stillness_press__ahjan__gen_z__anxiety",
            "format": "color_vertical_webtoon",
        },
        "assembly_manifest": {
            "schema_version": "1.0.0",
            "series_id": "stillness_press__ahjan__gen_z__anxiety",
            "canvas": {"width": 1080, "height": 1920},
            "panels": [
                {
                    "panel_id": "p1",
                    "layers": [
                        {
                            "layer_class": "L0",
                            "asset": "bank/L0/kitchen.png",
                            "provenance": "REAL",
                        },
                    ],
                },
            ],
        },
        "ite_fractal_report": {
            "schema_version": "1.0.0",
            "artifact_type": "ite_fractal_report",
            "stub_mode": True,
            "panels": [
                {
                    "panel_id": "p1",
                    "fd_estimate": 1.4,
                    "source_category": "arboreal",
                    "compliant": True,
                    "warn_out_of_band": False,
                    "note": "ok",
                },
            ],
            "blocker_no_fractal_nature_in_release_resolve": False,
        },
        "composition_meta": {
            "schema_version": "1.0.0",
            "asset_id": "L2_pilot_minimal",
            "layer_class": "L2",
            "crop_class": "waist_up",
            "anchor": {"point": "waist_line", "y_px": 800},
            "eye_y_px": 400,
            "implied_camera": {"angle_bucket": "eye_level", "el_crossing": "chest"},
        },
        "serial_spine": {
            **common,
            "artifact_type": "serial_spine",
            "series_id": "s",
            "genre": "shonen",
            "mode": "teacher",
            "serial_engine": "rank_gate_trials",
            "long_arc_spine": "Can the disciple prove worthy before the gate closes?",
            "renewable_unit": "trial arc with escalating rival",
            "escalation_axis": "rank and recognition",
            "binge_mechanism": "unresolved gate deadline",
            "volume_arcs": [
                {"volume": v, "title": f"V{v}", "logline": f"Arc {v}"}
                for v in range(1, 6)
            ],
            "named_pressures": [
                {"id": "p1", "kind": "rival", "label": "Rival"},
            ],
            "set_piece_registry": [
                {"id": "sp1", "label": "Trial gate"},
            ],
        },
        "series_continuity_state": {
            **common,
            "artifact_type": "series_continuity_state",
            "series_id": "s",
            "last_episode_id": "ep_001",
            "volume_arc_position": {
                "volume": 1,
                "chapter_in_volume": 1,
                "volume_title": "Opening",
            },
            "settled_state": "Protagonist believes the trial is won.",
            "rival_state": [],
            "motif_state": {"condition": "calm"},
            "active_pressures": ["p1"],
            "set_pieces_fired": ["sp1"],
            "unresolved_hooks": ["gate still closed"],
        },
        "story_excellence_realization_report": {
            "schema_version": "1.0.0",
            "artifact_type": "manga_story_excellence_realization_report",
            "status": "PASS",
            "production_blocking": False,
            "score": 100,
            "threshold": 100,
            "gates": [],
        },
    }
    if stem not in builders:
        raise KeyError(stem)
    return builders[stem]


@pytest.mark.parametrize("stem", iter_instance_schema_stems())
def test_minimal_instance_validates(stem: str) -> None:
    validate_instance(_minimal_payload(stem), stem)


def test_valid_chapter_request_fixture() -> None:
    load_and_validate(VALID / "minimal_chapter_request.json", "chapter_request")


def test_valid_story_handoff_fixture() -> None:
    data = load_and_validate(
        VALID / "minimal_story_architecture_handoff.json",
        "story_architecture_handoff",
    )
    assert_handoff_has_no_transmission_leakage(data)


def test_invalid_chapter_request_rejected() -> None:
    import jsonschema

    raw = json.loads((INVALID / "chapter_request_missing_series.json").read_text(encoding="utf-8"))
    with pytest.raises(jsonschema.ValidationError):
        validate_instance(raw, "chapter_request")


def test_handoff_fixture_with_leakage_fails_policy() -> None:
    import jsonschema

    raw = json.loads(
        (INVALID / "story_handoff_with_leakage.json").read_text(encoding="utf-8")
    )
    validate_instance(raw, "story_architecture_handoff")
    with pytest.raises(AssertionError, match="Transmission leakage"):
        assert_handoff_has_no_transmission_leakage(raw)


def test_internal_record_may_contain_carrier_beat() -> None:
    data = _minimal_payload("chapter_script_internal_record")
    validate_instance(data, "chapter_script_internal_record")


@pytest.mark.parametrize("stem", iter_instance_schema_stems())
def test_validator_for_each_stem(stem: str) -> None:
    v = validator_for(stem)
    v.validate(_minimal_payload(stem))
