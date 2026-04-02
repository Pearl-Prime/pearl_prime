#!/usr/bin/env python3
"""
Shared LLM client for localization scripts.

Supports two modes — chosen automatically based on environment:

  CLOUD MODE (priority):
    Set DASHSCOPE_API_KEY environment variable.
    Uses Alibaba Cloud Dashscope OpenAI-compatible endpoint with Qwen models.
    Recommended for GitHub Actions and CI/CD pipelines.

  LOCAL MODE (fallback):
    No DASHSCOPE_API_KEY set.
    Uses LM Studio at http://127.0.0.1:1234 (or config file base_url).
    Recommended for local development.

Environment variables:
  DASHSCOPE_API_KEY   — Dashscope API key (enables cloud mode)
  DASHSCOPE_MODEL     — Override cloud model (default: qwen-plus)
                        Options: qwen-plus, qwen-max, qwen-turbo, qwen-long

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

# Default: China mainland. Override with DASHSCOPE_BASE_URL env var for
# international regions (e.g. Singapore: https://dashscope-intl.aliyuncs.com/compatible-mode/v1).
DASHSCOPE_BASE_URL = os.environ.get(
    "DASHSCOPE_BASE_URL",
    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

# Model tier recommendations:
#   qwen-plus   → best cost/quality for batch translation (recommended default)
#   qwen-max    → highest quality, higher cost (use for final eval/judge pass)
#   qwen-turbo  → fastest/cheapest (use for dry-runs / structural validation)
DASHSCOPE_DEFAULT_MODEL = "qwen-plus"


# ─── CONFIG RESOLVER ─────────────────────────────────────────────────────────

def get_client_config(cfg: dict[str, Any], role: str = "draft") -> dict[str, Any]:
    """
    Resolve LLM client parameters from config dict + environment.

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

    api_key_env = os.environ.get("DASHSCOPE_API_KEY", "").strip()

    if api_key_env:
        # ── CLOUD MODE ────────────────────────────────────────────────────────
        cloud_model = (
            os.environ.get("DASHSCOPE_MODEL", "").strip()
            or model_cfg.get("cloud_model_id", "").strip()
            or DASHSCOPE_DEFAULT_MODEL
        )
        # Judge role: prefer higher quality model in cloud mode
        if role == "judge" and not os.environ.get("DASHSCOPE_MODEL"):
            cloud_model = model_cfg.get("cloud_judge_model_id", cloud_model)

        resolved = {
            "base_url": DASHSCOPE_BASE_URL,
            "api_key": api_key_env,
            "model_id": cloud_model,
            "temperature": float(model_cfg.get("temperature", 0.6)),
            "max_tokens": int(model_cfg.get("max_output_tokens", model_cfg.get("max_tokens", 2000))),
            "timeout": float(model_cfg.get("timeout_seconds", model_cfg.get("timeout", 180))),
            "mode": "cloud",
            # Dashscope does not use enable_thinking param for qwen-plus/max base models
            "enable_thinking": False,
        }
        logger.debug("LLM client: cloud mode, model=%s", cloud_model)

    else:
        # ── LOCAL MODE (LM Studio) ────────────────────────────────────────────
        resolved = {
            "base_url": model_cfg.get("base_url", "http://127.0.0.1:1234/v1"),
            "api_key": model_cfg.get("api_key", "lm-studio"),
            "model_id": model_cfg.get("model_id", model_cfg.get("model", "local-model")),
            "temperature": float(model_cfg.get("temperature", 0.6)),
            "max_tokens": int(model_cfg.get("max_output_tokens", model_cfg.get("max_tokens", 2000))),
            "timeout": float(model_cfg.get("timeout_seconds", model_cfg.get("timeout", 180))),
            "mode": "local",
            # LM Studio / local Qwen: disable thinking mode for speed
            "enable_thinking": False,
        }
        logger.debug("LLM client: local mode, base_url=%s, model=%s",
                     resolved["base_url"], resolved["model_id"])

    return resolved


# ─── CALL FUNCTION ────────────────────────────────────────────────────────────

def call_llm(
    system_prompt: str,
    user_prompt: str,
    cfg: dict[str, Any],
    role: str = "draft",
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """
    Call the LLM (cloud Qwen via Dashscope or local Qwen via LM Studio).

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

    # Build extra body — only pass enable_thinking for local Qwen builds that support it
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
    return response.choices[0].message.content or ""


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

    if mode == "cloud":
        # For Dashscope, just verify the API key is non-empty
        if params["api_key"]:
            return True, f"cloud mode: DASHSCOPE_API_KEY set, model={params['model_id']}"
        return False, "cloud mode: DASHSCOPE_API_KEY is empty"

    else:
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
