"""Tests for the manga spread/page layout solver."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.page_frame import render_framed_page  # type: ignore
from phoenix_v4.manga.chapter.spread_layout_solver import (  # type: ignore
    solve_page_layout,
)

PIL = pytest.importorskip("PIL")
from PIL import Image  # type: ignore  # noqa: E402


def _solid(w: int, h: int, rgb: tuple[int, int, int]) -> Image.Image:
    return Image.new("RGB", (w, h), rgb)


def test_solver_builds_real_facing_page_spread_for_two_panels():
    decision = solve_page_layout(
        {
            "page_type": "double_spread",
            "reading_direction": "rtl",
            "panels": [{"panel_id": "p1"}, {"panel_id": "p2"}],
        },
        genre="shonen",
    )
    assert decision["resolved_page_type"] == "double_spread"
    assert decision["spread"] is True
    assert decision["panel_capacity"] == 2
    right = decision["cells"][0]
    left = decision["cells"][1]
    assert right[0] > 0.5
    assert left[0] == pytest.approx(0.0)
    assert right[2] < 0.5
    assert left[2] < 0.5
    assert left[0] + left[2] < right[0]
    assert decision["validation"]["valid"] is True


def test_solver_downgrades_spread_on_vertical_scroll():
    decision = solve_page_layout(
        {
            "page_type": "double_spread",
            "reading_direction": "vertical_scroll",
            "panels": [{"panel_id": "p1"}, {"panel_id": "p2"}],
        },
        genre="shonen",
        format_id="webtoon",
    )
    assert decision["resolved_page_type"] == "standard"
    assert decision["spread"] is False
    assert decision["issues"][0]["rule_id"] == "requested_page_type_downgrade"


def test_solver_promotes_hero_page_to_spread_when_allowed():
    decision = solve_page_layout(
        {
            "page_type": "standard",
            "reading_direction": "rtl",
            "panels": [
                {"panel_id": "p1", "panel_function": "climactic_spread", "aspect_hint": "wide_16_9"},
                {"panel_id": "p2", "aspect_hint": "portrait_4_5"},
                {"panel_id": "p3", "aspect_hint": "portrait_4_5"},
            ],
        },
        genre="shonen",
    )
    assert decision["resolved_page_type"] == "double_spread"
    assert decision["spread"] is True
    assert decision["cells"][0][2] == pytest.approx(1.0)


def test_render_framed_page_uses_solver_for_spreads():
    right_first = _solid(700, 1000, (255, 0, 0))
    left_second = _solid(700, 1000, (0, 0, 255))
    page = render_framed_page(
        [right_first, left_second],
        page_type="double_spread",
        genre="shonen",
        reading_direction="rtl",
    )
    px = page.convert("RGB").load()
    assert px[int(page.width * 0.75), int(page.height * 0.5)] == (255, 0, 0)
    assert px[int(page.width * 0.25), int(page.height * 0.5)] == (0, 0, 255)


def test_solver_reserves_center_gutter_for_non_cross_spine_panels():
    decision = solve_page_layout(
        {
            "page_type": "double_spread",
            "reading_direction": "rtl",
            "panels": [{"panel_id": "p1"}, {"panel_id": "p2"}],
        },
        genre="shonen",
    )
    left = decision["cells"][1]
    right = decision["cells"][0]
    gutter_norm = right[0] - (left[0] + left[2])
    assert gutter_norm > 0.0
