# 01 — Wave 0: Durability + Substrate Lock (Pearl_DevOps)

EXECUTE. Do not stop at summary or plan. Turn ends only on the signals below or one
concrete BLOCKER with evidence. **The Wave-1 branch is local-only — preserving it
offline is the first, non-negotiable act (unpushed work gets wiped).**

```
STARTUP_RECEIPT
AGENT: Pearl_DevOps (lane 01)
TASK: Preserve agent/pearl-prime-perfect-books-wave1 to the offline remote; lock substrate + verify every Wave-2 premise
SUBSYSTEM: pearl_devops (authority: docs/GITHUB_OPERATIONS_FRAMEWORK.md; CLAUDE.md Non-Negotiable Git Rules) + pearl_pm coordination
AUTHORITY_DOCS: docs/agent_brief.txt; this pack's INDEX.md; PEARL_PRIME_PERFECT_BOOKS_SPEC.md
WRITE_SCOPE: offline remote refs (preserve-only); artifacts/qa/perfect_books_wave2_20260718/SUBSTRATE_LOCK.md; artifacts/qa/perfect_books_wave2_20260718/lane01/; handoffs/perfect_books_wave2_substrate_2026-07-18.md
OUT_OF_SCOPE: rewriting the Wave-1 branch; the dirty shared tree (never checkout over it); hot coordination files; any atom/gate content
PROVENANCE: none (durability/verification-class)
BACKGROUND_SAFE: no   RESUME_SURFACE: SUBSTRATE_LOCK.md + the preserved offline ref
```

## NETWORK STALL RULE (no `timeout(1)` on this host)

SSH → `-o ConnectTimeout=8 -o BatchMode=yes`; HTTPS git → `-c http.lowSpeedLimit=1000
-c http.lowSpeedTime=10`. Any command silent 60s: kill, retry once, then record that
item BLOCKED-item and continue.

## MISSION A — PRESERVE WAVE-1 (do first)

1. Verify `agent/pearl-prime-perfect-books-wave1` tip is
   `9056df3354df6a84755fb47a38da2793f141efa9` (gates commit `16c431bb38`). Router
   snapshot — re-derive live; record any delta.
2. Confirm it is NOT already on `pearlstar_offline`
   (`git -c core.sshCommand="ssh -o ConnectTimeout=8 -o BatchMode=yes" ls-remote pearlstar_offline | grep perfect-books-wave1`).
3. Push the branch tip to `refs/heads/offline/pearl-prime-perfect-books-wave1-20260718`
   (a branch push, not a plumbing commit — the branch history is intact and clean):
   `git push pearlstar_offline agent/pearl-prime-perfect-books-wave1:refs/heads/offline/pearl-prime-perfect-books-wave1-20260718`.
4. Verify the ref exists on the remote at the expected SHA. Emit
   `perfect-books-wave1-preserved=<ref@full-sha>` into SUBSTRATE_LOCK.md.
   This closes the durability gap regardless of whether GitHub returns.

## MISSION B — SUBSTRATE LOCK (the Wave-2 truth file)

Produce `artifacts/qa/perfect_books_wave2_20260718/SUBSTRATE_LOCK.md` with these
literal grep-able lines and evidence:

- `perfect-books-wave2-substrate=<github|pearlstar_offline>` — probe
  `git -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=10 ls-remote origin HEAD`
  (expected 403 suspended) + `gh auth status`.
- `perfect-books-wave2-baseline=<origin/main full sha>` (`git rev-parse origin/main`).
- `perfect-books-wave1-preserved=<ref@sha>` (from Mission A).

## DISCOVERY REPORT (verify each Wave-2 premise; a delta is SUCCESS)

1. Spec + Wave-1 closeout exist and read as INDEX describes; Wave-1 gates 35–37 wired
   in `drift-detectors.yml` (`grep -l acceptance_claim_language .github/workflows/drift-detectors.yml`).
2. Flagship goldens present + their parity gate exists
   (`scripts/ci/check_flagship_book_parity.py`) — record so lanes 02/03 can prove no
   golden drift.
3. `MATRIX.tsv` (100-book analysis) readable — this is Lane 03's cell-selection SSOT.
4. Line-edit scaffold `artifacts/qa/flagship_line_edit/README.md` present (Lane 03
   extends it).
5. Disk: `df -g /` free GB (<20 → lanes use plumbing only; <10 → dispatcher BLOCKER).
6. Already-done sweep: any handoff ≥2026-07-18 showing bank fill / line-edit /
   ONTGP already run → mark that lane RECONCILE-mode.

## SMOKE→PILOT→SCALE

Smoke = Mission A (preserve) + substrate probe. Pilot = discovery 1–4. Scale = full
report. Checkpoint after smoke so a kill leaves the preserved ref + partial lock.

## DO NOT

- Do not fix anything you find (record deltas; owning lanes act). Do not checkout/
  reset the dirty tree. Do not touch hot coordination files. Do not rewrite Wave-1.

## LANDING + CLEANUP + HANDOFF

Read/preserve lane: terminal state = REPORTED (SUBSTRATE_LOCK.md complete + Wave-1
preserved + handoff) or BLOCKED. Land SUBSTRATE_LOCK.md via the INDEX recipe onto
`offline/perfect-books-wave2-substrate-20260718`. Cleanup: temp index removed; no
scratch outside the proof root. Handoff:
`artifacts/coordination/handoffs/perfect_books_wave2_substrate_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT=Pearl_DevOps_lane01
WAVE1_PRESERVED=<offline/pearl-prime-perfect-books-wave1-20260718@full-sha>
SUBSTRATE=<github|pearlstar_offline>
BASELINE=<origin/main full sha>
PREMISES_VERIFIED=<n/n + deltas>
RECONCILE_MODE_LANES=<list or none>
DISK_FREE_GB=<n>
REPORT=artifacts/qa/perfect_books_wave2_20260718/SUBSTRATE_LOCK.md
HANDOFF=artifacts/coordination/handoffs/perfect_books_wave2_substrate_2026-07-18.md
SIGNAL=perfect-books-wave2-substrate=<github|pearlstar_offline>
NEXT_ACTION=dispatcher launches Wave 1 (Lane 02 bank fill + Lane 04 CI gates)
```
