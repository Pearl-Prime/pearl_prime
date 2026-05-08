"""Furigana (ruby) overlay rendering for Japanese dialogue lines.

Structured segments from lettering_spec::

    "furigana": [
      {"base": "漢字", "reading": "かんじ"},
      ...
    ]

Walks ``full_text`` left-to-right. When ``text.startswith(segment.base)``
at the cursor, renders reading centered above base; otherwise emits one
codepoint/glyph chunk as plain base text.
"""
from __future__ import annotations

import copy
from typing import Any, Mapping


def normalize_furigana_segments(line: Mapping[str, Any]) -> list[dict[str, str]]:
    """Extract valid furigana segments from a dialogue line."""
    raw = line.get("furigana")
    if not raw or not isinstance(raw, list):
        return []
    out: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        base = str(item.get("base") or "").strip()
        reading = str(item.get("reading") or "").strip()
        if base and reading:
            out.append({"base": base, "reading": reading})
    return out


def _text_width(draw: Any, s: str, font: Any) -> int:
    try:
        bbox = draw.textbbox((0, 0), s, font=font)
        return max(0, bbox[2] - bbox[0])
    except AttributeError:
        return int(draw.textsize(s, font=font)[0])  # type: ignore[attr-defined]


def _text_height(draw: Any, s: str, font: Any) -> int:
    try:
        bbox = draw.textbbox((0, 0), s, font=font)
        return max(1, bbox[3] - bbox[1])
    except AttributeError:
        return max(1, int(draw.textsize(s, font=font)[1]))  # type: ignore[attr-defined]


def furigana_ruby_above_height(draw: Any, segments: list[dict[str, str]], ruby_font: Any) -> int:
    """Extra pixels to reserve above the base line for ruby text."""
    if not segments:
        return 0
    h_max = max(_text_height(draw, seg["reading"], ruby_font) for seg in segments)
    return h_max + 2


def render_furigana_line(
    draw: Any,
    full_text: str,
    segments: list[dict[str, str]],
    x: int,
    y: int,
    *,
    base_font: Any,
    ruby_font: Any,
    text_fill: tuple[int, int, int, int] = (0, 0, 0, 255),
    ruby_fill: tuple[int, int, int, int] = (40, 40, 40, 255),
    dry_run: bool = False,
    segment_queue: list[dict[str, str]] | None = None,
) -> tuple[int, int]:
    """Draw a single line of text with ruby at (x, y).

    Ruby is stacked above baselines starting at ``y``. Base glyphs start at
    ``y + ruby_band``.

    If ``segment_queue`` is supplied, pops are applied to it (preserves leftover
    segments across successive lines). Otherwise a private copy of ``segments``
    is used.

    Returns ``(pixels_width, pixels_height)`` for the stacked block.
    """
    ruby_band = furigana_ruby_above_height(draw, segments, ruby_font)
    base_y = y + ruby_band

    if segment_queue is not None:
        work_queue = segment_queue
    else:
        work_queue = copy.deepcopy(list(segments))
    cursor_x = x
    i = 0
    max_bottom = base_y

    while i < len(full_text):
        matched = False
        if work_queue:
            b = work_queue[0]["base"]
            if full_text.startswith(b, i):
                r = work_queue[0]["reading"]
                work_queue.pop(0)
                base_w = _text_width(draw, b, base_font)
                ruby_w = _text_width(draw, r, ruby_font)
                rx = cursor_x + max(0, (base_w - ruby_w) // 2)
                if not dry_run:
                    draw.text((rx, y), r, font=ruby_font, fill=ruby_fill)
                    draw.text((cursor_x, base_y), b, font=base_font, fill=text_fill)
                cursor_x += base_w
                i += len(b)
                matched = True
                max_bottom = max(max_bottom, base_y + _text_height(draw, b, base_font))
        if matched:
            continue

        ch = full_text[i]
        if not dry_run:
            draw.text((cursor_x, base_y), ch, font=base_font, fill=text_fill)
        cw = _text_width(draw, ch, base_font)
        cursor_x += cw
        ch_h = _text_height(draw, ch, base_font)
        max_bottom = max(max_bottom, base_y + ch_h)
        i += 1

    total_h = max_bottom - y + 2
    return cursor_x - x, total_h
