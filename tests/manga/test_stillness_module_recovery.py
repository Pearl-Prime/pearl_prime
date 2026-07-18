"""Tests for stillness prerequisite modules (panel planning / chapter grammar / L2 annotate)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

from annotate_l2_composition_legal import annotate_file, legality_fields  # noqa: E402
from panel_planning_rules import (  # noqa: E402
    ARCHETYPE_SHOT_TYPE,
    shot_type_for_archetype,
    validate_manifest_composition_planning,
)
from validate_chapter_composition_grammar import (  # noqa: E402
    validate_chapter_composition_grammar,
)


def test_shot_type_for_archetype_core_map():
    assert shot_type_for_archetype("sparse_establishing_wide") == "establishing"
    assert shot_type_for_archetype("tea_beat_close_up") == "insert_object"
    assert shot_type_for_archetype("shared_meal_table_medium") == "re_establish"
    assert shot_type_for_archetype("miyazaki_ma_pause") == "pillow_ma"
    assert shot_type_for_archetype(None) is None
    assert shot_type_for_archetype("unknown_archetype_xyz") is None
    assert "character_at_table_medium" in ARCHETYPE_SHOT_TYPE


def test_planning_flags_half_person_on_full_render(tmp_path: Path):
    l0 = tmp_path / "L0.png"
    l2 = tmp_path / "L2_bust.png"
    l0.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    l2.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    (tmp_path / "L0.composition.json").write_text(
        json.dumps({
            "schema_version": "1.0.0",
            "asset_id": "L0",
            "layer_class": "L0",
            "bg_class": "full_render",
        })
    )
    (tmp_path / "L2_bust.composition.json").write_text(
        json.dumps({
            "schema_version": "1.0.0",
            "asset_id": "L2_bust",
            "layer_class": "L2",
            "crop_class": "bust",
            "abstract_stage_eligible": True,
            "room_capable": False,
        })
    )
    manifest = {
        "panels": [{
            "panel_id": "ep001_099",
            "shot_type": "dialogue_bust",
            "layers": [
                {"layer_class": "L0", "asset": str(l0), "provenance": "REAL"},
                {
                    "layer_class": "L2",
                    "asset": str(l2),
                    "provenance": "REAL",
                    "bbox_pct": [20, 20, 60, 60],
                },
            ],
        }]
    }
    errs = validate_manifest_composition_planning(manifest, tmp_path, tmp_path)
    assert any("HR-F01" in e for e in errs)


def test_planning_allows_bust_on_defocus(tmp_path: Path):
    l0 = tmp_path / "L0.png"
    l2 = tmp_path / "L2_bust.png"
    l0.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    l2.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    (tmp_path / "L0.composition.json").write_text(
        json.dumps({
            "schema_version": "1.0.0",
            "asset_id": "L0",
            "layer_class": "L0",
            "bg_class": "full_render",
        })
    )
    (tmp_path / "L2_bust.composition.json").write_text(
        json.dumps({
            "schema_version": "1.0.0",
            "asset_id": "L2_bust",
            "layer_class": "L2",
            "crop_class": "bust",
            "abstract_stage_eligible": True,
        })
    )
    manifest = {
        "panels": [{
            "panel_id": "ep001_005",
            "shot_type": "dialogue_bust",
            "layers": [
                {
                    "layer_class": "L0",
                    "asset": str(l0),
                    "provenance": "REAL",
                    "derivation": {"type": "defocus"},
                },
                {
                    "layer_class": "L2",
                    "asset": str(l2),
                    "provenance": "REAL",
                    "bbox_pct": [20, 20, 60, 60],
                },
            ],
        }]
    }
    errs = validate_manifest_composition_planning(manifest, tmp_path, tmp_path)
    assert not any("HR-F01" in e for e in errs)


def test_hr_u16_fails_after_seven_abstract():
    panels = []
    for i in range(1, 9):
        panels.append({
            "panel_id": f"ep001_{i:03d}",
            "shot_type": "insert_object",
            "layers": [{
                "layer_class": "L0",
                "asset": "x.png",
                "provenance": "REAL",
                "derivation": {"type": "tone_gradient"},
            }],
        })
    panels[0] = {
        "panel_id": "ep001_001",
        "shot_type": "establishing",
        "layers": [{"layer_class": "L0", "asset": "x.png", "provenance": "REAL"}],
    }
    findings = validate_chapter_composition_grammar({"panels": panels}, Path("."))
    u16 = [f for f in findings if f.rule_id == "HR-U16" and f.severity == "FAIL"]
    assert u16, findings
    assert u16[0].panel_id == "ep001_008"


def test_hr_u16_passes_with_re_establish_on_seventh_abstract():
    panels = [{
        "panel_id": "ep001_001",
        "shot_type": "establishing",
        "layers": [{"layer_class": "L0", "asset": "x.png", "provenance": "REAL"}],
    }]
    for i in range(2, 8):
        panels.append({
            "panel_id": f"ep001_{i:03d}",
            "shot_type": "insert_object",
            "layers": [{
                "layer_class": "L0",
                "asset": "x.png",
                "provenance": "REAL",
                "derivation": {"type": "tone_gradient"},
            }],
        })
    panels.append({
        "panel_id": "ep001_008",
        "shot_type": "re_establish",
        "layers": [{"layer_class": "L0", "asset": "x.png", "provenance": "REAL"}],
    })
    findings = validate_chapter_composition_grammar({"panels": panels}, Path("."))
    assert not [f for f in findings if f.rule_id == "HR-U16" and f.severity == "FAIL"]


def test_annotate_legality_fields_room_vs_bust():
    room = legality_fields("knees_up", asset_name="L2_seated_kitchen_knees_up_v1_alpha.png")
    assert room["room_capable"] is True
    assert room["abstract_stage_eligible"] is False
    bust = legality_fields("bust", asset_name="L2_clean_bust_calm_v2_alpha.png")
    assert bust["abstract_stage_eligible"] is True
    assert bust["room_capable"] is False


def test_annotate_file_writes_sidecar(tmp_path: Path):
    png = tmp_path / "L2_clean_bust_calm_v2_alpha.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)
    side = tmp_path / "L2_clean_bust_calm_v2_alpha.composition.json"
    side.write_text(json.dumps({
        "schema_version": "1.0.0",
        "asset_id": "L2_clean_bust_calm_v2",
        "layer_class": "L2",
        "crop_class": "bust",
    }))
    report = annotate_file(png, dry_run=False, infer_crop=False, force=True)
    assert report["action"] == "wrote"
    meta = json.loads(side.read_text())
    assert meta["abstract_stage_eligible"] is True
    assert meta["room_capable"] is False
