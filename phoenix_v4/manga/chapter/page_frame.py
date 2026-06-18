"""Page-layout FRAME engine — grid templates + frame/gutter renderer.

Until this module existed, ``page_compose.py`` tiled panel PNGs edge-to-edge in
a single horizontal strip and ``config/manga/panel_layout_templates/*.yaml`` were
inert (no renderer read ``panels_per_page`` / ``page_aspect`` / ``variable_grid``).
This module is the missing piece described in ``specs/MANGA_LAYOUT_AGENT_SPEC.md``
§4–§6: it

  1. loads a named multi-panel page-template LIBRARY (``config/manga/
     page_grid_templates.yaml``) of panel bounding-box sets keyed by
     ``(panel_count, page_type, genre)``, incl. irregular grids + splash +
     double-spread, with a calmer iyashikei/healing family,
  2. picks a template from the page's ``page_type`` + panel count + the
     series/brand genre (consuming ``panel_layout_templates/*.yaml`` page_aspect
     and per-panel ``aspect_hint``/``beat_type`` when present),
  3. renders the page with PIL: fits each panel image into its cell by aspect
     (crop-to-fill or contain), lays inter-panel gutters, and draws panel
     borders (stroke); supports RTL page-turn order for B&W tankōbon.

Public API
----------
``render_framed_page(panel_images, *, page_type, genre, reading_direction,
                     page_aspect, ...) -> PIL.Image``
    Compose a list of already-rendered panel images into one framed page.

``compose_framed_page_pngs(chapter_script, panel_images_manifest, out_dir, ...)``
    Drop-in replacement for ``page_compose.compose_final_page_pngs`` — writes
    ``page_001.png`` … with framed multi-panel grids instead of raw strips.

``select_template(panel_count, *, page_type, genre)`` / ``load_grid_library()``
    Pure helpers (no PIL) so tests + callers can introspect the chosen layout.

Genre defaults to the **healing/iyashikei** register for the Devotion brand
(Open Vessel Press / devotion_path / teacher Sai Ma) per the locked P0 decision:
devotion manga is HEALING / devotional-emotional-drama, NOT shonen/action.
"""
from __future__ import annotations

import functools
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

# ── Config location ──────────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).resolve().parents[3]
GRID_LIBRARY_PATH = _REPO_ROOT / "config" / "manga" / "page_grid_templates.yaml"

# Aspect ratio (w/h) lookup for the aspect_hint vocabulary used by
# config/manga/panel_templates/iyashikei.yaml. Used only as a *tiebreak hint*
# when scoring which cell a panel prefers — geometry still comes from the grid.
ASPECT_HINT_WH: dict[str, float] = {
    "square_1_1": 1.0,
    "portrait_4_5": 4 / 5,
    "tall_9_16": 9 / 16,
    "wide_16_9": 16 / 9,
    "portrait_4_5_or_square_1_1": (4 / 5 + 1.0) / 2,
    "square_1_1_or_portrait_4_5": (1.0 + 4 / 5) / 2,
    "wide_16_9_or_tall_9_16": (16 / 9 + 9 / 16) / 2,
}


class PageFrameError(RuntimeError):
    """Raised on unrecoverable layout/composition errors."""


# ── Library loading ──────────────────────────────────────────────────────────


@functools.lru_cache(maxsize=4)
def load_grid_library(path: str | None = None) -> dict[str, Any]:
    """Load and cache the page-grid template library YAML."""
    p = Path(path) if path else GRID_LIBRARY_PATH
    if not p.is_file():
        raise PageFrameError(f"grid library not found: {p}")
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if "layout_families" not in data or "genre_profiles" not in data:
        raise PageFrameError(f"grid library {p} missing required sections")
    return data


def resolve_genre_profile(genre: str | None, *, lib: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve a genre string to its profile dict (gutter/border/family/…).

    Unknown genres fall back to the ``default`` profile. Aliases (e.g.
    ``devotion_path`` → ``devotional``, ``cultivation`` → ``shonen``) are
    resolved via ``genre_alias``.
    """
    profiles = lib["genre_profiles"]
    alias = lib.get("genre_alias") or {}
    key = (genre or "").strip().lower()
    key = alias.get(key, key)
    prof = profiles.get(key) or profiles.get("default")
    if prof is None:
        raise PageFrameError("grid library has no 'default' genre profile")
    return dict(prof)


def select_template(
    panel_count: int,
    *,
    page_type: str = "standard",
    genre: str | None = None,
    lib: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Pick a page template for ``panel_count`` panels.

    Returns a dict::

        {
          "cells":          [ [x,y,w,h], ... ],   # fractional, content-area space
          "panel_capacity": int,                  # how many panels this page holds
          "page_type":      str,
          "genre_profile":  {...},                # gutter/border/margin/fill
          "page_type_rule": {...},                # splash/silent/etc overrides
        }

    If ``panel_count`` exceeds the largest defined template the caller should
    place ``panel_capacity`` panels here and overflow the rest to a follow-on
    page (``compose_framed_page_pngs`` does this automatically).
    """
    library = lib or load_grid_library()
    prof = resolve_genre_profile(genre, lib=library)
    family_name = prof.get("layout_family", "standard")
    families = library["layout_families"]
    family = families.get(family_name) or families["standard"]
    pt_rules = (library.get("page_type_rules") or {}).get(page_type, {}) or {}

    # Splash / single-cell page types force one full-bleed cell.
    if pt_rules.get("force_single_cell"):
        return {
            "cells": [[0.0, 0.0, 1.0, 1.0]],
            "panel_capacity": 1,
            "page_type": page_type,
            "genre_profile": prof,
            "page_type_rule": pt_rules,
        }

    cap = max(1, int(prof.get("max_panels_per_page", 6)))
    want = max(1, min(int(panel_count), cap))

    # Exact match, else the largest defined layout <= want.
    available = sorted(int(k) for k in family.keys())
    chosen_n = None
    for n in available:
        if n == want:
            chosen_n = n
            break
    if chosen_n is None:
        le = [n for n in available if n <= want]
        chosen_n = max(le) if le else min(available)

    raw_cells = family[chosen_n]
    cells = [list(c["bbox"]) for c in raw_cells]
    return {
        "cells": cells,
        "panel_capacity": len(cells),
        "page_type": page_type,
        "genre_profile": prof,
        "page_type_rule": pt_rules,
    }


# ── Geometry helpers ─────────────────────────────────────────────────────────


def _page_pixel_size(page_aspect: str, long_edge_px: int) -> tuple[int, int]:
    """Return (width, height) px for an aspect 'W:H' with the H == long_edge_px
    for portrait, or W == long_edge_px for landscape."""
    try:
        ws, hs = page_aspect.replace("approx_", "").split(":")
        wr, hr = float(ws), float(hs)
    except Exception:
        wr, hr = 2.0, 3.0
    if hr >= wr:  # portrait (or square): height is the long edge
        h = int(long_edge_px)
        w = int(round(long_edge_px * wr / hr))
    else:  # landscape: width is the long edge
        w = int(long_edge_px)
        h = int(round(long_edge_px * hr / wr))
    return max(1, w), max(1, h)


def _mirror_cells_rtl(cells: Sequence[Sequence[float]]) -> list[list[float]]:
    """Mirror cell x-coordinates for right-to-left reading.

    The cell list stays in reading order (index 0 = first panel read); only the
    physical x position flips so the first-read panel sits on the right.
    """
    out: list[list[float]] = []
    for x, y, w, h in cells:
        out.append([1.0 - x - w, y, w, h])
    return out


def _fit_into_cell(im: Any, cw: int, ch: int, *, mode: str, bg: tuple[int, int, int]):
    """Return an RGBA image exactly ``cw`` x ``ch`` containing ``im``.

    mode="crop"    → scale to cover the cell, center-crop the overflow (manga
                     panels read full-bleed within their frame).
    mode="contain" → scale to fit inside the cell, pad with background (healing
                     register keeps contemplative negative space intact).
    """
    from PIL import Image  # type: ignore

    if cw <= 0 or ch <= 0:
        return Image.new("RGBA", (1, 1), (*bg, 255))
    src_w, src_h = im.width, im.height
    if src_w <= 0 or src_h <= 0:
        return Image.new("RGBA", (cw, ch), (*bg, 255))

    if mode == "contain":
        scale = min(cw / src_w, ch / src_h)
        nw, nh = max(1, int(round(src_w * scale))), max(1, int(round(src_h * scale)))
        resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (cw, ch), (*bg, 255))
        canvas.paste(resized, ((cw - nw) // 2, (ch - nh) // 2), resized)
        return canvas

    # crop (cover)
    scale = max(cw / src_w, ch / src_h)
    nw, nh = max(1, int(round(src_w * scale))), max(1, int(round(src_h * scale)))
    resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - cw) // 2)
    top = max(0, (nh - ch) // 2)
    cropped = resized.crop((left, top, left + cw, top + ch))
    return cropped


# ── Page renderer ────────────────────────────────────────────────────────────


def render_framed_page(
    panel_images: Sequence[Any],
    *,
    page_type: str = "standard",
    genre: str | None = None,
    reading_direction: str = "ltr",
    page_aspect: str | None = None,
    long_edge_px: int | None = None,
    lib: Mapping[str, Any] | None = None,
):
    """Compose ``panel_images`` (PIL images, reading order) into one framed page.

    Returns a single RGBA ``PIL.Image`` with panel borders + gutters. Honors
    ``page_type`` (splash → borderless full bleed; silent → wider gutters),
    ``genre`` (healing/iyashikei → calmer profile), and ``reading_direction``
    (``rtl`` / ``right_to_left*`` → mirror cell x so first-read panel is on the
    right).
    """
    from PIL import Image, ImageDraw  # type: ignore

    library = lib or load_grid_library()
    pdefaults = library.get("page_defaults") or {}
    page_aspect = page_aspect or str(pdefaults.get("page_aspect", "2:3"))
    long_edge_px = int(long_edge_px or pdefaults.get("long_edge_px", 2400))
    bg = tuple(pdefaults.get("background_rgb", [255, 255, 255]))[:3]  # type: ignore

    n = len(panel_images)
    if n == 0:
        raise PageFrameError("render_framed_page called with zero panels")

    tpl = select_template(n, page_type=page_type, genre=genre, lib=library)
    prof = tpl["genre_profile"]
    pt_rule = tpl["page_type_rule"]
    cells = tpl["cells"]

    # Resolve frame cosmetics (page_type overrides genre profile).
    gutter_px = int(pt_rule.get("gutter_px", prof.get("gutter_px", 48)))
    if "gutter_multiplier" in pt_rule:
        gutter_px = int(round(gutter_px * float(pt_rule["gutter_multiplier"])))
    border_on = pt_rule.get("border", True)
    if border_on is None:
        border_on = True
    stroke = int(prof.get("border_stroke_px", 8)) if border_on else 0
    border_rgb = tuple(prof.get("border_rgb", [0, 0, 0]))[:3]  # type: ignore
    margin = int(pt_rule.get("outer_margin_px", prof.get("outer_margin_px", 90)))
    fill_mode = str(prof.get("cell_fill", "crop"))

    # Page pixel canvas; double-spread doubles the width and adds a spine gutter.
    pw, ph = _page_pixel_size(page_aspect, long_edge_px)
    spread = bool(pt_rule.get("spread"))
    center_gutter = int(pt_rule.get("center_gutter_px", 60)) if spread else 0
    if spread:
        pw = pw * 2 + center_gutter

    page = Image.new("RGBA", (pw, ph), (*bg, 255))

    # RTL mirror.
    rd = (reading_direction or "ltr").lower()
    if rd.startswith("rtl") or "right_to_left" in rd or rd == "right_to_left_horizontal":
        cells = _mirror_cells_rtl(cells)

    # Content area = page minus outer margin (and spine for spreads).
    content_x = margin
    content_y = margin
    content_w = pw - 2 * margin
    content_h = ph - 2 * margin
    if content_w <= 0 or content_h <= 0:
        content_x, content_y, content_w, content_h = 0, 0, pw, ph

    draw = ImageDraw.Draw(page)
    half_g = gutter_px / 2.0

    n_cells = min(n, len(cells))
    for i in range(n_cells):
        fx, fy, fw, fh = cells[i]
        # Fractional cell → absolute px within content area.
        cx0 = content_x + fx * content_w
        cy0 = content_y + fy * content_h
        cx1 = content_x + (fx + fw) * content_w
        cy1 = content_y + (fy + fh) * content_h
        # Inset by half a gutter on each interior side (clamp to page edge so
        # outer cells don't get a stray half-gutter at the margin).
        ix0 = cx0 + (half_g if fx > 1e-6 else 0)
        iy0 = cy0 + (half_g if fy > 1e-6 else 0)
        ix1 = cx1 - (half_g if (fx + fw) < 1 - 1e-6 else 0)
        iy1 = cy1 - (half_g if (fy + fh) < 1 - 1e-6 else 0)
        cell_w = int(round(ix1 - ix0))
        cell_h = int(round(iy1 - iy0))
        if cell_w < 1 or cell_h < 1:
            continue

        im = panel_images[i]
        if im.mode != "RGBA":
            im = im.convert("RGBA")
        fitted = _fit_into_cell(im, cell_w, cell_h, mode=fill_mode, bg=bg)
        ox, oy = int(round(ix0)), int(round(iy0))
        page.paste(fitted, (ox, oy), fitted)

        if stroke > 0:
            # Border drawn straddling the cell edge (outline outside per spec
            # §4.4: rectangle inflated by half the stroke).
            off = stroke / 2.0
            draw.rectangle(
                [ox - off, oy - off, ox + cell_w - 1 + off, oy + cell_h - 1 + off],
                outline=border_rgb,
                width=stroke,
            )

    return page


# ── Manifest-driven page composition (drop-in for page_compose) ──────────────


def _paths_by_panel_id(manifest: Mapping[str, Any]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for p in manifest.get("panels") or []:
        if str(p.get("status")) != "ok":
            continue
        path = p.get("path")
        if not path:
            continue
        out[str(p["panel_id"])] = Path(str(path)).resolve()
    return out


def _meta_by_panel_id(manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Carry per-panel render metadata (aspect_hint/beat_type/framing) if the
    manifest recorded it — used as soft hints; geometry stays grid-driven."""
    out: dict[str, dict[str, Any]] = {}
    for p in manifest.get("panels") or []:
        pid = p.get("panel_id")
        if pid is None:
            continue
        out[str(pid)] = dict(p)
    return out


def _resolve_genre(chapter_script: Mapping[str, Any], explicit: str | None) -> str | None:
    if explicit:
        return explicit
    for key in ("genre", "genre_family", "manga_genre", "register"):
        v = chapter_script.get(key)
        if v:
            return str(v)
    return None


def compose_framed_page_pngs(
    chapter_script: Mapping[str, Any],
    panel_images_manifest: Mapping[str, Any],
    out_dir: Path,
    *,
    genre: str | None = None,
    reading_direction: str | None = None,
    page_aspect: str | None = None,
    long_edge_px: int | None = None,
    lib: Mapping[str, Any] | None = None,
) -> list[Path]:
    """Write framed ``page_001.png`` … under ``out_dir`` (drop-in replacement for
    ``page_compose.compose_final_page_pngs``).

    For each page in ``chapter_script.pages``:
      * reads its ``page_type`` (default ``standard``),
      * selects a grid template by (panel_count, page_type, genre),
      * fits each ok panel image into its cell and draws borders + gutters.

    If a page declares more panels than the chosen template holds, the extra
    panels spill onto follow-on ``page_NNN`` composites so no panel is dropped.
    Pages whose panels are all non-ok (noop/dry-run backend) are skipped.
    """
    try:
        from PIL import Image  # type: ignore  # noqa: F401
    except ImportError as e:  # pragma: no cover
        raise PageFrameError(
            "compose_framed_page_pngs requires Pillow; pip install Pillow"
        ) from e
    from PIL import Image

    library = lib or load_grid_library()
    by_id = _paths_by_panel_id(panel_images_manifest)
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    genre = _resolve_genre(chapter_script, genre)
    # Reading direction: explicit arg wins, else chapter_script, else per-page.
    rd_default = reading_direction or str(
        chapter_script.get("reading_direction") or ""
    )

    written: list[Path] = []
    page_counter = 0
    pages = chapter_script.get("pages") or []
    for page in pages:
        page_type = str(page.get("page_type") or "standard")
        rd = str(page.get("reading_direction") or rd_default or "ltr")

        # Gather this page's ok panel image paths in declared order.
        paths: list[Path] = []
        for panel in page.get("panels") or []:
            pid = str(panel.get("panel_id") or "")
            if not pid:
                continue
            fp = by_id.get(pid)
            if fp is None or not fp.is_file():
                # non-ok panel — skip silently (matches noop/dry_run tolerance)
                continue
            paths.append(fp)

        if not paths:
            continue

        # Determine capacity for this (page_type, genre) so we can spill overflow.
        probe = select_template(
            len(paths), page_type=page_type, genre=genre, lib=library
        )
        capacity = max(1, int(probe["panel_capacity"]))

        for start in range(0, len(paths), capacity):
            chunk = paths[start : start + capacity]
            loaded = [Image.open(p).convert("RGBA") for p in chunk]
            try:
                page_img = render_framed_page(
                    loaded,
                    page_type=page_type,
                    genre=genre,
                    reading_direction=rd,
                    page_aspect=page_aspect,
                    long_edge_px=long_edge_px,
                    lib=library,
                )
                page_counter += 1
                out_path = out_dir / f"page_{page_counter:03d}.png"
                page_img.save(out_path, format="PNG")
                written.append(out_path)
            finally:
                for im in loaded:
                    im.close()
                try:
                    page_img.close()  # type: ignore[has-type]
                except Exception:
                    pass

    return written
