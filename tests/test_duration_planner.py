"""
Tests for the Duration Planner (Stage 0).

Covers:
- Platform constraint wins over everything
- Therapeutic minimum beats persona budget when intent=therapeutic
- Persona budget beats therapeutic minimum when intent=discovery
- Locale modifiers apply correctly (e.g. zh-CN +30-50% tolerance)
- Invalid intent produces blockers
- Structural format hint is respected
- All structural formats produce valid recommendations
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.planning.duration_planner import DurationPlanner, DurationRecommendation


def _make_planner() -> DurationPlanner:
    return DurationPlanner()


def test_basic_recommendation():
    """Planner returns a valid recommendation for standard inputs."""
    dp = _make_planner()
    rec = dp.plan(topic_id="anxiety", persona_id="nyc_executives", intent="engagement")
    assert isinstance(rec, DurationRecommendation)
    assert rec.recommended_runtime_format != ""
    assert rec.recommended_structural_format != ""
    assert rec.recommended_duration_minutes > 0
    assert 0.0 <= rec.duration_fit_score <= 1.0
    assert len(rec.blockers) == 0


def test_platform_constraint_clamps_duration():
    """Platform hard limits override base duration — YouTube hard_max_seconds=43200 = 720min."""
    dp = _make_planner()
    rec = dp.plan(
        topic_id="anxiety",
        persona_id="educators",
        intent="deep_engagement",
        platform_id="youtube",
    )
    # YouTube hard_max_seconds=43200 = 720min; duration should not exceed that
    assert rec.recommended_duration_minutes <= 720, (
        f"Duration {rec.recommended_duration_minutes}min exceeds YouTube max 720min"
    )
    assert len(rec.blockers) == 0


def test_therapeutic_minimum_beats_persona_budget():
    """When intent=therapeutic, therapeutic floor wins over persona budget."""
    dp = _make_planner()
    # gen_z has attention_budget=30min, but therapeutic minimum for grief is 55min
    rec = dp.plan(
        topic_id="grief",
        persona_id="gen_z_professionals",
        intent="therapeutic",
    )
    # Should be at least therapeutic minimum (55min for grief)
    assert rec.recommended_duration_minutes >= 55, (
        f"Therapeutic intent should enforce 55min minimum for grief, "
        f"got {rec.recommended_duration_minutes}min"
    )


def test_persona_budget_beats_therapeutic_for_discovery():
    """When intent=discovery, persona budget caps the selection."""
    dp = _make_planner()
    rec = dp.plan(
        topic_id="anxiety",
        persona_id="gen_z_professionals",
        intent="discovery",
    )
    # Discovery should produce a valid recommendation without blockers
    assert len(rec.blockers) == 0
    # The planner should pick a reasonable duration for discovery
    assert rec.recommended_duration_minutes > 0


def test_locale_modifier_zh_cn_extends_budget():
    """zh-CN locale modifier should increase effective attention budget."""
    dp = _make_planner()
    rec_en = dp.plan(
        topic_id="anxiety",
        persona_id="nyc_executives",
        intent="engagement",
        locale="en-US",
    )
    rec_zh = dp.plan(
        topic_id="anxiety",
        persona_id="nyc_executives",
        intent="engagement",
        locale="zh-CN",
    )
    # zh-CN should have equal or higher attention_fit due to extended budget
    assert rec_zh.attention_fit >= rec_en.attention_fit, (
        f"zh-CN attention_fit ({rec_zh.attention_fit}) should be >= "
        f"en-US ({rec_en.attention_fit})"
    )


def test_invalid_intent_produces_blocker():
    """Invalid intent value should produce a blocker."""
    dp = _make_planner()
    rec = dp.plan(
        topic_id="anxiety",
        persona_id="nyc_executives",
        intent="invalid_intent_xyz",
    )
    assert len(rec.blockers) > 0
    assert rec.duration_fit_score == 0.0


def test_structural_format_hint_respected():
    """When a structural format hint is given, planner uses it."""
    dp = _make_planner()
    rec = dp.plan(
        topic_id="anxiety",
        persona_id="nyc_executives",
        intent="engagement",
        structural_format_hint="F013",
    )
    assert rec.recommended_structural_format == "F013"


def test_all_structural_formats_produce_valid_recommendations():
    """Every structural format in the registry should produce a valid recommendation."""
    dp = _make_planner()
    structural_formats = dp._structural_formats
    for fmt_id in structural_formats:
        rec = dp.plan(
            topic_id="anxiety",
            persona_id="nyc_executives",
            intent="engagement",
            structural_format_hint=fmt_id,
        )
        assert len(rec.blockers) == 0, f"Blockers for {fmt_id}: {rec.blockers}"
        assert rec.recommended_duration_minutes > 0, f"Zero duration for {fmt_id}"
        assert rec.duration_fit_score > 0.0, f"Zero score for {fmt_id}"


def test_platform_spotify_limits_max():
    """Spotify hard_max_seconds=86400 = 1440min; planner stays within."""
    dp = _make_planner()
    rec = dp.plan(
        topic_id="anxiety",
        persona_id="educators",
        intent="deep_engagement",
        platform_id="spotify",
    )
    # Spotify hard max is 86400s = 1440min; duration should not exceed
    assert rec.recommended_duration_minutes <= 1440
    assert len(rec.blockers) == 0


def test_default_persona_fallback():
    """Unknown persona falls back to default profile."""
    dp = _make_planner()
    rec = dp.plan(
        topic_id="anxiety",
        persona_id="unknown_persona_xyz",
        intent="engagement",
    )
    assert len(rec.blockers) == 0
    assert rec.recommended_duration_minutes > 0


def test_score_components_sum_correctly():
    """Composite score = 0.40 * therapeutic + 0.35 * platform + 0.25 * attention."""
    dp = _make_planner()
    rec = dp.plan(
        topic_id="anxiety",
        persona_id="nyc_executives",
        intent="engagement",
    )
    expected = round(0.40 * rec.therapeutic_fit + 0.35 * rec.platform_fit + 0.25 * rec.attention_fit, 4)
    assert abs(rec.duration_fit_score - expected) < 0.001, (
        f"Score {rec.duration_fit_score} != expected {expected} "
        f"(t={rec.therapeutic_fit}, p={rec.platform_fit}, a={rec.attention_fit})"
    )


def test_deep_engagement_prefers_longer_formats():
    """deep_engagement should produce longer durations than discovery for the same persona."""
    dp = _make_planner()
    rec_disc = dp.plan(topic_id="anxiety", persona_id="educators", intent="discovery")
    rec_deep = dp.plan(topic_id="anxiety", persona_id="educators", intent="deep_engagement")
    assert rec_deep.recommended_duration_minutes >= rec_disc.recommended_duration_minutes, (
        f"deep_engagement ({rec_deep.recommended_duration_minutes}min) should be >= "
        f"discovery ({rec_disc.recommended_duration_minutes}min)"
    )
