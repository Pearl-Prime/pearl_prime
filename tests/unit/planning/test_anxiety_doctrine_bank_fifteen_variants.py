"""Anxiety composite doctrine bank — fifteen-variant unlock (v06–v15)."""
from __future__ import annotations

import re
from pathlib import Path

from phoenix_v4.planning.registry_resolver import (
    _load_composite_doctrine_atoms,
    _parse_canonical_txt,
)
from phoenix_v4.quality.composite_doctrine_secular_lint import lint_file

REPO = Path(__file__).resolve().parents[3]
BANK = REPO / "SOURCE_OF_TRUTH/composite_doctrine/anxiety/REFLECTION/CANONICAL.txt"
GOLDEN_V01_V05 = (
    REPO / "tests/fixtures/composite_doctrine/anxiety_reflection_v01_v05_golden.txt"
)
_BLOCK_RE = re.compile(
    r"(## COMPOSITE_DOCTRINE v(\d{2})\n---\n.*?\n---\n)",
    re.S,
)


def _blocks_by_num(text: str) -> dict[int, str]:
    return {int(m.group(2)): m.group(1) for m in _BLOCK_RE.finditer(text)}


def test_anxiety_reflection_bank_parses_fifteen_variants() -> None:
    atoms = _parse_canonical_txt(BANK, slot_type="COMPOSITE_DOCTRINE")
    ids = sorted({a["atom_id"] for a in atoms})
    assert ids == [f"COMPOSITE_DOCTRINE v{n:02d}" for n in range(1, 16)]


def test_v06_v15_word_count_band() -> None:
    atoms = _parse_canonical_txt(BANK, slot_type="COMPOSITE_DOCTRINE")
    by_id = {a["atom_id"]: a for a in atoms}
    for n in range(6, 16):
        aid = f"COMPOSITE_DOCTRINE v{n:02d}"
        wc = len(by_id[aid]["content"].split())
        assert 200 <= wc <= 380, f"{aid} has {wc} words"


def test_v01_v05_blocks_unchanged_from_main() -> None:
    golden_blocks = _blocks_by_num(GOLDEN_V01_V05.read_text(encoding="utf-8"))
    cur_blocks = _blocks_by_num(BANK.read_text(encoding="utf-8"))
    for n in range(1, 6):
        assert golden_blocks[n] == cur_blocks[n], f"v{n:02d} body drifted from main golden"


def test_secular_lint_clean_on_full_bank() -> None:
    assert lint_file(BANK) == []


def test_loader_exposes_fifteen_reflection_atoms() -> None:
    loaded = _load_composite_doctrine_atoms("anxiety", repo_root=REPO)
    pool = loaded.get("COMPOSITE_TEACHER_REFLECTION", [])
    variant_ids = {
        a["atom_id"]
        for a in pool
        if re.match(r"COMPOSITE_DOCTRINE v\d{2}$", a["atom_id"])
    }
    assert len(variant_ids) == 15
