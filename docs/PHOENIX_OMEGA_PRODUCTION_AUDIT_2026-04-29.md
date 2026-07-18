# Phoenix Omega — Whole-Repo Production Audit
**Date:** 2026-04-29  •  **Anchor SHA:** `6375c8fcbf` (main)  •  **Audit branch:** `claude/wonderful-meitner-e5ac76`  •  **Scope:** read-only

This is a top-to-bottom audit of Phoenix Omega's production readiness across all 22 subsystems, all 75 CI workflows, all 42 open PRs, all 104 active workstreams, and all spec-vs-code drift surfaces. It produces a chronological pathway to 100% production-ready, with both AI-only and hired-team timelines and cost envelopes.

**Pathway companion:** [`PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md`](./PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md).

## TL;DR

**Phoenix Omega is ~50% production-ready, weighted across 22 subsystems** ([`q4_subsystem_matrix.md`](../artifacts/audit/q4_subsystem_matrix.md)). Throughput is exceptional — 181 PRs merged and ~1,038 commits in the last 14 days. **Production-output throughput in those same 14 days: zero new shippable artifacts** ([`q1_production_outputs.md`](../artifacts/audit/q1_production_outputs.md)). The factory is producing content substrate at industrial scale and shipping no books, no manga episodes, no audiobooks, and no podcasts to paying surfaces.

**The 5 things that gate everything:**

| # | cliff | phase | effort | citation |
|---|---|---|---|---|
| 1 | No EPUB packager exists | 1 | 2-3 engineer-days | [`q5: C7`](../artifacts/audit/q5_top_cliffs.md#c7-no-epub-packager-exists-s-phase-1) |
| 2 | 35 manga panel prompts, 0 chapter-bound renders | 3 | ~2 hours operator + GPU | [`q5: C15`](../artifacts/audit/q5_top_cliffs.md#c15-35-panel-prompts-0-chapter-bound-renders-s-phase-3) |
| 3 | main branch ruleset is permissive | 0 | 30 min | [`q5: C1`](../artifacts/audit/q5_top_cliffs.md#c1-main-branch-ruleset-is-permissive-p0--s-phase-0) |
| 4 | No KDP submission pipeline | 1 | 3-5 engineer-days | [`q5: C8`](../artifacts/audit/q5_top_cliffs.md#c8-no-kdp-submission-pipeline-s-phase-1) |
| 5 | Pipeline-mode default is `registry` (legacy) not `spine` (canonical) | 2 | 30 min | [`q5: C11`](../artifacts/audit/q5_top_cliffs.md#c11---pipeline-mode-spine-is-canonical-but-code-defaults-to-registry-p0--s-phase-2) |

**Calendar to 100% (synthesizing all 12 questions):**

- AI-only path (operator + Claude Code Tier-1 subscription): **~6 months**, ~$4k tooling + 1 GPU upgrade
- Hired-team path (operator + 4 engineers): **~3.5-4 months** parallel, ~$85-105k

## How this audit was produced

- 6 parallel research subagents (Q4 book / Q4 manga / Q4 ops / Q6 spec drift / Q8 CI health / Q10 cruft) wrote ~12-section detailed reports under `artifacts/audit/`
- Main thread synthesized Q1, Q2, Q3, Q5, Q7, Q9, Q11, Q12 + the cross-cutting pathway
- Citations: every claim cites a path:line, commit SHA, or `gh` output
- Scope: **read-only** — this PR introduces no production code, content, spec, workflow, or config changes; only `docs/` and `artifacts/audit/` files
- 0 paid LLM API calls; ~30 web fetches against public pricing pages and GitHub APIs

## What was found, by question

### Q1 — Production-output inventory ([`q1_production_outputs.md`](../artifacts/audit/q1_production_outputs.md))

What ships today: 12 articles/day to pearlnewsuna.org (Pearl News, LIVE), 42+ HTML breathwork apps on Cloudflare Pages, the Pearl Prime web preview on Cloudflare Workers, brand_admin shell pages, partial teacher_showcase.

What does not ship today: full books, full audiobooks, manga episodes, podcasts, KDP submissions, Apple Books, LINE Manga, Spotify Podcasts. The pipeline ratio for manga is 35 panel prompts : 0 chapter-bound renders. For books: 2,584 atoms : 0 packaged EPUBs.

### Q2 — In-flight workstreams ([`q2_inflight_workstreams.md`](../artifacts/audit/q2_inflight_workstreams.md))

42 open PRs (25 CONFLICTING, 11 of those >14d old — abandonment candidates). 33 active/in_progress/proposed workstreams of 104 total. 4 active projects, 1 stale 22 days. Recommend a 4-hour PR triage sweep.

### Q3 — Last-7-days reconciliation ([`q3_last_7_days.md`](../artifacts/audit/q3_last_7_days.md))

181 PRs merged, dominated by spec-739 variant-coverage gate, B1/B2 catalog work, manga catalog reconciliation, teacher_showcase repair. Per the explicit ship plan in `proj_manga_first_ship_20260425`: ep_001 NOT shipped; ja_JP partial; zh_CN not started. The throughput-vs-output gap is structural.

### Q4 — Subsystem readiness ([`q4_subsystem_matrix.md`](../artifacts/audit/q4_subsystem_matrix.md), [`q4_book_cluster.md`](../artifacts/audit/q4_book_cluster.md), [`q4_manga_cluster.md`](../artifacts/audit/q4_manga_cluster.md), [`q4_ops_cluster.md`](../artifacts/audit/q4_ops_cluster.md))

22 subsystems audited. Cluster averages: book 57.5%, manga 50%, ops 47%. Highest readiness: pearl_devops 85%, integrations 80%, manga_catalog 80%. Lowest: storefront_distribution 15%, recommendations 15%, lora_pipeline 15%, marketing 20%, podcast 30%, dashboard 30%.

### Q5 — Top cliffs ([`q5_top_cliffs.md`](../artifacts/audit/q5_top_cliffs.md))

30 cliffs, ranked. Phase 0 (foundation) has 6; Phase 1 (catalog→storefront) has 4 including the EPUB packager (single highest-ROI fix); Phase 2 has 4; Phase 3 has 4 manga cliffs; Phase 4 has 4 surface cliffs; Phase 5 has 2 locale cliffs; Phase 6 + cross-cutting has 6. **Top 5 cliffs are all sub-week unblocks.**

### Q6 — Spec-vs-code drift ([`q6_spec_drift.md`](../artifacts/audit/q6_spec_drift.md))

4 CRITICAL, 5 HIGH, 5 MEDIUM, 2 LOW, 12 verified-OK. Dominant pattern: **specs are written ahead of CI gates and the gates either never get enforced or never finish landing**. The headline finding is that three different docs name four required checks for `main`, and the live ruleset honors none of those four lists.

### Q7 — Documentation cliff ([`q7_documentation_cliff.md`](../artifacts/audit/q7_documentation_cliff.md))

DOCS_INDEX.md last_updated = 2026-04-10, 19 days stale; misses ~80 post-2026-04-10 docs/specs including `PIPELINE_DASHBOARD_INDEX.md`, the entire spec-739 cluster, and `MANGA_PIPELINE_AUDIT_2026-04-26.md`. **`docs/PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md` does not exist** — flagged as a Phase-1 documentation cliff.

### Q8 — CI health ([`q8_ci_health.md`](../artifacts/audit/q8_ci_health.md))

75 workflows. 14 BROKEN, 13 DEAD, 10 FLAKY, 38 HEALTHY. **Aggregate 14-day pass rate: 60.8%**. 5 workflows reference banned `secrets.CLAUDE_API_KEY`. `change-impact.yml` 0/30 pass — would block every PR if branch protection required it. `pearl-star-health.yml` */30 cron, 0/30 pass = ~672 false alerts/fortnight.

### Q9 — Test-suite reality ([`q9_test_reality.md`](../artifacts/audit/q9_test_reality.md))

233 test files, 1,246 test functions. **Test count is correlated with CI workflow presence, not with subsystem readiness.** brand_admin has 0 tests at 55% readiness. pearl_prime (the flagship) has 5 test files. manga has 52. Revenue-adjacent surfaces are systematically under-tested.

### Q10 — Repo cruft ([`q10_repo_cruft.md`](../artifacts/audit/q10_repo_cruft.md))

128 squash-merged remote branches lingering. 91 empty orphan worktree dirs. 11 abandoned PRs >14d. ~7.5 operator-hours to execute the recommended cleanup. ~9 MB direct disk savings (real disk wins are in `artifacts/`/`image_bank/`/`node_modules/` per the deletion plan).

### Q11 — Cost envelope ([`q11_cost_envelope.md`](../artifacts/audit/q11_cost_envelope.md))

Today: ~$265-426/month [ESTIMATED, no invoice access]. At full scale: ~$5.5-16k/month, dominated by manga GPU. **Single largest cost lever:** PR #623's GPU/LoRA hardware decision. Recommend GPU upgrade ≥24GB ($1.5k one-time), payback <6 months at expected manga volume.

### Q12 — Pathway to 100% ([`PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md`](./PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md))

6 phases (Phase 0 foundation → Phase 6 full automation), each with deliverables, AI-only timeline, hired-team timeline, and Phase-tagged cliffs that gate transition.

## Three structural findings (the audit's editorial)

### Structural finding 1 — Substrate without ship surface

The repo has built a phenomenally deep content substrate (2,584 atoms × 14 personas × 14 teachers × 26 brands × ~270 master arcs × 4 locales). It has not built the packager-and-submission layer that turns substrate into product.

**Why it matters.** Each additional substrate-PR has diminishing returns. Each ship-surface-PR (EPUB packager, KDP submission, Apple Books) has compounding returns. The next 30-45 days should be ship-surface-heavy, substrate-light.

### Structural finding 2 — Specs drift faster than gates

In multiple cases ([q6 §C.2](../artifacts/audit/q6_spec_drift.md), [q6 §C.3](../artifacts/audit/q6_spec_drift.md), [q5 C11](../artifacts/audit/q5_top_cliffs.md#c11---pipeline-mode-spine-is-canonical-but-code-defaults-to-registry-p0--s-phase-2)) the canonical spec says A, the code default does B, and CI doesn't enforce A. This is the same drift pattern in all of them.

**Why it matters.** Drift compounds silently. Every silent legacy-mode caller is an additional invisible debt entry. The pipeline-mode default flip alone (C11, 30 min of work) closes one of these debt streams.

### Structural finding 3 — Operator-attended gates are the single point of failure

`proj_manga_first_ship_20260425` has been ready-for-operator on GATE-OP-1 (R2 secrets) and GATE-OP-2 (Pearl Star marker) for weeks. The agent system cannot complete these. The 35 panel prompts sit waiting; the runbook is exhaustively detailed; the GPU is on; the secrets need to be pasted.

**Why it matters.** When a system has many operator-required gates and one operator, the operator becomes the bottleneck. A "minimize operator-attended steps" pass on every active project would change throughput. For now: GATE-OP-1 + GATE-OP-2 are 30 minutes of operator work that gate weeks of downstream pipeline.

## What this audit does not say

- Whether Phoenix Omega should ship at this pace. (That's a strategy call, not a production-readiness call.)
- Whether the manga line should ship before the book line. (Both are at similar Phase, similar readiness; the audit recommends operator make the strategic priority call.)
- Anything about pricing, GTM, partnerships, or revenue forecasting. (Out of scope.)
- Whether the 26-brand book registry vs 37-brand manga registry separation is the right architectural choice. (That decision was made and ratified per PR #722; this audit takes it as given.)

## Acknowledgments / inputs that were leveraged (not duplicated)

- Predecessor `docs/FULL_REPO_SYSTEM_AUDIT_2026-04-26.md` — referenced; this audit is the 2026-04-29 successor
- Predecessor `docs/FULL_REPO_CANONICAL_SYSTEM_MAP_2026-04-26.md` — leveraged
- `docs/PIPELINE_DASHBOARD_INDEX.md` (PR #730) — already-good single-page index for 17 subsystems
- `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` — primary subsystem registry (18 rows)
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` — 104 workstreams, all 15-column schema-conformant
- `artifacts/coordination/ACTIVE_PROJECTS.tsv` — 4 active projects
- `artifacts/inventory/full_repo_pipeline_matrix_2026-04-27.csv` — pipeline matrix
- `artifacts/inventory/full_repo_doc_status_matrix_2026-04-27.csv.gz` — doc lifecycle (referenced; not deeply scanned)
- `docs/FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md` — referenced for Q10 deletion recommendations
- PR #802 (open) drift autopsy — primary input for manga rendering quality findings

## Files in this audit (deliverables)

| file | purpose |
|---|---|
| [`docs/PHOENIX_OMEGA_PRODUCTION_AUDIT_2026-04-29.md`](./PHOENIX_OMEGA_PRODUCTION_AUDIT_2026-04-29.md) | this document — synthesis + executive summary |
| [`docs/PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md`](./PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md) | Q12 — chronological pathway, 6 phases |
| [`artifacts/audit/q1_production_outputs.md`](../artifacts/audit/q1_production_outputs.md) | what actually ships today |
| [`artifacts/audit/q2_inflight_workstreams.md`](../artifacts/audit/q2_inflight_workstreams.md) | open PR + workstream + project state |
| [`artifacts/audit/q3_last_7_days.md`](../artifacts/audit/q3_last_7_days.md) | last-7-days plan-vs-reality reconciliation |
| [`artifacts/audit/q4_subsystem_matrix.md`](../artifacts/audit/q4_subsystem_matrix.md) | 22-subsystem readiness matrix |
| [`artifacts/audit/q4_book_cluster.md`](../artifacts/audit/q4_book_cluster.md) | 7-subsystem book-cluster deep dive |
| [`artifacts/audit/q4_manga_cluster.md`](../artifacts/audit/q4_manga_cluster.md) | 5-subsystem manga-cluster deep dive |
| [`artifacts/audit/q4_ops_cluster.md`](../artifacts/audit/q4_ops_cluster.md) | 10-subsystem ops-cluster deep dive |
| [`artifacts/audit/q5_top_cliffs.md`](../artifacts/audit/q5_top_cliffs.md) | 30 cliffs ranked by ROI × phase |
| [`artifacts/audit/q6_spec_drift.md`](../artifacts/audit/q6_spec_drift.md) | spec-vs-code drift, 28 items |
| [`artifacts/audit/q7_documentation_cliff.md`](../artifacts/audit/q7_documentation_cliff.md) | documentation freshness + missing files |
| [`artifacts/audit/q8_ci_health.md`](../artifacts/audit/q8_ci_health.md) | 75-workflow CI health audit |
| [`artifacts/audit/q9_test_reality.md`](../artifacts/audit/q9_test_reality.md) | 233 test files / 1,246 functions reality |
| [`artifacts/audit/q10_repo_cruft.md`](../artifacts/audit/q10_repo_cruft.md) | branches / worktrees / PRs / cruft delete-or-keep |
| [`artifacts/audit/q11_cost_envelope.md`](../artifacts/audit/q11_cost_envelope.md) | tooling/operations cost projections |

## Re-audit cadence

After Phase 0 closes, after Phase 1 first-ship, after Phase 3 first-ship, then quarterly.

---
**Audit produced by:** Claude Code (Opus 4.7, 1M context) via 6 parallel research subagents + main-thread synthesis. ~7 hours wall time. 0 production files modified.
