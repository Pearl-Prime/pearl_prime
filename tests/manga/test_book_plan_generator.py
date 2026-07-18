"""Tests for scripts/manga/generate_book_plans_from_series.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.manga.generate_book_plans_from_series import (  # type: ignore
    BOOK_SCHEMA,
    SERIES_ROOT,
    _book_id,
    _book_id_prefix,
    _engine_for_topic,
    _load_yaml,
    _page_target_count,
    build_book_plan,
    iter_series_plans,
    validate_plan,
)


@pytest.fixture(scope="module")
def schema():
    return json.loads(BOOK_SCHEMA.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def all_series_paths():
    return list(iter_series_plans())


# ─── book_id naming ────────────────────────────────────────────────────────


def test_book_id_prefix_per_format():
    assert _book_id_prefix("color_vertical_webtoon") == "ep"
    assert _book_id_prefix("bw_page_manga") == "chapter"
    assert _book_id_prefix("color_page_manga") == "chapter"
    assert _book_id_prefix("direct_self_help_illustrated") == "essay"


def test_book_id_zero_padding_per_format():
    assert _book_id("color_vertical_webtoon", 1) == "ep_001"
    assert _book_id("color_vertical_webtoon", 99) == "ep_099"
    assert _book_id("bw_page_manga", 1) == "chapter_01"
    assert _book_id("bw_page_manga", 14) == "chapter_14"
    assert _book_id("direct_self_help_illustrated", 5) == "essay_05"


def test_page_target_count_defaults_per_format():
    assert _page_target_count("color_vertical_webtoon") == 40   # 30-50 panel webtoon
    assert _page_target_count("bw_page_manga") == 20             # 18-22 page yokoyomi
    assert _page_target_count("direct_self_help_illustrated") == 8


# ─── engine mapping ────────────────────────────────────────────────────────


def test_engine_mapping_canonical():
    assert _engine_for_topic("anxiety") == "false_alarm"
    assert _engine_for_topic("burnout") == "overwhelm"
    assert _engine_for_topic("grief") == "grief"
    assert _engine_for_topic("comparison") == "comparison"


def test_engine_mapping_unknown_topic_returns_none():
    assert _engine_for_topic("not_a_real_topic") is None
    assert _engine_for_topic("") is None


# ─── plan construction ────────────────────────────────────────────────────


def test_build_book_plan_inherits_from_series(all_series_paths):
    if not all_series_paths:
        pytest.skip("no series plans on disk yet")
    series = _load_yaml(all_series_paths[0])
    plan = build_book_plan(series, 1)

    assert plan["book_plan_schema"] == "2.0.0"
    assert plan["series_id"] == series["series_id"]
    assert plan["master_format"] == (series.get("master_format") or series.get("format"))
    assert plan["flatten_exports"] == series.get("flatten_exports", [])
    assert plan["target_platforms"] == series["target_platforms"]
    assert plan["panel_layout_template"] == series["panel_layout_template"]


def test_build_book_plan_localized_titles_includes_locale(all_series_paths):
    if not all_series_paths:
        pytest.skip("no series plans on disk yet")
    series = _load_yaml(all_series_paths[0])
    plan = build_book_plan(series, 1)
    assert series["locale"] in plan["localized_titles"]


def test_build_book_plan_book_id_format_matches_master_format(all_series_paths):
    if not all_series_paths:
        pytest.skip("no series plans on disk yet")
    for path in all_series_paths[:5]:
        series = _load_yaml(path)
        plan = build_book_plan(series, 1)
        master = series.get("master_format") or series.get("format")
        prefix = _book_id_prefix(master)
        assert plan["book_id"].startswith(f"{prefix}_"), \
            f"{plan['series_id']}: book_id {plan['book_id']} doesn't match prefix {prefix}"


# ─── schema validation across all series ──────────────────────────────────


def test_every_series_chapter_produces_schema_valid_book_plan(all_series_paths, schema):
    """Every chapter of every series produces a book_plan that passes schema."""
    if not all_series_paths:
        pytest.skip("no series plans on disk yet")
    failures: list[str] = []
    for path in all_series_paths:
        series = _load_yaml(path)
        chapters = int(series.get("chapters_target") or 0)
        if chapters <= 0:
            continue
        # Sample first + last chapter (cheaper than all 14)
        for n in (1, chapters):
            plan = build_book_plan(series, n)
            errors = validate_plan(plan, schema)
            if errors:
                failures.append(f"{plan['series_id']}::{plan['book_id']}: {errors[0]}")
    assert not failures, f"{len(failures)} book_plans failed:\n  - " + "\n  - ".join(failures[:10])


def test_engine_attached_for_known_topics(all_series_paths):
    """Series whose topic is in the engine map attach the engine to the book."""
    if not all_series_paths:
        pytest.skip("no series plans on disk yet")
    found_with_engine = False
    for path in all_series_paths:
        series = _load_yaml(path)
        if _engine_for_topic(series.get("topic", "")):
            plan = build_book_plan(series, 1)
            assert "engine" in plan, f"{plan['series_id']}: known topic should attach engine"
            found_with_engine = True
            break
    assert found_with_engine, "expected at least one series with a mapped engine in fixture set"
