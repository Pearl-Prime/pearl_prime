"""Tests for scripts/manga/generate_series_plans_from_catalog.py.

Regression-locks the v2 schema generator: catalog parsing, format routing,
schema validation. Runs against the real MANGA_FULL_CATALOG_PLAN.md and
real format_routing.yaml — fast (<1s) and catches drift cheaply.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.manga.generate_series_plans_from_catalog import (  # type: ignore
    CATALOG_PLAN,
    ROUTING_CFG,
    _load_yaml,
    _slugify,
    build_plan,
    build_series_id,
    derive_brand_id,
    parse_catalog,
    resolve_connector_lane,
    resolve_flatten_exports,
    resolve_format,
    resolve_target_platforms,
    validate_plan,
)


@pytest.fixture(scope="module")
def rows():
    return parse_catalog(CATALOG_PLAN)


@pytest.fixture(scope="module")
def routing():
    return _load_yaml(ROUTING_CFG)


@pytest.fixture(scope="module")
def schema():
    return json.loads(
        (REPO / "schemas" / "manga" / "series_plan.schema.json").read_text(encoding="utf-8")
    )


# ─── catalog parser ─────────────────────────────────────────────────────────


def test_catalog_parser_returns_rows(rows):
    assert len(rows) > 100, f"expected >100 rows from catalog, got {len(rows)}"


def test_catalog_parser_assigns_teacher_and_locale(rows):
    for r in rows:
        assert r["teacher_id"], "teacher_id must be set"
        assert r["locale"] in ("en_US", "ja_JP", "zh_TW", "zh_CN")
        assert r["genre"] in (
            "iyashikei", "seinen", "shonen", "shojo", "horror",
            "cultivation", "manhwa", "webtoon_romance", "isekai", "josei_essay_manga",
        )
        assert r["chapters_target"] >= 1


def test_catalog_parser_includes_ahjan_en_us(rows):
    matches = [r for r in rows if r["teacher_id"] == "ahjan" and r["locale"] == "en_US"]
    assert len(matches) >= 20, f"expected ≥20 ahjan en_US rows, got {len(matches)}"


# ─── routing ────────────────────────────────────────────────────────────────


def test_resolve_format_uses_style_override_for_webtoon_definition(routing):
    # power_progression style → forced color_vertical_webtoon for any locale
    fmt = resolve_format(routing, "ja_JP", "shonen", "power_progression")
    assert fmt == "color_vertical_webtoon"


def test_resolve_format_locale_specific_seinen_dark_psychological(routing):
    # ja_JP dark_psychological seinen → bw_page_manga; en_US → webtoon
    assert resolve_format(routing, "ja_JP", "seinen", "dark_psychological") == "bw_page_manga"
    assert resolve_format(routing, "en_US", "seinen", "dark_psychological") == "color_vertical_webtoon"


def test_resolve_target_platforms_excludes_partner_only(routing):
    # ja_JP color_vertical_webtoon → line_manga_indies + bookwalker (NOT piccoma_smartoon)
    targets = resolve_target_platforms(routing, "ja_JP", "color_vertical_webtoon")
    assert "line_manga_indies" in targets
    assert "piccoma_smartoon" not in targets, "PARTNER_ONLY platforms must not appear in target_platforms"


def test_resolve_connector_lane_three_lanes_observable(routing):
    # PR #631 verifies three connectors are needed
    assert resolve_connector_lane(routing, "en_US", "color_vertical_webtoon") == "unified_canvas"
    assert resolve_connector_lane(routing, "ja_JP", "color_vertical_webtoon") == "line_manga_indies"
    # zh_TW is in unified CANVAS too
    assert resolve_connector_lane(routing, "zh_TW", "color_vertical_webtoon") == "unified_canvas"


def test_resolve_flatten_exports_includes_bw_for_seinen_en_us(routing):
    flatten = resolve_flatten_exports(routing, "en_US", "seinen")
    assert "bw_page_manga" in flatten


def test_resolve_flatten_exports_empty_for_pure_webtoon_genres(routing):
    # webtoon_romance has no B&W tradition
    flatten = resolve_flatten_exports(routing, "en_US", "webtoon_romance")
    assert flatten == []


# ─── series_id construction ────────────────────────────────────────────────


def test_build_series_id_includes_brand_teacher_locale_topic(rows):
    r = next(x for x in rows if x["teacher_id"] == "ahjan" and x["locale"] == "en_US")
    sid = build_series_id(r)
    assert "stillness_press" in sid
    assert "ahjan" in sid
    assert "en_US" in sid
    assert r["topic"] in sid


def test_build_series_id_falls_back_for_non_latin_titles():
    row = {
        "teacher_id": "ahjan",
        "locale": "ja_JP",
        "title": "嘘をつくアラーム",          # all CJK
        "topic": "anxiety",
        "row_number": 1,
    }
    sid = build_series_id(row)
    assert sid.endswith("__row01"), sid


def test_derive_brand_id_returns_unique_brand_per_teacher():
    teachers = ["ahjan", "joshin", "junko", "maat", "miki", "ra"]
    brands = {derive_brand_id(t) for t in teachers}
    assert len(brands) == len(teachers), "each teacher should map to a unique brand"


# ─── full plan build + schema validation ──────────────────────────────────


def test_every_parsed_row_produces_schema_valid_plan(rows, routing, schema):
    failures: list[str] = []
    for r in rows:
        plan = build_plan(r, routing)
        errors = validate_plan(plan, schema)
        if errors:
            failures.append(f"{plan['series_id']}: {errors[0]}")
    assert not failures, f"{len(failures)} plans failed:\n  - " + "\n  - ".join(failures[:10])


def test_v2_plans_declare_master_format_and_connector_lane(rows, routing, schema):
    r = rows[0]
    plan = build_plan(r, routing)
    assert plan["series_plan_schema"] == "2.0.0"
    assert plan["master_format"] in (
        "color_vertical_webtoon", "bw_page_manga", "color_page_manga", "direct_self_help_illustrated"
    )
    assert plan["connector_lane"] in (
        "unified_canvas", "line_manga_indies", "naver_webtoon_kr", "print_only",
        "partner_required", "gray_zone_with_disclosure", "hold_pending_market_clearance",
    )


def test_v2_plans_carry_localized_titles_dict(rows, routing):
    r = rows[0]
    plan = build_plan(r, routing)
    assert plan["locale"] in plan["localized_titles"]
    assert plan["localized_titles"][plan["locale"]] == plan["title"]


def test_v2_plans_zh_cn_route_to_gray_zone_with_disclosure(rows, routing):
    """zh_CN routes to gray_zone_with_disclosure per CATALOG_RECONCILIATION_SPEC D-19 (OQ-6 c).

    Pre-D-19: zh_CN was BLOCKED → partner_required (no path).
    Post-D-19: zh_CN gray-zone push to Bilibili + Kuaikan + Tencent with full
    AI-disclosure metadata. R-zh_CN-distribution=HIGH risk; account termination
    possible under PRC Generative AI Service Measures (2023).
    """
    zh_cn_rows = [r for r in rows if r["locale"] == "zh_CN"]
    if not zh_cn_rows:
        pytest.skip("no zh_CN rows in catalog")
    plan = build_plan(zh_cn_rows[0], routing)
    # zh_CN webtoon → gray_zone_with_disclosure (per D-19)
    if plan["master_format"] == "color_vertical_webtoon":
        assert plan["connector_lane"] == "gray_zone_with_disclosure"
    # pending_partner_targets retains documented intent for premium partner deals
    assert "pending_partner_targets" in plan


def test_slugify():
    assert _slugify("The Alarm Is Lying") == "the_alarm_is_lying"
    assert _slugify("嘘をつくアラーム") == ""
    assert _slugify("3am Mind!") == "3am_mind"
