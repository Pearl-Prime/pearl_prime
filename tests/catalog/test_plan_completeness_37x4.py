"""Layer 1 plan-completeness validator + podcast plan generator tests."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PODCAST_TSV = (
    REPO
    / "artifacts"
    / "catalog"
    / "worldwide_catalog_37_brand_podcast_plan_2026-05-27.tsv"
)
COMPLETENESS_TSV = (
    REPO / "artifacts" / "catalog" / "plan_completeness_37x4_20260527.tsv"
)
LAUNCH_LOCALES = {"en_US", "ja_JP", "zh_TW", "zh_CN"}


def test_podcast_generator_dimensions():
    from scripts.catalog.generate_podcast_plan_37x4 import build_rows

    rows = build_rows()
    assert len(rows) == 148  # 37 brands x 4 locales
    brands = {r[0] for r in rows}
    locales = {r[1] for r in rows}
    surfaces = {r[2] for r in rows}
    assert len(brands) == 37
    assert locales == LAUNCH_LOCALES
    assert surfaces == {"podcast"}
    # every cell carries positive, integer counts
    for _b, _l, _s, series, eps, _phase in rows:
        assert isinstance(series, int) and series > 0
        assert isinstance(eps, int) and eps > 0


def test_podcast_generator_locale_sizing_from_market_config():
    """series_count / episodes are driven by brand_podcast_plans.yaml per locale."""
    from scripts.catalog.generate_podcast_plan_37x4 import build_rows

    rows = build_rows()
    sizing = {r[1]: (r[3], r[4]) for r in rows if r[0] == "stillness_press"}
    # weekly cadence; values mirror config/podcast/brand_podcast_plans.yaml markets
    assert sizing["en_US"] == (6, 10)
    assert sizing["ja_JP"] == (4, 8)
    assert sizing["zh_TW"] == (3, 10)
    assert sizing["zh_CN"] == (4, 12)


def test_podcast_tsv_on_disk_is_current():
    if not PODCAST_TSV.exists():
        pytest.skip("podcast plan TSV not present")
    from scripts.catalog.generate_podcast_plan_37x4 import build_rows, render

    expected = render(build_rows())
    assert PODCAST_TSV.read_text(encoding="utf-8") == expected, (
        "podcast plan TSV is stale; rerun generate_podcast_plan_37x4.py"
    )


def test_plan_completeness_validator_passes():
    """The Layer 1 gate must report 444/444 cells covered (exit 0)."""
    from scripts.catalog.validate_plan_completeness_37x4 import validate

    # Skip if the manga series-plan SSOT is not materialized in this checkout
    # (worktrees may omit it); the validator raises SystemExit(2) in that case.
    manga_dir = REPO / "config" / "source_of_truth" / "manga_series_plans"
    if not manga_dir.exists() or not any(manga_dir.rglob("*.yaml")):
        pytest.skip("manga_series_plans SSOT not materialized in this checkout")
    rc = validate(write=False)
    assert rc == 0


def test_completeness_tsv_all_complete():
    if not COMPLETENESS_TSV.exists():
        pytest.skip("completeness TSV not present")
    rows = list(csv.DictReader(COMPLETENESS_TSV.open(encoding="utf-8"), delimiter="\t"))
    assert len(rows) == 148  # 37 brands x 4 locales
    assert all(r["status"] == "COMPLETE" for r in rows)
    assert {r["locale"] for r in rows} == LAUNCH_LOCALES
    assert len({r["brand_id"] for r in rows}) == 37
