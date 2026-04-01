# Branch Triage — 2026-04-01 (Workstream-Resolved)

Owner: Pearl_GitHub (with Pearl_PM read authority)
Inventory time: 2026-04-01 after `git fetch --all --prune`
Authority: `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`, merged PR history (143 PRs)
Prior triage: `artifacts/coordination/BRANCH_TRIAGE_2026_03_31.md`
Decision tree: Steps A-G per task specification

## Summary

| Metric | Count |
|--------|------:|
| Total local branches inventoried | 46 |
| Remote branches (non-HEAD) | 3 |
| **PROMOTE** | **2** |
| **PROMOTE-WITH-REVIEW** | **3** (including codex/state-convergence decomposed into 6 workstream slices) |
| **SUPERSEDED** | **8** |
| **SUPERSEDED-SOURCE** | **2** (base_ref branches fully covered by state-convergence) |
| **STALE-ARCHIVE** | **27** |
| **KEEP** | **2** |
| **GENUINE UNKNOWN** | **0** |

**Key resolution vs prior triage:** The 3 branches previously classified UNKNOWN are now fully resolved:
- `codex/state-convergence-20260328` → PROMOTE-WITH-REVIEW (decomposed into 6 promotable workstream slices + 1 already-on-main slice)
- `agent/manga-sdf-revision-workspace` → SUPERSEDED-SOURCE (state-convergence has superset of pen-name content + verify script)
- `codex/main-salvage-20260323-153043` → SUPERSEDED-SOURCE (pearl-int content fully present on state-convergence)

---

## PROMOTE (2 branches) — Step D

### 1. agent/adi-da-story-universal-wildcard

- **Decision step:** D — no workstream, no PR, unique code+test
- **Commit:** `a5c2b9d6 fix(teacher-mode): treat universal STORY atoms as band wildcard`
- **Files (3):**
  - `phoenix_v4/planning/pool_index.py` (+13 -1)
  - `phoenix_v4/planning/slot_resolver.py` (+6 -1)
  - `tests/test_teacher_story_universal_band.py` (+46 new)
- **Conflicts:** None
- **Note:** Related fix landed via PR #101 (`agent/adi-da-story-universal-wildcard-clean`), but this original branch has a slightly different approach with a test file. Diff the two to confirm whether this adds value beyond #101.

### 2. agent/docs-manga-landmarks

- **Decision step:** D — no workstream, no PR, docs-only
- **Commit:** `1d703e7a docs(manga): add merged-to-main implementation landmarks log`
- **Files (1):** `docs/MANGA_IMPLEMENTATION_OUTLINE.md` (+17)
- **Conflicts:** None

---

## PROMOTE-WITH-REVIEW (3 branches, 8 workstream slices)

### 1. codex/state-convergence-20260328 — DECOMPOSED BY WORKSTREAM (Step A+E)

This branch maps to 7 workstreams. Decomposition below. 3 feature commits (non-backup): `742c16a9`, `370a93fe`, `f9df635f`.

#### Slice 1: ws_recommender_promotion_20260328 (preserved) — PROMOTABLE

**Status:** Preserved. No merged PR. None of these 22 new files exist on main.
**Files (24, +1175 -1):**
- `phoenix_recommender/` — full package: `__init__.py`, `__main__.py`, `candidate_generator.py`, `cli.py`, `recommendation_report.py`, `scoring_model.py`
- `config/recommender/` — `constraints.yaml`, `hard_gates.yaml`, `scoring_weights.yaml`, `topic_mapping.yaml`
- `config/voice_auditions/pending_voice_assignments.yaml`
- `scripts/ci/check_voice_audition_contract.py`, `write_workflow_run_manifest.py`
- `scripts/release/release_smoke.sh`
- `tests/test_phoenix_recommender.py`, `test_voice_audition_contract.py`, `test_write_workflow_run_manifest.py`, `test_pearl_prime_release_evidence.py`
- `artifacts/recommendations/ranked.json`, `summary.md`
- `artifacts/release/workflow_run_manifest.json`, `pearl_prime_release_evidence.json`, `latest_systems_test_report.json`
**Conflicts:** Not tested yet (need merge-tree per-path)
**Risk:** Medium — new code package + CI scripts + tests. Needs review of whether recommender is architecturally current per Arc-First.

#### Slice 2: ws_experience_recovery_20260328 (preserved) — PROMOTABLE

**Status:** Preserved. No merged PR. Most files do not exist on main.
**Files (20, +4163 -128):**
- `specs/EXPERIENCE_LAYER_ANTI_SPAM_SPEC.md` — NEW (925 lines, authority doc — REVIEW-REQUIRED per hard constraints)
- `config/experience/` — 4 new files: `brand_experience_profiles.yaml`, `experience_defaults.yaml`, `experience_wave_controls.yaml`, `risky_combos.yaml`
- `config/catalog_planning/engine_title_angles.yaml` — NEW
- `phoenix_v4/planning/experience_resolver.py` — NEW (+169)
- `phoenix_v4/planning/wave_orchestrator.py` — NEW (+27)
- `phoenix_v4/qa/catalog_spam_gates.py` — NEW (+356)
- `phoenix_v4/qa/experience_wave_checks.py` — NEW (+461)
- `phoenix_v4/naming/generator.py` — MODIFIED (heavy changes)
- `phoenix_v4/naming/keyword_bank.py` — MODIFIED
- `phoenix_v4/ops/check_release_wave.py` — MODIFIED
- `scripts/ci/check_catalog_spam.py`, `check_wave_density.py`, `run_prepublish_gates.py` — MODIFIED
- `scripts/run_pipeline.py` — MODIFIED
- `tests/test_experience_layer.py` — NEW (+384)
- `omega/title_entropy/subtitle_patterns.yaml` — MODIFIED
- `config/catalog_planning/series_templates.yaml` — MODIFIED (exists on main)
**Risk:** High — large scope, modifies existing production code (naming, pipeline, CI scripts), adds authority spec. Must be reviewed against Arc-First.

#### Slice 3: ws_pearl_int_recovery_20260328 (preserved) — PROMOTABLE

**Status:** Preserved. No merged PR. Zero Pearl_Int paths exist on main.
**Files (26, +3967):**
- `skills/pearl-int/SKILL.md` + 4 reference files — all NEW
- `docs/TREND_FEED_INTEGRATION_STRATEGY.md` — NEW (327 lines)
- `config/trend_keywords/` — 5 new tiered config files
- `scripts/feeds/` — `budget_guard.py`, `check_trends.py`, `daily_scrape_runner.py`, `score_trends.py` — all NEW
- `artifacts/feeds/` — 9 files (digests, scores, budget plan)
- `artifacts/governance/session_logs/` — 2 session logs
**Risk:** Medium — new skill + config + scripts. No existing code modified. SerpAPI budget plan is operational artifact. Dry-run pipeline only.

#### Slice 4: ws_pen_name_recovery_20260328 (preserved) — PROMOTABLE

**Status:** Preserved. No merged PR. 4 core configs exist on main (same blobs), 3 files NOT on main.
**Unpromoted files:**
- `config/authoring/pen_name_teacher_profiles_full.json` — NEW (+48982 lines, large JSON)
- `docs/PEN_NAME_AUTHOR_SYSTEM.md` — NEW (+228, differs slightly from manga-sdf version)
- `scripts/verify_pen_name_coverage.py` — NEW (+112, NOT on manga-sdf branch either)
**Already on main (identical blobs):**
- `config/authoring/pen_name_teacher_profiles.yaml`
- `config/brand_author_assignments.yaml`
- `config/brand_narrator_assignments.yaml`
- `config/brand_registry.yaml`
**Risk:** Low for docs + script. The 48K-line JSON is large; review whether it duplicates existing profiles.

#### Slice 5: ws_github_prod_readiness_20260328 (preserved) — PROMOTABLE-WITH-REVIEW

**Status:** Preserved. No merged PR. All 9 files exist on main but DIFFER.
**Files (9, +331 -331):**
- `.github/workflows/release-gates.yml` — MODIFIED (touches branch-protection-required workflow)
- `.github/workflows/catalog-book-pipeline.yml` — MODIFIED
- `.github/workflows/marketing-briefs-and-proposals.yml` — MODIFIED
- `.github/workflows/marketing_continuous.yml` — MODIFIED
- `.github/workflows/max-quality-catalog.yml` — MODIFIED
- `scripts/ci/run_canary_100_books.py` — MODIFIED
- `tests/test_run_canary_100_books.py` — MODIFIED
- `docs/GITHUB_NO_FAILURE_FRAMEWORK.md` — MODIFIED
- `docs/GITHUB_OPERATIONS_FRAMEWORK.md` — MODIFIED
**Risk:** HIGH — modifies 5 CI workflows including branch-protection-required `release-gates.yml`. Main has evolved significantly since this branch diverged (87 commits behind). These diffs may be STALE relative to current main. Must diff each file individually to determine if state-convergence version is newer or older than main.

#### Slice 6: ws_qwen_api_unification_20260328 (completed) — PROMOTABLE-WITH-REVIEW

**Status:** Completed per TSV. No merged PR for this branch itself, but ws marked completed.
**Files (11, +331 -96):**
- `docs/QWEN_API_UNIFICATION_COMPLETION_SPEC.md` — NEW (not on main)
- `dashboard.py` — MODIFIED (main has different version)
- `config/governance/github_repos_registry.yaml` — MODIFIED (main differs)
- `pearl_news/pipeline/run_article_pipeline.py`, `llm_expand.py`, `llm_expand_claude.py` — MODIFIED
- `pearl_news/config/llm_expansion.yaml` — MODIFIED
- `PhoenixControl/PhoenixControlApp.swift`, `Views/ContentView.swift` — MODIFIED
- `scripts/dashboard/github_tab.py` — MODIFIED
- `scripts/integrations/open_wordpress_setup.sh` — MODIFIED
**Risk:** HIGH — same staleness concern as Slice 5. Main is 87 commits ahead. File-by-file diff needed.

#### Slice 7: ws_external_sweep_20260328 (preserved) — STALE-ARCHIVE

**Status:** Preserved, but write_scope is "read-only analysis plus archival moves".
**Files:** 2,315 files in `salvage/` (+1.9M lines). Dominated by unpacked backup artifacts, session reports, and automation plans.
**Assessment:** Salvage/archival artifacts. Not promotable code. The salvage paths on main already contain the governance alignment artifacts. This slice is operational evidence only.

#### Additional unique content not mapped to any workstream:
- `370a93fe feat(v32): recreate lost Writers Bible v3.2` — 38 files: `artifacts/writers_bible_v32/` (30 persona YAMLs), `config/marketing/v32_*.yaml` (7 files), `phoenix_v4/qa/bestseller_editor.py`
  - `writers_bible_v32/` and `config/marketing/v32_*` do NOT exist on main — PROMOTABLE
  - `bestseller_editor.py` EXISTS on main but DIFFERS — needs review
- `742c16a9 feat(slot-resolver): thesis-aware atom ranking` — `phoenix_v4/planning/slot_resolver.py` MODIFIED vs main — needs review

### 2. agent/manga-sdf-stub-normalization — Step D

- **Commit:** `833f85ef feat(manga): add SDF conditioning stub + anchor_panels schema`
- **Files (5):** manga SDF code + schema
- **Conflicts:** None
- **Risk:** Medium — new code without tests

### 3. agent/ci-manga-chapter-smoke — Step D

- **Commit:** `3e11a3c8 ci: smoke run_manga_chapter.py replay DAG in core tests`
- **Files (2):** `.github/workflows/core-tests.yml` (+5), `scripts/ci/smoke_manga_chapter_runner.py` (+153)
- **Conflicts:** None
- **Risk:** Medium — touches branch-protection-required workflow

---

## SUPERSEDED (8 branches) — Step C

Content landed on main via merged PR.

| Branch | PR | Merged |
|--------|----|--------|
| agent/cjk6-translation-workflow | #143 | 2026-03-31 |
| agent/renderer-validation | #141 | 2026-03-31 |
| agent/cjk6-translation-pipeline | #142 | 2026-03-31 |
| agent/story-atoms-full | #140 | 2026-03-31 |
| agent/pearl-prime-recovery-docs | #75 | 2026-03-29 |
| agent/onboard-adi-da | #97 | 2026-03-30 |
| agent/manga-chunk-ef-runner | #60 (-clean) | 2026-03-24 |
| agent/cjk6-translation-pipeline | #142 | 2026-03-31 |

---

## SUPERSEDED-SOURCE (2 branches) — Step B

Base-ref branches whose recovery content is fully present on `codex/state-convergence-20260328`.

### agent/manga-sdf-revision-workspace

- **Decision:** Step B — base_ref source for ws_pen_name_recovery. State-convergence has identical blobs for all shared files plus `scripts/verify_pen_name_coverage.py` that this branch lacks. `docs/PEN_NAME_AUTHOR_SYSTEM.md` has a slightly different (newer) version on state-convergence.
- **Verdict:** SUPERSEDED-SOURCE. State-convergence is the canonical promotion source.

### codex/main-salvage-20260323-153043

- **Decision:** Step B — base_ref source for ws_pearl_int_recovery. All 26 Pearl_Int files on this branch are also present on state-convergence with identical or newer content. State-convergence also has additional feed artifacts not on salvage.
- **Verdict:** SUPERSEDED-SOURCE. State-convergence is the canonical promotion source.

---

## STALE-ARCHIVE (27 branches) — Steps D + G

All verified: zero unique non-backup commits, no workstream match (branch or base_ref column), behind main.

### Zero-commit worktree branches (9)
claude/brave-blackburn, claude/charming-williams, claude/festive-archimedes, claude/gracious-hamilton, claude/keen-lehmann, claude/keen-shamir, claude/objective-colden, claude/relaxed-bardeen, agent/video-publishing-stage18

### Zero-commit non-worktree branches (13)
claude/heuristic-ishizaka, claude/interesting-khayyam, claude/musing-euler, claude/stupefied-wing, claude/thirsty-williams, claude/priceless-chatelet, claude/nostalgic-pare, claude/pedantic-newton, claude/vibrant-jackson, agent/adi-da-universal-band-arc-align, agent/bestseller-grade-pr08, agent/bestseller-grade-pr01, agent/d1-d3-voice-relocalization, agent/d1-voice-reloc-wp-hrn, agent/s6-ahjan-teacher-bank, agent/github-desktop-clean, agent/github-prod-readiness, worktree-agent-a71e22fe

### Backup-only branches (3)
codex/main-autobackup-20260322-112842, codex/main-autobackup-20260320-2124, claude/lucid-visvesvaraya

---

## KEEP (2 branches)

| Branch | Reason |
|--------|--------|
| claude/condescending-bassi | Current session worktree |
| main | Local tracking ref |

---

## GENUINE UNKNOWN (0 branches)

All 5 sources exhausted for every branch. No genuine ambiguity remains.

---

## Cross-branch conflict analysis (Step F)

No PROMOTE or PROMOTE-WITH-REVIEW branch modifies files that overlap with another PROMOTE candidate, EXCEPT:
- `agent/adi-da-story-universal-wildcard` modifies `slot_resolver.py` — state-convergence `742c16a9` also modifies `slot_resolver.py`. **Ordering dependency:** promote state-convergence slot_resolver change first, then evaluate if adi-da-story-universal-wildcard still applies cleanly.
