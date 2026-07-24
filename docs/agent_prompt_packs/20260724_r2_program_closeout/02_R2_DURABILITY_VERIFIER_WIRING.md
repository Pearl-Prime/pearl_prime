# 02 — Lane B (Pearl_Int) — Wire the R2 Durability Verifier into a Scheduled GHA

```text
EXECUTE. Do not stop at plan, at PR-open, or at "workflow added but never run". End
MERGED with a green scheduled-run proof, or BLOCKED. You are Pearl_Int for Phoenix Omega.

THE GAP: scripts/ci/deep_verify_r2_offload.py already EXISTS and is complete (spec §4.3 —
fetches each manifest entry from R2, verifies ContentLength + sha256, --head-only mode,
returns nonzero on any missing/mismatched blob). check_render_progress_bytes.py's docstring
even promises "Weekly deep-verify fetches from R2 via scripts/ci/deep_verify_r2_offload.py".
But `grep -rl deep_verify_r2_offload .github/` returns EMPTY — it is wired into NOTHING.
Now that real families (Wave 3 = 267 files, Wave 4 = 79 files) live ONLY in R2 on main, the
promise that those blobs are actually retrievable has no enforcement. This is
unwired-verifier-as-working drift ([[feedback_memory_is_recall_not_enforcement]]): a lesson
(durability must be verified) that never got promoted to an enforced mechanism. You promote it.

Repo: Ahjan108/phoenix_omega_v4.8. Branch from origin/main: agent/r2-durability-verify-wire-20260724.
DEPENDS ON: Lane A (r2-program-reconciliation) MERGED first — so you verify against reconciled
manifests and a truthful PROGRAM_STATE. If Lane A is not yet merged, BLOCK and say so.

STARTUP_RECEIPT:
- AGENT=Pearl_Int
- LANE=r2-durability-verifier-wiring
- EXECUTION_MODE=github_actions (adds a scheduled workflow; proves via workflow_dispatch run)
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=fresh worktree/clone of origin/main
- RESUME_SURFACE=artifacts/coordination/handoffs/r2-durability-verify_2026-07-24.md

READ FIRST:
- docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md §4.2 (gate contract — DO NOT change) and §4.3
  (the deep-verify spec this wiring fulfills).
- scripts/ci/deep_verify_r2_offload.py — read main()/argparse in full; confirm the flags below
  still match (--manifest-dir default artifacts/manifests/lfs_offload, --head-only, --repo-root).
- scripts/artifacts/r2_sync.py lines ~100-122 — the R2 credential env names it actually reads:
  CLOUDFLARE_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ENDPOINT (via boto3
  aws_access_key_id/secret). NOTE THE MISMATCH below.
- .github/workflows/podcast-weekly.yml — the canonical weekly-cron + R2-secrets pattern to
  MIRROR (schedule cron, workflow_dispatch, env block with R2_* from secrets).
- docs/ROBUST_AGENT_PROTOCOL.md — this job touches no GPU/LLM, but the RAP artifact-write
  detector (#73, on main) may flag workflow writes; read so you don't trip it.
- docs/reference GHA startup_failure note ([[reference_gha_startup_failure_actionlint.md]]):
  a red/0-jobs run = startup_failure; run actionlint locally — PyYAML-valid is NOT GHA-valid.

LIVE-TRUTH RECONCILIATION (CLAIMS — re-verify):
- git fetch; confirm Lane A merged (`gh pr list --search "r2-program-reconcile" --state merged`).
- `grep -rl deep_verify_r2_offload .github/` still empty (if a sibling already wired it, STAND
  DOWN, reconcile, report the delta — do not duplicate; [[feedback_sibling_session_collision]]).
- `gh secret list` (or ask operator) — confirm which R2 secret NAMES exist in repo Actions
  secrets. podcast-weekly.yml uses R2_ACCOUNT_ID; r2_sync.py reads CLOUDFLARE_ACCOUNT_ID.
  **Resolve this env-name mismatch explicitly** — either map the secret to the name the code
  reads (env: CLOUDFLARE_ACCOUNT_ID: ${{ secrets.R2_ACCOUNT_ID }}), or note the code path.
  Do NOT guess; a wrong env name = silent auth fail = false-green vacuous PASS.
- Confirm manifests exist: `ls artifacts/manifests/lfs_offload/*.tsv` — if empty, the verifier
  prints "no manifests found (PASS vacuous)". A vacuous pass is NOT proof; you need real manifests
  present (Lane A confirmed Wave 3/4 manifests are on main) so the run actually fetches bytes.

DISCOVERY REPORT BEFORE ACTION:
- exact verifier CLI you'll invoke; the R2 secret names that exist vs. what the code reads +
  your resolution; how many manifest entries a real run will fetch (so a green run is provably
  non-vacuous); the cron cadence choice (weekly, spec §4.3) + why.

PROVENANCE:
- research: NONE. documents: spec §4.3; podcast-weekly.yml pattern.
- builds_on: deep_verify_r2_offload.py (exists), r2_sync.py auth, spec §4.3.
- inventory: EXTENDS — adds ONE new workflow file; changes NO Python. If you find the verifier
  is actually broken (not just unwired), that's a stale-premise correction: fix it in this PR
  and say so, or split into a prereq lane if the fix is large.

MISSION:
1. Add .github/workflows/r2-offload-deep-verify.yml — weekly `schedule: cron` (pick a low-traffic
   slot distinct from podcast-weekly/nightly-regression) + `workflow_dispatch` (so you can prove
   it NOW without waiting a week). Env block wires R2 creds from repo secrets to the exact names
   deep_verify_r2_offload.py / r2_sync.py read (resolve the mismatch from reconciliation). Step:
   `python3 scripts/ci/deep_verify_r2_offload.py --manifest-dir artifacts/manifests/lfs_offload`
   (full sha256 mode, NOT --head-only, for the durability guarantee — head-only is a fast-path
   variant you may add as a SEPARATE more-frequent job if useful, but the authoritative weekly
   run downloads bodies and checks sha256).
2. PROVE IT: trigger `gh workflow run r2-offload-deep-verify.yml` on your branch (workflow_dispatch),
   watch it to completion (`gh run watch`), and confirm it prints
   "R2-OFFLOAD DEEP-VERIFY: PASS (N manifest(s))" with N>0 (non-vacuous) and exit 0. Capture the
   run URL + log tail as proof. A workflow that was added but never executed is CONFIG-EXISTS,
   NOT EXECUTED-REAL — do not report done on the file alone.
3. If the real run FAILS (a manifest entry missing from R2, sha256 mismatch): that is a REAL
   durability finding — the offload's round-trip proof was trusted but the blob isn't actually
   retrievable. Do NOT weaken the verifier or switch to --head-only to make it green. Capture the
   failing entry, mark BLOCKED, and surface to the operator: an offloaded family may be
   unrecoverable. This is exactly the failure the wiring exists to catch.
4. Update check_render_progress_bytes.py's docstring/comment ONLY if it now points to a real
   scheduled job (turn the aspirational "weekly deep-verify fetches..." into a concrete
   ".github/workflows/r2-offload-deep-verify.yml" reference). Do NOT change its gate logic.
5. Update ws_lfs_setup_20260410 evidence + PROGRAM_STATE DevOps note: durability verifier now
   SCHEDULED + proven (cite run URL). Layer-honest: "system-working (scheduled + one green
   non-vacuous run)", not "durability guaranteed forever".

TESTS/PROOFS:
- actionlint on the new workflow BEFORE push (GHA-validity, not just YAML).
- The workflow_dispatch run itself is the mutation test: PASS with N>0 manifests, exit 0, bytes
  actually fetched from R2. Run URL is the proof artifact.
- Governance preflight (pre_merge_check.sh + pr_governance_review.py) — name each check status.
- CLAUDE.md Mandatory Preflight before push.

DO NOT:
- Do NOT change check_render_progress_bytes.py's 50KB floor or manifest-verify logic (manga gate,
  separate agent's contract — spec §4.2). Docstring pointer only.
- Do NOT use --head-only as the authoritative weekly run (that skips sha256 body verification —
  it would false-green a corrupted-but-present blob).
- Do NOT report the workflow "working" on file-add alone — a scheduled run must have executed green.
- Do NOT hardcode credentials; secrets only. Never put R2 keys in the workflow file or logs.

LANDING CONTRACT:
- MERGED: workflow file + proven green workflow_dispatch run (URL captured), governance green
  (named), squash-merged, signal emitted.
- BLOCKED: exact blocker (auth env mismatch unresolved, a real R2-durability failure, missing
  secret) + evidence + branch pushed to remote.

CLEANUP LEDGER: worktree removed post-merge; local + remote branch deleted after merge; the
workflow_dispatch test run is expected/kept as proof (name it); no background jobs.

HANDOFF: artifacts/coordination/handoffs/r2-durability-verify_2026-07-24.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Int
- LANE: r2-durability-verifier-wiring
- STATUS=MERGED|BLOCKED
- BRANCH: agent/r2-durability-verify-wire-20260724
- PR: / MERGE_SHA:
- SIGNAL: r2-durability-verify=<merge-sha>
- ACCEPTANCE_LAYER: system-working (scheduled + ONE green non-vacuous run, URL=<...>). NOT
  "durability guaranteed" — it's now continuously CHECKED, which is the honest claim.
- PROOF: <workflow run URL + "PASS (N manifests)" tail, N=<count>>
- TESTS: <actionlint + per-check governance status, named>
- CLEANUP: <ledger>
- HANDOFF: artifacts/coordination/handoffs/r2-durability-verify_2026-07-24.md
- NEXT_ACTION: "Lane C (Phase B decision packet) can cite a truthful + continuously-verified R2
  baseline"
```
