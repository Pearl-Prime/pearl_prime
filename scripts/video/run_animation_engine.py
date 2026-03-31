#!/usr/bin/env python3
"""
Stage 13 — Animation Engine: composited_layers + shot_plan + timeline -> animation_plan.json.
VCE §5–§6: motion types, ITE camera mapping hints, arc entrainment from pacing config.
Usage: python scripts/video/run_animation_engine.py <composited_layers.json> <shot_plan.json> <timeline.json> -o animation_plan.json [--format short]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import config_snapshot_hash, load_json, load_yaml, should_skip_output, write_atomically

# All VCE motion kinds — cycled across shots for catalog coverage while arc picks therapeutic bias
_MOTION_CYCLE = (
    "ken_burns",
    "parallax_scroll",
    "breathing_pulse",
    "particle_system",
    "camera_pan",
    "scale_drift",
    "text_reveal",
    "water_nature_loop",
)


def _motion_for_arc(section: str) -> str:
    low_motion = {"RELEASE", "RESOLVE"}
    if section in low_motion:
        return "camera_pan" if section == "RELEASE" else "static"
    if section == "HOOK":
        return "ken_burns"
    if section == "PEAK":
        return "breathing_pulse"
    return "parallax_scroll"


def _motion_for_shot(section: str, shot_index: int) -> str:
    """Arc-first, with cycle index to expose every motion kind across a long plan."""
    base = _motion_for_arc(section)
    if shot_index % 4 == 0:
        return _MOTION_CYCLE[shot_index % len(_MOTION_CYCLE)]
    return base


def _ite_camera_mapping(motion_type: str) -> str:
    m = load_yaml("config/video/animation_types.yaml").get("motion_types") or {}
    return (m.get(motion_type) or {}).get("therapeutic_use", "none")


def _arc_cut_interval(section: str, arc_p: dict) -> dict:
    row = (arc_p or {}).get(section) or {}
    if isinstance(row.get("cut_interval_s"), list) and len(row["cut_interval_s"]) == 2:
        lo, hi = row["cut_interval_s"]
        return {"cut_interval_s_min": float(lo), "cut_interval_s_max": float(hi)}
    if row.get("cut_interval_s_min") is not None:
        return {
            "cut_interval_s_min": float(row.get("cut_interval_s_min", 2)),
            "cut_interval_s_max": float(row.get("cut_interval_s_max", 12)),
        }
    return {"cut_interval_s_min": 2.0, "cut_interval_s_max": 8.0}


def _ffmpeg_motion_bundle(
    motion_type: str,
    duration_s: float,
    out_w: int,
    out_h: int,
    fps: int,
    shot_id: str,
) -> dict:
    """Frame-accurate FFmpeg-oriented params (expressions verified for filtergraph syntax)."""
    frames = max(1, int(round(float(duration_s) * int(fps))))
    mt = (motion_type or "static").lower().replace("-", "_")
    tau = 10.0  # breathing / drift cycle (seconds); ~6 breaths/min for 10s sinusoid
    period = 10.0

    if mt == "ken_burns":
        return {
            "motion": mt,
            "fps": fps,
            "duration_frames": frames,
            "zoompan": (
                f"z='min(zoom+0.0015,1.5)':d={frames}:s={out_w}x{out_h}:fps={fps}"
            ),
            "notes": "Classic Ken Burns — accumulate zoom cap 1.5 (VCE §5 ken_burns).",
        }

    if mt == "parallax_scroll":
        speed = 12.0
        return {
            "motion": mt,
            "fps": fps,
            "duration_frames": frames,
            "crop": f"crop={out_w}:{out_h}:min(max(0\\,(iw-{out_w})/2+{speed}*t)\\,iw-{out_w}):0",
            "notes": "Parallax as sliding crop window on overscaled plate.",
        }

    if mt == "breathing_pulse":
        return {
            "motion": mt,
            "fps": fps,
            "duration_frames": frames,
            "zoompan": (
                f"z='1+0.03*sin(2*PI*t/{tau})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={frames}:s={out_w}x{out_h}:fps={fps}"
            ),
            "bpm_equiv": 6,
            "notes": "Subtle zoom sinusoid ~6 BPM therapeutic pulse (spec §6.5).",
        }

    if mt == "particle_system":
        vx = 28
        start = 0.0
        ow, oh = out_w, out_h
        return {
            "motion": mt,
            "fps": fps,
            "particle": {
                "overlay_position_x": f"if(gte(t\\,{start})\\,5+mod({vx}*t\\,{ow}-10)\\,5)",
                "overlay_position_y": f"if(gte(t\\,{start})\\,{oh}*0.2+0.15*{oh}*sin(2*PI*t/14)\\,{oh}*0.2)",
            },
            "overlay_filter_fragment": (
                f"[fg]format=rgba,colorchannelmixer=aa=0.55[fg_a];"
                f"[base][fg_a]overlay=x='if(gte(t\\,{start})\\,5+mod({vx}*t\\,{ow}-10)\\,5)':"
                f"y='if(gte(t\\,{start})\\,{oh}*0.2+0.15*{oh}*sin(2*PI*t/14)\\,{oh}*0.2)':format=auto"
            ),
            "notes": "Foreground spark layer composited over base.",
        }

    if mt == "camera_pan":
        return {
            "motion": mt,
            "fps": fps,
            "duration_frames": frames,
            "crop": (
                f"crop={out_w}:{out_h}:"
                f"'(iw-{out_w})/2+40*sin(t/6)':"
                f"'(ih-{out_h})/2+24*cos(t/7)'"
            ),
            "notes": "Angle-derived drift as separable sinusoids on crop origin.",
        }

    if mt == "scale_drift":
        return {
            "motion": mt,
            "fps": fps,
            "duration_frames": frames,
            "zoompan": (
                f"z='1+0.02*sin(2*PI*t/{period})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={frames}:s={out_w}x{out_h}:fps={fps}"
            ),
            "period_s": period,
        }

    if mt == "text_reveal":
        t0, t1 = 0.0, max(0.01, float(duration_s))
        return {
            "motion": mt,
            "fps": fps,
            "drawtext": (
                f"drawtext=text='{{caption}}':fontsize=52:fontcolor=white@'if(between(t\\,{t0}\\,{t1})\\,"
                f"(t-{t0})/{max(1e-6, t1 - t0)}\\,0)':"
                f"enable='between(t\\,{t0}\\,{t1})':x=(w-text_w)/2:y=h*0.78"
            ),
            "notes": "Alpha fades in over shot duration; caption substituted at render.",
        }

    if mt == "water_nature_loop":
        return {
            "motion": mt,
            "fps": fps,
            "loop_filter": f"loop=loop=-1:size={frames}:start=0",
            "setpts_reset": "setpts=N/FRAME_RATE/TB",
            "notes": "Seamless loop metadata for background clips (VCE water_nature_loop).",
        }

    # static
    return {
        "motion": "static",
        "fps": fps,
        "duration_frames": frames,
        "zoompan": f"z='1':d={frames}:s={out_w}x{out_h}:fps={fps}",
        "shot_id": shot_id,
    }


def run_animation(
    composited: dict,
    shot_plan: dict,
    timeline: dict,
    format_key: str,
) -> dict:
    motion_policy = load_yaml("config/video/motion_policy.yaml")
    pacing_yaml = load_yaml("config/video/pacing_by_content_type.yaml")
    arc_p = pacing_yaml.get("arc_section_pacing") or {}
    anim_types = load_yaml("config/video/animation_types.yaml").get("motion_types") or {}
    color_rules = load_yaml("config/video/therapeutic_video_rules.yaml").get("color_temp_arc") or {}

    fmt_cfg = load_yaml("config/video/format_specs.yaml")
    formats = fmt_cfg.get("formats") or {}
    spec = formats.get(format_key) or formats.get(fmt_cfg.get("default_format_key", "short"), {})
    reso = spec.get("resolution") or timeline.get("resolution") or {}
    out_w = int(reso.get("width", timeline.get("resolution", {}).get("width", 1080)))
    out_h = int(reso.get("height", timeline.get("resolution", {}).get("height", 1920)))
    fps = int(spec.get("fps") or timeline.get("fps") or 24)

    motion_templates = {
        m: _ffmpeg_motion_bundle(m, 5.0, out_w, out_h, fps, "template")
        for m in sorted(set(_MOTION_CYCLE) | {"ken_burns", "static"})
    }

    shots_anim = []
    cum_t = 0.0
    duration_total = float(timeline.get("duration_s") or 0)
    clips_by_shot = {c.get("shot_id"): c for c in timeline.get("clips") or []}

    for i, shot in enumerate(shot_plan.get("shots") or []):
        sid = shot["shot_id"]
        clip = clips_by_shot.get(sid) or {}
        dur = float(clip.get("end_time_s", cum_t + 3) - clip.get("start_time_s", cum_t))
        if dur <= 0:
            dur = float(shot.get("duration_s") or 3.0)
        cum_t += dur

        pct = (cum_t / duration_total * 100) if duration_total > 0 else 0
        if pct < 15:
            section = "HOOK"
        elif pct < 55:
            section = "BUILD"
        elif pct < 70:
            section = "PEAK"
        elif pct < 85:
            section = "RELEASE"
        else:
            section = "RESOLVE"

        motion_type = _motion_for_shot(section, i)
        type_spec = anim_types.get(motion_type) or {}
        max_speed = type_spec.get("max_speed_px_per_sec_l1") or type_spec.get("max_zoom_pct_per_sec") or type_spec.get("max_speed_deg_per_sec")

        fps_eff = int(type_spec.get("fps") or fps)
        bundle = _ffmpeg_motion_bundle(motion_type, dur, out_w, out_h, fps_eff, sid)

        shots_anim.append({
            "shot_id": sid,
            "arc_section": section,
            "motion_type": motion_type,
            "ite_motion_hint": _ite_camera_mapping(motion_type),
            "arc_pacing_ref": arc_p.get(section),
            "arc_cut_interval_s": _arc_cut_interval(section, arc_p),
            "max_speed_hint": max_speed,
            "static_fraction_policy": motion_policy.get("motion_distribution", {}).get("static"),
            "ffmpeg_motion": bundle,
            "colorbalance_section": color_rules.get(section),
            "duration_s": round(dur, 3),
            "clip_start_global_s": round(cum_t - dur, 3),
        })

    return {
        "plan_id": composited.get("plan_id") or shot_plan.get("plan_id"),
        "vce_format": format_key,
        "config_hash": config_snapshot_hash(),
        "content_type": shot_plan.get("content_type"),
        "output_resolution": {"width": out_w, "height": out_h},
        "default_fps": fps,
        "ffmpeg_motion_templates": motion_templates,
        "motion_cycle": list(_MOTION_CYCLE),
        "shots": shots_anim,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="VCE Stage 13 — Animation engine")
    ap.add_argument("composited_layers", help="composited_layers.json")
    ap.add_argument("shot_plan", help="shot_plan.json")
    ap.add_argument("timeline", help="timeline.json")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--format", default="short")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    paths = [Path(args.composited_layers), Path(args.shot_plan), Path(args.timeline)]
    if not all(p.exists() for p in paths):
        print("Error: input not found", file=sys.stderr)
        return 1
    comp = load_json(paths[0])
    sp = load_json(paths[1])
    tl = load_json(paths[2])
    out = Path(args.out)
    h = config_snapshot_hash()
    if should_skip_output(out, ["plan_id", "shots", "config_hash"], args.force, h):
        print(f"Skip (exists): {out}")
        return 0
    doc = run_animation(comp, sp, tl, args.format)
    write_atomically(out, doc)
    print(f"Wrote animation_plan with {len(doc['shots'])} shots to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
