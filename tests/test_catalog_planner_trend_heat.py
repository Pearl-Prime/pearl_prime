"""PR 3: BookSpec.trend_heat_score from structured trend_score JSON."""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture()
def planner():
    from phoenix_v4.planning.catalog_planner import CatalogPlanner

    return CatalogPlanner()


def _trend_file_for_grief(tmp_path: Path) -> Path:
    p = tmp_path / "trend_score_2026-08-01.json"
    payload = {
        "score_date": "2026-08-01",
        "top_signals": [
            {
                "kind": "google_trends_serpapi",
                "keyword": "grief",
                "pct_change_7d": 10.0,
                "spike": True,
                "current_interest": 50.0,
            }
        ],
    }
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def test_produce_single_sets_trend_heat_when_topic_matches(planner, tmp_path: Path) -> None:
    trend_path = _trend_file_for_grief(tmp_path)
    spec = planner.produce_single(
        "grief",
        "nyc_exec",
        trend_score_path=trend_path,
    )
    assert spec.trend_heat_score is not None
    assert spec.trend_heat_score >= 60.0
    assert spec.to_dict().get("trend_heat_score") == spec.trend_heat_score


def test_produce_single_no_path_leaves_trend_heat_none(planner) -> None:
    spec = planner.produce_single("grief", "nyc_exec")
    assert spec.trend_heat_score is None
    assert "trend_heat_score" not in spec.to_dict()


def test_produce_single_missing_file_degrades(planner, tmp_path: Path) -> None:
    spec = planner.produce_single(
        "grief",
        "nyc_exec",
        trend_score_path=tmp_path / "missing.json",
    )
    assert spec.trend_heat_score is None


def test_produce_single_no_signal_match(planner, tmp_path: Path) -> None:
    p = tmp_path / "trend.json"
    p.write_text(
        json.dumps(
            {
                "top_signals": [
                    {
                        "kind": "google_trends_serpapi",
                        "keyword": "unrelated_keyword",
                        "pct_change_7d": 99.0,
                        "spike": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    spec = planner.produce_single("grief", "nyc_exec", trend_score_path=p)
    assert spec.trend_heat_score is None


def test_trend_heat_from_confirmed_topics(planner, tmp_path: Path) -> None:
    p = tmp_path / "trend.json"
    p.write_text(
        json.dumps(
            {
                "confirmed_topics": [
                    {
                        "topic": "shame",
                        "et_volume": 1000,
                        "et_growth_pct": 120,
                        "matched_topic_ids": [],
                        "topic_id_match_count": 0,
                        "fast_publish_candidate": False,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    spec = planner.produce_single("shame", "nyc_exec", trend_score_path=p)
    assert spec.trend_heat_score is not None
    assert spec.trend_heat_score >= 60.0


def test_produce_wave_applies_trend_when_configured(planner, tmp_path: Path) -> None:
    trend_path = _trend_file_for_grief(tmp_path)
    specs = planner.produce_wave(12, seed="trend_wave", trend_score_path=trend_path)
    grief_specs = [s for s in specs if s.topic_id == "grief"]
    assert grief_specs
    assert all(s.trend_heat_score is not None for s in grief_specs)
