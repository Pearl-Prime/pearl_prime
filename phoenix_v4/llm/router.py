"""Local-first LLM routing — Gemma (English) / Qwen (CJK) on Pearl Star via Ollama."""
from __future__ import annotations

import os


def _detect_language(text: str) -> str:
    if not text.strip():
        return "en"
    cjk_count = sum(
        1
        for c in text
        if ("\u4e00" <= c <= "\u9fff") or ("\u3040" <= c <= "\u30ff") or ("\uac00" <= c <= "\ud7af")
    )
    return "cjk" if cjk_count > len(text) * 0.1 else "en"


def route_llm(
    prompt: str,
    *,
    language: str = "auto",
    model_hint: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    lang: str = _detect_language(prompt) if language == "auto" else str(language)
    if lang == "en":
        base_url = os.environ.get("GEMMA_BASE_URL", "http://192.168.1.101:11434/v1")
        model = model_hint or os.environ.get("GEMMA_MODEL", "gemma2:9b")
    elif lang in ("zh-CN", "zh-TW", "ja", "ko", "zh", "cjk"):
        base_url = os.environ.get("QWEN_BASE_URL", "http://192.168.1.101:11434/v1")
        model = model_hint or os.environ.get("QWEN_MODEL", "qwen2.5:7b")
    else:
        raise ValueError(f"Unsupported language: {lang}")

    from openai import OpenAI

    client = OpenAI(base_url=base_url.rstrip("/"), api_key="ollama", timeout=120.0)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    choice = resp.choices[0].message
    content = getattr(choice, "content", None) or ""
    if not isinstance(content, str):
        raise RuntimeError("Unexpected completion payload from Ollama")
    return content
