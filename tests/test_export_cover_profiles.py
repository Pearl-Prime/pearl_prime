"""Regression tests for the L5 platform cover exporter (lane 3, Kobo first).

Covers scripts/publishing/export_cover_profiles.py — the non-destructive
per-platform adaptation layer (Q-LEVELS-01, OPD-20260701-001).

SSOT for every asserted number:
  docs/authoring/BOOK_COVER_UNIFIED_RESEARCH_2026-07-01.md §2.3/§3.1/§4/§7
  config/publishing/platform_cover_profiles.yaml (kobo_ebook)
  docs/authoring/AUTHOR_COVER_ART_SPEC.md §4/§6/§7

Assertions:
  - Kobo export is EXACTLY 3:4 (1920x2560), not KDP 5:8.
  - A KDP 5:8 master is REFLOWED (cover-fit, no stretch) to 3:4, not distorted.
  - JPEG is <= Kobo max_file_mb (5 MB).
  - WCAG-AA contrast check RUNS on the reflowed text zone (report present).
  - Deterministic re-run is BYTE-IDENTICAL.
  - No letterbox bars where the profile forbids them.

Uses a type-dominant genre (boundaries) so the render path needs NO FLUX
illustration and is fully deterministic — no GPU, no paid LLM.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from scripts.publishing import export_cover_profiles as ecp
from scripts.publishing.load_cover_profiles import get_profile

pytestmark = pytest.mark.sanity

REPO_ROOT = Path(__file__).resolve().parents[1]
GENRE = "boundaries"  # type-dominant → no FLUX illustration required


def _sha(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def kobo_profile():
    return get_profile("kobo_ebook")


@pytest.fixture(scope="module")
def kobo_export(tmp_path_factory):
    out = tmp_path_factory.mktemp("kobo")
    return ecp.export(
        "test_boundaries_book",
        "test_author",
        "kobo_ebook",
        genre=GENRE,
        title="The Quiet Fix",
        author="Test Author",
        subtitle="A Field Guide",
        out_dir=out,
    )


# ─── ASPECT: exactly 3:4, not 5:8 ────────────────────────────────────


def test_kobo_recommended_is_exactly_3x4(kobo_export):
    from PIL import Image

    im = Image.open(kobo_export["outputs"]["png_recommended"])
    assert im.size == (1920, 2560), f"expected 1920x2560, got {im.size}"
    ratio = im.size[0] / im.size[1]
    assert abs(ratio - 0.75) < 1e-6, f"Kobo must be 3:4 (0.75), got {ratio:.4f}"
    # Must NOT be the KDP 5:8 aspect (0.625).
    assert abs(ratio - 0.625) > 0.1, "reflowed asset is still KDP 5:8, not Kobo 3:4"


def test_kobo_high_dpi_master_is_2500x3500(kobo_export):
    from PIL import Image

    hi = Image.open(kobo_export["outputs"]["png_high_dpi_master"])
    # 2500x3500 is 5:7 (~0.714), the high-DPI MASTER — distinct from 3:4.
    assert hi.size == (2500, 3500), f"expected 2500x3500 hi-DPI master, got {hi.size}"


def test_profile_recommended_matches_declared_aspect(kobo_profile):
    rec = kobo_profile["size_recommended"]
    assert (rec["width"], rec["height"]) == (1920, 2560)
    assert kobo_profile["aspect_ratio"]["decimal"] == 0.75


# ─── REFLOW: cover-fit, no stretch ───────────────────────────────────


def test_kdp_5x8_master_reflowed_not_stretched():
    """A KDP-native 1600x2560 (5:8) master must cover-fit to 3:4 by uniform
    scale + center-crop — NEVER stretched. We verify by placing a circle in
    the master and confirming it stays circular (equal scale on both axes)."""
    from PIL import Image, ImageDraw

    master = Image.new("RGB", (1600, 2560), (18, 24, 48))
    d = ImageDraw.Draw(master)
    # A circle centered in the master; a stretch would make it an ellipse.
    cx, cy, r = 800, 1280, 300
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 240, 240))

    reflowed = ecp._cover_fit(master, 1920, 2560)
    assert reflowed.size == (1920, 2560)

    # Cover-fit of 5:8 (0.625) into 3:4 (0.75, wider): scale = max(1920/1600,
    # 2560/2560) = 1.2 → 1920x3072 then center-crop vertically to 2560. The
    # circle's horizontal and vertical extents scale by the SAME 1.2 factor,
    # so it stays circular. Measure the white blob's width vs height.
    rgb = reflowed.convert("RGB")
    px = rgb.load()
    w, h = rgb.size
    xs = [x for x in range(w) if px[x, h // 2][0] > 200]
    ys = [y for y in range(h) if px[w // 2, y][0] > 200]
    assert xs and ys, "reflowed circle not found"
    blob_w = max(xs) - min(xs)
    blob_h = max(ys) - min(ys)
    # Equal scale → circle stays circular within a few px of rounding.
    assert abs(blob_w - blob_h) <= 4, (
        f"circle distorted to ellipse (w={blob_w} h={blob_h}) — reflow stretched"
    )
    # And it scaled up by the expected 1.2 (was 600px diameter → ~720px).
    assert 700 <= blob_w <= 740, f"unexpected scale: blob_w={blob_w}"


def test_reflow_strategy_is_cover_fit(kobo_export):
    assert kobo_export["reflow_strategy"] == "cover_fit_scale_to_fill_center_crop"


# ─── NO LETTERBOX where forbidden ────────────────────────────────────


def test_no_letterbox_bars_on_kobo(kobo_export, kobo_profile):
    from PIL import Image

    assert kobo_profile["letterbox_allowed"] is False
    im = Image.open(kobo_export["outputs"]["png_recommended"])
    assert not ecp._has_letterbox_bars(im), "Kobo forbids letterbox but bars present"


def test_letterbox_detector_flags_true_bars():
    """Detector must catch genuine padding bars (content strip + black bars)."""
    from PIL import Image

    lb = Image.new("RGB", (1920, 2560), (0, 0, 0))
    px = lb.load()
    for y in range(600, 1960):
        for x in range(1920):
            px[x, y] = (180, 60, 60)
    assert ecp._has_letterbox_bars(lb) is True


def test_letterbox_detector_ignores_flat_design_background():
    """A legitimately flat design background must NOT be flagged as letterbox."""
    from PIL import Image

    m = Image.new("RGB", (1920, 2560), (20, 30, 60))
    px = m.load()
    for y in range(700, 1000):
        for x in range(400, 1500):
            px[x, y] = (240, 240, 240)
    assert ecp._has_letterbox_bars(m) is False


# ─── JPEG ≤ max_file_mb ──────────────────────────────────────────────


def test_kobo_jpeg_within_max_file_mb(kobo_export, kobo_profile):
    jpeg = kobo_export["outputs"]["jpeg_recommended"]
    max_bytes = int(float(kobo_profile["max_file_mb"]) * 1024 * 1024)
    assert jpeg["bytes"] <= max_bytes, (
        f"JPEG {jpeg['bytes']} exceeds Kobo max {max_bytes} bytes"
    )
    assert jpeg["over_budget"] is False


def test_kobo_emits_jpg_because_profile_allows_it(kobo_profile):
    fmts = [f.lower() for f in kobo_profile["formats"]]
    assert "jpg" in fmts or "jpeg" in fmts


# ─── WCAG runs on the reflowed zone ──────────────────────────────────


def test_wcag_check_runs_on_reflowed_zone(kobo_export):
    wcag = kobo_export["wcag"]
    # The contrast check must have RUN at the new aspect (report populated).
    for key in ("wcag_contrast_ratio", "wcag_pass", "wcag_target",
                "wcag_zone_luminance", "wcag_text_luminance"):
        assert key in wcag, f"WCAG report missing {key}"
    assert wcag["wcag_target"] == 4.5
    assert isinstance(wcag["wcag_contrast_ratio"], float)


# ─── Determinism: byte-identical re-run ──────────────────────────────


def test_deterministic_byte_identical_rerun(tmp_path):
    kw = dict(
        genre=GENRE, title="The Quiet Fix", author="Test Author",
        subtitle="A Field Guide",
    )
    r1 = ecp.export("detbook", "detauthor", "kobo_ebook",
                    out_dir=tmp_path / "a", **kw)
    r2 = ecp.export("detbook", "detauthor", "kobo_ebook",
                    out_dir=tmp_path / "b", **kw)

    assert _sha(r1["outputs"]["png_recommended"]) == _sha(
        r2["outputs"]["png_recommended"]
    ), "recommended PNG not byte-identical across runs"
    assert _sha(r1["outputs"]["png_high_dpi_master"]) == _sha(
        r2["outputs"]["png_high_dpi_master"]
    ), "hi-DPI PNG not byte-identical"
    assert _sha(r1["outputs"]["jpeg_recommended"]["path"]) == _sha(
        r2["outputs"]["jpeg_recommended"]["path"]
    ), "JPEG not byte-identical"
    assert r1["phash"] == r2["phash"]
    assert r1["l4_seed"] == r2["l4_seed"]


# ─── L5 determinism seed carries the L4 seed unchanged (§2.3) ────────


def test_l4_seed_is_sha256_of_author_book():
    seed = ecp._l4_seed("author_x", "book_y")
    expected = hashlib.sha256("author_x:book_y".encode()).hexdigest()
    assert seed == expected


# ─── Output path contract ────────────────────────────────────────────


def test_output_path_contract(kobo_export):
    rec = kobo_export["outputs"]["png_recommended"]
    assert rec.endswith("test_boundaries_book_kobo_ebook_1920x2560.png")
    hi = kobo_export["outputs"]["png_high_dpi_master"]
    assert hi.endswith("test_boundaries_book_kobo_ebook_2500x3500.png")
