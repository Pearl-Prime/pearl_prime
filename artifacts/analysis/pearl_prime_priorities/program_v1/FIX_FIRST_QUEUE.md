# Fix-First Recurring-Bank Repair Queue (prioritized)

**Governed by:** `docs/specs/PEARL_PRIME_100_TO_1000_BESTSELLER_BUILD_PROGRAM.md` §7 + `PEARL_PRIME_1000_BOOK_BUILD_PROGRAM_V1_SPEC.md` §10.
**Source data:** `artifacts/analysis/pearl_prime_priorities/fix_first_roadmap.csv` (30 items).
**Machine-readable:** `fix_first_queue.csv` / `fix_first_queue.json` (this dir).

## Prioritization

1. number of top-100 books a repair unblocks/strengthens
2. recurrence across many topics for one persona
3. glue bank vs core story bank
4. whether the affected book is already near-buildable

Recurring persona-slot programs outrank one-off repairs. **Tier:** atom authoring + glue-bank repairs = Pearl_Writer / Pearl_Editor (Claude subagents, Tier 1, operator-present); personas are en-US; no paid LLM API.

## Phase B — glue banks first (PERMISSION / PIVOT / TAKEAWAY / THREAD)

The operator's named lead order: **first_responders → entrepreneurs → healthcare_rns** (then millennial_women_professionals). One glue-bank program strengthens many top-100 books at once.

| Pri | Program | Lift | Top-100 affected | Topics |
|---:|---|---:|---:|---:|
| 1 | first_responders / PERMISSION | 1216 | 9 | 15 |
| 2 | first_responders / PIVOT | 1216 | 9 | 15 |
| 3 | first_responders / TAKEAWAY | 1216 | 9 | 15 |
| 4 | first_responders / THREAD | 1216 | 9 | 15 |
| 5 | entrepreneurs / PERMISSION | 1125 | 8 | 15 |
| 6 | healthcare_rns / PERMISSION | 1042 | 7 | 16 |
| 7 | healthcare_rns / PIVOT | 1042 | 7 | 16 |
| 8 | healthcare_rns / TAKEAWAY | 1042 | 7 | 16 |
| 9 | healthcare_rns / THREAD | 1042 | 7 | 16 |
| 10 | entrepreneurs / PIVOT | 1020 | 7 | 14 |
| 11 | entrepreneurs / TAKEAWAY | 1020 | 7 | 14 |
| 12 | entrepreneurs / THREAD | 1020 | 7 | 14 |
| 13 | millennial_women_professionals / PERMISSION | 866 | 5 | 16 |
| 14 | millennial_women_professionals / PIVOT | 866 | 5 | 16 |
| 15 | millennial_women_professionals / TAKEAWAY | 866 | 5 | 16 |
| 16 | millennial_women_professionals / THREAD | 866 | 5 | 16 |
| 17 | gen_z_professionals / PERMISSION_GRANT | 423 | 1 | 1 |

## Phase C — STORY / SCENE depth for the strongest families

| Pri | Program | Lift | Top-100 affected | Topics |
|---:|---|---:|---:|---:|
| 18 | gen_z_student / SCENE | 381 | 0 | 15 |

## Near-buildable pair repairs (held back by glue banks)

| Pri | Pair | Held back by | Lift |
|---:|---|---|---:|
| 19 | gen_z_professionals / anxiety | PERMISSION_GRANT | 319 |
| 20 | entrepreneurs / burnout | PERMISSION·PIVOT·TAKEAWAY·THREAD | 283 |
| 21 | entrepreneurs / financial_anxiety | PERMISSION·PIVOT·TAKEAWAY·THREAD | 283 |
| 22 | entrepreneurs / imposter_syndrome | PERMISSION·PIVOT·TAKEAWAY·THREAD | 283 |
| 23 | entrepreneurs / overthinking | PERMISSION·PIVOT·TAKEAWAY·THREAD | 283 |
| 24 | entrepreneurs / sleep_anxiety | PERMISSION·PIVOT·TAKEAWAY·THREAD | 283 |
| 25 | entrepreneurs / social_anxiety | PERMISSION·PIVOT·TAKEAWAY·THREAD | 283 |
| 26 | entrepreneurs / somatic_healing | PERMISSION·PIVOT·TAKEAWAY·THREAD | 283 |
| 27 | first_responders / burnout | PERMISSION·PIVOT·TAKEAWAY·THREAD | 283 |
| 28 | first_responders / compassion_fatigue | PERMISSION·PIVOT·TAKEAWAY·THREAD | 283 |
| 29 | first_responders / courage | PERMISSION·PIVOT·TAKEAWAY·THREAD | 283 |
| 30 | first_responders / depression | PERMISSION·PIVOT·TAKEAWAY·THREAD | 283 |

**Note:** item #19 directly unblocks the Wave-1-deferred `gen_z_professionals / anxiety` book. Phase-B glue-bank programs (#1–12) are the highest-leverage repairs because each lifts 7–9 top-100 books across 14–16 topics.
