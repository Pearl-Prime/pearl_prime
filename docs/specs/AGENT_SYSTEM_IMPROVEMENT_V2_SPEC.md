# Agent-System Improvement V2 Spec

**Cap:** `AGENT-SYSTEM-IMPROVEMENT-V2-01`
**Project:** `PRJ-AGENT-SYSTEM-IMPROVEMENT-V2`
**Status:** ACTIVE (ratified 2026-06-12)
**Owner (spec):** Pearl_Architect
**Phase:** 1 (governance + spec-doc only — this document DESCRIBES the P0 builds; Phase-2 child workstreams BUILD them)
**Extends (does not re-litigate):** `docs/AGENT_SYSTEM_AUDIT_2026_04.md`, `docs/AGENT_SYSTEM_IMPROVEMENT_SPEC.md`
**Source roadmap (reproduced + cited below):** `artifacts/research/agent_systems_audit_20260611/IMPROVEMENT_ROADMAP.md` + `SYSTEMS_TOOLING_OPPORTUNITIES.md` (PR #1507, open do-not-merge research by Pearl_Research, 2026-06-11)

---

## 0. Purpose & standing

This spec **ratifies the P0 tier of the 2026-06-11 agent-systems improvement roadmap as a new root capability**, and locks two default tool choices (tracing + eval) so Phase-2 build workstreams have a settled target.

It stands **independently of PR #1507 merging.** #1507 is open, read-only research flagged do-not-merge; the roadmap content this spec ratifies is **reproduced in full below** so the cap does not gate on that PR landing. (When #1507 does merge, the research artifacts become the durable citation; until then, this spec is the authority for the ratified subset.)

**Scope boundary (Phase 1):** governance, spec-doc, and coordination only. This document describes six P0 build items with owners and sequencing; it ships **no implementation code**. Each build (validator script, tracing install, eval harness, handoff doc, memory cadence, SKILL.md trim) is a Phase-2 child workstream under its named owner agent.

---

## 1. What this extends (anti-re-litigation anchor)

The 2026-04 audit + improvement spec already exist on `main` and remain authoritative for everything they cover. This V2 spec **finishes their unshipped items and adds the observability/eval tooling they predate** — it does not rewrite them:

- `docs/AGENT_SYSTEM_AUDIT_2026_04.md` (275 lines) — the prior system audit. Not edited.
- `docs/AGENT_SYSTEM_IMPROVEMENT_SPEC.md` (170 lines) — outlined `docs/AGENT_HANDOFF_SPEC.md` (§4, "create next", line 94) and named `scripts/ci/check_agent_registry.py` as a future validator (§5, line 106). **Both were designed there and never built.** P0-5 and P0-1 below finish exactly those two outlined-but-unshipped items, which is why they are the highest-certainty, lowest-risk wins.

Verified against `origin/main` 2026-06-12: neither `check_agent_registry.py` nor `AGENT_HANDOFF_SPEC.md` is present; both are still just outlines in the 2026-04 spec.

---

## 2. The six P0 items (reproduced verbatim from IMPROVEMENT_ROADMAP.md)

🏛 = needs a Pearl_Architect spec before implementation (touches governance/coordination or a new subsystem). Items without 🏛 are self-contained enough to implement directly under their owner agent after operator approval.

| # | Item | What | Subsystem / owner | Effort | Expected gain | 🏛 |
|---|------|------|-------------------|--------|---------------|----|
| **P0-1** | **Build `scripts/ci/check_agent_registry.py`** | The validator IMPROVEMENT_SPEC §5 named as "future" and never built: assert every `subsystem_id` in `SUBSYSTEM_AUTHORITY_MAP.tsv` appears in exactly one agent's `subsystems` (or documented shared); assert `skill_path` is null-or-exists. Wire into CI. | github_operations / **Pearl_GitHub** | S | Stops silent registry↔map drift; makes the roster machine-trustworthy | — |
| **P0-2** | **Run `skill-creator` evals on the 4 skills** | Baseline trigger-accuracy + a handful of real-task benchmarks for pearl-github, pearl-int, deep-research, phoenix-isolation-pr. Record scores in the skill dirs. | all skills / authoring agents | S–M | First-ever regression guard for skills; catches mis-triggering | — |
| **P0-3** | **Trim pearl-github SKILL.md headroom** | At 479/500 lines — move one section (e.g. detailed FILES-YOU-OWN table or governance recap) into `references/` so future edits don't blow the budget. | github_operations / **Pearl_GitHub** | S | Keeps gold-standard skill within Agent-Skills budget | — |
| **P0-4** | **Stand up Langfuse (or Phoenix) self-hosted, trace ONE pipeline end-to-end** | Pilot scope: instrument the book or manga pipeline's LLM/tool calls + one agent session. Prove the OTel substrate before repo-wide rollout. | **agent_observability** (new) / **Pearl_DevOps** | M | Closes agent gaps #16/#17 in pilot; unblocks all eval work | 🏛 |
| **P0-5** | **Write `docs/AGENT_HANDOFF_SPEC.md`** | The §4 outline from IMPROVEMENT_SPEC, finally created: one `HANDOFF_TO` owner per commit, artifact-continuity fields (branch/SHA/failing-checks), blocked-state semantics. | repo_coordination / **Pearl_PM** | S | Enforces clean multi-agent handoffs; doc-only, no code risk | 🏛 |
| **P0-6** | **Add a `consolidate-memory` cadence for `MEMORY.md`** | Schedule the existing `consolidate-memory` skill to periodically challenge/merge memory entries — mitigates the documented self-reinforcing-error risk in reflective memory. | repo_coordination / **Pearl_PM** | S | Prevents memory ossifying a wrong lesson | — |

**P0 count: 6** (4 non-🏛: P0-1, P0-2, P0-3, P0-6 · 2 🏛: P0-4, P0-5).

> Note on P0-3 currency: `skills/pearl-github/SKILL.md` is **479 lines on `origin/main`** as of 2026-06-12 (verified) — still 21 lines under the 500-line Agent-Skills budget ceiling, so the trim is a headroom move, not a violation fix.

---

## 3. Ratified default tool choices

The roadmap names alternatives; this spec **locks the defaults** so Phase-2 builds do not re-open the selection. Both choices are self-hosted / free / local-judge and therefore Tier-2 compliant with zero paid-LLM-API dependency (see §6).

### 3.1 Tracing / observability — **Langfuse (self-hosted)**

- **Default:** **Langfuse** — Apache-2.0, self-hostable on Postgres + ClickHouse, OpenTelemetry-GenAI-native (`gen_ai.*` spans). Closes agent-audit gaps #16 (agent-trajectory eval substrate) and #17 (OTel tracing).
- **Sanctioned drop-in alternate:** **Arize Phoenix** — vendor-agnostic, runs locally/Docker, native Claude Agent SDK support. If Langfuse self-host proves operationally heavy in the P0-4 pilot, Pearl_DevOps may swap to Phoenix without re-ratification (both are self-hosted/free/OTel-shaped; the substrate contract is identical).
- **Rationale:** one install gives repo-wide observability and is the substrate every eval tool emits into. Langfuse is the default for its OTel-native span model + self-host maturity; Phoenix is the alternate for its native Agent-SDK hooks. Neither is a SaaS dependency — both run on our own infra.

### 3.2 Evaluation — **DeepEval + agentevals (LOCAL Gemma/Qwen judge)**

- **Default (primary):** **DeepEval** (Apache-2.0, 50+ metrics incl. hallucination/faithfulness, CI/CD-native) **+ `agentevals`** (MIT, ready-made trajectory evaluators). DeepEval covers component/output metrics; agentevals adds plan/tool-path trajectory scoring (agent-audit gap #16). The LLM-as-judge backend is pointed at **local Gemma/Qwen via Ollama** — never a paid API.
- **Domain companions (NOT primary, added per-subsystem where they fit):**
  - **RAGAS** (Apache-2.0) — reference-free, claim-level faithfulness/correctness for the EI/citation cascade (ei_v2, pearl_news). Companion, not the primary harness.
  - **CometKiwi** (reference-free MT quality estimation) — gates localization output without human refs (translation subsystem). Companion.
- **Rationale:** DeepEval+agentevals is the general harness (CI gates + trajectory); RAGAS/CometKiwi are narrow domain instruments layered on top where citation-faithfulness or MT-QE is the thing being measured. All run on a local judge, so all are unattended-safe and Tier-2 compliant.

---

## 4. The `agent_observability` subsystem (naming rationale)

P0-4 introduces a **new subsystem** for agent-trajectory tracing. The roadmap drafted it as "observability (new)"; this spec **registers it as `agent_observability`** instead, deliberately, to avoid a name collision:

- **`observability` is already a used subsystem token on `main`** — it appears as a free-text subsystem in historical coordination state (e.g. workstream `ws_content_inventory_20260407` carries `subsystem = content; observability; portal`), associated with the production-KPI / control-plane observability surface (executive dashboard, change-observation, control-plane runbooks). Reusing the bare token `observability` for agent-trajectory tracing would conflate two distinct concerns: **production-KPI observability** (are the brands/pipelines healthy in output terms) vs **agent-trajectory observability** (how did a Pearl session reason / where did it burn tokens / did it loop).
- **`agent_observability` is free on `main`** — verified 2026-06-12: no file contains the token `agent_observability`. It is collision-free and self-describing.
- **Decision:** the new subsystem is named **`agent_observability`**, owner **Pearl_DevOps**, authority doc = this spec (`docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md`). Its `SUBSYSTEM_AUTHORITY_MAP.tsv` registration is a Phase-2 task carried by the observability-tooling workstream (not done in this Phase-1 spec).

**Anti-reinvention note:** `agent_observability` does NOT duplicate or supersede the existing production-KPI observability surface (control-plane / executive-dashboard). Different axis, different owner, distinct subsystem id. Where the two eventually share infra (e.g. a single Langfuse/OTel collector serving both), that consolidation is a future P2 item, not a Phase-1 decision.

---

## 5. Sequencing

The roadmap's sequencing logic is adopted verbatim and mapped to workstream dispatch gating:

1. **The four non-🏛 P0 items (P0-1, P0-2, P0-3, P0-6) are the first operator-approved batch.** They are self-contained, finish-what-exists, near-zero-risk, and need no new subsystem. → workstream status **runnable** (dispatch immediately under their owners).
2. **The two 🏛 P0 items (P0-4 observability subsystem, P0-5 handoff spec) are ratified by this cap but dispatch-gated on `PEARL_ARCHITECT_STATE.md` cascade-settle** (per the serial-lane discipline for hot-governance-file work). → workstream status **proposed** (ratified, hold for the operator's "cascades settled" signal before dispatch).
3. **P0-4 (observability) is the keystone for all eval work** — it is the substrate every eval item (DeepEval, agentevals, RAGAS later) emits into. The *pilot* (one pipeline e2e) goes first so eval work has somewhere to land; full rollout is deferred to P2 (out of scope here).
4. **P0-2 (skill-creator evals) is runnable now and does not block on P0-4** — skill trigger-accuracy benchmarks are recorded in the skill dirs and do not require the trace store. It belongs to the eval-tooling area but rides the runnable batch.

Within the design-gap-closure area, the non-🏛 parts (P0-1 validator, P0-3 SKILL trim, P0-6 memory cadence) are runnable; the 🏛 part (P0-5 handoff spec) is held with the other 🏛 item.

---

## 6. Tier-2 compliance (CLAUDE.md LLM policy)

Every tool ratified here is **self-hostable / free / local-judge**, with **zero paid-LLM-API dependency in repo code** — fully compliant with the CLAUDE.md Tier policy and `.github/workflows/llm-policy-enforcement.yml`:

- **Tracing:** Langfuse (Apache-2.0, self-host) / Phoenix (self-host) — infra we run, not a SaaS LLM call.
- **Eval judges:** DeepEval / agentevals / RAGAS / CometKiwi all use an **LLM-as-judge pointed at local Gemma/Qwen via Ollama** (Tier-2, unattended-safe). No `ANTHROPIC_API_KEY` / OpenAI / DashScope-cloud / Together / Replicate / etc. in any of the P0 builds.
- **Audit hook:** Phase-2 builds must pass `python3 scripts/ci/audit_llm_callers.py` before push, same as all repo LLM code.

**Explicit anti-drift exclusions (what this spec does NOT adopt):**
- ❌ **No paid LLM API** anywhere (CLAUDE.md ban).
- ❌ **No LangGraph / CrewAI / AutoGen / OpenAI-Agents-SDK as a runtime.** We orchestrate Claude Code sessions over a git repo with coordination TSVs; adopting a Python agent framework would *add* reinvention and violate reuse-first (agent-audit finding #22). We borrow **patterns** (handoff contract, trajectory eval, evaluator-optimizer) and **OSS components** (Langfuse, DeepEval), never a framework runtime.
- ❌ **No rewrite of the 2026-04 audit/spec** — this extends and finishes them (§1).

---

## 7. Phase boundary & child workstreams

This is a **Phase-1 governance/spec deliverable. It contains no implementation code.** The six P0 builds are carried by three Phase-2 workstream lanes (registered in `ACTIVE_WORKSTREAMS.tsv` under project `PRJ-AGENT-SYSTEM-IMPROVEMENT-V2`):

1. **observability-tooling** — Pearl_DevOps, subsystem `agent_observability`. Carries **P0-4** (Langfuse/Phoenix self-host + trace one pipeline e2e). 🏛 → status **proposed** (cascade-settle-gated).
2. **eval-tooling** — carries the DeepEval+agentevals harness stand-up and **P0-2** (skill-creator evals on the 4 skills). P0-2 is runnable now; the broader CI-gate wiring is gated on P0-4's trace substrate → status **proposed** with P0-2 callable in the runnable batch.
3. **design-gap-closures** — carries **P0-1** (`check_agent_registry.py`, Pearl_GitHub), **P0-5** (`AGENT_HANDOFF_SPEC.md`, Pearl_PM, 🏛 doc-only), **P0-6** (consolidate-memory cadence, Pearl_PM), **P0-3** (pearl-github SKILL.md trim, Pearl_GitHub). The non-🏛 parts (P0-1/-3/-6) are **runnable**; the 🏛 part (P0-5) holds with the cascade-gated items.

P1 and P2 roadmap tiers are **out of scope for this cap** — they remain in `IMPROVEMENT_ROADMAP.md` for a future spec.

---

## 8. Open questions (operator-facing, defaults applied)

| ID | Question | Default applied |
|----|----------|-----------------|
| Q-ASIV2-DEVOPS-AGENT-01 | `Pearl_DevOps` is the named owner of the `pearl_devops` subsystem in `SUBSYSTEM_AUTHORITY_MAP.tsv` but is **not** one of the 14 agents in `config/agents/agent_registry.yaml`. P0-4/P0-1 assume Pearl_DevOps as owner. | **Default: keep Pearl_DevOps as owner** (per the subsystem map, which is the routing authority). The registry↔map gap is exactly the drift **P0-1's validator** is built to catch — flag for the operator to either add Pearl_DevOps to the registry or document it as a shared/virtual owner. |
| Q-ASIV2-TRACE-PILOT-01 | Which single pipeline does the P0-4 e2e trace pilot instrument — book or manga? | **Default: book (core_pipeline)** as the e2e pilot (densest LLM/tool call graph, most mature). Operator may redirect to manga. Non-blocking. |
| Q-ASIV2-EVAL-PRIMARY-01 | Confirm DeepEval+agentevals as the **primary** harness with RAGAS/CometKiwi as companions (not co-primary). | **Default: DeepEval+agentevals primary, RAGAS/CometKiwi domain companions** as ratified in §3.2. |
