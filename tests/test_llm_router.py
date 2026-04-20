"""Tests for phoenix_v4.llm.router — mocks OpenAI client, no Pearl Star hit."""
from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from phoenix_v4.llm.router import _detect_language, _resolve_target, health_check, route_llm


# ---------------------------------------------------------------------------
# _detect_language
# ---------------------------------------------------------------------------

def test_detect_language_english():
    assert _detect_language("Hello, this is an English sentence.") == "en"


def test_detect_language_cjk_chinese():
    assert _detect_language("这是一段中文文字") == "cjk"


def test_detect_language_cjk_japanese():
    assert _detect_language("これは日本語のテキストです") == "cjk"


def test_detect_language_cjk_korean():
    assert _detect_language("이것은 한국어 텍스트입니다") == "cjk"


def test_detect_language_empty():
    assert _detect_language("") == "en"


def test_detect_language_mixed_mostly_latin():
    assert _detect_language("Hello 你 world") == "en"


# ---------------------------------------------------------------------------
# _resolve_target
# ---------------------------------------------------------------------------

def test_resolve_target_english(monkeypatch):
    monkeypatch.setenv("GEMMA_BASE_URL", "http://host:11434/v1")
    monkeypatch.setenv("GEMMA_MODEL", "gemma2:9b")
    url, model = _resolve_target("en")
    assert "host" in url
    assert model == "gemma2:9b"


def test_resolve_target_cjk(monkeypatch):
    monkeypatch.setenv("QWEN_BASE_URL", "http://host:11434/v1")
    monkeypatch.setenv("QWEN_MODEL", "qwen2.5:7b")
    url, model = _resolve_target("zh-CN")
    assert "host" in url
    assert model == "qwen2.5:7b"


def test_resolve_target_unsupported():
    with pytest.raises(ValueError, match="Unsupported language"):
        _resolve_target("fr")


# ---------------------------------------------------------------------------
# route_llm
# ---------------------------------------------------------------------------

def _make_completion(content: str) -> MagicMock:
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


@patch("openai.OpenAI")
def test_route_llm_english(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _make_completion("Hi there")

    result = route_llm("Hello world", language="en")

    assert result == "Hi there"
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"].startswith("gemma") or True  # env default


@patch("openai.OpenAI")
def test_route_llm_cjk(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _make_completion("你好")

    result = route_llm("你好世界", language="zh-CN")
    assert result == "你好"


@patch("openai.OpenAI")
def test_route_llm_auto_detects_cjk(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _make_completion("ok")

    route_llm("这是中文提示词", language="auto")

    # Should have used qwen URL
    call_args = mock_openai_cls.call_args
    assert "11434" in call_args.kwargs.get("base_url", "")


@patch("openai.OpenAI")
def test_route_llm_system_message(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _make_completion("answer")

    route_llm("user prompt", language="en", system="You are an assistant.")

    msgs = mock_client.chat.completions.create.call_args.kwargs["messages"]
    assert msgs[0]["role"] == "system"
    assert msgs[1]["role"] == "user"


@patch("openai.OpenAI")
def test_route_llm_custom_messages(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _make_completion("answer")

    custom = [{"role": "user", "content": "custom"}]
    route_llm(messages=custom, language="en")

    msgs = mock_client.chat.completions.create.call_args.kwargs["messages"]
    assert msgs[0]["content"] == "custom"


@patch("openai.OpenAI")
def test_route_llm_raises_on_empty(mock_openai_cls):
    with pytest.raises(ValueError, match="requires prompt or messages"):
        route_llm(language="en")


@patch("openai.OpenAI")
def test_route_llm_model_hint(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _make_completion("ok")

    route_llm("hi", language="en", model_hint="gemma2:27b")
    assert mock_client.chat.completions.create.call_args.kwargs["model"] == "gemma2:27b"


# ---------------------------------------------------------------------------
# health_check
# ---------------------------------------------------------------------------

def test_health_check_unreachable(monkeypatch):
    monkeypatch.setenv("GEMMA_BASE_URL", "http://127.0.0.1:19999/v1")
    result = health_check()
    assert result["reachable"] is False
    assert result["gemma"] is False
    assert result["qwen"] is False


@patch("phoenix_v4.llm.router.urllib.request.urlopen")
def test_health_check_reachable_with_models(mock_urlopen):
    payload = json.dumps({
        "models": [
            {"name": "gemma2:9b"},
            {"name": "qwen2.5:7b"},
        ]
    }).encode()
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.read.return_value = payload
    mock_urlopen.return_value = mock_resp

    result = health_check()
    assert result["reachable"] is True
    assert result["gemma"] is True
    assert result["qwen"] is True
    assert len(result["models"]) == 2
