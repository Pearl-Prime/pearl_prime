"""Unit tests for scene_anchor_density gate (PR #1089 yield-recovery fix).

Covers:
  - Default cap is 3 (was 2 pre-2026-05-13) — see SCENE_ANCHOR_DENSITY_CAP_V2_SPEC.
  - A phrase recurring in exactly cap+1 paragraphs of one chapter is a violation.
  - A phrase recurring in cap paragraphs of one chapter is NOT a violation.
  - Overlapping n-gram offenders are collapsed (one motif → one offender entry)
    when collapse_overlapping_ngrams is enabled.
"""
from __future__ import annotations

from scripts.run_pipeline import (
    _load_scene_anchor_density_config,
    _scene_anchor_density_violations,
)


def _make_chapter(heading: str, paragraphs: list[str]) -> str:
    body = "\n\n".join(paragraphs)
    return f"{heading}\n\n{body}"


def test_default_cap_is_three() -> None:
    cfg = _load_scene_anchor_density_config()
    assert int(cfg.get("default_cap_per_chapter")) == 3, (
        "Default scene_anchor cap should be 3 per SCENE_ANCHOR_DENSITY_CAP_V2_SPEC."
    )


def test_phrase_at_cap_is_not_a_violation() -> None:
    # Phrase appears in exactly cap=3 paragraphs — should PASS (cap is "more than").
    paras = [
        "Each morning the same anchor phrase appears here.",
        "Each morning the same anchor phrase appears here.",
        "Each morning the same anchor phrase appears here.",
        "An unrelated sentence to add another paragraph.",
    ]
    prose = _make_chapter("Chapter 1", paras)
    violations = _scene_anchor_density_violations(prose, cap=3)
    assert violations == [], f"Expected no violations at cap, got {violations}"


def test_phrase_over_cap_is_a_violation() -> None:
    # Phrase appears in 4 paragraphs — exceeds cap=3.
    paras = [
        "Each morning the same anchor phrase appears here.",
        "Each morning the same anchor phrase appears here.",
        "Each morning the same anchor phrase appears here.",
        "Each morning the same anchor phrase appears here.",
    ]
    prose = _make_chapter("Chapter 1", paras)
    violations = _scene_anchor_density_violations(prose, cap=3)
    assert len(violations) == 1
    assert violations[0]["chapter"] == 1
    assert any(o["paragraph_count"] == 4 for o in violations[0]["offenders"])


def test_overlapping_ngrams_are_collapsed() -> None:
    # A single 8-word recurring motif would, without collapse, produce overlapping
    # 4..8 word n-gram offenders (5 entries) all at paragraph_count=4.
    # Use a sentence where each paragraph IS exactly the motif (no surrounding words)
    # so the 8-word phrase is the unique anchor and 4..7 subphrases are strict substrings.
    motif = "the long recurring anchor motif appears again repeatedly"  # 8 words
    paras = [f"{motif}.", f"{motif}.", f"{motif}.", f"{motif}."]
    prose = _make_chapter("Chapter 1", paras)
    violations = _scene_anchor_density_violations(prose, cap=3)
    assert len(violations) == 1
    offenders = violations[0]["offenders"]
    # After collapse, the 8-word phrase survives and the 4..7 word subphrases of
    # it are dropped. Pre-fix, this returned 5 entries (lengths 4..8). Post-fix: 1.
    matching = [o for o in offenders if o["phrase"] in motif and o["paragraph_count"] == 4]
    assert len(matching) == 1, (
        f"Overlapping n-grams should collapse to 1 entry; got {len(matching)}: {matching}"
    )
    assert matching[0]["phrase"] == motif


def test_zero_cap_disables_gate() -> None:
    paras = ["recurring phrase here"] * 10
    prose = _make_chapter("Chapter 1", paras)
    assert _scene_anchor_density_violations(prose, cap=0) == []


def test_violations_isolated_per_chapter() -> None:
    # A phrase appearing 4 times in chapter 1 violates; same phrase 2 times in
    # chapter 2 is fine. Violation should report chapter 1 only.
    motif = "the steady anchor phrase here"
    ch1 = _make_chapter("Chapter 1", [f"{motif}."] * 4)
    ch2 = _make_chapter("Chapter 2", [f"{motif}.", "An unrelated sentence."])
    prose = f"{ch1}\n\n{ch2}"
    violations = _scene_anchor_density_violations(prose, cap=3)
    assert len(violations) == 1
    assert violations[0]["chapter"] == 1
