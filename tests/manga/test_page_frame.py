"""Tests for the page-layout FRAME engine (phoenix_v4/manga/chapter/page_frame.py).

Covers (a) pure template selection / genre-profile resolution (no PIL) and
(b) PIL-backed framed rendering: borders + gutters present, splash is borderless,
RTL mirrors cell order, overflow spills to follow-on pages, healing register
picks the calm iyashikei family.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.page_frame import (  # type: ignore
    PageFrameError,
    compose_framed_page_pngs,
    load_grid_library,
    render_framed_page,
    resolve_genre_profile,
    select_template,
)

PIL = pytest.importorskip("PIL")
from PIL import Image  # type: ignore  # noqa: E402


# ─── pure: library + selection ─────────────────────────────────────────────


def test_library_loads_and_has_sections():
    lib = load_grid_library()
    assert "layout_families" in lib
    assert "genre_profiles" in lib
    assert "standard" in lib["layout_families"]
    assert "iyashikei" in lib["layout_families"]


def test_genre_alias_devotion_resolves_to_healing_family():
    lib = load_grid_library()
    prof = resolve_genre_profile("devotion_path", lib=lib)
    assert prof["layout_family"] == "iyashikei"
    # healing register breathes more than shonen
    shonen = resolve_genre_profile("shonen", lib=lib)
    assert prof["gutter_px"] > shonen["gutter_px"]
    assert prof["outer_margin_px"] > shonen["outer_margin_px"]
    assert prof["cell_fill"] == "contain"  # never crop contemplative space


def test_unknown_genre_falls_back_to_default():
    lib = load_grid_library()
    prof = resolve_genre_profile("not_a_real_genre", lib=lib)
    assert prof["layout_family"] == "standard"


def test_select_template_exact_count():
    tpl = select_template(4, page_type="standard", genre="shonen")
    assert tpl["panel_capacity"] == 4
    assert len(tpl["cells"]) == 4
    for c in tpl["cells"]:
        assert len(c) == 4  # [x, y, w, h]


def test_select_template_healing_caps_panels():
    # healing profile max_panels_per_page == 4 → 6 panels still selects 4-cell
    tpl = select_template(6, page_type="standard", genre="healing")
    assert tpl["panel_capacity"] == 4


def test_splash_forces_single_borderless_cell():
    tpl = select_template(3, page_type="splash", genre="shonen")
    assert tpl["panel_capacity"] == 1
    assert tpl["cells"] == [[0.0, 0.0, 1.0, 1.0]]
    assert tpl["page_type_rule"].get("border") is False


def test_cells_are_within_unit_square_and_disjoint_ish():
    tpl = select_template(4, page_type="standard", genre="shonen")
    for x, y, w, h in tpl["cells"]:
        assert 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0
        assert 0.0 < w <= 1.0 and 0.0 < h <= 1.0
        assert x + w <= 1.0001 and y + h <= 1.0001


# ─── PIL: framed render ────────────────────────────────────────────────────


def _solid(w: int, h: int, rgb=(180, 200, 220)) -> Image.Image:
    return Image.new("RGB", (w, h), rgb)


def test_render_two_panel_page_has_borders_and_gutter():
    panels = [_solid(800, 600), _solid(800, 600)]
    page = render_framed_page(panels, page_type="standard", genre="shonen")
    assert page.mode == "RGBA"
    assert page.width > 0 and page.height > 0
    # There must be black border pixels somewhere (stroke drawn).
    px = page.convert("RGB").load()
    found_black = any(
        px[x, y] == (0, 0, 0)
        for x in range(0, page.width, 7)
        for y in range(0, page.height, 7)
    )
    assert found_black, "expected visible black panel border pixels"
    # There must be white background (gutter / margin) too.
    found_white = any(
        px[x, y] == (255, 255, 255)
        for x in range(0, page.width, 7)
        for y in range(0, page.height, 7)
    )
    assert found_white, "expected white gutter/margin pixels"


def test_splash_has_no_border():
    page = render_framed_page([_solid(800, 1200)], page_type="splash", genre="shonen")
    px = page.convert("RGB").load()
    # Splash is full-bleed: corners are the panel color, not white margin or
    # black border.
    assert px[2, 2] != (0, 0, 0)
    assert px[page.width - 3, page.height - 3] != (0, 0, 0)


def test_rtl_mirrors_first_panel_to_the_right():
    # Distinct colors so we can locate panel 0 (first read) physically.
    left_color = (255, 0, 0)
    right_color = (0, 0, 255)
    panels = [_solid(800, 1200, left_color), _solid(800, 1200, right_color)]
    # Use a side-by-side 2-up layout via 'standard' family? standard[2] stacks
    # vertically; instead use iyashikei[3] hero+stack which splits on x. Simpler:
    # verify mirror at the cell level.
    from phoenix_v4.manga.chapter.page_frame import _mirror_cells_rtl

    cells = [[0.0, 0.0, 0.5, 1.0], [0.5, 0.0, 0.5, 1.0]]
    mirrored = _mirror_cells_rtl(cells)
    # First-read cell (index 0) should now sit on the right half.
    assert mirrored[0][0] == pytest.approx(0.5)
    assert mirrored[1][0] == pytest.approx(0.0)


def test_healing_render_uses_contain_keeps_whitespace():
    # A wide panel placed with 'contain' into a tall-ish cell leaves background
    # padding → there should be MORE white than a shonen crop of the same input.
    wide = _solid(1600, 400, (120, 160, 120))
    healing = render_framed_page([wide, wide], page_type="standard", genre="healing")
    shonen = render_framed_page([wide, wide], page_type="standard", genre="shonen")

    def white_frac(img: Image.Image) -> float:
        rgb = img.convert("RGB")
        px = rgb.load()
        tot = wcount = 0
        for x in range(0, rgb.width, 9):
            for y in range(0, rgb.height, 9):
                tot += 1
                if px[x, y] == (255, 255, 255):
                    wcount += 1
        return wcount / max(1, tot)

    assert white_frac(healing) > white_frac(shonen)


# ─── manifest-driven composition ───────────────────────────────────────────


def _write_panel(dirp: Path, pid: str, rgb=(150, 170, 190)) -> Path:
    p = dirp / f"{pid}.png"
    _solid(900, 700, rgb).save(p)
    return p


def test_compose_framed_page_pngs_writes_pages(tmp_path: Path):
    pdir = tmp_path / "panels"
    pdir.mkdir()
    p1 = _write_panel(pdir, "p1", (200, 100, 100))
    p2 = _write_panel(pdir, "p2", (100, 200, 100))
    p3 = _write_panel(pdir, "p3", (100, 100, 200))

    script = {
        "pages": [
            {
                "page_number": 1,
                "page_type": "standard",
                "panels": [
                    {"panel_id": "p1"},
                    {"panel_id": "p2"},
                    {"panel_id": "p3"},
                ],
            }
        ]
    }
    manifest = {
        "panels": [
            {"panel_id": "p1", "status": "ok", "path": str(p1)},
            {"panel_id": "p2", "status": "ok", "path": str(p2)},
            {"panel_id": "p3", "status": "ok", "path": str(p3)},
        ]
    }
    out = tmp_path / "out"
    pages = compose_framed_page_pngs(script, manifest, out, genre="iyashikei")
    assert len(pages) == 1
    assert pages[0].name == "page_001.png"
    assert pages[0].is_file()


def test_compose_overflow_spills_to_followon_pages(tmp_path: Path):
    pdir = tmp_path / "panels"
    pdir.mkdir()
    # 6 panels but healing capacity == 4 → spills to a 2nd page.
    panels = []
    for i in range(6):
        pid = f"p{i}"
        _write_panel(pdir, pid)
        panels.append({"panel_id": pid})
    script = {"pages": [{"page_number": 1, "page_type": "standard", "panels": panels}]}
    manifest = {
        "panels": [
            {"panel_id": f"p{i}", "status": "ok", "path": str(pdir / f"p{i}.png")}
            for i in range(6)
        ]
    }
    out = tmp_path / "out"
    pages = compose_framed_page_pngs(script, manifest, out, genre="healing")
    assert len(pages) == 2  # 4 + 2


def test_compose_skips_non_ok_panels(tmp_path: Path):
    pdir = tmp_path / "panels"
    pdir.mkdir()
    p1 = _write_panel(pdir, "p1")
    script = {
        "pages": [
            {
                "page_number": 1,
                "page_type": "standard",
                "panels": [{"panel_id": "p1"}, {"panel_id": "p2"}],
            }
        ]
    }
    manifest = {
        "panels": [
            {"panel_id": "p1", "status": "ok", "path": str(p1)},
            {"panel_id": "p2", "status": "pending"},  # not ok → skipped
        ]
    }
    out = tmp_path / "out"
    pages = compose_framed_page_pngs(script, manifest, out)
    assert len(pages) == 1  # only p1 placed


def test_compose_empty_manifest_yields_no_pages(tmp_path: Path):
    script = {"pages": [{"page_number": 1, "panels": [{"panel_id": "p1"}]}]}
    manifest = {"panels": [{"panel_id": "p1", "status": "pending"}]}
    out = tmp_path / "out"
    pages = compose_framed_page_pngs(script, manifest, out)
    assert pages == []
