"""Lane 04 — Storyblocks Audio search/confirm/MAU + mood query map + bed resolve."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import yaml

from scripts.storyblocks.api_client import StoryblocksAPIClient, pick_hd_url
from scripts.storyblocks.confirm_download import confirm_selection
from scripts.storyblocks.license_store import LicenseStore
from scripts.storyblocks.mau_ledger import MauLedger
from scripts.storyblocks.mood_audio import (
    MOOD_REGISTERS,
    load_mood_audio_query_map,
    query_params_for_mood,
    resolve_licensed_audio_bed,
    search_audio_for_mood,
)
from scripts.storyblocks.rate_limiter import SlidingWindowRateLimiter

REPO = Path(__file__).resolve().parents[2]
QUERY_MAP = REPO / "config" / "social" / "mood_register_audio_query_map.yaml"


def test_mood_register_audio_query_map_has_four_clusters():
    data = yaml.safe_load(QUERY_MAP.read_text(encoding="utf-8"))
    clusters = data["mood_register_audio"]
    assert set(clusters) == set(MOOD_REGISTERS)
    for mood in MOOD_REGISTERS:
        params = query_params_for_mood(mood, map_data=data)
        assert params["content_type"] == "music"
        assert params["has_vocals"] == "false"
        assert "keywords" in params and params["keywords"]


def test_search_audio_does_not_touch_mau(tmp_path: Path):
    ledger = MauLedger(path=tmp_path / "mau.jsonl", hard_cap=104)
    calls: list[tuple] = []

    def request_fn(method, url, params=None, timeout=30):
        calls.append((method, url, dict(params or {})))
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"results": [{"id": "SBA-1", "title": "Tense Pulse"}]}
        return resp

    client = StoryblocksAPIClient(
        public_key="pub",
        private_key="priv",
        rate_limiter=SlidingWindowRateLimiter(),
        request_fn=request_fn,
        require_keys=True,
    )
    payload = search_audio_for_mood(
        client,
        "tense_anxious",
        brand_id="way_stream_sanctuary",
        locale="en-US",
        work_unit_id="social_audio:anxiety",
        map_data=load_mood_audio_query_map(QUERY_MAP),
    )
    assert payload["results"][0]["id"] == "SBA-1"
    assert "/api/v2/audio/search" in calls[0][1]
    assert ledger.distinct_count() == 0
    assert not (tmp_path / "mau.jsonl").exists()
    assert "min_bpm" in calls[0][2]
    assert calls[0][2]["has_vocals"] == "false"


def test_pick_hd_url_audio():
    url, ext = pick_hd_url({"WAV": {"_max": "https://x/a.wav"}}, "audio")
    assert ext == "wav"
    assert url.endswith("a.wav")
    url2, ext2 = pick_hd_url({"MP3": "https://x/b.mp3"}, "audio")
    assert ext2 == "mp3"


def test_confirm_selection_audio_nests_under_audio_and_meters_mau(tmp_path: Path):
    store = LicenseStore(bank_root=tmp_path / "bank", index_path=tmp_path / "idx.jsonl")
    ledger = MauLedger(path=tmp_path / "mau.jsonl", hard_cap=104)
    limiter = SlidingWindowRateLimiter()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"WAV": {"_max": "https://cdn.example/bed.wav"}}

    client = StoryblocksAPIClient(
        public_key="pub",
        private_key="priv",
        rate_limiter=limiter,
        request_fn=lambda *a, **k: mock_resp,
        require_keys=True,
    )
    hd_body = SimpleNamespace(status_code=200, content=b"RIFFFAKEWAV")

    rec = confirm_selection(
        stock_id="SBA-42",
        media_type="audio",
        brand_id="way_stream_sanctuary",
        locale="en-US",
        work_unit_id="social_audio:anxiety",
        surface="social_broll",
        client=client,
        mau_ledger=ledger,
        license_store=store,
        http_get=lambda url, timeout=120: hd_body,
        metadata={"mood_register": "tense_anxious", "pro": None, "publisher": None},
    )
    assert rec.media_type == "audio"
    assert "/audio/" in rec.local_uri.replace("\\", "/")
    assert Path(rec.local_uri).read_bytes() == b"RIFFFAKEWAV"
    assert store.has_license("social_audio:anxiety", "SBA-42")
    assert ledger.distinct_count() == 1
    side = json.loads(
        store.sidecar_path("social_audio:anxiety", "SBA-42", media_type="audio").read_text()
    )
    assert side["metadata"]["mood_register"] == "tense_anxious"


def test_resolve_licensed_audio_bed_prefers_mood_tag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    store = LicenseStore(bank_root=tmp_path / "bank", index_path=tmp_path / "idx.jsonl")
    wu = "social_audio:pilot"
    audio_dir = store.work_unit_dir(wu) / "audio"
    audio_dir.mkdir(parents=True)
    path_a = audio_dir / "SBA-A.wav"
    path_b = audio_dir / "SBA-B.wav"
    path_a.write_bytes(b"A")
    path_b.write_bytes(b"B")
    store.put(
        __import__("scripts.storyblocks.license_store", fromlist=["LicenseRecord"]).LicenseRecord(
            source_provider="storyblocks",
            storyblocks_stock_id="SBA-A",
            work_unit_type="social_campaign",
            work_unit_id=wu,
            brand_id="way_stream_sanctuary",
            locale="en-US",
            surface="social_broll",
            media_type="audio",
            mau_user_id="x",
            download_query_at="2026-07-20T00:00:00Z",
            local_uri=str(path_a),
            metadata={"mood_register": "heavy_low"},
        )
    )
    store.put(
        __import__("scripts.storyblocks.license_store", fromlist=["LicenseRecord"]).LicenseRecord(
            source_provider="storyblocks",
            storyblocks_stock_id="SBA-B",
            work_unit_type="social_campaign",
            work_unit_id=wu,
            brand_id="way_stream_sanctuary",
            locale="en-US",
            surface="social_broll",
            media_type="audio",
            mau_user_id="x",
            download_query_at="2026-07-20T00:00:00Z",
            local_uri=str(path_b),
            metadata={"mood_register": "tense_anxious"},
        )
    )
    monkeypatch.delenv("STORYBLOCKS_AUDIO_BED_PATH", raising=False)
    hit = resolve_licensed_audio_bed("tense_anxious", wu, license_store=store)
    assert hit == path_b
    miss = resolve_licensed_audio_bed("empowering_courage", "no-such-wu", license_store=store)
    assert miss is None


def test_build_snippet_bed_keeps_sine_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Without licensed audio, sine bed path still runs (mocked ffmpeg)."""
    import scripts.social.build_video_snippet_bank as snip

    calls: list[list[str]] = []

    def fake_run(cmd: list[str]):
        calls.append(cmd)
        out = Path(cmd[-1])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"FAKEWAV")
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(snip, "run", fake_run)
    out = tmp_path / "bed.wav"
    snip.build_snippet_bed(out, 2.0, "tense_anxious", licensed_audio=None)
    assert out.exists()
    assert any("sine=frequency=" in " ".join(c) for c in calls)

    licensed = tmp_path / "licensed.wav"
    licensed.write_bytes(b"LIC")
    out2 = tmp_path / "bed2.wav"
    snip.build_snippet_bed(out2, 2.0, "tense_anxious", licensed_audio=licensed)
    assert out2.exists()
    assert any(str(licensed) in " ".join(c) for c in calls)
