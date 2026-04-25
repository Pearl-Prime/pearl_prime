"""Vertical-strip composer for color webtoon delivery (Phase 2 #11 of PR #631).

The page-manga path uses ``page_compose.py`` (horizontal strips, KDP/Bookwalker).
The vertical-scroll webtoon path needs a different geometry:

- Stacks panel PNGs vertically (top → bottom)
- Uses **beat-type-aware gutter heights** between panels for therapeutic pacing
  (PR #631 master reference §11 / therapeutic-craft companion):
      micro          —   30–50 px   (within-scene continuation)
      spatial        —    200 px    (same scene, different angle)
      standard       —  600–1000 px (scene transition)
      long_drop      — 1500–3000 px (Phoenix's named therapeutic technique)
      miyazaki_ma    — 2400–3200 px (once-per-arc decompression beat)
- Downsamples to **800 px wide** (WEBTOON Canvas hard requirement)
- Renders master at 1600×2560/panel, downsamples for delivery (PR #631 Decision 2 —
  2× supersample so tablet/desktop renders look sharp at 1.5–2× zoom)
- Slices the resulting tall image into ``≤ max_segment_px`` tall JPEG segments
  **at gutter midpoints, never through panel content**
- Honors WEBTOON Canvas episode caps: ``≤ 100 images / ≤ 20 MB total``
  (PR #631 technical companion §2.2)

Public API
----------
``compose_episode_strips(chapter_script, panel_images_manifest, out_dir, ...)``
    → episode_payload dict with segment list + total_bytes + caps_check

``compute_gutter_px(beat_type, ...)``
    → int — public so tests + callers can introspect the table

Doesn't depend on Pearl Star or R2 — runs on any host. R2 push afterwards
goes through ``r2_push_helper.push_book_render`` from PR #637.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

# ── Spec constants (PR #631 §2.2 / Decision 2) ─────────────────────────────

DEFAULT_STRIP_WIDTH_PX = 800           # WEBTOON Canvas standard
DEFAULT_MAX_SEGMENT_PX = 1280          # WEBTOON Canvas auto-slice point
DEFAULT_JPEG_QUALITY = 92              # PR #631 §2.4 — quality 92 sRGB
WEBTOON_CANVAS_MAX_IMAGES = 100
WEBTOON_CANVAS_MAX_TOTAL_BYTES = 20 * 1024 * 1024
WEBTOON_CANVAS_MAX_PER_IMAGE_BYTES = 2 * 1024 * 1024  # per-image cap

# ── Beat-type gutter table (per PR #631 master reference §11) ──────────────

GUTTER_PX_BY_BEAT: dict[str, int] = {
    "micro":        40,       # within-scene continuation (range 30–50)
    "spatial":      200,      # same scene, different angle
    "standard":     800,      # scene transition (range 600–1000)
    "long_drop":    2200,     # Phoenix therapeutic technique (range 1500–3000)
    "miyazaki_ma":  2800,     # once-per-arc decompression (range 2400–3200)
}
DEFAULT_GUTTER_PX = 200       # fall back to "spatial" when beat_type unset


# ── Errors ─────────────────────────────────────────────────────────────────


class WebtoonComposeError(RuntimeError):
    pass


# ── Helpers ────────────────────────────────────────────────────────────────


def compute_gutter_px(beat_type: str | None, *, default: int = DEFAULT_GUTTER_PX) -> int:
    """Return gutter pixel height for the given beat_type.

    Beat types map to the PR #631 §11 table; unknown / None falls back to
    ``default`` (which itself defaults to ``DEFAULT_GUTTER_PX`` = 200, the
    "spatial" beat — safe middle-of-the-road choice).
    """
    if beat_type is None:
        return default
    return GUTTER_PX_BY_BEAT.get(beat_type, default)


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


def _resize_to_width(im: Any, target_w: int):
    from PIL import Image  # type: ignore

    if im.width == target_w:
        return im
    new_h = max(1, int(round(im.height * target_w / im.width)))
    return im.resize((target_w, new_h), Image.Resampling.LANCZOS)


def _slice_at_gutter_midpoints(
    total_height: int,
    panel_y_ranges: list[tuple[int, int]],
    max_segment_px: int,
) -> list[tuple[int, int]]:
    """Return list of (y_start, y_end) segment ranges that:

    - Each segment <= max_segment_px tall
    - All cuts land in gutters (between panel_y_ranges), never through a panel
    - Cover the full [0, total_height)

    panel_y_ranges is sorted, non-overlapping, in scroll order.
    """
    if total_height <= max_segment_px:
        return [(0, total_height)]

    # Compute gutter ranges — every gap between consecutive panels.
    gutters: list[tuple[int, int]] = []
    if panel_y_ranges:
        if panel_y_ranges[0][0] > 0:
            gutters.append((0, panel_y_ranges[0][0]))
        for a, b in zip(panel_y_ranges[:-1], panel_y_ranges[1:]):
            gutters.append((a[1], b[0]))
        if panel_y_ranges[-1][1] < total_height:
            gutters.append((panel_y_ranges[-1][1], total_height))
    else:
        gutters = [(0, total_height)]

    segments: list[tuple[int, int]] = []
    cursor = 0
    while cursor < total_height:
        target_end = cursor + max_segment_px
        if target_end >= total_height:
            segments.append((cursor, total_height))
            break

        # Find the latest gutter midpoint at or before target_end (preferred),
        # falling back to the earliest gutter midpoint after cursor if none.
        best_cut = None
        for g_start, g_end in gutters:
            if g_end <= cursor:
                continue
            if g_start >= total_height:
                break
            mid = (g_start + g_end) // 2
            if mid <= cursor:
                continue
            if mid <= target_end:
                best_cut = mid       # keep updating to the latest valid one
            elif best_cut is None:
                # No gutter fits within [cursor, target_end] — must overshoot
                # into the next gutter.
                best_cut = mid
                break
        if best_cut is None or best_cut <= cursor:
            # No gutters at all — emit a single segment of the full length.
            segments.append((cursor, total_height))
            break

        segments.append((cursor, best_cut))
        cursor = best_cut

    return segments


# ── Main compose function ─────────────────────────────────────────────────


def compose_episode_strips(
    chapter_script: Mapping[str, Any],
    panel_images_manifest: Mapping[str, Any],
    out_dir: Path,
    *,
    strip_width: int = DEFAULT_STRIP_WIDTH_PX,
    max_segment_px: int = DEFAULT_MAX_SEGMENT_PX,
    jpeg_quality: int = DEFAULT_JPEG_QUALITY,
    background_color: tuple[int, int, int] = (255, 255, 255),
    episode_id: str = "ep_001",
) -> dict[str, Any]:
    """Compose a single webtoon episode from per-panel images.

    Reads panel ordering from ``chapter_script.pages[].panels[]`` (each panel
    may carry a ``beat_type`` string for gutter sizing). Reads panel image
    paths from ``panel_images_manifest.panels[]``.

    Writes ``episode_id_seg_001.jpg``, ``..._seg_002.jpg``, … to ``out_dir``.

    Returns a payload dict:
        {
          "episode_id": str,
          "strip_width": int,
          "total_height": int,
          "segments": [
            {"path": str, "y_start": int, "y_end": int, "bytes": int}
          ],
          "total_bytes": int,
          "caps_check": {
            "max_images_ok": bool,
            "max_total_bytes_ok": bool,
            "max_per_image_bytes_ok": bool,
            "violations": [str],
          }
        }
    """
    try:
        from PIL import Image  # type: ignore
    except ImportError as e:
        raise WebtoonComposeError(
            "compose_episode_strips requires Pillow; pip install Pillow"
        ) from e

    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    by_id = _paths_by_panel_id(panel_images_manifest)
    if not by_id:
        raise WebtoonComposeError("panel_images_manifest has no panels with status=ok")

    # Walk pages in order; each page's panels[] is the panel sequence.
    # Webtoon convention: pages are scene boundaries (so a page break
    # implicitly inserts a "standard" gutter between the page's last panel
    # and the next page's first panel, unless explicitly overridden).
    panels_in_order: list[dict[str, Any]] = []
    pages = list(chapter_script.get("pages") or [])
    for page_idx, page in enumerate(pages):
        for panel_idx, panel in enumerate(page.get("panels") or []):
            pid = str(panel.get("panel_id") or "")
            if not pid:
                raise WebtoonComposeError(
                    f"chapter_script page {page_idx} panel {panel_idx} has no panel_id"
                )
            entry = dict(panel)
            entry.setdefault("panel_id", pid)
            # First panel of each page (after page 0) gets standard scene-transition gutter
            # unless beat_type is already set.
            if panel_idx == 0 and page_idx > 0 and "beat_type" not in entry:
                entry["beat_type"] = "standard"
            panels_in_order.append(entry)

    if not panels_in_order:
        raise WebtoonComposeError("chapter_script has no panels in any page")

    # Load + resize each panel image to strip_width.
    loaded_panels: list[Any] = []
    closers: list[Any] = []
    panel_y_ranges: list[tuple[int, int]] = []

    try:
        cursor_y = 0
        running_segments: list[tuple[int, Any, str]] = []  # (y_start, image, panel_id)

        for i, panel in enumerate(panels_in_order):
            pid = str(panel.get("panel_id"))
            src_path = by_id.get(pid)
            if src_path is None or not src_path.is_file():
                raise WebtoonComposeError(
                    f"panel {pid!r}: no rendered image (manifest status != ok or path missing)"
                )
            with Image.open(src_path) as src_im:
                im = src_im.convert("RGB").copy()
            im = _resize_to_width(im, strip_width)
            loaded_panels.append(im)
            closers.append(im)

            # Insert gutter BEFORE this panel except for the very first.
            if i > 0:
                gutter_h = compute_gutter_px(panel.get("beat_type"))
                cursor_y += gutter_h

            panel_y_ranges.append((cursor_y, cursor_y + im.height))
            running_segments.append((cursor_y, im, pid))
            cursor_y += im.height

        total_height = cursor_y

        # Build the full-height canvas.
        canvas = Image.new("RGB", (strip_width, total_height), background_color)
        closers.append(canvas)
        for y_start, im, _pid in running_segments:
            canvas.paste(im, (0, y_start))

        # Slice into segments.
        cuts = _slice_at_gutter_midpoints(total_height, panel_y_ranges, max_segment_px)

        segments: list[dict[str, Any]] = []
        total_bytes = 0
        for seg_idx, (y_start, y_end) in enumerate(cuts, start=1):
            seg_im = canvas.crop((0, y_start, strip_width, y_end))
            closers.append(seg_im)
            seg_path = out_dir / f"{episode_id}_seg_{seg_idx:03d}.jpg"
            seg_im.save(seg_path, format="JPEG", quality=jpeg_quality, optimize=True)
            seg_bytes = seg_path.stat().st_size
            segments.append({
                "path": str(seg_path),
                "y_start": y_start,
                "y_end": y_end,
                "bytes": seg_bytes,
            })
            total_bytes += seg_bytes

        # Caps check.
        violations: list[str] = []
        if len(segments) > WEBTOON_CANVAS_MAX_IMAGES:
            violations.append(
                f"image count {len(segments)} > Canvas max {WEBTOON_CANVAS_MAX_IMAGES}"
            )
        if total_bytes > WEBTOON_CANVAS_MAX_TOTAL_BYTES:
            violations.append(
                f"total bytes {total_bytes} > Canvas max {WEBTOON_CANVAS_MAX_TOTAL_BYTES}"
            )
        for s in segments:
            if s["bytes"] > WEBTOON_CANVAS_MAX_PER_IMAGE_BYTES:
                violations.append(
                    f"segment {s['path']} = {s['bytes']} bytes > per-image cap "
                    f"{WEBTOON_CANVAS_MAX_PER_IMAGE_BYTES}"
                )

        return {
            "episode_id": episode_id,
            "strip_width": strip_width,
            "total_height": total_height,
            "segments": segments,
            "total_bytes": total_bytes,
            "caps_check": {
                "max_images_ok": len(segments) <= WEBTOON_CANVAS_MAX_IMAGES,
                "max_total_bytes_ok": total_bytes <= WEBTOON_CANVAS_MAX_TOTAL_BYTES,
                "max_per_image_bytes_ok": all(
                    s["bytes"] <= WEBTOON_CANVAS_MAX_PER_IMAGE_BYTES for s in segments
                ),
                "violations": violations,
            },
        }
    finally:
        for im in closers:
            try:
                im.close()
            except Exception:
                pass
