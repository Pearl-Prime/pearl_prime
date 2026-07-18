# Agent Observability Langfuse Pilot — artifacts (P0-4, first increment)

**Workstream:** `ws_agent_observability_langfuse_pilot_20260612`
**Spec:** [`docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md`](../../../docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md) (P0-4 🏛)
**Plan:** [`docs/observability/AGENT_OBSERVABILITY_PILOT_PLAN.md`](../../../docs/observability/AGENT_OBSERVABILITY_PILOT_PLAN.md)
**Subsystem:** `agent_observability` (new) · **Owner:** Pearl_DevOps

> **⚠️ DO NOT MERGE — Phase-2 implementation draft for operator review.**
> First increment: substrate + plan only. No self-host infra is deployed by this PR.

---

## What shipped in this increment

| Path | What |
|------|------|
| `docs/observability/AGENT_OBSERVABILITY_PILOT_PLAN.md` | The pilot plan: backend (Langfuse default / Phoenix alternate), the ONE pipeline to instrument (book/`core_pipeline`), the OTel-GenAI span shape, the `agent_observability` ↔ production-KPI `observability` boundary. |
| `phoenix_v4/observability/agent_trace.py` | Dependency-optional tracing hook. No-op when `LANGFUSE_*`/OTLP env unset or OTel absent; emits OTel-GenAI `gen_ai.*` + `phoenix.*` spans when configured. |
| `phoenix_v4/observability/pilot_example.py` | `traced_route_llm` — drop-in span-wrapper around the book pipeline's `phoenix_v4.llm.router.route_llm`, the pilot's first instrumented LLM call. |
| `phoenix_v4/observability/__init__.py` | Package surface for the `agent_observability` subsystem. |
| `artifacts/agent_observability/langfuse_pilot_20260612/SUBSYSTEM_AUTHORITY_MAP_proposed_row.tsv` | The proposed `agent_observability` row for the canonical authority map (follow-up append; NOT applied here). |

## What is deferred (operator follow-ups — see plan §7)

1. Deploy Langfuse (Postgres+ClickHouse) or Phoenix self-host (infra/creds).
2. Install OTel deps on the pilot host; set `LANGFUSE_*` / OTLP env.
3. Two-line wrap into `pearl_writer_expand.py::_call_claude_api` (kept additive here).
4. Append the proposed row to `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` (Pearl_PM; append-only singleton).
5. Token-usage fidelity (small `route_llm` enhancement to return usage).

## Self-verification performed (no infra, no LLM call, no network)

Run in `/tmp/ps/verify_p0_4` against a copy of the modules + a router stub:

- **No-op path (env unset, OTel absent — the default landing state):**
  - `import phoenix_v4.observability.{agent_trace,pilot_example}` succeeds with no third-party deps.
  - `is_enabled() == False`; `tracing_status().enabled == False`, `subsystem == "agent_observability"`.
  - `span(...)` yields a `NoOpSpan`; all span methods crash-free.
  - `record_llm_io(...)` silent no-op (incl. `None` handle).
  - `traced(...)` returns the function unchanged (identity) and still runs it.
  - `traced_route_llm(...)` passes through to the router with identical contract, zero span overhead.
  - Exceptions inside `span(...)` still propagate (tracing never swallows pipeline errors).
- **Enabled path (env set + a fake OTel injected to prove span emission):**
  - `is_enabled() == True`.
  - `span(...)` stamps `phoenix.subsystem/pipeline/agent/stage`; `record_llm_io` stamps `gen_ai.operation.name/system/request.model/request.max_tokens/request.temperature/usage.input_tokens/usage.output_tokens`.
  - `traced_route_llm("…", model_hint="gemma2:9b")` emits one span named `chat gemma2:9b` with `gen_ai.system=gemma`, `phoenix.agent=Pearl_Writer`, response char-len.
  - Exception path records the exception + `ERROR` status, then re-raises.
  - `PHOENIX_AGENT_TRACE_DISABLED=1` kill-switch forces no-op even with env set.
- **`python3 -m py_compile`** passes on all three modules under the repo's Python 3.9.6.
- **LLM-policy:** all three modules match **0** patterns in `config/governance/banned_llm_patterns.yaml` (the only `openai` token is a prose comment, not `from openai import OpenAI`).

## Smoke (safe; no network, no LLM, no infra)

```bash
# from repo root, once the files are on a branch:
python3 -m phoenix_v4.observability.pilot_example
# → prints pilot_self_check() JSON; with env unset, "tracing.enabled": false (no-op proof)
```
