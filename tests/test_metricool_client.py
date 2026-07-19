"""Offline unit tests for Metricool transport — no network."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "integrations" / "metricool"))

from client import (  # noqa: E402
    MetricoolAPIError,
    MetricoolConfigError,
    call_metricool_api,
    schedule_post,
)
import post as metricool_post  # noqa: E402

FIXTURE = REPO / "tests" / "fixtures" / "metricool" / "sample_asset.json"


def _ok_response(payload: dict | list, status: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = payload
    resp.text = json.dumps(payload)
    return resp


def test_schedule_post_payload_passthrough():
    captured = {}

    def fake_post(url, json=None, headers=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        return _ok_response({"data": {"id": 99, "draft": True}})

    payload = {
        "media": ["https://example.com/a.jpg"],
        "publicationDate": {"dateTime": "2026-07-22T09:00:00", "timezone": "America/New_York"},
        "providers": [{"network": "tiktok"}],
        "text": "hello",
        "draft": True,
        "autoPublish": False,
    }
    with patch("client.requests.post", side_effect=fake_post):
        with patch("client.time.sleep"):
            out = schedule_post(
                payload,
                user_id="3564167",
                blog_id="12345",
                api_key="test-key",
            )
    assert out["data"]["id"] == 99
    assert captured["json"] == payload
    assert captured["headers"]["X-Mc-Auth"] == "test-key"
    assert "blogId=12345" in captured["url"]
    assert "userId=3564167" in captured["url"]
    assert captured["url"].startswith("https://app.metricool.com/api/v2/scheduler/posts")


def test_retry_on_5xx_then_success():
    calls = {"n": 0}

    def flaky(url, json=None, headers=None, timeout=None):
        calls["n"] += 1
        if calls["n"] < 3:
            resp = MagicMock()
            resp.status_code = 503
            resp.text = "unavailable"
            resp.json.side_effect = ValueError("no json")
            return resp
        return _ok_response({"ok": True})

    with patch("client.requests.post", side_effect=flaky):
        with patch("client.time.sleep") as sleep_mock:
            out = call_metricool_api(
                "scheduler/posts",
                "POST",
                {"media": [], "publicationDate": {}, "providers": []},
                user_id="1",
                blog_id="2",
                api_key="k",
            )
    assert out == {"ok": True}
    assert calls["n"] == 3
    assert sleep_mock.call_count == 2
    assert [c.args[0] for c in sleep_mock.call_args_list] == [2, 4]


def test_no_retry_on_4xx():
    calls = {"n": 0}

    def client_err(url, json=None, headers=None, timeout=None):
        calls["n"] += 1
        resp = MagicMock()
        resp.status_code = 401
        resp.text = "unauthorized"
        resp.json.return_value = {"message": "bad auth"}
        return resp

    with patch("client.requests.post", side_effect=client_err):
        with patch("client.time.sleep") as sleep_mock:
            with pytest.raises(MetricoolAPIError, match="401"):
                call_metricool_api(
                    "scheduler/posts",
                    "POST",
                    {"media": [], "publicationDate": {}, "providers": []},
                    user_id="1",
                    blog_id="2",
                    api_key="k",
                )
    assert calls["n"] == 1
    sleep_mock.assert_not_called()


def test_pinterest_uses_brand_id_not_blog_id():
    captured = {}

    def fake_get(url, headers=None, timeout=None):
        captured["url"] = url
        return _ok_response([])

    with patch("client.requests.get", side_effect=fake_get):
        with patch("client.time.sleep"):
            call_metricool_api(
                "scheduler/boards/pinterest",
                "GET",
                None,
                user_id="1",
                blog_id="99",
                api_key="k",
            )
    assert "brandId=99" in captured["url"]
    assert "blogId=" not in captured["url"]


def test_non_pinterest_uses_blog_id():
    captured = {}

    def fake_get(url, headers=None, timeout=None):
        captured["url"] = url
        return _ok_response({"data": {}})

    with patch("client.requests.get", side_effect=fake_get):
        with patch("client.time.sleep"):
            call_metricool_api(
                "settings/brands/99",
                "GET",
                None,
                user_id="1",
                blog_id="99",
                api_key="k",
            )
    assert "blogId=99" in captured["url"]
    assert "brandId=" not in captured["url"]


def test_unwired_brand_refusal(tmp_path: Path, capsys):
    brands_map = {
        "account": "waystream",
        "user_id_env": "METRICOOL_USER_ID",
        "brands": {
            "stillness_press": {"blog_id": None, "status": "unwired"},
        },
    }
    map_path = tmp_path / "metricool_brands.yaml"
    map_path.write_text(yaml.safe_dump(brands_map), encoding="utf-8")
    rc = metricool_post.main(
        [
            "--brand",
            "stillness_press",
            "--asset",
            str(FIXTURE),
            "--draft",
            "--dry-run",
            "--brands-map",
            str(map_path),
        ]
    )
    assert rc == 2
    assert "unwired" in capsys.readouterr().err.lower()


def test_live_gate_without_approval(tmp_path: Path, capsys):
    brands_map = {
        "account": "waystream",
        "user_id_env": "METRICOOL_USER_ID",
        "brands": {
            "waystream_sanctuary": {
                "blog_id": "99999",
                "status": "wired",
                "timezone": "America/New_York",
            },
        },
    }
    map_path = tmp_path / "metricool_brands.yaml"
    map_path.write_text(yaml.safe_dump(brands_map), encoding="utf-8")

    # Missing --i-understand-live
    rc = metricool_post.main(
        [
            "--brand",
            "waystream_sanctuary",
            "--asset",
            str(FIXTURE),
            "--live",
            "--brands-map",
            str(map_path),
        ]
    )
    assert rc == 2
    err = capsys.readouterr().err
    assert "--i-understand-live" in err

    # Flag present but Q-METRIC-01 not ratified
    assert metricool_post.LIVE_PUBLISH_OPERATOR_APPROVED is False
    rc2 = metricool_post.main(
        [
            "--brand",
            "waystream_sanctuary",
            "--asset",
            str(FIXTURE),
            "--live",
            "--i-understand-live",
            "--brands-map",
            str(map_path),
        ]
    )
    assert rc2 == 2
    err2 = capsys.readouterr().err
    assert "Q-METRIC-01" in err2


def test_dry_run_waystream_placeholder_ok(tmp_path: Path, capsys):
    brands_map = {
        "account": "waystream",
        "user_id_env": "METRICOOL_USER_ID",
        "brands": {
            "waystream_sanctuary": {
                "blog_id": "WAYSTREAM_BLOG_ID_PENDING",
                "status": "wired",
                "timezone": "America/New_York",
            },
        },
    }
    map_path = tmp_path / "metricool_brands.yaml"
    map_path.write_text(yaml.safe_dump(brands_map), encoding="utf-8")
    rc = metricool_post.main(
        [
            "--brand",
            "waystream_sanctuary",
            "--asset",
            str(FIXTURE),
            "--draft",
            "--dry-run",
            "--brands-map",
            str(map_path),
        ]
    )
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["dry_run"] is True
    assert out["api_payload"]["draft"] is True
    assert out["api_payload"]["autoPublish"] is False
    assert out["api_payload"]["providers"] == [{"network": "tiktok"}]


def test_placeholder_blocks_nondry_run(tmp_path: Path, capsys):
    brands_map = {
        "account": "waystream",
        "user_id_env": "METRICOOL_USER_ID",
        "brands": {
            "waystream_sanctuary": {
                "blog_id": "WAYSTREAM_BLOG_ID_PENDING",
                "status": "wired",
                "timezone": "America/New_York",
            },
        },
    }
    map_path = tmp_path / "metricool_brands.yaml"
    map_path.write_text(yaml.safe_dump(brands_map), encoding="utf-8")
    rc = metricool_post.main(
        [
            "--brand",
            "waystream_sanctuary",
            "--asset",
            str(FIXTURE),
            "--draft",
            "--brands-map",
            str(map_path),
        ]
    )
    assert rc == 2
    assert "Q-METRIC-02" in capsys.readouterr().err
