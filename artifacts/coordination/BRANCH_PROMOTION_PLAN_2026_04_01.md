# Branch Promotion Plan — 2026-04-01 (Workstream-Resolved)

Owner: Pearl_GitHub
Input: `BRANCH_INVENTORY_2026_04_01.tsv`, `BRANCH_TRIAGE_2026_04_01.md`
Authority: `docs/GITHUB_OPERATIONS_FRAMEWORK.md`, `docs/PEARL_ARCHITECT_STATE.md`

---

## 1. Per-Workstream Promotion Queue (from codex/state-convergence-20260328)

All promotions from state-convergence use path-scoped cherry-pick extraction onto a fresh `agent/*` branch from `origin/main`. The state-convergence branch is 87 behind main with 42 commits — direct merge is not viable.

**Extraction procedure (once per workstream slice):**
```bash
git fetch origin
git checkout -b agent/<ws-name>-promotion origin/main
git checkout codex/state-convergence-20260328 -- <path1> <path2> ...
git add <paths>
git commit -m "feat(<scope>): promote <ws-name> from state-convergence"
PYTHONPATH=. python3 scripts/git/push_guard.py
scripts/ci/preflight_push.sh
bash scripts/git/health_check.sh
git push -u origin agent/<ws-name>-promotion
gh pr create ...
```

### WS-1: ws_pearl_int_recovery (preserved) — LOW RISK

**Workstream:** ws_pearl_int_recovery_20260328
**Source:** codex/state-convergence-20260328 (original base_ref: codex/main-salvage-20260323-153043)
**Files (26):** All NEW, nothing on main to conflict with.
- `skills/pearl-int/` (5 files)
- `docs/TREND_FEED_INTEGRATION_STRATEGY.md`
- `config/trend_keywords/` (5 files)
- `scripts/feeds/` (4 files: budget_guard.py, check_trends.py, daily_scrape_runner.py, score_trends.py)
- `artifacts/feeds/` (9 files)
- `artifacts/governance/session_logs/` (2 files)
**Strategy:** `git checkout codex/state-convergence-20260328 -- <all 26 paths>`
**Risk:** Low — all new files, no existing code modified
**Validation:** `python -c "import ast; ast.parse(open(f).read())" for each .py`
**Suggested PR:** "feat(pearl-int): promote Pearl_Int skill + trend pipeline from state-convergence"

### WS-2: ws_pen_name_recovery (preserved) — LOW RISK, 3 unpromoted files

**Workstream:** ws_pen_name_recovery_20260328
**Source:** codex/state-convergence-20260328 (original base_ref: agent/manga-sdf-revision-workspace)
**Unpromoted files (3):**
- `config/authoring/pen_name_teacher_profiles_full.json` (48982 lines — LARGE)
- `docs/PEN_NAME_AUTHOR_SYSTEM.md` (228 lines)
- `scripts/verify_pen_name_coverage.py` (112 lines)
**Already on main (skip):** pen_name_teacher_profiles.yaml, brand_registry.yaml, brand_author_assignments.yaml, brand_narrator_assignments.yaml
**Strategy:** `git checkout codex/state-convergence-20260328 -- <3 unpromoted paths>`
**Risk:** Low — new files only. Large JSON file may exceed push-guard max_total_mb (25MB) — check size.
**Validation:** `python -c "import json; json.load(open('config/authoring/pen_name_teacher_profiles_full.json'))"`; `python -c "import ast; ast.parse(open('scripts/verify_pen_name_coverage.py').read())"`
**Suggested PR:** "feat(authoring): promote pen-name system docs + full profiles JSON"

### WS-3: ws_recommender_promotion (preserved) — MEDIUM RISK

**Workstream:** ws_recommender_promotion_20260328
**Source:** codex/state-convergence-20260328
**Files (24, +1175):** All NEW except `artifacts/release/rollback_smoke_evidence.json` and `tests/test_pearl_prime_release_evidence.py` (exist on main).
**Strategy:** Extract all 22 new files + diff the 2 existing files to determine if updates are needed
**Risk:** Medium — introduces new `phoenix_recommender` package. Must verify against Arc-First that recommendation engine is not a drift pattern.
**Pre-review question:** Does `phoenix_recommender` exist as a governed subsystem in DOCS_INDEX or OWNERSHIP_MATRIX? If not, this may need architectural approval before promotion.
**Validation:** `python -m pytest tests/test_phoenix_recommender.py tests/test_voice_audition_contract.py tests/test_write_workflow_run_manifest.py`
**Suggested PR:** "feat(recommender): promote phoenix_recommender + voice audition + release tooling"

### WS-4: ws_experience_recovery (preserved) — HIGH RISK

**Workstream:** ws_experience_recovery_20260328
**Source:** codex/state-convergence-20260328 (original base_ref: codex/runtime-consolidation)
**Files (20, +4163 -128):** Mix of new files and modifications to existing production code.
**New files (11):** spec, configs, resolvers, QA gates, test
**Modified existing files (9):** `generator.py`, `keyword_bank.py`, `check_release_wave.py`, `check_wave_density.py`, `run_prepublish_gates.py`, `run_pipeline.py`, `subtitle_patterns.yaml`, `series_templates.yaml`
**REVIEW-REQUIRED:** `specs/EXPERIENCE_LAYER_ANTI_SPAM_SPEC.md` is an authority doc (per hard constraints)
**Risk:** HIGH — modifies production pipeline code (`run_pipeline.py`, naming engine), adds new spec. Must be reviewed against Arc-First.
**Strategy:** Extract all new files first. For modified files, diff state-convergence version against current main to determine if changes are additive or conflicting.
**Suggested PR (split into 2):**
  - PR-A: "feat(experience): add experience layer spec, configs, and QA gates" (new files only)
  - PR-B: "feat(experience): wire experience resolver into pipeline and naming" (modifications)

### WS-5: ws_github_prod_readiness (preserved) — HIGH RISK, STALENESS CONCERN

**Workstream:** ws_github_prod_readiness_20260328
**Source:** codex/state-convergence-20260328
**Files (9):** All exist on main but DIFFER. Branch is 87 commits behind.
**Critical concern:** Main has received 87 commits since this branch diverged. The workflow and doc modifications may be STALE — main may have already incorporated equivalent or better changes via other PRs.
**Required before promotion:** File-by-file diff of state-convergence version vs current main for each of the 9 files. If main is already ahead on a file, skip it.
**REVIEW-REQUIRED:** `.github/workflows/release-gates.yml` is branch-protection-required
**Risk:** HIGH — potential regression if state-convergence has older workflow versions
**Strategy:** DO NOT blindly checkout. Diff each file individually. Only promote files where state-convergence has genuinely newer/better content.
**Suggested PR:** "fix(github): promote prod-readiness hardening slices (post-staleness review)"

### WS-6: ws_qwen_api_unification (completed) — HIGH RISK, STALENESS CONCERN

**Workstream:** ws_qwen_api_unification_20260328
**Source:** codex/state-convergence-20260328
**Files (11):** 1 new (`QWEN_API_UNIFICATION_COMPLETION_SPEC.md`), 10 modified
**Same staleness concern as WS-5.** The completion spec is the key new artifact. The code modifications may be stale.
**Strategy:** Promote the completion spec doc. For the 10 modified files, diff against current main before deciding.
**Suggested PR:** "docs(qwen-api): promote unification completion spec + verified code updates"

### WS-7: Unregistered — Writers Bible v3.2 + slot-resolver — MEDIUM RISK

**Source:** codex/state-convergence-20260328, commits `370a93fe` and `742c16a9`
**New files (37):** `artifacts/writers_bible_v32/` (30 YAMLs), `config/marketing/v32_*.yaml` (7 files) — none on main
**Modified file (1):** `phoenix_v4/qa/bestseller_editor.py` — exists on main, DIFFERS
**Modified file (1):** `phoenix_v4/planning/slot_resolver.py` — exists on main, DIFFERS (thesis-aware ranking)
**Ordering note:** `slot_resolver.py` also modified by `agent/adi-da-story-universal-wildcard` — promote this first
**Strategy:** New files via checkout, modified files via individual review
**Suggested PR:** "feat(v32): Writers Bible v3.2 configs + bestseller editor + thesis ranking"

---

## 2. Standalone Branch Promotions

### Merge A: agent/docs-manga-landmarks — LOWEST RISK

- **Strategy:** cherry-pick `1d703e7a`
- **Files (1):** `docs/MANGA_IMPLEMENTATION_OUTLINE.md`
- **Risk:** Minimal

### Merge B: agent/adi-da-story-universal-wildcard — LOW RISK

- **Strategy:** cherry-pick `a5c2b9d6`
- **Files (3):** pool_index.py, slot_resolver.py, test
- **Ordering:** After WS-7 slot_resolver promotion (or verify compatibility)
- **Risk:** Low — has test

### Merge C: agent/ci-manga-chapter-smoke — MEDIUM RISK (REVIEW)

- **Strategy:** cherry-pick `3e11a3c8`
- **Files (2):** core-tests.yml, smoke script
- **Risk:** Modifies branch-protection-required workflow

### Merge D: agent/manga-sdf-stub-normalization — MEDIUM RISK (REVIEW)

- **Strategy:** cherry-pick `833f85ef`
- **Files (5):** SDF stub code + schema
- **Risk:** No tests, new code paths

---

## 3. Suggested Merge Order (dependency-aware)

1. **Merge A** — `agent/docs-manga-landmarks` (zero risk, docs-only)
2. **WS-1** — Pearl_Int recovery (all new files, no conflicts)
3. **WS-2** — Pen-name recovery (3 new files, no conflicts)
4. **WS-7** — Writers Bible v3.2 + slot-resolver (new files + 2 modified, review needed)
5. **Merge B** — `agent/adi-da-story-universal-wildcard` (after WS-7 for slot_resolver ordering)
6. **WS-3** — Recommender promotion (new package, architectural review needed)
7. **WS-4** — Experience recovery (high risk, pipeline modifications, split into 2 PRs)
8. **Merge C** — `agent/ci-manga-chapter-smoke` (workflow review needed)
9. **Merge D** — `agent/manga-sdf-stub-normalization` (code review needed)
10. **WS-5** — GitHub prod-readiness (staleness review required per-file)
11. **WS-6** — Qwen API unification (staleness review required per-file)

---

## 4. Archive Queue

### Remote deletion (1)
- `origin/agent/cjk6-translation-workflow` — PR #143 merged

### Local SUPERSEDED (8 branches, safe to delete)
| Branch | Evidence |
|--------|----------|
| agent/cjk6-translation-workflow | PR #143 merged |
| agent/renderer-validation | PR #141 merged |
| agent/cjk6-translation-pipeline | PR #142 merged |
| agent/story-atoms-full | PR #140 merged |
| agent/pearl-prime-recovery-docs | PR #75 merged |
| agent/onboard-adi-da | PR #97 merged |
| agent/manga-chunk-ef-runner | PR #60 merged (via -clean) |

### Local SUPERSEDED-SOURCE (2, delete after state-convergence promotion completes)
| Branch | Evidence |
|--------|----------|
| agent/manga-sdf-revision-workspace | Pen-name content superset on state-convergence |
| codex/main-salvage-20260323-153043 | Pearl-int content superset on state-convergence |

### Local STALE-ARCHIVE, non-worktree (19, safe to delete)
claude/heuristic-ishizaka, claude/interesting-khayyam, claude/musing-euler, claude/stupefied-wing, claude/thirsty-williams, claude/priceless-chatelet, claude/nostalgic-pare, claude/pedantic-newton, claude/lucid-visvesvaraya, claude/vibrant-jackson, agent/adi-da-universal-band-arc-align, agent/bestseller-grade-pr08, agent/bestseller-grade-pr01, agent/d1-d3-voice-relocalization, agent/d1-voice-reloc-wp-hrn, agent/s6-ahjan-teacher-bank, agent/github-desktop-clean, agent/github-prod-readiness, worktree-agent-a71e22fe

### Local STALE-ARCHIVE, backup-only (2, safe to delete)
codex/main-autobackup-20260322-112842, codex/main-autobackup-20260320-2124

### Local STALE-ARCHIVE, worktree branches (8, require worktree removal first)
claude/brave-blackburn, claude/charming-williams, claude/festive-archimedes, claude/gracious-hamilton, claude/keen-lehmann, claude/keen-shamir, claude/objective-colden, claude/relaxed-bardeen

### Main worktree branch (1, requires checkout switch)
agent/video-publishing-stage18 — main worktree currently on this branch

---

## 5. Keep Queue

| Branch | Reason |
|--------|--------|
| claude/condescending-bassi | Current session worktree |
| main | Local tracking ref |
| codex/state-convergence-20260328 | DO NOT delete until all workstream slices are promoted |

---

## 6. Genuine Unknowns

**None.** All 5 sources exhausted for all 46 branches.

---

## 7. Risk Summary and Rollback Plan

| Risk | Impact | Mitigation |
|------|--------|-----------|
| WS-4 experience changes break pipeline | High | Split into 2 PRs; new-files PR first, modifications PR second with full test run |
| WS-5/WS-6 stale workflow diffs regress main | High | Per-file diff review before any promotion; skip files where main is already ahead |
| WS-3 recommender violates Arc-First | Medium | Review against OWNERSHIP_MATRIX before promoting |
| WS-7 slot_resolver conflict with adi-da branch | Low | Promote WS-7 first, then rebase adi-da cherry-pick |
| Push-guard blocks large JSON (WS-2) | Low | Check file size; split PR if needed |
| Worktree deletion disrupts active sessions | Medium | Only delete after confirming no active Claude sessions |

**Rollback:** Each promotion is an independent branch + PR. If any causes CI failure or regression, close the PR without merging. For already-merged content, `git revert <merge-sha>`.

---

## 8. Workstream Registry Updates (proposed after promotion)

| workstream_id | Field | Current | Proposed |
|--------------|-------|---------|----------|
| ws_pearl_int_recovery_20260328 | status | preserved | completed (after WS-1 PR merges) |
| ws_pen_name_recovery_20260328 | status | preserved | completed (after WS-2 PR merges) |
| ws_recommender_promotion_20260328 | status | preserved | completed (after WS-3 PR merges) |
| ws_experience_recovery_20260328 | status | preserved | completed (after WS-4 PRs merge) |
| ws_github_prod_readiness_20260328 | status | preserved | completed (after WS-5 PR merges) |
| ws_external_sweep_20260328 | status | preserved | completed (salvage slice archived, no promotable code) |
| NEW ROW | ws_branch_consolidation_20260401 | active | Pearl_GitHub | This consolidation session |

---

## Appendix: Branch count reduction

| Category | Before | After full execution |
|----------|-------:|--------------------:|
| Local branches | 46 | 3 (main, condescending-bassi, state-convergence until done) |
| Remote branches | 3 | 2 (origin/main + active PR branch) |
| Active worktrees | 10 | 2 (main + condescending-bassi) |
| Workstreams preserved | 6 | 0 (all promoted or archived) |
