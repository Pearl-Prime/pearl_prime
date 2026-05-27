#!/usr/bin/env python3
"""
Render a single short podcast episode from a plain-text script.

MVP wrapper around scripts.podcast.render_podcast_audio internals: skips the
assemble step (which expects book-derived atoms) so we can ship a quick weekly
"check-in" style episode (60-120s) straight from a hand-authored script.

Outputs a final MP3 at --output with ffmpeg loudnorm + ID3 metadata, identical
encoding pipeline to the full assemble→render flow. Designed for the brand-admin
podcast axis MVP (ws_brand_admin_v2_real_content_build_podcast_axis_20260527).

Usage:
  PYTHONPATH=. python3 scripts/podcast/render_simple_episode.py \\
    --script artifacts/weekly_packages/<brand>/<week>/spotify_podcast/script.txt \\
    --output artifacts/weekly_packages/<brand>/<week>/spotify_podcast/<ep_id>.mp3 \\
    --brand-id stillness_press --series-title 'The Stillness Check-In' \\
    --episode-title 'Weekly Anxiety Check-In' --episode-number 1 \\
    --teacher-name 'Ahjan' --voice-id <11-labs-voice-id>

Requires ffmpeg + ELEVENLABS_API_KEY (load via scripts/ci/load_integration_env_from_keychain.py).
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.podcast.render_podcast_audio import (  # noqa: E402
    _edge_tts,
    _elevenlabs_tts,
    encode_mp3,
    get_ffmpeg,
    id3_mutagen,
    loudnorm_report,
    probe_duration,
    run_ff,
)


_FALLBACK_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # ElevenLabs "Rachel" — Tier 1 EN US default per _lib.py
_EDGE_FALLBACK_VOICE = "en-US-JennyNeural"  # Free Microsoft Edge TTS fallback (no API key required)


def render_simple(
    script_text: str,
    output_mp3: Path,
    *,
    voice_id: str,
    voice_model: str = "eleven_multilingual_v2",
    fmt: str = "podcast_short",
    title: str = "Weekly Check-In",
    teacher_name: str = "Teacher",
    series_title: str = "Stillness Check-In",
    episode_number: int = 1,
    edge_voice: str = _EDGE_FALLBACK_VOICE,
    prefer_provider: str = "auto",
) -> dict:
    """Render plain script_text to MP3.

    prefer_provider: "elevenlabs" forces 11Labs only, "edge" forces Edge TTS only,
    "auto" tries ElevenLabs first if voice_id is set + key present, else falls
    back to Edge TTS (free, no key required). Matches the fallback chain in
    scripts.podcast.render_podcast_audio.synth_speech.
    """
    script_text = (script_text or "").strip()
    if not script_text:
        return {"output_mp3": None, "errors": ["empty script"]}

    output_mp3 = output_mp3.resolve()
    output_mp3.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="podcast_simple_") as td:
        tdir = Path(td)
        raw_mp3 = tdir / "voice_raw.mp3"
        voice_wav = tdir / "voice.wav"

        provider_used = None
        attempts: list[str] = []
        if prefer_provider in ("auto", "elevenlabs") and voice_id:
            if _elevenlabs_tts(script_text, voice_id, voice_model, raw_mp3, dry_run=False):
                provider_used = "elevenlabs"
            else:
                attempts.append("elevenlabs")
        if provider_used is None and prefer_provider in ("auto", "edge"):
            if _edge_tts(script_text, edge_voice, raw_mp3, dry_run=False):
                provider_used = f"edge_tts:{edge_voice}"
            else:
                attempts.append("edge_tts")
        if provider_used is None:
            return {"output_mp3": None, "errors": [f"tts failed (tried {','.join(attempts) or 'nothing'})"]}

        # Normalize to 44.1k mono WAV before loudnorm encode (matches full pipeline).
        if not run_ff(
            [get_ffmpeg(), "-y", "-i", str(raw_mp3), "-ar", "44100", "-ac", "1", str(voice_wav)],
        ):
            return {"output_mp3": None, "errors": ["ffmpeg resample failed"]}

        meta = {
            "title": title,
            "teacher_name": teacher_name,
            "series_title": series_title,
            "episode_number": episode_number,
        }
        if not encode_mp3(voice_wav, output_mp3, meta, fmt, dry_run=False):
            return {"output_mp3": None, "errors": ["mp3 encode failed"]}

    id3_mutagen(output_mp3, {
        "title": title,
        "teacher_name": teacher_name,
        "series_title": series_title,
        "episode_number": episode_number,
    })

    duration = probe_duration(output_mp3)
    return {
        "output_mp3": str(output_mp3),
        "duration_s": duration,
        "file_size_bytes": output_mp3.stat().st_size if output_mp3.exists() else 0,
        "loudness": loudnorm_report(output_mp3),
        "provider_used": provider_used,
        "errors": [],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render simple podcast episode from a plain script")
    ap.add_argument("--script", type=Path, required=True, help="Path to .txt or .md script (full text)")
    ap.add_argument("--output", type=Path, required=True, help="Destination MP3 path")
    ap.add_argument("--brand-id", default="")
    ap.add_argument("--voice-id", default=_FALLBACK_VOICE_ID, help="ElevenLabs voice_id (default Rachel)")
    ap.add_argument("--voice-model", default="eleven_multilingual_v2")
    ap.add_argument("--edge-voice", default=_EDGE_FALLBACK_VOICE, help="Edge TTS voice name (used when ElevenLabs unavailable)")
    ap.add_argument("--prefer-provider", choices=["auto", "elevenlabs", "edge"], default="auto",
                    help="auto: try ElevenLabs then Edge; elevenlabs: 11Labs only; edge: Edge only (free)")
    ap.add_argument("--format", dest="fmt", default="podcast_short", help="Loudness profile slot in podcast_format.yaml")
    ap.add_argument("--episode-title", default="Weekly Check-In")
    ap.add_argument("--series-title", default="The Stillness Check-In")
    ap.add_argument("--teacher-name", default="Pearl Audio")
    ap.add_argument("--episode-number", type=int, default=1)
    args = ap.parse_args(argv)

    script_path = args.script.resolve()
    if not script_path.is_file():
        print(f"ERROR: script not found: {script_path}", file=sys.stderr)
        return 1

    script_text = script_path.read_text(encoding="utf-8")
    report = render_simple(
        script_text,
        args.output,
        voice_id=args.voice_id,
        voice_model=args.voice_model,
        fmt=args.fmt,
        title=args.episode_title,
        teacher_name=args.teacher_name,
        series_title=args.series_title,
        episode_number=args.episode_number,
        edge_voice=args.edge_voice,
        prefer_provider=args.prefer_provider,
    )

    if report.get("errors"):
        for err in report["errors"]:
            print("ERROR:", err, file=sys.stderr)
        return 1

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
