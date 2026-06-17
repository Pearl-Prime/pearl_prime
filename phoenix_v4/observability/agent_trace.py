"""Agent-trajectory tracing hook (``agent_observability`` subsystem — P0-4 pilot).

Authority: ``docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md`` §4 (the
``agent_observability`` subsystem) + §3.1 (Langfuse self-hosted / Arize Phoenix
drop-in alternate, OpenTelemetry-GenAI ``gen_ai.*`` spans).
Pilot plan: ``docs/observability/AGENT_OBSERVABILITY_PILOT_PLAN.md``.

WHAT THIS IS
------------
A *thin, dependency-optional* instrumentation shim that wraps a pipeline's
LLM / tool calls and emits OpenTelemetry-GenAI spans into a self-hosted trace
store (Langfuse or Arize Phoenix, both speak OTLP). It is the pilot substrate
for agent-trajectory observability — distinct from the existing production-KPI
``observability`` surface (``scripts/observability/``, ``config/observability_*``,
``artifacts/observability/``), which this module does NOT touch (spec §4
anti-reinvention note: different axis, different owner, distinct subsystem id).

WHY IT IS SAFE TO LAND TODAY (no-op by default)
------------------------------------------------
This module has **zero hard third-party imports at module load**. OpenTelemetry
is imported lazily, inside a ``try/except``, and only when tracing is *enabled*.
Tracing is enabled only when the operator sets ``LANGFUSE_*`` (or generic
``OTEL_*``) environment variables AND the ``opentelemetry`` SDK is installed.
When neither is true — which is the state on ``origin/main`` today — every public
entry point degrades to a transparent no-op:

  * ``span(...)``         → a context manager that yields a no-op handle
  * ``traced(...)``       → an identity decorator (returns the function unchanged)
  * ``record_llm_io(...)``→ silently returns
  * ``is_enabled()``      → ``False``

So importing or calling this module from a pipeline can NEVER crash a run and
NEVER adds a runtime dependency. The pilot wrapping in
``phoenix_v4/observability/pilot_example.py`` is written to be imported and run
with tracing OFF (no-op) or ON (emits spans) identically.

TIER-2 / LLM-POLICY COMPLIANCE
------------------------------
This module makes **no LLM call of any kind** — it only records metadata about
calls the pipeline already makes (which, for the book pilot, route to local
Gemma/Qwen via ``phoenix_v4.llm.router``). It therefore carries no paid-LLM-API
surface and passes ``scripts/ci/audit_llm_callers.py`` trivially. Langfuse /
Phoenix are self-hosted infra (Apache-2.0 / self-host), not a SaaS LLM call.

OTel-GenAI SPAN SHAPE (semantic conventions)
--------------------------------------------
Spans follow the OpenTelemetry GenAI semantic conventions so any OTel-native
backend (Langfuse, Phoenix) renders them without custom mapping:

  span name:  ``{gen_ai.operation.name} {gen_ai.request.model}``  e.g. ``chat gemma2:9b``
  attributes:
    gen_ai.system            e.g. "ollama" | "gemma" | "qwen" | "anthropic"
    gen_ai.operation.name    "chat" | "text_completion" | "embeddings"
    gen_ai.request.model     e.g. "gemma2:9b"
    gen_ai.request.max_tokens / .temperature
    gen_ai.response.model
    gen_ai.usage.input_tokens / .output_tokens   (when known)
    # Phoenix-org / pipeline-local context (namespaced to avoid collision):
    phoenix.subsystem        always "agent_observability"
    phoenix.pipeline         e.g. "core_pipeline"
    phoenix.agent            e.g. "Pearl_Writer"
    phoenix.stage            e.g. "thin_section_expansion"

This module is intentionally small and import-free at top level; see the spec
for why we borrow OSS components (Langfuse/OTel) but NOT a Python agent-framework
runtime (spec §6 anti-drift exclusions).
"""
from __future__ import annotations

import contextlib
import logging
import os
from typing import Any, Callable, Dict, Iterator, Mapping, Optional, TypeVar

logger = logging.getLogger(__name__)

__all__ = [
    "is_enabled",
    "span",
    "traced",
    "record_llm_io",
    "tracing_status",
    "SUBSYSTEM",
    "NoOpSpan",
]

# Subsystem id this module belongs to (spec §4). Used as a span attribute so the
# agent-trajectory surface is filterable separately from production-KPI
# observability in the same trace store.
SUBSYSTEM = "agent_observability"

# Env vars that, when present, signal "tracing is configured". Any one is enough.
# LANGFUSE_* is the default backend (spec §3.1); OTEL_EXPORTER_OTLP_ENDPOINT is the
# generic OTLP escape hatch (also covers the Arize Phoenix drop-in alternate).
_ENABLE_ENV_VARS = (
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_SECRET_KEY",
    "LANGFUSE_HOST",
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "PHOENIX_COLLECTOR_ENDPOINT",  # Arize Phoenix self-host collector
)

# Hard kill-switch: set PHOENIX_AGENT_TRACE_DISABLED=1 to force no-op even if the
# enable vars are present (operator escape hatch during incidents).
_DISABLE_ENV_VAR = "PHOENIX_AGENT_TRACE_DISABLED"

_F = TypeVar("_F", bound=Callable[..., Any])

# Lazily-resolved OTel tracer; None until first enabled use, False if unavailable.
_TRACER: Any = None
_TRACER_RESOLVED = False


# ──────────────────────────────────────────────────────────────────────────────
# Enablement
# ──────────────────────────────────────────────────────────────────────────────
def _env_requests_tracing() -> bool:
    """True iff the operator configured a trace backend via env (and not disabled)."""
    if os.environ.get(_DISABLE_ENV_VAR, "").strip() in ("1", "true", "True", "yes"):
        return False
    return any(os.environ.get(name, "").strip() for name in _ENABLE_ENV_VARS)


def _resolve_tracer() -> Any:
    """Lazily build an OTel tracer, or return None if OTel is unavailable.

    Imported lazily so the module has no hard dependency on ``opentelemetry``.
    The exporter/provider wiring itself is intentionally left to the OTel
    environment (standard ``OTEL_*`` env vars) or to whatever process-level
    setup the deploy does — this shim only *acquires a tracer* and emits spans.
    Langfuse's OTLP endpoint and Phoenix's collector are both configured the
    standard OTel way, so we never hard-code a vendor here.
    """
    global _TRACER, _TRACER_RESOLVED
    if _TRACER_RESOLVED:
        return _TRACER
    _TRACER_RESOLVED = True
    try:
        from opentelemetry import trace as _otel_trace  # type: ignore
    except Exception as exc:  # ImportError or any partial-install breakage
        logger.debug("agent_trace: OpenTelemetry not available, staying no-op (%s)", exc)
        _TRACER = None
        return None
    try:
        _TRACER = _otel_trace.get_tracer("phoenix_v4.agent_observability")
    except Exception as exc:  # never let tracer acquisition crash a pipeline
        logger.warning("agent_trace: failed to acquire OTel tracer, no-op (%s)", exc)
        _TRACER = None
    return _TRACER


def is_enabled() -> bool:
    """Return True only when tracing is BOTH configured (env) AND importable (OTel).

    This is the single gate every public entry point checks. When it returns
    False (the default on ``main``), all tracing entry points are no-ops.
    """
    if not _env_requests_tracing():
        return False
    return _resolve_tracer() is not None


def tracing_status() -> Dict[str, Any]:
    """Diagnostic snapshot (safe to call anytime; performs no I/O to the backend)."""
    env_on = _env_requests_tracing()
    otel_ok = False
    if env_on:
        otel_ok = _resolve_tracer() is not None
    return {
        "subsystem": SUBSYSTEM,
        "env_requests_tracing": env_on,
        "otel_available": otel_ok,
        "enabled": env_on and otel_ok,
        "configured_via": [n for n in _ENABLE_ENV_VARS if os.environ.get(n, "").strip()],
        "force_disabled": os.environ.get(_DISABLE_ENV_VAR, "").strip()
        in ("1", "true", "True", "yes"),
    }


# ──────────────────────────────────────────────────────────────────────────────
# No-op span handle (returned when tracing is off)
# ──────────────────────────────────────────────────────────────────────────────
class NoOpSpan:
    """A span handle that accepts every call and does nothing.

    Mirrors the small slice of the OTel span API the pilot uses, so call sites
    are identical whether tracing is on or off.
    """

    __slots__ = ()

    def set_attribute(self, key: str, value: Any) -> None:  # noqa: D401
        return None

    def set_attributes(self, attributes: Mapping[str, Any]) -> None:
        return None

    def record_exception(self, exc: BaseException) -> None:
        return None

    def set_status_error(self, message: str = "") -> None:
        return None

    def add_event(self, name: str, attributes: Optional[Mapping[str, Any]] = None) -> None:
        return None


_NOOP_SPAN = NoOpSpan()


class _OTelSpanWrapper:
    """Thin adapter over a live OTel span exposing the same surface as NoOpSpan.

    Keeps call sites backend-agnostic and shields them from OTel status-code
    imports (looked up lazily, failures swallowed).
    """

    __slots__ = ("_span",)

    def __init__(self, otel_span: Any) -> None:
        self._span = otel_span

    def set_attribute(self, key: str, value: Any) -> None:
        try:
            self._span.set_attribute(key, value)
        except Exception:  # never let telemetry raise into the pipeline
            pass

    def set_attributes(self, attributes: Mapping[str, Any]) -> None:
        for k, v in attributes.items():
            if v is None:
                continue
            self.set_attribute(k, v)

    def record_exception(self, exc: BaseException) -> None:
        try:
            self._span.record_exception(exc)
        except Exception:
            pass

    def set_status_error(self, message: str = "") -> None:
        try:
            from opentelemetry.trace import Status, StatusCode  # type: ignore

            self._span.set_status(Status(StatusCode.ERROR, message))
        except Exception:
            pass

    def add_event(self, name: str, attributes: Optional[Mapping[str, Any]] = None) -> None:
        try:
            self._span.add_event(name, attributes=dict(attributes or {}))
        except Exception:
            pass


# ──────────────────────────────────────────────────────────────────────────────
# Public: span context manager
# ──────────────────────────────────────────────────────────────────────────────
@contextlib.contextmanager
def span(
    name: str,
    *,
    pipeline: Optional[str] = None,
    agent: Optional[str] = None,
    stage: Optional[str] = None,
    attributes: Optional[Mapping[str, Any]] = None,
) -> Iterator[Any]:
    """Open a trace span around a unit of pipeline work.

    No-op (yields a :class:`NoOpSpan`) when tracing is disabled. When enabled,
    starts an OTel span named ``name`` with the standard ``phoenix.*`` context
    attributes set. Exceptions are recorded on the span and re-raised — tracing
    never swallows pipeline errors.

    Example::

        with agent_trace.span("expand_section", pipeline="core_pipeline",
                              agent="Pearl_Writer", stage="thin_expansion") as sp:
            sp.set_attribute("gen_ai.request.model", "gemma2:9b")
            ...
    """
    if not is_enabled():
        yield _NOOP_SPAN
        return

    tracer = _resolve_tracer()
    if tracer is None:  # defensive: is_enabled() already checked, but be safe
        yield _NOOP_SPAN
        return

    base_attrs: Dict[str, Any] = {"phoenix.subsystem": SUBSYSTEM}
    if pipeline:
        base_attrs["phoenix.pipeline"] = pipeline
    if agent:
        base_attrs["phoenix.agent"] = agent
    if stage:
        base_attrs["phoenix.stage"] = stage
    if attributes:
        for k, v in attributes.items():
            if v is not None:
                base_attrs[k] = v

    try:
        cm = tracer.start_as_current_span(name)
    except Exception as exc:  # acquisition failed at call time → degrade to no-op
        logger.debug("agent_trace: start_as_current_span failed, no-op (%s)", exc)
        yield _NOOP_SPAN
        return

    with cm as raw_span:
        wrapper = _OTelSpanWrapper(raw_span)
        wrapper.set_attributes(base_attrs)
        try:
            yield wrapper
        except Exception as exc:
            wrapper.record_exception(exc)
            wrapper.set_status_error(str(exc))
            raise


# ──────────────────────────────────────────────────────────────────────────────
# Public: record GenAI request/response metadata onto the current span
# ──────────────────────────────────────────────────────────────────────────────
def record_llm_io(
    span_handle: Any,
    *,
    system: Optional[str] = None,
    operation: str = "chat",
    request_model: Optional[str] = None,
    response_model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> None:
    """Stamp OTel-GenAI ``gen_ai.*`` attributes onto ``span_handle``.

    Accepts either an :class:`_OTelSpanWrapper`, a :class:`NoOpSpan`, or a raw
    OTel span (anything with ``set_attribute``). Silently returns if the handle
    is falsy. None-valued fields are skipped so the span stays clean.
    """
    if span_handle is None:
        return
    attrs: Dict[str, Any] = {
        "gen_ai.operation.name": operation,
        "gen_ai.system": system,
        "gen_ai.request.model": request_model,
        "gen_ai.request.max_tokens": max_tokens,
        "gen_ai.request.temperature": temperature,
        "gen_ai.response.model": response_model,
        "gen_ai.usage.input_tokens": input_tokens,
        "gen_ai.usage.output_tokens": output_tokens,
    }
    if extra:
        attrs.update(extra)
    setter = getattr(span_handle, "set_attributes", None)
    if callable(setter):
        try:
            setter({k: v for k, v in attrs.items() if v is not None})
            return
        except Exception:
            pass
    # Fall back to single-attribute setting for raw OTel spans.
    single = getattr(span_handle, "set_attribute", None)
    if callable(single):
        for k, v in attrs.items():
            if v is None:
                continue
            try:
                single(k, v)
            except Exception:
                pass


# ──────────────────────────────────────────────────────────────────────────────
# Public: decorator form
# ──────────────────────────────────────────────────────────────────────────────
def traced(
    name: Optional[str] = None,
    *,
    pipeline: Optional[str] = None,
    agent: Optional[str] = None,
    stage: Optional[str] = None,
) -> Callable[[_F], _F]:
    """Decorator that wraps a function call in a :func:`span`.

    Returns the function UNCHANGED when tracing is disabled (true identity
    decorator — zero overhead, zero wrapping) so it is safe to leave on a hot
    path in the default no-op state.

    Example::

        @agent_trace.traced("compose_section", pipeline="core_pipeline",
                            agent="Pearl_Writer", stage="compose")
        def compose_section(...): ...
    """

    def _decorator(func: _F) -> _F:
        # Decide at decoration time only as a fast-path; the per-call check in
        # the wrapper re-confirms so env set *after* import still works.
        import functools

        @functools.wraps(func)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            if not is_enabled():
                return func(*args, **kwargs)
            span_name = name or getattr(func, "__name__", "traced_call")
            with span(span_name, pipeline=pipeline, agent=agent, stage=stage):
                return func(*args, **kwargs)

        return _wrapper  # type: ignore[return-value]

    return _decorator
