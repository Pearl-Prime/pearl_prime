"""Abstract cover-art backgrounds + deterministic per-author fingerprint.

Replaces the flat type-dominant ("imagery_zone: null") cover path — which
shipped covers that were just a flat color + text with no imagery (the
"amateur orange cover" the operator flagged 2026-06-19) — with a generative
**gradient + minimal topic symbol** rendered deterministically in PIL (no GPU,
no paid API).

The same machinery doubles as the **anti-spam fingerprint**: a stable,
per-author signature derived from ``brand_id`` + ``author_id`` so that

  * same author  -> same look, every time (brand recognition), and
  * different author -> guaranteed-different look (KDP near-duplicate covers
    are flagged as spam).

Named teachers seed their gradient from the brand palette (so the cover stays
on-brand); everyone else — including the 336 composite brands that carry no
named author — derives a unique, tasteful palette from a hash of their id, so
NO cover is ever left on the identical-template fallback.

Consumed by ``scripts/publish/render_kdp_cover.py`` (the text pipeline composites
title/subtitle/author on top of the background this module returns).
"""
from __future__ import annotations

import colorsys
import hashlib
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CANVAS_W, CANVAS_H = 1600, 2560
_SS = 2  # supersample so vector symbols/edges stay crisp after downscale

# ── author-id reconciliation ────────────────────────────────────────────────
# The catalog (brand_admin_brands.json) uses ``sai_ma``; the identity system
# uses ``sai_maa``. Normalise so the same teacher always hashes to one
# fingerprint regardless of which spelling a caller passes. (Full registry
# merge is tracked separately; this keeps the runtime single-source.)
_AUTHOR_ALIASES = {"sai_ma": "sai_maa"}


def _norm_author(author_id: str | None) -> str | None:
    if not author_id:
        return author_id
    return _AUTHOR_ALIASES.get(author_id, author_id)


# ── color helpers ────────────────────────────────────────────────────────────
def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, int(c))) for c in rgb))


def _lum(rgb: tuple[int, int, int]) -> float:
    return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255.0


def _hsv(h: float, s: float, v: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return (int(r * 255), int(g * 255), int(b * 255))


# ── topic -> symbol motif ────────────────────────────────────────────────────
# Semantic, minimal, abstract. The fingerprint chooses the *treatment*
# (style variant / accent / placement); the topic chooses the *meaning*.
TOPIC_SYMBOL = {
    "imposter_syndrome": "twin_rings",   # the gap between who you are / who you fear being
    "boundaries": "divider",             # the line you draw
    "self_worth": "whole_circle",        # completeness / "enough"
    "overthinking": "spark_trio",        # racing thoughts
    "anxiety": "breath",                 # concentric calm
    "sleep_anxiety": "whole_circle",
    "burnout": "downslope",
    "grief": "single_dot",
    "courage": "upslope",
    "loss": "slash",
    "depression": "downslope",
}
_FALLBACK_MOTIFS = ["twin_rings", "divider", "whole_circle", "breath",
                    "spark_trio", "upslope"]


def fingerprint(
    author_id: str | None,
    brand_id: str | None,
    genre: str,
    *,
    primary_hex: str | None = None,
    secondary_hex: str | None = None,
    accent_hex: str | None = None,
) -> dict[str, Any]:
    """Deterministic cover signature.

    Seeds the gradient from the brand/genre palette when one is supplied (so
    named teachers stay on-brand), else derives a unique palette from the id
    hash (composites). Per-author hash bytes drive hue jitter, gradient
    direction, symbol style variant and accent so two authors never collide.
    """
    aid = _norm_author(author_id) or ""
    h = hashlib.sha256(f"{brand_id or ''}|{aid}|{genre}".encode()).digest()

    if primary_hex:
        base = _hex_to_rgb(primary_hex)
        bh, bs, bv = colorsys.rgb_to_hsv(*[c / 255.0 for c in base])
        jitter = (h[0] / 255.0 - 0.5) * 0.10          # +/- ~18 deg, per author
        top = _hsv(bh + jitter, min(1.0, bs * 1.04 + 0.02), max(bv, 0.52))
        bottom = _hsv(bh + jitter, min(1.0, bs * 1.10 + 0.08),
                      max(0.14, (bv if bv < 0.5 else bv) - 0.40))
    else:
        hue = h[0] / 255.0
        sat = 0.42 + h[1] / 255.0 * 0.30
        val = 0.58 + h[2] / 255.0 * 0.22
        top = _hsv(hue, sat, val)
        bottom = _hsv(hue, min(1.0, sat + 0.16), max(0.14, val - 0.42))

    if accent_hex:
        accent = _hex_to_rgb(accent_hex)
    else:
        th, _ts, _tv = colorsys.rgb_to_hsv(*[c / 255.0 for c in top])
        accent = _hsv(th + 0.45 + h[3] / 255.0 * 0.12, 0.66, 0.86)

    motif = TOPIC_SYMBOL.get(genre) or _FALLBACK_MOTIFS[h[6] % len(_FALLBACK_MOTIFS)]
    return {
        "grad_top": top,
        "grad_bottom": bottom,
        "accent": accent,
        "motif": motif,
        "direction": "diagonal" if h[5] % 2 else "vertical",
        "style_var": h[7] % 3,
        # Premium display face for the title, varied per author (Playfair vs
        # EB Garamond) — upgrades the plain sans default and adds variation.
        "title_family": ("display", "serif")[h[4] % 2],
        "seeded": bool(primary_hex),
    }


# ── gradient + vignette ──────────────────────────────────────────────────────
def _gradient(top: tuple[int, int, int], bottom: tuple[int, int, int],
              direction: str, w: int, h: int) -> Image.Image:
    a, b = np.array(top, float), np.array(bottom, float)
    if direction == "diagonal":
        yy, xx = np.mgrid[0:h, 0:w]
        t = (((xx / w) + (yy / h)) / 2.0)[..., None]
    else:
        t = np.linspace(0.0, 1.0, h)[:, None, None]
    img = np.broadcast_to(a * (1 - t) + b * t, (h, w, 3))
    return Image.fromarray(img.astype("uint8"), "RGB").convert("RGBA")


def _vignette(canvas: Image.Image, w: int, h: int, strength: int = 46) -> None:
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    alpha = (np.clip((d - 0.6) / 0.7, 0, 1) * strength).astype("uint8")
    v = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    v.putalpha(Image.fromarray(alpha, "L"))
    canvas.alpha_composite(v)


# ── symbol drawing (in supersampled pixel space) ─────────────────────────────
def _draw_symbol(dr: ImageDraw.ImageDraw, motif: str, style_var: int,
                 cx: int, cy: int, scale: int, accent: tuple[int, int, int]) -> None:
    a = accent + (235,)
    wd = max(2, int(scale * 0.085))

    if motif == "twin_rings":
        r, off = int(scale * 0.92), int(scale * 0.42)
        if style_var == 2:  # vertical offset pair
            for dy in (-off, off):
                dr.ellipse([cx - r, cy + dy - r, cx + r, cy + dy + r], outline=a, width=wd)
        else:
            for dx in (-off, off):
                dr.ellipse([cx + dx - r, cy - r, cx + dx + r, cy + r], outline=a, width=wd)
            if style_var == 1:  # one ring softly filled
                rr = int(r * 0.92)
                dr.ellipse([cx - off - rr, cy - rr, cx - off + rr, cy + rr],
                           fill=accent + (60,))
    elif motif == "divider":
        half = int(scale * 1.05)
        gap = int(scale * 0.16)
        dr.line([cx, cy - half, cx, cy - gap], fill=a, width=wd)
        dr.line([cx, cy + gap, cx, cy + half], fill=a, width=wd)
        dr.ellipse([cx - wd, cy - wd, cx + wd, cy + wd], fill=a)
        if style_var == 2:  # add side ticks
            t = int(scale * 0.35)
            dr.line([cx - t, cy - half, cx + t, cy - half], fill=a, width=wd)
            dr.line([cx - t, cy + half, cx + t, cy + half], fill=a, width=wd)
    elif motif == "whole_circle":
        R, r = int(scale * 0.95), int(scale * 0.5)
        dr.ellipse([cx - R, cy - R, cx + R, cy + R], outline=a, width=wd)
        fill = accent + (255,) if style_var != 1 else accent + (120,)
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    elif motif == "breath":
        for i, frac in enumerate((0.5, 0.72, 0.94)):
            R = int(scale * frac)
            if style_var == 1:
                dr.ellipse([cx - R, cy - R, cx + R, cy + R], outline=a, width=wd)
            else:
                dr.arc([cx - R, cy - R, cx + R, cy + R], 200, 340, fill=a, width=wd)
    elif motif == "spark_trio":
        for i, dx in enumerate((-0.55, 0.0, 0.55)):
            rr = int(scale * (0.16 + i * 0.07))
            X = cx + int(scale * dx)
            Y = cy - int(scale * i * 0.28)
            dr.ellipse([X - rr, Y - rr, X + rr, Y + rr], fill=a)
    elif motif in ("upslope", "downslope", "slash"):
        x0, x1 = cx - scale, cx + scale
        if motif == "upslope":
            y0, y1 = cy + int(scale * 0.6), cy - int(scale * 0.6)
        elif motif == "downslope":
            y0, y1 = cy - int(scale * 0.6), cy + int(scale * 0.6)
        else:  # slash
            y0, y1 = cy + int(scale * 0.9), cy - int(scale * 0.9)
        dr.line([x0, y0, x1, y1], fill=a, width=int(wd * 1.3))
        dr.ellipse([x1 - wd, y1 - wd, x1 + wd, y1 + wd], fill=a)
    else:  # single_dot
        r = int(scale * 0.42)
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=a)


def _zone_center_scale(symbol_zone: dict[str, Any] | None, w: int, h: int):
    if not symbol_zone:
        x0, y0, x1, y1 = 0.30, 0.56, 0.70, 0.80
    else:
        x0, x1 = symbol_zone["x_pct"][0] / 100, symbol_zone["x_pct"][1] / 100
        y0, y1 = symbol_zone["y_pct"][0] / 100, symbol_zone["y_pct"][1] / 100
    cx = int(w * (x0 + x1) / 2)
    cy = int(h * (y0 + y1) / 2)
    scale = int(min(w * (x1 - x0), h * (y1 - y0)) * 0.42)
    return cx, cy, scale


def _recommended_text(canvas: Image.Image, title_zone: dict[str, Any] | None):
    """Sample the title-zone region of the *final* background and pick a text
    color + stroke. Mid/dark zones -> warm cream + black stroke (the operator's
    'white text + black outline reads on anything'); light zones -> deep ink."""
    if title_zone:
        x0 = int(CANVAS_W * title_zone["x_pct"][0] / 100)
        x1 = int(CANVAS_W * title_zone["x_pct"][1] / 100)
        y0 = int(CANVAS_H * title_zone["y_pct"][0] / 100)
        y1 = int(CANVAS_H * title_zone["y_pct"][1] / 100)
    else:
        x0, y0, x1, y1 = 0, int(CANVAS_H * 0.12), CANVAS_W, int(CANVAS_H * 0.42)
    crop = np.asarray(canvas.convert("RGB").crop((x0, y0, x1, y1)), float)
    mean = crop.reshape(-1, 3).mean(axis=0)
    zone_lum = (0.299 * mean[0] + 0.587 * mean[1] + 0.114 * mean[2]) / 255.0
    if zone_lum > 0.62:
        return "#241A12", 0, "#241A12"          # deep ink on a light field, no stroke
    return "#F4ECDC", None, "#0D0D0D"           # warm cream + black stroke (width set by caller)


def build_background(
    genre: str,
    *,
    primary_hex: str,
    secondary_hex: str | None = None,
    accent_hex: str | None = None,
    author_id: str | None = None,
    brand_id: str | None = None,
    symbol_zone: dict[str, Any] | None = None,
    title_zone: dict[str, Any] | None = None,
) -> tuple[Image.Image, dict[str, Any]]:
    """Render a 1600x2560 RGBA abstract background (gradient + fingerprint
    symbol). Returns (canvas, meta) where meta carries the fingerprint summary
    and the recommended title text color / stroke for the renderer to apply."""
    fp = fingerprint(author_id, brand_id, genre,
                     primary_hex=primary_hex, secondary_hex=secondary_hex,
                     accent_hex=accent_hex)
    w, h = CANVAS_W * _SS, CANVAS_H * _SS
    canvas = _gradient(fp["grad_top"], fp["grad_bottom"], fp["direction"], w, h)
    _vignette(canvas, w, h)

    sym_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(sym_layer)
    cx, cy, scale = _zone_center_scale(symbol_zone, w, h)
    _draw_symbol(dr, fp["motif"], fp["style_var"], cx, cy, scale, fp["accent"])
    canvas.alpha_composite(sym_layer)

    bg = canvas.resize((CANVAS_W, CANVAS_H), Image.LANCZOS)

    text_hex, stroke_px, stroke_hex = _recommended_text(bg, title_zone)
    meta = {
        "abstract_background": True,
        "fingerprint_motif": fp["motif"],
        "fingerprint_style_var": fp["style_var"],
        "fingerprint_seeded": fp["seeded"],
        "title_family": fp["title_family"],
        "fingerprint_direction": fp["direction"],
        "grad_top_hex": _rgb_to_hex(fp["grad_top"]),
        "grad_bottom_hex": _rgb_to_hex(fp["grad_bottom"]),
        "accent_hex": _rgb_to_hex(fp["accent"]),
        "text_hex": text_hex,
        "stroke_hex": stroke_hex,
        "stroke_default_px": stroke_px,   # None -> caller applies role-scaled width
    }
    return bg, meta
