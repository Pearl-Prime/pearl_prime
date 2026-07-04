"""Safe zones + per-book layout grids (research §0.6, kdp_bestseller §R3).

Non-overlapping title / subtitle / image / symbol zones. Text fit-to-box;
collision checks keep text out of image busy-regions and symbol clusters.

Variants (per-book from book_id): stacked | split_above_below | frame_center
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from PIL import ImageDraw

from .fonts import get_font

W, H = 1600, 2560
LAYOUT_VARIANTS = ("stacked", "split_above_below", "frame_center")


@dataclass(frozen=True)
class Rect:
    x0: float
    y0: float
    x1: float
    y1: float

    def px(self, cw: int = W, ch: int = H) -> tuple[int, int, int, int]:
        return (int(self.x0 * cw), int(self.y0 * ch), int(self.x1 * cw), int(self.y1 * ch))

    def width_px(self, cw: int = W) -> int:
        return int((self.x1 - self.x0) * cw)

    def height_px(self, ch: int = H) -> int:
        return int((self.y1 - self.y0) * ch)


@dataclass(frozen=True)
class ZonePlan:
    variant: str
    title: Rect
    subtitle: Rect
    image: Rect
    symbol: Rect
    byline: Rect
    series: Rect


def layout_variant_for_book(book_id: str) -> str:
    h = hashlib.sha256(f"layout_grid|{book_id}".encode()).digest()
    return LAYOUT_VARIANTS[h[0] % len(LAYOUT_VARIANTS)]


def zone_plan(family: str, variant: str) -> ZonePlan:
    v = variant if variant in LAYOUT_VARIANTS else "stacked"
    if family == "full_bleed":
        if v == "split_above_below":
            return ZonePlan(v, Rect(0.08, 0.05, 0.92, 0.19), Rect(0.08, 0.60, 0.92, 0.76),
                            Rect(0.0, 0.20, 1.0, 0.58), Rect(0.28, 0.78, 0.72, 0.84),
                            Rect(0.08, 0.88, 0.92, 0.96), Rect(0.08, 0.84, 0.92, 0.88))
        if v == "frame_center":
            return ZonePlan(v, Rect(0.08, 0.06, 0.92, 0.20), Rect(0.08, 0.72, 0.92, 0.84),
                            Rect(0.0, 0.22, 1.0, 0.70), Rect(0.30, 0.42, 0.70, 0.56),
                            Rect(0.08, 0.88, 0.92, 0.96), Rect(0.08, 0.84, 0.92, 0.88))
        return ZonePlan(v, Rect(0.08, 0.06, 0.92, 0.24), Rect(0.08, 0.24, 0.92, 0.38),
                        Rect(0.0, 0.38, 1.0, 0.88), Rect(0.28, 0.58, 0.72, 0.70),
                        Rect(0.08, 0.87, 0.92, 0.95), Rect(0.08, 0.80, 0.92, 0.84))
    if family == "inset_card":
        if v == "split_above_below":
            return ZonePlan(v, Rect(0.08, 0.05, 0.92, 0.15), Rect(0.08, 0.54, 0.92, 0.68),
                            Rect(0.12, 0.17, 0.88, 0.52), Rect(0.34, 0.70, 0.66, 0.78),
                            Rect(0.08, 0.86, 0.92, 0.94), Rect(0.08, 0.78, 0.92, 0.82))
        return ZonePlan(v, Rect(0.08, 0.06, 0.92, 0.17), Rect(0.08, 0.17, 0.92, 0.28),
                        Rect(0.12, 0.29, 0.88, 0.63), Rect(0.34, 0.66, 0.66, 0.74),
                        Rect(0.08, 0.86, 0.92, 0.94), Rect(0.08, 0.78, 0.92, 0.82))
    if family == "panel_bands":
        return ZonePlan(v, Rect(0.08, 0.62, 0.92, 0.76), Rect(0.08, 0.76, 0.92, 0.86),
                        Rect(0.0, 0.155, 1.0, 0.60), Rect(0.34, 0.88, 0.66, 0.94),
                        Rect(0.08, 0.92, 0.92, 0.98), Rect(0.08, 0.04, 0.92, 0.12))
    if family == "title_block":
        if v == "split_above_below":
            return ZonePlan(v, Rect(0.10, 0.06, 0.90, 0.18), Rect(0.10, 0.66, 0.90, 0.80),
                            Rect(0.0, 0.18, 1.0, 0.64), Rect(0.36, 0.82, 0.64, 0.88),
                            Rect(0.08, 0.91, 0.92, 0.97), Rect(0.08, 0.88, 0.92, 0.91))
        return ZonePlan(v, Rect(0.10, 0.22, 0.90, 0.38), Rect(0.10, 0.38, 0.90, 0.50),
                        Rect(0.0, 0.0, 1.0, 0.62), Rect(0.36, 0.52, 0.64, 0.60),
                        Rect(0.08, 0.87, 0.92, 0.95), Rect(0.08, 0.80, 0.92, 0.84))
    if family == "gradient_solo":
        if v == "split_above_below":
            return ZonePlan(v, Rect(0.08, 0.08, 0.92, 0.22), Rect(0.08, 0.68, 0.92, 0.82),
                            Rect(0, 0, 0, 0), Rect(0.24, 0.40, 0.76, 0.58),
                            Rect(0.08, 0.87, 0.92, 0.95), Rect(0.08, 0.80, 0.92, 0.84))
        return ZonePlan(v, Rect(0.08, 0.10, 0.92, 0.26), Rect(0.08, 0.26, 0.92, 0.40),
                        Rect(0, 0, 0, 0), Rect(0.24, 0.42, 0.76, 0.58),
                        Rect(0.08, 0.87, 0.92, 0.95), Rect(0.08, 0.78, 0.92, 0.82))
    if family == "duotone_split":
        sub = Rect(0.08, 0.66, 0.92, 0.82) if v != "stacked" else Rect(0.08, 0.24, 0.92, 0.38)
        return ZonePlan(v, Rect(0.08, 0.08, 0.92, 0.24), sub, Rect(0, 0, 0.60, 1.0),
                        Rect(0.30, 0.64, 0.70, 0.76), Rect(0.08, 0.88, 0.92, 0.96),
                        Rect(0.08, 0.80, 0.92, 0.84))
    if family == "stripe_minimal":
        lx = 0.22
        if v == "split_above_below":
            return ZonePlan(v, Rect(lx, 0.10, 0.94, 0.22), Rect(lx, 0.68, 0.94, 0.82),
                            Rect(0, 0, 0.17, 1.0), Rect(0.04, 0.30, 0.16, 0.86),
                            Rect(lx, 0.88, 0.94, 0.96), Rect(lx, 0.80, 0.94, 0.84))
        return ZonePlan(v, Rect(lx, 0.18, 0.94, 0.32), Rect(lx, 0.32, 0.94, 0.46),
                        Rect(0, 0, 0.17, 1.0), Rect(0.04, 0.30, 0.16, 0.86),
                        Rect(lx, 0.86, 0.94, 0.94), Rect(lx, 0.78, 0.92, 0.82))
    if family == "framed":
        inset = 0.08
        if v == "split_above_below":
            return ZonePlan(v, Rect(inset, 0.12, 1 - inset, 0.24), Rect(inset, 0.68, 1 - inset, 0.82),
                            Rect(0, 0, 0, 0), Rect(0.30, 0.40, 0.70, 0.56),
                            Rect(inset, 0.86, 1 - inset, 0.94), Rect(inset, 0.80, 1 - inset, 0.84))
        return ZonePlan(v, Rect(inset, 0.16, 1 - inset, 0.30), Rect(inset, 0.30, 1 - inset, 0.42),
                        Rect(0, 0, 0, 0), Rect(0.30, 0.48, 0.70, 0.60),
                        Rect(inset, 0.82, 1 - inset, 0.90), Rect(inset, 0.72, 1 - inset, 0.76))
    if family == "type_dominant":
        return ZonePlan(v, Rect(0.08, 0.14, 0.92, 0.46), Rect(0.08, 0.48, 0.92, 0.62),
                        Rect(0, 0, 0, 0), Rect(0.40, 0.64, 0.60, 0.70),
                        Rect(0.08, 0.84, 0.92, 0.92), Rect(0.08, 0.76, 0.92, 0.80))
    return zone_plan("full_bleed", v)


def _overlap(a: Rect, b: Rect) -> bool:
    if b.x1 <= b.x0 and b.y1 <= b.y0:
        return False
    return not (a.x1 <= b.x0 or a.x0 >= b.x1 or a.y1 <= b.y0 or a.y0 >= b.y1)


def text_block_rect(y_px: int, block_h_px: int, zone: Rect) -> Rect:
    return Rect(zone.x0, y_px / H, zone.x1, min((y_px + block_h_px) / H, zone.y1))


def rects_collide(text_rect: Rect, forbidden: tuple[Rect, ...]) -> bool:
    return any(_overlap(text_rect, f) for f in forbidden if f.x1 > f.x0)


def _wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def _line_h(font):
    a, d = font.getmetrics()
    return a + d


def fit_in_zone(draw, text, font_family, zone, *, weight="bold", style="regular",
                max_lines=4, line_spacing=1.06, start_px=200, min_px=28, scale=1.0):
    maxw = zone.width_px() - 8
    max_h = zone.height_px() - 4
    start_px = max(int(round(start_px * scale)), int(round(min_px * scale)) + 4)
    min_px = max(20, int(round(min_px * scale)))
    for size in range(start_px, min_px - 1, -2):
        f = get_font(font_family, "italic" if style == "italic" else weight, size)
        lines = _wrap(draw, text, f, maxw)
        if len(lines) > max_lines:
            continue
        lh = int(_line_h(f) * line_spacing)
        block_h = len(lines) * lh
        if block_h <= max_h and all(draw.textlength(ln, font=f) <= maxw for ln in lines):
            return f, lines, size, block_h
    f = get_font(font_family, "italic" if style == "italic" else weight, min_px)
    lines = _wrap(draw, text, f, maxw)
    while len(lines) > max_lines and len(lines) > 1:
        lines = lines[:-1]
    lh = int(_line_h(f) * line_spacing)
    return f, lines, min_px, min(len(lines) * lh, max_h)
