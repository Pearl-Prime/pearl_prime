"""Tests for brand-wizard-app/server music survey YAML save (ws_music_brand_survey_save_post_yaml_advance)."""
from __future__ import annotations

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


@pytest.fixture()
def registry_tmp(tmp_path: Path) -> Path:
    """Throwaway copy of config/music/music_brand_registry.yaml's shape — NEVER the real
    repo file — per the lane's SMALLEST SAFE BATCH rule (never mutate the real registry
    during tests)."""
    p = tmp_path / "music_brand_registry.yaml"
    p.write_text(
        "schema_version: 1\n"
        "registry_id: music_brand_registry\n"
        "id_space_start: 38\n\n"
        "music_brands:\n\n"
        "  # Template entry — inactive placeholder, NOT a real musician brand.\n"
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
    repo file."""
    p = tmp_path / "canonical_brand_list.yaml"
    p.write_text(
        "schema_version: 1\ntotal_brands: 1\nbrands:\n  sample_manga_brand:\n    tier: core\n",
        encoding="utf-8",
    )
    return p


def test_new_yaml_creation(brands_tmp: Path, registry_tmp: Path, canonical_tmp: Path) -> None:
    out = handler.save_survey_to_brand_yaml(
        brands_dir=brands_tmp,
        wizard_session_id="music_sess_01",
        survey_responses={"display_name": "River Stone", "primary_genre": "ambient"},
        music_registry_path=registry_tmp,
        canonical_brand_list_path=canonical_tmp,
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


def test_existing_yaml_merge(brands_tmp: Path, registry_tmp: Path, canonical_tmp: Path) -> None:
    p = brands_tmp / "merge_case.yaml"
    p.write_text(
        "wizard_meta:\n  step: 4\nmusician_reflections:\n  display_name: Old\n  years_active: \"5\"\n",
        encoding="utf-8",
    )
    handler.save_survey_to_brand_yaml(
        brands_dir=brands_tmp,
        wizard_session_id="merge_case",
        survey_responses={"display_name": "New", "primary_genre": "folk"},
        music_registry_path=registry_tmp,
        canonical_brand_list_path=canonical_tmp,
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


def test_atomic_write_failure_preserves_original(
    brands_tmp: Path, registry_tmp: Path, canonical_tmp: Path
) -> None:
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
                music_registry_path=registry_tmp,
                canonical_brand_list_path=canonical_tmp,
            )
    assert p.read_text(encoding="utf-8") == "seed: true\n"
    leftovers = list(brands_tmp.glob(".atomic.yaml.*.tmp"))
    assert not leftovers
    # Registry must be untouched too — the wizard-YAML write fails first.
    assert "atomic_music" not in registry_tmp.read_text(encoding="utf-8")


def test_malformed_non_mapping_musician_reflections(
    brands_tmp: Path, registry_tmp: Path, canonical_tmp: Path
) -> None:
    p = brands_tmp / "badrefl.yaml"
    p.write_text("musician_reflections: not_a_mapping\n", encoding="utf-8")
    with pytest.raises(handler.MusicSurveySaveError, match="must be a mapping"):
        handler.save_survey_to_brand_yaml(
            brands_dir=brands_tmp,
            wizard_session_id="badrefl",
            survey_responses={"a": 1},
            music_registry_path=registry_tmp,
            canonical_brand_list_path=canonical_tmp,
        )


def test_post_endpoint_happy_path(
    brands_tmp: Path, registry_tmp: Path, canonical_tmp: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(routes, "_brands_directory", lambda: brands_tmp)
    monkeypatch.setattr(routes, "_music_registry_path", lambda: registry_tmp)
    monkeypatch.setattr(routes, "_canonical_brand_list_path", lambda: canonical_tmp)
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
    assert "api_music" in registry_tmp.read_text(encoding="utf-8")


def test_post_endpoint_422_validation(
    brands_tmp: Path, registry_tmp: Path, canonical_tmp: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(routes, "_brands_directory", lambda: brands_tmp)
    monkeypatch.setattr(routes, "_music_registry_path", lambda: registry_tmp)
    monkeypatch.setattr(routes, "_canonical_brand_list_path", lambda: canonical_tmp)
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


# ── MUSIC-MODE-BRAND-INTEGRATION-V1-01 §3/§5 — registry append/idempotency/anti-drift ──


def test_registry_append_exact_one_row(brands_tmp: Path, registry_tmp: Path, canonical_tmp: Path) -> None:
    before = yaml.safe_load(registry_tmp.read_text(encoding="utf-8"))
    assert len(before["music_brands"]) == 1  # just the template row

    handler.save_survey_to_brand_yaml(
        brands_dir=brands_tmp,
        wizard_session_id="iris_moss_music",
        survey_responses={"display_name": "Iris Moss", "primary_genre": "indie_folk"},
        music_registry_path=registry_tmp,
        canonical_brand_list_path=canonical_tmp,
    )

    after = yaml.safe_load(registry_tmp.read_text(encoding="utf-8"))
    rows = after["music_brands"]
    assert len(rows) == 2
    new_row = next(r for r in rows if r["brand_id"] == "iris_moss_music")
    assert new_row["musician_handle"] == "iris_moss"
    assert new_row["archetype"] == "indie_folk"
    assert new_row["mode"] == "music"
    assert new_row["status"] == "active"
    assert new_row["survey_yaml_pointer"] == "brands/iris_moss_music.yaml"
    assert new_row["created"]
    # Header/schema comments (the schema authority) must survive untouched.
    assert "schema_version: 1" in registry_tmp.read_text(encoding="utf-8")
    assert "# Template entry" in registry_tmp.read_text(encoding="utf-8")


def test_registry_resave_is_idempotent_update_in_place(
    brands_tmp: Path, registry_tmp: Path, canonical_tmp: Path
) -> None:
    for i in range(3):
        handler.save_survey_to_brand_yaml(
            brands_dir=brands_tmp,
            wizard_session_id="iris_moss_music",
            survey_responses={"display_name": "Iris Moss", "primary_genre": "indie_folk", "pass": i},
            music_registry_path=registry_tmp,
            canonical_brand_list_path=canonical_tmp,
        )

    doc = yaml.safe_load(registry_tmp.read_text(encoding="utf-8"))
    rows = [r for r in doc["music_brands"] if r["brand_id"] == "iris_moss_music"]
    assert len(rows) == 1  # never duplicated across 3 saves
    assert len(doc["music_brands"]) == 2  # template + the one music row


def test_registry_resave_preserves_original_created_date(
    brands_tmp: Path, registry_tmp: Path, canonical_tmp: Path
) -> None:
    handler.save_survey_to_brand_yaml(
        brands_dir=brands_tmp,
        wizard_session_id="iris_moss_music",
        survey_responses={"display_name": "Iris Moss"},
        music_registry_path=registry_tmp,
        canonical_brand_list_path=canonical_tmp,
        # today= is not a parameter of save_survey_to_brand_yaml; force distinguishable
        # `created` by calling upsert directly first, then re-saving via the real path.
    )
    doc1 = yaml.safe_load(registry_tmp.read_text(encoding="utf-8"))
    first_created = next(r for r in doc1["music_brands"] if r["brand_id"] == "iris_moss_music")["created"]

    # Simulate a re-save happening on a later date via the lower-level upsert (which
    # save_survey_to_brand_yaml calls with today's real date every time).
    handler.upsert_music_brand_registry_row(
        registry_path=registry_tmp,
        canonical_brand_list_path=canonical_tmp,
        brand_id="iris_moss_music",
        musician_handle="iris_moss",
        survey_yaml_pointer="brands/iris_moss_music.yaml",
        today="2099-01-01",
    )
    doc2 = yaml.safe_load(registry_tmp.read_text(encoding="utf-8"))
    second_created = next(r for r in doc2["music_brands"] if r["brand_id"] == "iris_moss_music")["created"]
    assert second_created == first_created
    assert second_created != "2099-01-01"


def test_registry_collision_with_canonical_brand_list_rejected(
    brands_tmp: Path, registry_tmp: Path, canonical_tmp: Path
) -> None:
    with pytest.raises(handler.MusicBrandRegistryCollisionError):
        handler.upsert_music_brand_registry_row(
            registry_path=registry_tmp,
            canonical_brand_list_path=canonical_tmp,
            brand_id="sample_manga_brand",  # collides with canonical_tmp's Path X row
            musician_handle="sample_manga_brand".replace("_music", ""),
            survey_yaml_pointer="brands/sample_manga_brand.yaml",
        )
    # Hard reject must not have mutated the registry file.
    doc = yaml.safe_load(registry_tmp.read_text(encoding="utf-8"))
    assert len(doc["music_brands"]) == 1


def test_registry_missing_file_raises(brands_tmp: Path, canonical_tmp: Path, tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.yaml"
    with pytest.raises(handler.MusicSurveySaveError):
        handler.upsert_music_brand_registry_row(
            registry_path=missing,
            canonical_brand_list_path=canonical_tmp,
            brand_id="ghost_music",
            musician_handle="ghost",
            survey_yaml_pointer="brands/ghost_music.yaml",
        )
