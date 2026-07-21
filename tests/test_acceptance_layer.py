#!/usr/bin/env python3
"""Unit tests for phoenix_v4/quality/acceptance_layer.py (Lane 04,
docs/agent_prompt_packs/20260721_bestseller_atom_flow/04_book_acceptance_layer_stamp.md).

Contract under test:
  - seed-43001-style inputs (Layer 1 gates PASS, research_fit unbound) ->
    structurally_clear, never higher.
  - Lane-02-style authored-cell inputs (Layer 1 PASS + research_fit bound +
    book_idea/motif + mechanism_called>0, no ONTGP review logged yet) ->
    authored_candidate, never higher.
  - No combination of gate-PASS-only inputs (i.e. without an explicit
    ontgp_sample_review / blind10_result) can ever reach system_working or
    bestseller_register — exhaustive sweep over the boolean/gate input space.
  - bestseller_craft floor (0.55) and the ONTGP chapter rubric (0 FAILs, <=2
    WEAKs) are enforced exactly as documented in the scorecard, not invented.
"""
from __future__ import annotations

import itertools

import pytest

from phoenix_v4.quality.acceptance_layer import (
    AUTHORED_CANDIDATE,
    BESTSELLER_CRAFT_SCORE_FLOOR,
    BESTSELLER_REGISTER,
    ONTGP_MAX_WEAKS_PER_CHAPTER,
    PATH_BROKEN,
    PATH_WORKS,
    STRUCTURALLY_CLEAR,
    SYSTEM_WORKING,
    compute_acceptance_layer,
)

_LAYER1_CLEAN_GATES = {
    "chapter_flow": "PASS",
    "register_gate": "PASS",
    "book_pass": "PASS",
    "ei_v2": "PASS",
    "transformation_arc": "PASS",
    "book_quality_gate": "PASS",
}


def test_seed_43001_style_book_caps_at_structurally_clear() -> None:
    """seed 43001 (millennial_women_professionals x courage), per pack
    INDEX.md: gate-PASS book, `research_fit: {}`, no book_idea/motif payoff,
    mechanism_called=0. Layer 1 gates clean; research_fit unbound is the cap.
    """
    result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        bestseller_craft_score=0.61,
        research_fit_bound=False,
        research_fit_unbound_reason="research_fit is empty ({}) with no mode/skip_reason set",
        book_idea_or_motif_present=False,
        mechanism_called=0,
    )
    assert result.acceptance_layer == STRUCTURALLY_CLEAR
    assert result.layer1_pass is True
    assert result.layer2_pass is False
    assert result.layer3_pass is None
    assert result.layer4_pass is None
    assert any("research_fit unbound" in r for r in result.reasons)


def test_lane02_authored_cell_book_reaches_authored_candidate_not_higher() -> None:
    """Lane 02 / ws_story_cell_authoring_20260425-style book: real story_atoms
    bank bound, book_idea/motif present, a named mechanism actually called —
    but no Pearl_Editor ONTGP sample read has been logged yet.
    """
    result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        bestseller_craft_score=0.61,
        research_fit_bound=True,
        book_idea_or_motif_present=True,
        mechanism_called=2,
        ontgp_sample_review=None,
    )
    assert result.acceptance_layer == AUTHORED_CANDIDATE
    assert result.layer1_pass is True
    assert result.layer2_pass is True
    assert result.layer3_pass is None
    assert result.layer4_pass is None


def test_book_txt_missing_is_path_broken_regardless_of_other_inputs() -> None:
    result = compute_acceptance_layer(
        book_txt_exists=False,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        research_fit_bound=True,
        book_idea_or_motif_present=True,
        mechanism_called=5,
    )
    assert result.acceptance_layer == PATH_BROKEN


@pytest.mark.parametrize("failing_gate", ["chapter_flow", "register_gate", "book_pass"])
def test_any_layer1_gate_failure_caps_at_path_works(failing_gate: str) -> None:
    gates = dict(_LAYER1_CLEAN_GATES)
    gates[failing_gate] = "FAIL"
    result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=gates,
        bestseller_craft_score=0.9,
        research_fit_bound=True,
        book_idea_or_motif_present=True,
        mechanism_called=3,
    )
    assert result.acceptance_layer == PATH_WORKS
    assert result.layer1_pass is False


def test_bestseller_craft_below_scorecard_floor_caps_at_path_works() -> None:
    """Scorecard line 50: bestseller_craft overall_score >= 0.55 is a Layer 1
    hard-gate floor, enforced numerically even if all named gate statuses say
    PASS under a looser local check."""
    just_below = BESTSELLER_CRAFT_SCORE_FLOOR - 0.01
    result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        bestseller_craft_score=just_below,
        research_fit_bound=True,
        book_idea_or_motif_present=True,
        mechanism_called=1,
    )
    assert result.acceptance_layer == PATH_WORKS
    assert any(str(BESTSELLER_CRAFT_SCORE_FLOOR) in r for r in result.reasons)


def test_bestseller_craft_at_exactly_the_floor_does_not_cap() -> None:
    result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        bestseller_craft_score=BESTSELLER_CRAFT_SCORE_FLOOR,
        research_fit_bound=False,
    )
    assert result.acceptance_layer == STRUCTURALLY_CLEAR


def test_no_layer1_gate_evidence_never_reaches_structurally_clear() -> None:
    result = compute_acceptance_layer(book_txt_exists=True, layer1_gate_statuses=None)
    assert result.acceptance_layer == PATH_WORKS
    assert result.layer1_pass is False


def test_no_book_idea_or_motif_caps_at_structurally_clear_even_if_bound() -> None:
    result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        bestseller_craft_score=0.7,
        research_fit_bound=True,
        book_idea_or_motif_present=False,
        mechanism_called=4,
    )
    assert result.acceptance_layer == STRUCTURALLY_CLEAR
    assert result.layer2_pass is False


def test_mechanism_not_called_caps_at_structurally_clear_even_if_bound() -> None:
    result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        bestseller_craft_score=0.7,
        research_fit_bound=True,
        book_idea_or_motif_present=True,
        mechanism_called=0,
    )
    assert result.acceptance_layer == STRUCTURALLY_CLEAR

    result_none = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        bestseller_craft_score=0.7,
        research_fit_bound=True,
        book_idea_or_motif_present=True,
        mechanism_called=None,
    )
    assert result_none.acceptance_layer == STRUCTURALLY_CLEAR


def test_no_gate_only_combination_reaches_layer3_or_4() -> None:
    """Exhaustive sweep: for every combination of gate-PASS-only inputs
    (no ontgp_sample_review, no blind10_result), the result can never be
    system_working or bestseller_register. This is the pack's explicit
    'no combination of gate-PASS-only inputs ever produces system_working or
    bestseller_register' proof requirement."""
    craft_scores = [0.0, 0.3, BESTSELLER_CRAFT_SCORE_FLOOR - 0.01, BESTSELLER_CRAFT_SCORE_FLOOR, 0.9, 1.0]
    bools = [True, False, None]
    mechanism_values = [None, 0, 1, 5]
    gate_variants = [
        _LAYER1_CLEAN_GATES,
        {**_LAYER1_CLEAN_GATES, "chapter_flow": "FAIL"},
        {**_LAYER1_CLEAN_GATES, "book_pass": "WARN"},
        {},
    ]
    combos = itertools.product(gate_variants, craft_scores, bools, bools, mechanism_values)
    checked = 0
    for gates, craft, rf_bound, idea_present, mech in combos:
        result = compute_acceptance_layer(
            book_txt_exists=True,
            layer1_gate_statuses=gates,
            bestseller_craft_score=craft,
            research_fit_bound=rf_bound,
            book_idea_or_motif_present=bool(idea_present),
            mechanism_called=mech,
            ontgp_sample_review=None,
            blind10_result=None,
        )
        assert result.acceptance_layer not in (SYSTEM_WORKING, BESTSELLER_REGISTER), (
            f"gate-only combo reached {result.acceptance_layer}: "
            f"gates={gates} craft={craft} rf_bound={rf_bound} "
            f"idea_present={idea_present} mech={mech}"
        )
        assert result.layer3_pass in (None, False)
        assert result.layer4_pass in (None, False)
        checked += 1
    assert checked == len(gate_variants) * len(craft_scores) * len(bools) * len(bools) * len(mechanism_values)


def _passing_ontgp_review() -> dict:
    dims = {"orient": "PASS", "name": "PASS", "turn": "PASS", "give": "PASS", "pull": "PASS"}
    return {"chapters": {"1": dims, "5": dims, "11": dims}}


def test_logged_passing_ontgp_review_reaches_system_working_not_bestseller() -> None:
    result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        bestseller_craft_score=0.7,
        research_fit_bound=True,
        book_idea_or_motif_present=True,
        mechanism_called=3,
        ontgp_sample_review=_passing_ontgp_review(),
        blind10_result=None,
    )
    assert result.acceptance_layer == SYSTEM_WORKING
    assert result.layer3_pass is True
    assert result.layer4_pass is None


def test_ontgp_review_with_too_many_weaks_fails_layer3() -> None:
    """Scorecard line 90: chapter passes ONTGP only if 0 FAILs AND <=2 WEAKs."""
    too_many_weaks = {
        "orient": "WEAK",
        "name": "WEAK",
        "turn": "WEAK",
        "give": "PASS",
        "pull": "PASS",
    }
    assert sum(1 for v in too_many_weaks.values() if v == "WEAK") > ONTGP_MAX_WEAKS_PER_CHAPTER
    review = {"chapters": {"1": too_many_weaks}}
    result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        bestseller_craft_score=0.7,
        research_fit_bound=True,
        book_idea_or_motif_present=True,
        mechanism_called=1,
        ontgp_sample_review=review,
    )
    assert result.acceptance_layer == AUTHORED_CANDIDATE
    assert result.layer3_pass is False


def test_ontgp_review_with_a_single_fail_fails_layer3() -> None:
    dims = {"orient": "PASS", "name": "FAIL", "turn": "PASS", "give": "PASS", "pull": "PASS"}
    result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        research_fit_bound=True,
        book_idea_or_motif_present=True,
        mechanism_called=1,
        ontgp_sample_review={"chapters": {"1": dims}},
    )
    assert result.acceptance_layer == AUTHORED_CANDIDATE
    assert result.layer3_pass is False


def test_bestseller_register_never_auto_assigned_without_blind10_result() -> None:
    result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        bestseller_craft_score=0.9,
        research_fit_bound=True,
        book_idea_or_motif_present=True,
        mechanism_called=10,
        ontgp_sample_review=_passing_ontgp_review(),
        blind10_result=None,
    )
    assert result.acceptance_layer == SYSTEM_WORKING
    assert result.acceptance_layer != BESTSELLER_REGISTER


def test_bestseller_register_surfaced_only_from_explicit_passing_blind10_result() -> None:
    result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        bestseller_craft_score=0.9,
        research_fit_bound=True,
        book_idea_or_motif_present=True,
        mechanism_called=10,
        ontgp_sample_review=_passing_ontgp_review(),
        blind10_result={"verdict": "PASS"},
    )
    assert result.acceptance_layer == BESTSELLER_REGISTER
    assert result.layer4_pass is True


def test_blind10_result_below_scorecard_thresholds_does_not_advance() -> None:
    """Scorecard line 113/114: system-level PASS needs >=7/10 felt_assembled
    AND >=6/10 shelf_next_to_trade_pub; 5-6 is WARN, <5 is FAIL — neither
    advances to bestseller_register."""
    warn_result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        research_fit_bound=True,
        book_idea_or_motif_present=True,
        mechanism_called=1,
        ontgp_sample_review=_passing_ontgp_review(),
        blind10_result={
            "felt_assembled_yes_count": 6,
            "shelf_next_to_trade_pub_yes_count": 6,
            "total_books": 10,
        },
    )
    assert warn_result.acceptance_layer == SYSTEM_WORKING
    assert warn_result.layer4_pass is False


def test_blind10_result_meeting_both_numeric_floors_advances() -> None:
    result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        research_fit_bound=True,
        book_idea_or_motif_present=True,
        mechanism_called=1,
        ontgp_sample_review=_passing_ontgp_review(),
        blind10_result={
            "felt_assembled_yes_count": 7,
            "shelf_next_to_trade_pub_yes_count": 6,
            "total_books": 10,
        },
    )
    assert result.acceptance_layer == BESTSELLER_REGISTER


def test_to_dict_round_trips_expected_keys() -> None:
    result = compute_acceptance_layer(
        book_txt_exists=True,
        layer1_gate_statuses=_LAYER1_CLEAN_GATES,
        research_fit_bound=False,
    )
    payload = result.to_dict()
    for key in (
        "acceptance_layer",
        "reasons",
        "layer1_pass",
        "layer2_pass",
        "layer3_pass",
        "layer4_pass",
        "research_fit_bound",
    ):
        assert key in payload
