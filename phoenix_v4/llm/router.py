"""Central LLM router for TIER 2 (unattended) LLM calls.

Routes scheduled / pipeline LLM work to local Ollama on Pearl Star:
  English → Gemma (gemma2:9b)
  CJK6    → Qwen (qwen2.5:7b)

For TIER 1 work (operator-present refactors, prose, analysis), use Claude Code
directly — do NOT import this router from ad-hoc scripts that a human runs.
This router exists so 3am crons don't need an open Claude Code session.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Iterable, Mapping, Any

_CJK_RANGES = (
    (0x4E00, 0x9FFF), (0x3040, 0x309F), (0x30A0, 0x30FF),
    (0xAC00, 0xD7AF), (0x3400, 0x4DBF),
)


def _detect_language(text: str) -> str:
    if not text.strip():
        return "en"
    cjk = sum(1 for ch in text for lo, hi in _CJK_RANGES if lo <= ord(ch) <= hi)
    return "cjk" if cjk > max(1, len(text) * 0.08) else "en"


def _resolve_target(language: str) -> tuple[str, str]:
    if language in ("en",):
        return (
            os.environ.get("GEMMA_BASE_URL", "http://192.168.1.101:11434/v1"),
            os.environ.get("GEMMA_MODEL", "gemma2:9b"),
        )
    if language in ("zh-CN", "zh-TW", "ja", "ko", "zh", "cjk",
                    "zh-HK", "zh-SG"):
        return (
            os.environ.get("QWEN_BASE_URL", "http://192.168.1.101:11434/v1"),
            os.environ.get("QWEN_MODEL", "qwen2.5:7b"),
        )
    raise ValueError(f"Unsupported language: {language!r}")


def route_llm(
    prompt: str | None = None,
    *,
    language: str = "auto",
    system: str | None = None,
    messages: list[Mapping[str, Any]] | None = None,
    model_hint: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    stream: bool = False,
) -> str | Iterable[str]:
    """Route a prompt to Gemma (EN) or Qwen (CJK) on Pearl Star via Ollama."""
    if language == "auto":
        probe = prompt or "".join(str(m.get("content", "")) for m in (messages or []))
        language = "en" if _detect_language(probe) == "en" else "zh-CN"

    base_url, default_model = _resolve_target(language)
    model = model_hint or default_model

    try:
        from openai import OpenAI
    except ImportError as e:
        raise ImportError(
            "phoenix_v4.llm.router requires the `openai` package (as Ollama client)."
        ) from e

    client = OpenAI(base_url=base_url.rstrip("/"), api_key="ollama", timeout=120.0)

    msgs: list[dict[str, Any]]
    if messages:
        msgs = [dict(m) for m in messages]
    else:
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": prompt or ""})

    if not msgs or not any(m.get("content") for m in msgs):
        raise ValueError("route_llm requires prompt or messages")

    try:
        if stream:
            r = client.chat.completions.create(
                model=model, messages=msgs,
                max_tokens=max_tokens, temperature=temperature, stream=True,
            )
            return (
                c.choices[0].delta.content
                for c in r
                if c.choices[0].delta.content
            )
        r = client.chat.completions.create(
            model=model, messages=msgs,
            max_tokens=max_tokens, temperature=temperature,
        )
        content = r.choices[0].message.content or ""
        if not isinstance(content, str):
            raise RuntimeError("Unexpected completion payload from Ollama")
        return content
    except Exception as e:
        raise RuntimeError(
            f"LLM route failed (lang={language}, model={model}): {e}"
        ) from e


def route_json(
    prompt: str,
    schema: dict,
    *,
    language: str = "auto",
    max_tokens: int = 2048,
    temperature: float = 0.2,
    max_retries: int = 3,
) -> dict:
    """Route a prompt expecting a JSON response validated against schema."""
    try:
        import jsonschema
    except ImportError as e:
        raise ImportError("route_json requires the `jsonschema` package.") from e

    full_prompt = f"{prompt}\n\nJSON only, matching schema:\n{json.dumps(schema)}"
    last: Exception | None = None
    for _ in range(max_retries):
        raw = route_llm(
            prompt=full_prompt, language=language,
            max_tokens=max_tokens, temperature=temperature,
        )
        cleaned = re.sub(
            r"^```(?:json)?\s*|\s*```$", "", (raw or "").strip(), flags=re.M
        )
        try:
            data = json.loads(cleaned)
            jsonschema.validate(data, schema)
            return data
        except Exception as e:
            last = e
    raise RuntimeError(f"route_json failed after {max_retries} tries: {last}")


def health_check() -> dict:
    """Return reachability and model availability for Pearl Star Ollama."""
    base = os.environ.get("GEMMA_BASE_URL", "http://192.168.1.101:11434/v1")
    tags_url = base.rsplit("/v1", 1)[0] + "/api/tags"
    out: dict[str, Any] = {
        "reachable": False, "gemma": False, "qwen": False, "models": [],
    }
    try:
        with urllib.request.urlopen(tags_url, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        models = [m.get("name", "") for m in data.get("models", [])]
        out.update(
            reachable=True,
            models=models,
            gemma=any("gemma" in m.lower() for m in models),
            qwen=any("qwen" in m.lower() for m in models),
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        pass
    return out
