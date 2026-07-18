"""Tests for JLREQ-aware lettering and SFX planning."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.bubble_render_v2 import render_bubbles_onto_panel_v2  # type: ignore
from phoenix_v4.manga.chapter.jlreq_lettering import (  # type: ignore
    plan_dialogue_lettering,
    plan_sfx_layout,
    render_jlreq_text_block,
)

PIL = pytest.importorskip("PIL")
from PIL import Image, ImageDraw, ImageFont  # type: ignore  # noqa: E402


def _panel(tmp_path: Path, name: str = "panel.png") -> Path:
    path = tmp_path / name
    Image.new("RGB", (260, 220), color=(245, 245, 240)).save(path)
    return path


def test_plan_dialogue_marks_vertical_japanese_runtime():
    plan = plan_dialogue_lettering(
        "ゴー!",
        locale="ja_JP",
        vertical_kanji=True,
    )
    assert plan["writing_mode"] == "vertical_rl"
    assert any(row["orientation"] == "rotate90" for row in plan["glyph_plan"])


def test_plan_dialogue_labels_vertical_furigana_as_partial():
    plan = plan_dialogue_lettering(
        "東京",
        locale="ja_JP",
        vertical_kanji=True,
        furigana=[{"base": "東京", "reading": "とうきょう"}],
    )
    assert plan["runtime_status"] == "partial_vertical_furigana_deferred"
    assert plan["writing_mode"] == "horizontal_tb"


def test_plan_sfx_avoids_occupied_bubble_regions():
    plan = plan_sfx_layout(
        "ドン",
        locale="ja_JP",
        panel_size=(300, 200),
        occupied_bboxes=[[200, 10, 295, 120], [30, 110, 120, 190]],
        reading_direction="rtl",
    )
    assert plan["occupied_overlap_area"] == 0
    assert plan["bbox"][0] >= 0
    assert plan["bbox"][2] <= 300


def test_render_jlreq_text_block_draws_nonempty_pixels():
    image = Image.new("RGBA", (120, 140), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    plan = plan_dialogue_lettering("ゴー", locale="ja_JP", vertical_kanji=True)
    render_jlreq_text_block(
        image,
        draw,
        "ゴー",
        90,
        10,
        font=font,
        locale="ja_JP",
        fill=(0, 0, 0, 255),
        max_column_height=100,
        plan=plan,
    )
    assert image.getbbox() is not None


def test_bubble_render_v2_records_jlreq_and_sfx_plan(tmp_path: Path):
    panel = _panel(tmp_path, "jp.png")
    layout = render_bubbles_onto_panel_v2(
        panel,
        [
            {
                "speaker": "A",
                "text_by_locale": {"ja_JP": "静かだ"},
                "vertical_kanji": True,
                "bubble_style": "round_normal",
            }
        ],
        sfx=["ドン"],
        narrator_caption=None,
        out_path=tmp_path / "out.png",
        locale="ja_JP",
    )
    dialogue = next(row for row in layout["bubbles"] if row.get("type") == "dialogue")
    sfx = next(row for row in layout["bubbles"] if row.get("type") == "sfx")
    assert dialogue["jlreq_plan"]["writing_mode"] == "vertical_rl"
    assert "placement_plan" in sfx
    assert sfx["placement_plan"]["occupied_overlap_area"] == 0

