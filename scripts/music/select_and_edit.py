#!/usr/bin/env python3
"""Select music from bank + apply anti-spam edits for a video.

Each video gets a unique audio fingerprint via deterministic edits
based on video_id hash: speed shift, pitch shift, EQ curve, start offset.

Usage:
    python3 scripts/music/select_and_edit.py \
        --video-id "vid-001" \
        --topic anxiety \
        --mood calm \
        --duration 60 \
        -o /tmp/output_music.mp3
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BANK_DIR = REPO_ROOT / "assets" / "music_bank"


def _load_index() -> list[dict]:
    """Load music bank index."""
    idx_yaml = BANK_DIR / "index.yaml"
    idx_json = BANK_DIR / "index.json"

    if yaml and idx_yaml.is_file():
        data = yaml.safe_load(idx_yaml.read_text(encoding="utf-8"))
    elif idx_json.is_file():
        data = json.loads(idx_json.read_text(encoding="utf-8"))
    else:
        return []
    return data.get("tracks", [])


def select_track(
    topic: str = "",
    mood: str = "calm",
    brand: str = "",
    energy: str = "low",
) -> dict | None:
    """Score tracks against metadata, return best match."""
    tracks = _load_index()
    if not tracks:
        return None

    scored = []
    for t in tracks:
        score = 0
        if topic and topic in t.get("topic_affinity", []):
            score += 3
        if mood and mood in t.get("mood", []):
            score += 2
        if brand and brand in t.get("brand_affinity", []):
            score += 2
        if energy and t.get("energy") == energy:
            score += 1
        scored.append((score, t))

    scored.sort(key=lambda x: -x[0])
    return scored[0][1] if scored else None


def anti_spam_edit(
    input_path: Path,
    output_path: Path,
    video_id: str,
    target_duration_s: float,
    *,
    ffmpeg_bin: str = "ffmpeg",
) -> None:
    """Apply deterministic-but-unique audio edits based on video_id.

    Edits: speed shift, pitch shift, EQ curve, start offset, loop if needed.
    Each video_id produces a reproducible but unique result.
    """
    seed = int(hashlib.sha256(video_id.encode()).hexdigest()[:8], 16)

    # Deterministic variations from seed
    speed = 0.97 + (seed % 7) * 0.01          # 0.97 to 1.03
    pitch_cents = -150 + (seed % 301)           # -150 to +150
    low_gain = -3 + (seed % 7)                  # -3 to +3 dB at 80Hz
    mid_gain = -2 + (seed % 5)                  # -2 to +2 dB at 2kHz
    high_gain = -3 + (seed % 7)                 # -3 to +3 dB at 8kHz
    offset_pct = (seed % 30) / 100              # 0-30% into track

    # Get source duration
    try:
        r = subprocess.run(
            [ffmpeg_bin.replace("ffmpeg", "ffprobe"), "-v", "quiet",
             "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
             str(input_path)],
            capture_output=True, text=True, timeout=10,
        )
        src_dur = float(r.stdout.strip())
    except Exception:
        src_dur = 180.0

    offset_s = src_dur * offset_pct

    # Build filter chain
    filters = [
        f"atempo={speed}",
        f"asetrate=44100*{1 + pitch_cents / 120000}",
        f"equalizer=f=80:t=q:w=1:g={low_gain}",
        f"equalizer=f=2000:t=q:w=1:g={mid_gain}",
        f"equalizer=f=8000:t=q:w=1:g={high_gain}",
        "afade=t=in:st=0:d=2",
        f"afade=t=out:st={max(0, target_duration_s - 3)}:d=3",
    ]

    # If video is longer than source track, crossfade-loop it
    effective_dur = src_dur - offset_s
    loop_count = max(1, int(target_duration_s / effective_dur) + 1)
    crossfade_s = 3.0  # 3-second crossfade between loops

    if loop_count <= 1:
        # Single play — no looping needed
        cmd = [
            ffmpeg_bin, "-y",
            "-ss", str(round(offset_s, 2)),
            "-i", str(input_path),
            "-af", ",".join(filters),
            "-t", str(round(target_duration_s, 2)),
            "-c:a", "libmp3lame", "-b:a", "128k",
            str(output_path),
        ]
    else:
        # Crossfade loop: overlay copies with fade transitions
        # Strategy: use stream_loop + acrossfade filter for smooth transitions
        # First, create a version that fades out at end and fades in at start
        loop_filters = list(filters)  # copy base filters
        # Remove the existing fade in/out (we'll do crossfade instead)
        loop_filters = [f for f in loop_filters if "afade" not in f]
        # Add crossfade-friendly fades: fade out last 3s, fade in first 3s
        loop_filters.append(f"afade=t=out:st={max(0, effective_dur - crossfade_s)}:d={crossfade_s}")

        cmd = [
            ffmpeg_bin, "-y",
            "-stream_loop", str(loop_count - 1),
            "-ss", str(round(offset_s, 2)),
            "-i", str(input_path),
            "-af", ",".join(loop_filters) + f",afade=t=in:st=0:d=2,afade=t=out:st={max(0, target_duration_s - 3)}:d=3",
            "-t", str(round(target_duration_s, 2)),
            "-c:a", "libmp3lame", "-b:a", "128k",
            str(output_path),
        ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(cmd, check=True, capture_output=True, timeout=60)


def main() -> int:
    ap = argparse.ArgumentParser(description="Select + edit music from bank for a video")
    ap.add_argument("--video-id", required=True)
    ap.add_argument("--topic", default="anxiety")
    ap.add_argument("--mood", default="calm")
    ap.add_argument("--brand", default="")
    ap.add_argument("--duration", type=float, default=60.0)
    ap.add_argument("-o", "--output", required=True, type=Path)
    ap.add_argument("--ffmpeg", default="ffmpeg")
    args = ap.parse_args()

    track = select_track(topic=args.topic, mood=args.mood, brand=args.brand)
    if not track:
        print("No matching track found in music bank", file=sys.stderr)
        return 1

    src = BANK_DIR / track["file"]
    if not src.is_file():
        print(f"Track file not found: {src}", file=sys.stderr)
        return 1

    print(f"Selected: {track['id']} ({track['category']}, {track['duration_s']}s)")
    print(f"Editing for video {args.video_id} ({args.duration}s)...")

    anti_spam_edit(src, args.output, args.video_id, args.duration, ffmpeg_bin=args.ffmpeg)
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
