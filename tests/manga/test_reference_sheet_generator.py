"""Tests for V2 Phase B.6 reference sheet generator (dry-run + skips)."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import yaml

from scripts.manga.character_individuation.reference_sheet_generator import (
    GenerationResult,
    generate_reference_sheet,
)


def _full_design_block():
    return {
        "axes": {
            "face_shape": {"value": "oval", "lockout": "yes"},
            "eye_geometry": {
                "size": "small", "shape": "almond", "lid_fold": "double",
                "eyelash_density": "minimal", "lockout": "yes",
            },
            "hair": {
                "length": "ear_length", "parting": "side_left",
                "fringe_style": "side_swept", "texture": "slight_wave",
                "color_signal": "black", "lockout": "yes",
            },
            "color_signal": {"value": "warm_earth_tone", "lockout": "yes"},
            "wardrobe_register": {"value": "monastic_casual", "lockout": "yes"},
            "age_signaling": {"value": "late_30s", "lockout": "yes"},
            "accessories": {"value": "prayer_beads_subtle", "lockout": "yes"},
            "mouth_jaw": {"lip_shape": "thin_both", "lockout": "yes"},
            "nose_construction": {"value": "straight_rounded", "lockout": "yes"},
            "build": {"value": "average", "lockout": "no"},
            "skin_treatment": {"value": "clean", "lockout": "no"},
            "posture_default": {"value": "contemplative_grounded", "lockout": "no"},
        },
    }


def _series_yaml():
    return {
        "series_id": "stillness_press_anxiety_vol1",
        "brand_id": "stillness_press",
        "market_demo": "seinen",
        "genre_family": "healing",
        "character_design": _full_design_block(),
    }


def test_dry_run_writes_provenance_only(tmp_path):
    cd_path = tmp_path / "stillness_press_anxiety_vol1.yaml"
    cd_path.write_text(yaml.safe_dump(_series_yaml(), sort_keys=False))

    res = generate_reference_sheet(
        cd_path,
        teacher_id="ahjan",
        brand_id="stillness_press",
        output_root=tmp_path,
        dry_run=True,
    )

    assert isinstance(res, GenerationResult)
    assert res.success is True
    assert res.skipped is False
    assert "ahjan" in res.out_path
    # provenance written; PNG NOT written in dry-run
    prov_path = Path(res.provenance_path)
    assert prov_path.is_file()
    png_path = Path(res.out_path)
    assert not png_path.is_file()
    prov = json.loads(prov_path.read_text())
    for key in (
        "teacher_id", "brand_id", "engine", "workflow_path", "sampler",
        "seed", "positive_prompt", "negative_prompt",
        "character_design_path", "character_design_sha256",
        "engine_router_reasoning", "ip_adapter_weight_target",
    ):
        assert key in prov
    assert prov["teacher_id"] == "ahjan"
    assert prov["brand_id"] == "stillness_press"
    # engine for healing genre + seinen demo: healing is in _ANIMAGINE_GENRES,
    # so router picks Animagine. Seed deterministic from teacher_id.
    assert prov["engine"] in {"animagine_xl_4_0", "qwen_image", "flux_schnell"}


def test_missing_yaml_returns_skipped_result(tmp_path):
    res = generate_reference_sheet(
        tmp_path / "does_not_exist.yaml",
        teacher_id="ghost",
        brand_id="ghost_brand",
        output_root=tmp_path,
        dry_run=True,
    )
    assert res.skipped is True
    assert "not found" in res.skip_reason


def test_yaml_without_axes_returns_skipped_result(tmp_path):
    bad = tmp_path / "broken.yaml"
    bad.write_text(yaml.safe_dump({"series_id": "x", "character_design": {}}))
    res = generate_reference_sheet(
        bad,
        teacher_id="x",
        brand_id="x_brand",
        output_root=tmp_path,
        dry_run=True,
    )
    assert res.skipped is True
    assert "axes" in res.skip_reason


def test_seed_is_deterministic_from_teacher_id(tmp_path):
    cd_path = tmp_path / "s.yaml"
    cd_path.write_text(yaml.safe_dump(_series_yaml(), sort_keys=False))
    a = generate_reference_sheet(cd_path, teacher_id="ahjan", output_root=tmp_path / "a", dry_run=True)
    b = generate_reference_sheet(cd_path, teacher_id="ahjan", output_root=tmp_path / "b", dry_run=True)
    c = generate_reference_sheet(cd_path, teacher_id="joshin", output_root=tmp_path / "c", dry_run=True)
    seed_a = json.loads(Path(a.provenance_path).read_text())["seed"]
    seed_b = json.loads(Path(b.provenance_path).read_text())["seed"]
    seed_c = json.loads(Path(c.provenance_path).read_text())["seed"]
    assert seed_a == seed_b
    assert seed_a != seed_c  # different teacher → different seed


def test_explicit_seed_override_respected(tmp_path):
    cd_path = tmp_path / "s.yaml"
    cd_path.write_text(yaml.safe_dump(_series_yaml(), sort_keys=False))
    res = generate_reference_sheet(
        cd_path, teacher_id="ahjan", output_root=tmp_path,
        seed=12345, dry_run=True,
    )
    assert json.loads(Path(res.provenance_path).read_text())["seed"] == 12345


def test_provenance_carries_character_design_sha256(tmp_path):
    cd_path = tmp_path / "s.yaml"
    cd_path.write_text(yaml.safe_dump(_series_yaml(), sort_keys=False))
    res = generate_reference_sheet(
        cd_path, teacher_id="ahjan", output_root=tmp_path, dry_run=True,
    )
    prov = json.loads(Path(res.provenance_path).read_text())
    assert len(prov["character_design_sha256"]) == 64


def test_workflow_template_missing_returns_skipped(tmp_path, monkeypatch):
    cd_path = tmp_path / "s.yaml"
    cd_path.write_text(yaml.safe_dump(_series_yaml(), sort_keys=False))

    # Monkeypatch _select_engine_for to return a path that doesn't exist
    from scripts.manga.character_individuation import reference_sheet_generator as rsg
    from scripts.manga.character_individuation.engine_router import EngineSelection

    fake_sel = EngineSelection(
        engine="qwen_image",
        workflow_path=tmp_path / "nonexistent.json",
        sampler={"steps": 24, "cfg": 4.0, "sampler": "euler", "scheduler": "simple",
                 "width": 1080, "height": 1920},
        reference_enabled=False,
        reasoning="test",
    )
    monkeypatch.setattr(rsg, "_select_engine_for", lambda cd: fake_sel)

    res = rsg.generate_reference_sheet(
        cd_path, teacher_id="ahjan", output_root=tmp_path, dry_run=False,
    )
    assert res.skipped is True
    assert "workflow template" in res.skip_reason


def test_comfy_url_unreachable_returns_skipped(tmp_path):
    cd_path = tmp_path / "s.yaml"
    cd_path.write_text(yaml.safe_dump(_series_yaml(), sort_keys=False))

    # Use a guaranteed-unreachable URL; non-dry-run will try to submit
    res = generate_reference_sheet(
        cd_path, teacher_id="ahjan",
        output_root=tmp_path,
        comfy_url="http://0.0.0.0:1/",
        dry_run=False,
    )
    # With workflow templates absent / unreachable comfy, expect skipped
    # rather than crash. (Workflow exists per repo defaults; ComfyUI URL
    # won't connect → skipped.)
    assert res.success is False
    assert res.skipped is True
