#!/usr/bin/env python3
"""Join caption-pack beats → voice-bank MP3s → reel_package (fail-closed).

Every social short that speaks must go through this joiner:
  - captions use speakable_text matching the MP3
  - beat duration_s = ffprobe(MP3) (not reading-WPM alone)
  - missing/ok≠status/wrong gender → hard fail (no silent lavfi-as-voice)

Usage:
  python3 scripts/social_media/assemble_reel_from_voice_bank.py \\
    --topic burnout --style broll --out /tmp/reel_package.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.social.evergreen_shortform_caption_pack import (  # noqa: E402
    DEFAULT_VOICE_BANK,
    build_pack,
)
from scripts.social_media.voice_bank_lookup import (  # noqa: E402
    VoiceBankError,
    VoiceBankIndex,
    load_index,
)

MATRIX_PATH = REPO / "config/tts/social_media_voice_matrix.yaml"
FFPROBE_CANDIDATES = (
    Path("/opt/homebrew/bin/ffprobe"),
    Path("/usr/local/bin/ffprobe"),
)


class ReelAssembleError(RuntimeError):
    """Hard-fail for missing bank coverage or gender mismatch."""


def _ffprobe_bin() -> str:
    for c in FFPROBE_CANDIDATES:
        if c.is_file():
            return str(c)
    return "ffprobe"


def probe_duration_s(path: Path) -> float:
    # Prefer mutagen — ffprobe can hang when many ffmpeg jobs saturate the host.
    try:
        from mutagen.mp3 import MP3

        length = float(MP3(path).info.length)
        if length > 0:
            return length
    except Exception:
        pass
    try:
        r = subprocess.run(
            [
                _ffprobe_bin(),
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=20,
        )
        return float(r.stdout.strip())
    except Exception as e:
        raise ReelAssembleError(f"duration probe failed for {path}: {e}") from e


def load_matrix(path: Path = MATRIX_PATH) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def resolve_favored_voice_id(
    matrix: dict[str, Any],
    persona: str,
    *,
    favor_gender: str | None = None,
) -> str:
    """Matrix default voice; optional favor_gender uses voice_id_alternate when set."""
    pv = (matrix.get("persona_voices") or {}).get(persona)
    if not pv:
        raise ReelAssembleError(f"persona not in voice matrix: {persona}")
    default = str(pv["voice_id"])
    if not favor_gender:
        return default
    want = favor_gender.strip().lower()
    if want not in ("male", "female"):
        raise ReelAssembleError(f"favor_gender must be male|female, got {favor_gender!r}")
    default_gender = str(pv.get("gender") or "").lower()
    if default_gender == want:
        return default
    alt = pv.get("voice_id_alternate")
    if not alt:
        raise ReelAssembleError(
            f"persona {persona} has no voice_id_alternate for favor_gender={want}"
        )
    return str(alt)


def assemble_reel_package(
    pack: dict[str, Any],
    *,
    bank: VoiceBankIndex | None = None,
    favor_gender: str | None = None,
    matrix: dict[str, Any] | None = None,
    pad_s: float = 0.12,
    min_beat_s: float = 2.0,
    max_beat_s: float = 14.0,
) -> dict[str, Any]:
    """Attach MP3s + rewrite durations. Fail if any beat lacks bank audio."""
    bank = bank or load_index(allow_r2_download=False)
    matrix = matrix or load_matrix()
    beats_out: list[dict[str, Any]] = []
    missing: list[str] = []
    t = 0.0

    for beat in pack.get("beats") or []:
        aid = beat.get("atom_id") or ""
        persona = beat.get("persona") or pack.get("persona") or ""
        favored = resolve_favored_voice_id(matrix, persona, favor_gender=favor_gender)
        try:
            hit = bank.resolve(aid, require_audio=True)
        except VoiceBankError as e:
            missing.append(f"{aid}: {e}")
            continue
        if hit.voice_id and hit.voice_id != favored:
            # Bank row must match favored gender voice (no mux-time invent)
            missing.append(
                f"{aid}: bank voice_id={hit.voice_id!r} != favored {favored!r} "
                f"(persona={persona}, favor_gender={favor_gender!r})"
            )
            continue
        assert hit.local_mp3 is not None
        audio_dur = probe_duration_s(hit.local_mp3)
        dur = max(min_beat_s, min(max_beat_s, audio_dur + pad_s))
        caption = hit.speakable_text
        beats_out.append(
            {
                **beat,
                "full_text": caption,
                "on_screen": beat.get("on_screen") or caption,
                "speakable_text": caption,
                "caption_source": "voice_bank_speakable",
                "mp3_path": str(hit.local_mp3),
                "r2_key": hit.r2_key,
                "voice_id": hit.voice_id,
                "favored_voice_id": favored,
                "start": round(t, 3),
                "end": round(t + dur, 3),
                "duration_s": round(dur, 3),
                "audio_duration_s": round(audio_dur, 3),
            }
        )
        t += dur

    if missing:
        raise ReelAssembleError(
            "voice-bank join failed (hard-fail; no lavfi-as-voice fallback):\n  - "
            + "\n  - ".join(missing)
        )

    return {
        "schema": "social_reel_package_v1",
        "topic": pack.get("topic"),
        "style": pack.get("style"),
        "persona": (pack.get("beats") or [{}])[0].get("persona"),
        "source_pack": pack.get("source"),
        "voice_bank_manifest": str(bank.manifest_path),
        "favor_gender": favor_gender,
        "total_duration_s": round(t, 3),
        "beats": beats_out,
        "status": "ok",
        "acceptance_layer": "system working — reel package joined to voice bank",
    }


def concat_narration_mp3(package: dict[str, Any], out_path: Path) -> Path:
    """Concatenate per-beat MP3s into one narration track (optional helper)."""
    ffmpeg = "/opt/homebrew/bin/ffmpeg"
    if not Path(ffmpeg).is_file():
        ffmpeg = "ffmpeg"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lst = out_path.parent / f"{out_path.stem}_concat.txt"
    lines = []
    for b in package["beats"]:
        p = Path(b["mp3_path"]).resolve()
        lines.append(f"file '{p}'")
    lst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(lst),
        "-c:a",
        "libmp3lame",
        "-q:a",
        "2",
        str(out_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ReelAssembleError(proc.stderr[-2000:] or proc.stdout[-2000:])
    package["narration_mp3"] = str(out_path)
    return out_path


def mix_vo_with_bed(
    video: Path,
    package: dict[str, Any],
    bed: Path,
    out_path: Path,
    *,
    bed_volume: float = 0.10,
) -> Path:
    """Mux video with delayed per-beat VO + ducked bed (primary audio = bank)."""
    ffmpeg = "/opt/homebrew/bin/ffmpeg"
    if not Path(ffmpeg).is_file():
        ffmpeg = "ffmpeg"
    beats = package["beats"]
    total = float(package["total_duration_s"])
    cmd = [ffmpeg, "-y", "-i", str(video), "-i", str(bed)]
    for b in beats:
        cmd.extend(["-i", str(b["mp3_path"])])
    parts = [
        f"[1:a]volume={bed_volume},afade=t=in:st=0:d=0.6,"
        f"afade=t=out:st={max(total - 1.8, 0):.2f}:d=1.5[bed]"
    ]
    vo_labels = []
    for i, b in enumerate(beats):
        ms = int(float(b["start"]) * 1000)
        inp = 2 + i
        parts.append(f"[{inp}:a]adelay={ms}|{ms},volume=1.0,apad[v{i}]")
        vo_labels.append(f"[v{i}]")
    labels = "[bed]" + "".join(vo_labels)
    n = 1 + len(vo_labels)
    parts.append(
        f"{labels}amix=inputs={n}:duration=first:dropout_transition=0,"
        f"alimiter=limit=0.95[aout]"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
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
            str(out_path),
        ]
    )
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ReelAssembleError(proc.stderr[-2500:] or "ffmpeg mix failed")
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--topic", default="anxiety")
    ap.add_argument("--style", default="broll", choices=("broll", "kinetic", "metaphor"))
    ap.add_argument("--manifest", type=Path, default=DEFAULT_VOICE_BANK)
    ap.add_argument("--favor-gender", default=None, choices=("male", "female"))
    ap.add_argument("--allow-r2", action="store_true")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--write-narration", type=Path, default=None)
    args = ap.parse_args()

    pack = build_pack(args.topic, style=args.style, voice_bank=args.manifest)
    bank = load_index(args.manifest, allow_r2_download=args.allow_r2)
    try:
        package = assemble_reel_package(
            pack, bank=bank, favor_gender=args.favor_gender
        )
    except ReelAssembleError as e:
        print(str(e), file=sys.stderr)
        return 2

    if args.write_narration:
        concat_narration_mp3(package, args.write_narration)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"OK reel_package topic={package['topic']} beats={len(package['beats'])} "
        f"dur={package['total_duration_s']}s → {args.out}"
    )
    for b in package["beats"]:
        print(
            f"  {b['role']:12} {b['duration_s']:5.2f}s  {b['voice_id']:14}  {b['atom_id']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
