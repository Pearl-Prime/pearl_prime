#!/usr/bin/env python3
"""Pilot batch: evergreen 5-beat packs × voice-bank VO → PRIMARY broll craft MP4s.

Reuses smoke_voice_bank_reel craft (broll montage + kinetic ASS + bank MP3s).
Default: anxiety × corporate_managers (5 roles / 5 bank atoms).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.social.evergreen_shortform_caption_pack import (  # noqa: E402
    ROLE_FAMILY,
    load_evergreen,
    pick_atom,
)
from scripts.social_media.voice_bank_lookup import load_index, resolve_atom  # noqa: E402
from scripts.social_media import smoke_voice_bank_reel as craft  # noqa: E402

DEFAULT_OUT = (
    REPO
    / "artifacts/social_media_voice_bank_2026-07-19"
    / "pilot_batch"
)

# Anxiety corporate picks (variant_index aligned with DEFAULT_PICKS spirit)
CORP_ANXIETY_VARIANTS = {
    "HOOK_COVER": 2,
    "PROBLEM_AGITATION": 2,
    "MECHANISM_EXPLAINER": 2,
    "TOOL_STEP": 1,
    "SAVEABLE_PAYOFF": 2,
}


def build_corp_anxiety_beats(bank) -> list[dict]:
    rows = load_evergreen()
    persona = "corporate_managers"
    topic = "anxiety"
    beats = []
    for role in craft.ROLES:
        fam = ROLE_FAMILY[role]
        atom = pick_atom(rows, topic, persona, fam, CORP_ANXIETY_VARIANTS[fam])
        hit = bank.resolve(atom["atom_id"], require_audio=True)
        beats.append(
            {
                "role": role,
                "family": fam,
                "atom_id": atom["atom_id"],
                "speakable_text": hit.speakable_text,
                "mp3": hit.local_mp3,
                "voice_id": hit.voice_id,
            }
        )
    return beats


def render_pack(beats: list[dict], out_dir: Path, pack_id: str) -> Path:
    """One MP4: 5 bank VO segments timed to probed durations + craft visuals."""
    work = out_dir / "_work" / pack_id
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Probe durations; pad small gaps between beats
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

    plates = [p for p in craft.PLATES if p.is_file()]
    if len(plates) < len(beats):
        raise FileNotFoundError("need 5 anxiety plates for broll montage")

    clip_paths = []
    for i, b in enumerate(beats):
        t0, t1 = bounds[i]
        clip = work / f"beat{i}.mp4"
        craft.render_beat_clip(
            plates[i], i, t1 - t0, craft.BEAT_MOTIONS[i % len(craft.BEAT_MOTIONS)], clip
        )
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

    # Stitch VO: delay each MP3 to beat start, mix with bed + cut sfx
    bed = work / "bed.wav"
    sfx = work / "sfx_cut.wav"
    craft.build_bed(bed, total)
    craft.build_cut_sfx(sfx)

    # Build multi-VO mix via ffmpeg
    cmd = [craft.FFMPEG, "-y", "-i", str(captioned), "-i", str(bed), "-i", str(sfx)]
    for b in beats:
        cmd.extend(["-i", str(b["mp3"])])
    # filter: bed + sfx delays + vo delays
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
        "acceptance_layer": "system working — pilot batch (broll + kinetic ASS + voice bank)",
        "style_stack": {
            "visual": "broll_montage (PRIMARY)",
            "captions": "kinetic_type ASS",
            "audio": "per-beat social_voice_bank MP3s",
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
    (out_dir / f"{pack_id}_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return mp4


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--manifest", type=Path, default=None)
    ap.add_argument(
        "--packs",
        default="anxiety_corporate",
        help="comma list; currently: anxiety_corporate",
    )
    args = ap.parse_args()
    bank = load_index(args.manifest, allow_r2_download=False)
    packs = [p.strip() for p in args.packs.split(",") if p.strip()]
    receipts = []
    for pack in packs:
        if pack != "anxiety_corporate":
            print(f"skip unknown pack {pack}", file=sys.stderr)
            continue
        print(f"== {pack} ==")
        beats = build_corp_anxiety_beats(bank)
        for b in beats:
            print(f"  {b['role']:12} {b['atom_id']}  {b['speakable_text'][:50]}…")
        mp4 = render_pack(beats, args.out_dir, pack)
        print(f"OK → {mp4}")
        receipts.append(mp4)
    print(f"DONE {len(receipts)} pilot MP4(s)")
    return 0 if receipts else 1


if __name__ == "__main__":
    raise SystemExit(main())
