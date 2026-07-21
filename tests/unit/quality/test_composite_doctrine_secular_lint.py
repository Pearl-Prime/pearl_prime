"""OPD-115 Phase B: composite_doctrine secular lint."""
from __future__ import annotations

from pathlib import Path

from phoenix_v4.quality.composite_doctrine_secular_lint import (
    REQUIRED_TEACHING_PARAGRAPHS,
    lint_canonical_file,
    lint_composite_doctrine_tree,
    lint_file,
)


def test_deity_name_rejected(tmp_path: Path) -> None:
    path = tmp_path / "CANONICAL.txt"
    path.write_text("She turned to the Buddha for comfort.\n", encoding="utf-8")
    hits = lint_file(path)
    assert any(v.matched_tell == "buddha" for v in hits)


def test_lineage_reference_rejected(tmp_path: Path) -> None:
    path = tmp_path / "CANONICAL.txt"
    path.write_text("As the buddha taught, notice the breath.\n", encoding="utf-8")
    hits = lint_file(path)
    assert any("as the buddha taught" in v.matched_tell for v in hits)


def test_translated_equivalents_allowed(tmp_path: Path) -> None:
    path = tmp_path / "CANONICAL.txt"
    path.write_text(
        "Notice suffering, no fixed self, awareness and presence. Return to noticing.\n",
        encoding="utf-8",
    )
    assert lint_file(path) == []


def test_allowlist_bypass(tmp_path: Path) -> None:
    path = tmp_path / "CANONICAL.txt"
    path.write_text("Channeling light from within.\n", encoding="utf-8")
    allow_path = tmp_path / "allow.yaml"
    allow_path.write_text("allowlist:\n  - channeling\n", encoding="utf-8")
    hits = lint_file(path, allowlist={"channeling"})
    assert hits == []


def test_capitalized_yoga_rejected(tmp_path: Path) -> None:
    path = tmp_path / "CANONICAL.txt"
    path.write_text("Her Yoga practice began at dawn.\n", encoding="utf-8")
    hits = lint_file(path)
    assert any("yoga" in v.matched_tell for v in hits)


def test_lowercase_yoga_adjective_allowed(tmp_path: Path) -> None:
    path = tmp_path / "CANONICAL.txt"
    path.write_text("A yoga mat under her feet.\n", encoding="utf-8")
    assert lint_file(path) == []


def test_lint_tree_finds_nested_canonical(tmp_path: Path) -> None:
    root = tmp_path / "composite_doctrine" / "anxiety"
    (root / "REFLECTION").mkdir(parents=True)
    (root / "CANONICAL.txt").write_text("Krishna imagery here.\n", encoding="utf-8")
    (root / "REFLECTION" / "CANONICAL.txt").write_text("Clean secular reflection.\n", encoding="utf-8")
    hits = lint_composite_doctrine_tree(root=tmp_path / "composite_doctrine")
    assert len(hits) == 1
    assert hits[0].matched_tell == "krishna"


def _three_para_secular_block() -> str:
    return (
      "## COMPOSITE_DOCTRINE v01\n"
      "---\n"
      "---\n"
      "First teaching paragraph with enough secular prose.\n\n"
      "Second teaching paragraph stays in ordinary language.\n\n"
      "Third teaching paragraph closes without religious framing.\n"
      "---\n"
  )


def _two_para_block() -> str:
    return (
        "## COMPOSITE_DOCTRINE v01\n"
        "---\n"
        "---\n"
        "Only one teaching paragraph here.\n\n"
        "And a second — still one short of the ruling.\n"
        "---\n"
    )


def test_shape_two_paragraph_fixture_rejected(tmp_path: Path) -> None:
    path = tmp_path / "CANONICAL.txt"
    path.write_text(_two_para_block(), encoding="utf-8")
    hits = lint_canonical_file(path)
    shape_hits = [v for v in hits if v.matched_tell.startswith("shape:")]
    assert len(shape_hits) == 1
    assert shape_hits[0].atom_id == "COMPOSITE_DOCTRINE v01"
    assert f"expected {REQUIRED_TEACHING_PARAGRAPHS}" in shape_hits[0].matched_tell


def test_shape_three_paragraph_secular_fixture_passes(tmp_path: Path) -> None:
    path = tmp_path / "CANONICAL.txt"
    path.write_text(_three_para_secular_block(), encoding="utf-8")
    assert lint_canonical_file(path) == []


def test_lint_file_secular_only_skips_shape(tmp_path: Path) -> None:
    """lint_file() remains secular-only for backward-compatible call sites."""
    path = tmp_path / "CANONICAL.txt"
    path.write_text(_two_para_block(), encoding="utf-8")
    assert lint_file(path) == []
