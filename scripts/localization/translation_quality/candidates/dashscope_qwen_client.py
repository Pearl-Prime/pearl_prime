#!/usr/bin/env python3
"""DashScope Qwen3.7 Max / Qwen-MT candidate client.

**LIVE as of 2026-07-23.** Lane 00
(docs/agent_prompt_packs/20260721_zh_tw_translation_quality_program/
00_governance_exception_dashscope_scoped.md) -- the scoped
`banned_llm_patterns.yaml` exemption for this exact module path -- has
landed on origin/main (`openai_api_cloud.exempt_paths` contains this
file's path). `_governance_exemption_landed()` below is still a REAL
runtime guard, not a formality: it re-checks the live config file on every
call, so if the exemption is ever reverted this client goes back to
raising `DashScopeNotYetExemptError` automatically, without a code change.

CALL SHAPE: this module talks to the OpenAI-compatible-mode endpoint
directly (`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`,
Singapore international site -- the Beijing/mainland endpoint is a
DIFFERENT, incompatible host and is intentionally never used here), via
the OpenAI Python SDK's client class + chat-completions method -- NOT the
native DashScope SDK's synchronous chat classes (the ones the
`dashscope_paid_tier` regex in `banned_llm_patterns.yaml` matches; that
regex does not fire against this file at all). The exemption lives on
`openai_api_cloud.exempt_paths`, same mechanism already used for
`scripts/localization/llm_client.py` itself.

**Deliberately does NOT go through `scripts.localization.llm_client
.call_llm_with_meta`.** That module's `get_client_config()` checks
`_is_ollama_endpoint()` FIRST, unconditionally, before looking at
`PHOENIX_TRANSLATION_ALLOW_CLOUD` or `PHOENIX_TRANSLATION_USE_DASHSCOPE_ONLY`
at all -- so in any real operator session where Keychain-loaded
`QWEN_BASE_URL` already points at the Pearl Star Ollama endpoint
(`*:11434`), routing through `call_llm_with_meta` would silently and
unconditionally return Ollama's config, never DashScope's, regardless of
any cloud opt-in flag. That is a real trap for this exact use case, so
this client builds its own `openai.OpenAI` instance pointed explicitly at
`DASHSCOPE_BASE_URL` + `DASHSCOPE_API_KEY`, bypassing `get_client_config()`
entirely. `PHOENIX_TRANSLATION_ALLOW_CLOUD=1` is still required (checked
directly below) -- this is an additional explicit opt-in, not a
bypass of it.

Hard requirements enforced here (not optional, per Lane 01's brief):
  (a) only callable when `PHOENIX_TRANSLATION_ALLOW_CLOUD=1` (checked
      directly, not delegated -- see rationale above) AND the Lane 00
      governance exemption is live (re-checked every call);
  (b) refuses to call any DashScope base URL that isn't the Singapore
      international host -- never the Beijing/mainland endpoint;
  (c) a hard per-run call cap (config value, default 500) with a running
      counter that raises once hit -- halts BEFORE the call that would
      exceed the cap, it does not make the call and log the overage;
  (d) logs an estimated cost per call (token count x published DashScope
      rate) and a running total to
      `artifacts/qa/translation_quality_cost_log_<date>.jsonl`;
  (e) this is the ONE module meant to be the DashScope exempt_paths entry.

Usage:
    python3 scripts/localization/translation_quality/candidates/dashscope_qwen_client.py \\
        --source-locale en-US --target-locale zh-CN --text-file source.txt \\
        --model qwen3.7-max
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import ClassVar

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts.localization.translation_quality.candidates import CandidateResult  # noqa: E402

DEFAULT_CALL_CAP = 500
COST_LOG_DIR = REPO_ROOT / "artifacts" / "qa"

# Singapore international site ONLY -- never the Beijing/mainland
# DashScope endpoint (see docs/INTEGRATION_CREDENTIALS_REGISTRY.md and
# CLAUDE.md: "Qwen/DashScope: ...ap-southeast-1... SINGAPORE ONLY. Beijing
# is WRONG."). Two real Singapore-region hosts are known to be in live use
# for this account: the public shared endpoint (dashscope-intl.aliyuncs.com)
# and a Keychain-configured dedicated MaaS gateway
# (*.ap-southeast-1.maas.aliyuncs.com, confirmed live 2026-07-23) -- accept
# either by checking for a Singapore-region marker, not a single hardcoded
# hostname. Reject anything that looks like a mainland region (cn-beijing,
# cn-hangzhou, cn-shanghai, or the bare dashscope.aliyuncs.com host with no
# region/intl marker at all).
DASHSCOPE_INTL_HOST = "dashscope-intl.aliyuncs.com"
DEFAULT_DASHSCOPE_BASE_URL = f"https://{DASHSCOPE_INTL_HOST}/compatible-mode/v1"
_SINGAPORE_MARKERS = ("dashscope-intl.aliyuncs.com", "ap-southeast-1")
_MAINLAND_MARKERS = ("cn-beijing", "cn-hangzhou", "cn-shanghai", "cn-shenzhen")

# Published DashScope per-1K-token rates (USD, international site,
# 2026-07-21 pricing page snapshot) -- update the date comment if DashScope
# repricing is confirmed. Used ONLY for the estimated-cost log, never for
# any accept/reject decision. qwen3.7-max is priced here as an estimate
# pending a confirmed published rate for that exact model id -- treat the
# cost log as directional until corrected.
DASHSCOPE_RATE_PER_1K_TOKENS_USD: dict[str, float] = {
    "qwen3.7-max": 0.0016,  # estimated, mirrors qwen-max pending confirmed pricing
    "qwen-max": 0.0016,
    "qwen-plus": 0.0004,
    "qwen-mt-plus": 0.0016,
    "qwen-mt-turbo": 0.0004,
}
DEFAULT_MODEL = "qwen3.7-max"

DEFAULT_SYSTEM_PROMPT = (
    "You are a professional literary translator. Translate the user's text "
    "from {source_locale} to {target_locale}. Preserve every placeholder "
    "token in {{curly_braces}}, every '## SHAPE vNN' header line and every "
    "frontmatter key/value line exactly as given (never translate them), "
    "every '---' delimiter, every Markdown link, every HTML tag, and every "
    "URL exactly as given. Output ONLY the translation, no commentary, no "
    "surrounding markdown fences."
)


class DashScopeEndpointError(RuntimeError):
    """Raised when the resolved DashScope base URL is not the Singapore
    international host. Never call the Beijing/mainland endpoint from
    here -- see module docstring."""


def _assert_intl_endpoint(base_url: str) -> None:
    low = base_url.lower()
    if any(m in low for m in _MAINLAND_MARKERS):
        raise DashScopeEndpointError(
            f"Refusing to call apparent mainland-China DashScope endpoint {base_url!r} "
            "-- Singapore (ap-southeast-1) only. Check DASHSCOPE_BASE_URL."
        )
    if not any(m in low for m in _SINGAPORE_MARKERS):
        raise DashScopeEndpointError(
            f"Refusing to call DashScope endpoint {base_url!r} -- it matches "
            f"no known Singapore-region marker ({_SINGAPORE_MARKERS}). If this "
            "is a genuine new Singapore endpoint, add its marker to "
            "_SINGAPORE_MARKERS rather than bypassing this check. Check "
            "DASHSCOPE_BASE_URL."
        )


class DashScopeNotYetExemptError(RuntimeError):
    """Raised while Lane 00's banned_llm_patterns.yaml exemption for this
    exact module has not landed on origin/main. See module docstring."""


def _governance_exemption_landed() -> bool:
    """Best-effort live check: has Lane 00 landed?

    Checks for this module's relative path in
    config/governance/banned_llm_patterns.yaml's exempt_paths (either the
    dashscope_paid_tier rule per Lane 00's draft, or openai_api_cloud per
    this module's actual call shape -- see docstring).
    """
    cfg_path = REPO_ROOT / "config" / "governance" / "banned_llm_patterns.yaml"
    if not cfg_path.is_file():
        return False
    rel = "scripts/localization/translation_quality/candidates/dashscope_qwen_client.py"
    try:
        text = cfg_path.read_text(encoding="utf-8")
    except OSError:
        return False
    return rel in text


@dataclass
class _CallBudget:
    """Per-process call cap + cost bookkeeping. Not persisted across runs
    by design -- each script invocation gets a fresh budget; a multi-run
    campaign should pass --call-cap explicitly per run."""

    cap: int = DEFAULT_CALL_CAP
    calls_made: int = 0
    total_estimated_cost_usd: float = 0.0

    _log_path: ClassVar[Path | None] = None

    def check_and_increment(self) -> None:
        if self.calls_made >= self.cap:
            raise RuntimeError(
                f"DashScope call cap ({self.cap}) reached for this run -- "
                "stopping, not just logging. Raise --call-cap explicitly "
                "if this run genuinely needs more (cost-visible decision, "
                "not a silent default)."
            )
        self.calls_made += 1

    def log_call(self, model: str, usage: dict[str, int]) -> float:
        total_tokens = usage.get("total_tokens") or (
            usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)
        )
        rate = DASHSCOPE_RATE_PER_1K_TOKENS_USD.get(model, DASHSCOPE_RATE_PER_1K_TOKENS_USD[DEFAULT_MODEL])
        cost = (total_tokens / 1000.0) * rate
        self.total_estimated_cost_usd += cost

        COST_LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_path = COST_LOG_DIR / f"translation_quality_cost_log_{date.today().isoformat()}.jsonl"
        row = {
            "ts": time.time(),
            "model": model,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(cost, 6),
            "running_total_estimated_cost_usd": round(self.total_estimated_cost_usd, 6),
            "call_number_this_run": self.calls_made,
            "call_cap_this_run": self.cap,
        }
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return cost


def _cloud_allowed() -> bool:
    return os.environ.get("PHOENIX_TRANSLATION_ALLOW_CLOUD", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def translate(
    text: str,
    *,
    source_locale: str = "en-US",
    target_locale: str = "zh-CN",
    model: str = DEFAULT_MODEL,
    budget: _CallBudget | None = None,
    timeout: float = 120.0,
) -> CandidateResult:
    """Translate via DashScope Qwen3.7 Max / Qwen-MT (Singapore intl endpoint).

    Raises DashScopeNotYetExemptError if the Lane 00 governance exemption
    is not (or no longer) present in banned_llm_patterns.yaml -- this is a
    real runtime guard, re-checked on every call, not a one-time gate.
    Raises RuntimeError if PHOENIX_TRANSLATION_ALLOW_CLOUD is not set or
    DASHSCOPE_API_KEY is missing. Raises DashScopeEndpointError if the
    resolved base URL is not the Singapore intl host.
    """
    if not _governance_exemption_landed():
        raise DashScopeNotYetExemptError(
            "Lane 00 (docs/agent_prompt_packs/20260721_zh_tw_translation_quality_program/"
            "00_governance_exception_dashscope_scoped.md) exemption is not "
            "present in config/governance/banned_llm_patterns.yaml right "
            "now -- refusing to call DashScope. This check re-runs on "
            "every call; it is not just a one-time landing gate."
        )

    if not _cloud_allowed():
        raise RuntimeError(
            "PHOENIX_TRANSLATION_ALLOW_CLOUD is not set to 1/true/yes -- "
            "refusing to call a paid cloud API without explicit opt-in. "
            "This is checked directly in this module (not delegated to "
            "scripts.localization.llm_client) -- see module docstring for "
            "why."
        )

    api_key = os.environ.get("DASHSCOPE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "DASHSCOPE_API_KEY is not set. Load it via "
            "scripts/ci/load_integration_env_from_keychain.py before calling."
        )

    base_url = os.environ.get("DASHSCOPE_BASE_URL", "").strip() or DEFAULT_DASHSCOPE_BASE_URL
    _assert_intl_endpoint(base_url)

    budget = budget or _CallBudget()
    budget.check_and_increment()

    try:
        import openai
    except ImportError as exc:
        raise RuntimeError("openai package required: pip install openai --break-system-packages") from exc

    client = openai.OpenAI(base_url=base_url, api_key=api_key, timeout=timeout)
    system_prompt = DEFAULT_SYSTEM_PROMPT.format(source_locale=source_locale, target_locale=target_locale)

    t0 = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.6,
        # Disable Qwen "thinking" mode -- confirmed live 2026-07-23 that
        # leaving this on burns ~500 hidden completion tokens per call
        # (real billed cost, not just latency) with the visible translation
        # output unchanged. Cuts measured completion_tokens from ~529 to
        # ~12-50 for a short item with no quality loss observed in the
        # smoke test. This is a real cost-control fix, not a style choice.
        extra_body={"enable_thinking": False},
    )
    elapsed = time.time() - t0

    out_text = response.choices[0].message.content or ""
    usage_obj = getattr(response, "usage", None)
    usage: dict[str, int] = {}
    if usage_obj is not None:
        for k in ("prompt_tokens", "completion_tokens", "total_tokens"):
            v = getattr(usage_obj, k, None)
            if v is not None:
                usage[k] = int(v)

    cost = budget.log_call(model, usage)

    return CandidateResult(
        candidate_id=f"dashscope_{model}",
        text=out_text,
        meta={
            "mode": "dashscope",
            "base_url": base_url,
            "model_requested": model,
            "model_response": getattr(response, "model", None) or "",
            "source_locale": source_locale,
            "target_locale": target_locale,
            "latency_s": round(elapsed, 3),
            "usage": usage,
            "estimated_cost_usd": round(cost, 6),
            "call_number_this_run": budget.calls_made,
            "call_cap_this_run": budget.cap,
        },
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source-locale", default="en-US")
    ap.add_argument("--target-locale", required=True)
    ap.add_argument("--text-file", type=Path, required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL, choices=sorted(DASHSCOPE_RATE_PER_1K_TOKENS_USD))
    ap.add_argument("--call-cap", type=int, default=DEFAULT_CALL_CAP)
    args = ap.parse_args(argv)

    text = args.text_file.read_text(encoding="utf-8")
    budget = _CallBudget(cap=args.call_cap)
    try:
        result = translate(
            text,
            source_locale=args.source_locale,
            target_locale=args.target_locale,
            model=args.model,
            budget=budget,
        )
    except (DashScopeNotYetExemptError, DashScopeEndpointError, RuntimeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(result.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
