# Agent Observability Pilot Plan (P0-4)

**Workstream:** `ws_agent_observability_langfuse_pilot_20260612` (project `PRJ-AGENT-SYSTEM-IMPROVEMENT-V2`)
**Roadmap item:** P0-4 (🏛) — "Stand up Langfuse (or Phoenix) self-hosted, trace ONE pipeline end-to-end"
**Authority:** [`docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md`](../specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md) §3.1, §4, §5
**Owner:** Pearl_DevOps · **Subsystem:** `agent_observability` (new)
**Status:** first-increment (substrate + plan authored; self-host infra deploy is operator work — see §7)

> **⚠️ DO NOT MERGE — Phase-2 implementation draft for operator review.**
> This plan + its companion hook module land additively and no-op by default; no
> infra is stood up by this PR. The Docker/self-host steps in §3 are the
> operator's deploy runbook, not executed here.

---

## 1. Purpose & the two-observability boundary (read first)

This pilot stands up **agent-trajectory observability** — *how a Pearl session
reasoned, where it burned tokens, whether a pipeline step looped or retried* —
for **one** pipeline end-to-end, to prove the OpenTelemetry substrate before any
repo-wide rollout (P2, out of scope here).

It is a **distinct subsystem** from the production-KPI observability that already
exists on `main`. Per spec §4, conflating the two is explicitly avoided:

| Axis | Subsystem id | Owner | Lives in | Answers |
|------|--------------|-------|----------|---------|
| **Production-KPI observability** (existing) | `observability` (free-text token in coordination state) | control-plane | `scripts/observability/`, `config/observability_*.yaml`, `artifacts/observability/`, `.github/workflows/production-observability.yml`, `PhoenixControl/Views/ObservabilityView.swift` | Are the brands / pipelines healthy in **output** terms? KPI targets, change-impact, operations board. |
| **Agent-trajectory observability** (this pilot) | **`agent_observability`** (new) | **Pearl_DevOps** | `phoenix_v4/observability/`, `docs/observability/`, `artifacts/agent_observability/` | How did the **agent/pipeline run**? LLM/tool spans, token burn, latency, retries, loops. |

**This pilot does NOT touch, supersede, or duplicate the production-KPI surface.**
Where the two eventually share a single OTLP collector, that consolidation is a
future P2 decision (spec §4 anti-reinvention note), not made here.

---

## 2. The ONE pipeline to instrument first

**Pilot pipeline = book / `core_pipeline`** (spec default per open-question
`Q-ASIV2-TRACE-PILOT-01`: densest LLM/tool call graph, most mature). Operator may
redirect to manga; this plan is written so the substrate is pipeline-agnostic and
a manga redirect changes only the wrap site, not the hook.

**Concrete first call site (verified on `origin/main` 2026-06-12):** the
Pearl_Writer thin-section expansion — the book pipeline's single most-instrumentable
LLM call. Its call chain is:

```
scripts/run_pipeline.py  (canonical bestseller CLI; CANONICAL_ARTIFACTS_REGISTRY → pearl_prime_bestseller_cli)
  └─ phoenix_v4/rendering/pearl_writer_expand.py :: expand_section()
       └─ _call_claude_api()
            └─ phoenix_v4/llm/router.py :: route_llm(language="en", ...)   # → Gemma on Pearl Star / Ollama (Tier-2)
```

The router (`phoenix_v4.llm.router`) is the natural choke point: **every** Tier-2
pipeline LLM call flows through `route_llm` / `route_json`, so instrumenting there
(or wrapping it, as the pilot does) gives the whole pipeline's LLM spans from one
seam. The pilot also demonstrates an **agent-session** span boundary around
`expand_section` (the "one agent session" half of the P0-4 scope).

**Why this call, not a deeper one:** it is a single, bounded, already-local
(Gemma/Ollama) call with a clean return contract — ideal to prove span shape +
backend round-trip without re-plumbing the whole 3,772-line CLI.

---

## 3. Self-hosted backend: Langfuse (default) or Arize Phoenix (alternate)

Both are **self-hosted / free / OTLP-native** — no SaaS LLM dependency, fully
Tier-2 compliant (spec §3.1, §6). **This PR installs neither**; this is the
operator deploy runbook. Pick ONE for the pilot.

### 3.1 Langfuse (default)

- Apache-2.0; self-hostable on **Postgres + ClickHouse**; OpenTelemetry-GenAI-native
  (ingests `gen_ai.*` spans directly).
- Self-host (operator, on Pearl Star or a control-plane host), e.g. via the
  official compose:
  ```bash
  # operator host — NOT run by this PR
  git clone https://github.com/langfuse/langfuse
  cd langfuse && docker compose up -d        # brings up Langfuse + Postgres + ClickHouse
  # then create a project, copy its keys
  ```
- Point the pipeline at it via env (the only wiring the code needs):
  ```bash
  export LANGFUSE_HOST="http://<pearl-star-host>:3000"
  export LANGFUSE_PUBLIC_KEY="pk-lf-..."
  export LANGFUSE_SECRET_KEY="sk-lf-..."
  # Langfuse exposes an OTLP endpoint; standard OTEL_* env points the SDK at it:
  export OTEL_EXPORTER_OTLP_ENDPOINT="http://<pearl-star-host>:3000/api/public/otel"
  export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic <base64(pk:sk)>"
  ```

### 3.2 Arize Phoenix (sanctioned drop-in alternate — spec §3.1)

If Langfuse self-host proves operationally heavy, Pearl_DevOps may swap to Phoenix
**without re-ratification** (substrate contract is identical):

```bash
# operator host — NOT run by this PR
pip install arize-phoenix              # local judge / collector, runs on the host
python -m phoenix.server.main serve    # OTLP collector on :6006 by default
export PHOENIX_COLLECTOR_ENDPOINT="http://<host>:6006"
export OTEL_EXPORTER_OTLP_ENDPOINT="http://<host>:6006/v1/traces"
```

The hook module treats `LANGFUSE_*`, `OTEL_EXPORTER_OTLP_ENDPOINT`, and
`PHOENIX_COLLECTOR_ENDPOINT` all as "tracing configured" signals, so either
backend lights it up with no code change.

### 3.3 Python deps (NOT installed by this PR; for the pilot host only)

The hook imports OpenTelemetry **lazily**; install on the pilot host only:

```bash
# pilot host — added to a pilot-only requirements file when the operator deploys, NOT to repo requirements here
pip install "opentelemetry-sdk" "opentelemetry-exporter-otlp" "opentelemetry-api"
# (Langfuse path may instead use the langfuse SDK's OTel bridge; either satisfies the hook.)
```

Until installed, `is_enabled()` returns `False` and everything no-ops — which is
exactly why the hook is safe to land in this PR ahead of the deploy.

---

## 4. OTel-GenAI span shape (the substrate contract)

Spans follow the **OpenTelemetry GenAI semantic conventions** so any OTel-native
backend renders them with zero custom mapping. The hook
(`phoenix_v4/observability/agent_trace.py`) emits exactly this shape:

```
span name:   "{gen_ai.operation.name} {gen_ai.request.model}"     e.g.  "chat gemma2:9b"

# GenAI semantic-convention attributes (backend-portable):
gen_ai.system               "ollama" | "gemma" | "qwen" | "anthropic"
gen_ai.operation.name       "chat" | "text_completion" | "embeddings"
gen_ai.request.model        "gemma2:9b"
gen_ai.request.max_tokens   400
gen_ai.request.temperature  0.4
gen_ai.response.model       "gemma2:9b"
gen_ai.usage.input_tokens   <int when known>
gen_ai.usage.output_tokens  <int when known>

# Phoenix-org context (namespaced "phoenix.*" to avoid colliding with gen_ai.* or
# with the production-KPI surface):
phoenix.subsystem           "agent_observability"   # always — makes agent spans filterable
phoenix.pipeline            "core_pipeline"
phoenix.agent               "Pearl_Writer"
phoenix.stage               "thin_section_expansion"
```

**Span tree for the pilot** (the "one pipeline e2e + one agent session" P0-4 scope):

```
core_pipeline run                      (phoenix.pipeline=core_pipeline)        ── agent-session root
└─ expand_section                      (phoenix.agent=Pearl_Writer, stage=thin_section_expansion)
   └─ chat gemma2:9b                    (gen_ai.* request/response, usage tokens) ── the LLM call span
```

Exceptions are recorded on the span (`record_exception` + `ERROR` status) and
**re-raised** — tracing never swallows a pipeline error.

---

## 5. Instrumentation hook (what lands in this PR)

`phoenix_v4/observability/agent_trace.py` — a thin, **dependency-optional** shim.
Public surface:

| Entry point | Disabled (default) | Enabled (`LANGFUSE_*`/OTLP set + OTel installed) |
|-------------|--------------------|--------------------------------------------------|
| `is_enabled()` | `False` | `True` |
| `span(name, pipeline=, agent=, stage=, attributes=)` | yields a `NoOpSpan` | OTel span with `phoenix.*` context |
| `record_llm_io(span, system=, operation=, request_model=, …)` | silent no-op | stamps `gen_ai.*` attrs |
| `traced(name, …)` (decorator) | **identity** (returns fn unchanged) | wraps call in a span |
| `tracing_status()` | diagnostic dict (no backend I/O) | same |

**Safety contract (why it lands ahead of infra):**
- **No hard third-party import at module load.** `opentelemetry` is imported
  lazily inside `try/except`, only when tracing is enabled.
- **No-op by default.** On `origin/main` today (no `LANGFUSE_*`, no OTel installed),
  every entry point degrades transparently. Importing/calling it cannot crash a
  run and adds no runtime dependency.
- **Kill switch:** `PHOENIX_AGENT_TRACE_DISABLED=1` forces no-op even if env is set.
- **Makes no LLM call itself** — only records metadata about calls the pipeline
  already makes (local Gemma/Qwen for the book pilot). Passes
  `scripts/ci/audit_llm_callers.py` (verified: zero banned-pattern matches).

`phoenix_v4/observability/pilot_example.py` ships `traced_route_llm` — a drop-in
wrapper around `route_llm` showing the exact pilot wrap, runnable on (and behaving
identically across) the no-op and enabled paths.

---

## 6. Pilot acceptance (definition of done for the e2e trace)

The pilot is "ONE pipeline traced end-to-end" when, with a self-hosted backend up
and env set, an operator run of the book pipeline's expansion produces, in the
Langfuse/Phoenix UI:

1. A **session/pipeline-root span** tagged `phoenix.pipeline=core_pipeline`.
2. A nested **`expand_section`** span tagged `phoenix.agent=Pearl_Writer`,
   `phoenix.stage=thin_section_expansion`.
3. A leaf **`chat gemma2:9b`** span carrying `gen_ai.request.model`,
   `gen_ai.request.max_tokens`, `gen_ai.request.temperature`, response char-len,
   and (where the router can surface them) token-usage counts.
4. The same code path run with env **unset** produces **no** spans and **no**
   errors (no-op parity).

Acceptance is recorded in `artifacts/agent_observability/langfuse_pilot_20260612/`.

---

## 7. What this PR does NOT do (operator follow-ups)

This is a **first increment**. Deferred (need infra/creds/operator decision):

1. **Deploy the self-host backend.** Langfuse (Postgres+ClickHouse) or Phoenix
   on Pearl Star / control-plane — operator infra, §3 is the runbook.
2. **Install OTel deps on the pilot host** and set `LANGFUSE_*` / OTLP env.
3. **Wire the wrap into the hot path.** The two-line swap inside
   `phoenix_v4/rendering/pearl_writer_expand.py :: _call_claude_api`
   (`from phoenix_v4.llm.router import route_llm` →
   `from phoenix_v4.observability.pilot_example import traced_route_llm as route_llm`)
   is **intentionally not made here** to keep this PR additive / zero-deletion and
   reviewable in isolation. It is a one-commit follow-up once the backend is up.
4. **Register `agent_observability` in `SUBSYSTEM_AUTHORITY_MAP.tsv`** — proposed
   row authored under
   `artifacts/agent_observability/langfuse_pilot_20260612/SUBSYSTEM_AUTHORITY_MAP_proposed_row.tsv`;
   the operator/Pearl_PM appends it to the canonical map (singleton; append-only —
   never fork the file per CANONICAL_ARTIFACTS_REGISTRY `subsystem_authority_map`).
5. **Token-usage fidelity.** The current router (`route_llm`) returns only the
   completion string; surfacing `gen_ai.usage.*` counts needs a small router
   enhancement (return usage alongside text) — tracked as a follow-up, not on the
   pilot's critical path (spans are still valid without token counts).
6. **Repo-wide rollout + eval emit-into-Langfuse** — P2 / the eval-tooling
   workstream; out of scope for P0-4.

---

## 8. Tier-2 / governance compliance

- **No paid LLM API.** The hook makes no LLM call; the instrumented pipeline call
  routes to **local Gemma/Qwen via Ollama** (`phoenix_v4.llm.router`). Backends
  (Langfuse/Phoenix) are self-hosted infra, not SaaS LLM calls. Verified: the
  authored modules match **zero** patterns in
  `config/governance/banned_llm_patterns.yaml`.
- **Reuse-not-greenfield.** Instruments the **existing** canonical router and
  bestseller CLI; authors no parallel pipeline. New code is confined to the new
  `agent_observability` subsystem dir, which the registry confirms is collision-free.
- **RULE-0.** Additive only — new files; edits to existing pipeline files are
  deferred to the post-deploy follow-up (§7.3).
