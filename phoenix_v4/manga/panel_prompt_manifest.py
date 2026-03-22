"""Compile chapter panel requests into deterministic panel prompt manifests."""
from __future__ import annotations

from dataclasses import fields
from typing import Any

from phoenix_v4.manga.visual_prompt_compiler import VisualPromptRequest, compile_visual_prompt

REQUEST_FIELD_NAMES = {field.name for field in fields(VisualPromptRequest)}


def compile_panel_prompts(chapter_request: dict[str, Any], config_hash: str) -> dict[str, Any]:
    panels = chapter_request.get("panels") or []
    if not panels:
        raise ValueError("chapter_request.panels must contain at least one panel request")

    variant_id = chapter_request.get("variant_id", "default")
    base_seed = int(chapter_request.get("base_seed", 1000))
    compiled_panels: list[dict[str, Any]] = []

    for index, panel_request in enumerate(panels):
        panel_id = panel_request.get("panel_id") or f"p{index:03d}"
        seed = int(panel_request.get("seed", base_seed + index))
        request_kwargs = {key: value for key, value in panel_request.items() if key in REQUEST_FIELD_NAMES}
        prompt = compile_visual_prompt(VisualPromptRequest(**request_kwargs))
        compiled_panels.append(
            {
                **prompt,
                "panel_id": panel_id,
                "seed": seed,
            }
        )

    return {
        "chapter_id": chapter_request["chapter_id"],
        "variant_id": variant_id,
        "config_hash": config_hash,
        "panels": compiled_panels,
    }
