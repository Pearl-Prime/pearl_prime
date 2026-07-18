# Pearl Prime Atom Analysis Pack

## Summary

- Personas scanned: `14`
- Topics scanned: `20`
- Persona-topic pairs: `220`
- Average STORY blocks per pair with STORY: `17.19`
- Average SCENE blocks per pair with SCENE: `22.38`
- Sparse slot/engine canonicals flagged: `300`

## Strongest current persona-topic pairs

| Persona | Topic | Slots | Engines | STORY blocks | SCENE blocks | Locales | Score |
|---|---:|---:|---:|---:|---:|---:|---:|
| gen_alpha_students | anxiety | 31 | 7 | 20 | 30 | 37 | 381 |
| gen_z_professionals | anxiety | 16 | 7 | 43 | 82 | 33 | 229 |
| gen_z_professionals | burnout | 12 | 7 | 20 | 30 | 33 | 191 |
| gen_z_professionals | financial_anxiety | 12 | 7 | 20 | 30 | 33 | 191 |
| gen_z_professionals | imposter_syndrome | 12 | 7 | 20 | 30 | 33 | 191 |
| gen_z_professionals | sleep_anxiety | 12 | 7 | 20 | 4 | 33 | 183 |
| corporate_managers | burnout | 11 | 7 | 20 | 30 | 27 | 181 |
| corporate_managers | financial_anxiety | 11 | 7 | 20 | 30 | 22 | 181 |
| corporate_managers | imposter_syndrome | 11 | 7 | 20 | 30 | 22 | 181 |
| corporate_managers | social_anxiety | 11 | 7 | 20 | 30 | 22 | 181 |
| corporate_managers | somatic_healing | 11 | 7 | 20 | 30 | 22 | 181 |
| educators | anxiety | 11 | 7 | 20 | 30 | 42 | 181 |
| entrepreneurs | anxiety | 11 | 7 | 20 | 29 | 22 | 181 |
| gen_alpha_students | boundaries | 11 | 7 | 20 | 30 | 37 | 181 |
| gen_alpha_students | burnout | 11 | 7 | 20 | 30 | 37 | 181 |

## Top bestseller gaps

### P1 — Source-bank thinness still limits cohesive bestseller flow
- Type: `data`
- Linked docs: `docs/BOOK_PLANNING_SYSTEM_SPEC.md`, `docs/HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md`, `docs/SOURCE_BANK_REPAIR_DEV_SPEC.md`
- Observation: 300 sparse slot/engine canonicals were detected; STORY missing in 4/220 persona-topic pairs and SCENE missing in 38/220.
- Evidence: `atoms/`, `scripts/analysis/build_pearl_prime_analysis_pack.py`, `phoenix_v4/planning/enrichment_select.py`
- Next fix: Upgrade STORY/SCENE source banks first, especially sparse persona-topic pairs before scaling more titles.

### P2 — Chapter architecture can still fall back to legacy uniform planning
- Type: `code`
- Linked docs: `docs/BOOK_PLANNING_SYSTEM_SPEC.md`, `docs/BESTSELLER_ATOM_ROUTING.md`, `docs/specs/PEARL_PRIME_HOLISTIC_CHAPTER_ARCHITECTURE_SPEC.md`
- Observation: chapter_planner has warn-path fallback contracts and legacy_uniform chapter selection when policy/archetype generation under-fills.
- Evidence: `phoenix_v4/planning/chapter_planner.py`, `phoenix_v4/planning/book_structure_plan.py`
- Next fix: Convert legacy_uniform fallbacks into explicit failures for production runs or produce authored replacements per runtime.

### P3 — Pipeline drift is guarded but not eliminated
- Type: `code/process`
- Linked docs: `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md`, `docs/DOCS_INDEX.md`
- Observation: run_pipeline still defaults pipeline_mode to registry in several branches, while CI separately scans for missing --pipeline-mode spine in production contexts.
- Evidence: `scripts/run_pipeline.py`, `scripts/ci/check_canonical_pipeline_path.py`
- Next fix: Make spine the code default for production book paths instead of relying on drift detection.

### P4 — Structure assignment still needs post-fix repair for edge cases
- Type: `code`
- Linked docs: `docs/BESTSELLER_STRUCTURES.md`, `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md`
- Observation: book_structure_plan patches repeated bestseller structures after assignment, indicating planner output is not fully trusted on its own.
- Evidence: `phoenix_v4/planning/chapter_planner.py`, `phoenix_v4/planning/book_structure_plan.py`
- Next fix: Move repeat-avoidance guarantees fully into assignment logic and cover with deterministic tests over seeds/chapter counts.

### P5 — Automated gates do not yet equal true bestseller acceptance
- Type: `quality/process`
- Linked docs: `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md`, `docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md`, `docs/CREATIVE_QUALITY_VALIDATION_CHECKLIST.md`
- Observation: spine mode runs chapter flow, bestseller craft, editorial and other checks, but registry mode still skips book-pass metadata checks and docs explicitly require human acceptance beyond gates.
- Evidence: `scripts/run_pipeline.py`, `phoenix_v4/quality/bestseller_craft_gate.py`, `phoenix_v4/quality/chapter_flow_gate.py`, `phoenix_v4/qa/editorial_report.py`
- Next fix: Track blind editorial scores across sample books and block promotion when gate pass diverges from human shelf-quality review.

### P6 — Teacher/persona fallback can preserve coverage while hiding native insufficiency
- Type: `code/data`
- Linked docs: `docs/TEACHER_PRODUCTION_READINESS.md`, `docs/HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md`, `docs/RECOGNITION_BANK_SPEC.md`
- Observation: teacher coverage gating exists, but story/exercise fallback paths and wrapper logic can still make output look complete while teacher-native or persona-native banks remain weak.
- Evidence: `phoenix_v4/teacher/coverage_gate.py`, `phoenix_v4/rendering/book_renderer.py`, `scripts/run_pipeline.py`
- Next fix: Expose native-vs-fallback share in release reports and set hard ceilings on fallback percentages for bestseller candidates.

### P7 — Locale and ARC-block readiness likely trail English base content
- Type: `data/code`
- Linked docs: `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md`, `docs/SOURCE_BANK_REPAIR_DEV_SPEC.md`
- Observation: The repo has 5526 locale overlay canonicals across primary slot dirs, while enrichment and depth logic explicitly fall back to English when locale files or parseable ARC blocks are missing.
- Evidence: `atoms/`, `phoenix_v4/planning/enrichment_select.py`, `scripts/run_pipeline.py`
- Next fix: Audit locale overlay parity and rewrite plain-prose CANONICAL files into block-structured canonicals for high-priority personas/topics.

### P8 — Depth expansion remains fragile when canonical files are not block-structured
- Type: `code/data`
- Linked docs: `docs/specs/PEARL_PRIME_HOLISTIC_CHAPTER_ARCHITECTURE_SPEC.md`, `docs/HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md`, `docs/GOLDEN_CHAPTER_WORKFLOW.md`
- Observation: enrichment_select contains an explicit degraded fallback path when CANONICAL.txt cannot be parsed into per-block units, which risks chunk-style repetition rather than chapter-shaped progression.
- Evidence: `phoenix_v4/planning/enrichment_select.py`
- Next fix: Prioritize block-structured CANONICAL authoring for STORY/SCENE/depth sources and log degraded fallback counts in production artifacts.
