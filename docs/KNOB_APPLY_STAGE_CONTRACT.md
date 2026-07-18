# Knob Apply Stage Contract

**Authority:** Describes the live implementation in `phoenix_v4/planning/knob_apply.py` (runtime) plus pipeline handoff to BeatmapCompile.  
**Subsystem:** `core_pipeline`  
**Project:** `proj_state_convergence_20260328`  
**Related config:** `config/knobs/topic_knob_profiles.yaml`, `config/spines/*_spine.yaml`, `config/format_selection/format_registry.yaml`, `config/topic_engine_bindings.yaml`, `config/catalog_planning/platform_knob_tuning.yaml`  
**Implementation:** `phoenix_v4/planning/knob_apply.py`  
**Design stub (non-runtime):** `config/pipeline/knob_apply_contract.py` — illustrative only; **do not treat as the live schema.**

This document must stay aligned with `knob_apply.py` (and its tests). If the stub module disagrees, **code + tests win**.

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
| `topic_engine_bindings.yaml` | No in KnobApply | Consumed by **BeatmapCompile** for default engine hints in atom criteria (SpineSelect still owns hard engine policy on the spine) |
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

## 2. Input schema — `SelectedSpine` (as loaded today)

`load_spine(topic)` reads `config/spines/<topic>_spine.yaml` (or test fixtures) into dataclass **`SelectedSpine`**:

| Field | Type | Notes |
|-------|------|--------|
| `schema_version` | `int` | Always `1` from loader |
| `topic` | `str` | Argument to loader |
| `family_id` | `str` | From YAML `family_id` or topic fallback |
| `primary_mechanism` | `str` | |
| `allowed_engines` | `List[str]` | |
| `reader_starting_state` | `str` | |
| `reader_ending_state` | `str` | |
| `chapters` | `List[SpineChapter]` | Sorted by `number` |
| `sequencing_rules` | `Dict[str, Any]` | Raw YAML block |
| `tone_and_pacing` | `Dict[str, Any]` | Raw YAML block |

**`SpineChapter`:** `number`, `role`, `working_title`, `thesis`, `emotional_job`, `practical_job`, `what_changes` (string), `required_sections`, `forbidden_moves`, `recommended_enrichments`.

The loader **does not** copy optional narrative-only YAML keys (e.g. `family_name`, `adjacent_topics`, per-chapter `claim_someone_could_argue`) onto `SelectedSpine` / `SpineChapter`. Downstream stages that need them must read YAML or extend the loader.

---

## 3. Input schema — `KnobProfile` (as loaded today)

`load_knob_profile(topic)` reads `topics.<topic>` from `config/knobs/topic_knob_profiles.yaml` (or fixtures):

| Field | Type |
|-------|------|
| `topic` | `str` |
| `source` | `str` | Relative path for audit |
| `knob_defaults` | `Dict[str, str]` |
| `hard_floors` | `Dict[str, str]` |
| `hard_ceilings` | `Dict[str, str]` |
| `phase_overrides` | `Dict[str, Dict[str, str]]` with keys `early_book`, `mid_book`, `late_book` |
| `dangerous_combinations` | `List[Dict[str, Any]]` |
| `persona_overrides` | `Optional[Dict[str, str]]` |
| `platform_overrides` | `Optional[Dict[str, str]]` |

---

## 4. Output schema — `ShapedSpine` / `ShapedChapter` / `KnobAudit` (as implemented)

### 4.1 `ShapedSpine`

| Field | Type |
|-------|------|
| `schema_version` | `int` |
| `stage` | `str` | `"knob_apply"` |
| `topic` | `str` |
| `family_id` | `str` |
| `runtime_format` | `str` |
| `chapters` | `List[ShapedChapter]` |
| `knob_audit` | `KnobAudit` |

No `structural_format` or `selected_spine_sha256` on this dataclass in code.

### 4.2 `ShapedChapter`

Immutable narrative fields carried from the spine (by value): **number, role, working_title, thesis, emotional_job, practical_job.**

| Field | Type | Notes |
|-------|------|--------|
| `shaped_section_weights` | `Dict[str, float]` | Relative weights; keys include HOOK, SCENE, STORY, … |
| `emotional_temperature` | `str` | From resolved `emotional_temperature` knob |
| `pacing` | `str` | From resolved `pacing_profile` knob (field name is `pacing`, not `pacing_profile`) |
| `target_word_count` | `int` | `round((word_range mid) / chapter_count)` |
| `phase` | `str` | Display label **`early`**, **`mid`**, or **`late`** (via `_yaml_phase_and_display`; not `early_book`) |
| `compression_allowed` | `bool` | `compression` knob not `none`/empty |
| `enrichment_priority` | `List[str]` | Slugs from `recommended_enrichments` lines (`_enrichment_slug`) |
| `knob_snapshot` | `Dict[str, str]` | Full merged knob state for the chapter |

`required_sections` / `forbidden_moves` are **not** duplicated on `ShapedChapter`; BeatmapCompile reloads the spine for those lists.

### 4.3 `KnobAudit`

| Field | Type |
|-------|------|
| `knobs_applied` | `Dict[str, str]` | Includes stringified `total_word_target`, optional persona/platform ids |
| `floors_enforced` | `List[Dict[str, Any]]` |
| `ceilings_enforced` | `List[Dict[str, Any]]` |
| `dangerous_combos_checked` | `List[Dict[str, Any]]` |
| `dangerous_combos_resolved` | `List[Dict[str, Any]]` |
| `platform_conflicts_resolved` | `List[Dict[str, Any]]` | Narrative-structure warning from `platform_knob_tuning` scan |

There are **no** `sequencing_constraints_applied` or `persona_adjustments_dropped` lists on this dataclass; spine sequencing is enforced inline (e.g. `_spine_blocks_exercise`, early anxiety mechanism cap) with entries in `dangerous_combos_resolved` where applicable.

---

## 5. Merge / repair order in `apply_knobs()` (code path)

Per-chapter merged knob state starts as **`knob_defaults`**, then **`phase_overrides[yaml_phase]`** (with `yaml_phase` = `early_book` / `mid_book` / `late_book` from `_yaml_phase_and_display`), then **`persona_overrides`**, then **`platform_overrides`**.

Then, in order:

1. **Spine exercise sequencing** — `_spine_blocks_exercise` may force `exercise_density` to `none` (topics with early practice bans).
2. **Anxiety early mechanism cap** — chapters 1–2 cap `mechanism_depth` at `light`.
3. **`hard_floors` / `hard_ceilings`** — `_clamp_knob` on each declared knob.
4. **Spine exercise sequencing** (again after clamps).
5. **`dangerous_combinations`** — tag match via `_knob_tags`; repair loop uses `_reduce_aggressive_for_resolution`, which steps knobs down in this **fixed order**:  
   `exercise_density`, `emotional_temperature`, `mechanism_depth`, `reflection_depth`, `compression`, `pacing_profile`, `spirituality_level`, `practical_vs_contemplative`,  
   then a special case that lifts `emotional_temperature` off `clinical` using the temperature floor.
6. **Section weights** — `_build_section_weights`; if `exercise_density == none`, `EXERCISE` weight forced to `0.0`.
7. **Platform / narrative audit** — `_platform_narrative_conflict` appends advisory rows (does not rewrite knobs today).

Conceptual priority remains: **spine sequencing wins over profile defaults**; floors/ceilings win over persona/platform suggestions inside the merged state.

---

## 6. What KnobApply must not do

Listed explicitly in §1.3; repeated for validators:

- No mutation of **thesis**, **role**, chapter order, or chapter count.
- No atom selection / registry resolution.
- No prose; no scoring.

KnobApply **shapes** densities and **relative** section prevalence.

---

## 7. How `BeatmapCompile` consumes `ShapedSpine`

Implemented in **`phoenix_v4/planning/beatmap_compile.py`** (tests: `tests/test_beatmap_compile.py`).

- **`shaped_section_weights`:** Include slot types with weight **> 0**; enforce spine `forbidden_moves` (practice/exercise ban patterns); if a required section has weight `0`, warn and bump to **`0.3`** (recovery path).
- **Canonical slot order:** From `load_format_spec()` → first compatible structural format’s `slot_template` in `format_registry.yaml` (e.g. **F006** for `standard_book`), else `default_slot_definitions`.
- **`target_word_count`:** Per-chapter budget; proportional allocation with minima (**HOOK ≥ 100**, **EXERCISE ≥ 80**, **INTEGRATION ≥ 60**, others **≥ 50**).
- **`enrichment_priority`:** Maps slugs to semantic **`enrichment_hooks`** on each `BeatmapSlot` (persona / teacher_voice / story_vividness / somatic_exercise defaults).
- **`emotional_temperature` / `pacing`:** Copied onto criteria and slots from `ShapedChapter` (the shaped field is `pacing`, sourced from knob `pacing_profile`).
- **`compression_allowed`:** If `false`, **COMPRESSION** is omitted even if weights were non-zero.

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

`config/pipeline/knob_apply_contract.py` is a **non-authoritative design stub** (`apply_knobs` raises `NotImplementedError`).  
Runtime types and behavior: **`phoenix_v4/planning/knob_apply.py`**.

---

## 13. Note on repo layout

As of this writing, authoritative **`topic_knob_profiles.yaml`** and **`config/spines/*.yaml`** may land from the promotion branch that generated them; this contract names their **canonical paths** independent of temporary worktree locations.
