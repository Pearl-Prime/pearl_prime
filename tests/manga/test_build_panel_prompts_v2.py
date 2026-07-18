"""End-to-end test for V2 build_panel_prompts_v2.py — Phase A.2 caller."""
from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import yaml


def test_build_panel_prompts_v2_end_to_end(tmp_path):
    """From chapter_script.yaml + character_design YAML → panel_prompts.json
    in the brand-2 / queue_panel_renders.py schema."""
    repo_root = Path(__file__).resolve().parents[2]

    # Chapter script in brand-2 schema (chapters {ch_id: panels []})
    chapter_script = {
        "brand": "test_brand",
        "topic": "healing",
        "title": {"en-US": "Test Chapter"},
        "chapters": {
            "ch01": {
                "title": "ch01 title",
                "panels": [
                    {
                        "panel_id": "ch01_p01",
                        "scene": "A woman at a kitchen table in muted morning light.",
                        "narration": {"en-US": "She has been awake since five."},
                        "dialogue": [],
                    },
                    {
                        "panel_id": "ch01_p02",
                        "scene": "Window view of empty street.",
                    },
                ],
            },
            "ch02": {
                "panels": [
                    {
                        "panel_id": "ch02_p01",
                        "scene": "She walks to the bus stop.",
                    },
                ],
            },
        },
    }
    cs_path = tmp_path / "ep_001.yaml"
    cs_path.write_text(yaml.safe_dump(chapter_script, sort_keys=False))

    # Series YAML carrying a character_design block
    series_yaml = {
        "series_id": "test_series",
        "brand_id": "test_brand",
        "market_demo": "josei",
        "genre_family": "healing",
        "character_design": {
            "axes": {
                "face_shape": {"value": "heart_shaped", "lockout": "yes"},
                "eye_geometry": {
                    "size": "small", "shape": "almond", "lid_fold": "single",
                    "eyelash_density": "minimal", "lockout": "yes",
                },
                "hair": {
                    "length": "shoulder", "color_signal": "dark_brown",
                    "texture": "straight", "lockout": "yes",
                },
                "color_signal": {"value": "muted_brown", "lockout": "yes"},
                "wardrobe_register": {"value": "everyday_casual", "lockout": "yes"},
                "age_signaling": {"value": "late_30s", "lockout": "yes"},
                "accessories": {"value": "round_glasses", "lockout": "yes"},
                "mouth_jaw": {"lip_shape": "thin_upper_full_lower", "lockout": "yes"},
                "nose_construction": {"value": "straight_pointed", "lockout": "yes"},
                "skin_treatment": {"value": "clean", "lockout": "no"},
                "build": {"value": "average", "lockout": "no"},
                "posture_default": {"value": "neutral_relaxed", "lockout": "no"},
            },
        },
    }
    series_path = tmp_path / "test_series.yaml"
    series_path.write_text(yaml.safe_dump(series_yaml, sort_keys=False))

    out_path = tmp_path / "ep_001.panel_prompts.json"

    cmd = [
        sys.executable,
        str(repo_root / "scripts" / "manga" / "build_panel_prompts_v2.py"),
        "--chapter-script", str(cs_path),
        "--character-design", str(series_path),
        "--base-model", "flux_schnell",
        "--width", "1080",
        "--height", "1920",
        "--output", str(out_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(repo_root))
    assert res.returncode == 0, res.stderr

    data = json.loads(out_path.read_text())
    assert data["schema_version"] == "1.0"
    assert data["brand"] == "test_brand"
    assert data["model"] == "flux_schnell"
    assert "1080x1920" in data["render_target"]
    assert len(data["prompts"]) == 3
    panel_ids = [p["panel_id"] for p in data["prompts"]]
    assert panel_ids == ["ch01_p01", "ch01_p02", "ch02_p01"]
    # Each panel has the brand-2 prompt schema keys
    for p in data["prompts"]:
        for key in ("panel_id", "prompt", "negative_prompt", "model", "width", "height", "char_count"):
            assert key in p
    # Character tokens present in first panel's prompt
    first_prompt = data["prompts"][0]["prompt"]
    assert "kitchen table" in first_prompt
    assert "small" in first_prompt  # eye size
    # Negative prompt has universal floors
    first_neg = data["prompts"][0]["negative_prompt"]
    assert "low quality" in first_neg or "blurry" in first_neg
