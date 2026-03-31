"""Structural validation of VCE filter_complex strings (no FFmpeg subprocess)."""
from __future__ import annotations

from scripts.video.run_layer_compositor import (  # noqa: E402
    run_compositor,
)
from scripts.video.run_animation_engine import run_animation  # noqa: E402
from scripts.video.vce_ffmpeg_builders import validate_filter_complex_structure  # noqa: E402


def test_compositor_filter_chains_validate():
    resolved = {"plan_id": "p1", "resolved": {"s1": {"asset_id": "a1"}}}
    shot_plan = {"plan_id": "p1", "shots": [{"shot_id": "s1", "segment_id": "x"}]}
    for fmt in ("short", "mid"):
        doc = run_compositor(resolved, shot_plan, fmt)
        for sh in doc["shots"]:
            ok, _reason = validate_filter_complex_structure(sh["filter_complex"])
            assert ok, sh["filter_complex"][:200]
            assert "overlay" in sh["filter_complex"]
            assert "[out_" in sh["filter_complex"]


def test_animation_zoompan_quotes_balanced():
    comp = {"plan_id": "p1", "shots": []}
    sp = {"plan_id": "p1", "shots": [{"shot_id": "s1"}], "content_type": "therapeutic"}
    tl = {
        "plan_id": "p1",
        "duration_s": 30,
        "fps": 24,
        "resolution": {"width": 1920, "height": 1080},
        "clips": [{"shot_id": "s1", "start_time_s": 0, "end_time_s": 8}],
    }
    doc = run_animation(comp, sp, tl, "mid")
    assert doc["shots"]
    zb = doc["shots"][0].get("ffmpeg_motion") or {}
    if zb.get("zoompan"):
        ok, reason = validate_filter_complex_structure(zb["zoompan"])
        assert ok, reason
