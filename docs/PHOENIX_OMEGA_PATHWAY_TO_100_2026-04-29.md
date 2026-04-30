# Phoenix Omega — Pathway to 100% Production Ready
**Date:** 2026-04-29  •  **Audit anchor SHA:** `6375c8fcbf`  •  **Audit branch:** `claude/wonderful-meitner-e5ac76`

This document answers: **what does it take to make Phoenix Omega 100% production ready, in chronological shipping order, with both an AI-only and a hired-team timeline?**

Synthesizes [`artifacts/audit/q1_production_outputs.md`](../artifacts/audit/q1_production_outputs.md) through [`artifacts/audit/q11_cost_envelope.md`](../artifacts/audit/q11_cost_envelope.md). All claims cite path:line, commit SHA, or `gh` output.

## Status today (2026-04-29)

- 22 subsystems average ~50% complete (per [`q4_subsystem_matrix.md`](../artifacts/audit/q4_subsystem_matrix.md))
- Throughput is healthy: 181 PRs merged in last 7 days, ~1,038 commits in last 14 days
- **Production-output throughput is zero new shippable artifacts in the last 7 days** (per [`q1_production_outputs.md`](../artifacts/audit/q1_production_outputs.md))
- The repo is a content-substrate factory; it does not yet ship product

## North-star definition of "100% production-ready"

A system is 100% production-ready when:
1. Phase-tagged subsystems can run their primary workflow end-to-end without operator-attended steps
2. Every subsystem has at least one shipped artifact reaching a paying surface (KDP, Apple Books, LINE Manga, WEBTOON, Spotify Podcasts, WordPress, Cloudflare Pages)
3. Quality gates (EI V2, governance, branch protection) are load-bearing, not advisory
4. CI pass rate ≥ 95% across all 75 workflows
5. ~800 books × 12 locales catalog substrate is sellable, not just authored

## Phase 0 — Foundation & safety (must precede all else)

**Goal:** restore the contract layer. Currently 3 different docs name 4 different sets of required CI checks; live ruleset honors none. Permissive ruleset means PR #245-class (20,006-file deletion) incidents could recur.

### Phase-0 deliverables
- D-0.1 — Tighten main branch ruleset: require `Core tests`, `Release gates`, `EI V2 gates`, `pr-governance-review`, `llm-policy-enforcement` [Q5: C1]
- D-0.2 — Set required reviewer count ≥1 on main ruleset; remove `bypass_actors: [{actor_type: RepositoryRole, bypass_mode: always}]` [Q5: C1]
- D-0.3 — Remove `secrets.CLAUDE_API_KEY` from 5 workflows ([`q8_ci_health.md`](../artifacts/audit/q8_ci_health.md) §Banned-secret) [Q5: C2]
- D-0.4 — Fix `change-impact.yml` (currently 0/30 passing) so it can be made required [Q5: C3]
- D-0.5 — Add DeepSeek + Google AI Studio + R2_* APIs to `INTEGRATION_CREDENTIALS_REGISTRY.md` [Q5: C4]
- D-0.6 — Fix or silence `pearl-star-health.yml` (0/30, 672 false alerts/fortnight) [Q5: C5]
- D-0.7 — Wire EI V2 first promotion gate run; flip `learned_params.json` from seed [Q5: C6]
- D-0.8 — Reconcile `BRANCH_PROTECTION_REQUIREMENTS.md` ↔ `PEARL_PRIME_RELEASE_CONTRACT.md` ↔ live ruleset [Q5: C1+C3]

### Phase-0 timeline

| path | calendar |
|---|---|
| **AI-only** (operator + Claude Code Tier-1) | 3-4 days, mostly ruleset edits + workflow debugging |
| **Hired-team** (operator + 1 DevOps engineer) | 5 working days, includes regression testing + handover docs |

## Phase 1 — Catalog → storefront (the revenue floor)

**Goal:** turn the content substrate into a sellable book on at least one storefront.

### Phase-1 deliverables
- D-1.1 — Write `docs/PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md` (currently MISSING per [`q7_documentation_cliff.md`](../artifacts/audit/q7_documentation_cliff.md) §C) [Q5: C10]
- D-1.2 — Build `scripts/publish/build_epub.py` (single-input prose → EPUB w/ cover, metadata, TOC, validation) [Q5: C7]
- D-1.3 — Build `scripts/publish/kdp_books_upload.py` (KDP API or kdspy automation; manual review queue handling) [Q5: C8]
- D-1.4 — Submission test ship: 1 brand × 1 persona × 1 topic × en_US → KDP. Verify visible artifact at every checkpoint per `docs/COLAB_AND_BROWSER_VERIFICATION_RUNBOOK.md`
- D-1.5 — Build `scripts/publish/apple_books_upload.py` (next-locale-up after en_US KDP) [Q5: C9]
- D-1.6 — Tests for `scripts/publish/*` (currently 0 — see [`q9_test_reality.md`](../artifacts/audit/q9_test_reality.md) §E)
- D-1.7 — Scale to 50 books on KDP

### Phase-1 timeline

| path | calendar |
|---|---|
| **AI-only** | 3-4 weeks: 1 week for D-1.1+D-1.2 (EPUB packager); 1 week for D-1.3 (KDP submission); 1 week for D-1.4 first ship + iteration; 1 week for D-1.5 + scale |
| **Hired-team** (1 backend engineer + 1 publishing-domain engineer) | 6-8 weeks parallel: backend builds packager + APIs; publishing engineer handles KDP/Apple Books/LINE Manga submission norms in parallel |

### Phase-1 cliffs that block transition to Phase 2
- C7, C8, C9, C10 closed
- At least 1 book on KDP visible to a paying customer

## Phase 2 — Pearl Prime book pipeline hardening

**Goal:** the book pipeline is the canonical default, not the legacy fork. End-to-end book runs without operator-attended steps. Audiobook + video at parity for shipped books.

### Phase-2 deliverables
- D-2.1 — Flip `scripts/run_pipeline.py` default to `--pipeline-mode spine` (currently `registry`) [Q5: C11]
- D-2.2 — Wire sentinel acceptance evidence into `artifacts/sentinel/`; verify against `PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md:99` [Q5: C12]
- D-2.3 — Land spec-739 Phase 3 strict-runtime (proposed workstream `ws_spec_739_phase_3_strict_runtime_20260427`)
- D-2.4 — Multi-chapter audiobook concat + chapter-marker M4B + cover (full-book TTS path) [Q5: C13]
- D-2.5 — End-to-end book→video render (locale-aware) [Q5: C14]
- D-2.6 — pearl_prime end-to-end smoke test (currently 5 test files for the flagship — under-tested per [`q9_test_reality.md`](../artifacts/audit/q9_test_reality.md))
- D-2.7 — teacher_showcase format-grid overhaul merge (PR #798 in flight)

### Phase-2 timeline

| path | calendar |
|---|---|
| **AI-only** | 4-6 weeks |
| **Hired-team** (1 backend + 1 audio/video engineer) | 4-5 weeks parallel |

## Phase 3 — Manga pipeline first ship

**Goal:** ep_001 of "The Alarm Is Lying" (or any one episode) lands on WEBTOON Canvas + LINE Manga + KDP Comics.

### Phase-3 deliverables
- D-3.1 — Operator GATE-OP-1: add R2_ACCOUNT_ID + R2_BUCKET + R2_ACCESS_KEY_ID + R2_SECRET_ACCESS_KEY to GitHub Actions secrets (env vars already in registry per PR #731)
- D-3.2 — Operator GATE-OP-2: install Pearl Star marker file per `docs/sessions/SESSION_HANDOFF_2026-04-25.md`
- D-3.3 — Run `scripts/manga/queue_panel_renders.py` for ep_001 (35 panels) on Pearl Star [Q5: C15]
- D-3.4 — Apply PR #802 drift-autopsy fixes: remove "no text, no typography" from POSITIVE prompts; reconfigure schnell to steps=4/cfg=1.0; remove en_US locale suppression [Q5: C16]
- D-3.5 — Hardware decision (PR #623): GPU upgrade ≥24GB OR cloud LoRA training OR IP-Adapter [Q5: C17]
- D-3.6 — Train first brand LoRA (assumes D-3.5 chose GPU upgrade or cloud); start with 1 of 37 brands
- D-3.7 — Bubble compose ep_001 panels → episode strip; R2 upload; WEBTOON Canvas package
- D-3.8 — Atomic deletion PR for 132 stale series_plans + 716 stale book_plans (per `proj_manga_catalog_reconciliation_20260426`) [Q5: C18]
- D-3.9 — Submit ep_001 to WEBTOON Canvas; submit equivalent en_US to KDP Comics

### Phase-3 timeline

| path | calendar |
|---|---|
| **AI-only** | 3-5 weeks (1 week operator gates + GPU decision; 2 weeks LoRA training + render; 1 week compose+ship) |
| **Hired-team** (1 GPU/ML engineer + 1 manga-pipeline engineer) | 3-4 weeks parallel |

### Phase-3 cliffs to mind
- LoRA training is structurally blocked without hardware decision
- Operator-side gates GATE-OP-1/2 cannot be agent-completed
- Drift autopsy (PR #802) findings must land before any volume rendering

## Phase 4 — Surfaces & ops

**Goal:** brand_admin per-brand authoring works; marketing has 5+ funnels; dashboard is interactive; freebie has automation.

### Phase-4 deliverables
- D-4.1 — brand_admin test harness (currently 0 tests at 55% readiness) [Q5: C20, C29]
- D-4.2 — Marketing funnel-builder template + 5 brand-specific funnels (currently 1 of ~26) [Q5: C19]
- D-4.3 — Interactive dashboard (currently `docs/PIPELINE_DASHBOARD_INDEX.md` is markdown only) [Q5: C20]
- D-4.4 — Pearl News daily cron pass rate >90% (currently 57%) [Q5: C21]
- D-4.5 — JP LINE freebie funnel implementation (currently paper-only PR #801)
- D-4.6 — Storefront_distribution authority doc (currently no spec) [Q5: C22]
- D-4.7 — trend_feeds → consumer pipeline wired (currently runs but output not consumed)

### Phase-4 timeline

| path | calendar |
|---|---|
| **AI-only** | 6-8 weeks |
| **Hired-team** (1 frontend + 1 backend + 1 marketing engineer) | 4-5 weeks parallel |

## Phase 5 — Multi-locale + podcast

**Goal:** all 5 locales (en_US, ja_JP, zh_TW, zh_CN, ko_KR-rendered-held) ship books and manga at parity. Podcast pipeline produces and submits 1 episode/week.

### Phase-5 deliverables
- D-5.1 — Translation: close zh_CN ~2,200 atoms (Pearl Star Qwen, Tier-2, free) [Q5: C23]
- D-5.2 — Translation: close ja_JP ~366 remaining atoms
- D-5.3 — Locale-aware EPUB packager (extension of D-1.2)
- D-5.4 — Podcast pipeline: build `pearl_news/research/podcast/` + `config/integrations/podcast_credentials.yaml` + episode pipeline + Spotify/Apple Podcasts/Anchor RSS submission [Q5: C24]
- D-5.5 — First locale-shipped book: 1 ja_JP EPUB on KDP

### Phase-5 timeline

| path | calendar |
|---|---|
| **AI-only** | 4-5 weeks (translation is the long pole at Tier-2 throughput) |
| **Hired-team** (1 localization + 1 podcast/audio engineer) | 3 weeks parallel |

## Phase 6 — Full automation

**Goal:** recommendations subsystem live; weekly cadence shipping books AND manga AND audiobooks AND podcasts AND Pearl News articles AND social posts without operator-attended steps.

### Phase-6 deliverables
- D-6.1 — Recommendations producer (currently 15% / `backlog`) [Q5: C25]
- D-6.2 — Weekly book rollout cron uses Phase 1-2 pipeline (currently `weekly-book-rollout.yml` exists, gate on actual ship)
- D-6.3 — Weekly manga rollout cron uses Phase 3 pipeline (currently `weekly-manga-rollout.yml` exists)
- D-6.4 — Audiobook + podcast + video cadence cron crons; all green ≥3 weeks
- D-6.5 — Cleanup pass: delete 128 squash-merged remote branches; close 11 stale PRs; delete 91 empty worktree dirs (per [`q10_repo_cruft.md`](../artifacts/audit/q10_repo_cruft.md))
- D-6.6 — Re-run this audit; target ≥90% subsystem readiness average

### Phase-6 timeline

| path | calendar |
|---|---|
| **AI-only** | 3-4 weeks of cron-tuning + cleanup |
| **Hired-team** (operator + 1 SRE) | 2-3 weeks |

## Total calendar summary

| path | total calendar to 100% |
|---|---|
| **AI-only** (operator + Claude Code Tier-1 subscription) | **~6 months** (24-26 weeks) |
| **Hired-team** (operator + 4 engineers blended: backend, audio/video, GPU/ML, frontend; one rolling) | **~3.5-4 months** (14-17 weeks) parallel |

## Total cost envelope (per [`q11_cost_envelope.md`](../artifacts/audit/q11_cost_envelope.md))

| path | tooling/ops cost (6mo) | engineer cost (6mo) | total |
|---|---:|---:|---:|
| **AI-only** | $1,800-2,500 | $0 (already paying $200/mo Claude Pro) | **~$2.5k + 1 GPU upgrade $1.5k = ~$4k** |
| **Hired-team** | $2,500-4,000 | ~$80-100k blended at $800/day × 4 engineers × 14-17 weeks | **~$85-105k** |

## Critical-path summary (the 5 things that gate everything)

1. **D-1.2 EPUB packager** — gates all book ships [Phase 1]
2. **D-3.5 GPU/LoRA hardware decision** — gates all manga ships [Phase 3]
3. **D-1.3 KDP submission pipeline** — pairs with #1 [Phase 1]
4. **D-3.1 + D-3.2 operator gates** — single-line ops, gates first manga ship [Phase 3]
5. **D-2.1 pipeline-mode default flip** — gates Pearl Prime canonical operation [Phase 2]

These five, if landed in the next ~30-45 days, unlock 80% of the remaining pathway. The other 95% of the work is volume scaling, locale expansion, and ops hardening.

## Recommended next 7 days

After this audit lands and the operator reviews:

1. Phase 0: D-0.1 + D-0.2 + D-0.4 + D-0.5 (4 hours operator time; restore branch ruleset to spec)
2. Phase 1: scope D-1.1 doc + start D-1.2 EPUB packager (1-2 days operator time)
3. Phase 3: complete D-3.1 + D-3.2 + run D-3.3 (operator GPU run, ~2-3 hours wall time once gates are open)
4. Phase 2: D-2.1 pipeline-mode flip (30 min)
5. Defer Phase 4-6 work; close 11 stale PRs in a single triage pass

If those happen, the next 7-day reconciliation will read "1 book on KDP, 1 manga on WEBTOON, branch ruleset hardened" — fundamentally different from this 7-day reconciliation.

## What this pathway does NOT include

- Marketing / GTM strategy (out of scope; this is a production-readiness audit, not a go-to-market plan)
- Customer-facing pricing or partnership decisions
- Storefront royalty rate analysis
- Legal review of zh_CN gray-zone distribution disclosure framework
- Hiring decisions (the "hired-team" path is illustrative only)

## Re-audit cadence

Recommend re-running this audit when:
- Phase 0 closes (validate ruleset hardening)
- Phase 1 first-ship lands
- Phase 3 first-ship lands
- Quarterly thereafter
