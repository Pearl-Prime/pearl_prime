#!/usr/bin/env python3
"""Generate teacher showcase videos: YouTube (10min, 16:9) + TikTok (90s, 9:16).

Descript-style audiobook videos: black background + white text + waveform + audio.
Uses FFmpeg directly — no external API needed.

Usage:
  python3 scripts/video/generate_teacher_showcase_videos.py
  python3 scripts/video/generate_teacher_showcase_videos.py --teacher ahjan
  python3 scripts/video/generate_teacher_showcase_videos.py --dry-run
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AUDIO_DIR = REPO_ROOT / "artifacts" / "showcase" / "audio"
YT_OUTPUT = REPO_ROOT / "artifacts" / "showcase" / "video" / "youtube"
TT_OUTPUT = REPO_ROOT / "artifacts" / "showcase" / "video" / "tiktok"

FFMPEG = os.environ.get("FFMPEG", "/opt/homebrew/bin/ffmpeg")

# Topic assignments from plan
TEACHER_YT_TOPIC = {
    "ahjan": "burnout", "adi_da": "courage", "joshin": "overthinking",
    "junko": "burnout", "maat": "self_worth", "master_feung": "somatic_healing",
    "master_sha": "somatic_healing", "master_wu": "burnout", "miki": "sleep_anxiety",
    "omote": "self_worth", "pamela_fellows": "somatic_healing", "ra": "depression",
    "sai_ma": "compassion_fatigue",
}

TEACHER_TT_TOPIC = {
    "ahjan": "self_worth", "adi_da": "boundaries", "joshin": "burnout",
    "junko": "courage", "maat": "social_anxiety", "master_feung": "courage",
    "master_sha": "depression", "master_wu": "boundaries", "miki": "anxiety",
    "omote": "social_anxiety", "pamela_fellows": "financial_anxiety", "ra": "courage",
    "sai_ma": "depression",
}

# Audiobook topic (for audio file lookup)
TEACHER_AUDIO_TOPIC = {
    "ahjan": "depression", "adi_da": "depression", "joshin": "sleep_anxiety",
    "junko": "imposter_syndrome", "maat": "courage", "master_feung": "self_worth",
    "master_sha": "anxiety", "master_wu": "self_worth", "miki": "compassion_fatigue",
    "omote": "imposter_syndrome", "pamela_fellows": "burnout", "ra": "self_worth",
    "sai_ma": "boundaries",
}

TEACHER_NAMES = {
    "ahjan": "Ahjan", "adi_da": "Adi Da", "joshin": "Joshin",
    "junko": "Junko", "maat": "Maat", "master_feung": "Master Feung",
    "master_sha": "Master Sha", "master_wu": "Master Wu", "miki": "Miki",
    "omote": "Omote", "pamela_fellows": "Pamela Fellows", "ra": "Ra",
    "sai_ma": "Sai Ma",
}

TEACHER_BRAND = {
    "ahjan": "Stillness Press", "adi_da": "Awakening Press", "joshin": "Clear Seeing Books",
    "junko": "Bare Form Books", "maat": "Feather & Scale Press", "master_feung": "Root & Meridian Press",
    "master_sha": "Night Architecture Books", "master_wu": "Iron Gate Press", "miki": "Present Tense Books",
    "omote": "Held Ground Press", "pamela_fellows": "Felt Sense Publishing", "ra": "Ember & Ash Publishing",
    "sai_ma": "Open Vessel Press",
}


def _render_video(
    audio_path: Path,
    output_path: Path,
    title: str,
    author: str,
    brand: str,
    width: int,
    height: int,
    max_duration: int | None = None,
    dry_run: bool = False,
) -> bool:
    """Render Descript-style audiobook video via FFmpeg."""
    if dry_run:
        print(f"    [DRY-RUN] → {output_path.name}")
        return True

    if not audio_path.exists():
        print(f"    ERROR: Audio not found: {audio_path}")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get audio duration
    probe = subprocess.run(
        [FFMPEG, "-i", str(audio_path), "-hide_banner"],
        capture_output=True, text=True,
    )
    duration_match = None
    for line in probe.stderr.splitlines():
        if "Duration:" in line:
            import re
            m = re.search(r"Duration:\s*(\d+):(\d+):(\d+)", line)
            if m:
                duration_match = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
    if duration_match is None:
        duration_match = max_duration or 600

    actual_dur = min(duration_match, max_duration) if max_duration else duration_match

    # Font size scales with resolution
    title_size = max(24, height // 20)
    author_size = max(16, height // 35)
    brand_size = max(12, height // 45)

    # Escape text for FFmpeg drawtext
    def esc(t: str) -> str:
        return t.replace("'", "'\\''").replace(":", "\\:")

    # Build FFmpeg filter chain: black bg + text overlays + waveform
    filter_parts = [
        f"color=c=black:s={width}x{height}:r=24:d={actual_dur}[bg]",
        f"[1:a]showwaves=s={width}x{height//6}:mode=cline:rate=24:colors=white@0.3[wave]",
        f"[bg][wave]overlay=0:{height - height//6}[base]",
        (
            f"[base]drawtext=text='{esc(title)}':fontsize={title_size}:"
            f"fontcolor=white:x=(w-tw)/2:y=h*0.15:fontfile=/System/Library/Fonts/Helvetica.ttc,"
            f"drawtext=text='{esc(author)}':fontsize={author_size}:"
            f"fontcolor=0xD4A574:x=(w-tw)/2:y=h*0.55:fontfile=/System/Library/Fonts/Helvetica.ttc,"
            f"drawtext=text='{esc(brand)}':fontsize={brand_size}:"
            f"fontcolor=0x888888:x=(w-tw)/2:y=h*0.65:fontfile=/System/Library/Fonts/Helvetica.ttc"
        ),
    ]

    filter_complex = ";".join(filter_parts)

    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi", "-i", f"color=c=black:s={width}x{height}:r=24:d={actual_dur}",
        "-i", str(audio_path),
        "-t", str(actual_dur),
        "-filter_complex", filter_complex,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "27",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-shortest",
        str(output_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            # Fallback: simpler filter without waveform
            cmd_simple = [
                FFMPEG, "-y",
                "-i", str(audio_path),
                "-t", str(actual_dur),
                "-f", "lavfi", "-i", f"color=c=black:s={width}x{height}:r=24:d={actual_dur}",
                "-filter_complex",
                (
                    f"[1:v]drawtext=text='{esc(title)}':fontsize={title_size}:"
                    f"fontcolor=white:x=(w-tw)/2:y=h*0.3:fontfile=/System/Library/Fonts/Helvetica.ttc,"
                    f"drawtext=text='{esc(author)}':fontsize={author_size}:"
                    f"fontcolor=0xD4A574:x=(w-tw)/2:y=h*0.55:fontfile=/System/Library/Fonts/Helvetica.ttc,"
                    f"drawtext=text='{esc(brand)}':fontsize={brand_size}:"
                    f"fontcolor=0x888888:x=(w-tw)/2:y=h*0.65:fontfile=/System/Library/Fonts/Helvetica.ttc[v]"
                ),
                "-map", "[v]", "-map", "0:a",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "27",
                "-c:a", "aac", "-b:a", "128k",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-shortest",
                str(output_path),
            ]
            result = subprocess.run(cmd_simple, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"    ERROR: FFmpeg failed: {result.stderr[-300:]}")
                return False

        if output_path.exists() and output_path.stat().st_size > 10000:
            size_mb = output_path.stat().st_size / 1048576
            print(f"    OK ({size_mb:.1f} MB) → {output_path.name}")
            return True
        print("    ERROR: Output file too small or missing")
        return False
    except subprocess.TimeoutExpired:
        print("    ERROR: FFmpeg timed out")
        return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate teacher showcase videos.")
    parser.add_argument("--teacher", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    teachers = list(TEACHER_NAMES.keys())
    if args.teacher:
        teachers = [t for t in teachers if t == args.teacher]

    ok = 0
    total = 0

    for tid in teachers:
        name = TEACHER_NAMES[tid]
        brand = TEACHER_BRAND[tid]
        audio_topic = TEACHER_AUDIO_TOPIC[tid]
        yt_topic = TEACHER_YT_TOPIC[tid]
        tt_topic = TEACHER_TT_TOPIC[tid]

        full_audio = AUDIO_DIR / f"{tid}_{audio_topic}.mp3"
        hook_audio = AUDIO_DIR / f"{tid}_{audio_topic}_hook.mp3"

        # YouTube 10-min (16:9)
        yt_title = f"{yt_topic.replace('_', ' ').title()} — {name}"
        yt_out = YT_OUTPUT / f"{tid}_{yt_topic}_youtube.mp4"
        print(f"\n  {tid} YouTube ({yt_topic}):")
        total += 1
        if _render_video(full_audio, yt_out, yt_title, name, brand, 1920, 1080, 600, args.dry_run):
            ok += 1

        # TikTok 90s (9:16)
        tt_title = f"{tt_topic.replace('_', ' ').title()}"
        tt_out = TT_OUTPUT / f"{tid}_{tt_topic}_tiktok.mp4"
        print(f"  {tid} TikTok ({tt_topic}):")
        total += 1
        if _render_video(hook_audio, tt_out, tt_title, name, brand, 1080, 1920, 90, args.dry_run):
            ok += 1

    print(f"\n{'='*50}")
    print(f"Generated: {ok}/{total} videos")
    return 0 if ok == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
