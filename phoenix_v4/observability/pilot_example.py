"""P0-4 pilot example — instrument the BOOK pipeline's one LLM call end-to-end.

Authority: ``docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md`` (P0-4, default pilot
pipeline = book / ``core_pipeline`` per Q-ASIV2-TRACE-PILOT-01).
Plan: ``docs/observability/AGENT_OBSERVABILITY_PILOT_PLAN.md``.

WHY A SEPARATE EXAMPLE MODULE (not an edit to the pipeline)
-----------------------------------------------------------
The pilot's first increment lands the *substrate* (``agent_trace``) without
touching the canonical bestseller pipeline files (``scripts/run_pipeline.py``,
``phoenix_v4/rendering/pearl_writer_expand.py``, ``phoenix_v4/llm/router.py``).
That keeps this PR additive / zero-deletion and lets the operator review the
instrumentation pattern in isolation before it is woven into the hot path.

This module shows the EXACT wrap the pilot applies to the book pipeline's
single most-instrumentable LLM call — the Pearl_Writer thin-section expansion,
whose call chain on ``origin/main`` is:

    phoenix_v4.rendering.pearl_writer_expand.expand_section()
      └─ _call_claude_api()
           └─ phoenix_v4.llm.router.route_llm(language="en", ...)   # → Gemma/Ollama

``traced_route_llm`` below is a drop-in wrapper around ``route_llm`` that emits
one OTel-GenAI ``chat`` span per call, carrying the ``gen_ai.*`` request shape
plus the ``phoenix.*`` agent/pipeline/stage context. It is:
  * a NO-OP passthrough when tracing is disabled (the default on ``main``), and
  * a span-emitting wrapper when ``LANGFUSE_*`` / OTLP env is configured.

The step-2 (post-pilot) wiring documented in the plan is a two-line change inside
``_call_claude_api`` — swap ``from phoenix_v4.llm.router import route_llm`` for
``from phoenix_v4.observability.pilot_example import traced_route_llm as route_llm``.
That edit is intentionally NOT made in this first increment (see remaining_work).

This module makes no LLM call itself; it only *wraps* the pipeline's existing
local-Gemma/Qwen route, so it adds no paid-LLM-API surface (Tier-2 compliant).
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from phoenix_v4.observability import agent_trace

logger = logging.getLogger(__name__)

PILOT_PIPELINE = "core_pipeline"          # book pipeline (spec default pilot)
PILOT_AGENT = "Pearl_Writer"              # the EN prose-expansion layer
PILOT_STAGE = "thin_section_expansion"    # pearl_writer_expand.expand_section


def _infer_gen_ai_system(model: Optional[str]) -> str:
    """Best-effort ``gen_ai.system`` label from a model id (no network)."""
    m = (model or "").lower()
    if "gemma" in m:
        return "gemma"
    if "qwen" in m:
        return "qwen"
    if "claude" in m:
        return "anthropic"
    # The book pilot routes through Ollama; default to that when unknown.
    return "ollama"


def traced_route_llm(
    prompt: Optional[str] = None,
    *,
    language: str = "auto",
    model_hint: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    pipeline: str = PILOT_PIPELINE,
    agent: str = PILOT_AGENT,
    stage: str = PILOT_STAGE,
    **kwargs: Any,
) -> Any:
    """Span-wrapped drop-in for ``phoenix_v4.llm.router.route_llm``.

    Identical call/return contract to ``route_llm`` (extra ``pipeline``/``agent``/
    ``stage`` kwargs are tracing-only and stripped before the real call). Emits
    one OTel-GenAI ``chat`` span when tracing is enabled; a transparent
    passthrough otherwise.

    The real router is imported lazily so this module stays importable even if
    the (already-present) router or its ``openai`` client dependency is absent.
    """
    from phoenix_v4.llm.router import route_llm  # canonical Tier-2 router (reuse)

    # Fast path: when tracing is off, call straight through with zero overhead.
    if not agent_trace.is_enabled():
        return route_llm(
            prompt,
            language=language,
            model_hint=model_hint,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

    model_for_span = model_hint or "(router-default)"
    span_name = f"chat {model_for_span}"
    with agent_trace.span(
        span_name, pipeline=pipeline, agent=agent, stage=stage
    ) as sp:
        agent_trace.record_llm_io(
            sp,
            system=_infer_gen_ai_system(model_hint),
            operation="chat",
            request_model=model_hint or "(router-default)",
            max_tokens=max_tokens,
            temperature=temperature,
            extra={
                "phoenix.route.language": language,
                "gen_ai.prompt.char_len": len(prompt) if isinstance(prompt, str) else 0,
            },
        )
        result = route_llm(
            prompt,
            language=language,
            model_hint=model_hint,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )
        if isinstance(result, str):
            sp.set_attribute("gen_ai.response.char_len", len(result))
        return result


def pilot_self_check() -> dict:
    """Lightweight wiring check for the pilot (NO LLM CALL, NO network).

    Confirms the trace substrate imports and reports whether tracing is on.
    Intended for ``python -m phoenix_v4.observability.pilot_example`` smoke use
    and for the artifacts README. Never raises on the default (no-op) path.
    """
    status = agent_trace.tracing_status()
    # Exercise the no-op span path to prove it is crash-free regardless of env.
    with agent_trace.span(
        "pilot_self_check", pipeline=PILOT_PIPELINE, agent=PILOT_AGENT, stage="self_check"
    ) as sp:
        agent_trace.record_llm_io(
            sp, system="ollama", operation="chat", request_model="gemma2:9b",
            max_tokens=256, temperature=0.4,
        )
    return {
        "module": "phoenix_v4.observability.pilot_example",
        "pilot_pipeline": PILOT_PIPELINE,
        "pilot_agent": PILOT_AGENT,
        "pilot_stage": PILOT_STAGE,
        "tracing": status,
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke entry
    import json

    print(json.dumps(pilot_self_check(), indent=2, sort_keys=True))
