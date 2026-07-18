"""Tests for V2 Phase A.2/A.5 prompt builder."""
from __future__ import annotations

from scripts.manga.character_individuation.prompt_builder import (
    BuilderConfig,
    build_prompt,
    load_builder_config,
    _genre_tokens,
    _blended_genre_tokens,
    _forbidden_tokens,
)


_AXES_CONFIG = {}  # builder doesn't read axes_config directly; rules live in tradition + blending + forbidden
_TRADITION = {
    "genres": {
        "healing": {
            "status": "top_8_deep",
            "A_line_tradition": {
                "line_weight_profile": "variable_quiet",
                "ink_density": "minimal",
            },
            "D_palette": {"dominant_value": "muted_warm"},
            "mangaka_exemplars": [{"name": "Yokoyari Mengo"}],
        },
        "dark_fantasy": {
            "status": "top_8_deep",
            "A_line_tradition": {
                "line_weight_profile": "heavy_dramatic",
                "ink_density": "dense",
            },
            "F_mangaka_exemplars": [{"name": "Berserk-Miura"}],
        },
        "battle": {"status": "deferred_phase2"},  # stub
    }
}
_BLENDING = {
    "pairs": {
        "healing_plus_slice_of_life": {
            "operator_status": "working_anchor",
            "blend_signature": "iyashikei tones with slice_of_life everydayness",
        },
        "healing_plus_dark_fantasy": {
            "operator_status": "intentional_divergence",
            "blend_signature": "iyashikei tones with dark_fantasy mood",
        },
    }
}
_FORBIDDEN = {
    "universal": {
        "quality_floor": ["low quality", "blurry"],
        "anatomy_floor": ["extra fingers"],
        "text_lock": ["text", "letters"],
        "unwanted_modes": ["photorealistic"],
    },
    "per_genre": {
        "healing": ["sparkle", "violence"],
        "dark_fantasy": ["bright cheerful"],
    },
    "per_market_demo": {
        "josei": ["shojo sparkle", "bow mouth"],
    },
    "base_model_adapter": {
        "animagine_xl_4_0": {"style": "danbooru_tags", "join": ", ", "cap_tokens": 30},
        "qwen_image": {"style": "natural_language_prose", "prefix": "avoiding ", "join": ", ", "cap_tokens": 20},
        "flux_schnell": {"style": "terse_tags", "join": ", ", "cap_tokens": 10},
    },
}


def _design(market_demo="josei"):
    return {
        "series_id": "test_s",
        "brand_id": "test_b",
        "market_demo": market_demo,
        "genre_family": "healing",
        "axes": {
            "face_shape": {"value": "heart_shaped", "lockout": "yes"},
            "eye_geometry": {
                "size": "small", "shape": "almond", "lid_fold": "single",
                "eyelash_density": "minimal", "lockout": "yes",
            },
            "hair": {
                "length": "shoulder", "parting": "side_left",
                "fringe_style": "side_swept", "texture": "straight",
                "color_signal": "dark_brown_with_grey", "lockout": "yes",
            },
            "color_signal": {"value": "muted_brown", "lockout": "yes"},
            "wardrobe_register": {"value": "everyday_casual", "lockout": "yes"},
            "age_signaling": {"value": "late_30s", "lockout": "yes"},
            "accessories": {"value": "round_glasses", "lockout": "yes"},
            "mouth_jaw": {"lip_shape": "thin_upper_full_lower", "lockout": "yes"},
            "nose_construction": {"value": "straight_pointed", "lockout": "yes"},
            "skin_treatment": {"value": "clean", "lockout": "no"},
            "build": {"value": "average", "lockout": "no"},
            "posture_default": {"value": "neutral_relaxed", "lockout": "no"},
        },
    }


def _cfg(base="flux_schnell"):
    return BuilderConfig(
        base_model=base,
        width=1080,
        height=1920,
        axes_config=_AXES_CONFIG,
        tradition_config=_TRADITION,
        blending_config=_BLENDING,
        forbidden_config=_FORBIDDEN,
    )


# ── basic build ──────────────────────────────────────────────────────────────

def test_build_includes_scene_and_character_tokens():
    p = build_prompt(
        panel_id="ch01_p01",
        scene_description="A woman at a kitchen table at dawn",
        character_design=_design(),
        primary_genre="healing",
        builder_config=_cfg(),
    )
    assert p.panel_id == "ch01_p01"
    assert "kitchen table" in p.positive
    assert "small" in p.positive  # eye size
    assert "shoulder" in p.positive  # hair length
    assert p.engine == "flux_schnell"
    assert p.width == 1080 and p.height == 1920


def test_genre_tokens_added_for_top8():
    p = build_prompt(
        panel_id="x", scene_description="scene",
        character_design=_design(), primary_genre="healing",
        builder_config=_cfg(),
    )
    assert "Yokoyari Mengo" in p.positive
    assert "variable quiet" in p.positive  # line_weight_profile token


def test_genre_tokens_skipped_for_deferred_phase2_genre():
    p = build_prompt(
        panel_id="x", scene_description="scene",
        character_design=_design(), primary_genre="battle",
        builder_config=_cfg(),
    )
    # battle has status=deferred_phase2 — no tokens emitted
    assert "Yokoyari Mengo" not in p.positive
    assert "variable quiet" not in p.positive


def test_cross_genre_blend_token_emitted():
    p = build_prompt(
        panel_id="x", scene_description="scene",
        character_design=_design(),
        primary_genre="healing", secondary_genre="slice_of_life",
        builder_config=_cfg(),
    )
    assert "iyashikei tones" in p.positive


def test_cross_genre_blend_no_op_when_secondary_missing():
    p = build_prompt(
        panel_id="x", scene_description="scene",
        character_design=_design(),
        primary_genre="healing", secondary_genre=None,
        builder_config=_cfg(),
    )
    assert "iyashikei tones" not in p.positive


# ── forbidden / negative ─────────────────────────────────────────────────────

def test_negative_includes_universal_and_per_genre_and_per_demo():
    p = build_prompt(
        panel_id="x", scene_description="scene",
        character_design=_design(market_demo="josei"),
        primary_genre="healing",
        builder_config=_cfg(base="animagine_xl_4_0"),
    )
    assert "low quality" in p.negative      # universal quality_floor
    assert "sparkle" in p.negative           # per_genre healing
    assert "shojo sparkle" in p.negative     # per_market_demo josei


def test_qwen_uses_natural_language_prefix():
    p = build_prompt(
        panel_id="x", scene_description="scene",
        character_design=_design(), primary_genre="healing",
        builder_config=_cfg(base="qwen_image"),
    )
    assert p.negative.startswith("avoiding ")


def test_flux_schnell_caps_negative_tokens_at_10():
    p = build_prompt(
        panel_id="x", scene_description="scene",
        character_design=_design(), primary_genre="healing",
        builder_config=_cfg(base="flux_schnell"),
    )
    # cap is 10 — fewer commas means truncation worked
    assert p.negative.count(",") < 12


def test_forbidden_tokens_helper_dedupes():
    out = _forbidden_tokens(_FORBIDDEN, genre_family="healing", market_demo="josei")
    # No duplicates
    assert len(out) == len(set(out))


# ── adapters ─────────────────────────────────────────────────────────────────

def test_animagine_emits_danbooru_style_tags():
    p = build_prompt(
        panel_id="x", scene_description="scene",
        character_design=_design(), primary_genre="healing",
        builder_config=_cfg(base="animagine_xl_4_0"),
    )
    # Animagine adapter format: "small eyes, almond eye shape" — single-word tags
    assert "small eyes" in p.positive


def test_qwen_emits_natural_language():
    p = build_prompt(
        panel_id="x", scene_description="scene",
        character_design=_design(), primary_genre="healing",
        builder_config=_cfg(base="qwen_image"),
    )
    # Qwen adapter format: "small almond eyes with single eyelid"
    assert "small almond eyes" in p.positive


# ── panel-prompt schema compatibility ────────────────────────────────────────

def test_to_panel_prompt_matches_queue_panel_renders_schema():
    p = build_prompt(
        panel_id="ch03_p02", scene_description="alley at dusk",
        character_design=_design(), primary_genre="healing",
        builder_config=_cfg(),
    )
    pp = p.to_panel_prompt()
    # Must carry every key the brand-2 queue_panel_renders.py reads from prompts[].
    for key in ("panel_id", "prompt", "negative_prompt", "model", "width", "height", "char_count"):
        assert key in pp
    assert pp["char_count"] == len(pp["prompt"])


# ── repo-config compatibility (smoke) ────────────────────────────────────────

def test_load_builder_config_against_real_repo():
    cfg = load_builder_config()
    assert "genres" in cfg.tradition_config
    assert "pairs" in cfg.blending_config
    assert "universal" in cfg.forbidden_config


# ── helper unit tests ────────────────────────────────────────────────────────

def test_genre_tokens_returns_empty_for_unknown_genre():
    assert _genre_tokens(_TRADITION, "made_up_genre") == []


def test_blended_genre_tokens_handles_reverse_pair_lookup():
    out = _blended_genre_tokens(_BLENDING, "slice_of_life", "healing")
    # Only "healing_plus_slice_of_life" exists; reverse should still match
    assert any("iyashikei" in tok for tok in out)
