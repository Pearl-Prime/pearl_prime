# 05 — Wave 2: Blind-10 Operator Prep Packet (Pearl_PM)

EXECUTE. Layer-4 `bestseller register` is the operator's blind read — an agent can
NEVER execute or claim it. This lane PREPARES the packet so the operator can run B1
when ready. Do not stop at summary/plan. Turn ends only on the signal below or one
concrete BLOCKER.

GATE CHECK: `grep "perfect-books-wave2-lineedit=" artifacts/coordination/handoffs/perfect_books_wave2_lineedit_2026-07-18.md` returns a full SHA (line-edit cells exist). Absent ⇒ STOP.

```
STARTUP_RECEIPT
AGENT: Pearl_PM (lane 05)
TASK: Assemble the operator blind-10 evaluation packet per protocol from the Wave-2 system-working cells + recent production ships; do NOT read/score/claim it
SUBSYSTEM: pearl_pm coordination (authority: docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md; docs/PEARL_PRIME_BLIND_10_OPERATOR_GUIDE.md)
AUTHORITY_DOCS: docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md; docs/PEARL_PRIME_BLIND_10_OPERATOR_GUIDE.md; PEARL_PRIME_PERFECT_BOOKS_SPEC.md §3.E (B1–B3) + §0 Layer-4 contract
WRITE_SCOPE: artifacts/qa/perfect_books_wave2_20260718/blind10_packet/; artifacts/qa/perfect_books_wave2_20260718/lane05/; handoffs/perfect_books_wave2_blind10_prep_2026-07-18.md
OUT_OF_SCOPE: reading/scoring the books (operator-only); editing manuscripts/banks; hot coordination files; any "register"/"bestseller" verdict
PROVENANCE: none (packet-assembly-class; the books' provenance is Lane 03's)
BACKGROUND_SAFE: no   RESUME_SURFACE: blind10_packet/ + offline ref
```

## DISCOVERY REPORT

1. Read the blind-10 protocol + operator guide IN FULL — the exact N, the
   blinding method (assembled-feel vs shelf-yes), the scoring sheet, the PASS bar
   (≥7/10 not-assembled-feel, ≥6/10 shelf-yes per spec §0).
2. From Lane 03's handoff, list the `system working` cells (ONTGP PASS). Combine with
   recent real production ships (e.g. the #1923 corporate_managers×burnout EPUB on
   main) to reach the protocol's N — record exactly which books, from where, and
   their acceptance layer. If fewer than N truly-eligible books exist, say so and
   prep a partial packet labeled as such (do not pad with draft/ineligible books).

## MISSION

Assemble the blind-10 packet: the blinded book set (rendered manuscripts/EPUBs the
operator reads), the protocol's scoring sheet (blank, ready), the read order, and a
one-page `HOW_TO_RUN.md` pointing to the operator guide. The packet is a **read-ready
kit**, nothing pre-scored. Explicitly mark it "Layer-4 pending operator read — no
register/bestseller claim exists until the operator records a verdict."

## SMOKE → PILOT → SCALE

Smoke: locate the protocol + confirm the scoring-sheet shape. Pilot: 1 blinded book
+ its sheet slot. Scale: the full N packet + HOW_TO_RUN + read order. Checkpoint
≤10 min. `open artifacts/qa/perfect_books_wave2_20260718/blind10_packet/` as the last
step so the operator sees it immediately.

## DO NOT

- Do NOT read, score, rank, or opine on the books (that voids the blind). Do NOT
  claim `bestseller register` / any Layer-4 result. Do NOT include draft/debug or
  ineligible books to hit N — label a short packet honestly. No `git add -A`.

## LANDING + CLEANUP + HANDOFF

Land the packet manifest + scoring sheet + HOW_TO_RUN (not multi-MB EPUBs — declare
those by path) via the INDEX recipe onto `offline/perfect-books-wave2-blind10-prep-20260718`
(or PR→merge if github). Cleanup: temp index removed; CLEANUP LEDGER in handoff.
Handoff: `artifacts/coordination/handoffs/perfect_books_wave2_blind10_prep_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT=Pearl_PM_lane05
PACKET=artifacts/qa/perfect_books_wave2_20260718/blind10_packet/ (opened via `open`)
BOOKS_IN_PACKET=<n>/<protocol N> (sources + acceptance layer each)
PARTIAL=<yes/no — if <N eligible, labeled>
SCORING_SHEET=<blank, ready — path>
ACCEPTANCE_LAYER=Layer-4 PENDING operator read (no register/bestseller claim made)
LANDED=<ref@full-sha | merge-sha>
CLEANUP_COMPLETE=yes
HANDOFF=artifacts/coordination/handoffs/perfect_books_wave2_blind10_prep_2026-07-18.md
SIGNAL=perfect-books-wave2-blind10-prep=<full-sha>
NEXT_ACTION=operator runs the blind-10 read; records verdict; PASS → first Layer-4 bestseller-register evidence; FAIL → line-edit + bank tickets (composer retune banned as first response, spec B3)
```
