# Buildability Dashboard — Phoenix Omega
Generated: 2026-04-22

## What Is This?
Truth panel: do we have the atoms needed to generate every catalog we want?
This is sourced from live repo data — run `python3 scripts/inventory/atom_coverage_audit.py` to refresh.

---

## Overall Coverage
- **Total CANONICAL.txt atoms** (all personas, all engines): 4,592
- **Canonical personas** (from canonical_personas.yaml): 11
- **Canonical topics** (from canonical_topics.yaml): 15
- **Total canonical combos**: 165 (11 personas × 15 topics)
- **Complete**: 165 (100.0%) — all combos have at least one engine with CANONICAL.txt
- **Partial**: 0
- **Missing**: 0

> Note: `catalog_generation_config.yaml` references 17 topics and 13 personas (includes `adhd_focus`, `mindfulness`,
> `midlife_women`, `nyc_executives`, `educators`). These extras exist in the atoms/ directory but are not in
> `canonical_topics.yaml` / `canonical_personas.yaml`. Audit uses canonical config as source of truth.

---

## By Persona

| Persona | Topics | Complete | Partial | Missing | Coverage% | Buildable? |
|---------|--------|----------|---------|---------|-----------|-----------|
| millennial_women_professionals | 15 | 15 | 0 | 0 | 100.0% | Yes |
| tech_finance_burnout | 15 | 15 | 0 | 0 | 100.0% | Yes |
| entrepreneurs | 15 | 15 | 0 | 0 | 100.0% | Yes |
| working_parents | 15 | 15 | 0 | 0 | 100.0% | Yes |
| gen_x_sandwich | 15 | 15 | 0 | 0 | 100.0% | Yes |
| corporate_managers | 15 | 15 | 0 | 0 | 100.0% | Yes |
| gen_z_professionals | 15 | 15 | 0 | 0 | 100.0% | Yes |
| healthcare_rns | 15 | 15 | 0 | 0 | 100.0% | Yes |
| gen_alpha_students | 15 | 15 | 0 | 0 | 100.0% | Yes |
| first_responders | 15 | 15 | 0 | 0 | 100.0% | Yes |
| gen_z_student | 15 | 15 | 0 | 0 | 100.0% | Yes |

---

## By Topic

| Topic | Personas | Complete | Partial | Missing | Coverage% | Buildable? |
|-------|----------|----------|---------|---------|-----------|-----------|
| anxiety | 11 | 11 | 0 | 0 | 100.0% | Yes |
| boundaries | 11 | 11 | 0 | 0 | 100.0% | Yes |
| burnout | 11 | 11 | 0 | 0 | 100.0% | Yes |
| compassion_fatigue | 11 | 11 | 0 | 0 | 100.0% | Yes |
| courage | 11 | 11 | 0 | 0 | 100.0% | Yes |
| depression | 11 | 11 | 0 | 0 | 100.0% | Yes |
| financial_anxiety | 11 | 11 | 0 | 0 | 100.0% | Yes |
| financial_stress | 11 | 11 | 0 | 0 | 100.0% | Yes |
| grief | 11 | 11 | 0 | 0 | 100.0% | Yes |
| imposter_syndrome | 11 | 11 | 0 | 0 | 100.0% | Yes |
| overthinking | 11 | 11 | 0 | 0 | 100.0% | Yes |
| self_worth | 11 | 11 | 0 | 0 | 100.0% | Yes |
| sleep_anxiety | 11 | 11 | 0 | 0 | 100.0% | Yes |
| social_anxiety | 11 | 11 | 0 | 0 | 100.0% | Yes |
| somatic_healing | 11 | 11 | 0 | 0 | 100.0% | Yes |

---

## Top 10 Gaps to Close

No missing canonical combos — all 165 persona × topic combos have complete atoms.
Gaps exist at the spec/roadmap level:

1. **Non-canonical topics in config but not in canonical_topics.yaml** — `adhd_focus`, `mindfulness` exist in catalog_generation_config.yaml but not canonical_topics.yaml. Audit them for atom coverage.
2. **Non-canonical personas** — `midlife_women`, `nyc_executives`, `educators` in catalog_generation_config.yaml but not canonical_personas.yaml. Add or formally retire.
3. **CJK atom coverage** — zh_TW, zh_CN, zh_HK, zh_SG brands have no atoms in atoms/ dir. Atoms exist only in English. CJK content relies on Qwen/CJK6 pipeline (not atom-based).
4. **Japan manga atoms** — No manga-specific atom structure exists. Japan dual-track (60% manga) has no atom coverage audit path.
5. **Korea webtoon atoms** — Same gap as Japan for webtoon track.
6. **312-brand target gap** — Registry shows 36 distinct brand entities (12 global + 24 zh). Path to 312 requires per-locale brand splits for all secondary/tertiary markets.
7. **Teacher mode generalization** — brands use named teachers (ahjan, joshin, etc.); generalized "teachings" variant not yet in config.
8. **QA findings registry** — config/quality/ has gate configs but no findings registry for tracking known issues.
9. **Bestseller analysis integration** — generate_full_catalog.py has --lane/--brand flags but no --scope all / --market flags.
10. **Atom coverage for catalog_generation_config personas** — 13 personas in catalog config vs 11 canonical; `educators` and one other not in canonical_personas.yaml.

---

## Market Buildability

| Market | Brands | Atom Coverage | Can Build? |
|--------|--------|---------------|-----------|
| US (en_US) | 12 | 100% — all canonical combos complete | Yes |
| Japan (ja_JP) | 12 | 100% English atoms; manga track: no atom path | Partial — manga needs separate pipeline |
| Korea (ko_KR) | 12 | 100% English atoms; webtoon: no atom path | Partial — webtoon needs separate pipeline |
| Germany/DACH (de_DE) | 12 | 100% English atoms; DE translation pipeline needed | Partial — translation pipeline required |
| France (fr_FR) | 12 | 100% English atoms; FR translation pipeline needed | Partial — translation pipeline required |
| Taiwan (zh_TW) | 18 | English atoms 100%; zh atoms via Qwen/CJK6 | Partial — CJK pipeline (Qwen, not atom-based) |
| China (zh_CN) | 18 | English atoms 100%; zh atoms via Qwen/CJK6 | Partial — CJK pipeline |
| Hong Kong (zh_HK) | 18 | English atoms 100%; zh atoms via Qwen/CJK6 | Partial — CJK pipeline |
| Spain (es_ES) | 12 | 100% English atoms; ES translation needed | Partial — translation pipeline required |
| LATAM (es_US) | 12 | 100% English atoms; ES-LATAM translation needed | Partial — translation pipeline required |
| Brazil (pt_BR) | 12 | 100% English atoms; PT-BR translation needed | Partial — translation pipeline required |
| Italy (it_IT) | 12 | 100% English atoms; IT translation needed | Partial — translation pipeline required |
| Singapore (zh_SG) | 18 | English atoms 100%; zh atoms via Qwen/CJK6 | Partial — CJK pipeline |
| Hungary (hu_HU) | 12 | 100% English atoms; HU translation needed | Partial — translation pipeline required |

---

## Phase 2 Readiness

- [x] All 11 canonical personas are 100% atom coverage (165/165 combos)
- [ ] All personas >= 90% atom coverage — TRUE for canonical set; non-canonical not yet audited
- [ ] Japan manga track configured — dual-track config exists in registry; manga atom pipeline TBD
- [ ] Bestseller engine connected to catalog build — generate_full_catalog.py has --lane/--brand; --scope all missing
- [ ] QA findings registry populated — config/quality/ has gates but no findings log
- [ ] CJK atoms / Qwen pipeline — exists as scheduled pipeline; not atom-based
- [ ] Non-canonical personas reconciled (midlife_women, nyc_executives, educators)
- [ ] Teacher mode generalized variant — currently named-teacher-only
