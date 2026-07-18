"""Regression test: daily cycle must produce v5.2 sidebar output.

Checks:
  1. --v52 flag is present in run_daily_news_cycle.py cmd
  2. --teacher flag is present in run_daily_news_cycle.py cmd
  3. assemble_v52() produces sidebar HTML when called directly
"""
from __future__ import annotations

from pathlib import Path


def test_daily_cycle_cmd_includes_v52():
    src = Path("scripts/pearl_news/run_daily_news_cycle.py").read_text()
    assert "--v52" in src, "REGRESSION: --v52 flag missing from daily cycle cmd"


def test_daily_cycle_cmd_includes_teacher():
    src = Path("scripts/pearl_news/run_daily_news_cycle.py").read_text()
    assert "--teacher" in src, "REGRESSION: --teacher flag missing from daily cycle cmd"


def test_run_article_pipeline_has_teacher_arg():
    src = Path("pearl_news/pipeline/run_article_pipeline.py").read_text()
    assert '--teacher' in src, "REGRESSION: --teacher argparse arg missing from run_article_pipeline.py"


def test_run_article_pipeline_output_has_template_id():
    """template_id must be written explicitly to article payload JSON."""
    src = Path("pearl_news/pipeline/run_article_pipeline.py").read_text()
    assert '"template_id": template_id' in src, (
        "REGRESSION: template_id not written to article_payload in run_article_pipeline.py"
    )


def test_assemble_v52_produces_sidebar():
    """assemble_v52() must produce sidebar HTML for a known teacher."""
    from pearl_news.pipeline.assemble_v52 import assemble_v52

    mock_item = {
        "title": "Test Article",
        "content": "Test content about mental health.",
        "teacher": "maat",
        "topic": "mental_health",
        "language": "en",
        "sdg": "3",
        "pillar": "Mind",
        "slots": {},
    }
    meta = {
        "teacher": "maat",
        "topic": "mental_health",
        "sdg": "3",
        "template": "hard_news_spiritual_response",
        "date": "2026-04-22",
        "news_event": "Test news event",
        "hero_image_url": "",
    }
    result = assemble_v52(mock_item, meta, standalone=False)
    # v5.2 assembler uses class "sidebar" (not pn-sidebar)
    assert "sidebar" in result, (
        "REGRESSION: assemble_v52 not producing sidebar HTML (no 'sidebar' class found)"
    )
    # Verify it's the v5.2 CSS-based layout, not the legacy pn-byline layout
    assert "sidebar-card" in result, (
        "REGRESSION: assemble_v52 sidebar missing sidebar-card blocks"
    )


def test_assemble_v52_teacher_db_covers_all_roster_teachers():
    """All 10 teachers in teacher_news_roster.yaml must have TEACHER_DB entries."""
    from pearl_news.pipeline.assemble_v52 import TEACHER_DB
    try:
        import yaml
    except ImportError:
        return  # yaml not installed in this env; skip

    roster_path = Path("pearl_news/config/teacher_news_roster.yaml")
    roster = yaml.safe_load(roster_path.read_text()) or {}
    roster_ids = list((roster.get("teachers") or {}).keys())

    missing = [tid for tid in roster_ids if tid not in TEACHER_DB]
    assert not missing, (
        f"REGRESSION: teacher(s) in roster but missing from TEACHER_DB: {missing}"
    )


# ── Layout-variant tests (PR-2: five-layout system + governing spec) ─────────
# See docs/PEARL_NEWS_LAYOUT_SYSTEM_2026-05-04.md.
import pytest

_BASE_ITEM = {
    "title": "Test Article",
    "content": "Test content about mental health.",
    "teacher": "maat",
    "topic": "mental_health",
    "language": "en",
    "sdg": "3",
    "pillar": "Mind",
    "slots": {},
}
_BASE_META = {
    "teacher": "maat",
    "topic": "mental_health",
    "sdg": "3",
    "template": "hard_news_spiritual_response",
    "date": "2026-04-22",
    "news_event": "Test news event",
    "hero_image_url": "",
}


def _render(layout=None, language="en"):
    from pearl_news.pipeline.assemble_v52 import assemble_v52
    item = {**_BASE_ITEM, "language": language}
    meta = dict(_BASE_META)
    if layout is not None:
        meta["layout"] = layout
    meta["language"] = language
    return assemble_v52(item, meta, standalone=True)


def test_layout_variants_constant_has_five():
    from pearl_news.pipeline.assemble_v52 import LAYOUT_VARIANTS
    assert LAYOUT_VARIANTS == frozenset(
        {"default", "scroll_story", "dock", "editorial", "wide"}
    ), "LAYOUT_VARIANTS must enumerate exactly five variants"


def test_default_layout_renders_right_sidebar():
    html = _render("default")
    # Default = right sidebar via 1fr 360px grid (in CSS_BLOCK, always present)
    assert "1fr 360px" in html, "default layout missing right-sidebar grid"
    assert "<div class=\"sidebar\">" in html
    # No layout-override CSS should be injected for the default variant
    assert "sidebar-dock" not in html, "default layout must not include dock rail"
    assert "flex-direction: row" not in html, "default layout must not include wide-strip CSS"


def test_dock_layout_renders_left_sticky_sidebar():
    html = _render("dock")
    # Dock = left sticky sidebar
    assert "sidebar-dock" in html, "dock layout missing left dock rail"
    assert "position: sticky" in html, "dock layout sidebar must be sticky"
    assert "280px 1fr" in html, "dock layout missing left-sidebar grid"


def test_wide_layout_renders_bottom_strip():
    html = _render("wide")
    # Wide = bottom-strip sidebar (display: block container, sidebar reflows as flex row)
    assert "CSS_WIDE" not in html, "constant name should not leak; only its rules should"
    assert "flex-direction: row" in html, (
        "wide layout missing horizontal flex strip on .sidebar"
    )
    # Default English label
    assert 'content: "PRACTICE & ENGAGE"' in html, (
        "wide layout missing 'PRACTICE & ENGAGE' strip header"
    )
    # Lang-aware overrides present in the stylesheet (active for ja/zh/ko)
    assert "実践と参加" in html, "wide layout missing JA strip header override"


def test_wide_layout_lang_attribute_threads_through():
    html = _render("wide", language="ja")
    assert 'lang="ja"' in html, "wide layout must propagate language to root attribute"


def test_editorial_layout_renders_wider_canvas():
    html = _render("editorial")
    # Editorial = wider canvas (1280px vs 1100px), right sidebar
    assert "max-width: 1280px" in html, "editorial layout missing 1280px canvas"
    assert "1fr 280px" in html, "editorial layout missing right-sidebar grid"


def test_scroll_story_layout_hides_sidebar():
    html = _render("scroll_story")
    # scroll_story = no sidebar; cards inline
    assert ".sidebar { display: none; }" in html, (
        "scroll_story layout must hide the sidebar"
    )


def test_unknown_layout_falls_back_to_default(caplog):
    import logging
    caplog.set_level(logging.WARNING, logger="pearl_news.pipeline.assemble_v52")
    html = _render("widee")  # typo
    # Falls back to default — warning emitted, no layout-override CSS injected
    assert "1fr 360px" in html, "unknown layout did not fall back to default"
    assert "sidebar-dock" not in html, "unknown layout leaked dock CSS"
    assert "flex-direction: row" not in html, "unknown layout leaked wide CSS"
    assert any(
        "unknown layout" in rec.message.lower() for rec in caplog.records
    ), "unknown layout must emit a logger.warning"


def test_dock_mobile_surfaces_sidebar_cards():
    """Dock mobile must surface the .sidebar block (cards) instead of leaving mobile users blank."""
    html = _render("dock")
    # Mobile media query must show .sidebar (cards) when dock rail is hidden
    assert "@media (max-width: 768px)" in html
    assert ".sidebar-dock { display: none" in html
    # The dock CSS must REVEAL .sidebar on mobile (not leave it display:none).
    # Look for the canonical rule we ship: ".pn-article-root .sidebar { display: flex" (any whitespace)
    import re
    sidebar_revealed = re.search(
        r"\.pn-article-root\s+\.sidebar\s*\{\s*display:\s*(flex|block)",
        html,
    )
    assert sidebar_revealed, (
        "dock mobile breakpoint must reveal .pn-article-root .sidebar with display:flex/block "
        "(BLOCKER: mobile dock users would lose practice/CTA cards)"
    )
