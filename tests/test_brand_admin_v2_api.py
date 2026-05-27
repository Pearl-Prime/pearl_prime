"""Tests for server/routes/brand_admin_public.py (brand index + v2 weekly-work)."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from server.routes import brand_admin_public  # noqa: E402


def _run(coro):
    return asyncio.run(coro)


def test_brand_index_manga_count_is_37():
    out = _run(brand_admin_public.brand_index())
    assert out["counts"]["manga"] == 37


def test_planned_volumes_shape():
    out = _run(brand_admin_public.planned_volumes("stillness_press"))
    assert out["brand_id"] == "stillness_press"
    assert "planned" in out
    assert "summary_line" in out
    assert "gaps" in out
    assert isinstance(out["locales_active"], list)
    assert out["planned"]["ebooks"] is not None
    assert out["planned"]["manga_series"] is not None
    assert out["planned"]["podcast"] is not None
    assert out["planned"]["audiobook"] is not None
    assert out["gaps"] == []
    assert "ebooks/yr" in out["summary_line"]
    assert "podcasts/yr" in out["summary_line"]
    assert "audiobooks/yr" in out["summary_line"]


def test_planned_volumes_canon_brand_without_legacy_series_plan_key():
    """Canonical-only brand IDs must resolve via manga_canon_planned_volumes.yaml."""
    out = _run(brand_admin_public.planned_volumes("adhd_forge_mystery"))
    assert out["planned"]["podcast"] is not None
    assert out["planned"]["audiobook"] is not None
    assert out["gaps"] == []


def test_planned_volumes_unknown_404():
    with pytest.raises(HTTPException) as exc:
        _run(brand_admin_public.planned_volumes("brand_that_does_not_exist_xyz"))
    assert exc.value.status_code == 404


def test_weekly_defaults_to_iso_week():
    out = _run(brand_admin_public.brand_weekly("stillness_press"))
    assert out["brand_id"] == "stillness_press"
    assert "-W" in out["week"]
    assert "platform_rows" in out
    assert "deliverables" in out
    assert isinstance(out["history_weeks"], list)


def test_weekly_invalid_week_400():
    with pytest.raises(HTTPException) as exc:
        _run(brand_admin_public.brand_weekly("stillness_press", week="2026-W99"))
    assert exc.value.status_code == 400


def test_weekly_path_traversal_400():
    with pytest.raises(HTTPException) as exc:
        _run(brand_admin_public.brand_weekly("stillness_press", week="../etc/passwd"))
    assert exc.value.status_code == 400


def test_history_weeks_max_12():
    out = _run(brand_admin_public.brand_weekly("stillness_press"))
    assert len(out["history_weeks"]) <= 12


def test_platform_rows_map_books_to_stores():
    out = _run(brand_admin_public.brand_weekly("stillness_press", week="2026-W22"))
    rows = out["platform_rows"]
    kdp = next(r for r in rows if r["platform"] == "Amazon KDP")
    assert kdp["from_deliverable"] == "books"
    assert kdp.get("platform_id") == "kdp"
    web = next(r for r in rows if r["platform"] == "WEBTOON")
    assert web["from_deliverable"] == "manga_panels"
    if kdp.get("download_url"):
        assert "?platform=kdp" in kdp["download_url"]


def test_books_by_platform_stillness_press():
    out = _run(brand_admin_public.books_by_platform("stillness_press"))
    assert out["brand_id"] == "stillness_press"
    assert "books" in out
