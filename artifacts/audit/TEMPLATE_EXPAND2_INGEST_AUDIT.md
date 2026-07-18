# template_expand2/ Ingest Audit

**Project:** `proj_state_convergence_20260328`
**Subsystem:** `core_pipeline`, `teacher_mode`
**Date:** 2026-04-11
**Auditor:** Pearl_Dev + Pearl_Editor + Pearl_Architect

---

## Source Summary

| Metric | Value |
|--------|-------|
| Total files | 44 |
| Zip archives | 21 |
| Text atom batches | 16 |
| Chat logs | 5 |
| Markdown specs | 3 |
| Total extracted size | 12 MB |

---

## TYPE A: V2 Somatic Template Library

**Source:** `qaudiobook_template_v2_somatic.zip` (590 KB)
**Extracted to:** `template_expand2/_extracted/qaudiobook_template_v2_somatic/sections_somatic_v2/`

| Metric | Measured |
|--------|----------|
| Chapters | 12 (chapter_01 – chapter_12) |
| Sections per chapter | 10 |
| Variants per section | 5 (f1 – f5) |
| Total YAML files | 600 (+ 1 registry.yaml = 601 total) |
| Total words | 92,325 |
| Average words per section | 153 |
| Content field | `content` (block scalar) |
| Section naming | `section_NN_type` (e.g. section_01_hook, section_06_teacherdoctrine) |
| Variant naming | `fN.yaml` (e.g. f1.yaml, f2.yaml) |
| Registry file | `registry.yaml` — section metadata with fingerprints |

**Section type mapping (matches legacy_template_index.yaml):**

| Dir name | Slot type |
|----------|-----------|
| section_01_hook | HOOK |
| section_02_scene | SCENE |
| section_03_reflection | REFLECTION |
| section_04_exercise | EXERCISE |
| section_05_scene | SCENE (2nd) |
| section_06_teacherdoctrine | TEACHER_DOCTRINE |
| section_07_reflection | REFLECTION (2nd) |
| section_08_exercise | EXERCISE (2nd) |
| section_09_scene | SCENE (3rd) |
| section_10_integration | INTEGRATION |

**Verdict:** COMPLETE 12×10×5 structure. This is the primary import target for the section_packet_composer.

---

## TYPE B: Persona Atom Batches (loose text files)

| File | Persona | Topics | Atoms (est.) | Words | Already in atoms/? |
|------|---------|--------|-------------|-------|--------------------|
| gen_alpha_students__anxiety__false_alarm__BATCH.txt | gen_alpha_students | anxiety | 20 | 1,955 | PARTIAL — 1,146 existing |
| gen_alpha_students__core__PILOT_BATCH.txt | gen_alpha_students | core/multi | 60 | 4,980 | PARTIAL |
| gen_alpha_students__grief_topic__grief__CANONICAL.txt | gen_alpha_students | grief | 20 | 1,613 | YES — grief dir exists |
| gen_alpha_students__grief_topic__watcher__CANONICAL.txt | gen_alpha_students | grief | 20 | 1,469 | YES |
| gen_z_professionals__grief_topic__grief__CANONICAL.txt | gen_z_professionals | grief | 20 | 1,423 | YES — grief dir exists |
| gen_z_professionals__grief_topic__watcher__CANONICAL.txt | gen_z_professionals | grief | 20 | 1,383 | YES |
| healthcare_rns__grief_topic__grief__CANONICAL.txt | healthcare_rns | grief | 20 | 1,428 | YES — grief dir exists |
| healthcare_rns__grief_topic__watcher__CANONICAL.txt | healthcare_rns | grief | 20 | 1,398 | YES |
| midlife_women__anxiety_part2__80atoms.txt | midlife_women | anxiety | 80 | 2,935 | NO — new persona |
| midlife_women__boundaries__ALL__60atoms.txt | midlife_women | boundaries | 60 | 2,225 | NO |
| midlife_women__boundaries_financial_courage__ALL.txt | midlife_women | boundaries+financial+courage | 180 | 4,337 | NO |
| midlife_women__boundaries_financial_courage__ALL (1).txt | midlife_women | (duplicate of above) | — | 4,337 | DUPLICATE |
| midlife_women__compassion_fatigue_depression__ALL.txt | midlife_women | compassion_fatigue+depression | 120 | 3,193 | NO |
| midlife_women__financial_stress_courage__120atoms.txt | midlife_women | financial_stress+courage | 120 | 4,059 | NO |
| midlife_women__self_worth_grief_topic__ALL.txt | midlife_women | self_worth+grief | 80 | 2,053 | NO |
| old_chat_personas.txt | — | — | — | 28,702 | prompt_lineage — DO NOT IMPORT |

---

## TYPE C: Persona Collection Zips

| Zip | Persona | Files | Words | Already in atoms/? |
|-----|---------|-------|-------|--------------------|
| midlife_women_complete.zip | midlife_women | 8 | 26,071 | NO — new persona |
| midlife_women_520_atoms.zip | midlife_women | 26 | 26,328 | NO — superset of complete |
| nyc_executives_combined.zip | nyc_executives | 12 | 29,026 | PARTIAL — 235 existing atoms |
| parents_teens_complete.zip | parents_teens | 26 | 30,432 | NO — new persona |
| creatives_freelancers_complete.zip | creatives_freelancers | 26 | 25,525 | NO — new persona |
| sf_founders_complete.zip | sf_founders | 26 | 28,778 | NO — new persona |
| smb_owners_complete.zip | smb_owners | 4 | 12,632 | NO — new persona |
| phase3_all_personas.zip | ALL Phase 3 | 50 | 93,254 | Superset of above 4 P3 personas |

**New personas not in canonical_personas.yaml:**
- `midlife_women`
- `parents_teens`
- `creatives_freelancers`
- `sf_founders`
- `smb_owners`

**Existing but partial:**
- `nyc_executives` — 235 atoms in atoms/, 12 files (29k words) in zip

---

## TYPE D: Numbered Files Zips (files.zip through files (11).zip)

| Zip | Files | Content | Classification |
|-----|-------|---------|----------------|
| files.zip | 4 | 2 chapter somatic zips + SOMATIC_Book_Template_Outline_GENERIC.md + BODY_FIRST_Book_Template_Outline.md | template_outline |
| files (1).zip | 42 | Breathwork app HTML pages (app25–app39) | breathwork_ui — reference only |
| files (2).zip | 7 | WHEN_HE_CHEATED manuscripts (3 MD) + Japan author YAMLs (4) | manuscript + author_config |
| files (3).zip | 17 | Contrarian template zips (2) + 06_integration.py + chapter CSV variations + REWRITE_SUMMARY.md | template_variant + code_embedded |
| files (4).zip | 33 | BODY_FIRST chapters V3 FINAL (14 MD files) + intro/conclusion | manuscript_chapters |
| files (5).zip | 11* | ALL template_expand zips (v2_bestseller, v2_somatic, v2_BOTH, v2_full, v4) + Python template modules (01–05) | **ARCHIVE BUNDLE** — contains the same zips as template_expand/ |
| files (6).zip | 4 | intro_10_variants.yaml + conclusion_10_variants.yaml + intro_universal.yaml/.md | intro_conclusion_variants |
| files (7).zip | 3 | topic_depression_personas_batch.zip + 2 midlife_women grief CANONICAL atoms | nested_zip + atoms |
| files (8).zip | 57 | Chapter slots zip + variation CSVs + individual scene/variant YAMLs | slot_scaffolds |
| files (9).zip | 5 | Template library MDs: NYC_EXEC, EMT, POLICE, FIREFIGHTER + END_TO_END_WALKTHROUGH | persona_template_reference |
| files (10).zip | 2 | quarter_life_workbook.html + workbook_intro_chapter.md | workbook_reference |
| files (11).zip | 4 | BODY_FIRST chapters 2–4 V3 + CONTENT_TEAM_SPEC_V1.2.docx | manuscript_chapters + spec |

*files (5) extracted 10 files because nested zips are not auto-extracted.

---

## TYPE E: Chat Logs

| File | Words | Classification |
|------|-------|----------------|
| chat_er.txt | 2,240 | prompt_lineage — activity graph dump |
| chat_lkjkj.txt | 2,874 | prompt_lineage — activity graph dump |
| chat_personas_stuff.txt | 2,829 | prompt_lineage — persona generation chat |
| chat_s.txt | 4,759 | prompt_lineage — audiobook production chat |
| old_chat_personas.txt | 28,702 | prompt_lineage — persona development history |

**Action:** Classify as `prompt_lineage`. Do NOT import as atoms.

---

## TYPE F: Specs (Markdown)

| File | Words | Classification |
|------|-------|----------------|
| PERSONA_EXPANSION_SPEC.md | ~1,400 | Phase 2 expansion plan: 5 new personas × 520 atoms |
| PHASE_3_PERSONA_SPEC.md | ~1,300 | Phase 3 expansion plan: 4 new personas × 520 atoms |
| WRITER_ONBOARDING_SHAME_ENGINE.md | ~750 | Shame engine writing guide for atom authors |

**Action:** Classify as `reference`. Do NOT import as content.

---

## Persona Status Matrix

| Persona | In canonical_personas.yaml? | Atoms in atoms/? | In template_expand2/? | Action |
|---------|---------------------------|-------------------|----------------------|--------|
| gen_alpha_students | YES | 1,146 | grief + anxiety batches | Check overlap, import new only |
| gen_z_professionals | YES | 737 | grief batches | Check overlap, import new only |
| healthcare_rns | YES | 382 | grief batches | Check overlap, import new only |
| nyc_executives | NO | 235 | 12 files (29k words) | Document — PM decision |
| midlife_women | NO | 0 | 520+ atoms (26k+ words) | Document — PM decision |
| parents_teens | NO | 0 | 26 files (30k words) | Document — PM decision |
| creatives_freelancers | NO | 0 | 26 files (26k words) | Document — PM decision |
| sf_founders | NO | 0 | 26 files (29k words) | Document — PM decision |
| smb_owners | NO | 0 | 4 files (13k words) | Document — PM decision |

**Per NON-NEGOTIABLE rules:** New personas are DOCUMENTED but NOT added to canonical_personas.yaml in this PR.

---

## Pipeline Impact

### V2 Somatic Library (PRIMARY)
- **600 section YAML files** ready for section_packet_composer
- Avg 153 words/section × 120 sections per book (12ch × 10sec) = **~18,360 words** of legacy scaffold per book
- Combined with enrichment + depth, this significantly closes the gap to 54k
- **Loader update needed:** section dirs use `section_NN_type` naming; variant files use `fN.yaml`

### Persona Atoms (SECONDARY)
- ~270k words of new atom content across 6+ personas
- Not directly used by section_packet_composer but feeds enrichment/depth
- Import deferred to PM approval for new persona promotion

---

## Recommendations

1. **IMMEDIATE:** Import V2 somatic library into template index + update loader naming
2. **IMMEDIATE:** Re-run anxiety pilot with real V2 somatic sections
3. **DEFERRED:** New persona atom import — requires PM approval
4. **REFERENCE ONLY:** Numbered files, chat logs, specs — classify but don't import
