"""Tests for furigana_renderer (ruby layout + dry-run)."""
from __future__ import annotations

import copy as _copy
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.furigana_renderer import (  # type: ignore
    normalize_furigana_segments,
    render_furigana_line,
)


class _DummyDraw:
    def textbbox(self, xy, text, font=None):
        # fixed cell per char for deterministic layout
        w = max(1, len(text) * 12)
        h = 16
        return (xy[0], xy[1], xy[0] + w, xy[1] + h)


def test_normalize_furigana_filters_blank():
    line = {"furigana": [{"base": "  ", "reading": " x "}, {"base": "東", "reading": "ひがし"}]}
    seg = normalize_furigana_segments(line)
    assert len(seg) == 1 and seg[0]["base"] == "東"


def test_normalize_furigana_empty_when_absent():
    assert normalize_furigana_segments({}) == []
    assert normalize_furigana_segments({"furigana": "oops"}) == []


def test_render_furigana_line_dry_run_no_draw_calls_but_sizes():
    draw = _DummyDraw()

    class _F:
        pass

    f = _F()
    segs = [{"base": "東", "reading": "ひがし"}, {"base": "京", "reading": "きょう"}]
    q = _copy.deepcopy(segs)
    w, h = render_furigana_line(
        draw,
        "東京へ",
        segs,
        0,
        0,
        base_font=f,
        ruby_font=f,
        dry_run=True,
        segment_queue=q,
    )
    assert w > 0 and h > 0
    assert q == [], "segment_queue is consumed like a real render walk"


def test_render_furigana_line_interleaves_literals():
    draw = _DummyDraw()

    class _F:
        pass

    f = _F()
    seg = [{"base": "漢字", "reading": "かんじ"}]
    queue = _copy.deepcopy(seg)
    w, _ = render_furigana_line(
        draw,
        "a漢字b",
        seg,
        0,
        0,
        base_font=f,
        ruby_font=f,
        dry_run=True,
        segment_queue=queue,
    )
    assert queue == []
    assert w > 36
