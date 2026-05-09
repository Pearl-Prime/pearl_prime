"""Tests for scripts.brand.weekly_package_endpoint."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
import textwrap

from scripts.brand.active_brand_classifier import ActiveBrandClassifier
from scripts.brand.weekly_package_endpoint import (
    build_weekly_package_status_payload,
    main as weekly_main,
    parse_weekly_packages_tsv,
    weekly_packages_tsv_path,
)


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")


def _complete_wizard(brand_id: str) -> str:
    return f"""
        schema_version: 1
        brand_id: {brand_id}
        display_name: {brand_id.title()}
        wizard_core:
          tagline: Calm copy
          positioning_line: One line
        """


def _classifier_with_brands(tmp_path: Path, *brand_ids: str) -> ActiveBrandClassifier:
    brands_yaml = "schema_version: 1\nbrands:\n"
    for bid in brand_ids:
        brands_yaml += f"  {bid}:\n    tier: core\n"
    _write(tmp_path / "config/manga/canonical_brand_list.yaml", brands_yaml)
    _write(tmp_path / "config/brand_registry.yaml", "schema_version: 1\nbrands: {}\n")
    wiz = tmp_path / "bw"
    for bid in brand_ids:
        _write(wiz / f"{bid}.yaml", _complete_wizard(bid))
    return ActiveBrandClassifier(repo_root=tmp_path, wizard_yaml_dir=wiz)


def test_parse_mixed_status_per_brand() -> None:
    tsv = """brand_id\tstatus\tdownload_url\tlast_updated
a_brand\tready\thttps://cdn.example/a.zip\t2026-05-05T08:00:00Z
a_brand\tpending\t\t2026-05-05T09:00:00Z
b_brand\tready\thttps://cdn.example/b.zip\t2026-05-04T12:00:00Z
"""
    by = parse_weekly_packages_tsv(tsv)
    assert by["a_brand"].ready_count == 1
    assert by["a_brand"].pending_count == 1
    assert by["b_brand"].ready_count == 1


def test_tsv_absent_returns_empty_dict(tmp_path: Path) -> None:
    c = _classifier_with_brands(tmp_path, "solo_brand")
    coord = tmp_path / "coord"
    coord.mkdir(parents=True, exist_ok=True)
    out = build_weekly_package_status_payload(c, coord_dir=coord, week_monday=date(2026, 5, 4))
    assert out == {}


def test_tsv_present_populated_active_brands(tmp_path: Path) -> None:
    c = _classifier_with_brands(tmp_path, "alpha_brand", "beta_brand")
    coord = tmp_path / "coord"
    mon = date(2026, 5, 4)
    p = weekly_packages_tsv_path(coord, mon)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        "brand_id\tstatus\tdownload_url\tlast_updated\n"
        "alpha_brand\tready\thttps://files.example/alpha.tgz\t2026-05-05T10:00:00Z\n"
        "beta_brand\tpending\t\t2026-05-05T11:00:00Z\n",
        encoding="utf-8",
    )
    out = build_weekly_package_status_payload(c, coord_dir=coord, week_monday=mon)
    assert set(out) == {"alpha_brand", "beta_brand"}
    assert out["alpha_brand"]["status"] == "ready"
    assert out["alpha_brand"]["ready_count"] == 1
    assert out["alpha_brand"]["pending_count"] == 0
    assert out["alpha_brand"]["download_url"] == "https://files.example/alpha.tgz"
    assert out["beta_brand"]["status"] == "pending"
    assert out["beta_brand"]["pending_count"] == 1


def test_refresh_signal_payload_changes_when_tsv_updates(tmp_path: Path) -> None:
    """Editing the coordination TSV changes counts / status (operator refresh)."""
    c = _classifier_with_brands(tmp_path, "gamma_brand")
    coord = tmp_path / "coord"
    mon = date(2026, 5, 4)
    p = weekly_packages_tsv_path(coord, mon)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        "brand_id\tstatus\tdownload_url\tlast_updated\n"
        "gamma_brand\tpending\t\t2026-05-05T08:00:00Z\n",
        encoding="utf-8",
    )
    first = build_weekly_package_status_payload(c, coord_dir=coord, week_monday=mon)
    p.write_text(
        "brand_id\tstatus\tdownload_url\tlast_updated\n"
        "gamma_brand\tready\thttps://cdn.example/g.zip\t2026-05-05T15:00:00Z\n",
        encoding="utf-8",
    )
    second = build_weekly_package_status_payload(c, coord_dir=coord, week_monday=mon)
    assert first != second
    assert first["gamma_brand"]["status"] == "pending"
    assert second["gamma_brand"]["status"] == "ready"


def test_cli_json_reference_utc_picks_iso_week_monday_file(tmp_path: Path, capsysbinary) -> None:
    """Sunday 2026-05-10 UTC → coordination file for Monday 2026-05-04."""
    _classifier_with_brands(tmp_path, "x")
    cdir = tmp_path / "coord"
    cdir.mkdir(parents=True, exist_ok=True)
    mon = date(2026, 5, 4)
    weekly_packages_tsv_path(cdir, mon).write_text(
        "brand_id\tstatus\tdownload_url\tlast_updated\nx\tready\thttps://u\t2026-05-05T01:00:00Z\n",
        encoding="utf-8",
    )
    # Wrong week file should be ignored
    weekly_packages_tsv_path(cdir, date(2026, 5, 11)).write_text(
        "brand_id\tstatus\tdownload_url\tlast_updated\nx\terror\t\t\n",
        encoding="utf-8",
    )
    code = weekly_main(
        [
            "--json",
            "--repo-root",
            str(tmp_path),
            "--wizard-dir",
            str(tmp_path / "bw"),
            "--coord-dir",
            str(cdir),
            "--reference-utc",
            "2026-05-10T12:00:00+00:00",
        ],
    )
    assert code == 0
    raw = json.loads(capsysbinary.readouterr().out.decode("utf-8"))
    assert raw["x"]["status"] == "ready"


def test_cli_json_with_classifier_fixture(tmp_path: Path, capsysbinary) -> None:
    _classifier_with_brands(tmp_path, "x")
    cdir = tmp_path / "coord"
    cdir.mkdir(parents=True, exist_ok=True)
    mon = date(2026, 5, 4)
    weekly_packages_tsv_path(cdir, mon).write_text(
        "brand_id\tstatus\tdownload_url\tlast_updated\nx\tready\thttps://u\t2026-05-05T01:00:00Z\n",
        encoding="utf-8",
    )
    code = weekly_main(
        [
            "--json",
            "--repo-root",
            str(tmp_path),
            "--wizard-dir",
            str(tmp_path / "bw"),
            "--coord-dir",
            str(cdir),
            "--week-monday",
            "2026-05-04",
        ],
    )
    assert code == 0
    raw = json.loads(capsysbinary.readouterr().out.decode("utf-8"))
    assert raw["x"]["status"] == "ready"


def test_iso_week_monday_anchor_sunday() -> None:
    d = date(2026, 5, 10)
    assert d.weekday() == 6
    assert d - timedelta(days=d.weekday()) == date(2026, 5, 4)
