# Qwen API Unification Completion Spec

**Purpose:** Complete the remaining retirement of LM Studio, Qwen-Agent operational paths, and the legacy audiobook comparator subsystem so the active Phoenix system uses only repo-local workflows plus Qwen-compatible API secrets.

**Status:** Lane implemented on convergence branch; use this file as the audit record. `ws_qwen_api_unification_20260328` should read `completed` or `preserved` in PM ledgers after verification.

**Primary owner:** Pearl_GitHub with Pearl_PM coordination.

**Base state requirement:** Start from the current convergence snapshot that already contains the first retirement tranche. Until that work lands on `main`, do **not** start this lane from `origin/main` and re-do the earlier deletions.

**Read before work:**
- `docs/ONBOARDING_START_HERE.md`
- `docs/SESSION_UNITY_PROTOCOL.md`
- `docs/DOCS_INDEX.md`
- `docs/GITHUB_OPERATIONS_FRAMEWORK.md`
- `docs/GITHUB_NO_FAILURE_FRAMEWORK.md`
- `docs/PEARL_PM_STATE.md`
- `artifacts/coordination/ACTIVE_PROJECTS.tsv`
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`
- this file

---

## 1. Goal

After this spec is completed:

1. Active Phoenix workflows, scripts, dashboards, docs, and operator UI use the repo-local Phoenix path plus `QWEN_BASE_URL`, `QWEN_API_KEY`, and `QWEN_MODEL`.
2. The legacy audiobook comparator subsystem is removed from the active system.
3. Qwen-Agent and LM Studio remain only in archival/history locations, not in active operator code or current authority docs.
4. Pearl_PM can point to one authority file for the rest of this lane.

---

## 2. Already Complete

The following work is already done and must **not** be re-done unless verification shows drift:

### Active workflow and authority cleanup

- `.github/workflows/audiobook-regression.yml` deleted
- `docs/AUDIOBOOK_PIPELINE_SPEC.md` deleted
- `docs/GO_LIVE_FINAL_CHECKLIST.md` deleted
- `docs/PEARL_NEWS_OPTION_B_RUNBOOK.md` deleted
- `docs/audiobook_operator_runbook.md` deleted

### Self-hosted Qwen policy already promoted

These active workflows already use the Phoenix-only Qwen API direction:

- `.github/workflows/catalog-book-pipeline.yml`
- `.github/workflows/marketing-briefs-and-proposals.yml`
- `.github/workflows/marketing_continuous.yml`
- `.github/workflows/max-quality-catalog.yml`
- `.github/workflows/pearl-news-fill-qwen.yml`

### Active docs already rewritten

- `docs/GITHUB_OPERATIONS_FRAMEWORK.md`
- `docs/GITHUB_NO_FAILURE_FRAMEWORK.md`
- `docs/PEARL_NEWS_GITHUB_SCHEDULING.md`
- `docs/TRANSLATE_QWEN_PIPELINE_CLI.md`
- `docs/OWNERSHIP_MATRIX.md`
- `docs/PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md`
- `docs/PEARL_NEWS_HARDENING_100_PERCENT.md`
- `docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md`
- `docs/PRODUCTION_100_PLAN.md`
- `docs/PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md`
- `docs/FULL_REPO_TEST_SUITE_PLAN.md`
- `scripts/dashboard/github_tab.py`
- `scripts/integrations/open_wordpress_setup.sh`
- `scripts/ci/README.md`

If any of the files above still show legacy wording, patch them in place. Do not create replacement duplicates.

---

## 3. Definition Of Done

This lane is only complete when all of the following are true:

1. No active system file depends on the legacy audiobook comparator subsystem.
2. No active system file instructs operators to run work from `Qwen-Agent`.
3. No active system file treats LM Studio as the production runtime path.
4. `dashboard.py` and PhoenixControl no longer expose the retired manual-review path.
5. `config/governance/github_repos_registry.yaml` describes only the active canonical repo model.
6. `docs/DOCS_INDEX.md` no longer inventories the retired audiobook subsystem as an active section.
7. Remaining references to Qwen-Agent or LM Studio exist only inside explicitly archival paths.

---

## 4. Allowed Residual Reference Zones

The following locations may keep historical references if needed:

- `salvage/**`
- `old_chat_specs/**`
- `de_chats_to_analyze/**`
- `phoenix_workspace_archive_2026_03_28/**`
- archived artifacts under `artifacts/**` that are not part of live operator guidance
- `.gitmodules` (submodule pin only; removing the historical submodule is follow-up git hygiene, not operator runbook text)

Outside those zones, legacy references must be removed, rewritten, or archived.

---

## 5. Required Work

### A. Delete the remaining legacy audiobook implementation layer

Delete these active files and folders if they still exist:

- `scripts/audiobook_script/run_comparator_loop.py`
- `scripts/audiobook_script/run_regression.py`
- `scripts/audiobook_script/run_staging.sh`
- `scripts/release/audiobook_rollback.sh`
- `config/audiobook_script/`
- `prompts/audiobook/`
- `schemas/comparator_result_v2.schema.json`

Rules:

- Delete the active files; do not leave them indexed as live system assets.
- If a historical copy is worth preserving, preserve it only in archival paths, not in the active tree.
- Do not delete normal audiobook business/content docs that are unrelated to this retired comparator subsystem.

### B. Remove the PhoenixControl manual-review feature

Retire the legacy UI surface tied to the deleted subsystem:

- delete `PhoenixControl/Views/ManualReviewView.swift`
- remove `manualReview` from `PhoenixControl/Views/ContentView.swift`
- remove the tab title, icon, and detail-route for the manual review screen
- verify `PhoenixControl/PhoenixControl.xcodeproj/project.pbxproj` does not reference the deleted file if a reference exists

Acceptance detail:

- PhoenixControl must still compile structurally after the tab removal
- no `manualReview` case remains in active Swift UI routing
- no UI help text points to `artifacts/audiobook/manual_review_queue.json`

### C. Rewrite `dashboard.py` away from Qwen-Agent and manual-review queue assumptions

The Pearl News tab in `dashboard.py` still points at:

- `Qwen-Agent/artifacts/pearl_news/drafts`
- `manual_review_queue.json`
- a command that tells the operator to `cd ~/phoenix_omega/Qwen-Agent`

Required outcome:

- use Phoenix repo-local Pearl News artifact locations only
- remove or replace the manual-review panel so it reflects current active gates/artifacts
- show an operator command that runs from the Phoenix repo itself

If the current repo no longer produces a review queue artifact, remove that panel entirely rather than preserving a dead path.

### D. Remove the retired second-repo model from live governance/config

Update:

- `config/governance/github_repos_registry.yaml`

Required outcome:

- Phoenix is the only active canonical repo described for this runtime model
- remove the `Qwen-Agent` repo entry unless there is a current, active, separately governed reason to keep it
- keep the file consistent with `docs/GITHUB_OPERATIONS_FRAMEWORK.md`

### E. Clean the active docs and inventory

Update the remaining live docs so they stop teaching or indexing the retired path.

Must-fix files:

- `docs/DOCS_INDEX.md`
- `docs/PEARL_PRIME_100_PERCENT_DEV_PLAN.md`
- `PhoenixControl/README.md`
- `CONTENT_PRODUCTION_PLAN_13K_BOOKS.md`

Likely historical docs that must either be rewritten or archived out of active guidance:

- `docs/research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md`
- `docs/RUNTIME_CONSOLIDATION_HARVEST_PLAN_2026_03_22.md`

`docs/DOCS_INDEX.md` specifically must:

1. remove the active “Qwen-Only Audiobook Pipeline” section
2. remove live inventory rows for deleted comparator scripts/config/prompts/schema/manual-review UI
3. stop treating retirement notes as active-system inventory
4. add or keep this spec discoverable as the authority for the remaining cleanup lane

If a note is only valuable as history, move it into an archival section or archival file rather than keeping it as active inventory.

### F. Update PM coordination truth

When the cleanup is complete, update:

- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`
- `artifacts/coordination/ACTIVE_PROJECTS.tsv`

Required outcome:

- `ws_qwen_api_unification_20260328` moves from `active` to `preserved` or `completed`
- blockers mention only real remaining work, not already-finished work
- the authority path includes this spec while the lane is active

---

## 6. Non-Goals

Do **not** do any of the following as part of this lane:

- do not revert unrelated salvage or state-convergence work
- do not scrub every historical use of the word `audiobook` from the repo
- do not delete archival folders just to get a cleaner grep
- do not introduce a new replacement subsystem unless the active docs already require one
- do not split work into a new duplicate spec when this file can be updated in place

---

## 7. Required Verification

Run these checks after the implementation changes:

### Core validation

```bash
PYTHONPATH=. python3 scripts/ci/check_docs_governance.py
python3 -m py_compile dashboard.py scripts/dashboard/github_tab.py
```

If Python files outside those paths are edited, include them in `py_compile`.

### Legacy-reference gate

Run:

```bash
rg -n "Qwen-Agent|LM Studio|run_comparator_loop.py|run_regression.py|run_staging.sh|audiobook_rollback.sh|config/audiobook_script|prompts/audiobook|comparator_result_v2|manual_review_queue.json|ManualReviewView|manualReview" . \
  -g '!salvage/**' \
  -g '!old_chat_specs/**' \
  -g '!de_chats_to_analyze/**' \
  -g '!phoenix_workspace_archive_2026_03_28/**' \
  -g '!artifacts/**' \
  -g '!docs/QWEN_API_UNIFICATION_COMPLETION_SPEC.md' \
  -g '!.gitmodules'
```

Desired result:

- zero hits in active operator code, governance, dashboards, workflows, configs, and docs
- if any hit remains, it must be intentionally justified in the closeout and either be moved to archive or patched before sign-off

### PhoenixControl validation

If the Swift UI is touched:

- verify no `manualReview` route remains in `PhoenixControl/Views/ContentView.swift`
- verify `ManualReviewView.swift` is deleted
- verify the Xcode project does not retain a stale file reference if one existed

### Governance consistency

Verify the repo registry and GitHub framework agree:

- `config/governance/github_repos_registry.yaml`
- `docs/GITHUB_OPERATIONS_FRAMEWORK.md`

They must describe the same canonical repo model.

---

## 8. Closeout Evidence

The dev must provide all of the following in closeout:

1. deleted-file list
2. rewritten-file list
3. before/after grep summary for the legacy-reference gate
4. docs governance output
5. compile output for touched Python files
6. note confirming PhoenixControl manual-review removal
7. updated workstream/project row summary

Use a `CLOSEOUT_RECEIPT` that names the exact files changed and the exact verification commands run.

---

## 9. Recommended Execution Order

1. remove the legacy implementation files
2. remove the PhoenixControl manual-review tab
3. rewrite `dashboard.py`
4. clean governance/config and live docs
5. run verification
6. update PM ledgers

This order reduces false-positive references during cleanup and keeps the verification gate simple.
