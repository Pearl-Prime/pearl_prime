"""Tests for Waystream feed rebuild (proxy URL mode)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts/marketing/rebuild_waystream_feed_from_r2.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("rebuild_waystream_feed_from_r2", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_proxy_url_relative():
    mod = _load_module()
    url = mod._proxy_url("way_stream_sanctuary__x__y", "2026-W26", "")
    assert url == "/download/way_stream_sanctuary__x__y?week=2026-W26"
    assert mod._proxy_url_ok(url)


def test_build_feed_proxy_mode(tmp_path):
    mod = _load_module()
    manifest = {
        "brand": "way_stream_sanctuary",
        "bucket": "phoenix-omega-artifacts",
        "objects": [
            {
                "book_id": "way_stream_sanctuary__a__b",
                "week": "2026-W26",
                "platform": "amazon_kdp",
                "file": "way_stream_sanctuary__a__b.epub",
                "key": "brand/way_stream_sanctuary/deliveries/2026-W26/amazon_kdp/way_stream_sanctuary__a__b.epub",
                "size": 1024,
            }
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    feed, rows = mod.build_feed(
        manifest_path,
        existing={},
        refresh_presign=False,
        presigned_ttl=604_800,
        use_proxy=True,
        proxy_base="",
    )
    assert len(rows) == 1
    entry = feed["weeks"]["2026-W26"]["amazon_kdp"][0]
    assert entry["url"].startswith("/download/")
    assert "week=2026-W26" in entry["url"]
    assert mod._proxy_url_ok(entry["url"])
