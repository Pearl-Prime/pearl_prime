"""Frame registry, frame_governance_check, and v2 apply_frame_enforcement."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from phoenix_v4.quality.frame_governor import (
    FrameEnforcementContext,
    FrameGovernanceHardFail,
    apply_frame_enforcement,
    frame_governance_check,
    load_frame_registry,
)


def _registry() -> dict:
    return load_frame_registry()


def test_somatic_flags_every_organ_frequency() -> None:
    reg = _registry()
    r = frame_governance_check(
        "Some teachers claim every organ has a frequency.",
        "somatic_first",
        5,
        reg,
    )
    assert any(v.get("type") == "absolute_claim" for v in r.violations)


def test_somatic_flags_disease_is_dissonance() -> None:
    reg = _registry()
    r = frame_governance_check(
        "They say disease is dissonance in the field.",
        "somatic_first",
        5,
        reg,
    )
    assert any(v.get("type") == "absolute_claim" for v in r.violations)


def test_somatic_does_not_flag_nervous_system() -> None:
    reg = _registry()
    r = frame_governance_check(
        "The nervous system responds to predictions before facts.",
        "somatic_first",
        0,
        reg,
    )
    assert not any(v.get("type") == "absolute_claim" for v in r.violations)


def test_spiritual_first_allows_patterns() -> None:
    reg = _registry()
    r = frame_governance_check(
        "Every organ has a frequency of love.",
        "spiritual_first",
        0,
        reg,
    )
    assert r.frame_compliant
    assert r.violations == []


def test_spiritual_entry_chapter_min_blocks_early_karma() -> None:
    reg = _registry()
    r = frame_governance_check(
        "You might describe chakra imagery in the chest.",
        "somatic_first",
        0,
        reg,
    )
    assert any(v.get("type") == "spiritual_before_entry_chapter" for v in r.violations)


def test_spiritual_allowed_from_chapter_three() -> None:
    reg = _registry()
    r = frame_governance_check(
        "You might describe chakra imagery in the chest.",
        "somatic_first",
        3,
        reg,
    )
    assert not any(v.get("type") == "spiritual_before_entry_chapter" for v in r.violations)


def test_missing_frame_registry_graceful(tmp_path: Path) -> None:
    r = frame_governance_check("anything", "somatic_first", 0, {})
    assert r.frame_compliant


def test_v2_strip_absolute_somatic_body() -> None:
    reg = load_frame_registry()
    ctx = FrameEnforcementContext(0, "somatic_first", False, False, "")
    text = "Keep breathing. Love melts all blockages here. Notice your shoulders.\n"
    out, res = apply_frame_enforcement(text, ctx, reg)
    assert "Love melts" not in out
    assert any(s.get("type") == "absolute_claim" for s in res.stripped_sentences)
    assert res.frame_compliant


def test_v2_doctrine_chapter_preserves_absolute_with_warn() -> None:
    reg = load_frame_registry()
    ctx = FrameEnforcementContext(1, "somatic_first", True, False, "")
    line = "In this lineage, love melts all blockages; the teaching is explicit."
    out, res = apply_frame_enforcement(line, ctx, reg)
    assert "love melts all" in out.lower()
    assert any(v.get("type") == "absolute_claim" for v in res.violations)
    assert not res.stripped_sentences


def test_v2_soften_early_spiritual_lexicon() -> None:
    reg = load_frame_registry()
    ctx = FrameEnforcementContext(0, "somatic_first", False, False, "")
    text = "Early chapter with chakra language before entry."
    out, res = apply_frame_enforcement(text, ctx, reg)
    assert "chakra" not in out.lower()
    assert res.softened_sentences
    assert res.frame_compliant


def test_v2_allow_early_spiritual_contract_skips_enforcement() -> None:
    reg = load_frame_registry()
    ctx = FrameEnforcementContext(0, "somatic_first", False, True, "")
    text = "Early chapter with chakra language before entry."
    out, res = apply_frame_enforcement(text, ctx, reg)
    assert out == text
    assert not res.softened_sentences


def test_v2_hard_fail_policy_raises() -> None:
    reg = deepcopy(load_frame_registry())
    gv2 = dict(reg.get("governance_v2") or {})
    pol = dict(gv2.get("violation_policies") or {})
    pol["absolute_claim"] = {"default": "hard_fail", "doctrine_chapter": "warn_only"}
    gv2["violation_policies"] = pol
    reg["governance_v2"] = gv2
    ctx = FrameEnforcementContext(5, "somatic_first", False, False, "")
    with pytest.raises(FrameGovernanceHardFail):
        apply_frame_enforcement("Love melts all blockages.", ctx, reg)


def test_v2_disabled_leaves_text_and_warns() -> None:
    reg = deepcopy(load_frame_registry())
    gv2 = dict(reg.get("governance_v2") or {})
    gv2["enabled"] = False
    reg["governance_v2"] = gv2
    ctx = FrameEnforcementContext(0, "somatic_first", False, False, "")
    text = "Love melts all blockages."
    out, res = apply_frame_enforcement(text, ctx, reg)
    assert out == text
    assert not res.frame_compliant
    assert res.violations
