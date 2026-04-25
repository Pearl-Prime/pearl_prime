"""Translator backends for the manga translation pipeline.

LLM Tier Policy compliance:
- ``qwen_ollama`` is the **default** (Tier 2: free, unattended-safe, runs on
  Pearl Star via Ollama; OpenAI-compatible API at $QWEN_BASE_URL).
- ``deepseek`` and ``google_ai`` are **operator-present overrides** for
  ship-quality translations (paid; selected via --backend flag).
- ``mock`` is for tests — deterministic, no network.

Per CLAUDE.md: paid LLM API reads are banned in repo CODE that runs
unattended in CI. These backends:
  - Are invoked only by ``scripts/manga/translate_chapter_script.py``
    which the operator runs (Tier 1) or which Pearl Star runs (Tier 2 Qwen path).
  - Read API keys from env (loaded via the Keychain bridge per CLAUDE.md).
  - Never run inside a GitHub Actions workflow (the audit_llm_callers.py
    scan would block that).

Public API:
    translate(text: str, *, target_locale: str, backend: str = "qwen_ollama",
              **kwargs) -> str
    bulk_translate(texts: list[str], *, target_locale: str, backend: str = ...,
                   **kwargs) -> list[str]
"""
from __future__ import annotations

import os
from typing import Any, Callable

from phoenix_v4.manga.translation.iyashikei_glossary import system_prompt_for


# ─── public errors ────────────────────────────────────────────────────────


class TranslationError(RuntimeError):
    pass


class BackendUnavailableError(TranslationError):
    pass


# ─── backend dispatch ─────────────────────────────────────────────────────


def translate(
    text: str,
    *,
    target_locale: str,
    backend: str = "qwen_ollama",
    timeout_s: int = 30,
    **kwargs: Any,
) -> str:
    """Translate `text` to `target_locale` via the named backend.

    Returns the translated string. Raises TranslationError on failure.

    For ``ko_KR`` placeholder mode (set ``backend="placeholder"``), returns
    ``text`` unchanged with a comment marker — useful when ko_KR connector
    isn't ready (Naver Korean is Phase 2 per PR #631).
    """
    if not text or not text.strip():
        return text

    if backend == "mock":
        return _mock_translate(text, target_locale)
    if backend == "placeholder":
        return text
    if target_locale == "en_US":
        # No-op: the source locale.
        return text

    fn = _BACKENDS.get(backend)
    if fn is None:
        raise BackendUnavailableError(
            f"Unknown backend: {backend}. Valid: {list(_BACKENDS.keys())}"
        )
    return fn(text, target_locale=target_locale, timeout_s=timeout_s, **kwargs)


def bulk_translate(
    texts: list[str],
    *,
    target_locale: str,
    backend: str = "qwen_ollama",
    timeout_s: int = 30,
    **kwargs: Any,
) -> list[str]:
    """Translate a list of strings. No batching across the wire (yet) — most
    backends don't have stable batch endpoints; sequential calls keep the
    contract simple."""
    return [
        translate(t, target_locale=target_locale, backend=backend, timeout_s=timeout_s, **kwargs)
        for t in texts
    ]


# ─── backends ────────────────────────────────────────────────────────────


def _mock_translate(text: str, locale: str) -> str:
    """Deterministic test backend. Wraps text in [LOCALE: ...] to make
    test assertions trivial."""
    return f"[{locale}] {text}"


def _qwen_ollama_translate(
    text: str, *, target_locale: str, timeout_s: int = 30, **_: Any
) -> str:
    """Qwen on Pearl Star via Ollama OpenAI-compatible endpoint.

    Reads QWEN_BASE_URL from env (default: http://192.168.1.101:11434/v1
    per integration_env_registry.py).

    This is the **Tier 2 default** — free, unattended-safe.
    """
    base_url = os.environ.get("QWEN_BASE_URL")
    if not base_url:
        raise BackendUnavailableError(
            "QWEN_BASE_URL not set. Load via: "
            "eval \"$(python3 scripts/ci/load_integration_env_from_keychain.py)\""
        )
    model = os.environ.get("QWEN_MODEL", "qwen2.5:7b")
    api_key = os.environ.get("QWEN_API_KEY", "ollama")  # Ollama ignores; just needs non-empty

    return _openai_compat_call(
        base_url=base_url,
        api_key=api_key,
        model=model,
        text=text,
        target_locale=target_locale,
        timeout_s=timeout_s,
    )


def _deepseek_translate(
    text: str, *, target_locale: str, timeout_s: int = 30, **_: Any
) -> str:
    """DeepSeek deepseek-chat (V3) — paid backend. zh-CN/zh-TW specialty.

    Operator-present override; not invoked by unattended schedulers."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise BackendUnavailableError("DEEPSEEK_API_KEY not set")
    base_url = "https://api.deepseek.com/v1"
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

    return _openai_compat_call(
        base_url=base_url,
        api_key=api_key,
        model=model,
        text=text,
        target_locale=target_locale,
        timeout_s=timeout_s,
    )


def _google_ai_translate(
    text: str, *, target_locale: str, timeout_s: int = 30, **_: Any
) -> str:
    """Google AI Studio Gemini 2.0 Flash — free tier (1M tokens/day).
    ja-JP specialty per integration_env_registry."""
    api_key = os.environ.get("GOOGLE_AI_API_KEY")
    if not api_key:
        raise BackendUnavailableError("GOOGLE_AI_API_KEY not set")

    try:
        import urllib.request
        import urllib.error
        import json
    except ImportError as e:
        raise TranslationError(f"stdlib http unavailable: {e}")

    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt_for(target_locale)}]},
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise TranslationError(
            f"Google AI HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}"
        )
    except Exception as e:
        raise TranslationError(f"Google AI call failed: {e}")

    candidates = body.get("candidates") or []
    if not candidates:
        raise TranslationError(f"Google AI returned no candidates: {body}")
    parts = candidates[0].get("content", {}).get("parts") or []
    out = "".join(p.get("text", "") for p in parts).strip()
    return out or text


def _openai_compat_call(
    *,
    base_url: str,
    api_key: str,
    model: str,
    text: str,
    target_locale: str,
    timeout_s: int,
) -> str:
    """Shared OpenAI-compatible chat-completion helper.

    Used by qwen_ollama (against Pearl Star Ollama) and deepseek (against
    api.deepseek.com/v1). Both honor the same JSON schema.
    """
    import json
    import urllib.error
    import urllib.request

    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt_for(target_locale)},
            {"role": "user", "content": text},
        ],
        "temperature": 0.2,
        "max_tokens": 2048,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise TranslationError(
            f"{base_url} HTTP {e.code}: "
            f"{e.read().decode('utf-8', 'replace')[:200]}"
        )
    except Exception as e:
        raise TranslationError(f"{base_url} call failed: {e}")

    choices = body.get("choices") or []
    if not choices:
        raise TranslationError(f"no choices in response: {body}")
    out = (choices[0].get("message") or {}).get("content", "").strip()
    return out or text


# ─── registry ────────────────────────────────────────────────────────────


_BACKENDS: dict[str, Callable[..., str]] = {
    "qwen_ollama": _qwen_ollama_translate,
    "deepseek": _deepseek_translate,
    "google_ai": _google_ai_translate,
}


def available_backends() -> list[str]:
    return list(_BACKENDS.keys()) + ["mock", "placeholder"]
