#!/usr/bin/env python3
"""Cheap semantic-failure gate for manga bank-layer PNGs.

Byte size alone is not quality. FLUX jobs can mark COMPLETED and land multi-MB
PNGs that are still dark noise / soft gradients with no scene structure
(the 2026-07-08 mecha L0 hangar/cockpit failure mode).

This gate rejects:
  - hard floor: small_edge < 3.0 (true noise blobs ~0.9–1.1)
  - low structure after Gaussian blur (noise washes out; real linework remains)
  - low edge density at heavy downsample on bright/white plates
  - all-dark soft plates (dark fraction + low blur-edge structure)
  - salt-pepper noise (high hf_ratio with weak mid-scale structure)

Usage:
    PYTHONPATH=. python3 scripts/manga/bank_layer_blob_gate.py path/to.png
    PYTHONPATH=. python3 scripts/manga/bank_layer_blob_gate.py --dir image_bank/
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageFilter

import numpy as np

# Calibrated 2026-07-08 against:
#   FAIL: mecha queue blobs jobs 513–514 (small_edge ~0.9–1.1, edge_blur8 ~0.37)
#   FAIL: white-backdrop noise blobs (high hf_ratio, low blur structure)
#   PASS: repaired hangar (small_edge ~3.9, edge_blur8 ~1.1 — dark but architectural)
#   PASS: repaired cockpit (small_edge ~6.8), flux-schnell covers (~11)
# Calibrated 2026-07-10 (prompt-builder v3 lane):
#   FAIL: seated_cockpit stipple-noise blob (small_edge ~7.3 PASS under v1 gate)
#         blue/cyan cast on bright plate + high local HF after blur
#   PASS: master_wu Qwen pose plates, mira_aoki_reference_qwen.png
HARD_EDGE_FLOOR = 3.0
MIN_SMALL_EDGE = 6.5
MIN_BLUR_EDGE = 0.80
MAX_HF_RATIO = 6.0
DARK_MEAN_CEILING = 40.0
DARK_FRAC_CEILING = 0.70
STIPPLE_MEAN_FLOOR = 175.0
STIPPLE_HF_FLOOR = 12.0
STIPPLE_BLUE_DOM_FLOOR = 15.0


@dataclass(frozen=True)
class BlobMetrics:
    path: str
    mean: float
    dark_frac: float
    edge_blur8: float
    small_edge: float
    bytes: int
    hf_local: float = 0.0
    blue_dom_bright: float = 0.0


@dataclass(frozen=True)
class BlobVerdict:
    ok: bool
    reasons: list[str]
    metrics: BlobMetrics

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "reasons": list(self.reasons),
            "metrics": asdict(self.metrics),
        }


def _mean_neighbor_edge(gray: Image.Image) -> float:
    """Mean abs adjacent-pixel delta (horiz+vert)/2 on an 8-bit L image."""
    w, h = gray.size
    pix = gray.load()
    edge_h = 0.0
    n_h = 0
    for y in range(h):
        for x in range(w - 1):
            edge_h += abs(pix[x + 1, y] - pix[x, y])
            n_h += 1
    edge_v = 0.0
    n_v = 0
    for x in range(w):
        for y in range(h - 1):
            edge_v += abs(pix[x, y + 1] - pix[x, y])
            n_v += 1
    return (edge_h / max(n_h, 1) + edge_v / max(n_v, 1)) / 2.0


def _stipple_metrics(im: Image.Image) -> tuple[float, float]:
    """Return (hf_local, blue_dom_bright) on a downsampled RGB work image."""
    rgb = im.convert("RGB").resize((270, 480), Image.Resampling.BILINEAR)
    gray = rgb.convert("L")
    arr = np.array(gray)
    blur = gray.filter(ImageFilter.GaussianBlur(radius=3))
    ba = np.array(blur)
    hf_local = float(np.abs(arr.astype(float) - ba.astype(float)).mean())
    ra = np.array(rgb)
    r, b = ra[:, :, 0], ra[:, :, 2]
    bright = arr > 180
    if bright.any():
        blue_dom = float(b[bright].mean() - r[bright].mean())
    else:
        blue_dom = 0.0
    return hf_local, blue_dom


def measure_png(path: Path) -> BlobMetrics:
    im = Image.open(path).convert("RGB")
    gray = im.convert("L")
    work = gray.resize((135, 240), Image.Resampling.BILINEAR)
    blur8 = work.filter(ImageFilter.GaussianBlur(radius=2))
    edge_blur8 = _mean_neighbor_edge(blur8)

    small = gray.resize((54, 96), Image.Resampling.BILINEAR)
    small_edge = _mean_neighbor_edge(small)

    hist = work.histogram()
    total = sum(hist) or 1
    mean = sum(i * c for i, c in enumerate(hist)) / total
    dark_frac = sum(hist[: int(DARK_MEAN_CEILING)]) / total
    hf_local, blue_dom_bright = _stipple_metrics(im)
    return BlobMetrics(
        path=str(path),
        mean=float(mean),
        dark_frac=float(dark_frac),
        edge_blur8=float(edge_blur8),
        small_edge=float(small_edge),
        bytes=path.stat().st_size,
        hf_local=float(hf_local),
        blue_dom_bright=float(blue_dom_bright),
    )


def judge_png(path: Path) -> BlobVerdict:
    m = measure_png(path)
    reasons: list[str] = []
    hf_ratio = m.small_edge / max(m.edge_blur8, 1e-6)

    if m.small_edge < HARD_EDGE_FLOOR:
        reasons.append(f"small_edge={m.small_edge:.2f}<{HARD_EDGE_FLOOR}")
    elif m.small_edge < MIN_SMALL_EDGE:
        # Dark architectural L0 plates can sit at small_edge≈3.5–5 if blur structure survives.
        if m.edge_blur8 < MIN_BLUR_EDGE:
            reasons.append(
                f"low_blur_structure small_edge={m.small_edge:.2f} "
                f"edge_blur8={m.edge_blur8:.3f}<{MIN_BLUR_EDGE}"
            )
        elif m.dark_frac > DARK_FRAC_CEILING:
            reasons.append(f"dark_soft_plate dark_frac={m.dark_frac:.2f}")
    if (
        hf_ratio > MAX_HF_RATIO
        and m.small_edge >= HARD_EDGE_FLOOR
        and m.edge_blur8 < MIN_BLUR_EDGE
    ):
        reasons.append(f"hf_noise_ratio={hf_ratio:.2f}>{MAX_HF_RATIO}")
    if (
        m.mean > STIPPLE_MEAN_FLOOR
        and m.hf_local > STIPPLE_HF_FLOOR
        and m.blue_dom_bright > STIPPLE_BLUE_DOM_FLOOR
    ):
        reasons.append(
            f"stipple_white_plate mean={m.mean:.1f} hf={m.hf_local:.1f} "
            f"blue_dom={m.blue_dom_bright:.1f}"
        )
    return BlobVerdict(ok=not reasons, reasons=reasons, metrics=m)


def assert_not_blob(path: Path) -> BlobVerdict:
    """Raise RuntimeError if PNG fails the semantic structure gate."""
    v = judge_png(path)
    if not v.ok:
        raise RuntimeError(
            f"BLOB_FAIL {path}: {', '.join(v.reasons)} "
            f"(bytes={v.metrics.bytes} is NOT proof of quality)"
        )
    return v


def is_blob_png(path: Path) -> bool:
    return not judge_png(path).ok


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--dir", type=Path, help="Scan directory recursively for PNGs")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    files: list[Path] = list(args.paths)
    if args.dir:
        files.extend(sorted(args.dir.rglob("*.png")))
    if not files:
        ap.error("provide paths and/or --dir")

    exit_code = 0
    rows = []
    for p in files:
        if not p.is_file():
            print(f"MISSING {p}", file=sys.stderr)
            exit_code = 1
            continue
        v = judge_png(p)
        rows.append(v.to_dict())
        tag = "PASS" if v.ok else "BLOB_FAIL"
        if not v.ok:
            exit_code = 1
        line = (
            f"{tag} {p} small_edge={v.metrics.small_edge:.2f} "
            f"edge_blur8={v.metrics.edge_blur8:.3f} dark={v.metrics.dark_frac:.2f} "
            f"bytes={v.metrics.bytes}"
            + (f" reasons={v.reasons}" if v.reasons else "")
        )
        print(line, file=sys.stdout if args.json else sys.stderr)
    if args.json:
        print(json.dumps({"results": rows}, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
