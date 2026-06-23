"""Tests for scripts.publish.render_kdp_cover.

Covers library import, both YAML schemas (R3 typography + R4 templates),
render correctness, auto-color against template flat-color background,
batch listing, override merging, per-genre layout differences,
type-dominant FLUX bypass, strict zone non-overlap, title-too-long
errors, and graceful refusal on missing inputs.

R5 (2026-04-30): renderer is now template-based. Title-zone background
is always the genre's ``palette.primary.hex`` (template enforces
title_zone never overlaps imagery_zone), so auto-color now picks against
that flat color rather than sampling pixels in the illustration. Tests
updated accordingly. The 14 R3 tests carry forward with the same API.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

import pytest
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.publish import render_kdp_cover as rkc  # noqa: E402


# ─── FIXTURES ─────────────────────────────────────────────────────────


@pytest.fixture()
def dark_illustration(tmp_path: Path) -> Path:
    """Solid dark-navy illustration; for image-bearing genres."""
    path = tmp_path / "dark_illo.png"
    Image.new("RGB", (1216, 870), (15, 23, 42)).save(path)
    return path


@pytest.fixture()
def light_illustration(tmp_path: Path) -> Path:
    """Solid light-cream illustration; for image-bearing genres."""
    path = tmp_path / "light_illo.png"
    Image.new("RGB", (1216, 870), (245, 240, 230)).save(path)
    return path


# ─── R3 TESTS (carried forward) ───────────────────────────────────────


def test_library_imports_cleanly() -> None:
    assert callable(rkc.render_kdp_cover)
    assert callable(rkc.load_typography_config)
    assert callable(rkc.load_templates_config)
    assert rkc.CANVAS_W == 1600
    assert rkc.CANVAS_H == 2560


def test_typography_yaml_loads_with_all_production_genres() -> None:
    cfg = rkc.load_typography_config()
    assert "genres" in cfg
    assert "defaults" in cfg
    expected = {
        "anxiety", "self_worth", "overthinking", "boundaries",
        "burnout", "grief", "courage", "imposter_syndrome", "sleep_anxiety",
        "depression", "social_anxiety", "somatic_healing", "compassion_fatigue",
        "financial_anxiety", "financial_stress",
    }
    assert set(cfg["genres"].keys()) == expected, (
        f"Expected exactly the {len(expected)} production genres, got {set(cfg['genres'].keys())}"
    )


def test_each_genre_has_required_schema() -> None:
    cfg = rkc.load_typography_config()
    for name, genre_cfg in cfg["genres"].items():
        assert "title_zone" in genre_cfg, f"{name} missing title_zone"
        assert "title_style" in genre_cfg, f"{name} missing title_style"
        zone = genre_cfg["title_zone"]
        for key in ("position", "anchor", "max_width_pct", "max_height_pct"):
            assert key in zone, f"{name}.title_zone missing {key}"
        style = genre_cfg["title_style"]
        for key in ("font_family", "font_weight", "size_px_at_1600x2560",
                    "case", "color"):
            assert key in style, f"{name}.title_style missing {key}"


def test_render_writes_exact_canvas_size(dark_illustration: Path,
                                          tmp_path: Path) -> None:
    out = tmp_path / "cover.png"
    meta = rkc.render_kdp_cover(
        illustration_path=dark_illustration,
        title="The Alarm Is Lying",
        author="Ahjan",
        subtitle="A Nervous System Guide to Anxiety Recovery",
        genre="anxiety",
        output_path=out,
    )
    assert out.exists()
    assert out.stat().st_size > 0
    img = Image.open(out)
    assert img.size == (1600, 2560)
    assert meta["output_size"] == (1600, 2560)


def test_typography_overrides_accepted(dark_illustration: Path,
                                        tmp_path: Path) -> None:
    out = tmp_path / "cover_override.png"
    meta = rkc.render_kdp_cover(
        illustration_path=dark_illustration, title="Override Test", author="A",
        genre="anxiety", output_path=out,
        typography_overrides={"title_style": {"color": "#FF00FF"}},
    )
    assert tuple(meta["title_color_rgb"]) == (255, 0, 255)


def test_genre_layouts_differ_anxiety_vs_grief(dark_illustration: Path,
                                                tmp_path: Path) -> None:
    """Anxiety puts title zone in the upper third; grief puts title closer
    to center. Outputs differ by visible pixel count."""
    templates = rkc.load_templates_config()["templates"]
    anxiety_y = templates["anxiety"]["title_zone"]["y_pct"]
    grief_y = templates["grief"]["title_zone"]["y_pct"]
    assert anxiety_y[0] < grief_y[0], (
        "Genre templates must place title at different vertical offsets"
    )

    out_a = tmp_path / "a.png"
    out_g = tmp_path / "g.png"
    rkc.render_kdp_cover(
        illustration_path=dark_illustration, title="Same Title", author="A",
        genre="anxiety", output_path=out_a,
    )
    rkc.render_kdp_cover(
        illustration_path=dark_illustration, title="Same Title", author="A",
        genre="grief", output_path=out_g,
    )
    img_a = Image.open(out_a).convert("RGB")
    img_g = Image.open(out_g).convert("RGB")
    diff = sum(
        1 for pa, pg in zip(img_a.getdata(), img_g.getdata()) if pa != pg
    )
    assert diff > 1000, f"Anxiety vs grief covers nearly identical (diff_px={diff})"


def test_centered_anchor_horizontally_centers_title(dark_illustration: Path,
                                                     tmp_path: Path) -> None:
    """Title should be roughly horizontally centered."""
    out = tmp_path / "centered.png"
    rkc.render_kdp_cover(
        illustration_path=dark_illustration, title="Centered",
        author="A", genre="anxiety", output_path=out,
    )
    img = Image.open(out).convert("RGB")
    # Anxiety primary palette is #F5EFE3 (cream); count text-darker pixels
    # in the title band.
    base = (245, 239, 227)
    left_count = right_count = 0
    cx = 1600 // 2
    pixels = img.load()
    # Anxiety title_zone y_pct is [10, 34] → y range [256..870].
    for y in range(280, 800, 4):
        for x in range(0, 1600, 4):
            if abs(pixels[x, y][0] - base[0]) > 10:
                if x < cx:
                    left_count += 1
                elif x > cx:
                    right_count += 1
    assert left_count > 0 and right_count > 0
    ratio = max(left_count, right_count) / max(1, min(left_count, right_count))
    assert ratio < 3.0, f"Title not centered (left={left_count} right={right_count})"


def test_refuses_missing_illustration(tmp_path: Path) -> None:
    """Image-bearing genres require a valid illustration_path."""
    with pytest.raises(FileNotFoundError):
        rkc.render_kdp_cover(
            illustration_path=tmp_path / "does_not_exist.png",
            title="X", author="Y", genre="anxiety",
            output_path=tmp_path / "out.png",
        )


def test_refuses_missing_title(dark_illustration: Path,
                                tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="title is required"):
        rkc.render_kdp_cover(
            illustration_path=dark_illustration, title="", author="Y",
            genre="anxiety", output_path=tmp_path / "out.png",
        )
    with pytest.raises(ValueError, match="title is required"):
        rkc.render_kdp_cover(
            illustration_path=dark_illustration, title="   ", author="Y",
            genre="anxiety", output_path=tmp_path / "out.png",
        )


def test_unknown_genre_refused(dark_illustration: Path,
                                tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unknown genre"):
        rkc.render_kdp_cover(
            illustration_path=dark_illustration, title="X", author="Y",
            genre="not_a_real_genre", output_path=tmp_path / "out.png",
        )


def test_batch_lists_books_without_crash(tmp_path: Path) -> None:
    """--batch reads TEACHER_BOOKS and processes each. Without v3 imagery
    on disk, image-bearing books are reported as skipped; type-dominant
    books succeed."""
    with mock.patch.object(rkc, "_find_v3_imagery", return_value=None), \
         mock.patch.object(rkc, "REPO_ROOT", tmp_path):
        # Force the renderer to write outputs into tmp_path so we don't
        # touch the real artifacts dir.
        results = rkc._run_batch()
    assert isinstance(results, list)
    assert len(results) >= 13, f"Expected >=13 teacher books, got {len(results)}"
    statuses = {r["status"] for r in results}
    # Type-dominant books succeed; image-bearing skipped.
    assert "skipped_no_illustration" in statuses
    assert "ok" in statuses


def test_resize_non_canonical_illustration(tmp_path: Path) -> None:
    """Illustrations of unexpected size are resized to the imagery_zone
    pixel dimensions before composite."""
    weird = tmp_path / "weird.png"
    Image.new("RGB", (800, 1280), (40, 40, 80)).save(weird)
    out = tmp_path / "resized.png"
    meta = rkc.render_kdp_cover(
        illustration_path=weird, title="Resize Test", author="A",
        genre="anxiety", output_path=out,
    )
    assert meta["output_size"] == (1600, 2560)
    assert Image.open(out).size == (1600, 2560)


def test_auto_color_against_template_palette(dark_illustration: Path,
                                              light_illustration: Path,
                                              tmp_path: Path) -> None:
    """R5: auto-color now picks against the GENRE palette (the title-zone
    background is the flat primary palette color), not against the
    illustration. Anxiety primary is cream (#F5EFE3), so auto-color
    picks the dark fallback regardless of the illustration."""
    out_a = tmp_path / "a.png"
    out_b = tmp_path / "b.png"
    meta_a = rkc.render_kdp_cover(
        illustration_path=dark_illustration, title="X", author="A",
        genre="anxiety", output_path=out_a,
    )
    meta_b = rkc.render_kdp_cover(
        illustration_path=light_illustration, title="X", author="A",
        genre="anxiety", output_path=out_b,
    )
    # Background is light → both auto-color picks should be dark.
    for meta in (meta_a, meta_b):
        r, g, b = meta["title_color_rgb"]
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        assert luminance < 0.5, (
            f"Cream-bg anxiety should auto-pick dark text, got rgb={meta['title_color_rgb']}"
        )


# ─── R5 NEW TESTS ─────────────────────────────────────────────────────


def test_template_loaded_for_each_genre() -> None:
    """Every genre in cookbook_v2.book_genre_map must have a template."""
    import yaml
    cookbook = yaml.safe_load(
        (REPO_ROOT / "config/manga/genre_prompt_cookbook_v2.yaml").read_text()
    )
    templates = rkc.load_templates_config()["templates"]
    bgm = cookbook.get("book_genre_map", {})
    for book, genre in bgm.items():
        assert genre in templates, f"Book '{book}' has genre '{genre}' but no template"


def test_type_dominant_skips_illustration(tmp_path: Path) -> None:
    """Pass a known-bad illustration path; render still succeeds for
    boundaries / self_worth / imposter_syndrome."""
    bad_path = tmp_path / "does_not_exist.png"
    for genre in ("boundaries", "self_worth", "imposter_syndrome"):
        out = tmp_path / f"td_{genre}.png"
        meta = rkc.render_kdp_cover(
            illustration_path=bad_path, title="No Means No",
            author="A", genre=genre, output_path=out,
        )
        assert meta["type_dominant"] is True
        assert meta["imagery_zone_used"] is False
        assert Image.open(out).size == (1600, 2560)
    # And: no illustration argument also works for type-dominant.
    out = tmp_path / "td_none.png"
    meta = rkc.render_kdp_cover(
        illustration_path=None, title="No Means No",
        author="A", genre="boundaries", output_path=out,
    )
    assert meta["type_dominant"] is True
    assert Image.open(out).size == (1600, 2560)


def test_imagery_zone_aspect_matches_template(dark_illustration: Path,
                                                tmp_path: Path) -> None:
    """For image-bearing genres, the rendered cover's imagery region is
    composited at the template's pixel coords with matching aspect."""
    templates = rkc.load_templates_config()["templates"]
    out = tmp_path / "anxiety_aspect.png"
    meta = rkc.render_kdp_cover(
        illustration_path=dark_illustration, title="X", author="A",
        genre="anxiety", output_path=out,
    )
    iz = templates["anxiety"]["imagery_zone"]
    expected_w = (iz["x_pct"][1] - iz["x_pct"][0]) / 100.0 * 1600
    expected_h = (iz["y_pct"][1] - iz["y_pct"][0]) / 100.0 * 2560
    expected_aspect = expected_w / expected_h
    assert abs(meta["imagery_aspect"] - expected_aspect) < 0.01
    # Sample the center of the imagery zone — should be dark navy from
    # the dark_illustration fixture (NOT the cream palette primary).
    img = Image.open(out).convert("RGB")
    cx, cy = (
        int(1600 * (iz["x_pct"][0] + iz["x_pct"][1]) / 200.0),
        int(2560 * (iz["y_pct"][0] + iz["y_pct"][1]) / 200.0),
    )
    pixel = img.getpixel((cx, cy))
    # dark_illustration is rgb(15, 23, 42); allow PNG quantization wiggle.
    assert pixel[0] < 60, f"Imagery zone center should be dark, got {pixel}"


@pytest.mark.parametrize("genre", [
    "anxiety", "sleep_anxiety", "grief", "overthinking", "burnout", "courage",
])
def test_title_zone_no_overlap_with_imagery_zone(genre: str) -> None:
    """For each image-bearing genre, title_zone and imagery_zone must not
    overlap (R4 universal §10.4-10.5 + overlap_rule=no_overlap)."""
    templates = rkc.load_templates_config()["templates"]
    tpl = templates[genre]
    tz = tpl["title_zone"]
    iz = tpl["imagery_zone"]
    assert iz is not None, f"{genre} expected to have imagery_zone"
    # Either title is fully above imagery_zone or fully below.
    title_below_imagery = tz["y_pct"][0] >= iz["y_pct"][1]
    title_above_imagery = tz["y_pct"][1] <= iz["y_pct"][0]
    assert title_below_imagery or title_above_imagery, (
        f"{genre}: title_zone y={tz['y_pct']} overlaps imagery_zone y={iz['y_pct']}"
    )


def test_title_too_long_raises(dark_illustration: Path, tmp_path: Path) -> None:
    """Long title vs grief's narrow zone → TitleTooLongForTemplateError."""
    very_long = (
        "A Profoundly Comprehensive And Exhaustively Detailed Treatise "
        "Concerning The Multidimensional Phenomenology Of Personal Grief "
        "Across Cultures Eras And Cosmologies Volume One"
    )
    with pytest.raises(rkc.TitleTooLongForTemplateError):
        rkc.render_kdp_cover(
            illustration_path=dark_illustration,
            title=very_long, author="A",
            genre="grief", output_path=tmp_path / "too_long.png",
        )


def test_no_more_matte_layer(dark_illustration: Path, tmp_path: Path) -> None:
    """Render does NOT call any backdrop/matte code path; legacy hooks
    are kept as no-ops for back-compat."""
    # Both hooks should exist (back-compat) but be no-ops.
    assert rkc._legacy_apply_matte() is None
    assert rkc._legacy_apply_backdrop_block() is None
    # The render output must NOT include the matte band rectangle that
    # R3 used to paint at 60% alpha across the title zone. We probe by
    # rendering a known-fixed-color illustration and checking that the
    # title-zone background equals the genre's palette.primary, not a
    # mid-luminance matte blend.
    out = tmp_path / "nomatte.png"
    rkc.render_kdp_cover(
        illustration_path=dark_illustration, title="Test", author="A",
        genre="anxiety", output_path=out,
    )
    img = Image.open(out).convert("RGB")
    # Anxiety primary palette is #F5EFE3 (cream).
    pixel = img.getpixel((50, 100))  # well inside title_zone, well outside text
    # Cream is ~(245, 239, 227); reject anything that's a darker matte blend.
    assert pixel[0] > 200 and pixel[1] > 200 and pixel[2] > 200, (
        f"Title zone background not the flat palette.primary cream — got {pixel}"
    )


def test_loads_templates_config() -> None:
    """The templates YAML must declare exactly the 9 production genres."""
    cfg = rkc.load_templates_config()
    expected = {
        "anxiety", "self_worth", "overthinking", "boundaries",
        "burnout", "grief", "courage", "imposter_syndrome", "sleep_anxiety",
    }
    assert set(cfg["templates"].keys()) == expected
