#!/usr/bin/env python3
"""
Generate benchmark MP3s for Brand Admin onboarding using Microsoft Edge TTS (edge-tts).
No API key required. Optional: ELEVENLABS_API_KEY + elevenlabs package for production voices later.

Outputs under brand-wizard-app/public/onboarding/audio/ (served on Cloudflare Pages).

Usage:
  pip install -r scripts/onboarding/requirements-tts.txt
  python3 scripts/onboarding/generate_voice_benchmark_audio.py
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "config" / "narrators" / "narrator_registry.yaml"
PASSAGES = ROOT / "config" / "narrators" / "voice_benchmark_passages.yaml"
OUT_DIR = ROOT / "brand-wizard-app" / "public" / "onboarding" / "audio"


def _load_yaml(path: Path) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


async def _edge_tts_save(text: str, voice: str, out_path: Path) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text.strip(), voice)
    await communicate.save(str(out_path))


async def main_async() -> int:
    if not REGISTRY.exists():
        print("Missing narrator registry", file=sys.stderr)
        return 1
    if not PASSAGES.exists():
        print("Missing voice_benchmark_passages.yaml", file=sys.stderr)
        return 1

    reg = _load_yaml(REGISTRY)
    passages_doc = _load_yaml(PASSAGES)
    narrators = reg.get("narrators") or {}
    locale = "en-US"
    passages = (passages_doc.get("locales") or {}).get(locale) or {}
    if not passages:
        print(f"No passages for locale {locale}", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    jobs: list[tuple[str, str, Path]] = []

    # Comparison set: same comfort passage, three Edge voices
    comfort = passages.get("comfort", "").strip()
    for nid in ("voice_regulating_female", "voice_warm_male", "voice_direct_authority"):
        entry = narrators.get(nid) or {}
        voice = entry.get("edge_tts_voice")
        if not voice:
            print(f"Skip {nid}: no edge_tts_voice", file=sys.stderr)
            continue
        fn = f"voice_cmp_comfort_{nid}.mp3"
        jobs.append((comfort, voice, OUT_DIR / fn))

    # Benchmark set: five passages, one voice (Jenny)
    jenny = (narrators.get("voice_regulating_female") or {}).get("edge_tts_voice")
    if jenny:
        for key in ("comfort", "authority", "instruction", "hope", "cta"):
            text = (passages.get(key) or "").strip()
            if not text:
                continue
            fn = f"voice_bench_{key}_jenny.mp3"
            jobs.append((text, jenny, OUT_DIR / fn))

    if not jobs:
        print("No generation jobs", file=sys.stderr)
        return 1

    for text, voice, path in jobs:
        print(f"Writing {path.name} voice={voice!r} …")
        await _edge_tts_save(text, voice, path)

    print(f"Done — {len(jobs)} file(s) in {OUT_DIR.relative_to(ROOT)}")
    return 0


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    raise SystemExit(main())
