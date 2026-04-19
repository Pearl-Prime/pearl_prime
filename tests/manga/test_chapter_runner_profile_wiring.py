"""Tests that chapter runner resolves manga_profile and passes it to QC."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from phoenix_v4.manga.runner.chapter_runner import _resolve_manga_profile
from phoenix_v4.manga.models import paths as manga_paths


def _make_workspace(tmp_path: Path, brand_id: str = "", genre_family: str = "", series_id: str = "") -> Path:
    ws = tmp_path / "ws"
    ws.mkdir()
    cr: dict = {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_request",
        "series_id": series_id or "test_series",
        "chapter_id": "ch_01",
        "chapter_number": 1,
    }
    if brand_id:
        cr["brand_id"] = brand_id
    if genre_family:
        cr["genre_family"] = genre_family
    (ws / manga_paths.CHAPTER_REQUEST).write_text(json.dumps(cr), encoding="utf-8")
    return ws


def test_resolve_returns_none_when_no_profile(tmp_path):
    ws = _make_workspace(tmp_path, series_id="nonexistent_series_xyz")
    result = _resolve_manga_profile(ws)
    assert result is None  # graceful — no profile = all gates skip


def test_resolve_by_brand_genre_from_chapter_request(tmp_path):
    ws = _make_workspace(tmp_path, brand_id="stillness_press", genre_family="healing")
    result = _resolve_manga_profile(ws)
    # stillness_press/healing profile exists in brands dir
    assert result is not None
    assert result.brand_id == "stillness_press"
    assert result.emotional_engine == "cozy_restoration"


def test_resolve_explicit_params_override_chapter_request(tmp_path):
    # chapter_request says stillness_press/healing, but caller explicitly passes warrior_calm/battle
    ws = _make_workspace(tmp_path, brand_id="stillness_press", genre_family="healing")
    result = _resolve_manga_profile(ws, brand_id="warrior_calm", genre_id="battle")
    assert result is not None
    assert result.brand_id == "warrior_calm"
    assert result.emotional_engine == "rivalry"


def test_resolve_none_when_workspace_missing_chapter_request(tmp_path):
    ws = tmp_path / "empty_ws"
    ws.mkdir()
    result = _resolve_manga_profile(ws)
    assert result is None
