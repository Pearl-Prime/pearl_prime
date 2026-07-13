"""Tests for real V5 selected-component structural assembly."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml
from PIL import Image

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

import assemble_real_v5_structural as real_v5  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "real_v5_structural_selection.json"


def _rect(image: Image.Image, bbox: list[int], color: list[int]) -> None:
    x0, y0, x1, y1 = bbox
    for x in range(x0, x1):
        for y in range(y0, y1):
            image.putpixel((x, y), tuple(color))


def _write_sidecar(path: Path, meta: dict) -> None:
    path.with_suffix(".composition.json").write_text(
        json.dumps(meta, indent=2) + "\n",
        encoding="utf-8",
    )


def _l0_meta(panel_id: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "asset_id": f"{panel_id}_l0",
        "layer_class": "L0",
        "genre": "mecha",
        "style_register": "mecha_test",
        "bg_class": "full_render",
        "light": {"azimuth": "ambient"},
        "camera": {
            "angle_bucket": "eye_level",
            "eye_level_y_pct": 42,
            "camera_height": "standing",
        },
        "anchor_slots": [],
        "support_zones": [{
            "zone_id": "clear_floor",
            "kind": "floor",
            "polygon_pct": [[0, 62], [100, 56], [100, 100], [0, 100]],
            "occupancy": "clear",
            "allows_character_support": True,
            "allowed_structural_templates": ["standing_room_scene"],
            "priority": 0,
        }],
        "structural_layer_contract": {
            "id": "mecha_clean_structural_layer_v1",
            "status": "clean",
            "role": "environment_support",
            "subject": "environment",
            "contains_primary_subject": False,
            "contains_foreground_subject": False,
            "contains_pilot": False,
            "contains": [],
        },
    }


def _fixture_panel(tmp_path: Path) -> Path:
    cfg = json.loads(FIXTURE.read_text())
    root = tmp_path / "source_v5_panel"
    root.mkdir()
    panel_id = cfg["panel_id"]
    width = cfg["canvas"]["width"]
    height = cfg["canvas"]["height"]

    Image.new("RGBA", (width, height), (0, 0, 180, 255)).save(root / "layer_00.png")
    Image.new("RGBA", (width, height), (20, 150, 80, 255)).save(root / "layer_01.png")
    _write_sidecar(root / "layer_01.png", _l0_meta(panel_id))

    l2 = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    _rect(l2, cfg["contaminated_layer_02"]["bbox"], cfg["contaminated_layer_02"]["color"])
    l2.save(root / "layer_02.png")

    l3 = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    _rect(l3, cfg["clean_layer_03"]["main_bbox"], cfg["clean_layer_03"]["color"])
    _rect(l3, cfg["clean_layer_03"]["stray_bbox"], cfg["clean_layer_03"]["stray_color"])
    l3.save(root / "layer_03.png")

    (root / "_telemetry.json").write_text(json.dumps({
        "panel_id": panel_id,
        "genre_id": "mecha",
        "layer_roles": {
            "layer_00.png": "model_composite_preview",
            "layer_01.png": "claimed_background",
            "layer_02.png": "claimed_l2_but_contaminated",
            "layer_03.png": "claimed_l3_but_actual_foreground",
        },
    }, indent=2) + "\n", encoding="utf-8")
    return root


def test_real_v5_selects_layer03_when_layer02_contacts_multiple_edges(tmp_path: Path):
    root = _fixture_panel(tmp_path)
    out = tmp_path / "out"
    result = real_v5.assemble_real_v5_structural(
        v5_panel_root=root,
        out_dir=out,
        subject="pilot",
        tests="pytest fixture",
    )

    assert result.selected_candidate.source_name == "layer_03.png"
    assert result.selected_candidate.removed_px == 169
    assert result.final_path.is_file()
    assert result.final_path.read_bytes() != (root / "layer_00.png").read_bytes()

    closeout = json.loads(result.closeout_path.read_text())
    layer02 = next(
        report for report in closeout["candidate_reports"]
        if report["source_name"] == "layer_02.png"
    )
    assert "main_component_contacts_multiple_edges" in layer02["rejection_reasons"]
    assert closeout["raw-v5-layer-roles"] == "not-green"
    assert closeout["selected-component-structural-assembly"] == "green-for-proof"
    assert closeout["manga-100pct-green"] == "not-claimed"


def test_real_v5_manifest_never_uses_layer00(tmp_path: Path):
    root = _fixture_panel(tmp_path)
    out = tmp_path / "out"
    result = real_v5.assemble_real_v5_structural(
        v5_panel_root=root,
        out_dir=out,
        subject="pilot",
    )
    manifest_text = result.manifest_path.read_text()
    manifest = yaml.safe_load(manifest_text)

    assert "layer_00.png" not in manifest_text
    layers = manifest["panels"][0]["layers"]
    assert layers[0]["asset"] == "layer_01.png"
    assert layers[1]["asset"] == "layer_02.png"

    provenance = json.loads((out / "_provenance.json").read_text())
    assert all("layer_00.png" not in row["asset"] for row in provenance["records"])


def test_real_v5_records_required_gate_report(tmp_path: Path):
    root = _fixture_panel(tmp_path)
    out = tmp_path / "out"
    real_v5.assemble_real_v5_structural(v5_panel_root=root, out_dir=out, subject="pilot")
    gate_report = json.loads((out / "gate_report.json").read_text())
    gates = {gate["gate"] for gate in gate_report["panels"][0]["gates"]}

    assert {
        "L0_STRUCTURAL_PURITY",
        "L2_STRUCTURAL_PURITY",
        "L2_QUALITY",
        "L0_SUPPORT_ZONE",
    } <= gates
    assert gate_report["panels"][0]["passed"] is True


def test_real_v5_uses_tuned_seated_defaults():
    assert real_v5._resolve_transform_values(
        support_mode="intentional_seat_table",
        tx_pct=None,
        ty_pct=None,
        uniform_scale=None,
    ) == (62.0, 74.0, 1.05)
    assert real_v5._resolve_transform_values(
        support_mode="standing_floor",
        tx_pct=None,
        ty_pct=None,
        uniform_scale=None,
    ) == (50.0, 86.0, 0.62)


def test_real_v5_fails_when_no_clean_candidate(tmp_path: Path):
    root = _fixture_panel(tmp_path)
    (root / "layer_03.png").unlink()

    with pytest.raises(real_v5.RealV5StructuralError, match="no clean foreground candidate"):
        real_v5.assemble_real_v5_structural(
            v5_panel_root=root,
            out_dir=tmp_path / "out",
            subject="pilot",
        )


def test_real_v5_help_exposes_v5_panel_root(capsys):
    with pytest.raises(SystemExit) as exc:
        real_v5.main(["--help"])
    assert exc.value.code == 0
    assert "--v5-panel-root" in capsys.readouterr().out
