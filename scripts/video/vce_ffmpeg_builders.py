"""
Shared FFmpeg-oriented builders for VCE: color arc keyframes, platform encode argv lists,
and lightweight filter_complex validation helpers (no subprocess).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


def parse_colorbalance_args(s: str) -> dict[str, float]:
    """Parse 'rs=0.1:gs=0.0:bs=-0.1' or 'colorbalance=rs=...' into floats."""
    t = (s or "").strip()
    if t.startswith("colorbalance="):
        t = t[len("colorbalance=") :]
    out: dict[str, float] = {"rs": 0.0, "gs": 0.0, "bs": 0.0}
    for part in t.split(":"):
        part = part.strip()
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        k, v = k.strip(), v.strip()
        if k in out:
            try:
                out[k] = float(v)
            except ValueError:
                pass
    return out


def color_temp_arc_anchors(color_temp_arc: dict) -> list[tuple[float, dict[str, float]]]:
    """Map narrative arc sections to (cumulative_pct_end, rgb deltas) in 0..100 space."""
    # Section end percentages from therapeutic_video_rules arc_section_pacing / VCE §6
    bounds = {
        "HOOK": 15.0,
        "BUILD": 55.0,
        "PEAK": 70.0,
        "RELEASE": 85.0,
        "RESOLVE": 100.0,
    }
    anchors: list[tuple[float, dict[str, float]]] = []
    order = ["HOOK", "BUILD", "PEAK", "RELEASE", "RESOLVE"]
    for sec in order:
        row = (color_temp_arc or {}).get(sec)
        if not isinstance(row, dict):
            continue
        cb = row.get("colorbalance")
        if not isinstance(cb, str):
            continue
        anchors.append((bounds[sec], parse_colorbalance_args(cb)))
    anchors.sort(key=lambda x: x[0])
    return anchors


def interpolate_colorbalance_at_pct(pct: float, anchors: list[tuple[float, dict[str, float]]]) -> dict[str, float]:
    """Piecewise linear rgb deltas over arc progress pct in [0,100]."""
    if not anchors:
        return {"rs": 0.0, "gs": 0.0, "bs": 0.0}
    pct = max(0.0, min(100.0, float(pct)))
    prev_pct = 0.0
    prev_cb = anchors[0][1]
    for end_pct, cb in anchors:
        if pct <= end_pct:
            span = max(1e-6, end_pct - prev_pct)
            t = (pct - prev_pct) / span
            return {
                "rs": prev_cb["rs"] + t * (cb["rs"] - prev_cb["rs"]),
                "gs": prev_cb["gs"] + t * (cb["gs"] - prev_cb["gs"]),
                "bs": prev_cb["bs"] + t * (cb["bs"] - prev_cb["bs"]),
            }
        prev_pct, prev_cb = end_pct, cb
    return dict(prev_cb)


def per_second_colorbalance_keyframes(
    duration_s: float,
    clip_start_global_s: float,
    timeline_duration_s: float,
    anchors: list[tuple[float, dict[str, float]]],
) -> list[tuple[int, dict[str, float]]]:
    """One sample per integer second for [0, duration_s)."""
    n = max(0, int(duration_s) + (1 if duration_s % 1 > 1e-6 else 0))
    out: list[tuple[int, dict[str, float]]] = []
    td = max(1e-6, float(timeline_duration_s))
    for i in range(n):
        g = clip_start_global_s + float(i)
        pct = max(0.0, min(100.0, (g / td) * 100.0))
        out.append((i, interpolate_colorbalance_at_pct(pct, anchors)))
    return out


def write_colorbalance_sendcmd_file(
    keyframes: list[tuple[int, dict[str, float]]],
    out_path: Path,
) -> Path:
    """
    Write an FFmpeg sendcmd-style command file (one command per second).
    Lines are suitable for use with the `sendcmd` filter's commands file syntax.
    See: https://ffmpeg.org/ffmpeg-filters.html#sendcmd
    """
    out_path = Path(out_path)
    lines: list[str] = [
        "# VCE §6.3 color temperature arc — per-second colorbalance targets",
        "# time_s colorbalance rs GS bs (gs in caps to mark channel — actual filter uses gs)",
    ]
    for sec, cb in keyframes:
        rs, gs, bs = cb["rs"], cb["gs"], cb["bs"]
        # sendcmd: time filter_name command args (pipe-separated channel commands in some builds).
        # We emit a conservative form: seconds + literal colorbalance= for manual merge / tooling.
        lines.append(f"{float(sec)} colorbalance rs {rs:.6f}|gs {gs:.6f}|bs {bs:.6f};")
    text = "\n".join(lines) + "\n"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    return out_path


def quality_tuning(quality: str) -> tuple[int, str]:
    """Return (crf_offset, preset_name_fragment).

    Values are loaded from config/video/render_defaults.yaml when available,
    falling back to hardcoded defaults for backward compatibility.
    """
    q = (quality or "standard").strip().lower()

    # Try loading from config (graceful fallback if missing or yaml unavailable)
    try:
        from scripts.video._config import load_yaml
        cfg = load_yaml("config/video/render_defaults.yaml")
        tiers = cfg.get("quality_tiers", {})
        if q in tiers:
            tier = tiers[q]
            return int(tier.get("crf_offset", 0)), str(tier.get("x264_preset", "medium"))
    except Exception:
        pass

    # Hardcoded fallback (matches render_defaults.yaml defaults)
    if q == "draft":
        return +4, "veryfast"
    if q == "high":
        return -2, "slow"
    return 0, "medium"


def platform_video_audio_argv(
    platform_key: str,
    base_crf: int,
    preset: str,
    pix_fmt: str = "yuv420p",
) -> tuple[list[str], list[str]]:
    """
    Return (video_args, audio_args) as argv fragments (no input/output paths).
    Platform keys: youtube, youtube_shorts, tiktok, instagram_reels, bilibili, douyin, webtoon
    """
    key = platform_key.strip().lower()
    v: list[str] = ["-c:v", "libx264", "-pix_fmt", pix_fmt]
    a: list[str] = ["-c:a", "aac", "-ar", "48000"]
    shortform_preset = "fast"  # TikTok-class vertical (spec §8)

    if key == "youtube":
        v += ["-preset", preset, "-crf", str(base_crf), "-profile:v", "high", "-movflags", "+faststart"]
        a += ["-b:a", "192k"]
    elif key == "youtube_shorts":
        v += ["-preset", preset, "-crf", str(base_crf), "-profile:v", "high", "-movflags", "+faststart"]
        a += ["-b:a", "192k"]
    elif key in ("tiktok", "instagram_reels", "douyin"):
        v += ["-preset", shortform_preset, "-crf", str(base_crf), "-profile:v", "main", "-movflags", "+faststart"]
        a += ["-b:a", "128k"]
    elif key == "bilibili":
        v += ["-preset", preset, "-crf", str(base_crf), "-profile:v", "high", "-movflags", "+faststart"]
        a += ["-b:a", "192k"]
    elif key == "webtoon":
        return [], []
    else:
        v += ["-preset", preset, "-crf", str(base_crf), "-profile:v", "high", "-movflags", "+faststart"]
        a += ["-b:a", "192k"]
    return v, a


def platform_duration_cap_argv(platform_key: str) -> list[str]:
    """Hard output duration caps for vertical / platform policies (encode phase)."""
    key = platform_key.strip().lower()
    if key == "youtube_shorts":
        return ["-t", "60"]
    if key == "instagram_reels":
        return ["-t", "90"]
    if key == "douyin":
        return ["-t", "300"]
    return []


def caption_policy_for_platform(platform_key: str) -> dict:
    """Burnt-in vs sidecar caption delivery hints (filter fragments are templates)."""
    key = platform_key.strip().lower()
    if key == "youtube":
        return {
            "mode": "srt_sidecar",
            "drawtext_template": None,
            "notes": "Prefer SRT sidecar; no burn-in for YouTube long-form.",
        }
    if key in ("youtube_shorts", "tiktok", "instagram_reels", "douyin"):
        return {
            "mode": "burn_in_drawtext",
            "fontfile": "Inter.ttf",
            "drawtext_template": (
                "drawtext=fontfile={fontfile}:fontsize=48:fontcolor=white:"
                "borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-100:text='{text}'"
            ),
            "cjk_fontfile": "NotoSansCJK.ttf",
            "cjk_fontsize": 40,
        }
    if key == "bilibili":
        return {
            "mode": "ass_danmaku_safe",
            "ass_margins": {"top_px": 120, "bottom_px": 180},
            "notes": "Use ASS with PlayRes and MarginV for danmaku-safe bands; zh required.",
        }
    if key == "webtoon":
        return {"mode": "in_panel", "notes": "WebP panels via cwebp per asset, not video burn-in."}
    return {"mode": "burn_in_drawtext", "drawtext_template": "drawtext=text='{text}'"}


def webp_panel_argv_template() -> list[str]:
    """Example cwebp argv list template for one panel (paths filled by caller)."""
    return ["cwebp", "-q", "90", "{in_path}", "-o", "{out_path}"]


def filter_complex_balanced_brackets(s: str) -> bool:
    """Lightweight structural check: square brackets for stream labels balance."""
    depth = 0
    for ch in s:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def filter_complex_no_broken_single_quotes(s: str) -> bool:
    """Ensure count of single quotes is even (FFmpeg expressions often quote)."""
    return s.count("'") % 2 == 0


def validate_filter_complex_structure(s: str) -> tuple[bool, str]:
    if not s or not s.strip():
        return False, "empty"
    if not filter_complex_balanced_brackets(s):
        return False, "unbalanced_brackets"
    if not filter_complex_no_broken_single_quotes(s):
        return False, "odd_quotes"
    # Disallow backticks/subshell injection; ';' and '|' are valid inside filter_complex.
    if re.search(r"[`$]", s):
        return False, "shell_metachar"
    return True, "ok"


def is_list_of_str(cmd: Iterable[str]) -> bool:
    return isinstance(cmd, list) and all(isinstance(x, str) for x in cmd)


# ── P0 upgrade helpers ────────────────────────────────────────────────────────


def build_xfade_filter(
    clip_paths: list[Path],
    transition: str = "dissolve",
    duration_s: float = 0.5,
    fps: int = 24,
) -> tuple[list[str], list[str]]:
    """Build an FFmpeg filter_complex and input list for xfade transitions between clips.

    Returns (input_args, filter_complex_parts) suitable for combining into a full
    FFmpeg command.  The caller must append ``-map "[vout]"`` (or last chain label)
    and output path.

    *clip_paths* — ordered list of clip files.
    *transition* — any xfade transition name (dissolve, fade, wipeleft, …).
    *duration_s* — crossfade overlap in seconds; must be shorter than the shortest clip.
    *fps* — frame rate (used to compute offset in frames).

    Returns empty lists if len(clip_paths) < 2 (caller falls back to concat demuxer).
    """
    if len(clip_paths) < 2:
        return [], []

    input_args: list[str] = []
    for p in clip_paths:
        input_args.extend(["-i", str(p)])

    # We need the duration of each clip to compute xfade offset accurately.
    # Fall back to probing via ffprobe; if unavailable use a rough estimate.
    durations: list[float] = []
    for p in clip_paths:
        try:
            import subprocess as _sp
            r = _sp.run(
                [
                    "ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(p),
                ],
                capture_output=True, text=True, timeout=10,
            )
            durations.append(float(r.stdout.strip()))
        except Exception:
            durations.append(5.0)  # safe fallback

    n = len(clip_paths)
    # Running cumulative offset in seconds (end of previous chain minus overlap)
    offsets: list[float] = []
    running = 0.0
    for i in range(n - 1):
        running += max(0.01, durations[i] - duration_s)
        offsets.append(running)

    parts: list[str] = []
    # Label inputs
    for i in range(n):
        parts.append(f"[{i}:v]setpts=PTS-STARTPTS[v{i}]")

    cur_label = "v0"
    for i in range(n - 1):
        next_label = f"v{i + 1}"
        out_label = f"xf{i}" if i < n - 2 else "vout"
        offset = offsets[i]
        parts.append(
            f"[{cur_label}][{next_label}]xfade=transition={transition}"
            f":duration={duration_s:.3f}:offset={offset:.3f}[{out_label}]"
        )
        cur_label = out_label

    return input_args, parts


def build_lut3d_filter(lut_path: str | Path) -> str:
    """Return FFmpeg filter fragment applying a 3D LUT with correct RGB chain.

    FFmpeg lut3d requires RGB input.  This helper wraps the filter with the
    necessary format conversions:  ``format=rgb24,lut3d=<path>,format=yuv420p``.

    The caller inserts this fragment into a filter_complex or -vf chain after
    the main video stream and before encoding.
    """
    safe_path = str(lut_path).replace("\\", "/")
    # Escape colons (Windows paths, though Linux/macOS rarely need this)
    safe_path = safe_path.replace(":", "\\:")
    return f"format=rgb24,lut3d={safe_path},format=yuv420p"


def build_noise_filter(intensity: int = 15) -> str | None:
    """Return FFmpeg noise filter fragment for film grain effect.

    *intensity* maps to ``c0s`` (luma noise strength).  ``c0f=t+u`` gives
    temporal + uniform noise for organic grain texture.
    Returns None when intensity <= 0 (disabled).
    """
    if intensity <= 0:
        return None
    return f"noise=c0s={intensity}:c0f=t+u"


def build_vignette_filter(angle: str | float = "PI/5") -> str | None:
    """Return FFmpeg vignette filter fragment.

    *angle* is the cone half-angle string or float (radians).  FFmpeg accepts
    expressions like ``PI/5`` directly.  Returns None when angle is 0 or "0".
    """
    a = str(angle).strip()
    if a in ("0", "0.0", ""):
        return None
    return f"vignette={a}"
