"""Tests for scripts.brand.active_brand_classifier (brand_wizard YAML SSOT)."""

from __future__ import annotations

from pathlib import Path
import textwrap

import pytest
import yaml

from scripts.brand.active_brand_classifier import (
    ActiveBrandClassifier,
    reset_default_classifier,
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


def test_active_complete_yaml(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/manga/canonical_brand_list.yaml",
        """
        schema_version: 1
        brands:
          alpha_brand:
            tier: core
        """,
    )
    _write(tmp_path / "config/brand_registry.yaml", "schema_version: 1\nbrands: {}\n")
    wiz = tmp_path / "bw"
    _write(wiz / "alpha_brand.yaml", _complete_wizard("alpha_brand"))
    c = ActiveBrandClassifier(repo_root=tmp_path, wizard_yaml_dir=wiz)
    assert c.is_active("alpha_brand") is True
    assert "alpha_brand" in c.list_active()
    assert "alpha_brand" not in c.list_inactive()
    assert c.reason_for("alpha_brand") == ""


def test_inactive_missing_yaml(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/manga/canonical_brand_list.yaml",
        """
        schema_version: 1
        brands:
          ghost_brand:
            tier: niche
        """,
    )
    _write(tmp_path / "config/brand_registry.yaml", "schema_version: 1\nbrands: {}\n")
    wiz = tmp_path / "bw"
    wiz.mkdir(parents=True, exist_ok=True)
    c = ActiveBrandClassifier(repo_root=tmp_path, wizard_yaml_dir=wiz)
    assert c.is_active("ghost_brand") is False
    assert "ghost_brand" in c.list_inactive()
    assert c.reason_for("ghost_brand") == "no brand_wizard YAML found"


def test_inactive_partial_yaml_missing_required_field(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/manga/canonical_brand_list.yaml",
        """
        schema_version: 1
        brands:
          partial_brand:
            tier: core
        """,
    )
    _write(tmp_path / "config/brand_registry.yaml", "schema_version: 1\nbrands: {}\n")
    wiz = tmp_path / "bw"
    # Missing wizard_core entirely
    _write(
        wiz / "partial_brand.yaml",
        """
        schema_version: 1
        brand_id: partial_brand
        display_name: Partial
        """,
    )
    c = ActiveBrandClassifier(repo_root=tmp_path, wizard_yaml_dir=wiz)
    assert c.is_active("partial_brand") is False
    assert c.reason_for("partial_brand").startswith("missing required field:")


def test_empty_registries_yield_empty_snapshot(tmp_path: Path) -> None:
    _write(tmp_path / "config/manga/canonical_brand_list.yaml", "schema_version: 1\nbrands: {}\n")
    _write(tmp_path / "config/brand_registry.yaml", "schema_version: 1\nbrands: {}\n")
    wiz = tmp_path / "bw"
    wiz.mkdir(parents=True, exist_ok=True)
    c = ActiveBrandClassifier(repo_root=tmp_path, wizard_yaml_dir=wiz)
    assert c.snapshot() == {}
    assert c.list_active() == []
    assert c.list_inactive() == []


def test_empty_wizard_directory_all_canonical_inactive(tmp_path: Path) -> None:
    """37-path canon: two-brand fixture stands in for full list; all inactive without YAML."""
    brands = {f"brand_{i}": {"tier": "niche"} for i in range(37)}
    _write(
        tmp_path / "config/manga/canonical_brand_list.yaml",
        yaml.safe_dump({"schema_version": 1, "brands": brands}, sort_keys=False),
    )
    _write(tmp_path / "config/brand_registry.yaml", "schema_version: 1\nbrands: {}\n")
    wiz = tmp_path / "bw"
    wiz.mkdir(parents=True, exist_ok=True)
    c = ActiveBrandClassifier(repo_root=tmp_path, wizard_yaml_dir=wiz)
    assert len(c.brand_universe()) == 37
    assert c.list_active() == []
    assert len(c.list_inactive()) == 37
    assert all(c.reason_for(b) == "no brand_wizard YAML found" for b in c.list_inactive())


def test_music_registry_absent_no_exception(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/manga/canonical_brand_list.yaml",
        """
        schema_version: 1
        brands:
          solo:
            tier: core
        """,
    )
    _write(tmp_path / "config/brand_registry.yaml", "schema_version: 1\nbrands: {}\n")
    assert not (tmp_path / "config/music/music_brand_registry.yaml").exists()
    c = ActiveBrandClassifier(repo_root=tmp_path, wizard_yaml_dir=tmp_path / "bw")
    assert c.music_registry_deferred is True
    assert c.music_brand_ids() == []
    c.snapshot()
    c.list_active()
    c.list_inactive()
