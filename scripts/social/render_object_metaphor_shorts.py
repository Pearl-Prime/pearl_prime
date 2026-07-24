#!/usr/bin/env python3
"""STYLE C — Object-metaphor story, done properly.

One master plate per pilot, FIVE deliberately different crop windows (wide ->
medium -> tight -> tighter -> hold-pulled-back), one per beat. Each beat is
rendered as its own clip (static crop window + a small in-beat push) and the
five clips are hard-cut concatenated, so every beat reads as a genuine
composition change instead of a single continuous Ken Burns drift.

Beat grammar (fixed 27s, matches shortform_publishable_storyboards.json):
  1. hook        0.0-1.5   WIDE establishing
  2. recognition 1.5-6.0   MEDIUM, clearer subject
  3. mechanism   6.0-13.0  DETAIL / tight crop + on-screen TYPE BUILD
  4. practice    13.0-22.0 ACTION framing (tighter crop, imperative caption)
  5. payoff      22.0-27.0 HOLD, pulled back for save/share readability

Audio: soft ambient bed (continuous) + synthesized SFX cues (soft hit on the
hook, three quiet ticks on the type build, one practical cue on practice,
a warm resolve tone on payoff). All audio is ffmpeg lavfi-generated — no
external SFX library dependency.

Authority: PEARL_ANIMATOR faceless_object_metaphor_story_30s + RQ5/RQ8.
Write scope: artifacts/qa/social_finish_20260718/lane03_research_complete/
variants/object_metaphor/ ONLY. Does not touch kinetic_type/ or
broll_montage/. Does not live-publish.
"""
from __future__ import annotations

import os as _os
def _mb_ffmpeg_preset() -> str:
    return _os.environ.get("MEDIA_BANK_FFMPEG_PRESET", "medium")

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
STORYBOARDS = (
    REPO
    / "artifacts/qa/social_visual_rebuild_publishable_quality_20260718"
    / "lane05_pearl_animator_rebuild/shortform_publishable_storyboards.json"
)
OUT_ROOT = (
    REPO
    / "artifacts/qa/social_finish_20260718/lane03_research_complete"
    / "variants/object_metaphor"
)
WIDTH, HEIGHT, FPS = 1080, 1920, 30
TOTAL_DURATION_S = 27.0

MASTER_PLATES = {
    "tt_anxiety_faceless": REPO
    / "artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x"
    / "downloads/pexels/anxiety/pexels__anxiety__8101094.jpeg",
    "tt_burnout_faceless": REPO
    / "artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x"
    / "downloads/pexels/hope/pexels__hope__36541765.jpeg",
    "yt_overthinking_faceless": REPO
    / "artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x"
    / "downloads/pexels/overthinking/pexels__overthinking__10290189.jpeg",
}

# role -> (duration_s, height_frac of source used for the crop window, in-beat
# micro-push zoom target). height_frac is the fraction of the source image's
# height captured by this beat's crop box (before the 9:16 crop is applied) —
# this is the "big reveal" lever: 1.00 -> 0.72 -> 0.42 -> 0.27 -> 0.55.
BEAT_GRAMMAR = [
    {"role": "hook", "duration_s": 1.5, "height_frac": 1.00, "zoom_to": 1.03},
    {"role": "recognition", "duration_s": 4.5, "height_frac": 0.72, "zoom_to": 1.05},
    {"role": "mechanism", "duration_s": 7.0, "height_frac": 0.42, "zoom_to": 1.06},
    {"role": "practice", "duration_s": 9.0, "height_frac": 0.27, "zoom_to": 1.08},
    {"role": "payoff", "duration_s": 5.0, "height_frac": 0.55, "zoom_to": 1.02},
]
assert abs(sum(b["duration_s"] for b in BEAT_GRAMMAR) - TOTAL_DURATION_S) < 1e-6

# Per-pilot subject centers (fraction of source W/H) for each beat, chosen by
# eye from the actual plates so each crop is a meaningful, motivated framing
# change on the SAME object/world (not a random re-center).
SUBJECT_CENTERS: dict[str, dict[str, tuple[float, float]]] = {
    # cord tangle on concrete floor — knot sits upper-middle of frame
    "tt_anxiety_faceless": {
        "hook": (0.50, 0.40),
        "recognition": (0.54, 0.33),
        "mechanism": (0.565, 0.27),
        "practice": (0.40, 0.375),
        "payoff": (0.50, 0.32),
    },
    # seedling emerging from moss, dark bokeh background
    "tt_burnout_faceless": {
        "hook": (0.45, 0.53),
        "recognition": (0.44, 0.46),
        "mechanism": (0.40, 0.335),
        "practice": (0.42, 0.62),
        "payoff": (0.44, 0.47),
    },
    # overhead hedge maze, symmetric, two small bench chambers
    "yt_overthinking_faceless": {
        "hook": (0.50, 0.50),
        "recognition": (0.45, 0.42),
        "mechanism": (0.404, 0.377),
        "practice": (0.452, 0.531),
        "payoff": (0.47, 0.46),
    },
}

# SFX cue timeline (absolute seconds in the 27s master timeline). Kept fixed
# across all 3 pilots because the beat grammar/durations are identical.
MECH_START, MECH_DUR = 6.0, 7.0
TICK_TIMES = [MECH_START + MECH_DUR * f for f in (0.0, 1 / 3, 2 / 3)]
SFX_CUES = {
    "hook_hit_s": 0.0,
    "mechanism_ticks_s": TICK_TIMES,
    "practice_cue_s": 13.0,
    "payoff_resolve_s": 22.0,
}


def _ffmpeg() -> str:
    for c in (Path("/opt/homebrew/bin/ffmpeg"), Path("/usr/local/bin/ffmpeg")):
        if c.is_file():
            return str(c)
    return "ffmpeg"


def _ffprobe() -> str:
    for c in (Path("/opt/homebrew/bin/ffprobe"), Path("/usr/local/bin/ffprobe")):
        if c.is_file():
            return str(c)
    return "ffprobe"


def _font() -> str:
    georgia = Path("/System/Library/Fonts/Supplemental/Georgia.ttf")
    if georgia.is_file():
        return str(georgia)
    return "/System/Library/Fonts/Helvetica.ttc"


def _font_bold() -> str:
    bold = Path("/System/Library/Fonts/Supplemental/Georgia Bold.ttf")
    if bold.is_file():
        return str(bold)
    return _font()


def _escape_drawtext(text: str) -> str:
    text = text.replace("\\", "\\\\").replace("'", "\u2019").replace(":", "\\:")
    return text.replace("%", "%%")


def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "ffmpeg command failed:\n"
            + " ".join(cmd)
            + "\n---stderr(tail)---\n"
            + proc.stderr[-3000:]
        )


def image_dims(path: Path) -> tuple[int, int]:
    proc = subprocess.run(
        [
            _ffprobe(),
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    w, h = proc.stdout.strip().split(",")
    return int(w), int(h)


def compute_crop_window(
    src_w: int, src_h: int, cx_frac: float, cy_frac: float, height_frac: float
) -> dict[str, int]:
    """9:16-shaped crop box of the requested vertical extent, centered on the
    subject and clamped inside the source image."""
    ch = height_frac * src_h
    cw = ch * WIDTH / HEIGHT
    if cw > src_w:
        cw = float(src_w)
        ch = cw * HEIGHT / WIDTH
    cw = max(16.0, min(cw, src_w))
    ch = max(16.0, min(ch, src_h))
    x = cx_frac * src_w - cw / 2
    y = cy_frac * src_h - ch / 2
    x = max(0.0, min(x, src_w - cw))
    y = max(0.0, min(y, src_h - ch))
    return {"x": int(round(x)), "y": int(round(y)), "w": int(round(cw)), "h": int(round(ch))}


def split_words_into_groups(text: str, n_groups: int = 3) -> list[str]:
    words = text.strip().split()
    if len(words) <= n_groups:
        return words
    per = max(1, round(len(words) / n_groups))
    groups, i = [], 0
    while i < len(words):
        groups.append(" ".join(words[i : i + per]))
        i += per
    while len(groups) > n_groups:
        groups[-2] = groups[-2] + " " + groups[-1]
        groups.pop()
    return groups


def build_type_build_stages(caption: str, beat_dur: float) -> list[dict[str, Any]]:
    groups = split_words_into_groups(caption, 3)
    n = len(groups)
    stages = []
    cumulative = ""
    for i, g in enumerate(groups):
        cumulative = (cumulative + " " + g).strip() if cumulative else g
        t0 = beat_dur * i / n
        t1 = beat_dur if i == n - 1 else beat_dur * (i + 1) / n
        stages.append({"text": cumulative, "start_s": round(t0, 3), "end_s": round(t1, 3)})
    return stages


def caption_band_and_text_vf(
    caption_stages: list[dict[str, Any]], role: str
) -> str:
    font = _font()
    parts = ["drawbox=x=0:y=1470:w=1080:h=420:color=black@0.38:t=fill"]
    for stage in caption_stages:
        text = _escape_drawtext(stage["text"])
        size = 58 if role != "mechanism" else 54
        parts.append(
            "drawtext="
            f"fontfile={font}:text='{text}':fontsize={size}:fontcolor=white:"
            "x=(w-text_w)/2:y=1580:shadowcolor=black@0.7:shadowx=2:shadowy=2:"
            f"enable='between(t\\,{stage['start_s']}\\,{max(stage['start_s'], stage['end_s'] - 0.001)})'"
        )
    if role == "practice":
        parts.append(
            "drawtext="
            f"fontfile={_font_bold()}:text='TRY IT':fontsize=34:fontcolor=#ffd54a:"
            "x=(w-text_w)/2:y=1500:shadowcolor=black@0.7:shadowx=1:shadowy=1"
        )
    elif role == "mechanism":
        parts.append(
            "drawtext="
            f"fontfile={_font_bold()}:text='THE MECHANISM':fontsize=30:fontcolor=#9ad1ff:"
            "x=(w-text_w)/2:y=1500:shadowcolor=black@0.7:shadowx=1:shadowy=1"
        )
    return ",".join(parts)


def render_beat_clip(
    plate: Path,
    crop: dict[str, int],
    zoom_to: float,
    duration_s: float,
    caption_stages: list[dict[str, Any]],
    role: str,
    out_path: Path,
) -> None:
    frames = max(1, int(round(duration_s * FPS)))
    zstep = (zoom_to - 1.0) / frames
    fast = _os.environ.get("MEDIA_BANK_FAST_MOTION", "").strip().lower() in {"1", "true", "yes", "2"}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if fast:
        # One still frame + stream-loop (load-average safe; avoids 150-frame encode stalls).
        vf = (
            f"crop={crop['w']}:{crop['h']}:{crop['x']}:{crop['y']},"
            f"scale={WIDTH}:{HEIGHT}:flags=lanczos,format=yuv420p,"
            + caption_band_and_text_vf(caption_stages, role)
        )
        (out_path.parent / f"{out_path.stem}.vf.txt").write_text(vf, encoding="utf-8")
        one = out_path.with_suffix(".1frame.mp4")
        _run(
            [
                _ffmpeg(),
                "-y",
                "-i",
                str(plate),
                "-vf",
                vf,
                "-frames:v",
                "1",
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-tune",
                "stillimage",
                "-crf",
                "18",
                "-an",
                str(one),
            ]
        )
        # Copy-loop stays fast under extreme host load; compact later if needed.
        _run(
            [
                _ffmpeg(),
                "-y",
                "-stream_loop",
                "-1",
                "-i",
                str(one),
                "-t",
                str(duration_s),
                "-c:v",
                "copy",
                "-an",
                str(out_path),
            ]
        )
        one.unlink(missing_ok=True)
        return
    vf = (
        f"crop={crop['w']}:{crop['h']}:{crop['x']}:{crop['y']},"
        f"zoompan=z='min(1+{zstep:.9f}*on,{zoom_to})':"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={WIDTH}x{HEIGHT}:fps={FPS},"
        "format=yuv420p,"
        + caption_band_and_text_vf(caption_stages, role)
    )
    (out_path.parent / f"{out_path.stem}.vf.txt").write_text(vf, encoding="utf-8")
    _run(
        [
            _ffmpeg(),
            "-y",
            "-loop",
            "1",
            "-i",
            str(plate),
            "-vf",
            vf,
            "-t",
            str(duration_s),
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-preset",
            _mb_ffmpeg_preset(),
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            str(out_path),
        ]
    )


def concat_beats(beat_clips: list[Path], out_path: Path) -> None:
    n = len(beat_clips)
    inputs: list[str] = []
    for c in beat_clips:
        inputs += ["-i", str(c)]
    chain = "".join(f"[{i}:v]" for i in range(n)) + f"concat=n={n}:v=1:a=0[outv]"
    _run(
        [
            _ffmpeg(),
            "-y",
            *inputs,
            "-filter_complex",
            chain,
            "-map",
            "[outv]",
            "-c:v",
            "libx264",
            "-preset",
            _mb_ffmpeg_preset(),
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(FPS),
            str(out_path),
        ]
    )


def build_sfx_track(out_path: Path, duration_s: float = TOTAL_DURATION_S) -> None:
    """Synthesize soft bed + hook hit + type-build ticks + practice cue +
    payoff resolve tone, all via ffmpeg lavfi generators. No external SFX
    assets required."""
    tick_times = SFX_CUES["mechanism_ticks_s"]
    inputs: list[str] = []
    _counter = {"n": 0}

    def lavfi(spec: str) -> int:
        inputs.extend(["-f", "lavfi", "-i", spec])
        idx = _counter["n"]
        _counter["n"] += 1
        return idx

    i_noise = lavfi(f"anoisesrc=color=brown:amplitude=0.015:duration={duration_s}")
    i_pad = lavfi(f"sine=frequency=220:duration={duration_s}:sample_rate=44100")
    i_hit = lavfi("sine=frequency=95:duration=0.35:sample_rate=44100")
    i_t0 = lavfi("sine=frequency=1500:duration=0.09:sample_rate=44100")
    i_t1 = lavfi("sine=frequency=1500:duration=0.09:sample_rate=44100")
    i_t2 = lavfi("sine=frequency=1500:duration=0.09:sample_rate=44100")
    i_practice = lavfi("sine=frequency=420:duration=0.28:sample_rate=44100")
    i_resolve_a = lavfi("sine=frequency=440:duration=2.2:sample_rate=44100")
    i_resolve_b = lavfi("sine=frequency=330:duration=2.2:sample_rate=44100")

    filt = []
    filt.append(f"[{i_noise}:a]lowpass=f=800,volume=0.32[bed_n]")
    filt.append(
        f"[{i_pad}:a]volume=0.028,afade=t=in:st=0:d=1.5,"
        f"afade=t=out:st={duration_s-3}:d=3[bed_s]"
    )
    filt.append(
        f"[{i_hit}:a]volume=0.55,afade=t=out:st=0:d=0.35,"
        f"adelay={int(SFX_CUES['hook_hit_s']*1000)}[hit]"
    )
    for idx, (src, t) in enumerate(zip((i_t0, i_t1, i_t2), tick_times)):
        filt.append(
            f"[{src}:a]volume=0.30,afade=t=out:st=0:d=0.09,"
            f"adelay={int(t*1000)}[tick{idx}]"
        )
    filt.append(
        f"[{i_practice}:a]volume=0.42,afade=t=out:st=0:d=0.28,"
        f"adelay={int(SFX_CUES['practice_cue_s']*1000)}[prac]"
    )
    filt.append(
        f"[{i_resolve_a}:a]volume=0.20,afade=t=in:st=0:d=0.3,afade=t=out:st=1.4:d=0.8,"
        f"adelay={int(SFX_CUES['payoff_resolve_s']*1000)}[res_a]"
    )
    filt.append(
        f"[{i_resolve_b}:a]volume=0.14,afade=t=in:st=0:d=0.3,afade=t=out:st=1.4:d=0.8,"
        f"adelay={int(SFX_CUES['payoff_resolve_s']*1000)}[res_b]"
    )
    mix_inputs = "[bed_n][bed_s][hit][tick0][tick1][tick2][prac][res_a][res_b]"
    filt.append(
        f"{mix_inputs}amix=inputs=9:duration=first:dropout_transition=0,"
        f"afade=t=in:st=0:d=0.6,afade=t=out:st={duration_s-2.5}:d=2.5[mixed]"
    )
    filt.append(f"[mixed]atrim=0:{duration_s},apad=whole_dur={duration_s}[outa]")

    _run(
        [
            _ffmpeg(),
            "-y",
            *inputs,
            "-filter_complex",
            ";".join(filt),
            "-map",
            "[outa]",
            "-ac",
            "2",
            "-ar",
            "44100",
            str(out_path),
        ]
    )


def mux(video: Path, audio: Path, out_path: Path, duration_s: float) -> None:
    _run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(video),
            "-i",
            str(audio),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-preset",
            _mb_ffmpeg_preset(),
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-t",
            str(duration_s),
            "-movflags",
            "+faststart",
            str(out_path),
        ]
    )


def validate_mp4(path: Path) -> dict[str, Any]:
    probe = subprocess.run(
        [
            _ffprobe(),
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type,codec_name,width,height,duration",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(probe.stdout)
    streams = data.get("streams") or []
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    decode = subprocess.run(
        [_ffmpeg(), "-v", "error", "-i", str(path), "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    dur = float(video.get("duration") or audio.get("duration") if audio else 0) or float(
        video.get("duration") or 0
    )
    return {
        "path": str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path),
        "width": video.get("width"),
        "height": video.get("height"),
        "duration_s": round(dur, 2),
        "has_audio": audio is not None,
        "audio_codec": (audio or {}).get("codec_name"),
        "full_decode_ok": decode.returncode == 0 and not decode.stderr.strip(),
        "duration_gate": 26.0 <= dur <= 28.5,
        "platform_contract": video.get("width") == WIDTH and video.get("height") == HEIGHT,
    }


def build_crop_plan_entry(example_id: str, item: dict) -> dict[str, Any]:
    plate = MASTER_PLATES[example_id]
    src_w, src_h = image_dims(plate)
    captions = {b["role"]: b["caption"].strip() for b in item["beats"]}
    beats_out = []
    for spec in BEAT_GRAMMAR:
        role = spec["role"]
        cx, cy = SUBJECT_CENTERS[example_id][role]
        crop = compute_crop_window(src_w, src_h, cx, cy, spec["height_frac"])
        beat_entry = {
            "role": role,
            "duration_s": spec["duration_s"],
            "height_frac_of_source": spec["height_frac"],
            "subject_center_frac": {"x": cx, "y": cy},
            "crop_px": crop,
            "crop_area_px2": crop["w"] * crop["h"],
            "micro_push_zoom_to": spec["zoom_to"],
            "caption": captions.get(role, ""),
        }
        if role == "mechanism":
            beat_entry["type_build_stages"] = build_type_build_stages(
                captions.get(role, ""), spec["duration_s"]
            )
        beats_out.append(beat_entry)
    areas = [b["crop_area_px2"] for b in beats_out]
    return {
        "example_id": example_id,
        "source_plate": str(plate.relative_to(REPO)),
        "source_dims_px": {"w": src_w, "h": src_h},
        "beats": beats_out,
        "framing_diversity_check": {
            "hook_to_mechanism_area_ratio": round(areas[0] / areas[2], 2),
            "hook_to_practice_area_ratio": round(areas[0] / areas[3], 2),
            "payoff_is_pulled_back_vs_practice": areas[4] > areas[3],
            "payoff_is_not_full_wide": areas[4] < areas[0],
            "monotonic_shrink_hook_through_practice": areas[0] > areas[1] > areas[2] > areas[3],
        },
        "sfx_cues_s": SFX_CUES,
    }


def render_one(example_id: str, item: dict, out_root: Path, crop_entry: dict) -> Path:
    work = out_root / "_work" / example_id
    work.mkdir(parents=True, exist_ok=True)
    plate = MASTER_PLATES[example_id]

    beat_clips = []
    for spec, beat in zip(BEAT_GRAMMAR, crop_entry["beats"]):
        role = spec["role"]
        if role == "mechanism":
            stages = [
                {"text": s["text"], "start_s": s["start_s"], "end_s": s["end_s"]}
                for s in beat["type_build_stages"]
            ]
        else:
            stages = [{"text": beat["caption"], "start_s": 0.0, "end_s": spec["duration_s"]}]
        clip_path = work / f"beat_{role}.mp4"
        render_beat_clip(
            plate,
            beat["crop_px"],
            spec["zoom_to"],
            spec["duration_s"],
            stages,
            role,
            clip_path,
        )
        beat_clips.append(clip_path)

    silent = work / "silent_full.mp4"
    concat_beats(beat_clips, silent)

    sfx = work / "sfx_track.wav"
    build_sfx_track(sfx, TOTAL_DURATION_S)

    final_dir = out_root / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    final = final_dir / f"{example_id}.mp4"
    mux(silent, sfx, final, TOTAL_DURATION_S)
    return final


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma-separated example_ids; default=all")
    ap.add_argument("--out", type=Path, default=OUT_ROOT)
    args = ap.parse_args()

    items = json.loads(STORYBOARDS.read_text(encoding="utf-8"))
    items_by_id = {i["example_id"]: i for i in items}
    only = {x.strip() for x in args.only.split(",") if x.strip()}
    example_ids = [e for e in MASTER_PLATES if (not only or e in only)]

    crop_plan = {"style": "object_metaphor", "generated_by": "scripts/social/render_object_metaphor_shorts.py"}
    entries = []
    for example_id in example_ids:
        entries.append(build_crop_plan_entry(example_id, items_by_id[example_id]))
    crop_plan["pilots"] = entries
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "crop_plan.json").write_text(json.dumps(crop_plan, indent=2), encoding="utf-8")

    receipts = []
    for entry in entries:
        example_id = entry["example_id"]
        item = items_by_id[example_id]
        print(f"== {example_id} ==")
        final = render_one(example_id, item, args.out, entry)
        receipt = validate_mp4(final)
        receipt["example_id"] = example_id
        receipt["topic"] = item.get("topic")
        receipt["style"] = "object_metaphor"
        receipt["viewer_captions_only"] = True
        receipt["director_notes_on_plate"] = False
        receipt["beat_count"] = len(BEAT_GRAMMAR)
        receipt["render_mode"] = "object_metaphor_progressive_crops"
        receipt["framing_diversity_check"] = entry["framing_diversity_check"]
        receipts.append(receipt)
        print(json.dumps(receipt, indent=2))

    (args.out / "validation_receipts.jsonl").write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in receipts) + "\n",
        encoding="utf-8",
    )
    failed = [
        r
        for r in receipts
        if not (
            r["full_decode_ok"]
            and r["duration_gate"]
            and r["platform_contract"]
            and r["has_audio"]
            and r["framing_diversity_check"]["monotonic_shrink_hook_through_practice"]
            and r["framing_diversity_check"]["payoff_is_pulled_back_vs_practice"]
        )
    ]
    if failed:
        print(f"FAIL: {len(failed)} receipts failed gates", file=sys.stderr)
        return 1
    print(f"OK: {len(receipts)} object-metaphor MP4s -> {args.out / 'final'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
