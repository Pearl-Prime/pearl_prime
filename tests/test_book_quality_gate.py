"""Tests for Pearl Prime book_quality_gate (deterministic release bands)."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "book_quality_gate"


def _read(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_reject_artifact_leakage() -> None:
    from phoenix_v4.quality.book_quality_gate import evaluate_book_quality

    rep = evaluate_book_quality(
        _read("reject_artifact_leakage.txt"),
        runtime_format_id="short_book_30",
        frame="spiritual_first",
    )
    assert rep.release_band == "Reject"
    assert "artifact_leakage" in rep.fail_reasons


def test_reject_verbatim_duplicate_blocks() -> None:
    from phoenix_v4.quality.book_quality_gate import evaluate_book_quality

    rep = evaluate_book_quality(
        _read("reject_duplicate_blocks.txt"),
        runtime_format_id="short_book_30",
        frame="spiritual_first",
    )
    assert rep.release_band == "Reject"
    assert "verbatim_duplicate_blocks" in rep.fail_reasons


def test_reject_stacked_modes_short_chapter() -> None:
    from phoenix_v4.quality.book_quality_gate import evaluate_book_quality

    text = _read("reject_stacked_modes.txt")
    rep = evaluate_book_quality(text, runtime_format_id="short_book_30", frame="spiritual_first")
    assert rep.release_band == "Reject"
    assert any("chapter_function_stacked_modes" in r for r in rep.fail_reasons)


def test_pass_clean_manuscript() -> None:
    from phoenix_v4.quality.book_quality_gate import evaluate_book_quality

    rep = evaluate_book_quality(
        _read("pass_clean.txt"),
        runtime_format_id="short_book_30",
        frame="spiritual_first",
        policy_override=False,
    )
    assert rep.release_band == "Pass to editorial", rep.fail_reasons + rep.hold_reasons


def test_runtime_micro_book_default_reject() -> None:
    from phoenix_v4.quality.book_quality_gate import evaluate_book_quality

    rep = evaluate_book_quality(
        _read("pass_clean.txt"),
        runtime_format_id="micro_book_15",
        frame="spiritual_first",
        policy_override=False,
    )
    assert "runtime_policy_reject" in rep.fail_reasons
    assert rep.release_band == "Reject"


def test_runtime_micro_book_override_clears_policy_only() -> None:
    from phoenix_v4.quality.book_quality_gate import evaluate_book_quality

    rep = evaluate_book_quality(
        _read("pass_clean.txt"),
        runtime_format_id="micro_book_15",
        frame="spiritual_first",
        policy_override=True,
    )
    assert "runtime_policy_reject" not in rep.fail_reasons


def test_corpus_micro_excerpt_rejects() -> None:
    from phoenix_v4.quality.book_quality_gate import evaluate_book_quality

    rep = evaluate_book_quality(
        _read("corpus_micro_excerpt.txt"),
        runtime_format_id="micro_book_15",
        frame="somatic_first",
        policy_override=True,
    )
    assert rep.release_band == "Reject"
    assert rep.fail_reasons


@pytest.mark.skipif(
    not (REPO_ROOT / "artifacts" / "qa" / "pearl_prime_ahjan_genz_anxiety_all_runtimes.txt").exists(),
    reason="full anxiety corpus not present in workspace",
)
def test_full_anxiety_corpus_micro_runtime_classification() -> None:
    from phoenix_v4.quality.book_quality_gate import evaluate_book_quality

    raw = (REPO_ROOT / "artifacts" / "qa" / "pearl_prime_ahjan_genz_anxiety_all_runtimes.txt").read_text(
        encoding="utf-8"
    )
    start = raw.find("# RUNTIME: micro_book_15")
    assert start >= 0
    next_rt = raw.find("# RUNTIME: micro_book_20", start + 1)
    assert next_rt > start
    chunk = raw[start:next_rt]
    ch1 = chunk.find("Chapter 1\n")
    assert ch1 >= 0
    prose = chunk[ch1:].strip()
    rep = evaluate_book_quality(
        prose,
        runtime_format_id="micro_book_15",
        frame="somatic_first",
        policy_override=True,
    )
    assert rep.release_band == "Reject"


def test_book_quality_config_loads() -> None:
    from phoenix_v4.quality.book_quality_gate import load_book_quality_config

    cfg = load_book_quality_config()
    assert int(cfg.get("schema_version") or 0) >= 1
