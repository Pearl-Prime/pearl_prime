"""Regression tests for bank_layer_blob_gate stipple + structure heuristics."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.manga.bank_layer_blob_gate import (
    HARD_EDGE_FLOOR,
    STIPPLE_BLUE_DOM_FLOOR,
    STIPPLE_HF_FLOOR,
    STIPPLE_MEAN_FLOOR,
    judge_png,
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "manga" / "blob_gate"
KNOWN_BAD = FIXTURES / "seated_cockpit_stipple_blob_20260708.png"
KNOWN_GOOD = FIXTURES / "master_wu_pose_strike_paused_known_good.png"


@pytest.mark.skipif(not KNOWN_BAD.is_file(), reason="bad blob fixture missing")
def test_known_bad_stipple_blob_fails() -> None:
    verdict = judge_png(KNOWN_BAD)
    assert not verdict.ok
    assert any("stipple_white_plate" in r for r in verdict.reasons)


@pytest.mark.skipif(not KNOWN_GOOD.is_file(), reason="known-good fixture missing")
def test_known_good_reference_passes() -> None:
    verdict = judge_png(KNOWN_GOOD)
    assert verdict.ok, verdict.reasons


def test_mutation_weakened_stipple_thresholds_would_pass_bad_blob() -> None:
    """Gate must fail the preserved blob; weakening stipple floors must not."""
    if not KNOWN_BAD.is_file():
        pytest.skip("bad blob fixture missing")
    m = judge_png(KNOWN_BAD).metrics
    would_pass_if_weakened = (
        m.mean > STIPPLE_MEAN_FLOOR * 2
        or m.hf_local < STIPPLE_HF_FLOOR / 2
        or m.blue_dom_bright < STIPPLE_BLUE_DOM_FLOOR / 2
    )
    assert not would_pass_if_weakened
    assert m.small_edge >= HARD_EDGE_FLOOR, "bad blob must have fooled byte/edge-only gate"
