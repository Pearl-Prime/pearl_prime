"""Tests for V2 Phase B.7 queue_panel_renders.py reference-image extension.

Exercises only the new --workflow-path + --reference-image flag wiring; the
ComfyUI submission path is covered by the brand-2 V1 ship + reference_sheet
_generator tests. We invoke the script in --dry-run mode so no ComfyUI URL
is needed.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _make_panel_prompts(tmp_path: Path) -> Path:
    pp = {
        "schema_version": "1.0",
        "brand": "test_brand",
        "episode": "ep_001",
        "model": "flux-schnell-fp8",
        "render_target": "1080x1920",
        "prompts": [
            {
                "panel_id": "ch01_p01",
                "prompt": "test scene",
                "negative_prompt": "low quality",
                "model": "flux-schnell-fp8",
                "width": 1080,
                "height": 1920,
                "char_count": 10,
            }
        ],
    }
    p = tmp_path / "ep_001.panel_prompts.json"
    p.write_text(json.dumps(pp))
    return p


def test_dry_run_works_with_default_workflow(tmp_path):
    """Back-compat: no --workflow-path / --reference-image → existing path."""
    repo = Path(__file__).resolve().parents[2]
    pp = _make_panel_prompts(tmp_path)
    out_dir = tmp_path / "out"
    res = subprocess.run(
        [sys.executable, str(repo / "scripts" / "manga" / "queue_panel_renders.py"),
         "--panel-prompts", str(pp),
         "--output-dir", str(out_dir),
         "--dry-run"],
        capture_output=True, text=True, cwd=str(repo),
    )
    assert res.returncode == 0, res.stderr
    assert "[dry] ch01_p01" in res.stderr


def test_workflow_path_override_accepted(tmp_path):
    """--workflow-path is parsed; dry-run doesn't require the file to be loaded."""
    repo = Path(__file__).resolve().parents[2]
    pp = _make_panel_prompts(tmp_path)
    out_dir = tmp_path / "out"

    res = subprocess.run(
        [sys.executable, str(repo / "scripts" / "manga" / "queue_panel_renders.py"),
         "--panel-prompts", str(pp),
         "--output-dir", str(out_dir),
         "--workflow-path", "scripts/image_generation/comfyui_workflows/flux_txt2img_manga_pulid.json",
         "--dry-run"],
        capture_output=True, text=True, cwd=str(repo),
    )
    assert res.returncode == 0, res.stderr


def test_reference_image_auto_selects_pulid_variant_in_help(tmp_path):
    """--help should advertise --reference-image + --workflow-path flags."""
    repo = Path(__file__).resolve().parents[2]
    res = subprocess.run(
        [sys.executable, str(repo / "scripts" / "manga" / "queue_panel_renders.py"), "--help"],
        capture_output=True, text=True, cwd=str(repo),
    )
    assert res.returncode == 0
    assert "--reference-image" in res.stdout
    assert "--workflow-path" in res.stdout
    assert "PuLID" in res.stdout or "pulid" in res.stdout
