#!/usr/bin/env python3
"""Build music bank index from audio files on disk.

Scans assets/music_bank/ for MP3/WAV files, extracts duration via ffprobe,
and writes index.yaml with metadata for pipeline matching.

Usage:
    python3 scripts/music/build_music_index.py [--bank-dir assets/music_bank]
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _ffprobe_duration(path: Path) -> float:
    """Get audio duration in seconds via ffprobe."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=10,
        )
        return float(r.stdout.strip()) if r.returncode == 0 else 0.0
    except Exception:
        return 0.0


def _mood_from_category(category: str) -> list[str]:
    """Assign default moods based on category folder name."""
    return {
        "ambient": ["calm", "contemplative", "meditative"],
        "lofi": ["warm", "relaxed", "gentle"],
        "gentle": ["warm", "soft", "peaceful"],
        "cinematic": ["dramatic", "inspiring", "emotional"],
        "nature": ["natural", "grounding", "peaceful"],
        "generated": ["calm", "ambient", "therapeutic"],
    }.get(category, ["calm"])


def _topic_affinity(category: str) -> list[str]:
    return {
        "ambient": ["anxiety", "sleep_anxiety", "somatic_healing", "depression"],
        "lofi": ["overthinking", "burnout", "boundaries", "self_worth"],
        "gentle": ["grief", "compassion_fatigue", "courage"],
        "cinematic": ["imposter_syndrome", "courage", "self_worth"],
        "nature": ["somatic_healing", "anxiety", "burnout"],
        "generated": ["anxiety", "burnout", "depression", "somatic_healing"],
    }.get(category, ["anxiety"])


def build_index(bank_dir: Path) -> dict:
    tracks = []
    for ext in ("*.mp3", "*.wav", "*.ogg", "*.flac"):
        for f in sorted(bank_dir.rglob(ext)):
            rel = f.relative_to(bank_dir)
            category = rel.parts[0] if len(rel.parts) > 1 else "uncategorized"
            track_id = f.stem

            dur = _ffprobe_duration(f)
            if dur < 5:
                continue  # skip very short files

            tracks.append({
                "id": track_id,
                "file": str(rel),
                "source": "generated" if category == "generated" else "free_library",
                "license": "cc0" if category != "generated" else "mit_musicgen",
                "attribution": None,
                "duration_s": round(dur, 1),
                "mood": _mood_from_category(category),
                "energy": "low" if category in ("ambient", "gentle", "nature") else "medium",
                "topic_affinity": _topic_affinity(category),
                "has_vocals": False,
                "loop_friendly": True,
                "category": category,
            })

    return {"version": 1, "track_count": len(tracks), "tracks": tracks}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Build music bank index")
    ap.add_argument("--bank-dir", type=Path, default=REPO_ROOT / "assets" / "music_bank")
    args = ap.parse_args()

    if not args.bank_dir.is_dir():
        print(f"Bank dir not found: {args.bank_dir}", file=sys.stderr)
        return 1

    index = build_index(args.bank_dir)

    out = args.bank_dir / "index.yaml"
    if yaml:
        out.write_text(yaml.dump(index, default_flow_style=False, allow_unicode=True), encoding="utf-8")
    else:
        out.with_suffix(".json").write_text(json.dumps(index, indent=2), encoding="utf-8")
        out = out.with_suffix(".json")

    print(f"Indexed {index['track_count']} tracks → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
