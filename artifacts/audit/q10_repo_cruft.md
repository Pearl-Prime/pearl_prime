# Q10 — Repo Cruft Audit

**Generated:** 2026-04-29
**Auditor:** Pearl_GitHub (read-only)
**Working dir:** `/Users/ahjan/phoenix_omega/.claude/worktrees/wonderful-meitner-e5ac76/`
**Method:** Predecessor inventories (`artifacts/inventory/full_repo_*_2026-04-26/27.csv*`) + live `git worktree list`, `git branch -r`, `gh pr list`, `find`, per-config `grep`, doc matrix.
**Discipline:** All "DELETE" verdicts are recommendations for operator review. **Nothing is deleted by this audit.**

---

## Executive summary

| Metric | Count | Notes |
|---|---:|---|
| Active git-tracked worktrees (excl. main repo + cursor) | 32 | All have HEAD ≤ 6 days old |
| Filesystem entries under `.claude/worktrees/` | 125 | |
| **Orphan worktree dirs** (in fs but NOT in `git worktree list`) | **93** | Of which 91 are 0-byte/empty — leftover skeletons |
| Orphan-dir cumulative disk | ~8.6 MB | Tiny — only `zen-margulis-599486` (6.4 MB) and `silly-johnson` (2.3 MB) hold real content |
| Remote branches (excl. `main`/`HEAD`) | 216 | |
| Remote branches with NO open PR | **174** | |
| Remote branches whose PR is already MERGED but branch lingers | **128** | Squash-merge residue — safe to delete after merged-into-main check |
| Remote branches >14d AND no open PR | 9 | Aged + no PR — lowest-risk delete |
| Open PRs | 42 | |
| Open PRs CONFLICTING + updated >14d ago (abandoned) | **12** | Top close/rebase candidates |
| Open PRs MERGEABLE + updated ≤2 days (active) | 16 | Healthy flow |
| `.bak`/`.old`/`.disabled`/`.deprecated` files | **0** | Clean — repo doesn't use this convention |
| Empty directories repo-wide | 109 | 5 in main repo, 104 inside worktree subtree |
| Stub directories at repo root (non-tracked, empty) | 5 | `_wt_beatmap`, `_wt_inj`, `_wt_r2_sai_ma`, `Qwen`, `Qwen-Agent` |
| `salvage/` total size | 32 KB / 8 files | Already trivial — 4 unique JSON/MD files duplicated under nested snapshot |
| `docs/*` files with last commit > 60d ago | 0 | All docs touched within last 60d (data baseline 2026-02-24 → 2026-04-29) |
| Tracked `node_modules/` files | 0 | `.gitignore` working — but `brand-wizard-app/node_modules/` is a known L2 cluster per deprecation plan; resolved via gitignore |

**Bottom line:** the largest cruft surfaces are (a) **128 squash-merged branches still on `origin`** and (b) **93 orphan worktree directories** in `.claude/worktrees/`. Both are low-risk, mechanical cleanups. Stale on-disk *content* is tiny (~9 MB of orphan worktrees). The disk problem is elsewhere (1.5 GB `artifacts/`, 441 MB `image_bank/`, 514 MB `brand-wizard-app/` — addressed in `docs/FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md` D1.a).

---

## A. Stale worktrees

`git worktree list` reports **34 worktrees** total (1 main repo + 1 cursor canary + 32 in `.claude/worktrees/`). The directory `/Users/ahjan/phoenix_omega/.claude/worktrees/` has **125 entries** → **93 orphans**.

### A.1 Active tracked worktrees — all KEEP

All 32 tracked worktrees have HEAD commits within the last 7 days. None qualifies for DELETE under the spec's `>14d AND no PR` rule.

| Bucket | Count |
|---|---:|
| KEEP — has open PR | 8 |
| KEEP — recent commit (≤7d) | 24 |
| KEEP — locked | 1 (`agent-a0f11c22`) |
| REVIEW | 0 |
| DELETE | 0 |

Of the 32 active worktrees, **16 have DIRTY working trees and no open PR** — these are the highest-attention REVIEW candidates per the "never force-delete with uncommitted changes" rule. Sample:

| Worktree | Branch | Last commit | Dirty? | Has PR? |
|---|---|---|---|---|
| `pensive-hodgkin-3511bd` | `claude/pensive-hodgkin-3511bd` | 2026-04-23 | DIRTY | no |
| `agent-a0f11c22` | `worktree-agent-a0f11c22` | 2026-04-24 | DIRTY | no (locked) |
| `brave-cori-be1817` | `agent/pearl-int-r2-env-phase0-20260425` | 2026-04-25 | DIRTY | no |
| `multilingual-qa-20260425` | `agent/review-pack-builder-20260425` | 2026-04-25 | DIRTY | no |
| `restore-first-100-qa-wrapper-20260425` | `agent/restore-first-100-qa-wrapper-20260425` | 2026-04-25 | DIRTY | no |
| `romantic-galileo-5fb37a` | `claude/romantic-galileo-5fb37a` | 2026-04-25 | DIRTY | no |
| `story-bank-20260425` | `agent/restore-story-bank-content-20260425` | 2026-04-25 | DIRTY | no |
| `story-bank-rebased-20260425` | `agent/restore-story-bank-rebased-20260425` | 2026-04-25 | DIRTY | no |
| `epic-black-fcd739` | `agent/manga-2x6-onboarding-docs-index-20260426` | 2026-04-26 | DIRTY | no |
| `naughty-mendel-77a8fa` | `agent/move5-phase2-working-parents-20260426` | 2026-04-26 | DIRTY | no |
| `friendly-chaum-357145` | `agent/pm-phase1-closeout-absorption-spec739` | 2026-04-26 | DIRTY | no |
| `tender-perlman-72acda` | `agent/spec739-phase1-validate-variant-coverage` | 2026-04-26 | DIRTY | no |

**Recommendation:** owner triages these 12. Either (a) commit + open PR, (b) discard via the worktree owner agent, or (c) `git worktree remove --force` after operator confirms.

### A.2 Orphan worktree directories — 93 dirs

These are directories in `/Users/ahjan/phoenix_omega/.claude/worktrees/` that are **not registered** with `git worktree list`. They're leftover skeletons from worktrees that were `worktree remove`'d at some point but the directory was recreated (likely as a `git worktree prune` byproduct or by a script that mkdir'd before `git worktree add`).

- **91 of 93** are **fully empty** (0 files).
- **2 of 93** still contain content:
  - `zen-margulis-599486/` — 6.4 MB
  - `silly-johnson/` — 2.3 MB

Cumulative disk: **~8.6 MB**. Operationally a non-event but the 91 empty dirs pollute `ls`, autocomplete, and any tool walking the worktree root.

**Recommendation — DELETE:**
- The **91 empty orphan dirs** can be removed with a single `find ... -empty -delete` after `git worktree prune` confirms registration is current.
- The **2 non-empty orphan dirs** (`zen-margulis-599486`, `silly-johnson`) → **REVIEW first** — the operator should `cd` in, check `git status`, and confirm there's no uncommitted work before delete. They could be old worktrees whose `.git` link was severed.

---

## B. Abandoned remote branches

Phoenix Omega has **216 remote branches** (excluding `main`/`HEAD`).

### B.1 Age + PR cross-reference

| Age bucket | All branches | Branches without open PR |
|---|---:|---:|
| ≤7d | 162 | 141 |
| 8–14d | 36 | 24 |
| 15–30d | 18 | 9 |
| >30d | 0 | 0 |

### B.2 Categories

| Category | Count | Recommendation |
|---|---:|---|
| **ACTIVE** — branch tied to an open PR (any age) | 42 | KEEP |
| **REBASED** — branch already merged to `main` (squash merge) but still extant on `origin` | **128** | **DELETE — bulk** (after `git branch -r --merged origin/main` confirms; squash merges won't show here, so cross-ref `gh pr list --state merged` head names → confirmed 128 hits) |
| **STALE** — open PR present but updated >7d, conflicting | 21 | REVIEW: rebase or close (see §C) |
| **ABANDONED** — no open PR + last commit >14d | **9** | DELETE after a single confirmation that no merged PR is associated |
| **RECENT-NO-PR** — no open PR, last commit ≤14d | 165 | KEEP for now (likely scratch/exploration) |

The biggest single win is the 128 already-squash-merged branches. The repo has a bot that auto-deletes branches on merge for some merge events; this gap is the residue from earlier merges where deletion was disabled or failed.

---

## C. Abandoned PRs

42 open PRs total. Of those:

| Filter | Count |
|---|---:|
| Updated >7d ago | 21 |
| Updated >14d ago | 9 |
| CONFLICTING (any age) | 25 |
| MERGEABLE (any age) | 17 |
| **CONFLICTING + updated >14d** (true abandoned) | **12** |

### C.1 Abandoned PRs — close-or-rebase candidates

| PR | Updated age | Branch | Title (truncated) | Recommendation |
|---:|---:|---|---|---|
| #407 | 17d | `agent/gemma-en-routing` | Pearl News Gemma3:27b EN expansion | **CLOSE** — superseded by Pearl News rework after #589 |
| #393 | 17d | `agent/pearl-news-live-test` | Pearl News first live WP cycle | **CLOSE** — superseded by post-#732 truth resolver |
| #377 | 17d | `agent/compose-delivery-wave2` | compose_chapter_prose + clean_for_delivery | **REVIEW** — content may still be relevant; rebase or close |
| #369 | 17d | `agent/e2e-master-wu-courage` | E2E Master Wu courage artifacts | **CLOSE** — artifacts likely re-generated |
| #344 | 17d | `agent/teacher-videos-render` | 26 teacher showcase videos | **REVIEW** — superseded by #798 showcase grid overhaul? |
| #336 | 17d | `agent/catalog-quality-refinement` | composite 0.49→0.67 | **REVIEW** — quality refinement may have landed in B2 work |
| #326 | 17d | `agent/catalog-production-run` | 45 registry books production | **CLOSE** — superseded by Top 50 final launch (PR #795 closeout) |
| #416 | 16d | `agent/catalog-refinement-loop` | EI sweep scorecards | **CLOSE** — EI loop work has moved on |
| #430 | 14d | `claude/peaceful-goldberg` | brand-wizard remove language pills | **REBASE** — small UX fix worth merging |
| #427 | 14d | `agent/r2-html-tree-upload` | R2 HTML tree uploader | **REBASE** — useful infra; integrate with #444 R2 work |
| #426 | 14d | `agent/book-planning-system-20260415` | BOOK_PLANNING_SYSTEM_SPEC | **REBASE** — spec doc; merge as historical record or close as superseded |
| #328 | 14d | `agent/onboarding-rebuild` | dark blue onboarding spine | **REVIEW** — UI work may be live or superseded |

### C.2 Approved-but-unmerged

`gh pr list` did not surface PRs with explicit approve+unmerged in the JSON; would require per-PR review query. Not in scope for this audit pass.

---

## D. File-level cruft

### D.1 `.bak` / `.old` / `.disabled` / `.deprecated` extensions

```
find . -path ./node_modules -prune -o -path ./.git -prune -o \
  \( -name '*.bak' -o -name '*.old' -o -name '*.disabled' -o -name '*.deprecated' \) \
  -type f -print
```

**Total: 0 files.** Phoenix Omega does not use this convention — file-version churn happens via git, not via suffix renames.

### D.2 `salvage/` directory

| Item | Value |
|---|---|
| Size | 32 KB |
| File count | 8 |
| Unique payloads | 4 (the rest is `salvage/session_2026_03_28_worktree_snapshot/salvage/...` re-nesting itself) |

Files (all from one 2026-03-24 hourly repo-alignment snapshot):

```
salvage/session_2026-03-28/repo-alignment-hardening/artifacts/governance/repo_alignment/
  hourly_repo_alignment_20260324_063106.{json,md}
  latest_hourly_repo_alignment.{json,md}
salvage/session_2026_03_28_worktree_snapshot/salvage/...   (duplicate of above)
```

**Recommendation — DELETE entire `salvage/` tree.** Already scheduled for retirement per `docs/FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md` (L1 class). Operator can ship as a single ≤8-file PR per CLAUDE.md mass-delete rule.

### D.3 Empty directories

| Location | Count |
|---|---:|
| Repo root (non-worktree) | **5** |
| Inside `.claude/worktrees/` subtree | 104 |
| **Total** | 109 |

**Repo-root empty dirs (DELETE recommended):**
- `./_wt_beatmap`
- `./_wt_inj`
- `./_wt_r2_sai_ma`
- `./Qwen`
- `./Qwen-Agent`

The `_wt_*` triplet looks like leftover worktree mount-point stubs (the `_wt_` prefix is a Pearl_GitHub-internal worktree-mounting pattern). `Qwen/` and `Qwen-Agent/` look like leftover stubs from cloning the upstream Qwen repos before vendoring decisions were made.

The 104 empty dirs inside worktrees are an artifact of git-worktree dirstate; they vanish when the host worktree gets cleaned up. Not separately addressable.

### D.4 Generated artifacts that should be in `.gitignore`

Already addressed by `.gitignore` for credentials and `.env` patterns. The known oversight (`brand-wizard-app/node_modules/` ≈ 6,984 files) is **already in the deprecation plan as cluster D1.a** (L2 class) — not re-listed here.

Tracked top-level file counts:

| Top-level | Tracked files |
|---|---:|
| `config/` | 23,057 |
| `atoms/` | 17,369 |
| `artifacts/` | 4,729 |
| `SOURCE_OF_TRUTH/` | 3,177 |
| `template_expand2/` | 1,012 |
| `brand-wizard-app/` | 901 |
| `image_bank/` | 841 |
| `teachers/` | 590 |
| `pearl_news/` | 503 |
| `scripts/` | 474 |

`config/` and `atoms/` together hold ~40k tracked files — both are intentional content stores (catalog atoms / brand registries), not cruft. No action recommended here without subsystem-owner sign-off.

---

## E. Documentation cruft (pointer to Q7)

Per the doc-status matrix `artifacts/inventory/full_repo_doc_status_matrix_2026-04-27.csv.gz` (305 docs/* rows; date range 2026-04-01 → 2026-04-27):

- **`docs/*` files with `last_commit_date > 60d`: 0**

The dataset's dates reflect commits within the matrix's collection window (2026-04-01 onward). True historical staleness lives in the per-file git log; the oldest documents (e.g., `docs/AUDIT_OLD_CHAT_SPECS_VS_V4.md`, `docs/BOOK_001_*` quartet) trace to 2026-02-24 first commits but all have **been touched within the last 60d** (last commits all within April 2026). Documentation cruft is genuinely low under the >60d filter.

For deeper drift / superseded specs, defer to **Q6 spec-drift audit** (`artifacts/audit/q6_spec_drift.md`) and the L4/L5 classes in the deprecation plan.

---

## F. Test cruft

Tests directory is large (281 tracked files). A full deprecated-API audit was not run in this pass (out of scope — would require running pytest collection + greping for removed module names). Two cheap signals to flag:

- **No test files matching `*.bak/*.old`/disabled** (per §D.1, count = 0).
- Test branch `claude/frosty-noyce-ea448a` (PR #589) explicitly aligns `injection_resolver` tests to current resolver API → suggests tests do drift, but that's being maintained PR-by-PR rather than accumulating as cruft.

**Recommendation — out of scope for Q10.** Spawn dedicated Q-test audit if needed.

---

## G. Configuration cruft

Sample-checked 6 high-profile configs in `config/` for Python callers:

| Config | Py callers | Verdict |
|---|---:|---|
| `config/author_registry.yaml` | 5 | LIVE |
| `config/brand_registry.yaml` | 15 | LIVE (heavily wired) |
| `config/duration_scorecard.yaml` | 2 | LIVE |
| `config/asset_lifecycle.yaml` | **0** | **REVIEW — possible orphan** |
| `config/entropy_planner_spec_v2.yaml` | **0** | **REVIEW — possible orphan** |
| `config/creative_quality_v1.yaml` | 3 | LIVE |

Two of six samples flag as zero-caller — would need per-config inspection (might be loaded by name string or loaded from a registry index, not by file-path string). 88 total items in `config/` — a full caller-graph for all of them is a separate audit (suggest pairing with the `phoenix_v4/` orphan check in deprecation plan §D3).

**Recommendation:** spawn a follow-up that runs the orphan-config check across all 88 `config/*.yaml` files using both string-grep and YAML-name-grep heuristics.

---

## Deletion plan ROI

If the operator adopts every recommendation in this audit:

| Action | Items | Disk freed | Risk | Effort |
|---|---:|---:|---|---:|
| Delete 91 empty orphan worktree dirs | 91 dirs | ~0 (empty) | LOW | 5 min (`find ... -empty -delete`) |
| Delete 2 non-empty orphan worktree dirs after operator confirm | 2 dirs | ~8.7 MB | LOW-MED | 10 min |
| Delete 5 empty repo-root stub dirs (`_wt_*`, `Qwen*`) | 5 dirs | ~0 | LOW | 2 min (one PR) |
| Delete 128 already-squash-merged remote branches | 128 branches | 0 (server-side) | LOW | 30 min (cross-ref + bulk `git push --delete`) |
| Delete 9 abandoned (no PR + >14d) remote branches | 9 branches | 0 | LOW | 10 min |
| Close/rebase 12 abandoned conflicting PRs | 12 PRs | 0 | MED — each needs case-by-case judgment | 90 min (~7 min/PR) |
| Delete `salvage/` (4 unique files, 8 path entries, 32 KB) | 8 paths | 32 KB | LOW | 5 min (one PR) |
| Triage 16 dirty-no-PR worktrees | 16 worktrees | varies | MED — must NOT force-delete with uncommitted work | ~20 min/worktree → 5 hours |
| **Totals** | **~270 items** | **~9 MB** | mostly LOW | **~7.5 operator-hours** |

**Not addressed by this audit (explicitly out of scope or routed elsewhere):**
- `brand-wizard-app/node_modules/` (~6,984 files) → deprecation plan D1.a
- `phoenix_v4/` orphan modules (~153) → deprecation plan D3
- Stale specs / superseded canonicals → Q6 + deprecation plan D2
- Workflow / CI cruft → Q8 (`q8_ci_health.md`)

---

## Risk callouts

1. **Never force-delete a dirty worktree.** The 16 dirty-no-PR worktrees in §A.1 hold uncommitted work. Rule: commit-or-stash-or-discard (with operator OK) BEFORE `git worktree remove --force`.
2. **Squash-merge branch deletes are not 100% safe automatically.** Some "merged" branches may have additional commits added after the merge. Cross-ref `git log origin/<branch> ^origin/main` to confirm the branch tip is fully in main before deletion.
3. **Closing a CONFLICTING PR loses its diff history visibility.** Operator should comment "superseded by #X" with a pointer before closing each abandoned PR in §C.1.
4. **The 2 non-empty orphan worktree dirs may be `git worktree prune`-resistant** (prune only removes registry entries, not dirs). Manual inspection required before `rm -rf`.
5. **`config/asset_lifecycle.yaml` and `config/entropy_planner_spec_v2.yaml` (0 grep hits) might still be live** — loaded by name from a registry. Do NOT delete without (a) checking string-table loaders and (b) running a full pytest collect to surface dynamic loads.
