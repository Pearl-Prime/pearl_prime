from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_list_zero_coverage_topics_cli_smoke() -> None:
    out = subprocess.check_output(
        [
            sys.executable,
            str(REPO / "scripts/manga/list_zero_coverage_topics.py"),
            "--brand",
            "stillness_press",
            "--format",
            "slugs",
            "--min-panels",
            "60",
        ],
        text=True,
    ).strip()
    assert isinstance(out, str)


def test_list_zero_coverage_json() -> None:
    out = subprocess.check_output(
        [sys.executable, str(REPO / "scripts/manga/list_zero_coverage_topics.py"), "--brand", "stillness_press", "--format", "json"],
        text=True,
    )
    assert "zero_coverage_topics" in out
