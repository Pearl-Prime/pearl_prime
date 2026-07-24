"""EPUB3 series/collection metadata (belongs-to-collection / collection-type /
group-position) — verifies build_epub() emits the OPF meta triple when
series_name is passed, and that omitting it changes nothing for non-series books.
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.release.build_epub import build_epub  # noqa: E402

_CLEAN_BOOK = """CHAPTER 1

You're at the kitchen table in scrubs still damp from shift, the pay stub and the rent bill spread out in front of you.

The anxiety is the body telling the truth about an accounting nobody has been keeping.
"""


def _opf_text(epub_path: Path) -> str:
    with zipfile.ZipFile(epub_path) as z:
        opf_name = next(n for n in z.namelist() if n.endswith(".opf"))
        return z.read(opf_name).decode("utf-8")


def _strip_volatile(opf: str) -> str:
    """Strip the dcterms:modified timestamp and dc:date so two builds diff cleanly."""
    opf = re.sub(r'<meta property="dcterms:modified">[^<]*</meta>', "", opf)
    opf = re.sub(r"<dc:date>[^<]*</dc:date>", "", opf)
    return opf


def _build(tmp_path: Path, name: str, **kwargs) -> Path:
    src = tmp_path / f"{name}.txt"
    src.write_text(_CLEAN_BOOK, encoding="utf-8")
    out = tmp_path / f"{name}.epub"
    build_epub(
        input_path=src,
        title="T",
        subtitle="S",
        author="A",
        publisher="P",
        output_path=out,
        topic="financial_anxiety",
        **kwargs,
    )
    return out


def test_series_metadata_emits_collection_triple(tmp_path: Path) -> None:
    out = _build(tmp_path, "series", series_name="The Signal Map", series_index=3)
    opf = _opf_text(out)
    assert '<meta property="belongs-to-collection" id="series-01">The Signal Map</meta>' in opf
    assert '<meta refines="#series-01" property="collection-type">series</meta>' in opf
    assert '<meta refines="#series-01" property="group-position">3</meta>' in opf


def test_series_metadata_omits_group_position_without_index(tmp_path: Path) -> None:
    out = _build(tmp_path, "series_no_index", series_name="The Signal Map")
    opf = _opf_text(out)
    assert '<meta property="belongs-to-collection" id="series-01">The Signal Map</meta>' in opf
    assert "group-position" not in opf


def test_no_series_name_produces_identical_opf_to_baseline(tmp_path: Path) -> None:
    baseline = _strip_volatile(_opf_text(_build(tmp_path, "baseline")))
    no_series = _strip_volatile(_opf_text(_build(tmp_path, "no_series", series_name="")))
    assert baseline == no_series
    assert "belongs-to-collection" not in baseline
