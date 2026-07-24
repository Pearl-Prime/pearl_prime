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


def test_locked_glossary_term_drift_is_caught(tmp_path, monkeypatch):
    """Regression test for 2026-07-23 wave1/shard04: DashScope rendered
    "compassion fatigue" as the plausible-but-undocumented 同情疲勞 instead
    of the glossary-locked 共情耗竭. That string was never in anyone's
    `avoid` list, so the old avoid-list-only check passed it silently.
    """
    import scripts.localization.translation_quality.structural_validator as sv

    adir = tmp_path / "zh_cn"
    adir.mkdir()
    (adir / "glossary_project.yaml").write_text(
        """
terms:
  - source: "compassion fatigue"
    preferred_by_context:
      title_or_header: 共情耗竭
      narrative_body: 共情耗竭
    avoid: ["同情心疲勞", "慈悲疲勞"]
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(sv, "_analysis_dir", lambda locale: adir if locale == "zh-CN" else None)

    source = "## HOOK v01\ncompassion fatigue is real.\n"
    drifted_candidate = "## HOOK v01\n同情疲劳是真实的。\n"  # undocumented synonym, not in avoid list
    locked_candidate = "## HOOK v01\n共情耗竭是真实的。\n"

    drifted = sv.validate(source, drifted_candidate, locale="zh-CN")
    assert not drifted.ok
    block_reasons = drifted.details.get("per_block_failures", {}).get("HOOK_v01", [])
    assert any("glossary_preferred_term_missing" in r for r in block_reasons), block_reasons

    locked = sv.validate(source, locked_candidate, locale="zh-CN")
    assert locked.ok, f"unexpectedly failed: {locked.reasons} {locked.details}"
