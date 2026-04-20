"""Tests for scripts/catalog_visibility/extract_manga_series_index.py."""

from __future__ import annotations

from pathlib import Path

from scripts.catalog_visibility.extract_manga_series_index import (
    NORMALIZED_KEYS,
    extract_all,
    gap_lines,
    raw_doc_to_entry,
)


def test_extract_outputs_required_keys(tmp_path: Path) -> None:
    reg = tmp_path / "brand_registry.yaml"
    reg.write_text(
        """
schema_version: 1
brands:
  test_brand:
    catalog_id: en_us_core
    locale: en_US
""".strip(),
        encoding="utf-8",
    )
    root = tmp_path / "manga_profiles"
    series_dir = root / "examples"
    series_dir.mkdir(parents=True)
    series_dir.joinpath("one.yaml").write_text(
        """
title_id: series_alpha
brand_id: test_brand
market_demo: shonen
genre_family: battle
subgenre: x
emotional_engine: aspiration
serialization_engine: arc_based
visual_grammar: kinetic_shonen
reader_promise: "Feel the climb."
""".strip(),
        encoding="utf-8",
    )
    entries, errs = extract_all(root, reg)
    assert not errs
    assert len(entries) == 1
    row = entries[0]
    for k in NORMALIZED_KEYS:
        assert k in row, f"missing normalized key {k}"


def test_null_propagation(tmp_path: Path) -> None:
    reg = tmp_path / "brand_registry.yaml"
    reg.write_text("schema_version: 1\nbrands: {}\n", encoding="utf-8")
    raw = {
        "title_id": "only_core",
        "brand_id": "missing_registry_brand",
        "market_demo": "shonen",
    }
    entry = raw_doc_to_entry(raw, Path("config/source_of_truth/manga_profiles/x.yaml"), {})
    assert entry["series_title"] is None
    assert entry["marketing_angle"] is None
    assert entry["hook_lines"] is None
    assert entry["main_character_image_path"] is None
    assert entry["catalog_id"] is None


def test_gap_report_accuracy() -> None:
    entry = {
        "series_id": "gap_test",
        "main_character_image_path": None,
        "series_description": None,
        "marketing_angle": None,
        "reader_promise": "present",
        "launch_priority": "P0",
    }
    lines = gap_lines([entry])  # type: ignore[arg-type]
    assert len(lines) == 1
    body = lines[0]
    assert "series_id=gap_test" in body
    assert "main_character_image_path" in body
    assert "series_description" in body
    assert "marketing_angle" in body
    assert body.count(",") >= 2


def test_build_dashboard_filter(tmp_path: Path) -> None:
    from scripts.catalog_visibility.build_dashboard import _filter_series

    rows = [
        {"brand_id": "stillness_press", "locale": "en_US", "series_id": "a"},
        {"brand_id": "cognitive_clarity", "locale": "en_US", "series_id": "b"},
    ]
    r = _filter_series(rows, brand_id="brand1", locale="en")
    assert len(r) == 1
    assert r[0]["series_id"] == "a"


def test_embed_json_escapes_script() -> None:
    from scripts.catalog_visibility.build_dashboard import _safe_embed_json

    s = _safe_embed_json({"x": "</script>"})
    assert "</script>" not in s
    assert "script" in s


def test_build_dashboard_multibrand(tmp_path: Path) -> None:
    """Omitting --brand produces a dashboard containing all brands."""
    from scripts.catalog_visibility.build_dashboard import _filter_series, build_html

    rows = [
        {"brand_id": "stillness_press", "locale": "en_US", "series_id": "sp_1"},
        {"brand_id": "cognitive_clarity", "locale": "en_US", "series_id": "cc_1"},
        {"brand_id": "other_brand", "locale": "ja_JP", "series_id": "ot_1"},
    ]
    # No brand_id filter — locale en only
    filtered = _filter_series(rows, brand_id=None, locale="en")
    assert len(filtered) == 2, f"expected 2 en rows, got {len(filtered)}"

    out = tmp_path / "us_eng_manga_dashboard.html"
    # Build via build_html directly (template lives in repo)
    html = build_html(series_slice=filtered, page_title="Test all brands")
    out.write_text(html, encoding="utf-8")

    content = out.read_text(encoding="utf-8")
    assert out.exists()
    assert "stillness_press" in content
    assert "cognitive_clarity" in content
