#!/usr/bin/env python3
"""Book → Audiobook → Video orchestrator.

Takes a book plan + audiobook MP3(s) and produces all video variants
(long-form chapters, shorts, full audiobook) with a drip upload schedule
that respects per-platform cadence limits.

Usage:
    # From audiobook MP3 directory + transcript
    python3 scripts/video/orchestrate_book_to_video.py \
        --audio-dir artifacts/audiobooks/book_001/ \
        --transcript artifacts/book_pass/book_001/book.txt \
        --brand stillness_press --teacher ahjan \
        -o artifacts/video/audiobook/book_001/

    # Single chapter quick test
    python3 scripts/video/orchestrate_book_to_video.py \
        --audio chapter_01.mp3 --transcript chapter_01.txt \
        --brand stillness_press --teacher ahjan \
        -o test_output/
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FFPROBE = "/opt/homebrew/bin/ffprobe"

sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def _get_duration(audio: Path) -> float:
    r = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", str(audio)],
        capture_output=True, text=True,
    )
    return float(json.loads(r.stdout)["format"]["duration"])


def _load_cadence() -> dict:
    p = REPO_ROOT / "config" / "release_velocity" / "video_cadence.yaml"
    if yaml and p.is_file():
        return yaml.safe_load(p.read_text())
    return {"book_video_drip": {
        "long_form_chapters": {"release_interval_days": 1},
        "shorts": {"release_interval_hours": 8, "start_offset_days": -3},
        "full_audiobook": {"release_offset_days": 21},
    }}


def _split_chapters_by_silence(audio: Path, min_silence_s: float = 2.0, threshold_db: float = -40) -> list[dict]:
    """Detect chapter boundaries via silence detection."""
    r = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", str(audio)],
        capture_output=True, text=True,
    )
    total_dur = float(json.loads(r.stdout)["format"]["duration"])

    # Use FFmpeg silencedetect
    r = subprocess.run(
        ["/opt/homebrew/bin/ffmpeg", "-i", str(audio),
         "-af", f"silencedetect=noise={threshold_db}dB:d={min_silence_s}",
         "-f", "null", "-"],
        capture_output=True, text=True,
    )

    import re
    silence_starts = [float(m.group(1)) for m in re.finditer(r"silence_start:\s*(\d+\.?\d*)", r.stderr)]
    silence_ends = [float(m.group(1)) for m in re.finditer(r"silence_end:\s*(\d+\.?\d*)", r.stderr)]

    # Build chapter boundaries from long silences (>3s = chapter break)
    breaks = [0.0]
    for s_start, s_end in zip(silence_starts, silence_ends):
        gap = s_end - s_start
        if gap >= 3.0 and s_start > 30:  # skip silence at very beginning
            midpoint = (s_start + s_end) / 2
            breaks.append(midpoint)
    breaks.append(total_dur)

    chapters = []
    for i in range(len(breaks) - 1):
        chapters.append({
            "index": i,
            "start": breaks[i],
            "end": breaks[i + 1],
            "duration": breaks[i + 1] - breaks[i],
        })
    return chapters


def _split_transcript(text: str, num_chapters: int) -> list[str]:
    """Split transcript text into roughly equal chunks for chapters."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    per_chapter = max(1, len(paragraphs) // num_chapters)
    chunks = []
    for i in range(num_chapters):
        start = i * per_chapter
        end = start + per_chapter if i < num_chapters - 1 else len(paragraphs)
        chunks.append("\n\n".join(paragraphs[start:end]))
    return chunks


def _find_best_clip(words: list[dict], target_dur: float = 45.0) -> tuple[float, float]:
    """Find the best clip window for a short.

    Prefers: sentence boundaries, emotional peaks (longer pauses before), middle third of chapter.
    """
    if not words:
        return 0, target_dur

    total_dur = words[-1]["end"]
    # Prefer middle third
    ideal_start = total_dur * 0.3
    ideal_end = ideal_start + target_dur

    # Snap to sentence boundary (period/question/exclamation)
    best_start = ideal_start
    for w in words:
        if w["start"] >= ideal_start - 5 and w["word"].rstrip().endswith((".", "!", "?")):
            # Start after this sentence
            best_start = w["end"] + 0.2
            break

    best_end = best_start + target_dur
    # Snap end to sentence boundary
    for w in words:
        if w["start"] >= best_end - 3 and w["word"].rstrip().endswith((".", "!", "?")):
            best_end = w["end"] + 0.5
            break

    return max(0, best_start), min(total_dur, best_end)


def generate_upload_schedule(
    videos: list[dict],
    brand_id: str,
    teacher: str,
    start_date: datetime | None = None,
) -> dict:
    """Generate a drip upload schedule respecting platform cadence."""
    cadence = _load_cadence()
    drip = cadence.get("book_video_drip", {})

    if start_date is None:
        start_date = datetime.now() + timedelta(days=7)  # 1 week from now

    long_interval = drip.get("long_form_chapters", {}).get("release_interval_days", 1)
    short_interval_h = drip.get("shorts", {}).get("release_interval_hours", 8)
    short_offset = drip.get("shorts", {}).get("start_offset_days", -3)
    full_offset = drip.get("full_audiobook", {}).get("release_offset_days", 21)

    schedule = []
    long_day = 0
    short_day = short_offset

    # Platform rotation for shorts
    short_platforms = ["tiktok", "youtube_shorts", "instagram_reels"]
    platform_idx = 0

    for v in videos:
        if v["type"] == "long":
            schedule.append({
                "day": long_day,
                "date": (start_date + timedelta(days=long_day)).strftime("%Y-%m-%d"),
                "platform": "youtube",
                "type": "long",
                "file": v["file"],
                "chapter": v.get("chapter", 0),
            })
            long_day += long_interval

        elif v["type"] == "short":
            platform = short_platforms[platform_idx % len(short_platforms)]
            platform_idx += 1
            schedule.append({
                "day": short_day,
                "date": (start_date + timedelta(days=short_day)).strftime("%Y-%m-%d"),
                "platform": platform,
                "type": "short",
                "file": v["file"],
                "chapter": v.get("chapter", 0),
            })
            # Advance by interval (convert hours to fractional days)
            short_day += short_interval_h / 24

        elif v["type"] == "full":
            schedule.append({
                "day": full_offset,
                "date": (start_date + timedelta(days=full_offset)).strftime("%Y-%m-%d"),
                "platform": "youtube",
                "type": "full_audiobook",
                "file": v["file"],
            })

    # Sort by day
    schedule.sort(key=lambda x: x["day"])

    return {
        "book_id": videos[0].get("book_id", "unknown") if videos else "unknown",
        "brand_id": brand_id,
        "teacher": teacher,
        "total_videos": len(schedule),
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": (start_date + timedelta(days=max(s["day"] for s in schedule))).strftime("%Y-%m-%d") if schedule else start_date.strftime("%Y-%m-%d"),
        "duration_days": int(max(s["day"] for s in schedule)) if schedule else 0,
        "schedule": schedule,
    }


def orchestrate(
    audio_files: list[Path],
    transcript: str,
    output_dir: Path,
    brand_id: str = "stillness_press",
    teacher: str = "ahjan",
    style: str = "default",
    quality: str = "standard",
    whisper_model: str = "base",
    book_id: str = "book_001",
) -> dict:
    """Full orchestration: audio files + transcript → rendered videos + schedule."""
    from scripts.video.render_audiobook import render_audiobook

    output_dir.mkdir(parents=True, exist_ok=True)
    videos = []

    # If single audio file, try to split by silence
    if len(audio_files) == 1:
        print(f"Single audio file: {audio_files[0]}")
        duration = _get_duration(audio_files[0])
        if duration > 600:  # > 10 min = likely multi-chapter
            print("  Detecting chapter boundaries...")
            chapters = _split_chapters_by_silence(audio_files[0])
            print(f"  Found {len(chapters)} chapters")
        else:
            chapters = [{"index": 0, "start": 0, "end": duration, "duration": duration}]
    else:
        chapters = [{"index": i, "start": 0, "end": _get_duration(f), "duration": _get_duration(f)}
                     for i, f in enumerate(audio_files)]

    # Split transcript
    transcript_chunks = _split_transcript(transcript, len(chapters))

    for i, chapter in enumerate(chapters):
        ch_num = i + 1
        audio_file = audio_files[0] if len(audio_files) == 1 else audio_files[i]
        ch_transcript = transcript_chunks[i] if i < len(transcript_chunks) else ""

        # Write chapter transcript to temp file
        ch_txt = output_dir / f"ch{ch_num:02d}_transcript.txt"
        ch_txt.write_text(ch_transcript, encoding="utf-8")

        # Clip boundaries (for single-file multi-chapter)
        clip_start = chapter["start"] if len(audio_files) == 1 else None
        clip_end = chapter["end"] if len(audio_files) == 1 else None

        # --- Long-form chapter video ---
        long_out = output_dir / f"ch{ch_num:02d}_long.mp4"
        print(f"\n--- Chapter {ch_num}/{len(chapters)} (long-form) ---")
        render_audiobook(
            audio=audio_file,
            transcript=ch_txt,
            output=long_out,
            format_key="long",
            style_name=style,
            clip_start=clip_start,
            clip_end=clip_end,
            quality=quality,
            whisper_model=whisper_model,
        )
        videos.append({
            "type": "long", "file": long_out.name, "chapter": ch_num,
            "book_id": book_id, "duration": chapter["duration"],
        })

        # --- Short clip ---
        # Find best 45s window
        short_start = (clip_start or 0) + chapter["duration"] * 0.3
        short_end = short_start + 45
        if short_end > (clip_end or chapter["end"]):
            short_end = clip_end or chapter["end"]
            short_start = max(clip_start or 0, short_end - 45)

        short_out = output_dir / f"ch{ch_num:02d}_short.mp4"
        print(f"\n--- Chapter {ch_num}/{len(chapters)} (short clip) ---")
        render_audiobook(
            audio=audio_file,
            transcript=ch_txt,
            output=short_out,
            format_key="short",
            style_name=style,
            clip_start=short_start,
            clip_end=short_end,
            quality=quality,
            whisper_model=whisper_model,
        )
        videos.append({
            "type": "short", "file": short_out.name, "chapter": ch_num,
            "book_id": book_id, "duration": short_end - short_start,
        })

    # Generate upload schedule
    schedule = generate_upload_schedule(videos, brand_id, teacher)
    schedule_path = output_dir / "upload_schedule.json"
    schedule_path.write_text(json.dumps(schedule, indent=2, ensure_ascii=False))
    print(f"\nUpload schedule: {schedule_path}")
    print(f"  {schedule['total_videos']} videos over {schedule['duration_days']} days")

    return schedule


def main() -> int:
    ap = argparse.ArgumentParser(description="Book → Audiobook → Video orchestrator")
    ap.add_argument("--audio", type=Path, help="Single audio file (MP3/WAV)")
    ap.add_argument("--audio-dir", type=Path, help="Directory of chapter MP3s")
    ap.add_argument("--transcript", required=True, type=Path, help="Transcript text file")
    ap.add_argument("--brand", default="stillness_press", help="Brand ID")
    ap.add_argument("--teacher", default="ahjan", help="Teacher name")
    ap.add_argument("--book-id", default="book_001", help="Book identifier")
    ap.add_argument("--style", default="default", help="Visual style preset")
    ap.add_argument("--quality", default="standard", choices=["draft", "standard", "high"])
    ap.add_argument("--whisper-model", default="base")
    ap.add_argument("-o", "--output-dir", required=True, type=Path)
    args = ap.parse_args()

    transcript = args.transcript.read_text(encoding="utf-8").strip()

    if args.audio:
        audio_files = [args.audio]
    elif args.audio_dir:
        audio_files = sorted(args.audio_dir.glob("*.mp3")) + sorted(args.audio_dir.glob("*.wav"))
        if not audio_files:
            print(f"No audio files found in {args.audio_dir}", file=sys.stderr)
            return 1
    else:
        print("Provide --audio or --audio-dir", file=sys.stderr)
        return 1

    orchestrate(
        audio_files=audio_files,
        transcript=transcript,
        output_dir=args.output_dir,
        brand_id=args.brand,
        teacher=args.teacher,
        book_id=args.book_id,
        style=args.style,
        quality=args.quality,
        whisper_model=args.whisper_model,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
