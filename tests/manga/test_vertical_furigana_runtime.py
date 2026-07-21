from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.vertical_furigana import (
    VerticalFuriganaError,
    plan_vertical_furigana,
    render_vertical_furigana,
    resolve_ruby_spans,
)


def test_japanese_vertical_furigana_plan_is_ready():
    plan = plan_vertical_furigana(
        "東京へ",
        [{"base": "東京", "reading": "とうきょう"}],
    )
    assert plan["writing_mode"] == "vertical_rl"
    assert plan["runtime_status"] == "ready_vertical_furigana"
    assert plan["spans"][0]["start"] == 0
    assert plan["spans"][0]["end"] == 2


def test_furigana_base_mismatch_fails_closed():
    with pytest.raises(VerticalFuriganaError, match="not found"):
        resolve_ruby_spans("大阪", [{"base": "東京", "reading": "とうきょう"}])


def test_vertical_furigana_renderer_emits_base_and_ruby_pixels():
    image = Image.new("RGBA", (220, 280), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    plan = plan_vertical_furigana("TOKYO", [{"base": "TOKYO", "reading": "tokyo"}])
    result = render_vertical_furigana(
        image,
        draw,
        "TOKYO",
        100,
        20,
        base_font=font,
        ruby_font=font,
        plan=plan,
    )
    assert result["runtime_status"] == "rendered_vertical_furigana"
    assert result["ruby_span_count"] == 1
    assert image.getbbox() is not None
