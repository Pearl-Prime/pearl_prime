"""Tests for phoenix_v4/quality/memorable_line_gate.py (BG-PR-10)."""
from __future__ import annotations

import logging
from pathlib import Path

import pytest

from phoenix_v4.quality.memorable_line_gate import (
    MemorableLineResult,
    evaluate_memorable_lines,
    load_memorable_line_policy,
    score_sentence,
)


def _policy_path(tmp_path: Path, block_on_violation: bool) -> Path:
    p = tmp_path / "memorable_line_registry_policy.yaml"
    p.write_text(
        """
memorable_line_registry:
  max_occurrences_global: 2
  block_on_violation: {block}
  strength_levels_tracked: [good, great]
""".replace("{block}", str(block_on_violation).lower()),
 encoding="utf-8",
    )
    return p


def test_strong_lines_pass_with_candidates() -> None:
    text = (
        "Your anxiety is not the problem. "
        "Your solution to it is. "
        "The habit loop tightens until your chest believes the alarm is the only truth."
    )
    r = evaluate_memorable_lines(text, policy_path=Path("/___nonexistent___/policy.yaml"))
    assert r.status == "PASS"
    assert r.memorable_line_count >= 1
    assert len(r.best_candidates) >= 1
    assert any("not the problem" in c.lower() for c in r.best_candidates)


def test_generic_prose_fails_when_block_true(tmp_path: Path) -> None:
    text = (
        "Things can be difficult sometimes. "
        "People often struggle with various challenges in life. "
        "It might be that situations are generally hard for everyone."
    )
    p = _policy_path(tmp_path, True)
    r = evaluate_memorable_lines(text, policy_path=p)
    assert r.status == "FAIL"
    assert r.memorable_line_count == 0
    assert "NO_MEMORABLE_LINE_CANDIDATES" in r.issues


def test_generic_prose_warns_when_block_false(tmp_path: Path) -> None:
    text = (
        "Things can be difficult sometimes. "
        "People often struggle with various challenges in life. "
        "It might be that situations are generally hard for everyone."
    )
    p = _policy_path(tmp_path, False)
    r = evaluate_memorable_lines(text, policy_path=p)
    assert r.status == "WARN"
    assert r.memorable_line_count == 0


def test_missing_policy_file_warns_no_crash(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)
    bogus = Path("/nonexistent/memorable_line_registry_policy.yaml")
    policy, warns = load_memorable_line_policy(bogus)
    assert "memorable_line_registry" in policy
    assert any("missing" in w.lower() or "nonexistent" in w.lower() for w in warns)
    assert any("memorable_line_policy" in r.message.lower() for r in caplog.records)
    r = evaluate_memorable_lines("Your fear is not the verdict.", policy_path=bogus)
    assert isinstance(r, MemorableLineResult)
    assert r.metrics.get("block_on_violation") is True


def test_deterministic_same_input() -> None:
    text = "Your fear is not the verdict. Your nervous system is asking a question."
    a = evaluate_memorable_lines(text, policy_path=Path("/nope/policy.yaml"))
    b = evaluate_memorable_lines(text, policy_path=Path("/nope/policy.yaml"))
    assert a.status == b.status
    assert a.memorable_line_count == b.memorable_line_count
    assert a.best_candidates == b.best_candidates
    assert a.metrics.get("candidate_count") == b.metrics.get("candidate_count")


def test_best_candidates_sorted_by_score_descending(tmp_path: Path) -> None:
    p = _policy_path(tmp_path, True)
    text = (
        "The real cost is what you call clarity. "
        "Your hands know before your story does. "
        "Still here."
    )
    r = evaluate_memorable_lines(text, policy_path=p)
    assert r.status == "PASS"
    assert len(r.best_candidates) <= 3
    max_w = int(r.metrics.get("max_words_per_candidate") or 20)
    scores = [score_sentence(s, max_w)[0] for s in r.best_candidates]
    assert scores == sorted(scores, reverse=True)
