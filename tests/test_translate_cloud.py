"""Unit tests for scripts/translate_atoms_all_locales_cloud.py (CJK6 bestseller translation)."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Import module under test (script lives at repo root scripts/)
sys.path.insert(0, str(REPO_ROOT))
from scripts import translate_atoms_all_locales_cloud as tac  # noqa: E402


def test_parse_canonical_real_file() -> None:
    path = REPO_ROOT / "atoms/corporate_managers/anxiety/PIVOT/CANONICAL.txt"
    text = path.read_text(encoding="utf-8")
    variants = tac.parse_canonical(text)
    assert len(variants) == 20
    h0, _meta0, p0 = variants[0]
    assert h0 == "## PIVOT v01"
    assert "reorg" in p0.lower() or "threat" in p0.lower()


def test_format_output_roundtrip() -> None:
    path = REPO_ROOT / "atoms/corporate_managers/anxiety/PIVOT/CANONICAL.txt"
    original = path.read_text(encoding="utf-8")
    v = tac.parse_canonical(original)
    rebuilt = tac.format_canonical(v)
    v2 = tac.parse_canonical(rebuilt)
    assert v2 == v


def test_format_output_translated_prose() -> None:
    src = REPO_ROOT / "atoms/corporate_managers/anxiety/PIVOT/CANONICAL.txt"
    variants = tac.parse_canonical(src.read_text(encoding="utf-8"))
    fake = [(h, m, "JA " + p) for h, m, p in variants]
    out = tac.format_canonical(fake)
    assert "## PIVOT v01" in out
    assert "JA " in out
    assert out.count("## PIVOT") == 20


def test_validation_ok() -> None:
    src = REPO_ROOT / "atoms/educators/anxiety/PIVOT/CANONICAL.txt"
    variants = tac.parse_canonical(src.read_text(encoding="utf-8"))
    ja = [(h, m, "（日本語）" + p) for h, m, p in variants]
    out = tac.format_canonical(ja)
    ok, msg = tac.validate_translation(variants, out)
    assert ok and msg == "ok"


def test_validation_wrong_count() -> None:
    src = REPO_ROOT / "atoms/educators/anxiety/PIVOT/CANONICAL.txt"
    variants = tac.parse_canonical(src.read_text(encoding="utf-8"))[:5]
    out = tac.format_canonical(variants)
    full = tac.parse_canonical(src.read_text(encoding="utf-8"))
    ok, msg = tac.validate_translation(full, out)
    assert not ok
    assert "variant count" in msg.lower()


def test_validation_empty_prose(monkeypatch: pytest.MonkeyPatch) -> None:
    """Empty prose is rejected; parse of malformed output may vary — stub parsed output."""
    src = [
        ("## PIVOT v01", "English one"),
        ("## PIVOT v02", "English two"),
    ]

    def fake_parse(_text: str) -> list[tuple[str, str]]:
        return [("## PIVOT v01", ""), ("## PIVOT v02", "ok")]

    monkeypatch.setattr(tac, "parse_canonical", fake_parse)
    ok, msg = tac.validate_translation(src, "dummy")
    assert not ok
    assert "empty" in msg.lower()


def test_validation_identical_to_english() -> None:
    src = REPO_ROOT / "atoms/educators/anxiety/PIVOT/CANONICAL.txt"
    variants = tac.parse_canonical(src.read_text(encoding="utf-8"))
    ok, msg = tac.validate_translation(variants, tac.format_canonical(variants))
    # Identical prose should fail (same as English)
    assert not ok
    assert "identical" in msg.lower()


def test_discover_atoms_educators() -> None:
    manifest = tac.discover_atoms(REPO_ROOT / "atoms", persona="educators")
    assert len(manifest) == 8 * 5  # 8 topics × 5 slots
    slots = {m[2] for m in manifest}
    assert slots == set(tac.SLOT_TYPES)


def test_dry_run_no_api(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    argv = [
        "translate_atoms_all_locales_cloud.py",
        "--persona",
        "educators",
        "--locale",
        "ja-JP",
        "--dry-run",
    ]
    with patch.object(sys, "argv", argv):
        code = tac.main()
    assert code == 0
    out = capsys.readouterr().out
    assert "40 files" in out
    assert "800 variants" in out
    assert "educators/anxiety/PIVOT" in out
