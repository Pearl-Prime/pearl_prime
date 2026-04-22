# Bestseller Atom Routing Pipeline

## Overview

Phoenix Omega's spine pipeline injects "bestseller structure" beats — PIVOT, PERMISSION,
TAKEAWAY, THREAD, and COMPRESSION — into every chapter according to a deterministically
assigned narrative structure. This document describes the full routing from structure
assignment through slot resolution to final prose output.

---

## 1. Structure Assignment (`bestseller_structure_map.py`)

`phoenix_v4/planning/bestseller_structure_map.py` defines twelve named structures, each
an ordered sequence of beat types. Example (promise_engine):

```
HOOK → SCENE → STORY → PIVOT → REFLECTION → EXERCISE → TAKEAWAY → INTEGRATION → PERMISSION → THREAD
```

`assign_bestseller_structures(chapter_count, selector_key_prefix)` in
`phoenix_v4/planning/chapter_planner.py` deterministically assigns one structure to each
chapter using `_deterministic_index(seed, n)`. The same seed always produces the same
chapter→structure mapping.

`validate_chapter_beat_order(beat_list)` enforces that required structure beats appear in
the prescribed order and raises `ValueError` on violations.

---

## 2. Slot Augmentation (`chapter_planner.py`)

`_augment_slots_for_bestseller_structure(base_row, structure_key)` is called from
`compile_plan` in `assembly_compiler.py` during plan compilation. It:

1. Looks up the structure's ordered beat steps from `BESTSELLER_BEAT_STEPS`
2. Inserts PIVOT / PERMISSION / TAKEAWAY / THREAD / COMPRESSION slots into the chapter's
   slot list at the positions specified by the structure
3. Preserves existing base slots (HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION)

The result is a fully augmented beat sequence for each chapter, ready for slot resolution.

---

## 3. Slot Resolution (`slot_resolver.py`)

`resolve_slot(slot_type, chapter_idx, slot_idx, context)` in
`phoenix_v4/planning/slot_resolver.py` handles any slot type, including the new
bestseller beats, via `pool_index.get_pool(slot_type, ...)`.

The constant `_TEACHER_FALLBACK_SLOTS` explicitly lists all slot types that support
teacher-atom fallback:

```python
_TEACHER_FALLBACK_SLOTS = frozenset({
    "HOOK", "SCENE", "INTEGRATION", "PIVOT", "PERMISSION",
    "TAKEAWAY", "THREAD", "EXERCISE", "STORY"
})
```

COMPRESSION falls through to the standard atom pool without teacher fallback.

---

## 4. HOOK Recognition Bank Routing (`injection_resolver.py`)

For HOOK slots, `_find_scene_content()` in
`phoenix_v4/planning/injection_resolver.py` routes to curated recognition-bank content
**before** the legacy template scaffold:

1. **Recognition bank** — `config/content_banks/anxiety_genz_scene_recognition_bank.yaml`
   (40 variants with `collision_family` tags). Selected via `BookSlotTracker.pick()`.
2. **Teacher STORY atoms** — `SOURCE_OF_TRUTH/teacher_banks/{tid}/approved_atoms/STORY/`
3. **Persona STORY / engine CANONICAL** — `atoms/{persona}/{topic}/STORY/CANONICAL.txt`
4. **Registry variant** — `registry/{topic}.yaml` chapter/section row

This routing is active in the **pilot path** only
(`scripts/pilot/run_legacy_template_packet_pilot.py` →
`phoenix_v4/rendering/section_packet_composer.py` →
`phoenix_v4/planning/injection_resolver.py`).

The main spine path (`scripts/run_pipeline.py` → `chapter_composer.compose_from_enriched_book`)
does not yet call `section_packet_composer`. When it does, `BookSlotTracker` will
automatically apply via the `slot_tracker=` parameter already threaded through.

---

## 5. BookSlotTracker (`injection_resolver.py`)

`BookSlotTracker` enforces variety across all HOOK recognition-bank picks for a full book:

- **Hard-exclude**: once a `variant_id` is used it is never reused in the same book
- **Collision-family spread**: picks from the least-used `collision_family` first
- **Graceful fallback**: if all variants are exhausted, returns `None` and the
  caller falls back to the next resolution tier

`BookSlotTracker` is instantiated once per book in both the pilot script and
`run_pipeline.py`. The `run_pipeline.py` instance is currently a no-op placeholder
(accepted by `compose_from_enriched_book` but not yet consumed by the spine renderer).

---

## 6. Mechanism Token Resolution (`injection_resolver.py`)

`_fill_mechanism_tokens(text, topic, persona_id, seed, repo_root)` resolves
`{selected_mechanism}` and `{selected_signal}` placeholders in REFLECTION atoms by
loading `config/content_banks/selected_mechanism_resolver.yaml`.

`_fill_locale_tokens(text, spine_context)` resolves locale-flavoured tokens such as
`{weather_detail}` (lowercase) and `{Weather_detail}` (title-case).

**Known gap**: REFLECTION atoms for 10 persona×topic combos (tech_finance_burnout ×
millennial_women_professionals across 6 topic verticals) still contain unresolved
`{selected_mechanism}` / `{selected_signal}`. These render as empty strings in the
pilot path until the relevant `selected_mechanism_resolver.yaml` entries are authored.

---

## 7. Bestseller Craft Gate (`bestseller_craft_gate.py`)

`phoenix_v4/quality/bestseller_craft_gate.py` post-validates rendered chapters:

- Checks that PIVOT, PERMISSION, TAKEAWAY, THREAD beats are present in the final prose
- Validates beat order matches the assigned structure
- Flags chapters where structure injection succeeded but prose output dropped a beat

The gate runs in `run_pipeline.py` after `compose_from_enriched_book` when
`quality_profile != "draft"`.

---

## 8. Recognition Bank Coverage

| Persona × Topic | Bank File | Variants |
|---|---|---|
| gen_z_professionals × anxiety | `config/content_banks/anxiety_genz_scene_recognition_bank.yaml` | 40 |
| All other combos (P1–P5) | *(fallback: generic HOOK atom pool)* | — |

See `docs/RECOGNITION_BANK_SPEC.md` for the full priority matrix and authoring spec for
the 14 remaining P1–P5 banks.

---

## Files

| File | Role |
|---|---|
| `phoenix_v4/planning/bestseller_structure_map.py` | 12 named structures + beat validation |
| `phoenix_v4/planning/chapter_planner.py` | Structure assignment + slot augmentation |
| `phoenix_v4/planning/slot_resolver.py` | Slot resolution for all beat types |
| `phoenix_v4/planning/injection_resolver.py` | BookSlotTracker + HOOK routing + token fill |
| `phoenix_v4/rendering/section_packet_composer.py` | Layer stacking (pilot path) |
| `phoenix_v4/rendering/chapter_composer.py` | Spine render (main path) |
| `phoenix_v4/quality/bestseller_craft_gate.py` | Post-render beat validation |
| `config/content_banks/anxiety_genz_scene_recognition_bank.yaml` | 40-variant HOOK bank |
| `config/content_banks/selected_mechanism_resolver.yaml` | Mechanism token resolver |
| `docs/RECOGNITION_BANK_SPEC.md` | Recognition bank authoring spec |
| `scripts/pilot/run_legacy_template_packet_pilot.py` | Pilot orchestrator (uses full stack) |
| `scripts/run_pipeline.py` | Main pipeline (BookSlotTracker wired, not yet consumed) |
