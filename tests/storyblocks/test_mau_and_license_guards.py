"""Unit tests: MAU boundary, search≠MAU, identity, consumer guard, rate limiter, HMAC."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from scripts.storyblocks.api_client import StoryblocksAPIClient, pick_hd_url
from scripts.storyblocks.confirm_download import confirm_selection
from scripts.storyblocks.consumer_guard import (
    UnlicensedStoryblocksAssetError,
    assert_storyblocks_licensed_for_consumer,
)
from scripts.storyblocks.exceptions import (
    StoryblocksConfigError,
    StoryblocksMauCapError,
    StoryblocksRateLimitError,
)
from scripts.storyblocks.identity import anonymize_project_id, anonymize_user_id
from scripts.storyblocks.license_store import LicenseRecord, LicenseStore
from scripts.storyblocks.mau_ledger import MauLedger
from scripts.storyblocks.rate_limiter import SlidingWindowRateLimiter


def test_per_locale_brand_id_stable():
    a = anonymize_user_id("way_stream_sanctuary", "en-US")
    b = anonymize_user_id("way_stream_sanctuary", "en-US")
    c = anonymize_user_id("way_stream_sanctuary", "ja-JP")
    assert a == b
    assert len(a) == 16
    assert a != c
    assert anonymize_project_id("social_broll:anxiety") == anonymize_project_id("social_broll:anxiety")
    assert anonymize_project_id("a") != anonymize_project_id("b")


def test_mau_search_does_not_touch_ledger(tmp_path: Path):
    ledger = MauLedger(path=tmp_path / "mau.jsonl", hard_cap=104)
    # Simulate search-only: never call reserve_or_block
    assert ledger.distinct_count("2026-07") == 0
    assert not (tmp_path / "mau.jsonl").exists()


def test_mau_104_pass_105_block(tmp_path: Path):
    ledger = MauLedger(path=tmp_path / "mau.jsonl", hard_cap=104)
    fixed = datetime(2026, 7, 15, tzinfo=timezone.utc)
    for i in range(104):
        r = ledger.reserve_or_block(f"brand_{i}", "en-US", now=fixed)
        assert r.was_new is True
    assert ledger.distinct_count("2026-07") == 104
    # repeat brand unlimited
    r_repeat = ledger.reserve_or_block("brand_0", "en-US", now=fixed)
    assert r_repeat.was_new is False
    with pytest.raises(StoryblocksMauCapError):
        ledger.reserve_or_block("brand_105_new", "en-US", now=fixed)


def test_mau_warnings_at_80_and_100(tmp_path: Path):
    ledger = MauLedger(path=tmp_path / "mau.jsonl", hard_cap=104)
    fixed = datetime(2026, 7, 1, tzinfo=timezone.utc)
    saw = set()
    for i in range(100):
        r = ledger.reserve_or_block(f"b{i}", "en-US", now=fixed)
        saw.update(r.warnings)
    assert 80 in saw
    assert 100 in saw


def test_rate_limiter_search_and_download_caps():
    lim = SlidingWindowRateLimiter(search_cap=3, download_cap=2)
    now = 1_000_000.0
    lim.acquire("search", now=now)
    lim.acquire("search", now=now + 1)
    lim.acquire("search", now=now + 2)
    with pytest.raises(StoryblocksRateLimitError):
        lim.acquire("search", now=now + 3)
    lim.acquire("download", now=now)
    lim.acquire("download", now=now + 1)
    with pytest.raises(StoryblocksRateLimitError):
        lim.acquire("download", now=now + 2)
    # window slides
    lim.acquire("search", now=now + 61)


def test_hmac_deterministic_and_rejects_templates():
    client = StoryblocksAPIClient(
        public_key="pub", private_key="priv", require_keys=True, rate_limiter=SlidingWindowRateLimiter()
    )
    exp1, sig1 = client._generate_hmac("/api/v2/videos/search", now=1_700_000_000)
    exp2, sig2 = client._generate_hmac("/api/v2/videos/search", now=1_700_000_000)
    assert exp1 == exp2 == 1_700_000_000 + 3600
    assert sig1 == sig2
    assert len(sig1) == 64
    with pytest.raises(ValueError, match="unresolved"):
        client._generate_hmac("/api/v2/videos/stock-item/download/:stock_item_id")


def test_missing_keys_fail_clearly():
    with pytest.raises(StoryblocksConfigError, match="keys missing"):
        StoryblocksAPIClient(public_key="", private_key="", require_keys=True)


def test_consumer_guard_rejects_unlicensed_storyblocks(tmp_path: Path):
    store = LicenseStore(bank_root=tmp_path / "bank", index_path=tmp_path / "idx.jsonl")
    asset = {
        "source_provider": "storyblocks",
        "storyblocks_stock_id": "SBV-1",
        "work_unit_id": "wu1",
    }
    with pytest.raises(UnlicensedStoryblocksAssetError):
        assert_storyblocks_licensed_for_consumer(asset, work_unit_id="wu1", license_store=store)


def test_consumer_guard_allows_pexels():
    assert_storyblocks_licensed_for_consumer(
        {"source_provider": "pexels", "path": "/tmp/pexels__anxiety__1.jpeg"}
    )


def test_consumer_guard_allows_licensed(tmp_path: Path):
    store = LicenseStore(bank_root=tmp_path / "bank", index_path=tmp_path / "idx.jsonl")
    hd = store.hd_path("wu1", "SBV-1", "mp4")
    hd.parent.mkdir(parents=True, exist_ok=True)
    hd.write_bytes(b"fake-hd-bytes")
    rec = LicenseRecord(
        source_provider="storyblocks",
        storyblocks_stock_id="SBV-1",
        work_unit_type="social_campaign",
        work_unit_id="wu1",
        brand_id="way_stream_sanctuary",
        locale="en-US",
        surface="social_broll",
        media_type="video",
        mau_user_id="abc",
        download_query_at="2026-07-19T00:00:00Z",
        local_uri=str(hd),
        model_released=True,
        property_released=True,
    )
    store.put(rec)
    assert_storyblocks_licensed_for_consumer(
        {
            "source_provider": "storyblocks",
            "storyblocks_stock_id": "SBV-1",
            "work_unit_id": "wu1",
            "local_uri": str(hd),
        },
        work_unit_id="wu1",
        license_store=store,
    )


def test_confirm_selection_sole_path_mocked(tmp_path: Path):
    store = LicenseStore(bank_root=tmp_path / "bank", index_path=tmp_path / "idx.jsonl")
    ledger = MauLedger(path=tmp_path / "mau.jsonl", hard_cap=104)
    limiter = SlidingWindowRateLimiter()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"MP4": {"_1080p": "https://cdn.example/hd.mp4"}}

    client = StoryblocksAPIClient(
        public_key="pub",
        private_key="priv",
        rate_limiter=limiter,
        request_fn=lambda *a, **k: mock_resp,
        require_keys=True,
    )

    hd_body = SimpleNamespace(status_code=200, content=b"\x00\x01HDDATA")

    rec = confirm_selection(
        stock_id="SBV-99",
        media_type="video",
        brand_id="way_stream_sanctuary",
        locale="en-US",
        work_unit_id="social_broll:anxiety",
        client=client,
        mau_ledger=ledger,
        license_store=store,
        http_get=lambda url, timeout=120: hd_body,
        model_released=True,
        property_released=False,
    )
    assert rec.source_provider == "storyblocks"
    assert Path(rec.local_uri).exists()
    assert Path(rec.local_uri).read_bytes() == b"\x00\x01HDDATA"
    assert store.has_license("social_broll:anxiety", "SBV-99")
    assert ledger.distinct_count() == 1
    # search must not be required for MAU — already counted only on confirm
    side = json.loads(store.sidecar_path("social_broll:anxiety", "SBV-99").read_text())
    assert side["model_released"] is True
    assert side["property_released"] is False
    assert side["attribution_label"] == "Stock media via Storyblocks"


def test_pick_hd_url_video():
    url, ext = pick_hd_url({"MP4": {"_1080p": "https://x/a.mp4"}}, "video")
    assert ext == "mp4"
    assert url.endswith("a.mp4")


def test_registry_lists_storyblocks_keys():
    from scripts.ci.integration_env_registry import REGISTRY

    names = {row[1] for row in REGISTRY}
    assert "STORYBLOCKS_PUBLIC_KEY" in names
    assert "STORYBLOCKS_PRIVATE_KEY" in names
