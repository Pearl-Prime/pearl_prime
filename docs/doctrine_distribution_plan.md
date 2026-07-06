# Doctrine Distribution Plan

**Authority:** REFLECTION-slot teaching arc for 12-chapter composite (no-teacher) books.  
**Wiring site:** `phoenix_v4/planning/doctrine_rotation.py` → `enrichment_select._try_composite_content` (REFLECTION step).  
**Config SSOT:** `config/source_of_truth/doctrine_rotation.yaml`

## What doctrine is

The teaching beat of a chapter — a psychological/somatic principle in the REFLECTION slot.  
Bank: `SOURCE_OF_TRUTH/composite_doctrine/<topic>/REFLECTION/CANONICAL.txt` (variant ids
`COMPOSITE_DOCTRINE vNN`). **A sequence may only assign variants that actually exist in
the topic's bank** — anxiety currently holds 5 authored variants (`v01`–`v05`).  
Distinct from story (STORY/SCENE) and exercise (EXERCISE).

## Rules

1. **One doctrine per chapter** — each chapter with a composite REFLECTION slot gets exactly one assigned variant, shared across every REFLECTION slot in that chapter.
2. **Bounded reuse, not strict no-repeat** — a variant MAY repeat across chapters, but not within a spacing window of `min(pool_size, chapter_count)` chapters, and never in two adjacent chapters. When the lesson library is smaller than the chapter count (e.g. 5 anxiety variants over 12 chapters) the library is cycled with maximal spacing; when it grows past the chapter count the window widens back toward strict no-repeat with no code change. Enforced by `pick_doctrine_atom_by_id` (`phoenix_v4/planning/doctrine_rotation.py`).
3. **Fail-safe, never drop or crash** — if an assigned variant is missing from the pool or would repeat within the spacing window, the picker degrades to the least-recently-used variant. It never leaves a chapter's REFLECTION slot empty (the old silent drop for `v06`–`v15`) and never raises.
4. **Deliberate order** — foundational → integrative arc, not hash-random selection.
5. **Brand-tuned dosage** — somatic brands receive composite doctrine on all assigned chapters; commercial brands on a lighter subset (see `doctrine_rotation.yaml` → `brand_dosage_profiles`).

## Resolution precedence

1. `chapter_continuity_plan` entry `doctrine_id` (12-shape plans under `config/source_of_truth/twelve_shape_chapter_plans/`)
2. Topic default sequence in `doctrine_rotation.yaml` → `topic_sequences`
3. No assignment → legacy dedup-aware hash pick (non-rotation path only)

## Default 12-chapter sequence (anxiety) — bounded reuse over 5 variants

Foundational → integrative, cycled. Drives `topic_sequences.anxiety.default_12` when no
persona-specific plan exists. The curated 5-variant order (`v03,v01,v05,v04,v02`) repeats
every 5 chapters, so each lesson recurs exactly `min(5,12)=5` chapters apart and never in
adjacent chapters.

| Ch | Variant | Teaching target |
|----|---------|-----------------|
| 1 | v03 | sensation vs story |
| 2 | v01 | weather vs climate |
| 3 | v05 | carrying / set down |
| 4 | v04 | breath already moving |
| 5 | v02 | what you've been carrying |
| 6 | v03 | sensation vs story (reprise) |
| 7 | v01 | weather vs climate (reprise) |
| 8 | v05 | carrying / set down (reprise) |
| 9 | v04 | breath already moving (reprise) |
| 10 | v02 | what you've been carrying (reprise) |
| 11 | v03 | sensation vs story (reprise) |
| 12 | v01 | weather vs climate (reprise) |

> Prior versions listed `v06`–`v15`, which do **not** exist in the anxiety bank, so
> chapters 6–12 were silently dropped. Grow the authored library to widen the spacing
> back toward strict no-repeat — no code change needed.

## gen_z_professionals × anxiety (12-shape)

Persona-specific plan: `config/source_of_truth/twelve_shape_chapter_plans/gen_z_professionals_anxiety.yaml`  
This plan still lists `v06`–`v15` for chapters 6–12; because those variants are not in the
bank, the fail-safe (rule 3) degrades each to a least-recently-used authored variant rather
than dropping the slot. Retuning this plan to an authored spaced cycle (and its
`expected_doctrine_snippet` hints) is a separate follow-up — it requires no code change.

## Brand dosage

| Profile | `book_frame` keys | Composite REFLECTION chapters |
|---------|-------------------|-------------------------------|
| `somatic_heavy` | `somatic_first`, `somatic` | 1–12 (all) |
| `commercial_light` | `commercial`, `mainstream` | 1, 4, 7, 10, 12 |

When dosage skips a chapter, rotation does not assign composite doctrine; the picker defers to persona/registry pools.
