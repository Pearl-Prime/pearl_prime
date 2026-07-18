#!/usr/bin/env python3
"""
Build Therapeutic Sound Effects Bank — download CC0 sounds from Freesound.org.

Downloads, normalizes, and indexes therapeutic SFX for the video pipeline.
All sounds are CC0 licensed (no attribution required).

Usage:
    # Download from Freesound API (requires API key)
    python scripts/video/build_sfx_bank.py --api-key $FREESOUND_API_KEY

    # Generate synthetic placeholder SFX (no API key needed)
    python scripts/video/build_sfx_bank.py --synthetic

    # Verify existing bank
    python scripts/video/build_sfx_bank.py --verify
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import subprocess
import sys
import wave
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SFX_BANK_DIR = REPO_ROOT / "assets" / "sfx_bank"
SFX_INDEX_PATH = REPO_ROOT / "config" / "video" / "sfx_bank_index.yaml"

try:
    import yaml
except ImportError:
    yaml = None

try:
    import requests
except ImportError:
    requests = None

# ── Freesound.org API ─────────────────────────────────────────────
FREESOUND_BASE = "https://freesound.org/apiv2"

# Search queries per category (CC0 license = license:"Creative Commons 0")
CATEGORY_QUERIES = {
    "nature_ambient": [
        "rain gentle ambient",
        "ocean waves calm",
        "forest birds morning",
        "wind soft breeze",
        "stream water flowing",
        "night crickets peaceful",
    ],
    "body_somatic": [
        "breathing slow meditation",
        "heartbeat resting calm",
        "breath deep relaxation",
    ],
    "resonant_tone": [
        "singing bowl meditation",
        "wind chimes gentle",
        "temple bell deep",
        "kalimba melody calm",
        "tingsha bells meditation",
    ],
    "transition_marker": [
        "whoosh soft air",
        "page turn paper",
        "sweep gentle transition",
        "shimmer sparkle subtle",
    ],
    "silence_breath": [
        "tone fade ambient",
        "room tone quiet",
        "pad soft atmospheric",
        "resonance decay sustain",
    ],
    "tension_release": [
        "hum warm drone",
        "thunder distant gentle",
        "chime resolve bright",
        "drone soft ambient",
    ],
}


def _generate_sine_wav(path: Path, frequency_hz: float, duration_s: float, amplitude: float = 0.3) -> None:
    """Generate a simple sine wave WAV file for synthetic SFX."""
    sample_rate = 48000
    n_samples = int(sample_rate * duration_s)
    path.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = i / sample_rate
            # Apply fade in/out envelope
            env = 1.0
            fade_s = min(2.0, duration_s * 0.1)
            if t < fade_s:
                env = t / fade_s
            elif t > duration_s - fade_s:
                env = (duration_s - t) / fade_s
            value = amplitude * env * math.sin(2 * math.pi * frequency_hz * t)
            data = struct.pack("<h", int(value * 32767))
            wf.writeframes(data)


def _wav_to_mp3(wav_path: Path, mp3_path: Path) -> bool:
    """Convert WAV to MP3 via FFmpeg."""
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame",
             "-b:a", "192k", "-ar", "48000", str(mp3_path)],
            capture_output=True, check=True, timeout=30,
        )
        wav_path.unlink()
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # No ffmpeg — keep WAV as fallback
        mp3_path.write_bytes(wav_path.read_bytes())
        return False


def build_synthetic_bank() -> dict:
    """Generate synthetic placeholder SFX (no API key needed)."""
    if not yaml:
        print("pyyaml required")
        sys.exit(1)

    index = yaml.safe_load(SFX_INDEX_PATH.read_text(encoding="utf-8")) or {}
    categories = index.get("categories") or {}
    generated = {}

    for cat_id, cat_data in categories.items():
        freq_range = cat_data.get("frequency_range_hz", [200, 1000])
        base_freq = (freq_range[0] + freq_range[1]) / 2
        variants = cat_data.get("variants") or []

        for i, variant in enumerate(variants):
            file_rel = variant["file"]
            mp3_path = SFX_BANK_DIR / file_rel
            wav_path = mp3_path.with_suffix(".wav")

            if mp3_path.exists():
                continue

            mp3_path.parent.mkdir(parents=True, exist_ok=True)
            duration = variant.get("duration_s", 10)
            # Vary frequency slightly per variant
            freq = base_freq + (i * 20)

            _generate_sine_wav(wav_path, freq, duration, amplitude=0.2)
            _wav_to_mp3(wav_path, mp3_path)
            generated[variant["id"]] = str(mp3_path)
            print(f"  ✓ {variant['id']} → {file_rel} ({duration}s, {freq:.0f}Hz)")

    return generated


def verify_bank() -> dict:
    """Verify all indexed SFX files exist."""
    if not yaml:
        print("pyyaml required")
        sys.exit(1)

    index = yaml.safe_load(SFX_INDEX_PATH.read_text(encoding="utf-8")) or {}
    categories = index.get("categories") or {}
    results = {"total": 0, "found": 0, "missing": []}

    for cat_id, cat_data in categories.items():
        for variant in cat_data.get("variants") or []:
            results["total"] += 1
            file_path = SFX_BANK_DIR / variant["file"]
            if file_path.exists():
                results["found"] += 1
            else:
                results["missing"].append(variant["id"])

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Build therapeutic SFX bank")
    parser.add_argument("--api-key", help="Freesound.org API key")
    parser.add_argument("--synthetic", action="store_true", help="Generate synthetic placeholder SFX")
    parser.add_argument("--verify", action="store_true", help="Verify existing bank completeness")
    parser.add_argument("--output", default=str(SFX_BANK_DIR), help="Output directory")
    args = parser.parse_args()

    if args.verify:
        results = verify_bank()
        print(f"SFX Bank: {results['found']}/{results['total']} files present")
        if results["missing"]:
            print(f"Missing: {', '.join(results['missing'][:10])}")
        return 0 if not results["missing"] else 1

    if args.synthetic:
        print("Generating synthetic SFX bank (placeholder sounds)...")
        generated = build_synthetic_bank()
        print(f"Generated {len(generated)} SFX files")

        # Verify
        results = verify_bank()
        print(f"Bank: {results['found']}/{results['total']} files present")
        return 0

    if args.api_key:
        print("Freesound API download not yet implemented — use --synthetic for now")
        # TODO: Implement Freesound API download
        # 1. Search per category using CATEGORY_QUERIES
        # 2. Filter: license=CC0, duration 5-60s, rating >3
        # 3. Download preview MP3s (no OAuth needed)
        # 4. Normalize to 48kHz, -24 LUFS via FFmpeg
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
