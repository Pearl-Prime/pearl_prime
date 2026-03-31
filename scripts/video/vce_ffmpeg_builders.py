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
    """Return (crf_offset, preset_name_fragment)."""
    q = (quality or "standard").strip().lower()
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
