"""Tests for scripts/qa/validate_spine_output.py — spine-mode safety gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.qa.validate_spine_output import (
    DEFAULT_WORD_MAX,
    DEFAULT_WORD_MIN,
    SEVERITY_ERROR,
    TINY_BOOK_FLOOR,
    validate_render_dir,
)

REAL_RENDER_WITH_REPORTS = REPO_ROOT / "artifacts" / "rendered" / "ea12e1c49ba35539ecb2dc94f3aa5aeb"


def _write_render(tmp_path: Path, *, book_text: str,
                  budget: dict | None = None,
                  flow_report: dict | None = None,
                  loc_report: dict | None = None) -> Path:
    d = tmp_path / "render"
    d.mkdir()
    (d / "book.txt").write_text(book_text, encoding="utf-8")
    if budget is not None:
        (d / "budget.json").write_text(json.dumps(budget), encoding="utf-8")
    if flow_report is not None:
        (d / "chapter_flow_report.json").write_text(json.dumps(flow_report), encoding="utf-8")
    if loc_report is not None:
        (d / "location_grounding_report.json").write_text(json.dumps(loc_report), encoding="utf-8")
    return d


def test_input_missing_dir(tmp_path: Path) -> None:
    r = validate_render_dir(tmp_path / "missing")
    codes = {f.code for f in r.errors}
    assert "no_render_dir" in codes


def test_input_missing_book_txt(tmp_path: Path) -> None:
    d = tmp_path / "render"
    d.mkdir()
    r = validate_render_dir(d)
    assert any(f.code == "no_book_txt" for f in r.errors)


def test_length_below_target_errors(tmp_path: Path) -> None:
    """Below-min word count → LENGTH ERROR (above tiny floor)."""
    body = "Chapter 1\n\n" + ("the quick brown fox " * 500) + "\n\nChapter 2\n\n" + ("jumped over " * 200)
    d = _write_render(tmp_path, book_text=body, budget={
        "runtime_format_id": "standard_book",
        "word_range_target": [DEFAULT_WORD_MIN, DEFAULT_WORD_MAX],
    })
    r = validate_render_dir(d)
    err_codes = {f.code for f in r.errors}
    assert "below_target_min" in err_codes


def test_length_tiny_render_skips_strict_gate(tmp_path: Path) -> None:
    """Below tiny floor → INFO, not ERROR (smoke renders shouldn't fail loudly)."""
    body = "Chapter 1\n\nshort"
    d = _write_render(tmp_path, book_text=body, budget={"runtime_format_id": "standard_book"})
    r = validate_render_dir(d)
    err_codes = {f.code for f in r.errors}
    assert "below_target_min" not in err_codes
    info_codes = {f.code for f in r.findings if f.severity == "INFO"}
    assert "tiny_render" in info_codes


def test_chapter_flow_fail_errors(tmp_path: Path) -> None:
    body = "Chapter 1\n\n" + ("word " * 12000)
    flow = {"status": "FAIL", "chapter_count": 3, "failed_chapters": 2,
            "chapters": [
                {"chapter": 1, "errors": ["WEAK_TRANSITIONS"]},
                {"chapter": 2, "errors": ["MISSING_CLEAR_POINT"]},
            ]}
    d = _write_render(tmp_path, book_text=body, flow_report=flow)
    r = validate_render_dir(d)
    err_codes = {f.code for f in r.errors}
    assert "chapter_flow_fail" in err_codes
    # Composition signature should also fire when those specific codes appear.
    assert "linear_concat_signature" in err_codes


def test_chapter_flow_pass_no_error(tmp_path: Path) -> None:
    body = "Chapter 1\n\n" + ("word " * 12000)
    flow = {"status": "PASS", "chapter_count": 3, "failed_chapters": 0, "chapters": []}
    d = _write_render(tmp_path, book_text=body, flow_report=flow)
    r = validate_render_dir(d)
    err_codes = {f.code for f in r.errors}
    assert "chapter_flow_fail" not in err_codes
    assert "linear_concat_signature" not in err_codes


def test_template_leak_jinja_double_brace(tmp_path: Path) -> None:
    body = "Chapter 1\n\n" + ("word " * 12000) + "\n\n{{ name }} should have been substituted."
    d = _write_render(tmp_path, book_text=body)
    r = validate_render_dir(d)
    err_codes = {f.code for f in r.errors}
    assert "jinja_double_brace" in err_codes


def test_template_leak_unbalanced_curly(tmp_path: Path) -> None:
    """Catches the failure mode visible in real renders: `{Lexington Avenue ...` with no `}`."""
    body = "Chapter 1\n\n" + ("word " * 12000) + (
        "\n\nLexington Avenue is visible. {the downtown Q train brings you regularly but you're not stressed.\n"
    )
    d = _write_render(tmp_path, book_text=body)
    r = validate_render_dir(d)
    err_codes = {f.code for f in r.errors}
    assert "unbalanced_curly_brace" in err_codes


def test_template_leak_balanced_curly_skipped(tmp_path: Path) -> None:
    """Properly balanced `{ ... }` should NOT be flagged."""
    body = "Chapter 1\n\n" + ("word " * 12000) + "\n\nThe set notation { x : x > 0 } is fine.\n"
    d = _write_render(tmp_path, book_text=body)
    r = validate_render_dir(d)
    err_codes = {f.code for f in r.errors}
    assert "unbalanced_curly_brace" not in err_codes


def test_template_leak_todo_placeholder(tmp_path: Path) -> None:
    body = "Chapter 1\n\n" + ("word " * 12000) + "\n\n<TODO: write hook here>"
    d = _write_render(tmp_path, book_text=body)
    r = validate_render_dir(d)
    err_codes = {f.code for f in r.errors}
    assert "todo_placeholder" in err_codes


def test_dup_block_cross_chapter(tmp_path: Path) -> None:
    """Same paragraph appearing in 2 chapters → DUP_BLOCK ERROR."""
    repeated = (
        "The point is that the exit multiple on yourself treats every decision like a permanent "
        "threat — that is the underlying mechanism worth naming early in this chapter."
    )
    body = (
        "Chapter 1\n\n" + ("word " * 200) + "\n\n" + repeated + "\n\n" + ("word " * 200) +
        "\n\nChapter 2\n\n" + ("word " * 200) + "\n\n" + repeated + "\n\n" + ("word " * 200) +
        "\n\nChapter 3\n\n" + ("word " * 11000)
    )
    d = _write_render(tmp_path, book_text=body)
    r = validate_render_dir(d)
    err_codes = {f.code for f in r.errors}
    assert "cross_chapter_duplicates" in err_codes


def test_dup_block_short_paragraphs_ignored(tmp_path: Path) -> None:
    """Short utility lines repeating across chapters should not trip the gate."""
    body = (
        "Chapter 1\n\nYes.\n\n" + ("word " * 200) +
        "\n\nChapter 2\n\nYes.\n\n" + ("word " * 11000)
    )
    d = _write_render(tmp_path, book_text=body)
    r = validate_render_dir(d)
    err_codes = {f.code for f in r.errors}
    assert "cross_chapter_duplicates" not in err_codes


def test_clean_render_passes(tmp_path: Path) -> None:
    """A render with adequate length, PASS chapter flow, no leaks/dups → no ERRORs."""
    chapters = []
    for ch in range(1, 4):
        unique = f"Chapter {ch} unique opening line that does not repeat across other chapters."
        chapters.append(f"Chapter {ch}\n\n{unique}\n\n" + (f"chapter{ch}word " * 4000))
    body = "\n\n".join(chapters)
    flow = {"status": "PASS", "chapter_count": 3, "failed_chapters": 0, "chapters": []}
    d = _write_render(tmp_path, book_text=body, flow_report=flow,
                      budget={"runtime_format_id": "standard_book",
                              "word_range_target": [DEFAULT_WORD_MIN, DEFAULT_WORD_MAX]})
    r = validate_render_dir(d)
    assert r.passed, [f.code for f in r.errors]


@pytest.mark.skipif(not REAL_RENDER_WITH_REPORTS.is_dir(), reason="real fixture render not present")
def test_real_fixture_render_fails_with_known_signals() -> None:
    """The shipped artifacts/rendered/ea12e1c... render demonstrates every spine
    failure mode. This test pins those signals so future fixes can be validated."""
    r = validate_render_dir(REAL_RENDER_WITH_REPORTS)
    err_codes = {f.code for f in r.errors}
    assert "below_target_min" in err_codes
    assert "chapter_flow_fail" in err_codes
    assert "linear_concat_signature" in err_codes
    assert "unbalanced_curly_brace" in err_codes
    assert "cross_chapter_duplicates" in err_codes
    assert not r.passed


def test_to_dict_round_trip(tmp_path: Path) -> None:
    body = "Chapter 1\n\n" + ("word " * 12000)
    d = _write_render(tmp_path, book_text=body, flow_report={"status": "PASS"})
    r = validate_render_dir(d)
    obj = r.to_dict()
    # Must be JSON-serialisable.
    json.dumps(obj)
    assert obj["render_dir"] == str(d)
    assert "passed" in obj
    assert "metrics" in obj
    assert "findings" in obj
