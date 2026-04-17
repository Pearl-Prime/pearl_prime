#!/usr/bin/env python3
"""Flip weekly manga lane: ``image_backend: replay`` → ``comfyui`` and ubuntu → self-hosted runner."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _replace_once(path: Path, old: str, new: str) -> bool:
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise ValueError(f"pattern not found in {path}:\n{old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("updated", path)
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--backend", default="comfyui")
    ap.add_argument(
        "--weekly-runs-on-line",
        default="    runs-on: [self-hosted, pearl-star-gpu]",
        help="Replacement line for weekly manga_rollout job (leading spaces included)",
    )
    args = ap.parse_args()

    try:
        cfg = REPO_ROOT / "config" / "weekly_rollout" / "manga_rollout.yaml"
        _replace_once(cfg, "image_backend: replay", f"image_backend: {args.backend}")

        weekly = REPO_ROOT / ".github" / "workflows" / "weekly-manga-rollout.yml"
        _replace_once(
            weekly,
            "  manga_rollout:\n    runs-on: ubuntu-latest",
            f"  manga_rollout:\n{args.weekly_runs_on_line}",
        )
    except (FileNotFoundError, ValueError) as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
