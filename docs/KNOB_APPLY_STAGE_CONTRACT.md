# Knob Apply Stage Contract

**Authority:** Architecture spec only (no runtime implementation in this change).  
**Subsystem:** `core_pipeline`  
**Project:** `proj_state_convergence_20260328`  
**Related config:** `config/knobs/topic_knob_profiles.yaml`, `config/spines/*_spine.yaml`, `config/format_selection/format_registry.yaml`, `config/topic_engine_bindings.yaml`, `config/catalog_planning/platform_knob_tuning.yaml`  
**Related code (context, not scope):** `phoenix_v4/planning/chapter_planner.py`, `phoenix_v4/planning/assembly_compiler.py`, `phoenix_v4/planning/registry_resolver.py`, `phoenix_v4/rendering/chapter_composer.py`, `scripts/run_pipeline.py`

This document is the single contract a developer needs to implement `apply_knobs()` without clarifying questions.

---

## 1. Stage position in pipeline

### 1.1 Target topology (new pipeline)

```
SpineSelect
  │
  │ Output: SelectedSpine (topic, family, chapters, sequencing rules, tone/pacing)
  │
  ▼
KnobApply  ◄── ResolvedKnobProfile (+ optional persona/platform/runtime overlays)
  │
  │ Output: ShapedSpine (per-chapter weights, targets, knob-derived fields, audit)
  │
  ▼
BeatmapCompile
  │
  │ Output: Beatmap (concrete slot_definitions per chapter, atom criteria, hooks)
  │
  ▼
EnrichmentSelect → ChapterCompose → BookRender → QualityGate
```

### 1.2 Inputs consumed

| Source | Consumed by KnobApply? | Notes |
|--------|-------------------------|-------|
| Selected spine YAML (via `SelectedSpine` JSON) | Yes | Structural and sequencing truth |
| `topic_knob_profiles.yaml` (via `KnobProfile` JSON) | Yes | Densities, floors, ceilings, phases, dangerous combos |
| `format_registry.yaml` | Yes (indirect) | `runtime_format` → word budget, default chapter count hint |
| `platform_knob_tuning.yaml` | Yes (optional) | Chapter duration bounds, preferred structures/runtimes |
| `topic_engine_bindings.yaml` | No (selection gate) | Belongs to SpineSelect / catalog gates before spine lock-in |
| `topic_skins.yaml` | No | Vocabulary guard; downstream prose |
| Beatmap / enrichments | No | Produced **after** KnobApply |

### 1.3 Responsibilities boundary

**KnobApply SHALL** merge spine-locked intent with topic knob policy and runtime/platform/persona overlays, emitting **numeric/nominal shaping** (weights, targets, allowed compression, phase labels, enrichment priorities) and a complete **audit trail**.

**KnobApply SHALL NOT:**

- Change any chapter **thesis**, **role**, **working_title** canonical text fields from the spine (copy-through only).
- Reorder, insert, or remove chapters (chapter count changes belong to **SpineSelect** + **BeatmapCompile**/`format_registry` compatibility, not KnobApply).
- Select atoms, registry variants, or teacher overlays ( **EnrichmentSelect** / `registry_resolver.py` ).
- Render prose ( **ChapterCompose** ).
- Run quality scoring ( **QualityGate** ).
- Override **spine sequencing rules** (see merge order §5).

---

## 2. Input schema — `SelectedSpine`

`SpineSelect` normalizes spine YAML (`config/spines/<family_id>_spine.yaml`) into machine JSON. Field names follow the spine files today.

### 2.1 Top-level object

```json
{
  "schema_version": 1,
  "stage": "spine_select",
  "family_id": "anxiety",
  "family_name": "Anxiety / False Alarm",
  "topic": "anxiety",
  "adjacent_topics": ["social_anxiety", "sleep_anxiety", "overthinking"],
  "primary_mechanism": "false_alarm",
  "allowed_engines": ["false_alarm", "spiral", "watcher", "overwhelm", "shame", "comparison", "grief"],
  "forbidden_engines": [],
  "reader_starting_state": "…",
  "reader_ending_state": "…",
  "what_makes_this_family_different": "…",
  "chapters": [ /* SelectedChapter × N */ ],
  "sequencing_rules": {
    "must_come_before": ["…"],
    "cannot_come_too_early": ["…"],
    "saved_for_late_book": ["…"]
  },
  "tone_and_pacing": {
    "intensity_profile": null,
    "trust_curve": "…",
    "action_timing": "…",
    "mechanism_timing": "…",
    "permission_timing": "…"
  },
  "source": {
    "path": "config/spines/anxiety_spine.yaml",
    "content_sha256": "optional; for audit replay"
  }
}
```

**`intensity_profile` normalization:** Spine YAML may store a list of labeled strings (anxiety, grief) or a 12-number array (burnout). `SelectedSpine` MUST normalize to **one** JSON-safe form:

```json
"intensity_profile": {
  "style": "labeled_list",
  "by_chapter": [
    { "chapter": 1, "label": "low — familiar, recognizing, safe" }
  ]
}
```

or

```json
"intensity_profile": {
  "style": "numeric_12",
  "levels": [3, 5, 5, 4, 6, 8, 5, 8, 5, 6, 5, 4]
}
```

Implementers of SpineSelect choose one style per spine family; KnobApply MUST accept either.

### 2.2 `SelectedChapter`

```json
{
  "number": 1,
  "role": "recognition",
  "working_title": "The Alarm That Won't Stop Ringing",
  "thesis": "…",
  "emotional_job": "…",
  "practical_job": "…",
  "what_changes": "…",
  "required_sections": ["HOOK", "SCENE", "REFLECTION"],
  "forbidden_moves": [
    "Do not introduce any practice, exercise, or technique."
  ],
  "recommended_enrichments": [
    "Open with a scene that is completely ordinary — morning, car, inbox —"
  ],
  "claim_someone_could_argue": "…",
  "why_this_chapter_exists": "…",
  "what_comes_next": "…"
}
```

**Real examples:**

- **Anxiety ch1** — `required_sections`: `["HOOK", "SCENE", "REFLECTION"]`; forbidden_moves include **no practice** and **do not explain the mechanism yet** (`anxiety_spine.yaml`).
- **Grief ch1** — same slot pattern; forbidden_moves include **no forward momentum toward resolution** (`grief_spine.yaml`).
- **Burnout ch4** — `required_sections` may include **`SOMATIC_INVENTORY`** in addition to HOOK/SCENE/REFLECTION (`burnout_spine.yaml`).

---

## 3. Input schema — `KnobProfile`

Produced by a **knob resolver** that loads `config/knobs/topic_knob_profiles.yaml` for `topics.<topic>` and maps YAML → JSON. All **knob field names** below match that file.

### 3.1 Top-level object

```json
{
  "schema_version": 1,
  "topic": "anxiety",
  "source": "config/knobs/topic_knob_profiles.yaml",
  "primary_mechanism": "false_alarm",
  "allowed_engines": ["false_alarm", "spiral", "watcher", "overwhelm", "shame", "comparison", "grief"],
  "forbidden_engines": [],
  "knob_defaults": {
    "story_density": "high",
    "exercise_density": "medium",
    "mechanism_depth": "medium",
    "reflection_depth": "medium",
    "pacing_profile": "measured",
    "emotional_temperature": "warm",
    "practical_vs_contemplative": "contemplative_first",
    "teacher_presence": "high",
    "spirituality_level": "secular",
    "compression": "none",
    "narrative_structure": "promise_engine",
    "runtime_target": "standard"
  },
  "hard_floors": {
    "emotional_temperature": "warm",
    "story_density": "medium",
    "pacing_profile": "measured"
  },
  "hard_ceilings": {
    "exercise_density": "medium",
    "spirituality_level": "moderate",
    "compression": "light"
  },
  "phase_overrides": {
    "early_book": {
      "exercise_density": "low",
      "mechanism_depth": "light",
      "practical_vs_contemplative": "contemplative",
      "teacher_presence": "high"
    },
    "mid_book": {
      "exercise_density": "medium",
      "mechanism_depth": "medium",
      "practical_vs_contemplative": "contemplative_first"
    },
    "late_book": {
      "exercise_density": "high",
      "practical_vs_contemplative": "balanced",
      "reflection_depth": "high"
    }
  },
  "dangerous_combinations": [
    {
      "knobs": ["exercise_density_high", "emotional_temperature_clinical"],
      "chapter_range": "ch1-4",
      "reason": "…"
    }
  ],
  "platform_conflicts": [
    {
      "platform": ["ximalaya", "kakao_page", "naver_audiobook"],
      "conflict": "…",
      "resolution": "…"
    }
  ],
  "research_citations": [],
  "requires_human_decision": [],
  "persona_overrides": {},
  "platform_overrides": {}
}
```

**Phase keys** are exactly `early_book`, `mid_book`, `late_book` (not `early`/`mid`/`late`).

**`runtime_target` in YAML** uses values like `standard`; the resolver MUST map `standard` → canonical runtime format id **`standard_book`** when passing into KnobApply (see §4.1).

**`dangerous_combinations.knobs`:** YAML uses symbolic tags (e.g. `exercise_density_high`, `chapter_range_ch1-8`). The resolver MUST preserve these tags verbatim for matching. KnobApply MUST expand **resolved** knob state into the same tag vocabulary for each chapter before evaluation (see §9).

**Grief exemplar fields** (`topics.grief`): `knob_defaults.exercise_density` is `"low"` with `hard_floors.exercise_density: "none"` until ch09; `hard_ceilings.practical_vs_contemplative` is `"contemplative"` (no practical before ch09); `phase_overrides.early_book.exercise_density` is `"none"`.

**Burnout exemplar fields** (`topics.burnout`): `knob_defaults.narrative_structure` is `"gladwell_spiral"`; `phase_overrides.mid_book.exercise_density` remains `"none"` through ch9; `late_book.pacing_profile` is `"slow"`.

---

## 4. Output schema — `ShapedSpine`

### 4.1 Top-level object

```json
{
  "schema_version": 1,
  "stage": "knob_apply",
  "topic": "anxiety",
  "family_id": "anxiety",
  "runtime_format": "standard_book",
  "structural_format": null,
  "chapters": [ /* ShapedChapter × N */ ],
  "knob_audit": { /* KnobAudit */ },
  "selected_spine_sha256": "optional"
}
```

- **`runtime_format`:** id from `format_registry.yaml` → `runtime_formats` (e.g. `standard_book`, `short_book_30`, `micro_book_15`).
- **`structural_format`:** optional `F00x` id; KnobApply does **not** select it—may be passthrough from catalog for BeatmapCompile.

### 4.2 `ShapedChapter`

For each input chapter, **copy immutable spine fields** unchanged: `number`, `role`, `working_title`, `thesis`, `emotional_job`, `practical_job`, `what_changes`, `required_sections`, `forbidden_moves`, `recommended_enrichments`, and optional narrative fields (`claim_someone_could_argue`, `why_this_chapter_exists`, `what_comes_next`).

**Add:**

```json
{
  "shaped_section_weights": {
    "HOOK": 1.0,
    "SCENE": 1.0,
    "STORY": 1.2,
    "REFLECTION": 0.9,
    "EXERCISE": 0.0,
    "INTEGRATION": 0.5,
    "COMPRESSION": 0.0,
    "PIVOT": 0.0,
    "TAKEAWAY": 0.0,
    "THREAD": 0.0,
    "PERMISSION": 0.0,
    "SOMATIC_INVENTORY": 0.0
  },
  "knob_state": {
    "story_density": "high",
    "exercise_density": "low",
    "mechanism_depth": "light",
    "reflection_depth": "medium",
    "pacing_profile": "measured",
    "emotional_temperature": "warm",
    "practical_vs_contemplative": "contemplative",
    "teacher_presence": "high",
    "spirituality_level": "secular",
    "compression": "none",
    "narrative_structure": "promise_engine"
  },
  "emotional_temperature": "warm",
  "pacing_profile": "measured",
  "target_word_count": 833,
  "phase": "early_book",
  "compression_allowed": false,
  "enrichment_priority": ["scene_ordinary_life_nervous_system", "persona_voice_dry_specific"]
}
```

**`shaped_section_weights` rules:**

- Every key is a **non-negative float**. Zero means “no slot of this type unless BeatmapCompile upgrades it for format-law reasons.”
- Weights are **relative within the chapter**, not absolute word counts.
- Any slot type listed in `required_sections` MUST have weight **> 0** after merge resolution (sequencing may force exercise weight 0 even if a profile defaults medium—see §5 example P1).
- Unknown slot types for a format remain 0 until BeatmapCompile maps format template.

**`enrichment_priority`:** stable snake_case tokens derived from `recommended_enrichments` + persona hints + topic defaults; used only for ordering atom pools in **EnrichmentSelect** (§8). They MUST NOT rewrite weights.

**`phase` assignment:** Map chapter `number` to `early_book` / `mid_book` / `late_book` using **topic profile boundaries**:

| Topic | early_book | mid_book | late_book |
|-------|------------|----------|-----------|
| anxiety | ch 1–4 | ch 5–8 | ch 9–12 |
| grief | ch 1–4 | ch 5–8 | ch 9–12 |
| burnout | ch 1–4 | ch 5–9 | ch 10–12 |

(These ranges mirror `phase_overrides` blocks in `topic_knob_profiles.yaml`.)

**`target_word_count`:** Let `[w_min, w_max]` be `runtime_formats[runtime_format].word_range` and `T = (w_min + w_max) / 2`. Let `n` be chapter count. Baseline `target_word_count = round(T / n)`. Optional spine- or profile-based **reallocation** MAY move ±15% between chapters if total remains within §10 tolerance.

**`compression_allowed`:** `true` only if `knob_state.compression` allows merging/skip **and** no spine `forbidden_moves` / sequencing rule bans compression for that chapter **and** `hard_ceilings.compression` is not violated.

### 4.3 `KnobAudit`

```json
{
  "knobs_applied": {
    "topic": "anxiety",
    "runtime_format": "standard_book",
    "persona_id": null,
    "platform_id": null
  },
  "sequencing_constraints_applied": [
    {
      "chapter": 2,
      "rule": "cannot_come_too_early:no_mechanism_depth_high",
      "source": "spine:anxiety chapter_02",
      "resolution": "mechanism_depth capped at light until chapter 6 mechanism_timing"
    }
  ],
  "floors_enforced": [
    { "chapter": 5, "knob": "emotional_temperature", "floor": "warm", "before": "clinical", "after": "warm" }
  ],
  "ceilings_enforced": [
    { "chapter": 3, "knob": "exercise_density", "ceiling": "low", "before": "high", "after": "low" }
  ],
  "dangerous_combos_checked": [
    {
      "chapter": 2,
      "pattern_id": "anxiety:exercise_density_high+emotional_temperature_clinical@ch1-4",
      "matched": false,
      "resolution": null
    }
  ],
  "platform_conflicts_resolved": [
    {
      "platform_id": "spotify",
      "issue": "preferred_structures include myth_killer conflicting with spine action_timing",
      "resolution": "spine_wins; narrative_structure locked to promise_engine",
      "notes": "Recorded for catalog; does not mutate SelectedSpine thesis/role/order"
    }
  ],
  "persona_adjustments_dropped": []
}
```

---

## 5. Merge order (authoritative)

**Conflict resolution priority (highest → lowest):** when two sources disagree, the higher priority wins.

1. **Spine sequencing_rules** + per-chapter `forbidden_moves` + `required_sections`
2. **Knob `hard_floors` / `hard_ceilings`**
3. **Knob `phase_overrides`** (for the chapter’s phase)
4. **Runtime / platform constraints** (`runtime_format`, `platform_knob_tuning.yaml`, `platform_overrides`)
5. **Persona preferences** (`persona_overrides`)

**Computation order (implementation hint, non-contradicting):** seed merged state from **`knob_defaults`**, apply **`phase_overrides`**, clamp to **`hard_floors` / `hard_ceilings`**, apply **spine-derived caps** (e.g. zero EXERCISE when `cannot_come_too_early` bans practice), merge **platform** within remaining envelope, merge **persona** last, then **re-clamp** floors/ceilings and spine caps, then run **dangerous_combination** repair (§9).

**Tie-break invariant:** If platform or persona equals or exceeds spine authority, **spine still wins** for sequencing and immutables; platform/persona may only add **audit entries** and soft adjustments inside spine+knob envelopes.

### 5.1 Priority 1 — Spine (examples)

**Conflict:** Persona + platform push **`exercise_density: high`** globally; anxiety spine `sequencing_rules.cannot_come_too_early` states **No practice of any kind before chapter_05**.

**Resolution:** For chapters 1–4, `shaped_section_weights.EXERCISE = 0` and `knob_state.exercise_density` resolves to **`none` or `low`** per profile (must satisfy “no practice” — treat as **no EXERCISE slot**). Persona/platform preferences are **dropped** with `knob_audit.persona_adjustments_dropped` / `platform_conflicts_resolved` entries.

**Conflict:** Resolver tries to name **false-alarm mechanism** in chapter 3; spine `mechanism_timing` says false-alarm logic arrives **chapter 6**.

**Resolution:** `mechanism_depth` capped so narrative cannot front-load mechanism teaching in ch3–5 (medium/high not allowed); `sequencing_constraints_applied` cites spine.

### 5.2 Priority 2 — Hard floors / ceilings

**Conflict:** Persona requests **`emotional_temperature: clinical`**; anxiety `hard_floors.emotional_temperature` is **`warm`**.

**Resolution:** Emit **`warm`**; log `floors_enforced`.

**Conflict:** **`exercise_density`** wants **`high`** in grief ch5; grief `hard_ceilings.exercise_density` is **`low`** and floor **`none`** through ch8.

**Resolution:** ch5–8 remain **`none`** or **`low`** per phase table; **never** `high` until `late_book` policy allows invitations (ch9+ still only **`low`** per profile exemplar).

### 5.3 Priority 3 — Phase overrides

**Conflict:** Baseline default `reflection_depth: medium` but `late_book` override sets **`high`** for ch10.

**Resolution:** Chapter 10 receives **`high`** subject to ceilings/floors.

### 5.4 Priority 4 — Platform

**Conflict:** Spotify profile (`platform_knob_tuning.yaml`) favors **`myth_killer`**; grief knob profile `dangerous_combinations` bans **`narrative_structure_myth_killer`** without spirituality pairing and spine forbids resolution framing.

**Resolution:** **`narrative_structure` stays `promise_engine`** for grief; `knob_audit.platform_conflicts_resolved` records spine+knob win. Runtime MAY still shorten episode delivery via **BeatmapCompile** (not by rewriting thesis).

**Conflict:** `micro_book_15` runtime implies aggressive compression; anxiety knob `platform_conflicts` text says **do not run anxiety spine in micro_book_15**.

**Resolution:** KnobApply still emits a `ShapedSpine` but MUST set `knob_audit.platform_conflicts_resolved` to **BLOCKING** recommendation for downstream gate (implementation detail: flag `blocking_platform_runtime: true` in audit extension) — **or** caller supplies an alternate runtime. Contract: **never** relax spine sequencing to satisfy micro-runtime.

### 5.5 Priority 5 — Persona

**Conflict:** Persona prefers **`pacing_profile: fast`**; grief `knob_defaults` and `phase_overrides` require **`slow` / measured** early witnessing.

**Resolution:** **`slow`** (or measured) wins for early_book chapters; persona suggestion logged under `persona_adjustments_dropped`.

---

## 6. What KnobApply must not do

Listed explicitly in §1.3; repeated for validators:

- No mutation of **thesis**, **role**, chapter order, or chapter count.
- No atom selection / registry resolution.
- No prose; no scoring.

KnobApply **shapes** densities and **relative** section prevalence.

---

## 7. How `BeatmapCompile` consumes `ShapedSpine`

- **`shaped_section_weights`:** Primary input to derive ordered **`slot_definitions[ch]`** per chapter ( HOOK/SCENE/STORY/… ), respecting `format_registry` `default_slot_definitions` / structural `slot_template` when a structural format is active.
- **`target_word_count`:** Total chapter budget; BeatmapCompile allocates per-slot word targets proportional to weights × format law.
- **`enrichment_priority`:** Marks preferred pools / tags for slot filling (not weights).
- **`emotional_temperature` / `pacing_profile`:** Passed through to **ChapterCompose** and prompts (matches `chapter_composer.py` bridge / temperature concerns conceptually).
- **`compression_allowed`:** If `false`, BeatmapCompile MUST NOT insert COMPRESSION slots even if a structural template could.
- **`knob_state.narrative_structure`:** Chooses bestseller `BESTSELLER_STRUCTURES` alignment in chapter planner context (see `chapter_planner.py`) **without** conflicting spine **role** labels.

---

## 8. How enrichment layers on top

After BeatmapCompile:

1. **Teacher atoms** overlay teacher-addressable slot types (per `registry_resolver.py`: `TEACHER_DOCTRINE`, HOOK, EXERCISE, INTEGRATION, PIVOT, PERMISSION, TAKEAWAY, THREAD — not SCENE in teacher mode).
2. **Persona atoms** overlay HOOK, SCENE, STORY in regular mode.
3. **Practice library fallback** when specific atoms missing (post-overlay).

Enrichment **fills slots**; it never overrides **`shaped_section_weights`** retroactively. If an atom would violate spine `forbidden_moves`, **QualityGate** / assembly guards reject (out of KnobApply scope).

---

## 9. Dangerous combination enforcement (mandatory)

For **each chapter**, after resolving `knob_state`:

1. Build **tag set** from resolved knobs, e.g. `exercise_density_high`, `emotional_temperature_clinical`, `compression_heavy`, `pacing_profile_fast`, `narrative_structure_myth_killer`, `spirituality_level_high`, etc. Mapping table is fixed per KnobApply version and MUST cover all symbols appearing in `topic_knob_profiles.yaml`.
2. For each `dangerous_combinations` row whose `chapter_range` matches the chapter index, test whether **all listed tags** are active.
3. If matched, append to `knob_audit.dangerous_combos_checked` with `"matched": true` and **resolve** by lowering the **more aggressive** knob toward its **`hard_floor`** (never violate spine P1).

**Worked example (anxiety ch2):**

- Candidate state: `exercise_density: high`, `emotional_temperature: clinical`.
- Rule: `[exercise_density_high, emotional_temperature_clinical]` on `ch1-4`.
- Resolution: reduce **`exercise_density`** to floor (`low`/`none` for early_book) **first**; if still conflicting, raise temperature to **`warm`** (floor). Final state must not match pattern.

**Worked example (grief ch3):**

- Candidate: `exercise_density: medium` triggers `exercise_density_medium + chapter_range_ch1-8` style rule.
- Resolution: force `none` / `low` per spine **no practice before ch09** — identical to spine P1 outcome; dangerous combo documents **why** double-validation matters.

---

## 10. Validation — `ShapedSpine` invalidity

`ShapedSpine` is **INVALID** if any of:

1. Any immutable spine field (thesis, role, titles) **differs** from `SelectedSpine` input (string equality after normalization).
2. Chapter order or count changed.
3. Any **`hard_floor`** violated (post-resolution).
4. Any **`hard_ceiling`** violated.
5. Any dangerous combination **matched** with no resolution recorded.
6. **Total words:** `sum(target_word_count)` outside **`[0.9·T, 1.1·T]`** where `T` is midpoint of `runtime_formats[runtime_format].word_range` for the declared chapter count (§4.2), unless `knob_audit` explicitly documents an approved alternate **`T`** from a platform override (still must be within YAML range).

---

## 11. Traceability matrix (repo sources)

| Concept | Where defined |
|---------|----------------|
| Spine narrative + sequencing | `config/spines/<family>_spine.yaml` |
| Topic knob policy | `config/knobs/topic_knob_profiles.yaml` |
| Runtime word budgets | `config/format_selection/format_registry.yaml` → `runtime_formats` |
| Allowed engines / roles | `config/topic_engine_bindings.yaml` (upstream of spine lock-in) |
| Platform duration / structures | `config/catalog_planning/platform_knob_tuning.yaml` |
| Archetype slot expectations | `config/source_of_truth/chapter_archetypes.yaml` (BeatmapCompile) |
| Slot policy archetypes | `config/source_of_truth/chapter_planner_policies.yaml` |

---

## 12. Python contract module

Dataclass signatures live in `config/pipeline/knob_apply_contract.py` (signatures only; `raise NotImplementedError`).

---

## 13. Note on repo layout

As of this writing, authoritative **`topic_knob_profiles.yaml`** and **`config/spines/*.yaml`** may land from the promotion branch that generated them; this contract names their **canonical paths** independent of temporary worktree locations.
