#!/usr/bin/env python3
"""Render Descript-style audiobook videos.

Produces videos with: white serif text on black, word-by-word karaoke
highlighting, amplitude-reactive waveform at bottom, synced to audio.

Usage:
    # Full chapter (16:9 long-form for YouTube)
    python3 scripts/video/render_audiobook.py \
        --audio chapter_01.mp3 \
        --transcript chapter_01.txt \
        --format long \
        -o chapter_01_video.mp4

    # Short clip (9:16 for Shorts/TikTok)
    python3 scripts/video/render_audiobook.py \
        --audio chapter_01.mp3 \
        --transcript chapter_01.txt \
        --format short --clip-start 45 --clip-end 105 \
        -o chapter_01_short.mp4

    # With style preset
    python3 scripts/video/render_audiobook.py \
        --audio chapter.mp3 --transcript chapter.txt \
        --style warm --format long -o warm_chapter.mp4
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"

sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def _get_audio_duration(audio: Path) -> float:
    r = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", str(audio)],
        capture_output=True, text=True,
    )
    return float(json.loads(r.stdout)["format"]["duration"])


def _load_style(style_name: str) -> dict:
    cfg_path = REPO_ROOT / "config" / "video" / "audiobook_style.yaml"
    defaults = {
        "background_color": "#000000",
        "font_family": "Georgia",
        "font_size_16_9": 72,
        "font_size_9_16": 52,
        "text_color": "#FFFFFF",
        "text_color_past": "#666666",
        "text_margin_x_pct": 8,
        "text_margin_y_pct": 8,
        "max_words_per_screen": 6,
        "waveform_height_pct": 15,
        "waveform_color": "#888888",
        "waveform_mode": "cline",
    }
    if yaml and cfg_path.is_file():
        cfg = yaml.safe_load(cfg_path.read_text())
        style = cfg.get("styles", {}).get(style_name, cfg["styles"].get("default", {}))
        defaults.update(style)
    return defaults


def _format_resolution(fmt: str) -> tuple[int, int, int]:
    """Returns (width, height, fps) for format."""
    if fmt == "short":
        return 1080, 1920, 30
    return 1920, 1080, 24


def render_audiobook(
    audio: Path,
    transcript: Path | None,
    output: Path,
    format_key: str = "long",
    style_name: str = "default",
    clip_start: float | None = None,
    clip_end: float | None = None,
    quality: str = "standard",
    whisper_model: str = "base",
) -> Path:
    """Render a Descript-style audiobook video.

    1. Align transcript to audio (Whisper or WPM fallback)
    2. Generate karaoke ASS subtitles
    3. FFmpeg: black bg + waveform + ASS + audio → MP4
    """
    from scripts.video.align_transcript import align
    from scripts.video.generate_karaoke_ass import generate_ass

    w, h, fps = _format_resolution(format_key)
    style = _load_style(style_name)
    duration = _get_audio_duration(audio)

    # Clip boundaries
    ss = clip_start or 0
    to = clip_end or duration
    clip_dur = to - ss

    print(f"Rendering audiobook video: {clip_dur:.1f}s, {w}x{h}@{fps}fps, style={style_name}")

    # Step 1: Align transcript to audio
    transcript_text = transcript.read_text(encoding="utf-8").strip() if transcript else None
    print("  Aligning transcript...")
    words = align(audio, transcript_text, whisper_model)

    # Filter words to clip range
    if clip_start or clip_end:
        words = [w for w in words if w["end"] > ss and w["start"] < to]
        # Adjust timestamps relative to clip start
        for word in words:
            word["start"] = max(0, word["start"] - ss)
            word["end"] = max(0, word["end"] - ss)

    if not words:
        print("  WARNING: No words in clip range, generating silent video")

    # Step 2: Generate ASS subtitles
    print(f"  Generating karaoke subtitles ({len(words)} words)...")
    ass_content = generate_ass(words, style_name, format_key, (w, h))

    # Step 3: FFmpeg render
    with tempfile.TemporaryDirectory() as tmpdir:
        ass_path = Path(tmpdir) / "karaoke.ass"
        ass_path.write_text(ass_content, encoding="utf-8")

        # Waveform dimensions
        wave_h = int(h * style["waveform_height_pct"] / 100)
        wave_color = style["waveform_color"].lstrip("#")
        bg_color = style["background_color"].lstrip("#")

        # Quality settings
        crf = {"draft": 27, "standard": 23, "high": 21}[quality]
        preset = {"draft": "veryfast", "standard": "medium", "high": "slow"}[quality]

        # If clipping, extract audio segment first (clean timestamps for showwaves)
        audio_input = audio
        if clip_start or clip_end:
            clipped_audio = Path(tmpdir) / "clipped.wav"
            clip_cmd = [FFMPEG, "-y"]
            if clip_start:
                clip_cmd.extend(["-ss", str(clip_start)])
            clip_cmd.extend(["-i", str(audio)])
            if clip_end:
                clip_cmd.extend(["-t", str(clip_dur)])
            clip_cmd.extend(["-c:a", "pcm_s16le", str(clipped_audio)])
            subprocess.run(clip_cmd, capture_output=True, check=True)
            audio_input = clipped_audio
            # Recalculate clip_dur from actual clipped file
            clip_dur = _get_audio_duration(clipped_audio)

        # Build FFmpeg command
        ass_escaped = str(ass_path).replace("\\", "/").replace(":", "\\:")

        filter_complex = (
            # Black background
            f"color=c=0x{bg_color}:s={w}x{h}:d={clip_dur}:r={fps}[bg];"
            # Waveform from audio (full clipped audio, timestamps start at 0)
            f"[0:a]showwaves=s={w}x{wave_h}:mode={style['waveform_mode']}"
            f":colors=0x{wave_color}:rate={fps}:scale=sqrt:draw=full[wave];"
            # Overlay waveform at bottom of frame
            f"[bg][wave]overlay=0:{h - wave_h}:shortest=1[with_wave];"
            # Burn ASS subtitles
            f"[with_wave]ass='{ass_escaped}'[vout]"
        )

        cmd = [
            FFMPEG, "-y",
            "-i", str(audio_input),
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "0:a",
            "-c:v", "libx264",
            "-crf", str(crf),
            "-preset", preset,
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "256k" if format_key == "long" else "128k",
            "-movflags", "+faststart",
            "-shortest",
            str(output),
        ]

        print(f"  Rendering with FFmpeg ({quality} quality)...")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"FFmpeg FAILED:\n{r.stderr[-2000:]}", file=sys.stderr)
            sys.exit(1)

    # Verify output
    out_size = output.stat().st_size / (1024 * 1024)
    out_dur = _get_audio_duration(output)
    print(f"  Output: {output} ({out_size:.1f} MB, {out_dur:.1f}s)")

    return output


def main() -> int:
    ap = argparse.ArgumentParser(description="Render Descript-style audiobook video")
    ap.add_argument("--audio", required=True, type=Path, help="Audio file (MP3/WAV)")
    ap.add_argument("--transcript", type=Path, help="Transcript text file")
    ap.add_argument("--format", default="long", choices=["long", "short"],
                     help="Video format: long (16:9) or short (9:16)")
    ap.add_argument("--style", default="default", help="Visual style preset")
    ap.add_argument("--clip-start", type=float, help="Clip start time (seconds)")
    ap.add_argument("--clip-end", type=float, help="Clip end time (seconds)")
    ap.add_argument("--quality", default="standard", choices=["draft", "standard", "high"])
    ap.add_argument("--whisper-model", default="base",
                     choices=["tiny", "base", "small", "medium", "large"])
    ap.add_argument("-o", "--output", required=True, type=Path, help="Output MP4 path")
    args = ap.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    render_audiobook(
        audio=args.audio,
        transcript=args.transcript,
        output=args.output,
        format_key=args.format,
        style_name=args.style,
        clip_start=args.clip_start,
        clip_end=args.clip_end,
        quality=args.quality,
        whisper_model=args.whisper_model,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
