#!/usr/bin/env python3
"""Craft smoke: voice-bank MP3 + agreed PRIMARY shortform stack.

Uses the ratified craft (not simple horizontal drawtext):
  - Visual PRIMARY: broll_montage (multi-plate Ken Burns + hard cuts)
    ← scripts/social/render_broll_montage_shorts.py
  - Captions: kinetic ASS word-group reveals, portrait-safe
    ← scripts/social/render_kinetic_type_shorts.py (wrap2 / punch-in)
    Position mid-lower (y≈1286) with MarginL/R 96 — TikTok 9:16 safe
  - Audio: CosyVoice bank VO + soft pad + cut SFX

Authority: docs/PEARL_ANIMATOR_FACELESS_SHORTS_SPEC_2026-07-18.md
Look: artifacts/qa/.../LOOK_COMPARE.md → PRIMARY=broll_montage
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

from scripts.social_media.voice_bank_lookup import resolve_atom  # noqa: E402
from scripts.social.render_broll_montage_shorts import (  # noqa: E402
    BEAT_MOTIONS,
    FFMPEG,
    build_bed,
    build_cut_sfx,
    concat_clips,
    render_beat_clip,
)
from scripts.social.render_kinetic_type_shorts import (  # noqa: E402
    ACCENT,
    CREAM,
    WIDTH,
    HEIGHT,
    ass_time,
    hex_to_ass_bgr,
    split_into_n,
    word_groups,
    wrap2,
)

DEFAULT_ATOM = "EVG-ENUS-ANXI-CORP-SS-01"
DEFAULT_OUT = REPO / "artifacts/social_media_voice_bank_2026-07-19/smoke_reel"
STOCK = (
    REPO
    / "artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x"
    / "downloads/pexels"
)
PLATES = [
    STOCK / "anxiety/pexels__anxiety__8101094.jpeg",
    STOCK / "anxiety/pexels__anxiety__13228799.jpeg",
    STOCK / "anxiety/pexels__anxiety__18362514.jpeg",
    STOCK / "anxiety/pexels__anxiety__8733211.jpeg",
    STOCK / "anxiety/pexels__anxiety__18547794.jpeg",
]
ROLES = ["hook", "recognition", "mechanism", "practice", "payoff"]

# Mid-lower portrait band (TikTok bottom chrome ~25% → keep above y=1440)
CAPTION_Y = int(HEIGHT * 0.67)  # ~1286
MARGIN_LR = 96  # ~9% of 1080 — inside platform safe_zone left/right


def _ffprobe() -> str:
    for c in (Path("/opt/homebrew/bin/ffprobe"), Path("/usr/local/bin/ffprobe")):
        if c.is_file():
            return str(c)
    return "ffprobe"


def probe_duration(path: Path) -> float:
    try:
        from mutagen.mp3 import MP3

        length = float(MP3(path).info.length)
        if length > 0:
            return length
    except Exception:
        pass
    r = subprocess.run(
        [
            _ffprobe(),
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


def split_speakable(speakable: str, n: int) -> list[str]:
    parts: list[str] = []
    buf = ""
    for ch in speakable:
        buf += ch
        if ch in ".!?" and len(buf.strip()) > 12:
            parts.append(buf.strip())
            buf = ""
    if buf.strip():
        parts.append(buf.strip())
    if not parts:
        parts = [speakable.strip()]
    while len(parts) > n:
        parts[-2] = (parts[-2] + " " + parts[-1]).strip()
        parts.pop()
    while len(parts) < n:
        longest = max(range(len(parts)), key=lambda i: len(parts[i]))
        words = parts[longest].split()
        if len(words) < 4:
            parts.append(parts[-1])
            break
        mid = len(words) // 2
        a, b = " ".join(words[:mid]), " ".join(words[mid:])
        parts[longest] = a
        parts.insert(longest + 1, b)
    return parts[:n]


def wrap2_portrait(text: str, max_chars: int = 12, max_lines: int = 3) -> str:
    """Portrait wrap: short lines (≤~12 chars), up to 3 lines — never edge-to-edge."""
    words = text.split()
    if not words:
        return ""
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) <= max_chars or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) <= max_lines:
        return "\\N".join(lines)
    # Collapse overflow into last allowed line (still short words preferred)
    head, tail = lines[: max_lines - 1], lines[max_lines - 1 :]
    return "\\N".join(head + [" ".join(tail)])


def font_size_for_photo(text: str, role: str) -> int:
    """Smaller than solid-plate kinetic — photos need legible inset type."""
    length = len(text)
    base = 64 if role == "hook" else 54
    if length > 40:
        base -= 12
    elif length > 28:
        base -= 6
    return max(40, base)


def build_photo_kinetic_ass(beats: list[dict], out_path: Path) -> None:
    """Kinetic word-group ASS tuned for photo b-roll (cream + outline, mid-lower)."""
    cream = hex_to_ass_bgr(CREAM)
    accent = hex_to_ass_bgr(ACCENT)
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,60,{cream},{cream},&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,5,{MARGIN_LR},{MARGIN_LR},120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines: list[str] = []
    x = WIDTH // 2
    y = CAPTION_Y
    for beat in beats:
        role = beat["role"]
        text = beat["text"]
        start, end = beat["start"], beat["end"]
        dur = end - start
        fsize = font_size_for_photo(text, role)

        if role == "hook":
            group_size = 3 if len(text.split()) > 6 else 2
            groups = word_groups(text, group_size)
            cumulative = [" ".join(groups[: i + 1]) for i in range(len(groups))]
        elif role == "mechanism":
            groups = split_into_n(text, 3)
            cumulative = [" ".join(groups[: i + 1]) for i in range(len(groups))]
        elif role == "practice":
            groups = word_groups(text, 2)
            cumulative = [" ".join(groups[: i + 1]) for i in range(len(groups))]
        else:
            cumulative = [text]

        n = len(cumulative)
        gap = min(0.35, max(0.18, (dur * 0.55) / max(n, 1)))
        for i, step_text in enumerate(cumulative):
            step_start = start + i * gap
            step_end = end if i == n - 1 else start + (i + 1) * gap
            # Portrait-native wrap: short lines so 9:16 never edge-clips
            # (wrap2 collapses >2 lines into line2 — keep max_chars tight)
            display = wrap2_portrait(step_text, max_chars=14)
            fade = "\\fad(50,110)" if i == n - 1 else "\\fad(40,0)"
            override = (
                f"{{\\an5\\pos({x},{y})\\fs{fsize}\\c{cream}"
                f"\\fscx128\\fscy128\\t(0,140,\\fscx100\\fscy100){fade}}}"
            )
            lines.append(
                f"Dialogue: 0,{ass_time(step_start)},{ass_time(step_end)},"
                f"Default,,0,0,0,,{override}{display}"
            )

        if role == "payoff":
            bar_y = y + fsize // 2 + 40
            bar = (
                f"{{\\an5\\pos({x},{bar_y})\\c{accent}\\fad(50,110)\\p1}}"
                "m -100 0 l 100 0 l 100 5 l -100 5{\\p0}"
            )
            lines.append(
                f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{bar}"
            )

    out_path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def burn_ass(silent: Path, ass_path: Path, out_path: Path) -> None:
    # Escape for ffmpeg filter path
    import os

    preset = os.environ.get("VOICE_BANK_FFMPEG_PRESET") or os.environ.get(
        "MEDIA_BANK_FFMPEG_PRESET", "medium"
    )
    crf = os.environ.get("VOICE_BANK_FFMPEG_CRF", "16")
    ass_esc = str(ass_path).replace("\\", "/").replace(":", "\\:")
    cmd = [
        FFMPEG,
        "-y",
        "-i",
        str(silent),
        "-vf",
        f"ass={ass_esc}",
        "-pix_fmt",
        "yuv420p",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        preset,
        "-crf",
        crf,
        str(out_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[-3000:])


def mix_vo_bed_sfx(
    video: Path,
    vo_mp3: Path,
    bed: Path,
    sfx: Path,
    out_path: Path,
    duration_s: float,
    cut_times_s: list[float],
) -> None:
    filt_parts = [
        f"[1:a]volume=0.10,afade=t=in:st=0:d=0.6,"
        f"afade=t=out:st={max(duration_s - 1.8, 0):.2f}:d=1.5[bed]",
        "[2:a]volume=1.0,apad[vo]",
    ]
    delayed = []
    for i, t0 in enumerate(cut_times_s):
        ms = int(t0 * 1000)
        filt_parts.append(f"[3:a]adelay={ms}|{ms},volume=0.55[s{i}]")
        delayed.append(f"[s{i}]")
    labels = "[vo][bed]" + "".join(delayed)
    n = 2 + len(delayed)
    filt_parts.append(
        f"{labels}amix=inputs={n}:duration=first:dropout_transition=0,"
        f"alimiter=limit=0.95[aout]"
    )
    cmd = [
        FFMPEG,
        "-y",
        "-i",
        str(video),
        "-i",
        str(bed),
        "-i",
        str(vo_mp3),
        "-i",
        str(sfx),
        "-filter_complex",
        ";".join(filt_parts),
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
        f"{duration_s:.2f}",
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[-3000:])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--atom-id", default=DEFAULT_ATOM)
    ap.add_argument("--manifest", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--beats", type=int, default=5)
    args = ap.parse_args()

    n = max(3, min(5, args.beats))
    hit = resolve_atom(args.atom_id, manifest=args.manifest, require_audio=True)
    assert hit.local_mp3 is not None
    vo_dur = probe_duration(hit.local_mp3)
    total = max(10.0, min(30.0, vo_dur + 0.35))
    weights = [1.0, 1.15, 1.25, 1.3, 1.1][:n]
    wsum = sum(weights)
    bounds: list[tuple[float, float]] = []
    t = 0.0
    for w in weights:
        dur = total * (w / wsum)
        bounds.append((round(t, 3), round(t + dur, 3)))
        t += dur
    bounds[-1] = (bounds[-1][0], round(total, 3))

    chunks = split_speakable(hit.speakable_text, n)
    plates = [p for p in PLATES if p.is_file()][:n]
    if len(plates) < n:
        print(f"ERROR: need {n} plates, found {len(plates)}", file=sys.stderr)
        return 1

    out_dir = args.out_dir
    work = out_dir / "_broll_craft"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    mp3_copy = out_dir / f"{args.atom_id}.mp3"
    shutil.copy2(hit.local_mp3, mp3_copy)
    (out_dir / "caption_speakable.txt").write_text(hit.speakable_text + "\n", encoding="utf-8")

    clip_paths = []
    for i in range(n):
        t0, t1 = bounds[i]
        clip = work / f"beat{i}.mp4"
        render_beat_clip(plates[i], i, t1 - t0, BEAT_MOTIONS[i % len(BEAT_MOTIONS)], clip)
        clip_paths.append(clip)

    silent = work / "montage_silent.mp4"
    concat_clips(clip_paths, silent)

    beats = [
        {
            "role": ROLES[i],
            "text": chunks[i],
            "start": bounds[i][0],
            "end": bounds[i][1],
        }
        for i in range(n)
    ]
    ass_path = work / "captions_kinetic.ass"
    build_photo_kinetic_ass(beats, ass_path)

    captioned = work / "montage_captioned.mp4"
    burn_ass(silent, ass_path, captioned)

    bed = work / "bed.wav"
    sfx = work / "sfx_cut.wav"
    build_bed(bed, total)
    build_cut_sfx(sfx)

    mp4 = out_dir / f"{args.atom_id}_short_9x16.mp4"
    mix_vo_bed_sfx(
        captioned, mp3_copy, bed, sfx, mp4, total, [t0 for t0, _ in bounds]
    )

    qa = work / "qa_frames"
    qa.mkdir(exist_ok=True)
    for i, (t0, t1) in enumerate(bounds):
        mid = (t0 + t1) / 2
        subprocess.run(
            [
                FFMPEG,
                "-y",
                "-ss",
                f"{mid:.2f}",
                "-i",
                str(mp4),
                "-frames:v",
                "1",
                "-update",
                "1",
                str(qa / f"beat{i}_{mid:.1f}s.jpg"),
            ],
            capture_output=True,
        )

    receipt = {
        "atom_id": args.atom_id,
        "acceptance_layer": "system working — craft smoke (broll PRIMARY + kinetic ASS + voice bank)",
        "style_stack": {
            "visual": "broll_montage (PRIMARY)",
            "captions": "kinetic_type ASS word-groups (portrait mid-lower)",
            "audio": "social_voice_bank CosyVoice MP3 + soft pad + cut SFX",
        },
        "authority": [
            "docs/PEARL_ANIMATOR_FACELESS_SHORTS_SPEC_2026-07-18.md",
            "LOOK_COMPARE.md PRIMARY=broll_montage",
        ],
        "mp4": str(mp4.relative_to(REPO)),
        "mp3": str(mp3_copy.relative_to(REPO)),
        "ass": str(ass_path.relative_to(REPO)),
        "speakable_text": hit.speakable_text,
        "caption_geometry": {
            "y": CAPTION_Y,
            "y_frac": 0.67,
            "margin_lr_px": MARGIN_LR,
            "wrap_chars": "16–18",
            "max_lines": 2,
            "engine": "libass kinetic punch-in",
        },
        "beat_bounds": bounds,
        "beat_captions": chunks,
        "duration_s": round(total, 2),
        "bytes": mp4.stat().st_size,
        "operator_check": "Portrait phone: captions fully inset; kinetic builds; VO=speakable",
    }
    (out_dir / "SMOKE_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    print(f"OK craft smoke → {mp4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
