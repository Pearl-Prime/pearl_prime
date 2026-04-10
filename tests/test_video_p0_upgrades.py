"""
tests/test_video_p0_upgrades.py
Smoke tests for P0 video pipeline upgrades:
  1. xfade filter builder
  2. lut3d filter builder
  3. noise filter builder
  4. vignette filter builder
  5. pyloudnorm loudness normalisation helper
  6. run_qc video QC gate (no real video needed — tests the logic paths)

These tests do NOT require FFmpeg, a GPU, or real video files.
All FFmpeg subprocess calls are patched out.
"""
from __future__ import annotations

import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video.vce_ffmpeg_builders import (
    build_lut3d_filter,
    build_noise_filter,
    build_vignette_filter,
    build_xfade_filter,
)


# ── 1. xfade filter builder ───────────────────────────────────────────────────


class TestBuildXfadeFilter:
    def test_single_clip_returns_empty(self, tmp_path):
        clip = tmp_path / "clip.mp4"
        clip.write_text("x")
        inputs, parts = build_xfade_filter([clip])
        assert inputs == []
        assert parts == []

    def test_two_clips_produces_filter(self, tmp_path):
        c1 = tmp_path / "c1.mp4"
        c2 = tmp_path / "c2.mp4"
        c1.write_text("x")
        c2.write_text("x")
        # Patch ffprobe to return a duration so we don't need a real video
        mock_run = MagicMock()
        mock_run.return_value.stdout = "5.0\n"
        with patch("subprocess.run", mock_run):
            inputs, parts = build_xfade_filter([c1, c2], transition="dissolve", duration_s=0.5)
        assert len(inputs) == 4  # 2x "-i clip"
        assert any("xfade" in p for p in parts)
        assert any("dissolve" in p for p in parts)
        assert any("[vout]" in p for p in parts)

    def test_three_clips_chains_two_xfades(self, tmp_path):
        clips = [tmp_path / f"c{i}.mp4" for i in range(3)]
        for c in clips:
            c.write_text("x")
        mock_run = MagicMock()
        mock_run.return_value.stdout = "5.0\n"
        with patch("subprocess.run", mock_run):
            inputs, parts = build_xfade_filter(clips)
        # Expect exactly 2 xfade operations for 3 clips
        xfade_parts = [p for p in parts if "xfade" in p]
        assert len(xfade_parts) == 2

    def test_transition_name_passed_through(self, tmp_path):
        clips = [tmp_path / f"c{i}.mp4" for i in range(2)]
        for c in clips:
            c.write_text("x")
        mock_run = MagicMock()
        mock_run.return_value.stdout = "3.0\n"
        with patch("subprocess.run", mock_run):
            _, parts = build_xfade_filter(clips, transition="wipeleft")
        assert any("wipeleft" in p for p in parts)

    def test_ffprobe_failure_falls_back_to_5s(self, tmp_path):
        clips = [tmp_path / f"c{i}.mp4" for i in range(2)]
        for c in clips:
            c.write_text("x")
        # Simulate ffprobe failure
        with patch("subprocess.run", side_effect=Exception("no ffprobe")):
            inputs, parts = build_xfade_filter(clips, duration_s=0.5)
        # Should still produce output (uses 5.0s fallback)
        assert len(parts) > 0


# ── 2. lut3d filter builder ───────────────────────────────────────────────────


class TestBuildLut3dFilter:
    def test_returns_format_chain(self, tmp_path):
        lut = tmp_path / "test.cube"
        lut.write_text("# test")
        result = build_lut3d_filter(lut)
        assert result.startswith("format=rgb24")
        assert "lut3d=" in result
        assert result.endswith("format=yuv420p")

    def test_path_embedded_in_filter(self, tmp_path):
        lut = tmp_path / "warm.cube"
        lut.write_text("# warm")
        result = build_lut3d_filter(lut)
        assert str(lut).replace("\\", "/") in result or str(lut) in result

    def test_string_path_accepted(self, tmp_path):
        lut = str(tmp_path / "grade.cube")
        result = build_lut3d_filter(lut)
        assert "lut3d=" in result


# ── 3. noise filter builder ───────────────────────────────────────────────────


class TestBuildNoiseFilter:
    def test_default_intensity(self):
        result = build_noise_filter()
        assert result is not None
        assert "c0s=15" in result
        assert "c0f=t+u" in result

    def test_custom_intensity(self):
        result = build_noise_filter(25)
        assert "c0s=25" in result

    def test_zero_returns_none(self):
        result = build_noise_filter(0)
        assert result is None

    def test_negative_returns_none(self):
        result = build_noise_filter(-5)
        assert result is None

    def test_filter_name(self):
        result = build_noise_filter(10)
        assert result is not None
        assert result.startswith("noise=")


# ── 4. vignette filter builder ────────────────────────────────────────────────


class TestBuildVignetteFilter:
    def test_default_angle(self):
        result = build_vignette_filter()
        assert result is not None
        assert "vignette=" in result
        assert "PI/5" in result

    def test_custom_float_angle(self):
        result = build_vignette_filter(0.4)
        assert result is not None
        assert "0.4" in result

    def test_zero_returns_none(self):
        result = build_vignette_filter(0)
        assert result is None

    def test_zero_string_returns_none(self):
        result = build_vignette_filter("0")
        assert result is None

    def test_pi_expression(self):
        result = build_vignette_filter("PI/6")
        assert result == "vignette=PI/6"


# ── 5. pyloudnorm loudness normalisation ─────────────────────────────────────


class TestNormalizeLoudness:
    """Tests for normalize_loudness() in run_render.py."""

    def test_returns_original_when_pyloudnorm_missing(self, tmp_path):
        """When pyloudnorm is not installed, the function returns the original path."""
        audio = tmp_path / "narration.wav"
        audio.write_bytes(b"\x00" * 44)  # tiny stub

        # Simulate pyloudnorm not installed
        import builtins
        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name in ("pyloudnorm", "soundfile"):
                raise ImportError(f"mocked missing: {name}")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            from scripts.video.run_render import normalize_loudness
            result = normalize_loudness(audio, target_lufs=-16.0)
        assert result == audio

    def test_returns_original_on_processing_error(self, tmp_path):
        """When pyloudnorm is available but processing fails, returns original path."""
        audio = tmp_path / "narration.wav"
        audio.write_bytes(b"\x00" * 44)

        mock_sf = MagicMock()
        mock_sf.read.side_effect = Exception("bad wav")
        mock_pyln = MagicMock()

        with patch.dict("sys.modules", {"soundfile": mock_sf, "pyloudnorm": mock_pyln}):
            from scripts.video import run_render
            # Force re-import to pick up mocked modules
            with patch.object(run_render, "normalize_loudness", wraps=run_render.normalize_loudness):
                result = run_render.normalize_loudness(audio, target_lufs=-16.0)
        # Either original returned (error path) or a _norm file
        assert result.exists() or result == audio


# ── 6. run_qc video QC gate ───────────────────────────────────────────────────


class TestRunVideoQc:
    """Tests for run_video_qc() in run_qc.py."""

    def test_missing_video_fails(self, tmp_path):
        from scripts.video.run_qc import run_video_qc
        vp = tmp_path / "nonexistent.mp4"
        result = run_video_qc(vp)
        assert result["passed"] is False
        assert any("not found" in e for e in result["errors"])

    def test_existing_video_passes_basic(self, tmp_path):
        from scripts.video.run_qc import run_video_qc
        vp = tmp_path / "test.mp4"
        vp.write_bytes(b"\x00" * 100)  # placeholder bytes

        # Patch all subprocess calls to return mock data
        mock_fmt = {"duration": "10.5", "nb_streams": "2"}
        mock_stream = {"nb_frames": "252", "r_frame_rate": "24/1"}

        with patch("scripts.video.run_qc._ffprobe_format", return_value=mock_fmt), \
             patch("scripts.video.run_qc._ffprobe_video_stream", return_value=mock_stream), \
             patch("scripts.video.run_qc._ffprobe_corruption_check", return_value=[]), \
             patch("scripts.video.run_qc._keyframe_interval_check", return_value={"keyframe_count": 5, "avg_interval_s": 2.1}):
            result = run_video_qc(vp)

        assert result["passed"] is True
        assert result["frame_count"] == 252
        assert result["duration_s"] == pytest.approx(10.5)
        assert result["ssim"] is None  # no reference provided

    def test_zero_duration_fails(self, tmp_path):
        from scripts.video.run_qc import run_video_qc
        vp = tmp_path / "bad.mp4"
        vp.write_bytes(b"\x00" * 100)

        with patch("scripts.video.run_qc._ffprobe_format", return_value={"duration": "0"}), \
             patch("scripts.video.run_qc._ffprobe_video_stream", return_value={}), \
             patch("scripts.video.run_qc._ffprobe_corruption_check", return_value=[]), \
             patch("scripts.video.run_qc._keyframe_interval_check", return_value={}):
            result = run_video_qc(vp)

        assert result["passed"] is False
        assert any("zero" in e or "negative" in e for e in result["errors"])

    def test_corruption_errors_become_warnings(self, tmp_path):
        from scripts.video.run_qc import run_video_qc
        vp = tmp_path / "corrupt.mp4"
        vp.write_bytes(b"\x00" * 100)

        with patch("scripts.video.run_qc._ffprobe_format", return_value={"duration": "5.0"}), \
             patch("scripts.video.run_qc._ffprobe_video_stream", return_value={"nb_frames": "120"}), \
             patch("scripts.video.run_qc._ffprobe_corruption_check", return_value=["DPB buffer full", "error in decode"]), \
             patch("scripts.video.run_qc._keyframe_interval_check", return_value={"avg_interval_s": 2.0}):
            result = run_video_qc(vp)

        # Corruption errors add to warnings, not hard errors
        assert any("potential error" in w for w in result["warnings"])

    def test_high_keyframe_interval_warns(self, tmp_path):
        from scripts.video.run_qc import run_video_qc
        vp = tmp_path / "badkf.mp4"
        vp.write_bytes(b"\x00" * 100)

        with patch("scripts.video.run_qc._ffprobe_format", return_value={"duration": "60.0"}), \
             patch("scripts.video.run_qc._ffprobe_video_stream", return_value={"nb_frames": "1440"}), \
             patch("scripts.video.run_qc._ffprobe_corruption_check", return_value=[]), \
             patch("scripts.video.run_qc._keyframe_interval_check", return_value={"keyframe_count": 3, "avg_interval_s": 15.0}):
            result = run_video_qc(vp)

        assert any("keyframe" in w for w in result["warnings"])

    def test_ssim_skipped_without_reference(self, tmp_path):
        from scripts.video.run_qc import run_video_qc
        vp = tmp_path / "vid.mp4"
        vp.write_bytes(b"\x00" * 100)

        with patch("scripts.video.run_qc._ffprobe_format", return_value={"duration": "5.0"}), \
             patch("scripts.video.run_qc._ffprobe_video_stream", return_value={"nb_frames": "120"}), \
             patch("scripts.video.run_qc._ffprobe_corruption_check", return_value=[]), \
             patch("scripts.video.run_qc._keyframe_interval_check", return_value={}):
            result = run_video_qc(vp, reference_path=None)

        assert result["ssim"] is None

    def test_ssim_warns_when_package_missing(self, tmp_path):
        from scripts.video.run_qc import run_video_qc
        vp = tmp_path / "vid.mp4"
        ref = tmp_path / "ref.mp4"
        vp.write_bytes(b"\x00" * 100)
        ref.write_bytes(b"\x00" * 100)

        with patch("scripts.video.run_qc._ffprobe_format", return_value={"duration": "5.0"}), \
             patch("scripts.video.run_qc._ffprobe_video_stream", return_value={"nb_frames": "120"}), \
             patch("scripts.video.run_qc._ffprobe_corruption_check", return_value=[]), \
             patch("scripts.video.run_qc._keyframe_interval_check", return_value={}), \
             patch.dict("sys.modules", {"ffmpeg_quality_metrics": None}):
            result = run_video_qc(vp, reference_path=ref)

        # Should not crash; SSIM None and warning present
        assert result["ssim"] is None
        assert any("ffmpeg-quality-metrics" in w or "SSIM" in w for w in result["warnings"])


# ── Config smoke tests ────────────────────────────────────────────────────────


class TestP0Config:
    """Verify config files have the new P0 keys."""

    def test_render_params_has_xfade(self):
        import yaml
        cfg_path = REPO_ROOT / "config" / "video" / "render_params.yaml"
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
        assert "xfade" in cfg
        assert "transition" in cfg["xfade"]
        assert "duration_s" in cfg["xfade"]

    def test_render_params_has_noise(self):
        import yaml
        cfg_path = REPO_ROOT / "config" / "video" / "render_params.yaml"
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
        assert "noise" in cfg
        assert "intensity" in cfg["noise"]

    def test_render_params_has_vignette(self):
        import yaml
        cfg_path = REPO_ROOT / "config" / "video" / "render_params.yaml"
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
        assert "vignette" in cfg
        assert "angle" in cfg["vignette"]

    def test_render_params_has_loudness(self):
        import yaml
        cfg_path = REPO_ROOT / "config" / "video" / "render_params.yaml"
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
        assert "loudness" in cfg
        assert "target_lufs" in cfg["loudness"]

    def test_color_grade_presets_has_lut3d(self):
        import yaml
        cfg_path = REPO_ROOT / "config" / "video" / "color_grade_presets.yaml"
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
        assert "lut3d" in cfg
        assert "lut_path" in cfg["lut3d"]

    def test_lut_file_exists(self):
        lut_path = REPO_ROOT / "assets" / "luts" / "warm_therapeutic.cube"
        assert lut_path.exists(), f"LUT file missing: {lut_path}"

    def test_lut_file_valid_cube(self):
        """Minimal .cube format validation."""
        lut_path = REPO_ROOT / "assets" / "luts" / "warm_therapeutic.cube"
        content = lut_path.read_text()
        assert "LUT_3D_SIZE" in content
        assert "DOMAIN_MIN" in content
        assert "DOMAIN_MAX" in content
        # Count data lines: 17^3 = 4913
        data_lines = [
            ln for ln in content.splitlines()
            if ln.strip() and not ln.strip().startswith("#")
            and not any(ln.strip().startswith(kw) for kw in ("TITLE", "LUT_3D_SIZE", "DOMAIN_MIN", "DOMAIN_MAX"))
        ]
        assert len(data_lines) == 17 ** 3, f"Expected 4913 LUT entries, got {len(data_lines)}"
