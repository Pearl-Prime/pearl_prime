#!/usr/bin/env python3
"""Word-level forced alignment using Whisper / stable-ts.

Takes an audio file + optional transcript and returns word-level timestamps.
Falls back to simple WPM estimation if Whisper is unavailable.

Usage:
    python3 scripts/video/align_transcript.py \
        --audio chapter_01.mp3 \
        --transcript chapter_01.txt \
        -o alignment.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FFPROBE = "/opt/homebrew/bin/ffprobe"


def _get_duration(audio_path: Path) -> float:
    """Get audio duration in seconds via ffprobe."""
    import subprocess
    r = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", str(audio_path)],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        return float(json.loads(r.stdout)["format"]["duration"])
    raise RuntimeError(f"ffprobe failed on {audio_path}")


def align_whisper(audio_path: Path, transcript: str | None = None, model_size: str = "base") -> list[dict]:
    """Align using stable-ts (Whisper with word-level timestamps).

    Returns list of {"word": str, "start": float, "end": float}.
    """
    import stable_whisper  # type: ignore

    model = stable_whisper.load_model(model_size)

    if transcript:
        # Forced alignment against known transcript
        result = model.align(str(audio_path), transcript, language="en")
    else:
        # Transcribe + align
        result = model.transcribe(str(audio_path), language="en")

    words = []
    for segment in result.segments:
        for word_obj in segment.words:
            words.append({
                "word": word_obj.word.strip(),
                "start": round(word_obj.start, 3),
                "end": round(word_obj.end, 3),
            })
    return words


def align_wpm_fallback(transcript: str, duration_s: float, wpm: float = 140.0) -> list[dict]:
    """Simple fallback: distribute words evenly across duration.

    Not as good as Whisper but works without GPU/model download.
    """
    raw_words = transcript.split()
    if not raw_words:
        return []

    # Seconds per word
    spw = 60.0 / wpm
    total_speech = len(raw_words) * spw

    # If speech would exceed audio, compress
    if total_speech > duration_s:
        spw = duration_s / len(raw_words)

    # Center speech in audio with small margins
    margin = max(0, (duration_s - total_speech) / 2)
    margin = min(margin, 2.0)  # max 2s lead-in

    words = []
    t = margin
    for w in raw_words:
        words.append({
            "word": w,
            "start": round(t, 3),
            "end": round(t + spw, 3),
        })
        t += spw
    return words


def align(audio_path: Path, transcript: str | None = None, model_size: str = "base") -> list[dict]:
    """Align audio to transcript. Uses Whisper if available, else WPM fallback."""
    try:
        return align_whisper(audio_path, transcript, model_size)
    except Exception as e:
        print(f"Whisper alignment failed ({e}), falling back to WPM estimation", file=sys.stderr)
        if transcript is None:
            raise RuntimeError("WPM fallback requires --transcript") from e
        duration = _get_duration(audio_path)
        return align_wpm_fallback(transcript, duration)


def main() -> int:
    ap = argparse.ArgumentParser(description="Word-level forced alignment")
    ap.add_argument("--audio", required=True, type=Path, help="Audio file (MP3/WAV)")
    ap.add_argument("--transcript", type=Path, help="Transcript text file (optional for Whisper, required for fallback)")
    ap.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large"],
                     help="Whisper model size (default: base)")
    ap.add_argument("-o", "--output", type=Path, help="Output JSON path")
    args = ap.parse_args()

    transcript_text = args.transcript.read_text(encoding="utf-8").strip() if args.transcript else None
    words = align(args.audio, transcript_text, args.model)

    output = {
        "audio": str(args.audio),
        "word_count": len(words),
        "duration_s": words[-1]["end"] if words else 0,
        "words": words,
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False))
        print(f"Aligned {len(words)} words → {args.output}")
    else:
        print(json.dumps(output, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
