#!/usr/bin/env python3
"""
Pearl News — Claude-powered slot expansion.

Delegates to `slot_expansion_engine` (shared with Qwen). Constants are re-exported
for backward compatibility with imports of `TEMPLATE_SLOTS_V52`, etc.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

from pearl_news.pipeline.slot_expansion_constants import (
    EXPLAINER_OPTIONAL_V52_SLOTS,
    EXPLAINER_V52_SLOTS,
    INTERFAITH_SLOTS,
    OPTIONAL_V52_SLOTS,
    STANDARD_V52_SLOTS,
    TEMPLATE_SLOTS,
    TEMPLATE_SLOTS_V52,
    V52_SLOT_MAP,
    V52_TO_LEGACY_MAP,
)
from pearl_news.pipeline.slot_expansion_engine import AnthropicBackend, expand_item_slots

logger = logging.getLogger(__name__)

__all__ = [
    "EXPLAINER_OPTIONAL_V52_SLOTS",
    "EXPLAINER_V52_SLOTS",
    "INTERFAITH_SLOTS",
    "OPTIONAL_V52_SLOTS",
    "STANDARD_V52_SLOTS",
    "TEMPLATE_SLOTS",
    "TEMPLATE_SLOTS_V52",
    "V52_SLOT_MAP",
    "V52_TO_LEGACY_MAP",
    "expand_with_claude",
]


def expand_with_claude(
    items: list[dict[str, Any]],
    config_root: Path | None = None,
    simulate: bool = False,
    provider_cfg: dict[str, Any] | None = None,
    max_retries: int = 1,
) -> list[dict[str, Any]]:
    """
    For each item, generate article content slot-by-slot using Claude via the shared engine.
    """
    root = Path(__file__).resolve().parent.parent
    config_root = config_root or (root / "config")
    prompts_root = root / "prompts"
    prov = provider_cfg or {}

    config_path = config_root / "llm_expansion.yaml"
    config: dict[str, Any] = {}
    if config_path.exists() and yaml:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    repo_root = Path(__file__).resolve().parents[2]
    backend = AnthropicBackend(prov, config=config)

    if not simulate and not backend.has_api_key():
        logger.error("No Anthropic API key found (ANTHROPIC_API_KEY or claude_api_key.rtf)")
        for item in items:
            item["_expansion_failed"] = True
            item["_expansion_error"] = "no_anthropic_api_key"
        return items

    logger.info("Claude expansion (slot engine): model=%s, %d items", backend.model_id, len(items))

    for item in items:
        lang = str(item.get("language") or "en").lower()
        expand_item_slots(
            item,
            backend=backend,
            config=config,
            prompts_root=prompts_root,
            repo_root=repo_root,
            language=lang,
            max_retries=max_retries,
            simulate=simulate,
            provider_cfg=prov,
        )
        if not item.get("_expansion_failed"):
            item["_expansion_provider"] = "claude"

    return items
