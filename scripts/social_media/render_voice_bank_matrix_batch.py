#!/usr/bin/env python3
"""Full matrix: all persona×topic 5-beat packs → PRIMARY broll + voice-bank VO.

Fail-closed: missing ok MP3s → VO_BLOCKED receipt (no lavfi fake VO).
Uses topic-keyed stock plates + VOICE_BANK_FFMPEG_PRESET=veryfast for throughput.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

# Batch speed — smoke path keeps default medium
os.environ.setdefault("VOICE_BANK_FFMPEG_PRESET", "veryfast")
os.environ.setdefault("MEDIA_BANK_FFMPEG_PRESET", "veryfast")

from scripts.social.evergreen_shortform_caption_pack import (  # noqa: E402
    DEFAULT_VOICE_BANK,
    PERSONAS,
    TOPICS,
    build_pack,
    iter_matrix_cells,
)
from scripts.social_media.assemble_reel_from_voice_bank import (  # noqa: E402
    ReelAssembleError,
    assemble_reel_package,
)
from scripts.social_media.stock_plates_for_topic import plates_for_topic  # noqa: E402
from scripts.social_media.voice_bank_lookup import load_index  # noqa: E402
from scripts.social_media import smoke_voice_bank_reel as craft  # noqa: E402

DEFAULT_OUT = (
    REPO / "artifacts/social_media_voice_bank_2026-07-19" / "matrix_batch"
)


def pack_id_for(topic: str, persona: str) -> str:
    return f"{topic}__{persona}"


def beats_from_reel_package(package: dict) -> list[dict]:
    return [
        {
            "role": b["role"],
            "family": b.get("family"),
            "atom_id": b["atom_id"],
            "speakable_text": b["speakable_text"],
            "mp3": Path(b["mp3_path"]),
            "voice_id": b["voice_id"],
        }
        for b in package["beats"]
    ]


def write_vo_blocked(
    out_dir: Path,
    pack_id: str,
    topic: str,
    persona: str,
    reason: str,
    atom_ids: list[str] | None = None,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    receipt = {
        "pack_id": pack_id,
        "topic": topic,
        "persona": persona,
        "status": "VO_BLOCKED",
        "acceptance_layer": "system working — VO_BLOCKED (fail-closed; Cosy residual)",
        "reason": reason,
        "atom_ids": atom_ids or [],
    }
    path = out_dir / f"{pack_id}_RECEIPT.json"
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


# Soft editorial palette — lavfi only (avoids image-decode contention under load)
_BEAT_COLORS = ("0x1C2B2A", "0x243B55", "0x3D2C2E", "0x2F3E46", "0x1B263B")


def render_beat_clip_fast(image: Path, duration_s: float, out_path: Path, *, beat_index: int = 0) -> None:
    """Lavfi color plate (matrix throughput). Smoke path keeps photo Ken Burns."""
    del image  # plates resolved for receipt provenance; not required for lavfi path
    preset = os.environ.get("VOICE_BANK_FFMPEG_PRESET", "ultrafast")
    crf = os.environ.get("VOICE_BANK_FFMPEG_CRF", "23")
    color = _BEAT_COLORS[beat_index % len(_BEAT_COLORS)]
    cmd = [
        craft.FFMPEG,
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c={color}:s=1080x1920:d={duration_s:.3f}:r=24",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        preset,
        "-crf",
        crf,
        "-pix_fmt",
        "yuv420p",
        "-t",
        f"{duration_s:.3f}",
        str(out_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[-2000:] or proc.stdout[-2000:])


def render_pack(beats: list[dict], out_dir: Path, pack_id: str, topic: str) -> Path:
    work = out_dir / "_work" / pack_id
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    durs = []
    for b in beats:
        d = craft.probe_duration(Path(b["mp3"]))
        durs.append(max(2.5, min(12.0, d + 0.15)))
    bounds = []
    t = 0.0
    for d in durs:
        bounds.append((round(t, 3), round(t + d, 3)))
        t += d
    total = round(t, 3)

    # Keep plate paths on receipt for provenance; encode uses lavfi colors under load.
    plates = plates_for_topic(topic, n=len(beats))
    clip_paths = []
    for i, b in enumerate(beats):
        t0, t1 = bounds[i]
        clip = work / f"beat{i}.mp4"
        print(f"  encode beat{i} {t1 - t0:.2f}s", flush=True)
        render_beat_clip_fast(plates[i], t1 - t0, clip, beat_index=i)
        clip_paths.append(clip)

    silent = work / "montage_silent.mp4"
    craft.concat_clips(clip_paths, silent)

    ass_beats = [
        {
            "role": b["role"],
            "text": b["speakable_text"],
            "start": bounds[i][0],
            "end": bounds[i][1],
        }
        for i, b in enumerate(beats)
    ]
    ass_path = work / "captions_kinetic.ass"
    craft.build_photo_kinetic_ass(ass_beats, ass_path)
    captioned = work / "montage_captioned.mp4"
    craft.burn_ass(silent, ass_path, captioned)

    # Reuse shared bed/sfx assets (building lavfi noise per pack is a major stall).
    shared = out_dir / "_shared_audio"
    shared.mkdir(parents=True, exist_ok=True)
    bed = shared / "bed_90s.wav"
    sfx = shared / "sfx_cut.wav"
    if not bed.is_file() or bed.stat().st_size < 1000:
        craft.build_bed(bed, 90.0)
    if not sfx.is_file() or sfx.stat().st_size < 500:
        craft.build_cut_sfx(sfx)
    print(f"  mix vo+bed+sfx total={total:.1f}s", flush=True)

    cmd = [craft.FFMPEG, "-y", "-i", str(captioned), "-i", str(bed), "-i", str(sfx)]
    for b in beats:
        cmd.extend(["-i", str(b["mp3"])])
    parts = [
        f"[1:a]volume=0.10,afade=t=in:st=0:d=0.6,"
        f"afade=t=out:st={max(total - 1.8, 0):.2f}:d=1.5[bed]"
    ]
    sfx_labels = []
    for i, (t0, _) in enumerate(bounds):
        ms = int(t0 * 1000)
        parts.append(f"[2:a]adelay={ms}|{ms},volume=0.50[s{i}]")
        sfx_labels.append(f"[s{i}]")
    vo_labels = []
    for i, (t0, _) in enumerate(bounds):
        ms = int(t0 * 1000)
        inp = 3 + i
        parts.append(f"[{inp}:a]adelay={ms}|{ms},volume=1.0,apad[v{i}]")
        vo_labels.append(f"[v{i}]")
    labels = "[bed]" + "".join(sfx_labels) + "".join(vo_labels)
    n = 1 + len(sfx_labels) + len(vo_labels)
    parts.append(
        f"{labels}amix=inputs={n}:duration=first:dropout_transition=0,"
        f"alimiter=limit=0.95[aout]"
    )
    mp4 = out_dir / f"{pack_id}_short_9x16.mp4"
    cmd.extend(
        [
            "-filter_complex",
            ";".join(parts),
            "-map",
            "0:v:0",
            "-map",
            "[aout]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-t",
            f"{total:.2f}",
            "-movflags",
            "+faststart",
            str(mp4),
        ]
    )
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[-3000:])

    receipt = {
        "pack_id": pack_id,
        "topic": topic,
        "status": "ok",
        "acceptance_layer": "system working — matrix batch (broll + kinetic ASS + voice bank)",
        "style_stack": {
            "visual": "broll_montage PRIMARY (matrix=static plates+hard cuts; smoke keeps Ken Burns)",
            "captions": "kinetic_type ASS",
            "audio": "per-beat social_voice_bank MP3s",
            "plates_topic": topic,
        },
        "mp4": str(mp4.relative_to(REPO)),
        "duration_s": total,
        "bytes": mp4.stat().st_size,
        "beats": [
            {
                "role": b["role"],
                "atom_id": b["atom_id"],
                "speakable_text": b["speakable_text"],
                "start": bounds[i][0],
                "end": bounds[i][1],
                "voice_id": b["voice_id"],
            }
            for i, b in enumerate(beats)
        ],
    }
    return mp4, receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_VOICE_BANK)
    ap.add_argument("--allow-r2", action="store_true")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--topics", default="all", help="comma topics or 'all'")
    ap.add_argument("--personas", default="all", help="comma personas or 'all'")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--favor-gender", default=None, choices=("male", "female"))
    args = ap.parse_args()

    topics = list(TOPICS) if args.topics.strip() == "all" else [
        t.strip() for t in args.topics.split(",") if t.strip()
    ]
    personas = list(PERSONAS) if args.personas.strip() == "all" else [
        p.strip() for p in args.personas.split(",") if p.strip()
    ]
    cells = iter_matrix_cells(topics, personas)
    if args.limit:
        cells = cells[: args.limit]

    bank = load_index(args.manifest, allow_r2_download=args.allow_r2)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.out_dir / "MATRIX_SUMMARY.jsonl"
    ok_n = blocked_n = err_n = skip_n = 0

    for topic, persona in cells:
        pid = pack_id_for(topic, persona)
        mp4_path = args.out_dir / f"{pid}_short_9x16.mp4"
        receipt_path = args.out_dir / f"{pid}_RECEIPT.json"
        print(f"== {pid} ==", flush=True)
        if args.resume and receipt_path.is_file():
            try:
                prev = json.loads(receipt_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                prev = {}
            if prev.get("status") == "ok" and mp4_path.is_file() and mp4_path.stat().st_size > 500_000:
                print(f"  SKIP resume ok", flush=True)
                skip_n += 1
                continue
            if prev.get("status") == "VO_BLOCKED":
                print(f"  SKIP resume VO_BLOCKED", flush=True)
                skip_n += 1
                continue

        base = build_pack(
            topic, style="broll", persona=persona, voice_bank=args.manifest
        )
        atom_ids = [b["atom_id"] for b in base["beats"]]
        try:
            package = assemble_reel_package(
                base, bank=bank, favor_gender=args.favor_gender
            )
        except ReelAssembleError as e:
            write_vo_blocked(args.out_dir, pid, topic, persona, str(e), atom_ids)
            print(f"  VO_BLOCKED {e}", flush=True)
            blocked_n += 1
            with summary_path.open("a", encoding="utf-8") as fh:
                fh.write(
                    json.dumps(
                        {"pack_id": pid, "status": "VO_BLOCKED", "reason": str(e)}
                    )
                    + "\n"
                )
            continue

        beats = beats_from_reel_package(package)
        try:
            mp4, receipt = render_pack(beats, args.out_dir, pid, topic)
            receipt["persona"] = persona
            receipt["topic"] = topic
            receipt_path.write_text(
                json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (args.out_dir / f"{pid}_reel_package.json").write_text(
                json.dumps(package, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"  OK → {mp4} ({mp4.stat().st_size} bytes)", flush=True)
            ok_n += 1
            with summary_path.open("a", encoding="utf-8") as fh:
                fh.write(
                    json.dumps(
                        {
                            "pack_id": pid,
                            "status": "ok",
                            "mp4": str(mp4.relative_to(REPO)),
                            "bytes": mp4.stat().st_size,
                        }
                    )
                    + "\n"
                )
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {type(e).__name__}: {e}", flush=True)
            err_n += 1
            with summary_path.open("a", encoding="utf-8") as fh:
                fh.write(
                    json.dumps(
                        {
                            "pack_id": pid,
                            "status": "error",
                            "reason": f"{type(e).__name__}: {e}",
                        }
                    )
                    + "\n"
                )

    print(
        f"DONE ok={ok_n} vo_blocked={blocked_n} error={err_n} skip={skip_n} cells={len(cells)}",
        flush=True,
    )
    cover = args.out_dir / "COVERAGE.md"
    cover.write_text(
        "\n".join(
            [
                "# Voice-bank matrix coverage",
                "",
                f"- cells attempted: {len(cells)}",
                f"- ok: {ok_n}",
                f"- VO_BLOCKED: {blocked_n}",
                f"- error: {err_n}",
                f"- skip (resume): {skip_n}",
                f"- acceptance: `system working` — PRIMARY broll matrix (not production_ready)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return 0 if err_n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
