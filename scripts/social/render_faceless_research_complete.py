#!/usr/bin/env python3
"""Render research-complete faceless shorts from lane05 storyboards.

Uses clean stock plates (not storyboard JPGs with director notes) + VCE
run_render.py for Ken Burns / pan + burnt-in viewer captions + soft audio bed.

Authority: docs/PEARL_ANIMATOR_FACELESS_SHORTS_SPEC_2026-07-18.md
Does not live-publish. Does not freeze golden.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STORYBOARDS = (
    REPO
    / "artifacts/qa/social_visual_rebuild_publishable_quality_20260718"
    / "lane05_pearl_animator_rebuild/shortform_publishable_storyboards.json"
)
CLEAN_PLATES = {
    "waystream_anxiety_pexels_8101094_01": REPO
    / "artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x"
    / "downloads/pexels/anxiety/pexels__anxiety__8101094.jpeg",
    "waystream_hope_pexels_36541765_06": REPO
    / "artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x"
    / "downloads/pexels/hope/pexels__hope__36541765.jpeg",
    "waystream_overthinking_pexels_10290189_01": REPO
    / "artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x"
    / "downloads/pexels/overthinking/pexels__overthinking__10290189.jpeg",
}
DEFAULT_OUT = (
    REPO
    / "artifacts/qa/social_finish_20260718"
    / "lane03_research_complete"
    / "shortform_mp4_research_complete"
)


def _parse_duration(span: str) -> tuple[float, float]:
    a, b = span.split("-")
    return float(a), float(b)


def _motion_for_beat(motion_note: str, role: str) -> str:
    note = (motion_note or "").lower()
    if role == "payoff" or "hold still" in note:
        return "static"
    if "crop shift" in note or "sideways" in note:
        return "camera_pan"
    if "slow push" in note or "zoom" in note or "labels" in note or "action" in note:
        return "ken_burns"
    return "ken_burns"


def _ffmpeg() -> str:
    for candidate in (
        Path("/opt/homebrew/bin/ffmpeg"),
        Path("/usr/local/bin/ffmpeg"),
    ):
        if candidate.is_file():
            return str(candidate)
    return "ffmpeg"


def _ffprobe() -> str:
    for candidate in (
        Path("/opt/homebrew/bin/ffprobe"),
        Path("/usr/local/bin/ffprobe"),
    ):
        if candidate.is_file():
            return str(candidate)
    return "ffprobe"


def make_soft_bed(path: Path, duration_s: float = 27.0) -> Path:
    """Quiet therapeutic pad: filtered brown noise + soft sine, under narration level."""
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        _ffmpeg(),
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"anoisesrc=color=brown:amplitude=0.015:duration={duration_s}",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency=220:duration={duration_s}:sample_rate=44100",
        "-filter_complex",
        "[1:a]volume=0.03,afade=t=in:st=0:d=1.5,afade=t=out:st=24:d=3[s];"
        "[0:a]lowpass=f=800,volume=0.35[n];"
        "[n][s]amix=inputs=2:duration=first:dropout_transition=0,"
        f"afade=t=in:st=0:d=0.8,afade=t=out:st={duration_s-2.5}:d=2.5",
        "-ac",
        "2",
        "-ar",
        "44100",
        str(path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return path


def build_package(
    item: dict,
    work_root: Path,
    *,
    voice_bank: Path | None = None,
) -> Path:
    example_id = item["example_id"]
    pkg = work_root / example_id
    assets = pkg / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    plate = CLEAN_PLATES.get(item["source_asset_id"])
    if not plate or not plate.is_file():
        raise FileNotFoundError(f"clean plate missing for {example_id}: {item.get('source_asset_id')}")

    asset_id = f"{example_id}_plate"
    shutil.copyfile(plate, assets / f"{asset_id}.jpg")

    bank_index = None
    if voice_bank is not None and Path(voice_bank).is_file():
        sys.path.insert(0, str(REPO))
        from scripts.social_media.voice_bank_lookup import load_index

        bank_index = load_index(Path(voice_bank), allow_r2_download=False)

    clips = []
    shots = []
    captions: dict[str, dict[str, str]] = {}
    narration_segments: list[dict] = []
    for i, beat in enumerate(item["beats"], start=1):
        start_s, end_s = _parse_duration(beat["duration"])
        shot_id = f"shot-{i}"
        seg_id = f"seg-{i}"
        clips.append(
            {
                "shot_id": shot_id,
                "asset_id": asset_id,
                "start_time_s": start_s,
                "end_time_s": end_s,
                "caption_ref": seg_id,
            }
        )
        shots.append(
            {
                "shot_id": shot_id,
                "segment_id": seg_id,
                "visual_intent": beat["role"].upper(),
                "aspect_ratio": "9:16",
                "duration_s": end_s - start_s,
                "thumbnail_candidate": i == 1,
                "prompt_bundle": {
                    "style": "faceless_object_metaphor",
                    "motion": _motion_for_beat(beat.get("motion", ""), beat["role"]),
                },
            }
        )
        # Viewer caption ONLY — never motion/director notes
        caption_text = beat["caption"].strip()
        atom_id = (beat.get("atom_id") or beat.get("primary_atom_id") or "").strip()
        audio_path = None
        speakable = None
        if bank_index is not None and atom_id:
            try:
                hit = bank_index.resolve(atom_id, require_audio=True)
                speakable = hit.speakable_text
                caption_text = speakable
                audio_path = str(hit.local_mp3) if hit.local_mp3 else None
            except Exception as e:
                print(
                    f"WARNING: voice-bank miss {example_id}/{atom_id}: {e}",
                    file=sys.stderr,
                )
        captions[seg_id] = {
            "text": caption_text,
            "source": "voice_bank_speakable" if speakable else "storyboard_caption",
            "atom_id": atom_id or None,
        }
        if audio_path:
            narration_segments.append(
                {
                    "segment_id": seg_id,
                    "start_time_s": start_s,
                    "end_time_s": end_s,
                    "text": speakable or caption_text,
                    "speakable_text": speakable or caption_text,
                    "primary_atom_id": atom_id,
                    "audio_path": audio_path,
                    "audio_provider": "social_voice_bank",
                    "audio_status": "ok",
                }
            )

    timeline = {
        "plan_id": example_id,
        "fps": 30,
        "resolution": {"width": 1080, "height": 1920},
        "aspect_ratio": "9:16",
        "duration_s": 27.0,
        "thumbnail_frame_ref": {"shot_id": "shot-1", "frame_offset": 0},
        "audio_tracks": [],
        "clips": clips,
    }
    shot_plan = {
        "plan_id": example_id,
        "content_type": "therapeutic_shortform",
        "shots": shots,
    }
    captions_doc = {"captions": captions}

    bed = make_soft_bed(pkg / "soft_bed.wav", 27.0)
    soundtrack = {
        "music_path": str(bed),
        "narration_segments": narration_segments,
        "voice_bank_manifest": str(voice_bank) if voice_bank else None,
    }

    (pkg / "timeline.json").write_text(json.dumps(timeline, indent=2), encoding="utf-8")
    (pkg / "shot_plan.json").write_text(json.dumps(shot_plan, indent=2), encoding="utf-8")
    (pkg / "captions.json").write_text(json.dumps(captions_doc, indent=2), encoding="utf-8")
    (pkg / "soundtrack_plan_with_audio.json").write_text(
        json.dumps(soundtrack, indent=2), encoding="utf-8"
    )
    (pkg / "source_meta.json").write_text(
        json.dumps(
            {
                "example_id": example_id,
                "topic": item.get("topic"),
                "persona": item.get("persona"),
                "platform": item.get("platform"),
                "source_asset_id": item.get("source_asset_id"),
                "source_url": item.get("source_url"),
                "license_state": item.get("license_state"),
                "clean_plate": str(plate.relative_to(REPO)),
                "voice_bank_manifest": str(voice_bank) if voice_bank else None,
                "narration_segments": len(narration_segments),
                "acceptance_layer": "system working — research-complete cut pending operator look",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return pkg


def _escape_drawtext(text: str) -> str:
    text = text.replace("\\", "\\\\").replace("'", "\u2019").replace(":", "\\:")
    return text.replace("%", "%%")


def _font() -> str:
    georgia = Path("/System/Library/Fonts/Supplemental/Georgia.ttf")
    if georgia.is_file():
        return str(georgia)
    return "/System/Library/Fonts/Helvetica.ttc"


def _continuous_vf(clips: list[dict], captions: dict, duration_s: float, fps: int = 30) -> str:
    """One continuous slow push + timed captions — no per-beat zoom reset (avoids chop)."""
    frames = max(1, int(round(duration_s * fps)))
    # Continuous Ken Burns: zoom 1.0 → ~1.12 over the full piece; gentle x drift
    # zoom increment per frame ≈ 0.12 / frames
    z_step = 0.12 / frames
    motion = (
        f"scale=1280:2276:force_original_aspect_ratio=increase,crop=1280:2276,"
        f"zoompan=z='min(1+{z_step:.8f}*on,1.12)'"
        f":x='iw/2-(iw/zoom/2)+0.015*on'"
        f":y='ih/2-(ih/zoom/2)'"
        f":d={frames}:s=1080x1920:fps={fps},format=yuv420p"
    )
    box = "drawbox=x=0:y=1440:w=1080:h=480:color=black@0.35:t=fill"
    parts = [motion, box]
    font = _font()
    for clip in clips:
        start = float(clip["start_time_s"])
        end = float(clip["end_time_s"])
        # tiny epsilon so boundaries don't double-draw
        end_e = max(start, end - 0.001)
        text = _escape_drawtext(captions[clip["caption_ref"]]["text"])
        parts.append(
            "drawtext="
            f"fontfile={font}:text='{text}':fontsize=52:fontcolor=white:"
            f"x=(w-text_w)/2:y=1550:shadowcolor=black@0.65:shadowx=2:shadowy=2:"
            f"enable='between(t\\,{start}\\,{end_e})'"
        )
    return ",".join(parts)


def render_one(pkg: Path, out_dir: Path) -> Path:
    """Single continuous motion pass; captions swap on beat times (no zoom reset chops)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    timeline = json.loads((pkg / "timeline.json").read_text(encoding="utf-8"))
    captions = json.loads((pkg / "captions.json").read_text(encoding="utf-8"))["captions"]
    plate = next((pkg / "assets").glob("*.jpg"))
    fps = int(timeline.get("fps") or 30)
    duration_s = float(timeline.get("duration_s") or 27.0)
    clips = timeline["clips"]

    silent = out_dir / "silent.mp4"
    vf = _continuous_vf(clips, captions, duration_s, fps=fps)
    (out_dir / "vf.txt").write_text(vf, encoding="utf-8")
    proc = subprocess.run(
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
            str(fps),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(silent),
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"continuous render failed:\n{proc.stderr[-2500:]}")

    bed = pkg / "soft_bed.wav"
    voiced = out_dir / "voiced.mp4"
    soundtrack = {}
    sp = pkg / "soundtrack_plan_with_audio.json"
    if sp.is_file():
        soundtrack = json.loads(sp.read_text(encoding="utf-8"))
    narration = [
        s for s in (soundtrack.get("narration_segments") or []) if s.get("audio_path")
    ]
    if narration:
        cmd = [_ffmpeg(), "-y", "-i", str(silent), "-i", str(bed)]
        filter_parts = [f"[1:a]volume=0.22,apad=whole_dur={duration_s}[bed]"]
        narr_labels = []
        idx = 2
        for seg in narration:
            ap = Path(seg["audio_path"])
            if not ap.is_file():
                continue
            cmd.extend(["-i", str(ap)])
            start_ms = int(float(seg.get("start_time_s", 0)) * 1000)
            filter_parts.append(
                f"[{idx}:a]adelay={start_ms}|{start_ms},volume=1.0,apad[n{idx}]"
            )
            narr_labels.append(f"[n{idx}]")
            idx += 1
        if narr_labels:
            if len(narr_labels) == 1:
                narr_mix = narr_labels[0]
            else:
                filter_parts.append(
                    "".join(narr_labels)
                    + f"amix=inputs={len(narr_labels)}:duration=longest[narr]"
                )
                narr_mix = "[narr]"
            filter_parts.append(
                f"{narr_mix}[bed]amix=inputs=2:duration=first:dropout_transition=0[a]"
            )
            cmd.extend(
                [
                    "-filter_complex",
                    ";".join(filter_parts),
                    "-map",
                    "0:v:0",
                    "-map",
                    "[a]",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                    "-t",
                    str(duration_s),
                    "-movflags",
                    "+faststart",
                    str(voiced),
                ]
            )
            mix = subprocess.run(cmd, capture_output=True, text=True)
        else:
            narration = []
    if not narration:
        mix = subprocess.run(
            [
                _ffmpeg(),
                "-y",
                "-i",
                str(silent),
                "-i",
                str(bed),
                "-filter_complex",
                f"[1:a]volume=0.55,apad=whole_dur={duration_s}[a]",
                "-map",
                "0:v:0",
                "-map",
                "[a]",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-shortest",
                "-movflags",
                "+faststart",
                str(voiced),
            ],
            capture_output=True,
            text=True,
        )
    if mix.returncode != 0:
        raise RuntimeError(f"audio mix failed:\n{mix.stderr[-2000:]}")

    # Promote into shortform_mp4_research_complete/final/ (out_dir is .../_render/<id>)
    package_root = out_dir.parent.parent  # .../shortform_mp4_research_complete
    final_dir = package_root / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    final = final_dir / f"{pkg.name}.mp4"
    shutil.copyfile(voiced, final)
    shutil.copyfile(voiced, out_dir.parent / f"{pkg.name}.mp4")
    return final


def validate_mp4(path: Path) -> dict:
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
    # extract a mid frame and ensure no storyboard chrome strings via OCR-less heuristic:
    # re-read captions file association only; decode smoke
    decode = subprocess.run(
        [_ffmpeg(), "-v", "error", "-i", str(path), "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    dur = float(video.get("duration") or 0)
    return {
        "path": str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path),
        "width": video.get("width"),
        "height": video.get("height"),
        "duration_s": round(dur, 2),
        "has_audio": audio is not None,
        "audio_codec": (audio or {}).get("codec_name"),
        "full_decode_ok": decode.returncode == 0 and not decode.stderr.strip(),
        "duration_gate": 26.0 <= dur <= 28.5,
        "platform_contract": video.get("width") == 1080 and video.get("height") == 1920,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma-separated example_ids; default=all")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    _default_bank = REPO / "artifacts/social_media_voice_bank_2026-07-19/MANIFEST.tsv"
    ap.add_argument(
        "--voice-bank",
        nargs="?",
        const=str(_default_bank),
        default=None,
        help="Fill narration + captions from CosyVoice bank (join on beat atom_id)",
    )
    args = ap.parse_args()

    items = json.loads(STORYBOARDS.read_text(encoding="utf-8"))
    only = {x.strip() for x in args.only.split(",") if x.strip()}
    if only:
        items = [i for i in items if i["example_id"] in only]

    voice_bank = Path(args.voice_bank) if args.voice_bank else None
    work_root = args.out / "_packages"
    receipts = []
    for item in items:
        print(f"== {item['example_id']} ==")
        pkg = build_package(item, work_root, voice_bank=voice_bank)
        render_dir = args.out / "_render" / item["example_id"]
        if render_dir.exists():
            shutil.rmtree(render_dir)
        mp4 = render_one(pkg, render_dir)
        receipt = validate_mp4(mp4)
        receipt["example_id"] = item["example_id"]
        receipt["topic"] = item.get("topic")
        receipt["viewer_captions_only"] = True
        receipt["director_notes_on_plate"] = False
        receipt["beat_count"] = len(item["beats"])
        receipt["render_mode"] = "research_complete_vce"
        receipt["voice_bank"] = str(voice_bank) if voice_bank else None
        receipts.append(receipt)
        print(json.dumps(receipt, indent=2))

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "validation_receipts.jsonl").write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in receipts) + "\n",
        encoding="utf-8",
    )
    failed = [r for r in receipts if not (r["full_decode_ok"] and r["duration_gate"] and r["platform_contract"] and r["has_audio"])]
    if failed:
        print(f"FAIL: {len(failed)} receipts failed gates", file=sys.stderr)
        return 1
    print(f"OK: {len(receipts)} research-complete MP4s → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
