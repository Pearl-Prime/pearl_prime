from __future__ import annotations

from phoenix_v4.manga.asset_resolver import resolve_panel_assets
from phoenix_v4.manga.panel_prompt_manifest import compile_panel_prompts


def _chapter_request() -> dict:
    return {
        "chapter_id": "chapter-001",
        "variant_id": "dark-psych",
        "base_seed": 500,
        "panels": [
            {
                "panel_id": "p000",
                "atom_type": "HOOK",
                "atom_text": "The doorway was never locked.",
                "style_id": "dark_psychological",
                "teacher_id": "ahjan",
                "engine_type": "shame",
                "cost_intensity": "high",
                "panel_expression": "silent doorway threshold, release beat",
            },
            {
                "panel_id": "p001",
                "atom_type": "EXERCISE",
                "atom_text": "Hand on chest. Wait for the breath to return.",
                "style_id": "cozy_iyashikei",
                "teacher_id": "maat",
                "engine_type": "grief",
                "cost_intensity": "low",
            },
        ],
    }


def test_compile_panel_prompts_assigns_ids_and_seeds() -> None:
    doc = compile_panel_prompts(_chapter_request(), config_hash="cfg123")

    assert doc["chapter_id"] == "chapter-001"
    assert doc["config_hash"] == "cfg123"
    assert [panel["seed"] for panel in doc["panels"]] == [500, 501]
    assert doc["panels"][0]["panel_id"] == "p000"


def test_resolve_panel_assets_prefers_matching_bank_asset() -> None:
    prompt_doc = compile_panel_prompts(_chapter_request(), config_hash="cfg123")
    assets = [
        {
            "asset_id": "hook-001",
            "atom_type": "HOOK",
            "style_id": "dark_psychological",
            "teacher_id": "ahjan",
            "engine_type": "shame",
            "panel_function": "splash_panel",
            "continuity_tags": ["teacher:ahjan", "style:dark_psychological", "engine:shame"],
            "composition_compat": {"page": 0.9},
        }
    ]

    result = resolve_panel_assets(prompt_doc, assets)

    assert result["resolved"][0]["asset_id"] == "hook-001"
    assert result["resolved"][0]["requires_generation"] is False
    assert result["resolved"][1]["source"] == "placeholder"
    assert result["unresolved_panel_ids"] == ["p001"]
