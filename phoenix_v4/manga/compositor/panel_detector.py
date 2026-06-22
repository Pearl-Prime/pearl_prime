"""Detect panel row boundaries in composed manga pages."""
from __future__ import annotations

from typing import Sequence

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore[assignment,misc]


def _row_ink_scores(gray, width: int, height: int) -> list[float]:
    """Sum of dark pixels per horizontal band (lower = more ink)."""
    pixels = gray.load()
    band_h = max(1, height // 80)
    scores: list[float] = []
    for y0 in range(0, height, band_h):
        y1 = min(height, y0 + band_h)
        total = 0.0
        for y in range(y0, y1):
            for x in range(width):
                total += 255 - pixels[x, y]
        scores.append(total / max(1, (y1 - y0) * width))
    return scores


def detect_panel_rows(
    image_path,
    *,
    min_strip_px: int = 120,
    ink_threshold: float = 18.0,
) -> list[tuple[int, int]]:
    """Return (y0, y1) panel row bands top-to-bottom.

    Uses horizontal ink banding; falls back to uniform vertical strips when
    no clear gutters are found.
    """
    if Image is None:
        raise RuntimeError("Pillow required for panel detection")

    with Image.open(image_path) as im:
        gray = im.convert("L")
        width, height = gray.size

    scores = _row_ink_scores(gray, width, height)
    if not scores:
        return [(0, height)]

    gutters: list[int] = [0]
    for idx, score in enumerate(scores[1:-1], start=1):
        if score < ink_threshold:
            gutters.append(idx)
    gutters.append(len(scores))

    band_h = max(1, height // len(scores))
    rows: list[tuple[int, int]] = []
    for i in range(len(gutters) - 1):
        y0 = gutters[i] * band_h
        y1 = min(height, gutters[i + 1] * band_h)
        if y1 - y0 >= min_strip_px:
            rows.append((y0, y1))

    if len(rows) >= 2:
        return rows

    # Uniform vertical strip fallback (3 strips)
    n = 3
    strip_h = max(min_strip_px, height // n)
    rows = []
    y = 0
    while y < height:
        y1 = min(height, y + strip_h)
        rows.append((y, y1))
        y = y1
    return rows


def crop_strips(image_path, rows: Sequence[tuple[int, int]]):
    if Image is None:
        raise RuntimeError("Pillow required for panel detection")
    with Image.open(image_path) as im:
        return [im.crop((0, y0, im.width, y1)) for y0, y1 in rows]
