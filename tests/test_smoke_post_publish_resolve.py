from __future__ import annotations

from pathlib import Path

from scripts.manga.smoke_post_publish import resolve_exports_dir


def test_resolve_exports_prefers_direct_exports(tmp_path: Path) -> None:
    d = tmp_path / "exports"
    d.mkdir()
    (d / "a.pdf").write_text("x")
    assert resolve_exports_dir(tmp_path) == d


def test_resolve_exports_nested_chapter(tmp_path: Path) -> None:
    (tmp_path / "chapter_001" / "exports").mkdir(parents=True)
    (tmp_path / "chapter_001" / "exports" / "x.pdf").write_text("x")
    assert resolve_exports_dir(tmp_path) == tmp_path / "chapter_001" / "exports"
