"""Tests for per-platform brand admin download (OPD-145 split-at-build)."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from server.brand_admin_platform import platform_zip_path  # noqa: E402
from server.routes import brand_admin_download, brand_admin_public  # noqa: E402

PACKAGES = ROOT / "artifacts" / "weekly_packages"
BRAND = "stillness_press"
WEEK = "2026-W22"


def _run(coro):
    return asyncio.run(coro)


def test_weekly_platform_rows_have_platform_query():
    out = _run(brand_admin_public.brand_weekly(BRAND, week=WEEK))
    kdp = next(r for r in out["platform_rows"] if r["platform"] == "Amazon KDP")
    if kdp["download_url"]:
        assert "?platform=kdp" in kdp["download_url"]
        assert kdp["platform_id"] == "kdp"
        assert kdp["deemphasized"] is False


def test_download_monolithic_without_platform():
    out = _run(brand_admin_download.download_admin_packet(BRAND, WEEK, platform=None))
    assert out.filename == f"{BRAND}_{WEEK}.zip"


@pytest.mark.skipif(
    not platform_zip_path(PACKAGES, BRAND, WEEK, "kdp").is_file(),
    reason="per-platform stub ZIP not seeded",
)
def test_download_per_platform_kdp():
    out = _run(brand_admin_download.download_admin_packet(BRAND, WEEK, platform="kdp"))
    assert out.filename == f"{BRAND}_{WEEK}_kdp.zip"


def test_download_invalid_platform_400():
    with pytest.raises(HTTPException) as exc:
        _run(brand_admin_download.download_admin_packet(BRAND, WEEK, platform="not_a_platform"))
    assert exc.value.status_code == 400


def test_download_path_traversal_platform_400():
    with pytest.raises(HTTPException) as exc:
        _run(brand_admin_download.download_admin_packet(BRAND, WEEK, platform="../etc"))
    assert exc.value.status_code == 400


def test_weekly_webtoon_and_podcast_platform_ids():
    out = _run(brand_admin_public.brand_weekly(BRAND, week=WEEK))
    web = next(r for r in out["platform_rows"] if r["platform"] == "WEBTOON")
    pod = next(r for r in out["platform_rows"] if r["platform"] == "Spotify Podcast")
    assert web.get("platform_id") == "webtoon"
    assert pod.get("platform_id") == "spotify_podcast"
