"""Tests for validate_layer.py — Phase B.1 step 2.

Per docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md §12 + §15.A.3.

Acceptance criteria (§15.A.3):
  - All class-A checks from §12.1–§12.5 implemented
  - class-A FAIL halts cache write (validated via all_class_a_passed)
  - Synthetic fixtures cover both pass AND fail cases for each check
  - Runs in ≤ 2 seconds per layer on CPU (no GPU dependency)
  - False-positive rate ≤ 1% on a 100-panel pilot (deferred; tested per-check here)

This test suite uses synthetic PIL-generated PNGs as fixtures so the tests
are hermetic — no dependency on external rembg / face detection output.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pytest
import yaml
from PIL import Image

REPO = Path(__file__).resolve().parents[4]
VALIDATOR = REPO / "scripts" / "manga" / "validate_layer.py"
COMPILED_SAFE_ZONES = REPO / "config" / "manga" / "compiled" / "safe_zones.yaml"

sys.path.insert(0, str(REPO / "scripts" / "manga"))
import validate_layer as vl  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# fixtures (synthetic PNGs generated per-test for hermeticity)
# ─────────────────────────────────────────────────────────────────────────────


CANVAS_W = 1080
CANVAS_H = 1920


def _safe_zone_for(row_key: str) -> dict:
    data = yaml.safe_load(COMPILED_SAFE_ZONES.read_text())
    return data["compiled"][row_key]


def _make_pure_white(path: Path):
    """Pure white #FFFFFF canvas, no subject."""
    Image.new("RGB", (CANVAS_W, CANVAS_H), (255, 255, 255)).save(path, "PNG")


def _make_pure_sage(path: Path):
    """Sage-colored canvas — the operator's known-fail mode."""
    Image.new("RGB", (CANVAS_W, CANVAS_H), (180, 195, 175)).save(path, "PNG")


def _make_white_with_centered_subject(path: Path, subject_pct=(0.4, 0.6)):
    """Pure white canvas with a black silhouette centered, sized as % of canvas."""
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), (255, 255, 255))
    arr = np.array(img)
    sw = int(CANVAS_W * subject_pct[0])
    sh = int(CANVAS_H * subject_pct[1])
    x0 = (CANVAS_W - sw) // 2
    y0 = (CANVAS_H - sh) // 2
    arr[y0:y0 + sh, x0:x0 + sw] = (20, 20, 20)
    Image.fromarray(arr).save(path, "PNG")


def _make_white_subject_touching_edge(path: Path):
    """Pure white canvas; subject extends to all four edges (margin violation)."""
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), (255, 255, 255))
    arr = np.array(img)
    arr[2:CANVAS_H - 2, 2:CANVAS_W - 2] = (20, 20, 20)  # subject 2px from each edge
    Image.fromarray(arr).save(path, "PNG")


def _make_white_subject_oversize(path: Path):
    """Pure white canvas; subject 90% of canvas (overflows CU safe zone)."""
    _make_white_with_centered_subject(path, subject_pct=(0.9, 0.95))


def _make_rgba_cutout(path: Path, subject_pct=(0.5, 0.6)):
    """Synthetic RGBA cutout: opaque centered rectangle, fully-transparent surround.
    Used for v0.6 L2 post-cutout checks."""
    arr = np.zeros((CANVAS_H, CANVAS_W, 4), dtype=np.uint8)
    arr[:, :, 0:3] = 60  # dark character color
    sw = int(CANVAS_W * subject_pct[0])
    sh = int(CANVAS_H * subject_pct[1])
    x0 = (CANVAS_W - sw) // 2
    y0 = (CANVAS_H - sh) // 2
    arr[y0:y0 + sh, x0:x0 + sw, 3] = 255  # opaque subject rectangle
    Image.fromarray(arr, "RGBA").save(path, "PNG")


def _make_rgba_cutout_full_bleed(path: Path):
    """Synthetic RGBA cutout where opaque region extends to the edges."""
    arr = np.zeros((CANVAS_H, CANVAS_W, 4), dtype=np.uint8)
    arr[:, :, 0:3] = 60
    arr[2:CANVAS_H - 2, 2:CANVAS_W - 2, 3] = 255
    Image.fromarray(arr, "RGBA").save(path, "PNG")


def _make_rgba_cutout_with_bleed(path: Path):
    """Synthetic RGBA cutout that has alpha bleed at the canvas edges (rembg failure mode)."""
    arr = np.zeros((CANVAS_H, CANVAS_W, 4), dtype=np.uint8)
    arr[:, :, 0:3] = 60
    # Opaque center
    sw = int(CANVAS_W * 0.5)
    sh = int(CANVAS_H * 0.6)
    x0 = (CANVAS_W - sw) // 2
    y0 = (CANVAS_H - sh) // 2
    arr[y0:y0 + sh, x0:x0 + sw, 3] = 255
    # Scene fragments left in the 20px-inward edge band
    arr[0:30, 0:CANVAS_W, 3] = 200    # 30px-wide top stripe of half-opaque pixels
    Image.fromarray(arr, "RGBA").save(path, "PNG")


def _make_clean_alpha_cutout(path: Path):
    """RGBA with clean bimodal alpha — 50% fully transparent, 50% fully opaque."""
    arr = np.zeros((CANVAS_H, CANVAS_W, 4), dtype=np.uint8)
    arr[:, :, 0:3] = 20  # dark subject color
    arr[CANVAS_H // 4:3 * CANVAS_H // 4, CANVAS_W // 4:3 * CANVAS_W // 4, 3] = 255
    # rest stays alpha=0
    Image.fromarray(arr, "RGBA").save(path, "PNG")


def _make_soft_alpha_cutout(path: Path):
    """RGBA with soft/gradient alpha — fringing failure mode."""
    arr = np.zeros((CANVAS_H, CANVAS_W, 4), dtype=np.uint8)
    arr[:, :, 0:3] = 20
    for y in range(CANVAS_H):
        a = int(255 * (y / CANVAS_H))  # ramp 0..255 — lots of gray values
        arr[y, :, 3] = a
    Image.fromarray(arr, "RGBA").save(path, "PNG")


def _make_l0_with_empty_bbox_region(path: Path, bbox_pct=(42, 5, 50, 50)):
    """L0 background with very low variance in the declared subject bbox region."""
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), (240, 235, 225))
    arr = np.array(img)
    # Make the bbox region near-uniform (slight noise but low variance)
    x0 = int(CANVAS_W * bbox_pct[0] / 100)
    y0 = int(CANVAS_H * bbox_pct[1] / 100)
    x1 = int(CANVAS_W * (bbox_pct[0] + bbox_pct[2]) / 100)
    y1 = int(CANVAS_H * (bbox_pct[1] + bbox_pct[3]) / 100)
    arr[y0:y1, x0:x1] = (245, 240, 230)  # uniform pale
    # Add detail OUTSIDE the bbox (windows, plants, etc.)
    arr[CANVAS_H // 2:, :CANVAS_W // 3] = np.random.randint(80, 220, (CANVAS_H - CANVAS_H // 2, CANVAS_W // 3, 3))
    Image.fromarray(arr).save(path, "PNG")


def _make_l0_with_busy_bbox_region(path: Path, bbox_pct=(42, 5, 50, 50)):
    """L0 background with HIGH variance (bimodal black/white stripes) in the bbox region — should FAIL.

    Uniform [0,255] random gives variance ~0.083 (below 0.15 threshold). To exceed
    the §11.1 threshold we need structured high-contrast content — bimodal stripes
    give normalized variance ~0.25, well above 0.15.
    """
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), (240, 235, 225))
    arr = np.array(img)
    x0 = int(CANVAS_W * bbox_pct[0] / 100)
    y0 = int(CANVAS_H * bbox_pct[1] / 100)
    x1 = int(CANVAS_W * (bbox_pct[0] + bbox_pct[2]) / 100)
    y1 = int(CANVAS_H * (bbox_pct[1] + bbox_pct[3]) / 100)
    # 4-px horizontal stripes alternating pure black + pure white
    for y in range(y0, y1):
        arr[y, x0:x1] = 255 if ((y - y0) // 4) % 2 == 0 else 0
    Image.fromarray(arr).save(path, "PNG")


# ─────────────────────────────────────────────────────────────────────────────
# 1. backdrop_corner_check
# ─────────────────────────────────────────────────────────────────────────────


def test_backdrop_corner_pure_white_passes(tmp_path: Path):
    img = tmp_path / "white.png"
    _make_pure_white(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
    )
    r = vl.check_backdrop_corner(inp)
    assert r.passed, f"pure white should pass: {r.evidence}"


def test_backdrop_corner_sage_fails_for_L1(tmp_path: Path):
    """Sage backdrop on L1 (object) must fail backdrop check.
    v0.6: L2 SKIPS pre-cutout backdrop (scene-context allowed) — tested on L1.
    The original layer-demo-v2 sage-Mira backdrop failure now manifests as a
    cutout-time failure for L2 (see test_real_world_sage_mira_*)."""
    img = tmp_path / "sage.png"
    _make_pure_sage(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L1",
        safe_zone_row=_safe_zone_for("subject=object_macro|framing=ECU|genre=healing"),
    )
    r = vl.check_backdrop_corner(inp)
    assert not r.passed
    assert "tl" in r.evidence["corners"]
    assert r.evidence["failed_corners"] == ["tl", "tr", "bl", "br"]


def test_backdrop_corner_l2_skipped_v06(tmp_path: Path):
    """v0.6 amendment: L2 backdrop check SKIPS — scene-context is allowed at render
    time; backdrop is verified post-cutout via background_bleed_check."""
    img = tmp_path / "sage.png"
    _make_pure_sage(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
    )
    r = vl.check_backdrop_corner(inp)
    assert r.skipped
    assert "L2 v0.6" in r.skip_reason


def test_backdrop_corner_l0_skipped(tmp_path: Path):
    """L0 has no isolated backdrop — check is N/A."""
    img = tmp_path / "scene.png"
    Image.new("RGB", (CANVAS_W, CANVAS_H), (100, 150, 120)).save(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L0",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
    )
    r = vl.check_backdrop_corner(inp)
    assert r.skipped
    assert r.passed  # skipped counts as pass


# ─────────────────────────────────────────────────────────────────────────────
# 2. subject_safe_zone
# ─────────────────────────────────────────────────────────────────────────────


def test_subject_safe_zone_centered_subject_passes(tmp_path: Path):
    img = tmp_path / "ok.png"
    _make_white_with_centered_subject(img, subject_pct=(0.5, 0.6))
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
    )
    r = vl.check_subject_safe_zone(inp)
    assert r.passed, f"centered 50%/60% subject should fit CU 65%×80% zone: {r.evidence}"


def test_subject_safe_zone_oversize_subject_fails(tmp_path: Path):
    """v0.6: for L2, safe_zone runs on the post-cutout RGBA. V4.1: must_not_touch
    axes track overflow. Use character_hand_only (all 4 axes guarded) so all 4
    overflow."""
    cutout = tmp_path / "big_cutout.png"
    _make_rgba_cutout(cutout, subject_pct=(0.9, 0.95))  # opaque region 90% of canvas
    inp = vl.LayerValidationInput(
        image_path=cutout, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_hand_only|framing=ECU|genre=healing"),
        cutout_image_path=cutout,
    )
    r = vl.check_subject_safe_zone(inp)
    assert not r.passed
    # V4.1: overflow is split into guarded vs permitted; both keys may exist
    assert "overflow_px_all" in r.evidence
    assert "overflow_guarded_px" in r.evidence
    # character_hand_only guards all 4 axes
    assert set(r.evidence["overflow_guarded_px"].keys()) == {"left", "top", "right", "bottom"}


def test_subject_safe_zone_no_subject_fails_for_L1(tmp_path: Path):
    """L1 empty white frame: no subject visible → FAIL.
    (v0.6 L2 runs on post-cutout RGBA; equivalent L2 test is below.)"""
    img = tmp_path / "empty.png"
    _make_pure_white(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L1",
        safe_zone_row=_safe_zone_for("subject=object_macro|framing=ECU|genre=healing"),
    )
    r = vl.check_subject_safe_zone(inp)
    assert not r.passed
    assert "no non-backdrop pixels" in r.evidence["reason"]


def test_subject_safe_zone_l2_requires_cutout(tmp_path: Path):
    """v0.6: L2 safe_zone check requires a cutout — SKIPS if absent."""
    img = tmp_path / "white.png"
    _make_pure_white(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
    )
    r = vl.check_subject_safe_zone(inp)
    assert r.skipped
    assert "L2 v0.6" in r.skip_reason


def test_subject_safe_zone_l0_skipped(tmp_path: Path):
    img = tmp_path / "scene.png"
    Image.new("RGB", (CANVAS_W, CANVAS_H), (100, 150, 120)).save(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L0",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
    )
    r = vl.check_subject_safe_zone(inp)
    assert r.skipped


# ─────────────────────────────────────────────────────────────────────────────
# 3. subject_does_not_touch_edge
# ─────────────────────────────────────────────────────────────────────────────


def test_subject_does_not_touch_edge_clear_passes(tmp_path: Path):
    img = tmp_path / "clear.png"
    _make_white_with_centered_subject(img, subject_pct=(0.4, 0.5))
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
    )
    r = vl.check_subject_does_not_touch_edge(inp)
    assert r.passed


def test_subject_does_not_touch_edge_full_bleed_fails(tmp_path: Path):
    """v0.6 L2: edge-touch check runs on post-cutout RGBA. Build a synthetic
    cutout whose opaque region extends to the canvas edges.

    Use character_hand_only (NOT character_face_only): per V4.1 §15.A.7,
    character_face_only permits bottom + right edge contact (CU portraits crop
    shoulders naturally). character_hand_only still guards all 4 axes."""
    cutout = tmp_path / "bleed_cutout.png"
    _make_rgba_cutout_full_bleed(cutout)
    inp = vl.LayerValidationInput(
        image_path=cutout, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_hand_only|framing=ECU|genre=healing"),
        cutout_image_path=cutout,
    )
    r = vl.check_subject_does_not_touch_edge(inp)
    assert not r.passed
    assert set(r.evidence["insufficient_sides"]) == {"left", "top", "right", "bottom"}


def test_subject_does_not_touch_edge_face_only_permits_bottom_right_v41(tmp_path: Path):
    """V4.1 §15.A.7: character_face_only permits bottom + right edge contact.
    Full-bleed cutout should FAIL only on top + left, not all 4 sides."""
    cutout = tmp_path / "face_only_bleed_cutout.png"
    _make_rgba_cutout_full_bleed(cutout)
    inp = vl.LayerValidationInput(
        image_path=cutout, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
        cutout_image_path=cutout,
    )
    r = vl.check_subject_does_not_touch_edge(inp)
    assert not r.passed
    assert set(r.evidence["insufficient_sides"]) == {"left", "top"}
    assert set(r.evidence["permitted_edge_touches"]) == {"bottom", "right"}


def test_subject_does_not_touch_edge_archetype_exception_skipped(tmp_path: Path):
    """window_light_threshold sets subject_must_not_touch_edge=false."""
    img = tmp_path / "bleed.png"
    _make_white_subject_touching_edge(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("archetype_exception=window_light_threshold"),
    )
    r = vl.check_subject_does_not_touch_edge(inp)
    assert r.skipped
    assert "permits edge contact" in r.skip_reason


# ─────────────────────────────────────────────────────────────────────────────
# 4. rembg_clean_alpha
# ─────────────────────────────────────────────────────────────────────────────


def test_rembg_clean_alpha_bimodal_passes(tmp_path: Path):
    cut = tmp_path / "clean.png"
    _make_clean_alpha_cutout(cut)
    inp = vl.LayerValidationInput(
        image_path=cut, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
        cutout_image_path=cut,
    )
    r = vl.check_rembg_clean_alpha(inp)
    assert r.passed, f"bimodal alpha should pass: {r.evidence}"


def test_rembg_clean_alpha_soft_alpha_fails(tmp_path: Path):
    cut = tmp_path / "soft.png"
    _make_soft_alpha_cutout(cut)
    inp = vl.LayerValidationInput(
        image_path=cut, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
        cutout_image_path=cut,
    )
    r = vl.check_rembg_clean_alpha(inp)
    assert not r.passed
    assert r.evidence["gray_band_50_200_pct"] > 1.0


def test_rembg_clean_alpha_no_cutout_skipped(tmp_path: Path):
    img = tmp_path / "white.png"
    _make_pure_white(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
    )
    r = vl.check_rembg_clean_alpha(inp)
    assert r.skipped


def test_rembg_clean_alpha_non_rgba_fails(tmp_path: Path):
    cut = tmp_path / "rgb_not_rgba.png"
    _make_pure_white(cut)  # RGB, not RGBA
    inp = vl.LayerValidationInput(
        image_path=cut, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
        cutout_image_path=cut,
    )
    r = vl.check_rembg_clean_alpha(inp)
    assert not r.passed
    assert r.evidence["mode"] == "RGB"


# ─────────────────────────────────────────────────────────────────────────────
# 5. negative_space_in_bbox (L0)
# ─────────────────────────────────────────────────────────────────────────────


def test_negative_space_in_bbox_empty_passes(tmp_path: Path):
    img = tmp_path / "scene_empty.png"
    _make_l0_with_empty_bbox_region(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L0",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
        archetype_metadata={"subject_placement_bbox": [42, 5, 50, 50]},
    )
    r = vl.check_negative_space_in_bbox(inp)
    assert r.passed, f"variance was {r.evidence.get('variance_normalized')}"


def test_negative_space_in_bbox_busy_fails(tmp_path: Path):
    img = tmp_path / "scene_busy.png"
    _make_l0_with_busy_bbox_region(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L0",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
        archetype_metadata={"subject_placement_bbox": [42, 5, 50, 50]},
    )
    r = vl.check_negative_space_in_bbox(inp)
    assert not r.passed


def test_negative_space_in_bbox_l2_skipped(tmp_path: Path):
    img = tmp_path / "char.png"
    _make_white_with_centered_subject(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
    )
    r = vl.check_negative_space_in_bbox(inp)
    assert r.skipped


# ─────────────────────────────────────────────────────────────────────────────
# 6. effect_density (L4)
# ─────────────────────────────────────────────────────────────────────────────


def test_effect_density_in_range_passes(tmp_path: Path):
    """L4 atmospheric: ~20% coverage of black backdrop with white particles."""
    img = tmp_path / "fx.png"
    arr = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)
    n_particles = int(CANVAS_W * CANVAS_H * 0.15)
    ys = np.random.randint(0, CANVAS_H, n_particles)
    xs = np.random.randint(0, CANVAS_W, n_particles)
    arr[ys, xs] = 255
    Image.fromarray(arr).save(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L4",
        safe_zone_row={"backdrop_hex": "#000000", "backdrop_corner_tolerance": 5},
    )
    r = vl.check_effect_density(inp)
    assert r.passed, f"~15% coverage should pass; got {r.evidence}"


def test_effect_density_too_sparse_fails(tmp_path: Path):
    img = tmp_path / "sparse.png"
    Image.new("RGB", (CANVAS_W, CANVAS_H), (0, 0, 0)).save(img)  # 0% coverage
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L4",
        safe_zone_row={"backdrop_hex": "#000000", "backdrop_corner_tolerance": 5},
    )
    r = vl.check_effect_density(inp)
    assert not r.passed


def test_effect_density_too_dense_fails(tmp_path: Path):
    img = tmp_path / "dense.png"
    Image.new("RGB", (CANVAS_W, CANVAS_H), (255, 255, 255)).save(img)  # 100%
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L4",
        safe_zone_row={"backdrop_hex": "#000000", "backdrop_corner_tolerance": 5},
    )
    r = vl.check_effect_density(inp)
    assert not r.passed


def test_effect_density_l0_skipped(tmp_path: Path):
    img = tmp_path / "scene.png"
    Image.new("RGB", (CANVAS_W, CANVAS_H), (200, 200, 200)).save(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L0",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
    )
    r = vl.check_effect_density(inp)
    assert r.skipped


# ─────────────────────────────────────────────────────────────────────────────
# 7. face_visible_threshold (upstream confidence)
# ─────────────────────────────────────────────────────────────────────────────


def test_face_visible_above_threshold_passes(tmp_path: Path):
    img = tmp_path / "char.png"
    _make_white_with_centered_subject(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
        face_confidence=0.92,
    )
    r = vl.check_face_visible_threshold(inp)
    assert r.passed


def test_face_visible_below_threshold_fails(tmp_path: Path):
    img = tmp_path / "char.png"
    _make_white_with_centered_subject(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
        face_confidence=0.40,
    )
    r = vl.check_face_visible_threshold(inp)
    assert not r.passed


def test_face_visible_no_confidence_skipped(tmp_path: Path):
    """Operator constraint: validator doesn't run ML. Skip if upstream didn't supply."""
    img = tmp_path / "char.png"
    _make_white_with_centered_subject(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
    )
    r = vl.check_face_visible_threshold(inp)
    assert r.skipped
    assert "validator does not run ML" in r.skip_reason


# ─────────────────────────────────────────────────────────────────────────────
# 8. lettering_safe_zones_clear
# ─────────────────────────────────────────────────────────────────────────────


def test_lettering_zones_clear_passes(tmp_path: Path):
    img = tmp_path / "char.png"
    _make_white_with_centered_subject(img, subject_pct=(0.4, 0.5))
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
        lettering_zones=[[2, 2, 25, 15]],  # top-left corner, away from centered subject
    )
    r = vl.check_lettering_safe_zones_clear(inp)
    assert r.passed, f"zone shouldn't overlap centered subject: {r.evidence}"


def test_lettering_zones_overlap_fails(tmp_path: Path):
    img = tmp_path / "char.png"
    _make_white_with_centered_subject(img, subject_pct=(0.5, 0.6))
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
        lettering_zones=[[40, 40, 20, 20]],  # right on top of subject center
    )
    r = vl.check_lettering_safe_zones_clear(inp)
    assert not r.passed
    assert r.evidence["conflicts"]


def test_lettering_zones_no_zones_skipped(tmp_path: Path):
    img = tmp_path / "char.png"
    _make_white_with_centered_subject(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
    )
    r = vl.check_lettering_safe_zones_clear(inp)
    assert r.skipped


# ─────────────────────────────────────────────────────────────────────────────
# 9. orchestration + all_class_a_passed
# ─────────────────────────────────────────────────────────────────────────────


def test_validate_layer_all_pass(tmp_path: Path):
    img = tmp_path / "ok.png"
    _make_white_with_centered_subject(img, subject_pct=(0.5, 0.6))
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
    )
    results = vl.validate_layer(inp)
    assert vl.all_class_a_passed(results), \
        f"failures: {[(r.check_id, r.evidence) for r in results if not r.passed]}"


def test_validate_layer_sage_backdrop_fails_all_class_a_for_L1(tmp_path: Path):
    """v0.6 amendment: the sage-backdrop failure mode is class-A on L1/L3
    (object layers still require pure backdrop). On L2 it's a cutout-time
    failure (see test_l2_cutout_with_bleed_fails)."""
    img = tmp_path / "sage.png"
    _make_pure_sage(img)
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L1",
        safe_zone_row=_safe_zone_for("subject=object_macro|framing=ECU|genre=healing"),
    )
    results = vl.validate_layer(inp)
    assert not vl.all_class_a_passed(results)
    failed = [r for r in results if not r.passed]
    assert any(r.check_id == "backdrop_corner_check" for r in failed)


def test_l2_cutout_with_edge_bleed_fails_v06(tmp_path: Path):
    """v0.6 + V4.1: scene fragments at the 20px edge band fail
    background_bleed_check. Use character_hand_only (all axes guarded) so top
    bleed counts in guarded_axes_bleed_pct."""
    cutout = tmp_path / "bleed_cutout.png"
    _make_rgba_cutout_with_bleed(cutout)
    inp = vl.LayerValidationInput(
        image_path=cutout, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_hand_only|framing=ECU|genre=healing"),
        cutout_image_path=cutout,
    )
    results = vl.validate_layer(inp)
    bleed = next(r for r in results if r.check_id == "background_bleed_check")
    assert not bleed.passed
    assert bleed.evidence["guarded_axes_bleed_pct"] > 5.0


def test_l2_clean_cutout_passes_new_gates_v06(tmp_path: Path):
    """v0.6: a clean centered cutout passes both new gates."""
    cutout = tmp_path / "clean_cutout.png"
    _make_rgba_cutout(cutout, subject_pct=(0.6, 0.75))  # within CU safe zone (65×80)
    inp = vl.LayerValidationInput(
        image_path=cutout, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
        cutout_image_path=cutout,
    )
    cec = vl.check_character_extraction_coverage(inp)
    bb = vl.check_background_bleed(inp)
    assert cec.passed, f"coverage failed: {cec.evidence}"
    assert bb.passed, f"bleed failed: {bb.evidence}"


def test_l2_eaten_cutout_fails_extraction_coverage_v06(tmp_path: Path):
    """v0.6: if rembg eats most of the character, character_extraction_coverage FAILS."""
    cutout = tmp_path / "eaten_cutout.png"
    _make_rgba_cutout(cutout, subject_pct=(0.05, 0.05))  # tiny opaque region
    inp = vl.LayerValidationInput(
        image_path=cutout, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
        cutout_image_path=cutout,
    )
    r = vl.check_character_extraction_coverage(inp)
    assert not r.passed
    assert r.evidence["coverage_ratio"] < 0.50


# ─────────────────────────────────────────────────────────────────────────────
# 10. performance: ≤ 2 seconds per layer (§15.A.3)
# ─────────────────────────────────────────────────────────────────────────────


def test_validator_runs_under_2_seconds(tmp_path: Path):
    """v0.6: L2 validation runs all class-A gates including 2 new ones in ≤ 2s."""
    img = tmp_path / "ok.png"
    _make_white_with_centered_subject(img, subject_pct=(0.5, 0.6))
    cut = tmp_path / "cut.png"
    _make_rgba_cutout(cut, subject_pct=(0.6, 0.75))   # within CU safe zone
    inp = vl.LayerValidationInput(
        image_path=img, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
        cutout_image_path=cut,
        face_confidence=0.91,
        lettering_zones=[[2, 2, 20, 15]],
    )
    t0 = time.time()
    results = vl.validate_layer(inp)
    elapsed = time.time() - t0
    assert elapsed < 2.0, f"validator took {elapsed:.2f}s (limit 2.0s per §15.A.3)"
    assert vl.all_class_a_passed(results), \
        f"failures: {[(r.check_id, r.evidence) for r in results if not r.passed]}"


# ─────────────────────────────────────────────────────────────────────────────
# 11. real-world fixture: the operator's sage-Mira layer demo
# ─────────────────────────────────────────────────────────────────────────────

REAL_MIRA_RAW = REPO / "artifacts" / "manga" / "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying" / "experiments" / "layer_demo_qwen" / "layer_character.png"
REAL_MIRA_CUTOUT = REPO / "artifacts" / "manga" / "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying" / "experiments" / "layer_demo_qwen" / "layer_character_alpha.png"


@pytest.mark.skipif(not REAL_MIRA_RAW.is_file(), reason="layer-demo Mira render not present")
def test_real_world_sage_mira_l2_backdrop_skipped_v06(tmp_path: Path):
    """v0.6 amendment: the original layer-demo sage-Mira render now SKIPS
    backdrop_corner_check at L2 (scene context allowed). The failure mode
    moved to background_bleed_check on the cutout output."""
    inp = vl.LayerValidationInput(
        image_path=REAL_MIRA_RAW, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
    )
    r = vl.check_backdrop_corner(inp)
    assert r.skipped
    assert "L2 v0.6" in r.skip_reason


@pytest.mark.skipif(not REAL_MIRA_CUTOUT.is_file(), reason="rembg cutout not present")
def test_real_world_sage_mira_cutout_evidence_available_v06(tmp_path: Path):
    """The original u2net_human_seg cutout exists; validate gates produce evidence."""
    inp = vl.LayerValidationInput(
        image_path=REAL_MIRA_RAW, layer_type="L2",
        safe_zone_row=_safe_zone_for("subject=character_face_only|framing=CU|genre=healing"),
        cutout_image_path=REAL_MIRA_CUTOUT,
    )
    r = vl.check_rembg_clean_alpha(inp)
    assert "gray_band_50_200_pct" in r.evidence
    # v0.6 threshold is 3% for L2; the original layer-demo cutout's gray band
    # value is informational (PASS or FAIL depending on the specific cutout).


# ─────────────────────────────────────────────────────────────────────────────
# 12. CLI smoke
# ─────────────────────────────────────────────────────────────────────────────


def test_cli_pass_l1(tmp_path: Path):
    """CLI smoke: clean L1 white render with centered object passes."""
    img = tmp_path / "ok.png"
    _make_white_with_centered_subject(img, subject_pct=(0.5, 0.6))
    r = subprocess.run(
        [
            sys.executable, str(VALIDATOR),
            "--image", str(img),
            "--layer-type", "L1",
            "--safe-zone-row", "subject=object_macro|framing=ECU|genre=healing",
        ],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stdout={r.stdout}\nstderr={r.stderr}"
    assert "[PASS] backdrop_corner_check" in r.stdout


def test_cli_fail_l1_sage_returns_1(tmp_path: Path):
    """CLI: L1 with sage backdrop fails."""
    img = tmp_path / "sage.png"
    _make_pure_sage(img)
    r = subprocess.run(
        [
            sys.executable, str(VALIDATOR),
            "--image", str(img),
            "--layer-type", "L1",
            "--safe-zone-row", "subject=object_macro|framing=ECU|genre=healing",
        ],
        capture_output=True, text=True,
    )
    assert r.returncode == 1
    assert "[FAIL] backdrop_corner_check" in r.stdout


def test_cli_unknown_row_exits_2(tmp_path: Path):
    img = tmp_path / "white.png"
    _make_pure_white(img)
    r = subprocess.run(
        [
            sys.executable, str(VALIDATOR),
            "--image", str(img),
            "--layer-type", "L2",
            "--safe-zone-row", "subject=nonexistent|framing=XX|genre=XX",
        ],
        capture_output=True, text=True,
    )
    assert r.returncode == 2
    assert "not in compiled safe_zones" in r.stderr
