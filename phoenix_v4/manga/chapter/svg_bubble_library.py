"""Vector speech-bubble templates (SVG) for Webtoon lettering V2.

Provides scalable bubble outlines for 9 legacy V1 styles plus 3 V2 shapes:
``wavy_supernatural``, ``off_panel``, ``singing``. Optional rasterization
via ``cairosvg`` when installed; otherwise callers fall back to Pillow
drawers from ``bubble_render`` so CI stays dependency-light.
"""
from __future__ import annotations

import math
from typing import Any

# IDs must match lettering_spec ``bubble_style`` enum + internal aliases.
BUBBLE_STYLE_IDS: tuple[str, ...] = (
    "round_normal",
    "spiky_emphasis",
    "cloud_thought",
    "square_narration",
    "whisper_dashed",
    "scream_ultra",
    "electronic_sharp",
    "drip_horror",
    "shojo_soft",
    "wavy_supernatural",
    "off_panel",
    "singing",
)


def _svg_wrap(view_w: int, view_h: int, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {view_w} {view_h}" width="{view_w}" height="{view_h}">'
        f"{body}</svg>"
    )


def bubble_svg(
    style_id: str,
    w: int,
    h: int,
    *,
    fill_rgba: tuple[int, int, int, int] = (255, 255, 255, 230),
    stroke_rgba: tuple[int, int, int, int] = (0, 0, 0, 255),
    stroke_width: float = 2.0,
) -> str:
    """Return standalone SVG markup for the bubble body (no tail).

    Tails stay vector-friendly when composited separately (PIL triangle);
    that matches print pipeline expectations and avoids fragile SVG joins.
    """
    rf, gf, bf, af = fill_rgba
    rs, gs, bs, aast = stroke_rgba
    fill = f"rgba({rf},{gf},{bf},{af / 255.0:.3f})"
    stroke = f"rgba({rs},{gs},{bs},{aast / 255.0:.3f})"
    cw, ch = w / 2, h / 2
    rx, ry = max(w / 2 - 4, 8), max(h / 2 - 4, 8)

    if style_id in ("round_normal", "shojo_soft"):
        body = (
            f'<ellipse cx="{cw:.1f}" cy="{ch:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )
    elif style_id == "square_narration":
        body = (
            f'<rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="4" ry="4" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )
    elif style_id == "electronic_sharp":
        body = (
            f'<polygon points="4,4 {w - 4},6 {w - 6},{h - 6} 6,{h - 4}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )
    elif style_id == "spiky_emphasis":
        pts = []
        spikes = 12
        for i in range(spikes * 2):
            ang = (math.tau / (spikes * 2)) * i
            rmul = rx + (4 if i % 2 else 0)
            x = cw + rmul * math.cos(ang)
            y = ch + ry * math.sin(ang)
            pts.append(f"{x:.1f},{y:.1f}")
        body = (
            f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{stroke_width}" stroke-linejoin="round"/>'
        )
    elif style_id == "scream_ultra":
        pts = []
        spikes = 18
        for i in range(spikes * 2):
            ang = (math.tau / (spikes * 2)) * i
            rmul = rx + (7 if i % 2 else 0)
            x = cw + rmul * math.cos(ang)
            y = ch + ry * math.sin(ang)
            pts.append(f"{x:.1f},{y:.1f}")
        stroke_scream = f"rgba({200},{0},{0},{255 / 255.0:.3f})"
        body = (
            f'<polygon points="{" ".join(pts)}" fill="{fill}" '
            f'stroke="{stroke_scream}" stroke-width="{stroke_width + 1}" '
            f'stroke-linejoin="round"/>'
        )
    elif style_id == "cloud_thought":
        circles = ""
        scallop_r = max(10, min(w, h) // 10)
        n = max(10, int(math.tau * max(rx, ry) / (scallop_r * 1.9)))
        for i in range(n):
            ang = math.tau * i / n
            sx = cw + max(0.0, rx - scallop_r * 0.5) * math.cos(ang)
            sy = ch + max(0.0, ry - scallop_r * 0.5) * math.sin(ang)
            circles += (
                f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{scallop_r}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width * 0.6:.1f}"/>'
            )
        body = (
            f'<ellipse cx="{cw:.1f}" cy="{ch:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
            f"{circles}"
        )
    elif style_id == "whisper_dashed":
        body = (
            f'<ellipse cx="{cw:.1f}" cy="{ch:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" '
            f'stroke-dasharray="6 5"/>'
        )
    elif style_id == "drip_horror":
        drips = ""
        for k in range(5):
            dx = 8 + (w - 24) * k / 4
            drips += (
                f'<path d="M {dx:.1f} {h - 6:.1f} Q {dx + 3:.1f} {h + 8:.1f} '
                f'{dx + 2:.1f} {h + 18:.1f}" fill="none" stroke="{stroke}" '
                f'stroke-width="{stroke_width * 0.8:.1f}"/>'
            )
        body = (
            f'<ellipse cx="{cw:.1f}" cy="{ch:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
            f"{drips}"
        )
    elif style_id == "wavy_supernatural":
        wave_pts = []
        sides = 64
        for i in range(sides):
            ang = math.tau * i / sides
            wav = 5 * math.sin(7 * ang)
            x = cw + (rx + wav) * math.cos(ang)
            y = ch + (ry + wav * 0.7) * math.sin(ang)
            wave_pts.append(f"{x:.1f},{y:.1f}")
        body = (
            f'<polygon points="{" ".join(wave_pts)}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}" '
            f'stroke-linejoin="round"/>'
        )
    elif style_id == "off_panel":
        body = (
            f'<rect x="{w * 0.45:.1f}" y="-8" width="{w * 0.55 + 10:.1f}" '
            f'height="{h + 18:.1f}" rx="14" ry="14" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}" '
            f'stroke-dasharray="5 8"/>'
        )
    elif style_id == "singing":
        notes = (
            f'<g fill="none" stroke="{stroke}" stroke-width="{max(1.5, stroke_width * 0.7):.1f}">'
            f'<ellipse cx="{w - 28:.1f}" cy="{16:.1f}" rx="12" ry="9" '
            f'fill="{fill}"/>'
            f'<ellipse cx="{w - 54:.1f}" cy="{10:.1f}" rx="9" ry="7" '
            f'fill="{fill}"/>'
            f'<path d="M {w - 16:.1f} {18:.1f} L {w - 16:.1f} {h * 0.35:.1f}"/>'
            f'<path d="M {w - 45:.1f} {12:.1f} L {w - 45:.1f} {h * 0.28:.1f}"/>'
            f"</g>"
        )
        body = (
            f'<ellipse cx="{cw:.1f}" cy="{ch:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
            f"{notes}"
        )
    else:
        body = (
            f'<ellipse cx="{cw:.1f}" cy="{ch:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )

    return _svg_wrap(w, h, body)


def svg_to_pil_rgba(svg_markup: str, *, width: int, height: int) -> Any | None:
    """Rasterize SVG to a PIL Image (RGBA) or None if no backend."""
    try:
        import cairosvg  # type: ignore
        from PIL import Image
        import io

        png = cairosvg.svg2png(
            bytestring=svg_markup.encode("utf-8"),
            output_width=width,
            output_height=height,
        )
        return Image.open(io.BytesIO(png)).convert("RGBA")
    except Exception:
        return None
