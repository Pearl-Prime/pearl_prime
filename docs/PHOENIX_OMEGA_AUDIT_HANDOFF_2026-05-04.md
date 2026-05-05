# Phoenix Omega — Whole-Repo Production Audit Handoff

**Author:** Claude (current session)
**Date written:** 2026-05-04
**Brief issued:** 2026-04-29 (operator)
**Status:** STARTUP_RECEIPT phase complete; deep audit deferred — this doc is the bridge.
**Read-only contract:** No production code, content, spec, or workflow modified by this PR.

This document is the handoff for the next agent to pick up the deep multi-hour audit defined in the operator's
2026-04-29 "DEEP AUDIT BRIEF — Phoenix Omega Whole-Repo Status & Pathway to 100% Production-Ready" brief.

It captures: anchor reads completed, repo state surveyed, materially-relevant findings the operator should see
before the deeper passes run, and a concrete next-action checklist.

---

## 1. Anchor reads completed (2026-04-29 → 2026-05-04 session)

| # | Doc | Status | Lines | Notes |
|---|---|---|---|---|
| 1 | `CLAUDE.md` (root) | read fully | 247 | governance + tier policy + non-negotiable git rules |
| 2 | `docs/DOCS_INDEX.md` | TOC + lead 200L; deep-grep deferred | 2,255 | last_updated **2026-04-10**; 18 days stale relative to recent merge wave (#728-#796) |
| 3 | `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md` | read fully | 184 | spine pipeline = single source of truth; cleanup phases A-F all "pending review" |
| 4 | `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` | exists | 587 | deferred read |
| 5 | `docs/PEARL_PRIME_RELEASE_CONTRACT.md` | exists | 89 | deferred read |
| 6 | `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md` | exists | 442 | deferred read |
| 7 | `docs/MANGA_PIPELINE_COMPLETE_GUIDE.md` | exists | 58 | deferred read |
| 8 | `docs/MANGA_PIPELINE_AUDIT_2026-04-26.md` | exists | 836 | deferred read |
| 9 | `docs/PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md` | **MISSING** | n/a | flagged as P1 doc cliff (Q7) |
| 10 | `docs/FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md` | exists | 155 | deferred read |
| 11 | `docs/FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md` | exists | 160 | deferred read |
| 12 | `docs/PIPELINE_DASHBOARD_INDEX.md` | read fully | 264 | already maps 17 subsystems w/ owners; closes GAP-G1 |
| 13 | `docs/PEARL_PM_STATE.md` | exists | 145 | last_verified 2026-04-10 (per GAP-G2: stale) |
| 14 | `docs/PEARL_ARCHITECT_STATE.md` | exists | 388 | DASH-02, BR-CANON-01 routing decisions |
| 15 | `specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md` | exists | 239 | deferred read |

---

## 2. Pre-existing audit infrastructure (the next agent must use these as primary inputs, not duplicate them)

`artifacts/coordination/` — all timestamped 2026-04-29:

| File | Bytes | Purpose |
|---|---|---|
| `SUBSYSTEM_AUTHORITY_MAP.tsv` | 2,994 | 17 subsystems + authority docs + owner agent (Q4 primary input) |
| `ACTIVE_WORKSTREAMS.tsv` | 114,075 | in-flight workstreams (Q2 primary input) — note **GAP-G3: 7 schema-malformed rows** |
| `ACTIVE_PROJECTS.tsv` | 14,509 | current projects (Q3 primary input) |
| `BRANCH_INVENTORY_2026_04_01.tsv` | 5,004 | branch state (stale by ~28 days) |
| `BRANCH_TRIAGE_2026_04_01.md` | 13,465 | branch disposition decisions |
| `REPO_HEALTH_REPORT_2026_04_10.md` | 3,915 | last full health snapshot (24 days stale) |
| `REPO_CLEANUP_CANDIDATES_2026.tsv` | 2,499 | deletion candidate inventory |
| `PR_STATUS_REPORT_2026_04_10.md` | 3,877 | last full PR triage (24 days stale) |

`artifacts/inventory/` — newest snapshot 2026-04-27:

| File | Bytes | Purpose |
|---|---|---|
| `full_repo_pipeline_matrix_2026-04-27.csv` | 117,568 | every pipeline + entrypoint + callers + configs (Q4 primary input) |
| `full_repo_doc_status_matrix_2026-04-27.csv.gz` | 127,575 | per-doc canonical/superseded/orphan classification (Q7 primary input) |
| `full_repo_file_inventory_2026-04-26.csv.gz` | 435,856 | every tracked file + size + type + last_touched (Q10 primary input) |
| `full_repo_git_history_index_2026-04-26.csv` | 333,168 | per-file commit history (Q10 primary input) |
| `full_repo_audit_baseline_2026-04-26.md` | 10,364 | narrative audit baseline — predecessor of this audit |
| `atom_coverage_matrix.json` + `atom_coverage_report.md` | 12,619 + 5,868 | atom coverage state |
| `buildability_dashboard.md` | 6,724 | buildability state |
| `content_inventory.json` + `_summary.md` | 10,905 + 2,042 | content inventory |
| `big_view_gap_report.md` | 6,787 | gap inventory |

**Bottom line:** the next agent should diff these snapshots against the live repo and report deltas, not rebuild from scratch. ~7 days have elapsed since these were generated; the spec-739 + B1/B2 + #771 wave is post-snapshot.

---

## 3. Repo state snapshot (2026-05-04, this session)

### 3.1 Current worktree
- **Branch:** `claude/infallible-visvesvaraya-656e92`
- **Status:** clean, 0/0 divergent vs `origin/main`
- **HEAD:** `6375c8fcbf` — `catalog(b2): cluster_titles.py — B2 acceptance gate (extracted from #789) (#792)`

### 3.2 Parent checkout (`/Users/ahjan/phoenix_omega`)
- **Branch:** `agent/agents-md-coding-assistant-brief-20260426`
- **Status:** dirty — sibling-worktree `m`-markers in submodule slots (normal worktree side effect; not a real cliff)
- **Untracked:** 1 file — `artifacts/backup_qwen_forks_err.log` (M)

### 3.3 Worktree population
- **122 directory entries** under `.claude/worktrees/`
- **32 active worktree refs** per `git worktree list`
- **~90 entries appear abandoned** (Apr 24 timestamps, 64-byte placeholder dirs; not in `worktree list`)
- Recommendation: cleanup pass — see Phase 0 below.

### 3.4 Open PRs (live)
**42 open PRs** as of 2026-04-29 11:49 UTC. Distribution:

| Cluster | Count | Examples |
|---|---|---|
| **Last 24h (current wave)** | 5 | #803 community-assets audit, #802 cookbook research, #801 LINE-JP funnel plan, #798 teacher-showcase format grid, #797 launch-qa packet |
| **3-7 days, mergeable=UNKNOWN** | 14 | #787 locale spec, #736 LLM policy relax, #732 pearl-news teacher resolver, #724 manga pre-render preview, #683 pearl-prime gap analysis, #678 lettering v3 fix |
| **7-30 days, likely abandoned** | 23 | #623 first-book-pilot, #610 protagonist-LoRA, #606 FLUX prompt fix, #589 injection-resolver tests, #587 pearl-news deterministic slots, #581 dashboard logline swap, #568 i18n flag-nav, #546 manga character images, #545 manga dashboard rebuild, #544 zh-CN sprint, #495 QA reader, #450 authored synthesis, #446 depth budget, #445 bestseller depth p2, #444 R2 env registry, #430 brand-wizard, #427 R2 HTML uploader, #426 book-planning spec, #419 EI v2 bestseller corpus, #416 catalog-refinement, #407 gemma EN routing, #393 pearl-news live test, #377 compose wave 2 |
| **>30 days, definitely abandoned** | 4 | #369 master-wu courage E2E, #363 exercise overhaul, #344 teacher-showcase videos, #336 catalog quality refinement, #328 onboarding rebuild, #326 catalog production run |

**1 PR is CONFLICTING** (per `gh pr list` mergeable field): #679 AGENTS.md cross-vendor brief.

### 3.5 Merged in last 14 days (2026-04-15 → 2026-04-28)
**88+ PRs merged.** The major waves:

| Wave | Count | Theme | Anchor PRs |
|---|---|---|---|
| **Issue #786 launch readiness** | 8 | catalog B1/B2 gates, locale-native titles, scoring backfill | #780, #788, #790, #792, #793, #795, #796 |
| **spec-739 atom coverage** | 16 | Phase 1-3, validator, content backfills × ~10 personas | #743-#770 |
| **Pearl Prime / manga catalog** | 1 | book-script catalogs × 4 locales + manga plan | #771 |
| **Teacher-showcase #778** | 4 | audit, portraits, CTA, audiobook | #779, #781, #784, #785 |
| **Manga pipeline 2X** | 6 | atomic schema flip, regen 19,740 book plans, archive | #694, #696, #698, #699, #700, #717 |
| **Full-repo recon (PR-1..4)** | 4 | inventory tools, snapshots, canonical docs | #692, #695, #702, plus support |
| **Manga catalog + ep001 mecha** | 5 | revenue-weighted distribution, 8-market extension, mecha rebrand | #693, #722, #723, #725, #727, #738 |
| **Governance + dead-code cleanup** | 6 | PR governance workflow, D1 dead code, brand-wizard node_modules | #703, #704, #705, #706, #707 |

### 3.6 Workflows (`.github/workflows/`)
**75 workflow files.** High-level inventory:

| Cluster | Count | Examples |
|---|---|---|
| Manga | 12 | manga-pipeline, manga-image-gen, manga-bubble-regression, manga-quality-analysis, manga-rollout-notify, manga-smoke-test |
| Pearl News | 5 | pearl-news-daily, pearl-news-fill-qwen, pearl-news-assemble, pearl-news-full-qa, pearl-star-health |
| Catalog / book pipeline | 6 | catalog-book-pipeline, full-catalog-cli-en-us, max-quality-catalog, weekly-book-rollout, book-flagship-qa-ladder, single-book-smoke |
| Audio / video / podcast | 4 | audiobook-regression, generate-video-bank, podcast-weekly, video-daily-publish |
| Marketing | 3 | marketing_continuous, marketing-briefs-and-proposals, marketing-config-gate |
| Translation / locale | 3 | translate-atoms-qwen-matrix, translate-bestseller-atoms, locale-gate |
| Governance / hygiene | 11 | github-governance-check, llm-policy-enforcement, llm-callers-audit, no-binary-blobs, brand-guards, branch-hygiene-sweep, cleanup-stale-worktrees, docs-ci, manga-workflows-yml-validate, pr-governance-review, change-impact |
| ML / regression | 7 | ml-editorial-weekly, ml-loop-continuous, ml-loop-daily-promotion, ml-loop-weekly-recalibration, nightly-regression, regression-investigation-{deep-book,exercise-coverage}, regression-museum-gate |
| Quality gates | 5 | ei-v2-gates, variant-coverage-gate, release-gates, teacher-gates, simulation-10k |
| Release / rollout | 5 | weekly-pipeline, weekly-manga-rollout, manga-backend-flip, manga-stash-reminder, manga-character-sheet-build |
| Production / observability | 3 | production-alerts, production-observability, remote-commit-review |
| Other | 11 | (auto-merge-bot-fix, blocked-platforms, brand-admin-onboarding-pages, ei-v2-gates, manga-fonts-acquire, manga-image-bank-build, manga-operator-setup-verify, operator-setup-verify, pages, manga-series-pitch, research-pipeline-run, research_feeds_ingest, server-ci, manga-quality-forensic-analysis) |

**CI-health pass/fail rates:** NOT YET MEASURED. Next agent: run `gh run list --workflow <wf> --limit 14 --json conclusion,createdAt` per workflow and tabulate.

### 3.7 Branch protection on `main`
**🔴 P0 FINDING — `main` is NOT branch-protected:**
```
$ gh api repos/Ahjan108/phoenix_omega_v4.8/branches/main/protection
{"message":"Branch not protected","status":"404"}
```
This contradicts:
- `CLAUDE.md` Non-Negotiable Git Rule #0 ("NEVER merge a PR that deletes more than 50 files")
- `docs/BRANCH_PROTECTION_REQUIREMENTS.md` (existence implies enforcement)
- `docs/GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md` (PR #245 incident — 20,006 file deletion — the protection was the cure)
- The `pr-governance-review.yml` workflow (PR #705) only runs *checks*; without branch protection requiring it, a maintainer can still bypass.

**Action:** Operator must apply branch protection. Recommended ruleset:
- require pull request before merge (1+ approval)
- require `pr-governance-review` to pass
- require `core-tests`, `llm-policy-enforcement`, `variant-coverage-gate` to pass
- block force-push to main
- block deletion of main

### 3.8 Test suite (Q9 partial)
- **Test files:** 231 (up from claimed 37 in DOCS_INDEX — DOCS_INDEX is stale)
- **Test functions:** 2,260
- **Skip markers:** 98 (`@pytest.mark.skip` + `pytest.skip` + `@unittest.skip`)
- **Pass-rate / flake-rate / runtime:** NOT YET MEASURED. Next agent: run `pytest --collect-only` for full count, then targeted runs by subsystem.

### 3.9 Repo size + cruft (Q10 partial)
**Top dirs by size:**
- `artifacts/` — 1.5G (4,729 files)
- `brand-wizard-app/` — 514M (901 files; **node_modules already removed PR #707**)
- `image_bank/` — 441M (841 files)
- `assets/` — 180M
- `atoms/` — 161M (17,369 files)
- `config/` — 99M (23,057 files — **largest by file count**)

**Worktree cleanup candidates:** 90+ stale `.claude/worktrees/` dirs from 2026-04-24, all 64-byte placeholders, not in active worktree list. Single `rm -rf` candidate.

---

## 4. The 12-question audit framework — deferred deep passes

The full deep audit (per operator's brief) breaks into 12 questions. Each one's input + delegation status below.

| Q | Topic | Primary inputs | Status | Owner agent |
|---|---|---|---|---|
| Q1 | What ships today | DOCS_INDEX + PIPELINE_DASHBOARD_INDEX + repo grep | not started | main thread |
| Q2 | What's in flight | `gh pr list`, ACTIVE_WORKSTREAMS.tsv, worktree list | partial (§3.4) | main thread |
| Q3 | Last-7-days reconciliation | merged PR list (§3.5) + ACTIVE_PROJECTS.tsv | partial (§3.5) | main thread |
| Q4 | Subsystem readiness matrix | SUBSYSTEM_AUTHORITY_MAP + pipeline_matrix CSV | not started | parallel general-purpose × 3 |
| Q5 | Top-20 production cliffs | post-Q4 + Q6 + Q8 + Q10 | not started | general-purpose (post-Q4) |
| Q6 | Spec-vs-code drift | specs/*.md + docs/*_SPEC.md | not started | general-purpose |
| Q7 | Documentation cliff | doc_status_matrix + DOCS_INDEX freshness | partial (§1 row 9; §1 row 2 noted stale) | main thread |
| Q8 | CI / gate health | `gh run list` × 75 workflows | not started | general-purpose + Bash |
| Q9 | Test-suite reality | pytest --collect-only + coverage | partial (§3.8) | main thread (post-Q4) |
| Q10 | Repo cruft | file_inventory + git_history_index + worktrees | partial (§3.3, §3.9) | Explore agent |
| Q11 | Cost / throughput envelope | RunComfy logs + public pricing | not started | general-purpose |
| Q12 | Phase 0–6 pathway | synthesis of all prior | not started | main thread |

---

## 5. Materially-relevant findings already surfaced (early signals)

Findings that the next agent should treat as **starting hypotheses to validate**, not conclusions:

### 5.1 P0 cliffs (block shipping anything)
1. **`main` is unprotected** (§3.7). PR #245 incident already cost "hundreds of hours." Reapply protection before any further `--admin` merges (which CLAUDE.md bans anyway).
2. **PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md is missing** (§1 row 9). Brief lists it as anchor read; cited in storefront pathway (Phase 5). Either create the doc or reframe Phase 5 around what already exists in `docs/MANGA_FULL_CATALOG_PLAN.md` artifact + book script catalogs.
3. **DOCS_INDEX is 24 days stale** (last_updated 2026-04-10). The 88-PR wave since #728 has not been indexed. Many "(document all)" inventory rows in DOCS_INDEX point at files claimed missing/backlog that may now exist (or vice versa). Audit cannot trust DOCS_INDEX as ground truth without a refresh PR.

### 5.2 P1 cliffs (block one product line)
4. **18 PRs with mergeable=UNKNOWN** (§3.4). Likely stale base branches needing rebase. Each one needs a triage decision: rebase / abandon / merge-as-is.
5. **23 PRs in 7-30 day staleness band** (§3.4). Most are likely candidates for archive; some may have salvageable work (#623 first-book-pilot, #610 protagonist-LoRA — both directly named in operator's recent manga work).
6. **Spec-739 strict-gate is shipping post-#770** (per merged PR description "drop --skip-registry from strict gate"). Verify in workflow YAML that no `--skip-registry` flag remains.
7. **Stillness_press tentpole mismatch** (per operator brief Q5 candidates): ja_JP warrior_calm — matrix says BATTLE 25%, mono-genre says CULTIVATION. Decision recorded in MEMORY: H2=C "warrior_calm coexist: CULTIVATION spine + ja_JP BATTLE volume bet." Audit needs to verify the resolution actually landed in the catalog generator inputs.
8. **Cookbook PR #802 is in-flight** with the schnell-config bug (steps=24 cfg=4.0 — wrong for schnell variant). Until merged, manga renders use bad config.
9. **23 of 24 manga brands still mono-genre** — only stillness_press migrated to brand_portfolio_allocation. Phase 1 of pathway.

### 5.3 P2 cliffs (quality debt)
10. **GAP-G3: 7 schema-malformed rows** in `ACTIVE_WORKSTREAMS.tsv` (PIPELINE_DASHBOARD_INDEX §18). Open since 2026-04-26.
11. **GAP-G2: PEARL_PM_STATE.md last_verified 2026-04-10**. 24 days stale.
12. **GAP-G5: Pearl_DevOps subsystem missing from authority map** despite owning 72+ workflows.
13. **GAP-N1/N2/N3: Pearl News gaps** (per PIPELINE_DASHBOARD_INDEX §18). Status partial/open since 2026-04-26.
14. **`PHOENIX_OMEGA_INVESTOR_DD.xlsx` lives at repo root** (top-level dir listing) — should be in a non-tracked `business/` dir or LFS.
15. **Worktree cruft:** 90+ stale dirs, single `rm -rf` candidate.
16. **DOCS_INDEX claims "37 test files, 224 tests" — actual is 231 files, 2,260 tests** (§3.8). 10× understated; index is wildly out-of-date.

### 5.4 P3 cliffs (nice-to-have)
17. **Multiple "_SPEC.md" docs claim features that may not be implemented** — the cookbook research PR is producing a similar autopsy for manga; book pipeline equivalent not yet done.
18. **Pearl Prime Cloudflare Workers build always fails** (per CLAUDE.md known-known). Either fix or document the workaround.

---

## 6. Phase 0–6 pathway — preliminary sketch

This is the **headline deliverable** of the brief. Below is a sketch only — the deep agent must materially populate
calendar durations, dependencies, exit criteria, and risk register per phase, with both AI-only and hired-team paths.

### Phase 0 — Stabilize (prereq for everything)
**Exit criteria:** all P0 cliffs (§5.1) closed; main protected; DOCS_INDEX refreshed; cookbook PR #802 merged
- Apply branch protection to `main` (operator action, ~1h)
- Refresh `docs/DOCS_INDEX.md` to reflect 88-PR wave (1 doc-PR, ~4-6h agent work)
- Create or reframe `docs/PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md` (1 doc-PR, ~2-4h)
- Triage 18 UNKNOWN-mergeable PRs + 23 stale PRs (1 PR-triage doc, ~3-5h)
- Land cookbook PR #802 (verify schnell-config fix)
- Land community-asset audit PR #803 (closes "what assets do we have" question)
- Resolve warrior_calm tentpole mismatch (verify catalog inputs)
- Re-run Pearl Prime catalog with native title_templates (closes 3,592 blank titles per #793 wave)
- **AI-only path:** ~2-3 weeks calendar | **Hired-team path:** ~1 week

### Phase 1 — Close the catalog gap
**Exit criteria:** 24/24 brands on brand_portfolio_allocation; manga catalog × 4 locales (en_US + ja_JP + zh_TW + zh_CN); 4,304 blocked_score rows unblocked
- Migrate 23 brands to brand_portfolio_allocation
- Extend manga catalog to zh_TW + zh_CN
- Author ~110 genre-bridge series YAMLs
- Backfill `teacher_topic_persona_scores.yaml`
- Land cookbook recommendations into `genre_prompt_cookbook.yaml`
- **AI-only path:** ~4-6 weeks | **Hired-team path:** ~2-3 weeks

### Phase 2 — Generate the assets
**Exit criteria:** 800 high-confidence books each have cover image; 110 series each have main_character.png; 12-20 brand LoRAs trained
- Regenerate failure-genre stillness_press images with new cookbook prompts
- Generate main_character.png × 110 series across 23 newly-migrated brands
- Train brand-character LoRAs (12-20 per cookbook recommendation)
- Implement character-consistency pipeline (PuLID or InstantID)
- Smoke-test against QA harness; iterate
- **AI-only path:** ~6-10 weeks (RunComfy queue-bound) | **Hired-team path:** ~3-5 weeks

### Phase 3 — Wire the funnels
**Exit criteria:** LINE-JP funnel running end-to-end on 1 brand; GHL funnel hardened; freebie auto-gen working
- Build LINE-JP infrastructure (LINE OA × 12 brands, webhook receiver, message orchestrator) — PR #801 is the plan
- Production-harden GHL freebie funnel for non-Japan markets
- Implement freebie asset auto-generation (PDF + audio + manga sample)
- A/B test soft-launch with 1 brand per funnel; scale on conversion data
- **AI-only path:** ~4-8 weeks (real-traffic dependency) | **Hired-team path:** ~2-4 weeks

### Phase 4 — Render at scale
**Exit criteria:** 800 books × 4 locales rendered to publishable EPUB + cover + audiobook + podcast + manga adaptation
- Run rendering pipeline at scale
- Cloudflare Workers fix for pearl-prime
- Translation pipeline operational for non-English manuscript adaptation
- **AI-only path:** ~8-12 weeks (cost-bound + queue-bound) | **Hired-team path:** ~5-7 weeks

### Phase 5 — Storefronts & monetization
**Exit criteria:** listings live on Amazon KDP / Apple Books / Kobo / BookWalker JP / LINE Manga / Audible
- Storefront submissions
- Affiliate / referral plumbing
- LINE Pay (Japan) + GHL Stripe (US) direct integration
- **AI-only path:** ~6-12 weeks (platform-review-bound) | **Hired-team path:** ~4-8 weeks

### Phase 6 — Operations & scale
**Exit criteria:** weekly autonomous production queue; Pearl_PM + Pearl_Architect running on every PR; Pearl News daily; multilingual QA automated; sales-feedback loop wired
- Operational hardening
- Pearl News daily output operational
- Catalog regeneration on schedule
- Sales data → title_templates feedback loop
- **AI-only path:** ~8-16 weeks (compounding ops) | **Hired-team path:** ~6-10 weeks

**Total calendar to "100% production-ready":**
- AI-only path: **~38-67 weeks (~9-15 months)**
- Hired-team path: **~23-43 weeks (~5-10 months)**

These are SKETCH numbers — the deep agent must materially defend each duration with task-level estimates,
prereq dependencies, and risk-adjusted bands.

---

## 7. NEXT_ACTION — what the next agent should do

### 7.1 If continuing the full audit (5-8 hours of agent work)
1. Re-read this handoff doc
2. Confirm operator approval of I1–I7 from the original brief (defaults: I1=estimate-and-label, I2=21 subsystems, I4=both calendars, I5=ROI rank, I6=inventory+recommend, I7=full scope)
3. Spawn parallel subagents per delegation plan in §F of original receipt:
   - 3 × `general-purpose` for Q4 subsystem matrix (book / manga / ops clusters)
   - 1 × `general-purpose` for Q6 spec drift
   - 1 × `general-purpose` for Q8 CI health (`gh run list`-driven)
   - 1 × `Explore` for Q10 cruft
   - 1 × `general-purpose` for Q11 cost envelope
4. Synthesize Q5 ROI ranking + Q12 phase pathway in main thread
5. Write the 11 deliverable files per brief
6. push_guard + preflight + governance check; open PR

### 7.2 If pivoting to fix-Phase-0-cliffs-first (operator's likely preference)
1. **Branch protection on main** — operator action via GitHub UI or `gh api PUT repos/.../branches/main/protection`
2. **Triage UNKNOWN-mergeable PRs** — single doc PR
3. **DOCS_INDEX refresh** — single doc PR
4. **Decide on stale PRs** (#363 / #344 / #336 / #328 / #326 etc.) — abandon or salvage
5. Then return to deep audit

### 7.3 If running tighter audit scope (operator told to do Q1+Q4+Q5+Q12 only)
1. Skip Q6 / Q7 / Q9 / Q10 / Q11 deep passes
2. Use this handoff's §3 + §5 as the Q5 starting point
3. Use SUBSYSTEM_AUTHORITY_MAP + pipeline_matrix CSV as Q4 input directly
4. Write 4 deliverable files: production audit, pathway, subsystem matrix, cliffs YAML
5. ~2 hours total

### 7.4 What the operator should review NOW
- §3.7: branch protection 404 — **highest-leverage single fix**
- §5.1 cliffs 1-3: P0 list
- §6 pathway sketch: AI-only ~9-15 months, hired-team ~5-10 months — does this match operator expectations?
- I-additional in original receipt: PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md missing — operator decision: create or reframe
- §3.4: 23 likely-abandoned PRs (#363, #344, #336, #328, #326, etc.) — operator approve archive?

---

## 8. Files this handoff did NOT create (audit-only contract held)
- No production code touched
- No content / catalog / image regen
- No spec or workflow modified
- No paid LLM / image API calls

## 9. Caveats
- This is a **STARTUP_RECEIPT-level** handoff, not the full deep audit. The deep audit (4-6 hours of subagent work) is deferred.
- Numbers in §3 are point-in-time as of 2026-05-04. The repo continues to move.
- §5 cliffs are **starting hypotheses to validate**, not final conclusions. The deep audit must verify each with citations.
- §6 phase calendar is a **sketch**, not a defended estimate. Deep agent must produce task-level breakdowns.
- §7 "NEXT_ACTION" assumes operator approval of I1–I7 defaults. Operator may override.

## 10. Source-of-truth files for the next agent
- This doc: `docs/PHOENIX_OMEGA_AUDIT_HANDOFF_2026-05-04.md`
- Operator brief: passed in chat 2026-04-29 (not in repo)
- Full receipt: also passed in chat 2026-04-29 (not in repo)
- Pre-existing audit infra: `artifacts/coordination/` + `artifacts/inventory/` (see §2)
- Anchor docs: see §1
