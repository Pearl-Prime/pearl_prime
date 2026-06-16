"""Per-brand Pearl_News slice mapping for weekly_package_writer (OPD-119 followup)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
import textwrap

from scripts.brand.weekly_package_writer import (
    _ArtifactIndex,
    build_tsv_rows,
    materialize_pearl_news_slice,
    week_iso_label,
)


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")


def _seed_brand_matrix(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/catalog_planning/brand_teacher_matrix.yaml",
        """
        brands:
          with_news:
            teachers: [ahjan]
          no_news:
            teachers: [miyuki]
        """,
    )
    _write(
        tmp_path / "config/brand_registry.yaml",
        """
        schema_version: 1
        brands:
          with_news:
            lifecycle: active
          no_news:
            lifecycle: active
          unmapped:
            lifecycle: active
        """,
    )
    _write(
        tmp_path / "config/manga/canonical_brand_list.yaml",
        """
        schema_version: 1
        brands:
          with_news:
            tier: core
          no_news:
            tier: core
          unmapped:
            tier: core
        """,
    )


def _seed_published_article(tmp_path: Path, *, day: str, teacher: str, name: str) -> Path:
    article = (
        tmp_path
        / "artifacts"
        / "pearl_news"
        / "published"
        / day
        / "morning"
        / teacher
        / name
    )
    article.parent.mkdir(parents=True, exist_ok=True)
    article.write_text('{"teacher_id": "%s"}\n' % teacher, encoding="utf-8")
    return article


def test_pearl_news_mapped_per_brand_and_pending_without_content(tmp_path: Path) -> None:
    _seed_brand_matrix(tmp_path)
    mon = date(2026, 5, 18)
    week_iso = week_iso_label(mon)
    _seed_published_article(
        tmp_path, day="2026-05-19", teacher="ahjan", name="article_ready.json"
    )
    _seed_published_article(
        tmp_path, day="2026-05-10", teacher="junko", name="article_outside_week.json"
    )

    index = _ArtifactIndex.build(tmp_path, mon)
    with_files = materialize_pearl_news_slice(
        tmp_path, "with_news", week_iso=week_iso, index=index
    )
    assert len(with_files) == 1
    assert with_files[0].endswith("2026-05-19/morning/ahjan/article_ready.json")
    slice_path = tmp_path / with_files[0]
    assert slice_path.is_file()

    no_files = materialize_pearl_news_slice(
        tmp_path, "no_news", week_iso=week_iso, index=index
    )
    assert no_files == []

    rows = build_tsv_rows(
        tmp_path,
        ["with_news", "no_news", "unmapped"],
        week_iso=week_iso,
        week_monday=mon,
        generated_at="2026-05-20T12:00:00Z",
    )
    by_brand = {
        (r.brand_id, r.deliverable_type): r
        for r in rows
        if r.deliverable_type == "pearl_news"
    }
    ready = by_brand[("with_news", "pearl_news")]
    assert ready.status == "ready"
    assert ready.download_url == ""
    assert ready.last_updated == "2026-05-20T12:00:00Z"

    pending = by_brand[("no_news", "pearl_news")]
    assert pending.status == "pending"
    assert pending.download_url == ""
    assert pending.last_updated == mon.isoformat()

    unmapped = by_brand[("unmapped", "pearl_news")]
    assert unmapped.status == "pending"
    assert unmapped.last_updated == mon.isoformat()

    manifest = json.loads(
        (tmp_path / "artifacts/weekly_packages/with_news" / week_iso / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    pearl_files = manifest["deliverables"]["pearl_news"]["files"]
    assert pearl_files == with_files
    assert manifest["deliverables"]["pearl_news"]["status"] == "ready"
