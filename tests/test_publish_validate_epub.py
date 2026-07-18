"""Tests for scripts/publish/validate_epub.py."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from ebooklib import epub

from scripts.publish.validate_epub import (
    KDP_COVER_MIN_H,
    KDP_COVER_MIN_W,
    SEVERITY_ERROR,
    SEVERITY_WARN,
    validate_epub,
)

FIXTURE_EPUBS = sorted((REPO_ROOT / "artifacts" / "epub").glob("*.epub"))


def _build_minimal_epub(tmp_path: Path, *,
                        title: str = "Test Book",
                        lang: str = "en",
                        uid: str = "test-uid",
                        author: str | None = "Test Author",
                        cover_size: tuple[int, int] | None = (1600, 2560),
                        chapters: list[str] | None = None) -> Path:
    """Build a minimal EPUB on disk for tests; return its path."""
    book = epub.EpubBook()
    if uid:
        book.set_identifier(uid)
    if title:
        book.set_title(title)
    if lang:
        book.set_language(lang)
    if author:
        book.add_author(author)

    if cover_size is not None:
        try:
            from PIL import Image
            img = Image.new("RGB", cover_size, color=(180, 60, 20))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            book.set_cover("cover.png", buf.getvalue())
        except ImportError:
            pytest.skip("Pillow not available")

    chapter_objs = []
    chs = chapters if chapters is not None else ["<h1>One</h1><p>" + "word " * 6000 + "</p>"]
    for i, body in enumerate(chs):
        ch = epub.EpubHtml(title=f"Ch{i}", file_name=f"chap_{i}.xhtml", lang=lang)
        ch.content = f"<html><body>{body}</body></html>"
        book.add_item(ch)
        chapter_objs.append(ch)

    book.toc = tuple(chapter_objs) if chapter_objs else ()
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav", *chapter_objs]

    out = tmp_path / "test.epub"
    epub.write_epub(str(out), book)
    return out


def test_valid_epub_passes(tmp_path: Path) -> None:
    p = _build_minimal_epub(tmp_path)
    r = validate_epub(p)
    assert not r.errors, [f.code for f in r.errors]
    assert r.metadata["title"] == "Test Book"
    assert r.metadata["chapter_count"] == 1


def test_missing_cover_errors(tmp_path: Path) -> None:
    p = _build_minimal_epub(tmp_path, cover_size=None)
    r = validate_epub(p)
    codes = {f.code for f in r.errors}
    assert "missing_cover" in codes


def test_cover_below_kdp_min_errors(tmp_path: Path) -> None:
    p = _build_minimal_epub(tmp_path, cover_size=(800, 800))
    r = validate_epub(p)
    codes = {f.code for f in r.errors}
    assert "cover_below_kdp_min" in codes


def test_invalid_language_errors() -> None:
    """ebooklib normalises lang on round-trip, so call _check_metadata directly
    against a book whose language attr we set after construction."""
    from scripts.publish.validate_epub import _check_metadata, Report
    book = epub.EpubBook()
    book.set_identifier("u")
    book.set_title("T")
    book.add_author("A")
    book.set_language("en")
    book.language = "not_a_bcp47"  # bypass setter normalisation

    r = Report(path="<in-memory>")
    _check_metadata(book, r)
    codes = {f.code for f in r.errors}
    assert "invalid_language" in codes, codes


def test_low_word_count_warns(tmp_path: Path) -> None:
    p = _build_minimal_epub(tmp_path, chapters=["<p>just a few words here</p>"])
    r = validate_epub(p)
    warn_codes = {f.code for f in r.warns}
    assert "word_count_low" in warn_codes
    assert not any(f.code == "no_chapter_documents" for f in r.errors)


def test_missing_file_errors(tmp_path: Path) -> None:
    r = validate_epub(tmp_path / "nonexistent.epub")
    assert any(f.code == "file_not_found" for f in r.errors)


def test_to_dict_round_trip(tmp_path: Path) -> None:
    p = _build_minimal_epub(tmp_path)
    r = validate_epub(p)
    d = r.to_dict()
    assert d["path"] == str(p)
    assert isinstance(d["errors"], list)
    assert isinstance(d["warns"], list)
    assert isinstance(d["metadata"], dict)


@pytest.mark.skipif(not FIXTURE_EPUBS, reason="no fixture EPUBs available")
def test_real_fixture_epubs_have_kdp_cover_finding() -> None:
    """All shipped artifacts/epub/*.epub use 1024x1024 covers — flagged for KDP.

    This is a real-state regression marker: when covers are upgraded to
    KDP-compliant 1600x2560, this test should be updated to expect zero
    cover_below_kdp_min findings.
    """
    fixture = FIXTURE_EPUBS[0]
    r = validate_epub(fixture)
    codes = {f.code for f in r.errors}
    assert "cover_below_kdp_min" in codes, (
        f"Expected cover_below_kdp_min on {fixture.name}; "
        f"got errors {codes}. If covers were upgraded, update this test."
    )
