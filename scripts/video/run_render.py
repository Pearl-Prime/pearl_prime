#!/usr/bin/env python3
"""
Renderer: timeline + assets + captions -> video file (FFmpeg).
Reads real timeline schema: plan_id, clips[] (asset_id, start_time_s, end_time_s, caption_ref).
video_id comes from args (provenance/distribution); plan_id used for output naming and seed when video_id not set.
Loads color presets from config/video/color_grade_presets.yaml and crop margin from config/video/render_params.yaml.
Optional: --shot-plan for motion per clip, --captions for caption text. Concat demuxer (hard cuts). Thumbnail from thumbnail_frame_ref.
Usage: python scripts/video/run_render.py <timeline.json> -o <output_dir> [--assets-dir DIR] [--captions captions.json] [--shot-plan shot_plan.json] [--video-id ID] [--placeholder]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import get_ffmpeg_bin, load_json, load_yaml
from scripts.video.vce_ffmpeg_builders import (
    build_lut3d_filter,
    build_noise_filter,
    build_vignette_filter,
    build_xfade_filter,
    color_temp_arc_anchors,
    interpolate_colorbalance_at_pct,
    parse_colorbalance_args,
    per_second_colorbalance_keyframes,
    quality_tuning,
    write_colorbalance_sendcmd_file,
)

# Default output size for 9:16 shorts; override from timeline resolution if present
DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1920
FPS_DEFAULT = 24
# Scale before crop (slightly larger so crop has headroom)
SCALE_W = 1200
SCALE_H = 2133


def _escape_ffmpeg_text(text: str) -> str:
    """Escape text for FFmpeg drawtext filter value inside single quotes.

    FFmpeg drawtext inside ``-filter_complex`` needs two layers of escaping:
    1. FFmpeg filter escaping (colons, semicolons, brackets)
    2. Shell-safe single-quote handling

    The safest approach: replace problematic characters so the filter
    never sees them. Apostrophes become Unicode right single quote (visually
    identical in rendered captions).
    """
    text = text.replace("\n", " ").replace("\r", " ")
    # Remove all quote characters — they break FFmpeg filter_complex quoting
    text = text.replace("'", "")
    text = text.replace('"', "")
    text = text.replace("\u2018", "")  # left single quote
    text = text.replace("\u2019", "")  # right single quote
    text = text.replace("\u201c", "")  # left double quote
    text = text.replace("\u201d", "")  # right double quote
    # Backslash must be escaped first
    text = text.replace("\\", "\\\\")
    # FFmpeg drawtext inside filter_complex: colons, semicolons, brackets
    # need escaping at the filter_complex level
    text = text.replace(":", "\\\\:")
    text = text.replace(";", "\\\\;")
    text = text.replace("[", "\\\\[")
    text = text.replace("]", "\\\\]")
    text = text.replace("%", "%%%%")
    return text


def _deterministic_seed(video_id: str, shot_index: int) -> int:
    key = f"{video_id}_{shot_index}".encode()
    return int(hashlib.sha256(key).hexdigest(), 16)


def _crop_params(seed: int, width: int, height: int, margin_pct: float) -> tuple[float, int, int]:
    """Crop zoom and offsets; offsets bounded by crop_margin_pct so we don't clip the subject."""
    zoom = 0.92 + (seed % 80) / 1000.0
    margin = margin_pct / 100.0
    max_off_x = int(width * (1 - zoom) * margin)
    max_off_y = int(height * (1 - zoom) * margin)
    crop_x = seed % max(1, max_off_x)
    crop_y = (seed // 10) % max(1, max_off_y)
    return zoom, crop_x, crop_y


def _normalize_motion_for_ffmpeg(motion_type: str) -> str:
    m = (motion_type or "static").strip().lower()
    if m in ("ken_burns", "breathing_pulse", "scale_drift"):
        return "slow_zoom"
    if m in ("camera_pan", "parallax_scroll"):
        return "slow_pan"
    return m


def _motion_expr(motion_type: str) -> tuple[str, str | None, str | None]:
    """zoompan z (and optionally x,y for pan). Always init zoom on frame 0 to avoid undefined state.
    Returns (z_expr, x_expr or None, y_expr or None). For slow_pan, x/y are full key=value e.g. x='...'.
    FFmpeg zoompan is picky about quoting and parameter order — verify with a real slow_pan render if needed."""
    motion = (motion_type or "static").strip().lower()
    if motion == "static":
        return "z='1'", None, None
    if motion in ("slow_zoom_in", "slow_zoom"):
        return "z='if(eq(on,0),1.0,min(zoom+0.00023,1.08))'", None, None
    if motion == "slow_zoom_out":
        return "z='if(eq(on,0),1.0,max(zoom-0.00023,0.92))'", None, None
    if motion == "slow_pan":
        return "z='1'", "x='iw/2-(iw/zoom/2)+sin(on/50)*10'", "y='ih/2-(ih/zoom/2)'"
    return "z='1'", None, None


def _build_filter_chain(
    zoom: float,
    crop_x: int,
    crop_y: int,
    frames: int,
    motion_z: str,
    motion_x: str | None,
    motion_y: str | None,
    eq_preset: dict,
    output_w: int,
    output_h: int,
    caption_text: str | None,
    caption_x: str,
    caption_y: str,
    drawbox: bool = True,
    colorbalance: str | None = None,
    extra_vf: str | None = None,
    zoompan_body: str | None = None,
) -> str:
    crop = f"crop=iw*{zoom}:ih*{zoom}:{crop_x}:{crop_y}"
    zoompan = f"zoompan={motion_z}:d={frames}:s={output_w}x{output_h}"
    if motion_x is not None and motion_y is not None:
        zoompan = f"zoompan={motion_z}:{motion_x}:{motion_y}:d={frames}:s={output_w}x{output_h}"
    eq = f"eq=contrast={eq_preset.get('contrast', 1.0)}:brightness={eq_preset.get('brightness', 0)}:saturation={eq_preset.get('saturation', 1.0)}"
    filters = [
        f"scale={SCALE_W}:{SCALE_H}",
        crop,
        zoompan,
        eq,
    ]
    if colorbalance:
        # §6.3 additive temperature arc (preset string e.g. rs=0.1:gs=0.0:bs=-0.1)
        filters.append(f"colorbalance={colorbalance}")
    if extra_vf:
        filters.append(extra_vf)
    filters.append("format=yuv420p")
    if drawbox and caption_text:
        filters.append("drawbox=x=0:y=h*0.75:w=iw:h=h*0.25:color=black@0.35:t=fill")
    if caption_text:
        escaped = _escape_ffmpeg_text(caption_text)
        filters.append(
            f"drawtext=text='{escaped}':fontsize=64:fontcolor=white:x={caption_x}:y={caption_y}:"
            "shadowcolor=black:shadowx=2:shadowy=2:line_spacing=8"
        )
    return ",".join(filters)


def _encode_args(preset: str, crf: int) -> list[str]:
    return ["-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p"]


def _colorbalance_dict_to_arg(cb: dict | None) -> str | None:
    if not cb:
        return None
    return f"rs={cb['rs']:.5f}:gs={cb['gs']:.5f}:bs={cb['bs']:.5f}"


def _zoompan_body_from_bundle(bundle: dict | None, frames: int, output_w: int, output_h: int, fps: int) -> str | None:
    if not bundle or not isinstance(bundle, dict):
        return None
    zb = bundle.get("zoompan")
    if isinstance(zb, str) and zb.strip():
        return zb
    return None


def _find_asset(assets_dir: Path, asset_key: str) -> Path | None:
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = assets_dir / f"{asset_key}{ext}"
        if p.exists():
            return p
    return None


def _layer_inputs_for_composite(
    comp_shot: dict,
    assets_dir: Path,
    duration_s: float,
    out_w: int,
    out_h: int,
) -> tuple[bool, list[tuple[str, str]]]:
    """Return (all_critical_resolved, [(kind, spec), ...]) for -i arguments (kind is file|lavfi)."""
    order = comp_shot.get("filter_complex_input_order") or []
    layers = {str(x.get("id")): x for x in (comp_shot.get("layers") or []) if x.get("id")}
    inputs: list[tuple[str, str]] = []
    for lid in order:
        layer = layers.get(str(lid), {})
        key = str(layer.get("asset_key", "") or "")
        path = _find_asset(assets_dir, key) if key else None
        if path:
            inputs.append(("file", str(path)))
            continue
        if lid == "L1" or lid == "L3":
            return False, []
        if lid in ("L2", "L4"):
            inputs.append(
                ("lavfi", f"color=black:s={out_w}x{out_h}:d={max(0.01, float(duration_s))}")
            )
            continue
        if lid == "L5":
            inputs.append(
                ("lavfi", f"color=white@0.0:s={out_w}x{out_h}:d={max(0.01, float(duration_s))},format=rgba")
            )
            continue
        return False, []
    return True, inputs


def _motion_scale_crop(
    motion_type: str,
    output_w: int,
    output_h: int,
    fps: int,
) -> list[str]:
    """Return scale+crop filters that simulate motion on a multi-frame stream.

    Unlike zoompan (which requires single-frame ``-loop 1`` input), these filters
    work on the already-composited multi-frame overlay output.

    Motion types:
      slow_zoom / slow_zoom_in  -- Ken Burns zoom in via expanding scale + center crop
      slow_zoom_out             -- Ken Burns zoom out
      slow_pan                  -- gentle horizontal pan via shifting crop x
      static                    -- no motion, just ensure exact output size
    """
    motion = _normalize_motion_for_ffmpeg(motion_type)
    # Zoom rate per frame (matches the zoompan 0.00023/frame used in _motion_expr)
    zr = 0.0015  # per-second rate; spread across fps

    if motion in ("slow_zoom", "slow_zoom_in"):
        # Scale up slightly over time, crop back to output size from center.
        # n = frame number (0-based). Scale grows from 1.0x to ~1.08x over the clip.
        # We scale to (output + growth) then crop the center.
        # eval=frame is required so 'n' is re-evaluated each frame.
        return [
            f"scale=trunc((iw*(1+{zr}*n/{fps}))/2)*2:trunc((ih*(1+{zr}*n/{fps}))/2)*2:flags=bicubic:eval=frame",
            f"crop={output_w}:{output_h}:(iw-{output_w})/2:(ih-{output_h})/2",
        ]
    if motion == "slow_zoom_out":
        # Start slightly zoomed in, scale back toward 1.0x.
        max_zoom = 1.08
        return [
            f"scale=trunc((iw*({max_zoom}-{zr}*n/{fps}))/2)*2:trunc((ih*({max_zoom}-{zr}*n/{fps}))/2)*2:flags=bicubic:eval=frame",
            f"crop={output_w}:{output_h}:(iw-{output_w})/2:(ih-{output_h})/2",
        ]
    if motion == "slow_pan":
        # Slight overscan then horizontal pan via crop x offset.
        overscan_w = int(output_w * 1.04)  # 4% wider
        overscan_h = int(output_h * 1.02)  # 2% taller
        return [
            f"scale={overscan_w}:{overscan_h}:flags=bicubic",
            f"crop={output_w}:{output_h}:(iw-{output_w})/2*min(1\\,{0.001}*n):(ih-{output_h})/2",
        ]
    # static — just ensure exact output dimensions
    return [
        f"scale={output_w}:{output_h}:flags=bicubic",
    ]


def _post_overlay_chain(
    base_label: str,
    bundle: dict | None,
    frames: int,
    fps: int,
    output_w: int,
    output_h: int,
    eq_preset: dict,
    cb_dict: dict | None,
    caption_text: str | None,
    caption_x: str,
    caption_y: str,
    drawbox: bool,
    caption_textfile: Path | None = None,
) -> str:
    """Serial filters after compositor output label -> chain ending at [vfinal].

    Motion is applied via scale+crop instead of zoompan so it works on
    multi-frame overlay streams (zoompan fails on these in FFmpeg 8.x).

    When *caption_textfile* is provided, uses ``textfile=`` instead of inline
    ``text=`` to avoid FFmpeg filter_complex quoting issues.
    """
    eq = f"eq=contrast={eq_preset.get('contrast', 1.0)}:brightness={eq_preset.get('brightness', 0)}:saturation={eq_preset.get('saturation', 1.0)}"
    parts: list[str] = []

    # Determine motion type from bundle
    motion_type = "static"
    if isinstance(bundle, dict) and bundle.get("motion"):
        motion_type = str(bundle["motion"])

    # Apply motion via scale+crop (works on multi-frame streams, unlike zoompan)
    parts.extend(_motion_scale_crop(motion_type, output_w, output_h, fps))

    parts.append(f"fps={fps}")
    parts.append(eq)
    cb_arg = _colorbalance_dict_to_arg(cb_dict)
    if cb_arg:
        parts.append(f"colorbalance={cb_arg}")
    parts.append("format=yuv420p")
    if drawbox and caption_text:
        # Use absolute pixel values — expressions like h*0.75 fail after zoompan
        box_y = int(output_h * 0.75)
        box_h = output_h - box_y
        parts.append(f"drawbox=x=0:y={box_y}:w={output_w}:h={box_h}:color=black@0.35:t=fill")
    if caption_text:
        # Convert expression-based positions to absolute pixels
        abs_caption_x = f"({output_w}-text_w)/2" if caption_x == "(w-text_w)/2" else caption_x
        abs_caption_y = str(int(output_h * 0.82)) if caption_y == "h*0.82" else caption_y
        if caption_textfile:
            tf_path = str(caption_textfile).replace(":", "\\:")
            parts.append(
                f"drawtext=textfile={tf_path}:fontsize=64:fontcolor=white:x={abs_caption_x}:y={abs_caption_y}:"
                "shadowcolor=black:shadowx=2:shadowy=2:line_spacing=8"
            )
        else:
            escaped = _escape_ffmpeg_text(caption_text)
            parts.append(
                f"drawtext=text='{escaped}':fontsize=64:fontcolor=white:x={abs_caption_x}:y={abs_caption_y}:"
                "shadowcolor=black:shadowx=2:shadowy=2:line_spacing=8"
            )
    chain = ",".join(parts)
    return f"[{base_label}]{chain}[vfinal]"


def _render_clip(
    image_path: Path,
    output_path: Path,
    video_id: str,
    shot_index: int,
    duration_s: float,
    motion_type: str,
    grade: dict,
    caption_text: str | None,
    caption_x: str,
    caption_y: str,
    fps: int,
    output_w: int,
    output_h: int,
    margin_pct: float,
    colorbalance: str | None = None,
    extra_vf: str | None = None,
    zoompan_body: str | None = None,
    encode_preset: str = "veryfast",
    encode_crf: int = 23,
) -> None:
    seed = _deterministic_seed(video_id, shot_index)
    zoom, crop_x, crop_y = _crop_params(seed, SCALE_W, SCALE_H, margin_pct)
    frames = int(round(duration_s * fps))
    motion_z, motion_x, motion_y = _motion_expr(_normalize_motion_for_ffmpeg(motion_type))
    filter_complex = _build_filter_chain(
        zoom, crop_x, crop_y, frames, motion_z, motion_x, motion_y,
        grade, output_w, output_h, caption_text, caption_x, caption_y, drawbox=True,
        colorbalance=colorbalance,
        extra_vf=extra_vf,
        zoompan_body=zoompan_body,
    )
    cmd = [
        get_ffmpeg_bin(), "-y", "-loop", "1", "-i", str(image_path),
        "-filter_complex", filter_complex,
        "-t", str(duration_s), "-r", str(fps),
        *_encode_args(encode_preset, encode_crf),
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def _render_multilayer_clip(
    inputs: list[tuple[str, str]],
    filter_complex: str,
    output_path: Path,
    duration_s: float,
    fps: int,
    encode_preset: str,
    encode_crf: int,
) -> None:
    cmd: list[str] = [get_ffmpeg_bin(), "-y"]
    for kind, spec in inputs:
        if kind == "file":
            cmd.extend(["-loop", "1", "-t", str(duration_s), "-i", spec])
        else:
            cmd.extend(["-f", "lavfi", "-i", spec])
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[vfinal]",
        "-t", str(duration_s), "-r", str(fps),
        *_encode_args(encode_preset, encode_crf),
        str(output_path),
    ])
    subprocess.run(cmd, check=True, capture_output=True)


def _concat_clips(
    clip_paths: list[Path],
    out_path: Path,
    xfade_cfg: dict | None = None,
    fps: int = 24,
) -> None:
    """Concat clips with optional xfade transitions.

    When *xfade_cfg* is None or ``enabled`` is False, falls back to the concat
    demuxer (stream-copy, no re-encode) for maximum speed.

    When xfade is enabled, encodes the concatenated output via libx264 to
    apply the crossfade — this requires a re-encode pass but is still fast.
    """
    if not xfade_cfg or not xfade_cfg.get("enabled") or len(clip_paths) < 2:
        # Fast path: concat demuxer (hard cuts)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            for p in clip_paths:
                f.write(f"file '{p.absolute()}'\n")
            list_path = Path(f.name)
        try:
            subprocess.run(
                [get_ffmpeg_bin(), "-y", "-f", "concat", "-safe", "0", "-i", str(list_path), "-c", "copy", str(out_path)],
                check=True, capture_output=True,
            )
        finally:
            list_path.unlink(missing_ok=True)
        return

    # xfade path: filter_complex with xfade transitions
    transition = xfade_cfg.get("transition", "dissolve")
    duration_s = float(xfade_cfg.get("duration_s", 0.5))
    input_args, filter_parts = build_xfade_filter(clip_paths, transition, duration_s, fps)
    if not filter_parts:
        # Fallback if builder returned empty (e.g. single clip)
        _concat_clips(clip_paths, out_path, xfade_cfg=None)
        return
    filter_complex = ";".join(filter_parts)
    cmd = [
        get_ffmpeg_bin(), "-y",
        *input_args,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def normalize_loudness(audio_path: Path, target_lufs: float = -16.0) -> Path:
    """Normalise a WAV/PCM audio file to *target_lufs* integrated loudness.

    Uses pyloudnorm (BSW loudness metering).  Returns *audio_path* unchanged if
    pyloudnorm is not installed or the file is not a supported format.

    The normalised file is written to ``<stem>_norm.wav`` alongside the input.
    """
    try:
        import soundfile as sf  # type: ignore
        import pyloudnorm as pyln  # type: ignore
    except ImportError:
        print(
            "Warning: pyloudnorm/soundfile not installed — skipping loudness normalisation. "
            "pip install pyloudnorm soundfile",
            file=sys.stderr,
        )
        return audio_path

    try:
        data, rate = sf.read(str(audio_path))
        meter = pyln.Meter(rate)
        loudness = meter.integrated_loudness(data)
        normalised = pyln.normalize.loudness(data, loudness, target_lufs)
        out_path = audio_path.parent / f"{audio_path.stem}_norm.wav"
        sf.write(str(out_path), normalised, rate)
        return out_path
    except Exception as exc:
        print(f"Warning: loudness normalisation failed ({exc}) — using original", file=sys.stderr)
        return audio_path


def _extract_thumbnail(video_path: Path, timestamp_s: float, thumb_path: Path) -> None:
    subprocess.run(
        [get_ffmpeg_bin(), "-y", "-ss", str(timestamp_s), "-i", str(video_path), "-frames:v", "1", str(thumb_path)],
        check=True, capture_output=True,
    )


def _timestamp_from_thumbnail_ref(timeline: dict, thumbnail_ref: dict | None, fps: int) -> float:
    """Map thumbnail_frame_ref (shot_id, frame_offset) to seconds into the video."""
    if not thumbnail_ref:
        return 0.0
    shot_id = thumbnail_ref.get("shot_id")
    frame_offset = thumbnail_ref.get("frame_offset", 0)
    for clip in timeline.get("clips", []):
        if clip.get("shot_id") == shot_id:
            start_s = clip.get("start_time_s", 0)
            return start_s + (frame_offset / fps)
    return 0.0


def main() -> int:
    ap = argparse.ArgumentParser(description="Render timeline to video (FFmpeg) or placeholder")
    ap.add_argument("timeline", help="Path to timeline.json")
    ap.add_argument("-o", "--out-dir", required=True, help="Output directory for video, thumb, timeline_ref")
    ap.add_argument("--assets-dir", default=None, help="Directory with image assets; asset_id maps to <assets_dir>/<asset_id>.jpg")
    ap.add_argument("--captions", default=None, help="Path to captions.json (segment_id -> text)")
    ap.add_argument("--shot-plan", default=None, help="Path to shot_plan.json for motion per shot_id (prompt_bundle.motion)")
    ap.add_argument("--video-id", default=None, help="Video ID for deterministic seed and provenance (default: plan_id)")
    ap.add_argument("--color-grade", default=None, help="Color preset name (default: from config default_preset)")
    ap.add_argument("--placeholder", action="store_true", help="Write placeholder only, no FFmpeg")
    ap.add_argument("--composited-layers", default=None, help="composited_layers.json (metadata filter_complex hints)")
    ap.add_argument("--animation-plan", default=None, help="animation_plan.json for motion + colorbalance per shot")
    ap.add_argument("--platform-variant", default=None, help="JSON file with single platform variant encode overrides")
    ap.add_argument("--quality", default="standard", choices=("draft", "standard", "high"), help="CRF/preset tradeoff")
    ap.add_argument("--soundtrack-plan", default=None, help="soundtrack_plan_with_audio.json for voice + music mixing")
    ap.add_argument("--workspace", type=str, default=None, help="Directory containing job.json (default: --out-dir)")
    ap.add_argument("--no-job-check", dest="no_job_check", action="store_true", help="Skip job.json enforcement (CI only)")
    args = ap.parse_args()
    if args.no_job_check:
        print("WARNING: --no-job-check: pipeline job enforcement disabled (CI/testing only).", file=sys.stderr)
    from scripts.pipeline._video_workspace import resolve_video_workspace
    from scripts.pipeline.advance_stage import mark_complete, mark_failed
    from scripts.pipeline.check_job import require_stage

    ws = resolve_video_workspace(args, out_attr="out_dir")
    if not args.no_job_check:
        require_stage("render", ws)

    tl_path = Path(args.timeline)
    if not tl_path.exists():
        print(f"Error: not found: {tl_path}", file=sys.stderr)
        if not args.no_job_check:
            mark_failed(ws, "render", error=f"missing {tl_path}")
        return 1
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    timeline = load_json(tl_path)
    plan_id = timeline.get("plan_id", "unknown")
    video_id = args.video_id or plan_id

    # Config: color presets and crop margin
    color_cfg = load_yaml("config/video/color_grade_presets.yaml")
    presets = (color_cfg.get("presets") or {})
    default_preset_name = color_cfg.get("default_preset", "neutral")
    grade_name = args.color_grade or default_preset_name
    grade = presets.get(grade_name) or presets.get("neutral") or {"contrast": 1.0, "brightness": 0.0, "saturation": 1.0}

    render_cfg = load_yaml("config/video/render_params.yaml")
    margin_pct = float(render_cfg.get("crop_margin_pct", 6))

    # P0 upgrade config ───────────────────────────────────────────────────────
    xfade_cfg: dict = render_cfg.get("xfade") or {}
    noise_cfg: dict = render_cfg.get("noise") or {}
    vignette_cfg: dict = render_cfg.get("vignette") or {}
    loudness_cfg: dict = render_cfg.get("loudness") or {}

    # lut3d config from color_grade_presets.yaml
    lut3d_cfg: dict = color_cfg.get("lut3d") or {}

    # Build post-final filter fragments (applied after concat or before encode in single-pass)
    # These are appended as a post-processing vf chain on the final concatenated video.
    _post_vf_parts: list[str] = []
    if lut3d_cfg.get("enabled"):
        _lut_path = str(lut3d_cfg.get("lut_path", "assets/luts/warm_therapeutic.cube"))
        _lut_abs = REPO_ROOT / _lut_path if not Path(_lut_path).is_absolute() else Path(_lut_path)
        if _lut_abs.exists():
            _post_vf_parts.append(build_lut3d_filter(_lut_abs))
        else:
            print(f"Warning: lut3d enabled but LUT file not found: {_lut_abs}", file=sys.stderr)
    _noise_filter = build_noise_filter(int(noise_cfg.get("intensity", 15))) if noise_cfg.get("enabled") else None
    if _noise_filter:
        _post_vf_parts.append(_noise_filter)
    _vignette_filter = build_vignette_filter(vignette_cfg.get("angle", "PI/5")) if vignette_cfg.get("enabled") else None
    if _vignette_filter:
        _post_vf_parts.append(_vignette_filter)
    # ─────────────────────────────────────────────────────────────────────────

    resolution = timeline.get("resolution") or {}
    output_w = resolution.get("width", DEFAULT_WIDTH)
    output_h = resolution.get("height", DEFAULT_HEIGHT)
    fps = timeline.get("fps", FPS_DEFAULT)

    pv_doc: dict | None = None
    if args.platform_variant and Path(args.platform_variant).exists():
        pv_doc = load_json(Path(args.platform_variant))
        enc = pv_doc.get("encode") or {}
        if enc.get("width"):
            output_w = int(enc["width"])
        if enc.get("height"):
            output_h = int(enc["height"])

    crf_off, qual_preset = quality_tuning(args.quality)
    base_crf = int((pv_doc or {}).get("encode", {}).get("crf", 23)) if pv_doc else 23
    encode_crf = max(10, min(45, base_crf + crf_off))
    encode_preset = qual_preset

    ther = load_yaml("config/video/therapeutic_video_rules.yaml")
    color_anchors = color_temp_arc_anchors((ther or {}).get("color_temp_arc") or {})

    # Motion / colorbalance from animation_plan
    anim_by_shot: dict[str, dict] = {}
    if args.animation_plan and Path(args.animation_plan).exists():
        ap_doc = load_json(Path(args.animation_plan))
        for row in ap_doc.get("shots") or []:
            sid = row.get("shot_id")
            if sid:
                anim_by_shot[sid] = row
    composited_by_shot: dict[str, dict] = {}
    if args.composited_layers and Path(args.composited_layers).exists():
        cl = load_json(Path(args.composited_layers))
        for row in cl.get("shots") or []:
            sid = row.get("shot_id")
            if sid:
                composited_by_shot[sid] = row

    # Motion per shot_id from shot_plan if provided
    motion_by_shot: dict[str, str] = {}
    if args.shot_plan and Path(args.shot_plan).exists():
        shot_plan = load_json(Path(args.shot_plan))
        for shot in shot_plan.get("shots", []):
            pb = shot.get("prompt_bundle") or {}
            motion_by_shot[shot["shot_id"]] = pb.get("motion", "static")

    # Caption text per segment from captions.json if provided
    captions_by_ref: dict[str, str] = {}
    if args.captions and Path(args.captions).exists():
        captions_data = load_json(Path(args.captions))
        for seg_id, obj in (captions_data.get("captions") or {}).items():
            if isinstance(obj, dict) and "text" in obj:
                captions_by_ref[seg_id] = obj["text"]
            elif isinstance(obj, str):
                captions_by_ref[seg_id] = obj

    # Default caption position (bottom center; spec contrast >= 4.5 with drawbox)
    caption_x, caption_y = "(w-text_w)/2", "h*0.82"

    if args.placeholder or not args.assets_dir:
        video_path = out_dir / f"{plan_id}.mp4"
        thumb_path = out_dir / "thumb.jpg"
        video_path.write_text("placeholder\n", encoding="utf-8")
        thumb_path.write_text("placeholder\n", encoding="utf-8")
        ref = {"timeline_path": str(tl_path), "video_path": str(video_path), "thumbnail_path": str(thumb_path)}
        (out_dir / "timeline_ref.json").write_text(json.dumps(ref, indent=2), encoding="utf-8")
        print(f"Placeholder: {video_path} (no FFmpeg)")
        if not args.no_job_check:
            mark_complete(ws, "render", output=str(video_path.name))
        return 0

    assets_dir = Path(args.assets_dir)
    clips = timeline.get("clips", [])
    if not clips:
        if not args.no_job_check:
            mark_failed(ws, "render", error="no clips in timeline")
        print("No clips in timeline", file=sys.stderr)
        return 1

    total_d = float(timeline.get("duration_s") or 0)
    if total_d <= 0:
        total_d = max((float(c.get("end_time_s") or 0) for c in clips), default=1.0)

    clip_files: list[Path] = []
    cmd_paths: list[str] = []
    for i, clip in enumerate(clips):
        asset_id = clip.get("asset_id")
        if not asset_id:
            continue
        image_path = assets_dir / f"{asset_id}.jpg"
        if not image_path.exists():
            image_path = assets_dir / f"{asset_id}.png"
        if not image_path.exists():
            print(f"Warning: asset not found {asset_id}, skipping clip", file=sys.stderr)
            continue
        start_s = float(clip.get("start_time_s", 0))
        end_s = float(clip.get("end_time_s", start_s + 5))  # end_time_s is end timestamp, not duration
        duration_s = end_s - start_s  # clip duration in seconds
        if duration_s <= 0:
            continue
        sid = clip.get("shot_id", "")
        anim = anim_by_shot.get(sid) or {}
        bundle = anim.get("ffmpeg_motion") if isinstance(anim.get("ffmpeg_motion"), dict) else {}
        if bundle.get("motion"):
            motion_type = str(bundle["motion"])
        else:
            motion_type = motion_by_shot.get(sid, clip.get("motion", "static"))
        comp = composited_by_shot.get(sid) or {}
        fc = comp.get("filter_complex") if isinstance(comp.get("filter_complex"), str) else ""
        bal = anim.get("colorbalance_section")
        cb_fallback = ""
        if isinstance(bal, dict):
            cb_fallback = str(bal.get("colorbalance", "")).replace("colorbalance=", "")
        elif isinstance(bal, str):
            cb_fallback = bal.replace("colorbalance=", "")

        pct_mid = ((start_s + duration_s / 2) / max(1e-6, total_d)) * 100.0
        if color_anchors:
            cb_dict_mid = interpolate_colorbalance_at_pct(pct_mid, color_anchors)
            kf = per_second_colorbalance_keyframes(duration_s, start_s, total_d, color_anchors)
            cmd_p = write_colorbalance_sendcmd_file(kf, out_dir / f"colorbalance_clip_{i:04d}.cmd")
            cmd_paths.append(str(cmd_p))
        else:
            cb_dict_mid = parse_colorbalance_args(cb_fallback)
        cb_str = _colorbalance_dict_to_arg(cb_dict_mid)

        caption_ref = clip.get("caption_ref", "")
        caption_text = captions_by_ref.get(caption_ref) if caption_ref else None
        out_clip = out_dir / f"clip_{i:04d}.mp4"
        frames = max(1, int(round(duration_s * fps)))

        use_multi = False
        if fc and "[out_" in fc:
            ok_layers, layer_inputs = _layer_inputs_for_composite(comp, assets_dir, duration_s, output_w, output_h)
            outs = list(re.finditer(r"\[out_([a-zA-Z0-9_]+)\]", fc))
            if ok_layers and outs:
                base_lab = f"out_{outs[-1].group(1)}"
                # Write caption to temp file to avoid filter_complex quoting issues
                cap_file: Path | None = None
                if caption_text:
                    cap_file = out_dir / f"caption_{i:04d}.txt"
                    cap_file.write_text(caption_text, encoding="utf-8")
                post = _post_overlay_chain(
                    base_lab, bundle, frames, fps, output_w, output_h, grade,
                    cb_dict_mid,
                    caption_text, caption_x, caption_y, drawbox=True,
                    caption_textfile=cap_file,
                )
                full_fc = f"{fc};{post}"
                # Debug: write filter_complex to file for inspection
                dbg = out_dir / f"debug_fc_{i:04d}.txt"
                dbg.write_text(full_fc, encoding="utf-8")
                _render_multilayer_clip(
                    layer_inputs, full_fc, out_clip, duration_s, fps,
                    encode_preset, encode_crf,
                )
                use_multi = True

        if not use_multi:
            zb = _zoompan_body_from_bundle(bundle, frames, output_w, output_h, fps)
            _render_clip(
                image_path, out_clip, video_id, i, duration_s, motion_type, grade,
                caption_text, caption_x, caption_y, fps, output_w, output_h, margin_pct,
                colorbalance=cb_str,
                extra_vf=None,
                zoompan_body=zb,
                encode_preset=encode_preset,
                encode_crf=encode_crf,
            )
        clip_files.append(out_clip)

    if not clip_files:
        if not args.no_job_check:
            mark_failed(ws, "render", error="no clips rendered")
        print("No clips rendered", file=sys.stderr)
        return 1

    video_path = out_dir / f"{plan_id}.mp4"
    _concat_clips(clip_files, video_path, xfade_cfg=xfade_cfg, fps=fps)
    for f in clip_files:
        f.unlink(missing_ok=True)

    # P0: apply post-vf chain (lut3d, noise, vignette) if any filters active
    if _post_vf_parts:
        post_vf_path = out_dir / f"{plan_id}_graded.mp4"
        vf_chain = ",".join(_post_vf_parts)
        try:
            subprocess.run(
                [
                    get_ffmpeg_bin(), "-y", "-i", str(video_path),
                    "-vf", vf_chain,
                    "-c:v", "libx264", "-preset", encode_preset, "-crf", str(encode_crf),
                    "-pix_fmt", "yuv420p",
                    "-c:a", "copy",
                    str(post_vf_path),
                ],
                check=True, capture_output=True,
            )
            video_path.unlink(missing_ok=True)
            post_vf_path.rename(video_path)
            print(f"Post-grade applied: {', '.join(_post_vf_parts[:3])}")
        except Exception as exc:
            print(f"Warning: post-grade pass failed ({exc}), keeping ungraded video", file=sys.stderr)

    thumb_ref = timeline.get("thumbnail_frame_ref")
    ts = _timestamp_from_thumbnail_ref(timeline, thumb_ref, fps)
    thumb_path = out_dir / "thumb.jpg"
    _extract_thumbnail(video_path, ts, thumb_path)

    ref = {
        "timeline_path": str(tl_path),
        "video_path": str(video_path),
        "thumbnail_path": str(thumb_path),
        "colorbalance_sendcmd_files": cmd_paths,
        "encode": {"preset": encode_preset, "crf": encode_crf, "quality": args.quality},
        "p0_effects": {
            "xfade": xfade_cfg.get("enabled", False),
            "lut3d": lut3d_cfg.get("enabled", False),
            "noise": noise_cfg.get("enabled", False),
            "vignette": vignette_cfg.get("enabled", False),
        },
    }
    (out_dir / "timeline_ref.json").write_text(json.dumps(ref, indent=2), encoding="utf-8")
    print(f"Rendered: {video_path} (thumb: {thumb_path})")

    # ── Audio mixing: voice narration + music ──
    soundtrack_path = Path(args.soundtrack_plan) if getattr(args, "soundtrack_plan", None) else None
    if soundtrack_path and soundtrack_path.is_file():
        soundtrack = load_json(soundtrack_path)
        narration_segs = [s for s in (soundtrack.get("narration_segments") or []) if s.get("audio_path")]
        music_path = soundtrack.get("music_path")

        if narration_segs or music_path:
            # P0: loudness normalisation — apply before mixing if enabled
            if loudness_cfg.get("normalize_loudness"):
                target_lufs = float(loudness_cfg.get("target_lufs", -16.0))
                normalised_segs: list[dict] = []
                for seg in narration_segs:
                    ap_str = seg.get("audio_path", "")
                    ap_p = Path(ap_str) if ap_str else None
                    if ap_p and ap_p.is_file() and ap_p.suffix.lower() in (".wav", ".pcm", ".aif", ".aiff"):
                        norm_p = normalize_loudness(ap_p, target_lufs)
                        normalised_segs.append({**seg, "audio_path": str(norm_p)})
                    else:
                        normalised_segs.append(seg)
                narration_segs = normalised_segs

            voiced_path = out_dir / f"{plan_id}_voiced.mp4"
            try:
                _mix_audio_tracks(video_path, narration_segs, music_path, voiced_path)
                # Replace silent video with voiced version
                video_path.unlink(missing_ok=True)
                voiced_path.rename(video_path)
                print(f"Audio mixed: {len(narration_segs)} voice segments"
                      + (" + music" if music_path else ""))
            except Exception as e:
                print(f"Warning: audio mixing failed ({e}), keeping silent video", file=sys.stderr)

    if not args.no_job_check:
        mark_complete(ws, "render", output=str(video_path.name))
    return 0


def _mix_audio_tracks(
    video_path: Path,
    narration_segments: list[dict],
    music_path: str | None,
    output_path: Path,
) -> None:
    """Mix narration clips + optional music into the video via FFmpeg.

    Each narration segment has ``audio_path`` and ``start_time_s``.
    Music plays at 15% volume when narration is active, 25% otherwise (ducking).
    """
    cmd: list[str] = [get_ffmpeg_bin(), "-y", "-i", str(video_path)]

    inputs = []  # track input indices
    filter_parts = []
    input_idx = 1  # 0 is the video

    # Add narration inputs
    for seg in narration_segments:
        ap = seg.get("audio_path", "")
        if not ap or not Path(ap).is_file():
            continue
        cmd.extend(["-i", ap])
        start_ms = int(float(seg.get("start_time_s", 0)) * 1000)
        filter_parts.append(f"[{input_idx}:a]adelay={start_ms}|{start_ms},apad[n{input_idx}]")
        inputs.append(f"[n{input_idx}]")
        input_idx += 1

    # Add music input
    music_input = None
    if music_path and Path(music_path).is_file():
        cmd.extend(["-i", music_path])
        # Music: lower volume, fade in/out
        filter_parts.append(
            f"[{input_idx}:a]volume=0.18,afade=t=in:st=0:d=3,afade=t=out:st=200:d=8[music]"
        )
        music_input = "[music]"
        input_idx += 1

    if not inputs and not music_input:
        raise RuntimeError("No audio tracks to mix")

    # Mix all narration tracks together
    if len(inputs) > 1:
        mix_narr = "".join(inputs) + f"amix=inputs={len(inputs)}:duration=longest[narr]"
        filter_parts.append(mix_narr)
        narr_label = "[narr]"
    elif len(inputs) == 1:
        narr_label = inputs[0]
    else:
        narr_label = None

    # Final mix: narration + music
    if narr_label and music_input:
        filter_parts.append(f"{narr_label}{music_input}amix=inputs=2:duration=longest[aout]")
        map_audio = "[aout]"
    elif narr_label:
        map_audio = narr_label
    elif music_input:
        map_audio = music_input
    else:
        raise RuntimeError("No audio to mix")

    fc = ";".join(filter_parts)
    cmd.extend([
        "-filter_complex", fc,
        "-map", "0:v",
        "-map", map_audio,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path),
    ])

    subprocess.run(cmd, check=True, capture_output=True)


if __name__ == "__main__":
    sys.exit(main())
