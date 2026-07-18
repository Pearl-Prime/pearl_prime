#!/usr/bin/env python3
"""Emit pytest paths for manga bubble regression (only files that exist)."""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CANDIDATES = (
    "tests/test_lettering_spec_v2.py",
    "tests/test_bubble_render.py",
    "tests/test_manga_dialogue_gates.py",
    "tests/test_manga_bubble_e2e.py",
    "tests/test_chapter_production_bubble.py",
)


def main() -> None:
    paths = [str(REPO_ROOT / p) for p in CANDIDATES if (REPO_ROOT / p).is_file()]
    if not paths:
        print("tests/test_manga_lettering_from_script.py")
        return
    print(" ".join(paths))


if __name__ == "__main__":
    main()
