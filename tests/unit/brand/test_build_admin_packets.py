"""Unit tests for scripts.brand.build_admin_packets."""

from __future__ import annotations

import json
import zipfile
from datetime import date
from pathlib import Path

from scripts.brand.build_admin_packets import build_packets, build_zip_for_brand
from scripts.brand.weekly_package_writer import render_tsv, write_weekly_packages


def test_build_zip_from_tsv(tmp_path: Path) -> None:
    brand = "beta_brand"
    mon = date(2026, 5, 4)
    week_iso = "2026-W19"

    coord = tmp_path / "coord"
    pkg = tmp_path / "packages"
    book = pkg / brand / week_iso / "books" / "title.txt"
    book.parent.mkdir(parents=True, exist_ok=True)
    book.write_text("hello\n", encoding="utf-8")

    manifest = {
        "brand_id": brand,
        "week_iso": week_iso,
        "deliverables": {
            "books": {
                "status": "ready",
                "files": [book.resolve().relative_to(tmp_path.resolve()).as_posix()],
            }
        },
    }
    (pkg / brand / week_iso / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    from scripts.brand.weekly_package_writer import TsvRow

    rows = [
        TsvRow(brand, week_iso, "books", "ready", "", "2026-05-05T10:00:00Z"),
    ]
    from scripts.brand.weekly_package_endpoint import weekly_packages_tsv_path

    tsv_path = weekly_packages_tsv_path(coord, mon)
    tsv_path.parent.mkdir(parents=True, exist_ok=True)
    tsv_path.write_text(render_tsv(rows), encoding="utf-8")

    built = build_packets(
        tmp_path,
        coord_dir=coord,
        packages_dir=pkg,
        week_monday=mon,
    )
    assert brand in built
    zip_path = tmp_path / built[brand]
    assert zip_path.is_file()
    assert zip_path.stat().st_size > 0

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())
        assert "manifest.json" in names
        rel = book.resolve().relative_to(tmp_path.resolve()).as_posix()
        assert rel in names


def test_end_to_end_writer_then_builder(tmp_path: Path) -> None:
    brand = "gamma_brand"
    (tmp_path / "config/manga").mkdir(parents=True, exist_ok=True)
    (tmp_path / "config/brand_registry.yaml").write_text(
        f"schema_version: 1\nbrands:\n  {brand}:\n    lifecycle: active\n",
        encoding="utf-8",
    )
    (tmp_path / "config/manga/canonical_brand_list.yaml").write_text(
        f"schema_version: 1\nbrands:\n  {brand}:\n    tier: core\n",
        encoding="utf-8",
    )

    mon = date(2026, 5, 4)
    week_iso = "2026-W19"
    book = tmp_path / "artifacts/weekly_packages" / brand / week_iso / "books" / "x.txt"
    book.parent.mkdir(parents=True, exist_ok=True)
    book.write_text("z\n", encoding="utf-8")

    write_weekly_packages(tmp_path, week_monday=mon, brand_ids=[brand], generated_at="2026-05-05T12:00:00Z")

    built = build_packets(tmp_path, week_monday=mon)
    assert brand in built
    zip_path, _ = build_zip_for_brand(tmp_path, brand, week_iso)
    assert zip_path is not None
    assert zip_path.stat().st_size > 0
