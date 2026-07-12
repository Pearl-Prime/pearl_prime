"""JLREQ-aware dialogue and SFX planning helpers.

This module keeps the current renderer honest:

- vertical Japanese/CJK planning is supported for simple columnar lettering,
- vertical+furigana is still partial and explicitly labeled as such,
- SFX placement is planned against occupied bubble regions instead of using a
  fixed x/y heuristic.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from phoenix_v4.manga.chapter.cjk_text_shaper import (
    _glyph_height,
    is_cjk_locale,
    measure_vertical_cjk_block,
    render_text_to_pil,
)
from phoenix_v4.manga.chapter.spread_layout_solver import normalize_reading_direction

_ROTATE_GLYPHS = frozenset({
    "ー",
    "…",
    "―",
    "–",
    "—",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    "<",
    ">",
    "《",
    "》",
    "〈",
    "〉",
    "（",
    "）",
    "【",
    "】",
    "［",
    "］",
})


def _is_ascii_latin(ch: str) -> bool:
    return ("A" <= ch <= "Z") or ("a" <= ch <= "z") or ("0" <= ch <= "9")


def _glyph_orientation(ch: str) -> str:
    if _is_ascii_latin(ch) or ch in _ROTATE_GLYPHS:
        return "rotate90"
    return "upright"


def plan_dialogue_lettering(
    text: str,
    *,
    locale: str,
    vertical_kanji: bool = False,
    furigana: Sequence[Mapping[str, Any]] | None = None,
    explicit_writing_mode: str | None = None,
) -> dict[str, Any]:
    """Return a machine-checkable JLREQ plan for one dialogue line."""
    furigana = list(furigana or [])
    writing_mode = "horizontal_tb"
    runtime_status = "ready"
    note = "horizontal lettering"

    if explicit_writing_mode:
        mode = str(explicit_writing_mode).strip().lower()
        if mode in {"vertical_rl", "vertical", "tategaki"}:
            writing_mode = "vertical_rl"
        elif mode in {"horizontal_tb", "horizontal", "yokogaki"}:
            writing_mode = "horizontal_tb"
    elif vertical_kanji and is_cjk_locale(locale):
        writing_mode = "vertical_rl"

    if writing_mode == "vertical_rl":
        note = "vertical columns planned under JLREQ-style flow"
        if furigana:
            # We deliberately keep this partial until the runtime can place ruby
            # along a vertical base string without resorting to unsafe heuristics.
            writing_mode = "horizontal_tb"
            runtime_status = "partial_vertical_furigana_deferred"
            note = "vertical+furigana requested; current runtime falls back to horizontal ruby"

    glyph_plan = [
        {"char": ch, "orientation": _glyph_orientation(ch)}
        for ch in text
        if ch and ch != "\n"
    ]
    return {
        "schema_version": "1.0.0",
        "locale": locale,
        "writing_mode": writing_mode,
        "runtime_status": runtime_status,
        "column_gap_px": 6 if writing_mode == "vertical_rl" else 0,
        "line_gap_px": 2,
        "glyph_plan": glyph_plan,
        "furigana_count": len(furigana),
        "note": note,
    }


def _measure_glyph(draw: Any, ch: str, font: Any, orientation: str) -> tuple[int, int]:
    try:
        bbox = draw.textbbox((0, 0), ch, font=font)
        width = max(1, int(bbox[2] - bbox[0]))
    except AttributeError:
        width = max(1, int(draw.textsize(ch, font=font)[0]))  # type: ignore[attr-defined]
    height = max(1, int(_glyph_height(draw, ch, font)))
    if orientation == "rotate90":
        return height, width
    return width, height


def _build_vertical_columns(
    draw: Any,
    text: str,
    *,
    font: Any,
    max_column_height: int,
    plan: Mapping[str, Any],
) -> list[list[dict[str, Any]]]:
    glyph_plan = list(plan.get("glyph_plan") or [])
    orientation_by_index = {
        idx: str(row.get("orientation") or "upright")
        for idx, row in enumerate(glyph_plan)
    }
    columns: list[list[dict[str, Any]]] = []
    col: list[dict[str, Any]] = []
    col_h = 0
    glyph_index = 0
    line_gap = int(plan.get("line_gap_px", 2) or 2)

    for ch in text.strip():
        if ch == "\n":
            if col:
                columns.append(col)
                col = []
                col_h = 0
            continue
        orientation = orientation_by_index.get(glyph_index, _glyph_orientation(ch))
        glyph_index += 1
        glyph_w, glyph_h = _measure_glyph(draw, ch, font, orientation)
        advance = glyph_h + line_gap
        if col and col_h + advance > max_column_height:
            columns.append(col)
            col = []
            col_h = 0
        col.append(
            {
                "char": ch,
                "orientation": orientation,
                "width": glyph_w,
                "height": glyph_h,
            }
        )
        col_h += advance

    if col:
        columns.append(col)
    return columns


def measure_jlreq_text_block(
    draw: Any,
    text: str,
    *,
    font: Any,
    locale: str,
    max_column_height: int,
    plan: Mapping[str, Any],
) -> tuple[int, int]:
    """Measure dialogue according to its JLREQ plan."""
    if str(plan.get("writing_mode") or "horizontal_tb") != "vertical_rl":
        if not text:
            return (0, 0)
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            return (max(1, int(bbox[2] - bbox[0])), max(1, int(bbox[3] - bbox[1])))
        except AttributeError:
            return tuple(int(v) for v in draw.textsize(text, font=font))  # type: ignore[attr-defined]

    if not any(row.get("orientation") == "rotate90" for row in plan.get("glyph_plan") or []):
        return measure_vertical_cjk_block(
            draw,
            text,
            font=font,
            locale=locale,
            max_column_height=max_column_height,
            column_gap=int(plan.get("column_gap_px", 6) or 6),
        )

    columns = _build_vertical_columns(
        draw,
        text,
        font=font,
        max_column_height=max_column_height,
        plan=plan,
    )
    total_w = 0
    tallest = 0
    column_gap = int(plan.get("column_gap_px", 6) or 6)
    line_gap = int(plan.get("line_gap_px", 2) or 2)
    for column in columns:
        column_w = max((int(row["width"]) for row in column), default=1)
        column_h = sum(int(row["height"]) + line_gap for row in column)
        total_w += column_w + column_gap
        tallest = max(tallest, column_h)
    total_w = max(0, total_w - column_gap)
    return total_w, tallest


def _draw_rotated_glyph(
    image: Any,
    ch: str,
    *,
    x: int,
    y: int,
    font: Any,
    locale: str,
    fill: tuple[int, int, int, int],
) -> None:
    from PIL import Image, ImageDraw

    # Draw upright, rotate, then paste. This keeps the same font fallback path
    # as the base renderer without requiring a separate glyph rasterizer.
    probe = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    probe_draw = ImageDraw.Draw(probe)
    try:
        bbox = probe_draw.textbbox((0, 0), ch, font=font)
        width = max(1, int(bbox[2] - bbox[0])) + 8
        height = max(1, int(bbox[3] - bbox[1])) + 8
    except AttributeError:
        width, height = (max(1, int(v)) + 8 for v in probe_draw.textsize(ch, font=font))  # type: ignore[attr-defined]

    tmp = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    tmp_draw = ImageDraw.Draw(tmp)
    render_text_to_pil(
        tmp_draw,
        ch,
        4,
        4,
        font=font,
        locale=locale,
        fill=fill,
    )
    rotated = tmp.rotate(90, expand=True)
    image.alpha_composite(rotated, (int(x), int(y)))


def render_jlreq_text_block(
    image: Any,
    draw: Any,
    text: str,
    right_x: int,
    top_y: int,
    *,
    font: Any,
    locale: str,
    fill: tuple[int, int, int, int] = (0, 0, 0, 255),
    max_column_height: int,
    plan: Mapping[str, Any],
) -> tuple[int, int]:
    """Render text according to a JLREQ plan."""
    if str(plan.get("writing_mode") or "horizontal_tb") != "vertical_rl":
        render_text_to_pil(draw, text, right_x, top_y, font=font, locale=locale, fill=fill)
        try:
            bbox = draw.textbbox((right_x, top_y), text, font=font)
            return int(bbox[2] - bbox[0]), int(bbox[3] - bbox[1])
        except AttributeError:
            width, height = draw.textsize(text, font=font)  # type: ignore[attr-defined]
            return int(width), int(height)

    if not any(row.get("orientation") == "rotate90" for row in plan.get("glyph_plan") or []):
        from phoenix_v4.manga.chapter.cjk_text_shaper import render_vertical_cjk_block

        return render_vertical_cjk_block(
            draw,
            text,
            right_x,
            top_y,
            font=font,
            locale=locale,
            fill=fill,
            max_column_height=max_column_height,
            column_gap=int(plan.get("column_gap_px", 6) or 6),
        )

    columns = _build_vertical_columns(
        draw,
        text,
        font=font,
        max_column_height=max_column_height,
        plan=plan,
    )
    column_gap = int(plan.get("column_gap_px", 6) or 6)
    line_gap = int(plan.get("line_gap_px", 2) or 2)
    x_right = int(right_x)
    tallest = 0
    for column in columns:
        column_w = max((int(row["width"]) for row in column), default=1)
        x_left = x_right - column_w
        cur_y = int(top_y)
        for row in column:
            if row["orientation"] == "rotate90":
                _draw_rotated_glyph(
                    image,
                    str(row["char"]),
                    x=x_left,
                    y=cur_y,
                    font=font,
                    locale=locale,
                    fill=fill,
                )
            else:
                render_text_to_pil(
                    draw,
                    str(row["char"]),
                    x_left,
                    cur_y,
                    font=font,
                    locale=locale,
                    fill=fill,
                )
            cur_y += int(row["height"]) + line_gap
        tallest = max(tallest, cur_y - int(top_y))
        x_right = x_left - column_gap
    total_w = max(0, int(right_x) - x_right - column_gap)
    return total_w, tallest


def _bbox_overlap_area(a: Sequence[int], b: Sequence[int]) -> int:
    ax1, ay1, ax2, ay2 = (int(v) for v in a)
    bx1, by1, bx2, by2 = (int(v) for v in b)
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0
    return (ix2 - ix1) * (iy2 - iy1)


def plan_sfx_layout(
    text: str,
    *,
    locale: str,
    panel_size: tuple[int, int],
    occupied_bboxes: Sequence[Sequence[int]] = (),
    reading_direction: str = "rtl",
    format_id: str | None = None,
    font: Any | None = None,
    draw: Any | None = None,
    index: int = 0,
) -> dict[str, Any]:
    """Plan an SFX anchor/bbox against occupied bubbles and format direction."""
    panel_w, panel_h = (int(panel_size[0]), int(panel_size[1]))
    rd = normalize_reading_direction(reading_direction)
    prefer_vertical = locale == "ja_JP" and any(ord(ch) > 127 for ch in text)
    jlreq_plan = plan_dialogue_lettering(
        text,
        locale=locale,
        vertical_kanji=prefer_vertical,
    )

    if jlreq_plan["writing_mode"] == "vertical_rl" and draw is not None and font is not None:
        block_w, block_h = measure_jlreq_text_block(
            draw,
            text,
            font=font,
            locale=locale,
            max_column_height=max(60, int(panel_h * 0.4)),
            plan=jlreq_plan,
        )
    elif draw is not None and font is not None:
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            block_w = max(1, int(bbox[2] - bbox[0]))
            block_h = max(1, int(bbox[3] - bbox[1]))
        except AttributeError:
            block_w, block_h = (int(v) for v in draw.textsize(text, font=font))  # type: ignore[attr-defined]
    else:
        block_w = max(40, len(text) * 18)
        block_h = 54

    pad = 10
    box_w = block_w + pad * 2
    box_h = block_h + pad * 2
    if jlreq_plan["writing_mode"] == "vertical_rl":
        box_h = max(box_h, int(panel_h * 0.22))

    candidates: list[tuple[str, int, int]] = []
    if rd == "vertical_scroll" or format_id == "webtoon":
        candidates.extend(
            [
                ("below_action", int(panel_w * 0.55), int(panel_h * 0.72)),
                ("upper_band", int(panel_w * 0.58), int(panel_h * 0.16)),
                ("lower_band", int(panel_w * 0.26), int(panel_h * 0.78)),
            ]
        )
    elif rd == "rtl":
        candidates.extend(
            [
                ("leading_gutter", int(panel_w * 0.88), int(panel_h * 0.14)),
                ("trailing_gutter", int(panel_w * 0.26), int(panel_h * 0.64)),
                ("lower_band", int(panel_w * 0.70), int(panel_h * 0.76)),
            ]
        )
    else:
        candidates.extend(
            [
                ("leading_gutter", int(panel_w * 0.18), int(panel_h * 0.14)),
                ("trailing_gutter", int(panel_w * 0.70), int(panel_h * 0.64)),
                ("lower_band", int(panel_w * 0.28), int(panel_h * 0.76)),
            ]
        )

    # Nudge later SFX candidates so stacked onomatopoeia do not collapse.
    jitter_y = index * max(12, int(panel_h * 0.04))
    best_anchor = candidates[0][0] if candidates else "lower_band"
    best_bbox = [0, 0, box_w, box_h]
    best_score: int | None = None
    best_right_x = 0
    best_top_y = 0
    for anchor, right_x, top_y in candidates:
        top_y = min(max(0, top_y + jitter_y), max(0, panel_h - box_h))
        if jlreq_plan["writing_mode"] == "vertical_rl":
            bbox = [max(0, right_x - box_w), top_y, min(panel_w, right_x), min(panel_h, top_y + box_h)]
        else:
            left_x = max(0, min(panel_w - box_w, right_x))
            bbox = [left_x, top_y, min(panel_w, left_x + box_w), min(panel_h, top_y + box_h)]
        score = sum(_bbox_overlap_area(bbox, other) for other in occupied_bboxes)
        if best_score is None or score < best_score:
            best_anchor = anchor
            best_bbox = bbox
            best_score = score
            best_right_x = bbox[2] - pad if jlreq_plan["writing_mode"] == "vertical_rl" else bbox[0] + pad
            best_top_y = bbox[1] + pad
            if score == 0:
                break

    return {
        "schema_version": "1.0.0",
        "kind": "sfx_layout_plan",
        "anchor": best_anchor,
        "bbox": [int(v) for v in best_bbox],
        "occupied_overlap_area": int(best_score or 0),
        "writing_mode": jlreq_plan["writing_mode"],
        "runtime_status": jlreq_plan["runtime_status"],
        "right_x": int(best_right_x),
        "top_y": int(best_top_y),
        "max_column_height": max(60, int(best_bbox[3] - best_bbox[1] - (pad * 2))),
        "jlreq_plan": jlreq_plan,
    }

