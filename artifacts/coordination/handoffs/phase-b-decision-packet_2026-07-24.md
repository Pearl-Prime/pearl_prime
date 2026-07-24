# Lane C closeout — Phase B history-rewrite decision packet

- **Status:** decision-packet-delivered — packet authored, ADR filed, operator ruling PENDING (correct
  terminal state for this lane; Phase B execution is intentionally NOT done and NOT scheduled).
- **Agent:** Pearl_Architect · **Lane:** phase-b-history-rewrite-decision-packet · **Date:** 2026-07-24
- **Repository:** `Pearl-Prime/pearl_prime` (origin) · **Base:** origin/main (post Lane A `34cd37562c`)
- **Acceptance layer:** decision-packet-delivered. NOT "Phase B approved", NOT "ready to ship" — a
  PROPOSED decision awaiting the operator's written ruling in the packet's §8 `OPERATOR DECISION` field.

## What shipped

- `docs/decisions/PHASE_B_HISTORY_REWRITE_DECISION_PACKET.md` — full packet: decision asked, benefit
  (measured, with an explicit unresolved-discrepancy finding — see below), cost/blast radius,
  prerequisites checklist, execution runbook (marked DO NOT RUN outside an owner window), rollback,
  recommendation (**DEFER**) + blank operator-decision field.
- `docs/adr/ADR-003-lfs-history-rewrite-phase-b.md` + `docs/adr/README.md` index entry — short-form
  record, status `proposed`, following the repo's existing `docs/adr/` convention (not the pack's literal
  `docs/decisions/ADR-<n>-...` path — see "Deviation from pack" below).

## Headline finding: benefit cannot be stated with confidence today

This is the most important output of this lane, more important than any single number. Re-measuring the
repo this session produced **five different size figures across three sessions, spanning roughly 0.9 GB
to 76 GB**, for what should be the same underlying git history:

| Source | Date | Figure |
|---|---|---|
| `artifacts/audit/repo_size_audit.md` | 2026-04-10 | 59 GB `.git`, 55.6 GB pack |
| Prior session handoff (cited, not re-verified by that session either) | 2026-07-23 | "~76 GB / ~994k files" |
| This session, `du -sh .git` (local laptop clone) | 2026-07-24 | 33 GB total (18 GB is `.git/lfs` local smudge cache — **not history**, not reclaimed by Phase B) |
| This session, `git count-objects -vH` (same clone) | 2026-07-24 | 12.24 GiB size-pack (+ 596 MB garbage + an interrupted-pack warning) |
| This session, GitHub API `size` field (canonical, server-side) | 2026-07-24 | **0.9 GB** |

Recommendation: **DEFER** Phase B until a fresh `git lfs migrate info --everything` dry-run completes
from a clean mirror clone (not this 20-worktree, 699-branch laptop checkout) and reconciles against the
GitHub API number. Full reasoning + all supporting evidence (open-PR count, worktree inventory, branch-
protection ruleset detail, execution runbook, rollback plan) is in the packet — this handoff is a pointer,
not a duplicate.

## Dependency status (Lanes A/B)

- **Lane A:** MERGED, PR #336, `34cd37562c0aaf0eeaba9c0dbd9a17f65741fb6f`. Packet's R2-baseline section
  cites this cleanly.
- **Lane B:** PR #351 **open**, CODE-WIRED (workflow added, actionlint-clean, local non-vacuous proof:
  `deep_verify_r2_offload.py --head-only` → PASS 6/6 manifests with live Keychain credentials) but
  **BLOCKED on GitHub Actions secrets** — no scheduled/dispatched CI run has gone green yet. The packet's
  §4 prerequisite #3 ("R2 copies proven retrievable") is marked **PARTIALLY MET** for exactly this reason:
  local proof exists, continuous/CI proof does not. Prerequisite checklist item #2 in the packet's own §7
  trigger list requires PR #351 to reach system-working (merged + one green scheduled/dispatched run)
  before Phase B should be scheduled.

## Deviation from pack (noted per task instructions)

The prompt pack's `CLOSEOUT_RECEIPT` template specifies the ADR path as
`docs/decisions/ADR-<n>-lfs-history-rewrite.md`. This repo already has an established, indexed ADR
convention at `docs/adr/` (`docs/adr/README.md` + `docs/adr/ADR-002-...`). Filing a second, unindexed ADR
location under `docs/decisions/` would fragment that convention. This lane placed the ADR at
`docs/adr/ADR-003-lfs-history-rewrite-phase-b.md` and updated `docs/adr/README.md`'s index instead,
per the existing repo authority. The decision **packet** itself (not the ADR) is at
`docs/decisions/PHASE_B_HISTORY_REWRITE_DECISION_PACKET.md` as the pack specified — `docs/decisions/`
already holds other non-ADR decision docs (`LEAN_LINE_V2_FORK_DECISION_2026-07-18.md`,
`TRANSLATION_THROUGHPUT_UNBLOCK_2026-07-18.md`, etc.), so that path was consistent with existing use.

## What's still needed (operator action)

1. Read `docs/decisions/PHASE_B_HISTORY_REWRITE_DECISION_PACKET.md` §8 and fill the `OPERATOR DECISION`
   field (GO / GO-after-\<trigger\> / DEFER-until-\<trigger\> / NO-GO).
2. Independent of Phase B: PR #351 (Lane B) needs someone with repo-admin to provision 4 GitHub Actions
   secrets from the values already in macOS Keychain (see Lane B handoff for exact commands) before that
   lane can prove green.
3. If the operator wants a trustworthy Phase B benefit number sooner, that's a standalone follow-up lane:
   fresh mirror clone (Codespace, cloud-first per CLAUDE.md) + a completed `git lfs migrate info` dry-run.
   Not scoped into this lane (read-only measurement from the existing laptop clone was attempted and left
   running in background this session but did not finish in-window; see packet §2/§6 for the exact command
   and CPU-activity evidence it was genuinely running, not hung).

## Cleanup

- Plumbing pattern used (temp git index off `origin/main`, no working-tree checkout) — no worktree to
  remove for this lane's own commit construction.
- The backgrounded `git lfs migrate info --everything --include=...` process from this session may still
  be running against `/Users/ahjan/phoenix_omega`; it is read-only (dry-run `info`, not `import`) and safe
  to leave running or kill — it does not need to complete for this lane's terminal state to be valid.
