"""Canonical Qwen model for CJK6 + Pearl Star Ollama (:11434).

Keychain or cloud defaults (e.g. qwen-plus) must not be sent to Ollama.
"""
from __future__ import annotations

PEARL_STAR_CJK_MODEL = "qwen2.5:14b"


def is_ollama_openai_base_url(base_url: str | None) -> bool:
    u = (base_url or "").strip().lower()
    return ":11434" in u
