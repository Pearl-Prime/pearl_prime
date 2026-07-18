#!/usr/bin/env python3
"""Apply 24 channel DNA transforms (FFmpeg) to every base track.

Expects base audio under --base-dir (e.g. assets/music_bank/base/*.mp3).
Reads config/music/brand_music_dna.yaml and writes:

    {output-root}/{ch_xxx}/{original_basename}

Requires ffmpeg on PATH.

    python3 scripts/music/apply_brand_dna_batch.py \\
        --base-dir assets/music_bank/base \\
        --output-dir assets/music_bank/by_brand

Texture overlays from YAML are not mixed here (add a second-pass amix if you place
assets/music_bank/textures/<name>.mp3 files). This pass applies pitch/tempo/EQ/reverb/stereo only.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required", file=sys.stderr)
    raise SystemExit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DNA_PATH = REPO_ROOT / "config" / "music" / "brand_music_dna.yaml"
def _atempo_segments(factor: float) -> list[str]:
    """FFmpeg atempo must be ~0.5–2.0 per stage."""
    parts: list[str] = []
    f = factor
    while f > 2.0:
        parts.append("atempo=2.0")
        f /= 2.0
    while f < 0.5:
        parts.append("atempo=0.5")
        f /= 0.5
    parts.append(f"atempo={f:.6f}")
    return parts


def _build_afilter(dna: dict) -> str:
    st = float(dna["key_offset_semitones"])
    bm = float(dna["bpm_multiplier"])
    pf = 2.0 ** (st / 12.0)
    tempo_comp = bm / pf
    eq = dna["eq_profile"]
    rev = dna["reverb"]
    stereo = dna["stereo"]

    low_f = float(eq["low_freq_hz"])
    low_g = float(eq["low_gain_db"])
    mid_f = float(eq["mid_freq_hz"])
    mid_g = float(eq["mid_gain_db"])
    high_f = float(eq["high_freq_hz"])
    high_g = float(eq["high_gain_db"])

    delay_ms = max(10, int(rev["delay_ms"]))
    decay = float(rev["decay"])
    decay_clamped = min(0.9, max(0.1, decay))
    width = float(stereo["width"])
    balance = float(stereo["balance"])

    chain: list[str] = [
        f"asetrate=44100*{pf:.6f}",
        "aresample=44100",
        *_atempo_segments(tempo_comp),
        f"equalizer=f={low_f}:t=q:w=1.5:g={low_g}",
        f"equalizer=f={mid_f}:t=q:w=1.0:g={mid_g}",
        f"equalizer=f={high_f}:t=q:w=1.5:g={high_g}",
        f"aecho=0.85:{decay_clamped:.2f}:{delay_ms}:{decay_clamped * 0.35:.2f}",
        f"extrastereo,m={width:.3f}",
    ]
    if abs(balance) > 0.001:
        b = balance
        chain.append(
            f"pan=stereo|c0=c0+{b:.3f}*c1|c1=c1+{b:.3f}*c0"
        )

    return ",".join(chain)


def _run_ffmpeg_simple(in_path: Path, out_path: Path, af: str, ffmpeg: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-y", "-i", str(in_path),
        "-af", af,
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=600)


def main() -> int:
    ap = argparse.ArgumentParser(description="Batch-apply brand_music_dna.yaml to base tracks")
    ap.add_argument("--base-dir", type=Path, default=REPO_ROOT / "assets" / "music_bank" / "base")
    ap.add_argument("--output-dir", type=Path, default=REPO_ROOT / "assets" / "music_bank" / "by_brand")
    ap.add_argument("--dna", type=Path, default=DNA_PATH)
    ap.add_argument("--limit-brands", type=int, default=0, help="0 = all 24 channels")
    ap.add_argument("--limit-tracks", type=int, default=0, help="0 = all base tracks")
    ap.add_argument("--ffmpeg", default="ffmpeg")
    args = ap.parse_args()

    if not args.dna.is_file():
        print(f"Missing {args.dna}", file=sys.stderr)
        return 1
    if not args.base_dir.is_dir():
        print(f"Missing base dir {args.base_dir}", file=sys.stderr)
        return 1

    doc = yaml.safe_load(args.dna.read_text(encoding="utf-8")) or {}
    brands: dict[str, dict] = doc.get("brands") or {}
    if not brands:
        print("No brands: in YAML", file=sys.stderr)
        return 1

    tracks = sorted(
        list(args.base_dir.glob("*.mp3"))
        + list(args.base_dir.glob("*.wav"))
        + list(args.base_dir.glob("*.flac")),
    )
    if args.limit_tracks:
        tracks = tracks[: args.limit_tracks]
    if not tracks:
        print(f"No audio files in {args.base_dir}", file=sys.stderr)
        return 1

    ch_keys = sorted(brands.keys(), key=lambda k: (len(k), k))
    if args.limit_brands:
        ch_keys = ch_keys[: args.limit_brands]

    for ch in ch_keys:
        dna = brands[ch]
        af = _build_afilter(dna)

        for src in tracks:
            rel = src.name
            dst = args.output_dir / ch / rel
            if dst.is_file():
                continue
            try:
                _run_ffmpeg_simple(src, dst, af, args.ffmpeg)
                print(f"OK {ch} ← {rel}")
            except subprocess.CalledProcessError as e:
                print(f"FAIL {ch} {rel}: {e.stderr.decode(errors='replace')[:400]}", file=sys.stderr)

    print(f"\nDone. Output under {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
