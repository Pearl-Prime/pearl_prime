"""Tests for scripts.publish.render_kdp_cover.

Covers library import, YAML schema, render correctness, auto-color,
batch listing, override merging, per-genre layout differences, and
graceful refusal on missing inputs.

No network or LLM calls — Pillow only. Uses tmp_path fixtures and
solid-color stand-in illustrations for the FLUX-rendered base.
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
    """Solid dark-navy 1600x2560 illustration; auto-color should pick light text."""
    path = tmp_path / "dark_illo.png"
    Image.new("RGB", (1600, 2560), (15, 23, 42)).save(path)
    return path


@pytest.fixture()
def light_illustration(tmp_path: Path) -> Path:
    """Solid light-cream 1600x2560 illustration; auto-color should pick dark text."""
    path = tmp_path / "light_illo.png"
    Image.new("RGB", (1600, 2560), (245, 240, 230)).save(path)
    return path


# ─── TESTS ────────────────────────────────────────────────────────────


def test_library_imports_cleanly() -> None:
    assert callable(rkc.render_kdp_cover)
    assert callable(rkc.load_typography_config)
    assert rkc.CANVAS_W == 1600
    assert rkc.CANVAS_H == 2560


def test_typography_yaml_loads_with_all_nine_genres() -> None:
    cfg = rkc.load_typography_config()
    assert "genres" in cfg
    assert "defaults" in cfg
    expected = {
        "anxiety", "self_worth", "overthinking", "boundaries",
        "burnout", "grief", "courage", "imposter_syndrome", "sleep_anxiety",
    }
    assert set(cfg["genres"].keys()) == expected, (
        f"Expected exactly the 9 production genres, got {set(cfg['genres'].keys())}"
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
        for key in ("font_family", "font_weight", "size_px_at_1600x2560", "case", "color"):
            assert key in style, f"{name}.title_style missing {key}"


def test_render_writes_exact_canvas_size(dark_illustration: Path, tmp_path: Path) -> None:
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


def test_auto_color_picks_light_on_dark_zone(dark_illustration: Path, tmp_path: Path) -> None:
    out = tmp_path / "cover_dark.png"
    meta = rkc.render_kdp_cover(
        illustration_path=dark_illustration, title="Dark Test", author="A",
        genre="anxiety", output_path=out,
    )
    r, g, b = meta["title_color_rgb"]
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    assert luminance > 0.7, f"On dark illustration expected light text, got rgb={meta['title_color_rgb']}"


def test_auto_color_picks_dark_on_light_zone(light_illustration: Path, tmp_path: Path) -> None:
    out = tmp_path / "cover_light.png"
    meta = rkc.render_kdp_cover(
        illustration_path=light_illustration, title="Light Test", author="A",
        genre="anxiety", output_path=out,
    )
    r, g, b = meta["title_color_rgb"]
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    assert luminance < 0.3, f"On light illustration expected dark text, got rgb={meta['title_color_rgb']}"


def test_typography_overrides_accepted(dark_illustration: Path, tmp_path: Path) -> None:
    out = tmp_path / "cover_override.png"
    meta = rkc.render_kdp_cover(
        illustration_path=dark_illustration, title="Override Test", author="A",
        genre="anxiety", output_path=out,
        typography_overrides={"title_style": {"color": "#FF00FF"}},
    )
    assert tuple(meta["title_color_rgb"]) == (255, 0, 255)


def test_genre_layouts_differ_anxiety_vs_grief(dark_illustration: Path, tmp_path: Path) -> None:
    """Anxiety puts title at top; grief puts title near center. Outputs differ."""
    cfg = rkc.load_typography_config()
    anxiety_zone = cfg["genres"]["anxiety"]["title_zone"]
    grief_zone = cfg["genres"]["grief"]["title_zone"]
    assert anxiety_zone["position"] != grief_zone["position"], (
        "Genre defaults must produce visually different layouts"
    )
    assert anxiety_zone["vertical_offset_pct"] < grief_zone["vertical_offset_pct"]

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
    # Pixel diff: at least *some* pixels must differ between the two layouts.
    img_a = Image.open(out_a).convert("RGB")
    img_g = Image.open(out_g).convert("RGB")
    diff = sum(
        1 for pa, pg in zip(img_a.getdata(), img_g.getdata()) if pa != pg
    )
    assert diff > 1000, f"Anxiety vs grief covers nearly identical (diff_px={diff})"


def test_centered_anchor_horizontally_centers_title(dark_illustration: Path, tmp_path: Path) -> None:
    """For anchor='centered', text bounding box should be roughly centered."""
    out = tmp_path / "centered.png"
    rkc.render_kdp_cover(
        illustration_path=dark_illustration, title="Centered",
        author="A", genre="anxiety", output_path=out,
    )
    img = Image.open(out).convert("RGB")
    # Find non-background pixels in top portion of canvas.
    base = (15, 23, 42)
    left_count = right_count = 0
    cx = 1600 // 2
    # Sample title zone band
    pixels = img.load()
    for y in range(150, 700, 4):
        for x in range(0, 1600, 4):
            if pixels[x, y] != base:
                if x < cx:
                    left_count += 1
                elif x > cx:
                    right_count += 1
    assert left_count > 0 and right_count > 0
    # Symmetry: the lighter side shouldn't be more than ~3x the heavier side
    ratio = max(left_count, right_count) / max(1, min(left_count, right_count))
    assert ratio < 3.0, f"Title not centered (left={left_count} right={right_count})"


def test_refuses_missing_illustration(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        rkc.render_kdp_cover(
            illustration_path=tmp_path / "does_not_exist.png",
            title="X", author="Y", genre="anxiety",
            output_path=tmp_path / "out.png",
        )


def test_refuses_missing_title(dark_illustration: Path, tmp_path: Path) -> None:
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


def test_unknown_genre_refused(dark_illustration: Path, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unknown genre"):
        rkc.render_kdp_cover(
            illustration_path=dark_illustration, title="X", author="Y",
            genre="not_a_real_genre", output_path=tmp_path / "out.png",
        )


def test_batch_lists_books_without_crash(tmp_path: Path) -> None:
    """--batch reads TEACHER_BOOKS and processes each. With no real
    illustrations in tmp, every book should be reported as skipped — no crash."""
    fake_repo = tmp_path / "fake_repo"
    fake_repo.mkdir()
    with mock.patch.object(rkc, "_find_latest_illustration", return_value=None):
        results = rkc._run_batch()
    assert isinstance(results, list)
    assert len(results) >= 13, f"Expected ≥13 teacher books, got {len(results)}"
    assert all(r["status"] == "skipped_no_illustration" for r in results)


def test_resize_non_canonical_illustration(tmp_path: Path) -> None:
    """Illustration of wrong size is resized to 1600x2560 before composite."""
    weird = tmp_path / "weird.png"
    Image.new("RGB", (800, 1280), (40, 40, 80)).save(weird)
    out = tmp_path / "resized.png"
    meta = rkc.render_kdp_cover(
        illustration_path=weird, title="Resize Test", author="A",
        genre="anxiety", output_path=out,
    )
    assert meta["output_size"] == (1600, 2560)
    assert Image.open(out).size == (1600, 2560)
