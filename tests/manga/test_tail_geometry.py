"""Tests for tail_geometry (mouth targeting + ellipse math)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.tail_geometry import (  # type: ignore
    _hint_to_mouth,
    mouth_from_head_bbox_fraction,
    resolve_mouth_pixel,
    tail_anchor_on_ellipse,
    tail_vector,
)


def test_hint_corners_round_trip_coordinates():
    mouth = _hint_to_mouth("top_right", 1000, 800)
    assert mouth[1] == int(800 * 0.55)
    assert mouth[0] >= 750


def test_mouth_anchor_fraction_positions():
    m = mouth_from_head_bbox_fraction(
        {"x1": 0.5, "y1": 0.1, "x2": 0.55, "y2": 0.35},
        pw=1000,
        ph=800,
        mouth_depth=0.15,
    )
    cx = int(((0.5 + 0.55) / 2) * 1000)
    assert m[0] == cx


def test_resolve_mouth_uses_explicit_anchor_before_bbox():
    line = {"speaker": "A", "mouth_anchor": {"x": 0.1, "y": 0.2}}
    panel = {
        "character_head_bboxes": {
            "A": {"x1": 0.8, "y1": 0.8, "x2": 0.95, "y2": 0.98},
        }
    }
    mx, my = resolve_mouth_pixel(
        panel_w=1000,
        panel_h=1000,
        line=line,
        panel_lettering=panel,
        panel_rgba=None,
    )
    assert mx == 100 and my == 200


def test_resolve_mouth_character_head_bbox():
    line = {"speaker": "Mina"}
    panel = {
        "character_head_bboxes": {
            "Mina": {"x1": 0.0, "y1": 0.0, "x2": 0.1, "y2": 0.3},
        }
    }
    mx, my = resolve_mouth_pixel(
        panel_w=100,
        panel_h=100,
        line=line,
        panel_lettering=panel,
        panel_rgba=None,
    )
    assert mx == 5


def test_resolve_mouth_falls_back_to_hint():
    line = {"speaker": "X", "position_hint": "bottom_left"}
    mx, my = resolve_mouth_pixel(
        panel_w=100,
        panel_h=100,
        line=line,
        panel_lettering={},
        panel_rgba=None,
    )
    approx = _hint_to_mouth("bottom_left", 100, 100)
    assert (mx, my) == approx


def test_tail_vector_unit_length():
    vx, vy = tail_vector((10.0, 10.0), (30, 10))
    assert abs(vx - 1.0) < 1e-6 and abs(vy) < 1e-6


def test_tail_anchor_on_ellipse_horizonal_ray():
    bbox = (0, 0, 40, 20)
    ax, ay = tail_anchor_on_ellipse(bbox, (1.0, 0.0))
    assert pytest.approx(ax, abs=2) == 40
    assert pytest.approx(ay, abs=1) == 10
