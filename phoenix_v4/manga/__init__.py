"""Phoenix Omega manga kernel: prompts, manifests, assets, artifact models, transmission, chapter stubs."""

from phoenix_v4.manga.asset_resolver import resolve_panel_asset, resolve_panel_assets
from phoenix_v4.manga.panel_prompt_manifest import compile_panel_prompts
from phoenix_v4.manga.visual_prompt_compiler import (
    VisualPromptRequest,
    compile_visual_prompt,
    resolve_panel_layout,
)

__all__ = [
    "VisualPromptRequest",
    "compile_panel_prompts",
    "compile_visual_prompt",
    "resolve_panel_asset",
    "resolve_panel_assets",
    "resolve_panel_layout",
]
