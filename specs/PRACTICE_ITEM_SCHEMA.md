# Practice Item Schema (Canonical Data Model)

**Purpose:** Normalized schema for practice items from library_34 JSONs, ab_tady_37, or manual entries. Used by the practice library store and EXERCISE backstop.

**Authority:** Adapter layer spec; `config/practice/validation.yaml` enforces.

**Schema version history:**

| Version | Date | Authority | Changes |
|---|---|---|---|
| 1 | (initial) | original | `blocks: {setup, instruction, prompt, close}` 4-nullable-slot envelope (all-null permitted; in practice all rows ingested as all-null) |
| **2** | **2026-06-10** | cap entry `EXERCISE-COMPONENT-SCHEMA-LIFT-01` | Adds **parallel `components` field** preserving the 5-component × {full, lean} authoring shape from `exercises_ab_tady_37_PRODUCTION_READY.json` + `*_library_34_PRODUCTION_READY.json`. Existing `blocks` field retained for back-compat. Renderer prefers `components` when present. |

---

## 1. Canonical field order (for deterministic hashing)

Fields must appear in this order in JSON/JSONL:

**Schema v1 (legacy; still valid):**

1. `practice_id`
2. `source`
3. `content_type`
4. `duration_seconds`
5. `intensity_band`
6. `text`
7. `blocks`
8. `allowed_personas`
9. `allowed_topics`
10. `angle_affinity`
11. `tags`
12. `version`

**Schema v2 (current; preferred):**

1. `practice_id`
2. `source`
3. `content_type`
4. `duration_seconds`
5. `intensity_band`
6. `text`
7. `blocks`
8. `components` *(new; nullable for legacy items; required-non-null for ab_tady_37 + library_34 PRODUCTION_READY sources)*
9. `allowed_personas`
10. `allowed_topics`
11. `angle_affinity`
12. `tags`
13. `version`

---

## 2. Field definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| **practice_id** | string | ✅ | Stable unique id. Format: `<source_prefix>_<content_type>_<zero_padded_index>` (e.g. `lib34_sensory_grounding_01`, `ab37_breath_regulation_01`). lowercase, snake_case, ≤80 chars. |
| **source** | enum | ✅ | `library_34` \| `ab_tady_37` \| `manual` |
| **content_type** | enum | ✅ | One of: affirmations, body_awareness, gratitude_practices, integration_bridges, meditations, reflections, self_inquiry, sensory_grounding, thought_experiments; or slot_07 types (breath_regulation, grounding_orientation, body_awareness_scan, somatic_release_discharge, nervous_system_downregulation, nervous_system_upregulation, vagal_stimulation_sound, self_contact_touch, emotional_processing_completion, embodied_intention_direction, integration_return_to_baseline). |
| **duration_seconds** | int | ✅ | 30–1200 |
| **intensity_band** | int | ✅ | 1–5; default 3. 1=gentle, 2=mild, 3=neutral, 4=deep, 5=intense. |
| **text** | string | ✅ | Original prose (single blob; equivalent to `components.description.full` when components present). Whitespace-normalized only. Must pass safety lint. |
| **blocks** | object | ✅ | Legacy v1 segmentation: `setup`, `instruction`, `prompt`, `close` (strings or null). May be all null. Retained for back-compat; renderer prefers `components` when present. |
| **components** | object \| null | ✅ (v2) | **NEW in v2.** 5-slot × 2-variant structured shape. See §2.5. Null permitted only for v1 legacy items (`source=manual` + version=1); required-non-null for `source ∈ {library_34, ab_tady_37}` at v2. |
| **allowed_personas** | list[str] | ✅ | Empty = all. Otherwise only these personas may use. |
| **allowed_topics** | list[str] | ✅ | Empty = all. Otherwise only these topics. |
| **angle_affinity** | list[str] | ✅ | Optional angle ids for preference. Empty allowed. |
| **tags** | list[str] | ✅ | Free tags; max 50. |
| **version** | int | ✅ | Schema version. v1 items have version=1; v2 items have version=2. |

---

## 2.5 Components (v2)

The `components` field preserves the rich 5-component × {full, lean} authoring shape that ships in `exercises_ab_tady_37_PRODUCTION_READY.json` + `*_library_34_PRODUCTION_READY.json` inbox files.

### Shape

```json
{
  "components": {
    "bridge":       { "full": "<string>", "lean": "<string>" },
    "intro":        { "full": "<string>", "lean": "<string>" },
    "description":  { "full": "<string>", "lean": "<string>" },
    "aha":          { "full": "<string>", "lean": "<string>" },
    "integration":  { "full": "<string>", "lean": "<string>" }
  }
}
```

### Component roles

| Slot | Role | Reader-facing function | Word target (full) | Word target (lean) |
|---|---|---|---|---|
| **bridge** | Book-flow wrapper that announces the upcoming exercise | "Before you keep reading, try something with your breath..." | 30-50 | 8-15 |
| **intro** | Names the practice + frames why it works | "This is cyclic sighing. The double inhale..." | 40-70 | 8-15 |
| **description** | The instruction prose itself (imperatives only per `PHOENIX_V4_5_WRITER_SPEC.md` §4.5) | "Breathe in through your nose. At the top..." | 60-120 | 20-40 |
| **aha** | The moment-of-recognition payload — what just shifted | "Now, notice that your inhale may feel slightly fuller..." | 50-90 | 15-30 |
| **integration** | Carry-back into the chapter; what to take forward | "Before you move on, take one moment to notice..." | 30-60 | 10-25 |

### Variant rules

- **`full`** — used for runtime formats with `duration_minutes ≥ 120` (extended_book_2h, deep_book_4h, deep_book_6h) per `config/practice/selection_rules.yaml` `component_variant_by_format`. Bandwidth for the rich teaching shape.
- **`lean`** — used for compact formats (micro_book_15, micro_book_20, short_book_30, standard_book, compact_*). Word budget too tight for full components.
- Both variants required at authoring time. Selection happens at render time per format.

### Component validation rules

Per `config/practice/validation.yaml` `components_schema`:

- All 5 slots required (`bridge`, `intro`, `description`, `aha`, `integration`) when `components` is non-null.
- Each slot must have both `full` and `lean` non-empty strings.
- Per-slot word caps enforced via `tts_rhythm` lint (max avg sentence words = 18 per existing rule; applies to each component string independently).
- Banned phrases per existing `banned_phrases` list apply to every component string (not just `text`).

### Back-compat

- **v1 → v2 lift:** When the ingest re-processes inbox files (per `ws_pearl_dev_practice_ingest_components_lift_20260610`), each item gets its `components` populated from the inbox's `components` field and its `version` bumped to 2. The legacy `text` and `blocks` fields are preserved unchanged.
- **Reading v2 items in v1 code:** `text` always carries `components.description.full` so v1-only consumers continue to function.
- **Writing new v2 items:** `manual` source MAY omit `components` (sets to null + version=1). All `library_34` + `ab_tady_37` sources MUST include `components` (version=2).

---

## 3. Store layout

- **Store:** `SOURCE_OF_TRUTH/practice_library/store/practice_items.jsonl` (one PracticeItem per line).
- **Index:** `SOURCE_OF_TRUTH/practice_library/index/by_content_type/<content_type>.json` (list of practice_id).
- **Inbox:** `SOURCE_OF_TRUTH/practice_library/inbox/` — raw `*_library_34.json` (PRODUCTION_READY + non-suffixed pair per content_type) + `exercises_ab_tady_37_PRODUCTION_READY.json` + `gratitude_practices_v1_BASELINE.json` (BASELINE only; not for production per `EXERCISE-BANK-RESOLUTION-01`).

---

## 4. Integration

- **EXERCISE backstop:** When `atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt` is missing or empty AND `--quality-profile` is not `production` (per `EXERCISE-BANK-RESOLUTION-01` Option 1), pool can be filled from practice store (`selection_rules.EXERCISE_BACKSTOP`). Under `production`, fall-through raises `EnrichmentGapError` instead.
- **Teacher fallback:** When a teacher has insufficient EXERCISE atoms, they may pull from practice store with a **teacher wrapper** (doctrine-aligned intro/frame); see `docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md`. **In v2:** if the pulled practice item has `components` populated, the renderer prefers `components.intro` over the teacher-config `exercise_wrapper.intro_templates` — the practice item's own structured intro is closer to the reader experience the author intended. Teacher-config wrappers remain as fallback when `components` is null (v1 items).
- **Rendering:** Prose resolver resolves `atom_id` when it matches a practice_id (e.g. `lib34_*`, `ab37_*`) by loading from practice store. Renderer reads `components.{bridge, intro, description, aha, integration}.<variant>` where `<variant>` is picked from format registry per `selection_rules.component_variant_by_format`.

---

## 5. Schema versioning

- **`version` field is the binding declaration.** Consumers must accept v1 items (legacy) AND v2 items.
- **v1 items** are detectable by `version: 1` AND (typically) `components: null`. Renderer falls back to `text` blob + teacher-config wrappers.
- **v2 items** are detectable by `version: 2` AND `components: { ... }` populated. Renderer uses structured shape.
- **No v3 path scheduled.** If a future amendment shrinks/expands the component set, bump to v3 + cap entry.
- **Migration:** `ws_pearl_dev_practice_ingest_components_lift_20260610` lifts the 272-row store from v1 → v2 in a single PR (re-ingest from inbox + bump version) + `ws_pearl_dev_renderer_practice_components_consume_20260610` upgrades the renderer to prefer components when present.

---

## 6. Cross-references

- Cap entry: `EXERCISE-COMPONENT-SCHEMA-LIFT-01` (`docs/PEARL_ARCHITECT_STATE.md`)
- Cap entry: `EXERCISE-BANK-RESOLUTION-01` (production-profile strict-canonical; orthogonal)
- Cap entry: `ATOM-100PCT-COVERAGE-SSOT-V1-01` (atom coverage SSOT; EXERCISE backing flows into Tier P0)
- Spec: `specs/PHOENIX_V4_5_WRITER_SPEC.md` §4.5 (three-source EXERCISE resolution)
- Doc: `docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md` (teacher wrapper interaction; updated in lock-step with this schema)
- Config: `config/practice/validation.yaml` (schema enforcement)
- Config: `config/practice/selection_rules.yaml` (per-format variant policy)
- Inbox precedent: `SOURCE_OF_TRUTH/practice_library/inbox/exercises_ab_tady_37_PRODUCTION_READY.json` (gold reference for component shape; 39 items)
- Inbox precedent: `SOURCE_OF_TRUTH/practice_library/inbox/affirmations_library_34_PRODUCTION_READY.json` + 7 sibling banks (272 items at the same component shape)
