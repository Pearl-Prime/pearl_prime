"""LANE D — render-routing + character-individuation wiring into the visual stage.

Covers CHARACTER_INDIVIDUATION_PIPELINE_SPEC §2.3/§2.5 + license_risk_register
2026-04-29: the production visual stage must (1) record a deterministic engine
routing decision and (2) fold axis-specific character tokens into each panel's
prompt — while staying backward-compatible for callers that pass no brand/genre.
"""
from __future__ import annotations

import re

import pytest

from phoenix_v4.manga.chapter.visual_from_script import (
    compile_panel_prompts_from_chapter_script,
)
from scripts.manga.character_individuation.engine_router import (
    ENGINE_ANIMAGINE,
    ENGINE_FLUX_SCHNELL,
)
from scripts.manga.character_individuation.prompt_builder import (
    build_prompt,
    load_builder_config,
)


def _chapter_script():
    return {
        "pages": [
            {
                "page_number": 1,
                "panels": [
                    {"panel_id": "c1p1", "action": "kneeling in quiet prayer at dawn",
                     "mood": "calm", "dialogue": ["..."]},
                    {"panel_id": "c1p2", "action": "a slow exhale, shoulders softening",
                     "mood": "calm"},
                ],
            }
        ]
    }


def _devotion_design(series_id: str, **axes) -> dict:
    blocks = {}
    for name, sub in axes.items():
        blk = dict(sub)
        blk["lockout"] = "yes"
        blocks[name] = blk
    return {
        "_series_id": series_id,
        "_brand_id": "devotion_path",
        "market_demo": "josei",
        "axes": blocks,
    }


# ── Backward compatibility ────────────────────────────────────────────────────

def test_legacy_call_without_brand_genre_is_verbatim():
    """No routing signal → no render_routing block (legacy artifact shape)."""
    doc = compile_panel_prompts_from_chapter_script(_chapter_script(), series_id="no_such_series")
    assert "render_routing" not in doc
    assert "render_routing" not in doc["panels"][0]
    # Core legacy fields still present
    assert doc["panels"][0]["panel_id"] == "c1p1"
    assert "prompt" in doc["panels"][0]


# ── Genre routing (LOCKED P0: devotion = healing / iyashikei → soft-line) ──────

@pytest.mark.parametrize("genre", ["healing", "iyashikei"])
def test_devotion_healing_routes_to_animagine_soft_line(genre):
    doc = compile_panel_prompts_from_chapter_script(
        _chapter_script(),
        series_id="devotion_demo",
        brand_id="devotion_path",
        genre_id=genre,
        market_demo="josei",
    )
    rr = doc["render_routing"]
    assert rr["engine"] == ENGINE_ANIMAGINE
    assert "animagine" in str(rr["workflow_path"]).lower()
    # mirrored onto every panel
    for p in doc["panels"]:
        assert p["render_routing"]["engine"] == ENGINE_ANIMAGINE


def test_routing_differs_from_legacy_flux_schnell_default():
    """Devotion-healing must NOT fall through to the FLUX-schnell-for-everything default."""
    doc = compile_panel_prompts_from_chapter_script(
        _chapter_script(), series_id="devotion_demo",
        brand_id="devotion_path", genre_id="healing", market_demo="josei",
    )
    assert doc["render_routing"]["engine"] != ENGINE_FLUX_SCHNELL


def test_color_mode_records_flux_schnell_baseline():
    doc = compile_panel_prompts_from_chapter_script(
        _chapter_script(), series_id="devotion_demo",
        brand_id="devotion_path", genre_id="healing", color_mode="color",
    )
    assert doc["render_routing"]["engine"] == ENGINE_FLUX_SCHNELL


# ── Character individuation distinctness ──────────────────────────────────────

def test_same_brand_devotion_characters_render_distinct():
    """Two same-brand devotion designs with different axes → distinct prompts
    (the average-face attractor is broken). Tested at the build_prompt layer that
    the visual stage folds in, using the Animagine engine the router selects for
    devotion-healing."""
    char_a = _devotion_design(
        "devotion_sai_disciple_A",
        face_shape={"value": "oval"},
        eye_geometry={"size": "large", "shape": "round", "lid_fold": "double",
                      "eyelash_density": "heavy"},
        hair={"length": "long", "parting": "center", "fringe_style": "curtain",
              "texture": "wavy", "color_signal": "black"},
    )
    char_b = _devotion_design(
        "devotion_sai_disciple_B",
        face_shape={"value": "heart"},
        eye_geometry={"size": "narrow", "shape": "almond", "lid_fold": "monolid",
                      "eyelash_density": "sparse"},
        hair={"length": "short", "parting": "side", "fringe_style": "swept",
              "texture": "straight", "color_signal": "silver"},
    )
    bcfg = load_builder_config(base_model=ENGINE_ANIMAGINE)
    pa = build_prompt(panel_id="p1", scene_description="kneeling in quiet prayer at dawn",
                      character_design=char_a, primary_genre="healing", builder_config=bcfg)
    pb = build_prompt(panel_id="p1", scene_description="kneeling in quiet prayer at dawn",
                      character_design=char_b, primary_genre="healing", builder_config=bcfg)
    assert pa.positive != pb.positive
    ta = set(re.split(r"[,.\s]+", pa.positive.lower()))
    tb = set(re.split(r"[,.\s]+", pb.positive.lower()))
    # Each character contributes its own distinguishing axis tokens.
    assert (ta - tb) and (tb - ta)
    assert "oval" in ta and "heart" in tb


def test_individuation_flag_set_when_design_present():
    """When a series has a character_design in the catalog, the pipeline folds it
    in and flags individuation_engaged=True on the chapter + panels."""
    from scripts.manga.character_individuation.constraint_solver import load_catalog_designs

    cat = load_catalog_designs()
    if not cat:
        pytest.skip("no character_design catalog available in this checkout")
    real = cat[0]
    series_id = str(real.get("_series_id"))
    brand_id = str(real.get("_brand_id"))
    market_demo = real.get("market_demo")
    doc = compile_panel_prompts_from_chapter_script(
        _chapter_script(),
        series_id=series_id,
        brand_id=brand_id,
        genre_id="healing",
        market_demo=market_demo,
    )
    assert doc["render_routing"]["individuation_engaged"] is True
    assert doc["panels"][0]["render_routing"]["individuation_engaged"] is True
