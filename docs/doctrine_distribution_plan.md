# Doctrine Distribution Plan

**Authority:** REFLECTION-slot teaching arc for 12-chapter composite (no-teacher) books.  
**Wiring site:** `phoenix_v4/planning/doctrine_rotation.py` → `enrichment_select._try_composite_content` (REFLECTION step).  
**Config SSOT:** `config/source_of_truth/doctrine_rotation.yaml`

## What doctrine is

The teaching beat of a chapter — a psychological/somatic principle in the REFLECTION slot.  
Bank: `SOURCE_OF_TRUTH/composite_doctrine/<topic>/REFLECTION/CANONICAL.txt` (variants `COMPOSITE_DOCTRINE v01`–`v15`).  
Distinct from story (STORY/SCENE) and exercise (EXERCISE).

## Rules

1. **One doctrine per chapter** — each chapter with a composite REFLECTION slot gets exactly one assigned variant.
2. **No repeats across a book** — a variant used in chapter N cannot appear in chapter M≠N (fail closed).
3. **Deliberate order** — foundational → integrative arc, not hash-random selection.
4. **Brand-tuned dosage** — somatic brands receive composite doctrine on all assigned chapters; commercial brands on a lighter subset (see `doctrine_rotation.yaml` → `brand_dosage_profiles`).

## Resolution precedence

1. `chapter_continuity_plan` entry `doctrine_id` (12-shape plans under `config/source_of_truth/twelve_shape_chapter_plans/`)
2. Topic default sequence in `doctrine_rotation.yaml` → `topic_sequences`
3. No assignment → legacy dedup-aware hash pick (non-rotation path only)

## Default 12-chapter sequence (anxiety)

Foundational → integrative. Drives `topic_sequences.anxiety.default_12` when no persona-specific plan exists.

| Ch | Variant | Teaching target |
|----|---------|-----------------|
| 1 | v03 | sensation vs story |
| 2 | v01 | weather vs climate |
| 3 | v05 | carrying / set down |
| 4 | v04 | breath already moving |
| 5 | v02 | what you've been carrying |
| 6 | v06 | alarm before argument |
| 7 | v07 | body as ally |
| 8 | v08 | practice without performance |
| 9 | v09 | return after disruption |
| 10 | v10 | regulation as skill |
| 11 | v11 | workplace panic response |
| 12 | v15 | integrated Tuesday |

## gen_z_professionals × anxiety (12-shape)

Persona-specific plan: `config/source_of_truth/twelve_shape_chapter_plans/gen_z_professionals_anxiety.yaml`  
Matches the default anxiety sequence above (ch1=v03 sensation-vs-story … ch12=v15).

## Brand dosage

| Profile | `book_frame` keys | Composite REFLECTION chapters |
|---------|-------------------|-------------------------------|
| `somatic_heavy` | `somatic_first`, `somatic` | 1–12 (all) |
| `commercial_light` | `commercial`, `mainstream` | 1, 4, 7, 10, 12 |

When dosage skips a chapter, rotation does not assign composite doctrine; the picker defers to persona/registry pools.
