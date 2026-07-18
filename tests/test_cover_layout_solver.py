"""Cover layout collision solver — assertion must refuse overlapping covers."""
from __future__ import annotations

import pytest

from scripts.publish.waystream_covers import layout_solver as LS
from scripts.publish.waystream_covers import layout_zones as Z


def test_framing_rect_includes_line_above():
    glyph = (700, 1400, 900, 1500)
    framed = LS.framing_forbidden_rect(glyph, "line_above", pad=46, line_w=7)
    # Framed top must be above glyph top (includes pad + line)
    assert framed.y0 < glyph[1] / Z.H - 0.01


def test_framing_rect_includes_line_below():
    glyph = (700, 1400, 900, 1500)
    framed = LS.framing_forbidden_rect(glyph, "line_below", pad=46, line_w=7)
    assert framed.y1 > glyph[3] / Z.H + 0.01


def test_assert_zero_overlaps_passes_clear_boxes():
    a = Z.Rect(0.1, 0.1, 0.9, 0.2)
    b = Z.Rect(0.1, 0.25, 0.9, 0.35)
    report = LS.assert_zero_overlaps([
        LS.ElementBox("title", a),
        LS.ElementBox("subtitle", b),
    ])
    assert report["overlap_count"] == 0


def test_assert_zero_overlaps_raises_on_planted_overlap():
    a = Z.Rect(0.1, 0.1, 0.9, 0.3)
    b = Z.Rect(0.1, 0.2, 0.9, 0.4)
    with pytest.raises(LS.CoverLayoutCollisionError) as exc:
        LS.assert_zero_overlaps([
            LS.ElementBox("subtitle", a),
            LS.ElementBox("symbol_framed", b),
        ])
    assert ("subtitle", "symbol_framed") in exc.value.overlaps or (
        "symbol_framed", "subtitle"
    ) in exc.value.overlaps


def test_effective_framing_swaps_line_above_when_symbol_below_text():
    sub = Z.Rect(0.1, 0.74, 0.9, 0.84)
    sym = Z.Rect(0.34, 0.88, 0.66, 0.92)
    assert LS.effective_framing("line_above", sym, sub) == "line_below"
    assert LS.effective_framing("line_below", sym, sub) == "line_below"


def test_find_clear_y_skips_forbidden_band():
    zone = Z.Rect(0.08, 0.76, 0.92, 0.86)
    block_h = 80
    forbidden = (Z.Rect(0.08, 0.80, 0.92, 0.84),)
    y = LS.find_clear_y(zone, block_h, forbidden, step=4)
    assert y is not None
    box = LS.text_block_at(y, block_h, zone)
    assert not Z.rects_collide(box, forbidden)
