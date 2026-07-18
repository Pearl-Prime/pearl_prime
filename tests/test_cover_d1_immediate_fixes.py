"""Regression tests for cover-system D1 immediate fixes.

Two specific cover defects surfaced by operator on 2026-05-04, both diagnosed in
artifacts/research/cover_design_intelligence_gap_2026-05-04.md §B:

1. Maat boundaries cover ("No That Saved Me") — gibberish title because
   _wrap_to_width is syntax-naive and orphans articles/conjunctions at line ends.
2. Joshin anxiety cover — shipped with NO title rendered because the manga
   cover_assembler swallowed the title-render exception and continued.

These tests pin both fixes so they don't regress.
"""
from __future__ import annotations

from pathlib import Path

import pytest


# ── D1a — orphan-prevention in _wrap_to_width ────────────────────────────────


def _make_draw_and_font(font_size: int = 60):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (1000, 200))
    draw = ImageDraw.Draw(img)
    # Use the default PIL font — exact metrics don't matter for wrapping logic;
    # we only need a real font object so _measure_text returns sensible widths.
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()
    return draw, font


def test_wrap_does_not_orphan_leading_article_when_geometry_allows():
    """'The Book of No' must not wrap as ['The Book', 'of No'] when 'The Book of' fits one line.

    Wrapper-level test: pick a width where the orphan-free version geometrically fits,
    and assert orphan-prevention runs. Width too tight = geometry wins; that's the
    fitter's job to shrink the font and is exercised in the fitter test below.
    """
    from scripts.publish.render_kdp_cover import _wrap_to_width, _measure_text
    draw, font = _make_draw_and_font(60)
    # Target a width that fits "The Book of" on one line so orphan-prevention can succeed.
    # Empirical: at size 60 Arial, "The Book of" is ~280-340px wide. Use 400 for safety.
    text = "The Book of No"
    full_w, _ = _measure_text(draw, text, font, 0)
    max_width = max(400, full_w // 2 + 100)  # wide enough that pulling "of" works
    lines = _wrap_to_width(draw, text, font, tracking_px=0, max_width=max_width)
    for line in lines[:-1]:  # last line cannot orphan
        tokens = line.split()
        if tokens:
            assert tokens[-1].lower() not in ("the", "of", "a", "an"), (
                f"orphan at end of line: {line!r} (full wrap: {lines!r}, max_width={max_width})"
            )


def test_wrap_does_not_orphan_short_preposition():
    """'Stories of Boundaries' must not wrap as ['Stories of', 'Boundaries'].

    Pick a width where 'of Boundaries' fits on one line so the orphan-pull works.
    If 'Boundaries' alone is wider than 'of Boundaries' minus ~40px tracking, the
    pull is geometrically valid and the wrapper must apply it.
    """
    from scripts.publish.render_kdp_cover import _wrap_to_width, _measure_text
    draw, font = _make_draw_and_font(60)
    text = "Stories of Boundaries"
    full_w, _ = _measure_text(draw, text, font, 0)
    # Set max_width from the actual measured width of "of Boundaries" plus a small margin,
    # so the orphan-pull is geometrically valid regardless of font metrics on the runner.
    # int(full_w * 0.65) was font-metric-fragile: on the CI runner's font, "of Boundaries"
    # measured wider than 0.65 * "Stories of Boundaries" and the pull bailed (CI run
    # 25294763610 / job 74151675435).
    of_boundaries_w, _ = _measure_text(draw, "of Boundaries", font, 0)
    max_width = of_boundaries_w + 4
    lines = _wrap_to_width(draw, text, font, tracking_px=0, max_width=max_width)
    for line in lines[:-1]:
        tokens = line.split()
        if tokens:
            assert tokens[-1].lower() != "of", (
                f"orphan preposition 'of' at end of line: {line!r} (full wrap: {lines!r}, "
                f"max_width={max_width}, full_text_w={full_w})"
            )


def test_wrap_does_not_orphan_no_or_not():
    """'The No That Saved Me' (Maat-style title) must not orphan 'No' when geometry permits."""
    from scripts.publish.render_kdp_cover import _wrap_to_width, _measure_text
    draw, font = _make_draw_and_font(60)
    text = "The No That Saved Me"
    full_w, _ = _measure_text(draw, text, font, 0)
    # Width that fits ~85% of full title — enough room for orphan-prevention to pull words down.
    # 70% was too tight; greedy lands on "The No / That Saved Me" and orphan-pull can't
    # geometrically fit "No That Saved Me" on one line.
    max_width = int(full_w * 0.85)
    lines = _wrap_to_width(draw, text, font, tracking_px=0, max_width=max_width)
    for line in lines[:-1]:
        tokens = line.split()
        if tokens:
            assert tokens[-1].lower() not in ("no", "not", "the"), (
                f"orphan word at end of line: {line!r} (full wrap: {lines!r}, "
                f"max_width={max_width}, full_text_w={full_w})"
            )


def test_fit_font_shrinks_to_avoid_orphan():
    """_fit_font_to_box prefers orphan-free even if it means a smaller font.

    The fitter is the integration point: when greedy + orphan-prevention can't
    avoid an orphan at the initial size, the fitter must shrink the font until
    orphan prevention succeeds. This is the production code path for titles
    like 'The Book of No' rendering in a tight box.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path("scripts/publish").resolve()))
    from scripts.publish.render_kdp_cover import _fit_font_to_box, load_typography_config
    cfg = load_typography_config()
    style = {"font_family": "serif", "font_weight": "bold", "tracking_pct": 0}
    # Box that's tight at large fonts but workable at smaller ones
    _font, lines, size = _fit_font_to_box(
        cfg, "The Book of No", style,
        max_width=400, max_height=400,
        initial_size=120, min_size=24,
    )
    # No line may end with an orphan-candidate
    for line in lines[:-1]:
        tokens = line.split()
        if tokens:
            assert tokens[-1].lower() not in ("the", "a", "an", "of", "no", "not"), (
                f"_fit_font_to_box returned orphan at size {size}: lines={lines!r}"
            )


def test_wrap_preserves_long_word_overflow():
    """A single word wider than max_width must still emit (typography fitter shrinks font separately)."""
    from scripts.publish.render_kdp_cover import _wrap_to_width
    draw, font = _make_draw_and_font(60)
    lines = _wrap_to_width(draw, "Antidisestablishmentarianism", font, tracking_px=0, max_width=50)
    assert lines == ["Antidisestablishmentarianism"], (
        "single-word overflow must not be split; got: %r" % lines
    )


def test_wrap_handles_empty_string():
    from scripts.publish.render_kdp_cover import _wrap_to_width
    draw, font = _make_draw_and_font(60)
    assert _wrap_to_width(draw, "", font, tracking_px=0, max_width=100) == [""]
    assert _wrap_to_width(draw, "   ", font, tracking_px=0, max_width=100) == [""]


def test_wrap_skips_orphan_pass_for_cjk():
    """CJK titles do not have English-style article orphans; the orphan pass must NOT touch them."""
    from scripts.publish.render_kdp_cover import _wrap_to_width, _is_ascii_dominant
    # Sanity: the heuristic identifies CJK as non-ASCII-dominant
    assert _is_ascii_dominant("境界線の本") is False
    assert _is_ascii_dominant("The Book of No") is True
    # And the wrapper still splits CJK normally (greedy whitespace, no orphan rules)
    draw, font = _make_draw_and_font(40)
    lines = _wrap_to_width(draw, "境界線 の 本", font, tracking_px=0, max_width=80)
    assert lines  # just don't crash


# ── D1b — manga cover_assembler is fail-closed on missing title ──────────────


def _minimal_cover_params(*, title_text: str, typography_config=None):
    """Minimal CoverParams for tests — fills required fields with stub values."""
    from phoenix_v4.manga.covers.cover_selector import CoverParams
    return CoverParams(
        series_id="test",
        brand_id="test",
        volume_number=1,
        market_code="ja",
        seed=1,
        genre="general",
        art_style_token="test",
        positive_prompt="",
        negative_prompt="",
        steps=28,
        cfg_scale=3.5,
        sampler="dpmpp_2m",
        scheduler="karras",
        flux_width=640,
        flux_height=960,
        title_text=title_text,
        title_zone_fraction=0.30,
        typography_config=typography_config,
    )


def test_manga_cover_assembler_rejects_missing_title(tmp_path: Path):
    """CoverAssembler.apply_typography must raise when title_text is empty.

    Historical bug (2026-04..05): manga covers shipped to artifacts/pipeline_examples/
    with no title because the assembler swallowed the exception and continued.
    Now the contract is fail-closed.
    """
    from PIL import Image
    from phoenix_v4.manga.covers.cover_assembler import CoverAssembler

    raw_path = tmp_path / "raw.png"
    Image.new("RGB", (640, 960), color=(40, 60, 90)).save(raw_path)
    out_path = tmp_path / "out.png"
    assembler = CoverAssembler()

    with pytest.raises(ValueError, match="title_text is required"):
        assembler.overlay_typography_front(raw_path, _minimal_cover_params(title_text=""), out_path)
    with pytest.raises(ValueError, match="title_text is required"):
        assembler.overlay_typography_front(raw_path, _minimal_cover_params(title_text="   "), out_path)


def test_manga_cover_assembler_rejects_missing_typography_config(tmp_path: Path):
    """A non-empty title with no typography_config is also a fail."""
    from PIL import Image
    from phoenix_v4.manga.covers.cover_assembler import CoverAssembler

    raw_path = tmp_path / "raw.png"
    Image.new("RGB", (640, 960), color=(40, 60, 90)).save(raw_path)
    out_path = tmp_path / "out.png"
    assembler = CoverAssembler()

    with pytest.raises(ValueError, match="typography_config is required"):
        assembler.overlay_typography_front(
            raw_path,
            _minimal_cover_params(title_text="Anxiety: A Field Guide", typography_config=None),
            out_path,
        )
