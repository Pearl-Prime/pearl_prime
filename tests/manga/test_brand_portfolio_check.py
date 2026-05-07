"""Tests for V2 Phase A.6 brand × genre portfolio check."""
from __future__ import annotations

from scripts.manga.check_brand_portfolio import (
    Verdict,
    check_portfolio,
    load_allocation_config,
)


_CFG = {
    "allocations": {
        "en_US": {
            "stillness_press": {
                "healing": 40,
                "essay": 12,
                "slice_of_life": 10,
                "memoir": 8,
                "supernatural_everyday": 5,
                "comedy": 3,
            },
            "cognitive_clarity": {
                "essay": 35,
                "battle_internal": 10,
                "supernatural_everyday": 2,
            },
        },
        "ja_JP": {
            "stillness_press": {
                "healing": 30,
                "iyashikei": 15,
            },
        },
    },
    "tentpole_divergence_policy": {
        "warrior_calm": {
            "decision": "coexist",
        },
    },
}


def test_high_allocation_returns_on_portfolio():
    r = check_portfolio("stillness_press", "healing", "en_US", config=_CFG)
    assert r.verdict == Verdict.ON
    assert r.allocation_pct == 40
    assert r.primary_genre == "healing"


def test_at_threshold_boundary_is_on():
    r = check_portfolio("stillness_press", "slice_of_life", "en_US", config=_CFG)
    assert r.allocation_pct == 10
    assert r.verdict == Verdict.ON


def test_low_allocation_returns_warn():
    r = check_portfolio("stillness_press", "memoir", "en_US", config=_CFG)
    assert r.allocation_pct == 8
    assert r.verdict == Verdict.WARN


def test_one_pct_threshold_lower_bound():
    r = check_portfolio("cognitive_clarity", "supernatural_everyday", "en_US", config=_CFG)
    assert r.allocation_pct == 2
    assert r.verdict == Verdict.WARN


def test_unregistered_genre_is_hard():
    r = check_portfolio("stillness_press", "mecha", "en_US", config=_CFG)
    assert r.allocation_pct == 0
    assert r.verdict == Verdict.HARD


def test_unregistered_brand_is_hard():
    r = check_portfolio("nonexistent_brand", "healing", "en_US", config=_CFG)
    assert r.allocation_pct == 0
    assert r.verdict == Verdict.HARD


def test_locale_lookup_isolates():
    # ja_JP stillness_press primary is healing 30% (not en_US's 40%)
    r = check_portfolio("stillness_press", "iyashikei", "ja_JP", config=_CFG)
    assert r.verdict == Verdict.ON
    assert r.allocation_pct == 15
    assert r.primary_genre == "healing"


def test_tentpole_divergence_flag_surfaces():
    # warrior_calm registered as coexist
    cfg = dict(_CFG)
    cfg = {**_CFG, "allocations": {"en_US": {"warrior_calm": {"battle": 25, "cultivation": 22}}}}
    cfg["tentpole_divergence_policy"] = _CFG["tentpole_divergence_policy"]
    r = check_portfolio("warrior_calm", "battle", "en_US", config=cfg)
    assert r.tentpole_divergence is True
    assert r.primary_genre == "battle"


def test_threshold_overrides():
    # Tighten on-threshold to 50% — healing 40% drops to WARN
    r = check_portfolio("stillness_press", "healing", "en_US", config=_CFG, on_threshold=50)
    assert r.verdict == Verdict.WARN


# Smoke test against real repo config.
def test_load_real_allocation_yaml():
    cfg = load_allocation_config()
    assert "allocations" in cfg
    en_us = cfg["allocations"].get("en_US") or {}
    assert "stillness_press" in en_us
    # Real value should be on-portfolio per the registered allocation
    r = check_portfolio("stillness_press", "healing", "en_US", config=cfg)
    assert r.verdict == Verdict.ON
