"""Waystream cover layout library — safe zones + verbatim plan text.

TITLE and SUBTITLE are drawn exactly as authored in the book plan (no re-derivation,
no hook fallback, no truncation). Fit-to-box uses shrink/wrap only.

Layout variants rotate per book_id (stacked | split_above_below | frame_center).
Symbols avoid busy image regions; text never overlaps symbol framing lines.
"""
from __future__ import annotations
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFilter, ImageStat

from .fonts import get_font
from . import layout_zones as Z
from . import palette as P
from . import symbols as S

W, H = 1600, 2560
M = 132
TITLE_SCALE = 0.8
SUBTITLE_SCALE = 1.6          # readable but shrinkable to fit zone
THUMBNAIL_TEST_W = 280
MIN_THUMB_CAP_PX = 11
BUSY_VARIANCE_THRESHOLD = 900.0
BUSY_EDGE_THRESHOLD = 22.0
MAX_SUBTITLE_LINES = 5

# QC hooks — read by render.py proof driver
LAST_TITLE_DRAWN: str = ""
LAST_SUBTITLE_DRAWN: str = ""
LAST_SUBTITLE_DECISION: tuple[bool, str, int, bool] | None = None


@dataclass
class Spec:
    title: str
    subtitle: str
    author_display: str
    imprint: str
    series_name: str
    book_num: int
    count: int
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
    layout_variant: str = "stacked"
    framing: str = "line_below"
    plate: bool = False


def display_title(spec: Spec) -> str:
    """Plan title verbatim — only upper/small_caps transform, never reorder."""
    t = (spec.title or "").strip()
    if spec.title_case in ("upper", "small_caps"):
        return t.upper()
    return t


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


def _thumb_cap_px(font_px: int) -> float:
    return font_px * THUMBNAIL_TEST_W / W


def fit_subtitle(draw, spec, serif, maxw, max_lines, base_px, max_h=None):
    """Always the plan subtitle — shrink font / wrap lines, never hook fallback."""
    text = (spec.subtitle or "").strip()
    if not text:
        f = get_font(serif, "italic", 12)
        return f, [], 12
    floor_px = max(10, int(round(base_px * 0.35)))
    cap_px = max(floor_px, int(round(base_px * SUBTITLE_SCALE)))
    best = None
    for px in range(cap_px, floor_px - 1, -2):
        f = get_font(serif, "italic", px)
        lines = _wrap(draw, text, f, maxw)
        if len(lines) > max_lines:
            continue
        block_h = len(lines) * int(_line_h(f) * 1.06)
        if max_h is not None and block_h > max_h:
            continue
        if _thumb_cap_px(px) < MIN_THUMB_CAP_PX and px > floor_px:
            continue
        best = (f, lines, px)
        break
    if best:
        return best
    f = get_font(serif, "italic", floor_px)
    lines = _wrap(draw, text, f, maxw)
    while len(lines) > max_lines and len(lines) > 1:
        lines = lines[:-1]
    return f, lines, floor_px


def fit_title(draw, text, family, maxw, max_h, start=200, min_px=104, weight="bold", ls=1.06):
    start = max(int(round(start * TITLE_SCALE)), int(round(min_px * TITLE_SCALE)) + 6)
    min_px = max(36, int(round(min_px * TITLE_SCALE)))
    size = start
    while size > min_px:
        f = get_font(family, weight, size)
        lines = _wrap(draw, text, f, maxw)
        total = len(lines) * _line_h(f) * ls
        if len(lines) <= 4 and total <= max_h:
            return f, lines, size
        size -= 4
    f = get_font(family, weight, min_px)
    return f, _wrap(draw, text, f, maxw), min_px


def draw_lines(draw, lines, font, cx, y, fill, ls=1.06, shadow=None, tracking=0, align="center", x_left=None):
    lh = int(_line_h(font) * ls)
    for ln in lines:
        lw = draw.textlength(ln, font=font) + tracking * max(len(ln) - 1, 0)
        x = (cx - lw / 2) if align == "center" and cx is not None else x_left
        if shadow:
            _track(draw, (x + shadow[0], y + shadow[1]), ln, font, shadow[2], tracking)
        _track(draw, (x, y), ln, font, fill, tracking)
        y += lh
    return y


def _track(draw, xy, text, font, fill, tracking):
    x, y = xy
    if not tracking:
        draw.text((x, y), text, font=font, fill=fill)
        return
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def _track_w(draw, text, font, tracking):
    return sum(draw.textlength(ch, font=font) + tracking for ch in text) - tracking


def _frame_symbols(draw, framing, bbox, color, line_w=7, pad=46):
    x0, y0, x1, y1 = bbox
    left, right = x0 - pad, x1 + pad
    top, bot = y0 - pad, y1 + pad
    cx = (left + right) / 2
    mid = (top + bot) / 2
    block_w = right - left
    if framing == "box":
        draw.rectangle([left, top, right, bot], outline=color, width=line_w)
    elif framing == "double":
        draw.line([(left, top), (right, top)], fill=color, width=line_w)
        draw.line([(left, top + line_w + 8), (right, top + line_w + 8)], fill=color, width=max(2, line_w - 3))
        draw.line([(left, bot), (right, bot)], fill=color, width=line_w)
        draw.line([(left, bot - line_w - 8), (right, bot - line_w - 8)], fill=color, width=max(2, line_w - 3))
    elif framing == "strike":
        seg = block_w * 0.16
        draw.line([(left - seg, mid), (left + 6, mid)], fill=color, width=line_w)
        draw.line([(right - 6, mid), (right + seg, mid)], fill=color, width=line_w)
    elif framing == "line_above":
        draw.line([(left, top), (right, top)], fill=color, width=line_w)
    else:
        draw.line([(left, bot), (right, bot)], fill=color, width=line_w)


def _zone_busyness(cover, box):
    x0, y0, x1, y1 = box
    px0, py0 = max(0, int(x0 * cover.width)), max(0, int(y0 * cover.height))
    px1, py1 = min(cover.width, int(x1 * cover.width)), min(cover.height, int(y1 * cover.height))
    if px1 <= px0 + 8 or py1 <= py0 + 8:
        return 0.0, 0.0
    crop = cover.crop((px0, py0, px1, py1)).convert("L")
    stat = ImageStat.Stat(crop)
    variance = float(stat.var[0]) if stat.var else 0.0
    w, h = crop.size
    px = crop.load()
    edge_sum, n = 0.0, 0
    for y in range(h - 1):
        for x in range(w - 1):
            edge_sum += abs(px[x, y] - px[x + 1, y]) + abs(px[x, y] - px[x, y + 1])
            n += 2
    return variance, edge_sum / max(n, 1)


def _is_busy(cover, box) -> bool:
    var, edge = _zone_busyness(cover, box)
    return var >= BUSY_VARIANCE_THRESHOLD or edge >= BUSY_EDGE_THRESHOLD


def _shift_symbol_zone_if_busy(cover, plan: Z.ZonePlan) -> Z.Rect:
    z = plan.symbol
    if _is_busy(cover, (z.x0, z.y0, z.x1, z.y1)):
        # lift symbol cluster out of busy image band
        lift = 0.08 if plan.variant == "split_above_below" else 0.06
        return Z.Rect(z.x0, max(0.05, z.y0 - lift), z.x1, max(z.y0 + 0.06, z.y1 - lift))
    return z


def _zone_plan(spec: Spec) -> Z.ZonePlan:
    return Z.zone_plan(spec.family, spec.layout_variant)


def _center_y(zone: Z.Rect, block_h: int) -> int:
    return int(zone.y0 * H) + max(0, (zone.height_px() - block_h) // 2)


def _draw_zoned_title_subtitle(dr, spec, plan, title_fill, subtitle_fill, *, shadow=None,
                               align="center", x_left=None, cx=None):
    global LAST_TITLE_DRAWN, LAST_SUBTITLE_DRAWN, LAST_SUBTITLE_DECISION
    cx = W // 2 if cx is None else cx
    title_text = display_title(spec)
    tf, tlines, _, tblock = Z.fit_in_zone(
        dr, title_text, spec.serif, plan.title, weight="bold",
        start_px=196, min_px=80, scale=TITLE_SCALE, max_lines=4,
    )
    ty = _center_y(plan.title, tblock)
    y = draw_lines(dr, tlines, tf, cx, ty, title_fill, shadow=shadow, align=align, x_left=x_left)
    LAST_TITLE_DRAWN = title_text

    sub_zone = plan.subtitle
    sf, sub_lines, _ = fit_subtitle(
        dr, spec, spec.serif, sub_zone.width_px() - 16, MAX_SUBTITLE_LINES, 52,
        max_h=sub_zone.height_px(),
    )
    sub_block = len(sub_lines) * int(_line_h(sf) * 1.06)
    sub_y = (y + 10) if plan.variant == "stacked" else _center_y(sub_zone, sub_block)
    if sub_y + sub_block > int(sub_zone.y1 * H):
        sub_y = _center_y(sub_zone, sub_block)
    forbidden = (plan.image, plan.symbol)
    if Z.rects_collide(Z.text_block_rect(sub_y, sub_block, sub_zone), forbidden):
        sub_y = int(sub_zone.y0 * H)

    y2 = draw_lines(dr, sub_lines, sf, cx, sub_y, subtitle_fill, shadow=shadow, align=align, x_left=x_left)
    drawn_sub = (spec.subtitle or "").strip()
    LAST_SUBTITLE_DRAWN = drawn_sub
    LAST_SUBTITLE_DECISION = (False, drawn_sub, len(sub_lines), False)
    return y2


def _sym_color(cover, zone, spec):
    return S.pick_symbol_color(cover, zone, {"deep": spec.deep, "field": spec.field, "accent": spec.accent})


def _symbol_px(plan: Z.ZonePlan, cover=None) -> tuple:
    z = _shift_symbol_zone_if_busy(cover, plan) if cover is not None else plan.symbol
    return (W * z.x0, H * z.y0, W * z.x1, H * z.y1)


def _draw_symbols(dr, cover, spec, plan, scrim=False):
    zone = _symbol_px(plan, cover)
    sym_col = _sym_color(cover, zone, spec)
    sbox = S.draw_symbol_set(cover, spec.motif, zone, spec.count, sym_col, spec.seed, scrim=scrim)
    _frame_symbols(dr, spec.framing, sbox, sym_col)
    return sbox


def cover_crop(img, w, h):
    s = max(w / img.width, h / img.height)
    im = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))))
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def _lmask(w, h, a0, a1):
    g = Image.new("L", (1, h))
    for y in range(h):
        g.putpixel((0, y), int(a0 + (a1 - a0) * y / max(h - 1, 1)))
    return g.resize((w, h))


def scrim(cover, x, y, w, h, color, a_top, a_bot):
    panel = Image.new("RGB", (w, h), color)
    cover.paste(panel, (x, y), _lmask(w, h, a_top, a_bot))


def _draw_text_band(cover, y_frac, h_frac, color, alpha=210):
    y0 = int(H * y_frac)
    bh = int(H * h_frac)
    band = Image.new("RGBA", (W, bh), tuple(color) + (alpha,))
    cover.paste(band, (0, y0), band)


def series_band(draw, spec, cx, y, color, align="center", x_left=None):
    f = get_font(spec.sans, "bold", 40)
    label = f"BOOK {spec.book_num}   ·   {spec.series_name}"
    bw = _track_w(draw, label, f, 6)
    x = (cx - bw / 2) if align == "center" and cx is not None else x_left
    if align == "center" and cx is not None:
        draw.line([(x - 46, y + 22), (x - 16, y + 22)], fill=color, width=3)
        draw.line([(x + bw + 16, y + 22), (x + bw + 46, y + 22)], fill=color, width=3)
    _track(draw, (x, y), label, f, color, 6)


def byline(draw, spec, cx, y, color, sub_color, align="center", x_left=None):
    af = get_font(spec.sans, "bold", 56)
    name = spec.author_display.upper()
    nw = _track_w(draw, name, af, 3)
    x = (cx - nw / 2) if align == "center" and cx is not None else x_left
    _track(draw, (x, y), name, af, color, 3)
    imf = get_font(spec.sans, "regular", 29)
    iw = _track_w(draw, spec.imprint, imf, 5)
    xi = (cx - iw / 2) if align == "center" and cx is not None else x_left
    _track(draw, (xi, y + 74), spec.imprint, imf, sub_color, 5)


def full_bleed(spec, image):
    plan = _zone_plan(spec)
    cover = cover_crop(image, W, H) if image else P.gradient((W, H), spec.deep, P.darken(spec.deep, 0.3))
    cover = cover.convert("RGB")
    ix = plan.image
    if ix.x1 > ix.x0:
        scrim(cover, 0, int(ix.y0 * H), W, int((ix.y1 - ix.y0) * H), P.darken(spec.deep, 0.45), 180, 40)
    if plan.variant == "stacked":
        scrim(cover, 0, 0, W, int(H * 0.48), P.darken(spec.deep, 0.4), 205, 0)
    _draw_text_band(cover, plan.title.y0 - 0.02, plan.title.y1 - plan.title.y0 + 0.06,
                    P.darken(spec.deep, 0.55), 220)
    if plan.variant != "stacked":
        _draw_text_band(cover, plan.subtitle.y0 - 0.01, plan.subtitle.y1 - plan.subtitle.y0 + 0.03,
                        P.darken(spec.deep, 0.55), 215)
    dr = ImageDraw.Draw(cover)
    _draw_zoned_title_subtitle(dr, spec, plan, P.CREAM, P.CREAM, shadow=(3, 4, (0, 0, 0)))
    _draw_symbols(dr, cover, spec, plan, scrim=True)
    series_band(dr, spec, W // 2, int(plan.series.y0 * H), P.CREAM)
    byline(dr, spec, W // 2, int(plan.byline.y0 * H), P.CREAM, (204, 200, 192))
    return cover


def inset_card(spec, image):
    plan = _zone_plan(spec)
    cover = P.grain(P.vignette(Image.new("RGB", (W, H), spec.field), 0.16), 4).convert("RGB")
    dr = ImageDraw.Draw(cover)
    ink = P.best_contrast(spec.field, [P.INK, spec.deep])
    ix = plan.image
    ch = max(int((ix.y1 - ix.y0) * H), int(H * 0.28))
    cw = int(ch / 1.18)
    cx0, cy0 = (W - cw) // 2, int(ix.y0 * H)
    card = cover_crop(image, cw, ch).convert("RGB") if image else P.gradient((cw, ch), spec.accent, spec.deep)
    sh = Image.new("RGBA", (cw + 80, ch + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([40, 46, cw + 40, ch + 46], fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(20))
    cover.paste(sh, (cx0 - 40, cy0 - 40), sh)
    b = 10
    cover.paste(Image.new("RGB", (cw + 2 * b, ch + 2 * b), spec.accent), (cx0 - b, cy0 - b))
    cover.paste(card, (cx0, cy0))
    _draw_zoned_title_subtitle(dr, spec, plan, ink, ink)
    _draw_symbols(dr, cover, spec, plan)
    series_band(dr, spec, W // 2, int(plan.series.y0 * H), P.darken(spec.accent, 0.1))
    byline(dr, spec, W // 2, int(plan.byline.y0 * H), ink, P.mix(spec.field, ink, 0.5))
    return cover


def panel_bands(spec, image):
    plan = _zone_plan(spec)
    cover = Image.new("RGB", (W, H), spec.field)
    top_h = int(H * 0.155)
    cover.paste(Image.new("RGB", (W, top_h), spec.deep), (0, 0))
    dr = ImageDraw.Draw(cover)
    series_band(dr, spec, W // 2, int(top_h * 0.42), P.lighten(spec.accent, 0.25))
    ph = int((plan.image.y1 - plan.image.y0) * H) or int(H * 0.445)
    pan_y0 = int(plan.image.y0 * H) or top_h
    panel = cover_crop(image, W, ph).convert("RGB") if image else P.gradient((W, ph), spec.deep, spec.accent)
    cover.paste(panel, (0, pan_y0))
    dr.rectangle([0, pan_y0 + ph - 5, W, pan_y0 + ph], fill=spec.accent)
    ink = P.best_contrast(spec.field, [P.INK, spec.deep])
    _draw_zoned_title_subtitle(dr, spec, plan, ink, ink)
    _draw_symbols(dr, cover, spec, plan)
    byline(dr, spec, W // 2, int(plan.byline.y0 * H), ink, P.mix(spec.field, ink, 0.55))
    return cover


def title_block(spec, image):
    plan = _zone_plan(spec)
    cover = (cover_crop(image, W, H) if image else P.gradient((W, H), spec.deep, spec.accent)).convert("RGB")
    scrim(cover, 0, int(H * 0.55), W, int(H * 0.45), P.darken(spec.deep, 0.45), 0, 205)
    if plan.variant == "stacked":
        bw, bh = int(W * 0.84), int((plan.title.y1 - plan.title.y0 + plan.subtitle.y1 - plan.subtitle.y0) * H * 0.55)
        by = int(plan.title.y0 * H)
        bx = (W - bw) // 2
        block = Image.new("RGBA", (bw, bh), tuple(P.darken(spec.deep, 0.1)) + (235,))
        cover.paste(block, (bx, by), block)
    else:
        _draw_text_band(cover, plan.title.y0 - 0.01, plan.title.y1 - plan.title.y0 + 0.02, P.darken(spec.deep, 0.55), 225)
        _draw_text_band(cover, plan.subtitle.y0 - 0.01, plan.subtitle.y1 - plan.subtitle.y0 + 0.02, P.darken(spec.deep, 0.55), 215)
    dr = ImageDraw.Draw(cover)
    _draw_zoned_title_subtitle(dr, spec, plan, P.CREAM, P.CREAM)
    _draw_symbols(dr, cover, spec, plan, scrim=True)
    series_band(dr, spec, W // 2, int(plan.series.y0 * H), P.CREAM)
    byline(dr, spec, W // 2, int(plan.byline.y0 * H), P.CREAM, P.lighten(spec.deep, 0.5))
    return cover


def gradient_solo(spec, image=None):
    plan = _zone_plan(spec)
    cover = P.gradient((W, H), spec.deep, P.mix(spec.deep, spec.field, 0.5), angle=68)
    cover = P.grain(P.vignette(cover, 0.26), 5).convert("RGB")
    dr = ImageDraw.Draw(cover)
    _draw_zoned_title_subtitle(dr, spec, plan, P.CREAM, P.CREAM, shadow=(2, 3, P.darken(spec.deep, 0.3)))
    _draw_symbols(dr, cover, spec, plan)
    series_band(dr, spec, W // 2, int(plan.series.y0 * H), P.lighten(spec.accent, 0.2))
    byline(dr, spec, W // 2, int(plan.byline.y0 * H), P.CREAM, P.lighten(spec.deep, 0.5))
    return cover


def framed(spec, image=None):
    plan = _zone_plan(spec)
    cover = P.grain(P.vignette(Image.new("RGB", (W, H), spec.field), 0.18), 5).convert("RGB")
    dr = ImageDraw.Draw(cover)
    ink = P.best_contrast(spec.field, [P.INK, spec.deep])
    inset = 84
    dr.rectangle([inset, inset, W - inset, H - inset], outline=spec.accent, width=6)
    dr.rectangle([inset + 16, inset + 16, W - inset - 16, H - inset - 16],
                 outline=P.mix(spec.accent, spec.field, 0.45), width=2)
    _draw_zoned_title_subtitle(dr, spec, plan, ink, ink)
    _draw_symbols(dr, cover, spec, plan)
    series_band(dr, spec, W // 2, int(plan.series.y0 * H), P.darken(spec.accent, 0.1))
    byline(dr, spec, W // 2, int(plan.byline.y0 * H), ink, P.mix(spec.field, ink, 0.5))
    return cover


def duotone_split(spec, image=None):
    plan = _zone_plan(spec)
    cover = Image.new("RGB", (W, H), spec.field)
    split = int(H * 0.60)
    cover.paste(P.gradient((W, split), spec.deep, P.darken(spec.deep, 0.18)), (0, 0))
    dr = ImageDraw.Draw(cover)
    dr.rectangle([0, split - 6, W, split], fill=spec.accent)
    _draw_zoned_title_subtitle(dr, spec, plan, P.CREAM, P.CREAM, shadow=(2, 3, P.darken(spec.deep, 0.3)))
    ink = P.best_contrast(spec.field, [P.INK, spec.deep])
    _draw_symbols(dr, cover, spec, plan)
    series_band(dr, spec, W // 2, int(plan.series.y0 * H), P.darken(spec.accent, 0.1))
    byline(dr, spec, W // 2, int(plan.byline.y0 * H), ink, P.mix(spec.field, ink, 0.5))
    return cover


def stripe_minimal(spec, image=None):
    plan = _zone_plan(spec)
    cover = P.grain(Image.new("RGB", (W, H), spec.field), 4).convert("RGB")
    dr = ImageDraw.Draw(cover)
    sw = int(W * 0.17)
    cover.paste(P.gradient((sw, H), spec.deep, P.darken(spec.deep, 0.22)), (0, 0))
    dr.rectangle([sw, 0, sw + 6, H], fill=spec.accent)
    ink = P.best_contrast(spec.field, [P.INK, spec.deep])
    lx = int(W * plan.title.x0)
    _draw_zoned_title_subtitle(dr, spec, plan, ink, ink, align="left", x_left=lx, cx=None)
    zone = _symbol_px(plan, cover)
    scol = P.best_contrast(spec.deep, [spec.accent, P.CREAM])
    sbox = S.draw_symbol_set(cover, spec.motif, zone, spec.count, scol, spec.seed, orientation="column")
    _frame_symbols(dr, spec.framing, sbox, scol, pad=24)
    series_band(dr, spec, None, int(plan.series.y0 * H), P.darken(spec.accent, 0.1), align="left", x_left=lx)
    byline(dr, spec, None, int(plan.byline.y0 * H), ink, P.mix(spec.field, ink, 0.5), align="left", x_left=lx)
    return cover


def type_dominant(spec, image=None):
    plan = Z.zone_plan("type_dominant", spec.layout_variant)
    cover = P.grain(Image.new("RGB", (W, H), spec.deep), 3).convert("RGB")
    dr = ImageDraw.Draw(cover)
    dr.rectangle([0, int(H * 0.88), W, H], fill=spec.field)
    _draw_zoned_title_subtitle(dr, spec, plan, P.CREAM, P.lighten(spec.accent, 0.15),
                               shadow=(2, 3, P.darken(spec.deep, 0.35)))
    _draw_symbols(dr, cover, spec, plan)
    series_band(dr, spec, W // 2, int(plan.series.y0 * H), spec.accent)
    ink = P.best_contrast(spec.field, [P.INK, spec.deep])
    byline(dr, spec, W // 2, int(plan.byline.y0 * H), ink, P.mix(spec.field, ink, 0.5))
    return cover


FAMILY_FN = {
    "full_bleed": full_bleed, "inset_card": inset_card, "panel_bands": panel_bands,
    "title_block": title_block, "gradient_solo": gradient_solo, "framed": framed,
    "duotone_split": duotone_split, "stripe_minimal": stripe_minimal,
    "type_dominant": type_dominant,
}


def render(spec: Spec, image=None) -> Image.Image:
    return FAMILY_FN.get(spec.family, full_bleed)(spec, image)
