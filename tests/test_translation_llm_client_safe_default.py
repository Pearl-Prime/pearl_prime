"""Tests for translation LLM client safe-by-default provider routing."""
from __future__ import annotations

import pytest

from scripts.localization.llm_client import (
    NONLOCAL_PROVIDER_MODES,
    get_client_config,
)


CFG = {"draft_model": {"temperature": 0.2, "max_tokens": 1000}}


@pytest.fixture(autouse=True)
def _clear_provider_env(monkeypatch: pytest.MonkeyPatch):
    for key in (
        "OLLAMA_HOST",
        "QWEN_BASE_URL",
        "OLLAMA_MODEL",
        "PHOENIX_TRANSLATION_ALLOW_CLOUD",
        "PHOENIX_TRANSLATION_USE_DASHSCOPE_ONLY",
        "DEEPSEEK_API_KEY",
        "TOGETHER_API_KEY",
        "GOOGLE_AI_API_KEY",
        "DASHSCOPE_API_KEY",
        "CLOUDFLARE_AI_BASE_URL",
        "CLOUDFLARE_AI_API_TOKEN",
    ):
        monkeypatch.delenv(key, raising=False)


def test_default_ignores_paid_keys_without_opt_in(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-deepseek-test")
    monkeypatch.setenv("TOGETHER_API_KEY", "tg-test")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "ds-test")
    params = get_client_config(CFG)
    assert params["mode"] == "local"
    assert params["mode"] not in NONLOCAL_PROVIDER_MODES


def test_ollama_wins_even_when_paid_keys_present(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-deepseek-test")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "ds-test")
    params = get_client_config(CFG)
    assert params["mode"] == "ollama"
    assert params["base_url"].endswith("/v1")
    assert params["api_key"] == "ollama"


def test_cloud_opt_in_allows_deepseek(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PHOENIX_TRANSLATION_ALLOW_CLOUD", "1")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-deepseek-test")
    params = get_client_config(CFG)
    assert params["mode"] == "deepseek"
    assert params["mode"] in NONLOCAL_PROVIDER_MODES


def test_qwen_base_url_11434_selects_ollama(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("QWEN_BASE_URL", "http://100.92.68.74:11434/v1")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "ds-test")
    params = get_client_config(CFG)
    assert params["mode"] == "ollama"
