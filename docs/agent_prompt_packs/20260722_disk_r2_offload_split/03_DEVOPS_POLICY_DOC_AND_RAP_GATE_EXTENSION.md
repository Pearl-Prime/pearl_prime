# Lane 03 — "What Runs Where" Policy Doc + RAP Compliance Gate Extension

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_DevOps for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

PRE-REQUISITE CHECK (hard gate — do not skip):
- Lane 01 (local-disk-cleanup-r2-backup) AND Lane 02 (lfs-r2-offload-waves-2-4) from this
  same pack must both be in a TERMINAL state (MERGED or BLOCKED) before this lane starts.
  Check their handoffs:
  - artifacts/coordination/handoffs/local-disk-cleanup-r2-backup_2026-07-22.md
  - artifacts/coordination/handoffs/lfs-r2-offload-waves-2-4_2026-07-22.md
  If either is missing or shows an in-progress/non-terminal state, STOP — report BLOCKED
  (prerequisite lane not yet terminal), do not proceed on stale assumptions about what
  they'll eventually say.

STARTUP_RECEIPT:
- AGENT=Pearl_DevOps
- LANE=devops-what-runs-where-policy
- EXECUTION_MODE=github_actions (lands as a reviewed PR)
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=any
- PERSISTENCE_SURFACES=branch + PR
- RESUME_SURFACE=artifacts/coordination/handoffs/devops-what-runs-where-policy_2026-07-22.md

READ FIRST:
- docs/PROGRAM_STATE.md (re-verify SSOT line)
- docs/GITHUB_OPERATIONS_FRAMEWORK.md (the file you are extending — read its full
  section list; "Workflow matrix," "Canonical ownership," and "Secrets and runners" are
  the closest existing sections to slot a new "What runs where" section next to)
- docs/ROBUST_AGENT_PROTOCOL.md (RAP — the queue-first dispatch mandate this policy
  formalizes for the laptop-vs-Pearl-Star half)
- scripts/ci/check_rap_compliance.py (the gate you are extending — read its current
  checks in full: pscli status, direct-GPU-process patterns, --via-queue regression;
  understand its existing pattern-matching approach before adding a new check in the
  same style)
- config/artifacts/r2_buckets.yaml + scripts/artifacts/r2_sync.py (the R2 half of the
  policy — cite these, do not re-describe their internals; link to them)
- .github/workflows/manga-pipeline.yml and .github/workflows/pearl-news-daily.yml (live
  examples of `runs-on: [self-hosted, pearl-star*]` — cite these as the concrete proof
  that "GitHub Actions triggering Pearl Star execution" already works, not a proposal)
- artifacts/coordination/handoffs/local-disk-cleanup-r2-backup_2026-07-22.md and
  artifacts/coordination/handoffs/lfs-r2-offload-waves-2-4_2026-07-22.md (lanes 01/02's
  closeouts — cite their merge SHAs as evidence this policy is backed by real landed
  work, not just aspiration)

LIVE STATE RECONCILIATION:
- `git fetch origin`; confirm origin/main SHA.
- Re-read docs/GITHUB_OPERATIONS_FRAMEWORK.md's CURRENT section structure (it may have
  changed since 2026-07-22) and insert the new section in whatever location makes
  sense given its actual current shape — do not assume the section list above is
  unchanged.
- Confirm `scripts/ci/check_rap_compliance.py` current checks by reading the file live —
  this prompt describes it from a 2026-07-22 research pass; re-verify before extending.

PRE-REQUISITE CHECKS:
- lanes-01-02-terminal=<both handoffs exist and show MERGED or BLOCKED> (see hard gate
  above — repeated here as the machine-checkable form).

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- exact current structure of docs/GITHUB_OPERATIONS_FRAMEWORK.md (section headers);
- exact current checks in scripts/ci/check_rap_compliance.py (function names, what
  patterns each one matches, how it reports pass/warn/fail);
- confirm no open PR is already mid-flight on either file
  (`gh pr list --search "GITHUB_OPERATIONS_FRAMEWORK" --state open`,
  `gh pr list --search "check_rap_compliance" --state open`);
- proposed smallest safe batch (below).

PROVENANCE:
- research: NONE — this codifies an architecture that already exists and already runs
  (self-hosted Pearl Star runner, RAP, r2_sync.py); it documents and enforces, it does
  not invent.
- documents: docs/ROBUST_AGENT_PROTOCOL.md; docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md;
  docs/GITHUB_OPERATIONS_FRAMEWORK.md (the file being extended)
- builds_on: docs/GITHUB_OPERATIONS_FRAMEWORK.md (canonical DevOps authority doc, per
  SUBSYSTEM_AUTHORITY_MAP.tsv pearl_devops row — edit in place, do not create a new
  parallel "runs where" doc); scripts/ci/check_rap_compliance.py (canonical RAP gate,
  per CANONICAL_ARTIFACTS_REGISTRY.tsv `rap_compliance_gate` row — edit in place)
- inventory: EXTENDS both files; UNCHANGED everything else. This is the "memory is
  recall, not enforcement" promotion (agent_brief.txt §14): a lesson from this session
  (laptop disk/RAM bloat caused by local pipeline runs) becomes a documented policy AND
  a CI-enforced check, not just a chat transcript.

MISSION:
1. Add a "What Runs Where" policy section to docs/GITHUB_OPERATIONS_FRAMEWORK.md stating:
   laptop/Cursor = code editing only, no local pipeline/render/QA-batch execution;
   Pearl Star = all GPU/LLM heavy compute, dispatched via `pscli enqueue` per RAP, never
   raw Bash/SSH; GitHub Actions = orchestration layer, explicitly noting Pearl Star is
   itself a registered self-hosted runner (cite manga-pipeline.yml / pearl-news-daily.yml
   by name as live proof) so pushing a commit/PR can trigger heavy compute without
   touching the laptop; R2 (scripts/artifacts/r2_sync.py) = the only place binaries
   live, repo keeps sha256+key manifests only (cite lane 01/02's merge SHAs as the
   concrete instance of this policy already being applied).
2. Extend scripts/ci/check_rap_compliance.py with a new check (following its existing
   pattern-matching style) that flags any new/changed script under scripts/ or
   phoenix_v4/ that writes artifact binaries (image/audio/video/render output) directly
   under artifacts/**, assets/**, or brand-wizard-app/public/** without a corresponding
   call into scripts/artifacts/r2_sync.py or scripts/pearl_star/bin/pscli — mirroring
   how the existing checks flag direct-GPU-process patterns. WARN-only initially (per
   spec §Phase-1-pattern used elsewhere in this repo — e.g. variant-coverage-gate.yml's
   warn-then-strict flip), not a hard fail, since this is a repo-wide behavior change
   that will surface many pre-existing scripts on day one.
3. Update artifacts/coordination/ACTIVE_WORKSTREAMS.tsv `ws_lfs_setup_20260410` row (or
   file a new row if this genuinely doesn't fit that workstream's scope — check first)
   to reflect the policy doc + gate extension as landed.
4. Update docs/PROGRAM_STATE.md DevOps/repo-hygiene section.

DELIVERABLES:
- docs/GITHUB_OPERATIONS_FRAMEWORK.md: new "What Runs Where" section.
- scripts/ci/check_rap_compliance.py: new WARN-only check + accompanying test (mirror
  existing test file for this script if one exists; if not, note that gap rather than
  silently skipping test coverage).
- Mutation test proof (agent_brief.txt §14): add a throwaway script under a scratch path
  that DOES write binaries locally without R2/pscli, confirm the new check goes RED/WARN
  on it, then remove the throwaway script — document this in the PR description as the
  gate's own proof of working.
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv row update.
- docs/PROGRAM_STATE.md update.

SMALLEST SAFE BATCH:
- smoke: draft the policy doc section text only, get it structurally right (headers,
  cross-references to RAP/R2/spec docs), commit that alone first if splitting into two
  PRs reduces risk.
- pilot: add the RAP gate check as WARN-only, run it against the full current repo once
  to see how much it flags — if it's an unreasonable flood (hundreds of pre-existing
  hits), that's a finding for the PR description, not a reason to weaken the check
  (agent_brief.txt §15 — fix the ruler only for provable false positives, never bend it
  to reduce noise).
- scale: not really applicable here — this is an inherently small lane (one doc section
  + one gate check). If it starts sprawling into "also fix the hundreds of flagged
  scripts," STOP — that's a separate, larger follow-on lane, not this one's scope.

HANG PREVENTION:
- poll interval: 5 minutes (this is a small/fast lane; CI run time is the main wait).
- no-progress rule: check CI logs after two unchanged polls.
- hard stall rule: BLOCKED after three unchanged polls.
- max window: 45 minutes — this should be a small, fast lane; if it's sprawling past
  that, you've likely scope-crept into fixing flagged scripts (see SMALLEST SAFE BATCH
  note above) — pull back to just the doc + gate + mutation-test proof.

TESTS/PROOFS:
- `python3 scripts/ci/check_rap_compliance.py` — runs clean (or WARN-only as designed)
  against current origin/main.
- Mutation test: throwaway violation script → RED/WARN → removed → clean again.
- Any existing pytest suite for check_rap_compliance.py, if present, still passes.
- Proof root: the PR description itself (this lane doesn't need a separate artifacts/
  proof directory — it's a doc + gate, not a data-producing pipeline).

DO NOT:
- Do NOT make the new RAP-gate check a hard FAIL on first landing — WARN-only, per the
  established warn-then-strict-flip pattern elsewhere in this repo (avoids an
  unreviewed repo-wide break).
- Do NOT create a second "what runs where" doc — extend docs/GITHUB_OPERATIONS_FRAMEWORK.md
  in place; it is the canonical pearl_devops authority doc per
  SUBSYSTEM_AUTHORITY_MAP.tsv.
- Do NOT fork scripts/ci/check_rap_compliance.py into a new script — extend it in place
  per CANONICAL_ARTIFACTS_REGISTRY.tsv (`rap_compliance_gate`, edit_not_recreate=YES).
- Do NOT attempt to fix every script the new gate flags in this same lane — that's
  scope creep into a much larger follow-on; name the flagged count in the PR and stop.
- Do NOT start this lane before lanes 01 and 02 are terminal (hard gate above).

LANDING CONTRACT:
- MERGED: PR opened, required checks green, squash-merged, signal emitted.
- BLOCKED: exact blocker, evidence, work pushed to a remote branch.

CLEANUP LEDGER REQUIRED:
- worktree: none expected (small doc+code lane, can likely work in a lightweight
  clone); removed if created.
- local branch: deleted after merge.
- remote branch: deleted after squash-merge.
- scratch files: the mutation-test throwaway script must be removed before final commit
  (verify it's not in the staged diff) — this is exactly the kind of debug instrumentation
  agent_brief.txt §17 requires to be fully reverted before commit.
- background jobs: none.
- held artifacts: none expected.

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/devops-what-runs-where-policy_2026-07-22.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_DevOps
- LANE: devops-what-runs-where-policy
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL: devops-runs-where-policy=<merge-sha>
- PROOF_ROOT: <PR URL + mutation-test description>
- TESTS: <check_rap_compliance.py run + mutation test result>
- CLEANUP: <ledger above>
- HANDOFF: artifacts/coordination/handoffs/devops-what-runs-where-policy_2026-07-22.md
- NEXT_ACTION: <e.g. "flagged-script remediation is a separate follow-on lane, count=<N>,
  not started here">
```
