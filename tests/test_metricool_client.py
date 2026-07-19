"""Offline unit tests for Metricool transport + managed-system layer — no network."""

from __future__ import annotations

import json
import re
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
    list_scheduler_posts,
    schedule_post,
)
import post as metricool_post  # noqa: E402
import pilot_preflight  # noqa: E402
import validate_config  # noqa: E402
import sync_brands_from_registry as sync_brands  # noqa: E402
import status as metricool_status  # noqa: E402
from brand_keys import collect_canonical_brand_keys  # noqa: E402

FIXTURE = REPO / "tests" / "fixtures" / "metricool" / "sample_asset.json"
METRICOOL_SCRIPTS = REPO / "scripts" / "integrations" / "metricool"
BRANDS_YAML = REPO / "config" / "integrations" / "metricool_brands.yaml"

# Key-shaped literals (API keys / long hex secrets) — must not appear in managed files.
_KEY_SHAPED = re.compile(
    r"(?i)("
    r"sk-[A-Za-z0-9_\-]{20,}"
    r"|['\"][A-Fa-f0-9]{32,}['\"]"
    r"|api[_-]?key\s*[:=]\s*['\"][^'\"]{16,}['\"]"
    r"|x-mc-auth\s*[:=]\s*['\"][^'\"]{16,}['\"]"
    r")"
)


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


def test_list_scheduler_posts_get():
    captured = {}

    def fake_get(url, headers=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        return _ok_response({"data": [{"id": 1}]})

    with patch("client.requests.get", side_effect=fake_get):
        with patch("client.time.sleep"):
            out = list_scheduler_posts(
                user_id="3564167",
                blog_id="12345",
                api_key="test-key",
                start="2026-07-20T00:00:00",
                end="2026-07-25T00:00:00",
                timezone="America/New_York",
            )
    assert out == {"data": [{"id": 1}]}
    assert captured["url"].startswith("https://app.metricool.com/api/v2/scheduler/posts")
    assert "blogId=12345" in captured["url"]
    assert "userId=3564167" in captured["url"]
    assert "start=2026-07-20T00:00:00" in captured["url"]
    assert "end=2026-07-25T00:00:00" in captured["url"]
    assert captured["headers"]["X-Mc-Auth"] == "test-key"


def test_list_scheduler_posts_by_id():
    captured = {}

    def fake_get(url, headers=None, timeout=None):
        captured["url"] = url
        return _ok_response({"data": {"id": 99, "draft": True}})

    with patch("client.requests.get", side_effect=fake_get):
        with patch("client.time.sleep"):
            out = list_scheduler_posts(
                user_id="3564167",
                blog_id="12345",
                api_key="test-key",
                post_id="99",
            )
    assert out["data"]["id"] == 99
    assert "scheduler/posts/99?" in captured["url"]


def test_pilot_preflight_blocked_placeholder(tmp_path: Path, monkeypatch, capsys):
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
    monkeypatch.delenv("METRICOOL_API_KEY", raising=False)
    monkeypatch.delenv("METRICOOL_USER_ID", raising=False)
    rc = pilot_preflight.main(["--brand", "waystream_sanctuary", "--brands-map", str(map_path)])
    assert rc == 2
    err_out = capsys.readouterr().out
    assert "PRIMARY_BLOCKER=Q-METRIC-CREDS" in err_out
    assert "Q-METRIC-02" in err_out


def test_pilot_preflight_ready(tmp_path: Path, monkeypatch, capsys):
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
    monkeypatch.setenv("METRICOOL_API_KEY", "test-key")
    monkeypatch.setenv("METRICOOL_USER_ID", "3564167")
    rc = pilot_preflight.main(
        ["--brand", "waystream_sanctuary", "--brands-map", str(map_path), "--json"]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ready_for_draft_pilot"] is True
    assert payload["primary_blocker"] is None
    assert payload["checks"]["METRICOOL_API_KEY"] == "set"
    assert payload["checks"]["METRICOOL_USER_ID"] == "3564167"


def test_network_kill_switch_blocks_http(tmp_path: Path, monkeypatch, capsys):
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
    monkeypatch.delenv("METRICOOL_ALLOW_NETWORK", raising=False)
    monkeypatch.setenv("METRICOOL_API_KEY", "test-key")
    monkeypatch.setenv("METRICOOL_USER_ID", "3564167")
    with patch("post.schedule_post") as sched:
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
    assert "kill-switch" in capsys.readouterr().err.lower()
    sched.assert_not_called()


def test_network_flag_allows_schedule(tmp_path: Path, monkeypatch):
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
    monkeypatch.delenv("METRICOOL_ALLOW_NETWORK", raising=False)
    monkeypatch.setenv("METRICOOL_API_KEY", "test-key")
    monkeypatch.setenv("METRICOOL_USER_ID", "3564167")
    with patch("post.schedule_post", return_value={"data": {"id": 7}}) as sched:
        rc = metricool_post.main(
            [
                "--brand",
                "waystream_sanctuary",
                "--asset",
                str(FIXTURE),
                "--draft",
                "--network",
                "--brands-map",
                str(map_path),
            ]
        )
    assert rc == 0
    sched.assert_called_once()


def test_empty_media_refused_without_allow_text_only():
    with pytest.raises(MetricoolConfigError, match="media requires"):
        metricool_post.assert_media_ready(
            {
                "media": [],
                "publicationDate": {"dateTime": "2026-07-22T09:00:00", "timezone": "UTC"},
                "providers": [{"network": "tiktok"}],
            },
            allow_text_only=False,
        )


def test_empty_media_allowed_with_flag():
    metricool_post.assert_media_ready({"media": []}, allow_text_only=True)


def test_validate_config_canonical_map_ok():
    report = validate_config.load_and_validate(BRANDS_YAML)
    assert report["ok"] is True
    assert report["wired_count"] >= 1
    # Q-METRIC-02 resolved: live Waystream Sanctuary blog_id is wired (not placeholder).
    assert "waystream_sanctuary" not in (report.get("pending_placeholders") or [])
    strict = validate_config.load_and_validate(BRANDS_YAML, strict_blog_ids=True)
    assert strict["ok"] is True


def test_validate_config_orphan_fails(tmp_path: Path):
    data = {
        "account": "waystream",
        "brands": {
            "waystream_sanctuary": {
                "blog_id": "WAYSTREAM_BLOG_ID_PENDING",
                "status": "wired",
            },
            "not_a_real_brand_xyz": {"blog_id": None, "status": "unwired"},
        },
    }
    # Provide tiny canonical set so orphan is detected without loading full registries
    report = validate_config.validate_brand_map(
        data,
        canonical_keys={"waystream_sanctuary", "way_stream_sanctuary"},
    )
    assert report["ok"] is False
    assert any("orphan" in e for e in report["errors"])


def test_validate_config_unwired_must_be_null():
    data = {
        "account": "waystream",
        "brands": {
            "waystream_sanctuary": {"blog_id": "1", "status": "wired"},
            "stillness_press": {"blog_id": "oops", "status": "unwired"},
        },
    }
    report = validate_config.validate_brand_map(
        data, canonical_keys={"waystream_sanctuary", "stillness_press"}
    )
    assert report["ok"] is False
    assert any("unwired" in e and "null" in e for e in report["errors"])


def test_sync_merge_preserves_blog_id(tmp_path: Path):
    # Point pin at a matching blog_id so durable re-apply does not overwrite the fixture.
    pin = tmp_path / "metricool_waystream_pin.yaml"
    pin.write_text(
        "brand_key: waystream_sanctuary\nblog_id: '12345'\nstatus: wired\n",
        encoding="utf-8",
    )
    sync_brands.PIN_PATH = pin
    existing = {
        "account": "waystream",
        "user_id_env": "METRICOOL_USER_ID",
        "brands": {
            "waystream_sanctuary": {
                "blog_id": "12345",
                "status": "wired",
                "timezone": "America/New_York",
            },
            "stillness_press": {"blog_id": None, "status": "unwired"},
        },
    }
    canonical = {"waystream_sanctuary", "stillness_press", "stoic_edge", "way_stream_sanctuary"}
    merged, stats = sync_brands.merge_brand_map(existing, canonical)
    assert merged["brands"]["waystream_sanctuary"]["blog_id"] == "12345"
    assert merged["brands"]["waystream_sanctuary"]["status"] == "wired"
    assert merged["brands"]["stoic_edge"] == {"blog_id": None, "status": "unwired"}
    assert "stoic_edge" in stats["added"]


def test_sync_prune_orphans():
    existing = {
        "account": "waystream",
        "brands": {
            "waystream_sanctuary": {"blog_id": "1", "status": "wired"},
            "ghost_brand": {"blog_id": None, "status": "unwired"},
        },
    }
    merged, stats = sync_brands.merge_brand_map(
        existing, {"waystream_sanctuary"}, prune_orphans=True
    )
    assert "ghost_brand" not in merged["brands"]
    assert stats["pruned"] == ["ghost_brand"]


def test_status_presence_only(tmp_path: Path, monkeypatch, capsys):
    # Point at real brands map via default path would work; use tmp for isolation
    brands_map = yaml.safe_load(BRANDS_YAML.read_text(encoding="utf-8"))
    map_path = tmp_path / "metricool_brands.yaml"
    map_path.write_text(yaml.safe_dump(brands_map), encoding="utf-8")
    monkeypatch.delenv("METRICOOL_API_KEY", raising=False)
    monkeypatch.delenv("METRICOOL_USER_ID", raising=False)
    monkeypatch.delenv("METRICOOL_ALLOW_NETWORK", raising=False)
    rc = metricool_status.main(["--brands-map", str(map_path), "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["credentials"]["METRICOOL_API_KEY"] == "MISSING"
    assert payload["network_kill_switch"]["METRICOOL_ALLOW_NETWORK"].startswith("OFF")
    assert "test-key" not in json.dumps(payload)
    assert payload["primary_blocker"] == "Q-METRIC-CREDS"


def test_no_key_shaped_literals_in_metricool_managed_files():
    paths = list(METRICOOL_SCRIPTS.glob("*.py")) + [BRANDS_YAML]
    offenders: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            if _KEY_SHAPED.search(line):
                # Allow documented default user id and placeholder tokens
                if "3564167" in line or "WAYSTREAM_BLOG_ID_PENDING" in line:
                    continue
                if "test-key" in line:  # only in tests file, not here
                    continue
                offenders.append(f"{path.relative_to(REPO)}:{i}:{line.strip()[:80]}")
    assert offenders == []


def test_metricool_api_txt_gitignored():
    gitignore = (REPO / ".gitignore").read_text(encoding="utf-8")
    assert "docs/metricool_api.txt" in gitignore
    assert "docs/*_api.txt" in gitignore


def test_canonical_keys_cover_current_map():
    canon = collect_canonical_brand_keys()
    data = yaml.safe_load(BRANDS_YAML.read_text(encoding="utf-8"))
    map_keys = set((data.get("brands") or {}).keys())
    assert map_keys <= canon
    assert "waystream_sanctuary" in map_keys


def test_install_keychain_extracts_token_not_markdown():
    import install_keychain_creds as install

    raw = "** note of stuff\n\nMETRICOOL_API_KEY:\n\nOBNK" + ("A" * 60) + "\n\nUSER_ID:\n\n3564167\n"
    key = install.extract_api_key(raw)
    assert len(key) == 64
    assert key.startswith("OBNK")
    assert install.extract_user_id(raw) == "3564167"


def test_sync_reapplies_waystream_pin(tmp_path: Path):
    pin = tmp_path / "metricool_waystream_pin.yaml"
    pin.write_text(
        "brand_key: waystream_sanctuary\nblog_id: '6582629'\nstatus: wired\ntimezone: America/New_York\n",
        encoding="utf-8",
    )
    # Monkeypatch pin path used by sync module
    sync_brands.PIN_PATH = pin
    existing = {
        "account": "waystream",
        "brands": {
            "waystream_sanctuary": {
                "blog_id": "WAYSTREAM_BLOG_ID_PENDING",
                "status": "wired",
            },
            "stillness_press": {"blog_id": None, "status": "unwired"},
        },
    }
    merged, stats = sync_brands.merge_brand_map(
        existing, {"waystream_sanctuary", "stillness_press"}
    )
    assert merged["brands"]["waystream_sanctuary"]["blog_id"] == "6582629"
    assert stats.get("pin_applied") is True


def test_check_metricool_managed_pin_and_registry():
    import sys
    ci = str(REPO / "scripts" / "ci")
    if ci not in sys.path:
        sys.path.insert(0, ci)
    import check_metricool_managed as gate

    brands = yaml.safe_load(BRANDS_YAML.read_text(encoding="utf-8"))
    pin = yaml.safe_load((REPO / "config" / "integrations" / "metricool_waystream_pin.yaml").read_text(encoding="utf-8"))
    assert gate.check_pin(brands, pin) == []
    assert gate.check_registry() == []
    assert gate.check_gitignore() == []


