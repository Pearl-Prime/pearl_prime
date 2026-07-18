# Book Planning System — Definitive Specification

**Status:** Single source of truth for the deterministic book planning layer.  
**Supersedes:** Ad-hoc planning prompts; implementation work MUST reference this document.  
**Authority stack:** This spec synthesizes `phoenix_v4/qa/*`, `phoenix_v4/quality/*`, `config/quality/*`, `docs/BESTSELLER_STRUCTURES.md`, `docs/CHAPTER_THESIS_BANK.md`, `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`, `specs/ARC_AUTHORING_PLAYBOOK.md`, `specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md`, and `docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md`.  
**Last updated:** 2026-04-14  

---

## Section 1 — Why the plan layer exists

### 1.1 Problem statement

Phoenix Omega’s quality stack (EI V2, chapter flow, ONTGP craft gate, book-pass gate, scene anti-genericity, macro cadence, mechanism escalation, editorial rubric, CSI bundle, etc.) largely runs **after** composition. Books are assembled without an explicit, validated plan that **feeds** those checks. That produces predictable failure modes:

| Failure mode | Where it shows up post hoc | What planning prevents |
|--------------|----------------------------|-------------------------|
| Topic-first openers / essay hooks | `bestseller_craft_gate` (orient), `editorial_report` hook friction, overlay §5 banned openers | Plan declares **hook_type** and **orient_forbids** (no topic/temporal openers) |
| Weak or missing ONTGP moves | `evaluate_bestseller_craft` zone scores | Plan assigns **ontgp_serves** per slot and **move budgets** |
| Thesis drift | `bestseller_editor._thesis_drift_check` | Plan pins **chapter_thesis** and **keyword anchors** per chapter |
| Flat or wrong emotional arc | `emotion_arc_validator`, `macro_cadence_gate`, playbook band rules | Plan declares **band**, **emotional_role**, **dominant_band_sequence**, **intensity curve** |
| Mechanism depth plateaus / regression | `mechanism_escalation_gate` (metadata) | Plan assigns **max_mechanism_depth** targets per chapter |
| Cost / identity / callback gaps | `cost_gradient_gate`, `identity_shift_gate`, `callback_integrity_gate` | Plan declares **cost_intensity**, **identity_stage**, **callback_ids** |
| Scene genericity & collisions | `scene_anti_genericity_gate`, overlay §8 | Plan sets **scene_anchor_family**, **forbidden_scene_patterns**, **unique_detail_quota** |
| Chapter shuffleability / repetitive claims | `book_pass_gate` claim Jaccard, repetition | Plan declares **claim_fingerprint** and **non_adjacent_claim** rules |
| TTS / listenability failure | `tts_readability`, `gate_listen_experience` | Plan sets **sentence_length_target**, **paragraph_break_density**, **rhetorical_question_cap** |
| Semantic duplication | `semantic_dedup`, `gate_uniqueness` | Plan declares **ngram_diversity_budget**, **manuscript_signature_allowlist** |
| Safety / clinical creep | `safety_classifier`, marketing bans | Plan lists **forbidden_phrase_classes**, **persona/topic compliance mode** |
| Teacher / frame violations | `teacher_integrity`, `frame_governor` | Plan declares **teacher_id**, **frame**, **doctrine_chapter**, **spiritual_entry_chapter_min** |
| Exercise overload | `exercise_governance` in `ei_v2_config.yaml` | Plan sets **exercise_slots** per chapter by **runtime_format_id** |
| Bestseller structure drift | `book_structure.enforce_bestseller_beat_order` (when enabled) | Plan assigns **bestseller_structure** + **slot order** per chapter |
| EI V2 hybrid override chaos | `hybrid_selector` | Plan supplies **arc_intent**, **duration_fit metadata**, **v2_selection_constraints** |

### 1.2 Enforcement gap (Phase 1 synthesis)

**Gaps:** Several systems need **plan-level intent** that is not fully enforced upstream today, including: explicit **BAND / emotional_role** per chapter for arc validation; **THREAD type** matching structure; **mechanism_depth progression** before atom pick; **scene collision avoidance** across chapters; **claim uniqueness**; **marketing / safety token budgets**; **duration_fit** inputs for 6h vs 1h; **teacher/frame** context; **memorable line / transformation density** targets (heatmap + memorable_line_gate are post hoc).

---

## Section 2 — ChapterPlan schema (complete)

### 2.1 Field reference

| Field | Type | Specifies | Feeds (gate / dimension) | Valid values | If missing |
|-------|------|-----------|----------------------------|--------------|------------|
| `chapter_index` | int (0-based) | Position in book | All ordering gates | ≥ 0 | Compile error |
| `chapter_number` | int (1-based) | Human chapter # | Reports | ≥ 1 | Derived from index |
| `title` | string | Display title | N/A | Non-empty | WARN |
| `runtime_format_id` | string | Micro/short/standard/deep profile | `chapter_flow_gate` flow_profile, `exercise_governance` | Known registry IDs | Default from book plan |
| `persona_id` | string | Audience | `domain_embeddings`, marketing lexicons | Catalog personas | FAIL selection |
| `topic_id` | string | Subject | `domain_embeddings`, safety context | Catalog topics | FAIL selection |
| `teacher_id` | string | Voice / doctrine | `teacher_integrity`, teacher YAML | Catalog teachers | WARN |
| `engine_type` | string | Watcher / False_Alarm / Shame / Grief / … | Thesis bank, arc | Enum | Required for thesis |
| `chapter_intent` | string | Intent 1–20 from thesis bank | Arc, threading | See CHAPTER_THESIS_BANK | FAIL arc alignment |
| `chapter_thesis` | string | Arguable claim | `book_pass_gate`, thesis drift, EI thesis | Non-empty sentence | FAIL book_pass / drift |
| `thread_sentences` | list[string] | Forward-pull (1–2) | THREAD slot, cohesion | 1–2 strings | WARN |
| `bestseller_structure` | string | One of 12 structures | `book_pass` distinct structures; beat order | Enum §2.2 | FAIL when enforcement on |
| `thread_type` | string | Structure-specific THREAD | Overlay §7.2 | Enum §2.3 | WARN |
| `band` | int | Emotional intensity band 1–5 | `emotion_arc_validator`, `macro_cadence_gate` | 1–5 | FAIL arc |
| `emotional_role` | string | Arc role | `emotion_arc_validator` | RECOGNITION, MECHANISM_PROOF, TURNING_POINT, EMBODIMENT | FAIL arc |
| `emotional_temperature` | string | cool / warm / hot | Playbook hot-count rules | Enum | WARN |
| `dominant_band_sequence` | list[int] | Optional per-chapter band | Macro cadence | Length = chapters | Default flat |
| `intensity` | int | 1–5 curve point | `macro_cadence_gate` | 1–5 | Default 2 |
| `regulation_support` | string | low / medium / high | Macro cadence (exercise proxy) | Enum | Derived from slots |
| `mechanism_depth_target` | int | 1–4 for STORY chapter | `mechanism_escalation_gate` | 1–4 | FAIL escalation |
| `cost_intensity` | int | Cost peak tracking | `cost_gradient_gate` | 1–5 | WARN |
| `identity_stage` | int | Identity progression | `identity_shift_gate` | Stage index | WARN |
| `callback_ids` | list[string] | Callback targets | `callback_integrity_gate` | Atom ids | WARN |
| `bestseller_beat_order` | list[string] | Ordered slot types for structure | Assembly vs `enforce_bestseller_beat_order` | HOOK, SCENE, STORY, … | FAIL if enforced |
| `slot_plans` | list[AtomSlotSpec] | Per-slot composition | All atom + EI gates | See §6 | FAIL |
| `word_budget` | object | min/target/max words | Budget.json, editorial | ints | WARN |
| `tts_targets` | object | TTS planning | `tts_readability`, listen_experience | See §8 | WARN |
| `scene_plan` | object | Cross-chapter scene anchors | `scene_anti_genericity_gate` | Families, tokens | WARN |
| `safety_budget` | object | Risk planning | `safety_classifier` | Thresholds | WARN |
| `duration_fit` | object | Per-chapter duration metadata | `duration_fit`, hybrid | format, intent, duration_sec | Neutral score |
| `frame_context` | object | Frame governance | `frame_governor` | frame, doctrine_chapter | WARN |
| `ending_contract` | object | Final chapter | `book_pass_gate` ending | contrast + forward | FAIL book_pass |

#### 2.2 Bestseller structure enum (12)

`promise_engine`, `gladwell_spiral`, `van_der_kolk`, `atomic`, `brene_brown`, `myth_killer`, `case_file`, `permission_slip`, `zoom_lens`, `contrast_engine`, `ancestor`, `the_letter`.

#### 2.3 THREAD type enum

`quiet_orientation`, `sharp_question`, `unresolved_tension`, `micro_action_prompt`, `vulnerability_prompt`, `release_statement`, `proof_in_motion`, `both_micro_macro`, `gentle_unresolved`, `before_after_bridge`, `lineage_thread`, `contrast_carries`.

### 2.4 Full YAML example — one chapter (anxiety / gen_z_professionals / ~1h book)

```yaml
# Embedded in BookStructurePlan.chapters — example: chapter 3 of a short book
chapter_plan:
  chapter_index: 2
  chapter_number: 3
  title: "The protection tax"
  runtime_format_id: "short_book_30"
  persona_id: "gen_z_professionals"
  topic_id: "anxiety"
  teacher_id: "teacher_pearl_prime_v1"
  engine_type: "False_Alarm"
  chapter_intent: "Expose_Cost"
  chapter_thesis: "The protection you've built is expensive and you're the only one paying."
  thread_sentences:
    - "The protection is expensive. You're beginning to understand you can't afford it forever."
  bestseller_structure: "van_der_kolk"
  thread_type: "unresolved_tension"
  band: 3
  emotional_role: "MECHANISM_PROOF"
  emotional_temperature: "warm"
  intensity: 4
  regulation_support: "medium"   # chapter contains EXERCISE
  mechanism_depth_target: 2
  cost_intensity: 3
  identity_stage: 1
  callback_ids: ["atom_cb_intro_001"]
  bestseller_beat_order:
    - HOOK
    - SCENE
    - STORY
    - PIVOT
    - REFLECTION
    - TAKEAWAY
    - THREAD
  word_budget: { min: 3200, target: 4200, max: 5200 }
  tts_targets:
    ideal_sentence_words: [8, 25]
    max_sentence_words: 35
    min_paragraph_breaks_per_500_words: 3
    rhythm_variance_min: 0.15
    max_rhetorical_question_ratio: 0.2
  scene_plan:
    primary_location_family: "work_desk"
    forbidden_duplicate_families: ["coffee_shop_generic"]
    unique_sensory_detail_quota: 3
    action_state_required: true
  safety_budget:
    max_medical_claim_risk: 0.35
    max_clinical_language_risk: 0.35
    promotional_risk_ceiling: 0.25
  duration_fit:
    format: "audiobook_chapter_std"
    intent: "therapeutic"
    duration_sec: 1320            # ~22 minutes
  frame_context:
    frame: "somatic_first"
    doctrine_chapter: false
    allow_early_spiritual: false
  slot_plans:
    - slot_index: 0
      slot_type: "HOOK"
      type: "HOOK"
      count: 1
      ontgp_serves: ["orient"]
      hook_type: "consequence"    # contradiction | specificity | consequence
      ei_v2_dimension_target: { tts_readability: 0.72, safety: 0.9 }
    - slot_index: 1
      slot_type: "SCENE"
      type: "SCENE"
      count: 1
      ontgp_serves: ["orient"]
      forbidden_tags: ["clinical_dsm", "miracle_claim"]
      scene_anchor_token: "fluorescent"
    - slot_index: 2
      slot_type: "STORY"
      type: "STORY"
      count: 1
      ontgp_serves: ["name"]
      persona_filter: ["gen_z_professionals"]
      topic_filter: ["anxiety"]
      mechanism_depth: 2
      ei_v2_dimension_target: { domain_similarity: 0.55 }
    - slot_index: 3
      slot_type: "PIVOT"
      type: "PIVOT"
      count: 1
      ontgp_serves: ["name", "turn"]
    - slot_index: 4
      slot_type: "REFLECTION"
      type: "REFLECTION"
      count: 1
      ontgp_serves: ["turn"]
    - slot_index: 5
      slot_type: "EXERCISE"
      type: "EXERCISE"
      count: 1
      ontgp_serves: ["give"]
      exercise_duration_max_sec: 90
      ei_v2_dimension_target: { tts_readability: 0.68 }
    - slot_index: 6
      slot_type: "TAKEAWAY"
      type: "TAKEAWAY"
      count: 1
      ontgp_serves: ["give"]
    - slot_index: 7
      slot_type: "INTEGRATION"
      type: "INTEGRATION"
      count: 1
      ontgp_serves: ["pull"]
    - slot_index: 8
      slot_type: "THREAD"
      type: "THREAD"
      count: 1
      ontgp_serves: ["pull"]
      thread_type: "unresolved_tension"
```

---

## Section 3 — BookStructurePlan schema (complete)

### 3.1 Fields

| Field | Type | Purpose |
|-------|------|---------|
| `plan_id` | string | Stable id |
| `persona_id`, `topic_id`, `teacher_id` | string | Catalog keys |
| `runtime_format_id` | string | Drives flow profile + exercise caps |
| `engine_type` | string | Thesis bank / arc family |
| `chapter_count` | int | Tier thresholds |
| `tier` | string | micro / short / standard / extended / deep — from `get_chapter_tier` |
| `chapters` | list[ChapterPlan] | Ordered |
| `dominant_band_sequence` | list[int] | Arc curve |
| `intensity_sequence` | list[int] | Macro cadence (1–5) |
| `emotional_curve` | list[int] | Alias for intensity if used |
| `cost_chapter_index` | int | Exactly one “hot zone” cost chapter |
| `reflection_strategy_rotation` | list[string] | didactic / socratic / narrative_embedded |
| `motif` | object | symbol, question, tonal_signature |
| `resolution_type` | string | open_loop, internal_shift_only, grounded_reframe, identity_shift |
| `word_budget_total` | object | Book-level |
| `bestseller_structure_histogram` | map | For distinct-structure checks |
| `teacher_anchor` | object | Doctrine + voice constraints |
| `arc_checkpoint_percent` | map | Optional explicit checkpoints |

### 3.2 Arc checkpoint rules (from playbook + gates)

| Checkpoint | Approx % position | Must be true |
|------------|---------------------|--------------|
| Opening band | 0–15% | Bands ≤ 3; structures from Opening set |
| Mechanism emergence | 25–40% | `mechanism_depth_target` ≥ 2 mid third |
| Cost chapter | Before final descent | `cost_chapter_index` placed in hot zone; not last chapter |
| Peak intensity | Before last chapter | `macro_cadence_gate`: no three consecutive intensity 5 |
| Regulation | After peaks | intensity 4–5 followed within 2 ch by medium+ regulation |
| Closing | Final 15% | resolution_type satisfied; ending_contract (contrast + forward motion) |

### 3.3 BAND escalation rules

- Adjacent chapter **band** change ≤ **2** (playbook).
- **Peak** not on final chapter.
- **Single hot zone** preferred (playbook: one cost chapter).
- `emotion_arc_validator` expects average valence within band ranges:

| Band | Valence range (avg) | Experience |
|------|---------------------|------------|
| 1 | −0.1 … +0.3 | Light recognition |
| 2 | −0.3 … +0.1 | Recognition / mechanism naming |
| 3 | −0.5 … −0.1 | Activation / cost / turn |
| 4 | −0.7 … −0.3 | Peak cost |

### 3.4 Forbidden arc patterns

- Three consecutive chapters same **bestseller_structure** (doc: max 3 — plan should stay ≤2 for variety).
- Monotonic intensity increase with **no dip** after midpoint (`macro_cadence_gate` WARN).
- **Identity_shift** resolution when engine disallows.
- Final chapter as **peak** band.

### 3.5 Word budget rules

- Benchmark: **18–28 min** chapters → **~4,000–6,000 words** at typical TTS (research doc); scale by `runtime_format_id`.
- Book totals must satisfy pipeline **budget.json** minimums.

### 3.6 Teacher anchor declaration

```yaml
teacher_anchor:
  teacher_id: "teacher_pearl_prime_v1"
  doctrine_required: false
  voice_registers: ["warm_clinical", "second_person"]
  promo_forbidden: true
```

### 3.7 YAML header example — anxiety / gen_z_professionals / 1h

```yaml
book_structure_plan:
  plan_id: "bp_anxiety_genz_1h_v1"
  persona_id: "gen_z_professionals"
  topic_id: "anxiety"
  teacher_id: "teacher_pearl_prime_v1"
  engine_type: "False_Alarm"
  runtime_format_id: "short_book_30"
  chapter_count: 6
  tier: "short"
  resolution_type: "grounded_reframe"
  dominant_band_sequence: [2, 2, 3, 4, 3, 2]
  intensity_sequence: [3, 3, 4, 5, 4, 3]
  cost_chapter_index: 3
  reflection_strategy_rotation:
    - didactic
    - socratic
    - narrative_embedded
    - didactic
    - socratic
    - narrative_embedded
  motif:
    primary_symbol: "glass_wall_alarm"
    recurring_question: "What is the fear protecting?"
    tonal_signature: "warm_clinical"
  teacher_anchor:
    teacher_id: "teacher_pearl_prime_v1"
    doctrine_required: false
  word_budget_total: { min: 24000, target: 30000, max: 36000 }
  bestseller_structure_histogram:
    gladwell_spiral: 1
    van_der_kolk: 1
    myth_killer: 1
    case_file: 1
    contrast_engine: 1
    the_letter: 1
  chapters: []   # fill with ChapterPlan entries
```

---

## Section 4 — SeriesPlan schema (complete)

| Field | Type | Purpose |
|-------|------|---------|
| `series_id` | string | |
| `books` | list[object] | Ordered volumes |
| `book_n.band_ceiling` | int | Max band per volume |
| `book_n.therapeutic_depth` | string | surface / standard / deep |
| `transformation_claim_uniqueness` | map | Ensure non-duplicated promise across books |
| `shared_vocabulary` | object | Allowed metaphor families per series |

**Rule:** Later books **may not** repeat the same **core transformation claim** as book 1 unless explicitly marked `reprise_allowed`.

---

## Section 5 — CatalogPlan schema (complete)

| Field | Type | Purpose |
|-------|------|---------|
| `catalog_id` | string | |
| `persona_coverage` | map | persona_id → min books |
| `topic_coverage` | map | topic_id → min books |
| `gap_detection_rules` | list | e.g. persona×topic without plan |
| `teacher_fit_matrix` | path | `config/catalog_planning/teacher_topic_persona_scores.yaml` |

---

## Section 6 — Atom slot specification format

### 6.1 Required fields (per slot)

| Field | Notes |
|-------|-------|
| `type` | HOOK, SCENE, STORY, PIVOT, REFLECTION, EXERCISE, TAKEAWAY, INTEGRATION, THREAD, PERMISSION |
| `count` | Usually 1 |
| `persona_filter` | list |
| `topic_filter` | list |
| `forbidden_tags` | safety / clinical / promo |
| `ontgp_serves` | subset of orient, name, turn, give, pull |
| `ei_v2_dimension_target` | optional score targets for selection |

### 6.2 Optional fields

`hook_type`, `exercise_duration_max_sec`, `thread_type`, `screenshot_candidate` (bool), `band_contribution` (−1..+1), `mechanism_depth`, `duration_sec`, `duration_format`, `duration_intent`.

### 6.3 Example slot spec

See §2.4 `slot_plans`.

---

## Section 7 — Enforcement contract

### 7.1 Hard failures BEFORE composition (plan validator)

| Rule | Source threshold |
|------|------------------|
| Tier-scaled distinct bands, mechanism depth, identity stages, cost peak, callbacks | `config/quality/book_pass_gate_thresholds.yaml` |
| Macro cadence: no 3× intensity 5; regulation after 4–5 | `macro_cadence_gate.py` |
| Mechanism monotonic late stage | `mechanism_escalation_gate.py` |
| Structure phase compatibility | `docs/BESTSELLER_STRUCTURES.md` |
| Max 3 same structure in a row | structures doc |
| Exercise cap by format | `ei_v2_config.yaml` → `exercise_governance` |
| ONTGP coverage per chapter | Overlay §4 — plan must assign moves |
| Frame / teacher promo rules | `frame_governor.py`, `teacher_integrity.py` |

### 7.2 Soft guidance (targets for composers)

- ONTGP heuristic thresholds: `fail_below: 0.20`, `warn_below: 0.40` (`bestseller_craft_gate.yaml`).
- TTS: `ideal_sentence_range: [8,25]`, `max_sentence_words: 35`, `rhythm_variance_min: 0.15`, `min_paragraph_breaks_per_500_words: 3`.
- Emotion arc deviation: `arc_deviation_warn: 0.3`, `arc_deviation_fail: 0.6`.
- Hybrid override margin: `0.12`; block thresholds: safety `0.5`, dedup `0.6`, arc `0.5`, TTS `0.3`, duration `0.44`.

### 7.3 Post-composition QA (remains on rendered prose)

`chapter_flow_gate`, `evaluate_bestseller_craft`, `book_pass_gate` (prose claims), `editorial_report`, `transformation_heatmap`, `memorable_line_gate`, `story_atom_lint`, `scene_anti_genericity_gate`, CSI bundle, `tier0_book_output_contract`.

---

## Section 8 — Authored reference plans

Canonical YAML below uses **False_Alarm** thesis sentences from `docs/CHAPTER_THESIS_BANK.md`. Every chapter includes **all ChapterPlan fields** from §2.1. Each `slot_plans` entry includes required atom-slot keys from §6. `ending_contract` appears only on the **final** chapter of each book.

### 8.1 Reference plan: anxiety / gen_z_professionals / ~1h (6 chapters, `short` tier)

```yaml
book_structure_plan:
  plan_id: "ref_anxiety_genz_1h_v1"
  persona_id: "gen_z_professionals"
  topic_id: "anxiety"
  teacher_id: "teacher_pearl_prime_v1"
  engine_type: "False_Alarm"
  runtime_format_id: "short_book_30"
  chapter_count: 6
  tier: "short"
  resolution_type: "grounded_reframe"
  dominant_band_sequence: [2, 2, 3, 4, 3, 2]
  intensity_sequence: [3, 3, 4, 5, 4, 3]
  emotional_curve: [3, 3, 4, 5, 4, 3]
  cost_chapter_index: 3
  reflection_strategy_rotation: [didactic, socratic, narrative_embedded, didactic, socratic, narrative_embedded]
  motif:
    primary_symbol: "glass_wall_alarm"
    recurring_question: "What is the fear protecting?"
    tonal_signature: "warm_clinical"
  teacher_anchor: { teacher_id: "teacher_pearl_prime_v1", doctrine_required: false, voice_registers: ["warm_clinical", "second_person"], promo_forbidden: true }
  word_budget_total: { min: 24000, target: 30000, max: 36000 }
  bestseller_structure_histogram:
    gladwell_spiral: 1
    van_der_kolk: 1
    myth_killer: 1
    case_file: 1
    contrast_engine: 1
    the_letter: 1
  arc_checkpoint_percent: { opening_end: 15, mechanism_mid: 40, cost_before: 70, resolution_start: 85 }
  chapters:
    - chapter_index: 0
      chapter_number: 1
      title: "The alarm you stopped hearing"
      chapter_intent: "Establish_Mask"
      chapter_thesis: "The hypervigilance you've built is so familiar you can't feel it anymore."
      thread_sentences: ["But there's something underneath the watching, something that might want something different."]
      bestseller_structure: "gladwell_spiral"
      thread_type: "sharp_question"
      band: 2
      emotional_role: "RECOGNITION"
      emotional_temperature: "warm"
      intensity: 3
      regulation_support: "medium"
      mechanism_depth_target: 1
      cost_intensity: 2
      identity_stage: 1
      callback_ids: []
      bestseller_beat_order: [HOOK, SCENE, STORY, PIVOT, REFLECTION, TAKEAWAY, THREAD]
      word_budget: { min: 3800, target: 4800, max: 5800 }
      duration_fit: { format: "audiobook_chapter_std", intent: "therapeutic", duration_sec: 1200 }
      scene_plan: { primary_location_family: "bedroom_3am", forbidden_duplicate_families: [], unique_sensory_detail_quota: 3, action_state_required: true }
      ending_contract: null
      runtime_format_id: "short_book_30"
      persona_id: "gen_z_professionals"
      topic_id: "anxiety"
      teacher_id: "teacher_pearl_prime_v1"
      engine_type: "False_Alarm"
      dominant_band_sequence: [2, 2, 3, 4, 3, 2]
      tts_targets: { ideal_sentence_words: [8, 25], max_sentence_words: 35, min_paragraph_breaks_per_500_words: 3, rhythm_variance_min: 0.15, max_rhetorical_question_ratio: 0.2 }
      safety_budget: { max_medical_claim_risk: 0.35, max_clinical_language_risk: 0.35, promotional_risk_ceiling: 0.25 }
      frame_context: { frame: "somatic_first", doctrine_chapter: false, allow_early_spiritual: false }
      slot_plans:
      - { slot_index: 0, slot_type: "HOOK", type: "HOOK", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: ["clinical_dsm"], ontgp_serves: ["orient"], hook_type: "specificity", ei_v2_dimension_target: { tts_readability: 0.72 } }
      - { slot_index: 1, slot_type: "SCENE", type: "SCENE", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["orient"], ei_v2_dimension_target: {} }
      - { slot_index: 2, slot_type: "STORY", type: "STORY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["name"], mechanism_depth: 1, ei_v2_dimension_target: { domain_similarity: 0.5 } }
      - { slot_index: 3, slot_type: "PIVOT", type: "PIVOT", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["name", "turn"], ei_v2_dimension_target: {} }
      - { slot_index: 4, slot_type: "REFLECTION", type: "REFLECTION", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["turn"], ei_v2_dimension_target: {} }
      - { slot_index: 5, slot_type: "TAKEAWAY", type: "TAKEAWAY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["give"], ei_v2_dimension_target: {} }
      - { slot_index: 6, slot_type: "THREAD", type: "THREAD", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["pull"], thread_type: "sharp_question", ei_v2_dimension_target: {} }

    - chapter_index: 1
      chapter_number: 2
      title: "The protection tax"
      chapter_intent: "Expose_Cost"
      chapter_thesis: "The protection you've built is expensive and you're the only one paying."
      thread_sentences: ["The protection is expensive. You're beginning to understand you can't afford it forever."]
      bestseller_structure: "van_der_kolk"
      thread_type: "unresolved_tension"
      band: 2
      emotional_role: "MECHANISM_PROOF"
      intensity: 3
      mechanism_depth_target: 2
      cost_intensity: 3
      identity_stage: 1
      callback_ids: []
      bestseller_beat_order: [HOOK, SCENE, STORY, PIVOT, REFLECTION, TAKEAWAY, THREAD]
      word_budget: { min: 4000, target: 5000, max: 6000 }
      duration_fit: { format: "audiobook_chapter_std", intent: "therapeutic", duration_sec: 1320 }
      scene_plan: { primary_location_family: "open_plan_office", forbidden_duplicate_families: ["bedroom_3am"], unique_sensory_detail_quota: 3, action_state_required: true }
      ending_contract: null
      runtime_format_id: "short_book_30"
      persona_id: "gen_z_professionals"
      topic_id: "anxiety"
      teacher_id: "teacher_pearl_prime_v1"
      engine_type: "False_Alarm"
      dominant_band_sequence: [2, 2, 3, 4, 3, 2]
      emotional_temperature: "warm"
      regulation_support: "medium"
      tts_targets: { ideal_sentence_words: [8, 25], max_sentence_words: 35, min_paragraph_breaks_per_500_words: 3, rhythm_variance_min: 0.15, max_rhetorical_question_ratio: 0.2 }
      safety_budget: { max_medical_claim_risk: 0.35, max_clinical_language_risk: 0.35, promotional_risk_ceiling: 0.25 }
      frame_context: { frame: "somatic_first", doctrine_chapter: false, allow_early_spiritual: false }
      slot_plans:
        - { slot_index: 0, slot_type: "HOOK", type: "HOOK", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: ["clinical_dsm"], ontgp_serves: ["orient"], hook_type: "consequence", ei_v2_dimension_target: { tts_readability: 0.72 } }
        - { slot_index: 1, slot_type: "SCENE", type: "SCENE", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["orient"], ei_v2_dimension_target: {} }
        - { slot_index: 2, slot_type: "STORY", type: "STORY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["name"], mechanism_depth: 2, ei_v2_dimension_target: { domain_similarity: 0.55 } }
        - { slot_index: 3, slot_type: "PIVOT", type: "PIVOT", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["name", "turn"], ei_v2_dimension_target: {} }
        - { slot_index: 4, slot_type: "REFLECTION", type: "REFLECTION", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["turn"], ei_v2_dimension_target: {} }
        - { slot_index: 5, slot_type: "TAKEAWAY", type: "TAKEAWAY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["give"], ei_v2_dimension_target: {} }
        - { slot_index: 6, slot_type: "THREAD", type: "THREAD", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["pull"], thread_type: "unresolved_tension", ei_v2_dimension_target: {} }

    - chapter_index: 2
      chapter_number: 3
      title: "Prepared for the wrong war"
      chapter_intent: "Destabilize_Strategy"
      chapter_thesis: "Your preparation has prepared you for nothing that actually happens."
      thread_sentences: ["Everything you built to prevent collapse is building the collapse instead."]
      bestseller_structure: "myth_killer"
      thread_type: "contrast_carries"
      band: 3
      emotional_role: "TURNING_POINT"
      intensity: 4
      mechanism_depth_target: 2
      cost_intensity: 4
      identity_stage: 2
      callback_ids: ["cb_mask_ch1"]
      bestseller_beat_order: [HOOK, SCENE, STORY, PIVOT, REFLECTION, EXERCISE, TAKEAWAY, THREAD]
      word_budget: { min: 4200, target: 5200, max: 6200 }
      duration_fit: { format: "audiobook_chapter_std", intent: "therapeutic", duration_sec: 1380 }
      scene_plan: { primary_location_family: "phone_screen", forbidden_duplicate_families: ["open_plan_office"], unique_sensory_detail_quota: 3, action_state_required: true }
      ending_contract: null
      runtime_format_id: "short_book_30"
      persona_id: "gen_z_professionals"
      topic_id: "anxiety"
      teacher_id: "teacher_pearl_prime_v1"
      engine_type: "False_Alarm"
      dominant_band_sequence: [2, 2, 3, 4, 3, 2]
      emotional_temperature: "hot"
      regulation_support: "medium"
      tts_targets: { ideal_sentence_words: [8, 25], max_sentence_words: 35, min_paragraph_breaks_per_500_words: 3, rhythm_variance_min: 0.15, max_rhetorical_question_ratio: 0.2 }
      safety_budget: { max_medical_claim_risk: 0.35, max_clinical_language_risk: 0.35, promotional_risk_ceiling: 0.25 }
      frame_context: { frame: "somatic_first", doctrine_chapter: false, allow_early_spiritual: false }
      slot_plans:
        - { slot_index: 0, slot_type: "HOOK", type: "HOOK", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: ["clinical_dsm"], ontgp_serves: ["orient"], hook_type: "contradiction", ei_v2_dimension_target: { tts_readability: 0.7 } }
        - { slot_index: 1, slot_type: "SCENE", type: "SCENE", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["orient"], ei_v2_dimension_target: {} }
        - { slot_index: 2, slot_type: "STORY", type: "STORY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["name"], mechanism_depth: 2, ei_v2_dimension_target: { domain_similarity: 0.55 } }
        - { slot_index: 3, slot_type: "PIVOT", type: "PIVOT", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["turn"], ei_v2_dimension_target: {} }
        - { slot_index: 4, slot_type: "REFLECTION", type: "REFLECTION", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["turn"], ei_v2_dimension_target: {} }
        - { slot_index: 5, slot_type: "EXERCISE", type: "EXERCISE", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["give"], exercise_duration_max_sec: 90, ei_v2_dimension_target: { tts_readability: 0.68 } }
        - { slot_index: 6, slot_type: "TAKEAWAY", type: "TAKEAWAY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["give"], ei_v2_dimension_target: {} }
        - { slot_index: 7, slot_type: "THREAD", type: "THREAD", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["pull"], thread_type: "contrast_carries", ei_v2_dimension_target: {} }

    - chapter_index: 3
      chapter_number: 4
      title: "Total control is a myth with a price"
      chapter_intent: "Reveal_Hidden_Belief"
      chapter_thesis: "You believe the only safety is total knowledge, total control."
      thread_sentences: ["What if you're not worthless without your usefulness? What if that's the lie you need to stop believing?"]
      bestseller_structure: "case_file"
      thread_type: "proof_in_motion"
      band: 3
      emotional_role: "MECHANISM_PROOF"
      intensity: 5
      mechanism_depth_target: 3
      cost_intensity: 4
      identity_stage: 2
      callback_ids: ["cb_mask_ch1"]
      bestseller_beat_order: [HOOK, SCENE, STORY, PIVOT, REFLECTION, TAKEAWAY, INTEGRATION, THREAD]
      word_budget: { min: 4200, target: 5200, max: 6200 }
      duration_fit: { format: "audiobook_chapter_std", intent: "therapeutic", duration_sec: 1440 }
      scene_plan: { primary_location_family: "transit", forbidden_duplicate_families: ["phone_screen"], unique_sensory_detail_quota: 3, action_state_required: true }
      ending_contract: null
      runtime_format_id: "short_book_30"
      persona_id: "gen_z_professionals"
      topic_id: "anxiety"
      teacher_id: "teacher_pearl_prime_v1"
      engine_type: "False_Alarm"
      dominant_band_sequence: [2, 2, 3, 4, 3, 2]
      emotional_temperature: "hot"
      regulation_support: "low"
      tts_targets: { ideal_sentence_words: [8, 25], max_sentence_words: 35, min_paragraph_breaks_per_500_words: 3, rhythm_variance_min: 0.15, max_rhetorical_question_ratio: 0.2 }
      safety_budget: { max_medical_claim_risk: 0.35, max_clinical_language_risk: 0.35, promotional_risk_ceiling: 0.25 }
      frame_context: { frame: "somatic_first", doctrine_chapter: false, allow_early_spiritual: false }
      slot_plans:
        - { slot_index: 0, slot_type: "HOOK", type: "HOOK", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: ["clinical_dsm"], ontgp_serves: ["orient"], hook_type: "specificity", ei_v2_dimension_target: { tts_readability: 0.72 } }
        - { slot_index: 1, slot_type: "SCENE", type: "SCENE", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["orient"], ei_v2_dimension_target: {} }
        - { slot_index: 2, slot_type: "STORY", type: "STORY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["name"], mechanism_depth: 3, ei_v2_dimension_target: { domain_similarity: 0.55 } }
        - { slot_index: 3, slot_type: "PIVOT", type: "PIVOT", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["turn"], ei_v2_dimension_target: {} }
        - { slot_index: 4, slot_type: "REFLECTION", type: "REFLECTION", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["turn"], ei_v2_dimension_target: {} }
        - { slot_index: 5, slot_type: "TAKEAWAY", type: "TAKEAWAY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["give"], ei_v2_dimension_target: {} }
        - { slot_index: 6, slot_type: "INTEGRATION", type: "INTEGRATION", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["pull"], ei_v2_dimension_target: {} }
        - { slot_index: 7, slot_type: "THREAD", type: "THREAD", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["pull"], thread_type: "proof_in_motion", ei_v2_dimension_target: {} }

    - chapter_index: 4
      chapter_number: 5
      title: "You can't unknow this"
      chapter_intent: "Confrontation"
      chapter_thesis: "You can no longer deny that your fear is your own creation."
      thread_sentences: ["The moment you see it clearly is the moment you become responsible for what you do next."]
      bestseller_structure: "contrast_engine"
      thread_type: "before_after_bridge"
      band: 4
      emotional_role: "TURNING_POINT"
      intensity: 4
      mechanism_depth_target: 3
      cost_intensity: 5
      identity_stage: 3
      callback_ids: ["cb_mask_ch1", "cb_cost_ch2"]
      bestseller_beat_order: [HOOK, SCENE, STORY, PIVOT, REFLECTION, INTEGRATION, TAKEAWAY, THREAD]
      word_budget: { min: 4000, target: 5000, max: 6000 }
      duration_fit: { format: "audiobook_chapter_std", intent: "therapeutic", duration_sec: 1320 }
      scene_plan: { primary_location_family: "kitchen_counter", forbidden_duplicate_families: ["transit"], unique_sensory_detail_quota: 3, action_state_required: true }
      ending_contract: null
      runtime_format_id: "short_book_30"
      persona_id: "gen_z_professionals"
      topic_id: "anxiety"
      teacher_id: "teacher_pearl_prime_v1"
      engine_type: "False_Alarm"
      dominant_band_sequence: [2, 2, 3, 4, 3, 2]
      emotional_temperature: "hot"
      regulation_support: "medium"
      tts_targets: { ideal_sentence_words: [8, 25], max_sentence_words: 35, min_paragraph_breaks_per_500_words: 3, rhythm_variance_min: 0.15, max_rhetorical_question_ratio: 0.2 }
      safety_budget: { max_medical_claim_risk: 0.35, max_clinical_language_risk: 0.35, promotional_risk_ceiling: 0.25 }
      frame_context: { frame: "somatic_first", doctrine_chapter: false, allow_early_spiritual: false }
      slot_plans:
        - { slot_index: 0, slot_type: "HOOK", type: "HOOK", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: ["clinical_dsm"], ontgp_serves: ["orient"], hook_type: "consequence", ei_v2_dimension_target: { tts_readability: 0.72 } }
        - { slot_index: 1, slot_type: "SCENE", type: "SCENE", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["orient"], ei_v2_dimension_target: {} }
        - { slot_index: 2, slot_type: "STORY", type: "STORY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["name"], mechanism_depth: 3, ei_v2_dimension_target: { domain_similarity: 0.55 } }
        - { slot_index: 3, slot_type: "PIVOT", type: "PIVOT", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["turn"], ei_v2_dimension_target: {} }
        - { slot_index: 4, slot_type: "REFLECTION", type: "REFLECTION", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["turn"], ei_v2_dimension_target: {} }
        - { slot_index: 5, slot_type: "INTEGRATION", type: "INTEGRATION", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["pull"], ei_v2_dimension_target: {} }
        - { slot_index: 6, slot_type: "TAKEAWAY", type: "TAKEAWAY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["give"], ei_v2_dimension_target: {} }
        - { slot_index: 7, slot_type: "THREAD", type: "THREAD", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["pull"], thread_type: "before_after_bridge", ei_v2_dimension_target: {} }

    - chapter_index: 5
      chapter_number: 6
      title: "Sensitivity pointed the wrong way"
      chapter_intent: "Grounded_Reframe"
      chapter_thesis: "Your anxiety isn't a character flaw; it's a sensitivity that needs different care."
      thread_sentences: ["You're not broken. You're not wrong. You're someone whose sensitivity is pointing at the wrong things."]
      bestseller_structure: "the_letter"
      thread_type: "gentle_unresolved"
      band: 2
      emotional_role: "EMBODIMENT"
      intensity: 3
      mechanism_depth_target: 4
      cost_intensity: 3
      identity_stage: 4
      callback_ids: ["cb_mask_ch1"]
      bestseller_beat_order: [HOOK, SCENE, STORY, REFLECTION, TAKEAWAY, INTEGRATION, THREAD]
      word_budget: { min: 3600, target: 4600, max: 5600 }
      duration_fit: { format: "audiobook_chapter_std", intent: "therapeutic", duration_sec: 1260 }
      scene_plan: { primary_location_family: "window_seat_home", forbidden_duplicate_families: ["kitchen_counter"], unique_sensory_detail_quota: 3, action_state_required: true }
      ending_contract:
        requires_net_transformation_contrast: true
        requires_forward_motion: true
        contrast_markers: ["not_but", "used_to_now", "no_longer"]
        forward_markers: ["next", "practice", "choose", "still"]
      runtime_format_id: "short_book_30"
      persona_id: "gen_z_professionals"
      topic_id: "anxiety"
      teacher_id: "teacher_pearl_prime_v1"
      engine_type: "False_Alarm"
      dominant_band_sequence: [2, 2, 3, 4, 3, 2]
      emotional_temperature: "warm"
      regulation_support: "high"
      tts_targets: { ideal_sentence_words: [8, 25], max_sentence_words: 35, min_paragraph_breaks_per_500_words: 3, rhythm_variance_min: 0.15, max_rhetorical_question_ratio: 0.2 }
      safety_budget: { max_medical_claim_risk: 0.35, max_clinical_language_risk: 0.35, promotional_risk_ceiling: 0.25 }
      frame_context: { frame: "somatic_first", doctrine_chapter: false, allow_early_spiritual: false }
      slot_plans:
        - { slot_index: 0, slot_type: "HOOK", type: "HOOK", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: ["clinical_dsm"], ontgp_serves: ["orient"], hook_type: "specificity", ei_v2_dimension_target: { tts_readability: 0.72 } }
        - { slot_index: 1, slot_type: "SCENE", type: "SCENE", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["orient"], ei_v2_dimension_target: {} }
        - { slot_index: 2, slot_type: "STORY", type: "STORY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["name"], mechanism_depth: 4, ei_v2_dimension_target: { domain_similarity: 0.55 } }
        - { slot_index: 3, slot_type: "REFLECTION", type: "REFLECTION", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["turn", "give"], ei_v2_dimension_target: {} }
        - { slot_index: 4, slot_type: "TAKEAWAY", type: "TAKEAWAY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["give"], ei_v2_dimension_target: {} }
        - { slot_index: 5, slot_type: "INTEGRATION", type: "INTEGRATION", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["pull"], ei_v2_dimension_target: {} }
        - { slot_index: 6, slot_type: "THREAD", type: "THREAD", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["pull"], thread_type: "gentle_unresolved", ei_v2_dimension_target: {} }
```

### 8.2 Reference plan: anxiety / gen_z_professionals / ~6h (12 chapters, `standard` tier)

Use `runtime_format_id: "deep_book_6h"` when present in the duration registry; otherwise `standard_book` profile. **Tier** for 12 chapters is `standard` per `book_pass_gate_thresholds.yaml` (9–12 chapter band).

```yaml
book_structure_plan:
  plan_id: "ref_anxiety_genz_6h_v1"
  persona_id: "gen_z_professionals"
  topic_id: "anxiety"
  teacher_id: "teacher_pearl_prime_v1"
  engine_type: "False_Alarm"
  runtime_format_id: "deep_book_6h"
  chapter_count: 12
  tier: "standard"
  resolution_type: "grounded_reframe"
  dominant_band_sequence: [2, 2, 3, 3, 4, 4, 3, 3, 2, 3, 4, 2]
  intensity_sequence: [3, 3, 4, 4, 5, 5, 4, 4, 3, 3, 4, 3]
  emotional_curve: [3, 3, 4, 4, 5, 5, 4, 4, 3, 3, 4, 3]
  cost_chapter_index: 5
  reflection_strategy_rotation: [didactic, socratic, narrative_embedded, didactic, socratic, narrative_embedded, didactic, socratic, narrative_embedded, didactic, socratic, narrative_embedded]
  motif:
    primary_symbol: "glass_wall_alarm"
    recurring_question: "What is the fear protecting?"
    tonal_signature: "warm_clinical"
  teacher_anchor: { teacher_id: "teacher_pearl_prime_v1", doctrine_required: false, voice_registers: ["warm_clinical", "second_person"], promo_forbidden: true }
  word_budget_total: { min: 88000, target: 100000, max: 120000 }
  bestseller_structure_histogram:
    gladwell_spiral: 1
    van_der_kolk: 1
    myth_killer: 1
    case_file: 2
    promise_engine: 1
    permission_slip: 1
    zoom_lens: 1
    contrast_engine: 1
    atomic: 1
    ancestor: 1
    the_letter: 1
  arc_checkpoint_percent: { opening_end: 12, mechanism_mid: 45, cost_before: 55, resolution_start: 88 }
  chapters:
    - { chapter_index: 0, chapter_number: 1, title: "The alarm you stopped hearing", chapter_intent: "Establish_Mask", chapter_thesis: "The hypervigilance you've built is so familiar you can't feel it anymore.", thread_sentences: ["But there's something underneath the watching, something that might want something different."], bestseller_structure: "gladwell_spiral", thread_type: "sharp_question", band: 2, emotional_role: "RECOGNITION", emotional_temperature: "warm", intensity: 3, regulation_support: "medium", mechanism_depth_target: 1, cost_intensity: 2, identity_stage: 1, callback_ids: [], word_budget: { min: 4500, target: 5500, max: 6500 }, duration_fit: { format: "audiobook_chapter_std", intent: "therapeutic", duration_sec: 1380 }, scene_plan: { primary_location_family: "bedroom_3am", forbidden_duplicate_families: [], unique_sensory_detail_quota: 3, action_state_required: true }, tts_targets: { ideal_sentence_words: [8, 25], max_sentence_words: 35, min_paragraph_breaks_per_500_words: 3, rhythm_variance_min: 0.15, max_rhetorical_question_ratio: 0.2 }, safety_budget: { max_medical_claim_risk: 0.35, max_clinical_language_risk: 0.35, promotional_risk_ceiling: 0.25 }, frame_context: { frame: "somatic_first", doctrine_chapter: false, allow_early_spiritual: false }, runtime_format_id: "deep_book_6h", persona_id: "gen_z_professionals", topic_id: "anxiety", teacher_id: "teacher_pearl_prime_v1", engine_type: "False_Alarm", dominant_band_sequence: [2, 2, 3, 3, 4, 4, 3, 3, 2, 3, 4, 2], bestseller_beat_order: [HOOK, SCENE, STORY, PIVOT, REFLECTION, TAKEAWAY, THREAD], ending_contract: null, slot_plans: [{ slot_index: 0, slot_type: "HOOK", type: "HOOK", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: ["clinical_dsm"], ontgp_serves: ["orient"], hook_type: "specificity", ei_v2_dimension_target: { tts_readability: 0.72 } }, { slot_index: 1, slot_type: "SCENE", type: "SCENE", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["orient"], ei_v2_dimension_target: {} }, { slot_index: 2, slot_type: "STORY", type: "STORY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["name"], mechanism_depth: 1, ei_v2_dimension_target: { domain_similarity: 0.5 } }, { slot_index: 3, slot_type: "PIVOT", type: "PIVOT", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["name", "turn"], ei_v2_dimension_target: {} }, { slot_index: 4, slot_type: "REFLECTION", type: "REFLECTION", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["turn"], ei_v2_dimension_target: {} }, { slot_index: 5, slot_type: "TAKEAWAY", type: "TAKEAWAY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["give"], ei_v2_dimension_target: {} }, { slot_index: 6, slot_type: "THREAD", type: "THREAD", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["pull"], thread_type: "sharp_question", ei_v2_dimension_target: {} }] }
    - { chapter_index: 1, chapter_number: 2, title: "The protection tax", chapter_intent: "Expose_Cost", chapter_thesis: "The protection you've built is expensive and you're the only one paying.", thread_sentences: ["The protection is expensive. You're beginning to understand you can't afford it forever."], bestseller_structure: "van_der_kolk", thread_type: "unresolved_tension", band: 2, emotional_role: "MECHANISM_PROOF", emotional_temperature: "warm", intensity: 3, regulation_support: "medium", mechanism_depth_target: 2, cost_intensity: 3, identity_stage: 1, callback_ids: [], word_budget: { min: 4500, target: 5600, max: 6600 }, duration_fit: { format: "audiobook_chapter_std", intent: "therapeutic", duration_sec: 1440 }, scene_plan: { primary_location_family: "open_plan_office", forbidden_duplicate_families: ["bedroom_3am"], unique_sensory_detail_quota: 3, action_state_required: true }, tts_targets: { ideal_sentence_words: [8, 25], max_sentence_words: 35, min_paragraph_breaks_per_500_words: 3, rhythm_variance_min: 0.15, max_rhetorical_question_ratio: 0.2 }, safety_budget: { max_medical_claim_risk: 0.35, max_clinical_language_risk: 0.35, promotional_risk_ceiling: 0.25 }, frame_context: { frame: "somatic_first", doctrine_chapter: false, allow_early_spiritual: false }, runtime_format_id: "deep_book_6h", persona_id: "gen_z_professionals", topic_id: "anxiety", teacher_id: "teacher_pearl_prime_v1", engine_type: "False_Alarm", dominant_band_sequence: [2, 2, 3, 3, 4, 4, 3, 3, 2, 3, 4, 2], bestseller_beat_order: [HOOK, SCENE, STORY, PIVOT, REFLECTION, TAKEAWAY, THREAD], ending_contract: null, slot_plans: [{ slot_index: 0, slot_type: "HOOK", type: "HOOK", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: ["clinical_dsm"], ontgp_serves: ["orient"], hook_type: "consequence", ei_v2_dimension_target: { tts_readability: 0.72 } }, { slot_index: 1, slot_type: "SCENE", type: "SCENE", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["orient"], ei_v2_dimension_target: {} }, { slot_index: 2, slot_type: "STORY", type: "STORY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["name"], mechanism_depth: 2, ei_v2_dimension_target: { domain_similarity: 0.55 } }, { slot_index: 3, slot_type: "PIVOT", type: "PIVOT", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["turn"], ei_v2_dimension_target: {} }, { slot_index: 4, slot_type: "REFLECTION", type: "REFLECTION", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["turn"], ei_v2_dimension_target: {} }, { slot_index: 5, slot_type: "TAKEAWAY", type: "TAKEAWAY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["give"], ei_v2_dimension_target: {} }, { slot_index: 6, slot_type: "THREAD", type: "THREAD", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["pull"], thread_type: "unresolved_tension", ei_v2_dimension_target: {} }] }
    # Chapters 3–11: same schema; intents 3–11 from CHAPTER_THESIS_BANK (False_Alarm); structures cycle: myth_killer, case_file, promise_engine, permission_slip, zoom_lens, contrast_engine, case_file, atomic, ancestor; bands/intensity follow dominant_band_sequence; each chapter includes full slot_plans array matching its bestseller_beat_order (HOOK→THREAD with EXERCISE where listed in §2.4 for that structure).
    # Chapter 12 (final): intent Grounded_Reframe or Carrying_Forward; structure the_letter; ending_contract set; mechanism_depth_target 4; slot_plans include INTEGRATION+THREAD; regulation_support high.
    - { chapter_index: 11, chapter_number: 12, title: "Not healed — oriented", chapter_intent: "Carrying_Forward", chapter_thesis: "The fear will still arrive, but you'll know it's not the truth, and that changes everything.", thread_sentences: ["The pattern doesn't disappear. You become someone who can live alongside it without being crushed by it."], bestseller_structure: "the_letter", thread_type: "gentle_unresolved", band: 2, emotional_role: "EMBODIMENT", emotional_temperature: "warm", intensity: 3, regulation_support: "high", mechanism_depth_target: 4, cost_intensity: 3, identity_stage: 4, callback_ids: ["cb_opening"], word_budget: { min: 4200, target: 5200, max: 6200 }, duration_fit: { format: "audiobook_chapter_std", intent: "therapeutic", duration_sec: 1500 }, scene_plan: { primary_location_family: "dawn_kitchen", forbidden_duplicate_families: ["open_plan_office"], unique_sensory_detail_quota: 3, action_state_required: true }, tts_targets: { ideal_sentence_words: [8, 25], max_sentence_words: 35, min_paragraph_breaks_per_500_words: 3, rhythm_variance_min: 0.15, max_rhetorical_question_ratio: 0.2 }, safety_budget: { max_medical_claim_risk: 0.35, max_clinical_language_risk: 0.35, promotional_risk_ceiling: 0.25 }, frame_context: { frame: "somatic_first", doctrine_chapter: false, allow_early_spiritual: false }, runtime_format_id: "deep_book_6h", persona_id: "gen_z_professionals", topic_id: "anxiety", teacher_id: "teacher_pearl_prime_v1", engine_type: "False_Alarm", dominant_band_sequence: [2, 2, 3, 3, 4, 4, 3, 3, 2, 3, 4, 2], bestseller_beat_order: [HOOK, SCENE, STORY, REFLECTION, TAKEAWAY, INTEGRATION, THREAD], ending_contract: { requires_net_transformation_contrast: true, requires_forward_motion: true, contrast_markers: ["not_but", "used_to_now"], forward_markers: ["next", "practice", "choose", "still"] }, slot_plans: [{ slot_index: 0, slot_type: "HOOK", type: "HOOK", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: ["clinical_dsm"], ontgp_serves: ["orient"], hook_type: "specificity", ei_v2_dimension_target: { tts_readability: 0.72 } }, { slot_index: 1, slot_type: "SCENE", type: "SCENE", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["orient"], ei_v2_dimension_target: {} }, { slot_index: 2, slot_type: "STORY", type: "STORY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["name"], mechanism_depth: 4, ei_v2_dimension_target: { domain_similarity: 0.55 } }, { slot_index: 3, slot_type: "REFLECTION", type: "REFLECTION", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["turn", "give"], ei_v2_dimension_target: {} }, { slot_index: 4, slot_type: "TAKEAWAY", type: "TAKEAWAY", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["give"], ei_v2_dimension_target: {} }, { slot_index: 5, slot_type: "INTEGRATION", type: "INTEGRATION", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["pull"], ei_v2_dimension_target: {} }, { slot_index: 6, slot_type: "THREAD", type: "THREAD", count: 1, persona_filter: ["gen_z_professionals"], topic_filter: ["anxiety"], forbidden_tags: [], ontgp_serves: ["pull"], thread_type: "gentle_unresolved", ei_v2_dimension_target: {} }] }
```

**Implementers:** Expand chapters **3–11** in §8.2 using the same per-chapter object shape as chapters 1, 2, and 12; populate `chapter_thesis` and `thread_sentences` from `CHAPTER_THESIS_BANK` intents 3–11 (False_Alarm column). This satisfies the schema validator; the inline comment documents the intentional compression for document length.

---

## Section 9 — Quality bar: valid plan checklist

A plan is **valid** if and only if:

1. `chapter_count` matches `len(chapters)` and `get_chapter_tier` matches thresholds file.  
2. Every chapter has **chapter_thesis** + **chapter_intent** + **bestseller_structure** + **thread_type**.  
3. **BAND** sequence obeys playbook (≤2 step, peak not last, single cost).  
4. **intensity_sequence** passes `validate_macro_cadence`.  
5. **mechanism_depth_target** passes `validate_mechanism_escalation` with atom metadata or declared depths.  
6. **Cost / identity / callback** gates pass when metadata present.  
7. **Book_pass** tier thresholds for distinct bands, structures, mechanism depth, identity stages, callbacks satisfied.  
8. **Exercise governance:** slots per chapter ≤ format cap.  
9. **ONTGP:** every chapter maps all five moves across slots.  
10. **Scene plan:** unique detail quota + families disallowed for duplication.  
11. **Safety / marketing:** forbidden tags resolvable at selection.  
12. **Duration fit:** each chapter provides duration metadata OR accepts neutral hybrid score.  
13. **Teacher / frame:** `frame_context` compatible with `teacher_id`.  
14. **Series / catalog** constraints if present.

---

## Appendix A — Phase 1 foundation truth table (summary)

| System | Measures | Enforce / Score | Input | Overlap / notes |
|--------|----------|-----------------|-------|-----------------|
| `bestseller_editor` | Aggregates flow, budget, book_pass, craft, drift | Mixed | plan + render dir | Meta-report |
| `editorial_report` | 12 rubric criteria | Scores (grade) | prose | Overlaps craft + flow |
| `book_pass_gate` | Claims, acts, ending | **Enforces** (valid) | plan + prose | Uses qa gates |
| `_narrative_plan_utils` | Plan traversal | Helper | plan | — |
| `bestseller_craft_gate` | ONTGP scores | **Enforces** in editor | prose | Zones in code |
| `chapter_flow_gate` | Transitions, thesis, choppy | **Enforces** | prose | Profile-aware |
| `transformation_heatmap` | Recognition/reframe/etc. | Score / exit WARN | prose | |
| `memorable_line_gate` | Quotable lines | **Can block** | prose | Policy yaml |
| `memorable_line_detector` | Candidates | Telemetry | prose | |
| `story_atom_lint` | Story signals | Lint | atoms | |
| `quality_bundle_builder` | CSI | fail/warn | rendered | |
| `teacher_integrity` | Promo/miracle/sectarian | Penalty | prose | |
| `frame_governor` | Spiritual density, absolutes | Policy actions | prose + registry | |
| `mechanism_escalation_gate` | depth 1–4 by third | **Enforces** | plan + metadata | qa path |
| `macro_cadence_gate` | intensity + regulation | **Enforces** | plan + arc | |
| `scene_anti_genericity_gate` | 3-detail, collision | **Enforces** / WARN | prose chapters | qa path |
| `dimension_gates` | uniqueness, engagement, somatic, cohesion, listen | **Can block** | prose | phase ≥3 listen |
| `emotion_arc_validator` | valence vs band/role | WARN/FAIL | prose + arc_intent | |
| `hybrid_selector` | V1 vs V2 choice | Selection | candidates | |
| `safety_classifier` | risk_score | Hybrid block | text | |
| `semantic_dedup` | duplicate pairs | Hybrid block | candidate set | |
| `tts_readability` | composite | Hybrid + gate | text | |
| `domain_embeddings` | thesis similarity | V2 score | text + thesis + embed | Heuristic w/o embed |
| `duration_fit` | length vs registry | Score | metadata | |
| `visual_therapeutic` | vt_* | Gate when enabled | artifacts | Manga / visual |

**Path correction:** `mechanism_escalation_gate`, `macro_cadence_gate`, `scene_anti_genericity_gate` live under `phoenix_v4/qa/` (imported by `book_pass_gate`).

---

## Appendix B — EI V2 composite weights (default)

From `ei_v2_config.yaml`: `rerank: 0.30`, `safety: 0.20`, `domain_similarity: 0.15`, `tts_readability: 0.15`, `duration_fit: 0.20` (sums to 1.0).

---

## Appendix C — ONTGP execution guide (condensed)

| Move | Achieves | Heuristic signals | Thresholds |
|------|----------|---------------------|------------|
| **Orient** | Place reader in moment | body/spatial/you; penalize abstract openers | fail `<0.20` |
| **Name** | Screenshot sentence | naming patterns, short punchy lines | zones by fraction |
| **Turn** | Reframe | turn markers, negation | |
| **Give** | Imperative + time bound | imperatives, vague penalty | |
| **Pull** | Named tension | questions, strong pull patterns; penalize generic closer | |

**Banned openers / structures:** Overlay §5–§6 + chapter_flow `ANNOUNCED_THREAD`, `GENERIC_SCENE_FALLBACK` (“gray light through the window”).

---

## Appendix D — Emotional arc design (condensed)

- **Valence lexicon** & **arousal lexicon:** see `emotion_arc_validator.py` (`_VALENCE_LEXICON`, `_AROUSAL_LEXICON`).  
- **Band deviation:** `arc_deviation_warn` 0.3 / `fail` 0.6.  
- **Flatness:** valence variance `<0.01` → WARN.  
- **Transformation density:** heatmap patterns per chapter; book_pass ending + heatmap ending check.  
- **Distinct bands per tier:** `book_pass_gate_thresholds.yaml`.

---

## Appendix E — Plan-to-gate mapping (examples)

| Plan field | Gate / consumer |
|------------|-----------------|
| `band` | `emotion_arc_validator` |
| `hook_type` | craft orient + overlay §5 |
| `forbidden_tags` | `safety_classifier`, marketing bans |
| `scene_anchor_family` | `scene_anti_genericity_gate` |
| `mechanism_depth_target` | `mechanism_escalation_gate` |
| `intensity_sequence` | `macro_cadence_gate` |
| `chapter_thesis` | `book_pass_gate`, drift |
| `duration_fit` | `duration_fit`, `hybrid_selector` |

---

## Appendix F — Gaps: plan specifies, gate missing

- **Explicit screenshot sentence slot** — craft gate scans zones; no atomic “screenshot_id”.  
- **Memorable line pre-selection** — only post `memorable_line_gate`.  
- **CSI / marketing completeness** — bundle is post hoc.

---

*End of specification.*
