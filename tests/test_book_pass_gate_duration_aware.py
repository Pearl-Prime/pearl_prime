"""
Tests for duration-aware book-pass gate thresholds.

Validates that:
1. Chapter tier detection works correctly for all tiers
2. Tier thresholds are loaded from config
3. Micro books (3-5 chapters) get relaxed thresholds
4. Standard books (9-12 chapters) maintain original thresholds
5. Deep books (19+) get stricter bestseller structure requirements
6. Config file is loaded when present
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.qa.book_pass_gate import get_chapter_tier, get_tier_thresholds


def test_micro_tier_3_chapters():
    assert get_chapter_tier(3) == "micro"


def test_micro_tier_5_chapters():
    assert get_chapter_tier(5) == "micro"


def test_short_tier_6_chapters():
    assert get_chapter_tier(6) == "short"


def test_short_tier_8_chapters():
    assert get_chapter_tier(8) == "short"


def test_standard_tier_9_chapters():
    assert get_chapter_tier(9) == "standard"


def test_standard_tier_12_chapters():
    assert get_chapter_tier(12) == "standard"


def test_extended_tier_13_chapters():
    assert get_chapter_tier(13) == "extended"


def test_extended_tier_18_chapters():
    assert get_chapter_tier(18) == "extended"


def test_deep_tier_19_chapters():
    assert get_chapter_tier(19) == "deep"


def test_deep_tier_24_chapters():
    assert get_chapter_tier(24) == "deep"


def test_below_minimum_defaults_to_micro():
    assert get_chapter_tier(1) == "micro"
    assert get_chapter_tier(2) == "micro"


def test_large_chapter_count_defaults_to_deep():
    assert get_chapter_tier(100) == "deep"


def test_micro_thresholds_relaxed():
    """Micro books should have lower requirements than standard."""
    micro = get_tier_thresholds(4)
    standard = get_tier_thresholds(10)
    assert micro["min_distinct_bands"] < standard["min_distinct_bands"]
    assert micro["min_mechanism_depth"] < standard["min_mechanism_depth"]
    assert micro["identity_stages_required"] < standard["identity_stages_required"]
    assert micro["require_callback_completion"] is False
    assert micro["min_bestseller_structures_distinct"] < standard["min_bestseller_structures_distinct"]


def test_standard_thresholds_match_original_defaults():
    """Standard tier should match the original hardcoded defaults."""
    standard = get_tier_thresholds(10)
    assert standard["min_distinct_bands"] == 4
    assert standard["min_mechanism_depth"] == 4
    assert standard["identity_stages_required"] == 4
    assert standard["min_cost_intensity_peak"] == 4
    assert standard["require_self_claim_final"] is True
    assert standard["require_callback_completion"] is True
    assert standard["min_bestseller_structures_distinct"] == 4


def test_deep_thresholds_stricter_bestseller():
    """Deep books should require more distinct bestseller structures."""
    deep = get_tier_thresholds(20)
    standard = get_tier_thresholds(10)
    assert deep["min_bestseller_structures_distinct"] > standard["min_bestseller_structures_distinct"]


def test_extended_thresholds():
    """Extended tier should have same mechanism depth as standard but more bestseller variety."""
    extended = get_tier_thresholds(15)
    assert extended["min_mechanism_depth"] == 4
    assert extended["min_bestseller_structures_distinct"] == 5


def test_short_thresholds_between_micro_and_standard():
    """Short tier thresholds should be between micro and standard."""
    micro = get_tier_thresholds(4)
    short = get_tier_thresholds(7)
    standard = get_tier_thresholds(10)
    assert micro["min_distinct_bands"] <= short["min_distinct_bands"] <= standard["min_distinct_bands"]
    assert micro["min_mechanism_depth"] <= short["min_mechanism_depth"] <= standard["min_mechanism_depth"]


def test_config_file_exists():
    """The book_pass_gate_thresholds.yaml config should exist."""
    config_path = REPO_ROOT / "config" / "quality" / "book_pass_gate_thresholds.yaml"
    assert config_path.exists(), f"Config not found: {config_path}"


def test_config_has_all_tiers():
    """Config should define all five tiers."""
    try:
        import yaml
    except ImportError:
        return
    config_path = REPO_ROOT / "config" / "quality" / "book_pass_gate_thresholds.yaml"
    if not config_path.exists():
        return
    with open(config_path) as f:
        data = yaml.safe_load(f)
    book_pass = data.get("book_pass", {})
    for tier in ("micro", "short", "standard", "extended", "deep"):
        assert tier in book_pass, f"Missing tier '{tier}' in config"
        for key in ("min_distinct_bands", "min_mechanism_depth", "identity_stages_required",
                     "min_cost_intensity_peak", "require_self_claim_final",
                     "require_callback_completion", "min_bestseller_structures_distinct"):
            assert key in book_pass[tier], f"Missing key '{key}' in tier '{tier}'"
