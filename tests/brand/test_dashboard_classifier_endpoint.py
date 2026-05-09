"""Tests for scripts.brand.dashboard_classifier_endpoint."""

from __future__ import annotations

import json
from pathlib import Path
import textwrap

import pytest

from scripts.brand.active_brand_classifier import ActiveBrandClassifier, reset_default_classifier
from scripts.brand.dashboard_classifier_endpoint import build_dashboard_payload
from scripts.brand.dashboard_classifier_endpoint import main as endpoint_main


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


def test_build_dashboard_payload_regions_and_totals(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/manga/canonical_brand_list.yaml",
        """
        schema_version: 1
        brands:
          manga_only:
            tier: core
        """,
    )
    _write(
        tmp_path / "config/brand_registry.yaml",
        """
        schema_version: 1
        brands:
          book_only:
            tier: core
        """,
    )
    wiz = tmp_path / "bw"
    _write(wiz / "manga_only.yaml", _complete_wizard("manga_only"))
    _write(wiz / "book_only.yaml", _complete_wizard("book_only"))

    c = ActiveBrandClassifier(repo_root=tmp_path, wizard_yaml_dir=wiz)
    payload = build_dashboard_payload(c)

    assert payload["schema_version"] == 1
    assert payload["totals"]["active"] == 2
    assert payload["totals"]["inactive"] == 0
    assert payload["totals"]["universe"] == 2
    assert payload["locale_breakdown"] is None
    assert payload["by_region"]["manga_canonical"]["active"] == 1
    assert payload["by_region"]["other_registry"]["active"] == 1

    by_id = {b["brand_id"]: b for b in payload["brands"]}
    assert by_id["manga_only"]["region"] == "manga_canonical"
    assert by_id["manga_only"]["status"] == "active"
    assert by_id["manga_only"]["last_wizard_run"] is not None
    assert by_id["manga_only"]["reason"] == ""
    assert by_id["book_only"]["region"] == "other_registry"


def test_build_dashboard_inactive_reason(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/manga/canonical_brand_list.yaml",
        """
        schema_version: 1
        brands:
          ghost:
            tier: niche
        """,
    )
    _write(tmp_path / "config/brand_registry.yaml", "schema_version: 1\nbrands: {}\n")
    wiz = tmp_path / "bw"
    wiz.mkdir(parents=True, exist_ok=True)
    c = ActiveBrandClassifier(repo_root=tmp_path, wizard_yaml_dir=wiz)
    payload = build_dashboard_payload(c)
    assert payload["totals"]["active"] == 0
    assert payload["totals"]["inactive"] == 1
    g = next(b for b in payload["brands"] if b["brand_id"] == "ghost")
    assert g["status"] == "inactive"
    assert "no brand_wizard YAML" in g["reason"]
    assert g["last_wizard_run"] is None


def test_cli_json_exit_zero(tmp_path: Path, capsysbinary) -> None:
    _write(
        tmp_path / "config/manga/canonical_brand_list.yaml",
        "schema_version: 1\nbrands:\n  x:\n    tier: core\n",
    )
    _write(tmp_path / "config/brand_registry.yaml", "schema_version: 1\nbrands: {}\n")
    wiz = tmp_path / "bw"
    _write(wiz / "x.yaml", _complete_wizard("x"))
    code = endpoint_main(
        ["--json", "--repo-root", str(tmp_path), "--wizard-dir", str(wiz)],
    )
    assert code == 0
    raw = capsysbinary.readouterr().out
    data = json.loads(raw.decode("utf-8"))
    assert data["totals"]["active"] == 1
