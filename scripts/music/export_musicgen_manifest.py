#!/usr/bin/env python3
"""Build a 400-row MusicGen job manifest from config/music/therapeutic_music_prompts.yaml.

Run locally (repo root). Upload the output JSONL to Colab next to the notebook / musicgen_colab.py cell.

    PYTHONPATH=. python3 scripts/music/export_musicgen_manifest.py \\
        --output artifacts/music/musicgen_manifest.jsonl

Each line: {"id": "base_042", "prompt": "..."} — prompts include loop-safe suffixes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    raise SystemExit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_YAML = REPO_ROOT / "config" / "music" / "therapeutic_music_prompts.yaml"

_LOOP_SUFFIX = (
    ", continuous ambient drone texture, seamless loop, no beginning no ending, "
    "no melody resolution, no crescendo, no decrescendo, no drums, no vocals, "
    "no rhythm changes, constant evolving texture, infinite feeling"
)

# Six micro-variations to expand 75 canonical prompts toward 400+ without huge semantic drift.
_MICRO = [
    ", imperceptible stereo field slow breathe",
    ", ultra-slow harmonic partial drift",
    ", deepest sub-layer warmth only",
    ", airy high partials barely present",
    ", midrange focus narrow Q gentle resonance",
    ", phase-coherent mono-safe bed with hint of width",
]


def _collect_prompts(obj: object, out: list[str]) -> None:
    if isinstance(obj, dict):
        p = obj.get("prompt")
        if isinstance(p, str) and p.strip():
            out.append(" ".join(p.split()))
        for v in obj.values():
            _collect_prompts(v, out)
    elif isinstance(obj, list):
        for x in obj:
            _collect_prompts(x, out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Export MusicGen manifest (default 400 jobs)")
    ap.add_argument("--yaml", type=Path, default=DEFAULT_YAML)
    ap.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts" / "music" / "musicgen_manifest.jsonl")
    ap.add_argument("--count", type=int, default=400)
    args = ap.parse_args()

    if not args.yaml.is_file():
        print(f"Missing {args.yaml}", file=sys.stderr)
        return 1

    data = yaml.safe_load(args.yaml.read_text(encoding="utf-8")) or {}
    base: list[str] = []
    _collect_prompts(data, base)
    if not base:
        print("No prompts found in YAML", file=sys.stderr)
        return 1

    jobs: list[dict[str, str]] = []
    n = 0
    while len(jobs) < args.count:
        for p in base:
            suf = _MICRO[n % len(_MICRO)]
            full = p + _LOOP_SUFFIX + suf
            jobs.append({"id": f"base_{len(jobs) + 1:03d}", "prompt": full})
            if len(jobs) >= args.count:
                break
        n += 1
        if n > 2000:
            break

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        for j in jobs:
            f.write(json.dumps(j, ensure_ascii=False) + "\n")

    print(f"Wrote {len(jobs)} jobs → {args.output} (from {len(base)} canonical prompts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
