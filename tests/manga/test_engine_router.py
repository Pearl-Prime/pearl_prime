"""Tests for V2 Phase B.7 engine router."""
from __future__ import annotations

from pathlib import Path

from scripts.manga.character_individuation.engine_router import (
    ENGINE_ANIMAGINE,
    ENGINE_FLUX_SCHNELL,
    ENGINE_QWEN,
    select_engine,
    load_brand_list,
)


_BRAND_LIST = {
    "brands": {
        "stillness_press": {"demographic": "seinen"},
        "cognitive_clarity": {"demographic": "josei"},
        "warrior_calm": {"demographic": "seinen"},
        "qi_foundation": {"demographic": "seinen"},
    }
}


def test_seinen_essay_routes_to_qwen():
    sel = select_engine(brand_id="cognitive_clarity", genre="essay",
                         market_demo="josei", brand_list=_BRAND_LIST)
    # essay is in _QWEN_GENRES → Qwen wins despite josei demographic
    assert sel.engine == ENGINE_QWEN
    assert "Qwen-Image" in sel.reasoning


def test_josei_healing_routes_to_animagine():
    sel = select_engine(brand_id="stillness_press", genre="healing",
                         brand_list=_BRAND_LIST)
    assert sel.engine == ENGINE_ANIMAGINE
    assert "Animagine" in sel.reasoning


def test_seinen_battle_routes_to_animagine():
    sel = select_engine(brand_id="warrior_calm", genre="battle", brand_list=_BRAND_LIST)
    assert sel.engine == ENGINE_ANIMAGINE


def test_color_mode_overrides_genre_to_flux_schnell():
    sel = select_engine(brand_id="stillness_press", genre="healing",
                         color_mode="color", brand_list=_BRAND_LIST)
    # color_mode=color forces FLUX-schnell baseline
    assert sel.engine == ENGINE_FLUX_SCHNELL
    assert "color" in sel.reasoning


def test_brand_demographic_lookup_when_market_demo_unset():
    sel = select_engine(brand_id="stillness_press", genre=None, brand_list=_BRAND_LIST)
    # demographic from brand list = seinen → Qwen
    assert sel.engine == ENGINE_QWEN


def test_unknown_brand_no_genre_falls_back_to_flux_schnell():
    sel = select_engine(brand_id=None, genre=None, brand_list=_BRAND_LIST)
    assert sel.engine == ENGINE_FLUX_SCHNELL
    assert sel.fallback_used is True
    assert "fallback" in sel.fallback_reason.lower()


def test_use_reference_picks_pulid_workflow_for_flux():
    sel = select_engine(brand_id=None, use_reference=True, brand_list=_BRAND_LIST)
    # FLUX fallback + use_reference=True → PuLID variant
    assert sel.engine == ENGINE_FLUX_SCHNELL
    assert "pulid" in sel.workflow_path.name.lower()
    assert sel.reference_enabled is True


def test_no_reference_picks_non_pulid_workflow():
    sel = select_engine(brand_id=None, use_reference=False, brand_list=_BRAND_LIST)
    assert sel.engine == ENGINE_FLUX_SCHNELL
    # non-PuLID FLUX path = the existing brand-2 V1 workflow
    assert "pulid" not in sel.workflow_path.name.lower()
    assert sel.reference_enabled is False


def test_qwen_keeps_workflow_under_use_reference_flag():
    sel = select_engine(brand_id="cognitive_clarity", genre="essay",
                         use_reference=True, brand_list=_BRAND_LIST)
    assert sel.engine == ENGINE_QWEN
    # Same workflow file used with reference slot conditional
    assert "qwen" in sel.workflow_path.name.lower()


def test_sampler_config_matches_engine():
    flux = select_engine(brand_id=None, brand_list=_BRAND_LIST)
    assert flux.sampler["steps"] == 4
    assert flux.sampler["cfg"] == 1.0

    animagine = select_engine(brand_id="stillness_press", genre="healing", brand_list=_BRAND_LIST)
    assert animagine.sampler["steps"] == 28
    assert animagine.sampler["cfg"] == 6.0

    qwen = select_engine(brand_id="cognitive_clarity", genre="essay", brand_list=_BRAND_LIST)
    assert qwen.sampler["steps"] == 24
    assert qwen.sampler["cfg"] == 4.0


def test_to_dict_serialisable():
    sel = select_engine(brand_id="stillness_press", genre="healing", brand_list=_BRAND_LIST)
    d = sel.to_dict()
    assert d["engine"] == ENGINE_ANIMAGINE
    assert d["sampler"]["steps"] == 28
    assert isinstance(d["workflow_path"], str)


def test_load_brand_list_against_real_repo():
    bl = load_brand_list()
    # canonical_brand_list.yaml on main has the 37-brand canon
    assert "brands" in bl
    # at least one stillness_press-like brand exists
    brands = bl["brands"]
    if isinstance(brands, dict):
        assert len(brands) >= 1
    elif isinstance(brands, list):
        assert len(brands) >= 1


# ── Phase B Path B fallback (operator-supervised install scenario) ──────────

def test_available_engines_filter_degrades_to_flux_when_qwen_not_installed():
    """Path B: Qwen install deferred. seinen/essay routes that would pick
    Qwen instead degrade to FLUX-schnell with explicit fallback reasoning."""
    sel = select_engine(
        brand_id="cognitive_clarity", genre="essay",
        market_demo="josei", brand_list=_BRAND_LIST,
        available_engines={ENGINE_FLUX_SCHNELL, ENGINE_ANIMAGINE},
    )
    assert sel.engine == ENGINE_FLUX_SCHNELL
    assert sel.fallback_used is True
    assert "qwen_image" in sel.fallback_reason or "Qwen-Image" in sel.fallback_reason or "qwen" in sel.fallback_reason.lower()


def test_available_engines_passes_through_when_chosen_engine_installed():
    """Animagine route passes through when Animagine IS in available_engines."""
    sel = select_engine(
        brand_id="stillness_press", genre="healing",
        brand_list=_BRAND_LIST,
        available_engines={ENGINE_FLUX_SCHNELL, ENGINE_ANIMAGINE},
    )
    assert sel.engine == ENGINE_ANIMAGINE
    # Routing-rule fallback should NOT fire — engine matched the routing
    # rule AND was available
    assert "not in available_engines" not in sel.fallback_reason


def test_available_engines_none_means_trust_routing_rules():
    """available_engines=None preserves pre-runtime-registry behavior
    (the unit-test default + the back-compat path for non-Pearl-Star
    consumers)."""
    sel = select_engine(
        brand_id="cognitive_clarity", genre="essay",
        market_demo="josei", brand_list=_BRAND_LIST,
        available_engines=None,
    )
    # No availability check applied — Qwen wins per the routing rule
    assert sel.engine == ENGINE_QWEN
