# Content inventory stats — depth module sources (measured)

**Date:** 2026-04-11  
**Method:** Python scan of tracked files (no estimates).  
**Companion:** `config/depth/depth_module_map.yaml` (`inventory_snapshot`).

---

## Teacher banks

**Root:** `SOURCE_OF_TRUTH/teacher_banks/`  
**Teachers with `approved_atoms/`:** 13 (`adi_da`, `ahjan`, `joshin`, `junko`, `maat`, `master_feung`, `master_sha`, `master_wu`, `miki`, `omote`, `pamela_fellows`, `ra`, `sai_ma`).

**Slot-type directories:** `COMPRESSION`, `EXERCISE`, `HOOK`, `INTEGRATION`, `PERMISSION`, `PIVOT`, `QUOTE`, `REFLECTION`, `SCENE`, `STORY`, `TAKEAWAY`, `TEACHING`, `THREAD`.

**Atom text field:** `body` (not `content`) in YAML.

| Slot type | Atom files | Total words (sum of `body`) | Avg words |
|-----------|------------|-----------------------------|-----------|
| COMPRESSION | 164 | 4067 | 25 |
| EXERCISE | 237 | 19466 | 82 |
| HOOK | 174 | 3343 | 19 |
| INTEGRATION | 164 | 4298 | 26 |
| PERMISSION | 200 | 4140 | 21 |
| PIVOT | 200 | 3563 | 18 |
| QUOTE | 9 | 181 | 20 |
| REFLECTION | 174 | 4439 | 26 |
| SCENE | 164 | 5706 | 35 |
| STORY | 260 | 45066 | 173 |
| TAKEAWAY | 200 | 1867 | 9 |
| THREAD | 200 | 3831 | 19 |
| TEACHING | 100 | 7056 | 71 |
| **Total** | **2246** | — | — |

### ahjan only (sample requested)

| Slot type | YAML count |
|-----------|------------|
| COMPRESSION | 12 |
| EXERCISE | 65 |
| HOOK | 12 |
| INTEGRATION | 12 |
| PERMISSION | 15 |
| PIVOT | 15 |
| QUOTE | 9 |
| REFLECTION | 12 |
| SCENE | 12 |
| STORY | 20 |
| TAKEAWAY | 15 |
| TEACHING | 100 |
| THREAD | 15 |

---

## Persona atoms

**Pattern:** `atoms/{persona}/{topic}/**/CANONICAL.txt`  
**Total `CANONICAL.txt` files:** 5817  
**Distinct `{persona}/{topic}` roots:** 187  

**Loader contract:** `phoenix_v4.planning.registry_resolver._load_persona_atoms` — slot-type directories `HOOK`, `SCENE`, `STORY`, plus engine subdirectories merged into `STORY`.

**Example:** `atoms/gen_z_professionals/anxiety/false_alarm/CANONICAL.txt` — multi-block file with RECOGNITION / MECHANISM proof stories (story_scene + mechanism_depth + consequence_exposure).

---

## Registry YAMLs

**Glob:** `registry/*.yaml` — **15 topics** (anxiety, boundaries, burnout, compassion_fatigue, courage, depression, financial_anxiety, financial_stress, grief, imposter_syndrome, overthinking, self_worth, sleep_anxiety, social_anxiety, somatic_healing).

**Aggregate across all topics (all variants, all section types):**

| Section type | Variant count | Total words | Avg words |
|--------------|---------------|-------------|-----------|
| HOOK | 900 | 25671 | 28.5 |
| SCENE | 1050 | 48858 | 46.5 |
| REFLECTION | 1849 | 87715 | 47.4 |
| EXERCISE | 301 | 21364 | 71.0 |
| INTEGRATION | 559 | 29125 | 52.1 |
| TEACHER_DOCTRINE | 80 | 2760 | 34.5 |

**Note:** `grief` has fewer total variants than other packs (203 vs 324) but higher average prose length per variant in many sections — see `artifacts/audit/depth_gap_analysis.md`.

---

## exercises_v4 approved

**Path:** `SOURCE_OF_TRUTH/exercises_v4/approved/*.yaml`  
**Count:** 11 files  
**Average words (concat `content` string fields):** 420.2  

**Standards:**  
- `SOURCE_OF_TRUTH/exercises_v4/aha_noticing_phoenix_standard.yaml`  
- `SOURCE_OF_TRUTH/exercises_v4/integration_phoenix_standard.yaml`  

**Bridge templates:** `SOURCE_OF_TRUTH/exercises_v4/bridge_templates.yaml`

---

## Practice library (inbox)

**Path:** `SOURCE_OF_TRUTH/practice_library/inbox/*_PRODUCTION_READY.json`  
**Loader:** `phoenix_v4.exercises.practice_library_loader`  

| File | Exercises |
|------|-----------|
| affirmations_library_34_PRODUCTION_READY.json | 34 |
| body_awareness_library_34_PRODUCTION_READY.json | 34 |
| integration_bridges_library_34_PRODUCTION_READY.json | 34 |
| meditations_library_34_PRODUCTION_READY.json | 34 |
| reflections_library_34_PRODUCTION_READY.json | 34 |
| self_inquiry_library_34_PRODUCTION_READY.json | 34 |
| sensory_grounding_library_34_PRODUCTION_READY.json | 34 |
| thought_experiments_library_34_PRODUCTION_READY.json | 34 |
| exercises_ab_tady_37_PRODUCTION_READY.json | 39 |
| **Total** | **311** |

---

## Pearl practice component templates

**Path:** `config/pearl_practice/component_templates.yaml` (runtime path used by `practice_library_loader`; not `config/exercises_v4/` — that path does not exist in-repo).

| Pool | Entries |
|------|---------|
| bridge | 12 |
| aha_permission | 12 |
| integration_closing | 12 |
| intro_mechanism (per sub-pool) | 12 each × 9 sub-pools = 108 |
| aha_observation (per sub-pool) | 12 each × 9 sub-pools = 108 |
| integration_takeaway (per sub-pool) | 12 each × 9 sub-pools = 108 |

---

## Structural configs (classification reference)

- `config/source_of_truth/chapter_archetypes.yaml` — archetype → `slot_expectations`  
- `config/source_of_truth/book_structure_archetypes.yaml` — structure families  
- `config/source_of_truth/chapter_planner_policies.yaml` — quotas, `slot_policy` per archetype  
- `config/format_selection/format_registry.yaml` — default slot templates, runtime word ranges  

---

## Classification by function (summary)

| Source family | Primary depth functions |
|----------------|-------------------------|
| Teacher HOOK/SCENE | recognition_depth, teacher_voice, persona_specificity (when paired with persona) |
| Teacher STORY | story_scene, consequence_exposure |
| Teacher REFLECTION/COMPRESSION/TEACHING | mechanism_depth, teacher_voice, consequence_exposure |
| Teacher EXERCISE | somatic_detail, practice_scaffold |
| Teacher THREAD/INTEGRATION/PIVOT | bridge_transition, integration_landing |
| Persona CANONICAL | story_scene, recognition_depth, persona_specificity |
| Registry variants | All modules depending on section type; grief REFLECTION → witnessing_presence |
| exercises_v4 + pearl_practice | practice_scaffold, somatic_detail |
| Practice library inbox | practice_scaffold (mostly cognitive/reflective; tag somatic when body_awareness / meditations) |
