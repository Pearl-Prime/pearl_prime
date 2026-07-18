# Finding — `one_hour_book` +23% word-overshoot at 8 chapters (depth-budget handoff)

**Author:** Pearl_Prime, 2026-06-15 · **Owner of fix:** duration-derivation / depth-budget lane
(NOT chapter-count). **Surfaced by:** PR #1612 (Option S). **Evidence:**
[`../../qa/duration_ladder_subset_proof_20260615/INDEX.md`](../../qa/duration_ladder_subset_proof_20260615/INDEX.md).

## Symptom

`one_hour_book` (`word_range: [8000, 10000]`, `chapter_count_default: 8`) renders **12291 words at
8 chapters** (gen_z × anxiety). Subsetting helped (12ch/13095w → 8ch/12291w; F1 39→28) but the book
is still **+23% over** the 10000 ceiling. The chapter-count lever cannot close this gap.

## Root cause — the atom floor, not the chapter count

Each rendered chapter has a practical **minimum word floor** (~1500w) set by the 10-slot
`SOMATIC_10_SLOT_GRID` and per-atom minimum render sizes — largely **independent of the per-chapter
word budget** (the budget can scale chapters *up* but not below their atom floor). So:

| chapters | ≈ rendered words | vs one_hour band [8000,10000] |
|:--:|:--:|:--|
| 5 (`[1,4,7,10,12]`) | ~7,500 | UNDER (−6%) |
| 8 (`[1,3,4,6,7,9,10,12]`) | ~12,300 | OVER (+23%) |

The 8000–10000 band falls in the **gap between the 5ch and 8ch atom floors**. No chapter count hits
it cleanly at the current atom density. `chapter_count_default: 8` is correct per SSoT (AUTO-PLAN-SSOT-01);
the mismatch is between that count, the word_range, and the atom floor.

## Out of the chapter-count envelope

`config/format_selection/format_registry.yaml` `word_range`/`word_budget` is **out of scope** for the
chapter-count lane (per the originating brief). The fix lives in the **depth-budget / duration-derivation**
subsystem. (Note: PR #1632 already did book-wide depth-dedup for *F1*; this is a distinct *word-count* vs
*word_range* reconciliation.)

## Options for the depth-budget / duration-derivation owner

1. **Per-chapter word cap under depth pass** — trim 8ch chapters to ~1100w each (~8800 total, in-band).
   Cleanest if the depth pass can enforce a per-chapter ceiling without starving slots. **Recommended.**
2. **Reconcile `word_range` upward** — e.g. 10000 → ~12500 to match the 8ch atom floor (DURATION-DERIVATION-01
   re-derivation; changes the advertised "1-hour" minutes → needs the duration owner's sign-off).
3. **Drop to a 6-chapter subset** for one_hour (≈9000–10000w) — but 6 ≠ `chapter_count_default` 8, so it
   would require also changing the declared count (SSoT change) — heavier.
4. **Accept +23%** as the honest minimum for an 8-chapter book at this atom density, and relabel duration.

Recommendation: **Option 1** (per-chapter cap) or **Option 2** (word_range re-derivation). Either is a
small, contained change owned outside the chapter-count lane.
