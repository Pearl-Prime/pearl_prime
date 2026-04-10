# Registry Coverage vs Catalog Demand

**Date:** 2026-04-10
**Project:** proj_state_convergence_20260328
**Scope:** registry/*.yaml × atoms/{persona}/{topic} × SOURCE_OF_TRUTH/teacher_banks/{teacher}/approved_atoms

---

## Summary

| Metric | Value |
|--------|-------|
| Canonical topics | 15 |
| Registry files present | **15/15** |
| Canonical personas | 11 (per canonical_personas.yaml) |
| On-disk personas | 13 (includes educators, nyc_executives) |
| Persona×topic combos (13 personas × 15 topics) | 195 |
| Combos with atoms >0 | 178/195 (91.3%) |
| Combos with 0 atoms | **17/195** (8.7%) |
| Teachers with all 13 approved slots | 1/13 (ahjan) |
| Teacher slot gaps (QUOTE + TEACHING) | **24** (12×2) |
| Catalog entries (full_catalog.csv) | **8,287** rows |

---

## Registry File Coverage

All 15 topic registry files exist:

| Topic | Registry File | Exists |
|-------|--------------|--------|
| anxiety | registry/anxiety.yaml | Yes |
| boundaries | registry/boundaries.yaml | Yes |
| burnout | registry/burnout.yaml | Yes |
| compassion_fatigue | registry/compassion_fatigue.yaml | Yes |
| courage | registry/courage.yaml | Yes |
| depression | registry/depression.yaml | Yes |
| financial_anxiety | registry/financial_anxiety.yaml | Yes |
| financial_stress | registry/financial_stress.yaml | Yes |
| grief | registry/grief.yaml | Yes |
| imposter_syndrome | registry/imposter_syndrome.yaml | Yes |
| overthinking | registry/overthinking.yaml | Yes |
| self_worth | registry/self_worth.yaml | Yes |
| sleep_anxiety | registry/sleep_anxiety.yaml | Yes |
| social_anxiety | registry/social_anxiety.yaml | Yes |
| somatic_healing | registry/somatic_healing.yaml | Yes |

---

## Persona Atom Coverage Gaps

These persona×topic combinations have **0 atoms** and will prevent book assembly:

| # | Persona | Missing Topics | Gap Count |
|---|---------|---------------|-----------|
| 1 | educators | burnout, financial_anxiety, imposter_syndrome, overthinking, sleep_anxiety, social_anxiety, somatic_healing | 7 |
| 2 | nyc_executives | burnout, financial_anxiety, imposter_syndrome, overthinking, sleep_anxiety, social_anxiety, somatic_healing | 7 |
| 3 | gen_z_student | compassion_fatigue, financial_anxiety, financial_stress | 3 |
| | **Total** | | **17** |

---

## Teacher Approved Atom Coverage

### Slot types with universal gaps

| Slot Type | Teachers with 0 atoms | Impact |
|-----------|----------------------|--------|
| QUOTE | 12/13 (all except ahjan) | Teacher-attributed quote injection will fail |
| TEACHING | 12/13 (all except ahjan) | Teaching-voice differentiation will fail |

### Teacher total approved atoms

| Teacher | Total Approved | Has all 13 slots? |
|---------|---------------|-------------------|
| ahjan | 314 | Yes (reference teacher) |
| adi_da | 260 | No — missing QUOTE, TEACHING |
| joshin–sai_ma (11 teachers) | 152 each | No — missing QUOTE, TEACHING |

---

## Assembly Risk Assessment

### Hard-Fail Combos

| Risk Type | Count | Examples |
|-----------|-------|---------|
| Persona has 0 atoms for topic | 17 combos | educators×burnout, nyc_executives×financial_anxiety, gen_z_student×compassion_fatigue |
| Teacher has 0 atoms in QUOTE | 12 teachers | joshin, junko, maat, master_feung, master_sha, master_wu, miki, omote, pamela_fellows, ra, sai_ma, adi_da |
| Teacher has 0 atoms in TEACHING | 12 teachers | Same 12 |

### Soft-Risk Combos

| Risk Type | Threshold | Affected |
|-----------|-----------|----------|
| Persona×topic < 15 atoms | 15 | gen_z_student: 12 combos at 11 atoms each |
| Teacher slot < 12 atoms | 12 | ahjan QUOTE (9 atoms) |

---

## Catalog Demand Notes

- **Catalog:** `artifacts/catalog/full_catalog.csv` has 8,287 data rows (header + 8,287 entries).
- The catalog references `brand_id`, `lane_id`, `teacher_id`, `topic_id`, `persona_id` per entry.
- **Catalog persona field uses brand-derived personas**, not always matching atoms/ directory names directly. Cross-mapping requires the identity_aliases.yaml resolver.
- Full catalog demand audit against atom pools requires running the assembly pipeline in dry-run mode — beyond this read-only audit scope.

---

## Recommendations

1. **P0 — Fill 17 zero-atom persona×topic combos** (educators: 7, nyc_executives: 7, gen_z_student: 3). These block assembly.
2. **P0 — Generate QUOTE and TEACHING atoms** for 12 teachers. These are universal slot gaps.
3. **P1 — Increase gen_z_student atom density** from 11 per topic to ≥21 (parity with other personas).
4. **P1 — Increase ahjan QUOTE count** from 9 to ≥15.
5. **P2 — Run dry-run assembly** against full catalog to identify exact catalog entries blocked by gaps.
