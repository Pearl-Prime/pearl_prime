"""Tests for scripts.brand.manga_character_endpoint."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from scripts.brand.active_brand_classifier import ActiveBrandClassifier, reset_default_classifier
from scripts.brand.manga_character_endpoint import (
    build_manga_character_panel_payload,
    load_series_index,
    resolve_main_character_path,
)


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")


def _complete_wizard(brand_id: str = "alpha_brand") -> str:
    return f"""
        schema_version: 1
        brand_id: {brand_id}
        display_name: Alpha
        wizard_core:
          tagline: Calm copy
          positioning_line: One line
        """


@pytest.fixture(autouse=True)
def _reset_default():
    reset_default_classifier()
    yield
    reset_default_classifier()


def test_load_series_index_tsv_present_and_per_locale(tmp_path: Path) -> None:
    tsv_en = tmp_path / "artifacts/catalog/worldwide_catalog_plan_en_US_2026-05-10.tsv"
    _write(
        tsv_en,
        """
        brand_id\tseries_id\tlocale
        brand_a\ts_one\ten_US
        brand_a\ts_two\tja_JP
        """,
    )
    idx, seen = load_series_index(tmp_path)
    assert seen is True
    assert idx["brand_a"]["en_US"] == {"s_one"}
    assert idx["brand_a"]["ja_JP"] == {"s_two"}


def test_load_series_index_tsv_absent(tmp_path: Path) -> None:
    (tmp_path / "artifacts/catalog").mkdir(parents=True, exist_ok=True)
    idx, seen = load_series_index(tmp_path)
    assert seen is False
    assert idx == {}


def test_build_payload_missing_image_graceful(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/manga/canonical_brand_list.yaml",
        """
        schema_version: 1
        brands:
          brand_x:
            tier: core
        """,
    )
    _write(tmp_path / "config/brand_registry.yaml", "schema_version: 1\nbrands: {}\n")
    wiz = tmp_path / "bw"
    _write(wiz / "brand_x.yaml", _complete_wizard("brand_x"))
    tsv = tmp_path / "artifacts/catalog/worldwide_catalog_plan_en_US_2026-05-10.tsv"
    _write(
        tsv,
        """
        brand\tseries_id
        brand_x\tseries_missing
        """,
    )
    c = ActiveBrandClassifier(repo_root=tmp_path, wizard_yaml_dir=wiz)
    payload = build_manga_character_panel_payload(c)
    assert "brand_x" in payload
    en_series = payload["brand_x"]["en_US"]["series"]
    assert len(en_series) == 1
    assert en_series[0]["series_id"] == "series_missing"
    assert en_series[0]["main_character_image_path"] is None
    assert en_series[0]["status"] == "missing"


def test_resolve_main_character_prefers_locale_segment(tmp_path: Path) -> None:
    img = tmp_path / "artifacts/manga/en_US/brand_x/sid_a/main_character.png"
    img.parent.mkdir(parents=True, exist_ok=True)
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    rel, st = resolve_main_character_path(tmp_path, "brand_x", "sid_a", "en_US")
    assert st == "ready"
    assert rel == "artifacts/manga/en_US/brand_x/sid_a/main_character.png"


def test_build_payload_ready_when_png_present(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/manga/canonical_brand_list.yaml",
        """
        schema_version: 1
        brands:
          brand_x:
            tier: core
        """,
    )
    _write(tmp_path / "config/brand_registry.yaml", "schema_version: 1\nbrands: {}\n")
    wiz = tmp_path / "bw"
    _write(wiz / "brand_x.yaml", _complete_wizard("brand_x"))
    tsv = tmp_path / "artifacts/catalog/worldwide_catalog_plan_en_US_2026-05-10.tsv"
    _write(
        tsv,
        """
        brand_id\tseries_id\tlocale
        brand_x\tsid_ok\ten_US
        """,
    )
    img = tmp_path / "artifacts/manga/en_US/brand_x/sid_ok/main_character.png"
    img.parent.mkdir(parents=True, exist_ok=True)
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    c = ActiveBrandClassifier(repo_root=tmp_path, wizard_yaml_dir=wiz)
    payload = build_manga_character_panel_payload(c)
    row = payload["brand_x"]["en_US"]["series"][0]
    assert row["status"] == "ready"
    assert row["main_character_image_path"] == "artifacts/manga/en_US/brand_x/sid_ok/main_character.png"


def test_main_json_smoke(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/manga/canonical_brand_list.yaml",
        """
        schema_version: 1
        brands:
          z_brand:
            tier: core
        """,
    )
    _write(tmp_path / "config/brand_registry.yaml", "schema_version: 1\nbrands: {}\n")
    wiz = tmp_path / "bw"
    _write(wiz / "z_brand.yaml", _complete_wizard("z_brand"))
    repo = Path(__file__).resolve().parents[2]
    script = repo / "scripts" / "brand" / "manga_character_endpoint.py"
    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--json",
            "--repo-root",
            str(tmp_path),
            "--wizard-dir",
            str(wiz),
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(repo),
        env={**os.environ, "PYTHONPATH": str(repo)},
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert "z_brand" in data
    assert data["z_brand"]["en_US"]["series"] == []
    assert data["z_brand"]["ja_JP"]["series"] == []
