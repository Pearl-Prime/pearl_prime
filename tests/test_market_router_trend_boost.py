"""PR 3: Market router optional boost from structured trend_score JSON."""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture()
def artifacts_dir(tmp_path: Path) -> Path:
    d = tmp_path / "ml_ed"
    d.mkdir()
    (d / "section_scores.jsonl").write_text(
        json.dumps({"book_id": "bk1", "weak_flags": []}) + "\n",
        encoding="utf-8",
    )
    (d / "reader_fit_scores.jsonl").write_text(
        json.dumps(
            {
                "book_id": "bk1",
                "persona_id": "nyc_exec",
                "topic_id": "grief",
                "locale": "en-US",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (d / "variant_rankings.jsonl").write_text(
        json.dumps({"book_id": "bk1", "variant": "a"}) + "\n",
        encoding="utf-8",
    )
    return d


def _trend_high_grief(tmp_path: Path) -> Path:
    p = tmp_path / "trend_score.json"
    p.write_text(
        json.dumps(
            {
                "top_signals": [
                    {
                        "kind": "google_trends_serpapi",
                        "keyword": "grief",
                        "pct_change_7d": 12.0,
                        "spike": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return p


def test_router_boosts_priority_when_trend_file_matches_topic(
    artifacts_dir: Path,
    tmp_path: Path,
) -> None:
    from scripts.ml_editorial.run_market_router import run_market_router

    out = tmp_path / "market_actions.jsonl"
    trend = _trend_high_grief(tmp_path)
    run_market_router(artifacts_dir, out, {}, trend_score_path=trend)
    lines = [ln for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["priority"] == "high"
    assert row.get("trend_priority_boost") is True
    assert row.get("trend_heat_score") is not None
    assert "structured trend_score" in row["rationale"]


def test_router_no_boost_without_trend_path(artifacts_dir: Path, tmp_path: Path) -> None:
    from scripts.ml_editorial.run_market_router import run_market_router

    out = tmp_path / "market_actions.jsonl"
    run_market_router(artifacts_dir, out, {})
    row = json.loads(out.read_text(encoding="utf-8").strip().splitlines()[0])
    assert row["priority"] == "medium"
    assert "trend_heat_score" not in row
    assert "trend_priority_boost" not in row


def test_router_weak_sections_stays_low_even_with_trend(
    tmp_path: Path,
) -> None:
    from scripts.ml_editorial.run_market_router import run_market_router

    d = tmp_path / "ml_ed"
    d.mkdir()
    (d / "section_scores.jsonl").write_text(
        json.dumps({"book_id": "bk2", "weak_flags": ["thin_intro"]}) + "\n",
        encoding="utf-8",
    )
    (d / "reader_fit_scores.jsonl").write_text(
        json.dumps({"book_id": "bk2", "topic_id": "grief", "persona_id": "p"}) + "\n",
        encoding="utf-8",
    )
    (d / "variant_rankings.jsonl").write_text(
        json.dumps({"book_id": "bk2"}) + "\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.jsonl"
    trend = _trend_high_grief(tmp_path)
    run_market_router(d, out, {}, trend_score_path=trend)
    row = json.loads(out.read_text(encoding="utf-8").strip().splitlines()[0])
    assert row["priority"] == "low"
    assert row.get("trend_priority_boost") is not True
