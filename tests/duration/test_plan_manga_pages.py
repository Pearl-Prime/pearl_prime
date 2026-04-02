from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.duration.plan_manga_pages import plan_manga  # noqa: E402


def test_iyashikei_overhead():
    d = plan_manga("webtoon", "iyashikei", True, "en-US", breath_sequences=2)
    assert d["therapeutic_overhead_panels"] >= 14
    assert 20 <= d["recommended_panel_count"] <= 80


def test_kakao_min_panels():
    d = plan_manga("kakao", "fantasy", False, "ko-KR", 0)
    assert d["panel_range"][0] >= 40


def test_cli(tmp_path):
    out = tmp_path / "m.json"
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "duration" / "plan_manga_pages.py"), "-o", str(out)],
        cwd=REPO_ROOT,
        check=True,
    )
    assert "recommended_panel_count" in json.loads(out.read_text(encoding="utf-8"))
