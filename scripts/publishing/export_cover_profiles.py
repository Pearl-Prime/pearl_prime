#!/usr/bin/env python3
"""L5 platform cover exporter — non-destructive per-platform adaptation.

Lane 3 of docs/authoring/BOOK_COVER_UNIFIED_RESEARCH_2026-07-01.md §7.
Ratified defaults OPD-20260701-001 (Q-LEVELS-01, Q-PLATFORM-PRIORITY-01,
Q-PROFILE-MASTER-01). First consumer: Kobo 3:4 (``kobo_ebook``).

WHAT THIS IS
------------
A config-driven exporter that takes an L4 book design (author_id, book_id,
genre) + a platform profile key and produces the correct per-platform asset.
Platform is the **non-destructive L5 adaptation layer** (Q-LEVELS-01): it
re-presents the SAME L1-L4 portrait design at the target aspect/size/format —
it NEVER re-runs FLUX and NEVER changes the core design.

MASTER-RENDER-THEN-REFLOW (Q-PROFILE-MASTER-01)
-----------------------------------------------
1. Render (or load) the L4 portrait master via
   ``scripts.publish.render_kdp_cover.render_kdp_cover`` (native 1600x2560,
   5:8 = 0.625). Imagery only comes from the existing render path; NO FLUX
   re-prompt here.
2. Reflow the master to the profile aspect with **cover-fit** (uniform
   scale-to-fill + center-crop). Because Kobo 3:4 (0.75) is *wider* than KDP
   5:8 (0.625), cover-fit scales by height and crops horizontal excess — no
   letterbox bars (profile ``letterbox_allowed: false``), no aspect
   distortion (uniform scale, never stretch).
3. Re-composite the title/byline text at the NEW geometry (PIL stage) and
   re-run the WCAG-AA 4.5:1 contrast pick against the reflowed text zone's
   actual luminance (§2.3 carry-across — luminance changes at a new aspect).
4. Export PNG + JPEG (quality-step 92->75 by 3, floored at the profile's
   ``max_file_mb``, per AUTHOR_COVER_ART_SPEC §6). The high-DPI master
   (2500x3500) is emitted too and downscaled to the 1920x2560 recommended
   submission size (§4 "prefer for Kobo-first").

DETERMINISM (§2.3)
------------------
L5 is a pure function of the L4 master + target profile — no new randomness.
Same ``(author_id, book_id, profile_key)`` -> byte-identical bytes. pHash
anti-dup is carried at the L4 design (guard scoped by book_id) so platform
variants of the same book are intentionally near-identical and do not trip
the guard against each other.

Utilities are IMPORTED, never forked:
  scripts.publish.render_kdp_cover  -> render_kdp_cover, _pick_contrast_color,
    _zone_avg_luminance, _luminance_rgb, _hex_to_rgb, _draw_block_in_zone,
    _pct_zone_to_pixels, load_typography_config, load_templates_config,
    CANVAS_W, CANVAS_H
  scripts.publishing.load_cover_profiles -> get_profile, aspect_matches

Authority:
  docs/authoring/BOOK_COVER_UNIFIED_RESEARCH_2026-07-01.md §2.3/§3.1/§5.2/§7
  docs/authoring/AUTHOR_COVER_ART_SPEC.md §3/§4/§6/§7
  config/publishing/platform_cover_profiles.yaml (SSOT)

CLI:
  python3 scripts/publishing/export_cover_profiles.py \
      --book-id corporate_managers_burnout --author-id lena_thorne \
      --genre anxiety --title "The Quiet Fix" --author "Lena Thorne" \
      --profile kobo_ebook
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any

from PIL import Image

# Repo root on sys.path so the sibling render module imports cleanly whether
# invoked as a module or a script.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# IMPORT the render + contrast utilities — do NOT fork them.
from scripts.publish import render_kdp_cover as rkc  # noqa: E402
from scripts.publishing.load_cover_profiles import (  # noqa: E402
    aspect_matches,
    get_profile,
)

DEFAULT_OUT_ROOT = _REPO_ROOT / "artifacts" / "covers"

# WCAG-AA target contrast ratio (AUTHOR_COVER_ART_SPEC §4).
WCAG_AA_RATIO = 4.5

# JPEG quality stepping (AUTHOR_COVER_ART_SPEC §6): start 92, step -3, floor 75.
JPEG_QUALITY_START = 92
JPEG_QUALITY_FLOOR = 75
JPEG_QUALITY_STEP = 3


# ─── DETERMINISM SEED (§2.3 / AUTHOR_COVER_ART_SPEC §5) ───────────────


def _l4_seed(author_id: str, book_id: str) -> str:
    """SHA256(author_id + ':' + book_id) — the L4 design seed. L5 adds no
    randomness, so the seed is carried unchanged into the export metadata."""
    return hashlib.sha256(f"{author_id}:{book_id}".encode("utf-8")).hexdigest()


# ─── SIMPLE pHASH (AUTHOR_COVER_ART_SPEC §7 — 16x16 average-hash) ─────


def average_hash(image: Image.Image, hash_size: int = 16) -> int:
    """Simplified average-hash (16x16 grayscale), per AUTHOR_COVER_ART_SPEC §7.

    Pure-PIL — no ``imagehash`` dependency at this tier. Returns an int whose
    bits are 1 where the pixel exceeds the grayscale mean. For production at
    scale the spec notes an upgrade path to DCT-based pHash.
    """
    small = image.convert("L").resize((hash_size, hash_size), Image.Resampling.LANCZOS)
    pixels = list(small.getdata())
    avg = sum(pixels) / len(pixels)
    bits = 0
    for px in pixels:
        bits = (bits << 1) | (1 if px >= avg else 0)
    return bits


def hamming_distance(a: int, b: int) -> int:
    """Bit-count of a XOR b."""
    return bin(a ^ b).count("1")


# ─── ASPECT REFLOW (cover-fit: scale-to-fill + center-crop) ──────────


def _cover_fit(image: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Reflow ``image`` to exactly (target_w, target_h) with cover-fit.

    Uniform scale-to-fill then center-crop the overflow axis. This preserves
    composition and never distorts (no stretch) and never letterboxes (no
    bars) — the L5 non-destructive re-present of the same design at a new
    aspect. Profiles with ``letterbox_allowed: false`` REQUIRE this behavior.
    """
    src_w, src_h = image.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w = max(target_w, int(round(src_w * scale)))
    new_h = max(target_h, int(round(src_h * scale)))
    resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def _has_letterbox_bars(image: Image.Image, bar_px: int = 6, tol: int = 3) -> bool:
    """Detect TRUE letterbox/pillarbox bars: a symmetric pair of opposite
    outer bands, each internally flat AND matching each other, but DISTINCT
    from the image interior. That triad is the signature of padding bars.

    A legitimately flat design background (e.g. a type-dominant cover on a
    solid primary color) is NOT flagged: its edges match the interior, so the
    'distinct from interior' condition fails. Cover-fit never pads, so this is
    a defensive assertion — bars are structurally impossible on that path.
    """
    rgb = image.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    cx, cy = w // 2, h // 2
    interior = px[cx, cy]

    def _flat(coords: list[tuple[int, int]]) -> tuple[int, int, int] | None:
        first = px[coords[0]]
        for c in coords:
            if any(abs(px[c][k] - first[k]) > tol for k in range(3)):
                return None
        return first

    def _distinct(a: tuple[int, int, int], b: tuple[int, int, int]) -> bool:
        return any(abs(a[k] - b[k]) > tol for k in range(3))

    def _match(a: tuple[int, int, int], b: tuple[int, int, int]) -> bool:
        return all(abs(a[k] - b[k]) <= tol for k in range(3))

    step_x = max(1, w // 48)
    step_y = max(1, h // 48)
    top = _flat([(x, y) for y in range(bar_px) for x in range(0, w, step_x)])
    bot = _flat([(x, y) for y in range(h - bar_px, h) for x in range(0, w, step_x)])
    if top and bot and _match(top, bot) and _distinct(top, interior):
        return True
    left = _flat([(x, y) for x in range(bar_px) for y in range(0, h, step_y)])
    right = _flat([(x, y) for x in range(w - bar_px, w) for y in range(0, h, step_y)])
    if left and right and _match(left, right) and _distinct(left, interior):
        return True
    return False


# ─── TEXT RE-COMPOSITE AT NEW GEOMETRY + WCAG RE-CHECK ───────────────


def _pct_zone_to_pixels_scaled(
    zone: dict[str, Any], canvas_w: int, canvas_h: int
) -> tuple[int, int, int, int]:
    """Percent-of-canvas zone -> pixel rect on an arbitrary (canvas_w,
    canvas_h). Mirrors render_kdp_cover._pct_zone_to_pixels but parameterized
    on the reflowed canvas size (which is NOT the fixed 1600x2560)."""
    x_pct = zone["x_pct"]
    y_pct = zone["y_pct"]
    return (
        int(canvas_w * x_pct[0] / 100),
        int(canvas_h * y_pct[0] / 100),
        int(canvas_w * x_pct[1] / 100),
        int(canvas_h * y_pct[1] / 100),
    )


def _recomposite_text_and_check_wcag(
    canvas: Image.Image,
    *,
    genre: str,
    title: str,
    subtitle: str,
    author: str,
    publisher: str | None,
) -> dict[str, Any]:
    """Re-draw title/subtitle/author on the reflowed canvas at the new
    geometry and re-run the WCAG-AA contrast pick against the reflowed text
    zone's ACTUAL luminance (§2.3: luminance shifts at a new aspect).

    Reuses the imported render_kdp_cover helpers — no forked drawing code.
    Returns the WCAG report for the title zone.
    """
    typography_cfg = rkc.load_typography_config()
    templates_cfg = rkc.load_templates_config()
    if genre not in templates_cfg["templates"]:
        raise ValueError(f"genre {genre!r} has no template entry")
    template = templates_cfg["templates"][genre]
    genre_typography = typography_cfg["genres"][genre]

    canvas_w, canvas_h = canvas.size
    rgba = canvas.convert("RGBA")

    palette_options = (
        genre_typography.get("palette_hints", {}).get("hex_palette_fallback")
        or [template["palette"]["secondary"]["hex"]]
    )
    type_dominant = bool(template.get("type_dominant", False))

    report: dict[str, Any] = {}

    def _draw(zone_key: str, style_key: str, text: str, role: str,
              min_size: int, size_pct_key: str) -> None:
        if not text:
            return
        zone = template.get(zone_key)
        if not zone:
            return
        rect = _pct_zone_to_pixels_scaled(zone, canvas_w, canvas_h)
        # WCAG carry-across: sample the reflowed zone's true luminance so the
        # contrast pick reflects the NEW aspect, not the master's.
        zone_lum = rkc._zone_avg_luminance(rgba, rect)
        bg_rgb_sample = tuple(int(round(zone_lum * 255)) for _ in range(3))
        target_pct = template["type_size_ratios"].get(size_pct_key, 6)
        initial = int(canvas_h * target_pct / 100.0)
        style = genre_typography.get(style_key) or typography_cfg.get(
            "defaults", {}
        ).get(f"default_{style_key}", {"font_family": "sans_serif"})
        _size, _lines, fill_rgb = rkc._draw_block_in_zone(
            rgba, text, style, rect,
            type_dominant=type_dominant,
            cfg=typography_cfg,
            palette_options=palette_options,
            background_rgb=bg_rgb_sample,
            initial_size=initial,
            min_size=min_size,
            role=role,
        )
        if role == "title":
            fill_lum = rkc._luminance_rgb(fill_rgb)
            # WCAG relative-contrast ratio (lighter+0.05)/(darker+0.05).
            hi, lo = max(zone_lum, fill_lum), min(zone_lum, fill_lum)
            ratio = (hi + 0.05) / (lo + 0.05)
            report.update(
                {
                    "wcag_zone_luminance": round(zone_lum, 4),
                    "wcag_text_luminance": round(fill_lum, 4),
                    "wcag_contrast_ratio": round(ratio, 3),
                    "wcag_pass": ratio >= WCAG_AA_RATIO,
                    "wcag_target": WCAG_AA_RATIO,
                }
            )

    author_label = f"{author}  ·  {publisher}" if publisher else author
    _draw("title_zone", "title_style", title, "title", 72, "title")
    _draw("subtitle_zone", "subtitle_style", subtitle, "subtitle", 28, "subtitle")
    _draw("author_zone", "author_style", author_label, "author", 22, "author")

    canvas.paste(rgba.convert(canvas.mode))
    return report


# ─── JPEG EXPORT WITH QUALITY STEPPING (AUTHOR_COVER_ART_SPEC §6) ─────


def _export_jpeg(image: Image.Image, path: Path, max_file_mb: float) -> dict[str, Any]:
    """Export JPEG, stepping quality 92->75 by 3 until <= max_file_mb.
    If still over at the floor, export anyway with a warning flag."""
    max_bytes = int(max_file_mb * 1024 * 1024)
    rgb = image.convert("RGB")
    quality = JPEG_QUALITY_START
    warned = False
    while True:
        rgb.save(path, format="JPEG", quality=quality, optimize=True, progressive=True)
        size = path.stat().st_size
        if size <= max_bytes or quality <= JPEG_QUALITY_FLOOR:
            if size > max_bytes:
                warned = True
            break
        quality -= JPEG_QUALITY_STEP
    return {
        "path": str(path),
        "quality": quality,
        "bytes": path.stat().st_size,
        "max_bytes": max_bytes,
        "over_budget": warned,
    }


# ─── PUBLIC API ──────────────────────────────────────────────────────


def export(
    book_id: str,
    author_id: str,
    profile_key: str,
    *,
    genre: str = "anxiety",
    title: str | None = None,
    subtitle: str = "",
    author: str | None = None,
    publisher: str | None = None,
    illustration_path: Path | None = None,
    master_path: Path | None = None,
    out_dir: Path | None = None,
    profiles_path: Path | None = None,
) -> dict[str, Any]:
    """Produce the per-platform cover asset for ``profile_key``.

    Renders (or loads) the L4 portrait master, reflows it to the profile's
    aspect (cover-fit, no letterbox, no stretch), re-composites text at the
    new geometry, re-runs WCAG-AA, and exports PNG + JPEG (and the high-DPI
    master for Kobo). Deterministic: same (author, book, profile) -> identical
    bytes.

    Parameters mirror the L4 design; ``title``/``author`` default to
    human-readable forms of the ids when not supplied.
    """
    profile = get_profile(profile_key, profiles_path)
    title = title or book_id.replace("_", " ").title()
    author = author or author_id.replace("_", " ").title()

    out_dir = Path(out_dir) if out_dir else (DEFAULT_OUT_ROOT / author_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. L4 portrait master (native 1600x2560, 5:8). NO FLUX re-prompt: the
    #    imagery path is either a pre-rendered illustration or the render
    #    module's own type-dominant/abstract background.
    master_png = out_dir / f"{book_id}_portrait_master.png"
    if master_path and Path(master_path).exists():
        master_img = Image.open(master_path).convert("RGB")
    else:
        rkc.render_kdp_cover(
            illustration_path=illustration_path,
            title=title,
            author=author,
            subtitle=subtitle,
            genre=genre,
            output_path=master_png,
            publisher=publisher,
            book_id=book_id,
        )
        master_img = Image.open(master_png).convert("RGB")

    # 2. Resolve the profile's target sizes.
    rec = profile["size_recommended"]
    target_w, target_h = int(rec["width"]), int(rec["height"])
    hi_master = profile.get("size_high_dpi_master")

    if not aspect_matches(profile, target_w, target_h):
        raise ValueError(
            f"{profile_key}: size_recommended {target_w}x{target_h} does not "
            f"match declared aspect {profile.get('aspect_ratio')}"
        )

    surface = profile.get("surface", "ebook")
    plat = profile_key  # used in filenames

    outputs: dict[str, Any] = {}

    # 3. Reflow master -> recommended target aspect (cover-fit) + re-composite.
    reflowed = _cover_fit(master_img, target_w, target_h)
    wcag = _recomposite_text_and_check_wcag(
        reflowed,
        genre=genre,
        title=title,
        subtitle=subtitle,
        author=author,
        publisher=publisher,
    )

    # No-letterbox contract enforcement.
    if not profile.get("letterbox_allowed", False):
        if _has_letterbox_bars(reflowed):
            raise ValueError(
                f"{profile_key} forbids letterbox but reflowed asset has "
                f"uniform edge bars"
            )

    rec_png = out_dir / f"{book_id}_{plat}_{target_w}x{target_h}.png"
    reflowed.convert("RGB").save(rec_png, format="PNG", optimize=True)
    outputs["png_recommended"] = str(rec_png)

    fmts = [f.lower() for f in profile.get("formats", [])]
    if any(f in ("jpg", "jpeg") for f in fmts):
        rec_jpg = out_dir / f"{book_id}_{plat}_{target_w}x{target_h}.jpg"
        outputs["jpeg_recommended"] = _export_jpeg(
            reflowed, rec_jpg, float(profile["max_file_mb"])
        )

    # 4. High-DPI master (Kobo 2500x3500, 5:7) if the profile declares one.
    if hi_master:
        hw, hh = int(hi_master["width"]), int(hi_master["height"])
        hi_reflowed = _cover_fit(master_img, hw, hh)
        _recomposite_text_and_check_wcag(
            hi_reflowed,
            genre=genre, title=title, subtitle=subtitle,
            author=author, publisher=publisher,
        )
        hi_png = out_dir / f"{book_id}_{plat}_{hw}x{hh}.png"
        hi_reflowed.convert("RGB").save(hi_png, format="PNG", optimize=True)
        outputs["png_high_dpi_master"] = str(hi_png)

    # 5. Determinism seed + pHash (carried at L4 design, guard scoped by book).
    seed = _l4_seed(author_id, book_id)
    phash = average_hash(reflowed)

    return {
        "book_id": book_id,
        "author_id": author_id,
        "profile_key": profile_key,
        "platform": profile.get("platform"),
        "surface": surface,
        "aspect_decimal": (profile.get("aspect_ratio") or {}).get("decimal"),
        "recommended_size": [target_w, target_h],
        "high_dpi_master_size": (
            [int(hi_master["width"]), int(hi_master["height"])] if hi_master else None
        ),
        "master_png": str(master_png),
        "outputs": outputs,
        "wcag": wcag,
        "l4_seed": seed,
        "phash": phash,
        "reflow_strategy": "cover_fit_scale_to_fill_center_crop",
        "letterbox_allowed": bool(profile.get("letterbox_allowed", False)),
    }


# ─── CLI ─────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="L5 platform cover exporter (Kobo 3:4 first). "
        "Reflows the L4 portrait master to a platform profile; no FLUX re-run.",
    )
    p.add_argument("--book-id", required=True)
    p.add_argument("--author-id", required=True)
    p.add_argument("--profile", required=True, help="platform_cover_profiles.yaml key")
    p.add_argument("--genre", default="anxiety")
    p.add_argument("--title", default=None)
    p.add_argument("--subtitle", default="")
    p.add_argument("--author", default=None)
    p.add_argument("--publisher", default=None)
    p.add_argument("--illustration-path", default=None)
    p.add_argument("--master-path", default=None)
    p.add_argument("--out-dir", default=None)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = export(
        args.book_id,
        args.author_id,
        args.profile,
        genre=args.genre,
        title=args.title,
        subtitle=args.subtitle,
        author=args.author,
        publisher=args.publisher,
        illustration_path=Path(args.illustration_path) if args.illustration_path else None,
        master_path=Path(args.master_path) if args.master_path else None,
        out_dir=Path(args.out_dir) if args.out_dir else None,
    )
    import json

    print(json.dumps(result, indent=2))
    wcag = result.get("wcag", {})
    if wcag and not wcag.get("wcag_pass", True):
        print(
            f"WARNING: WCAG-AA {wcag.get('wcag_target')}:1 not met "
            f"(got {wcag.get('wcag_contrast_ratio')}:1)",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
