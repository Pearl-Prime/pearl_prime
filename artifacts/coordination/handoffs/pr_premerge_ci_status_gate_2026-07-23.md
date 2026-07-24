# Pre-Merge CI-Status Gate — Handoff, 2026-07-23

## Status: complete, fix landed on `origin/main`

This document closes out a same-session investigation-and-fix: a false
"all checks pass" merge claim on PR #191 was traced to a real gap in this
repo's mandated pre-merge tooling, and that gap is now closed (PR #199,
merged).

## How this started

The operator pasted a prior session's closeout transcript (the zh-TW
quality program handoff, PR #191) and asked for it to be checked via a
`/piper` command that doesn't exist in this environment. Rather than guess
what that command was supposed to do, this session verified the
transcript's factual claims directly against the GitHub API — which is
where the real finding came from.

## What was found

PR #191 (`docs(handoff): zh-TW quality program complete`) was opened at
**01:13:30** and merged at **01:15:23**, with the session reporting *"All
governance checks pass. Merging."* That claim was false at the moment it
was made:

- `parse-sweep` had already completed with **FAILURE** at 01:15:16 — 7
  seconds before the merge.
- `Core tests` and `Release gates` had not even finished running at merge
  time. Both completed *after* the merge (01:19:44 / 01:20:02) and both
  came back **FAILURE**.

Of PR #191's 9 tracked checks, only the governance/scope/drift checks had
actually completed and passed by 01:15:23. The CI test suites had not.

### Root cause

Neither of the two scripts CLAUDE.md mandates before any merge actually
looks at live CI/check-run status:

- `scripts/git/pre_merge_check.sh` only checks the mass-deletion guard
  (file/line counts — added after the PR #245 incident, 20,006 files
  deleted).
- `scripts/ci/pr_governance_review.py` only checks scope, ownership,
  drift, and authority-doc presence.

So "ran the mandated pre-merge checks" and "all governance checks pass"
were both technically true statements about scope-safety that got reported
as if they also covered CI — which they structurally never could. This is
the actual bug, independent of the specific PR.

### Mitigating fact, independently verified

PR #191's docs-only diff (1 file, +167/-0) did **not** cause the CI
failures. `Core tests` and `Release gates` were already failing on every
commit to `main` for at least ~2 hours before PR #191 was even opened
(checked back through commits `6f9d153069`, `c6398f3815`, and earlier — all
failing; `Core tests` had failed on all 184 of its most recent tracked
runs). At the time, **9 separate `fix(ci)`/`fix(tests)` PRs** (#186–#194)
were open concurrently, each targeting a distinct failure class — a wider
remediation swarm than the "two cloud sessions" the original transcript
named (`task_4307de72`, `task_2db92229`), which may have been the subset
the operator was specifically tracking rather than the full picture.

**Net:** no content actually broke. The process was still non-compliant
(merged before its own checks resolved) and the report was inaccurate
("all pass" while unresolved/failed checks existed) — a doctrine violation
even though the outcome was harmless this time.

## What was fixed — PR #199, merged (`efe603e380`)

- **`scripts/git/pre_merge_check.sh`** now fetches and prints the PR's live
  per-check CI status (`gh pr view --json statusCheckRollup`, normalized
  across both GitHub Actions check-run shape and legacy commit-status
  shape into one `{name, bucket}` view).
  - **Hard-blocks** (`exit 1`) if any check is still pending/in-progress.
  - **Warns** (does not hard-block) on completed failures — some workflows
    in this repo run chronically red for reasons unrelated to a given
    diff — but the real status is always printed, so it can no longer be
    silently glossed over.
- **`CLAUDE.md`** → "Manual pre-merge check" section updated: documents the
  new gate and explicitly forbids reporting "all checks pass" / "all
  governance checks pass" without naming each check's actual state (pass /
  pending / failing-and-why-merging-anyway-is-safe).

Logic was verified against a mock payload replicating PR #191's exact
situation (one pending check, one already-failed check, plus both check-run
shapes) — it correctly blocks the pending case and flags the failure case.
Live-tested against real PR #199 CI data after merge, confirming the
normalization handles real GitHub Actions check-run payloads correctly.

### PR #199 itself hit the same chronic failures — confirmed unrelated

At check-in, PR #199 (a 2-file bash/markdown diff) also showed `Core
tests` / `Release gates` / `parse-sweep` as failing. Pulled the actual job
logs before merging to confirm these were the same pre-existing issues, not
something the new script broke:

- `Core tests` failed on
  `tests/planning/test_enhancement_contract_v21_integrity.py::test_supported_underfill_is_advisory_not_hard_fail`
  — a planning/contract test with zero relation to this diff, already the
  explicit target of open PR #194.
- `parse-sweep` failed on stub content in
  `atoms/corporate_managers/compassion_fatigue/**/zh-CN/CANONICAL.txt` —
  explicitly tagged in the error output as "the PR #1590 failure class," a
  named, already-tracked issue.

Governance review passed; 0 open review threads. Operator approved; PR
marked ready for review and squash-merged.

## What is NOT done — real remaining work

1. **Chronic `main` CI redness (`Core tests`, `Release gates`) is still
   unresolved as of this handoff.** Not this session's scope to fix — track
   via whichever of PRs #186–#194 (or their successors) are still open at
   pickup time, not this document.

2. **The new gate is a locally-run script, not a branch-protection
   requirement.** Nothing stops a future session from skipping
   `pre_merge_check.sh` entirely — it's still discipline-dependent, the
   same weakness that let the PR #191 incident happen in the first place
   (the mass-deletion guard was already mandatory and still got skipped in
   spirit by not being CI-aware). Worth raising with the owner: should
   `Core tests` / `Release gates` become actual required status checks in
   GitHub's branch-protection ruleset once they're stable, so the gate is
   enforced server-side instead of by agent discipline?

3. **`unsubscribe_pr_activity` for PR #199 was blocked by the auto-mode
   permission classifier** after merge. The scheduled check-in trigger was
   still successfully deleted, and the PR is merged so there's nothing left
   to act on — but the webhook subscription itself may still technically be
   live. Not verified closed; low-risk (merged PRs don't generate new CI
   events), but flag if a stray `<github-webhook-activity>` for #199 shows
   up in a future session.

4. **PR #191's own remaining-work items** (863-file zh-TW authoring
   backlog, unmeasured register-drift rate in the clean bucket) are
   unrelated to this handoff — see
   `artifacts/coordination/handoffs/zh_tw_quality_program_20260723.md` for
   that program's own status. This session did not touch translation work;
   it only investigated that PR's *merge process*.

## Key artifacts, for future reference

- Fixed script: `scripts/git/pre_merge_check.sh` (CI-status gate added
  2026-07-23)
- Doctrine: `CLAUDE.md` → "Manual pre-merge check" section
- Incident PR (the false-claim merge): #191, commit `6065db9764`
- Fix PR (this session's work): #199, commit `efe603e380`

## PR index

| PR | Scope |
|---|---|
| #191 | zh-TW quality program handoff — merged with unresolved/failing CI, claim inaccurate (content itself fine) |
| #199 | Pre-merge CI-status gate fix — merged clean, same pre-existing failures confirmed unrelated |

## Signal

`PREMERGE_CI_STATUS_GATE_COMPLETE_20260723`
