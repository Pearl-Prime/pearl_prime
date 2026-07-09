from __future__ import annotations

from scripts.manga.prompt_authority import (
    build_authority_prompt_block,
    resolve_canonical_genre,
    task_to_base_model,
)


def test_alias_resolution_uses_canonical_genre_registry() -> None:
    assert resolve_canonical_genre("psychological_thriller") == "mystery"
    assert resolve_canonical_genre("iyashikei") == "healing"


def test_flux_dev_override_falls_back_to_supported_prompt_family() -> None:
    assert task_to_base_model("t2i_flux_dev_h1a") == "flux_schnell"


def test_healing_authority_block_carries_research_tokens() -> None:
    style, negative, provenance = build_authority_prompt_block(
        genre_id="healing",
        task="t2i_flux_schnell",
        market_demo="josei",
        visual_grammar="healing_iyashikei",
        extra_style="soft pen-and-ink linework",
    )
    low = style.lower()
    assert "josei manga register" in low
    assert "soft pen-and-ink linework" in low
    assert any(token in low for token in ("watercolor", "peaceful", "gentle", "slice of life"))
    assert provenance["tradition_tokens_applied"] is True
    assert "dramatic" in negative.lower() or "harsh" in negative.lower()
