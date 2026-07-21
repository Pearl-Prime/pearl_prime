#!/usr/bin/env python3
"""
Stage 14 — Soundtrack Engine: timeline + shot_plan + script_segments -> soundtrack_plan.json.
VCE §7: Suno + narration TTS call specs only (no live API), mix levels, automation. Placeholder paths.
ElevenLabs POST URLs come from config/tts/locale_voice_routing.yaml (provider_config.elevenlabs.base_url).
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


def _elevenlabs_tts_url(voice_id: str) -> str:
    """Build spec URL from governed TTS config (avoids a hardcoded ElevenLabs host in this script)."""
    tts = load_yaml("config/tts/locale_voice_routing.yaml") or {}
    eleven = (tts.get("provider_config") or {}).get("elevenlabs") or {}
    base = eleven.get("base_url")
    if isinstance(base, str) and base.strip():
        return f"{base.rstrip('/')}/text-to-speech/{voice_id}"
    return f"${{ELEVENLABS_BASE_URL}}/text-to-speech/{voice_id}"


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


import hashlib

# ── Arc timing boundaries (match _arc_from_time) ─────────────────
_ARC_TIMING = {
    "hook": (0.0, 0.15),
    "build": (0.15, 0.55),
    "peak": (0.55, 0.70),
    "release": (0.70, 0.85),
    "resolve": (0.85, 1.0),
}


def _selector_index(key: str, count: int) -> int:
    """Same deterministic hash selector as everywhere else."""
    if count <= 0:
        return 0
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    n = int.from_bytes(digest[:16], "big")
    return n % count


def _generate_sfx_events(plan_id: str, channel_id: str, duration_s: float) -> list[dict]:
    """Generate therapeutic SFX events per arc section from the SFX bank index.

    Returns list of SFX events, each with: arc, category, asset_id, file,
    start_s, end_s, level_db, pitch_shift_pct.

    Light touch: 1-2 layers per arc section, -22 to -30 dB.
    Deterministic: same plan_id + channel_id → same SFX selection.
    """
    sfx_index = load_yaml("config/video/sfx_bank_index.yaml")
    if not sfx_index:
        return []

    categories = sfx_index.get("categories") or {}
    arc_to_sfx = sfx_index.get("arc_to_sfx") or {}
    arc_to_level = sfx_index.get("arc_to_level_db") or {}

    events = []
    for arc, (start_pct, end_pct) in _ARC_TIMING.items():
        arc_sfx = arc_to_sfx.get(arc)
        if not arc_sfx:
            continue

        start_s = round(duration_s * start_pct, 2)
        end_s = round(duration_s * end_pct, 2)
        level_db = arc_to_level.get(arc, -26)

        # Primary SFX layer
        primary_cat = arc_sfx.get("primary")
        if primary_cat and primary_cat in categories:
            variants = categories[primary_cat].get("variants") or []
            if variants:
                idx = _selector_index(f"sfx|{primary_cat}|{channel_id}|{plan_id}", len(variants))
                variant = variants[idx]
                # Deterministic pitch shift: ±3% based on hash
                pitch_hash = _selector_index(f"pitch|{primary_cat}|{plan_id}", 7)
                pitch_shift = (pitch_hash - 3) * 1.0  # -3% to +3%
                events.append({
                    "arc": arc,
                    "layer": "primary",
                    "category": primary_cat,
                    "asset_id": variant["id"],
                    "file": variant["file"],
                    "start_s": start_s,
                    "end_s": end_s,
                    "level_db": level_db,
                    "pitch_shift_pct": round(pitch_shift, 1),
                    "fade_in_s": 2.0,
                    "fade_out_s": 2.0,
                })

        # Secondary SFX layer (if specified and arc has 2 layers)
        secondary_cat = arc_sfx.get("secondary")
        layers = arc_sfx.get("layers", 1)
        if secondary_cat and layers >= 2 and secondary_cat in categories:
            variants = categories[secondary_cat].get("variants") or []
            if variants:
                idx = _selector_index(f"sfx|{secondary_cat}|{channel_id}|{plan_id}|secondary", len(variants))
                variant = variants[idx]
                events.append({
                    "arc": arc,
                    "layer": "secondary",
                    "category": secondary_cat,
                    "asset_id": variant["id"],
                    "file": variant["file"],
                    "start_s": start_s,
                    "end_s": end_s,
                    "level_db": level_db - 4,  # secondary is 4dB quieter
                    "pitch_shift_pct": 0,
                    "fade_in_s": 3.0,
                    "fade_out_s": 3.0,
                })

    return events


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
            "primary_atom_id": seg.get("primary_atom_id") or "",
            "speakable_text": seg.get("speakable_text") or "",
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
            "url": _elevenlabs_tts_url(voice_id),
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

    # ── Therapeutic SFX events (per arc section) ────────────────────
    # Resolved from config/video/sfx_bank_index.yaml.
    # Light touch: 1-2 layers, -22 to -30 dB, deterministic selection.
    sfx_events = _generate_sfx_events(plan_id, channel_id, duration)

    # Add SFX tracks to mix_spec
    if sfx_events:
        mix_spec["tracks"].append(
            {"id": "sfx_primary", "level_db": -26, "pan": "stereo",
             "optional": True, "ducking": "voice_minus_4db_when_active"}
        )
        mix_spec["tracks"].append(
            {"id": "sfx_secondary", "level_db": -30, "pan": "wide_stereo",
             "optional": True}
        )

    return {
        "plan_id": plan_id,
        "channel_id": channel_id,
        "config_hash": config_snapshot_hash(),
        "duration_s": duration,
        "narration_segments": narration_segments,
        "suno_api_calls": suno_calls,
        "elevenlabs_api_calls": eleven_calls,
        "sfx_events": sfx_events,
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
    ap.add_argument("--workspace", type=str, default=None, help="Directory containing job.json (default: parent of --out)")
    ap.add_argument("--no-job-check", dest="no_job_check", action="store_true", help="Skip job.json enforcement (CI only)")
    args = ap.parse_args()
    if args.no_job_check:
        print("WARNING: --no-job-check: pipeline job enforcement disabled (CI/testing only).", file=sys.stderr)
    from scripts.pipeline._video_workspace import resolve_video_workspace
    from scripts.pipeline.advance_stage import mark_complete, mark_failed
    from scripts.pipeline.check_job import require_stage

    ws = resolve_video_workspace(args, out_attr="out")
    if not args.no_job_check:
        require_stage("soundtrack", ws)

    paths = [Path(args.timeline), Path(args.shot_plan), Path(args.script_segments)]
    if not all(p.exists() for p in paths):
        if not args.no_job_check:
            mark_failed(ws, "soundtrack", error="input not found")
        print("Error: input not found", file=sys.stderr)
        return 1
    tl, sp, ss = load_json(paths[0]), load_json(paths[1]), load_json(paths[2])
    out = Path(args.out)
    h = config_snapshot_hash()
    if should_skip_output(out, ["plan_id", "mix_spec", "config_hash"], args.force, h):
        print(f"Skip (exists): {out}")
        if not args.no_job_check:
            mark_complete(ws, "soundtrack", output=out.name)
        return 0
    doc = run_soundtrack(tl, sp, ss, args.channel_id)
    write_atomically(out, doc)
    print(f"Wrote soundtrack_plan to {out}")
    if not args.no_job_check:
        mark_complete(ws, "soundtrack", output=out.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
