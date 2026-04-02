#!/usr/bin/env python3
"""
Stage 14 — Soundtrack Engine: timeline + shot_plan + script_segments -> soundtrack_plan.json.
VCE §7: Suno/ElevenLabs call specs (no live API), mix levels, automation. Placeholder audio paths.
Usage: python scripts/video/run_soundtrack_engine.py <timeline.json> <shot_plan.json> <script_segments.json> -o soundtrack_plan.json [--channel-id ch_001]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import config_snapshot_hash, load_json, load_yaml, should_skip_output, write_atomically

SUNO_BASE = "https://api.suno.ai/v1/generate"
ELEVEN_BASE = "https://api.elevenlabs.io/v1/text-to-speech"


def _arc_from_time(t: float, duration: float) -> str:
    if duration <= 0:
        return "hook"
    p = t / duration
    if p < 0.15:
        return "hook"
    if p < 0.55:
        return "build"
    if p < 0.70:
        return "peak"
    if p < 0.85:
        return "release"
    return "resolve"


def run_soundtrack(timeline: dict, shot_plan: dict, script_segments: dict, channel_id: str) -> dict:
    music_policy = load_yaml("config/video/music_policy.yaml")
    arc_to_mood = music_policy.get("arc_to_mood") or {}
    registry = load_yaml("config/video/channel_registry.yaml")
    channels = registry.get("channels") or {}
    ch = channels.get(channel_id) or channels.get("ch_001", {})
    voice_id = ch.get("tts_voice_id", "en-US-Journey-F")

    duration = float(timeline.get("duration_s") or 0)
    plan_id = timeline.get("plan_id") or shot_plan.get("plan_id")

    narration_segments = []
    for seg in script_segments.get("segments") or []:
        t0 = float(seg.get("start_time_s", 0))
        arc = _arc_from_time(t0, duration)
        narration_segments.append({
            "segment_id": seg.get("segment_id"),
            "start_time_s": t0,
            "end_time_s": seg.get("end_time_s"),
            "text": seg.get("text", ""),
            "arc": arc,
        })

    moods = [arc_to_mood.get(a, "calm_resolution") for a in ["hook", "build", "peak", "release", "resolve"]]

    suno_calls = [
        {
            "provider": "suno",
            "method": "POST",
            "url": SUNO_BASE,
            "params": {
                "duration_s": min(max(duration, 10), 120),
                "bpm_range": [60, 72],
                "scale": "pentatonic",
                "instrumental": True,
                "phrase_s": 10,
                "mood_arc": moods,
            },
            "expected_output": {
                "paths": [f"artifacts/audio/{plan_id}/music_bed_placeholder.wav"],
                "format": "wav",
            },
        }
    ]

    eleven_calls = [
        {
            "provider": "elevenlabs",
            "method": "POST",
            "url": f"{ELEVEN_BASE}/{voice_id}",
            "params": {
                "voice_id": voice_id,
                "model_id": "eleven_turbo_v2_5",
                "text": seg["text"][:500],
                "output_format": "mp3_44100_128",
            },
            "expected_output": {
                "path": f"artifacts/audio/{plan_id}/narration_{seg['segment_id']}_placeholder.mp3",
            },
        }
        for seg in narration_segments
    ]

    automation = []
    for clip in timeline.get("clips") or []:
        automation.append({
            "event": "scene_cut",
            "time_s": clip.get("start_time_s"),
            "music_swell_db": 2,
            "swell_ms": 200,
        })

    mix_spec = {
        "tracks": [
            {"id": "narration", "level_db": -6, "pan": "center", "ducking": "music_minus_6db_when_active"},
            {"id": "music_bed", "level_db_under_narration": -12, "level_db_solo": -8, "pan": "stereo"},
            {"id": "ambience", "level_db": -18, "pan": "wide_stereo"},
            {"id": "therapeutic_isochronic", "level_db_max": -18, "pan": "center", "optional": True},
            {"id": "therapeutic_subbass", "level_db_max": -18, "pan": "center", "optional": True},
        ],
        "master": {"true_peak_db_tp": -1.0, "integrated_lufs_target": -14.0},
        "placeholders": {
            "music": f"artifacts/audio/{plan_id}/music_bed_placeholder.wav",
            "ambience": f"artifacts/audio/{plan_id}/ambience_placeholder.wav",
        },
        "automation": automation + [
            {"event": "nature_onset", "ambience_fade_to_db": -12, "over_s": 2.0},
            {"event": "silence_point", "fade_all_to_db": -40, "over_s": 1.0},
            {"event": "breathing_peak", "subbass_lift_db": 3, "phase": "exhale"},
            {"event": "caption_reveal", "preroll_ms": 200, "music_duck": True},
        ],
        "mix_validation": {
            "integrated_lufs": -14.0,
            "passes": True,
            "note": "stub until loudness measure on rendered master",
        },
    }

    return {
        "plan_id": plan_id,
        "channel_id": channel_id,
        "config_hash": config_snapshot_hash(),
        "duration_s": duration,
        "narration_segments": narration_segments,
        "suno_api_calls": suno_calls,
        "elevenlabs_api_calls": eleven_calls,
        "mix_spec": mix_spec,
        "arc_to_mood_applied": arc_to_mood,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="VCE Stage 14 — Soundtrack engine (call specs only)")
    ap.add_argument("timeline")
    ap.add_argument("shot_plan")
    ap.add_argument("script_segments")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--channel-id", default="ch_001")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    paths = [Path(args.timeline), Path(args.shot_plan), Path(args.script_segments)]
    if not all(p.exists() for p in paths):
        print("Error: input not found", file=sys.stderr)
        return 1
    tl, sp, ss = load_json(paths[0]), load_json(paths[1]), load_json(paths[2])
    out = Path(args.out)
    h = config_snapshot_hash()
    if should_skip_output(out, ["plan_id", "mix_spec", "config_hash"], args.force, h):
        print(f"Skip (exists): {out}")
        return 0
    doc = run_soundtrack(tl, sp, ss, args.channel_id)
    write_atomically(out, doc)
    print(f"Wrote soundtrack_plan to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
