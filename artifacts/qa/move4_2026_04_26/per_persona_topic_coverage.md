# Move 4 — Catalog QA Sweep Coverage Report (2026-04-26)

## Summary

- Sweep: en-US, target=30, seed-tag=move4_sweep
- Assembled: 30 / quality_gates_pass: 29 / book.txt: 29
- Mean word count: 9259
- Elapsed: 396.0s (6.6 min)

## Per-grade aggregate

- BESTSELLER-grade: 27 / 30 (90%)
  - via story_plan/CALLBACK_ID: 1
  - via engine-bank named-character: 26
- PARTIAL (engine-bank generic, no named chars): 2
- FAILED (no book.txt): 1
- OTHER: 0

## Per-book breakdown

| # | persona × topic | grade | sec2 | sec5 | sec9 | named chars |
|---|---|---|---|---|---|---|
| 0 | anxiety_millennial_women_professionals | BESTSELLER (story_plan/CALLBACK_ID) | story_plan | story_plan | story_plan | Elena(11), Carmen(5), Sarah(6), Mia(5) |
| 1 | boundaries_tech_finance_burnout | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Marcus(1) |
| 2 | burnout_entrepreneurs | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Alex(24), Maya(33) |
| 3 | compassion_fatigue_working_parents | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Tara(5), Greg(1) |
| 4 | courage_gen_x_sandwich | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Diane(14), Tom(10) |
| 5 | depression_corporate_managers | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Sarah(8) |
| 6 | financial_anxiety_gen_z_professionals | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Marcus(4), Priya(2), Jordan(9), Sam(8), Alex(1) |
| 7 | financial_stress_healthcare_rns | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Marcus(8), Aisha(8), Tom(13) |
| 8 | grief_gen_alpha_students | PARTIAL (engine-bank generic) | persona_atom | persona_atom | persona_atom | — |
| 9 | imposter_syndrome_first_responders | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Marcus(2), Sofia(4) |
| 10 | overthinking_gen_z_student | FAILED | ? | ? | ? | — |
| 11 | social_anxiety_millennial_women_professionals | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Elena(4), Carmen(6), Sarah(1), Mia(4), Rachel(2), Lena(2), Jess(1) |
| 12 | somatic_healing_tech_finance_burnout | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Marcus(14), Priya(13), Sam(1) |
| 13 | anxiety_entrepreneurs | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Alex(16), Maya(24) |
| 14 | boundaries_working_parents | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Tara(24), Greg(1) |
| 15 | burnout_gen_x_sandwich | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Sam(1), Diane(8), Tom(5) |
| 16 | compassion_fatigue_corporate_managers | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Marcus(1), Sarah(10), Rachel(4) |
| 17 | courage_gen_z_professionals | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Marcus(3), Priya(9), Jordan(20), Sam(16), Alex(5), Maya(9) |
| 18 | depression_healthcare_rns | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Aisha(9), Tom(1) |
| 19 | financial_anxiety_gen_alpha_students | PARTIAL (engine-bank generic) | persona_atom | persona_atom | persona_atom | — |
| 20 | financial_stress_first_responders | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Marcus(3), Sofia(6) |
| 21 | self_worth_millennial_women_professionals | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Elena(3), Carmen(4), Sarah(5), Mia(4), Diane(1), Rachel(1), Lena(1), Tara(1), Je |
| 22 | sleep_anxiety_tech_finance_burnout | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Marcus(6), Priya(5) |
| 23 | social_anxiety_entrepreneurs | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Priya(5), Sam(1), Alex(3), Maya(6), Tom(4) |
| 24 | somatic_healing_working_parents | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Sam(1), Tara(14), Greg(3) |
| 25 | anxiety_gen_x_sandwich | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Diane(1), Greg(7), Tom(6) |
| 26 | boundaries_corporate_managers | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Sam(1), Sarah(11), Rachel(9), Tom(1) |
| 27 | burnout_gen_z_professionals | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Marcus(15), Priya(13), Jordan(17), Sam(10), Maya(18) |
| 28 | compassion_fatigue_healthcare_rns | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Aisha(12), Tom(1) |
| 29 | courage_gen_alpha_students | BESTSELLER (engine-bank named-character) | persona_atom | persona_atom | persona_atom | Maya(2) |

## Pearl_Prime sign-off

QA pass criteria met: 27 bestseller-grade books / 30 total / 2 partial-grade with documented sources / 1 failed.

Known gaps surfaced:
- midlife_women persona: not represented in this sweep (zero master_arcs; gated on ws_midlife_women_arc_authoring_20260427 — Pearl_Prime authoring; tracked separately)
- Personas without story_atoms/anchored coverage produce engine-bank-named-character SCENE (bestseller-grade per PR #670) but without through-book CALLBACK_ID continuity (Move 5 rolling enhancement under ws_story_cell_authoring_20260425)

Evidence:
- Per-book renders: /tmp/move4_sweep/renders/ (not committed; ephemeral)
- Assembly summary snapshot: this report's aggregate sourced from /tmp/move4_sweep/assembly_summary.json