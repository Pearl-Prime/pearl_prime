"""Tests for the duration-derivation registry-loader helper (DURATION-DERIVATION-01).

Covers docs/DURATION_DERIVATION_SPEC.md:
  * §4.1 per-regime word_target math (cap / floor / midpoint, + cap_word_target)
  * §4.2 derive_minutes (round(words / wpm))
  * §4.3 WPM constants single-sourced from duration_scorecard.yaml (tts=150, ebook=230)
  * §4.4 standard_book ≈ 147 audiobook min (and the full worked-examples table)
  * §3.2 deep_book_6h floor regime (52,000 → 347 audiobook min)
  * §6.3 ±15% label-acceptance band vs each format's advertised real duration
  * §7  non-en-US early-skip
  * §8  word_range-less (stub) skip
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.ops.duration_derivation import (  # noqa: E402
    DEFAULT_EBOOK_WPM,
    DEFAULT_TTS_WPM,
    derive_all,
    derive_format_minutes,
    derive_minutes,
    load_wpm_constants,
    word_target,
)

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


# --------------------------------------------------------------------------- #
# Fixtures / helpers
# --------------------------------------------------------------------------- #
def _load_registry():
    p = REPO_ROOT / "config" / "format_selection" / "format_registry.yaml"
    if yaml is None or not p.exists():
        return {}
    with open(p) as f:
        return yaml.safe_load(f) or {}


def _load_scorecard():
    p = REPO_ROOT / "config" / "duration_scorecard.yaml"
    if yaml is None or not p.exists():
        return {}
    with open(p) as f:
        return yaml.safe_load(f) or {}


# Spec §4.4 worked-examples table: format -> (word_range, regime, cap_override,
# expected_word_target, expected_audiobook_min, expected_ebook_min, old_label,
# advertised_real_audiobook_min_for_band_check_or_None).
# word_ranges are the values this PR writes to format_registry.yaml (standard_book
# ceiling reconciled 18k→22k per §5).
WORKED = {
    "micro_book_15":          ([2500, 4500],  "midpoint", None, 3500,  23,  15, 15,  None),
    "micro_book_20":          ([3000, 5500],  "midpoint", None, 4250,  28,  18, 20,  None),
    "short_book_30":          ([4500, 7500],  "midpoint", None, 6000,  40,  26, 30,  None),
    "standard_book":          ([9000, 22000], "cap",     22000, 22000, 147, 96, 55,  143.4),
    "extended_book_2h":       ([17000, 25000],"midpoint", None, 21000, 140, 91, 120, None),
    "deep_book_4h":           ([20000, 40000],"midpoint", None, 30000, 200, 130,240, 216.6),
    "deep_book_6h":           ([50000, 72000],"floor",    None, 52000, 347, 226,360, 368.1),
    "compact_book_5ch_15min": ([3000, 4500],  "midpoint", None, 3750,  25,  16, 15,  None),
    "compact_book_5ch_20min": ([4000, 5500],  "midpoint", None, 4750,  32,  21, 20,  None),
    "compact_book_8ch_30min": ([5500, 7500],  "midpoint", None, 6500,  43,  28, 30,  None),
}


# --------------------------------------------------------------------------- #
# §4.1 word_target — per-regime math
# --------------------------------------------------------------------------- #
def test_word_target_midpoint():
    assert word_target([2500, 4500], "midpoint") == 3500
    assert word_target([3000, 5500], "midpoint") == 4250
    assert word_target([17000, 25000], "midpoint") == 21000


def test_word_target_floor_uses_104_multiplier():
    # §3.2: floor regime = round(min * 1.04), NOT the raw floor.
    assert word_target([50000, 72000], "floor") == 52000
    assert word_target([50000, 72000], "floor") != 50000


def test_word_target_cap_uses_ceiling_by_default():
    assert word_target([20000, 40000], "cap") == 40000


def test_word_target_cap_override_wins():
    # standard_book: cap_word_target pins to 22000 regardless of word_range max.
    assert word_target([9000, 22000], "cap", cap_word_target=22000) == 22000
    assert word_target([9000, 18000], "cap", cap_word_target=22000) == 22000


def test_word_target_unknown_regime_raises():
    with pytest.raises(ValueError):
        word_target([1, 2], "ceiling")


def test_word_target_stub_returns_none():
    # §8: no word_range and no cap override -> None (skip).
    assert word_target(None, "midpoint") is None
    assert word_target(None, "floor") is None
    # cap regime with explicit cap override may still derive even without a range.
    assert word_target(None, "cap", cap_word_target=12000) == 12000


# --------------------------------------------------------------------------- #
# §4.2 derive_minutes
# --------------------------------------------------------------------------- #
def test_derive_minutes_rounds():
    assert derive_minutes(22000, 150) == 147   # 146.67 -> 147
    assert derive_minutes(22000, 230) == 96     # 95.65 -> 96
    assert derive_minutes(3500, 150) == 23      # 23.33 -> 23


def test_derive_minutes_positive_wpm_required():
    with pytest.raises(ValueError):
        derive_minutes(1000, 0)
    with pytest.raises(ValueError):
        derive_minutes(1000, -150)


# --------------------------------------------------------------------------- #
# §4.3 single-sourced WPM constants
# --------------------------------------------------------------------------- #
def test_load_wpm_from_explicit_config():
    cfg = {"duration_adherence_scorecard": {"tts_wpm": 150, "ebook_wpm": 230}}
    assert load_wpm_constants(cfg) == (150, 230)


def test_load_wpm_falls_back_when_absent():
    # Pre-migration config (no ebook_wpm) still yields a usable pair.
    cfg = {"duration_adherence_scorecard": {"tts_wpm": 150}}
    tts, ebook = load_wpm_constants(cfg)
    assert tts == 150
    assert ebook == DEFAULT_EBOOK_WPM
    # Empty config -> both defaults.
    assert load_wpm_constants({}) == (DEFAULT_TTS_WPM, DEFAULT_EBOOK_WPM)


@pytest.mark.skipif(yaml is None, reason="PyYAML not available")
def test_scorecard_on_disk_declares_both_wpm():
    """The shipped duration_scorecard.yaml must single-source tts_wpm AND ebook_wpm."""
    block = _load_scorecard().get("duration_adherence_scorecard", {})
    assert block.get("tts_wpm") == 150, "tts_wpm must stay 150 (OVERLAY §413)"
    assert block.get("ebook_wpm") == 230, "ebook_wpm:230 must be added (§4.3)"


# --------------------------------------------------------------------------- #
# §4.4 full worked-examples table + standard_book ≈ 147 / deep_6h floor
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", list(WORKED.keys()))
def test_worked_examples_match_spec(name):
    wr, regime, cap, exp_wt, exp_audio, exp_ebook, _old, _real = WORKED[name]
    wt = word_target(wr, regime, cap)
    assert wt == exp_wt, f"{name}: word_target {wt} != spec {exp_wt}"
    assert derive_minutes(wt, 150) == exp_audio, f"{name}: audiobook_minutes"
    assert derive_minutes(wt, 230) == exp_ebook, f"{name}: ebook_minutes"


def test_standard_book_is_about_147_minutes():
    """The headline reconciliation: standard_book ≈ 147 audiobook min (not 55)."""
    fmt = {"word_range": [9000, 22000], "fill_regime": "cap", "cap_word_target": 22000}
    out = derive_format_minutes(fmt, 150, 230)
    assert out is not None
    assert out["audiobook_minutes"] == 147
    assert 145 <= out["audiobook_minutes"] <= 149  # ~147
    assert out["ebook_minutes"] == 96


def test_deep_book_6h_floor_regime():
    fmt = {"word_range": [50000, 72000], "fill_regime": "floor"}
    out = derive_format_minutes(fmt, 150, 230)
    assert out["word_target"] == 52000          # round(50000 * 1.04)
    assert out["audiobook_minutes"] == 347       # round(52000 / 150)


# --------------------------------------------------------------------------- #
# §6.3 ±15% label-acceptance band vs each format's advertised real duration
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "name", [n for n, v in WORKED.items() if v[7] is not None]
)
def test_derived_label_within_15pct_of_real(name):
    """Derived audiobook label must sit within ±15% of the advertised real minutes.

    Real values from the landed audit (DURATION_CORRECTNESS_REPORT / projection):
    standard_book ≈143.4, deep_book_4h ≈216.6, deep_book_6h ≈368.1.
    """
    wr, regime, cap, _wt, _a, _e, _old, real = WORKED[name]
    wt = word_target(wr, regime, cap)
    derived = derive_minutes(wt, 150)
    lo, hi = real * 0.85, real * 1.15
    assert lo <= derived <= hi, (
        f"{name}: derived {derived} outside ±15% band [{lo:.0f},{hi:.0f}] of {real}"
    )


# --------------------------------------------------------------------------- #
# §7 / §8 skip rules
# --------------------------------------------------------------------------- #
def test_non_en_locale_skipped():
    fmt = {"word_range": [9000, 22000], "fill_regime": "cap", "cap_word_target": 22000}
    for loc in ("ja-JP", "zh-TW", "zh-CN", "ko-KR", "es-ES"):
        assert derive_format_minutes(fmt, 150, 230, locale=loc) is None
    # en-US / en still derive.
    assert derive_format_minutes(fmt, 150, 230, locale="en-US") is not None
    assert derive_format_minutes(fmt, 150, 230, locale="en") is not None


def test_stub_format_skipped():
    # §8: only chapter_count_default, no word_range -> skipped.
    assert derive_format_minutes({"chapter_count_default": 5}, 150, 230) is None


# --------------------------------------------------------------------------- #
# Integration against the shipped registry (if present on disk)
# --------------------------------------------------------------------------- #
@pytest.mark.skipif(yaml is None, reason="PyYAML not available")
def test_derive_all_against_shipped_registry():
    registry = _load_registry()
    if not registry:
        pytest.skip("format_registry.yaml not on disk in this checkout")
    scorecard = _load_scorecard()
    derived = derive_all(registry, scorecard_config=scorecard)

    # All 10 fully-specced formats derive; none of the 10 stubs do.
    expected_specced = set(WORKED.keys())
    assert expected_specced.issubset(set(derived.keys())), (
        f"missing derived formats: {expected_specced - set(derived.keys())}"
    )
    stubs = {
        "five_min_practice", "pocket_guide", "ten_things_to_do",
        "symptom_to_action_atlas", "daily_text_audio_companion", "crisis_cards",
        "weekly_challenge_pack", "faq_audiobook", "myth_vs_mechanism",
        "protocol_library",
    }
    assert not (stubs & set(derived.keys())), "stub formats must be skipped"

    # The derived values must match the registry's stored audiobook/ebook fields
    # (i.e. config and helper agree — the SSOT invariant).
    runtime = registry["runtime_formats"]
    for name, vals in derived.items():
        fmt = runtime[name]
        if "audiobook_minutes" in fmt:
            assert fmt["audiobook_minutes"] == vals["audiobook_minutes"], (
                f"{name}: registry audiobook_minutes != derived"
            )
        if "ebook_minutes" in fmt:
            assert fmt["ebook_minutes"] == vals["ebook_minutes"], (
                f"{name}: registry ebook_minutes != derived"
            )
        # The deprecated duration_minutes should have been overwritten with the
        # derived audiobook value (§9).
        if "duration_minutes" in fmt:
            assert fmt["duration_minutes"] == vals["audiobook_minutes"], (
                f"{name}: duration_minutes not overwritten with derived audiobook"
            )
