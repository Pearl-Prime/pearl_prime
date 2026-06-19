"""Speech bubble renderer V2 — SVG-capable hulls, furigana, vertical CJK, manifests.

Keeps ``bubble_render`` (v1) on disk for backward compatibility. V2 adds:

- Vector bubble bodies via ``svg_bubble_library`` (rasterised with Cairo when
  available; Pillow fallback matches v1 raster quality).
- ``tail_geometry``: mouth targeting from fractional head boxes, anchors, or
  optional MediaPipe, then zone heuristic.
- ``furigana_renderer``: per-line ruby for ja-JP.
- Optional ``skip_text_overlay`` + ``emit_text_manifest`` for publish-time text
  rehydration (art + bubble chrome without baked dialogue).

Public API mirrors v1::

    render_bubbles_onto_panel_v2(...)
    render_bubbles_on_panels_v2(...)
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from phoenix_v4.manga.chapter import bubble_render as br
from phoenix_v4.manga.chapter.cjk_text_shaper import (
    is_cjk_locale,
    measure_vertical_cjk_block,
    render_text_to_pil,
    render_vertical_cjk_block,
    select_font_path_for_locale,
)
from phoenix_v4.manga.chapter.furigana_renderer import (
    normalize_furigana_segments,
    render_furigana_line,
)
from phoenix_v4.manga.chapter.svg_bubble_library import bubble_svg, svg_to_pil_rgba
from phoenix_v4.manga.chapter.tail_geometry import (
    detect_anime_face_boxes,
    resolve_mouth_pixel,
)

_FONT_CACHE_V2: dict[tuple[str, str, str, bool, int], Any] = {}

# ── Genre bubble-style register (config/manga/genre_bubble_styles.yaml) ──────
_GENRE_STYLE_MAP_CACHE: dict[str, Any] | None = None


def _load_genre_style_map() -> dict[str, Any]:
    """Read config/manga/genre_bubble_styles.yaml. Returns {} if missing.

    Cached after first read. The map provides per-genre bubble shape, font
    role, and tail defaults so each genre's dialogue has a distinct resting
    look (soft iyashikei vs punchy shonen) on top of the intensity layer.
    """
    global _GENRE_STYLE_MAP_CACHE
    if _GENRE_STYLE_MAP_CACHE is not None:
        return _GENRE_STYLE_MAP_CACHE
    repo_root = Path(__file__).resolve().parents[3]
    cfg_path = repo_root / "config" / "manga" / "genre_bubble_styles.yaml"
    data: dict[str, Any] = {}
    if cfg_path.exists():
        try:
            import yaml  # type: ignore

            data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        except Exception:
            data = {}
    _GENRE_STYLE_MAP_CACHE = data
    return data


def _resolve_genre_style(
    bubble_style_config: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    """Resolve the active genre's bubble-style dict from bubble_style_config.

    bubble_style_config may carry ``genre`` (a register/tradition name such as
    ``iyashikei`` / ``shonen`` / ``seinen`` / ``shoujo``, or a canonical genre
    id like ``healing``) and optionally a preloaded ``genre_styles`` map. When
    ``genre_styles`` is absent the map is loaded from disk. Returns the
    resolved style dict (after following ``alias_of``) or None when no genre is
    set / no match is found (renderer then keeps intensity defaults).
    """
    if not bubble_style_config:
        return None
    genre = bubble_style_config.get("genre")
    if not genre:
        return None
    genre = str(genre).strip().lower()

    style_map = bubble_style_config.get("genre_styles")
    if not isinstance(style_map, Mapping):
        style_map = _load_genre_style_map()
    genres = (style_map or {}).get("genres") or {}

    seen: set[str] = set()
    entry = genres.get(genre)
    # Follow alias_of chains (bounded) to the concrete register.
    while isinstance(entry, Mapping) and entry.get("alias_of") and genre not in seen:
        seen.add(genre)
        genre = str(entry["alias_of"]).strip().lower()
        entry = genres.get(genre)
    if isinstance(entry, Mapping):
        return dict(entry)
    # Fall back to the map's default register if defined.
    default = (style_map or {}).get("default")
    return dict(default) if isinstance(default, Mapping) else None


def _load_pil_font(path: Path, size: int) -> Any:
    from PIL import ImageFont

    return ImageFont.truetype(str(path), size=size)


def _get_font_v2(
    locale: str, intensity: str, bold: bool, *, font_role: str = "body"
) -> Any:
    """Return a REAL FreeTypeFont via FONT_REGISTRY for ALL locales.

    Resolves ``locale_coverage_required[locale].<font_role>`` (e.g. ``body``
    for clean dialogue, ``handwritten`` for the gentle iyashikei/shoujo face)
    through ``select_font_path_for_locale`` for every locale — not just CJK.
    This guarantees en_US dialogue uses the registered manga dialogue face
    (Comic Neue / Anime Ace) instead of whatever the directory glob happens to
    sort first, and never falls back to the load_default() bitmap when the
    registry has a present font. Only if the registry has no present font for
    the locale/role do we fall back to v1 discovery.
    """
    size = br._FONT_SIZES.get(intensity, 14)  # type: ignore[attr-defined]
    if bold:
        size = min(size + 2, 28)
    key = (locale, intensity, font_role, bold, size)
    if key in _FONT_CACHE_V2:
        return _FONT_CACHE_V2[key]

    font = None
    # Registry-first for ALL locales (CJK and Latin alike).
    p = select_font_path_for_locale(locale, role=font_role)
    if (p is None or not p.is_file()) and font_role != "body":
        # Requested role not present -> try the locale's body font.
        p = select_font_path_for_locale(locale, role="body")
    if p and p.is_file():
        try:
            font = _load_pil_font(p, size)
        except Exception:
            font = None
    if font is None:
        font = br._get_font(intensity, bold=bold)  # type: ignore[attr-defined]

    _FONT_CACHE_V2[key] = font
    return font


def _effective_bubble_style(line: Mapping[str, Any]) -> str:
    style = str(line.get("bubble_style") or "round_normal")
    dem = line.get("demonic_bubble")
    if isinstance(dem, Mapping) and dem.get("enabled") is True:
        return "wavy_supernatural"
    return style


def _line_used_intensity_default(line: Mapping[str, Any]) -> tuple[bool, bool]:
    """Whether this line's bubble_style / tail_style are the *intensity default*.

    Returns ``(style_is_default, tail_is_default)``. When True the genre
    register is allowed to override that field; when False the author set an
    explicit per-line value in the chapter_script and it is preserved.

    Compares against ``lettering_from_script``'s intensity->default maps so the
    detection stays in lockstep with how lettering_from_script derives the
    defaults.
    """
    try:
        from phoenix_v4.manga.chapter.lettering_from_script import (
            _INTENSITY_TO_BUBBLE,
            _INTENSITY_TO_TAIL,
        )
    except Exception:  # pragma: no cover - defensive
        return (True, True)
    intensity = str(line.get("intensity") or "normal").lower()
    cur_style = str(line.get("bubble_style") or "round_normal")
    cur_tail = str(line.get("tail_style") or "pointer")
    style_default = _INTENSITY_TO_BUBBLE.get(intensity, "round_normal")
    tail_default = _INTENSITY_TO_TAIL.get(intensity, "pointer")
    return (cur_style == style_default, cur_tail == tail_default)


def _apply_genre_to_line(
    line: Mapping[str, Any],
    base_bubble_style: str,
    base_tail_style: str,
    genre_style: Mapping[str, Any] | None,
) -> tuple[str, str, str]:
    """Fold the genre register into a line's bubble shape / tail / font role.

    Precedence (per config/manga/genre_bubble_styles.yaml):
      1. Explicit per-line author override -> preserved.
      2. Genre register default -> applied when the line used the intensity
         default AND a demonic/supernatural bubble is not forcing a shape.
      3. Intensity default -> unchanged.

    Returns ``(bubble_style, tail_style, font_role)``.
    """
    font_role = "body"
    if not genre_style:
        return base_bubble_style, base_tail_style, font_role

    g_style = genre_style.get("bubble_style")
    g_tail = genre_style.get("tail_style")
    g_font_role = genre_style.get("font_role")
    if isinstance(g_font_role, str) and g_font_role.strip():
        font_role = g_font_role.strip()

    # A supernatural/demonic bubble forces wavy_supernatural; never override it.
    dem = line.get("demonic_bubble")
    demonic = isinstance(dem, Mapping) and dem.get("enabled") is True

    style_is_default, tail_is_default = _line_used_intensity_default(line)

    bubble_style = base_bubble_style
    if (
        not demonic
        and style_is_default
        and isinstance(g_style, str)
        and g_style.strip()
    ):
        bubble_style = g_style.strip()

    tail_style = base_tail_style
    if tail_is_default and isinstance(g_tail, str) and g_tail.strip():
        tail_style = g_tail.strip()

    return bubble_style, tail_style, font_role


def _bubble_fill_for_style(style: str) -> tuple[int, int, int, int]:
    if style == "shojo_soft":
        return (255, 245, 250, 220)
    if style == "electronic_sharp":
        return (200, 230, 255, 210)
    if style == "scream_ultra":
        return (255, 240, 200, 230)
    if style == "square_narration":
        return (0, 0, 0, 180)
    return (255, 255, 255, 230)


def _as_rgba(val: Any) -> tuple[int, int, int, int] | None:
    """Coerce a 4-element list/tuple from the genre config into an RGBA tuple."""
    if isinstance(val, (list, tuple)) and len(val) == 4:
        try:
            r, g, b, a = (int(val[0]), int(val[1]), int(val[2]), int(val[3]))
        except (TypeError, ValueError):
            return None
        return (
            max(0, min(255, r)),
            max(0, min(255, g)),
            max(0, min(255, b)),
            max(0, min(255, a)),
        )
    return None


def _bubble_fill_with_genre(
    style: str, line: Mapping[str, Any]
) -> tuple[int, int, int, int]:
    """Bubble fill, honoring a genre ``_genre_fill_tint`` override when set."""
    override = _as_rgba(line.get("_genre_fill_tint"))
    if override is not None:
        return override
    return _bubble_fill_for_style(style)


def _stroke_for_style(style: str, line: Mapping[str, Any]) -> tuple[int, int, int, int]:
    override = _as_rgba(line.get("_genre_stroke_tint"))
    if override is not None:
        return override
    dem = line.get("demonic_bubble")
    if isinstance(dem, Mapping) and dem.get("enabled") is True:
        return (90, 0, 120, 255)
    if style == "scream_ultra":
        return (200, 0, 0, 255)
    if style == "electronic_sharp":
        return (0, 100, 200, 255)
    if style == "whisper_dashed":
        return (100, 100, 100, 200)
    if style == "cloud_thought":
        return (80, 80, 80, 255)
    return (0, 0, 0, 255)


def _draw_bubble_body(
    overlay: Any,
    draw: Any,
    bubble_bbox: tuple[int, int, int, int],
    style: str,
    line: Mapping[str, Any],
) -> None:
    x1, y1, x2, y2 = bubble_bbox
    w, h = max(8, x2 - x1), max(8, y2 - y1)
    fill = _bubble_fill_with_genre(style, line)
    stroke = _stroke_for_style(style, line)
    svg = bubble_svg(style, w, h, fill_rgba=fill, stroke_rgba=stroke)
    ras = svg_to_pil_rgba(svg, width=w, height=h)
    if ras is not None:
        overlay.paste(ras, (x1, y1), ras)
        return

    drawer = br._BUBBLE_DRAWERS.get(style, br._draw_round_bubble)  # type: ignore[attr-defined]
    if style == "shojo_soft":
        # Soft pillowy rounded-rect — the gentle healing/iyashikei/shoujo look.
        # Drawn directly here (not the ellipse drawer) so the soft shape renders
        # even when cairosvg is absent and the SVG raster path is unavailable.
        x1, y1, x2, y2 = bubble_bbox
        radius = max(int(min(x2 - x1, y2 - y1) * 0.46), 8)
        soft_stroke = (stroke[0], stroke[1], stroke[2], stroke[3])
        try:
            draw.rounded_rectangle(
                [x1, y1, x2, y2], radius=radius,
                fill=fill, outline=soft_stroke, width=2,
            )
        except (AttributeError, TypeError):  # very old Pillow — fall back to oval
            drawer(draw, bubble_bbox, fill=fill)
    elif style == "electronic_sharp":
        drawer(draw, bubble_bbox, fill=fill, outline=(stroke[0], stroke[1], stroke[2], stroke[3]))
    elif style == "whisper_dashed":
        drawer(draw, bubble_bbox)
    elif style == "scream_ultra":
        drawer(draw, bubble_bbox)
    else:
        drawer(draw, bubble_bbox, fill=fill, outline=(stroke[0], stroke[1], stroke[2], stroke[3]))


def _write_text_manifest(
    path: Path,
    *,
    panel_stem: str,
    locale: str,
    entries: list[dict[str, Any]],
    sfx: Sequence[str],
    narrator_caption: str | None,
) -> None:
    doc = {
        "schema_version": "1.0.0",
        "kind": "lettering_text_manifest",
        "panel_stem": panel_stem,
        "locale": locale,
        "rehydration_pattern": "text_rehydrated_at_publish_time",
        "entries": entries,
        "sfx": list(sfx),
        "narrator_caption": narrator_caption,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _layout_text_measure(
    draw: Any,
    text: str,
    *,
    locale: str,
    vertical_kanji: bool,
    font: Any,
    max_text_w: int,
    furigana: list[dict[str, str]],
) -> tuple[str, list[str], tuple[int, int]]:
    """Return layout mode, horizontal wrapped lines (empty if not used), and size."""
    if vertical_kanji and is_cjk_locale(locale):
        max_h = max(40, int(max_text_w * 1.8))
        tw, th = measure_vertical_cjk_block(
            draw, text, font=font, locale=locale, max_column_height=max_h
        )
        return "vert", [], (tw, th)

    if furigana and locale == "ja_JP":
        tw, th = _measure_wrapped_furigana(draw, text, furigana, font, max_text_w)
        return "furi", [], (tw, th)

    wrapped = list(
        br._wrap_text(text, font, draw, max(40, max_text_w))  # type: ignore[attr-defined]
    )
    tw, th = br._measure_wrapped(wrapped, font, draw)  # type: ignore[attr-defined]
    return "horiz", wrapped, (tw, th)


def _measure_wrapped_furigana(
    draw: Any,
    text: str,
    segments: list[dict[str, str]],
    font: Any,
    max_width: int,
) -> tuple[int, int]:
    import copy as _copy

    lines = text.split("\n") if "\n" in text else textwrap_split(draw, text, font, max_width)
    ruby_font = shrink_font(font, max(8, int(getattr(font, "size", 14)) - 4))
    queue: list[dict[str, str]] = _copy.deepcopy(segments)
    total_h = 0
    max_w = 0
    for ln in lines:
        lw, lh = render_furigana_line(
            draw,
            ln,
            segments,
            0,
            0,
            base_font=font,
            ruby_font=ruby_font,
            dry_run=True,
            segment_queue=queue,
        )
        max_w = max(max_w, lw)
        total_h += lh + 2
    return max(max_w, 1), total_h


def textwrap_split(draw: Any, text: str, font: Any, max_width: int) -> list[str]:
    """Word-ish wrap fallback when text has no explicit newlines."""
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    cur: list[str] = []
    for w in words:
        trial = (" ".join(cur + [w])).strip()
        tw = _line_width_approx(draw, trial, font)
        if cur and tw > max_width:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines if lines else [text]


def _line_width_approx(draw: Any, line: str, font: Any) -> int:
    try:
        bbox = draw.textbbox((0, 0), line, font=font)
        return bbox[2] - bbox[0]
    except AttributeError:
        return int(draw.textsize(line, font=font)[0])  # type: ignore[attr-defined]


def shrink_font(base_font: Any, size: int) -> Any:
    path = getattr(base_font, "path", None)
    from PIL import ImageFont

    if path:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            pass
    return base_font


def _compute_bbox_from_wh(
    zone_bbox: tuple[int, int, int, int],
    tw: int,
    th: int,
    pw: int,
    ph: int,
) -> tuple[int, int, int, int]:
    zx1, zy1, zx2, zy2 = zone_bbox
    bw = max(60, tw + br._H_PAD * 2)  # type: ignore[attr-defined]
    bh = max(30, th + br._V_PAD * 2)  # type: ignore[attr-defined]
    cx = (zx1 + zx2) // 2
    cy = (zy1 + zy2) // 2
    x1 = max(zx1, cx - bw // 2)
    y1 = max(zy1, cy - bh // 2)
    x2 = min(zx2, x1 + bw)
    y2 = min(zy2, y1 + bh)
    if x2 - x1 < bw:
        x1 = max(0, x2 - bw)
    if y2 - y1 < bh:
        y1 = max(0, y2 - bh)
    x2 = min(pw, x1 + bw)
    y2 = min(ph, y1 + bh)
    return (x1, y1, x2, y2)


def render_bubbles_onto_panel_v2(
    panel_image_path: Path,
    dialogue_lines: list[dict[str, Any]],
    sfx: list[str],
    narrator_caption: str | None,
    *,
    bubble_style_config: dict[str, Any] | None = None,
    out_path: Path | None = None,
    coverage_limit: float = 0.30,
    locale: str = "en_US",
    default_locale: str = "en_US",
    lettering_panel: Mapping[str, Any] | None = None,
    emit_text_manifest: bool = True,
    skip_text_overlay: bool = False,
    manifest_out_path: Path | None = None,
) -> dict[str, Any]:
    from PIL import Image, ImageDraw

    panel_image_path = Path(panel_image_path)
    lettering_panel = lettering_panel or {}
    if out_path is None:
        out_path = panel_image_path.with_name(
            panel_image_path.stem + "_bubbled_v2" + panel_image_path.suffix
        )
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    manifest_out_path = (
        manifest_out_path
        if manifest_out_path is not None
        else out_path.with_name(
            f"{out_path.stem}_lettering_{locale.replace('-', '_')}.json"
        )
    )

    from phoenix_v4.manga.chapter.locale_resolver import (  # type: ignore
        resolve_dialogue_text,
        resolve_font_override,
    )

    with Image.open(panel_image_path) as base_img:
        img = base_img.convert("RGBA")

    pw, ph = img.size
    # Detect faces ONCE per panel (not per dialogue line) so tails anchor at the
    # speaker's actual face. No-op (→ zone fallback) when cv2/cascade absent.
    detected_faces = detect_anime_face_boxes(img)
    overlay = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    placed_bubbles: list[tuple[int, int, int, int]] = []
    layout_records: list[dict[str, Any]] = []
    manifest_entries: list[dict[str, Any]] = []

    # Resolve the genre register once for this panel (soft iyashikei vs punchy
    # shonen). None when no genre is set -> intensity defaults are used.
    genre_style = _resolve_genre_style(bubble_style_config)
    caption_font_role = "body"
    if genre_style and isinstance(genre_style.get("font_role"), str):
        # Captions follow the genre's lettering face (gentle for healing).
        caption_font_role = str(genre_style["font_role"]).strip() or "body"

    zone_seq = br._default_zone_sequence()  # type: ignore[attr-defined]
    zone_idx = 0

    if narrator_caption:
        cap_font = _get_font_v2(locale, "calm", False, font_role=caption_font_role)
        cap_lines = br._wrap_text(narrator_caption, cap_font, draw, int(pw * 0.9))  # type: ignore[attr-defined]
        _, line_h = br._text_bbox(cap_lines[0] if cap_lines else "M", cap_font, draw)  # type: ignore[attr-defined]
        cap_h = (len(cap_lines) * (line_h + 2)) + br._V_PAD * 2  # type: ignore[attr-defined]
        cap_bbox: tuple[int, int, int, int] = (0, 0, pw, min(ph, cap_h + 4))
        br._draw_caption_box(draw, cap_bbox)  # type: ignore[attr-defined]
        if not skip_text_overlay:
            br._render_text_in_bubble(  # type: ignore[attr-defined]
                draw, cap_bbox, cap_lines, cap_font, narrator=True
            )
        placed_bubbles.append(cap_bbox)
        layout_records.append({"type": "caption", "bbox": cap_bbox, "text": narrator_caption})
        manifest_entries.append({
            "kind": "narrator_caption",
            "text": narrator_caption,
            "bbox": list(cap_bbox),
        })

    for line in dialogue_lines:
        raw_text = resolve_dialogue_text(line, locale=locale, default_locale=default_locale)
        text_stripped = (raw_text or "").strip()
        if not text_stripped:
            continue

        intensity: str = str(line.get("intensity") or "normal")
        bubble_style: str = _effective_bubble_style(line)
        position_hint: str = str(line.get("position_hint") or zone_seq[zone_idx % len(zone_seq)])
        tail_style: str = str(line.get("tail_style") or "pointer")
        vertical_kanji = bool(line.get("vertical_kanji"))

        # Fold the genre register in: distinct resting bubble shape + lettering
        # face + tail per genre (e.g. iyashikei -> soft shojo_soft + handwritten
        # + soft tail; shonen -> crisp round_normal + body + pointer). Explicit
        # per-line author overrides and intensity-driven emphasis are preserved.
        bubble_style, tail_style, font_role = _apply_genre_to_line(
            line, bubble_style, tail_style, genre_style
        )
        # Carry genre fill/stroke tints onto a line copy for the bubble body so
        # iyashikei's warm off-white reads distinct from shonen's crisp white.
        line_for_body: dict[str, Any] = dict(line)
        if genre_style:
            if genre_style.get("fill_tint") is not None:
                line_for_body["_genre_fill_tint"] = genre_style["fill_tint"]
            if genre_style.get("stroke_tint") is not None:
                line_for_body["_genre_stroke_tint"] = genre_style["stroke_tint"]

        furigana_segments = normalize_furigana_segments(line)
        if furigana_segments and locale != "ja_JP":
            furigana_segments = []

        bold = intensity in ("excited", "shouting", "screaming") or resolve_font_override(
            line, locale=locale, default_locale=default_locale
        ) == "bold_action"
        italic = intensity == "internal"
        font = _get_font_v2(locale, intensity, bold=bold, font_role=font_role)
        _ = italic  # italic emphasis — future OT feature

        layout_mode = "horiz"
        wrapped_horiz: list[str] = []
        for attempt in range(4):
            zone_bbox = br._zone_to_pixels(position_hint, pw, ph)  # type: ignore[attr-defined]
            max_text_w = (zone_bbox[2] - zone_bbox[0]) - br._H_PAD * 2  # type: ignore[attr-defined]
            layout_mode, wrapped_horiz, (tw, th) = _layout_text_measure(
                draw,
                text_stripped,
                locale=locale,
                vertical_kanji=vertical_kanji,
                font=font,
                max_text_w=max_text_w,
                furigana=furigana_segments,
            )
            bubble_bbox = _compute_bbox_from_wh(zone_bbox, tw, th, pw, ph)
            test_bubbles = placed_bubbles + [bubble_bbox]
            if br._coverage_ratio(test_bubbles, pw, ph) <= coverage_limit:  # type: ignore[attr-defined]
                break
            tiers = ["screaming", "shouting", "excited", "normal", "calm", "whisper"]
            cur = tiers.index(intensity) if intensity in tiers else 3
            intensity = tiers[min(cur + 1, len(tiers) - 1)]
            font = _get_font_v2(locale, intensity, bold=False, font_role=font_role)
        else:
            layout_records.append({
                "type": "skipped",
                "reason": "coverage_limit",
                "text": text_stripped[:40],
            })
            continue

        _draw_bubble_body(overlay, draw, bubble_bbox, bubble_style, line_for_body)

        # "pointer" = sharp mouth-targeted tail; "soft" = gentle iyashikei/shoujo
        # tail (same mouth targeting, genre fill). "none" draws no tail.
        if tail_style in ("pointer", "soft"):
            mouth = resolve_mouth_pixel(
                panel_w=pw,
                panel_h=ph,
                line=line,
                panel_lettering=lettering_panel,
                panel_rgba=img,
                detected_faces=detected_faces,
            )
            bubble_fill = _bubble_fill_with_genre(bubble_style, line_for_body)
            br._draw_tail_pointer(  # type: ignore[attr-defined]
                draw, bubble_bbox, mouth, fill=bubble_fill
            )

        if not skip_text_overlay:
            text_fill: tuple[int, int, int, int] = (
                (255, 255, 255, 255) if bubble_style == "square_narration" else (0, 0, 0, 255)
            )
            x1, y1, x2, y2 = bubble_bbox
            inner_w = (x2 - x1) - br._H_PAD * 2  # type: ignore[attr-defined]

            if layout_mode == "vert":
                col_h = max(40, int(inner_w * 1.85))
                right_x = x2 - br._H_PAD  # type: ignore[attr-defined]
                top_y = y1 + br._V_PAD + ( (y2 - y1 - col_h) // 2 if col_h < (y2 - y1) else 0 )  # type: ignore[attr-defined]
                render_vertical_cjk_block(
                    draw,
                    text_stripped,
                    right_x,
                    top_y,
                    font=font,
                    locale=locale,
                    fill=text_fill,
                    max_column_height=col_h,
                )
            elif layout_mode == "furi" and furigana_segments:
                import copy as _copy

                ruby_sz = max(8, int(getattr(font, "size", 14)) - 4)
                ruby_font = shrink_font(font, ruby_sz)
                lines_tp = (
                    text_stripped.split("\n")
                    if "\n" in text_stripped
                    else textwrap_split(draw, text_stripped, font, inner_w)
                )
                measure_q = _copy.deepcopy(furigana_segments)
                total_block = 0
                for ln in lines_tp:
                    _, lh = render_furigana_line(
                        draw,
                        ln,
                        furigana_segments,
                        0,
                        0,
                        base_font=font,
                        ruby_font=ruby_font,
                        dry_run=True,
                        segment_queue=measure_q,
                    )
                    total_block += lh + 2
                start_y = y1 + max(br._V_PAD, (y2 - y1 - total_block) // 2)  # type: ignore[attr-defined]
                draw_q = _copy.deepcopy(furigana_segments)
                cur_y = start_y
                for ln in lines_tp:
                    _, lh = render_furigana_line(
                        draw,
                        ln,
                        furigana_segments,
                        x1 + br._H_PAD,  # type: ignore[attr-defined]
                        cur_y,
                        base_font=font,
                        ruby_font=ruby_font,
                        text_fill=text_fill,
                        segment_queue=draw_q,
                    )
                    cur_y += lh + 2
            else:
                br._render_text_in_bubble(  # type: ignore[attr-defined]
                    draw,
                    bubble_bbox,
                    wrapped_horiz,
                    font,
                    text_fill=text_fill,
                )

        manifest_entries.append({
            "kind": "dialogue",
            "speaker": line.get("speaker"),
            "text": text_stripped,
            "text_by_locale": line.get("text_by_locale"),
            "bubble_style": bubble_style,
            "furigana": furigana_segments,
            "vertical_kanji": vertical_kanji,
            "bbox": list(bubble_bbox),
            "demonic_bubble": line.get("demonic_bubble"),
        })

        placed_bubbles.append(bubble_bbox)
        layout_records.append({
            "type": "dialogue",
            "speaker": line.get("speaker"),
            "text": text_stripped,
            "bubble_style": bubble_style,
            "tail_style": tail_style,
            "font_role": font_role,
            "intensity": intensity,
            "position_hint": position_hint,
            "bbox": bubble_bbox,
            "furigana": furigana_segments,
            "vertical_kanji": vertical_kanji,
        })

        zone_idx += 1

    # SFX uses the punchy display face (Bangers en_US) when the registry has it.
    sfx_font_role = "display"
    for sfx_text in sfx:
        if not sfx_text:
            continue
        sfx_font = _get_font_v2(locale, "screaming", bold=True, font_role=sfx_font_role)
        sfx_idx = sfx.index(sfx_text)
        sfx_x = int(pw * (0.30 + sfx_idx * 0.15) % pw)
        sfx_y = int(ph * 0.40)
        outline_col = (0, 0, 0, 200)
        sfx_fill = (220, 40, 40, 255)
        if not skip_text_overlay:
            for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, -2), (0, 2)]:
                render_text_to_pil(
                    draw, sfx_text, sfx_x + ox, sfx_y + oy,
                    font=sfx_font, locale=locale, fill=outline_col,
                )
            render_text_to_pil(draw, sfx_text, sfx_x, sfx_y, font=sfx_font, locale=locale, fill=sfx_fill)
        layout_records.append({"type": "sfx", "text": sfx_text, "position": (sfx_x, sfx_y)})
        manifest_entries.append({"kind": "sfx", "text": sfx_text, "position": [sfx_x, sfx_y]})

    composite = Image.alpha_composite(img, overlay)
    composite.save(str(out_path), format="PNG")

    if emit_text_manifest:
        _write_text_manifest(
            manifest_out_path,
            panel_stem=panel_image_path.stem,
            locale=locale,
            entries=manifest_entries,
            sfx=sfx,
            narrator_caption=narrator_caption,
        )

    final_cov = br._coverage_ratio(placed_bubbles, pw, ph)  # type: ignore[attr-defined]
    return {
        "panel_stem": panel_image_path.stem,
        "out_path": str(out_path),
        "bubble_render_version": 2,
        "genre": (bubble_style_config or {}).get("genre"),
        "text_manifest_path": str(manifest_out_path) if emit_text_manifest else None,
        "bubbles": layout_records,
        "coverage_ratio": round(final_cov, 4),
        "panel_size": (pw, ph),
        "skipped_text_overlay": skip_text_overlay,
    }


def render_bubbles_on_panels_v2(
    chapter_script: Mapping[str, Any],
    lettering_spec: Mapping[str, Any],
    panel_images_manifest: Mapping[str, Any],
    bubble_style_config: Mapping[str, Any] | None,
    out_dir: Path,
    *,
    locale: str | None = None,
    emit_text_manifest: bool = True,
    skip_text_overlay: bool = False,
) -> dict[str, Any]:
    from phoenix_v4.manga.chapter.locale_resolver import (  # type: ignore
        resolve_narrator_caption,
        resolve_sfx,
    )

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    default_locale = str(lettering_spec.get("default_locale") or "en_US")
    active_locale = str(locale or default_locale)

    lettering_by_pid: dict[str, dict[str, Any]] = {}
    for row in lettering_spec.get("lettering_panels") or []:
        pid = str(row.get("panel_id") or "")
        if pid:
            lettering_by_pid[pid] = row

    updated_manifest = copy.deepcopy(dict(panel_images_manifest))
    layouts: list[dict[str, Any]] = []

    for panel_entry in updated_manifest.get("panels") or []:
        if str(panel_entry.get("status")) != "ok":
            continue
        pid = str(panel_entry.get("panel_id") or "")
        letter = lettering_by_pid.get(pid, {})
        if letter.get("silence_confirmed", True):
            continue
        src_path = panel_entry.get("path")
        if not src_path or not Path(src_path).is_file():
            continue

        dialogue_lines: list[dict[str, Any]] = list(letter.get("dialogue_lines") or [])
        sfx_list: list[str] = list(resolve_sfx(letter, locale=active_locale, default_locale=default_locale))
        narr = resolve_narrator_caption(letter, locale=active_locale, default_locale=default_locale)

        if not dialogue_lines and not sfx_list and not narr:
            continue

        bubbled_path = out_dir / (Path(src_path).stem + "_bubbled_v2.png")
        manifest_path = bubbled_path.with_name(
            f"{bubbled_path.stem}_lettering_{active_locale.replace('-', '_')}.json"
        )
        lay = render_bubbles_onto_panel_v2(
            Path(src_path),
            dialogue_lines,
            sfx_list,
            narr,
            bubble_style_config=dict(bubble_style_config or {}),
            out_path=bubbled_path,
            locale=active_locale,
            default_locale=default_locale,
            lettering_panel=letter,
            emit_text_manifest=emit_text_manifest,
            skip_text_overlay=skip_text_overlay,
            manifest_out_path=manifest_path,
        )
        panel_entry["path"] = str(bubbled_path)
        panel_entry["bubble_render_v2"] = {
            "applied": True,
            "coverage_ratio": lay["coverage_ratio"],
            "bubble_count": sum(1 for r in lay["bubbles"] if r.get("type") == "dialogue"),
            "text_manifest_path": lay.get("text_manifest_path"),
            "skipped_text_overlay": lay.get("skipped_text_overlay"),
        }
        layouts.append(lay)

    updated_manifest["bubble_render_v2_summary"] = {
        "panels_processed": len(layouts),
        "out_dir": str(out_dir),
    }
    return updated_manifest
