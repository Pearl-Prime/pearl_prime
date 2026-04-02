from __future__ import annotations

from phoenix_v4.manga.config import load_manga_gates, load_panel_layouts, load_seed_atoms, load_style_archetypes
from phoenix_v4.manga.visual_prompt_compiler import VisualPromptRequest, compile_visual_prompt, resolve_panel_layout


def test_manga_config_loaders_expose_kernel_inputs() -> None:
    styles = load_style_archetypes()
    layouts = load_panel_layouts()
    gates = load_manga_gates()
    atoms = load_seed_atoms()

    assert "dark_psychological" in styles
    assert "HOOK" in layouts
    assert gates["gates"]
    assert "seed_shame_hook_release" in atoms


def test_story_layout_expands_panel_count_by_mechanism_depth() -> None:
    assert resolve_panel_layout("STORY", "shallow")["panels"] == 4
    assert resolve_panel_layout("STORY", "moderate")["panels"] == 5
    assert resolve_panel_layout("STORY", "deep")["panels"] == 6


def test_compile_visual_prompt_uses_config_and_seed_override() -> None:
    prompt = compile_visual_prompt(
        VisualPromptRequest(
            atom_id="seed_shame_hook_release",
            atom_type="HOOK",
        )
    )

    assert prompt["panel_function"] == "splash_panel"
    assert "young woman, dark hair" in prompt["positive"]
    assert "doorway threshold" in prompt["positive"]
    assert prompt["silence_compliance"] is True
    assert "panel_expression=" in prompt["composition_notes"]


def test_compile_visual_prompt_supports_direct_request_overrides() -> None:
    prompt = compile_visual_prompt(
        VisualPromptRequest(
            atom_type="STORY",
            style_id="power_progression",
            teacher_id="ra",
            engine_type="overwhelm",
            cost_intensity="high",
            mechanism_depth="deep",
            panel_expression="energy bursting through a crowded frame",
        )
    )

    assert prompt["style_id"] == "power_progression"
    assert prompt["teacher_id"] == "ra"
    assert prompt["panels"] == 6
    assert "strong figure, commanding presence" in prompt["positive"]
    assert "cluttered environment" in prompt["positive"]
    assert prompt["prompt_token_count"] <= 120
    assert prompt["negative_token_count"] <= 60
