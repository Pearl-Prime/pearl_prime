"""Color temperature arc keyframe generation (no FFmpeg)."""
from __future__ import annotations

import pytest

from scripts.video.vce_ffmpeg_builders import (  # noqa: E402
    color_temp_arc_anchors,
    interpolate_colorbalance_at_pct,
    parse_colorbalance_args,
    per_second_colorbalance_keyframes,
    write_colorbalance_sendcmd_file,
)


def _sample_arc():
    return {
        "HOOK": {"colorbalance": "rs=0.1:gs=0.0:bs=-0.1"},
        "BUILD": {"colorbalance": "rs=0.0:gs=0.0:bs=0.0"},
        "PEAK": {"colorbalance": "rs=-0.05:gs=0.0:bs=0.05"},
        "RELEASE": {"colorbalance": "rs=0.02:gs=0.02:bs=0.0"},
        "RESOLVE": {"colorbalance": "rs=0.08:gs=0.03:bs=-0.05"},
    }


def test_parse_colorbalance():
    d = parse_colorbalance_args("rs=0.1:gs=-0.02:bs=0.0")
    assert d["rs"] == pytest.approx(0.1)
    assert d["gs"] == pytest.approx(-0.02)


def test_interpolation_piecewise():
    anchors = color_temp_arc_anchors(_sample_arc())
    assert anchors
    mid_hook = interpolate_colorbalance_at_pct(7.5, anchors)
    assert mid_hook["rs"] > 0.0
    neutral = interpolate_colorbalance_at_pct(40.0, anchors)
    assert neutral["rs"] == pytest.approx(0.0, abs=0.05)


def test_write_sendcmd_file(tmp_path):
    anchors = color_temp_arc_anchors(_sample_arc())
    kf = per_second_colorbalance_keyframes(3.0, 0.0, 60.0, anchors)
    p = write_colorbalance_sendcmd_file(kf, tmp_path / "arc.cmd")
    text = p.read_text(encoding="utf-8")
    assert "colorbalance" in text
    assert "0.0 colorbalance" in text or "1.0 colorbalance" in text
