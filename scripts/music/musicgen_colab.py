#!/usr/bin/env python3
"""MusicGen ambient loop generator — run on Google Colab (free T4 GPU).

Copy this script to a Colab notebook cell and run. Generates 30-second
ambient loops per brand, saves to Google Drive.

Usage (in Colab):
    1. Open Google Colab (colab.research.google.com)
    2. Runtime → Change runtime type → T4 GPU
    3. Paste this entire script into a cell
    4. Run the cell
    5. Download the generated MP3s from the output directory

The small model (300M params) runs on free Colab T4 (16GB VRAM).
Each generation takes ~15-30 seconds. 10 tracks = ~5 minutes.
MIT license on code, model weights are CC-BY-NC 4.0 for commercial
use verification (small model may have more permissive terms).
"""

# ── Install dependencies (Colab only) ──
# !pip install -q audiocraft soundfile

from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import torch
from pathlib import Path

# ── Configuration ──
OUTPUT_DIR = Path("music_bank")
OUTPUT_DIR.mkdir(exist_ok=True)

# Load MusicGen small model (300M params, fits free Colab T4)
print("Loading MusicGen-small...")
model = MusicGen.get_pretrained("facebook/musicgen-small")
model.set_generation_params(
    duration=30,        # 30 seconds per track
    temperature=1.0,    # creativity level
    top_k=250,          # sampling diversity
    cfg_coef=3.0,       # classifier-free guidance
)

# ── Brand-specific prompts ──
# Each brand gets its own mood/style for unique music identity

# ── CRITICAL: All prompts must produce SEAMLESS CONTINUOUS AMBIENT ──
# No start, no end, no melody resolution, no crescendo, no decrescendo.
# Just an infinite-feeling texture that can loop without any audible join.
_LOOP_SUFFIX = (
    ", continuous ambient drone texture, seamless loop, no beginning no ending, "
    "no melody resolution, no crescendo, no decrescendo, no drums, no vocals, "
    "no rhythm changes, constant evolving texture, infinite feeling"
)

BRAND_PROMPTS = {
    "stillness_press": [
        "warm synthesizer pad drone, slow evolving harmonics, breathing room atmosphere, 432Hz tuning" + _LOOP_SUFFIX,
        "gentle piano sustain with deep reverb wash, notes dissolving into ambient space, contemplative" + _LOOP_SUFFIX,
        "zen water and wind chime texture, natural ambient field recording with soft pad layer" + _LOOP_SUFFIX,
        "deep warm bass hum with soft overtones, therapeutic 6 BPM breath pacing embedded" + _LOOP_SUFFIX,
        "morning mist strings and harp harmonics, ethereal and weightless, slow tonal drift" + _LOOP_SUFFIX,
    ],
    "cognitive_clarity": [
        "clean electronic pad wash, bright focused energy, alpha wave frequency undertone" + _LOOP_SUFFIX,
        "crystal clear piano harmonics with spacious reverb, structured and calm" + _LOOP_SUFFIX,
        "subtle binaural texture, warm synth foundation, mental clarity atmosphere" + _LOOP_SUFFIX,
        "glass-like tones with soft granular texture, precision and space, clear thinking" + _LOOP_SUFFIX,
        "gentle electronic hum with slow filter sweep, productive calm energy" + _LOOP_SUFFIX,
    ],
    "norcal_dharma": [
        "singing bowl resonance layered with deep meditation drone, sacred space" + _LOOP_SUFFIX,
        "temple bell decay stretched into infinite reverb, incense smoke atmosphere" + _LOOP_SUFFIX,
        "earth frequency deep bass with subtle overtone singing, grounding" + _LOOP_SUFFIX,
        "soft sitar drone with tanpura texture, warm devotional atmosphere" + _LOOP_SUFFIX,
        "mountain wind through pine trees with distant monastery bell, solitude" + _LOOP_SUFFIX,
    ],
    "zh_brands": [
        "guzheng harmonics with deep reverb, chinese ambient texture, contemplative" + _LOOP_SUFFIX,
        "flowing water over stones with distant bamboo flute sustain, tai chi energy" + _LOOP_SUFFIX,
        "warm erhu long bow sustain dissolving into pad, chinese healing atmosphere" + _LOOP_SUFFIX,
        "deep qigong breathing rhythm embedded in warm synth foundation, energy flow" + _LOOP_SUFFIX,
        "stone garden atmosphere, water drip resonance, zen minimalist chinese" + _LOOP_SUFFIX,
    ],
    "ja_brands": [
        "koto harmonics sustained with infinite reverb, zen garden wabi sabi atmosphere" + _LOOP_SUFFIX,
        "forest ambient with distant shamisen sustain, shinrin yoku bath in sound" + _LOOP_SUFFIX,
        "onsen steam atmosphere with warm water resonance, deep soaking relaxation" + _LOOP_SUFFIX,
        "soft piano with vinyl warmth texture, japanese lo-fi ambient, cherry blossom" + _LOOP_SUFFIX,
        "iyashikei anime healing background, gentle warmth and comfort, safe space" + _LOOP_SUFFIX,
    ],
}

# ── Generate tracks ──
for brand_id, prompts in BRAND_PROMPTS.items():
    brand_dir = OUTPUT_DIR / brand_id
    brand_dir.mkdir(exist_ok=True)

    for i, prompt in enumerate(prompts):
        track_id = f"{brand_id}_{i + 1:03d}"
        out_path = brand_dir / track_id

        if (brand_dir / f"{track_id}.wav").exists():
            print(f"  {track_id}: cached")
            continue

        print(f"  Generating {track_id}...", end=" ", flush=True)
        try:
            wav = model.generate([prompt])
            audio_write(str(out_path), wav[0].cpu(), model.sample_rate, strategy="loudness")
            print(f"OK ({(brand_dir / f'{track_id}.wav').stat().st_size // 1024}KB)")
        except Exception as e:
            print(f"FAILED: {e}")

print(f"\nDone! Files in {OUTPUT_DIR}/")
print(f"Total tracks: {sum(1 for f in OUTPUT_DIR.rglob('*.wav'))}")

# ── Optional: Convert WAV to MP3 (needs ffmpeg in Colab) ──
# !apt-get install -qq ffmpeg > /dev/null 2>&1
# import subprocess
# for wav in OUTPUT_DIR.rglob("*.wav"):
#     mp3 = wav.with_suffix(".mp3")
#     subprocess.run(["ffmpeg", "-y", "-i", str(wav), "-b:a", "128k", str(mp3)],
#                   capture_output=True)
#     print(f"  {wav.stem}.mp3")

# ── Optional: Download from Colab ──
# from google.colab import files
# import shutil
# shutil.make_archive("music_bank", "zip", OUTPUT_DIR)
# files.download("music_bank.zip")
