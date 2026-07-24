#!/usr/bin/env python3
"""Extract keyed candidate frames from a capture clip.

Deterministic (no LLM): keyed sampling for anticipation / impact / follow-through,
near-duplicate clustering, pose-phase tagging stubs.

Default for 5s clips: 8–12 keyed candidates (supply spec §4.2), not uniform dump.

Usage:
  PYTHONPATH=. python3 scripts/manga/video_bank/extract_frames.py \\
    --clip path/to/clip.mp4 --out-dir path/to/candidates --target-count 10
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL import Image

REPO = Path(__file__).resolve().parents[3]

PHASES = ("rest", "anticipation", "impact", "follow_through", "turn")


@dataclass
class FrameCandidate:
    path: str
    frame_index: int
    time_s: float
    phase: str
    cluster_id: int
    kept: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _ffprobe_duration(clip: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(clip),
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    return float(out)


def keyed_timestamps(duration_s: float, target_count: int) -> list[float]:
    """Prefer anticipation / impact / follow-through denser than endpoints."""
    n = max(3, min(int(target_count), 16))
    if duration_s <= 0:
        raise ValueError("clip duration must be > 0")
    # Weighted positions: early rest, anticipation cluster, mid impact, late follow.
    weights = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.92, 0.97]
    if n <= len(weights):
        # pick evenly from weights
        step = len(weights) / n
        idxs = [int(i * step) for i in range(n)]
        fracs = [weights[i] for i in idxs]
    else:
        fracs = [i / (n - 1) for i in range(n)]
    times = [min(duration_s * 0.999, max(0.0, duration_s * f)) for f in fracs]
    # unique-ish
    uniq: list[float] = []
    for t in times:
        if not uniq or abs(t - uniq[-1]) > 1e-3:
            uniq.append(t)
    return uniq


def phase_for_frac(frac: float) -> str:
    if frac < 0.12:
        return "rest"
    if frac < 0.35:
        return "anticipation"
    if frac < 0.55:
        return "impact"
    if frac < 0.80:
        return "follow_through"
    return "turn"


def _extract_one(clip: Path, time_s: float, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{time_s:.4f}",
        "-i",
        str(clip),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(dest),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _mean_rgb(path: Path) -> tuple[float, float, float]:
    im = Image.open(path).convert("RGB").resize((32, 32), Image.Resampling.BILINEAR)
    px = list(im.getdata())
    n = max(len(px), 1)
    r = sum(p[0] for p in px) / n
    g = sum(p[1] for p in px) / n
    b = sum(p[2] for p in px) / n
    return (r, g, b)


def _dist(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def cluster_near_duplicates(
    paths: list[Path],
    *,
    threshold: float = 18.0,
) -> list[int]:
    """Greedy clustering by mean-RGB distance; returns cluster_id per path."""
    means = [_mean_rgb(p) for p in paths]
    centers: list[tuple[float, float, float]] = []
    ids: list[int] = []
    for m in means:
        assigned = None
        for i, c in enumerate(centers):
            if _dist(m, c) <= threshold:
                assigned = i
                break
        if assigned is None:
            assigned = len(centers)
            centers.append(m)
        ids.append(assigned)
    return ids


def extract_frames(
    clip: Path,
    out_dir: Path,
    *,
    target_count: int = 10,
    duration_s: float | None = None,
    ffmpeg_available: bool | None = None,
) -> list[FrameCandidate]:
    if ffmpeg_available is None:
        ffmpeg_available = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None
    if not ffmpeg_available:
        raise RuntimeError("ffmpeg/ffprobe required for extract_frames")

    dur = duration_s if duration_s is not None else _ffprobe_duration(clip)
    times = keyed_timestamps(dur, target_count)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i, t in enumerate(times):
        dest = out_dir / f"frame_{i:03d}.png"
        _extract_one(clip, t, dest)
        paths.append(dest)

    clusters = cluster_near_duplicates(paths)
    # Keep best representative per cluster: prefer impact/anticipation phases.
    best_for_cluster: dict[int, int] = {}
    phase_rank = {p: i for i, p in enumerate(("impact", "anticipation", "follow_through", "rest", "turn"))}
    candidates: list[FrameCandidate] = []
    for i, (path, t) in enumerate(zip(paths, times)):
        frac = t / dur if dur else 0.0
        phase = phase_for_frac(frac)
        cid = clusters[i]
        cand = FrameCandidate(
            path=str(path),
            frame_index=i,
            time_s=round(t, 4),
            phase=phase,
            cluster_id=cid,
            kept=False,
        )
        candidates.append(cand)
        prev = best_for_cluster.get(cid)
        if prev is None:
            best_for_cluster[cid] = i
        else:
            if phase_rank.get(phase, 99) < phase_rank.get(candidates[prev].phase, 99):
                best_for_cluster[cid] = i

    for i in best_for_cluster.values():
        candidates[i].kept = True

    meta = {
        "clip": str(clip),
        "duration_s": dur,
        "target_count": target_count,
        "candidates": [c.to_dict() for c in candidates],
        "kept_count": sum(1 for c in candidates if c.kept),
    }
    (out_dir / "extract_manifest.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    return candidates


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--clip", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--target-count", type=int, default=10)
    ap.add_argument("--duration-s", type=float, default=None, help="Override ffprobe duration")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cands = extract_frames(
            args.clip,
            args.out_dir,
            target_count=args.target_count,
            duration_s=args.duration_s,
        )
    except (RuntimeError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "candidates": len(cands),
                "kept": sum(1 for c in cands if c.kept),
                "out_dir": str(args.out_dir),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
