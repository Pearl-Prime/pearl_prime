# Operator Session Status — Wave-2 Blind-10

**APPROVED** — operator ratified: **blind-10 read approved**  
**Timestamp (UTC):** 2026-07-18T21:36:00Z  
**OPD row:** `OPD-W2-BLIND10-01`  
**SIGNAL:** `perfect-books-wave2-blind10=READY_FOR_OPERATOR`

## Honest ceiling (do not soften)

- Packet books = Layer 1 **`structurally clear`** only (register-gate PASS ≠ bestseller).
- **SYSTEM_WORKING_CELLS = 0** (Wave-2 line-edit: 3/3 ONTGP FAIL; those FAIL cells are not in this packet).
- Prior authored-candidate ceiling still holds for deep-edit work; this blind-10 samples the production shipping stream.
- Approval is to **run the prepared packet** — not to fake scores or claim Layer-4 bestseller register until the operator records a real verdict.

## Packet verification (facilitator, 2026-07-18)

| Check | Result |
|-------|--------|
| `HOW_TO_RUN.md` present + read | PASS |
| 10 Layer-1 books in `MANIFEST.tsv` | PASS (Book_01…Book_10) |
| All 10 source EPUBs on disk | PASS (bytes verified; none missing) |
| `SCORING_SHEET.md` blank | PASS (no agent scores) |
| Anonymization script + KEY sealed | PASS (`make_blind_copies.sh`; `KEY_SEALED.md` has 10 Book_IDs) |
| Blind reading copies materialised | PASS → `/tmp/blind10_reading_copies_20260718/Book_01.epub`…`Book_10.epub` |
| Agent invented scores / Layer-4 PASS | **NO** (forbidden; not done) |

### Packet paths

| Role | Path |
|------|------|
| Runbook | `artifacts/qa/perfect_books_wave2_20260718/blind10_packet/HOW_TO_RUN.md` |
| Read order | `…/READ_ORDER.md` |
| Blank scores (packet) | `…/SCORING_SHEET.md` |
| Blank scores (session capture) | `…/OPERATOR_SCORE_CAPTURE.md` |
| Sealed key (AFTER scoring) | `…/KEY_SEALED.md` |
| Manifest (AFTER scoring) | `…/MANIFEST.tsv` |
| Anonymize script | `…/make_blind_copies.sh` |
| Blind copies (local scratch) | `/tmp/blind10_reading_copies_20260718/` |
| Authority guide | `docs/PEARL_PRIME_BLIND_10_OPERATOR_GUIDE.md` |
| Wave audit | `artifacts/qa/perfect_books_wave2_20260718/FINAL_AUDIT.md` |

### Rubric polarity note

`SCORING_SHEET.md` / `OPERATOR_SCORE_CAPTURE.md` compute  
`felt_assembled_pass_rate` as count of **"no"** on Q1 (did **not** feel assembled).  
Use those sheets for verdict math. (Older guide prose that counts "yes" on Q1 conflicts with the bad/good semantics of "felt assembled" — do not resolve by inventing scores; resolve at verdict write time using the sheets.)

## What the operator must do next

1. **Stay blind:** do not open `MANIFEST.tsv`, `KEY_SEALED.md`, gate reports, or any `ONTGP_VERDICT.md` / persona×topic spoilers until all 10 rows are scored.
2. **Confirm reading copies** exist under `/tmp/blind10_reading_copies_20260718/` (re-run `make_blind_copies.sh` from repo root if missing).
3. **Read in order** Book_01 → Book_10 from that folder only (filenames are anonymized).
4. **Minimum sample each book:** Chapter 1 + Chapter 6 + Chapter 12 (~15–20 min/book; ~2.5–4 hrs total).
5. **Score immediately after each book** in `OPERATOR_SCORE_CAPTURE.md` (or `SCORING_SHEET.md`):
   - Felt assembled? (yes/no)
   - Sit next to trade-pub? (yes/no)
   - Strongest dimension (5–15 words)
   - Weakest dimension (5–15 words)
6. **Optional:** fill the 5-axis 1–5 table (not required for Layer-4 math).
7. **Compute rates** only after all 10 rows are filled (see polarity note above).
8. **Unseal** `KEY_SEALED.md`; cluster weakest/strongest patterns; route per operator guide Step 5.
9. **Write** `artifacts/qa/BLIND_10_VERDICT_<YYYY-MM-DD>.md` with an honest label: Layer-1 input pool; SYSTEM_WORKING_CELLS=0. Do not claim bestseller register from agent proxies.

## Facilitator constraints (this session)

- Prep / facilitate / capture scaffolding only.
- No invented blind scores.
- No Layer-4 PASS mark by agent.
- Offline scaffolding land: `pearlstar_offline` (GitHub still 403); explicit paths only — never `git add -A`.
