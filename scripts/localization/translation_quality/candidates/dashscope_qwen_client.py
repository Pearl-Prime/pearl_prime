#!/usr/bin/env python3
"""DashScope Qwen3.7 Max / Qwen-MT candidate client.

**GATED, NOT YET LIVE.** As of this lane's landing, Lane 00
(docs/agent_prompt_packs/20260721_zh_tw_translation_quality_program/
00_governance_exception_dashscope_scoped.md) -- the scoped
`banned_llm_patterns.yaml` exemption for this exact module path -- has NOT
landed on origin/main. Calling `translate()` below raises
`DashScopeNotYetExemptError` unconditionally until that lands, so this
module can exist and be imported/tested without tripping
`scripts/ci/audit_llm_callers.py` on a phantom live call site.

CALL SHAPE (report for Lane 00 exemption wiring): this module goes through
the EXISTING OpenAI-compatible-mode endpoint already implemented in
`scripts/localization/llm_client.py` (`DASHSCOPE_BASE_URL =
https://dashscope-intl.aliyuncs.com/compatible-mode/v1`, called via the
OpenAI Python SDK's client class + chat-completions method) -- NOT the
native DashScope SDK's synchronous chat classes (the ones the
`dashscope_paid_tier` regex in `banned_llm_patterns.yaml` matches). That
regex will NOT fire against this file at all -- the exemption Lane 00
actually needs is on the `openai_api_cloud` rule (the OpenAI-SDK-client
call site), same mechanism already used for
`scripts/localization/llm_client.py` itself. Lane 00's draft snippet
assumed the native SDK; it should add this file's path to
`openai_api_cloud.exempt_paths` instead (or in addition). (Exact regex
strings intentionally not spelled out literally in this docstring --
spelling them out trips scripts/ci/audit_llm_callers.py on the docstring
text itself, not a real call site; see banned_llm_patterns.yaml directly
for the literal patterns.)

Hard requirements enforced here (not optional, per Lane 01's brief):
  (a) only callable when `PHOENIX_TRANSLATION_ALLOW_CLOUD=1` -- delegated
      entirely to `scripts/localization/llm_client.py`, never
      reimplemented;
  (b) a hard per-run call cap (config value, default 500) with a running
      counter that raises once hit;
  (c) logs an estimated cost per call (token count x published DashScope
      rate) and a running total to
      `artifacts/qa/translation_quality_cost_log_<date>.jsonl`;
  (d) this is the ONE module meant to be the DashScope exempt_paths entry.

Usage:
    python3 scripts/localization/translation_quality/candidates/dashscope_qwen_client.py \\
        --source-locale en-US --target-locale zh-CN --text-file source.txt \\
        --model qwen-mt-plus
"""
from __future__ import annotations

import argparse
import json
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

# Published DashScope per-1K-token rates (USD, international site,
# 2026-07-21 pricing page snapshot) -- update the date comment if DashScope
# repricing is confirmed. Used ONLY for the estimated-cost log, never for
# any accept/reject decision.
DASHSCOPE_RATE_PER_1K_TOKENS_USD: dict[str, float] = {
    "qwen-max": 0.0016,
    "qwen-plus": 0.0004,
    "qwen-mt-plus": 0.0016,
    "qwen-mt-turbo": 0.0004,
}
DEFAULT_MODEL = "qwen-mt-plus"


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


def translate(
    text: str,
    *,
    source_locale: str = "en-US",
    target_locale: str = "zh-CN",
    model: str = DEFAULT_MODEL,
    budget: _CallBudget | None = None,
) -> CandidateResult:
    """Translate via DashScope Qwen3.7 Max / Qwen-MT.

    Raises DashScopeNotYetExemptError until Lane 00 lands (see module
    docstring) -- this is intentional gating, not a bug: it keeps
    scripts/ci/audit_llm_callers.py from ever scanning a live, uncleared
    DashScope call site introduced by this lane.
    """
    if not _governance_exemption_landed():
        raise DashScopeNotYetExemptError(
            "Lane 00 (docs/agent_prompt_packs/20260721_zh_tw_translation_quality_program/"
            "00_governance_exception_dashscope_scoped.md) has not landed the "
            "banned_llm_patterns.yaml exemption for this module yet. This "
            "client is scaffolded and ready (call-cap + cost-log wiring "
            "complete) but the actual API call stays disabled until that "
            "governance exception lands. See this file's module docstring "
            "for the exact exempt_paths entry Lane 00 needs to add."
        )

    budget = budget or _CallBudget()
    budget.check_and_increment()

    # NOTE for whoever picks this up post-Lane-00: the actual call is a
    # thin pass-through to scripts.localization.llm_client.call_llm_with_meta
    # with PHOENIX_TRANSLATION_ALLOW_CLOUD=1 and PHOENIX_TRANSLATION_USE_DASHSCOPE_ONLY=1
    # set, role="draft", model_cfg={"draft_model": {"cloud_model_id": model}}.
    # Left as NotImplementedError (not wired) until the governance check
    # above can return True in a real environment.
    raise NotImplementedError(
        "DashScope call site intentionally not wired until Lane 00 lands "
        "(see module docstring for the exact llm_client.py call this "
        "should become: call_llm_with_meta(..., cfg={'draft_model': "
        "{'cloud_model_id': model}}, role='draft') with "
        "PHOENIX_TRANSLATION_ALLOW_CLOUD=1)."
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
    except (DashScopeNotYetExemptError, NotImplementedError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(result.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
