# Q8 — CI / Workflow Health Audit

**Generated:** 2026-04-29
**Auditor:** Pearl_GitHub (read-only)
**Scope:** All 75 workflow files in `.github/workflows/`
**Method:** `gh run list --workflow=<file> --limit 30 --json conclusion,createdAt,status,event` per workflow + `head -40` for trigger config + `gh api repos/:owner/:repo/branches/main/protection`.

---

## Executive summary

- **Total workflows:** 75
- **HEALTHY:** 38 (50.7%)
- **BROKEN (3+ consecutive failures):** 14 (18.7%)
- **FLAKY (intermittent):** 10 (13.3%)
- **DEAD (>30d no run, or never run):** 13 (17.3%)
- **Aggregate 14d pass rate (success / non-cancelled runs across all workflows):** **562/924 = 60.8%**
- **Workflows scheduled (cron):** 28
- **PR-triggered:** 23 — but **0 of these gate main** because branch protection is OFF (P0).
- **Required-on-main checks:** **NONE** — `gh api .../branches/main/protection` returns HTTP 404 "Branch not protected".

Bottom line: PR governance + LLM policy enforcement workflows are passing, but they are advisory only. Anyone with push access can merge to `main` regardless of CI verdict. This is the single biggest CI risk in the repo.

---

## A. Workflow health table (75 rows)

Legend: `gates_main` = workflow has `if: github.ref == 'refs/heads/main'` or `branches: [main]` filter (does NOT mean it's a *required* check — see Section D).

| # | filename | trigger | cron | last_status | last_date | 14d_pass | gates_main | subsystem | health | drift |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `audiobook-regression.yml` | pull_request+push+workflow_dispatch | `` | failure | 2026-04-01 | 0/0 | no | catalog | BROKEN | MED |
| 2 | `auto-merge-bot-fix.yml` | pull_request | `` | skipped | 2026-04-29 | 0/30 | no | misc | FLAKY | MED |
| 3 | `blocked-platforms.yml` | pull_request+push | `` | success | 2026-04-24 | 4/4 | no | policy | HEALTHY | MED |
| 4 | `book-flagship-qa-ladder.yml` | workflow_dispatch | `` | success | 2026-04-17 | 1/1 | no | catalog | HEALTHY | LOW |
| 5 | `branch-hygiene-sweep.yml` | schedule+workflow_dispatch | `0 10 * * MON` | failure | 2026-04-29 | 0/30 | no | git-ops | BROKEN | HIGH |
| 6 | `brand-admin-onboarding-pages.yml` | push+workflow_dispatch | `` | success | 2026-04-28 | 25/29 | no | ops | HEALTHY | LOW |
| 7 | `brand-guards.yml` | pull_request+push | `` | success | 2026-04-08 | 0/0 | no | policy | HEALTHY | MED |
| 8 | `catalog-book-pipeline.yml` | schedule+workflow_dispatch | `0 6 * * 1` | cancelled | 2026-04-27 | 0/0 | no | catalog | FLAKY | HIGH |
| 9 | `change-impact.yml` | pull_request | `` | failure | 2026-04-29 | 0/30 | yes | policy | BROKEN | MED |
| 10 | `cleanup-stale-worktrees.yml` | schedule+workflow_dispatch | `17 3 * * *` | success | 2026-04-29 | 5/5 | no | ops | HEALTHY | LOW |
| 11 | `core-tests.yml` | pull_request+push | `` | success | 2026-04-29 | 30/30 | no | core | HEALTHY | MED |
| 12 | `docs-ci.yml` | pull_request+push | `` | success | 2026-04-29 | 30/30 | no | docs | HEALTHY | MED |
| 13 | `ei-v2-gates.yml` | pull_request+push+schedule+workflow_dispatch | `0 4 * * 1` | success | 2026-04-29 | 30/30 | no | ei | HEALTHY | MED |
| 14 | `full-catalog-cli-en-us.yml` | workflow_dispatch | `` | success | 2026-03-23 | 0/0 | no | catalog | DEAD | LOW |
| 15 | `generate-and-translate-atoms.yml` | workflow_dispatch | `` | cancelled | 2026-04-02 | 0/0 | no | translate | FLAKY | LOW |
| 16 | `generate-video-bank.yml` | workflow_dispatch | `` | success | 2026-04-02 | 0/0 | no | media | HEALTHY | LOW |
| 17 | `github-governance-check.yml` | pull_request+push | `` | success | 2026-04-29 | 30/30 | no | governance | HEALTHY | HIGH |
| 18 | `llm-callers-audit.yml` | pull_request+schedule+workflow_dispatch | `0 9 * * 5` | success | 2026-04-29 | 30/30 | no | llm-policy | HEALTHY | HIGH |
| 19 | `llm-policy-enforcement.yml` | pull_request+workflow_dispatch | `` | success | 2026-04-29 | 30/30 | no | llm-policy | HEALTHY | HIGH |
| 20 | `locale-gate.yml` | pull_request+push | `` | success | 2026-04-24 | 21/21 | yes | i18n | HEALTHY | MED |
| 21 | `manga-backend-flip.yml` | workflow_dispatch | `` | never_run | never | 0/0 | no | manga | DEAD | LOW |
| 22 | `manga-bubble-regression.yml` | schedule+workflow_dispatch | `0 8 * * *` | success | 2026-04-29 | 10/10 | no | manga | HEALTHY | LOW |
| 23 | `manga-catalog-plan-regen-check.yml` | pull_request+push | `` | success | 2026-04-28 | 30/30 | yes | manga | HEALTHY | MED |
| 24 | `manga-character-sheet-build.yml` | workflow_dispatch | `` | never_run | never | 0/0 | no | manga | DEAD | LOW |
| 25 | `manga-fonts-acquire.yml` | workflow_dispatch | `` | never_run | never | 0/0 | no | manga | DEAD | LOW |
| 26 | `manga-image-bank-build.yml` | workflow_dispatch | `` | never_run | never | 0/0 | no | manga | DEAD | LOW |
| 27 | `manga-image-gen.yml` | workflow_dispatch | `` | failure | 2026-04-02 | 0/0 | no | manga | FLAKY | LOW |
| 28 | `manga-operator-setup-verify.yml` | schedule+workflow_dispatch | `0 */6 * * *` | failure | 2026-04-29 | 0/30 | no | manga | BROKEN | HIGH |
| 29 | `manga-pipeline.yml` | workflow_dispatch | `` | never_run | never | 0/0 | no | manga | DEAD | LOW |
| 30 | `manga-quality-analysis.yml` | workflow_dispatch | `` | never_run | never | 0/0 | no | manga | DEAD | LOW |
| 31 | `manga-quality-forensic-analysis.yml` | workflow_dispatch | `` | never_run | never | 0/0 | no | manga | DEAD | LOW |
| 32 | `manga-rollout-notify.yml` | workflow_run | `` | success | 2026-04-27 | 2/2 | no | manga | HEALTHY | LOW |
| 33 | `manga-series-pitch.yml` | workflow_dispatch | `` | never_run | never | 0/0 | no | manga | DEAD | LOW |
| 34 | `manga-smoke-test.yml` | pull_request+workflow_dispatch | `` | success | 2026-04-17 | 3/3 | no | manga | HEALTHY | MED |
| 35 | `manga-stash-reminder.yml` | workflow_dispatch | `` | never_run | never | 0/0 | no | manga | DEAD | LOW |
| 36 | `manga-workflows-yml-validate.yml` | pull_request | `` | success | 2026-04-26 | 6/6 | no | manga | HEALTHY | MED |
| 37 | `marketing-briefs-and-proposals.yml` | schedule+workflow_dispatch | `0 8 * * *` | queued | 2026-04-29 | 0/1 | no | marketing | FLAKY | HIGH |
| 38 | `marketing-config-gate.yml` | pull_request+push | `` | success | 2026-04-26 | 2/2 | yes | marketing | HEALTHY | MED |
| 39 | `marketing_continuous.yml` | schedule+workflow_dispatch | `15 * * * *` | queued | 2026-04-29 | 0/1 | no | marketing | FLAKY | HIGH |
| 40 | `max-quality-catalog.yml` | workflow_dispatch | `` | failure | 2026-04-29 | 0/30 | no | catalog | BROKEN | LOW |
| 41 | `ml-editorial-weekly.yml` | schedule+workflow_dispatch | `0 9 * * 1` | success | 2026-04-27 | 2/2 | no | ml-loop | HEALTHY | LOW |
| 42 | `ml-loop-continuous.yml` | schedule+workflow_dispatch | `0 * * * *` | success | 2026-04-29 | 29/30 | no | ml-loop | HEALTHY | LOW |
| 43 | `ml-loop-daily-promotion.yml` | schedule+workflow_dispatch | `0 8 * * *` | success | 2026-04-29 | 14/14 | no | ml-loop | HEALTHY | LOW |
| 44 | `ml-loop-weekly-recalibration.yml` | schedule+workflow_dispatch | `0 10 * * 1` | success | 2026-04-27 | 2/2 | no | ml-loop | HEALTHY | LOW |
| 45 | `nightly-regression.yml` | schedule+workflow_dispatch | `0 3 * * *` | success | 2026-04-29 | 13/13 | no | regression | HEALTHY | LOW |
| 46 | `no-binary-blobs.yml` | pull_request | `` | success | 2026-04-29 | 29/30 | yes | policy | HEALTHY | MED |
| 47 | `operator-setup-verify.yml` | schedule+workflow_dispatch | `0 */6 * * *` | failure | 2026-04-29 | 0/30 | no | ops | BROKEN | HIGH |
| 48 | `pages.yml` | push+workflow_dispatch | `` | success | 2026-04-28 | 28/28 | no | ops | HEALTHY | LOW |
| 49 | `pearl-news-assemble.yml` | workflow_dispatch+workflow_call | `` | never_run | never | 0/0 | no | pearl-news | DEAD | LOW |
| 50 | `pearl-news-daily.yml` | schedule+workflow_dispatch | `0 22 * * *` | success | 2026-04-29 | 16/28 | no | pearl-news | HEALTHY | LOW |
| 51 | `pearl-news-fill-qwen.yml` | workflow_dispatch+workflow_call | `` | never_run | never | 0/0 | no | pearl-news | DEAD | LOW |
| 52 | `pearl-news-full-qa.yml` | workflow_dispatch | `` | failure | 2026-04-29 | 0/30 | no | pearl-news | BROKEN | LOW |
| 53 | `pearl-star-health.yml` | schedule+workflow_dispatch | `*/30 * * * *` | failure | 2026-04-29 | 0/30 | no | ops | BROKEN | HIGH |
| 54 | `podcast-weekly.yml` | schedule+workflow_dispatch | `0 10 * * 1` | failure | 2026-04-27 | 0/2 | no | media | BROKEN | HIGH |
| 55 | `pr-governance-review.yml` | pull_request | `` | success | 2026-04-29 | 30/30 | no | governance | HEALTHY | HIGH |
| 56 | `production-alerts.yml` | workflow_run | `` | skipped | 2026-04-29 | 1/30 | no | ops | FLAKY | LOW |
| 57 | `production-observability.yml` | schedule+workflow_dispatch | `0 7 * * *` | failure | 2026-04-29 | 2/14 | no | ops | BROKEN | HIGH |
| 58 | `regression-investigation-deep-book.yml` | workflow_dispatch | `` | failure | 2026-04-17 | 0/2 | no | catalog | FLAKY | LOW |
| 59 | `regression-investigation-exercise-coverage.yml` | workflow_dispatch | `` | failure | 2026-04-17 | 0/1 | no | regression | FLAKY | LOW |
| 60 | `regression-museum-gate.yml` | pull_request+workflow_dispatch | `` | success | 2026-04-29 | 30/30 | no | regression | HEALTHY | MED |
| 61 | `release-gates.yml` | pull_request+push+schedule+workflow_dispatch | `0 6 * * 0` | success | 2026-04-29 | 25/30 | yes | release | HEALTHY | MED |
| 62 | `remote-commit-review.yml` | schedule+workflow_dispatch | `0 9 * * 1` | success | 2026-04-27 | 2/2 | no | git-ops | HEALTHY | LOW |
| 63 | `research-pipeline-run.yml` | workflow_dispatch | `` | never_run | never | 0/0 | no | research | DEAD | LOW |
| 64 | `research_feeds_ingest.yml` | schedule+workflow_dispatch | `0 12 * * 1` | success | 2026-04-27 | 2/2 | no | research | HEALTHY | LOW |
| 65 | `server-ci.yml` | pull_request+push | `` | success | 2026-04-09 | 0/0 | no | core | HEALTHY | MED |
| 66 | `simulation-10k.yml` | push+schedule+workflow_dispatch | `0 6 * * 1` | failure | 2026-04-27 | 0/2 | no | simulation | BROKEN | HIGH |
| 67 | `single-book-smoke.yml` | workflow_dispatch | `` | success | 2026-04-17 | 1/1 | no | catalog | HEALTHY | LOW |
| 68 | `teacher-gates.yml` | pull_request+push | `` | failure | 2026-04-23 | 4/19 | no | teacher | BROKEN | MED |
| 69 | `translate-atoms-qwen-matrix.yml` | schedule+workflow_dispatch | `0 2 * * 0` | failure | 2026-04-26 | 0/2 | no | translate | BROKEN | HIGH |
| 70 | `translate-bestseller-atoms.yml` | workflow_dispatch | `` | failure | 2026-04-29 | 0/30 | no | translate | BROKEN | LOW |
| 71 | `variant-coverage-gate.yml` | pull_request+workflow_dispatch | `` | success | 2026-04-28 | 25/25 | no | policy | HEALTHY | MED |
| 72 | `video-daily-publish.yml` | schedule+workflow_dispatch | `0 14 * * *` | success | 2026-04-28 | 14/14 | no | media | HEALTHY | LOW |
| 73 | `weekly-book-rollout.yml` | schedule+workflow_dispatch | `0 6 * * 0` | success | 2026-04-26 | 2/2 | no | catalog | HEALTHY | LOW |
| 74 | `weekly-manga-rollout.yml` | schedule+workflow_dispatch | `0 14 * * 1` | failure | 2026-04-27 | 0/2 | no | ops | FLAKY | HIGH |
| 75 | `weekly-pipeline.yml` | schedule+workflow_dispatch | `0 8 * * 1` | success | 2026-04-27 | 2/2 | no | ops | HEALTHY | LOW |

---

## B. Top 10 broken / flaky workflows (last 5 runs each)

Sorted by drift risk × failure recency. All citations from `gh run list --workflow=<file> --limit 30`.

### 1. `pearl-star-health.yml` — BROKEN, drift=HIGH (cron `*/30 * * * *`)
Last 5 runs (all schedule):
- 2026-04-29 failure
- 2026-04-29 failure
- 2026-04-29 failure
- 2026-04-29 failure
- 2026-04-29 failure

14d pass: **0/30**. Health probe firing every 30 min and failing every time — produces 48 false alerts/day. Fix or silence.

### 2. `manga-operator-setup-verify.yml` — BROKEN, drift=HIGH (cron `0 */6 * * *`)
- 2026-04-29 failure (schedule) ×3 today, 2026-04-28 failure ×2.
- 14d pass: **0/30**. Verifies operator setup; chronic failure means the manga onboarding signal is dead.

### 3. `operator-setup-verify.yml` — BROKEN, drift=HIGH (cron `0 */6 * * *`)
- 2026-04-29 failure (push) ×5.
- 14d pass: **0/30**. Same pattern as above for the general operator setup.

### 4. `branch-hygiene-sweep.yml` — BROKEN, drift=HIGH (cron `0 10 * * MON`)
- 2026-04-29 failure (push) ×5.
- 14d pass: **0/30**. Pearl_GitHub-owned. Stale-branch sweep failing means hygiene drift is silently accumulating.

### 5. `production-observability.yml` — BROKEN, drift=HIGH (cron `0 7 * * *`)
- 2026-04-29 failure
- 2026-04-28 failure
- 2026-04-27 failure
- 2026-04-26 failure
- 2026-04-25 failure
- 14d pass: **2/14**. Daily. The `production-alerts.yml` workflow that depends on it is mostly skipped (1/30 in 14d) — observability layer non-functional.

### 6. `change-impact.yml` — BROKEN, drift=MED (PR-triggered, gates_main=yes)
- 2026-04-29 failure (push) ×5.
- 14d pass: **0/30**. Gates main on paper but main has no protection so it doesn't actually block; once protection is restored this becomes a P0 merge blocker.

### 7. `simulation-10k.yml` — BROKEN, drift=HIGH (cron `0 6 * * 1`, also push trigger)
- 2026-04-27 failure (schedule)
- 2026-04-20 failure (schedule)
- 2026-04-13 failure (schedule)
- 2026-04-12 failure (push)
- 2026-04-06 failure (schedule)
- 14d pass: **0/2**. Failing every Monday for 4 consecutive weeks.

### 8. `translate-atoms-qwen-matrix.yml` — BROKEN, drift=HIGH (cron `0 2 * * 0`)
- 2026-04-26 failure (schedule)
- 2026-04-19 failure (schedule)
- 2026-04-12 failure (schedule)
- 2026-04-05 failure (schedule)
- 2026-04-02 success (workflow_dispatch)
- 14d pass: **0/2**. Last successful scheduled run unknown (>30d). CJK6 translation matrix dark.

### 9. `podcast-weekly.yml` — BROKEN, drift=HIGH (cron `0 10 * * 1`)
- 2026-04-27 failure (schedule)
- 2026-04-20 failure (schedule)
- 2026-04-13 failure (schedule)
- 14d pass: **0/2**. Weekly podcast publish broken for 3+ weeks.

### 10. `teacher-gates.yml` — BROKEN, drift=MED (PR-triggered)
- 2026-04-23 failure (push)
- 2026-04-23 failure (pull_request)
- 2026-04-23 failure (pull_request)
- 2026-04-22 failure (pull_request)
- 2026-04-22 failure (pull_request)
- 14d pass: **4/19** (~21%). Teacher subsystem PR gate flaky-to-broken.

Honourable mentions: `pearl-news-full-qa.yml` (0/30), `max-quality-catalog.yml` (0/30), `translate-bestseller-atoms.yml` (0/30), `audiobook-regression.yml` (last green never within window).

---

## C. Scheduled pipelines health (28 cron-driven workflows)

| cron | filename | last_status | last_date | 14d_pass | health |
|---|---|---|---|---|---|
| `*/30 * * * *` | `pearl-star-health.yml` | failure | 2026-04-29 | 0/30 | BROKEN |
| `0 * * * *` | `ml-loop-continuous.yml` | success | 2026-04-29 | 29/30 | HEALTHY |
| `0 */6 * * *` | `manga-operator-setup-verify.yml` | failure | 2026-04-29 | 0/30 | BROKEN |
| `0 */6 * * *` | `operator-setup-verify.yml` | failure | 2026-04-29 | 0/30 | BROKEN |
| `0 10 * * 1` | `ml-loop-weekly-recalibration.yml` | success | 2026-04-27 | 2/2 | HEALTHY |
| `0 10 * * 1` | `podcast-weekly.yml` | failure | 2026-04-27 | 0/2 | BROKEN |
| `0 10 * * MON` | `branch-hygiene-sweep.yml` | failure | 2026-04-29 | 0/30 | BROKEN |
| `0 12 * * 1` | `research_feeds_ingest.yml` | success | 2026-04-27 | 2/2 | HEALTHY |
| `0 14 * * *` | `video-daily-publish.yml` | success | 2026-04-28 | 14/14 | HEALTHY |
| `0 14 * * 1` | `weekly-manga-rollout.yml` | failure | 2026-04-27 | 0/2 | FLAKY |
| `0 2 * * 0` | `translate-atoms-qwen-matrix.yml` | failure | 2026-04-26 | 0/2 | BROKEN |
| `0 22 * * *` | `pearl-news-daily.yml` | success | 2026-04-29 | 16/28 | HEALTHY (~57%) |
| `0 3 * * *` | `nightly-regression.yml` | success | 2026-04-29 | 13/13 | HEALTHY |
| `0 4 * * 1` | `ei-v2-gates.yml` | success | 2026-04-29 | 30/30 | HEALTHY |
| `0 6 * * 0` | `release-gates.yml` | success | 2026-04-29 | 25/30 | HEALTHY |
| `0 6 * * 0` | `weekly-book-rollout.yml` | success | 2026-04-26 | 2/2 | HEALTHY |
| `0 6 * * 1` | `catalog-book-pipeline.yml` | cancelled | 2026-04-27 | 0/0 | FLAKY |
| `0 6 * * 1` | `simulation-10k.yml` | failure | 2026-04-27 | 0/2 | BROKEN |
| `0 7 * * *` | `production-observability.yml` | failure | 2026-04-29 | 2/14 | BROKEN |
| `0 8 * * *` | `manga-bubble-regression.yml` | success | 2026-04-29 | 10/10 | HEALTHY |
| `0 8 * * *` | `marketing-briefs-and-proposals.yml` | queued | 2026-04-29 | 0/1 | FLAKY |
| `0 8 * * *` | `ml-loop-daily-promotion.yml` | success | 2026-04-29 | 14/14 | HEALTHY |
| `0 8 * * 1` | `weekly-pipeline.yml` | success | 2026-04-27 | 2/2 | HEALTHY |
| `0 9 * * 1` | `ml-editorial-weekly.yml` | success | 2026-04-27 | 2/2 | HEALTHY |
| `0 9 * * 1` | `remote-commit-review.yml` | success | 2026-04-27 | 2/2 | HEALTHY |
| `0 9 * * 5` | `llm-callers-audit.yml` | success | 2026-04-29 | 30/30 | HEALTHY |
| `15 * * * *` | `marketing_continuous.yml` | queued | 2026-04-29 | 0/1 | FLAKY |
| `17 3 * * *` | `cleanup-stale-worktrees.yml` | success | 2026-04-29 | 5/5 | HEALTHY |

**Findings:**
- **8 of 28 cron workflows are BROKEN** (29%): pearl-star-health, manga-operator-setup-verify, operator-setup-verify, branch-hygiene-sweep, podcast-weekly, simulation-10k, production-observability, translate-atoms-qwen-matrix.
- **`pearl-star-health.yml` is the worst offender** — `*/30 * * * *` × 0/30 = 30 false alerts in 14d (subset; actual is ~672). Recommend: stand it down OR fix the health probe target.
- **3 cron workflows stuck in `queued`** today: `marketing-briefs-and-proposals.yml`, `marketing_continuous.yml`. Either runner backlog or labeled-runner not online.
- **Healthy cron set (20 workflows)** carries the daily/weekly content + ML pipelines — pearl-news-daily (16/28 ≈ 57% — should investigate), ml-loop-* (all 100%), nightly-regression (13/13), release-gates (25/30), ei-v2-gates (30/30), llm-callers-audit (30/30).

---

## D. Branch protection drift — **THE P0 FINDING**

```
$ gh api repos/:owner/:repo/branches/main/protection
{"message":"Branch not protected","documentation_url":"...","status":"404"}
```

**No required checks. No required reviewers. No PR-required-to-merge enforcement.** Anyone with push permission can `git push origin main` directly, and PRs can be merged with red CI.

### Workflows that LOOK like they should gate main but currently gate nothing

The following 23 workflows are PR-triggered or main-conditional, but none are required because protection is OFF:

| filename | trigger | currently gates main? |
|---|---|---|
| `audiobook-regression.yml` | pull_request+push | NO (BROKEN, would block) |
| `auto-merge-bot-fix.yml` | pull_request | NO |
| `blocked-platforms.yml` | pull_request+push | NO |
| `brand-guards.yml` | pull_request+push | NO |
| `change-impact.yml` | pull_request | NO (BROKEN, would block; gates_main flag set) |
| `core-tests.yml` | pull_request+push | NO |
| `docs-ci.yml` | pull_request+push | NO |
| `ei-v2-gates.yml` | pull_request+push+schedule | NO |
| `github-governance-check.yml` | pull_request+push | NO |
| `llm-callers-audit.yml` | pull_request+schedule | NO |
| `llm-policy-enforcement.yml` | pull_request | NO |
| `locale-gate.yml` | pull_request+push | NO (gates_main flag set) |
| `manga-catalog-plan-regen-check.yml` | pull_request+push | NO (gates_main flag set) |
| `manga-smoke-test.yml` | pull_request | NO |
| `manga-workflows-yml-validate.yml` | pull_request | NO |
| `marketing-config-gate.yml` | pull_request+push | NO (gates_main flag set) |
| `no-binary-blobs.yml` | pull_request | NO (gates_main flag set) |
| `pr-governance-review.yml` | pull_request | NO |
| `regression-museum-gate.yml` | pull_request | NO |
| `release-gates.yml` | pull_request+push+schedule | NO (gates_main flag set) |
| `server-ci.yml` | pull_request+push | NO |
| `teacher-gates.yml` | pull_request+push | NO (BROKEN, 4/19 in 14d) |
| `variant-coverage-gate.yml` | pull_request | NO |

Per `docs/BRANCH_PROTECTION_REQUIREMENTS.md` and `docs/GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md` (PR #245 deleted 20,006 files because protection was off), **this is a known governance incident class**. CLAUDE.md rule #0 still holds via human discipline only — there is no machine enforcement.

### Recommended required checks (when protection is restored)

Based on `scripts/git/pre_merge_check.sh` + `scripts/ci/pr_governance_review.py`, the minimum required-on-main set should be:

1. `pr-governance-review.yml` (mass deletion blocker, PR size, scope)
2. `github-governance-check.yml`
3. `llm-policy-enforcement.yml` (paid-API ban, per CLAUDE.md)
4. `llm-callers-audit.yml` (paid-API ban scan)
5. `core-tests.yml`
6. `no-binary-blobs.yml`
7. `change-impact.yml` (currently BROKEN — must fix before requiring)
8. `release-gates.yml`
9. `locale-gate.yml`
10. `marketing-config-gate.yml`

`teacher-gates.yml` is also conceptually a gate but is BROKEN (14d 4/19) — fix before requiring.

---

## E. Dead workflows (>30d no run, or never run)

| filename | trigger | last_run | recommendation |
|---|---|---|---|
| `full-catalog-cli-en-us.yml` | workflow_dispatch | 2026-03-23 success | DELETE if superseded by `catalog-book-pipeline.yml` / `weekly-book-rollout.yml`; otherwise revive |
| `manga-backend-flip.yml` | workflow_dispatch | never | DELETE or document trigger plan |
| `manga-character-sheet-build.yml` | workflow_dispatch | never | Likely PRE-rollout helper — DELETE or document |
| `manga-fonts-acquire.yml` | workflow_dispatch | never | One-shot bootstrap — DELETE if fonts already acquired |
| `manga-image-bank-build.yml` | workflow_dispatch | never | DELETE or fold into pipeline |
| `manga-pipeline.yml` | workflow_dispatch | never | Authority unclear vs `weekly-manga-rollout.yml` — DELETE one |
| `manga-quality-analysis.yml` | workflow_dispatch | never | DELETE |
| `manga-quality-forensic-analysis.yml` | workflow_dispatch | never | Uses `secrets.CLAUDE_API_KEY` — VIOLATES CLAUDE.md tier policy. **DELETE** |
| `manga-series-pitch.yml` | workflow_dispatch | never | Uses `secrets.CLAUDE_API_KEY` — VIOLATES CLAUDE.md tier policy. **DELETE** |
| `manga-stash-reminder.yml` | workflow_dispatch | never | DELETE |
| `pearl-news-assemble.yml` | workflow_dispatch+workflow_call | never | Subroutine of `pearl-news-daily.yml`? — verify reuse, else DELETE |
| `pearl-news-fill-qwen.yml` | workflow_dispatch+workflow_call | never | Same as above |
| `research-pipeline-run.yml` | workflow_dispatch | never | DELETE or rewire to schedule |

**Drift risk:** 13 dead workflows × surface area for token / secret reference drift. Two manga workflows (`manga-quality-forensic-analysis.yml`, `manga-series-pitch.yml`) reference `secrets.CLAUDE_API_KEY` which is BANNED per CLAUDE.md tier policy — these violate policy on paper even though they never run.

---

## F. LLM / TTS policy enforcement health

### `llm-policy-enforcement.yml` — HEALTHY
- Trigger: `pull_request + workflow_dispatch`
- Last 5 runs (all PR): 2026-04-29 success ×5
- 14d pass: **30/30 = 100%**
- Status: Working but ADVISORY only (not required-on-main).

### `llm-callers-audit.yml` — HEALTHY
- Trigger: `pull_request + schedule(0 9 * * 5) + workflow_dispatch`
- Last 5 runs (all PR): 2026-04-29 success ×5
- 14d pass: **30/30 = 100%**
- Weekly Friday 09:00 UTC schedule firing.
- Status: Working, ADVISORY only.

### `pr-governance-review.yml` — HEALTHY
- Trigger: `pull_request`
- 14d pass: **30/30**
- Mass-deletion + PR-size + subsystem-scope blocker. Working, ADVISORY only.

### `github-governance-check.yml` — HEALTHY
- Trigger: `pull_request + push`
- 14d pass: **30/30**
- Working, ADVISORY only.

**Risk:** All four governance gates are passing 100% but none are enforced on main. PR #245-class incident remains possible.

### Banned-API references found in workflow `env:` blocks (cross-check vs CLAUDE.md tier policy)

```
$ grep -rn "secrets\.CLAUDE_API_KEY\|secrets\.ANTHROPIC_API_KEY" .github/workflows/
.github/workflows/manga-series-pitch.yml:35:    CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
.github/workflows/weekly-manga-rollout.yml:54-75: CLAUDE_API_KEY (×2)
.github/workflows/manga-smoke-test.yml: (CLAUDE_API_KEY-adjacent)
.github/workflows/manga-quality-forensic-analysis.yml:28,65: CLAUDE_API_KEY (×2)
.github/workflows/manga-pipeline.yml: CLAUDE_API_KEY-adjacent
```

5 workflows reference `secrets.CLAUDE_API_KEY`, which CLAUDE.md flags as BANNED. The `llm-callers-audit.yml` policy script may be allow-listing these (need to verify against `scripts/ci/audit_llm_callers.py`). 4 of these 5 are DEAD/never-run, but the secret references themselves drift.

---

## G. Phase tag rollup

Mapping by subsystem (best-guess from filename) of overall health.

| subsystem | total | HEALTHY | BROKEN | FLAKY | DEAD |
|---|---|---|---|---|---|
| manga | 16 | 5 | 1 | 1 | 9 |
| catalog | 7 | 4 | 2 | 1 | 1 (full-catalog-cli-en-us) |
| ops | 8 | 3 | 3 | 1 | 0 |
| pearl-news | 4 | 1 | 1 | 0 | 2 |
| ml-loop | 4 | 4 | 0 | 0 | 0 |
| llm-policy | 2 | 2 | 0 | 0 | 0 |
| governance | 2 | 2 | 0 | 0 | 0 |
| policy | 5 | 4 | 1 | 0 | 0 |
| translate | 3 | 0 | 2 | 1 | 0 |
| regression | 3 | 2 | 0 | 1 | 0 |
| marketing | 3 | 1 | 0 | 2 | 0 |
| media | 3 | 2 | 1 | 0 | 0 |
| git-ops | 2 | 1 | 1 | 0 | 0 |
| core | 2 | 2 | 0 | 0 | 0 |
| teacher | 1 | 0 | 1 | 0 | 0 |
| simulation | 1 | 0 | 1 | 0 | 0 |
| ei | 1 | 1 | 0 | 0 | 0 |
| docs | 1 | 1 | 0 | 0 | 0 |
| release | 1 | 1 | 0 | 0 | 0 |
| research | 2 | 1 | 0 | 0 | 1 |
| i18n | 1 | 1 | 0 | 0 | 0 |
| misc | 3 | 0 | 0 | 3 | 0 |

**Worst-health subsystems:** manga (9 dead of 16 = 56%), translate (2/3 broken), ops (3/8 broken), pearl-news (2/4 dead).
**Cleanest subsystems:** ml-loop (4/4 healthy), llm-policy + governance (4/4 healthy), core (2/2 healthy).

---

## H. Secrets / env-var drift

Cross-check of `secrets.X` references in `.github/workflows/*.yml` vs `scripts/ci/integration_env_registry.py`:

**Used by workflows but NOT in registry (potential drift):**
- `secrets.CF_R` — looks like a typo (probably meant `CF_R2_*`); **investigate**
- `secrets.CLAUDE_API_KEY` — **BANNED per CLAUDE.md**, present in 5 workflows
- `secrets.R` — typo (probably `secrets.R2_*`); **investigate**
- `secrets.SENDGRID_API_KEY` — used in `weekly-manga-rollout.yml`, `manga-smoke-test.yml`; missing from registry. Either add to registry or remove from workflows.

**In registry and used:** 18 secrets — `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, `COMFYUI_URL`, `COSYVOICE_URL`, `DASHSCOPE_API_KEY`, `ELEVENLABS_API_KEY`, `GEMMA_BASE_URL`, `GITHUB_TOKEN`, `PEARL_STAR_IP`, `QWEN_API_KEY`, `QWEN_BASE_URL`, `QWEN_MODEL`, `RUNCOMFY_API_KEY`, `RUNCOMFY_TOKEN`, `TOGETHER_API_KEY`, `WORDPRESS_APP_PASSWORD`, `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, `ANTHROPIC_API_KEY` (banned but tracked).

---

## I. Top 5 P0 / P1 CI fixes (recommended ordering)

1. **P0 — Restore branch protection on `main`** with required checks (governance + LLM policy + core-tests + no-binary-blobs + release-gates + locale-gate + marketing-config-gate). Without this, the 38 healthy workflows are advisory ornaments. Per `docs/BRANCH_PROTECTION_REQUIREMENTS.md`.
2. **P0 — Fix or silence `pearl-star-health.yml`** (cron `*/30 * * * *`, 0/30 in 14d). Generates ~672 false alerts every 14 days; either repair the probe or remove the schedule.
3. **P0 — Fix `change-impact.yml`** (PR-triggered, gates_main flag set, 0/30 in 14d). It's the canonical impact analyzer and currently red-on-every-PR — once protection is restored it would block ALL merges.
4. **P1 — Fix `operator-setup-verify.yml` + `manga-operator-setup-verify.yml`** (both cron `0 */6 * * *`, both 0/30). Operator-setup signal is the hourly "is this repo healthy" indicator. Both broken since at least 2026-04-15.
5. **P1 — Triage manga workflow graveyard** (9 of 16 manga workflows DEAD/never-run). DELETE pruning needed for `manga-quality-forensic-analysis.yml`, `manga-series-pitch.yml` (BANNED secret refs); audit which of the rest are still authoritative versus replaced by `weekly-manga-rollout.yml`. Also covers the `secrets.CF_R` / `secrets.R` typo risk.

P2 follow-ups:
- Fix `branch-hygiene-sweep.yml` (Pearl_GitHub-owned).
- Fix `production-observability.yml` (cascades into `production-alerts.yml` which is 1/30 skipped).
- Fix `simulation-10k.yml` and `translate-atoms-qwen-matrix.yml` (chronic Monday/Sunday cron failures).
- Investigate `pearl-news-daily.yml` 16/28 (~57%) — half the daily news cycle is failing.
- Resolve `marketing_continuous.yml` + `marketing-briefs-and-proposals.yml` queued status (runner availability?).
- Reconcile `secrets.SENDGRID_API_KEY` with `integration_env_registry.py`.
- Audit and remove `secrets.CLAUDE_API_KEY` references (CLAUDE.md tier policy violation).

---

## Appendix — Method notes

- All run-history claims sourced from `gh run list --workflow=<file> --limit 30 --json conclusion,createdAt,status,event` executed 2026-04-29.
- Pass rate = `success / (total - cancelled)` over the 14-day window ending 2026-04-29.
- Health classifier:
  - `BROKEN` = last 3 conclusions all `failure`.
  - `FLAKY` = last conclusion is `failure` / `cancelled` / `skipped` / `queued` but at least one `success` in last 5.
  - `DEAD` = never_run, OR last run > 30 days ago and no schedule.
  - `HEALTHY` = last conclusion `success`.
- `gates_main` heuristic: `if: github.ref == 'refs/heads/main'` OR `branches: [main]` filter present. **Does NOT mean required check** — see Section D.
- 0 workflows hit `gh` rate limits during this audit.
