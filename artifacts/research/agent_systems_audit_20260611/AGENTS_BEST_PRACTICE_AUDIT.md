# Agents — Best-Practice Audit (2025–2026 SOTA vs the Pearl System)

**Date:** 2026-06-11
**Agent:** Pearl_Research (background subagent)
**Scope:** Verify whether our organizational Pearl agent system (14 agents + router + cascade discipline) uses current best practices in agent design. SOTA inventory → per-finding map against our system.
**Relation to prior work:** This **extends** `docs/AGENT_SYSTEM_AUDIT_2026_04.md` (which was an *organizational necessity* audit — keep/merge/skill-ify each agent) and `docs/AGENT_SYSTEM_IMPROVEMENT_SPEC.md` (registry + dispatch protocol). Neither prior doc compared our system against external agent-engineering SOTA. **That comparison is this document's job.** Nothing here re-litigates the merge verdicts.

**Method note:** All claims trace to cited URLs with access dates (see end). Where a primary Anthropic engineering post defines a named technique, that technique is the scoring rubric. Uncertain items are marked `[verify]`. No fabricated benchmarks.

**Scoring legend:**
- ✅ **DOING** — we already implement this, with repo evidence.
- 🟡 **PARTIAL** — present in spirit/ad hoc but not formalized or not consistently applied.
- ❌ **GAP** — not present; actionable.
- ⚪ **N/A** — does not apply to our Tier-policy / scope.

---

## 0. Executive summary

Our Pearl system is **unusually strong on the parts of agent design that the field has only recently formalized** — specifically: orchestrator-worker fan-out, isolated worker contexts, separate verification passes, externalized state/memory, and a "find the smallest set of high-signal tokens" discipline. Much of this we arrived at empirically (the worktree-poison, serial-lane, and disk-constraint lessons in `MEMORY.md` are textbook context-engineering and cost-control findings).

Where we lag is **not architecture but instrumentation and self-improvement loops**: we have no agent-trajectory evaluation, no structured observability/tracing, no eval harness for our skills/agents, and our reflective memory (`MEMORY.md`) carries the known self-reinforcing-error risk that the literature warns about (we partially mitigate it with the "git-first drift recovery" rule, which is itself a good pattern).

**Headline counts:** 9 SOTA patterns scored ✅ DOING, 7 🟡 PARTIAL, **6 ❌ GAP**, 2 ⚪ N/A. The 6 gaps are the roadmap spine (see `IMPROVEMENT_ROADMAP.md`).

---

## 1. SOTA inventory — what the field looks like now (2025–2026)

### 1.1 Anthropic's canonical guidance (the rubric we score against)

Anthropic has published a coherent four-part doctrine that is now the de-facto reference for production agents:

1. **"Building Effective Agents"** (Dec 2024, widely cited through 2026) — five workflow patterns: *prompt chaining, routing, parallelization, orchestrator-worker, evaluator-optimizer*. Core philosophy: **simplicity and composability over frameworks**; add agentic complexity only when simpler solutions fall short. [1][2]
2. **"How we built our multi-agent research system"** (2025) — orchestrator-worker with 3–5 parallel subagents + a **separate citation pass**; beat single-agent Opus 4 by **90.2%** on their internal eval at **~15× the token cost**. The three transferable patterns: *(a) externalize state to memory before context fills; (b) isolate workers with self-contained task descriptions; (c) verify high-stakes outputs with a separate pass.* Crucially: *most systems can capture the reliability gains inside a single agent without the 15× cost.* Early failure modes: spawning 50 subagents for trivial queries, endless web-scouring for nonexistent sources, agents distracting each other. [3][4]
3. **"Effective context engineering for AI agents"** (Sep 29, 2025) — eight named techniques: *system-prompt altitude, tool design, few-shot prompting, just-in-time retrieval, compaction, structured note-taking, sub-agent architectures, hybrid retrieval.* Guiding principle: *find the smallest set of high-signal tokens that maximize the likelihood of the desired outcome.* [5][6]
4. **"Effective harnesses for long-running agents"** + the **Claude Agent SDK** (Sep 2025, renamed from Claude Code SDK) — the harness = CLAUDE.md + tools (grep/glob/bash/web) + **Skills** + **subagents** + **hooks** + MCP + compaction + a memory tool. Subagents get isolated context windows and return condensed summaries. [7][8][9][10]

### 1.2 The multi-agent framework landscape (for context — we are NOT adopting one)

- **LangGraph** — explicit stateful graph, checkpointing + time-travel/rollback; production-durable; steeper learning curve. Surpassed CrewAI in GitHub stars in early 2026. [11][12]
- **CrewAI** — role-based "crews," lowest learning curve, mimics human team structure. [11][12]
- **AutoGen → Microsoft Agent Framework** — conversational multi-agent; AutoGen + Semantic Kernel unified into **Microsoft Agent Framework** (graph workflows, 1.0 GA) as the go-forward. [12][13]
- **OpenAI Agents SDK** — core abstraction is the **handoff** (explicit control transfer carrying context); OpenAI-models-only. [11][14]
- **Microsoft Magentic-One** — SOTA multi-agent team (web browse + code exec + file handling) built on AgentChat. [13]
- **Pydantic AI** (v1.0 Sep 2025) — "FastAPI feeling for GenAI," type-safe, validates LLM output against Pydantic models. [13][15]
- **Smolagents** (HF) — simplest; agents write **code** to act (code-as-action), yields measured performance gains. [15]
- **Mastra** (TS-native, YC W25) — workflows + memory + studio in one TS package. [15]
- **LangChain Deep Agents** — opinionated long-running-task layer over LangGraph (planner + sub-agents + file-system tool + detailed prompt). [13]

**Takeaway for us:** none of these is a fit to adopt wholesale — they're code frameworks; we orchestrate Claude Code sessions over a git repo with coordination TSVs. But several **patterns** inside them are worth borrowing (handoff contracts, graph-checkpoint thinking, code-as-action). Scored below.

### 1.3 Design patterns the field now treats as table-stakes

Orchestrator-worker · routing · parallelization/fan-out · evaluator-optimizer (generator+critic loop) · reflection/self-critique (Reflexion: write a verbal post-mortem, prepend on retry) [16][17] · ReAct/planning · memory systems (short-term trajectory + long-term experience; ExpeL-style rule extraction) [17][18] · context engineering (compaction, JIT retrieval, structured notes) · deep-agents (long-horizon planner + subagents + scratchpad) · subagent fan-out with condensed returns.

### 1.4 Evaluation & observability (the field's newest center of gravity)

- **Agent evaluation** splits three ways: *end-to-end (black box)*, *trajectory-level (plan/reasoning/tool-calls/retries/handoffs)*, *component-level (retriever/model/subagent)*. LLM-as-judge and **agent-as-judge** (judge the whole trajectory, not just the final output) are standard. Tools: LangSmith trajectory evals + `agentevals` package, DeepEval (50+ metrics, CI/CD-native), MLflow. [19][20][21]
- **Observability/tracing** — **OpenTelemetry GenAI semantic conventions** (`gen_ai.*`) are stabilizing into the cross-vendor standard for agent/LLM/MCP spans; **Langfuse** (Apache-2.0, self-hostable on Postgres+ClickHouse) and **Arize Phoenix** (vendor-agnostic, runs locally/Docker, native Claude Agent SDK support) are the leading OSS self-hosted options; **MLflow** (30M+ downloads/mo, Apache-2.0, no paywall) covers tracing+eval+prompt-opt. [22][23][24]

### 1.5 Agent Skills as an open standard (relevant to A2, noted here)

Anthropic released **Agent Skills as an open standard on 2025-12-18**; within weeks **OpenAI, Google, GitHub, and Cursor adopted it.** Progressive disclosure (frontmatter → SKILL.md body → on-demand references/scripts) is the design pattern. [25][26] — full treatment in `SKILLS_BEST_PRACTICE_AUDIT.md`.

---

## 2. Per-finding map — SOTA pattern × our Pearl system

Evidence anchors used below: `config/agents/agent_registry.yaml` (14 agents), `docs/SESSION_UNITY_PROTOCOL.md` (STARTUP/CLOSEOUT receipts, one-agent-one-workstream), `docs/agent_brief.txt` (router), `artifacts/coordination/*.tsv` (coordination state), `skills/*/SKILL.md`, and the operational lessons in `~/.claude/.../MEMORY.md`.

| # | SOTA pattern | Status | Evidence in our system / gap detail |
|---|--------------|--------|--------------------------------------|
| 1 | **Orchestrator-worker** | ✅ DOING | Our entire dispatch model: a router/orchestrator session emits paste-ready prompts (`docs/agent_brief.txt`, SESSION_UNITY §"Universal router prompt"); background subagents (like this one) execute and return a CLOSEOUT. This *is* orchestrator-worker. |
| 2 | **Parallelization / subagent fan-out** | ✅ DOING | Parallel worktree dispatch is a first-class pattern (`MEMORY.md` worktree-disk-constraint, isolation-PR skill cites #966–#988 fan-outs). |
| 3 | **Isolated worker context + condensed return** | ✅ DOING | Each subagent runs in its own session/worktree; the CLOSEOUT_RECEIPT *is* the condensed-summary return contract (SESSION_UNITY §Handoff). Matches Anthropic's "isolate workers with self-contained task descriptions." |
| 4 | **Externalize state before context fills** | ✅ DOING | We persist to coordination TSVs, `PEARL_*_STATE.md`, and `MEMORY.md` rather than holding state in-context. `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md` mandates persist-or-dump. Textbook structured note-taking. |
| 5 | **Separate verification pass for high-stakes output** | ✅ DOING | PR governance CI (`pr_governance_review.py`), push-guard, preflight, pre-merge check are all *separate verification passes* over high-stakes git actions — exactly the "verify with a separate pass" lesson. Citation-gap research has its own verification spec. |
| 6 | **Cost-control on fan-out (avoid 15× waste / 50-subagent blowups)** | ✅ DOING | This is our **serial-lane discipline** (`MEMORY.md`: serialize PRs on hot governance files; validation-before-scaling; disk-constraint prune-before-fan-out). We independently learned Anthropic's exact lesson: don't fan out when tasks aren't truly parallel / share state. |
| 7 | **Routing (task → right specialist)** | ✅ DOING | `SUBSYSTEM_AUTHORITY_MAP.tsv` + `agent_registry.yaml` + dispatch resolver (IMPROVEMENT_SPEC §3.2) = a routing workflow. |
| 8 | **System-prompt altitude** (not too brittle, not too vague) | ✅ DOING | SKILL.md files + CLAUDE.md hit a good altitude: concrete rules ("NEVER merge >50 deletions") + judgment ("when in doubt, stop and verify"). |
| 9 | **Reuse-first / anti-reinvention** | ✅ DOING (as policy) | `MEMORY.md` anti-reinvention architecture (router principle 9 + Canonical Artifacts Registry + CI reinvention guard). NB: the *registry file and CI guard are not yet on `main`* (gated on cascade-settle) — so this is policy-present, implementation-pending. Counts ✅ for *intent*, tracked as a build item. |
| 10 | **Just-in-time retrieval** (lightweight refs, load on demand) | 🟡 PARTIAL | Skills use progressive disclosure (references/ loaded on demand) ✅, but agent *prompts* still front-load large authority-doc read-lists rather than letting the agent pull just-in-time. Our DISCOVERY-REPORT pattern is a manual JIT pass. Opportunity: lean on glob/grep + a search index more, read-list less. |
| 11 | **Compaction for long-horizon sessions** | 🟡 PARTIAL | Claude Code gives us compaction for free at the harness level, but we have **no explicit checkpoint/resume protocol** for a multi-day workstream beyond the STATE.md files. Long cascades rely on re-reading state docs (works, but token-heavy). |
| 12 | **Evaluator-optimizer (generator + critic loop)** | 🟡 PARTIAL | We have *human-in-the-loop* review (Tier-1) and CI gates as critics, but no **automated generator→critic→regenerate loop** for content (e.g. an EI/quality critic that loops a chapter until it passes). The pieces exist (ei_v2, quality gates); they're not wired as an optimizer loop. |
| 13 | **Reflection / self-critique with persistent lessons** | 🟡 PARTIAL | `MEMORY.md` IS a Reflexion-style verbal-lessons store (post-mortems prepended to future sessions). Strong. But it's **manually curated**, not auto-written from failed trajectories, and carries the documented **self-reinforcing-error risk** [17] — partially mitigated by the "drift-recovery: git-first" rule that forces re-checking ground truth. |
| 14 | **Handoff contract between agents** | 🟡 PARTIAL | CLOSEOUT_RECEIPT `HANDOFF_TO`/`NEXT_ACTION` is a handoff contract ✅, but `AGENT_HANDOFF_SPEC.md` (IMPROVEMENT_SPEC §4) was **outlined and never created** — sub-handoff fields ("who owns the next commit") aren't enforced. OpenAI-SDK-style explicit handoff is the model to finish. |
| 15 | **Code-as-action** (agent writes code to act vs JSON tool calls) | 🟡 PARTIAL | Our agents already act via Bash/scripts (de-facto code-as-action) ✅, but we don't lean into the Smolagents finding deliberately; many flows could collapse multi-tool sequences into one script the agent writes. Minor. |
| 16 | **Agent trajectory evaluation** | ❌ GAP | No trajectory eval, no `agentevals`-style scoring of whether a Pearl session took a sensible plan/tool path. We judge *outputs* (PR diffs, artifacts) but never the *trajectory*. This is the single clearest gap vs SOTA. |
| 17 | **Structured observability / tracing (OTel GenAI)** | ❌ GAP | No spans, no trace store. We have logs (`artifacts/backup_*.log`) but nothing OTel-shaped. Can't answer "which step burned the tokens / where did the agent loop." Langfuse/Phoenix self-hosted would fit Tier-2. |
| 18 | **Skill/agent eval harness** | ❌ GAP | `skill-creator` ships an eval capability (we have the skill available) but we run **no evals** on our SKILL.md files or agent prompts. No regression test that a prompt still routes correctly. |
| 19 | **Machine-checkable registry validation** | ❌ GAP | `agent_registry.yaml` exists but `scripts/ci/check_agent_registry.py` (named as "future" in IMPROVEMENT_SPEC §5) was never built — registry can drift from `SUBSYSTEM_AUTHORITY_MAP.tsv` silently. (Cheap P0.) |
| 20 | **Auto-dispatch from path touches** (`git diff` → suggest owner agent) | ❌ GAP | IMPROVEMENT_SPEC §7 P2 / audit §D P2 named it; not built. A `code_globs` field + suggester would cut routing errors. |
| 21 | **Eval-driven skill improvement loop** (Claude-A refines / Claude-B tests) | ❌ GAP | The canonical skill-authoring loop (test with one agent, refine with another, observe, iterate) [25] is not part of our skill maintenance. We hand-edit SKILLs. |
| 22 | **Adopt a heavyweight agent framework** (LangGraph/CrewAI/etc.) | ⚪ N/A | We orchestrate Claude Code sessions over git, not a Python agent runtime. Adopting one would *add* reinvention, violating our own reuse-first principle. Borrow patterns, not the framework. |
| 23 | **Paid-API agent services** (hosted multi-agent, OpenAI-only SDK) | ⚪ N/A | Banned by CLAUDE.md Tier policy in repo code. Tier-1 (Claude Code, operator-present) and Tier-2 (Gemma/Qwen local) only. |

**Tally:** ✅ 9 · 🟡 7 · ❌ 6 · ⚪ 2.

---

## 3. Where we are genuinely ahead of the curve

Worth stating plainly for the operator — these are not lucky accidents, they're the system's real strengths and should be protected in any refactor:

1. **We learned the multi-agent cost lesson the hard way and codified it.** Anthropic warns "don't fan out 50 subagents / don't fan out when state is shared." Our `MEMORY.md` serial-lane + disk-constraint + validation-before-scaling rules are the operational form of exactly that. Most teams adopting agents in 2026 are *just now* hitting the 15× cost wall.
2. **Our CLOSEOUT_RECEIPT is a disciplined condensed-return contract** — the thing Anthropic's multi-agent post says workers must do. Many framework users let subagents dump full context back; we don't.
3. **Git-as-durable-memory + persist-or-dump** is a stronger durability story than most in-memory agent frameworks (LangGraph checkpointing is the closest commercial analog).
4. **Reuse-first as a stated principle** pre-empts the #1 agent-system failure mode (agents greenfielding parallel implementations).

---

## 4. The honest gaps (ranked)

1. **No trajectory eval / no observability (#16, #17).** We are flying blind on *how* agents reach outcomes. Everything else is downstream of this — without traces we can't even measure the other improvements. **Highest leverage.**
2. **No eval harness for skills/agents (#18, #21).** We can't catch a prompt regression or a skill that stopped triggering. `skill-creator` already gives us the tooling; we just don't run it.
3. **Unfinished handoff + registry-validation plumbing (#14, #19, #20).** All three were *designed in the 2026-04 spec and never built.* Cheap to finish; high governance payoff.
4. **No evaluator-optimizer content loop (#12).** Quality gates exist but aren't wired as an auto-regenerate loop — relevant to book/manga/EI quality.
5. **Reflective-memory self-reinforcement risk (#13).** `MEMORY.md` could ossify a wrong lesson. The git-first rule helps; a periodic "challenge the memory" consolidation pass (the `consolidate-memory` skill exists) would help more.

---

## 5. Cross-references

- Skills-specific SOTA + map → `SKILLS_BEST_PRACTICE_AUDIT.md`
- OSS tooling that closes the observability/eval gaps (Langfuse, Phoenix, DeepEval, agentevals) → `SYSTEMS_TOOLING_OPPORTUNITIES.md`
- Prioritized fixes for the 6 gaps → `IMPROVEMENT_ROADMAP.md`

---

## Sources (accessed 2026-06-11)

1. Anthropic — Building Effective AI Agents. https://www.anthropic.com/research/building-effective-agents
2. Anthropic — Building Effective Agents (engineering). https://www.anthropic.com/engineering/building-effective-agents
3. Anthropic — How we built our multi-agent research system. https://www.anthropic.com/engineering/multi-agent-research-system
4. ByteByteGo — How Anthropic Built a Multi-Agent Research System. https://blog.bytebytego.com/p/how-anthropic-built-a-multi-agent
5. Anthropic — Effective context engineering for AI agents (2025-09-29). https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
6. howaiworks — Context Engineering: AI Agent Optimization Guide. https://howaiworks.ai/blog/anthropic-context-engineering-for-agents
7. Anthropic — Effective harnesses for long-running agents. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
8. Anthropic — Building agents with the Claude Agent SDK. https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk
9. Claude Docs — Agent SDK overview. https://code.claude.com/docs/en/agent-sdk/overview
10. Claude Docs — Subagents in the SDK. https://platform.claude.com/docs/en/agent-sdk/subagents
11. Composio — OpenAI Agents SDK vs LangGraph vs AutoGen vs CrewAI. https://composio.dev/content/openai-agents-sdk-vs-langgraph-vs-autogen-vs-crewai
12. gurusup — Best Multi-Agent Frameworks 2026. https://gurusup.com/blog/best-multi-agent-frameworks-2026
13. LangChain — The best AI agent frameworks in 2026. https://www.langchain.com/resources/ai-agent-frameworks
14. Galileo — AutoGen vs CrewAI vs LangGraph vs OpenAI Agents. https://galileo.ai/blog/autogen-vs-crewai-vs-langgraph-vs-openai-agents-framework
15. Speakeasy — Choosing an agent framework (LangChain/LangGraph/CrewAI/PydanticAI/Mastra/Vercel). https://www.speakeasy.com/blog/ai-agent-framework-comparison
16. promptingguide — Reflexion technique. https://www.promptingguide.ai/techniques/reflexion
17. Shinn et al. — Reflexion: Language Agents with Verbal Reinforcement Learning. https://arxiv.org/pdf/2303.11366
18. ACM TOIS — A Survey on the Memory Mechanism of LLM-based Agents. https://dl.acm.org/doi/10.1145/3748302
19. Confident AI / DeepEval — LLM Agent Evaluation Complete Guide. https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide
20. LangChain Docs — Trajectory evaluations (LangSmith). https://docs.langchain.com/langsmith/trajectory-evals
21. langchain-ai/agentevals — readymade trajectory evaluators. https://github.com/langchain-ai/agentevals
22. OpenTelemetry — AI Agent Observability: Evolving Standards. https://opentelemetry.io/blog/2025/ai-agent-observability/
23. Langfuse (GitHub) — open-source AI engineering platform. https://github.com/langfuse/langfuse
24. Arize Phoenix (GitHub) — AI Observability & Evaluation. https://github.com/arize-ai/phoenix
25. Anthropic — Equipping agents for the real world with Agent Skills. https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
26. SwirlAI — Agent Skills: Progressive Disclosure as a System Design Pattern. https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure
