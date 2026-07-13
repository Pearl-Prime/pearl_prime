"""Deterministic vertical Japanese ruby/furigana planning and rendering.

This helper does not load bundled fonts. It uses the font objects supplied by the
caller and therefore preserves the repository's existing CJK fallback policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


class VerticalFuriganaError(ValueError):
    pass


@dataclass(frozen=True)
class RubySpan:
    base: str
    reading: str
    start: int
    end: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "base": self.base,
            "reading": self.reading,
            "start": self.start,
            "end": self.end,
        }


def resolve_ruby_spans(
    text: str,
    furigana: Sequence[Mapping[str, Any]],
) -> list[RubySpan]:
    """Resolve ordered, non-overlapping ruby spans against the exact base text."""
    cursor = 0
    spans: list[RubySpan] = []
    for row in furigana:
        base = str(row.get("base") or "")
        reading = str(row.get("reading") or "")
        if not base or not reading:
            raise VerticalFuriganaError("furigana rows require non-empty base and reading")
        explicit_start = row.get("start")
        if explicit_start is None:
            start = text.find(base, cursor)
        else:
            start = int(explicit_start)
            if text[start:start + len(base)] != base:
                raise VerticalFuriganaError(
                    f"furigana base mismatch at start={start}: expected {base!r}"
                )
        if start < 0:
            raise VerticalFuriganaError(f"furigana base not found in text: {base!r}")
        end = start + len(base)
        if spans and start < spans[-1].end:
            raise VerticalFuriganaError("furigana spans overlap")
        spans.append(RubySpan(base=base, reading=reading, start=start, end=end))
        cursor = end
    return spans


def plan_vertical_furigana(
    text: str,
    furigana: Sequence[Mapping[str, Any]],
    *,
    column_gap_px: int = 8,
    ruby_gap_px: int = 2,
) -> dict[str, Any]:
    spans = resolve_ruby_spans(text, furigana)
    ruby_by_index: dict[int, dict[str, Any]] = {}
    for span_index, span in enumerate(spans):
        for index in range(span.start, span.end):
            ruby_by_index[index] = {
                "span_index": span_index,
                "span_start": span.start,
                "span_end": span.end,
                "reading": span.reading,
            }
    return {
        "schema_version": "1.0.0",
        "writing_mode": "vertical_rl",
        "runtime_status": "ready_vertical_furigana",
        "column_gap_px": int(column_gap_px),
        "ruby_gap_px": int(ruby_gap_px),
        "spans": [span.to_dict() for span in spans],
        "ruby_by_base_index": ruby_by_index,
        "fallback_policy": "caller_font_fallback; never silently drop ruby",
    }


def _text_bbox(draw: Any, text: str, font: Any) -> tuple[int, int]:
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return max(1, int(bbox[2] - bbox[0])), max(1, int(bbox[3] - bbox[1]))
    except AttributeError:  # pragma: no cover - old Pillow
        width, height = draw.textsize(text, font=font)
        return max(1, int(width)), max(1, int(height))


def render_vertical_furigana(
    image: Any,
    draw: Any,
    text: str,
    right_x: int,
    top_y: int,
    *,
    base_font: Any,
    ruby_font: Any,
    fill: tuple[int, int, int, int] = (0, 0, 0, 255),
    ruby_fill: tuple[int, int, int, int] | None = None,
    line_gap_px: int = 2,
    plan: Mapping[str, Any],
) -> dict[str, Any]:
    """Render one vertical base column and ruby readings to its right.

    The caller remains responsible for column wrapping. This primitive is intended
    for a single dialogue column or a pre-wrapped column from the JLREQ planner.
    """
    if plan.get("runtime_status") != "ready_vertical_furigana":
        raise VerticalFuriganaError("plan is not ready_vertical_furigana")
    ruby_fill = ruby_fill or fill
    spans = [RubySpan(**row) for row in plan.get("spans") or []]
    base_positions: dict[int, tuple[int, int, int, int]] = {}
    cur_y = int(top_y)
    max_base_w = 1
    for index, ch in enumerate(text):
        if ch == "\n":
            continue
        width, height = _text_bbox(draw, ch, base_font)
        x = int(right_x) - width
        draw.text((x, cur_y), ch, font=base_font, fill=fill)
        base_positions[index] = (x, cur_y, x + width, cur_y + height)
        max_base_w = max(max_base_w, width)
        cur_y += height + int(line_gap_px)

    ruby_gap = int(plan.get("ruby_gap_px", 2))
    ruby_rows: list[dict[str, Any]] = []
    for span in spans:
        boxes = [
            base_positions[index]
            for index in range(span.start, span.end)
            if index in base_positions
        ]
        if not boxes:
            raise VerticalFuriganaError(
                f"resolved ruby span has no rendered base glyphs: {span.base!r}"
            )
        span_top = min(box[1] for box in boxes)
        span_bottom = max(box[3] for box in boxes)
        glyph_sizes = [_text_bbox(draw, ch, ruby_font) for ch in span.reading]
        reading_height = sum(height + 1 for _, height in glyph_sizes)
        ruby_y = span_top + max(0, (span_bottom - span_top - reading_height) // 2)
        ruby_x = int(right_x) + ruby_gap
        for ch, (width, height) in zip(span.reading, glyph_sizes):
            draw.text((ruby_x, ruby_y), ch, font=ruby_font, fill=ruby_fill)
            ruby_y += height + 1
        ruby_rows.append({
            **span.to_dict(),
            "x": ruby_x,
            "top_y": span_top,
            "bottom_y": span_bottom,
        })

    return {
        "runtime_status": "rendered_vertical_furigana",
        "base_glyph_count": len(base_positions),
        "ruby_span_count": len(ruby_rows),
        "ruby_rows": ruby_rows,
        "bbox": [
            int(right_x) - max_base_w,
            int(top_y),
            int(right_x) + ruby_gap + max(
                (_text_bbox(draw, ch, ruby_font)[0] for span in spans for ch in span.reading),
                default=0,
            ),
            cur_y,
        ],
    }
