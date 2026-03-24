"""One integration path: script → prompts → replay images → manifest → lettering → page PNG."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from phoenix_v4.manga.chapter.chapter_production import produce_chapter_assets
from phoenix_v4.manga.image_backend import FixtureReplayImageBackend
from phoenix_v4.manga.models.validation import validate_instance

pytest.importorskip("PIL")

# Minimal 1x1 RGBA PNG (same as test_manga_chapter_visual)
_MIN_PNG = bytes(
    [
        0x89,
        0x50,
        0x4E,
        0x47,
        0x0D,
        0x0A,
        0x1A,
        0x0A,
        0x00,
        0x00,
        0x00,
        0x0D,
        0x49,
        0x48,
        0x44,
        0x52,
        0x00,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x01,
        0x08,
        0x06,
        0x00,
        0x00,
        0x00,
        0x1F,
        0x15,
        0xC4,
        0x89,
        0x00,
        0x00,
        0x00,
        0x0A,
        0x49,
        0x44,
        0x41,
        0x54,
        0x78,
        0x9C,
        0x63,
        0x00,
        0x01,
        0x00,
        0x00,
        0x05,
        0x00,
        0x01,
        0x0D,
        0x0A,
        0x2D,
        0xB4,
        0x00,
        0x00,
        0x00,
        0x00,
        0x49,
        0x45,
        0x4E,
        0x44,
        0xAE,
        0x42,
        0x60,
        0x82,
    ]
)


def test_chapter_production_replay_to_page_png(tmp_path: Path) -> None:
    replay_dir = tmp_path / "replay"
    replay_dir.mkdir()
    (replay_dir / "p_a.png").write_bytes(_MIN_PNG)
    (replay_dir / "p_b.png").write_bytes(_MIN_PNG)
    map_path = replay_dir / "map.json"
    map_path.write_text(
        json.dumps({"p_a": "p_a.png", "p_b": "p_b.png"}),
        encoding="utf-8",
    )

    chapter_script = {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_script_writer_handoff",
        "series_id": "int_series",
        "chapter_id": "ch_int",
        "pages": [
            {
                "page_number": 1,
                "page_type": "standard",
                "panels": [
                    {
                        "panel_id": "p_a",
                        "dialogue": ["Line"],
                        "action": "left",
                        "camera": "wide",
                        "mood": "neutral",
                    },
                    {
                        "panel_id": "p_b",
                        "dialogue": [],
                        "action": "right",
                        "camera": "wide",
                        "mood": "neutral",
                    },
                ],
            }
        ],
    }

    backend = FixtureReplayImageBackend.from_json_file(map_path)
    out_pages = tmp_path / "final_page_composite"
    bundle = produce_chapter_assets(
        chapter_script,
        image_backend=backend,
        config_hash="integration",
        final_pages_out=out_pages,
    )

    validate_instance(bundle["panel_prompts"], "panel_prompts")
    validate_instance(bundle["panel_images_manifest"], "panel_images_manifest")
    validate_instance(bundle["lettering_spec"], "lettering_spec")

    assert bundle["lettering_spec"]["lettering_panels"][0]["silence_confirmed"] is False
    assert bundle["lettering_spec"]["lettering_panels"][1]["silence_confirmed"] is True

    paths = bundle["final_page_paths"]
    assert len(paths) == 1
    page_png = paths[0]
    assert page_png.is_file()
    from PIL import Image

    with Image.open(page_png) as im:
        assert im.size == (2, 1)
