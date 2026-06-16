#!/usr/bin/env python3
"""ToonOut side-by-side test against v4_b_test L2 renders.

Per docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md §13 Phase 1 step 5/6.
Tier 1 (operator-present). No LLM calls. Per CLAUDE.md tier policy.

Usage:
    python3 scripts/manga/v4_toonout_side_by_side.py

Outputs cutouts at:
    artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/
        experiments/v4_toonout_test/<source>_alpha_toonout_v1.png

Compare visually against existing rembg cutouts at
    artifacts/manga/.../experiments/v4_b_test/<source>_alpha_<rembg-model>_v2.png
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "manga"))
from manga_cutout_toonout import toonout_cutout  # noqa: E402

ARTIFACTS = REPO / "artifacts" / "manga" / "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
SRC_DIR = ARTIFACTS / "experiments" / "v4_b_test"
OUT_DIR = ARTIFACTS / "experiments" / "v4_toonout_test"
SOURCES = [
    "ep001_003_L2_v4btest.png",
    "ep001_006_L2_v4btest2_face_only.png",
    "ep001_006_L2_v4btest3_tight_framing.png",
    "ep001_006_L2_v4btest4_breathing_room.png",
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"=== ToonOut side-by-side test ===")
    print(f"  source: {SRC_DIR}")
    print(f"  output: {OUT_DIR}")
    for name in SOURCES:
        src = SRC_DIR / name
        if not src.is_file():
            print(f"  SKIP {name} (missing)")
            continue
        dst = OUT_DIR / (src.stem + "_alpha_toonout_v1.png")
        rgba = toonout_cutout(Image.open(src))
        rgba.save(dst)
        alpha = rgba.split()[-1]
        opaque = sum(1 for px in alpha.getdata() if px > 250)
        bbox = rgba.getbbox()
        print(f"  {dst.relative_to(REPO)}  opaque_px={opaque}  bbox={bbox}")
    print(f"\nReview in Finder: open {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
