"""Color + gradient helpers. The point of this module is the CONTRAST guarantee:
the pilot shipped a light-blue symbol that vanished into a light background.
best_contrast() picks, from a candidate set, the color with the highest WCAG
contrast against the actual local background — so every symbol/byline is legible.
"""
from __future__ import annotations
import math

CREAM = (244, 236, 220)
INK = (33, 26, 18)
WHITE = (250, 247, 240)
BLACK = (12, 12, 14)


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _lin(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (_lin(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def best_contrast(bg: tuple[int, int, int], candidates: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    return max(candidates, key=lambda c: contrast(bg, c))


def mix(a, b, t: float):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def darken(rgb, t: float):
    return mix(rgb, (0, 0, 0), t)


def lighten(rgb, t: float):
    return mix(rgb, (255, 255, 255), t)


def is_dark(rgb) -> bool:
    return luminance(rgb) < 0.32


# ---- gradients / texture ----
try:
    import numpy as _np
    _HAVE_NP = True
except Exception:  # pragma: no cover
    _HAVE_NP = False

from PIL import Image, ImageDraw


def gradient(size, c0, c1, angle: float = 90.0) -> Image.Image:
    """Linear gradient c0->c1 across `size`. angle 90=top->bottom, 0=left->right,
    45=diagonal. Uses numpy when available; falls back to a 1-D vertical resize."""
    w, h = size
    if _HAVE_NP:
        yy, xx = _np.mgrid[0:h, 0:w].astype(_np.float32)
        rad = math.radians(angle)
        proj = xx * math.cos(rad) + yy * math.sin(rad)
        proj -= proj.min()
        m = proj.max()
        if m > 1e-6:
            proj /= m
        a = _np.array(c0, dtype=_np.float32)
        b = _np.array(c1, dtype=_np.float32)
        arr = a[None, None, :] * (1 - proj[..., None]) + b[None, None, :] * proj[..., None]
        return Image.fromarray(arr.astype("uint8"), "RGB")
    # fallback: vertical only
    col = Image.new("RGB", (1, h))
    for y in range(h):
        col.putpixel((0, y), mix(c0, c1, y / max(h - 1, 1)))
    return col.resize((w, h))


def vignette(img: Image.Image, strength: float = 0.22) -> Image.Image:
    """Darken edges subtly so flat fields don't read as PowerPoint."""
    w, h = img.size
    if _HAVE_NP:
        yy, xx = _np.mgrid[0:h, 0:w].astype(_np.float32)
        cx, cy = w / 2, h / 2
        d = _np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2)
        d = _np.clip(d / 1.42, 0, 1)
        mask = (1 - strength * (d ** 2.2))
        arr = _np.asarray(img).astype(_np.float32) * mask[..., None]
        return Image.fromarray(_np.clip(arr, 0, 255).astype("uint8"), "RGB")
    return img


def grain(img: Image.Image, amount: int = 6) -> Image.Image:
    """Fine film grain to kill the digital-flat look."""
    if not _HAVE_NP or amount <= 0:
        return img
    w, h = img.size
    noise = _np.random.default_rng(7).integers(-amount, amount + 1, size=(h, w, 1)).astype(_np.float32)
    arr = _np.asarray(img).astype(_np.float32) + noise
    return Image.fromarray(_np.clip(arr, 0, 255).astype("uint8"), "RGB")


def sample_region(img: Image.Image, box) -> tuple[int, int, int]:
    """Average RGB of a region (x0,y0,x1,y1) — used to pick contrasting marks."""
    x0, y0, x1, y1 = (int(v) for v in box)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(img.width, x1), min(img.height, y1)
    if x1 <= x0 or y1 <= y0:
        return (128, 128, 128)
    crop = img.crop((x0, y0, x1, y1)).convert("RGB")
    crop = crop.resize((16, 16))
    if _HAVE_NP:
        a = _np.asarray(crop).reshape(-1, 3).mean(axis=0)
        return (int(a[0]), int(a[1]), int(a[2]))
    px = list(crop.getdata())
    n = len(px)
    return tuple(sum(c[i] for c in px) // n for i in range(3))
