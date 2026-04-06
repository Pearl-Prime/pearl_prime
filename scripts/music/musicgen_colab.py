#!/usr/bin/env python3
"""MusicGen base-track generator — intended for Google Colab (free T4 GPU).

**400 base tracks workflow**
1. On your laptop (repo root): `python3 scripts/music/export_musicgen_manifest.py`
2. Upload `artifacts/music/musicgen_manifest.jsonl` to Colab (same folder as this script).
3. Colab: Runtime → T4 GPU, run `!pip install -q audiocraft soundfile`, then paste/run this file.

Outputs WAVs under `music_bank/base/` (e.g. `base_001.wav`). Zip and download, then place under
`assets/music_bank/base/` in the repo, convert to MP3 if you want smaller files, run
`python3 scripts/music/build_music_index.py`.

MIT license on code; MusicGen weights: check Meta license for your use case.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# ── Colab deps (uncomment in notebook if needed) ──
# !pip install -q audiocraft soundfile

from audiocraft.data.audio import audio_write  # noqa: E402
from audiocraft.models import MusicGen  # noqa: E402
import torch  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_MANIFEST = Path("musicgen_manifest.jsonl")
FALLBACK_MANIFEST = REPO_ROOT / "artifacts" / "music" / "musicgen_manifest.jsonl"


def _manifest_path() -> Path:
    env = os.environ.get("MUSICGEN_MANIFEST", "").strip()
    if env:
        return Path(env)
    if DEFAULT_MANIFEST.is_file():
        return DEFAULT_MANIFEST
    return FALLBACK_MANIFEST

OUTPUT_DIR = Path("music_bank") / "base"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _load_jobs() -> list[dict[str, str]]:
    path = _manifest_path()
    if not path.is_file():
        print(
            "No manifest. In Colab, upload musicgen_manifest.jsonl from "
            "scripts/music/export_musicgen_manifest.py output.",
            file=sys.stderr,
        )
        return []
    jobs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        jobs.append(json.loads(line))
    return jobs


def main() -> int:
    jobs = _load_jobs()
    if not jobs:
        return 1

    print("Loading MusicGen-small...")
    model = MusicGen.get_pretrained("facebook/musicgen-small")
    model.set_generation_params(
        duration=30,
        temperature=1.0,
        top_k=250,
        cfg_coef=3.0,
    )

    for job in jobs:
        jid = job["id"]
        prompt = job["prompt"]
        out_path = OUTPUT_DIR / jid
        wav_file = OUTPUT_DIR / f"{jid}.wav"
        if wav_file.is_file():
            print(f"  {jid}: cached")
            continue
        print(f"  Generating {jid}...", end=" ", flush=True)
        try:
            wav = model.generate([prompt])
            audio_write(str(out_path), wav[0].cpu(), model.sample_rate, strategy="loudness")
            print(f"OK ({wav_file.stat().st_size // 1024}KB)")
        except Exception as e:
            print(f"FAILED: {e}")

    n = sum(1 for _ in OUTPUT_DIR.glob("*.wav"))
    print(f"\nDone! {n} wav files in {OUTPUT_DIR}/")

    # Optional MP3 (ffmpeg in Colab)
    if os.environ.get("MUSICGEN_EXPORT_MP3", "").lower() in ("1", "true", "yes"):
        try:
            subprocess.run(["bash", "-c", "command -v ffmpeg"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("ffmpeg not found; skip MP3")
            return 0
        for wav in OUTPUT_DIR.glob("*.wav"):
            mp3 = wav.with_suffix(".mp3")
            if mp3.is_file():
                continue
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(wav), "-b:a", "128k", str(mp3)],
                capture_output=True,
                timeout=120,
            )
        print("MP3 export complete.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
