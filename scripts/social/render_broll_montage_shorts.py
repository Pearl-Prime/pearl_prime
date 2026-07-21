#!/usr/bin/env python3
"""Pearl_Animator — Style B: B-roll montage + captions.

Renders 3 vertical (1080x1920) faceless shorts where every beat cuts to a
DIFFERENT stock plate (true montage, not one photo held for 27s). Ken Burns
motion runs continuously within a beat only; the hard cut between beats is
the intentional edit point. Captions are burnt in (drawtext) with a contrast
plate. Audio is synthesized with ffmpeg lavfi: a soft ambient bed plus a
whoosh/hit transient at every cut.

Scope (write): artifacts/qa/social_finish_20260718/lane03_research_complete/
variants/broll_montage/{final/*.mp4, assets_manifest.json, LOOK_VARIANT.md,
validation_receipts.jsonl, _work/**}. This script does not touch
kinetic_type/ or object_metaphor/ and never publishes anything live.
"""
from __future__ import annotations

import os as _os
def _mb_ffmpeg_preset() -> str:
    # Prefer voice-bank batch override, then media-bank, else medium (smoke quality).
    return (
        _os.environ.get("VOICE_BANK_FFMPEG_PRESET")
        or _os.environ.get("MEDIA_BANK_FFMPEG_PRESET")
        or "medium"
    )

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

from PIL import ImageFont

FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"
# Matrix batch sets VOICE_BANK_FFMPEG_PRESET=veryfast; smoke keeps medium quality.
FFMPEG_PRESET = os.environ.get("VOICE_BANK_FFMPEG_PRESET", "medium")
FFMPEG_CRF = os.environ.get("VOICE_BANK_FFMPEG_CRF", "16")

ROOT = Path(__file__).resolve().parents[2]
OUT_ROOT = ROOT / "artifacts/qa/social_finish_20260718/lane03_research_complete/variants/broll_montage"
WORK = OUT_ROOT / "_work"
FINAL = OUT_ROOT / "final"
STOCK_BASE = (
    ROOT
    / "artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x"
    / "downloads/pexels"
)
STORYBOARD_JSON = (
    ROOT
    / "artifacts/qa/social_visual_rebuild_publishable_quality_20260718"
    / "lane05_pearl_animator_rebuild/shortform_publishable_storyboards.json"
)

FONT_CAPTION = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"

W, H, FPS = 1080, 1920, 30
CANVAS_W, CANVAS_H = 1404, 2496  # 1.3x oversized cover-crop canvas for Ken Burns headroom

BEAT_BOUNDS = [(0.0, 1.5), (1.5, 6.0), (6.0, 13.0), (13.0, 22.0), (22.0, 27.0)]
BEAT_ROLES = ["hook", "recognition", "mechanism", "practice", "payoff"]
# One movement per shot; roughly follows motion_policy.yaml intent (mostly
# static/slow) while giving the montage the "several shots telling the
# story" feel the brief asks for. No zoom/pan resets within a beat.
BEAT_MOTIONS = ["push", "pan", "push", "static", "static"]
TOTAL_DURATION_S = BEAT_BOUNDS[-1][1]

CAPTION_MAX_LINES = 2
CAPTION_MAX_WIDTH_PX = 940  # safe render width inside 1080px frame + box padding
CAPTION_START_SIZE = 64
CAPTION_MIN_SIZE = 38

PILOT_ASSETS = {
    "tt_anxiety_faceless": [
        "anxiety/pexels__anxiety__8101094.jpeg",
        "anxiety/pexels__anxiety__13228799.jpeg",
        "anxiety/pexels__anxiety__18362514.jpeg",
        "anxiety/pexels__anxiety__8733211.jpeg",
        "anxiety/pexels__anxiety__18547794.jpeg",
    ],
    "tt_burnout_faceless": [
        "burnout/pexels__burnout__6173662.jpeg",
        "burnout/pexels__burnout__6475563.jpeg",
        "burnout/pexels__burnout__8788374.jpeg",
        "burnout/pexels__burnout__8085943.jpeg",
        "hope/pexels__hope__36541765.jpeg",
    ],
    "yt_overthinking_faceless": [
        "overthinking/pexels__overthinking__10290189.jpeg",
        "overthinking/pexels__overthinking__10432207.jpeg",
        "overthinking/pexels__overthinking__707676.jpeg",
        "overthinking/pexels__overthinking__8004028.jpeg",
        "overthinking/pexels__overthinking__16261090.jpeg",
    ],
}

PILOT_TOPIC = {
    "tt_anxiety_faceless": "anxiety",
    "tt_burnout_faceless": "burnout",
    "yt_overthinking_faceless": "overthinking",
}


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL, **kwargs
    )
    if proc.returncode != 0:
        sys.stderr.write(f"CMD FAILED: {' '.join(cmd)}\n")
        sys.stderr.write(proc.stdout[-4000:] + "\n")
        sys.stderr.write(proc.stderr[-4000:] + "\n")
        raise SystemExit(proc.returncode)
    return proc


def load_storyboard_captions() -> dict[str, list[str]]:
    data = json.loads(STORYBOARD_JSON.read_text())
    out: dict[str, list[str]] = {}
    for entry in data:
        example_id = entry["example_id"]
        beats = entry["beats"]
        role_to_caption = {b["role"]: b["caption"] for b in beats}
        ordered = [role_to_caption[r] for r in BEAT_ROLES]
        out[example_id] = ordered
    return out


def fit_caption(caption: str) -> tuple[int, str]:
    """Pick the largest fontsize/line-wrap combo (Georgia Bold, this font
    file) whose rendered line width stays under CAPTION_MAX_WIDTH_PX, at
    most CAPTION_MAX_LINES lines. Measured with the real font metrics
    (PIL) rather than a fixed chars-per-line guess, since a 42-char line
    at fontsize 64 can visually overflow a 1080px-wide frame."""
    for size in range(CAPTION_START_SIZE, CAPTION_MIN_SIZE - 1, -2):
        font = ImageFont.truetype(FONT_CAPTION, size)
        for width_chars in range(46, 10, -1):
            lines = textwrap.wrap(caption, width=width_chars)
            if not lines or len(lines) > CAPTION_MAX_LINES:
                continue
            if all(font.getlength(l) <= CAPTION_MAX_WIDTH_PX for l in lines):
                return size, "\n".join(lines)
    font = ImageFont.truetype(FONT_CAPTION, CAPTION_MIN_SIZE)
    lines = textwrap.wrap(caption, width=14)[:CAPTION_MAX_LINES]
    return CAPTION_MIN_SIZE, "\n".join(lines)


def build_zoompan_expr(motion: str, beat_index: int, duration_s: float, frames: int):
    """Return (zoom_expr, x_expr, y_expr) for the zoompan filter, honoring
    motion_policy.yaml intent: slow, one movement per shot, no restart."""
    if motion == "push":
        # ~1.2%/s push-in, capped so it stays subtle even on longer beats.
        zoom_target = min(1.0 + 0.012 * duration_s, 1.10)
        rate = (zoom_target - 1.0) / max(frames, 1)
        zoom_expr = f"min(zoom+{rate:.8f},{zoom_target:.6f})"
        x_expr = "(iw-iw/zoom)/2"
        y_expr = "(ih-ih/zoom)/2"
    elif motion == "pan":
        pan_zoom = 1.18
        zoom_expr = f"{pan_zoom:.4f}"
        last = max(frames - 1, 1)
        if beat_index % 2 == 0:
            x_expr = f"(iw-iw/zoom)*on/{last}"
        else:
            x_expr = f"(iw-iw/zoom)*(1-on/{last})"
        y_expr = "(ih-ih/zoom)/2"
    else:  # static
        zoom_expr = "1.0"
        x_expr = "(iw-iw/zoom)/2"
        y_expr = "(ih-ih/zoom)/2"
    return zoom_expr, x_expr, y_expr


def render_beat_clip(image_path: Path, beat_index: int, duration_s: float, motion: str, out_path: Path):
    frames = round(duration_s * FPS)
    # zoompan at 1080x1920 OOMs/kills parallel media-bank workers under load.
    # Fast path: encode ONE still frame, then stream-loop to duration (copy) —
    # survives load averages >100 where per-frame encode stalls at ~0.05x.
    fast = _os.environ.get("MEDIA_BANK_FAST_MOTION", "").strip().lower() in {"1", "true", "yes", "2"}
    if fast:
        # Still plate held for beat duration (no Ken Burns). Encode once at
        # ultrafast — avoid stream_loop+copy which balloons to 50–200MB/beat.
        vf = (
            f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},format=yuv420p,fps={FPS}"
        )
        run(
            [
                FFMPEG, "-y",
                "-loop", "1",
                "-i", str(image_path),
                "-vf", vf,
                "-t", str(duration_s),
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-tune", "stillimage",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-an",
                str(out_path),
            ]
        )
        return
    zoom_expr, x_expr, y_expr = build_zoompan_expr(motion, beat_index, duration_s, frames)
    vf = (
        f"scale={CANVAS_W}:{CANVAS_H}:force_original_aspect_ratio=increase,"
        f"crop={CANVAS_W}:{CANVAS_H},"
        f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d={frames}:s={W}x{H}:fps={FPS}"
    )
    cmd = [
        FFMPEG, "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-vf", vf,
        "-frames:v", str(frames),
        "-r", str(FPS),
        "-pix_fmt", "yuv420p",
        "-an",
        "-c:v", "libx264",
        "-preset", _mb_ffmpeg_preset(),
        "-crf", "16",
        str(out_path),
    ]
    run(cmd)


def concat_clips(clip_paths: list[Path], out_path: Path):
    list_file = out_path.with_suffix(".txt")
    # Absolute paths: concat demuxer resolves relatives against the list file dir.
    list_file.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in clip_paths) + "\n",
        encoding="utf-8",
    )
    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(out_path),
    ]
    run(cmd)


def burn_captions(silent_video: Path, captions: list[str], caption_dir: Path, out_path: Path):
    caption_dir.mkdir(parents=True, exist_ok=True)
    drawtext_filters = []
    for i, caption in enumerate(captions):
        fontsize, wrapped = fit_caption(caption)
        txt_path = caption_dir / f"caption_{i}.txt"
        txt_path.write_text(wrapped)
        t0, t1 = BEAT_BOUNDS[i]
        drawtext_filters.append(
            "drawtext="
            f"fontfile='{FONT_CAPTION}':"
            f"textfile='{txt_path}':"
            f"fontsize={fontsize}:"
            "fontcolor=white:"
            "line_spacing=12:"
            "box=1:boxcolor=black@0.55:boxborderw=30:"
            "x=(w-text_w)/2:"
            "y=h*0.67:"
            f"enable='between(t,{t0},{t1})'"
        )
    vf = ",".join(drawtext_filters)
    cmd = [
        FFMPEG, "-y",
        "-i", str(silent_video),
        "-vf", vf,
        "-pix_fmt", "yuv420p",
        "-an",
        "-c:v", "libx264",
        "-preset", _mb_ffmpeg_preset(),
        "-crf", "16",
        str(out_path),
    ]
    run(cmd)


def build_cut_sfx(out_path: Path):
    """Short whoosh+hit transient (~0.4s) reused at every hard cut."""
    thump = out_path.parent / "sfx_thump.wav"
    whoosh = out_path.parent / "sfx_whoosh.wav"
    run([
        FFMPEG, "-y",
        "-f", "lavfi", "-i", "sine=frequency=95:duration=0.30",
        "-af", "afade=t=out:st=0.03:d=0.27,volume=0.55",
        str(thump),
    ])
    run([
        FFMPEG, "-y",
        "-f", "lavfi", "-i", "anoisesrc=color=white:amplitude=0.7:duration=0.40",
        "-af",
        "bandpass=f=2800:width_type=h:w=3600,"
        "afade=t=in:st=0:d=0.03,afade=t=out:st=0.12:d=0.28,volume=0.30",
        str(whoosh),
    ])
    run([
        FFMPEG, "-y",
        "-i", str(thump), "-i", str(whoosh),
        "-filter_complex", "[0][1]amix=inputs=2:duration=longest,alimiter=limit=0.9",
        str(out_path),
    ])


def build_bed(out_path: Path, duration_s: float):
    """Soft ambient pad, low volume, faded in/out. Not music, not a hook."""
    freqs = [110, 164.81, 220]
    inputs = []
    for f in freqs:
        inputs += ["-f", "lavfi", "-i", f"sine=frequency={f}:duration={duration_s}"]
    fade_out_start = max(duration_s - 2.0, 0.0)
    filt = (
        "[0][1][2]amix=inputs=3:weights=1 1 1,"
        "lowpass=f=1200,"
        f"volume=0.07,afade=t=in:st=0:d=1.5,afade=t=out:st={fade_out_start:.2f}:d=2"
    )
    cmd = [FFMPEG, "-y", *inputs, "-filter_complex", filt, str(out_path)]
    run(cmd)


def build_audio_track(bed: Path, sfx: Path, out_path: Path, duration_s: float):
    cut_times_ms = [int(t0 * 1000) for t0, _ in BEAT_BOUNDS]
    delayed_labels = []
    filt_parts = []
    for i, ms in enumerate(cut_times_ms):
        label = f"s{i}"
        filt_parts.append(f"[1]adelay={ms}|{ms}[{label}]")
        delayed_labels.append(f"[{label}]")
    mix_inputs = "[0]" + "".join(delayed_labels)
    n = 1 + len(delayed_labels)
    filt_parts.append(f"{mix_inputs}amix=inputs={n}:normalize=0,alimiter=limit=0.9[mixout]")
    filt = ";".join(filt_parts)
    cmd = [
        FFMPEG, "-y",
        "-i", str(bed),
        "-i", str(sfx),
        "-filter_complex", filt,
        "-map", "[mixout]",
        "-t", f"{duration_s}",
        "-c:a", "aac", "-b:a", "160k",
        str(out_path),
    ]
    run(cmd)


def mux_final(video: Path, audio: Path, out_path: Path):
    cmd = [
        FFMPEG, "-y",
        "-i", str(video),
        "-i", str(audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "160k",
        "-t", f"{TOTAL_DURATION_S}",
        "-movflags", "+faststart",
        str(out_path),
    ]
    run(cmd)


def ffprobe_json(path: Path) -> dict:
    cmd = [
        FFPROBE, "-v", "error",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(path),
    ]
    proc = run(cmd)
    return json.loads(proc.stdout)


def validate_video(path: Path) -> dict:
    info = ffprobe_json(path)
    v_streams = [s for s in info["streams"] if s["codec_type"] == "video"]
    a_streams = [s for s in info["streams"] if s["codec_type"] == "audio"]
    fmt = info["format"]
    duration_s = float(fmt.get("duration", 0.0))
    checks = {}
    checks["has_video_stream"] = len(v_streams) == 1
    checks["has_audio_stream"] = len(a_streams) == 1
    if v_streams:
        v = v_streams[0]
        checks["resolution_1080x1920"] = (int(v["width"]), int(v["height"])) == (W, H)
        checks["video_codec_h264"] = v["codec_name"] == "h264"
    else:
        checks["resolution_1080x1920"] = False
        checks["video_codec_h264"] = False
    if a_streams:
        checks["audio_codec_aac"] = a_streams[0]["codec_name"] == "aac"
    else:
        checks["audio_codec_aac"] = False
    checks["duration_25s_to_27s"] = 25.0 <= duration_s <= 27.5
    checks["file_size_nonzero"] = path.stat().st_size > 50_000
    overall = "PASS" if all(checks.values()) else "FAIL"
    return {
        "path": str(path.relative_to(ROOT)),
        "duration_s": round(duration_s, 3),
        "width": int(v_streams[0]["width"]) if v_streams else None,
        "height": int(v_streams[0]["height"]) if v_streams else None,
        "video_codec": v_streams[0]["codec_name"] if v_streams else None,
        "audio_codec": a_streams[0]["codec_name"] if a_streams else None,
        "file_size_bytes": path.stat().st_size,
        "checks": checks,
        "status": overall,
    }


def extract_qa_frames(video: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    sample_times = [0.4, 3.0, 9.0, 17.0, 24.5]
    for i, t in enumerate(sample_times):
        out_path = out_dir / f"frame_beat{i}_{t:.1f}s.jpg"
        run([
            FFMPEG, "-y",
            "-ss", f"{t}",
            "-i", str(video),
            "-frames:v", "1",
            "-update", "1",
            str(out_path),
        ])


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)

    captions_by_pilot = load_storyboard_captions()

    common = WORK / "_common_audio"
    common.mkdir(parents=True, exist_ok=True)
    sfx_path = common / "sfx_cut.wav"
    bed_path = common / "bed.wav"
    audio_path = common / "audio_full.aac"
    build_cut_sfx(sfx_path)
    build_bed(bed_path, TOTAL_DURATION_S)
    build_audio_track(bed_path, sfx_path, audio_path, TOTAL_DURATION_S)

    manifest = {
        "style": "broll_montage",
        "resolution": f"{W}x{H}",
        "fps": FPS,
        "duration_s": TOTAL_DURATION_S,
        "beat_bounds": BEAT_BOUNDS,
        "beat_roles": BEAT_ROLES,
        "beat_motions": BEAT_MOTIONS,
        "font_caption": FONT_CAPTION,
        "audio": {
            "bed": "synthesized_soft_pad_110_165_220hz_lowpass",
            "cut_sfx": "synthesized_thump95hz_plus_bandpass_whoosh",
            "cut_times_s": [t0 for t0, _ in BEAT_BOUNDS],
            "shared_across_pilots": True,
        },
        "pilots": {},
    }

    receipts = []

    for pilot, rel_paths in PILOT_ASSETS.items():
        print(f"=== {pilot} ===")
        pilot_work = WORK / pilot
        pilot_work.mkdir(parents=True, exist_ok=True)
        captions = captions_by_pilot[pilot]

        asset_records = []
        clip_paths = []
        for i, rel in enumerate(rel_paths):
            img_path = STOCK_BASE / rel
            if not img_path.exists():
                raise SystemExit(f"Missing stock asset: {img_path}")
            t0, t1 = BEAT_BOUNDS[i]
            motion = BEAT_MOTIONS[i]
            clip_path = pilot_work / f"beat{i}_{BEAT_ROLES[i]}.mp4"
            render_beat_clip(img_path, i, t1 - t0, motion, clip_path)
            clip_paths.append(clip_path)
            asset_records.append({
                "beat_index": i,
                "role": BEAT_ROLES[i],
                "duration": f"{t0}-{t1}",
                "motion": motion,
                "caption": captions[i],
                "source_relpath": f"artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x/downloads/pexels/{rel}",
            })

        silent = pilot_work / "montage_silent.mp4"
        concat_clips(clip_paths, silent)

        captioned = pilot_work / "montage_captioned.mp4"
        burn_captions(silent, captions, pilot_work / "captions", captioned)

        final_path = FINAL / f"{pilot}.mp4"
        mux_final(captioned, audio_path, final_path)

        extract_qa_frames(final_path, pilot_work / "qa_frames")

        receipt = validate_video(final_path)
        receipt["pilot"] = pilot
        receipt["topic"] = PILOT_TOPIC[pilot]
        receipts.append(receipt)

        manifest["pilots"][pilot] = {
            "topic": PILOT_TOPIC[pilot],
            "final_mp4": str(final_path.relative_to(ROOT)),
            "beats": asset_records,
        }
        print(f"  -> {final_path} [{receipt['status']}]")

    (OUT_ROOT / "assets_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    with (OUT_ROOT / "validation_receipts.jsonl").open("w") as f:
        for r in receipts:
            f.write(json.dumps(r) + "\n")

    fail = [r for r in receipts if r["status"] != "PASS"]
    print("\n=== SUMMARY ===")
    for r in receipts:
        print(f"{r['pilot']}: {r['status']} duration={r['duration_s']}s size={r['file_size_bytes']}")
    if fail:
        print(f"{len(fail)} video(s) FAILED validation.")
        sys.exit(1)
    print("All videos PASS validation.")


if __name__ == "__main__":
    main()
