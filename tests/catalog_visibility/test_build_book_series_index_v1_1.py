"""Tests for the V1.1 planned-catalog ingestion in ``build_book_series_index``.

Covers the new ``_load_v1_1_planned_books`` helper and the merge behavior
with the legacy rendered ``TEACHER_BOOKS`` row set:

- Planned book count equals sum(series_count) across ebook rows
- Each planned row carries ``status="planned"``
- ``book_id`` is deterministic from (brand_id, locale, series_idx)
- A (brand, locale) cell with no themes still emits synthetic planned rows
  (no crash, fallback title is human-readable)
- Rendered vs planned merge: identical book_id keeps rendered metadata
- Status filter chip math: rendered+planned == total
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.catalog_visibility import build_book_series_index as bbsi


SYNTH_TSV = (
    "brand_id\tlocale\tsurface\tseries_count\tepisode_per_series_count\tpriority_phase\n"
    "alpha_brand\ten_US\tebook\t3\t5\tV1.1_proposed\n"
    "alpha_brand\tja_JP\tebook\t2\t5\tV1.1_proposed\n"
    "alpha_brand\ten_US\tmanga\t10\t24\tV1.1_proposed\n"  # manga ignored
    "beta_brand\ten_US\tebook\t4\t5\tV1.1_proposed\n"
    "beta_brand\tja_JP\tebook\t2\t5\tV1.1_proposed\n"
    "gamma_no_themes\ten_US\tebook\t2\t5\tV1.1_proposed\n"
)


SYNTH_THEMES = """\
schema_version: 1
brands:
  alpha_brand:
    topic_anchor: "Alpha topic"
    series:
      en_US:
        - {series_title: "Alpha One", arc_shape: "shape A1", emotional_throughline: "thru A1"}
        - {series_title: "Alpha Two", arc_shape: "shape A2", emotional_throughline: "thru A2"}
        - {series_title: "Alpha Three", arc_shape: "shape A3", emotional_throughline: "thru A3"}
      ja_JP:
        - {series_title: "アルファ1", arc_shape: "形a1", emotional_throughline: "通a1"}
        # Only 1 theme but series_count=2 → second row must fall back synthetically.
  beta_brand:
    topic_anchor: "Beta topic"
    series:
      en_US:
        - {series_title: "Beta E1", arc_shape: "shape B1", emotional_throughline: "thru B1"}
        - {series_title: "Beta E2", arc_shape: "shape B2", emotional_throughline: "thru B2"}
        - {series_title: "Beta E3", arc_shape: "shape B3", emotional_throughline: "thru B3"}
        - {series_title: "Beta E4", arc_shape: "shape B4", emotional_throughline: "thru B4"}
      ja_JP:
        - {series_title: "ベータ1", arc_shape: "形b1", emotional_throughline: "通b1"}
        - {series_title: "ベータ2", arc_shape: "形b2", emotional_throughline: "通b2"}
"""


@pytest.fixture()
def synthetic_inputs(tmp_path: Path) -> tuple[Path, Path]:
    alloc = tmp_path / "alloc.tsv"
    alloc.write_text(SYNTH_TSV, encoding="utf-8")
    themes = tmp_path / "themes.yaml"
    themes.write_text(SYNTH_THEMES, encoding="utf-8")
    return alloc, themes


def test_planned_book_count_matches_allocation_sum(synthetic_inputs):
    """sum(series_count) over ebook rows must equal the planned row count."""
    alloc, themes = synthetic_inputs
    rows = bbsi._load_v1_1_planned_books(allocation_path=alloc, themes_path=themes)
    # alpha_brand: 3+2 ; beta_brand: 4+2 ; gamma_no_themes: 2 → 13 total ebook rows
    assert len(rows) == 3 + 2 + 4 + 2 + 2 == 13


def test_manga_rows_are_excluded(synthetic_inputs):
    """The TSV contains a manga row; ebook-only filter must skip it."""
    alloc, themes = synthetic_inputs
    rows = bbsi._load_v1_1_planned_books(allocation_path=alloc, themes_path=themes)
    # All planned rows must be ebook surface
    assert all(r["surface"] == "ebook" for r in rows)
    assert all(r["format"] == "ebook" for r in rows)


def test_status_field_is_planned(synthetic_inputs):
    alloc, themes = synthetic_inputs
    rows = bbsi._load_v1_1_planned_books(allocation_path=alloc, themes_path=themes)
    assert rows
    assert all(r["status"] == "planned" for r in rows)
    assert all(r["book_cover_image_path"] is None for r in rows)
    assert all(r["book_cover_status"] == "planned" for r in rows)


def test_book_id_is_deterministic(synthetic_inputs):
    alloc, themes = synthetic_inputs
    rows1 = bbsi._load_v1_1_planned_books(allocation_path=alloc, themes_path=themes)
    rows2 = bbsi._load_v1_1_planned_books(allocation_path=alloc, themes_path=themes)
    ids1 = [r["book_id"] for r in rows1]
    ids2 = [r["book_id"] for r in rows2]
    assert ids1 == ids2
    # Format: <brand>__<locale>__<idx>
    assert "alpha_brand__en_US__01" in ids1
    assert "alpha_brand__en_US__03" in ids1
    assert "alpha_brand__ja_JP__02" in ids1
    # No duplicate book_ids within an allocation cell
    assert len(set(ids1)) == len(ids1)


def test_titles_populated_from_themes_when_available(synthetic_inputs):
    alloc, themes = synthetic_inputs
    rows = bbsi._load_v1_1_planned_books(allocation_path=alloc, themes_path=themes)
    by_id = {r["book_id"]: r for r in rows}
    assert by_id["alpha_brand__en_US__01"]["book_title"] == "Alpha One"
    assert by_id["alpha_brand__en_US__02"]["book_title"] == "Alpha Two"
    assert by_id["alpha_brand__en_US__03"]["book_title"] == "Alpha Three"
    # ja_JP only has 1 theme; second row falls back to synthetic title.
    assert by_id["alpha_brand__ja_JP__01"]["book_title"] == "アルファ1"
    assert "Series 2" in by_id["alpha_brand__ja_JP__02"]["book_title"]


def test_brand_with_no_themes_does_not_crash(synthetic_inputs):
    """gamma_no_themes has no themes entry; planned rows still emit cleanly."""
    alloc, themes = synthetic_inputs
    rows = bbsi._load_v1_1_planned_books(allocation_path=alloc, themes_path=themes)
    gamma = [r for r in rows if r["brand_id"] == "gamma_no_themes"]
    assert len(gamma) == 2
    for r in gamma:
        # Synthetic title must be human-readable, not a None / "x"
        assert r["book_title"]
        assert "Series" in r["book_title"]
        assert r["book_subtitle"] is None
        assert r["book_description"] is None
        # author_id is allowed to be None; planned rows must not block on this
        assert r["author_id"] is None
        assert r["status"] == "planned"
        # priority_phase carried through from TSV
        assert r["priority_phase"] == "V1.1_proposed"


def test_episode_per_series_count_is_carried_through(synthetic_inputs):
    alloc, themes = synthetic_inputs
    rows = bbsi._load_v1_1_planned_books(allocation_path=alloc, themes_path=themes)
    assert all(r["episode_per_series_count"] == 5 for r in rows)


def test_missing_allocation_path_returns_empty(tmp_path: Path):
    missing = tmp_path / "does_not_exist.tsv"
    themes = tmp_path / "themes.yaml"
    themes.write_text("schema_version: 1\nbrands: {}\n", encoding="utf-8")
    rows = bbsi._load_v1_1_planned_books(allocation_path=missing, themes_path=themes)
    assert rows == []


def test_missing_themes_path_still_emits_synthetic_titles(tmp_path: Path):
    alloc = tmp_path / "alloc.tsv"
    alloc.write_text(SYNTH_TSV, encoding="utf-8")
    missing_themes = tmp_path / "missing.yaml"
    rows = bbsi._load_v1_1_planned_books(allocation_path=alloc, themes_path=missing_themes)
    assert len(rows) == 13
    # All titles must be synthetic but populated
    assert all(r["book_title"] for r in rows)


def test_integration_with_repo_inputs_real():
    """Smoke test against the real repo inputs — should be hundreds of rows."""
    rows = bbsi._load_v1_1_planned_books()
    assert len(rows) >= 500, "Expected 700+ planned ebook rows from V1.1 TSV"
    locales = {r["locale"] for r in rows}
    assert {"en_US", "ja_JP", "zh_TW", "zh_CN"}.issubset(locales)
    # Every row has status=planned and no rendered cover
    assert all(r["status"] == "planned" for r in rows)
    assert all(r["book_cover_image_path"] is None for r in rows)


def test_build_book_series_index_merges_rendered_and_planned():
    """Full pipeline: index has both rendered and planned rows; rendered wins on collision."""
    out = bbsi.build_book_series_index()
    books = out["books"]
    stats = out["stats"]
    rendered = [b for b in books if b["status"] == "rendered"]
    planned = [b for b in books if b["status"] == "planned"]
    assert stats["rendered_books"] == len(rendered)
    assert stats["planned_books"] == len(planned)
    assert len(books) == len(rendered) + len(planned)
    # No book_id collision between rendered and planned (rendered wins)
    rendered_ids = {b["book_id"] for b in rendered}
    planned_ids = {b["book_id"] for b in planned}
    assert rendered_ids.isdisjoint(planned_ids)
    # Sanity: planned count must dominate (V1.1 expansion = ~740 vs 13 rendered)
    assert len(planned) > len(rendered) * 10


def test_build_book_series_index_writes_json(tmp_path: Path, monkeypatch):
    """Smoke test of the writer path."""
    out_path = tmp_path / "index.json"
    monkeypatch.setattr(bbsi, "INDEX_OUTPUT", out_path)
    rc = bbsi.main()
    assert rc == 0
    assert out_path.is_file()
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert "books" in payload
    assert "stats" in payload
    assert payload["schema_version"] == 2


def test_slug_helper_handles_punctuation():
    """The slug helper underpins synthetic ids — must be ascii-safe."""
    assert bbsi._slug("Hello, World!") == "hello_world"
    assert bbsi._slug("ja_JP") == "ja_jp"
    assert bbsi._slug("") == "x"
