# Persona Atom Pool Audit

> **DEPRECATED 2026-06-06** — superseded by [`docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md`](../../docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md) **§8.1** (per-persona atom-type coverage) and **§8.3** (P×T 9-type completeness). This doc is retained as historical lineage per [`AGENT_FILE_PERSISTENCE_PROTOCOL.md`](../../docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md). For current 100% coverage state, query the SSOT + the gap matrix at [`artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv`](../qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv).

---

**Date:** 2026-04-10
**Project:** proj_state_convergence_20260328
**Scope:** atoms/ — 13 personas × 15 canonical topics

---

## Summary

| Metric | Value |
|--------|-------|
| Persona directories | 13 |
| Canonical topics | 15 |
| Total persona×topic combos | 195 |
| Combos with >0 atoms | **178** (91.3%) |
| Combos with 0 atoms | **17** (8.7%) — hard-fail risk |
| Fully covered personas (15/15 topics) | **10** |
| Partially covered personas | **3** (educators 8/15, gen_z_student 12/15, nyc_executives 8/15) |
| Total atoms (all .txt + .yaml) | **6,040** |

**Note:** atoms/ also contains `educators` and `nyc_executives` which are NOT in canonical_personas.yaml (11 canonical). The 13 personas listed here are all directories found on disk.

---

## Persona × Topic Atom Count Matrix

| Persona | anx | bnd | brn | cf | cou | dep | fa | fs | grf | imp | ovr | sw | sla | soc | som | Total |
|---------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-------|
| corporate_managers | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 315 |
| educators | 46 | 42 | **0** | 42 | 42 | 43 | **0** | 42 | 41 | **0** | **0** | 41 | **0** | **0** | **0** | 339 |
| entrepreneurs | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 315 |
| first_responders | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 315 |
| gen_alpha_students | 74 | 74 | 74 | 74 | 74 | 74 | 74 | 74 | 74 | 74 | 74 | 74 | 74 | 74 | 74 | 1,110 |
| gen_x_sandwich | 28 | 25 | 25 | 25 | 28 | 25 | 25 | 28 | 26 | 26 | 25 | 26 | 25 | 25 | 26 | 388 |
| gen_z_professionals | 49 | 49 | 49 | 49 | 49 | 49 | 49 | 49 | 49 | 49 | 49 | 49 | 49 | 49 | 49 | 735 |
| gen_z_student | 22 | 11 | 11 | **0** | 11 | 11 | **0** | **0** | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 143 |
| healthcare_rns | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 315 |
| millennial_women_professionals | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 345 |
| nyc_executives | 51 | 23 | **0** | 23 | 23 | 24 | **0** | 23 | 22 | **0** | **0** | 46 | **0** | **0** | **0** | 235 |
| tech_finance_burnout | 80 | 67 | 67 | 67 | 79 | 67 | 67 | 79 | 71 | 71 | 67 | 71 | 67 | 67 | 71 | 1,043 |
| working_parents | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 405 |

**Legend:** anx=anxiety, bnd=boundaries, brn=burnout, cf=compassion_fatigue, cou=courage, dep=depression, fa=financial_anxiety, fs=financial_stress, grf=grief, imp=imposter_syndrome, ovr=overthinking, sw=self_worth, sla=sleep_anxiety, soc=social_anxiety, som=somatic_healing

**Note:** Totals exclude "anchored" subdirectories (non-canonical topic found in gen_alpha_students: 35, healthcare_rns: 64, millennial_women_professionals: 80, working_parents: 84).

---

## Zero-Atom Combos (Hard-Fail Risk) — 17 total

| # | Persona | Topic | Assembly Impact |
|---|---------|-------|-----------------|
| 1 | educators | burnout | Cannot assemble books |
| 2 | educators | financial_anxiety | Cannot assemble books |
| 3 | educators | imposter_syndrome | Cannot assemble books |
| 4 | educators | overthinking | Cannot assemble books |
| 5 | educators | sleep_anxiety | Cannot assemble books |
| 6 | educators | social_anxiety | Cannot assemble books |
| 7 | educators | somatic_healing | Cannot assemble books |
| 8 | gen_z_student | compassion_fatigue | Cannot assemble books |
| 9 | gen_z_student | financial_anxiety | Cannot assemble books |
| 10 | gen_z_student | financial_stress | Cannot assemble books |
| 11 | nyc_executives | burnout | Cannot assemble books |
| 12 | nyc_executives | financial_anxiety | Cannot assemble books |
| 13 | nyc_executives | imposter_syndrome | Cannot assemble books |
| 14 | nyc_executives | overthinking | Cannot assemble books |
| 15 | nyc_executives | sleep_anxiety | Cannot assemble books |
| 16 | nyc_executives | social_anxiety | Cannot assemble books |
| 17 | nyc_executives | somatic_healing | Cannot assemble books |

---

## Per-Persona Summary

| Persona | Topics Covered | Total Atoms | Status |
|---------|---------------|-------------|--------|
| corporate_managers | 15/15 | 315 | Full |
| educators | 8/15 | 339 | 7 gaps |
| entrepreneurs | 15/15 | 315 | Full |
| first_responders | 15/15 | 315 | Full |
| gen_alpha_students | 15/15 | 1,110 | Full (highest) |
| gen_x_sandwich | 15/15 | 388 | Full |
| gen_z_professionals | 15/15 | 735 | Full |
| gen_z_student | 12/15 | 143 | 3 gaps (lowest) |
| healthcare_rns | 15/15 | 315 | Full |
| millennial_women_professionals | 15/15 | 345 | Full |
| nyc_executives | 8/15 | 235 | 7 gaps |
| tech_finance_burnout | 15/15 | 1,043 | Full |
| working_parents | 15/15 | 405 | Full |

---

## Observations

- **educators** and **nyc_executives** are NOT in `config/catalog_planning/canonical_personas.yaml` (which lists 11 personas). They exist on disk as legacy/extended personas.
- **gen_z_student** IS in canonical_personas.yaml and has the lowest atom count (143) and 3 topic gaps.
- All canonical personas except gen_z_student have ≥15/15 topic coverage.
- Some personas have "anchored" subdirectories (non-canonical topic) — not counted in totals.

---

## Recommendations

1. **P0 — Fill educators gaps (7 topics):** burnout, financial_anxiety, imposter_syndrome, overthinking, sleep_anxiety, social_anxiety, somatic_healing.
2. **P0 — Fill nyc_executives gaps (7 topics):** same set as educators.
3. **P1 — Fill gen_z_student gaps (3 topics):** compassion_fatigue, financial_anxiety, financial_stress.
4. **P1 — Increase gen_z_student density** from 11 atoms/topic to ≥21 (parity with other canonical personas).
5. **P2 — Clarify canonical persona list:** educators and nyc_executives exist on disk but are not in canonical_personas.yaml. Either add them or deprecate the directories.
