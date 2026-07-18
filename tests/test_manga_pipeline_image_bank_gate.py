from __future__ import annotations

from pathlib import Path

from scripts.run_manga_pipeline import count_topic_panel_pngs


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_count_topic_panel_pngs_burnout() -> None:
    n = count_topic_panel_pngs(REPO_ROOT, "stillness_press", "burnout")
    assert n >= 50
