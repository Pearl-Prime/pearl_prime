"""Slot-role schema acceptance for mindfulness/adhd_focus style banks."""
from __future__ import annotations

from pathlib import Path

from phoenix_v4.planning.assembly_compiler import (
    _parse_canonical_txt,
    validate_canonical_atom_file,
)
from scripts.localization.validate_cjk_atom import validate_locale_atom

REPO = Path(__file__).resolve().parents[1]


_SLOT_PIVOT = """## PIVOT v01
---
---
Your mind is drafting the parent email during silent reading.
---

## PIVOT v05
---
---
Notice the rehearsal, then set it down and ask what is actually happening.
---

## PIVOT v12
---
---
Scan actual faces at your next checkpoint before independent work.
---
"""


def test_slot_pivot_schema_accepts_v05_plus(tmp_path: Path):
    path = tmp_path / "atoms" / "educators" / "mindfulness" / "PIVOT" / "CANONICAL.txt"
    path.parent.mkdir(parents=True)
    path.write_text(_SLOT_PIVOT, encoding="utf-8")

    # Point helpers at tmp tree by writing under real-looking relative structure via chdir
    # is fragile; instead invoke validators on absolute path (bank detection uses "atoms" segment).
    errs = validate_canonical_atom_file(path)
    assert errs == [], errs
    atoms = _parse_canonical_txt(path)
    assert [a["role"] for a in atoms] == ["PIVOT", "PIVOT", "PIVOT"]
    assert all(a["role"] == "PIVOT" for a in atoms)


def test_locale_slot_pivot_validate_locale_atom(tmp_path: Path, monkeypatch):
    # Build under repo atoms/ so relative-to-REPO paths work for validate_locale_atom.
    locale_dir = (
        REPO
        / "atoms"
        / "_tmp_schema_fixture"
        / "mindfulness"
        / "PIVOT"
        / "locales"
        / "zh-TW"
    )
    locale_dir.mkdir(parents=True, exist_ok=True)
    path = locale_dir / "CANONICAL.txt"
    path.write_text(_SLOT_PIVOT, encoding="utf-8")
    try:
        ok, reasons = validate_locale_atom(path)
        assert ok, reasons
        assert reasons == []
    finally:
        path.unlink(missing_ok=True)
        # best-effort cleanup of empty fixture dirs
        for p in [locale_dir, locale_dir.parent, locale_dir.parent.parent, locale_dir.parent.parent.parent, locale_dir.parent.parent.parent.parent]:
            try:
                p.rmdir()
            except OSError:
                break


def test_story_engine_still_requires_path(tmp_path: Path):
    path = tmp_path / "atoms" / "educators" / "anxiety" / "overwhelm" / "CANONICAL.txt"
    path.parent.mkdir(parents=True)
    path.write_text(
        """## RECOGNITION v01
---
BAND: 1
---
Prose without a path line should still fail for story engines.
---
""",
        encoding="utf-8",
    )
    errs = validate_canonical_atom_file(path)
    assert any("missing path" in e for e in errs)
