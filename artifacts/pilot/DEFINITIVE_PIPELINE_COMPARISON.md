# Definitive Pipeline Comparison — Spine vs Registry (15 Topics)

**Date:** 2026-04-11  
**Persona:** gen_z_professionals  
**Spine settings:** `--pipeline-mode spine --runtime-format standard_book` (runtime applies to knob/beatmap only; Stage 2 format selection unchanged).  
**Registry settings:** default `--pipeline-mode registry` (section-registry fast-path).  
**Quality profile:** draft (gates run; failures are non-blocking except where noted).  
**PR #380:** Depth Pass v1 merged before this evaluation.

## Summary

| Metric | Spine Mode | Registry Mode |
|--------|------------|----------------|
| Topics run | 15/15 | 15/15 |
| Average word count (delivery `book.txt`) | 7367 | 4828 |
| Median word count | 7366 | 4693 |
| Min word count (topic) | 5781 (somatic_healing) | 4170 (somatic_healing) |
| Max word count (topic) | 8353 (grief) | 7273 (grief) |
| Average chapters | 12 | 12 |
| Spine wins on word count | 15/15 | — |
| Registry wins on word count | — | 0/15 |
| Topics in standard_book band 9000–11000 words (spine) | 0/15 | 0/15 |

## Per-Topic Detail

| Topic | Spine Words | Registry Words | Delta | Winner | Depth modules used (unique) |
|-------|-------------|----------------|-------|--------|----------------------------|
| anxiety | 8344 | 4904 | +70.1% | Spine | bridge_transition, integration_landing, mechanism_depth, practice_scaffold, recognition_depth, somatic_detail, story_scene, witnessing_presence |
| grief | 8353 | 7273 | +14.8% | Spine | integration_landing, mechanism_depth, persona_specificity, practice_scaffold, recognition_depth, somatic_detail, story_scene, witnessing_presence |
| burnout | 7393 | 4693 | +57.5% | Spine | consequence_exposure, integration_landing, mechanism_depth, persona_specificity, practice_scaffold, recognition_depth, somatic_detail, story_scene, witnessing_presence |
| self_worth | 7693 | 4653 | +65.3% | Spine | bridge_transition, consequence_exposure, integration_landing, mechanism_depth, persona_specificity, practice_scaffold, recognition_depth, somatic_detail, story_scene |
| imposter_syndrome | 7049 | 4174 | +68.9% | Spine | bridge_transition, consequence_exposure, integration_landing, mechanism_depth, practice_scaffold, recognition_depth, somatic_detail, story_scene, teacher_voice |
| boundaries | 7038 | 4831 | +45.7% | Spine | bridge_transition, consequence_exposure, integration_landing, mechanism_depth, persona_specificity, practice_scaffold, recognition_depth, somatic_detail, story_scene, teacher_voice |
| depression | 7502 | 4516 | +66.1% | Spine | bridge_transition, integration_landing, mechanism_depth, practice_scaffold, recognition_depth, somatic_detail, story_scene, witnessing_presence |
| courage | 6759 | 4774 | +41.6% | Spine | bridge_transition, consequence_exposure, integration_landing, mechanism_depth, practice_scaffold, recognition_depth, somatic_detail, story_scene, teacher_voice |
| overthinking | 7628 | 4913 | +55.3% | Spine | bridge_transition, consequence_exposure, integration_landing, mechanism_depth, persona_specificity, practice_scaffold, recognition_depth, somatic_detail, story_scene |
| compassion_fatigue | 6958 | 4574 | +52.1% | Spine | consequence_exposure, integration_landing, mechanism_depth, persona_specificity, practice_scaffold, recognition_depth, somatic_detail, story_scene, witnessing_presence |
| social_anxiety | 7237 | 4250 | +70.3% | Spine | bridge_transition, consequence_exposure, integration_landing, mechanism_depth, practice_scaffold, recognition_depth, somatic_detail, story_scene |
| sleep_anxiety | 8151 | 5363 | +52.0% | Spine | bridge_transition, consequence_exposure, integration_landing, mechanism_depth, persona_specificity, practice_scaffold, recognition_depth, somatic_detail, story_scene |
| financial_anxiety | 7248 | 4709 | +53.9% | Spine | bridge_transition, consequence_exposure, integration_landing, mechanism_depth, practice_scaffold, recognition_depth, somatic_detail, story_scene, teacher_voice |
| financial_stress | 7366 | 4623 | +59.3% | Spine | bridge_transition, consequence_exposure, integration_landing, mechanism_depth, persona_specificity, practice_scaffold, recognition_depth, somatic_detail, story_scene, teacher_voice |
| somatic_healing | 5781 | 4170 | +38.6% | Spine | bridge_transition, integration_landing, mechanism_depth, persona_specificity, practice_scaffold, recognition_depth, somatic_detail, story_scene, teacher_voice |

## Topics Where Spine Fails

- **Chapter flow gate:** For all 15 topics, `chapter_flow_report.json` status is **FAIL** (12/12 chapters failed in each run). Primary issues include `WEAK_TRANSITIONS`, `MISSING_CLEAR_POINT`, and (where applicable) `GENERIC_SCENE_FALLBACK`. Root cause: spine mode uses `compose_from_enriched_book`, which **concatenates slot bodies in beatmap order** — not the full thesis-threaded `compose_chapter_prose` path used in the legacy atom pipeline.
- **standard_book word band:** No topic reached the 9000–11000 word band on either mode in this batch (registry tops out at 7273 words for grief).
- **Book pass gate:** Not applicable in spine mode (no compiled `atom_ids` / slot sequence); same limitation as registry mode.

## Topics Where Spine Excels

- **Word count vs registry:** Spine mode produced **more words than registry on all 15 topics**, with the depth pass closing much of the gap versus pre-depth enrichment totals.
- **Structural intent:** Spine + knobs + beatmap encode chapter roles, forbidden moves, and topic-specific depth policy (e.g. grief early bans) in a way the registry fast-path does not surface.
- **Depth pass:** Measurable lift from pre-depth to post-depth enriched totals (see table below).

## Depth Pass Effectiveness

| Topic | Pre-Depth Words (enriched total) | Post-Depth Words (enriched total) | Depth rows appended | Notes |
|-------|----------------------------------|-----------------------------------|----------------------|--------|
| anxiety | 2595 | 8015 | 35 | Large deficit fill |
| grief | 3241 | 8217 | 26 | |
| burnout | 2032 | 7415 | 36 | |
| self_worth | 2064 | 7450 | 32 | |
| imposter_syndrome | 1637 | 6950 | 31 | |
| boundaries | 1277 | 6827 | 35 | |
| depression | 1011 | 7281 | 42 | |
| courage | 995 | 6539 | 34 | |
| overthinking | 1536 | 7437 | 41 | |
| compassion_fatigue | 1293 | 6835 | 36 | |
| social_anxiety | 840 | 7125 | 38 | |
| sleep_anxiety | 2286 | 7920 | 34 | |
| financial_anxiety | 1359 | 7191 | 36 | |
| financial_stress | 1364 | 7135 | 36 | |
| somatic_healing | 918 | 5667 | 32 | |

Delivery word counts (`book.txt`) can differ slightly from post-depth enriched totals because composition is linear concatenation.

## Quality Gate Results (draft)

| Topic | Chapter flow | Book pass | Bestseller craft (advisory) |
|-------|--------------|-----------|-----------------------------|
| All 15 | FAIL (12/12 chapters) | SKIPPED (spine) | Generally PASS/WARN band in stderr (ONTGP ~0.4+) |

## Architecture Verdict

- **Is spine mode ready to be the DEFAULT?** **No.** Conditions to revisit: wire **full chapter composition** (thesis-threaded `compose_chapter_prose` / exercise assembly path) for spine output, then re-run chapter flow; and raise delivery word counts into the **standard_book** band (9000–11000) if that remains the product target.
- **standard_book range (9000–11000):** **0%** of topics met it for spine in this run; registry also **0/15**.
- **Remaining gap:** Narrative-flow quality gates fail on spine composition; word count still short of the long-form band for almost all topics.
- **Next improvement (specific):** Replace slot-only concatenation in `compose_from_enriched_book` with the same **bridge + mechanism + exercise assembly** path used when resolving atoms, **or** render from a compiled plan that carries slot metadata through `compose_chapter_prose`, then re-measure chapter flow.

## What Registry Mode Still Does Better

- **Operational simplicity:** No spine YAML, knob profile, or beatmap dependency; auto-detects `registry/{topic}.yaml`.
- **Predictable prose shape:** Registry resolver + `to_prose()` is a known quantity for the funnel and QA.
- **Speed / fewer moving parts:** Faster runs in this batch (~seconds vs tens of seconds per topic).

## What Spine Mode Does Better

- **Word count and depth:** Consistently higher delivery word count than registry; depth pass applies topic-aware modules from `depth_module_map.yaml`.
- **Governance of structure:** Explicit spine roles, sequencing rules, and knob shaping before enrichment.
- **Auditability:** `enrichment_audit.json` with depth module rows supports debugging.

## Recommendation

**B) Keep registry as default — spine needs more work.**

Rationale: **chapter flow fails everywhere** in spine mode with the current composer, and **no topic** hit the 9000–11000 word band. Ship spine as an **explicit opt-in** (`--pipeline-mode spine`) for experiments and parity measurement until composition and length targets are met.

**Optional later C:** Hybrid routing per topic only after composer parity and word-count evidence — not justified yet.

---

## Evidence paths

- Spine outputs: `artifacts/pilot/full_15_spine/<topic>/`
- Registry outputs: `artifacts/pilot/full_15_registry/<topic>/`
- Spine wiring: `scripts/run_pipeline.py` (`_run_spine_pipeline_mode`, `--pipeline-mode`)

## Note on `config/spines/`

Fifteen spine YAMLs were promoted into `config/spines/` (from the in-repo worktree snapshot) so all registry topics have a loadable spine. Four files required **YAML quoting fixes** for list items containing `:` so PyYAML parses them.
