#!/usr/bin/env python3
"""Generate ASS subtitle file with karaoke-style word highlighting.

Takes word-level alignment JSON (from align_transcript.py) and produces
an ASS subtitle file where each phrase appears with word-by-word color
transitions — matching the Descript audiobook video style.

Usage:
    python3 scripts/video/generate_karaoke_ass.py \
        --alignment alignment.json \
        --style default \
        --format long \
        -o karaoke.ass
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# ASS time format: H:MM:SS.cc (centiseconds)
def _ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    cs = int((s - int(s)) * 100)
    return f"{h}:{m:02d}:{int(s):02d}.{cs:02d}"


def _load_style_config(style_name: str) -> dict:
    cfg_path = REPO_ROOT / "config" / "video" / "audiobook_style.yaml"
    if cfg_path.is_file():
        cfg = yaml.safe_load(cfg_path.read_text())
        return cfg.get("styles", {}).get(style_name, cfg["styles"]["default"])
    # Hardcoded fallback
    return {
        "font_family": "Georgia",
        "font_size_16_9": 72,
        "font_size_9_16": 52,
        "text_color": "#FFFFFF",
        "text_color_past": "#666666",
        "text_margin_x_pct": 8,
        "text_margin_y_pct": 8,
        "max_words_per_screen": 6,
    }


def _hex_to_ass_color(hex_color: str) -> str:
    """Convert #RRGGBB to ASS &HBBGGRR& format."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"&H00{b:02X}{g:02X}{r:02X}"


def chunk_words(words: list[dict], max_per_screen: int = 6) -> list[list[dict]]:
    """Split words into display phrases (chunks shown together on screen).

    Rules:
    - Max max_per_screen words per chunk
    - Break at sentence boundaries (period, question mark, exclamation)
    - Break at clause boundaries (comma, semicolon, dash) if chunk is getting long
    """
    chunks = []
    current = []

    for w in words:
        current.append(w)
        text = w["word"]

        # Force break at sentence end
        is_sentence_end = text.rstrip().endswith((".", "!", "?", '."', '!"', '?"'))
        is_clause_break = text.rstrip().endswith((",", ";", "—", " —"))

        if is_sentence_end or (is_clause_break and len(current) >= 4) or len(current) >= max_per_screen:
            chunks.append(current)
            current = []

    if current:
        chunks.append(current)

    return chunks


def generate_ass(
    words: list[dict],
    style_name: str = "default",
    format_key: str = "long",
    resolution: tuple[int, int] = (1920, 1080),
) -> str:
    """Generate ASS subtitle content with karaoke timing."""
    style = _load_style_config(style_name)
    w, h = resolution

    font_size = style["font_size_16_9"] if w >= h else style["font_size_9_16"]
    margin_x = int(w * style["text_margin_x_pct"] / 100)
    margin_y = int(h * style["text_margin_y_pct"] / 100)
    max_words = style["max_words_per_screen"]

    primary_color = _hex_to_ass_color(style["text_color"])
    past_color = _hex_to_ass_color(style["text_color_past"])

    # ASS header
    header = f"""[Script Info]
Title: Audiobook Karaoke
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style["font_family"]},{font_size},{primary_color},&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,{margin_x},{margin_x},{margin_y},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    chunks = chunk_words(words, max_words)
    events = []

    for chunk in chunks:
        if not chunk:
            continue

        start_time = chunk[0]["start"]
        end_time = chunk[-1]["end"] + 0.3  # small linger after last word

        # Build karaoke text: each word gets \k tag (duration in centiseconds)
        # Words start in past_color, transition to primary_color via \k
        parts = []
        for i, word in enumerate(chunk):
            word_dur_cs = max(1, int((word["end"] - word["start"]) * 100))

            if i == 0:
                # Gap from chunk start to first word
                gap_cs = max(0, int((word["start"] - start_time) * 100))
                if gap_cs > 0:
                    parts.append(f"{{\\kf{gap_cs}}}")

            parts.append(f"{{\\kf{word_dur_cs}}}{word['word']} ")

            # Gap between words
            if i < len(chunk) - 1:
                gap = chunk[i + 1]["start"] - word["end"]
                if gap > 0.05:
                    gap_cs = int(gap * 100)
                    parts.append(f"{{\\kf{gap_cs}}}")

        karaoke_text = "".join(parts).rstrip()

        # Use \1c for highlight color (primary) and \2c for pre-highlight (past)
        # \kf = smooth fill from secondary to primary
        line = (
            f"{{\\1c{primary_color}\\2c{past_color}}}"
            f"{karaoke_text}"
        )

        events.append(
            f"Dialogue: 0,{_ass_time(start_time)},{_ass_time(end_time)},Default,,0,0,0,,{line}"
        )

    return header + "\n".join(events) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate karaoke ASS subtitles")
    ap.add_argument("--alignment", required=True, type=Path, help="Word alignment JSON")
    ap.add_argument("--style", default="default", help="Visual style preset")
    ap.add_argument("--format", default="long", choices=["long", "short"], help="Video format")
    ap.add_argument("--width", type=int, default=None)
    ap.add_argument("--height", type=int, default=None)
    ap.add_argument("-o", "--output", type=Path, required=True, help="Output .ass file")
    args = ap.parse_args()

    data = json.loads(args.alignment.read_text())
    words = data["words"]

    if args.width and args.height:
        resolution = (args.width, args.height)
    elif args.format == "short":
        resolution = (1080, 1920)
    else:
        resolution = (1920, 1080)

    ass_content = generate_ass(words, args.style, args.format, resolution)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(ass_content, encoding="utf-8")
    print(f"Generated {len(words)} words karaoke → {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
