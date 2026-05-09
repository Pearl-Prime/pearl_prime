"""Tests for brand-wizard-app/server music survey YAML save (ws_music_brand_survey_save_post_yaml_advance)."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BW_SERVER = REPO_ROOT / "brand-wizard-app" / "server"
if str(BW_SERVER) not in sys.path:
    sys.path.insert(0, str(BW_SERVER))

import music_survey_save_handler as handler  # noqa: E402
import music_survey_routes as routes  # noqa: E402


@pytest.fixture()
def brands_tmp(tmp_path: Path) -> Path:
    d = tmp_path / "brands"
    d.mkdir()
    return d


def test_new_yaml_creation(brands_tmp: Path) -> None:
    out = handler.save_survey_to_brand_yaml(
        brands_dir=brands_tmp,
        wizard_session_id="music_sess_01",
        survey_responses={"display_name": "River Stone", "primary_genre": "ambient"},
    )
    assert out == {
        "status": "saved",
        "next_step": "step5",
        "yaml_path": "brands/music_sess_01.yaml",
    }
    p = brands_tmp / "music_sess_01.yaml"
    assert p.exists()
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert doc["musician_reflections"]["display_name"] == "River Stone"
    assert doc["musician_reflections"]["primary_genre"] == "ambient"


def test_existing_yaml_merge(brands_tmp: Path) -> None:
    p = brands_tmp / "merge_case.yaml"
    p.write_text(
        "wizard_meta:\n  step: 4\nmusician_reflections:\n  display_name: Old\n  years_active: \"5\"\n",
        encoding="utf-8",
    )
    handler.save_survey_to_brand_yaml(
        brands_dir=brands_tmp,
        wizard_session_id="merge_case",
        survey_responses={"display_name": "New", "primary_genre": "folk"},
    )
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert doc["wizard_meta"]["step"] == 4
    assert doc["musician_reflections"]["display_name"] == "New"
    assert doc["musician_reflections"]["years_active"] == "5"
    assert doc["musician_reflections"]["primary_genre"] == "folk"


def test_validate_session_rejects_traversal() -> None:
    with pytest.raises(handler.MusicSurveySaveError):
        handler.validate_wizard_session_id("../etc/passwd")


def test_validate_survey_not_object() -> None:
    with pytest.raises(handler.MusicSurveySaveError):
        handler.validate_survey_responses(["not", "a", "dict"])


def test_atomic_write_failure_preserves_original(brands_tmp: Path) -> None:
    p = brands_tmp / "atomic.yaml"
    p.write_text("seed: true\n", encoding="utf-8")

    def boom(*_a, **_k):
        raise OSError("simulated replace failure")

    with patch("music_survey_save_handler.os.replace", side_effect=boom):
        with pytest.raises(OSError, match="simulated replace failure"):
            handler.save_survey_to_brand_yaml(
                brands_dir=brands_tmp,
                wizard_session_id="atomic",
                survey_responses={"x": 1},
            )
    assert p.read_text(encoding="utf-8") == "seed: true\n"
    leftovers = list(brands_tmp.glob(".atomic.yaml.*.tmp"))
    assert not leftovers


def test_malformed_non_mapping_musician_reflections(brands_tmp: Path) -> None:
    p = brands_tmp / "badrefl.yaml"
    p.write_text("musician_reflections: not_a_mapping\n", encoding="utf-8")
    with pytest.raises(handler.MusicSurveySaveError, match="must be a mapping"):
        handler.save_survey_to_brand_yaml(
            brands_dir=brands_tmp,
            wizard_session_id="badrefl",
            survey_responses={"a": 1},
        )


def test_post_endpoint_happy_path(brands_tmp: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(routes, "_brands_directory", lambda: brands_tmp)
    from fastapi.testclient import TestClient

    client = TestClient(routes.create_music_survey_app())
    r = client.post(
        "/wizard/music-survey/save",
        json={
            "wizard_session_id": "api_ok",
            "survey_responses": {"display_name": "API"},
        },
    )
    assert r.status_code == 200
    assert r.json()["status"] == "saved"
    assert r.json()["next_step"] == "step5"


def test_post_endpoint_422_validation(brands_tmp: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(routes, "_brands_directory", lambda: brands_tmp)
    from fastapi.testclient import TestClient

    client = TestClient(routes.create_music_survey_app())
    r = client.post(
        "/wizard/music-survey/save",
        json={"wizard_session_id": "x", "survey_responses": "nope"},
    )
    assert r.status_code == 422

    r2 = client.post(
        "/wizard/music-survey/save",
        json={"wizard_session_id": "..bad", "survey_responses": {}},
    )
    assert r2.status_code == 422
