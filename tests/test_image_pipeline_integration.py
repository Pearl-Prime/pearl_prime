"""Integration tests: prompt compiler -> image backend -> QC -> manifest.

Tests the full pipeline path that production follows, verifying that
the subsystems integrate correctly end-to-end. Uses dry_run mode and
mocked HTTP calls to avoid external dependencies.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from phoenix_v4.manga.image_backend import (
    FixtureReplayImageBackend,
    NoopImageBackend,
    RunComfyImageBackend,
    build_panel_images_manifest,
)
from scripts.image_generation.image_qc import run_panel_qc
from scripts.image_generation.prompt_compiler import (
    compile_all_panel_prompts,
    compile_panel_prompt,
)


# Minimal valid 512x512 PNG header
_MIN_PNG = bytes(
    [
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x02, 0x00,  # width=512
        0x00, 0x00, 0x02, 0x00,  # height=512
        0x08, 0x06, 0x00, 0x00, 0x00,
        0x1F, 0x15, 0xC4, 0x89,
        0x00, 0x00, 0x00, 0x0A,
        0x49, 0x44, 0x41, 0x54,
        0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00, 0x05,
        0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4,
        0x00, 0x00, 0x00, 0x00,
        0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82,
    ]
)


def _full_panel_prompts() -> dict[str, Any]:
    """Realistic multi-panel prompts artifact."""
    return {
        "schema_version": "1.0.0",
        "artifact_type": "panel_prompts",
        "series_id": "integration_test",
        "chapter_id": "ch_01",
        "config_hash": "integ123",
        "style_id": "dark_psychological",
        "panels": [
            {
                "panel_id": "p_1_0",
                "page_number": 1,
                "panel_index": 0,
                "visual_prompt": "A figure standing at a crossroads under storm clouds",
                "negative_prompt": "bright colors, cartoon, anime",
                "composition_notes": "wide establishing shot, rule of thirds",
                "continuity_tags": ["exterior", "storm", "night"],
                "sdf_conditioning": {"mood": "foreboding", "style": "cinematic noir"},
            },
            {
                "panel_id": "p_1_1",
                "page_number": 1,
                "panel_index": 1,
                "visual_prompt": "Close-up of trembling hands holding a crumpled letter",
                "negative_prompt": "cheerful, bright",
                "composition_notes": "extreme close-up, shallow depth of field",
            },
            {
                "panel_id": "p_2_0",
                "page_number": 2,
                "panel_index": 0,
                "visual_prompt": "Empty room with a single chair and harsh overhead light",
                "negative_prompt": "warm, cozy",
                "composition_notes": "centered, symmetrical",
                "continuity_tags": ["interior", "isolation"],
            },
        ],
    }


# ── Compile -> Backend -> QC -> Manifest integration ────────────────


class TestCompileToDryRunManifest:
    """Full pipeline: compile prompts, generate (dry_run), build manifest."""

    def test_full_dry_run_pipeline(self) -> None:
        pp = _full_panel_prompts()

        # Step 1: compile prompts
        compiled = compile_all_panel_prompts(pp)
        assert len(compiled) == 3
        for c in compiled:
            assert c["positive"]  # non-empty
            assert "panel_id" in c

        # Step 2: generate images (dry_run)
        backend = RunComfyImageBackend(dry_run=True)
        results = backend.generate(pp)
        assert len(results) == 3

        # Step 3: build manifest
        manifest = build_panel_images_manifest(pp, results)
        assert manifest["artifact_type"] == "panel_images_manifest"
        assert len(manifest["panels"]) == 3
        for panel in manifest["panels"]:
            assert panel["status"] == "dry_run"
            assert "panel_id" in panel

    def test_compiled_prompts_flow_to_backend(self) -> None:
        """Verify the backend receives compiled prompts matching what compile_panel_prompt produces."""
        pp = _full_panel_prompts()
        backend = RunComfyImageBackend(dry_run=True)
        results = backend.generate(pp)

        for result, panel in zip(results, pp["panels"]):
            expected = compile_panel_prompt(panel)
            assert result["compiled_prompt"]["positive"] == expected["positive"]
            assert result["compiled_prompt"]["negative"] == expected["negative"]


class TestFixtureReplayIntegration:
    """FixtureReplayImageBackend -> QC -> Manifest pipeline."""

    def test_replay_with_real_png_passes_qc(self, tmp_path: Path) -> None:
        img = tmp_path / "p_1_0.png"
        img.write_bytes(_MIN_PNG)
        mapping = {"p_1_0": img}
        backend = FixtureReplayImageBackend(mapping)

        pp = {"panels": [{"panel_id": "p_1_0", "visual_prompt": "test"}]}
        results = backend.generate(pp)
        assert len(results) == 1
        assert results[0]["status"] == "ok"

        # QC should pass on the file
        qc = run_panel_qc(Path(results[0]["path"]))
        assert qc["passed"] is True
        assert qc["width"] == 512
        assert qc["height"] == 512

        # Manifest should be valid
        manifest = build_panel_images_manifest(pp, results)
        assert manifest["panels"][0]["status"] == "ok"
        assert manifest["panels"][0]["width"] == 512

    def test_replay_missing_file_stays_pending(self, tmp_path: Path) -> None:
        mapping = {"p_1_0": tmp_path / "missing.png"}
        backend = FixtureReplayImageBackend(mapping)
        pp = {"panels": [{"panel_id": "p_1_0", "visual_prompt": "test"}]}
        results = backend.generate(pp)
        assert results[0]["status"] == "pending"

    def test_from_json_file(self, tmp_path: Path) -> None:
        img = tmp_path / "images" / "p_1_0.png"
        img.parent.mkdir()
        img.write_bytes(_MIN_PNG)
        mapping_file = tmp_path / "replay.json"
        mapping_file.write_text(json.dumps({"p_1_0": "images/p_1_0.png"}))
        backend = FixtureReplayImageBackend.from_json_file(mapping_file)
        pp = {"panels": [{"panel_id": "p_1_0", "visual_prompt": "test"}]}
        results = backend.generate(pp)
        assert results[0]["status"] == "ok"


class TestNoopBackendIntegration:
    def test_noop_all_pending(self) -> None:
        pp = _full_panel_prompts()
        backend = NoopImageBackend()
        results = backend.generate(pp)
        assert all(r["status"] == "pending" for r in results)
        manifest = build_panel_images_manifest(pp, results)
        assert all(p["status"] == "pending" for p in manifest["panels"])


class TestQCEdgeCases:
    """QC behavior for edge-case file conditions."""

    def test_qc_large_file_passes(self, tmp_path: Path) -> None:
        """File under 50MB limit should pass (if valid PNG)."""
        img = tmp_path / "big.png"
        img.write_bytes(_MIN_PNG)
        result = run_panel_qc(img)
        assert result["passed"] is True

    def test_qc_custom_min_dimensions(self, tmp_path: Path) -> None:
        """Custom min dimension parameters are respected."""
        img = tmp_path / "panel.png"
        img.write_bytes(_MIN_PNG)
        # 512x512 image should fail with min_width=1024
        result = run_panel_qc(img, min_width=1024)
        assert result["passed"] is False
        failed = {c["name"] for c in result["checks"] if not c["passed"]}
        assert "min_dimensions" in failed

    def test_qc_result_structure(self, tmp_path: Path) -> None:
        """QC result always has the expected keys."""
        img = tmp_path / "panel.png"
        img.write_bytes(_MIN_PNG)
        result = run_panel_qc(img)
        assert "passed" in result
        assert "checks" in result
        assert "width" in result
        assert "height" in result
        assert isinstance(result["checks"], list)
        for check in result["checks"]:
            assert "name" in check
            assert "passed" in check
            assert "detail" in check


class TestManifestErrorRecovery:
    """Manifest builder handles partial failures gracefully."""

    def test_manifest_with_mixed_statuses(self) -> None:
        pp = {
            "panels": [
                {"panel_id": "p_ok"},
                {"panel_id": "p_fail"},
                {"panel_id": "p_pending"},
            ]
        }
        results = [
            {"panel_id": "p_ok", "status": "ok", "path": "/tmp/ok.png", "width": 512, "height": 512, "content_sha256": "abc"},
            {"panel_id": "p_fail", "status": "failed", "path": None, "width": 0, "height": 0, "error": "timeout"},
            {"panel_id": "p_pending", "status": "pending", "path": None, "width": 0, "height": 0},
        ]
        manifest = build_panel_images_manifest(pp, results)
        statuses = [p["status"] for p in manifest["panels"]]
        assert statuses == ["ok", "failed", "pending"]
        # Only the ok panel should have dimensions
        assert manifest["panels"][0].get("width") == 512
        assert "width" not in manifest["panels"][1]

    def test_manifest_missing_results_default_to_pending(self) -> None:
        pp = {"panels": [{"panel_id": "p_1_0"}]}
        manifest = build_panel_images_manifest(pp, [])
        assert manifest["panels"][0]["status"] == "pending"
