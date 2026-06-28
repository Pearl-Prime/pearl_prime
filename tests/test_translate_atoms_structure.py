"""Tests for CJK atom translation structure preservation."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.localization.run_translation_loop import format_canonical, parse_canonical
from scripts.localization.translate_atoms_to_locale import _translate_canonical_atom


REPO = Path(__file__).resolve().parents[1]


def test_parse_canonical_roundtrip_hook():
    text = (REPO / "atoms/educators/burnout/HOOK/CANONICAL.txt").read_text(encoding="utf-8")
    variants = parse_canonical(text)
    assert len(variants) == 5
    rebuilt = format_canonical(variants)
    assert rebuilt.strip() == text.strip()


def test_translate_preserves_structure_and_metadata():
    text = (REPO / "atoms/midlife_women/anxiety/STORY/CANONICAL.txt").read_text(encoding="utf-8")
    variants = parse_canonical(text)
    assert variants[0][1].startswith("MECHANISM_DEPTH:")

    def fake_ollama(prompt: str, ollama_url: str, model: str, num_predict: int) -> str:
        # Return fixed CJK placeholder for prose-only segment
        return "テスト本文です。"

    with patch(
        "scripts.localization.translate_atoms_to_locale._ollama_generate",
        side_effect=fake_ollama,
    ):
        out = _translate_canonical_atom(text, "ja-JP", "http://localhost:11434", "qwen3:14b")

    assert out is not None
    out_variants = parse_canonical(out)
    assert len(out_variants) == len(variants)
    for (eh, em, _), (oh, om, ob) in zip(variants, out_variants):
        assert eh == oh
        assert em == om
        assert ob == "テスト本文です。"
        assert "MECHANISM_DEPTH" in om


def test_format_empty_metadata_hook_block():
    text = (REPO / "atoms/educators/burnout/HOOK/CANONICAL.txt").read_text(encoding="utf-8")
    variants = parse_canonical(text)
    rebuilt = format_canonical([(h, m, "翻訳") for h, m, _ in variants])
    assert rebuilt.count("## HOOK") == len(variants)
    assert "---" in rebuilt
    assert "翻訳" in rebuilt
