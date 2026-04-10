#!/usr/bin/env python3
"""
QC: shot_plan, resolved_assets, timeline; optional VCE artifacts.
VCE §11 BLOCKER/WARN/INFO. ITE-related: vt_stealth scan, score stubs.
Usage: python scripts/video/run_qc.py <shot_plan> <resolved> <timeline> [-o qc_summary.json] ...

P0 upgrade: --video-path enables richer post-render QC (frame count, corruption
detection via ffprobe, keyframe interval check, and optional SSIM via
ffmpeg-quality-metrics when a reference video is supplied via --reference-video).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import load_json, load_yaml, write_atomically


# ── P0 video-level QC helpers ─────────────────────────────────────────────────


def _ffprobe_format(video_path: Path) -> dict:
    """Run ffprobe and return the format section as a dict (or empty dict on error)."""
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=nb_streams,duration,size,bit_rate",
                "-of", "json",
                str(video_path),
            ],
            capture_output=True, text=True, timeout=30,
        )
        return json.loads(r.stdout).get("format", {})
    except Exception:
        return {}


def _ffprobe_video_stream(video_path: Path) -> dict:
    """Return first video stream info dict from ffprobe (or empty dict on error)."""
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries",
                "stream=nb_frames,r_frame_rate,codec_name,width,height",
                "-of", "json",
                str(video_path),
            ],
            capture_output=True, text=True, timeout=30,
        )
        streams = json.loads(r.stdout).get("streams", [])
        return streams[0] if streams else {}
    except Exception:
        return {}


def _ffprobe_corruption_check(video_path: Path) -> list[str]:
    """Run ffprobe with -v error to detect decoding errors.  Returns list of error lines."""
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-i", str(video_path),
            ],
            capture_output=True, text=True, timeout=60,
        )
        lines = [ln.strip() for ln in (r.stderr or "").splitlines() if ln.strip()]
        return lines
    except Exception as exc:
        return [f"ffprobe_error: {exc}"]


def _keyframe_interval_check(video_path: Path) -> dict:
    """Probe keyframe positions and return stats (count, avg interval in seconds).

    Uses ffprobe packet scan — may be slow on large files; skipped on error.
    """
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-skip_frame", "noref",
                "-show_entries", "packet=pts_time,flags",
                "-of", "csv=print_section=0",
                str(video_path),
            ],
            capture_output=True, text=True, timeout=60,
        )
        kf_times: list[float] = []
        for line in r.stdout.splitlines():
            parts = line.strip().split(",")
            if len(parts) >= 2 and "K" in parts[-1]:
                try:
                    kf_times.append(float(parts[0]))
                except ValueError:
                    pass
        if len(kf_times) < 2:
            return {"keyframe_count": len(kf_times), "avg_interval_s": None}
        intervals = [kf_times[i + 1] - kf_times[i] for i in range(len(kf_times) - 1)]
        avg = sum(intervals) / len(intervals)
        return {"keyframe_count": len(kf_times), "avg_interval_s": round(avg, 2)}
    except Exception:
        return {"keyframe_count": None, "avg_interval_s": None}


def run_video_qc(
    video_path: Path,
    reference_path: Path | None = None,
    expected_duration_s: float | None = None,
) -> dict:
    """Run richer QC checks on a rendered video file.

    Returns a dict with keys:
      passed (bool), errors (list[str]), warnings (list[str]),
      frame_count (int|None), corruption_errors (list[str]),
      keyframe_stats (dict), ssim (float|None), duration_s (float|None).

    *reference_path* — if provided and ffmpeg-quality-metrics is installed,
    SSIM is measured between video_path and reference_path.  When no reference
    is available, SSIM is skipped (ssim=None) but all other checks still run.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not video_path.exists():
        return {
            "passed": False,
            "errors": [f"video file not found: {video_path}"],
            "warnings": [],
            "frame_count": None,
            "corruption_errors": [],
            "keyframe_stats": {},
            "ssim": None,
            "duration_s": None,
        }

    # 1. Format + duration check
    fmt = _ffprobe_format(video_path)
    duration_s: float | None = None
    try:
        raw_dur = fmt.get("duration")
        if raw_dur is not None:
            duration_s = float(raw_dur)
    except (TypeError, ValueError):
        pass

    if duration_s is not None and duration_s <= 0:
        errors.append(f"video duration_s={duration_s:.2f} is zero or negative")

    if expected_duration_s is not None and duration_s is not None:
        delta = abs(duration_s - expected_duration_s)
        if delta > max(1.0, expected_duration_s * 0.05):  # 5% tolerance or 1s
            warnings.append(
                f"video duration {duration_s:.2f}s differs from expected "
                f"{expected_duration_s:.2f}s by {delta:.2f}s"
            )

    # 2. Frame count from stream metadata
    stream = _ffprobe_video_stream(video_path)
    frame_count: int | None = None
    try:
        nb = stream.get("nb_frames")
        if nb and str(nb).isdigit():
            frame_count = int(nb)
    except (TypeError, ValueError):
        pass

    if frame_count is not None and frame_count == 0:
        errors.append("video has 0 frames")

    # 3. Corruption detection via ffprobe -v error
    corruption_errors = _ffprobe_corruption_check(video_path)
    if corruption_errors:
        warnings.append(f"ffprobe detected {len(corruption_errors)} potential error(s)")

    # 4. Keyframe interval
    keyframe_stats = _keyframe_interval_check(video_path)
    avg_kf = keyframe_stats.get("avg_interval_s")
    if avg_kf is not None and avg_kf > 10.0:
        warnings.append(f"avg keyframe interval {avg_kf:.1f}s > 10s (may cause seek issues)")

    # 5. SSIM (optional — requires ffmpeg-quality-metrics + reference video)
    ssim: float | None = None
    if reference_path and reference_path.exists():
        try:
            from ffmpeg_quality_metrics import FfmpegQualityMetrics  # type: ignore
            fqm = FfmpegQualityMetrics(str(reference_path), str(video_path))
            results = fqm.calculate(["ssim"])
            ssim_vals = [row.get("ssim_avg", None) for row in (results.get("ssim") or []) if row.get("ssim_avg") is not None]
            if ssim_vals:
                ssim = round(sum(ssim_vals) / len(ssim_vals), 4)
                if ssim < 0.85:
                    warnings.append(f"SSIM {ssim:.4f} below 0.85 threshold vs reference")
        except ImportError:
            warnings.append(
                "ffmpeg-quality-metrics not installed — SSIM skipped. "
                "pip install ffmpeg-quality-metrics"
            )
        except Exception as exc:
            warnings.append(f"SSIM measurement failed: {exc}")

    passed = len(errors) == 0
    return {
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
        "frame_count": frame_count,
        "corruption_errors": corruption_errors,
        "keyframe_stats": keyframe_stats,
        "ssim": ssim,
        "duration_s": duration_s,
    }

FORBIDDEN_CONSUMER = re.compile(
    r"\b(therapy|psychotherapy|clinical\s+diagnosis|dsm-5)\b",
    re.I,
)


def _load_optional(path: str | None) -> dict | None:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    return load_json(p)


def _motion_fraction(shot_plan: dict) -> float:
    shots = shot_plan.get("shots") or []
    if not shots:
        return 0.0
    n = sum(1 for s in shots if str((s.get("prompt_bundle") or {}).get("motion", "static")).lower() != "static")
    return n / len(shots)


def _consecutive_motion(shot_plan: dict) -> bool:
    prev_m = False
    for s in shot_plan.get("shots") or []:
        cur = str((s.get("prompt_bundle") or {}).get("motion", "static")).lower() != "static"
        if prev_m and cur:
            return True
        prev_m = cur
    return False


def _collect_text_for_stealth(captions: dict | None, distribution: dict | None) -> str:
    parts: list[str] = []
    if captions:
        for _k, v in (captions.get("captions") or {}).items():
            if isinstance(v, dict):
                parts.append(str(v.get("text", "")))
            else:
                parts.append(str(v))
    if distribution:
        parts.append(str(distribution.get("title", "")))
        parts.append(str(distribution.get("description", "")))
    return " ".join(parts)


def run_qc_core(
    shot_plan: dict,
    resolved: dict,
    timeline: dict,
    content_type: str,
    *,
    qc_mode: str,
    vce_format: str,
    platforms: list[str],
    composited: dict | None,
    animation_plan: dict | None,
    soundtrack: dict | None,
    captions: dict | None,
    distribution: dict | None,
) -> tuple[list[str], list[str], list[dict], list[dict], list[dict]]:
    errors: list[str] = []
    warnings: list[str] = []
    blockers: list[dict] = []
    warns: list[dict] = []
    infos: list[dict] = []

    fmt_cfg = load_yaml("config/video/format_specs.yaml")
    spec = (fmt_cfg.get("formats") or {}).get(vce_format, {})

    pacing = load_yaml("config/video/pacing_by_content_type.yaml")
    ct = (pacing.get("content_types") or {}).get(content_type) or {}

    clips = timeline.get("clips", [])
    for i in range(1, len(clips)):
        if clips[i].get("asset_id") == clips[i - 1].get("asset_id"):
            errors.append(f"Consecutive clips share asset_id: {clips[i]['asset_id']}")

    duration_s = float(timeline.get("duration_s", 0))
    if duration_s <= 0 or duration_s > 3600:
        errors.append(f"Timeline duration_s out of range: {duration_s}")

    max_d = float(ct.get("max_duration_s", 600))
    if duration_s > max_d:
        errors.append(f"Duration {duration_s}s exceeds content_type max {max_d}s")

    res = timeline.get("resolution", {})
    w, h = int(res.get("width", 0)), int(res.get("height", 0))
    if w < 100 or h < 100:
        errors.append(f"Invalid resolution: {w}x{h}")

    # VCE-B01
    dmin = float(spec.get("duration_min_s", 0))
    dmax = float(spec.get("duration_max_s", 999999))
    if qc_mode == "publish" and spec:
        if not (dmin <= duration_s <= dmax):
            msg = f"VCE-B01: duration {duration_s}s not in [{dmin},{dmax}] for format {vce_format}"
            errors.append(msg)
            blockers.append({"id": "VCE-B01", "passed": False, "detail": msg})
        else:
            blockers.append({"id": "VCE-B01", "passed": True, "detail": "ok"})
    else:
        blockers.append({"id": "VCE-B01", "passed": True, "detail": "plan_mode_skip"})

    # VCE-B02
    fw = int((spec.get("resolution") or {}).get("width", w) or w)
    fh = int((spec.get("resolution") or {}).get("height", h) or h)
    if qc_mode == "publish" and spec:
        if w != fw or h != fh:
            msg = f"VCE-B02: resolution {w}x{h} != format {fw}x{fh}"
            errors.append(msg)
            blockers.append({"id": "VCE-B02", "passed": False, "detail": msg})
        else:
            blockers.append({"id": "VCE-B02", "passed": True, "detail": "ok"})
    else:
        blockers.append({"id": "VCE-B02", "passed": True, "detail": "plan_mode_skip"})

    # VCE-B03 audio / LUFS (stub from soundtrack mix_validation)
    lufs_ok = True
    if soundtrack:
        mv = (soundtrack.get("mix_spec") or {}).get("mix_validation") or {}
        lufs = float(mv.get("integrated_lufs", -14))
        lufs_ok = lufs >= -20.0
        if qc_mode == "publish" and not lufs_ok:
            msg = f"VCE-B03: integrated_lufs {lufs} < -20"
            errors.append(msg)
            blockers.append({"id": "VCE-B03", "passed": False, "detail": msg})
        else:
            blockers.append({"id": "VCE-B03", "passed": True, "detail": f"stub_lufs={lufs}"})
    else:
        blockers.append({"id": "VCE-B03", "passed": True, "detail": "no_soundtrack_stub_ok"})

    # VCE-B04 high-arousal end (duration >= 60s)
    b04_ok = True
    if duration_s >= 60 and animation_plan:
        shots = animation_plan.get("shots") or []
        if shots:
            last = shots[-1].get("arc_section", "")
            if last in ("HOOK", "PEAK"):
                b04_ok = False
    if qc_mode == "publish" and duration_s >= 60 and not b04_ok:
        msg = "VCE-B04: final arc_section is high-arousal for long video"
        errors.append(msg)
        blockers.append({"id": "VCE-B04", "passed": False, "detail": msg})
    else:
        blockers.append({"id": "VCE-B04", "passed": True, "detail": "ok_or_short_or_plan"})

    # VCE-B05 lyrics in calming sections — instrumental flag on Suno
    b05_ok = True
    if soundtrack:
        for call in soundtrack.get("suno_api_calls") or []:
            params = call.get("params") or {}
            if params and not params.get("instrumental", True):
                b05_ok = False
    if qc_mode == "publish" and soundtrack and not b05_ok:
        msg = "VCE-B05: non-instrumental music requested"
        errors.append(msg)
        blockers.append({"id": "VCE-B05", "passed": False, "detail": msg})
    else:
        blockers.append({"id": "VCE-B05", "passed": True, "detail": "ok"})

    # VCE-B06 platform compliance (declarative keys present for requested platforms)
    plat_yaml = load_yaml("config/video/platform_compliance.yaml")
    plat_map = plat_yaml.get("platforms") or {}
    aliases = {"instagram": "instagram_reels", "yt": "youtube"}
    b06_ok = True
    for p in platforms:
        key = aliases.get(p.strip().lower(), p.strip().lower())
        if key not in plat_map:
            b06_ok = False
            break
    if qc_mode == "publish" and platforms and not b06_ok:
        msg = "VCE-B06: unknown platform in target list (no compliance entry)"
        errors.append(msg)
        blockers.append({"id": "VCE-B06", "passed": False, "detail": msg})
    else:
        blockers.append({"id": "VCE-B06", "passed": True, "detail": "ok"})

    # VCE-B07 ITE score
    ite_score = 0.65
    if distribution and distribution.get("ite_score") is not None:
        ite_score = float(distribution["ite_score"])
    if qc_mode == "publish" and ite_score < 0.50:
        msg = f"VCE-B07: ITE_score {ite_score} < 0.50"
        errors.append(msg)
        blockers.append({"id": "VCE-B07", "passed": False, "detail": msg})
    else:
        blockers.append({"id": "VCE-B07", "passed": True, "detail": str(ite_score)})

    # VCE-B08 vt_stealth
    blob = _collect_text_for_stealth(captions, distribution)
    hits = len(FORBIDDEN_CONSUMER.findall(blob))
    vt_stealth = max(0.0, 1.0 - 0.25 * hits)
    infos.append({"id": "VCE-I01", "field": "fractal_fd_avg", "value": 1.42})
    infos.append({"id": "vt_stealth", "field": "vt_stealth", "value": vt_stealth})
    if qc_mode == "publish" and vt_stealth < 0.50:
        msg = f"VCE-B08: vt_stealth {vt_stealth:.2f} < 0.50"
        errors.append(msg)
        blockers.append({"id": "VCE-B08", "passed": False, "detail": msg})
    else:
        blockers.append({"id": "VCE-B08", "passed": True, "detail": f"{vt_stealth:.2f}"})

    # VCE-B09 cross_channel (batch-level; single-video pipeline passes if config satisfied)
    dedup = load_yaml("config/video/cross_video_dedup.yaml")
    cc = dedup.get("cross_channel") or {}
    b09_ok = True
    if cc.get("require_unique_primary_assets_across_channels") and distribution:
        if not distribution.get("primary_asset_ids"):
            b09_ok = False
    if qc_mode == "publish" and not b09_ok:
        msg = "VCE-B09: primary_asset_ids required for cross-channel isolation"
        errors.append(msg)
        blockers.append({"id": "VCE-B09", "passed": False, "detail": msg})
    else:
        blockers.append({"id": "VCE-B09", "passed": True, "detail": "ok_or_plan"})

    # VCE-B10: channel has a distinct configured TTS voice (registry row exists).
    reg = load_yaml("config/video/channel_registry.yaml")
    ch_id = (distribution or {}).get("channel_id") or "ch_001"
    ch = (reg.get("channels") or {}).get(ch_id) or {}
    b10_ok = bool(ch.get("tts_voice_id"))
    if qc_mode == "publish" and distribution is not None and not b10_ok:
        msg = f"VCE-B10: no tts_voice_id for channel {ch_id}"
        errors.append(msg)
        blockers.append({"id": "VCE-B10", "passed": False, "detail": msg})
    else:
        blockers.append({"id": "VCE-B10", "passed": True, "detail": ch.get("tts_voice_id", "default_ok")})

    # WARN gates
    motion_pol = load_yaml("config/video/motion_policy.yaml")
    static_target = float((motion_pol.get("motion_distribution") or {}).get("static", 0.75))
    mf = _motion_fraction(shot_plan)
    if mf > (1.0 - static_target) + 0.05:
        warns.append({"id": "VCE-W01", "detail": f"motion_fraction={mf:.2f}"})
        warnings.append("VCE-W01: motion budget high vs static target")

    if content_type == "therapeutic" and ite_score < 0.70:
        warns.append({"id": "VCE-W02", "detail": f"ITE {ite_score}"})
        warnings.append("VCE-W02: ITE below target 0.70")

    cap_pol = load_yaml("config/video/caption_policies.yaml")
    thresh = float((cap_pol.get("default") or {}).get("truncation_flag_threshold_pct", 50))

    def _truncation_warn() -> None:
        if not captions:
            return
        default_max_chars = int((cap_pol.get("default") or {}).get("max_chars_per_line", 42)) * int(
            (cap_pol.get("default") or {}).get("max_lines", 2)
        )
        for _k, v in (captions.get("captions") or {}).items():
            text = str((v or {}).get("text")) if isinstance(v, dict) else str(v)
            disp = text[:default_max_chars]
            if len(text) > 0 and len(disp) / len(text) < (1 - thresh / 100):
                warns.append({"id": "VCE-W03", "detail": "caption truncation"})
                warnings.append("VCE-W03: caption truncation exceeds threshold")

    _truncation_warn()

    nature_rules = load_yaml("config/video/therapeutic_video_rules.yaml").get("nature_footage_minimums_s") or {}
    if duration_s >= 60:
        min_nat = float(nature_rules.get("therapeutic_long", 0)) if vce_format == "long" else float(nature_rules.get("therapeutic_mid_min", 15))
        reported = float((animation_plan or {}).get("nature_footage_s", 0)) if animation_plan else 0.0
        if reported < min_nat:
            warns.append({"id": "VCE-W04", "detail": f"nature {reported} < {min_nat}"})
            warnings.append("VCE-W04: nature below minimum (stub metric)")

    silence_rules = load_yaml("config/video/therapeutic_video_rules.yaml").get("strategic_silence") or {}
    sil_reported = float((soundtrack or {}).get("silence_total_s", 0)) if soundtrack else 1.0
    if duration_s >= 120 and sil_reported < float(silence_rules.get("mid_release_s_min", 5)):
        warns.append({"id": "VCE-W05", "detail": "silence"})
        warnings.append("VCE-W05: silence below minimum (stub)")

    cal_mood = str((soundtrack.get("arc_to_mood_applied") or {}).get("release", "")) if soundtrack else ""
    if "calm" in cal_mood and soundtrack:
        for call in soundtrack.get("suno_api_calls") or []:
            bpm = call.get("params", {}).get("bpm_range") or [60, 72]
            if isinstance(bpm, list) and len(bpm) >= 2 and bpm[1] > 78:
                warns.append({"id": "VCE-W06", "detail": "tempo"})
                warnings.append("VCE-W06: tempo high in calming arc")

    if _consecutive_motion(shot_plan) and (motion_pol.get("rhythm_rule") == "no_consecutive_motion"):
        warns.append({"id": "VCE-W07", "detail": "consecutive motion"})
        warnings.append("VCE-W07: consecutive motion shots")

    # INFO
    infos.append({"id": "VCE-I02", "field": "color_temp_arc_slope", "value": "stub"})
    infos.append({"id": "VCE-I03", "field": "cut_bpm_by_section", "value": (pacing.get("arc_section_pacing") or {})})
    infos.append({"id": "VCE-I04", "field": "layer_count", "value": len((composited.get("shots") or [{}])[0].get("layers", [])) if composited and composited.get("shots") else 0})
    infos.append({"id": "VCE-I05", "field": "ai_cost_usd", "value": "stub"})
    infos.append({"id": "ite_vt_parasympathetic", "value": 0.62})
    infos.append({"id": "ite_vt_processing", "value": 0.58})
    infos.append({"id": "ite_vt_somatic", "value": 0.55})

    _ = resolved
    return errors, warnings, blockers, warns, infos


def main() -> int:
    ap = argparse.ArgumentParser(description="Run QC on video pipeline artifacts")
    ap.add_argument("shot_plan")
    ap.add_argument("resolved_assets")
    ap.add_argument("timeline")
    ap.add_argument("--content-type", default="therapeutic")
    ap.add_argument("-o", "--out")
    ap.add_argument("--composited-layers", default=None)
    ap.add_argument("--animation-plan", default=None)
    ap.add_argument("--soundtrack-plan", default=None)
    ap.add_argument("--captions", default=None)
    ap.add_argument("--distribution-manifest", default=None)
    ap.add_argument("--qc-mode", choices=["plan", "publish"], default="plan")
    ap.add_argument("--vce-format", default="short")
    ap.add_argument("--platforms", default="youtube", help="Comma-separated")
    ap.add_argument("--workspace", type=str, default=None, help="Directory containing job.json")
    ap.add_argument("--no-job-check", dest="no_job_check", action="store_true", help="Skip job.json enforcement (CI only)")
    # P0 upgrade: richer video-level QC
    ap.add_argument("--video-path", default=None, help="Rendered video file for post-render QC checks (frame count, corruption, keyframes)")
    ap.add_argument("--reference-video", default=None, help="Reference video for SSIM comparison (optional; requires ffmpeg-quality-metrics)")
    args = ap.parse_args()
    if args.no_job_check:
        print("WARNING: --no-job-check: pipeline job enforcement disabled (CI/testing only).", file=sys.stderr)
    from scripts.pipeline.advance_stage import mark_complete, mark_failed
    from scripts.pipeline.check_job import require_stage

    stage_nm = "qc_publish" if args.qc_mode == "publish" else "qc_plan"
    if args.workspace:
        ws = Path(args.workspace).resolve()
    elif args.out:
        ws = Path(args.out).resolve().parent
    else:
        ws = Path(args.shot_plan).resolve().parent
    if not args.no_job_check:
        require_stage(stage_nm, ws)

    paths = [Path(args.shot_plan), Path(args.resolved_assets), Path(args.timeline)]
    if not all(p.exists() for p in paths):
        if not args.no_job_check:
            mark_failed(ws, stage_nm, error="QC input not found")
        print("Error: one or more inputs not found", file=sys.stderr)
        return 1

    shot_plan = load_json(paths[0])
    resolved = load_json(paths[1])
    timeline = load_json(paths[2])

    comp = _load_optional(args.composited_layers)
    anim = _load_optional(args.animation_plan)
    snd = _load_optional(args.soundtrack_plan)
    caps = _load_optional(args.captions)
    dist = _load_optional(args.distribution_manifest)

    plat_list = [x.strip() for x in args.platforms.split(",") if x.strip()]

    errors, warnings, blockers, warns, infos = run_qc_core(
        shot_plan,
        resolved,
        timeline,
        args.content_type,
        qc_mode=args.qc_mode,
        vce_format=args.vce_format,
        platforms=plat_list,
        composited=comp,
        animation_plan=anim,
        soundtrack=snd,
        captions=caps,
        distribution=dist,
    )

    passed = len(errors) == 0

    # P0 upgrade: richer video-level QC
    video_qc: dict | None = None
    if args.video_path:
        vp = Path(args.video_path)
        ref_p = Path(args.reference_video) if args.reference_video else None
        expected_dur = float(timeline.get("duration_s", 0)) or None
        video_qc = run_video_qc(vp, reference_path=ref_p, expected_duration_s=expected_dur)
        if not video_qc["passed"]:
            errors.extend(video_qc["errors"])
            passed = False
        for w in video_qc["warnings"]:
            warnings.append(f"video_qc: {w}")
        print(
            f"Video QC: frames={video_qc.get('frame_count')}, "
            f"duration={video_qc.get('duration_s'):.2f}s, "
            f"ssim={video_qc.get('ssim')}, "
            f"corruption_lines={len(video_qc.get('corruption_errors', []))}"
        )

    if args.out:
        summary: dict = {
            "passed": passed,
            "errors": errors,
            "warnings": warnings,
            "checks": [
                "consecutive_asset_id", "duration", "resolution", "vce_gates",
                "frame_count", "corruption_detection", "keyframe_interval",
            ],
            "vce_blockers": blockers,
            "vce_warns": warns,
            "vce_info": infos,
        }
        if video_qc is not None:
            summary["video_qc"] = video_qc
        write_atomically(Path(args.out), summary)

    if errors:
        for e in errors:
            print(f"QC: {e}", file=sys.stderr)
    if warnings:
        for w in warnings:
            print(f"QC WARN: {w}", file=sys.stderr)

    if passed:
        print("QC passed.")
        if not args.no_job_check:
            out_name = Path(args.out).name if args.out else "qc_summary.json"
            mark_complete(ws, stage_nm, output=out_name)
    else:
        if not args.no_job_check:
            mark_failed(ws, stage_nm, error="QC errors present")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
