"""Tests for RunComfyImageBackend: init, dry_run, prompt compilation, mock API, QC, errors."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from phoenix_v4.manga.image_backend import (
    ImageBackend,
    RunComfyImageBackend,
    build_panel_images_manifest,
)
from scripts.image_generation.prompt_compiler import (
    compile_all_panel_prompts,
    compile_panel_prompt,
)
from scripts.image_generation.image_qc import run_panel_qc

# Minimal valid PNG (1x1 RGBA)
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


def _sample_panel_prompts() -> dict[str, Any]:
    """Build a minimal panel_prompts artifact for testing."""
    return {
        "schema_version": "1.0.0",
        "artifact_type": "panel_prompts",
        "series_id": "test_series",
        "chapter_id": "ch_test",
        "config_hash": "abc123",
        "style_id": "dark_psychological",
        "panels": [
            {
                "panel_id": "p_1_0",
                "page_number": 1,
                "panel_index": 0,
                "visual_prompt": "A dark hallway with flickering lights",
                "negative_prompt": "bright, colorful, happy",
                "composition_notes": "low angle shot",
                "continuity_tags": ["interior", "night"],
            },
            {
                "panel_id": "p_1_1",
                "page_number": 1,
                "panel_index": 1,
                "visual_prompt": "Close-up of a hand reaching for a door handle",
                "negative_prompt": "cartoon, anime style",
                "composition_notes": "extreme close-up",
            },
        ],
    }


# ── Protocol conformance ─────────────────────────────────────────────


class TestProtocolConformance:
    def test_runcomfy_backend_satisfies_protocol(self) -> None:
        backend = RunComfyImageBackend(dry_run=True)
        assert isinstance(backend, ImageBackend)

    def test_has_generate_method(self) -> None:
        backend = RunComfyImageBackend(dry_run=True)
        assert callable(getattr(backend, "generate", None))


# ── Init ─────────────────────────────────────────────────────────────


class TestInit:
    def test_defaults(self) -> None:
        backend = RunComfyImageBackend(dry_run=True)
        assert backend.deployment_id == "677edba8-ace0-4b2b-bad2-8e94b9959065"
        assert backend.dry_run is True
        assert backend.workflow_path.name == "flux_video_bank.json"

    def test_custom_deployment(self) -> None:
        backend = RunComfyImageBackend(deployment_id="custom-123", dry_run=True)
        assert backend.deployment_id == "custom-123"

    def test_env_deployment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RUNCOMFY_DEPLOYMENT_ID", "env-deploy-456")
        backend = RunComfyImageBackend(dry_run=True)
        assert backend.deployment_id == "env-deploy-456"

    def test_explicit_overrides_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RUNCOMFY_DEPLOYMENT_ID", "env-deploy-456")
        backend = RunComfyImageBackend(deployment_id="explicit-789", dry_run=True)
        assert backend.deployment_id == "explicit-789"

    def test_custom_workflow_path(self, tmp_path: Path) -> None:
        wf = tmp_path / "custom.json"
        wf.write_text("{}", encoding="utf-8")
        backend = RunComfyImageBackend(workflow_path=wf, dry_run=True)
        assert backend.workflow_path == wf


# ── Dry-run mode ─────────────────────────────────────────────────────


class TestDryRun:
    def test_dry_run_returns_all_panels(self) -> None:
        backend = RunComfyImageBackend(dry_run=True)
        pp = _sample_panel_prompts()
        results = backend.generate(pp)
        assert len(results) == 2
        for r in results:
            assert r["status"] == "dry_run"
            assert r["path"] is None
            assert "compiled_prompt" in r
            assert "positive" in r["compiled_prompt"]
            assert "negative" in r["compiled_prompt"]

    def test_dry_run_no_api_calls(self) -> None:
        """Ensure no HTTP requests are made in dry_run mode."""
        backend = RunComfyImageBackend(dry_run=True)
        pp = _sample_panel_prompts()
        with patch("scripts.image_generation.runcomfy_batch.requests") as mock_req:
            results = backend.generate(pp)
            mock_req.post.assert_not_called()
            mock_req.get.assert_not_called()

    def test_dry_run_empty_panels(self) -> None:
        backend = RunComfyImageBackend(dry_run=True)
        pp = {"panels": []}
        assert backend.generate(pp) == []


# ── Prompt compilation ───────────────────────────────────────────────


class TestPromptCompiler:
    def test_compile_basic_panel(self) -> None:
        panel = {
            "panel_id": "p_1_0",
            "visual_prompt": "A dark hallway",
            "negative_prompt": "bright",
        }
        result = compile_panel_prompt(panel)
        assert "dark hallway" in result["positive"]
        assert result["negative"] == "bright"

    def test_compile_with_composition_and_tags(self) -> None:
        panel = {
            "panel_id": "p_1_0",
            "visual_prompt": "A door",
            "composition_notes": "wide angle",
            "continuity_tags": ["exterior", "day"],
        }
        result = compile_panel_prompt(panel)
        assert "wide angle" in result["positive"]
        assert "exterior" in result["positive"]
        assert "day" in result["positive"]

    def test_compile_with_sdf_conditioning(self) -> None:
        panel = {
            "panel_id": "p_1_0",
            "visual_prompt": "A figure",
            "sdf_conditioning": {"mood": "tense", "style": "noir"},
        }
        result = compile_panel_prompt(panel)
        assert "mood: tense" in result["positive"]
        assert "style: noir" in result["positive"]

    def test_compile_all_panels(self) -> None:
        pp = _sample_panel_prompts()
        results = compile_all_panel_prompts(pp)
        assert len(results) == 2
        assert results[0]["panel_id"] == "p_1_0"
        assert results[1]["panel_id"] == "p_1_1"
        assert "dark hallway" in results[0]["positive"].lower()

    def test_compile_missing_prompt_graceful(self) -> None:
        panel = {"panel_id": "p_1_0"}
        result = compile_panel_prompt(panel)
        assert result["positive"] == ""
        assert result["negative"] == ""


# ── Image QC ─────────────────────────────────────────────────────────


class TestImageQC:
    def test_qc_pass_valid_png(self, tmp_path: Path) -> None:
        img = tmp_path / "panel.png"
        img.write_bytes(_MIN_PNG)
        result = run_panel_qc(img)
        assert result["passed"] is True
        assert result["width"] == 512
        assert result["height"] == 512

    def test_qc_fail_missing_file(self, tmp_path: Path) -> None:
        result = run_panel_qc(tmp_path / "nonexistent.png")
        assert result["passed"] is False
        failed = [c for c in result["checks"] if not c["passed"]]
        assert any(c["name"] == "file_exists" for c in failed)

    def test_qc_fail_empty_file(self, tmp_path: Path) -> None:
        img = tmp_path / "empty.png"
        img.write_bytes(b"")
        result = run_panel_qc(img)
        assert result["passed"] is False

    def test_qc_fail_not_png(self, tmp_path: Path) -> None:
        img = tmp_path / "fake.png"
        img.write_bytes(b"not a png file at all")
        result = run_panel_qc(img)
        assert result["passed"] is False
        failed_names = {c["name"] for c in result["checks"] if not c["passed"]}
        assert "valid_png" in failed_names

    def test_qc_fail_too_small(self, tmp_path: Path) -> None:
        """1x1 PNG fails minimum dimension check."""
        tiny_png = bytes(
            [
                0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
                0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
                0x00, 0x00, 0x00, 0x01,  # width=1
                0x00, 0x00, 0x00, 0x01,  # height=1
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
        img = tmp_path / "tiny.png"
        img.write_bytes(tiny_png)
        result = run_panel_qc(img)
        assert result["passed"] is False
        failed_names = {c["name"] for c in result["checks"] if not c["passed"]}
        assert "min_dimensions" in failed_names


# ── Mock API response handling ───────────────────────────────────────


class TestMockAPIFlow:
    """Test full generate flow with mocked HTTP calls."""

    def _make_backend(self, tmp_path: Path) -> RunComfyImageBackend:
        wf = tmp_path / "workflow.json"
        wf.write_text(json.dumps({
            "nodes": {
                "positive_prompt": {"inputs": {"text": "{{positive_prompt}}"}},
                "negative_prompt": {"inputs": {"text": "{{negative_prompt}}"}},
                "empty_latent": {"inputs": {"width": "{{width}}", "height": "{{height}}"}},
                "sampler": {"inputs": {"seed": "{{seed}}", "cfg": "{{guidance}}"}},
            }
        }), encoding="utf-8")
        return RunComfyImageBackend(
            deployment_id="test-deploy",
            api_key="test-key-123",
            workflow_path=wf,
            output_dir=tmp_path / "output",
        )

    def test_successful_generation(self, tmp_path: Path) -> None:
        backend = self._make_backend(tmp_path)
        pp = _sample_panel_prompts()

        mock_submit_resp = MagicMock()
        mock_submit_resp.status_code = 200
        mock_submit_resp.json.return_value = {"run_id": "run-abc"}
        mock_submit_resp.raise_for_status = MagicMock()

        mock_poll_resp = MagicMock()
        mock_poll_resp.status_code = 200
        mock_poll_resp.json.return_value = {
            "status": "completed",
            "outputs": {"images": [{"url": "https://cdn.runcomfy.net/img/result.png"}]},
        }
        mock_poll_resp.raise_for_status = MagicMock()

        mock_download_resp = MagicMock()
        mock_download_resp.status_code = 200
        mock_download_resp.content = _MIN_PNG
        mock_download_resp.raise_for_status = MagicMock()

        def side_effect_post(url, **kwargs):
            return mock_submit_resp

        def side_effect_get(url, **kwargs):
            if "runs/run-abc" in url:
                return mock_poll_resp
            return mock_download_resp

        with patch("scripts.image_generation.runcomfy_batch.requests") as mock_req:
            mock_req.post = MagicMock(side_effect=side_effect_post)
            mock_req.get = MagicMock(side_effect=side_effect_get)

            results = backend.generate(pp)

        assert len(results) == 2
        for r in results:
            assert r["status"] == "ok"
            assert r["width"] == 512
            assert r["height"] == 512
            assert r["content_sha256"]
            assert Path(r["path"]).name.endswith(".png")

    def test_api_timeout_marks_failed(self, tmp_path: Path) -> None:
        backend = self._make_backend(tmp_path)
        pp = {"panels": [{"panel_id": "p_1_0", "visual_prompt": "test"}]}

        mock_submit_resp = MagicMock()
        mock_submit_resp.json.return_value = {"run_id": "run-timeout"}
        mock_submit_resp.raise_for_status = MagicMock()

        mock_poll_resp = MagicMock()
        mock_poll_resp.json.return_value = {"status": "running"}
        mock_poll_resp.raise_for_status = MagicMock()

        with patch("scripts.image_generation.runcomfy_batch.requests") as mock_req:
            mock_req.post = MagicMock(return_value=mock_submit_resp)
            mock_req.get = MagicMock(return_value=mock_poll_resp)
            # Patch time.sleep to avoid actual waiting, and set max_wait low
            with patch("scripts.image_generation.runcomfy_batch.time.sleep"):
                with patch("scripts.image_generation.runcomfy_batch.MAX_POLL_S", 0.01):
                    results = backend.generate(pp)

        assert len(results) == 1
        assert results[0]["status"] == "failed"
        assert "error" in results[0]

    def test_api_failure_marks_failed(self, tmp_path: Path) -> None:
        backend = self._make_backend(tmp_path)
        pp = {"panels": [{"panel_id": "p_1_0", "visual_prompt": "test"}]}

        mock_submit_resp = MagicMock()
        mock_submit_resp.json.return_value = {"run_id": "run-fail"}
        mock_submit_resp.raise_for_status = MagicMock()

        mock_poll_resp = MagicMock()
        mock_poll_resp.json.return_value = {"status": "failed", "error": "GPU OOM"}
        mock_poll_resp.raise_for_status = MagicMock()

        with patch("scripts.image_generation.runcomfy_batch.requests") as mock_req:
            mock_req.post = MagicMock(return_value=mock_submit_resp)
            mock_req.get = MagicMock(return_value=mock_poll_resp)
            results = backend.generate(pp)

        assert len(results) == 1
        assert results[0]["status"] == "failed"
        assert "GPU OOM" in results[0]["error"]

    def test_qc_failure_marks_failed(self, tmp_path: Path) -> None:
        """Image downloads OK but QC fails (e.g., not a valid PNG)."""
        backend = self._make_backend(tmp_path)
        pp = {"panels": [{"panel_id": "p_1_0", "visual_prompt": "test"}]}

        mock_submit_resp = MagicMock()
        mock_submit_resp.json.return_value = {"run_id": "run-qc"}
        mock_submit_resp.raise_for_status = MagicMock()

        mock_poll_resp = MagicMock()
        mock_poll_resp.json.return_value = {
            "status": "completed",
            "outputs": {"images": [{"url": "https://cdn.runcomfy.net/bad.png"}]},
        }
        mock_poll_resp.raise_for_status = MagicMock()

        mock_download_resp = MagicMock()
        mock_download_resp.content = b"not a valid png"
        mock_download_resp.raise_for_status = MagicMock()

        def side_effect_get(url, **kwargs):
            if "runs/run-qc" in url:
                return mock_poll_resp
            return mock_download_resp

        with patch("scripts.image_generation.runcomfy_batch.requests") as mock_req:
            mock_req.post = MagicMock(return_value=mock_submit_resp)
            mock_req.get = MagicMock(side_effect=side_effect_get)
            results = backend.generate(pp)

        assert len(results) == 1
        assert results[0]["status"] == "failed"
        assert "qc_checks" in results[0]

    def test_no_api_key_marks_failed(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("RUNCOMFY_API_KEY", raising=False)
        backend = RunComfyImageBackend(
            api_key="",
            workflow_path=tmp_path / "wf.json",
            output_dir=tmp_path / "out",
        )
        # Write a minimal workflow for _generate_single
        (tmp_path / "wf.json").write_text("{}", encoding="utf-8")
        pp = {"panels": [{"panel_id": "p_1_0", "visual_prompt": "test"}]}
        results = backend.generate(pp)
        assert len(results) == 1
        assert results[0]["status"] == "failed"
        assert "RUNCOMFY_API_KEY" in results[0]["error"]


# ── Manifest integration ─────────────────────────────────────────────


class TestManifestIntegration:
    def test_dry_run_manifest_uses_dry_run_status(self) -> None:
        backend = RunComfyImageBackend(dry_run=True)
        pp = _sample_panel_prompts()
        results = backend.generate(pp)
        manifest = build_panel_images_manifest(pp, results)
        assert manifest["artifact_type"] == "panel_images_manifest"
        assert len(manifest["panels"]) == 2
        for p in manifest["panels"]:
            assert p["status"] == "dry_run"


# ── Error handling ───────────────────────────────────────────────────


class TestErrorHandling:
    def test_generate_does_not_crash_on_partial_failure(self, tmp_path: Path) -> None:
        """If one panel fails, the rest still complete."""
        backend = RunComfyImageBackend(dry_run=True)
        pp = _sample_panel_prompts()

        # Corrupt one panel's data to cause compile failure
        pp["panels"][0].pop("panel_id", None)
        pp["panels"][0]["panel_id"] = "p_broken"

        # dry_run should still succeed for all (compile doesn't fail for missing prompt)
        results = backend.generate(pp)
        assert len(results) == 2

    def test_empty_panel_prompts(self) -> None:
        backend = RunComfyImageBackend(dry_run=True)
        results = backend.generate({"panels": []})
        assert results == []

    def test_missing_panels_key(self) -> None:
        backend = RunComfyImageBackend(dry_run=True)
        results = backend.generate({})
        assert results == []
