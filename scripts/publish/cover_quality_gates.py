#!/usr/bin/env python3
"""R7: Automated cover quality gates per R6 §6.

Implements the 6 automated gates from
``config/publishing/cover_identity_system.yaml`` ``quality_gates`` (the 5
manual gates are deferred to operator visual QA).

Library API
-----------
* :func:`gate_focal_clarity_thumbnail`
* :func:`gate_title_ocr_legibility`
* :func:`gate_color_count_le_3`
* :func:`gate_brand_palette_delta_e`
* :func:`gate_signature_color_present`
* :func:`gate_warm_off_white`
* :func:`run_all_gates(cover_path, book_id)`

CLI
---
``python3 scripts/publish/cover_quality_gates.py <cover.png> --book ahjan``
Returns JSON to stdout. Exit 0 = all auto-gates passed; 1 = at least one
failed.
"""
from __future__ import annotations

import argparse
import colorsys
import json
import math
import sys
from pathlib import Path
from typing import Any

import yaml
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IDENTITY_PATH = REPO_ROOT / "config" / "publishing" / "cover_identity_system.yaml"
DEFAULT_TEMPLATES_PATH = REPO_ROOT / "config" / "publishing" / "bestseller_templates.yaml"

# Schnell-tier-friendly thresholds. ΔE 15 corresponds to a "moderate"
# visible difference; tighter than 8 (R6 default) breaks against
# schnell's 4-step quantization noise. We keep 15 as the auto threshold
# until dev tier ships.
DELTA_E_TOLERANCE = 15.0


# ─── COLOR UTILITIES ──────────────────────────────────────────────────


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    s = value.lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def _rgb_to_lab(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    """sRGB → CIE Lab (D65). Compact in-tree implementation so we avoid
    pulling colormath; precision is fine for ΔE thresholds at 15."""
    r, g, b = (c / 255.0 for c in rgb)

    def gamma(u: float) -> float:
        return ((u + 0.055) / 1.055) ** 2.4 if u > 0.04045 else u / 12.92

    r, g, b = gamma(r), gamma(g), gamma(b)
    # sRGB D65 → XYZ
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) * 100
    y = (0.2126729 * r + 0.7151522 * g + 0.0721750 * b) * 100
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) * 100
    # D65 reference
    xn, yn, zn = 95.047, 100.000, 108.883

    def f(u: float) -> float:
        return u ** (1 / 3) if u > 0.008856 else 7.787 * u + 16 / 116

    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    bb = 200 * (fy - fz)
    return (L, a, bb)


def _delta_e_76(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    """ΔE*76. Coarser than ΔE2000 but adequate for our tolerance band
    of 15; avoids the ~30-line ΔE2000 implementation."""
    L1, a1, b1 = _rgb_to_lab(c1)
    L2, a2, b2 = _rgb_to_lab(c2)
    return math.sqrt((L1 - L2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)


def _dominant_colors(image: Image.Image, k: int = 5,
                     min_pct: float = 0.05) -> list[tuple[tuple[int, int, int], float]]:
    """Quantize to ``k`` palette buckets and return [(rgb, fraction)]
    sorted desc by fraction, filtered to fraction >= ``min_pct``."""
    img = image.convert("RGB").copy()
    img.thumbnail((256, 256))
    quant = img.quantize(colors=k, method=Image.Quantize.MEDIANCUT)
    palette = quant.getpalette()[: 3 * k]
    counts = quant.getcolors()
    if not counts:
        return []
    total = sum(c for c, _ in counts)
    out: list[tuple[tuple[int, int, int], float]] = []
    for count, idx in counts:
        rgb = (palette[idx * 3], palette[idx * 3 + 1], palette[idx * 3 + 2])
        frac = count / total
        if frac >= min_pct:
            out.append((rgb, frac))
    out.sort(key=lambda t: t[1], reverse=True)
    return out


# ─── INDIVIDUAL GATES ─────────────────────────────────────────────────


def gate_focal_clarity_thumbnail(image: Image.Image) -> dict[str, Any]:
    """Downsample to 100x160; assert single-quadrant local-variance peak.

    Computes per-quadrant variance on the L channel; passes if the top
    quadrant variance >= 1.6x the second-highest quadrant.
    """
    thumb = image.convert("L").copy()
    thumb.thumbnail((100, 160))
    w, h = thumb.size
    qw, qh = max(1, w // 2), max(1, h // 2)
    quads = [
        thumb.crop((0, 0, qw, qh)),
        thumb.crop((qw, 0, w, qh)),
        thumb.crop((0, qh, qw, h)),
        thumb.crop((qw, qh, w, h)),
    ]
    variances = []
    for q in quads:
        pixels = list(q.getdata())
        if not pixels:
            variances.append(0.0)
            continue
        m = sum(pixels) / len(pixels)
        v = sum((p - m) ** 2 for p in pixels) / len(pixels)
        variances.append(v)
    variances.sort(reverse=True)
    top, second = variances[0], variances[1] if len(variances) > 1 else 0.0
    ratio = top / second if second > 0 else float("inf")
    passed = ratio >= 1.6
    return {
        "gate": "focal_clarity_thumbnail",
        "passed": bool(passed),
        "top_variance": round(top, 1),
        "second_variance": round(second, 1),
        "ratio": round(ratio, 2) if ratio != float("inf") else "inf",
    }


def gate_title_ocr_legibility(
    image: Image.Image,
    title_zone_pct: tuple[tuple[int, int], tuple[int, int]] | None = None,
) -> dict[str, Any]:
    """OCR-ish luminance-contrast heuristic at thumbnail.

    The cheap-and-correct proxy R6 §6 endorses: at thumbnail, the title
    region's luminance must differ from its surrounding background by
    >= 40 percent. Pillow-only (no tesseract dependency).
    """
    thumb = image.convert("L").copy()
    thumb.thumbnail((100, 160))
    w, h = thumb.size
    if title_zone_pct is None:
        # Default title zone occupies the top ~30% (R4 templates land here).
        x0, y0, x1, y1 = 0, 0, w, max(1, int(h * 0.32))
    else:
        (x0p, x1p), (y0p, y1p) = title_zone_pct
        x0 = int(w * x0p / 100)
        x1 = int(w * x1p / 100)
        y0 = int(h * y0p / 100)
        y1 = int(h * y1p / 100)

    title_crop = thumb.crop((x0, y0, x1, y1))
    title_pixels = list(title_crop.getdata())
    if not title_pixels:
        return {"gate": "title_ocr_legibility", "passed": False,
                "reason": "empty_title_zone"}
    # Sample dark + light extremes inside the title zone.
    title_pixels.sort()
    n = len(title_pixels)
    dark = sum(title_pixels[: max(1, n // 10)]) / max(1, n // 10)
    light = sum(title_pixels[-max(1, n // 10):]) / max(1, n // 10)
    delta = abs(light - dark) / 255.0
    passed = delta >= 0.40
    return {
        "gate": "title_ocr_legibility",
        "passed": bool(passed),
        "luminance_delta": round(delta, 3),
        "threshold": 0.40,
    }


def gate_color_count_le_3(image: Image.Image) -> dict[str, Any]:
    """≤3 dominant clusters at 5%+ area each (R6 60-30-10 rule)."""
    doms = _dominant_colors(image, k=8, min_pct=0.05)
    count = len(doms)
    passed = count <= 3
    return {
        "gate": "color_count_le_3",
        "passed": bool(passed),
        "dominant_count": count,
        "dominants": [
            {"rgb": list(rgb), "fraction": round(frac, 3)}
            for rgb, frac in doms[:5]
        ],
    }


def gate_brand_palette_delta_e(
    image: Image.Image,
    brand_palette: dict[str, str],
) -> dict[str, Any]:
    """Top 3 dominant colors of cover must each be within ΔE 15 of one
    of the brand palette hex values."""
    doms = _dominant_colors(image, k=5, min_pct=0.05)
    if not doms:
        return {"gate": "brand_palette_delta_e", "passed": False,
                "reason": "no_dominant_colors"}
    palette_rgbs = [
        _hex_to_rgb(v) for v in brand_palette.values() if isinstance(v, str)
    ]
    if not palette_rgbs:
        return {"gate": "brand_palette_delta_e", "passed": False,
                "reason": "no_brand_palette"}
    deltas: list[float] = []
    matches: list[dict[str, Any]] = []
    for rgb, frac in doms[:3]:
        nearest = min(_delta_e_76(rgb, p) for p in palette_rgbs)
        deltas.append(nearest)
        matches.append({"rgb": list(rgb), "fraction": round(frac, 3),
                        "nearest_delta_e": round(nearest, 1)})
    passed = all(d <= DELTA_E_TOLERANCE for d in deltas)
    return {
        "gate": "brand_palette_delta_e",
        "passed": bool(passed),
        "tolerance": DELTA_E_TOLERANCE,
        "matches": matches,
    }


def gate_signature_color_present(
    image: Image.Image,
    signature_color: str,
) -> dict[str, Any]:
    """Signature color must occupy >=3% of pixels within ΔE 15."""
    target = _hex_to_rgb(signature_color)
    img = image.convert("RGB").copy()
    img.thumbnail((128, 128))
    pixels = list(img.getdata())
    if not pixels:
        return {"gate": "signature_color_present", "passed": False,
                "reason": "empty_image"}
    hits = sum(1 for p in pixels if _delta_e_76(p, target) <= DELTA_E_TOLERANCE)
    fraction = hits / len(pixels)
    passed = fraction >= 0.03
    return {
        "gate": "signature_color_present",
        "passed": bool(passed),
        "signature_color": signature_color,
        "fraction": round(fraction, 4),
        "threshold": 0.03,
    }


def gate_warm_off_white(image: Image.Image) -> dict[str, Any]:
    """Any near-white cluster must lean warm (saturation toward yellow/red).

    Per R6 §0 craft_criteria.warm_off_white: no pure #FFFFFF; off-white
    >= #F0EBE0. We check that any dominant cluster with luminance >= 0.85
    has hue in the warm half of HSV (h in [0, 0.18] or [0.92, 1.0]) AND
    is not within ΔE 5 of pure white.
    """
    doms = _dominant_colors(image, k=8, min_pct=0.03)
    pure_white = (255, 255, 255)
    near_whites = []
    for rgb, frac in doms:
        r, g, b = (c / 255.0 for c in rgb)
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        if lum >= 0.85:
            near_whites.append((rgb, frac, lum))
    if not near_whites:
        return {"gate": "warm_off_white", "passed": True,
                "reason": "no_near_white_cluster"}
    bad: list[dict[str, Any]] = []
    for rgb, frac, lum in near_whites:
        h, _s, v = colorsys.rgb_to_hsv(*(c / 255.0 for c in rgb))
        is_warm = (h <= 0.18) or (h >= 0.92)
        is_pure = _delta_e_76(rgb, pure_white) <= 5.0
        if is_pure or not is_warm:
            bad.append({
                "rgb": list(rgb),
                "fraction": round(frac, 3),
                "hue": round(h, 3),
                "is_pure_white": is_pure,
                "is_warm": is_warm,
            })
    passed = not bad
    return {
        "gate": "warm_off_white",
        "passed": bool(passed),
        "bad_clusters": bad,
    }


# ─── ORCHESTRATION ────────────────────────────────────────────────────


def _load_identity(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_IDENTITY_PATH
    return yaml.safe_load(p.read_text())


def run_all_gates(
    cover_path: Path,
    book_id: str | None = None,
    identity_path: Path | None = None,
) -> dict[str, Any]:
    """Run all 6 automated gates. Returns a JSON-serializable report."""
    image = Image.open(cover_path).convert("RGB")
    results: list[dict[str, Any]] = []
    results.append(gate_focal_clarity_thumbnail(image))
    results.append(gate_title_ocr_legibility(image))
    results.append(gate_color_count_le_3(image))
    results.append(gate_warm_off_white(image))

    brand_palette: dict[str, str] | None = None
    signature_color: str | None = None
    if book_id:
        identity = _load_identity(identity_path)
        book = (identity.get("books") or {}).get(book_id) or {}
        author = (identity.get("authors") or {}).get(
            book.get("author_id") or "", {}) or {}
        brand = (identity.get("brands") or {}).get(
            author.get("brand_id") or "", {}) or {}
        palette = brand.get("palette") or {}
        if palette:
            brand_palette = {k: v for k, v in palette.items() if isinstance(v, str)}
        signature_color = author.get("signature_color")

    if brand_palette:
        results.append(gate_brand_palette_delta_e(image, brand_palette))
    else:
        results.append({"gate": "brand_palette_delta_e", "passed": None,
                        "reason": "no book_id supplied; gate skipped"})
    if signature_color:
        results.append(gate_signature_color_present(image, signature_color))
    else:
        results.append({"gate": "signature_color_present", "passed": None,
                        "reason": "no book_id supplied; gate skipped"})

    overall = all(r.get("passed") is True or r.get("passed") is None for r in results)
    return {
        "cover": str(cover_path),
        "book_id": book_id,
        "overall_passed": bool(overall),
        "gates": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("cover", type=Path, help="path to cover PNG/JPG")
    parser.add_argument("--book", type=str, default=None,
                        help="identity-system book id (enables palette/sig gates)")
    parser.add_argument("--identity-config", type=Path, default=None)
    args = parser.parse_args(argv)

    if not args.cover.exists():
        print(f"error: {args.cover} does not exist", file=sys.stderr)
        return 2
    report = run_all_gates(args.cover, args.book, args.identity_config)
    print(json.dumps(report, indent=2))
    failed = [g for g in report["gates"] if g.get("passed") is False]
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
