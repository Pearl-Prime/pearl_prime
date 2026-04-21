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
