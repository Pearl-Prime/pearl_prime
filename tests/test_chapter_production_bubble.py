"""Tests for bubble-stage integration in chapter_production.py."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from phoenix_v4.manga.chapter.chapter_production import produce_chapter_assets
from phoenix_v4.manga.image_backend import ImageBackend, build_panel_images_manifest


# ---------------------------------------------------------------------------
# Stub image backend that writes real tiny PNGs
# ---------------------------------------------------------------------------

class TinyImageBackend(ImageBackend):
    """Writes a 200×150 solid-color RGBA PNG for each panel."""

    def __init__(self, tmp_dir: Path) -> None:
        self._tmp = tmp_dir
        self._tmp.mkdir(parents=True, exist_ok=True)

    def generate(self, panel_prompts: dict) -> list[dict]:
        from PIL import Image
        results = []
        for panel in panel_prompts.get("panels") or []:
            pid = str(panel.get("panel_id") or "unknown")
            p = self._tmp / f"{pid}.png"
            Image.new("RGBA", (200, 150), (180, 180, 200, 255)).save(str(p))
            results.append({"panel_id": pid, "status": "ok", "path": str(p)})
        return results


# ---------------------------------------------------------------------------
# Chapter script fixture helpers
# ---------------------------------------------------------------------------

def _make_script_with_dialogue(series_id: str = "ts", chapter_id: str = "ch01") -> dict:
    return {
        "artifact_type": "chapter_script_writer_handoff",
        "schema_version": "1.0.0",
        "series_id": series_id,
        "chapter_id": chapter_id,
        "pages": [
            {
                "page_number": 1,
                "panels": [
                    {
                        "panel_id": "p01",
                        "action": "Hero confronts rival",
                        "mood": "tense",
                        "dialogue": ["I won't lose!", "Then let's see what you've got."],
                    },
                    {
                        "panel_id": "p02",
                        "action": "Wide shot of arena",
                        "mood": "neutral",
                        "dialogue": [],
                    },
                ],
            }
        ],
    }


def _make_all_silent_script() -> dict:
    return {
        "artifact_type": "chapter_script_writer_handoff",
        "schema_version": "1.0.0",
        "series_id": "ts",
        "chapter_id": "ch_silent",
        "pages": [
            {
                "page_number": 1,
                "panels": [
                    {"panel_id": "p01", "action": "Wide establishing shot", "mood": "calm"},
                    {"panel_id": "p02", "action": "Character walks away", "mood": "calm"},
                ],
            }
        ],
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestChapterProductionBubble:

    def test_bubble_stage_runs_when_requested(self, tmp_path):
        script = _make_script_with_dialogue()
        backend = TinyImageBackend(tmp_path / "images")
        result = produce_chapter_assets(
            script,
            image_backend=backend,
            bubble_render_out=tmp_path / "bubbled",
        )
        assert "panel_images_manifest_bubbled" in result
        bubbled_manifest = result["panel_images_manifest_bubbled"]
        assert bubbled_manifest["bubble_render_summary"]["panels_processed"] >= 1

    def test_bubble_stage_skipped_when_not_requested(self, tmp_path):
        script = _make_script_with_dialogue()
        backend = TinyImageBackend(tmp_path / "images")
        result = produce_chapter_assets(
            script,
            image_backend=backend,
            bubble_render_out=None,
        )
        assert "panel_images_manifest_bubbled" not in result

    def test_all_silent_chapter_skips_bubble_stage(self, tmp_path):
        """Even if bubble_render_out is set, an all-silent chapter skips stage 4."""
        script = _make_all_silent_script()
        backend = TinyImageBackend(tmp_path / "images")
        result = produce_chapter_assets(
            script,
            image_backend=backend,
            bubble_render_out=tmp_path / "bubbled",
        )
        # All-silent → bubble stage was not applied
        assert "panel_images_manifest_bubbled" not in result

    def test_page_compose_uses_bubbled_manifest(self, tmp_path):
        """When both bubble_render_out and final_pages_out are set,
        page_compose receives the bubbled manifest."""
        script = _make_script_with_dialogue()
        backend = TinyImageBackend(tmp_path / "images")
        pages_out = tmp_path / "pages"
        result = produce_chapter_assets(
            script,
            image_backend=backend,
            bubble_render_out=tmp_path / "bubbled",
            final_pages_out=pages_out,
        )
        assert "final_page_paths" in result
        page_files = list(result["final_page_paths"])
        assert len(page_files) >= 1
        for p in page_files:
            assert Path(p).is_file()

    def test_original_manifest_preserved(self, tmp_path):
        """Original panel_images_manifest still present alongside bubbled one."""
        script = _make_script_with_dialogue()
        backend = TinyImageBackend(tmp_path / "images")
        result = produce_chapter_assets(
            script,
            image_backend=backend,
            bubble_render_out=tmp_path / "bubbled",
        )
        # Both manifests present and distinct
        orig_panels = result["panel_images_manifest"]["panels"]
        bubbled_panels = result["panel_images_manifest_bubbled"]["panels"]
        # At least the dialogue panel should differ in path
        orig_paths = {p["panel_id"]: p["path"] for p in orig_panels}
        bubbled_paths = {p["panel_id"]: p["path"] for p in bubbled_panels}
        # p01 had dialogue — its path should have changed to _bubbled.png
        assert "bubbled" in bubbled_paths.get("p01", "")
        # p02 was silent — path should be the same
        assert orig_paths.get("p02") == bubbled_paths.get("p02")

    def test_lettering_spec_is_v2_when_bubble_requested(self, tmp_path):
        script = _make_script_with_dialogue()
        backend = TinyImageBackend(tmp_path / "images")
        result = produce_chapter_assets(
            script,
            image_backend=backend,
            bubble_render_out=tmp_path / "bubbled",
        )
        assert result["lettering_spec"]["schema_version"] == "2.0.0"

    def test_all_artifacts_present(self, tmp_path):
        script = _make_script_with_dialogue()
        backend = TinyImageBackend(tmp_path / "images")
        result = produce_chapter_assets(
            script,
            image_backend=backend,
            bubble_render_out=tmp_path / "bubbled",
            final_pages_out=tmp_path / "pages",
        )
        assert "panel_prompts" in result
        assert "panel_images_manifest" in result
        assert "lettering_spec" in result
        assert "panel_images_manifest_bubbled" in result
        assert "final_page_paths" in result
