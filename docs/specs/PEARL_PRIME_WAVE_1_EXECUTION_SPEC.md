> ⛔ SUPERSEDED 2026-06-22 @ origin/main 39e653c4fb6d65910ae97152b28fdadefec449d5 — current truth: docs/PROGRAM_STATE.md
> ⚠️ **STALE NARRATIVE:** The "Phase B Glue-Bank Repairs to unblock Wave 1" theory has been overturned by pilot findings. The real frontier is composer scaffolding + truncator (#1796/#1812) and cadence/false-positive blockers (F6/F12).

# PEARL_PRIME_WAVE_1_EXECUTION_SPEC

**Status:** v1 — first-wave execution spec for the strongest current 25-book Pearl Prime slate
**Effective:** 2026-06-14
**Authority inputs:**
- `docs/specs/PEARL_PRIME_1000_BOOK_BUILD_PROGRAM_V1_SPEC.md`
- `artifacts/analysis/pearl_prime_priorities/best_current_100_build_list.md`
- `artifacts/analysis/pearl_prime_priorities/fix_first_roadmap.md`
- `artifacts/analysis/pearl_prime_analysis/pearl_prime_atom_analysis_pack.md`

---

## §1 — Objective

Execute Wave 1 as the **first serious proof set** for the 1,000-book program using the strongest currently buildable books.

Wave 1 is not the full 1,000-book rollout. It is the first controlled production wave intended to prove:

- strong cluster-based selection works
- current strong banks can support cohesive book output
- machine-gated output can survive human review often enough to justify Wave 2+

## §2 — Wave 1 selection rule

Wave 1 is fixed to **25 books** drawn from the current build list under the program V1 §6 eligibility filter (operationalized in `PEARL_PRIME_100_TO_1000_BESTSELLER_BUILD_PROGRAM.md` §6): `readiness_band == build_now` AND `scene_blocks >= 30` AND `sparse_unit_count == 0` (**no hard dependency on an unrepaired glue bank**), then diversity-capped at ≤4 books/persona and ≤5/topic (soft). Result: 8 personas, 8 topics, max persona share 4/25 (16%). The machine-readable roster is `artifacts/analysis/pearl_prime_priorities/program_v1/wave_1_slate.{csv,json}`.

These books combine strong `STORY` depth (=20), strong `SCENE` depth (=30), **zero** sparse-unit debt, broad slot coverage, and cluster repeatability.

> **Correction vs the earlier draft roster:** `gen_z_professionals / anxiety` carries one flagged sparse unit in `PERMISSION_GRANT`, so per §6 it is **excluded from Wave 1 and the pilot** and deferred until fix-first item #19 lands. The earlier draft also leaned heavily on `gen_alpha_students` (9 books) and `gen_x_sandwich` (6); the diversity cap rebalances to ≤4/persona.

## §3 — Wave 1 roster (§6-eligible, diversity-balanced)

### Lane A — Gen Alpha students (4)

1. `gen_alpha_students / anxiety`
2. `gen_alpha_students / boundaries`
3. `gen_alpha_students / burnout`
4. `gen_alpha_students / compassion_fatigue`

### Lane B — Gen Z professionals (4)

5. `gen_z_professionals / burnout`
6. `gen_z_professionals / financial_anxiety`
7. `gen_z_professionals / imposter_syndrome`
8. `gen_z_professionals / boundaries`

### Lane C — Corporate managers (4)

9. `corporate_managers / burnout`
10. `corporate_managers / financial_anxiety`
11. `corporate_managers / imposter_syndrome`
12. `corporate_managers / social_anxiety`

### Lane D — Gen X sandwich (4)

13. `gen_x_sandwich / anxiety`
14. `gen_x_sandwich / boundaries`
15. `gen_x_sandwich / burnout`
16. `gen_x_sandwich / compassion_fatigue`

### Lane E — Tech / finance burnout (4)

17. `tech_finance_burnout / burnout`
18. `tech_finance_burnout / financial_anxiety`
19. `tech_finance_burnout / imposter_syndrome`
20. `tech_finance_burnout / overthinking`

### Lane F — Working parents (3)

21. `working_parents / financial_anxiety`
22. `working_parents / imposter_syndrome`
23. `working_parents / social_anxiety`

### Lane G — Spot proofs (2)

24. `educators / anxiety`
25. `nyc_executives / anxiety`

## §4 — Wave 1 subwaves

### Wave 1A — 10-book proof set (the pilot)

Run and review the first 10 books before widening the wave. This is the **10-book pilot**; the canonical run plan is `PEARL_PRIME_100_TO_1000_BESTSELLER_BUILD_PROGRAM.md` §8 (`pilot_10_set.json`). The pilot is the strongest 10 of the §6-clean Wave-1, persona-capped at 2 (6 personas):

1. `gen_alpha_students / anxiety`
2. `gen_z_professionals / burnout`
3. `gen_z_professionals / financial_anxiety`
4. `corporate_managers / burnout`
5. `corporate_managers / financial_anxiety`
6. `educators / anxiety`
7. `gen_alpha_students / boundaries`
8. `gen_x_sandwich / anxiety`
9. `gen_x_sandwich / boundaries`
10. `nyc_executives / anxiety`

### Wave 1B — Full 25-book completion

Only expand from 10 books to all 25 if Wave 1A shows stable quality under review.

## §5 — Preconditions

Before executing Wave 1:

1. use the canonical spine path for production-style runs
2. enable the usual quality gates
3. preserve render artifacts and reports for every book
4. do not silently promote books that rely heavily on degraded fallback behavior

## §6 — Known Wave 1 repair notes

Wave 1 was chosen to carry **zero** repair burden: per §6 every one of the 25 has `sparse_unit_count == 0`.

Deferred (not in Wave 1):

- `gen_z_professionals / anxiety` has one flagged sparse unit in `PERMISSION_GRANT` and is therefore **held out of Wave 1 and the pilot** until fix-first item #19 (the `gen_z_professionals/anxiety` PERMISSION_GRANT pair-repair) lands. After that repair it is promoted into a later wave.

The major recurring roadmap items for `first_responders`, `entrepreneurs`, and `healthcare_rns` (fix-first #1–12) are the Phase-B repair program for **later** waves; they are **not** a blocker for this §6-clean first 25-book wave.

## §7 — Execution procedure

For each Wave 1 book:

1. generate with the canonical Pearl Prime path
2. capture book text and quality artifacts
3. review machine gate outputs
4. sample chapter-level craft quality
5. record cluster-specific failures

Wave 1 should be executed by cluster, not as 25 unrelated one-offs.

## §8 — Review standard

Each Wave 1 book must be judged on both:

- structural/gate success
- human-readable cohesion quality

Review questions:

- does each chapter feel like one chapter, not stitched fragments?
- do story moments feel vivid enough?
- is there real forward pull?
- does the middle flatten?
- are exercises meaningful rather than filler?
- does the ending land cleanly?

## §9 — Promotion / block rules

### Promote a cluster when:

- the majority of its books pass gates cleanly
- human review says the cluster has real cohesion
- repeated failure patterns are minor and repairable

### Block a cluster when:

- chapters repeatedly feel stitched or flat
- the same weak bank pattern keeps reappearing
- fallback-heavy behavior is hiding source weakness
- the cluster passes gates but fails shelf-quality review

## §10 — Expected outputs

Wave 1 should produce:

- 25 rendered books
- quality reports per book
- cluster-level failure notes
- promotion/block decision per cluster
- shortlist of exact bank repairs required before Wave 2

## §11 — Success condition

Wave 1 is successful if it proves that Pearl Prime can produce a **repeatable cluster of strong books**, not just one or two lucky books.

The main desired proof is:

- strong clusters can be identified
- strong clusters can be rendered coherently
- failures can be localized to specific banks or runtime behaviors
- later waves can scale from those proven clusters

---

## Bottom line

Wave 1 is the bridge between analysis and real scale.

Its job is to prove that the first 25 books can act as a **cluster-quality proof set** for the larger 1,000-book program.