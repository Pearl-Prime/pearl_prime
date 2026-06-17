"""``agent_observability`` subsystem — agent-trajectory tracing (P0-4 pilot).

Authority: ``docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md`` §4.
Pilot plan:  ``docs/observability/AGENT_OBSERVABILITY_PILOT_PLAN.md``.

This package is the agent-trajectory observability surface (how a Pearl session
reasoned / where it burned tokens / did it loop). It is deliberately DISTINCT
from the production-KPI ``observability`` surface under ``scripts/observability/``,
``config/observability_*`` and ``artifacts/observability/`` (brand/pipeline output
health). See spec §4 for the naming rationale and anti-reinvention boundary.

Everything here is dependency-optional and no-ops by default — importing it can
never add a runtime dependency or crash a pipeline. See ``agent_trace`` docstring.
"""
from __future__ import annotations

from phoenix_v4.observability.agent_trace import (
    SUBSYSTEM,
    NoOpSpan,
    is_enabled,
    record_llm_io,
    span,
    traced,
    tracing_status,
)

__all__ = [
    "SUBSYSTEM",
    "NoOpSpan",
    "is_enabled",
    "record_llm_io",
    "span",
    "traced",
    "tracing_status",
]
