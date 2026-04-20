# PR #492 (regression museum) — diagnosis & land (2026-04-18)

**Operator:** Pearl_GitHub (Cursor Agent)  
**Repo:** `Ahjan108/phoenix_omega_v4.8`  
**API spend:** $0 (git + `gh` metadata only; no model calls)

---

## Phase 1 — Diagnose (before merge)

### PR #492 state (GitHub)

| Field | Value |
|--------|--------|
| `state` | **OPEN** (at investigation start) |
| `mergedAt` | `null` |
| `mergeCommit` | `null` |
| `baseRefName` | `main` |
| `headRefName` | `agent/regression-museum-lockdown-20260418` |
| URL | https://github.com/Ahjan108/phoenix_omega_v4.8/pull/492 |

### Why the museum was not on `main`

**Case: never merged.** PR #492 was still **open** with no `mergeCommit`. The head commit `35fb99f0325bafe94e4ce371497f54b612590370` (“regression museum”) therefore was **not** an ancestor of `origin/main` before the merge action.

### `origin/main` vs museum commit (before fetch/merge)

- `origin/main` (stale): `70a69088116a52d47b85bbc52fd9834ad2a4fc9b`
- `git merge-base --is-ancestor 35fb99f032 origin/main` → **non-zero** (not on main)

### Checks on PR #492 (snapshot)

`gh pr checks 492` showed:

- **Pass:** Core tests, EI V2 gates, Release gates, Verify governance, audit (LLM Callers Audit), gate (Regression Museum Gate)
- **Fail:** **Workers Builds: pearl-prime** (external Cloudflare Workers build)

`gh pr view 492 --json mergeStateStatus,mergeable`:

- `mergeable`: **MERGEABLE**
- `mergeStateStatus`: **UNSTABLE** (failing / non-green external check)

So: **GitHub considered the PR mergeable** while rollup was **UNSTABLE** due to Workers Builds.

### Ruled out (by PR JSON + history spot-check)

- **Merged then reverted:** not applicable — PR was open with no merge commit.
- **Merged to wrong base:** `baseRefName` was `main`; issue was absence of merge, not wrong base.

### Branches containing `35fb99f032`

Not exhaustively re-listed here (large clone); the commit was the PR head lineage. After merge, **`origin/main` contains the museum** via merge commit below.

---

## Phase 2 — Land

**Path taken: Case A — merge open PR**

Command run:

```bash
gh pr merge 492 --merge
```

**Result:** **MERGED** successfully.

| Field | Value |
|--------|--------|
| `state` | **MERGED** |
| `mergedAt` | `2026-04-18T03:35:21Z` |
| `mergeCommit.oid` | `4aa14983d85ee7c43db178885b70b372b5c044c6` |

**Note for operator:** **Workers Builds: pearl-prime** was still **failing** at check snapshot time. Merge proceeded anyway (likely not a required branch-protection check, or policy allows merge with UNSTABLE). **Follow up** on that Workers failure separately; do not assume Workers is healthy.

**Not used:** cherry-pick / reopen (not Case B/D). **Not used:** Case C (no revert).

---

## Phase 3 — Verify (post-merge)

After `git fetch origin`:

- `origin/main` → `4aa14983d85ee7c43db178885b70b372b5c044c6`
- `git merge-base --is-ancestor 35fb99f032 origin/main` → **exit 0** (**museum commit is on main**)

### Tree presence

- `git cat-file -e origin/main:phoenix_v4/quality/regression_museum/__init__.py` → OK

### Import + ratchet tests (without switching local branch)

Local checkout of `main` was not completed (long-running / dirty worktree risk). Verification used **`git archive origin/main`** for museum paths, **temporary overlay** in the working tree, then:

- `PYTHONPATH=. python3 -c "from phoenix_v4.quality.regression_museum import run_museum_gates; print('import_ok')"` → **import_ok**
- `PYTHONPATH=. python3 -m pytest tests/test_regression_museum_backfill.py -q` → **8 passed** in ~12s

Overlay files were removed after the run.

---

## Side note — `agent/teacher-showcase-reels-20260418`

`gh pr list --head agent/teacher-showcase-reels-20260418`:

| PR | Title | State |
|----|--------|--------|
| **494** | Teacher showcase: example reels for Ahjan, Adi Da, Master Wu | **OPEN** |

URL pattern: https://github.com/Ahjan108/phoenix_omega_v4.8/pull/494  

Separate thread from museum; track independently.

---

## CLOSEOUT_RECEIPT

| Item | Value |
|------|--------|
| PR #492 actual state (root cause) | **OPEN / unmerged** — museum never reached `main` until merge |
| Action taken | **`gh pr merge 492 --merge`** → **MERGED** |
| New PR for cherry-pick | **None** (not needed) |
| `origin/main` SHA with museum present | **`4aa14983d85ee7c43db178885b70b372b5c044c6`** (merge commit) |
| Backfill test (`test_regression_museum_backfill.py`) | **8 passed** (on `origin/main` snapshot via overlay) |
| API spend | **$0** |
| **NEXT_ACTION** | Pull `main` locally, then rerun **Phase B** canary render + museum on rendered `book.txt`; attach artifact for Pearl_Editor markup. Optionally fix **Workers Builds: pearl-prime** if it is required elsewhere. |
