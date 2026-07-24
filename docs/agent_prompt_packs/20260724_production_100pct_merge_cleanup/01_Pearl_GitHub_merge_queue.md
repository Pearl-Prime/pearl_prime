# EXECUTE — Lane 01 (Pearl_GitHub): Drain the merge queue (33 open PRs)

This is an execution prompt, not a planning request. End state: **every open PR is
MERGED, CLOSED-superseded, or HELD with a named gate** — zero "still in line" PRs.
Do not stop at plan / PR-open / tests-running.

## Contract (in-band)
- STARTUP_RECEIPT: branch, HEAD SHA, `git status --short | head`, `gh auth status`,
  `git fetch origin && git log origin/main -1 --oneline`.
- **Every PR disposition below is a CLAIM from 2026-07-24 authoring.** Re-verify each:
  `gh pr view N --json state,mergeable,mergeStateStatus,title` before acting. Check
  `mergeable` explicitly — yesterday three PRs sat with `CONFLICTING` unnoticed
  because closeouts only looked at check colors.
- Phase 1 (verify + close superseded) starts NOW. Phase 2 (merges) starts only on
  Lane 02's `PIPER100-L02-MAIN-GREEN` signal — the live CI-status gate in
  `pre_merge_check.sh` (PR #199) will correctly refuse merges before that.
- Merge rules per PR: **Rule-0** `gh pr diff <n> --stat | tail -1` (STOP if >50
  deletions — PR #245-class disasters start here); `bash scripts/git/pre_merge_check.sh <n>`;
  `python3 scripts/ci/pr_governance_review.py` ("BLOCKED + 0 files + empty blockers"
  = known spurious, re-run once). Squash-merge, delete remote branch.
- Sibling-collision check before touching any PR: search merged+open PR titles for
  overlapping scope (`gh pr list --search "<keywords>" --state all`).
- Layer-honest: merging a docs PR ships a DOCUMENT, not the work it describes —
  never report subsystem progress from a docs merge.
- `gh pr diff --name-status` is INVALID — use `gh api repos/{owner}/{repo}/pulls/<n>/files`.

## Dispositions (verify each live, then act)

**CLOSE as superseded (comment with the superseding PR/SHA, then close):**
- **#131, #231** — duplicate of **#234 (MERGED 2026-07-23T18:17Z)**. Verify file-for-file:
  `gh api .../pulls/131/files` vs what #234 landed; if #131 covers any file #234
  missed, cherry-pick the remainder into a fresh PR first.
- **#235** — baseline-regen approach; #234 fixed by authoring real prose. Close if
  parse-sweep is green on main (Lane 02 confirms); else hand to Lane 02.
- **#55** — superseded by #54/#75/#201/#175 per `main_orphan_imports_zh_tw_pr49_unbreak_2026-07-22.md`.
  Verify the orphan modules exist on main before closing.
- **#53** — metricool social package; check what (if anything) is still missing on
  main after #54/#75/#201. Close-or-slim accordingly.

**MERGE — docs/QA records (low risk, Rule-0 + governance still bind):**
#56, #60, #74, #76, #89, #93, #94, #95, #211 (merge as the historical record of the
first zh-TW book attempt; its blocker chain is resolved by #234+#223), #213, #215,
#271, #272, #274, #276. Undraft drafts (`gh pr ready N`) before merging.

**MERGE — code/feat (verify CI per-PR, rebase if CONFLICTING):**
- **#223** — locale-aware EXERCISE classifier. Was chained behind #131; #234's merge
  unblocks it. This is Lane 06's hard dependency — do it FIRST in phase 2 and signal
  `PIPER100-L01-223-MERGED`.
- **#107** — content-bank backfill (its 3 red checks were pre-existing main redness;
  re-run after Lane 02).
- **#50** (gt30d Wave-A+B), **#62** (zh-TW glossary), **#73** (devops policy + RAP
  detector), **#97** (Cursor cloud env), **#100** (manga wave-2 items 1/2/4),
  **#104 + #120** (store-series naming — rebase first; #133 already merged their old
  blocker), **#142** (disk cleanup + r2_sync fixes — Rule-0 check ESPECIALLY here,
  it deletes files by design), **#200** (teacher/music manga wiring — the manga
  handoff says merge this before #74/#76/#94/#100), **#246** (zh_TW reader-market
  allowlist).

**HOLD (do not merge — operator quality gate):**
- **#243, #245** — zh_TW manga smoke cell + doc-drift. The manga dispatch doctrine
  forbids merging the smoke cell without an operator read (OPERATOR_ACTIONS.md item E1).
  Comment "HELD for operator read per pack 20260724" on each.

**Closed-unmerged (flag, don't reopen here):**
- **#58** → Lane 05 owns (assignment.js bug may be live).
- **#68** → Lane 03 owns (verify superseded by #152–155, then discard branch).

## Order within phase 2
1. #223 (Lane 06 dependency) → 2. #200 → #74/#76/#94/#100 (manga chain per its
handoff) → 3. #104 → #120 (naming chain) → 4. everything else, docs last.
After EACH merge: `git fetch origin` and re-verify the next PR's mergeable state —
each merge can conflict the next.

## Closeout
```
CLOSEOUT_RECEIPT: PIPER100-L01-DONE
merged: <PR#s + squash SHAs>
closed_superseded: <PR#s + superseding refs>
held: <PR#s + gate names>
conflicts_rebased: <PR#s>
queue_remaining: <must be 0 or each explained>
acceptance_layer_note: docs merges = records only; code merges = system working at most
NEXT_ACTION: <e.g. Lane 06 go — #223 merged>
```
Append a dated note to this pack's INDEX.md. BLOCKED acceptable only with blocker +
resume signal named.
