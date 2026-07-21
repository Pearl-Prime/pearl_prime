# Handoff — Lane 03 batch-driver-cellaware (2026-07-21)

## CLOSEOUT_RECEIPT

- AGENT: Pearl_Architect
- LANE: batch-driver-cellaware
- STATUS: LANDED-OFFLINE (local branch + diffs only; no commit, no push — per
  operator constraint; Claude Sonnet 5 will review/land)
- BRANCH: `agent/bestseller-atom-flow-lanes-20260721`
- PR: none (do not open — operator constraint + GitHub API 403/account
  suspended, unverified this session)
- MERGE_SHA: n/a
- PILOT_RESULT: not run — operator explicitly capped this session at the
  1-book **smoke** test (`SMALLEST SAFE BATCH` tier 1 of 3 in the lane pack).
  The 5-book pilot and the 96-book scale tier are both HOLD, pending
  operator go/no-go.
- SMOKE_RESULT: 1 real render OK (seed 43057), 56/57 correctly
  skipped-and-logged as unauthored, 0 fail, 0 timeout, 0 orphan processes.
- PROOF_ROOT: `artifacts/qa/random_2h_x100_20260721/smoke_lane03/`
- TESTS: see "Smoke test" below (no unit tests added — Lane 03 pack calls
  for a real-render pilot/smoke proof, not a mocked test suite)
- ACCEPTANCE_LAYER_OF_THIS_LANE'S_OWN_CLAIM: infrastructure (batch driver
  fix) — not bestseller; the one real book this session rendered is at most
  Layer 1 "structurally clear" (its own `enrichment_audit.json` shows
  `research_fit: null`, see caveat below)
- CLEANUP: no worktree created (see branch/isolation note below — shared
  working tree with `agent/storyblocks-fill-social-bank-20260721`, by
  design, since nothing is committed); new local branch kept (HOLD —
  uncommitted diffs, reviewer will commit/land); no remote branch; scratch
  smoke-test artifacts under `artifacts/qa/random_2h_x100_20260721/` and
  `artifacts/qa/random_2h_books/random_2h_20260721_healthcare_rns__financial_stress__43057/`
  kept as proof root, not scratch; zero background jobs held (batch driver
  ran to completion in foreground, no orphan `run_pipeline.py` /
  `run_random_2h*` processes confirmed via `ps aux` after the run)
- HANDOFF: this file
- NEXT_ACTION: operator go/no-go on the 5-book pilot (mix of authored +
  unauthored cells) before any scale-up. **Do not start Lane 04 from this
  handoff** (explicit operator instruction this session).

## Branch / isolation note (IMPORTANT — read before landing)

- `origin/main` was **unreachable this session**: `git fetch origin` /
  `git ls-remote --heads origin` returned zero refs (consistent with the
  pack's documented "GitHub API 403 — account suspended" blocker, and with
  Lane 01's own handoff hitting the same wall). No cached `origin/main` ref
  exists locally (`git rev-parse origin/main` fails). A stale local `main`
  branch exists (tip `ab0c4bec13`, dated 2026-03-30) — 4 months stale,
  **not used** as a base since it would misrepresent Lane 01's already-dirty
  edits to `scripts/run_production_readiness_gates.py` etc. as huge diffs
  against ancient content instead of the small, real diffs they are.
- New branch `agent/bestseller-atom-flow-lanes-20260721` was created via
  `git checkout -b <name>` **from the current HEAD**
  (`a1ced029868f8978f53b6c03b1ee46d80626713a`, tip of
  `agent/storyblocks-fill-social-bank-20260721`) — an instant, zero-file-churn
  operation (same commit, same tree) rather than a fresh checkout of
  `origin/main`, because origin/main was unreachable.
- **The two branches share the same working directory** (this was a plain
  `checkout -b`, not `git worktree add`). A separate worktree was
  deliberately **not** created: (a) nothing in this session is committed, so
  worktree-level isolation buys no safety against loss, only tidiness; (b)
  this repo's working tree carries several thousand pre-existing
  untracked/modified files (Storyblocks/teacher-onboarding WIP,
  `config/source_of_truth/book_plans_es_us/*.yaml`, LFS-tracked media, etc.)
  and a full second checkout was judged too slow/risky given this session
  also observed the live IDE git integration under heavy, possibly
  contention-related load (`git status`/`git fetch` on this repo took
  multiple minutes unscoped; hundreds of concurrent `git-lfs
  filter-process` and repeated `.git/index.lock` contention from what
  appears to be Cursor's own background git polling, independent of this
  session's commands).
- **Consequence:** switching to the new branch did **not** touch, stage, or
  alter any of the pre-existing Storyblocks/teacher-onboarding
  uncommitted files — they are exactly as found, on both branch names
  (since nothing is committed, "which branch" doesn't change what's on
  disk). Checking out `agent/storyblocks-fill-social-bank-20260721` again
  will show the identical working tree. **Only** the Lane 01 files (already
  present before this session) and the Lane 03 files below were touched by
  this session's work.
- Recommendation for the reviewer/lander: when landing, cherry-pick /
  re-apply **only** the Lane 01 + Lane 03 file list onto a fresh
  `origin/main` branch once GitHub access is confirmed — do not open a PR
  off this branch as-is, since its history still carries the unrelated
  Storyblocks commits (`a1ced0298`, `eae593f0b0`, `ac7e8b7`, ...) that predate
  this session and are out of Lane 03's scope.

## Pre-requisite checks (per pack)

- `ps aux | grep run_pipeline` before starting: **clean**, no orphans from
  the prior 42000–42006 timeout batch.
- 3/3-books-succeeded-via-plain-subprocess claim: **not independently
  re-reproduced this session** (would have cost ~3×90–800s with no new
  information — the code-level diagnosis below is sufficiently conclusive
  and the new driver's own smoke run empirically re-confirms the plain-path
  hypothesis with a fresh real render). Treat the original "wrapper is the
  culprit" diagnosis as **strongly supported by code inspection + this
  session's clean run**, not a byte-for-byte reproduction of the original
  1/7 hang.

## Discovery report — exact diff between the two subprocess paths

- `run_random_2h_book_with_trace.py`'s `run_render()` (unchanged, proven
  3/3): `subprocess.run(cmd, cwd=cwd)` — no timeout, no new session, no
  process group. Simplest possible blocking call.
- The **old** (pre-Lane-03) `run_random_2h_book_x100.py` used:
  `subprocess.Popen(..., start_new_session=True)` →
  `proc.wait(timeout=args.timeout_s)` with **`--timeout-s` default 180**, and
  on `TimeoutExpired`: `os.killpg(proc.pid, 9)`.
- **Smoking gun found by inspection:** the same old script's own docstring
  says observed real `extended_book_2h` renders take **~822s**, i.e. **4.5x**
  the 180s default timeout. That means essentially *every* book render would
  have been mid-flight SIGKILLed via `killpg` before finishing — fully
  consistent with the freeze/orphan pattern the operator saw (1/7 "hung").
  A process-group kill mid-render (while `run_pipeline.py`'s own subprocess
  tree and any file handles/locks it holds are active) is a much riskier
  failure mode than a plain `terminate()`/`kill()` on a single child, and is
  the more likely source of orphaned state than the wrapper itself.
- This session's clean run (90.7s real render, default 1200s timeout never
  approached) does not, by itself, prove the old wrapper's killpg *causes*
  orphans — but it does confirm the plain-subprocess path is fast and
  reliable for an authored cell, and the 180s-vs-822s mismatch alone fully
  explains why the old wrapper would have killed nearly every run.

## Lane 03 deliverable

### Files changed

| Path | Status | Notes |
|---|---|---|
| `scripts/qa/run_random_2h_book_x100.py` | REWRITTEN (was untracked ad-hoc killpg wrapper; canonical location unchanged — matches existing `scripts/qa/` convention) | 356 lines, no killpg/process-group kill, cell-aware pre-check, checkpoint reporting, `research_fit_bound` field |
| `scripts/qa/run_random_2h_book_with_trace.py` | **UNCHANGED** (pre-existing untracked file, read + imported from, not edited — its proven plain-subprocess `run_render()` is exactly what Lane 03 preserves) | listed in pack's "Hot files" as a dependency, not an edit target |

No other files touched by Lane 03.

### What the new driver does

1. **Plain-subprocess path, no process-group kill.** `subprocess.Popen`
   without `start_new_session`; on timeout: `terminate()` → bounded
   `wait(30s)` → `kill()`, on the single child pid only. Default
   `--timeout-s 1200` (>= the pack's 900s floor; observed real runs ~822s).
2. **Cell-aware pre-check.** Before invoking the wrapper subprocess, calls
   the *exact same* `list_candidates()` / `pick_candidate()` the wrapper
   uses internally (same unfiltered pool, so seed→cell mapping is identical
   in-process and in the subprocess) and checks
   `story_atoms/<persona>/anchored/<topic>/<engine>/` via the wrapper's own
   `_has_story_atoms()`. Unauthored cells are **skipped** (no subprocess
   launched) and logged to `<out-dir>/cells_needing_authoring.jsonl`
   (feeds Lane 02 / `ws_story_cell_authoring_20260425`). `--allow-unauthored`
   overrides this to render floor-only smoke books anyway.
3. **Checkpoint reporting every N (`--checkpoint-every`, default 5)
   attempted books** (run or skip both count), writing
   `CHECKPOINT_NNN.json` with seed/cell/ok/fail/skip counts, plus a
   `research_fit_bound` field per rendered book (true/false once an
   `enrichment_audit.json` is present with an active `research_fit.mode`;
   `null` if no audit file exists yet) — the field Lane 01's gate will make
   meaningful once it lands.
4. **Retirement of the ad-hoc version**: there is only one file at the
   canonical path now — the old killpg logic was replaced in place, not left
   as a second parallel script.

### Smoke test (per pack `SMALLEST SAFE BATCH` — smoke tier only, pilot/scale withheld)

Command run:

```bash
PYTHONPATH=. python3 scripts/qa/run_random_2h_book_x100.py \
  --seed-start 43001 --n 57 \
  --out-dir artifacts/qa/random_2h_x100_20260721/smoke_lane03 \
  --checkpoint-every 5
```

Result: **PASS**

- seeds 43001–43056 (56 cells): all correctly resolved to **no story_atoms
  bank** and were skipped without launching any subprocess; each logged to
  `cells_needing_authoring.jsonl` (56 lines, verified).
- seed 43057 → `healthcare_rns × financial_stress × overwhelm` (one of the
  6 banked personas / 5 banked topics from the pack's ground truth) →
  correctly resolved as **authored** → rendered for real:
  `OK seed=43057 90.7s ... words=17919 research_fit_bound=False
  pipeline_exit=1`. `book.txt` and `human_atom_trace.txt` both exist on
  disk.
- `SUMMARY.json`: `{"ok": 1, "fail": 0, "skip": 56, "n": 57}`.
- 11 `CHECKPOINT_*.json` files written at 5/10/.../55.
- `ps aux | grep -i 'run_pipeline\|run_random_2h'` immediately after: **zero
  matches** — no orphans.

Caveat worth flagging to the reviewer (not a Lane 03 defect, out of scope
to fix here): the one real render's own `enrichment_audit.json` has
`research_fit: null` (key present, value `null`) even though its cell has a
story_atoms bank and `_has_story_atoms()` correctly returned `True`. That is
a `story_planner.py` / gate-wiring question for Lane 01/02, not a driver
bug — the driver's `research_fit_bound` field correctly reports `False`
from whatever the audit actually contains; also `pipeline_exit=1` (some
downstream gate failed) even though `book.txt`/trace both exist, matching
the wrapper's own pre-existing "trace whenever artifacts exist, even if
gates failed after writing book/SPA" behavior — `book_ok` intentionally
does not require `pipeline_exit == 0`, exactly as the proven wrapper already
does.

## What the reviewer should verify before landing

1. Re-run the smoke command above (or a fresh seed range) and confirm the
   same skip/run split behavior — cell selection depends on the current
   `config/source_of_truth/master_arcs/*.yaml` listing, so exact seed→cell
   mappings can shift if arcs are added/removed on `origin/main` relative to
   this branch.
2. Decide the real base to land on once GitHub access is restored — this
   session could not fetch `origin/main` at all, so the diff here is against
   this branch's HEAD, not verified-fresh `origin/main`.
3. Confirm `--allow-unauthored` behavior explicitly (not exercised in the
   smoke test — only the default skip-by-default path was proven).
4. Confirm the timeout escalation path
   (`terminate()`→`wait(30s)`→`kill()`) is acceptable without a live
   reproduction of an actual 1200s+ hang (none occurred in this smoke test;
   the 90.7s real render never approached the timeout).
5. Re-run `python3 scripts/ci/audit_llm_callers.py` and
   `PYTHONPATH=. python3 scripts/ci/check_rap_compliance.py` before any
   push, per CLAUDE.md (not run this session — no commit/push occurred).

## Explicit stop condition

**STOPPED after the Lane 03 smoke test passed, as instructed.** Did not run
the 5-book pilot, did not scale to 96 more books, and did **not** start
Lane 04 (book-acceptance-stamp). No commit, no push, no PR opened. All
changes are uncommitted diffs on local branch
`agent/bestseller-atom-flow-lanes-20260721`, ready for Claude Sonnet 5 to
review and land.
