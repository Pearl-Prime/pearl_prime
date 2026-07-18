"""Collision-free cover layout solver — structural overlap guarantee.

Every drawn element (title, subtitle, byline, symbol glyph, symbol framing line)
gets a bounding box. Placement scans for a clear band; post-compose assertion
RAISES if any pair overlaps — a broken cover cannot ship.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import layout_zones as Z
from . import symbols as S

W, H = Z.W, Z.H

# Must match templates._frame_symbols defaults
FRAME_PAD = 46
FRAME_LINE_W = 7
BYLINE_BLOCK_H = 160
SERIES_BLOCK_H = 48
TEXT_SYMBOL_GAP = 0.028  # min clear band between subtitle bottom and symbol framing (~72px)


class CoverLayoutCollisionError(RuntimeError):
    """Raised when two layout element boxes overlap after compose."""

    def __init__(self, overlaps: list[tuple[str, str]], boxes: dict[str, Z.Rect]):
        self.overlaps = overlaps
        self.boxes = boxes
        pairs = ", ".join(f"{a}×{b}" for a, b in overlaps)
        super().__init__(f"cover layout collision: {pairs}")


@dataclass
class ElementBox:
    name: str
    rect: Z.Rect


@dataclass
class SolvedLayout:
    title_y: int
    title_font: object
    title_lines: list[str]
    title_box: Z.Rect
    subtitle_y: int
    subtitle_font: object
    subtitle_lines: list[str]
    subtitle_box: Z.Rect
    symbol_glyph_box: Z.Rect
    symbol_framed_box: Z.Rect
    byline_y: int
    byline_box: Z.Rect
    series_y: int
    series_box: Z.Rect
    elements: list[ElementBox] = field(default_factory=list)


def px_to_norm(x0: float, y0: float, x1: float, y1: float) -> Z.Rect:
    return Z.Rect(x0 / W, y0 / H, x1 / W, y1 / H)


def framing_forbidden_rect(
    glyph_bbox_px: tuple[int, int, int, int],
    framing: str,
    *,
    pad: int = FRAME_PAD,
    line_w: int = FRAME_LINE_W,
) -> Z.Rect:
    """Glyph bbox + pad + framing line extent (the bug fix: line was missing)."""
    x0, y0, x1, y1 = glyph_bbox_px
    left = x0 - pad
    right = x1 + pad
    top = y0 - pad
    bot = y1 + pad
    extra = line_w + 2
    if framing == "none":
        pass
    elif framing == "box":
        top -= extra
        bot += extra
        left -= extra
        right += extra
    elif framing == "double":
        top -= (line_w + 8 + line_w)
        bot += (line_w + 8 + line_w)
    elif framing == "strike":
        pass  # padded box covers horizontal strike
    elif framing == "line_above":
        top -= extra
    else:  # line_below and default
        bot += extra
    return px_to_norm(left, top, right, bot)


def _line_h(font) -> int:
    a, d = font.getmetrics()
    return a + d


def text_block_at(y_px: int, block_h_px: int, zone: Z.Rect) -> Z.Rect:
    return Z.text_block_rect(y_px, block_h_px, zone)


def _ordered_y_candidates(zone: Z.Rect, block_h: int, step: int = 6) -> list[int]:
    y_min = int(zone.y0 * H)
    y_max = max(y_min, int(zone.y1 * H) - block_h)
    if y_max < y_min:
        return [y_min]
    center = y_min + (y_max - y_min) // 2
    cands = list(range(y_min, y_max + 1, step))
    return sorted(cands, key=lambda y: abs(y - center))


def find_clear_y(
    zone: Z.Rect,
    block_h: int,
    forbidden: tuple[Z.Rect, ...],
    *,
    step: int = 6,
) -> int | None:
    for y in _ordered_y_candidates(zone, block_h, step):
        if not Z.rects_collide(text_block_at(y, block_h, zone), forbidden):
            return y
    return None


def count_overlaps(boxes: list[ElementBox]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for i, a in enumerate(boxes):
        for b in boxes[i + 1 :]:
            if Z._overlap(a.rect, b.rect):
                out.append((a.name, b.name))
    return out


def assert_zero_overlaps(boxes: list[ElementBox]) -> dict:
    """Hard gate: overlap_count must be 0 or raise."""
    overlaps = count_overlaps(boxes)
    rect_map = {b.name: b.rect for b in boxes}
    if overlaps:
        raise CoverLayoutCollisionError(overlaps, rect_map)
    return {"overlap_count": 0, "elements": list(rect_map.keys())}


def effective_framing(framing: str, symbol_zone: Z.Rect, subtitle_box: Z.Rect) -> str:
    """When the symbol sits below the subtitle, line_above reads as a rule under the text."""
    if symbol_zone.y0 > subtitle_box.y1 + 0.008:
        if framing == "line_above":
            return "line_below"
        if framing == "double":
            return "line_below"
    return framing


def symbol_zone_after_text(plan: Z.ZonePlan, subtitle_box: Z.Rect) -> Z.Rect:
    """Place symbol cluster below subtitle with mandatory gap; shift down, never up into text."""
    z = plan.symbol
    if z.x1 <= z.x0:
        return z
    headroom = (FRAME_PAD + FRAME_LINE_W + 6) / H
    min_y0 = subtitle_box.y1 + TEXT_SYMBOL_GAP + headroom
    h = max(0.03, min(z.y1 - z.y0, 0.06))
    max_y1 = plan.byline.y0 - TEXT_SYMBOL_GAP
    y0 = max(z.y0, min_y0)
    if y0 + h > max_y1:
        h = max(0.025, max_y1 - y0)
    y0 = max(0.03, min(y0, max_y1 - h))
    return Z.Rect(z.x0, y0, z.x1, min(y0 + h, max_y1))


def resolve_symbol_zone(cover, plan: Z.ZonePlan, is_busy_fn) -> Z.Rect:
    """Shift symbol off busy image regions only (never toward title/subtitle)."""
    z = plan.symbol
    if z.x1 <= z.x0:
        return z
    if cover is not None and is_busy_fn(cover, (z.x0, z.y0, z.x1, z.y1)):
        lift = 0.08 if plan.variant == "split_above_below" else 0.06
        z = Z.Rect(z.x0, max(0.05, z.y0 - lift), z.x1, max(z.y0 + 0.06, z.y1 - lift))
    return z


def measure_symbol_boxes(
    cover,
    spec,
    plan: Z.ZonePlan,
    zone: Z.Rect,
    sym_color: tuple,
    *,
    framing: str | None = None,
    orientation: str = "auto",
    scrim: bool = False,
) -> tuple[tuple[int, int, int, int], Z.Rect, Z.Rect]:
    zone_px = (W * zone.x0, H * zone.y0, W * zone.x1, H * zone.y1)
    sbox = S.draw_symbol_set(
        cover, spec.motif, zone_px, spec.count, sym_color, spec.seed,
        orientation=orientation, scrim=scrim,
    )
    glyph = px_to_norm(*sbox)
    fr = framing if framing is not None else spec.framing
    framed = framing_forbidden_rect(sbox, fr)
    return sbox, glyph, framed


def solve_subtitle_y(
    dr,
    spec,
    plan: Z.ZonePlan,
    forbidden: tuple[Z.Rect, ...],
    title_box: Z.Rect,
    *,
    fit_subtitle_fn,
    max_lines: int,
    base_px: int,
    prefer_below_title_y: int | None = None,
) -> tuple[int, object, list[str], int]:
    """Shrink font if needed, then scan subtitle zone for collision-free y."""
    zone = plan.subtitle
    maxw = zone.width_px() - 16
    max_h = zone.height_px()
    block_forbid = forbidden + (title_box,)

    for shrink_round in range(8):
        scale = 1.0 - shrink_round * 0.08
        px = max(28, int(base_px * scale))
        sf, sub_lines, _ = fit_subtitle_fn(
            dr, spec, spec.serif, maxw, max_lines, px, max_h=max_h,
        )
        lh = int(_line_h(sf) * 1.06)
        block_h = len(sub_lines) * lh

        if prefer_below_title_y is not None:
            y_try = prefer_below_title_y
            if y_try + block_h <= int(zone.y1 * H) and not Z.rects_collide(
                text_block_at(y_try, block_h, zone), block_forbid,
            ):
                return y_try, sf, sub_lines, block_h

        y = find_clear_y(zone, block_h, block_forbid)
        if y is not None:
            return y, sf, sub_lines, block_h

    # Last resort: top of zone (solver already tried all y; assertion will catch if still bad)
    sf, sub_lines, _ = fit_subtitle_fn(dr, spec, spec.serif, maxw, max_lines, 28, max_h=max_h)
    lh = int(_line_h(sf) * 1.06)
    block_h = len(sub_lines) * lh
    return int(zone.y0 * H), sf, sub_lines, block_h
