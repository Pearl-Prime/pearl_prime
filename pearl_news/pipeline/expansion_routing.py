"""
Language-based expansion routing: English → Claude (slot engine), CJK → Qwen slot engine (or legacy full-doc).
Reads `routing` section from pearl_news/config/llm_expansion.yaml.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


def _load_expansion_yaml(config_root: Path) -> dict[str, Any]:
    path = config_root / "llm_expansion.yaml"
    if not path.exists() or yaml is None:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _env_or(key: str | None, default: str | None) -> str | None:
    if not key:
        return default
    v = os.environ.get(key, "").strip()
    return v if v else default


def merge_qwen_provider(full_cfg: dict[str, Any], provider: dict[str, Any]) -> dict[str, Any]:
    """Build Qwen/OpenAI-compatible config dict for llm_expand / slot OpenAI backend."""
    skip = {
        "engine",
        "slot_backend",
        "base_url_env",
        "model_env",
        "api_key_env",
        "fallback",
        "expansion_provider_label",
    }
    merged = {k: v for k, v in full_cfg.items() if k not in ("routing", "ei_scoring")}
    for k, v in provider.items():
        if k in skip:
            continue
        merged[k] = v

    base_url = _env_or(provider.get("base_url_env"), merged.get("base_url") or provider.get("base_url"))
    if base_url:
        merged["base_url"] = base_url.strip()
    model = _env_or(provider.get("model_env"), merged.get("model") or provider.get("model"))
    if model:
        merged["model"] = model.strip()
    api_key = _env_or(provider.get("api_key_env"), merged.get("api_key") or provider.get("api_key"))
    if api_key is not None:
        merged["api_key"] = str(api_key).strip()

    if provider.get("system_prompt"):
        merged["system_prompt"] = str(provider["system_prompt"])

    if ":11434" in (merged.get("base_url") or "") or os.environ.get("OLLAMA_HOST", ""):
        if not merged.get("api_key") or merged["api_key"] == "lm-studio":
            merged["api_key"] = "ollama"
        from pearl_news.pipeline.cjk_qwen_model import PEARL_STAR_CJK_MODEL, is_ollama_openai_base_url

        if is_ollama_openai_base_url(merged.get("base_url")):
            merged["model"] = PEARL_STAR_CJK_MODEL

    merged["enabled"] = full_cfg.get("enabled", True)
    return merged


def _is_cjk_lang(lang: str) -> bool:
    l = (lang or "").strip().lower()
    if l in {"ja", "ko", "zh-cn", "zh-tw", "zh-hk", "zh-sg", "vi", "zh"}:
        return True
    return l.startswith("zh-")


def run_routed_expansion(
    items: list[dict[str, Any]],
    config_root: Path | None = None,
    max_retries: int = 1,
) -> list[dict[str, Any]]:
    """
    Route each item by language to slot_expansion (Claude or OpenAI-compatible) or legacy full-document Qwen.
    """
    pearl_root = Path(__file__).resolve().parent.parent
    repo_root = pearl_root.parent
    config_root = config_root or (pearl_root / "config")
    prompts_root = pearl_root / "prompts"
    full = _load_expansion_yaml(config_root)
    routing = full.get("routing") or {}
    language_map = routing.get("language_map") or {}
    providers = routing.get("providers") or {}
    fallback_cfg = routing.get("fallback") or {}
    max_retries = int(fallback_cfg.get("max_retries") or max_retries)
    use_legacy_cjk = bool(fallback_cfg.get("use_legacy_full_document_cjk"))

    if not language_map or not providers:
        from pearl_news.pipeline.llm_expand import run_expansion

        logger.info("No routing config; using legacy Qwen expansion for all items")
        return run_expansion(items, config_root=config_root, max_retries=max_retries)

    default_key = routing.get("default_provider") or "qwen_slots"
    qwen_slot_prov = providers.get("qwen_slots") or providers.get("qwen") or {}
    qwen_merged = merge_qwen_provider(full, qwen_slot_prov)

    from pearl_news.pipeline.llm_expand import expand_one_item_qwen
    from pearl_news.pipeline.llm_expand_claude import expand_with_claude
    from pearl_news.pipeline.slot_expansion_engine import AnthropicBackend, OpenAICompatibleBackend, expand_item_slots

    for item in items:
        lang = str(item.get("language") or "en").lower()
        provider_key = language_map.get(lang, default_key)
        prov = providers.get(provider_key) or providers.get(default_key) or qwen_slot_prov
        engine = prov.get("engine") or "llm_expand"

        if use_legacy_cjk and _is_cjk_lang(lang):
            legacy_prov = providers.get("qwen_legacy") or qwen_slot_prov
            merged = merge_qwen_provider(full, legacy_prov)
            expand_one_item_qwen(item, config_root, merged, max_retries=max_retries)
            continue

        if engine == "slot_expansion":
            item.pop("_expansion_failed", None)
            backend_type = (prov.get("slot_backend") or "openai_compatible").strip().lower()
            if backend_type == "anthropic":
                backend = AnthropicBackend(prov, config=full)
            else:
                merged = merge_qwen_provider(full, prov)
                backend = OpenAICompatibleBackend(merged)
            expand_item_slots(
                item,
                backend=backend,
                config=full,
                prompts_root=prompts_root,
                repo_root=repo_root,
                language=lang,
                max_retries=max_retries,
                provider_cfg=prov,
            )
            continue

        if engine == "llm_expand_claude":
            item.pop("_expansion_failed", None)
            expand_with_claude(
                [item],
                config_root=config_root,
                provider_cfg=prov,
                max_retries=max_retries,
            )
            if not item.get("_expansion_failed"):
                item["_expansion_provider"] = "claude"
            elif fallback_cfg.get("on_provider_error") == "retry_with_default":
                logger.warning(
                    "Claude expansion failed for %s; falling back to Qwen",
                    item.get("id"),
                )
                item.pop("_expansion_failed", None)
                expand_one_item_qwen(item, config_root, qwen_merged, max_retries=max_retries)
        else:
            merged = merge_qwen_provider(full, prov)
            expand_one_item_qwen(item, config_root, merged, max_retries=max_retries)

    return items
