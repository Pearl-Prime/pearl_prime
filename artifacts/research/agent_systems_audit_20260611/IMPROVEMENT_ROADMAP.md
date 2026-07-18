# Improvement Roadmap — Agents · Skills · Systems Tooling

**Date:** 2026-06-11
**Agent:** Pearl_Research
**Inputs:** `AGENTS_BEST_PRACTICE_AUDIT.md` (6 agent gaps), `SKILLS_BEST_PRACTICE_AUDIT.md` (5 skill gaps), `SYSTEMS_TOOLING_OPPORTUNITIES.md` (per-subsystem OSS picks).
**Principle:** Build on what exists. Several items here simply **finish work the 2026-04 IMPROVEMENT_SPEC designed but never shipped** — those are the cheapest, highest-certainty wins. Everything respects the Tier policy (local judges / self-hosted only in repo code).

**Effort:** S ≤1 day · M a few days · L multi-week.
**🏛 = needs a Pearl_Architect spec before implementation** (touches governance/coordination or multi-subsystem). Items without 🏛 are self-contained enough to implement directly under their owner agent after operator approval.

---

## P0 — quick wins (high certainty, ≤ a few days each, finish-what-exists first)

| # | Item | What | Subsystem / owner | Effort | Expected gain | 🏛 |
|---|------|------|-------------------|--------|---------------|----|
| P0-1 | **Build `scripts/ci/check_agent_registry.py`** | The validator IMPROVEMENT_SPEC §5 named as "future" and never built: assert every `subsystem_id` in `SUBSYSTEM_AUTHORITY_MAP.tsv` appears in exactly one agent's `subsystems` (or documented shared); assert `skill_path` is null-or-exists. Wire into CI. | github_operations / Pearl_GitHub | S | Stops silent registry↔map drift; makes the roster machine-trustworthy | — |
| P0-2 | **Run `skill-creator` evals on the 4 skills** | Baseline trigger-accuracy + a handful of real-task benchmarks for pearl-github, pearl-int, deep-research, phoenix-isolation-pr. Record scores in the skill dirs. | all skills / authoring agents | S–M | First-ever regression guard for skills; catches mis-triggering | — |
| P0-3 | **Trim pearl-github SKILL.md headroom** | At 479/500 lines — move one section (e.g. detailed FILES-YOU-OWN table or governance recap) into `references/` so future edits don't blow the budget. | github_operations / Pearl_GitHub | S | Keeps gold-standard skill within Agent-Skills budget | — |
| P0-4 | **Stand up Langfuse (or Phoenix) self-hosted, trace ONE pipeline end-to-end** | Pilot scope: instrument the book or manga pipeline's LLM/tool calls + one agent session. Prove the OTel substrate before repo-wide rollout. | observability (new) / Pearl_DevOps | M | Closes agent gaps #16/#17 in pilot; unblocks all eval work | 🏛 |
| P0-5 | **Write `docs/AGENT_HANDOFF_SPEC.md`** | The §4 outline from IMPROVEMENT_SPEC, finally created: one `HANDOFF_TO` owner per commit, artifact-continuity fields (branch/SHA/failing-checks), blocked-state semantics. | repo_coordination / Pearl_PM | S | Enforces clean multi-agent handoffs; doc-only, no code risk | 🏛 |
| P0-6 | **Add a `consolidate-memory` cadence for `MEMORY.md`** | Schedule the existing `consolidate-memory` skill to periodically challenge/merge memory entries — mitigates the documented self-reinforcing-error risk in reflective memory. | repo_coordination / Pearl_PM | S | Prevents memory ossifying a wrong lesson | — |

**P0 count: 6.**

---

## P1 — high value, larger scope

| # | Item | What | Subsystem / owner | Effort | Expected gain | 🏛 |
|---|------|------|-------------------|--------|---------------|----|
| P1-1 | **Author `skills/pearl-prime/SKILL.md` + `skills/pearl-dev/SKILL.md`** | Convert `PEARL_*_ITE_PROMPT.md` into progressive-disclosure skills (the long-deferred 2026-04 §2.2 P0). | core_pipeline, manga_pipeline | M each | 10/14 agents currently skill-less; these two are highest spec-density | 🏛 |
| P1-2 | **DeepEval + RAGAS quality gates in CI** | Local-judge faithfulness/hallucination/coherence gates for ei_v2 + core_pipeline + pearl_news. Emit into Langfuse (P0-4). | ei_v2, core_pipeline, pearl_news | M | Quality becomes measured/gated, not manual-read | 🏛 |
| P1-3 | **Evaluator-optimizer content loop** | Wire existing quality gates as generator→critic→regenerate so a chapter/panel auto-revises until pass. | core_pipeline / Pearl_Prime | L | Higher first-pass quality; less human rework | 🏛 |
| P1-4 | **CometKiwi reference-free MT gate** | Add QE scoring to localization quality_contracts so locales gate without human refs. | translation / Pearl_Localization | M | Scales localization QA across 12+ locales | — |
| P1-5 | **Kokoro/F5-TTS draft+fallback tier** | Local TTS for proofs before ElevenLabs spend + cloning fallback on quota. | audiobook_pipeline / Pearl_Dev | M | Cuts vendor cost; removes single-vendor risk | — |
| P1-6 | **agentevals trajectory scoring on research + dispatch** | Score whether agent sessions took sensible plan/tool paths (not just output quality). | ei_v2 / Pearl_Research | M | Closes agent gap #16 properly | 🏛 |
| P1-7 | **`scripts/` helper for phoenix-isolation-pr** | Turn the deterministic worktree→sparse→safety-gate→commit prose into a script the SKILL calls (also encodes the worktree-poison guard). | github_operations / Pearl_GitHub | M | Less drift, faster fan-out, fewer poison incidents | — |

**P1 count: 7.**

---

## P2 — strategic / nice-to-have

| # | Item | What | Subsystem / owner | Effort | Expected gain | 🏛 |
|---|------|------|-------------------|--------|---------------|----|
| P2-1 | **Auto-dispatch suggester** | `code_globs` field in registry + `git diff --name-only` → suggested owner agent (IMPROVEMENT_SPEC §7 P2). | repo_coordination / Pearl_PM | M | Fewer routing errors at task start | 🏛 |
| P2-2 | **Per-skill `CHANGELOG.md` + `version` frontmatter** | Skill versioning so changes are auditable/rollback-able. | all skills | S | Skill maintenance hygiene | — |
| P2-3 | **Repo-wide observability rollout** | Extend P0-4 pilot to all pipelines + all agent sessions. | observability / Pearl_DevOps | L | Full-system visibility | 🏛 |
| P2-4 | **Music-mode standardize on ACE-Step/YuE (Apache-2.0)** | Local-model music posture (litigation-safe + Tier-aligned). | music_mode / Pearl_Editor | M | Risk-correct, cost-free music generation | — |
| P2-5 | **Two-Claude skill-refinement loop as standing practice** | Adopt observe-B → feed-A loop whenever a skill mis-triggers in evals. | all skills | ongoing | Continuously improving skills | — |
| P2-6 | **InstantID/EcomID as angle-robust manga face alternate** | Add to manga face-lock toolbox where PuLID drops likeness on non-frontal panels. | manga_pipeline / Pearl_Dev | M | Better face consistency on hard angles | — |

**P2 count: 6.**

---

## Sequencing logic (why this order)

1. **P0-4 (observability) is the keystone.** It's the substrate every eval item (P1-2, P1-6, RAGAS/DeepEval) emits into. Do the *pilot* first so eval work has somewhere to land — but it's 🏛 (new subsystem), so it needs an Architect spec.
2. **The un-🏛 P0 items (P0-1, P0-2, P0-3, P0-6) can start immediately** under their owners — they're self-contained, finish-what-exists, near-zero-risk. Recommend these as the first operator-approved batch.
3. **P1 is gated on P0:** skills (P1-1) want the eval harness (P0-2) to verify they trigger; quality gates (P1-2) want observability (P0-4) to emit into.
4. **Nothing here adopts a heavyweight agent framework** — that would violate reuse-first (agent audit #22). We borrow *patterns* (handoff contract, evaluator-optimizer, trajectory eval) and *OSS components* (Langfuse, DeepEval, Kokoro), not runtimes.

---

## Items that need a Pearl_Architect spec (🏛 summary)

P0-4 (observability subsystem), P0-5 (handoff spec — doc), P1-1 (new skills under cascade governance), P1-2 (CI quality gates), P1-3 (evaluator-optimizer loop), P1-6 (trajectory eval), P2-1 (auto-dispatch), P2-3 (obs rollout).

Per `MEMORY.md` anti-reinvention note, **Architect-gated items must wait for `PEARL_ARCHITECT_STATE.md` cascade-settle** before dispatch, and any new-file work should ride the parallel lane while append-to-hot-governance-file work stays serial.

---

## What we are NOT recommending (and why)

- ❌ Any paid LLM API in repo code (CLAUDE.md ban). All eval judges = Gemma/Qwen local.
- ❌ Adopting LangGraph/CrewAI/AutoGen as our runtime — we orchestrate Claude Code over git; a framework adds reinvention.
- ❌ Rewriting the 2026-04 audit — this roadmap *extends* it and finishes its unshipped items.
