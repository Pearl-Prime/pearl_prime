#!/usr/bin/env python3
"""Validate a rendered layer against its compiled class-A contract gates.

Per docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md §12 + §13.2 — Phase B.1 step 2.

V1 implements ONLY class-A contract validators (deterministic, FAIL severity):
  - backdrop_corner_check        (4-corner RGB sample vs declared backdrop)
  - subject_safe_zone            (non-backdrop bbox ⊆ compiled safe zone)
  - subject_does_not_touch_edge  (≥ margin_min_pct_all_sides clearance from canvas edge)
  - rembg_clean_alpha            (cutout alpha histogram bimodal at 0 and 255)
  - negative_space_in_bbox       (L0: archetype subject-placement region variance < 0.15)
  - effect_density               (L4: non-backdrop coverage 5-35%)
  - face_visible_threshold       (L2: upstream-supplied face_confidence > 0.85)
  - lettering_safe_zones_clear   (composite: bubble zones don't intersect subject bbox)

DEPENDENCY-FREE ON ML LIBRARIES.

The validator INSPECTS pipeline outputs (rendered PNGs, supplied metadata).
It does NOT invoke rembg, face detectors, CLIP, or any model. ML inference
happens upstream; this script checks what the pipeline produced.

Class-B / C / D scorers come in Phase B.2.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np
import yaml
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
DEFAULT_COMPILED_SAFE_ZONES = REPO / "config" / "manga" / "compiled" / "safe_zones.yaml"


Severity = Literal["FAIL", "WARN", "SCORE"]
ValidatorClass = Literal["A", "B", "C", "D"]


# ─────────────────────────────────────────────────────────────────────────────
# data structures
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class LayerValidationInput:
    """All inputs the validator needs to verify a rendered layer.

    Fields are populated by the orchestrator; validator never reads disk
    beyond what these paths point to.

    v0.6: L2 is two-stage (pre-cutout render + post-cutout RGBA). The
    cutout-stage checks operate on `cutout_image_path`; the pre-cutout
    image_path is kept for traceability but most pre-cutout gates SKIP for L2.
    """

    image_path: Path
    layer_type: str                              # L0/L1/L2/L3/L4
    safe_zone_row: dict                          # compiled row (one of `compiled` entries)
    archetype_metadata: dict | None = None       # subject_placement_bbox, archetype id, etc.
    cutout_image_path: Path | None = None        # rembg output (RGBA)
    cutout_policy: dict | None = None            # v0.6: per-archetype cutout contract
    face_confidence: float | None = None         # upstream face-detection result
    lettering_zones: list[list[float]] | None = None  # [[x_pct, y_pct, w_pct, h_pct], ...]


@dataclass
class ValidationResult:
    check_id: str
    class_: ValidatorClass
    severity: Severity
    passed: bool
    score: float                # 0.0 = perfect; 1.0 = worst
    evidence: dict[str, Any]
    remediation_hint: str
    skipped: bool = False        # True if check N/A for this layer
    skip_reason: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["class"] = d.pop("class_")
        return d


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────


def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    s = hex_str.lstrip("#")
    if len(s) != 6:
        raise ValueError(f"bad hex color {hex_str!r}")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def _na(check_id: str, reason: str, klass: ValidatorClass = "A", severity: Severity = "FAIL") -> ValidationResult:
    return ValidationResult(
        check_id=check_id,
        class_=klass,
        severity=severity,
        passed=True,
        score=0.0,
        evidence={},
        remediation_hint="",
        skipped=True,
        skip_reason=reason,
    )


def _fail(check_id: str, evidence: dict, hint: str, score: float = 1.0,
          klass: ValidatorClass = "A", severity: Severity = "FAIL") -> ValidationResult:
    return ValidationResult(
        check_id=check_id, class_=klass, severity=severity,
        passed=False, score=score, evidence=evidence, remediation_hint=hint,
    )


def _ok(check_id: str, evidence: dict, klass: ValidatorClass = "A", severity: Severity = "FAIL") -> ValidationResult:
    return ValidationResult(
        check_id=check_id, class_=klass, severity=severity,
        passed=True, score=0.0, evidence=evidence, remediation_hint="",
    )


def _subject_mask(image_path: Path, backdrop_rgb: tuple[int, int, int],
                  tolerance: int) -> tuple[np.ndarray, int, int]:
    """Return (H,W) boolean mask of non-backdrop pixels + (W, H)."""
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img, dtype=np.int16)
    W, H = img.size
    bg = np.array(backdrop_rgb, dtype=np.int16).reshape(1, 1, 3)
    diff = np.abs(arr - bg).max(axis=2)
    return diff > tolerance, W, H


# ─────────────────────────────────────────────────────────────────────────────
# class-A check: backdrop_corner_check
# ─────────────────────────────────────────────────────────────────────────────


def check_backdrop_corner(inp: LayerValidationInput, sample_px: int = 16) -> ValidationResult:
    if inp.layer_type == "L0":
        return _na("backdrop_corner_check", "L0 IS the scene; no isolated backdrop")
    if inp.layer_type == "L2":
        # v0.6 amendment: L2 renders include scene context. Backdrop is verified
        # at cutout time (background_bleed_check), not at render time.
        return _na("backdrop_corner_check",
                   "L2 v0.6: scene-context render; backdrop verified post-cutout via background_bleed_check")

    backdrop_hex = inp.safe_zone_row.get("backdrop_hex")
    if backdrop_hex is None:
        # Fall back to backdrop_name → standard mapping
        backdrop_name = inp.safe_zone_row.get("backdrop", "pure_white")
        backdrop_hex = {"pure_white": "#FFFFFF", "pure_black": "#000000",
                        "mid_gray": "#808080"}.get(backdrop_name, "#FFFFFF")
    bd_rgb = _hex_to_rgb(backdrop_hex)
    tolerance = inp.safe_zone_row.get("backdrop_corner_tolerance", 5)

    img = Image.open(inp.image_path).convert("RGB")
    arr = np.array(img, dtype=np.int16)
    H, W = arr.shape[:2]
    s = min(sample_px, H // 2, W // 2)

    corners = {
        "tl": arr[0:s, 0:s],
        "tr": arr[0:s, W - s:W],
        "bl": arr[H - s:H, 0:s],
        "br": arr[H - s:H, W - s:W],
    }
    results = {}
    failed = []
    for name, patch in corners.items():
        mean_rgb = patch.mean(axis=(0, 1)).round(1)
        max_delta = float(np.abs(mean_rgb - np.array(bd_rgb)).max())
        results[name] = {"mean_rgb": mean_rgb.tolist(), "max_delta": max_delta}
        if max_delta > tolerance:
            failed.append(name)

    if failed:
        worst_delta = max(r["max_delta"] for r in results.values())
        return _fail(
            "backdrop_corner_check",
            evidence={"corners": results, "expected_rgb": list(bd_rgb),
                      "tolerance": tolerance, "failed_corners": failed},
            hint=f"Backdrop drift at corners {failed}: max RGB delta {worst_delta:.1f} > tolerance {tolerance}. "
                 f"Re-render with explicit '#{backdrop_hex.lstrip('#')} NO COLOR NO SCENE' clause.",
            score=min(worst_delta / 255.0, 1.0),
        )
    return _ok("backdrop_corner_check",
               evidence={"corners": results, "expected_rgb": list(bd_rgb), "tolerance": tolerance})


# ─────────────────────────────────────────────────────────────────────────────
# class-A check: subject_safe_zone
# ─────────────────────────────────────────────────────────────────────────────


def check_subject_safe_zone(inp: LayerValidationInput) -> ValidationResult:
    if inp.layer_type == "L0":
        return _na("subject_safe_zone", "L0 has no isolated subject")

    zone = inp.safe_zone_row.get("subject_zone_pct")
    if zone is None:
        return _na("subject_safe_zone", "no zone declared (ELS or scene-fit)")

    # v0.6: L2 runs this check on the post-cutout RGBA, not the pre-cutout render.
    # If a cutout exists, use that; otherwise (L1/L3) use the rendered image.
    if inp.layer_type == "L2":
        if inp.cutout_image_path is None:
            return _na("subject_safe_zone",
                       "L2 v0.6: pre-cutout check skipped; provide cutout for post-cutout bbox validation")
        # For post-cutout, use alpha > 250 as the subject mask
        img = Image.open(inp.cutout_image_path)
        if img.mode != "RGBA":
            return _fail("subject_safe_zone", {"mode": img.mode}, "cutout must be RGBA")
        alpha = np.array(img.split()[-1])
        mask = alpha > 250
        W, H = img.size
    else:
        backdrop_hex = inp.safe_zone_row.get("backdrop_hex", "#FFFFFF")
        bd_rgb = _hex_to_rgb(backdrop_hex)
        tolerance = inp.safe_zone_row.get("backdrop_corner_tolerance", 5)
        mask, W, H = _subject_mask(inp.image_path, bd_rgb, tolerance)
    if not mask.any():
        return _fail(
            "subject_safe_zone",
            evidence={"reason": "no non-backdrop pixels detected"},
            hint="No subject visible — re-render with subject prompt clause restored.",
        )

    ys, xs = np.where(mask)
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))

    zone_w_pct, zone_h_pct = zone
    zone_w = W * zone_w_pct / 100
    zone_h = H * zone_h_pct / 100
    zone_x0 = (W - zone_w) / 2
    zone_y0 = (H - zone_h) / 2
    zone_x1 = zone_x0 + zone_w
    zone_y1 = zone_y0 + zone_h

    # V4.1: only flag overflow on axes declared must_not_touch=true
    axes_dict = inp.safe_zone_row.get("subject_must_not_touch_edge_axes") or {}
    v1_bool = inp.safe_zone_row.get("subject_must_not_touch_edge", True)
    if v1_bool is False:
        axes_must = {"top": False, "bottom": False, "left": False, "right": False}
    elif isinstance(axes_dict, dict):
        axes_must = {s: bool(axes_dict.get(s, True)) for s in ("top", "bottom", "left", "right")}
    else:
        axes_must = {"top": True, "bottom": True, "left": True, "right": True}

    overflow_all = {
        "left": max(0, zone_x0 - bbox[0]),
        "top": max(0, zone_y0 - bbox[1]),
        "right": max(0, bbox[2] - zone_x1),
        "bottom": max(0, bbox[3] - zone_y1),
    }
    overflow_guarded = {s: v for s, v in overflow_all.items() if axes_must[s] and v > 0}
    overflow_permitted = {s: v for s, v in overflow_all.items() if not axes_must[s] and v > 0}

    evidence = {
        "subject_bbox_px": list(bbox),
        "safe_zone_px": [round(zone_x0, 1), round(zone_y0, 1),
                         round(zone_x1, 1), round(zone_y1, 1)],
        "subject_zone_pct": list(zone),
        "canvas_size": [W, H],
        "axes_must_not_touch": axes_must,
        "overflow_px_all": {k: round(v, 1) for k, v in overflow_all.items()},
    }
    if overflow_permitted:
        evidence["overflow_permitted_px"] = {k: round(v, 1) for k, v in overflow_permitted.items()}
    if not overflow_guarded:
        return _ok("subject_safe_zone", evidence=evidence)
    evidence["overflow_guarded_px"] = {k: round(v, 1) for k, v in overflow_guarded.items()}
    return _fail(
        "subject_safe_zone",
        evidence=evidence,
        hint=f"Subject bbox extends outside safe zone on must_not_touch axes {list(overflow_guarded.keys())}. "
             f"safe_zone is {zone[0]}% x {zone[1]}%. Re-render with tighter framing on those axes "
             f"OR declare per-axis tolerance.",
        score=min(max(overflow_guarded.values()) / max(W, H), 1.0),
    )


# ─────────────────────────────────────────────────────────────────────────────
# class-A check: subject_does_not_touch_edge
# ─────────────────────────────────────────────────────────────────────────────


def check_subject_does_not_touch_edge(inp: LayerValidationInput) -> ValidationResult:
    if inp.layer_type == "L0":
        return _na("subject_does_not_touch_edge", "L0 IS the canvas")

    # V4.1 (spec §15.A.7): per-axis edge contract precedence:
    #   1. If v1 boolean subject_must_not_touch_edge is False → universal off-switch
    #      (preserves backward compat with archetype_exception=window_light_threshold)
    #   2. Else if per-axis dict subject_must_not_touch_edge_axes present → read per axis
    #   3. Else → all 4 axes guarded (v1.0 default)
    v1_bool = inp.safe_zone_row.get("subject_must_not_touch_edge", True)
    if v1_bool is False:
        return _na("subject_does_not_touch_edge",
                   "archetype_exception permits edge contact (all axes via v1 boolean)")

    axes_dict = inp.safe_zone_row.get("subject_must_not_touch_edge_axes")
    if isinstance(axes_dict, dict):
        axes_must = {
            "top": bool(axes_dict.get("top", True)),
            "bottom": bool(axes_dict.get("bottom", True)),
            "left": bool(axes_dict.get("left", True)),
            "right": bool(axes_dict.get("right", True)),
        }
        if not any(axes_must.values()):
            return _na("subject_does_not_touch_edge",
                       "all 4 axes permit edge contact (per-axis contract)")
    else:
        axes_must = {"top": True, "bottom": True, "left": True, "right": True}

    margin_min_pct = inp.safe_zone_row.get("margin_min_pct_all_sides", 5)

    # v0.6: L2 uses post-cutout alpha mask, not pre-cutout RGB mask.
    if inp.layer_type == "L2":
        if inp.cutout_image_path is None:
            return _na("subject_does_not_touch_edge",
                       "L2 v0.6: pre-cutout check skipped; provide cutout for post-cutout edge validation")
        img = Image.open(inp.cutout_image_path)
        if img.mode != "RGBA":
            return _fail("subject_does_not_touch_edge", {"mode": img.mode}, "cutout must be RGBA")
        alpha = np.array(img.split()[-1])
        mask = alpha > 250
        W, H = img.size
    else:
        backdrop_hex = inp.safe_zone_row.get("backdrop_hex", "#FFFFFF")
        bd_rgb = _hex_to_rgb(backdrop_hex)
        tolerance = inp.safe_zone_row.get("backdrop_corner_tolerance", 5)
        mask, W, H = _subject_mask(inp.image_path, bd_rgb, tolerance)
    if not mask.any():
        return _fail(
            "subject_does_not_touch_edge",
            evidence={"reason": "no subject visible"},
            hint="No subject visible.",
        )

    ys, xs = np.where(mask)
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
    margin_px = int(min(W, H) * margin_min_pct / 100)

    clearance = {
        "left": bbox[0],
        "top": bbox[1],
        "right": W - 1 - bbox[2],
        "bottom": H - 1 - bbox[3],
    }
    # V4.1: only flag insufficient on axes that must_not_touch is True
    insufficient = [s for s, v in clearance.items() if axes_must[s] and v < margin_px]
    permitted_touches = [s for s, v in clearance.items() if not axes_must[s] and v < margin_px]
    evidence = {
        "clearance_px": clearance,
        "required_min_px": margin_px,
        "required_min_pct": margin_min_pct,
        "axes_must_not_touch": axes_must,
        "subject_bbox_px": list(bbox),
        "canvas_size": [W, H],
    }
    if permitted_touches:
        evidence["permitted_edge_touches"] = permitted_touches
    if not insufficient:
        return _ok("subject_does_not_touch_edge", evidence=evidence)

    evidence["insufficient_sides"] = insufficient
    return _fail(
        "subject_does_not_touch_edge",
        evidence=evidence,
        hint=f"Subject too close to {','.join(insufficient)} edge(s) "
             f"(min clearance {margin_min_pct}% / {margin_px}px); "
             f"these axes are declared must_not_touch=true. "
             f"Re-render with explicit margin clause OR declare per-axis tolerance.",
        score=min(1.0 - (min(clearance[s] for s in insufficient) / max(margin_px, 1)), 1.0),
    )


# ─────────────────────────────────────────────────────────────────────────────
# class-A check: rembg_clean_alpha (validates rembg OUTPUT, doesn't run rembg)
# ─────────────────────────────────────────────────────────────────────────────


def check_rembg_clean_alpha(inp: LayerValidationInput) -> ValidationResult:
    if inp.cutout_image_path is None:
        return _na("rembg_clean_alpha", "no cutout image supplied — pipeline didn't run rembg")

    img = Image.open(inp.cutout_image_path)
    if img.mode != "RGBA":
        return _fail(
            "rembg_clean_alpha",
            evidence={"mode": img.mode},
            hint=f"Cutout must be RGBA, got {img.mode}. Re-export PNG with alpha channel.",
        )

    alpha = np.array(img.split()[-1])
    total = alpha.size
    fully_transparent = int((alpha <= 5).sum())
    fully_opaque = int((alpha >= 250).sum())
    gray_band = int(((alpha > 50) & (alpha < 200)).sum())
    gray_pct = gray_band / total * 100

    # v0.6: L2 scene-context renders have softer silhouettes than L1/L3 white-bg renders.
    # Threshold relaxed to 3% for L2; 1% retained for L1/L3/L4.
    threshold_pct = 3.0 if inp.layer_type == "L2" else 1.0

    evidence = {
        "fully_transparent_pct": round(fully_transparent / total * 100, 2),
        "fully_opaque_pct": round(fully_opaque / total * 100, 2),
        "gray_band_50_200_pct": round(gray_pct, 2),
        "bimodal_threshold_pct": threshold_pct,
        "layer_type": inp.layer_type,
    }
    if gray_pct >= threshold_pct:
        return _fail(
            "rembg_clean_alpha",
            evidence=evidence,
            hint=f"Alpha not bimodal: {gray_pct:.2f}% of pixels in gray band "
                 f"(>{threshold_pct}% threshold for {inp.layer_type}). "
                 f"rembg left soft edges. Try alpha_matting=True with stricter "
                 f"thresholds (foreground=240, background=10), or switch cutout "
                 f"model (u2net_human_seg <-> birefnet-portrait).",
            score=min(gray_pct / 100, 1.0),
        )
    return _ok("rembg_clean_alpha", evidence=evidence)


# ─────────────────────────────────────────────────────────────────────────────
# class-A check (v0.6): character_extraction_coverage
# ─────────────────────────────────────────────────────────────────────────────


def check_character_extraction_coverage(inp: LayerValidationInput) -> ValidationResult:
    """v0.6: confirm rembg didn't eat the character. Post-cutout opaque bbox
    area must be at least `coverage_min_pct` × declared safe-zone area."""
    if inp.cutout_image_path is None:
        return _na("character_extraction_coverage",
                   "no cutout supplied — pipeline didn't run rembg")
    if inp.layer_type not in ("L2", "L3"):
        return _na("character_extraction_coverage",
                   f"{inp.layer_type}-not-applicable (L2/L3 only)")

    zone = inp.safe_zone_row.get("subject_zone_pct")
    if zone is None:
        return _na("character_extraction_coverage",
                   "no subject_zone_pct declared (ELS or scene-fit)")

    img = Image.open(inp.cutout_image_path)
    if img.mode != "RGBA":
        return _fail(
            "character_extraction_coverage",
            evidence={"mode": img.mode},
            hint=f"Cutout must be RGBA, got {img.mode}.",
        )
    alpha = np.array(img.split()[-1])
    opaque = alpha > 250
    if not opaque.any():
        return _fail(
            "character_extraction_coverage",
            evidence={"reason": "no opaque pixels — character was eaten by cutout"},
            hint="Cutout produced fully-transparent output. Try alternate cutout model "
                 "or check the input render.",
        )

    ys, xs = np.where(opaque)
    bbox_w = int(xs.max() - xs.min())
    bbox_h = int(ys.max() - ys.min())
    bbox_area = bbox_w * bbox_h
    H, W = alpha.shape
    zone_area = (W * zone[0] / 100) * (H * zone[1] / 100)

    coverage_min_pct = (inp.cutout_policy or {}).get(
        "character_extraction_coverage_min_pct", 0.50
    )
    actual_ratio = bbox_area / zone_area if zone_area > 0 else 0.0

    evidence = {
        "bbox_dims_px": [bbox_w, bbox_h],
        "bbox_area_px": bbox_area,
        "safe_zone_area_px": int(zone_area),
        "coverage_ratio": round(actual_ratio, 3),
        "coverage_min_pct": coverage_min_pct,
        "canvas_size": [W, H],
    }
    if actual_ratio < coverage_min_pct:
        return _fail(
            "character_extraction_coverage",
            evidence=evidence,
            hint=f"Extracted character bbox is {actual_ratio*100:.1f}% of safe-zone area; "
                 f"required ≥ {coverage_min_pct*100:.0f}%. Cutout model may be too aggressive "
                 f"or character render too small. Try u2net_human_seg if using birefnet, or "
                 f"check the pre-cutout render quality.",
            score=1.0 - actual_ratio / max(coverage_min_pct, 0.01),
        )
    return _ok("character_extraction_coverage", evidence=evidence)


# ─────────────────────────────────────────────────────────────────────────────
# class-A check (v0.6): background_bleed_check
# ─────────────────────────────────────────────────────────────────────────────


def check_background_bleed(inp: LayerValidationInput, edge_inset_px: int = 20) -> ValidationResult:
    """v0.6: post-cutout, sample alpha in a 20px-inward edge frame.
    These pixels should be ≥95% transparent (alpha ≤ 30) — proves the scene
    background was removed even though it wasn't pure white."""
    if inp.cutout_image_path is None:
        return _na("background_bleed_check",
                   "no cutout supplied — pipeline didn't run rembg")
    if inp.layer_type not in ("L2", "L3"):
        return _na("background_bleed_check",
                   f"{inp.layer_type}-not-applicable (L2/L3 only)")

    img = Image.open(inp.cutout_image_path)
    if img.mode != "RGBA":
        return _fail(
            "background_bleed_check",
            evidence={"mode": img.mode},
            hint=f"Cutout must be RGBA, got {img.mode}.",
        )
    alpha = np.array(img.split()[-1])
    H, W = alpha.shape

    # V4.1: per-axis edge contract. Only measure bleed on must_not_touch axes
    # (per §12.3 limitation: bleed can't distinguish subject-body-at-edge from
    # scene-fragment-at-edge; for permitted-touch axes the bleed IS the subject,
    # not contamination).
    axes_dict = inp.safe_zone_row.get("subject_must_not_touch_edge_axes") or {}
    v1_bool = inp.safe_zone_row.get("subject_must_not_touch_edge", True)
    if v1_bool is False:
        axes_must = {s: False for s in ("top", "bottom", "left", "right")}
    elif isinstance(axes_dict, dict):
        axes_must = {s: bool(axes_dict.get(s, True)) for s in ("top", "bottom", "left", "right")}
    else:
        axes_must = {s: True for s in ("top", "bottom", "left", "right")}

    edge_bands = {
        "top": alpha[:edge_inset_px, :].flatten(),
        "bottom": alpha[-edge_inset_px:, :].flatten(),
        "left": alpha[:, :edge_inset_px].flatten(),
        "right": alpha[:, -edge_inset_px:].flatten(),
    }
    per_axis_bleed = {
        s: (round(float((b > 30).sum() / b.size * 100), 2) if b.size > 0 else 0.0)
        for s, b in edge_bands.items()
    }
    # Only count must_not_touch axes
    guarded_bands = [b for s, b in edge_bands.items() if axes_must[s]]
    if guarded_bands:
        guarded = np.concatenate(guarded_bands)
        bleed_pct = float((guarded > 30).sum() / guarded.size * 100)
    else:
        bleed_pct = 0.0

    max_bleed_pct = (inp.cutout_policy or {}).get("background_bleed_max_pct", 5.0)

    evidence = {
        "edge_inset_px": edge_inset_px,
        "axes_must_not_touch": axes_must,
        "per_axis_bleed_pct": per_axis_bleed,
        "guarded_axes_bleed_pct": round(bleed_pct, 2),
        "max_bleed_pct": max_bleed_pct,
    }
    if not any(axes_must.values()):
        return _na("background_bleed_check",
                   "all 4 axes permit edge contact; bleed check is moot for this archetype")
    if bleed_pct > max_bleed_pct:
        return _fail(
            "background_bleed_check",
            evidence=evidence,
            hint=f"Background bleed on guarded axes {bleed_pct:.2f}% > {max_bleed_pct}% threshold. "
                 f"Per-axis bleed: {per_axis_bleed}. Scene fragments remain on must_not_touch axes.",
            score=min(bleed_pct / 100, 1.0),
        )
    return _ok("background_bleed_check", evidence=evidence)


# ─────────────────────────────────────────────────────────────────────────────
# class-A check: negative_space_in_bbox (L0 only)
# ─────────────────────────────────────────────────────────────────────────────


def check_negative_space_in_bbox(inp: LayerValidationInput) -> ValidationResult:
    if inp.layer_type != "L0":
        return _na("negative_space_in_bbox", "L0-only check")

    bbox_pct = (inp.archetype_metadata or {}).get("subject_placement_bbox")
    if not bbox_pct or len(bbox_pct) != 4:
        return _na("negative_space_in_bbox", "no archetype subject_placement_bbox declared")

    img = Image.open(inp.image_path).convert("RGB")
    arr = np.array(img, dtype=np.float32)
    H, W = arr.shape[:2]

    x0 = int(W * bbox_pct[0] / 100)
    y0 = int(H * bbox_pct[1] / 100)
    x1 = int(W * (bbox_pct[0] + bbox_pct[2]) / 100)
    y1 = int(H * (bbox_pct[1] + bbox_pct[3]) / 100)
    x0, x1 = max(0, min(x0, x1)), max(x0, x1)
    y0, y1 = max(0, min(y0, y1)), max(y0, y1)

    if x1 - x0 < 2 or y1 - y0 < 2:
        return _na("negative_space_in_bbox", f"bbox region too small: ({x0},{y0})-({x1},{y1})")

    region = arr[y0:y1, x0:x1]
    variance = float(region.var() / (255.0 ** 2))
    threshold = 0.15
    evidence = {
        "variance_normalized": round(variance, 4),
        "threshold": threshold,
        "bbox_pct": list(bbox_pct),
        "bbox_px": [x0, y0, x1, y1],
    }
    if variance >= threshold:
        return _fail(
            "negative_space_in_bbox",
            evidence=evidence,
            hint=f"L0 background has detail at archetype's subject region "
                 f"(variance {variance:.3f} ≥ {threshold}). Re-render with explicit "
                 f"'generous empty space at {bbox_pct}' clause.",
            score=min(variance / threshold, 1.0) - 1.0 if variance >= threshold else 0.0,
        )
    return _ok("negative_space_in_bbox", evidence=evidence)


# ─────────────────────────────────────────────────────────────────────────────
# class-A check: effect_density (L4 only)
# ─────────────────────────────────────────────────────────────────────────────


def check_effect_density(inp: LayerValidationInput) -> ValidationResult:
    if inp.layer_type != "L4":
        return _na("effect_density", "L4-only check")

    backdrop_hex = inp.safe_zone_row.get("backdrop_hex", "#000000")
    bd_rgb = _hex_to_rgb(backdrop_hex)
    tolerance = inp.safe_zone_row.get("backdrop_corner_tolerance", 5)
    mask, W, H = _subject_mask(inp.image_path, bd_rgb, tolerance)
    coverage_pct = float(mask.sum() / mask.size * 100)
    min_pct, max_pct = 5.0, 35.0
    evidence = {
        "coverage_pct": round(coverage_pct, 2),
        "range": [min_pct, max_pct],
    }
    if not (min_pct <= coverage_pct <= max_pct):
        return _fail(
            "effect_density",
            evidence=evidence,
            hint=f"Atmospheric overlay coverage {coverage_pct:.1f}% outside range "
                 f"{min_pct}-{max_pct}%. Sparse effects (steam, dust, petals) "
                 f"should be ~5-35% non-backdrop.",
            score=min(abs(coverage_pct - (min_pct + max_pct) / 2) / 50.0, 1.0),
        )
    return _ok("effect_density", evidence=evidence)


# ─────────────────────────────────────────────────────────────────────────────
# class-A check: face_visible_threshold (uses upstream face_confidence)
# ─────────────────────────────────────────────────────────────────────────────


def check_face_visible_threshold(inp: LayerValidationInput, threshold: float = 0.85) -> ValidationResult:
    if inp.face_confidence is None:
        return _na("face_visible_threshold",
                   "no upstream face_confidence supplied (validator does not run ML)")
    evidence = {"face_confidence": inp.face_confidence, "threshold": threshold}
    if inp.face_confidence < threshold:
        return _fail(
            "face_visible_threshold",
            evidence=evidence,
            hint=f"Upstream face detection {inp.face_confidence:.2f} < threshold {threshold}. "
                 f"Re-render with explicit 'face visible, eyes open, frontal portrait' clause.",
            score=1.0 - inp.face_confidence,
        )
    return _ok("face_visible_threshold", evidence=evidence)


# ─────────────────────────────────────────────────────────────────────────────
# class-A check: lettering_safe_zones_clear (composite-level)
# ─────────────────────────────────────────────────────────────────────────────


def check_lettering_safe_zones_clear(inp: LayerValidationInput) -> ValidationResult:
    if not inp.lettering_zones:
        return _na("lettering_safe_zones_clear", "no lettering zones supplied")
    if inp.layer_type == "L0":
        return _na("lettering_safe_zones_clear", "L0 has no isolated subject to conflict with")

    backdrop_hex = inp.safe_zone_row.get("backdrop_hex", "#FFFFFF")
    bd_rgb = _hex_to_rgb(backdrop_hex)
    tolerance = inp.safe_zone_row.get("backdrop_corner_tolerance", 5)

    mask, W, H = _subject_mask(inp.image_path, bd_rgb, tolerance)
    if not mask.any():
        return _na("lettering_safe_zones_clear", "no subject visible to conflict with")

    ys, xs = np.where(mask)
    subj_bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))

    conflicts = []
    for i, z in enumerate(inp.lettering_zones):
        if len(z) != 4:
            return _fail(
                "lettering_safe_zones_clear",
                evidence={"bad_zone": z, "index": i},
                hint="lettering_zone must be [x_pct, y_pct, w_pct, h_pct]",
            )
        zx, zy, zw, zh = z
        z_px = (int(W * zx / 100), int(H * zy / 100),
                int(W * (zx + zw) / 100), int(H * (zy + zh) / 100))
        if not (z_px[2] <= subj_bbox[0] or z_px[0] >= subj_bbox[2]
                or z_px[3] <= subj_bbox[1] or z_px[1] >= subj_bbox[3]):
            conflicts.append({"zone_index": i, "zone_pct": list(z), "zone_px": list(z_px)})

    evidence = {
        "subject_bbox_px": list(subj_bbox),
        "lettering_zones_pct": [list(z) for z in inp.lettering_zones],
        "conflicts": conflicts,
    }
    if conflicts:
        return _fail(
            "lettering_safe_zones_clear",
            evidence=evidence,
            hint=f"Bubble zone(s) {[c['zone_index'] for c in conflicts]} overlap subject bbox. "
                 f"Move bubbles to negative-space regions or downscale subject.",
        )
    return _ok("lettering_safe_zones_clear", evidence=evidence)


# ─────────────────────────────────────────────────────────────────────────────
# orchestration
# ─────────────────────────────────────────────────────────────────────────────


def validate_layer(inp: LayerValidationInput) -> list[ValidationResult]:
    """Run all applicable class-A checks. Returns ordered results."""
    return [
        check_backdrop_corner(inp),
        check_subject_safe_zone(inp),
        check_subject_does_not_touch_edge(inp),
        check_rembg_clean_alpha(inp),
        check_character_extraction_coverage(inp),     # v0.6
        check_background_bleed(inp),                   # v0.6
        check_negative_space_in_bbox(inp),
        check_effect_density(inp),
        check_face_visible_threshold(inp),
        check_lettering_safe_zones_clear(inp),
    ]


def all_class_a_passed(results: list[ValidationResult]) -> bool:
    """True iff no class-A FAIL severity check failed (skipped counts as pass)."""
    return all(r.passed for r in results if r.class_ == "A" and r.severity == "FAIL")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def _load_safe_zone(compiled_path: Path, row_key: str) -> dict:
    if not compiled_path.is_file():
        raise FileNotFoundError(f"compiled safe_zones not found: {compiled_path}")
    data = yaml.safe_load(compiled_path.read_text())
    rows = data.get("compiled", {})
    if row_key not in rows:
        raise KeyError(f"row {row_key!r} not in compiled safe_zones "
                       f"(available: first 5: {list(rows.keys())[:5]})")
    return rows[row_key]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Validate a rendered layer against class-A contract gates."
    )
    ap.add_argument("--image", type=Path, required=True, help="Rendered layer PNG")
    ap.add_argument("--layer-type", required=True, choices=["L0", "L1", "L2", "L3", "L4"])
    ap.add_argument("--safe-zone-row", required=True,
                    help="Row key in compiled safe_zones (e.g., 'subject=character_face_only|framing=CU|genre=healing')")
    ap.add_argument("--compiled", type=Path, default=DEFAULT_COMPILED_SAFE_ZONES)
    ap.add_argument("--cutout", type=Path, help="Optional rembg cutout (RGBA)")
    ap.add_argument("--archetype-metadata-json", type=Path,
                    help="Optional JSON file with archetype subject_placement_bbox etc.")
    ap.add_argument("--face-confidence", type=float,
                    help="Optional upstream face-detection confidence (0-1)")
    ap.add_argument("--lettering-zones-json", type=Path,
                    help="Optional JSON file with bubble zone list [[x,y,w,h], ...]")
    ap.add_argument("--output-json", type=Path, help="Write full results as JSON")
    args = ap.parse_args(argv)

    try:
        safe_zone = _load_safe_zone(args.compiled, args.safe_zone_row)
    except (FileNotFoundError, KeyError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    archetype_meta = None
    if args.archetype_metadata_json and args.archetype_metadata_json.is_file():
        archetype_meta = json.loads(args.archetype_metadata_json.read_text())

    lettering_zones = None
    if args.lettering_zones_json and args.lettering_zones_json.is_file():
        lettering_zones = json.loads(args.lettering_zones_json.read_text())

    inp = LayerValidationInput(
        image_path=args.image,
        layer_type=args.layer_type,
        safe_zone_row=safe_zone,
        archetype_metadata=archetype_meta,
        cutout_image_path=args.cutout,
        face_confidence=args.face_confidence,
        lettering_zones=lettering_zones,
    )

    results = validate_layer(inp)
    passed = all_class_a_passed(results)

    for r in results:
        status = "SKIP" if r.skipped else ("PASS" if r.passed else "FAIL")
        line = f"[{status}] {r.check_id}"
        if r.skipped:
            line += f" — {r.skip_reason}"
        elif not r.passed:
            line += f" (class {r.class_} {r.severity}; score {r.score:.3f}): {r.remediation_hint}"
        print(line)

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(
            {"passed": passed, "results": [r.to_dict() for r in results]},
            indent=2, default=str,
        ))

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
