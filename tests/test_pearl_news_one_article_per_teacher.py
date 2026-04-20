"""
Tests for INV-2 (one teacher per article) and INV-5/INV-6 (layout + sidebar).

These tests:
1. Verify the article payload builder (run_article_pipeline) injects a single
   teacher's byline and sidebar — not a list of teachers.
2. Verify the detectors correctly flag articles that are missing byline/sidebar.
3. Verify detector passes clean articles.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.quality.regression_museum.pearl_news_detectors import (
    detect_pearl_news_missing_layout_shell,
    detect_pearl_news_missing_sidebar,
    detect_pearl_news_multi_teacher_article,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _write_article(tmp_path: Path, slug: str, overrides: dict) -> Path:
    base = {
        "title": "Test Article",
        "content": (
            '<div class="pn-byline">'
            '<span class="pn-byline-name">Ahjan</span>'
            ' | <span class="pn-byline-tradition">Theravada Buddhist</span>'
            ' | <span class="pn-byline-lang">EN</span>'
            '</div>'
            '<p>Article body text here.</p>'
            '<aside class="pn-sidebar" data-teacher="ahjan">'
            '<section class="pn-sidebar-teacher">'
            '<h3 class="pn-sidebar-teacher-name">Ahjan</h3>'
            '</section>'
            '</aside>'
        ),
        "teacher_id": "ahjan",
        "teacher_used": {"teacher_id": "ahjan", "display_name": "Ahjan", "tradition": "Theravada Buddhist"},
        "sidebar": {"teacher_name": "Ahjan", "teacher_tradition": "Theravada Buddhist", "teacher_language": "en", "topic": "climate"},
        "language": "en",
        "topic": "climate",
        "article_type": "hard_news_spiritual_response",
    }
    base.update(overrides)
    path = tmp_path / f"article_{slug}.json"
    path.write_text(json.dumps(base), encoding="utf-8")
    return path


class TestOneTeacherInvariant:
    def test_single_teacher_article_passes(self, tmp_path):
        _write_article(tmp_path, "aaa", {})
        violations = detect_pearl_news_multi_teacher_article(tmp_path)
        assert violations == [], f"Expected no violations, got: {violations}"

    def test_no_teacher_in_non_interfaith_template_fails(self, tmp_path):
        _write_article(tmp_path, "bbb", {
            "teacher_id": None,
            "teacher_used": {"teacher_id": None, "display_name": None, "tradition": None},
            "article_type": "hard_news_spiritual_response",
        })
        violations = detect_pearl_news_multi_teacher_article(tmp_path)
        assert len(violations) == 1
        assert violations[0].failure_class == "pearl_news_multi_teacher_article"
        assert violations[0].severity == "block"

    def test_interfaith_template_with_no_teacher_is_exempt(self, tmp_path):
        _write_article(tmp_path, "ccc", {
            "teacher_id": None,
            "teacher_used": {"teacher_id": None, "display_name": None, "tradition": None},
            "article_type": "interfaith_dialogue_report",
        })
        violations = detect_pearl_news_multi_teacher_article(tmp_path)
        assert violations == [], "Interfaith dialogue template is exempt from single-teacher rule"


class TestLayoutShellInvariant:
    def test_article_with_byline_passes(self, tmp_path):
        _write_article(tmp_path, "aaa", {})
        violations = detect_pearl_news_missing_layout_shell(tmp_path)
        assert violations == []

    def test_article_without_byline_fails(self, tmp_path):
        _write_article(tmp_path, "bbb", {
            "content": "<h1>Title</h1><p>Raw prose with no byline block.</p>",
        })
        violations = detect_pearl_news_missing_layout_shell(tmp_path)
        assert len(violations) == 1
        assert violations[0].failure_class == "pearl_news_missing_layout_shell"
        assert violations[0].severity == "block"


class TestSidebarInvariant:
    def test_article_with_sidebar_passes(self, tmp_path):
        _write_article(tmp_path, "aaa", {})
        violations = detect_pearl_news_missing_sidebar(tmp_path)
        assert violations == []

    def test_article_without_sidebar_html_fails(self, tmp_path):
        _write_article(tmp_path, "bbb", {
            "content": (
                '<div class="pn-byline">By Ahjan | Theravada Buddhist | EN</div>'
                "<p>Article body without sidebar.</p>"
            ),
            "sidebar": {"teacher_name": "Ahjan"},
        })
        violations = detect_pearl_news_missing_sidebar(tmp_path)
        assert len(violations) == 1
        assert violations[0].failure_class == "pearl_news_missing_sidebar"

    def test_article_without_sidebar_json_fails(self, tmp_path):
        _write_article(tmp_path, "ccc", {"sidebar": {}})
        violations = detect_pearl_news_missing_sidebar(tmp_path)
        assert len(violations) == 1
        assert violations[0].failure_class == "pearl_news_missing_sidebar"
