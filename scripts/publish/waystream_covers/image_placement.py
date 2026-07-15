"""Image-aware type placement — saliency/free-space analysis for photo backgrounds.

WHY THIS EXISTS
---------------
`templates.py` already places type inside fixed zone grids and already knows how
to detect a busy region (`_zone_busyness` / `_is_busy`) and how to keep a font
legible at thumbnail size (`_thumb_cap_px` / `MIN_THUMB_CAP_PX`). What it does
NOT do is *choose* where the title goes based on the photograph underneath: the
zone plan is picked from the book_id, not from the image.

This module adds exactly that missing step, additively:

    analyze_bands()  -> per-band busyness/luminance over a downsampled image
    choose_placement() -> pick the quietest band that fits the type block
    decide_treatment() -> plain / scrim / backing box, from measured busyness
    ink_for()        -> cream vs dark ink, from measured luminance
    thumbnail_ok()   -> reuse the production thumbnail legibility rule

It imports the production thresholds rather than restating them, so the busy
verdict here cannot silently drift from the renderer's.

SCOPE: this module is consumed by the NON-PRODUCTION example builder
(`scripts/publish/build_cover_social_examples.py`). No production cover path
imports it. It adds no behaviour to existing renderer modules.

DETERMINISM: pure function of pixels + text metrics. No randomness, no clock,
no network. Same image + same text -> same placement.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

from PIL import Image, ImageFilter, ImageStat

from .templates import (
    BUSY_EDGE_THRESHOLD,
    BUSY_VARIANCE_THRESHOLD,
    MIN_THUMB_CAP_PX,
    THUMBNAIL_TEST_W,
)

# Analysis is done on a downsampled copy: the production `_zone_busyness` walks
# every pixel in pure Python, which is far too slow to scan many candidate bands
# on a 1600x2560 canvas. Downsampling preserves the variance/edge signal we need
# while keeping a full 12-topic build in seconds. `test_cover_social_recipes.py`
# pins this fast path against the production verdict on synthetic images.
ANALYSIS_W = 220

# A band quieter than this reads as usable negative space (sky, wall, water):
# set type directly on it, no backing.
QUIET_VARIANCE = BUSY_VARIANCE_THRESHOLD * 0.45   # 405.0
QUIET_EDGE = BUSY_EDGE_THRESHOLD * 0.45           # 9.9

TREATMENT_PLAIN = "plain"
TREATMENT_SCRIM = "scrim"
TREATMENT_BOX = "backing_box"

# Luminance (0-255) above which dark ink beats cream on the measured band.
LIGHT_BAND_LUMA = 150.0


@dataclass(frozen=True)
class BandStat:
    """Measured signal for one horizontal candidate band, in normalized y."""
    y0: float
    y1: float
    variance: float
    edge: float
    luma: float

    @property
    def busy(self) -> bool:
        return self.variance >= BUSY_VARIANCE_THRESHOLD or self.edge >= BUSY_EDGE_THRESHOLD

    @property
    def quiet(self) -> bool:
        return self.variance <= QUIET_VARIANCE and self.edge <= QUIET_EDGE

    def score(self) -> float:
        """Lower is calmer. Normalized so variance and edge contribute evenly."""
        return (self.variance / BUSY_VARIANCE_THRESHOLD) + (self.edge / BUSY_EDGE_THRESHOLD)


@dataclass(frozen=True)
class Placement:
    """Where the title goes and how it must be protected."""
    band: BandStat
    treatment: str
    ink: tuple[int, int, int]
    reason: str

    def as_dict(self) -> dict:
        d = asdict(self)
        d["band"] = {
            "y0": round(self.band.y0, 4),
            "y1": round(self.band.y1, 4),
            "variance": round(self.band.variance, 1),
            "edge": round(self.band.edge, 2),
            "luma": round(self.band.luma, 1),
            "busy": self.band.busy,
            "quiet": self.band.quiet,
        }
        return d


def _analysis_copy(img: Image.Image) -> Image.Image:
    """Deterministic greyscale downsample used for every measurement."""
    w, h = img.size
    if w <= 0 or h <= 0:
        raise ValueError("cannot analyze zero-size image")
    scale = ANALYSIS_W / float(w)
    target = (ANALYSIS_W, max(1, int(round(h * scale))))
    return img.convert("L").resize(target, Image.Resampling.LANCZOS)


def band_stat(analysis: Image.Image, y0: float, y1: float) -> BandStat:
    """Measure one band of an already-downsampled greyscale image."""
    y0 = max(0.0, min(1.0, y0))
    y1 = max(0.0, min(1.0, y1))
    if y1 <= y0:
        raise ValueError(f"invalid band: y0={y0} y1={y1}")
    w, h = analysis.size
    py0, py1 = int(y0 * h), max(int(y0 * h) + 1, int(y1 * h))
    crop = analysis.crop((0, py0, w, py1))
    stat = ImageStat.Stat(crop)
    variance = float(stat.var[0]) if stat.var else 0.0
    luma = float(stat.mean[0]) if stat.mean else 0.0
    # Mean gradient magnitude. FIND_EDGES leaves a 1px invalid border, so trim it.
    edges = crop.filter(ImageFilter.FIND_EDGES)
    ew, eh = edges.size
    if ew > 2 and eh > 2:
        edges = edges.crop((1, 1, ew - 1, eh - 1))
    edge = float(ImageStat.Stat(edges).mean[0]) if edges.size[0] and edges.size[1] else 0.0
    return BandStat(y0=y0, y1=y1, variance=variance, edge=edge, luma=luma)


def analyze_bands(
    img: Image.Image,
    *,
    block_h: float,
    candidates: tuple[float, ...] | None = None,
    step: float = 0.04,
    margin: float = 0.04,
) -> list[BandStat]:
    """Measure every candidate band of height `block_h` (normalized) top to bottom.

    `margin` keeps the scan away from the extreme canvas edges, where a title
    would collide with trim/safe-area anyway.
    """
    if not 0 < block_h < 1:
        raise ValueError(f"block_h must be in (0,1), got {block_h}")
    analysis = _analysis_copy(img)
    if candidates is None:
        tops: list[float] = []
        y = margin
        limit = 1.0 - margin - block_h
        while y <= limit + 1e-9:
            tops.append(round(y, 4))
            y += step
        if not tops:
            tops = [max(0.0, min(margin, 1.0 - block_h))]
    else:
        tops = [c for c in candidates if 0 <= c <= 1 - block_h]
        if not tops:
            tops = [max(0.0, min(margin, 1.0 - block_h))]
    return [band_stat(analysis, t, t + block_h) for t in tops]


def decide_treatment(band: BandStat) -> tuple[str, str]:
    """Measured busyness -> how the type must be protected. Returns (treatment, reason)."""
    if band.quiet:
        return TREATMENT_PLAIN, (
            f"band is quiet (var={band.variance:.0f}<={QUIET_VARIANCE:.0f}, "
            f"edge={band.edge:.1f}<={QUIET_EDGE:.1f}): type set directly on negative space"
        )
    if band.busy:
        return TREATMENT_BOX, (
            f"band is busy (var={band.variance:.0f}, edge={band.edge:.1f} vs "
            f"var>={BUSY_VARIANCE_THRESHOLD:.0f} or edge>={BUSY_EDGE_THRESHOLD:.0f}): "
            "title needs an opaque backing box"
        )
    return TREATMENT_SCRIM, (
        f"band is mid-busy (var={band.variance:.0f}, edge={band.edge:.1f}): "
        "gradient scrim is enough to hold contrast"
    )


def ink_for(band: BandStat, cream: tuple[int, int, int], dark: tuple[int, int, int]) -> tuple[int, int, int]:
    """Pick ink from measured luminance.

    Only meaningful for TREATMENT_PLAIN: scrim/box impose their own dark ground,
    so cream always wins there (see `choose_placement`).
    """
    return dark if band.luma >= LIGHT_BAND_LUMA else cream


def choose_placement(
    img: Image.Image,
    *,
    block_h: float,
    cream: tuple[int, int, int],
    dark: tuple[int, int, int] = (24, 24, 26),
    candidates: tuple[float, ...] | None = None,
    step: float = 0.04,
    margin: float = 0.04,
    prefer: str | None = None,
) -> Placement:
    """Pick the calmest band that fits the type block, then decide its treatment.

    `prefer` ("top"|"bottom") only breaks ties between bands whose calmness is
    within 12% of each other — the image still decides, the recipe only nudges.
    """
    bands = analyze_bands(img, block_h=block_h, candidates=candidates, step=step, margin=margin)
    if not bands:
        raise ValueError("no candidate bands produced")
    best = min(bands, key=lambda b: b.score())

    if prefer in ("top", "bottom"):
        tol = best.score() * 1.12 + 1e-9
        near = [b for b in bands if b.score() <= tol]
        if near:
            best = min(near, key=lambda b: b.y0) if prefer == "top" else max(near, key=lambda b: b.y0)

    treatment, reason = decide_treatment(best)
    # A scrim/box lays a dark ground under the type, so cream is correct there
    # regardless of the photo's own luminance.
    ink = cream if treatment in (TREATMENT_SCRIM, TREATMENT_BOX) else ink_for(best, cream, dark)
    return Placement(band=best, treatment=treatment, ink=ink, reason=reason)


def thumb_cap_px(font_px: int, canvas_w: int) -> float:
    """Cap height this font would present at THUMBNAIL_TEST_W. Mirrors templates._thumb_cap_px."""
    return font_px * THUMBNAIL_TEST_W / float(canvas_w)


def thumbnail_ok(font_px: int, canvas_w: int) -> bool:
    """Production legibility rule: subtitle must survive a 280px-wide thumbnail."""
    return thumb_cap_px(font_px, canvas_w) >= MIN_THUMB_CAP_PX


def min_font_px_for_thumbnail(canvas_w: int) -> int:
    """Smallest font size that still passes `thumbnail_ok` on this canvas."""
    px = 1
    while not thumbnail_ok(px, canvas_w):
        px += 1
        if px > 10_000:  # unreachable guard
            raise RuntimeError("no font size satisfies thumbnail rule")
    return px
