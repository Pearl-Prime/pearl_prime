#!/usr/bin/env python3
"""Assemble guided therapeutic practices from pre-recorded sentence bank.

Takes an exercise definition (list of sentence IDs + pause durations),
looks up pre-recorded MP3 clips from assets/sentence_bank/, applies
post-production (slow, EQ, reverb), inserts silences, mixes with
ambient music, outputs final practice MP3.

Usage:
    python3 scripts/pearl_practice/assemble_from_bank.py \
        --exercise exercises/grief_healthcare_v01.yaml \
        -o ~/Desktop/grief_practice.mp3

    python3 scripts/pearl_practice/assemble_from_bank.py \
        --persona healthcare_rns --topic grief --variant 1 \
        -o ~/Desktop/grief_practice.mp3
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    print("PyYAML required", file=sys.stderr)
    sys.exit(1)

BANK_DIR = REPO_ROOT / "assets" / "sentence_bank"
FF = os.environ.get("FFMPEG_BIN", "/opt/homebrew/bin/ffmpeg")


def _load_bank_index() -> dict:
    cfg = yaml.safe_load((REPO_ROOT / "config" / "pearl_practice" / "sentence_bank.yaml").read_text())
    return cfg.get("sentences", {})


def _find_clip(sentence_id: str) -> Path | None:
    """Find pre-recorded clip by sentence ID."""
    p = BANK_DIR / f"{sentence_id}.mp3"
    return p if p.is_file() else None


def _find_clip_by_text(text: str, bank: dict) -> tuple[str, Path] | None:
    """Find clip by matching text content."""
    for sid, data in bank.items():
        if data["text"].strip().lower() == text.strip().lower():
            p = BANK_DIR / f"{sid}.mp3"
            if p.is_file():
                return sid, p
    return None


def _generate_silence(duration_s: float, out: Path):
    subprocess.run([FF, "-y", "-f", "lavfi", "-i",
                    f"anullsrc=channel_layout=mono:sample_rate=44100",
                    "-t", str(round(duration_s, 2)),
                    "-c:a", "libmp3lame", "-b:a", "64k", str(out)],
                   capture_output=True, timeout=10)


def _post_produce_clip(src: Path, dst: Path, tempo: float = 0.82, warmth: float = 3):
    """Apply slow + warm EQ + reverb + compression to one clip."""
    subprocess.run([FF, "-y", "-i", str(src),
                    "-af", (f"atempo={tempo},"
                            f"equalizer=f=300:t=q:w=1:g={warmth},"
                            "equalizer=f=3500:t=q:w=1:g=-4,"
                            "aecho=0.8:0.7:40:0.2,"
                            "compand=attacks=0.3:decays=0.8:"
                            "points=-80/-80|-45/-45|-27/-25:soft-knee=6"),
                    "-c:a", "libmp3lame", "-b:a", "192k", str(dst)],
                   capture_output=True, timeout=10)


def assemble_practice(
    sections: list[dict],
    out_path: Path,
    *,
    tempo: float = 0.82,
    warmth: float = 3,
    include_ambient: bool = True,
) -> dict:
    """Assemble a practice from section definitions.

    Each section: {"text": str, "sentence_id": str (optional), "pause_s": float, "section": str}
    If sentence_id provided, uses pre-recorded clip. Otherwise tries text match.
    """
    bank = _load_bank_index()
    work = out_path.parent / ".work"
    work.mkdir(parents=True, exist_ok=True)

    concat_parts: list[Path] = []
    total_speech = 0
    total_silence = 0
    matched = 0
    missed = 0

    for i, sec in enumerate(sections):
        # Find the pre-recorded clip
        clip_src = None
        sid = sec.get("sentence_id", "")
        if sid:
            clip_src = _find_clip(sid)

        if not clip_src:
            result = _find_clip_by_text(sec["text"], bank)
            if result:
                sid, clip_src = result

        if not clip_src:
            missed += 1
            print(f"  MISS [{i+1}]: \"{sec['text'][:50]}\" — not in bank", flush=True)
            continue

        matched += 1

        # Post-produce
        pp = work / f"pp_{i:03d}.mp3"
        _post_produce_clip(clip_src, pp, tempo=tempo, warmth=warmth)
        concat_parts.append(pp)

        # Get clip duration
        try:
            r = subprocess.run([FF.replace("ffmpeg", "ffprobe"), "-v", "quiet",
                                "-show_entries", "format=duration",
                                "-of", "default=noprint_wrappers=1:nokey=1", str(pp)],
                               capture_output=True, text=True, timeout=5)
            clip_dur = float(r.stdout.strip())
        except Exception:
            clip_dur = 1.5
        total_speech += clip_dur

        # Silence
        pause_s = sec.get("pause_s", 4)
        if pause_s > 0.3:
            sil = work / f"sil_{i:03d}.mp3"
            _generate_silence(pause_s, sil)
            concat_parts.append(sil)
            total_silence += pause_s

    if not concat_parts:
        raise RuntimeError("No clips assembled — check sentence bank")

    # Concat
    concat_list = work / "concat.txt"
    with open(concat_list, "w") as f:
        for p in concat_parts:
            f.write(f"file '{p}'\n")

    voice = work / "voice.mp3"
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
                    "-c:a", "libmp3lame", "-b:a", "192k", str(voice)],
                   capture_output=True, timeout=30)

    total_dur = total_speech + total_silence

    if not include_ambient:
        import shutil
        shutil.copy2(voice, out_path)
    else:
        # Mix with ambient
        amb = REPO_ROOT / "assets" / "music_bank" / "generated" / "amb_001.mp3"
        if amb.is_file():
            loops = max(1, int(total_dur / 30) + 1)
            music = work / "music.mp3"
            subprocess.run([FF, "-y", "-stream_loop", str(loops), "-i", str(amb),
                            "-af", f"volume=0.15,afade=t=in:st=0:d=5,afade=t=out:st={max(0,total_dur-5)}:d=5",
                            "-t", str(round(total_dur + 2)),
                            "-c:a", "libmp3lame", "-b:a", "128k", str(music)],
                           capture_output=True, timeout=15)

            out_path.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run([FF, "-y", "-i", str(voice), "-i", str(music),
                            "-filter_complex",
                            "[0:a]volume=1.0[v];[1:a]volume=0.15[m];[v][m]amix=inputs=2:duration=first[out]",
                            "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k", str(out_path)],
                           capture_output=True, timeout=15)
        else:
            import shutil
            shutil.copy2(voice, out_path)

    # Cleanup work dir
    for f in work.glob("*"):
        f.unlink(missing_ok=True)
    work.rmdir()

    return {
        "total_duration_s": round(total_dur, 1),
        "speech_s": round(total_speech, 1),
        "silence_s": round(total_silence, 1),
        "speech_ratio": round(total_speech / max(1, total_dur), 2),
        "sentences_matched": matched,
        "sentences_missed": missed,
    }


# ── Grief exercise definition (pre-written, reusable) ──────────────

GRIEF_HEALTHCARE_V01 = [
    # Intro
    {"text": "Close your eyes.", "pause_s": 4, "section": "intro"},
    {"text": "Take a breath.", "pause_s": 4, "section": "intro"},
    {"text": "You are safe here.", "pause_s": 5, "section": "intro"},
    {"text": "Nothing needs to happen right now.", "pause_s": 5, "section": "intro"},
    # Desc
    {"text": "You lost someone.", "pause_s": 4, "section": "desc"},
    {"text": "The pain is real.", "pause_s": 5, "section": "desc"},
    {"text": "You don't need to fix it.", "pause_s": 4, "section": "desc"},
    # Exercise
    {"text": "Feel your body.", "pause_s": 5, "section": "exercise"},
    {"text": "Where is the weight.", "pause_s": 6, "section": "exercise"},
    {"text": "Your chest.", "pause_s": 5, "section": "exercise"},
    {"text": "Your throat.", "pause_s": 5, "section": "exercise"},
    {"text": "Put your hand there.", "pause_s": 8, "section": "exercise"},
    {"text": "Hold it.", "pause_s": 10, "section": "exercise"},
    {"text": "Cry if you need to.", "pause_s": 8, "section": "exercise"},
    {"text": "That is allowed.", "pause_s": 8, "section": "exercise"},
    # Integration
    {"text": "You showed up.", "pause_s": 4, "section": "integration"},
    {"text": "That took courage.", "pause_s": 5, "section": "integration"},
    {"text": "There is no rush.", "pause_s": 6, "section": "integration"},
    {"text": "When you are ready, open your eyes.", "pause_s": 5, "section": "integration"},
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Assemble practice from sentence bank")
    ap.add_argument("-o", "--output", required=True, type=Path)
    ap.add_argument("--exercise", type=Path, help="YAML exercise definition file")
    ap.add_argument("--preset", default="grief_healthcare_v01", help="Built-in preset name")
    ap.add_argument("--tempo", type=float, default=0.82)
    ap.add_argument("--warmth", type=float, default=3)
    ap.add_argument("--no-ambient", action="store_true")
    args = ap.parse_args()

    if args.exercise and args.exercise.is_file():
        sections = yaml.safe_load(args.exercise.read_text())
        if isinstance(sections, dict):
            sections = sections.get("sections", [])
    else:
        presets = {"grief_healthcare_v01": GRIEF_HEALTHCARE_V01}
        sections = presets.get(args.preset, GRIEF_HEALTHCARE_V01)

    print(f"Assembling {len(sections)} sections from sentence bank...", flush=True)
    stats = assemble_practice(sections, args.output, tempo=args.tempo,
                              warmth=args.warmth, include_ambient=not args.no_ambient)

    print(f"\nDone: {args.output}", flush=True)
    print(f"  Duration: {stats['total_duration_s']}s ({stats['total_duration_s']/60:.1f}min)", flush=True)
    print(f"  Speech: {stats['speech_ratio']:.0%} voice / {1-stats['speech_ratio']:.0%} silence", flush=True)
    print(f"  Bank: {stats['sentences_matched']} matched, {stats['sentences_missed']} missed", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
