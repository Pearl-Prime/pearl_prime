# Depth gap analysis — spine pipeline (new) vs registry baseline (pilot)

**Project:** `proj_state_convergence_20260328`  
**Subsystem:** `core_pipeline`, `teacher_mode`  
**Evidence:** `artifacts/pilot/{anxiety,grief,burnout}_{new,baseline}/`, `artifacts/pilot/PIPELINE_COMPARISON_REPORT.md`  
**Date:** 2026-04-11  

This document compares **actual** pilot manuscripts and budgets. The new path uses **EnrichmentSelect** over a **beatmap** (fewer slots per chapter than the registry fast-path resolves), and the pilot **concatenates slot bodies** without full `chapter_composer` bridges, mechanism distillation, or assembled exercises — so totals are expected to be lower until parity wiring lands (see `PIPELINE_COMPARISON_REPORT.md`).

---

## Global summary

| Topic   | New words (enrichment audit) | Baseline words (`budget.json`) | Delta (baseline − new) |
|---------|------------------------------:|-------------------------------:|-----------------------:|
| anxiety | 2413                         | 4904                           | 2491                   |
| grief   | 2768                         | 7273                           | 4505                   |
| burnout | 2347                         | 4693                           | 2346                   |

**Enrichment audit (all three pilots):** `teacher_id=ahjan`, `persona_id=gen_z_professionals`, `slots_from_practice_library=0`, `slots_empty=0`, `total_target_words≈9996` (beatmap budget) vs **actual** `total_words` in table above — slots are structurally **thin** vs per-slot targets (see per-chapter budgets in `*_new/budget.json`).

---

## Anxiety

### Chapter word counts (new vs baseline)

| Ch | New | Baseline | Δ (base−new) |
|---:|-----:|---------:|-------------:|
| 1 | 184 | 454 | 270 |
| 2 | 183 | 399 | 216 |
| 3 | 189 | 358 | 169 |
| 4 | 185 | 413 | 228 |
| 5 | 265 | 316 | 51 |
| 6 | 194 | 322 | 128 |
| 7 | 271 | 844 | **573** |
| 8 | 177 | 565 | 388 |
| 9 | 179 | 301 | 122 |
| 10 | 220 | 314 | 94 |
| 11 | 182 | 306 | 124 |
| 12 | 184 | 312 | 128 |

### Where baseline is longer (Δ > 100 words)

Across almost every chapter, the baseline pulls **more sections and longer registry variants** per chapter than the beatmap pilot (six default types × full chapter flow in the old path vs four–five slots in the new pilot for early chapters). The largest gap is **chapter 7** (baseline 844 vs new 271): baseline stacks **practice-heavy** material (exposure / skills chapter in the rendered book) while the new run still only fills discrete HOOK/SCENE/REFLECTION/EXERCISE/INTEGRATION slots without composer expansion.

**Dominant depth types missing in the new pilot (vs baseline):**

- **practice_scaffold** — baseline exercise chapters carry full instruction + closure; new path shows EXERCISE slots with teacher atoms but no component assembly (bridge, intro mechanism, aha, integration).
- **bridge_transition** — baseline read is continuous; new pilot is sequential slot paste (`PIPELINE_COMPARISON_REPORT.md`).
- **mechanism_depth** — registry REFLECTION variants are short in the new pilot (~46 words per REFLECTION slot in `budget.json`); baseline chapters accumulate more reflective + explanatory mass.
- **story_scene** — SCENE slots in new run are persona-backed but short (~50–58 words) vs long hydrated scenes in baseline.

### Where the new pipeline is stronger

- **Structure:** Beatmap + spine roles align chapters to `tests/fixtures/knob_apply/spines/anxiety_spine.yaml` roles (recognition → mechanism → practice).
- **Thesis / intent:** Per-chapter `working_title` and thesis lines are explicit in `book_plan.json` / shaped spine.
- **Source transparency:** `budget.json` records `source` per slot (`teacher_atom`, `persona_atom`, `registry`) for tuning.

### Enrichment audit — anxiety (`artifacts/pilot/anxiety_new/enrichment_audit.json`)

| Metric | Value |
|--------|------:|
| total_slots | 51 |
| slots_from_teacher | 27 |
| slots_from_persona | 12 |
| slots_from_registry | 12 |
| slots_from_practice_library | 0 |
| slots_empty | 0 |
| total_words | 2413 |
| total_target_words | 9996 |

### Thin slots (actual ≪ target) — pattern

From `artifacts/pilot/anxiety_new/budget.json`, **HOOK** and **SCENE** are consistently far under `target_words` (e.g. ch1 HOOK target 278 vs actual 29; SCENE target 249 vs actual 52). **REFLECTION** is pinned near **~46 words** whenever source is `registry` — many variants are short in the anxiety pack. **INTEGRATION** teacher atoms land closer but still under target. **EXERCISE** in ch5/ch7 is relatively strong (89–90 words) vs other slots.

---

## Grief

### Chapter word counts (new vs baseline)

| Ch | New | Baseline | Δ (base−new) |
|---:|-----:|---------:|-------------:|
| 1 | 367 | 880 | **513** |
| 2 | 258 | 814 | **556** |
| 3 | 220 | 679 | 459 |
| 4 | 229 | 617 | 388 |
| 5 | 199 | 537 | 338 |
| 6 | 208 | 500 | 292 |
| 7 | 205 | 667 | 462 |
| 8 | 197 | 653 | 456 |
| 9 | 245 | 447 | 202 |
| 10 | 207 | 485 | 278 |
| 11 | 207 | 495 | 288 |
| 12 | 226 | 499 | 273 |

### Depth gap characterization

- **registry/grief.yaml** carries **very long** HOOK/REFLECTION variants (gold-standard prose density). In the new pilot, **one variant per section** still underfills beatmap targets for HOOK/SCENE/INTEGRATION; REFLECTION can spike (e.g. ch1 **233 words** when registry hits) — so grief’s gap is **not** uniform: early chapters mix **witnessing_presence** depth in baseline with thin teacher/persona overlays when the waterfall picks short teacher HOOKs.
- **Where new is stronger:** Spine contract from `tests/fixtures/knob_apply/spines/grief_spine.yaml` (late practice, witnessing early) is visible in **slot mix**; forbidden early practice is respected relative to spine rules.
- **Where new is thinner:** Same structural reasons as anxiety — fewer composed layers, no bridges, no full exercise assembly; baseline totals dominate across all chapters.

### Enrichment audit — grief (`artifacts/pilot/grief_new/enrichment_audit.json`)

| Metric | Value |
|--------|------:|
| total_slots | 49 |
| slots_from_teacher | 25 |
| slots_from_persona | 12 |
| slots_from_registry | 12 |
| slots_from_practice_library | 0 |
| total_words | 2768 |
| total_target_words | 9996 |

---

## Burnout

### Chapter word counts (new vs baseline)

| Ch | New | Baseline | Δ (base−new) |
|---:|-----:|---------:|-------------:|
| 1 | 195 | 460 | 265 |
| 2 | 189 | 408 | 219 |
| 3 | 192 | 353 | 161 |
| 4 | 197 | 388 | 191 |
| 5 | 189 | 303 | 114 |
| 6 | 201 | 308 | 107 |
| 7 | 199 | **601** | **402** |
| 8 | 193 | **626** | **433** |
| 9 | 214 | 308 | 94 |
| 10 | 193 | 309 | 116 |
| 11 | 186 | 314 | 128 |
| 12 | 199 | 315 | 116 |

### Depth gap characterization

- Peaks at **chapters 7–8** (baseline much longer): **practice / relational consequence** chapters in full render — aligns with **practice_scaffold**, **consequence_exposure**, **story_scene**.
- Early chapters: baseline still exceeds new on **recognition + cost** prose density.

### Enrichment audit — burnout (`artifacts/pilot/burnout_new/enrichment_audit.json`)

| Metric | Value |
|--------|------:|
| total_slots | 48 |
| slots_from_teacher | 24 |
| slots_from_persona | 12 |
| slots_from_registry | 12 |
| slots_from_practice_library | 0 |
| total_words | 2347 |
| total_target_words | 9996 |

---

## Cross-cutting conclusions

1. **Volume:** Baseline books are longer because the registry fast-path resolves **full per-chapter section sets** and longer composed output; the new path is **slot-limited** and **pilot-composed** without bridges and full exercise assembly.
2. **Depth functions to raise first:** **practice_scaffold**, **bridge_transition**, **mechanism_depth** (where REFLECTION/registry variants are short), and **story_scene** (expand SCENE/HOOk or add alternate registry variants F2–F5).
3. **Next architecture step:** Request **depth modules by function** (this workstream) before mutating atoms — see `config/depth/depth_module_map.yaml` and `docs/DEPTH_MODULE_PROTOCOL.md`.
