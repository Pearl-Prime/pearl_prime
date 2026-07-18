"""Tests for Waystream catalog uniqueness gate and subtitle regen dry-run artifact."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "artifacts/waystream/subtitle_regen_dryrun.json"


@pytest.mark.skipif(not ARTIFACT.exists(), reason="dry-run artifact not built")
def test_dryrun_artifact_800_unique():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["count"] == 800
    assert data["distinct_titles"] == 800
    assert data["distinct_subtitles"] == 800
    assert data["distinct_pairs"] == 800
    assert not data.get("dup_subtitles")


def test_check_waystream_script_importable():
    from scripts.ci import check_waystream_catalog_uniqueness as m
    assert m.EXPECTED == 800
