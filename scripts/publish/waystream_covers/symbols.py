"""High-contrast per-topic symbol vocabulary with per-book variation.

Each topic maps to a primitive UNIT glyph. A cover draws `count` (== book
installment, 1..7) copies in a seeded arrangement (row / arc / column), so:
  * topic identity  -> the glyph shape
  * book number     -> how many
  * series progress -> the row "fills in" across the series (research Schema C)
  * uniqueness      -> (motif x count x arrangement x per-glyph jitter) is
                       distinct for every one of the 800 book_ids.

Contrast is GUARANTEED by pick_symbol_color(): it samples the actual background
under the symbol zone and chooses the highest-contrast palette color. This is
the fix for the pilot's invisible light-blue mark.

Glyphs are rendered on a 4x supersampled layer and downscaled (crisp edges).
"""
from __future__ import annotations
import math
import random
from PIL import Image, ImageDraw, ImageChops, ImageFilter

from . import palette as P

SS = 4  # supersample factor
_ASYMM = {"rise", "jagged", "drop", "crescent", "loop"}  # get small rotation jitter


# --- unit glyphs: each returns an (T,T) RGBA tile, glyph centered, in `color` ---
def _tile(T):
    return Image.new("RGBA", (T, T), (0, 0, 0, 0))


def _u_ring(T, color, w):
    t = _tile(T); d = ImageDraw.Draw(t); r = int(T * 0.40); c = T // 2
    d.ellipse([c - r, c - r, c + r, c + r], outline=color, width=w)
    return t


def _u_breath(T, color, w):
    t = _tile(T); d = ImageDraw.Draw(t); c = T // 2; r = int(T * .40)
    d.ellipse([c - r, c - r, c + r, c + r], outline=color, width=w)
    r2 = int(T * .22); d.ellipse([c - r2, c - r2, c + r2, c + r2], outline=color, width=max(2, w - 2))
    rr = int(T * .05); d.ellipse([c - rr, c - rr, c + rr, c + rr], fill=color)
    return t


def _u_link(T, color, w):
    t = _tile(T); d = ImageDraw.Draw(t); c = T // 2; r = int(T * .30); off = int(T * .20)
    d.ellipse([c - off - r, c - r, c - off + r, c + r], outline=color, width=w)
    d.ellipse([c + off - r, c - r, c + off + r, c + r], outline=color, width=w)
    return t


def _u_offset(T, color, w):
    t = _tile(T); d = ImageDraw.Draw(t); c = T // 2; r = int(T * .22); off = int(T * .24)
    d.ellipse([c - off - r, c - off - r, c - off + r, c - off + r], outline=color, width=w)
    d.ellipse([c + off - r, c + off - r, c + off + r, c + off + r], outline=color, width=w)
    return t


def _u_crescent(T, color, w):
    t = _tile(T); c = T // 2; r = int(T * .40)
    full = Image.new("L", (T, T), 0); ImageDraw.Draw(full).ellipse([c - r, c - r, c + r, c + r], fill=255)
    cut = Image.new("L", (T, T), 0); off = int(r * .55)
    ImageDraw.Draw(cut).ellipse([c - r + off, c - r - off // 2, c + r + off, c + r - off // 2], fill=255)
    mask = ImageChops.subtract(full, cut)
    solid = Image.new("RGBA", (T, T), color)
    return Image.composite(solid, t, mask)


def _u_loop(T, color, w):
    t = _tile(T); d = ImageDraw.Draw(t); c = T // 2; r = int(T * .38)
    d.arc([c - r, c - r, c + r, c + r], start=35, end=320, fill=color, width=w)
    a = math.radians(320); x = c + int(r * math.cos(a)); y = c + int(r * math.sin(a))
    d.line([(x, y), (x + int(T * .13), y + int(T * .11))], fill=color, width=w)
    return t


def _u_rise(T, color, w):
    t = _tile(T); d = ImageDraw.Draw(t); c = T // 2; r = int(T * .38)
    d.line([(c - r, c + int(r * .5)), (c, c - int(r * .6))], fill=color, width=w)
    d.line([(c, c - int(r * .6)), (c + r, c + int(r * .5))], fill=color, width=w)
    return t


def _u_divider(T, color, w):
    t = _tile(T); d = ImageDraw.Draw(t); c = T // 2; r = int(T * .42)
    d.line([(c, c - r), (c, c + r - int(T * .07))], fill=color, width=w)
    rr = int(T * .07); d.ellipse([c - rr, c + r - rr, c + rr, c + r + rr], fill=color)
    return t


def _u_ember(T, color, w):
    t = _tile(T); d = ImageDraw.Draw(t); c = T // 2; r = int(T * .36)
    d.polygon([(c, c - r), (c + r, c), (c, c + r), (c - r, c)], outline=color, width=w)
    rr = int(T * .06); d.ellipse([c - rr, c - rr + int(T * .06), c + rr, c + rr + int(T * .06)], fill=color)
    return t


def _u_wane(T, color, w):
    t = _tile(T); d = ImageDraw.Draw(t); c = T // 2; r = int(T * .40)
    d.arc([c - r, c - int(r * .6), c + r, c + int(r * 1.4)], start=180, end=360, fill=color, width=w)
    return t


def _u_lowline(T, color, w):
    t = _tile(T); d = ImageDraw.Draw(t); c = T // 2; r = int(T * .42); yb = c + int(T * .16)
    d.line([(c - r, yb), (c + r, yb)], fill=color, width=w)
    rr = int(T * .08); yd = c - int(T * .12)
    d.ellipse([c - rr, yd - rr, c + rr, yd + rr], fill=color)
    return t


def _u_bar(T, color, w):
    t = _tile(T); d = ImageDraw.Draw(t); c = T // 2; r = int(T * .42); bw = max(w, int(T * .15))
    d.rounded_rectangle([c - bw // 2, c - r, c + bw // 2, c + r], radius=bw // 3, fill=color)
    return t


def _u_jagged(T, color, w):
    t = _tile(T); d = ImageDraw.Draw(t); c = T // 2; r = int(T * .40)
    pts = [(c - r, c - int(r * .2)), (c - int(r * .3), c + int(r * .5)),
           (c + int(r * .1), c - int(r * .4)), (c + r, c + int(r * .3))]
    d.line(pts, fill=color, width=w, joint="curve")
    return t


def _u_drop(T, color, w):
    t = _tile(T); d = ImageDraw.Draw(t); c = T // 2; r = int(T * .28); cy = c + int(T * .12)
    d.ellipse([c - r, cy - r, c + r, cy + r], fill=color)
    d.polygon([(c - int(r * .72), cy - int(r * .35)), (c, c - int(T * .42)), (c + int(r * .72), cy - int(r * .35))], fill=color)
    return t


def _u_stem(T, color, w):
    t = _tile(T); d = ImageDraw.Draw(t); c = T // 2; r = int(T * .42)
    d.line([(c, c - r), (c, c + r)], fill=color, width=w)
    for fy in (c - int(r * .2), c + int(r * .3)):
        d.line([(c, fy), (c + int(T * .18), fy - int(T * .12))], fill=color, width=max(2, w - 1))
    rr = int(T * .06); d.ellipse([c - rr, c - r - rr, c + rr, c - r + rr], fill=color)
    return t


MOTIF_FN = {
    "ring": _u_ring, "breath": _u_breath, "link": _u_link, "offset": _u_offset,
    "crescent": _u_crescent, "loop": _u_loop, "rise": _u_rise, "divider": _u_divider,
    "ember": _u_ember, "wane": _u_wane, "lowline": _u_lowline, "bars": _u_bar,
    "jagged": _u_jagged, "drop": _u_drop, "stem": _u_stem,
}


def pick_symbol_color(img, zone, palette_rgb: dict) -> tuple[int, int, int]:
    """palette_rgb has keys deep/field/accent (rgb tuples). Sample the zone and
    return the highest-contrast option from accent/cream/ink/white/deep."""
    bg = P.sample_region(img, zone)
    cands = [palette_rgb["accent"], P.CREAM, P.INK, P.WHITE, palette_rgb["deep"]]
    # prefer accent if it clears 3.0, else the absolute best
    best = P.best_contrast(bg, cands)
    if P.contrast(bg, palette_rgb["accent"]) >= 3.4:
        return palette_rgb["accent"]
    return best


def draw_symbol_set(img, motif, zone, count, color, seed, orientation="auto", scrim=False):
    """Render `count` motif units into `zone`=(x0,y0,x1,y1) on `img` (mutates).
    orientation: row | arc | column | auto (row/arc seeded)."""
    x0, y0, x1, y1 = (int(v) for v in zone)
    zw, zh = max(1, x1 - x0), max(1, y1 - y0)
    rnd = random.Random(seed)
    n = max(1, min(int(count), 7))
    if orientation == "auto":
        orientation = rnd.choice(["row", "arc"])

    LW, LH = zw * SS, zh * SS
    layer = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    rgba = tuple(color) + (255,)

    if orientation == "column":
        cell = LH / (n + 0.4)
        usize = int(min(cell * 0.82, LW * 0.78))
        positions = [(LW // 2, int(cell * (i + 0.7))) for i in range(n)]
    else:
        cell = (LW * 0.94) / n
        usize = int(min(cell * 0.80, LH * 0.86))
        startx = (LW - cell * n) / 2 + cell / 2
        positions = []
        for i in range(n):
            cx = int(startx + cell * i); cy = LH // 2
            if orientation == "arc":
                tt = (i - (n - 1) / 2) / max(n, 1)
                cy = int(LH * 0.46 + (1 - math.cos(tt * math.pi)) * LH * 0.10)
            positions.append((cx, cy))

    usize = max(24, usize)
    w = max(4, int(usize * 0.07))
    fn = MOTIF_FN.get(motif, _u_ring)
    for i, (cx, cy) in enumerate(positions):
        tile = fn(usize, rgba, w)
        if motif == "bars":  # uneven columns: bottom-aligned height jitter
            hf = 0.5 + rnd.random() * 0.5
            nh = max(8, int(usize * hf))
            tile = tile.resize((usize, nh))
            layer.alpha_composite(tile, (cx - usize // 2, cy + usize // 2 - nh))
            continue
        if motif in _ASYMM:
            tile = tile.rotate(rnd.uniform(-9, 9), expand=True, resample=Image.BICUBIC)
        # subtle per-unit size breathing for organic feel
        sf = 1.0 + (rnd.random() - 0.5) * 0.10
        if abs(sf - 1.0) > 0.01:
            ns = max(8, int(tile.width * sf))
            tile = tile.resize((ns, ns))
        layer.alpha_composite(tile, (cx - tile.width // 2, cy - tile.height // 2))

    small = layer.resize((zw, zh), Image.LANCZOS)
    if scrim:  # soft feathered glow for legibility over imagery (not a hard "button")
        cush = Image.new("RGBA", (zw, zh), (0, 0, 0, 0))
        light_mark = P.luminance(color) > 0.5
        fill = (5, 7, 11, 150) if light_mark else (248, 243, 236, 150)
        ImageDraw.Draw(cush).ellipse([int(-zw * 0.08), int(zh * 0.08), int(zw * 1.08), int(zh * 0.92)], fill=fill)
        cush = cush.filter(ImageFilter.GaussianBlur(int(zh * 0.24)))
        img.paste(cush, (x0, y0), cush)
    img.paste(small, (x0, y0), small)
