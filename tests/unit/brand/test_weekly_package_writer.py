"""Unit tests for scripts.brand.weekly_package_writer."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
import textwrap

from scripts.brand.weekly_package_writer import (
    DELIVERABLE_TYPES,
    TSV_COLUMNS,
    build_tsv_rows,
    render_tsv,
    resolve_week_monday,
    write_weekly_packages,
)


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")


def _seed_catalog(tmp_path: Path, brand_id: str = "alpha_brand") -> None:
    _write(
        tmp_path / "config/brand_registry.yaml",
        f"""
        schema_version: 1
        brands:
          {brand_id}:
            lifecycle: active
            teacher_ids: [teacher_one]
        """,
    )
    _write(
        tmp_path / "config/manga/canonical_brand_list.yaml",
        f"""
        schema_version: 1
        brands:
          {brand_id}:
            tier: core
        """,
    )


def _seed_week_content(tmp_path: Path, brand_id: str, week_iso: str) -> Path:
    book = (
        tmp_path
        / "artifacts"
        / "weekly_packages"
        / brand_id
        / week_iso
        / "books"
        / "sample.txt"
    )
    book.parent.mkdir(parents=True, exist_ok=True)
    book.write_text("book body\n", encoding="utf-8")
    return book


def test_writer_tsv_columns_and_rows(tmp_path: Path) -> None:
    brand = "alpha_brand"
    _seed_catalog(tmp_path, brand)
    mon = date(2026, 5, 4)
    week_iso = "2026-W19"
    _seed_week_content(tmp_path, brand, week_iso)

    rows = build_tsv_rows(
        tmp_path,
        [brand],
        week_iso=week_iso,
        week_monday=mon,
        generated_at="2026-05-05T10:00:00Z",
    )
    assert len(rows) == len(DELIVERABLE_TYPES)
    dtypes = {r.deliverable_type for r in rows}
    assert dtypes == set(DELIVERABLE_TYPES)
    books = next(r for r in rows if r.deliverable_type == "books")
    assert books.status == "ready"
    assert books.brand_id == brand
    assert books.week_iso == week_iso

    tsv = render_tsv(rows)
    header = tsv.splitlines()[0].split("\t")
    assert header == list(TSV_COLUMNS)


def test_manifest_lists_referenced_files(tmp_path: Path) -> None:
    brand = "alpha_brand"
    _seed_catalog(tmp_path, brand)
    mon = date(2026, 5, 4)
    week_iso = "2026-W19"
    book = _seed_week_content(tmp_path, brand, week_iso)

    build_tsv_rows(
        tmp_path,
        [brand],
        week_iso=week_iso,
        week_monday=mon,
        generated_at="2026-05-05T10:00:00Z",
    )
    manifest_path = tmp_path / "artifacts/weekly_packages" / brand / week_iso / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    books_files = manifest["deliverables"]["books"]["files"]
    rel_book = book.resolve().relative_to(tmp_path.resolve()).as_posix()
    assert rel_book in books_files


def test_idempotent_tsv_on_same_monday(tmp_path: Path) -> None:
    brand = "alpha_brand"
    _seed_catalog(tmp_path, brand)
    mon = resolve_week_monday(reference_date=date(2026, 5, 7))  # Wednesday → Monday 2026-05-04

    first = write_weekly_packages(
        tmp_path,
        week_monday=mon,
        brand_ids=[brand],
        generated_at="2026-05-05T10:00:00Z",
    )
    text_a = first.read_text(encoding="utf-8")

    second = write_weekly_packages(
        tmp_path,
        week_monday=mon,
        brand_ids=[brand],
        generated_at="2026-05-05T10:00:00Z",
    )
    text_b = second.read_text(encoding="utf-8")
    assert text_a == text_b
