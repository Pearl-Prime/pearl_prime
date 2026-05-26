"""
Tests for server/routes/brand_admin_public.py — the live-registry endpoints the
operations dashboard at brand-wizard-app/public/brand_admin.html consumes.

These tests are direct router-function calls (no test client / no server start)
so they run anywhere pytest is available. They assert schema shape, not exact
counts (counts shift as registries grow). Read-only — no fixtures write to repo.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Make repo root importable when pytest is invoked from anywhere in the tree.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402

from server.routes import brand_admin_public  # noqa: E402


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro) if not hasattr(asyncio, "run") else asyncio.run(coro)


def test_brand_index_returns_three_axes_with_expected_keys():
    out = _run(brand_admin_public.brand_index())
    assert set(out.keys()) >= {"book", "manga", "music", "counts", "sources", "axes_note"}
    assert isinstance(out["book"], list)
    assert isinstance(out["manga"], list)
    assert isinstance(out["music"], list)
    assert set(out["counts"].keys()) == {"book", "manga", "music", "total"}
    assert out["counts"]["total"] == out["counts"]["book"] + out["counts"]["manga"] + out["counts"]["music"]


def test_brand_index_surfaces_more_than_legacy_24_brands():
    """The whole point of this endpoint is to surpass the prior hardcoded 24."""
    out = _run(brand_admin_public.brand_index())
    assert out["counts"]["total"] > 24, f"Only {out['counts']['total']} brands; should be 60+"


def test_brand_index_manga_axis_has_path_x_canon_count():
    """Per BR-CANON-01 Path X, manga axis canon is 37 brands."""
    out = _run(brand_admin_public.brand_index())
    assert out["counts"]["manga"] == 37, f"Manga count {out['counts']['manga']} != 37 (Path X canon)"


def test_brand_index_each_row_has_axis_and_brand_id():
    out = _run(brand_admin_public.brand_index())
    for axis in ("book", "manga", "music"):
        for row in out[axis]:
            assert row.get("brand_id"), f"{axis} row missing brand_id: {row}"
            assert row.get("axis") == axis, f"{axis} row axis mismatch: {row}"


def test_books_by_platform_manga_brand_returns_topic_rows():
    """For a manga brand, primary_topic + secondary_topics map to store_url_tracker."""
    out = _run(brand_admin_public.books_by_platform("stillness_press"))
    assert out["brand_id"] == "stillness_press"
    assert out["axis"] in ("manga", "book")  # exists on both axes per Path X
    assert "books" in out
    assert "platforms_header" in out
    assert set(out["platforms_header"]) <= {"kdp", "apple_books", "google_play", "kobo", "store_url_live"}


def test_books_by_platform_unknown_brand_returns_404():
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        _run(brand_admin_public.books_by_platform("this_brand_does_not_exist_anywhere"))
    assert exc.value.status_code == 404


def test_books_by_platform_rejects_path_traversal():
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        _run(brand_admin_public.books_by_platform("../etc/passwd"))
    assert exc.value.status_code == 400


def test_brand_index_book_brand_carries_locale():
    """Book-axis rows should expose locale (e.g. en_US, zh_TW) from brand_registry.yaml."""
    out = _run(brand_admin_public.brand_index())
    book_rows = out["book"]
    assert any(r.get("locale") for r in book_rows), "no book row has a locale"
