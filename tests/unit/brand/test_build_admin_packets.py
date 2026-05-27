"""Unit tests for scripts.brand.build_admin_packets."""

from __future__ import annotations

import json
import zipfile
from datetime import date
from pathlib import Path

from scripts.brand.build_admin_packets import (
    build_packets,
    build_platform_zips_for_brand,
    build_zip_for_brand,
)
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


def test_platform_zip_includes_deliverable_files(tmp_path: Path) -> None:
    """Book axis MVP: per-platform ZIP must embed the actual deliverable, not
    just the platform manifest. Regression guard for stillness_press 2026-W22
    KDP wiring."""
    brand = "delta_press"
    week_iso = "2026-W22"
    pkg = tmp_path / "artifacts" / "weekly_packages"
    week_dir = pkg / brand / week_iso
    (week_dir / "kdp").mkdir(parents=True, exist_ok=True)

    epub_rel = f"artifacts/weekly_packages/{brand}/{week_iso}/kdp/{brand}_{week_iso}_kdp.epub"
    epub_path = tmp_path / epub_rel
    epub_path.write_bytes(b"PK\x03\x04epub-fixture-bytes\n")

    manifest = {
        "brand_id": brand,
        "week_iso": week_iso,
        "deliverables": {
            "books": {
                "status": "ready",
                "files": [epub_rel],
            }
        },
    }
    (week_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    built = build_platform_zips_for_brand(tmp_path, brand, week_iso, packages_dir=pkg)
    kdp_zip = pkg / brand / week_iso / "kdp" / f"{brand}_{week_iso}_kdp.zip"
    assert kdp_zip in built
    with zipfile.ZipFile(kdp_zip, "r") as zf:
        names = set(zf.namelist())
        assert "manifest.json" in names
        assert epub_rel in names, f"kdp zip missing deliverable file: {sorted(names)}"


def test_audiobook_axis_per_platform_zip(tmp_path: Path) -> None:
    """AMENDMENT-2026-05-27 §3 audiobook axis: M4B under ``<brand>/<week>/audiobook/``
    must be discovered and emitted into per-platform ZIPs for both ``audible`` and
    ``google_play_audiobook`` slugs via the split-at-build packager (OPD-145)."""
    brand = "delta_brand"
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
    audiobook_dir = tmp_path / "artifacts/weekly_packages" / brand / week_iso / "audiobook"
    audiobook_dir.mkdir(parents=True, exist_ok=True)
    m4b = audiobook_dir / f"{brand}_{week_iso}_audiobook.m4b"
    cue = audiobook_dir / f"{brand}_{week_iso}_audiobook.cue"
    m4b.write_bytes(b"\x00\x00\x00\x18ftypM4B \x00\x00\x00\x00")  # minimal MP4 ftyp atom
    cue.write_text("FILE \"x.m4b\" MP4\n", encoding="utf-8")

    write_weekly_packages(
        tmp_path, week_monday=mon, brand_ids=[brand], generated_at="2026-05-05T12:00:00Z"
    )

    # The writer should discover and mark audiobook as ready.
    manifest = json.loads(
        (tmp_path / "artifacts/weekly_packages" / brand / week_iso / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    ab_block = manifest["deliverables"]["audiobook"]
    assert ab_block["status"] == "ready"
    ab_rels = set(ab_block["files"])
    assert any(p.endswith("_audiobook.m4b") for p in ab_rels)
    assert any(p.endswith("_audiobook.cue") for p in ab_rels)

    built = build_packets(tmp_path, week_monday=mon)
    assert brand in built

    # Both audible + google_play_audiobook per-platform ZIPs must contain the M4B.
    for platform in ("audible", "google_play_audiobook"):
        platform_zip = (
            tmp_path
            / "artifacts/weekly_packages"
            / brand
            / week_iso
            / platform
            / f"{brand}_{week_iso}_{platform}.zip"
        )
        assert platform_zip.is_file(), f"missing per-platform ZIP for {platform}"
        with zipfile.ZipFile(platform_zip, "r") as zf:
            names = set(zf.namelist())
            assert "manifest.json" in names
            plat_manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
            assert plat_manifest["platform"] == platform
            assert plat_manifest["deliverable_type"] == "audiobook"


def test_platform_zip_includes_manga_deliverable_for_all_manga_platforms(
    tmp_path: Path,
) -> None:
    """Manga axis MVP: per-platform ZIPs for ALL THREE manga platform slugs
    (WEBTOON, LINE Manga, Piccoma) must embed the rendered manga deliverable
    files (e.g. manga.pdf + manga.png) referenced under
    ``deliverables.manga_panels.files``. Regression guard for stillness_press
    2026-W22 WEBTOON wiring."""
    brand = "epsilon_press"
    week_iso = "2026-W22"
    pkg = tmp_path / "artifacts" / "weekly_packages"
    week_dir = pkg / brand / week_iso
    week_dir.mkdir(parents=True, exist_ok=True)
    (week_dir / "README.txt").write_text("test readme\n", encoding="utf-8")

    # Two real deliverable files on disk (KDP-style PDF and WEBTOON-style PNG).
    pdf_rel = f"artifacts/weekly_packages/{brand}/{week_iso}/kdp/{brand}_{week_iso}_manga.pdf"
    png_rel = f"artifacts/weekly_packages/{brand}/{week_iso}/webtoon/{brand}_{week_iso}_manga.png"
    for rel in (pdf_rel, png_rel):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"manga-deliverable-fixture\n")

    manifest = {
        "brand_id": brand,
        "week_iso": week_iso,
        "deliverables": {
            "manga_panels": {
                "status": "ready",
                "files": [pdf_rel, png_rel],
            }
        },
    }
    (week_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    built = build_platform_zips_for_brand(tmp_path, brand, week_iso, packages_dir=pkg)
    built_platforms = {p.parent.name for p in built}
    assert {"webtoon", "line_manga", "piccoma"}.issubset(
        built_platforms
    ), f"expected all 3 manga platforms; got {sorted(built_platforms)}"

    webtoon_zip = next(p for p in built if p.parent.name == "webtoon")
    with zipfile.ZipFile(webtoon_zip, "r") as zf:
        names = set(zf.namelist())
        assert "manifest.json" in names
        assert pdf_rel in names, f"webtoon zip missing pdf: {sorted(names)}"
        assert png_rel in names, f"webtoon zip missing png: {sorted(names)}"
