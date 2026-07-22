"""Smoke test: structural_validator.py against 5 known-good + 5 known-bad
fixtures (per Lane 01's TESTS/PROOFS requirement in
docs/agent_prompt_packs/20260721_zh_tw_translation_quality_program/
01_cursor_build_translation_quality_pipeline.md).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.localization.translation_quality.structural_validator import validate

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "translation_quality"
SOURCE_TEXT = (FIXTURES / "source_en.txt").read_text(encoding="utf-8")

GOOD_FIXTURES = sorted(FIXTURES.glob("good_*.txt"))
BAD_FIXTURES = sorted(FIXTURES.glob("bad_*.txt"))


def test_fixture_counts():
    assert len(GOOD_FIXTURES) == 5, GOOD_FIXTURES
    assert len(BAD_FIXTURES) == 5, BAD_FIXTURES


@pytest.mark.parametrize("path", GOOD_FIXTURES, ids=lambda p: p.name)
def test_good_fixtures_pass(path: Path):
    candidate_text = path.read_text(encoding="utf-8")
    result = validate(SOURCE_TEXT, candidate_text, locale="zh-CN")
    assert result.ok, f"{path.name} unexpectedly failed: {result.reasons} {result.details}"


@pytest.mark.parametrize("path", BAD_FIXTURES, ids=lambda p: p.name)
def test_bad_fixtures_fail(path: Path):
    candidate_text = path.read_text(encoding="utf-8")
    result = validate(SOURCE_TEXT, candidate_text, locale="zh-CN")
    assert not result.ok, f"{path.name} unexpectedly passed"
