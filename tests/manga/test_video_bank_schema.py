"""Schema round-trip for character_capture_manifest (Lane 04)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

REPO = Path(__file__).resolve().parents[2]
SCHEMA = REPO / "schemas" / "manga" / "character_capture_manifest.schema.json"
GOLDEN = REPO / "tests" / "fixtures" / "manga" / "video_bank" / "golden_capture_manifest.json"
FIXTURE_INV = (
    REPO / "tests" / "fixtures" / "manga" / "video_bank" / "demand" / "character_pose_inventory.yaml"
)


@pytest.mark.skipif(not SCHEMA.is_file(), reason="capture manifest schema not on disk yet")
def test_golden_manifest_validates() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    example = json.loads(GOLDEN.read_text(encoding="utf-8"))
    Draft7Validator(schema).validate(example)


@pytest.mark.skipif(not SCHEMA.is_file(), reason="capture manifest schema not on disk yet")
def test_compiler_round_trip(tmp_path: Path) -> None:
    from scripts.manga.video_bank.compile_capture_manifest import compile_manifest
    from scripts.manga.video_bank._schema import validate_manifest

    manifest = compile_manifest(
        series_id="stillness_en_01",
        character_id="mira_aoki",
        outfit_id="cream_sweater",
        identity_version="pulid_sheet_v1",
        anchor_path="tests/fixtures/manga/video_bank/frames/anchor.png",
        bank_contracts_path=FIXTURE_INV,
        engine="wan2.7-i2v",
        duration_s=5,
        reserve_seconds=10,
    )
    assert manifest["demand_source"]["mode"] == "bank_contracts_fallback"
    assert manifest["capture_sets"]
    validate_manifest(manifest)
    out = tmp_path / "m.json"
    out.write_text(json.dumps(manifest), encoding="utf-8")
    again = json.loads(out.read_text(encoding="utf-8"))
    validate_manifest(again)


@pytest.mark.skipif(not SCHEMA.is_file(), reason="capture manifest schema not on disk yet")
def test_compiler_rejects_non_cloud_engine() -> None:
    from scripts.manga.video_bank.compile_capture_manifest import compile_manifest

    with pytest.raises(ValueError, match="not in allowed"):
        compile_manifest(
            series_id="stillness_en_01",
            character_id="mira_aoki",
            outfit_id="cream_sweater",
            identity_version="pulid_sheet_v1",
            anchor_path="tests/fixtures/manga/video_bank/frames/anchor.png",
            bank_contracts_path=FIXTURE_INV,
            engine="vace-1.3b",
        )
