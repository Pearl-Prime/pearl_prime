"""Tests for visual_from_script_v3 — v3 chapter_script → panel_prompts."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.visual_from_script_v3 import (  # type: ignore
    _STYLE_ANCHORS,
    _BASE_NEGATIVE,
    compile_v3_panel_prompts,
)


def _min_script(panels: list[dict]) -> dict:
    return {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_script_writer_handoff",
        "series_id": "test_series",
        "chapter_id": "ep_001",
        "style": "cozy_iyashikei",
        "main_characters": [
            {"id": "mira", "name": "Mira Aoki", "visual_anchor": "long brown hair, cream sweater"}
        ],
        "scene_palette": {
            "primary": "warm cream + dawn gold",
            "secondary": "muted sage",
            "accent": "jade green",
            "flashback_palette": "desaturated cool grey-blue",
        },
        "pages": [{"panels": panels}],
    }


# ─── basic compilation ─────────────────────────────────────────────────────


def test_compile_emits_one_prompt_per_panel():
    script = _min_script([
        {"panel_id": "p001", "scene": "morning bedroom", "beat_type": "spatial"},
        {"panel_id": "p002", "scene": "tea cup close", "beat_type": "micro"},
    ])
    out = compile_v3_panel_prompts(script)
    assert out["artifact_type"] == "panel_prompts"
    assert out["total_panels"] == 2
    assert len(out["panels"]) == 2
    assert out["panels"][0]["panel_id"] == "p001"
    assert out["panels"][1]["panel_id"] == "p002"


def test_compile_includes_palette_in_prompt():
    script = _min_script([{"panel_id": "p1", "scene": "kitchen morning"}])
    out = compile_v3_panel_prompts(script)
    assert "warm cream" in out["panels"][0]["prompt"]
    assert "jade green" in out["panels"][0]["prompt"]


def test_compile_includes_character_lock_in():
    script = _min_script([{"panel_id": "p1", "scene": "test"}])
    out = compile_v3_panel_prompts(script)
    assert "Mira Aoki" in out["panels"][0]["prompt"]
    assert "long brown hair" in out["panels"][0]["prompt"]


def test_compile_includes_scene_text_verbatim():
    script = _min_script([{"panel_id": "p1", "scene": "specific marker xyz789"}])
    out = compile_v3_panel_prompts(script)
    assert "specific marker xyz789" in out["panels"][0]["prompt"]


def test_compile_uses_style_anchor_tail():
    script = _min_script([{"panel_id": "p1", "scene": "test"}])
    out = compile_v3_panel_prompts(script)
    # cozy_iyashikei tail mentions iyashikei + Studio Ghibli
    prompt = out["panels"][0]["prompt"]
    assert "iyashikei" in prompt.lower()
    assert "ghibli" in prompt.lower() or "studio ghibli" in prompt.lower()


# ─── beat_type → composition cue ─────────────────────────────────────────


def test_beat_type_long_drop_includes_decompression_cue():
    script = _min_script([{"panel_id": "p1", "scene": "silent kitchen", "beat_type": "long_drop"}])
    out = compile_v3_panel_prompts(script)
    prompt = out["panels"][0]["prompt"]
    assert "decompression" in prompt.lower() or "negative space" in prompt.lower()


def test_beat_type_micro_includes_close_up():
    script = _min_script([{"panel_id": "p1", "scene": "hand on cup", "beat_type": "micro"}])
    out = compile_v3_panel_prompts(script)
    assert "close-up" in out["panels"][0]["prompt"].lower()


def test_beat_type_miyazaki_ma_includes_awe_cue():
    script = _min_script([{"panel_id": "p1", "scene": "vast sky", "beat_type": "miyazaki_ma"}])
    out = compile_v3_panel_prompts(script)
    p = out["panels"][0]["prompt"].lower()
    assert "awe" in p or "vast" in p


# ─── flashback palette swap ──────────────────────────────────────────────


def test_flashback_panel_uses_flashback_palette():
    script = _min_script([
        {
            "panel_id": "fb1",
            "scene": "FLASHBACK PALETTE — desaturated, cool grey-blue. A conference room.",
            "beat_type": "standard",
            "intent": "Pendulation — past failure register",
        }
    ])
    out = compile_v3_panel_prompts(script)
    prompt = out["panels"][0]["prompt"]
    # Palette should be the flashback (desaturated cool grey-blue), NOT the warm cream primary
    assert "desaturated" in prompt or "grey-blue" in prompt
    # Primary palette warm cream should NOT be in this panel
    assert "warm cream" not in prompt


def test_non_flashback_panel_uses_primary_palette():
    script = _min_script([{"panel_id": "p1", "scene": "kitchen morning"}])
    out = compile_v3_panel_prompts(script)
    prompt = out["panels"][0]["prompt"]
    assert "warm cream" in prompt
    assert "desaturated" not in prompt


# ─── negative prompt ──────────────────────────────────────────────────────


def test_negative_prompt_contains_anti_ai_look_terms():
    script = _min_script([{"panel_id": "p1", "scene": "test"}])
    out = compile_v3_panel_prompts(script)
    neg = out["panels"][0]["negative_prompt"]
    assert "extra fingers" in neg
    assert "uncanny" in neg.lower() or "AI gloss" in neg


def test_all_panels_share_the_same_negative_prompt():
    script = _min_script([
        {"panel_id": "p1", "scene": "test1"},
        {"panel_id": "p2", "scene": "test2"},
    ])
    out = compile_v3_panel_prompts(script)
    assert out["panels"][0]["negative_prompt"] == out["panels"][1]["negative_prompt"]
    assert out["panels"][0]["negative_prompt"] == _BASE_NEGATIVE


# ─── series/chapter id propagation ───────────────────────────────────────


def test_series_and_chapter_id_propagate():
    script = _min_script([{"panel_id": "p1", "scene": "test"}])
    out = compile_v3_panel_prompts(script)
    assert out["series_id"] == "test_series"
    assert out["chapter_id"] == "ep_001"


def test_total_panels_matches_count():
    script = _min_script([
        {"panel_id": "p1", "scene": "a"},
        {"panel_id": "p2", "scene": "b"},
        {"panel_id": "p3", "scene": "c"},
    ])
    out = compile_v3_panel_prompts(script)
    assert out["total_panels"] == 3


# ─── style_overrides ─────────────────────────────────────────────────────


def test_style_override_changes_anchor():
    script = _min_script([{"panel_id": "p1", "scene": "fight scene"}])
    out = compile_v3_panel_prompts(script, style_overrides={"style_id": "power_progression"})
    prompt = out["panels"][0]["prompt"].lower()
    assert "shonen" in prompt or "solo leveling" in prompt


def test_unknown_style_falls_back_to_cozy_iyashikei():
    script = _min_script([{"panel_id": "p1", "scene": "test"}])
    script["style"] = "not_a_real_style"
    out = compile_v3_panel_prompts(script)
    # Default cozy_iyashikei tail should still apply
    assert "iyashikei" in out["panels"][0]["prompt"].lower()


# ─── error paths ──────────────────────────────────────────────────────────


def test_panel_without_panel_id_raises():
    script = _min_script([{"scene": "no id"}])
    with pytest.raises(ValueError, match="panel_id"):
        compile_v3_panel_prompts(script)


def test_panel_without_scene_uses_default_quiet_beat():
    script = _min_script([{"panel_id": "p1"}])
    out = compile_v3_panel_prompts(script)
    assert "quiet" in out["panels"][0]["prompt"].lower() or "ambient" in out["panels"][0]["prompt"].lower()


# ─── style anchor coverage ───────────────────────────────────────────────


def test_all_six_documented_styles_resolve():
    """The 6 styles named in MANGA_FULL_CATALOG_PLAN.md must all have anchors."""
    expected_styles = {
        "cozy_iyashikei", "dark_psychological", "hyper_clean_cinematic",
        "power_progression", "webtoon_vertical_romance", "social_media_simulacra",
    }
    for style in expected_styles:
        assert style in _STYLE_ANCHORS, f"missing style anchor: {style}"
        anchor = _STYLE_ANCHORS[style]
        assert "tail" in anchor and anchor["tail"], f"{style}: empty tail"
        assert "palette" in anchor, f"{style}: missing palette"
        assert "lighting" in anchor, f"{style}: missing lighting"


# ─── end-to-end against ep_001 (the real chapter script) ───────────────


def test_real_ep001_compiles_to_35_prompts():
    """The committed ep_001 chapter script (PR #651) should compile cleanly."""
    import yaml  # type: ignore

    ep001_path = (
        REPO / "artifacts" / "manga" / "chapter_scripts" /
        "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying" / "ep_001.yaml"
    )
    if not ep001_path.exists():
        pytest.skip("ep_001 not yet on this branch")
    script = yaml.safe_load(ep001_path.read_text(encoding="utf-8"))
    out = compile_v3_panel_prompts(script)
    assert out["total_panels"] == 35
    # The Long Drop panel (29) should have decompression in its prompt
    long_drop = [p for p in out["panels"] if p.get("beat_type") == "long_drop"]
    assert len(long_drop) == 1
    assert "decompression" in long_drop[0]["prompt"].lower() or "negative space" in long_drop[0]["prompt"].lower()
    # The flashback panel (16) should use the desaturated palette
    fb_panels = [p for p in out["panels"] if "flashback" in p["composition_notes"]["scene_excerpt"].lower()]
    if fb_panels:
        assert "desaturated" in fb_panels[0]["prompt"].lower() or "grey-blue" in fb_panels[0]["prompt"].lower()
