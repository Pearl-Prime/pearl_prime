from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.quality.ei_v2.duration_fit import score_duration_fit  # noqa: E402


def test_duration_fit_on_target():
    out = score_duration_fit(
        {"format": "video_short", "intent": "discovery", "duration_sec": 22},
    )
    assert out["dimension"] == "duration_fit"
    assert out["score"] >= 0.5
    assert "pass" in out


def test_duration_fit_pages():
    out = score_duration_fit(
        {"format": "ebook_standard", "intent": "therapeutic", "page_count": 200},
    )
    assert out["score"] > 0.4
