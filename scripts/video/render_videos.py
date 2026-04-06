#!/usr/bin/env python3
"""
render_videos.py — Render 13 YouTube + 13 TikTok videos from video_plan.json files.

YouTube: 10 min, 1920x1080, full narration, Ken Burns backgrounds, ambient SFX.
TikTok:  90 sec, 1080x1920, HOOK segment only, bolder text, faster pacing.

Uses FFmpeg subprocess calls (no Python bindings, no ElevenLabs).

Usage:
    python3 scripts/video/render_videos.py
    python3 scripts/video/render_videos.py --dry-run
    python3 scripts/video/render_videos.py --teachers adi_da,ra
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Paths (all relative to repo root)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]

PIPELINE_DIR = REPO_ROOT / "artifacts" / "pipeline_examples"
VIDEO_BANK_DIR = REPO_ROOT / "brand-wizard-app" / "public" / "assets" / "video_bank"
SFX_DIR = REPO_ROOT / "assets" / "sfx_bank"
SFX_AMBIENT_DIR = SFX_DIR / "nature_ambient"
SFX_SOMATIC_DIR = SFX_DIR / "body_somatic"

OUT_YT_DIR = REPO_ROOT / "artifacts" / "videos" / "youtube"
OUT_TT_DIR = REPO_ROOT / "artifacts" / "videos" / "tiktok"

# ---------------------------------------------------------------------------
# Theme colours
# ---------------------------------------------------------------------------
BG_HEX = "0e0a06"
AMBER_HEX = "d97706"
TEXT_HEX = "faf6f0"

# ---------------------------------------------------------------------------
# Teacher display names
# ---------------------------------------------------------------------------
TEACHER_DISPLAY: dict[str, str] = {
    "adi_da": "Adi Da Samraj",
    "ahjan": "Ahjan",
    "joshin": "Joshin",
    "junko": "Junko",
    "maat": "Ma'at",
    "master_feung": "Master Feung",
    "master_sha": "Master Sha",
    "master_wu": "Master Wu",
    "miki": "Miki",
    "omote": "Omote",
    "pamela_fellows": "Pamela Fellows",
    "ra": "Ra",
    "sai_ma": "Sai Ma",
}

ALL_TEACHERS = list(TEACHER_DISPLAY.keys())

# ---------------------------------------------------------------------------
# Topic → video_bank background mapping (with fallback)
# ---------------------------------------------------------------------------
TOPIC_BG_MAP: dict[str, list[str]] = {
    "anxiety": ["vb_anxiety_calm.png"],
    "self_worth": ["vb_abstract_warmth.png"],
    "grief": ["vb_nature_forest.png"],
    "overthinking": ["vb_abstract_warmth.png"],
    "burnout": ["vb_nature_forest.png"],
    "boundaries": ["vb_abstract_warmth.png"],
    "courage": ["vb_nature_forest.png"],
    "imposter_syndrome": ["vb_anxiety_calm.png", "vb_abstract_warmth.png"],
    "sleep_anxiety": ["vb_nature_forest.png"],
}
FALLBACK_BG = "vb_abstract_warmth.png"


def _resolve_backgrounds(topic: str) -> list[Path]:
    """Return list of background image paths for a topic, verified to exist."""
    candidates = TOPIC_BG_MAP.get(topic, [FALLBACK_BG])
    # Also add all available video_bank images for variety
    all_vb = sorted(VIDEO_BANK_DIR.glob("vb_*.png"))
    resolved: list[Path] = []
    # Prioritise topic-specific images
    for name in candidates:
        p = VIDEO_BANK_DIR / name
        if p.exists():
            resolved.append(p)
    # Fill remaining from all_vb
    for p in all_vb:
        if p not in resolved:
            resolved.append(p)
    if not resolved:
        return []
    return resolved


def _resolve_ambient_sfx() -> Optional[Path]:
    """Pick an ambient SFX file (.mp3 preferred) from nature_ambient/."""
    if not SFX_AMBIENT_DIR.exists():
        return None
    mp3s = sorted(SFX_AMBIENT_DIR.glob("*.mp3"))
    if mp3s:
        return mp3s[0]
    wavs = sorted(SFX_AMBIENT_DIR.glob("*.wav"))
    return wavs[0] if wavs else None


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def _escape_ffmpeg_text(text: str) -> str:
    """Escape special characters for FFmpeg drawtext filter."""
    # FFmpeg drawtext requires escaping: \ ' : %
    text = text.replace("\\", "\\\\\\\\")
    text = text.replace("'", "\u2019")  # curly apostrophe avoids escaping
    text = text.replace(":", "\\:")
    text = text.replace("%", "%%")
    text = text.replace('"', '\\"')
    text = text.replace("\n", " ")
    return text


def _wrap_text(text: str, width: int = 55) -> str:
    """Word-wrap text for subtitle display."""
    lines = textwrap.wrap(text, width=width)
    return "\n".join(lines)


def _wrap_text_tiktok(text: str, width: int = 30) -> str:
    """Word-wrap text for TikTok (narrower, bolder)."""
    lines = textwrap.wrap(text, width=width)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# FFmpeg command builders
# ---------------------------------------------------------------------------

def _build_title_card_cmd(
    output_path: Path,
    teacher_name: str,
    title: str,
    duration: float,
    width: int,
    height: int,
) -> list[str]:
    """Generate a title card video clip (solid colour + text)."""
    safe_teacher = _escape_ffmpeg_text(teacher_name)
    safe_title = _escape_ffmpeg_text(title)

    # Title card: dark background, teacher name in amber, book title in white
    filter_str = (
        f"color=c=0x{BG_HEX}:s={width}x{height}:d={duration}:r=30,"
        f"drawtext=text='{safe_teacher}'"
        f":fontsize={int(height * 0.05)}"
        f":fontcolor=0x{AMBER_HEX}"
        f":x=(w-text_w)/2:y=(h/2)-text_h-20"
        f":font=Arial,"
        f"drawtext=text='{safe_title}'"
        f":fontsize={int(height * 0.04)}"
        f":fontcolor=0x{TEXT_HEX}"
        f":x=(w-text_w)/2:y=(h/2)+20"
        f":font=Arial"
    )

    return [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", filter_str,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-t", str(duration),
        str(output_path),
    ]


def _build_end_card_cmd(
    output_path: Path,
    duration: float,
    width: int,
    height: int,
) -> list[str]:
    """Generate an end card with Pearl Prime branding."""
    brand = _escape_ffmpeg_text("Pearl Prime")
    cta = _escape_ffmpeg_text("Subscribe for daily practices")

    filter_str = (
        f"color=c=0x{BG_HEX}:s={width}x{height}:d={duration}:r=30,"
        f"drawtext=text='{brand}'"
        f":fontsize={int(height * 0.06)}"
        f":fontcolor=0x{AMBER_HEX}"
        f":x=(w-text_w)/2:y=(h/2)-text_h-30"
        f":font=Arial,"
        f"drawtext=text='{cta}'"
        f":fontsize={int(height * 0.03)}"
        f":fontcolor=0x{TEXT_HEX}"
        f":x=(w-text_w)/2:y=(h/2)+30"
        f":font=Arial"
    )

    return [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", filter_str,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-t", str(duration),
        str(output_path),
    ]


def _build_segment_clip_cmd(
    output_path: Path,
    bg_image: Path,
    text: str,
    duration: float,
    width: int,
    height: int,
    is_tiktok: bool = False,
) -> list[str]:
    """Build a single narration-segment clip: Ken Burns bg + text overlay."""
    wrapped = _wrap_text_tiktok(text, 28) if is_tiktok else _wrap_text(text, 50)
    safe_text = _escape_ffmpeg_text(wrapped)

    # Ken Burns: slow zoom from 1.0 to 1.15 over the duration
    # zoompan filter: z starts at 1.0, increases to 1.15
    fps = 30
    total_frames = int(duration * fps)
    zoom_expr = f"min(1+0.15*on/{total_frames},1.15)"

    # Font sizes
    if is_tiktok:
        font_size = int(height * 0.028)
        box_y = f"h-h*0.35"
    else:
        font_size = int(height * 0.028)
        box_y = f"h-h*0.25"

    # Build complex filter
    # 1. Scale bg image to fill frame, then apply zoompan for Ken Burns
    # 2. Overlay text with semi-transparent box
    vf = (
        f"scale={width * 2}:{height * 2},"
        f"zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={total_frames}:s={width}x{height}:fps={fps},"
        f"fade=t=in:st=0:d=1,fade=t=out:st={max(0, duration - 1)}:d=1,"
        f"drawbox=x=0:y={box_y}:w=iw:h=ih*0.35:color=0x{BG_HEX}@0.7:t=fill,"
        f"drawtext=text='{safe_text}'"
        f":fontsize={font_size}"
        f":fontcolor=0x{TEXT_HEX}"
        f":x=(w-text_w)/2:y={box_y}+20"
        f":font=Arial"
        f":line_spacing=8"
    )

    return [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(bg_image),
        "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-t", str(duration),
        str(output_path),
    ]


def _build_concat_with_audio_cmd(
    clip_list_file: Path,
    audio_file: Optional[Path],
    output_path: Path,
    total_duration: float,
) -> list[str]:
    """Concatenate clips and mix in looped ambient audio."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(clip_list_file),
    ]
    if audio_file and audio_file.exists():
        cmd.extend([
            "-stream_loop", "-1",  # loop audio
            "-i", str(audio_file),
        ])
        cmd.extend([
            "-filter_complex",
            f"[1:a]afade=t=in:st=0:d=3,afade=t=out:st={max(0, total_duration - 3)}:d=3,"
            f"volume=0.15[bg];[bg]atrim=0:{total_duration}[ao]",
            "-map", "0:v", "-map", "[ao]",
        ])
    cmd.extend([
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        "-t", str(total_duration),
        str(output_path),
    ])
    return cmd


# ---------------------------------------------------------------------------
# Render orchestrator
# ---------------------------------------------------------------------------

def render_video(
    plan: dict,
    platform: str,
    dry_run: bool = False,
) -> Optional[Path]:
    """
    Render a single video (youtube or tiktok) from a video plan.

    Returns the output path on success, None on skip/failure.
    """
    teacher_id = plan["teacher_id"]
    topic = plan.get("topic", "general")
    title = plan.get("title", "Untitled")
    segments = plan.get("narration_segments", [])
    teacher_name = TEACHER_DISPLAY.get(teacher_id, teacher_id.replace("_", " ").title())

    if not segments:
        print(f"  [SKIP] No narration segments for {teacher_id}")
        return None

    # Platform params
    if platform == "youtube":
        width, height = 1920, 1080
        total_duration = 600.0  # 10 min
        title_dur = 3.0
        end_dur = 5.0
        out_dir = OUT_YT_DIR
        # Use all segments
        render_segments = segments
    else:  # tiktok
        width, height = 1080, 1920
        total_duration = 90.0
        title_dur = 2.0
        end_dur = 3.0
        out_dir = OUT_TT_DIR
        # Only HOOK segment
        render_segments = [s for s in segments if s.get("type") == "HOOK"]
        if not render_segments:
            render_segments = segments[:1]

    out_dir.mkdir(parents=True, exist_ok=True)

    # Resolve backgrounds
    backgrounds = _resolve_backgrounds(topic)
    if not backgrounds:
        print(f"  [WARN] No background images found, using solid colour fallback")
        backgrounds = []

    # Resolve ambient audio
    ambient = _resolve_ambient_sfx()

    # Calculate segment durations
    content_duration = total_duration - title_dur - end_dur
    n_segs = len(render_segments)
    seg_duration = content_duration / n_segs

    # Work directory for intermediate clips
    slug = f"{teacher_id}_{topic}_{platform}"
    work_dir = out_dir / f".work_{slug}"
    work_dir.mkdir(parents=True, exist_ok=True)

    clip_paths: list[Path] = []
    all_cmds: list[tuple[str, list[str]]] = []

    # 1. Title card
    title_clip = work_dir / "00_title.mp4"
    cmd = _build_title_card_cmd(title_clip, teacher_name, title, title_dur, width, height)
    all_cmds.append(("Title card", cmd))
    clip_paths.append(title_clip)

    # 2. Segment clips
    for i, seg in enumerate(render_segments):
        seg_clip = work_dir / f"{i + 1:02d}_seg_{seg.get('type', 'UNK').lower()}.mp4"
        # Cycle through backgrounds
        if backgrounds:
            bg = backgrounds[i % len(backgrounds)]
        else:
            # Create a solid-colour fallback — use title card generator trick
            bg = None

        text = seg.get("text", "")
        # Truncate text for display (keep first ~300 chars for readability)
        display_text = text[:400] + "..." if len(text) > 400 else text

        if bg and bg.exists():
            cmd = _build_segment_clip_cmd(
                seg_clip, bg, display_text, seg_duration, width, height,
                is_tiktok=(platform == "tiktok"),
            )
        else:
            # Solid colour fallback with text only
            safe_text = _escape_ffmpeg_text(_wrap_text(display_text, 50))
            filter_str = (
                f"color=c=0x{BG_HEX}:s={width}x{height}:d={seg_duration}:r=30,"
                f"drawtext=text='{safe_text}'"
                f":fontsize={int(height * 0.028)}"
                f":fontcolor=0x{TEXT_HEX}"
                f":x=(w-text_w)/2:y=(h-text_h)/2"
                f":font=Arial:line_spacing=8"
            )
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", filter_str,
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-t", str(seg_duration),
                str(seg_clip),
            ]

        all_cmds.append((f"Segment {i + 1} ({seg.get('type', '?')})", cmd))
        clip_paths.append(seg_clip)

    # 3. End card
    end_clip = work_dir / "99_end.mp4"
    cmd = _build_end_card_cmd(end_clip, end_dur, width, height)
    all_cmds.append(("End card", cmd))
    clip_paths.append(end_clip)

    # 4. Concat list file
    concat_file = work_dir / "concat.txt"
    concat_content = "\n".join(f"file '{p}'" for p in clip_paths)

    # 5. Final concat + audio mix
    output_path = out_dir / f"{slug}.mp4"
    concat_cmd = _build_concat_with_audio_cmd(concat_file, ambient, output_path, total_duration)
    all_cmds.append(("Final concat + audio", concat_cmd))

    # Execute or print
    if dry_run:
        print(f"\n  [DRY-RUN] {platform.upper()} — {teacher_name} — {title}")
        for label, cmd in all_cmds:
            print(f"    {label}:")
            print(f"      {' '.join(cmd)}\n")
        print(f"    Concat list ({concat_file}):")
        print(f"      {concat_content}\n")
        print(f"    Output: {output_path}")
        return output_path

    # Actually run
    print(f"\n  [RENDER] {platform.upper()} — {teacher_name} — {title}")
    t0 = time.time()

    for label, cmd in all_cmds[:-1]:  # all except final concat
        print(f"    {label}...", end=" ", flush=True)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                print(f"FAILED (rc={result.returncode})")
                stderr_tail = result.stderr[-500:] if result.stderr else "(no stderr)"
                print(f"      stderr: {stderr_tail}")
                return None
            print("OK")
        except FileNotFoundError:
            print("FAILED — ffmpeg not found on PATH")
            return None
        except subprocess.TimeoutExpired:
            print("FAILED — timeout (300s)")
            return None

    # Write concat list
    concat_file.write_text(concat_content, encoding="utf-8")

    # Run final concat
    label, cmd = all_cmds[-1]
    print(f"    {label}...", end=" ", flush=True)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            print(f"FAILED (rc={result.returncode})")
            stderr_tail = result.stderr[-500:] if result.stderr else "(no stderr)"
            print(f"      stderr: {stderr_tail}")
            return None
        print("OK")
    except FileNotFoundError:
        print("FAILED — ffmpeg not found on PATH")
        return None
    except subprocess.TimeoutExpired:
        print("FAILED — timeout (600s)")
        return None

    elapsed = time.time() - t0
    file_size_mb = output_path.stat().st_size / (1024 * 1024) if output_path.exists() else 0
    print(f"    Done in {elapsed:.1f}s — {file_size_mb:.1f} MB — {output_path}")

    # Cleanup intermediate clips (keep concat list for debugging)
    for p in clip_paths:
        if p.exists():
            p.unlink()

    return output_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render YouTube + TikTok videos from video plan JSONs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print FFmpeg commands without executing.",
    )
    parser.add_argument(
        "--teachers",
        type=str,
        default=None,
        help="Comma-separated list of teacher IDs to render (default: all 13).",
    )
    parser.add_argument(
        "--platform",
        type=str,
        choices=["youtube", "tiktok", "both"],
        default="both",
        help="Which platform(s) to render (default: both).",
    )
    args = parser.parse_args()

    teachers = args.teachers.split(",") if args.teachers else ALL_TEACHERS
    platforms = ["youtube", "tiktok"] if args.platform == "both" else [args.platform]

    # Verify ffmpeg is available (unless dry-run)
    if not args.dry_run:
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                print("[ERROR] ffmpeg returned non-zero. Is it installed correctly?")
                sys.exit(1)
            version_line = result.stdout.split("\n")[0] if result.stdout else "unknown"
            print(f"[OK] FFmpeg: {version_line}")
        except FileNotFoundError:
            print("[ERROR] ffmpeg not found on PATH. Install it first.")
            sys.exit(1)

    # Ensure output dirs
    OUT_YT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_TT_DIR.mkdir(parents=True, exist_ok=True)

    # Collect plans
    plans: list[tuple[str, dict]] = []
    for teacher_id in teachers:
        plan_path = PIPELINE_DIR / teacher_id / "video_plan.json"
        if not plan_path.exists():
            print(f"[WARN] No video_plan.json for {teacher_id} at {plan_path}")
            continue
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                plan = json.load(f)
            plans.append((teacher_id, plan))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[WARN] Failed to load {plan_path}: {exc}")
            continue

    if not plans:
        print("[ERROR] No valid video plans found. Nothing to render.")
        sys.exit(1)

    print(f"\n{'=' * 60}")
    print(f"Pearl Prime Video Renderer")
    print(f"{'=' * 60}")
    print(f"Teachers:   {len(plans)}")
    print(f"Platforms:  {', '.join(platforms)}")
    print(f"Mode:       {'DRY-RUN' if args.dry_run else 'LIVE RENDER'}")
    print(f"YouTube →   {OUT_YT_DIR}")
    print(f"TikTok  →   {OUT_TT_DIR}")
    print(f"{'=' * 60}")

    # Check assets
    bg_count = len(list(VIDEO_BANK_DIR.glob("vb_*.png"))) if VIDEO_BANK_DIR.exists() else 0
    sfx_count = len(list(SFX_AMBIENT_DIR.glob("*.*"))) if SFX_AMBIENT_DIR.exists() else 0
    print(f"Backgrounds: {bg_count} images in video_bank/")
    print(f"Ambient SFX: {sfx_count} files in sfx_bank/nature_ambient/")

    results: dict[str, list[str]] = {"success": [], "failed": [], "skipped": []}

    for teacher_id, plan in plans:
        for platform in platforms:
            tag = f"{teacher_id}/{platform}"
            try:
                out = render_video(plan, platform, dry_run=args.dry_run)
                if out:
                    results["success"].append(tag)
                else:
                    results["failed"].append(tag)
            except Exception as exc:
                print(f"  [ERROR] {tag}: {exc}")
                results["failed"].append(tag)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"RENDER SUMMARY")
    print(f"{'=' * 60}")
    print(f"Success: {len(results['success'])}")
    for tag in results["success"]:
        print(f"  [OK] {tag}")
    if results["failed"]:
        print(f"Failed:  {len(results['failed'])}")
        for tag in results["failed"]:
            print(f"  [FAIL] {tag}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
