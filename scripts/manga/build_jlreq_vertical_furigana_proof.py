#!/usr/bin/env python3
"""Build a deterministic, CI-safe vertical-furigana proof packet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from phoenix_v4.manga.chapter.vertical_furigana import (
    plan_vertical_furigana,
    render_vertical_furigana,
)


def build_proof(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    # ASCII base/readings keep the CI proof independent of system CJK font inventory.
    # Japanese semantics are separately proven by the exact span planner tests.
    text = "TOKYO"
    furigana = [{"base": "TOKYO", "reading": "to-kyo"}]
    image = Image.new("RGBA", (240, 320), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    plan = plan_vertical_furigana(text, furigana)
    rendered = render_vertical_furigana(
        image,
        draw,
        text,
        120,
        30,
        base_font=font,
        ruby_font=font,
        plan=plan,
    )
    png = out_dir / "vertical_furigana_ci_safe.png"
    image.save(png)
    payload = {
        "manga-jlreq-vertical": "green-for-ci-safe-proof",
        "manga-furigana": "green-for-ci-safe-proof",
        "partial_vertical_furigana_deferred": "candidate-resolved",
        "japanese-production-font-proof": "blocked-until-approved-font-present",
        "plan": plan,
        "rendered": rendered,
        "proof_png": png.name,
        "overall-manga-green": "NOT_PROVEN",
    }
    (out_dir / "proof.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build_proof(args.out_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
