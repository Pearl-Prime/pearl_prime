"""Regression: article_assembler must never return raw YAML as article content."""

from pathlib import Path

import pytest


@pytest.fixture
def no_group_articles(monkeypatch):
    """Deterministic: teacher slot tests must exercise pack path, not USLF group branch."""
    monkeypatch.setattr(
        "pearl_news.pipeline.article_assembler._is_uslf_group_article",
        lambda _item, _config_root: False,
    )


def test_teacher_slot_no_yaml_bleed(no_group_articles):
    """teacher_quotes_practices slot must return rendered prose, not raw YAML."""
    from pearl_news.pipeline.article_assembler import _resolve_slot

    item = {
        "teacher_id": "miki",
        "template_id": "hard_news_spiritual_response",
        "language": "en",
    }
    atoms_root = Path("pearl_news/atoms")
    result = _resolve_slot(
        "teacher_perspective",
        "teacher_quotes_practices",
        item,
        atoms_root,
        "climate",
        "13",
        {},
        "",
        Path("pearl_news/config"),
    )
    yaml_markers = ["topic_key:", "atoms:", "- >", "teachers:\n", "schema_version:"]
    for marker in yaml_markers:
        assert marker not in result, f"REGRESSION: raw YAML marker '{marker}' found in article slot output"


def test_teacher_slot_is_html_prose(no_group_articles):
    """teacher_quotes_practices slot must return HTML-ready prose, not raw topic dump."""
    from pearl_news.pipeline.article_assembler import _resolve_slot

    item = {"teacher_id": "maat", "template_id": "hard_news_spiritual_response", "language": "en"}
    atoms_root = Path("pearl_news/atoms")
    result = _resolve_slot(
        "teacher_perspective",
        "teacher_quotes_practices",
        item,
        atoms_root,
        "mental_health",
        "3",
        {},
        "",
        Path("pearl_news/config"),
    )
    assert isinstance(result, str) and len(result) > 20
    assert ":" not in result[:50] or "<" in result[:50], "Result looks like YAML, not prose"
