#!/usr/bin/env python3
"""
Shared LLM client for localization scripts.

Provider chain (safe-by-default — CLAUDE.md Tier 2):

  0. OLLAMA (Pearl Star / local):          Set OLLAMA_HOST or QWEN_BASE_URL with :11434.
  1. LOCAL (LM Studio):                    Fallback to http://127.0.0.1:1234.
  2. Nonlocal/cloud providers:             ONLY when PHOENIX_TRANSLATION_ALLOW_CLOUD=1
     (DeepSeek → Together → Gemini → Cloudflare → DashScope).

Paid/banned cloud keys in a Keychain-loaded env must NEVER silently win over Ollama.

Environment variables:
  OLLAMA_HOST         — Ollama endpoint (preferred Tier-2 path)
  QWEN_BASE_URL       — If contains :11434, treated as Ollama endpoint
  OLLAMA_MODEL        — Override Ollama model (default: qwen2.5:14b)
  PHOENIX_TRANSLATION_ALLOW_CLOUD — if 1/true/yes: allow nonlocal provider keys
  DEEPSEEK_API_KEY / TOGETHER_API_KEY / GOOGLE_AI_API_KEY / DASHSCOPE_API_KEY /
  CLOUDFLARE_AI_*     — only consulted when ALLOW_CLOUD is set
  PHOENIX_TRANSLATION_USE_DASHSCOPE_ONLY — if 1/true with ALLOW_CLOUD: skip
      DeepSeek+Together+Gemini+Cloudflare, use DashScope

Usage:
  from scripts.localization.llm_client import call_llm, get_client_config

  cfg = load_your_yaml_config()
  response = call_llm(system_prompt, user_prompt, cfg)
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any

logger = logging.getLogger("llm_client")

# ─── CLOUD CONSTANTS ──────────────────────────────────────────────────────────

# DeepSeek (opt-in only — Chinese lab, first-class zh-CN/zh-TW/ja-JP quality).
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_DEFAULT_MODEL = "deepseek-chat"  # DeepSeek V3 — best cost/quality for CJK translation

# Together AI (opt-in only — US-based, no Chinese identity verification).
TOGETHER_BASE_URL = "https://api.together.xyz/v1"
# Model mapping: Together AI model IDs for Qwen equivalents
TOGETHER_MODELS = {
    "draft": "Qwen/Qwen2.5-7B-Instruct-Turbo",      # fast, cheap — equivalent to qwen-turbo
    "judge": "Qwen/Qwen3-235B-A22B-Instruct-2507-tput",  # best quality — equivalent to qwen-max
}

# Google AI Studio — Gemini 2.0 Flash (opt-in only).
# OpenAI-compatible endpoint — works with the openai Python SDK directly.
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_DEFAULT_MODEL = "gemini-2.0-flash"  # free tier: 15 RPM, 1M TPM, 1500 RPD
GEMINI_MAX_TOKENS_CAP = 8192  # Gemini 2.0 Flash max output tokens

# Cloudflare Workers AI — Gemma 3 12B (opt-in only).
# Base URL comes from CLOUDFLARE_AI_BASE_URL env var (accounts/<ID>/ai/v1).
CLOUDFLARE_AI_DEFAULT_MODEL = "@cf/google/gemma-3-12b-it"
CLOUDFLARE_AI_MAX_TOKENS_CAP = 8192

# DashScope (opt-in only — Alibaba Cloud, requires active billing; banned by default policy).
DASHSCOPE_BASE_URL = os.environ.get(
    "DASHSCOPE_BASE_URL",
    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

# Model tier recommendations:
#   qwen-plus   → best cost/quality for batch translation (recommended default)
#   qwen-max    → highest quality, higher cost (use for final eval/judge pass)
#   qwen-turbo  → fastest/cheapest (use for dry-runs / structural validation)
DASHSCOPE_DEFAULT_MODEL = "qwen-plus"

# Modes that route off-box / paid-or-banned cloud surfaces.
NONLOCAL_PROVIDER_MODES = frozenset({
    "deepseek", "together", "gemini", "cloudflare", "cloud",
})


def _is_ollama_endpoint() -> bool:
    """Detect if environment points to an Ollama server."""
    if os.environ.get("OLLAMA_HOST", "").strip():
        return True
    qwen_base = os.environ.get("QWEN_BASE_URL", "").strip()
    return bool(qwen_base and ":11434" in qwen_base)


def _cloud_providers_allowed() -> bool:
    """Explicit opt-in required before any nonlocal/paid provider is selected."""
    return os.environ.get("PHOENIX_TRANSLATION_ALLOW_CLOUD", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _ollama_config(model_cfg: dict[str, Any]) -> dict[str, Any]:
    """Build Ollama (Pearl Star Tier-2) client params."""
    ollama_host = os.environ.get("OLLAMA_HOST", "").strip()
    qwen_base = os.environ.get("QWEN_BASE_URL", "").strip()
    base_url = ollama_host.rstrip("/") + "/v1" if ollama_host else qwen_base
    if not base_url.endswith("/v1"):
        base_url = base_url.rstrip("/") + "/v1"

    ollama_model = (
        os.environ.get("OLLAMA_MODEL", "").strip()
        or model_cfg.get("ollama_model_id", "").strip()
        or "qwen2.5:14b"  # Pearl Star only has qwen2.5:14b
    )

    resolved = {
        "base_url": base_url,
        "api_key": "ollama",
        "model_id": ollama_model,
        "temperature": float(model_cfg.get("temperature", 0.6)),
        "max_tokens": int(model_cfg.get("max_output_tokens", model_cfg.get("max_tokens", 2000))),
        "timeout": float(model_cfg.get("timeout_seconds", model_cfg.get("timeout", 180))),
        "mode": "ollama",
        "enable_thinking": False,
    }
    logger.debug("LLM client: Ollama mode, base_url=%s, model=%s", base_url, ollama_model)
    return resolved


def _local_config(model_cfg: dict[str, Any]) -> dict[str, Any]:
    """Build LM Studio / local OpenAI-compatible client params."""
    resolved = {
        "base_url": model_cfg.get("base_url", "http://127.0.0.1:1234/v1"),
        "api_key": model_cfg.get("api_key", "lm-studio"),
        "model_id": model_cfg.get("model_id", model_cfg.get("model", "local-model")),
        "temperature": float(model_cfg.get("temperature", 0.6)),
        "max_tokens": int(model_cfg.get("max_output_tokens", model_cfg.get("max_tokens", 2000))),
        "timeout": float(model_cfg.get("timeout_seconds", model_cfg.get("timeout", 180))),
        "mode": "local",
        "enable_thinking": False,
    }
    logger.debug(
        "LLM client: local mode, base_url=%s, model=%s",
        resolved["base_url"],
        resolved["model_id"],
    )
    return resolved


# ─── CONFIG RESOLVER ─────────────────────────────────────────────────────────

def get_client_config(cfg: dict[str, Any], role: str = "draft") -> dict[str, Any]:
    """
    Resolve LLM client parameters from config dict + environment.

    Default: Ollama-first (or local LM Studio). Nonlocal/paid providers require
    ``PHOENIX_TRANSLATION_ALLOW_CLOUD=1`` — Keychain-loaded cloud keys alone never win.

    Args:
        cfg:  Loaded YAML config (llm_expansion.yaml or comparator_config.yaml).
        role: "draft" uses draft_model key; "judge" uses judge_model key.

    Returns dict with keys:
        base_url, api_key, model_id, temperature, max_tokens, timeout, mode
    """
    # Pick the right sub-config based on role
    if role == "judge":
        model_cfg = cfg.get("judge_model", cfg.get("draft_model", cfg))
    else:
        model_cfg = cfg.get("draft_model", cfg)

    # ── Tier-2 default: Ollama / local — never silently skip to paid cloud ──
    if _is_ollama_endpoint():
        return _ollama_config(model_cfg)

    allow_cloud = _cloud_providers_allowed()
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    together_key = os.environ.get("TOGETHER_API_KEY", "").strip()
    google_ai_key = os.environ.get("GOOGLE_AI_API_KEY", "").strip()
    dashscope_key = os.environ.get("DASHSCOPE_API_KEY", "").strip()
    cf_ai_base = os.environ.get("CLOUDFLARE_AI_BASE_URL", "").strip()
    cf_ai_token = os.environ.get("CLOUDFLARE_AI_API_TOKEN", "").strip()
    dashscope_only = os.environ.get("PHOENIX_TRANSLATION_USE_DASHSCOPE_ONLY", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )

    if allow_cloud and deepseek_key and not dashscope_only:
        deepseek_model = (
            os.environ.get("DEEPSEEK_MODEL", "").strip()
            or DEEPSEEK_DEFAULT_MODEL
        )
        raw_max = int(model_cfg.get("max_output_tokens", model_cfg.get("max_tokens", 2000)))
        resolved = {
            "base_url": DEEPSEEK_BASE_URL,
            "api_key": deepseek_key,
            "model_id": deepseek_model,
            "temperature": float(model_cfg.get("temperature", 0.6)),
            "max_tokens": min(raw_max, 8192),
            "timeout": float(model_cfg.get("timeout_seconds", model_cfg.get("timeout", 180))),
            "mode": "deepseek",
            "enable_thinking": False,
        }
        logger.debug("LLM client: DeepSeek mode, model=%s, max_tokens=%d", deepseek_model, resolved["max_tokens"])
        return resolved

    if allow_cloud and together_key and not dashscope_only:
        together_model = (
            os.environ.get("TOGETHER_MODEL", "").strip()
            or TOGETHER_MODELS.get(role, TOGETHER_MODELS["draft"])
        )
        raw_max = int(model_cfg.get("max_output_tokens", model_cfg.get("max_tokens", 2000)))
        max_tokens = min(raw_max, 16000)

        resolved = {
            "base_url": TOGETHER_BASE_URL,
            "api_key": together_key,
            "model_id": together_model,
            "temperature": float(model_cfg.get("temperature", 0.6)),
            "max_tokens": max_tokens,
            "timeout": float(model_cfg.get("timeout_seconds", model_cfg.get("timeout", 180))),
            "mode": "together",
            "enable_thinking": False,
        }
        logger.debug("LLM client: Together AI mode, model=%s", together_model)
        return resolved

    if allow_cloud and google_ai_key and not dashscope_only:
        gemini_model = (
            os.environ.get("GEMINI_MODEL", "").strip()
            or GEMINI_DEFAULT_MODEL
        )
        raw_max = int(model_cfg.get("max_output_tokens", model_cfg.get("max_tokens", 2000)))
        resolved = {
            "base_url": GEMINI_BASE_URL,
            "api_key": google_ai_key,
            "model_id": gemini_model,
            "temperature": float(model_cfg.get("temperature", 0.6)),
            "max_tokens": min(raw_max, GEMINI_MAX_TOKENS_CAP),
            "timeout": float(model_cfg.get("timeout_seconds", model_cfg.get("timeout", 180))),
            "mode": "gemini",
            "enable_thinking": False,
        }
        logger.debug("LLM client: Gemini Flash mode, model=%s, max_tokens=%d", gemini_model, resolved["max_tokens"])
        return resolved

    if allow_cloud and cf_ai_base and cf_ai_token and not dashscope_only:
        cf_model = (
            os.environ.get("CLOUDFLARE_AI_MODEL", "").strip()
            or CLOUDFLARE_AI_DEFAULT_MODEL
        )
        raw_max = int(model_cfg.get("max_output_tokens", model_cfg.get("max_tokens", 2000)))
        base_url = cf_ai_base.rstrip("/")
        if not base_url.endswith("/v1"):
            base_url = base_url + "/v1"
        resolved = {
            "base_url": base_url,
            "api_key": cf_ai_token,
            "model_id": cf_model,
            "temperature": float(model_cfg.get("temperature", 0.6)),
            "max_tokens": min(raw_max, CLOUDFLARE_AI_MAX_TOKENS_CAP),
            "timeout": float(model_cfg.get("timeout_seconds", model_cfg.get("timeout", 180))),
            "mode": "cloudflare",
            "enable_thinking": False,
        }
        logger.debug("LLM client: Cloudflare Workers AI mode, model=%s", cf_model)
        return resolved

    if allow_cloud and dashscope_key:
        if role == "judge":
            cloud_model = (
                os.environ.get("DASHSCOPE_JUDGE_MODEL", "").strip()
                or os.environ.get("DASHSCOPE_MODEL", "").strip()
                or model_cfg.get("cloud_judge_model_id", "").strip()
                or model_cfg.get("cloud_model_id", "").strip()
                or DASHSCOPE_DEFAULT_MODEL
            )
        else:
            cloud_model = (
                os.environ.get("DASHSCOPE_MODEL", "").strip()
                or model_cfg.get("cloud_model_id", "").strip()
                or DASHSCOPE_DEFAULT_MODEL
            )

        resolved = {
            "base_url": DASHSCOPE_BASE_URL,
            "api_key": dashscope_key,
            "model_id": cloud_model,
            "temperature": float(model_cfg.get("temperature", 0.6)),
            "max_tokens": int(model_cfg.get("max_output_tokens", model_cfg.get("max_tokens", 2000))),
            "timeout": float(model_cfg.get("timeout_seconds", model_cfg.get("timeout", 180))),
            "mode": "cloud",
            "enable_thinking": False,
        }
        logger.debug("LLM client: DashScope mode, model=%s", cloud_model)
        return resolved

    if not allow_cloud and (
        deepseek_key or together_key or google_ai_key or dashscope_key or (cf_ai_base and cf_ai_token)
    ):
        logger.warning(
            "LLM client: nonlocal API keys present but ignored "
            "(set PHOENIX_TRANSLATION_ALLOW_CLOUD=1 to opt in); using local fallback"
        )

    return _local_config(model_cfg)



# ─── CALL FUNCTION ────────────────────────────────────────────────────────────


def call_llm_with_meta(
    system_prompt: str,
    user_prompt: str,
    cfg: dict[str, Any],
    role: str = "draft",
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> tuple[str, dict[str, Any]]:
    """Returns (assistant text, meta) where meta includes model id, usage, latency."""
    try:
        import openai
    except ImportError:
        raise RuntimeError(
            "openai package required: pip install openai --break-system-packages"
        )

    params = get_client_config(cfg, role=role)
    if temperature is not None:
        params["temperature"] = temperature
    if max_tokens is not None:
        params["max_tokens"] = max_tokens

    client = openai.OpenAI(
        base_url=params["base_url"],
        api_key=params["api_key"],
        timeout=params["timeout"],
    )

    extra_body: dict[str, Any] = {}
    if params["mode"] == "local":
        extra_body["enable_thinking"] = False

    t0 = time.time()
    try:
        response = client.chat.completions.create(
            model=params["model_id"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=params["temperature"],
            max_tokens=params["max_tokens"],
            **({"extra_body": extra_body} if extra_body else {}),
        )
    except Exception as e:
        elapsed = time.time() - t0
        logger.error(
            "LLM call failed after %.1fs [%s mode, model=%s]: %s",
            elapsed, params["mode"], params["model_id"], e,
        )
        raise

    elapsed = time.time() - t0
    logger.info(
        "LLM call OK in %.1fs [%s mode, model=%s]",
        elapsed, params["mode"], params["model_id"],
    )
    text = response.choices[0].message.content or ""
    usage_obj = getattr(response, "usage", None)
    usage: dict[str, int] = {}
    if usage_obj is not None:
        for k in ("prompt_tokens", "completion_tokens", "total_tokens"):
            v = getattr(usage_obj, k, None)
            if v is not None:
                usage[k] = int(v)
    meta: dict[str, Any] = {
        "mode": params["mode"],
        "model_requested": params["model_id"],
        "model_response": getattr(response, "model", None) or "",
        "latency_s": round(elapsed, 3),
        "usage": usage,
    }
    return text, meta


def call_llm(
    system_prompt: str,
    user_prompt: str,
    cfg: dict[str, Any],
    role: str = "draft",
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """
    Call the LLM (DeepSeek / Together AI / DashScope / local).

    Args:
        system_prompt: System message content.
        user_prompt:   User message content.
        cfg:           Raw loaded YAML config dict.
        role:          "draft" or "judge" — selects model tier.
        temperature:   Override temperature (optional).
        max_tokens:    Override max output tokens (optional).

    Returns:
        Model response text.

    Raises:
        RuntimeError:  If openai package not installed.
        Exception:     Re-raises any OpenAI API errors after logging.
    """
    text, _meta = call_llm_with_meta(
        system_prompt,
        user_prompt,
        cfg,
        role=role,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return text


# ─── CONVENIENCE: preflight check ────────────────────────────────────────────

def preflight_check(cfg: dict[str, Any]) -> tuple[bool, str]:
    """
    Quick connectivity check before running a batch job.

    Returns (ok: bool, message: str).
    """
    import urllib.request
    import urllib.error

    params = get_client_config(cfg)
    mode = params["mode"]

    if mode == "deepseek":
        if params["api_key"]:
            return True, f"deepseek mode: DEEPSEEK_API_KEY set, model={params['model_id']}"
        return False, "deepseek mode: DEEPSEEK_API_KEY is empty"

    if mode == "together":
        if params["api_key"]:
            return True, f"together mode: TOGETHER_API_KEY set, model={params['model_id']}"
        return False, "together mode: TOGETHER_API_KEY is empty"

    if mode == "gemini":
        if params["api_key"]:
            return True, f"gemini mode: GOOGLE_AI_API_KEY set, model={params['model_id']}"
        return False, "gemini mode: GOOGLE_AI_API_KEY is empty"

    if mode == "cloudflare":
        if params["api_key"]:
            return True, f"cloudflare mode: CLOUDFLARE_AI_API_TOKEN set, model={params['model_id']}"
        return False, "cloudflare mode: CLOUDFLARE_AI_API_TOKEN is empty"

    if mode == "cloud":
        if params["api_key"]:
            return True, f"cloud mode: DASHSCOPE_API_KEY set, model={params['model_id']}"
        return False, "cloud mode: DASHSCOPE_API_KEY is empty"

    if mode == "ollama":
        base_url = params["base_url"].rstrip("/v1").rstrip("/")
        try:
            req = urllib.request.Request(f"{base_url}/v1/models", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return True, f"ollama mode: reachable at {base_url}, model={params['model_id']}"
                return False, f"ollama mode: HTTP {resp.status} from {base_url}"
        except Exception as e:
            return False, f"ollama mode: unreachable at {base_url} — {e}"

    # Local: ping /v1/models
    base_url = params["base_url"].rstrip("/v1").rstrip("/")
    try:
        req = urllib.request.Request(f"{base_url}/v1/models", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                return True, f"local mode: LM Studio reachable at {base_url}"
            return False, f"local mode: LM Studio returned HTTP {resp.status}"
    except Exception as e:
        return False, f"local mode: LM Studio unreachable at {base_url} — {e}"
