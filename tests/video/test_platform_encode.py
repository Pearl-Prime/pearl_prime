"""Platform FFmpeg encode argv lists (no subprocess)."""
from __future__ import annotations

from scripts.video.run_platform_adapter import run_platform_adapter  # noqa: E402
from scripts.video.vce_ffmpeg_builders import (  # noqa: E402
    is_list_of_str,
    platform_duration_cap_argv,
    platform_video_audio_argv,
    quality_tuning,
    webp_panel_argv_template,
)


def test_quality_tuning_monotonic():
    d_crf, _ = quality_tuning("draft")
    s_crf, _ = quality_tuning("standard")
    h_crf, _ = quality_tuning("high")
    assert d_crf > s_crf > h_crf


def test_platform_matrices_shapes():
    for plat, sub in [
        ("youtube", "libx264"),
        ("youtube_shorts", "libx264"),
        ("tiktok", "libx264"),
        ("instagram_reels", "libx264"),
        ("bilibili", "libx264"),
        ("douyin", "libx264"),
    ]:
        v, a = platform_video_audio_argv(plat, 23, "medium")
        assert is_list_of_str(v) and is_list_of_str(a)
        assert sub in v
        assert "aac" in a
        assert "48000" in a or "-ar" in a
    assert platform_video_audio_argv("webtoon", 21, "medium") == ([], [])


def test_duration_caps():
    assert "-t" in platform_duration_cap_argv("youtube_shorts")
    assert platform_duration_cap_argv("youtube") == []


def test_webtoon_template():
    t = webp_panel_argv_template()
    assert t[0] == "cwebp" and "{in_path}" in t


def test_platform_adapter_has_ffmpeg_block():
    tl = {"plan_id": "p1", "duration_s": 60, "resolution": {"width": 1920, "height": 1080}}
    dist = {"video_id": "v1", "plan_id": "p1", "title": "t", "description": "", "tags": []}
    ani = {"shots": [{"shot_id": "s1"}]}
    doc = run_platform_adapter(tl, dist, ani, ["youtube", "tiktok", "youtube_shorts", "webtoon"])
    assert len(doc["variants"]) == 4
    for v in doc["variants"]:
        assert "ffmpeg" in v
        assert is_list_of_str(v["ffmpeg"]["video_encode_argv"])
        if v["platform"] != "webtoon":
            assert v["ffmpeg"]["video_encode_argv"]
        assert "caption_delivery" in v
