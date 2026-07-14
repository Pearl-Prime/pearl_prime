# Lane 08 — pt_BR / en_US catalog merge sweep

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_GitHub for Phoenix Omega, lane 08 of the PR Backlog Clear pack.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_GitHub
- LANE=catalog-merge-sweep-08
- EXECUTION_MODE=github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=cloud-agent
- PERSISTENCE_SURFACES=PR list, gh merge history, artifacts/coordination/handoffs/
- RESUME_SURFACE=artifacts/coordination/handoffs/catalog-merge-sweep-08_2026-07-14.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/agent_brief.txt (Router Operating Principles v3 §1, §4, §5, §17; v4 §21, §22, §23)
- docs/agent_prompt_packs/20260714_pr_backlog_clear/INDEX.md
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv (catalog subsystem row)

PRE-REQUISITE CHECKS:
- foundation-triage-complete=<signal from lane 01> must exist before you start.
  If lane 01 has not emitted this signal, STOP and report BLOCKED.
- Confirm push_guard and governance file caps are not currently tripped repo-wide:
  `PYTHONPATH=. python3 scripts/git/push_guard.py --dry-run` (or equivalent read-only check).

LIVE STATE RECONCILIATION:
- fetch origin/main; do not trust any PR count in this file — re-derive live:
  `gh pr list --state open --search "feat(catalog): pt_BR / en_US skeletons" --json number,title,headRefName,mergeable,statusCheckRollup`
- This lane's approximate scope at pack-authoring time was **246 (240+6) open PRs**
  across locale(s): pt_br,en_us. Treat this as a floor/ceiling sanity check only,
  not ground truth — if the live count differs materially, note the delta in
  your closeout, don't silently reconcile it away.
- Check for sibling-agent collision: no other running session should be merging
  PRs under `config/source_of_truth/book_plans_{pt_br,en_us}/` right now. If
  `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` shows another owner already
  on this exact scope, STAND DOWN and report BLOCKED with the conflicting row.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- live count of open PRs matching this lane's locale(s), by CI status
  (green / red / pending / no-checks-configured);
- confirm every PR in scope is additive-only (no file deletions) via
  `gh pr view <n> --json files -q '[.files[].additions,.files[].deletions]'`
  spot-check on at least 3 PRs before bulk action — Rule 0 (never merge a PR
  net-deleting >50 files without explicit owner approval) applies per PR;
- proposed smallest safe batch (see below).

PROVENANCE:
- research: NONE (this is git-ops hygiene, not new content authorship)
- documents: docs/agent_brief.txt, docs/GITHUB_OPERATIONS_FRAMEWORK.md, docs/GITHUB_GOVERNANCE.md
- builds_on: existing catalog skeleton generation pipeline (these PRs are already-generated CI output, not new work you are authoring)
- inventory: EXTENDS (merging registers new book-plan YAML files; nothing existing is removed or reduced)

MISSION:
- Merge every open, CI-green, additive-only `feat(catalog): ... skeletons ...`
  PR under locale(s) pt_br,en_us into main via squash-merge with branch deletion.
- Every PR that is CI-red, has merge conflicts, or fails the additive-only
  check gets triaged (not force-merged): log it as BLOCKED with the specific
  reason, do not attempt content fixes yourself (that is not this lane's job —
  flag it to Pearl_PM for a follow-up lane if the count is non-trivial).

DELIVERABLES:
- Every eligible PR in scope merged and its remote branch deleted.
- A per-PR merge log (PR number, merge SHA, branch deleted y/n).
- A short BLOCKED list for anything not merged, with reason.

SMALLEST SAFE BATCH (mandatory ramp — never a single blind bulk merge):
- smoke: pick ONE PR in scope, confirm CI green + additive-only, squash-merge
  it, delete its branch, confirm origin/main still builds / CI on main is
  green after the merge before proceeding.
- pilot: repeat for the next 4 PRs (5 total merged), re-confirm main CI green.
- scale: merge the remainder in checkpointed chunks of ~25–50 PRs; after each
  chunk, re-run the live open-PR count for this lane's scope and log it.

HANG PREVENTION:
- checkpoint/log interval: every chunk of ~25 merges, or every 10 minutes,
  whichever comes first.
- no-progress rule: if two consecutive checkpoints show no increase in merged
  count, inspect `gh run list` / CI logs for a systemic failure (e.g. a shared
  CI check newly broken) before continuing.
- hard stall rule: after three no-progress checkpoints, STOP, mark BLOCKED
  with evidence (failing check name, sample PR numbers), do not keep retrying
  the same failure across hundreds of PRs.
- max batch window: 90 minutes for this lane; if not complete, report partial
  MERGED count + BLOCKED remainder and hand off cleanly (do not leave it silently
  running past this window).

TESTS/PROOFS:
- Each PR's own required status checks (visible in `statusCheckRollup`) must
  be green pre-merge — no override, no `--admin`.
- After each checkpoint chunk: `gh api search/issues?q=repo:Ahjan108/phoenix_omega_v4.8+is:pr+is:open+in:title+"pt_BR / en_US skeletons"&per_page=1 -q '.total_count'`
  logged as the proof root for progress.

DO NOT:
- no gate weakening — do not disable or skip a required check to force a merge;
- no `git add -A` / `git add .` if you touch the working tree for any reason;
- no force-merging a PR with deletions >50 files (Rule 0) without explicit
  operator approval logged first;
- no fake proof — a "merged" claim must carry the real merge SHA from `gh`;
- no local-only finish;
- no giant batch first — smoke and pilot must precede scale.

LANDING CONTRACT:
- MERGED: every eligible PR in scope squash-merged, branch deleted, final
  live-count re-check confirms 0 (or the residual BLOCKED count) remaining
  for this lane's locale(s).
- BLOCKED: exact PR numbers + reasons for anything unmerged, evidence attached,
  nothing left half-done (a PR you started resolving is either merged or
  explicitly logged BLOCKED — never abandoned mid-triage).

CLEANUP LEDGER REQUIRED:
- worktree: none-needed (this lane operates via `gh pr merge`, no local checkout of PR branches required)
- local branch: none-needed
- remote branch: deleted for every merged PR (`gh pr merge <n> --squash --delete-branch`)
- scratch files: remove any /tmp PR-list dumps this lane created
- background jobs: none expected — declare none-needed unless you spawned one
- held artifacts: none expected

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/catalog-merge-sweep-08_2026-07-14.md
  containing: merged PR list with SHAs, BLOCKED list with reasons, before/after
  live count for this lane's scope, checkpoint log.

CLOSEOUT_RECEIPT:
- AGENT=Pearl_GitHub
- LANE=catalog-merge-sweep-08
- STATUS=MERGED|BLOCKED
- SCOPE=pt_br,en_us
- MERGED_COUNT=<n>
- BLOCKED_COUNT=<n> (list PR numbers + reasons)
- SIGNAL=catalog-merge-sweep-08-complete=<merged>/<total>
- PROOF_ROOT=<live count command output, before and after>
- TESTS=<CI check names verified green per PR>
- CLEANUP=<ledger above, filled in>
- HANDOFF=artifacts/coordination/handoffs/catalog-merge-sweep-08_2026-07-14.md
- NEXT_ACTION=<report to Pearl_PM dispatcher; if BLOCKED_COUNT > 0, name the exact follow-up>
```
