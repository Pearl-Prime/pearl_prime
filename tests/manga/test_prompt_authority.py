from __future__ import annotations

from scripts.manga.prompt_authority import (
    DEFAULT_PANEL_TASK,
    build_authority_prompt_block,
    build_panel_prompt,
    resolve_panel_task,
    task_to_base_model,
)
from phoenix_v4.manga.genre_tradition import (
    cookbook_entry,
    preferred_panel_model,
    resolve_canonical_genre,
)


def test_alias_resolution_uses_canonical_genre_registry() -> None:
    assert resolve_canonical_genre("psychological_thriller") == "mystery"
    assert resolve_canonical_genre("iyashikei") == "healing"


def test_panel_task_defaults_to_qwen_not_flux() -> None:
    assert task_to_base_model("t2i_panel_render") == "qwen_image"
    assert resolve_panel_task(None, genre_id="mecha") == DEFAULT_PANEL_TASK
    assert preferred_panel_model("mecha") == "qwen_image"


def test_flux_dev_override_still_maps_to_flux_family() -> None:
    assert task_to_base_model("t2i_flux_dev_h1a") == "flux_schnell"


def test_mecha_cookbook_entry_exists() -> None:
    entry = cookbook_entry("mecha")
    assert entry is not None
    assert entry["preferred_model"] == "qwen_image"
    assert "manga panel" in entry["positive_scaffold"].lower()


def test_healing_authority_block_carries_cookbook_register() -> None:
    style, negative, provenance = build_authority_prompt_block(
        genre_id="healing",
        task="t2i_qwen_image",
        market_demo="josei",
        visual_grammar="healing_iyashikei",
        extra_style="soft pen-and-ink linework",
        locale="en_US",
    )
    low = style.lower()
    assert "manga panel" in low
    assert "josei manga register" in low
    assert provenance["cookbook_applied"] is True
    assert provenance["base_model"] == "qwen_image"
    assert "stipple" in negative.lower() or "dramatic" in negative.lower()


def test_mecha_panel_prompt_has_five_slot_scaffold() -> None:
    style, negative, provenance = build_panel_prompt(
        genre_id="mecha",
        subject="pilot seated in cockpit harness",
        composition="medium close-up, panel border visible",
        locale="en_US",
        market_demo="seinen",
        task="t2i_qwen_image",
    )
    low = style.lower()
    assert "manga panel" in low
    assert "pilot seated" in low
    assert "medium close-up" in low
    assert provenance["scaffold_slots"]
    assert "REGISTER" in provenance["scaffold_slots"]
    assert "stipple" in negative.lower()
