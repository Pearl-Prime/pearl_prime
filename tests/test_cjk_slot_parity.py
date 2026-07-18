"""Routing tests: CJK slot engine vs Claude vs legacy Qwen full-document."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_routing_config(
    tmp_path: Path,
    *,
    use_legacy: bool = False,
) -> Path:
    cfg = {
        "enabled": True,
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:14b",
        "api_key": "ollama",
        "max_tokens": 500,
        "temperature": 0.5,
        "routing": {
            "default_provider": "qwen_slots",
            "language_map": {"ja": "qwen_slots", "en": "claude_slots"},
            "providers": {
                "qwen_slots": {
                    "engine": "slot_expansion",
                    "slot_backend": "openai_compatible",
                    "base_url_env": "QWEN_BASE_URL",
                    "model_env": "QWEN_MODEL",
                    "api_key_env": "QWEN_API_KEY",
                },
                "claude_slots": {
                    "engine": "slot_expansion",
                    "slot_backend": "anthropic",
                    "api_key_env": "ANTHROPIC_API_KEY",
                    "model_env": "CLAUDE_MODEL",
                },
                "qwen_legacy": {"engine": "llm_expand"},
            },
            "fallback": {
                "on_provider_error": "retry_with_default",
                "max_retries": 1,
                "use_legacy_full_document_cjk": use_legacy,
            },
        },
    }
    root = tmp_path / "pearl_news" / "config"
    root.mkdir(parents=True)
    p = root / "llm_expansion.yaml"
    p.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return root


def test_routing_ja_uses_slot_engine(tmp_path: Path) -> None:
    from pearl_news.pipeline.expansion_routing import run_routed_expansion

    config_root = _write_routing_config(tmp_path)
    item = {
        "id": "1",
        "language": "ja",
        "content": "<p>draft</p>",
        "topic": "climate",
        "template_id": "hard_news_spiritual_response",
    }
    with patch("pearl_news.pipeline.slot_expansion_engine.expand_item_slots") as mock_slots:
        run_routed_expansion([item], config_root=config_root)
    mock_slots.assert_called_once()
    kwargs = mock_slots.call_args.kwargs
    assert kwargs.get("language") == "ja"


def test_routing_en_still_uses_anthropic_slot_path(tmp_path: Path) -> None:
    from pearl_news.pipeline.expansion_routing import run_routed_expansion

    config_root = _write_routing_config(tmp_path)
    item = {
        "id": "2",
        "language": "en",
        "content": "<p>draft</p>",
        "topic": "climate",
        "template_id": "hard_news_spiritual_response",
    }
    with patch("pearl_news.pipeline.slot_expansion_engine.expand_item_slots") as mock_slots:
        run_routed_expansion([item], config_root=config_root)
    mock_slots.assert_called_once()
    backend = mock_slots.call_args.kwargs.get("backend")
    assert backend.__class__.__name__ == "AnthropicBackend"


def test_legacy_fallback_flag(tmp_path: Path) -> None:
    from pearl_news.pipeline.expansion_routing import run_routed_expansion

    config_root = _write_routing_config(tmp_path, use_legacy=True)
    item = {
        "id": "3",
        "language": "ja",
        "content": "<p>draft</p>",
        "topic": "climate",
    }
    with patch("pearl_news.pipeline.llm_expand.expand_one_item_qwen") as mock_qwen:
        with patch("pearl_news.pipeline.slot_expansion_engine.expand_item_slots") as mock_slots:
            run_routed_expansion([item], config_root=config_root)
    mock_qwen.assert_called_once()
    mock_slots.assert_not_called()
