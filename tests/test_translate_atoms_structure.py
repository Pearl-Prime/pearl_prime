"""Tests for CJK atom translation structure preservation + Ollama empty retry."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.localization.run_translation_loop import format_canonical, parse_canonical
from scripts.localization.translate_atoms_to_locale import (
    _ollama_generate,
    _translate_canonical_atom,
)


REPO = Path(__file__).resolve().parents[1]

_MINIMAL_HOOK = """## HOOK v01
---
---
English hook prose one that is long enough.
---

## HOOK v02
---
---
English hook prose two that is long enough.
---
"""


def test_parse_canonical_roundtrip_inline():
    variants = parse_canonical(_MINIMAL_HOOK)
    assert len(variants) == 2
    rebuilt = format_canonical(variants)
    assert [h for h, _, _ in variants] == ["## HOOK v01", "## HOOK v02"]
    roundtrip = parse_canonical(rebuilt)
    assert len(roundtrip) == 2
    assert roundtrip[0][2].startswith("English hook prose one")
    assert roundtrip[1][2].startswith("English hook prose two")


def test_translate_preserves_structure_and_metadata_inline():
    text = """## STORY v01
---
MECHANISM_DEPTH: 2
---
English story prose body here.
---
"""
    variants = parse_canonical(text)
    assert variants[0][1].startswith("MECHANISM_DEPTH:")

    def fake_ollama(prompt: str, ollama_url: str, model: str, num_predict: int) -> str:
        return "テスト本文です。"

    with patch(
        "scripts.localization.translate_atoms_to_locale._ollama_generate",
        side_effect=fake_ollama,
    ):
        out = _translate_canonical_atom(text, "ja-JP", "http://localhost:11434", "qwen2.5:14b")

    assert out is not None
    out_variants = parse_canonical(out)
    assert len(out_variants) == len(variants)
    for (eh, em, _), (oh, om, ob) in zip(variants, out_variants):
        assert eh == oh
        assert em == om
        assert ob == "テスト本文です。"
        assert "MECHANISM_DEPTH" in om


def test_format_empty_metadata_hook_block():
    variants = parse_canonical(_MINIMAL_HOOK)
    rebuilt = format_canonical([(h, m, "翻訳") for h, m, _ in variants])
    assert rebuilt.count("## HOOK") == len(variants)
    assert "---" in rebuilt
    assert "翻訳" in rebuilt


def _fake_urlopen_factory(responses: list[str]):
    """Build a urlopen side_effect that returns JSON Ollama payloads in order."""
    calls = {"n": 0}

    def _urlopen(req, timeout=300):  # noqa: ARG001
        idx = calls["n"]
        calls["n"] += 1
        body = json.dumps({"response": responses[idx]}).encode("utf-8")
        cm = MagicMock()
        cm.__enter__.return_value = MagicMock(read=MagicMock(return_value=body))
        cm.__exit__.return_value = False
        return cm

    return _urlopen, calls


def test_ollama_generate_retries_on_empty_completion():
    """Empty/short Ollama replies retry until a usable completion arrives."""
    urlopen, calls = _fake_urlopen_factory(["", "   ", "這是一段足夠長的繁體中文翻譯內容。"])
    with patch("scripts.localization.translate_atoms_to_locale.urllib.request.urlopen", side_effect=urlopen):
        out = _ollama_generate(
            "translate please",
            "http://127.0.0.1:11434",
            "qwen2.5:14b",
            128,
            max_retries=3,
        )
    assert out == "這是一段足夠長的繁體中文翻譯內容。"
    assert calls["n"] == 3


def test_ollama_generate_returns_none_after_exhausted_empty_retries():
    urlopen, calls = _fake_urlopen_factory(["", "", ""])
    with patch("scripts.localization.translate_atoms_to_locale.urllib.request.urlopen", side_effect=urlopen):
        out = _ollama_generate(
            "translate please",
            "http://127.0.0.1:11434",
            "qwen2.5:14b",
            128,
            max_retries=3,
        )
    assert out is None
    assert calls["n"] == 3


@pytest.mark.skipif(
    not (REPO / "atoms/educators/burnout/HOOK/CANONICAL.txt").exists(),
    reason="sparse checkout missing sample atom file",
)
def test_parse_canonical_roundtrip_hook():
    text = (REPO / "atoms/educators/burnout/HOOK/CANONICAL.txt").read_text(encoding="utf-8")
    variants = parse_canonical(text)
    assert len(variants) == 5
    rebuilt = format_canonical(variants)
    assert rebuilt.strip() == text.strip()
