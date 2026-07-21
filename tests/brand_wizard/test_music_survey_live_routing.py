"""Tests for GET /wizard/step/music-survey (live embed vs deprecated file://)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BW_SERVER = REPO_ROOT / "brand-wizard-app" / "server"
if str(BW_SERVER) not in sys.path:
    sys.path.insert(0, str(BW_SERVER))

import music_survey_routes as routes  # noqa: E402


@pytest.fixture()
def brands_tmp(tmp_path: Path) -> Path:
    d = tmp_path / "brands"
    d.mkdir()
    return d


@pytest.fixture()
def registry_tmp(tmp_path: Path) -> Path:
    """Throwaway copy of config/music/music_brand_registry.yaml's shape — NEVER the real
    repo file (lane rule: never mutate the real registry during tests)."""
    p = tmp_path / "music_brand_registry.yaml"
    p.write_text(
        "music_brands:\n\n"
        "  - brand_id: _template_music\n"
        "    musician_handle: _template\n"
        "    archetype: placeholder\n"
        "    mode: music\n"
        "    status: inactive\n"
        "    survey_yaml_pointer: artifacts/musician_survey/SURVEY_TEMPLATE.yaml\n"
        "    created: 2026-05-09\n"
        '    notes: "Schema-only template entry."\n',
        encoding="utf-8",
    )
    return p


@pytest.fixture()
def canonical_tmp(tmp_path: Path) -> Path:
    """Throwaway copy of config/manga/canonical_brand_list.yaml's shape — NEVER the real
    repo file. `collision_brand_music` intentionally mirrors the `<handle>_music` shape so
    test_post_save_registry_collision_is_400 can exercise a real collision."""
    p = tmp_path / "canonical_brand_list.yaml"
    p.write_text(
        "brands:\n  sample_manga_brand:\n    tier: core\n  collision_brand_music:\n    tier: core\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture()
def live_client(
    brands_tmp: Path,
    registry_tmp: Path,
    canonical_tmp: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    from fastapi.testclient import TestClient

    monkeypatch.setattr(routes, "_brands_directory", lambda: brands_tmp)
    monkeypatch.setattr(routes, "_music_registry_path", lambda: registry_tmp)
    monkeypatch.setattr(routes, "_canonical_brand_list_path", lambda: canonical_tmp)
    return TestClient(routes.create_music_survey_app())


def test_normalize_locale_defaults_and_aliases() -> None:
    assert routes.normalize_music_survey_locale(None) == "en"
    assert routes.normalize_music_survey_locale("") == "en"
    assert routes.normalize_music_survey_locale("EN") == "en"
    assert routes.normalize_music_survey_locale("zh-TW") == "zh-tw"
    assert routes.normalize_music_survey_locale("zh_tw") == "zh-tw"
    assert routes.normalize_music_survey_locale("zh_CN") == "zh-cn"
    assert routes.normalize_music_survey_locale("not-a-locale") is None


def test_unknown_locale_404(live_client) -> None:
    r = live_client.get("/wizard/step/music-survey", params={"locale": "klingon"})
    assert r.status_code == 404


@pytest.mark.parametrize(
    "loc,expect_cl",
    [
        ("en", "en"),
        ("ja", "ja"),
        ("zh-tw", "zh-Hant"),
        ("zh-cn", "zh-Hans"),
    ],
)
def test_each_supported_locale_served_200(live_client, loc: str, expect_cl: str) -> None:
    r = live_client.get("/wizard/step/music-survey", params={"locale": loc})
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert r.headers.get("content-language") == expect_cl
    assert f'name="pearl-music-survey-locale" content="{loc}"' in r.text


def test_default_locale_en_without_query(live_client) -> None:
    r = live_client.get("/wizard/step/music-survey")
    assert r.status_code == 200
    assert f'name="pearl-music-survey-locale" content="en"' in r.text


def test_missing_survey_bundle_graceful_503(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi.testclient import TestClient

    monkeypatch.setenv("BRAND_WIZARD_MUSIC_SURVEY_ROOT", str(tmp_path))
    monkeypatch.setenv("BRAND_WIZARD_MUSIC_SURVEY_ROOT_EXCLUSIVE", "1")
    try:
        client = TestClient(routes.create_music_survey_app())
        r = client.get("/wizard/step/music-survey", params={"locale": "en"})
        assert r.status_code == 503
        assert "not installed" in r.text or "Survey unavailable" in r.text
    finally:
        monkeypatch.delenv("BRAND_WIZARD_MUSIC_SURVEY_ROOT", raising=False)
        monkeypatch.delenv("BRAND_WIZARD_MUSIC_SURVEY_ROOT_EXCLUSIVE", raising=False)


def test_post_save_still_registered(live_client) -> None:
    """Regression: stacking PR must keep save route on the same app factory."""
    assert live_client.post(
        "/wizard/music-survey/save",
        json={"wizard_session_id": "x", "survey_responses": {}},
    ).status_code in (200, 422)


def test_post_save_registry_collision_is_400(live_client, registry_tmp: Path) -> None:
    """MUSIC-MODE-BRAND-INTEGRATION-V1-01 anti-drift: a brand_id colliding with
    config/manga/canonical_brand_list.yaml (Path X, frozen 37) is a hard 400 reject,
    distinct from an ordinary 422 validation failure."""
    r = live_client.post(
        "/wizard/music-survey/save",
        json={
            "wizard_session_id": "collision_case",
            "survey_responses": {"display_name": "collision_brand"},
        },
    )
    assert r.status_code == 400
    doc = yaml.safe_load(registry_tmp.read_text(encoding="utf-8"))
    assert len(doc["music_brands"]) == 1  # rejected, never appended
