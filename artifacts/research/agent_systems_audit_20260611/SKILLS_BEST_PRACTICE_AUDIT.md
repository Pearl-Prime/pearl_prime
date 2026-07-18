# Skills — Best-Practice Audit (2025–2026 SOTA vs `skills/`)

**Date:** 2026-06-11
**Agent:** Pearl_Research
**Scope:** Is our skills system using the best of what exists? SOTA inventory for the Claude Agent Skills standard → map vs our `skills/` tree.
**Companion:** `AGENTS_BEST_PRACTICE_AUDIT.md` (§1.5 introduces the standard).

**Our skills inventory (verified on `origin/main`):**
- `skills/pearl-github/SKILL.md` + `references/{git_system.md, repo_memory.md}` — gold standard, rich operational memory.
- `skills/pearl-int/SKILL.md` + `references/` (8 files: feeds, env template, credential staging, node inventory, …).
- `skills/deep-research/SKILL.md` + `references/{citation_format, regional_routing, tool_catalog}.md` + **`scripts/{detect_region.py, init_research_dir.sh}`** — the only skill shipping executable helpers.
- `skills/phoenix-isolation-pr/SKILL.md` — pattern-extraction skill (collapses ~300 lines of worktree/PR boilerplate; cites isolation PRs #966–#988).

Plus many **plugin/marketplace skills** available to sessions (anthropic-skills:pptx/docx/xlsx/pdf, skill-creator, deep-research, brand-voice:*, engineering:*, data:*, etc.) — these are consumed, not authored by us.

---

## 0. Executive summary

Our four authored skills are **already aligned with the Agent Skills standard's core design pattern — progressive disclosure** — better than most teams. Three of four use the `SKILL.md` + `references/` split correctly; `deep-research` additionally ships `scripts/`, which is the recommended "execution layer." The frontmatter `description` fields are detailed and trigger-rich (pearl-github's is a model of "when to load / when not to").

The gaps are **not structure but lifecycle**: (a) no skill **evals** despite `skill-creator` providing them; (b) pearl-github SKILL.md sits at 479 lines — within the 500-line/5k-token budget but **21 lines from the ceiling** (watch item); (c) no skill **versioning/changelog**; (d) we under-use **scripts** (only deep-research has them) where deterministic helpers would beat prose instructions; (e) no skills for the **domain agents** (Pearl_Prime, Pearl_Dev, etc.) that the 2026-04 spec said to author — those agents still run on ad hoc `*_ITE_PROMPT.md` files instead of progressive-disclosure skills.

**Counts:** 5 ✅ DOING · 4 🟡 PARTIAL · **5 ❌ GAP**.

---

## 1. SOTA inventory — Agent Skills standard (2025–2026)

- **Open standard, broad adoption.** Anthropic released Agent Skills as an **open standard on 2025-12-18**; **OpenAI, Google, GitHub, Cursor adopted within weeks.** Skills are now portable across agent runtimes. [1][2]
- **Progressive disclosure = the central pattern.** Three layers: **(1) Discovery** — only `name`+`description` frontmatter is pre-loaded into the system prompt (cheap, always-on); **(2) Instructions** — SKILL.md body loaded when the skill triggers; **(3) Execution** — `references/`, `scripts/`, templates pulled **on demand** when a step needs them. "Show just enough to decide what to do next, then reveal more." [2][3][4]
- **Budgets.** Keep SKILL.md body **under ~500 lines** and **≤ 5,000 tokens (recommended)**; overflow → split into `references/`. Full skill dir guidance also caps at 500 lines of always-relevant content. [4][5]
- **`description` is load-bearing.** The agent decides whether to load a skill **purely from the frontmatter description** — so it must say *when to use it AND when not to*, with concrete triggers. Vague descriptions = mis-triggering. (Same lesson as MCP tool descriptions.) [4][5]
- **Scripts > prose for determinism.** When a step is deterministic (init a dir, detect a region, validate a schema), ship a script in `scripts/` and have the SKILL.md call it, rather than describing the procedure in natural language. The execution layer exists for exactly this. [3][4]
- **Skill-creator + eval loop.** Both Anthropic and Google ship a **skill-creator** (generates skill files from NL). The authoring discipline is a **two-Claude loop**: Claude-A (expert) refines the SKILL.md; Claude-B (worker) uses it on *real* tasks; observe B's failures, feed back to A; strengthen language ("MUST filter" > "always filter"), reorganize for prominence. Real workflows, not test scenarios. [4][6]
- **Skills vs MCP.** Skills = portable, context-efficient procedural knowledge (no live connection); MCP = live access to external systems/data. Best systems combine both. [7]

---

## 2. Per-finding map — SOTA × our `skills/`

| # | SOTA practice | Status | Evidence / gap |
|---|---------------|--------|----------------|
| 1 | **Progressive disclosure (SKILL.md + references/)** | ✅ DOING | 3 of 4 skills split correctly. pearl-github → `references/{git_system, repo_memory}`; pearl-int → 8 reference files; deep-research → 3 references. Exactly the pattern. |
| 2 | **Execution layer (scripts/)** | ✅ DOING (one skill) | deep-research ships `scripts/detect_region.py` + `init_research_dir.sh` and the SKILL calls them. Model example — but it's the *only* skill that does this (see gap #C). |
| 3 | **Trigger-rich frontmatter `description`** | ✅ DOING | pearl-github's description enumerates concrete triggers + "always use this skill instead of raw git." deep-research lists exact trigger phrases ("research [topic]", "deep research", …) and an explicit MANDATORY rule. Strong. |
| 4 | **Operational memory inside the skill** | ✅ DOING (ahead of curve) | pearl-github keeps `references/repo_memory.md` and instructs "consult before risky git work." This is a Reflexion-style persistent-lessons store *scoped to a skill* — more sophisticated than the standard requires. |
| 5 | **Pattern-extraction to kill boilerplate** | ✅ DOING | phoenix-isolation-pr exists *specifically* to stop re-stating ~300 lines of worktree/PR boilerplate per subagent — a direct application of "move detail out of the prompt." Reuse-first, in skill form. |
| 6 | **SKILL.md body budget (≤500 lines / 5k tokens)** | 🟡 PARTIAL | Measured: pearl-github **479 lines / ~3.3k tok**, pearl-int **413 / ~3.0k**, phoenix-isolation-pr **310 / ~2.3k**, deep-research **206 / ~1.7k**. All *within* both budgets — but pearl-github is **21 lines from the 500-line ceiling**, so the next addition should land in `references/`, not the body. Flag as a watch item, not a violation. |
| 7 | **`description` says when NOT to use** | 🟡 PARTIAL | pearl-github/pearl-int say "you are NOT a general X assistant" ✅; deep-research is all positive triggers (no "don't use for…"). Minor; add negative triggers for cleaner routing. |
| 8 | **Skills vs MCP boundary is deliberate** | 🟡 PARTIAL | We *do* combine both (deep-research drives the Claude-in-Chrome MCP; pearl-int manages MCP-adjacent integrations) ✅, but it's not documented *why a skill vs an MCP server* for each capability. |
| 9 | **Portability of skills (open standard)** | 🟡 PARTIAL | Our SKILLs are standard-shaped so they'd port, but they're deeply repo-coupled (hard-coded paths, repo memory). That's *fine* for internal skills — just noting they're not reusable outside Phoenix Omega, by design. |
| 10 | **Skill evals (skill-creator eval capability)** | ❌ GAP | `skill-creator` (available to us) can benchmark a skill's trigger accuracy + task performance with variance analysis. **We run zero evals.** No regression guard that pearl-github still triggers on "push my branch," etc. |
| 11 | **Two-Claude refinement loop** | ❌ GAP | We hand-edit SKILLs. The canonical observe-B-feed-A loop isn't part of maintenance. |
| 12 | **Scripts for deterministic steps (broadly)** | ❌ GAP | Only deep-research ships scripts. pearl-github describes preflight in prose but could ship a `preflight.sh` wrapper the SKILL calls (it references repo scripts, but the skill itself ships none). phoenix-isolation-pr is *all prose* for a highly deterministic git sequence — a prime script candidate. |
| 13 | **Skill versioning / changelog** | ❌ GAP | No `CHANGELOG` or version field per skill dir (audit §D P2 named it). Can't tell when/why a skill changed, or roll back a bad edit except via git archaeology. |
| 14 | **Skills for domain agents (Pearl_Prime/Dev/News/…)** | ❌ GAP | 10 of 14 Pearl agents have `skill_path: null` in `agent_registry.yaml`; they run on `artifacts/coordination/PEARL_*_ITE_PROMPT.md` ad hoc prompts. The 2026-04 IMPROVEMENT_SPEC §2.2 prioritized authoring Pearl_Prime + Pearl_Dev skills first — **still not done.** Converting those prompts to progressive-disclosure SKILLs is the biggest skills win. |

**Tally:** ✅ 5 · 🟡 4 · ❌ 5.

---

## 3. Where our skills are ahead

1. **Skill-scoped operational memory** (`repo_memory.md`) is more advanced than the baseline standard — it's persistent reflection at the skill level.
2. **Boilerplate-killing skill** (phoenix-isolation-pr) is a textbook reuse-first move most teams haven't thought to make.
3. **Region-aware scripts in deep-research** show we already understand the execution layer; we just need to spread it.

---

## 4. Recommendations (feed into roadmap)

- **P0:** Run `skill-creator` evals on the 4 authored skills (trigger accuracy + a few real-task benchmarks). Cheap, catches regressions, establishes a baseline. → `IMPROVEMENT_ROADMAP.md` P0.
- **P0:** Audit pearl-github + pearl-int SKILL.md line counts; relocate overflow to `references/` to stay under budget.
- **P1:** Author `skills/pearl-prime/SKILL.md` and `skills/pearl-dev/SKILL.md` (convert the ITE prompts) — finishing the long-deferred 2026-04 P0.
- **P1:** Add a `scripts/` helper to phoenix-isolation-pr (the deterministic worktree→safety-gate→commit sequence).
- **P2:** Per-skill `CHANGELOG.md` + a `version` frontmatter field; adopt the two-Claude refinement loop for any skill that mis-triggers in evals.

---

## Sources (accessed 2026-06-11)

1. Claude Docs — Agent Skills overview. https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
2. Anthropic — Equipping agents for the real world with Agent Skills. https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
3. SwirlAI — Agent Skills: Progressive Disclosure as a System Design Pattern. https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure
4. Claude Docs — Skill authoring best practices. https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
5. Firecrawl — Agent Skills Explained: How SKILL.md Files Work. https://www.firecrawl.dev/blog/agent-skills
6. Anthropic — The Complete Guide to Building Skills for Claude (PDF). https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf
7. guptadeepak — MCP Enterprise Adoption Guide (Skills vs MCP). https://guptadeepak.com/the-complete-guide-to-model-context-protocol-mcp-enterprise-adoption-market-trends-and-implementation-strategies/
8. leehanchung — Claude Agent Skills: A First Principles Deep Dive. https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/
