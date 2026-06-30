"""THE GATE — assembly path: build_epub HARD-FAILS on an unfilled stub.

#3787 wired the stub-catch into book_renderer.delivery_contract_gate +
book_quality_gate, but scripts/release/build_epub.py — the operator/pathway EPUB
packager — never invoked it (the flip pilot proved build_epub did NOT call the
delivery gate). So a stub-bearing book text could still be packaged into a
shippable EPUB. These tests prove build_epub now invokes the SAME gate before
emission: an injected stub blocks (raises / exits non-zero) and no EPUB is
written; clean text still builds.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.rendering.book_renderer import DeliveryContractError  # noqa: E402
from scripts.release.build_epub import build_epub  # noqa: E402


_STUB_BOOK = """CHAPTER 1

[Persona-specific hook for healthcare_rns × financial_anxiety]

Some chapter prose that would otherwise look fine and ship.
"""

_CLEAN_BOOK = """CHAPTER 1

You're at the kitchen table in scrubs still damp from shift, the pay stub and the rent bill spread out in front of you.

The anxiety is the body telling the truth about an accounting nobody has been keeping.
"""


def test_build_epub_blocks_injected_stub(tmp_path: Path) -> None:
    src = tmp_path / "stub_book.txt"
    src.write_text(_STUB_BOOK, encoding="utf-8")
    out = tmp_path / "stub.epub"
    with pytest.raises(DeliveryContractError):
        build_epub(
            input_path=src,
            title="T",
            subtitle="S",
            author="A",
            publisher="P",
            output_path=out,
            topic="financial_anxiety",
        )
    # Hard-fail BEFORE emission — no EPUB on disk.
    assert not out.exists()


def test_build_epub_builds_clean_book(tmp_path: Path) -> None:
    src = tmp_path / "clean_book.txt"
    src.write_text(_CLEAN_BOOK, encoding="utf-8")
    out = tmp_path / "clean.epub"
    result = build_epub(
        input_path=src,
        title="T",
        subtitle="S",
        author="A",
        publisher="P",
        output_path=out,
        topic="financial_anxiety",
    )
    assert result == out
    assert out.exists() and out.stat().st_size > 0


def test_build_epub_cli_exits_nonzero_on_stub(tmp_path: Path) -> None:
    src = tmp_path / "stub_book.txt"
    src.write_text(_STUB_BOOK, encoding="utf-8")
    out = tmp_path / "stub.epub"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/release/build_epub.py",
            "--input",
            str(src),
            "--title",
            "T",
            "--author",
            "A",
            "--output",
            str(out),
        ],
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(REPO_ROOT), "PATH": "/usr/bin:/bin", "GIT_LFS_SKIP_SMUDGE": "1"},
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode != 0, f"stub build should exit non-zero: {result.stdout}\n{result.stderr}"
    assert not out.exists()


def test_build_epub_skip_gate_escape_hatch(tmp_path: Path) -> None:
    # The documented escape hatch lets legacy fixtures bypass the gate.
    src = tmp_path / "stub_book.txt"
    src.write_text(_STUB_BOOK, encoding="utf-8")
    out = tmp_path / "stub.epub"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/release/build_epub.py",
            "--input",
            str(src),
            "--title",
            "T",
            "--author",
            "A",
            "--output",
            str(out),
        ],
        cwd=REPO_ROOT,
        env={
            "PYTHONPATH": str(REPO_ROOT),
            "PATH": "/usr/bin:/bin",
            "GIT_LFS_SKIP_SMUDGE": "1",
            "PHOENIX_EPUB_SKIP_STUB_GATE": "1",
        },
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert out.exists()
