"""Tests for G-LAYER catalog manifest acceptance_layer gate."""
from __future__ import annotations

from scripts.ci.check_catalog_manifest_acceptance_layer import validate_manifest


def test_missing_layer_fails():
    v = validate_manifest(
        {
            "quality_profile": "production",
            "books": [{"book_id": "b1", "status": "ok"}],
        },
        label="m",
    )
    assert any("missing acceptance_layer" in x for x in v)


def test_path_works_ok():
    v = validate_manifest(
        {
            "quality_profile": "flagship",
            "books": [
                {
                    "book_id": "b1",
                    "status": "ok",
                    "acceptance_layer": "path_works",
                }
            ],
        },
        label="m",
    )
    assert v == []


def test_system_working_requires_artifact():
    v = validate_manifest(
        {
            "quality_profile": "production",
            "books": [
                {
                    "book_id": "b1",
                    "status": "ok",
                    "acceptance_layer": "system_working",
                }
            ],
        },
        label="m",
    )
    assert any("requires" in x for x in v)


def test_system_working_with_artifact_ok():
    v = validate_manifest(
        {
            "quality_profile": "production",
            "books": [
                {
                    "book_id": "b1",
                    "status": "ok",
                    "acceptance_layer": "system working",
                    "layer3_artifact": "artifacts/qa/flagship_line_edit/x/ONTGP_VERDICT.md",
                }
            ],
        },
        label="m",
    )
    assert v == []


def test_draft_profile_blocked():
    v = validate_manifest(
        {"quality_profile": "draft", "books": []},
        label="m",
    )
    assert any("D3" in x for x in v)
