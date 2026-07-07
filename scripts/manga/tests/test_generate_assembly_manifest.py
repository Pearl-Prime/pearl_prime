"""Tests for generate_assembly_manifest.py — continuity_state → assembly manifest."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

import assemble_from_bank as afb  # noqa: E402
import generate_assembly_manifest as gam  # noqa: E402

SERIES = "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
CONT_DIR = REPO / "artifacts" / "manga" / SERIES / "continuity_state" / "ep_001"


@pytest.mark.skipif(not CONT_DIR.is_dir(), reason="stillness ep_001 continuity_state absent")
def test_ep001_generates_35_panels():
    manifest, gaps = gam.generate(
        series_id=SERIES,
        profile_id="stillness_en_01",
        episode_id="ep_001",
    )
    assert gaps["stats"]["panels_total"] == 35
    assert len(manifest["panels"]) <= 35
    assert gaps["unique_L0"] >= 1
    assert gaps["unique_L2"] >= 1


@pytest.mark.skipif(not CONT_DIR.is_dir(), reason="stillness ep_001 continuity_state absent")
def test_manifest_validates_when_panels_present():
    manifest, _ = gam.generate(
        series_id=SERIES,
        profile_id="stillness_en_01",
        episode_id="ep_001",
    )
    if not manifest["panels"]:
        pytest.skip("no complete panels — bank assets not on disk")
    errors = afb.validate_manifest(manifest)
    assert errors == []


@pytest.mark.skipif(not CONT_DIR.is_dir(), reason="stillness ep_001 continuity_state absent")
def test_real_layers_resolved_from_cache(tmp_path):
    manifest, gaps = gam.generate(
        series_id=SERIES,
        profile_id="stillness_en_01",
        episode_id="ep_001",
    )
    if gaps["stats"]["layers_real"] == 0:
        pytest.skip("v4_render_cache not present in this checkout")
    assert gaps["stats"]["layers_real"] > 0
    for panel in manifest["panels"]:
        for layer in panel["layers"]:
            assert layer["provenance"] in ("REAL", "INTERIM")
            if layer["provenance"] == "REAL":
                p = REPO / layer["asset"]
                assert p.is_file(), layer["asset"]


@pytest.mark.skipif(not CONT_DIR.is_dir(), reason="stillness ep_001 continuity_state absent")
def test_cli_writes_artifacts(tmp_path):
    out = tmp_path / "ep_001_from_continuity.yaml"
    rc = gam.main([
        "--series", SERIES,
        "--profile", "stillness_en_01",
        "--episode", "ep_001",
        "--out", str(out),
    ])
    assert rc == 0
    assert out.is_file()
    gaps_path = out.with_name("ep_001_bank_gaps.json")
    assert gaps_path.is_file()
    gaps = json.loads(gaps_path.read_text())
    assert gaps["stats"]["panels_total"] == 35
    yaml.safe_load(out.read_text())
