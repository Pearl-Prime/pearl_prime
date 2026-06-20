"""The layout LIBRARY: 8 distinct cover families. 4 use a FLUX image
(full_bleed, inset_card, panel_bands, title_block); 4 are image-free
(gradient_solo, framed, duotone_split, stripe_minimal).

Each family is a function(spec, image) -> RGB Image (1600x2560). They share the
typography/scrim/band helpers below. Per-cover craft stays clean (one focal
element, <=2 fonts, <=3 colors, one high-contrast topic mark); variation comes
from which family/fonts/palette an author gets + the per-book symbol set.
"""
from __future__ import annotations
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFilter

from .fonts import get_font
from . import palette as P
from . import symbols as S

W, H = 1600, 2560
M = 132  # base margin


@dataclass
class Spec:
    title: str
    subtitle: str
    author_display: str
    imprint: str
    series_name: str        # cluster, already cleaned (e.g. "STEADY GROUND")
    book_num: int
    count: int              # symbol repetitions (== installment, 1..7)
    topic: str
    motif: str
    serif: str
    sans: str
    title_case: str
    deep: tuple
    field: tuple
    accent: tuple
    seed: int
    family: str = ""


# ---------------- typography helpers ----------------
def _case(s: str, case: str) -> str:
    if case == "upper" or case == "small_caps":
        return s.upper()
    if case == "title":
        return s.title()
    return s


def _wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = wd
    if cur:
        lines.append(cur)
    return lines


def _line_h(font):
    a, d = font.getmetrics()
    return a + d


def fit_title(draw, text, family, maxw, max_h, start=200, min_px=104, weight="bold", ls=1.06):
    size = start
    while size > min_px:
        f = get_font(family, weight, size)
        lines = _wrap(draw, text, f, maxw)
        total = len(lines) * _line_h(f) * ls
        if len(lines) <= 3 and total <= max_h:
            return f, lines, size
        size -= 6
    f = get_font(family, weight, min_px)
    return f, _wrap(draw, text, f, maxw), min_px


def draw_lines(draw, lines, font, cx, y, fill, ls=1.06, shadow=None, tracking=0, align="center", x_left=None):
    lh = int(_line_h(font) * ls)
    for ln in lines:
        lw = draw.textlength(ln, font=font) + tracking * max(len(ln) - 1, 0)
        x = (cx - lw / 2) if align == "center" else x_left
        if shadow:
            _track(draw, (x + shadow[0], y + shadow[1]), ln, font, shadow[2], tracking)
        _track(draw, (x, y), ln, font, fill, tracking)
        y += lh
    return y


def _track(draw, xy, text, font, fill, tracking):
    x, y = xy
    if not tracking:
        draw.text((x, y), text, font=font, fill=fill); return
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def _track_w(draw, text, font, tracking):
    return sum(draw.textlength(ch, font=font) + tracking for ch in text) - tracking


def cover_crop(img, w, h):
    s = max(w / img.width, h / img.height)
    im = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))))
    x = (im.width - w) // 2; y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def _lmask(w, h, a0, a1):
    g = Image.new("L", (1, h))
    for y in range(h):
        g.putpixel((0, y), int(a0 + (a1 - a0) * y / max(h - 1, 1)))
    return g.resize((w, h))


def scrim(cover, x, y, w, h, color, a_top, a_bot):
    panel = Image.new("RGB", (w, h), color)
    cover.paste(panel, (x, y), _lmask(w, h, a_top, a_bot))


def series_band(draw, spec, cx, y, color, align="center", x_left=None):
    f = get_font(spec.sans, "bold", 40)
    label = f"BOOK {spec.book_num}   ·   {spec.series_name}"
    bw = _track_w(draw, label, f, 6)
    x = (cx - bw / 2) if align == "center" else x_left
    if align == "center":
        draw.line([(x - 46, y + 22), (x - 16, y + 22)], fill=color, width=3)
        draw.line([(x + bw + 16, y + 22), (x + bw + 46, y + 22)], fill=color, width=3)
    _track(draw, (x, y), label, f, color, 6)


def byline(draw, spec, cx, y, color, sub_color, align="center", x_left=None):
    af = get_font(spec.sans, "bold", 56)
    name = spec.author_display.upper()
    nw = _track_w(draw, name, af, 3)
    x = (cx - nw / 2) if align == "center" else x_left
    _track(draw, (x, y), name, af, color, 3)
    imf = get_font(spec.sans, "regular", 29)
    iw = _track_w(draw, spec.imprint, imf, 5)
    xi = (cx - iw / 2) if align == "center" else x_left
    _track(draw, (xi, y + 74), spec.imprint, imf, sub_color, 5)


def _sym_color(cover, zone, spec):
    return S.pick_symbol_color(cover, zone, {"deep": spec.deep, "field": spec.field, "accent": spec.accent})


# ---------------- 1. FULL BLEED (image) ----------------
def full_bleed(spec, image):
    cover = cover_crop(image, W, H) if image else P.gradient((W, H), spec.deep, P.darken(spec.deep, 0.3))
    cover = cover.convert("RGB")
    scrim(cover, 0, 0, W, int(H * 0.50), P.darken(spec.deep, 0.4), 205, 0)
    scrim(cover, 0, int(H * 0.58), W, int(H * 0.42), P.darken(spec.deep, 0.5), 0, 215)
    dr = ImageDraw.Draw(cover)
    tf, lines, _ = fit_title(dr, _case(spec.title, spec.title_case), spec.serif, W - 2 * M, H * 0.30, start=196)
    y = int(H * 0.10)
    y = draw_lines(dr, lines, tf, W // 2, y, P.CREAM, shadow=(3, 4, (0, 0, 0)))
    sf = get_font(spec.serif, "italic", 58)
    y = draw_lines(dr, _wrap(dr, spec.subtitle, sf, W - 2 * int(M * 1.25)), sf, W // 2, y + 16, P.lighten(spec.accent, 0.25), shadow=(2, 2, (0, 0, 0)))
    zone = (W * 0.30, H * 0.60, W * 0.70, H * 0.69)
    S.draw_symbol_set(cover, spec.motif, zone, spec.count, _sym_color(cover, zone, spec), spec.seed, scrim=True)
    series_band(dr, spec, W // 2, int(H * 0.805), P.CREAM)
    byline(dr, spec, W // 2, int(H * 0.875), P.CREAM, (204, 200, 192))
    return cover


# ---------------- 2. INSET CARD (image) ----------------
def inset_card(spec, image):
    # light paper field so a (typically dark, atmospheric) portrait card POPS
    cover = P.grain(P.vignette(Image.new("RGB", (W, H), spec.field), 0.16), 4).convert("RGB")
    dr = ImageDraw.Draw(cover)
    ink = P.best_contrast(spec.field, [P.INK, spec.deep])
    tf, lines, _ = fit_title(dr, _case(spec.title, spec.title_case), spec.serif, W - 2 * M, H * 0.16, start=148)
    y = draw_lines(dr, lines, tf, W // 2, int(H * 0.072), ink)
    sf = get_font(spec.serif, "italic", 48)
    draw_lines(dr, _wrap(dr, spec.subtitle, sf, W - 2 * int(M * 1.3)), sf, W // 2, y + 6, P.darken(spec.accent, 0.12))
    # portrait image card, centered
    ch = int(H * 0.34); cw = int(ch / 1.18)
    cx0, cy0 = (W - cw) // 2, int(H * 0.30)
    card = cover_crop(image, cw, ch).convert("RGB") if image else P.gradient((cw, ch), spec.accent, spec.deep)
    sh = Image.new("RGBA", (cw + 80, ch + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([40, 46, cw + 40, ch + 46], fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(20))
    cover.paste(sh, (cx0 - 40, cy0 - 40), sh)
    b = 10
    cover.paste(Image.new("RGB", (cw + 2 * b, ch + 2 * b), spec.accent), (cx0 - b, cy0 - b))
    cover.paste(card, (cx0, cy0))
    zone = (W * 0.34, cy0 + ch + int(H * 0.028), W * 0.66, cy0 + ch + int(H * 0.088))
    S.draw_symbol_set(cover, spec.motif, zone, spec.count, _sym_color(cover, zone, spec), spec.seed)
    series_band(dr, spec, W // 2, int(H * 0.80), P.darken(spec.accent, 0.1))
    byline(dr, spec, W // 2, int(H * 0.88), ink, P.mix(spec.field, ink, 0.5))
    return cover


# ---------------- 3. PANEL BANDS (image) ----------------
def panel_bands(spec, image):
    cover = Image.new("RGB", (W, H), spec.field)
    # top deep band w/ kicker
    top_h = int(H * 0.155)
    cover.paste(Image.new("RGB", (W, top_h), spec.deep), (0, 0))
    dr = ImageDraw.Draw(cover)
    series_band(dr, spec, W // 2, int(top_h * 0.42), P.lighten(spec.accent, 0.25))
    # image panel
    pan_y0, pan_y1 = top_h, int(H * 0.60)
    ph = pan_y1 - pan_y0
    panel = cover_crop(image, W, ph).convert("RGB") if image else P.gradient((W, ph), spec.deep, spec.accent)
    cover.paste(panel, (0, pan_y0))
    dr.rectangle([0, pan_y1 - 5, W, pan_y1], fill=spec.accent)
    # bottom field: title (ink), subtitle, symbol, byline
    ink = P.best_contrast(spec.field, [P.INK, spec.deep])
    tf, lines, _ = fit_title(dr, _case(spec.title, spec.title_case), spec.serif, W - 2 * M, H * 0.16, start=150)
    y = draw_lines(dr, lines, tf, W // 2, int(H * 0.645), ink)
    sf = get_font(spec.serif, "italic", 48)
    draw_lines(dr, _wrap(dr, spec.subtitle, sf, W - 2 * int(M * 1.3)), sf, W // 2, y + 8, P.darken(spec.accent, 0.15))
    zone = (W * 0.34, H * 0.855, W * 0.66, H * 0.915)
    S.draw_symbol_set(cover, spec.motif, zone, spec.count, _sym_color(cover, zone, spec), spec.seed)
    byline(dr, spec, W // 2, int(H * 0.93), ink, P.mix(spec.field, ink, 0.55))
    return cover


# ---------------- 4. TITLE BLOCK (image) ----------------
def title_block(spec, image):
    cover = (cover_crop(image, W, H) if image else P.gradient((W, H), spec.deep, spec.accent)).convert("RGB")
    scrim(cover, 0, int(H * 0.62), W, int(H * 0.38), P.darken(spec.deep, 0.45), 0, 205)
    # solid title block
    bw, bh = int(W * 0.84), int(H * 0.27)
    bx, by = (W - bw) // 2, int(H * 0.26)
    block = Image.new("RGBA", (bw, bh), tuple(P.darken(spec.deep, 0.1)) + (235,))
    cover.paste(block, (bx, by), block)
    dr = ImageDraw.Draw(cover)
    dr.rectangle([bx, by, bx + bw, by + 6], fill=spec.accent)
    dr.rectangle([bx, by + bh - 6, bx + bw, by + bh], fill=spec.accent)
    tf, lines, _ = fit_title(dr, _case(spec.title, spec.title_case), spec.serif, bw - 90, bh * 0.62, start=150)
    y = draw_lines(dr, lines, tf, W // 2, by + int(bh * 0.13), P.CREAM)
    sf = get_font(spec.serif, "italic", 46)
    draw_lines(dr, _wrap(dr, spec.subtitle, sf, bw - 120), sf, W // 2, y + 6, P.lighten(spec.accent, 0.25))
    zone = (W * 0.40, by + bh + int(H * 0.02), W * 0.60, by + bh + int(H * 0.075))
    S.draw_symbol_set(cover, spec.motif, zone, spec.count, _sym_color(cover, zone, spec), spec.seed, scrim=True)
    series_band(dr, spec, W // 2, int(H * 0.815), P.CREAM)
    byline(dr, spec, W // 2, int(H * 0.885), P.CREAM, P.lighten(spec.deep, 0.5))
    return cover


# ---------------- 5. GRADIENT SOLO (no image) ----------------
def gradient_solo(spec, image=None):
    cover = P.gradient((W, H), spec.deep, P.mix(spec.deep, spec.field, 0.5), angle=68)
    cover = P.grain(P.vignette(cover, 0.26), 5).convert("RGB")
    dr = ImageDraw.Draw(cover)
    tf, lines, _ = fit_title(dr, _case(spec.title, spec.title_case), spec.serif, W - 2 * M, H * 0.22, start=176)
    y = draw_lines(dr, lines, tf, W // 2, int(H * 0.115), P.CREAM, shadow=(2, 3, P.darken(spec.deep, 0.3)))
    sf = get_font(spec.serif, "italic", 56)
    draw_lines(dr, _wrap(dr, spec.subtitle, sf, W - 2 * int(M * 1.25)), sf, W // 2, y + 14, P.lighten(spec.accent, 0.25))
    # HERO symbol (the focal element when there is no image)
    zone = (W * 0.24, H * 0.42, W * 0.76, H * 0.56)
    col = _sym_color(cover, zone, spec)
    S.draw_symbol_set(cover, spec.motif, zone, spec.count, col, spec.seed)
    series_band(dr, spec, W // 2, int(H * 0.78), P.lighten(spec.accent, 0.2))
    byline(dr, spec, W // 2, int(H * 0.875), P.CREAM, P.lighten(spec.deep, 0.5))
    return cover


# ---------------- 6. FRAMED (no image) ----------------
def framed(spec, image=None):
    cover = P.grain(P.vignette(Image.new("RGB", (W, H), spec.field), 0.18), 5).convert("RGB")
    dr = ImageDraw.Draw(cover)
    ink = P.best_contrast(spec.field, [P.INK, spec.deep])
    inset = 84
    dr.rectangle([inset, inset, W - inset, H - inset], outline=spec.accent, width=6)
    dr.rectangle([inset + 16, inset + 16, W - inset - 16, H - inset - 16], outline=P.mix(spec.accent, spec.field, 0.45), width=2)
    tf, lines, _ = fit_title(dr, _case(spec.title, spec.title_case), spec.serif, W - 2 * (inset + 70), H * 0.22, start=172)
    y = draw_lines(dr, lines, tf, W // 2, int(H * 0.20), ink, tracking=(6 if spec.title_case == "small_caps" else 0))
    sf = get_font(spec.serif, "italic", 54)
    draw_lines(dr, _wrap(dr, spec.subtitle, sf, W - 2 * (inset + 110)), sf, W // 2, y + 16, P.darken(spec.accent, 0.12))
    zone = (W * 0.30, H * 0.52, W * 0.70, H * 0.62)
    S.draw_symbol_set(cover, spec.motif, zone, spec.count, _sym_color(cover, zone, spec), spec.seed)
    series_band(dr, spec, W // 2, int(H * 0.74), P.darken(spec.accent, 0.1))
    byline(dr, spec, W // 2, int(H * 0.83), ink, P.mix(spec.field, ink, 0.5))
    return cover


# ---------------- 7. DUOTONE SPLIT (no image) ----------------
def duotone_split(spec, image=None):
    cover = Image.new("RGB", (W, H), spec.field)
    split = int(H * 0.60)
    cover.paste(P.gradient((W, split), spec.deep, P.darken(spec.deep, 0.18)), (0, 0))
    dr = ImageDraw.Draw(cover)
    dr.rectangle([0, split - 6, W, split], fill=spec.accent)
    tf, lines, _ = fit_title(dr, _case(spec.title, spec.title_case), spec.serif, W - 2 * M, H * 0.24, start=182)
    y = draw_lines(dr, lines, tf, W // 2, int(H * 0.13), P.CREAM, shadow=(2, 3, P.darken(spec.deep, 0.3)))
    sf = get_font(spec.serif, "italic", 54)
    draw_lines(dr, _wrap(dr, spec.subtitle, sf, W - 2 * int(M * 1.3)), sf, W // 2, y + 12, P.lighten(spec.accent, 0.3))
    ink = P.best_contrast(spec.field, [P.INK, spec.deep])
    zone = (W * 0.30, split + int(H * 0.04), W * 0.70, split + int(H * 0.14))
    S.draw_symbol_set(cover, spec.motif, zone, spec.count, _sym_color(cover, zone, spec), spec.seed)
    series_band(dr, spec, W // 2, int(H * 0.82), P.darken(spec.accent, 0.1))
    byline(dr, spec, W // 2, int(H * 0.90), ink, P.mix(spec.field, ink, 0.5))
    return cover


# ---------------- 8. STRIPE MINIMAL (no image) ----------------
def stripe_minimal(spec, image=None):
    cover = P.grain(Image.new("RGB", (W, H), spec.field), 4).convert("RGB")
    dr = ImageDraw.Draw(cover)
    sw = int(W * 0.17)
    cover.paste(P.gradient((sw, H), spec.deep, P.darken(spec.deep, 0.22)), (0, 0))
    dr.rectangle([sw, 0, sw + 6, H], fill=spec.accent)
    ink = P.best_contrast(spec.field, [P.INK, spec.deep])
    lx = sw + 80
    tw = W - lx - M
    tf, lines, _ = fit_title(dr, _case(spec.title, spec.title_case), spec.serif, tw, H * 0.30, start=176)
    y = int(H * 0.24)
    y = draw_lines(dr, lines, tf, None, y, ink, align="left", x_left=lx)
    sf = get_font(spec.serif, "italic", 52)
    draw_lines(dr, _wrap(dr, spec.subtitle, sf, tw), sf, None, y + 14, P.darken(spec.accent, 0.1), align="left", x_left=lx)
    # symbols climb the stripe (count == book number)
    zone = (sw * 0.16, H * 0.30, sw * 0.84, H * 0.86)
    scol = P.best_contrast(spec.deep, [spec.accent, P.CREAM])
    S.draw_symbol_set(cover, spec.motif, zone, spec.count, scol, spec.seed, orientation="column")
    series_band(dr, spec, None, int(H * 0.80), P.darken(spec.accent, 0.1), align="left", x_left=lx)
    byline(dr, spec, None, int(H * 0.88), ink, P.mix(spec.field, ink, 0.5), align="left", x_left=lx)
    return cover


FAMILY_FN = {
    "full_bleed": full_bleed, "inset_card": inset_card, "panel_bands": panel_bands,
    "title_block": title_block, "gradient_solo": gradient_solo, "framed": framed,
    "duotone_split": duotone_split, "stripe_minimal": stripe_minimal,
}


def render(spec: Spec, image=None) -> Image.Image:
    fn = FAMILY_FN.get(spec.family, full_bleed)
    return fn(spec, image)
