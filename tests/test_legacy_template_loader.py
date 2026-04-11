"""Tests for phoenix_v4.planning.legacy_template_loader."""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.planning.legacy_template_loader import (
    estimate_legacy_library_words,
    load_chapter_bridge,
    load_legacy_section,
    load_legacy_template_index,
    load_transition_bridge_for_chapter_start,
    parse_chapter_bridges_markdown,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_load_index():
    data = load_legacy_template_index(repo_root=REPO_ROOT)
    assert data.get("schema_version") == 1
    assert "libraries" in data
    assert "v4_therapeutic" in (data.get("libraries") or {})


def test_load_fixture_section(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_index(*_a, **_k):
        return {
            "libraries": {
                "fixture_v4": {
                    "path": "tests/fixtures/legacy_template/minimal_v4",
                }
            }
        }

    monkeypatch.setattr(
        "phoenix_v4.planning.legacy_template_loader.load_legacy_template_index",
        fake_index,
    )
    sec = load_legacy_section("fixture_v4", 1, 1, "F1", repo_root=REPO_ROOT)
    assert sec.word_count > 40
    assert "false alarm" in sec.text.lower()
    assert not sec.warnings or all("section_yaml_not_found" not in w for w in sec.warnings)


def test_parse_chapter_bridge():
    sample = """
**CHAPTER 1 - BRIDGES**
*Chapter Conclusion:* "Alpha conclusion here."
*Next Chapter Bridge:* "Beta next bridge here."

**CHAPTER 2 - BRIDGES**
*Chapter Conclusion:* "Gamma."
*Next Chapter Bridge:* "Delta."
"""
    blocks = parse_chapter_bridges_markdown(sample)
    assert blocks[1]["conclusion"] == "Alpha conclusion here."
    assert blocks[1]["next_bridge"] == "Beta next bridge here."
    assert blocks[2]["next_bridge"] == "Delta."


def test_load_chapter_bridge_integration():
    text = load_chapter_bridge(
        1,
        repo_root=REPO_ROOT,
        bridges_path="tests/fixtures/legacy_template/chapter_bridges_sample.md",
    )
    assert text
    assert "Chapter Conclusion" not in text  # stripped to quoted body only in fn
    # Combined conclusion + next bridge
    assert "recognition" in text.lower() or "journey" in text.lower()


def test_transition_bridge_chapter_start():
    t = load_transition_bridge_for_chapter_start(
        2,
        repo_root=REPO_ROOT,
        bridges_path="tests/fixtures/legacy_template/chapter_bridges_sample.md",
    )
    assert t
    assert "next chapter" in t.lower() or "chapter" in t.lower()


def test_missing_library_returns_warning():
    sec = load_legacy_section("nonexistent_lib___", 1, 1, repo_root=REPO_ROOT)
    assert sec.text == ""
    assert any("unknown_library" in w for w in sec.warnings)


def test_word_estimate_hooks_code(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_index(*_a, **_k):
        return {
            "libraries": {
                "hooks_code": {
                    "path": "tests/fixtures/legacy_template/hooks_wordy.txt",
                }
            }
        }

    monkeypatch.setattr(
        "phoenix_v4.planning.legacy_template_loader.load_legacy_template_index",
        fake_index,
    )
    w = estimate_legacy_library_words("hooks_code", repo_root=REPO_ROOT)
    assert w > 500


def test_word_estimate_missing_v4():
    w = estimate_legacy_library_words("v4_therapeutic", repo_root=REPO_ROOT)
    assert w == 0
