# Spine Ch2 Packet Repair Audit

**Repro:** `burnout` / `corporate_managers` / `standard_book` / seed `4242` / chapter `2`
**Git SHA:** `8939c676db272fb7e9420f7f7488f6fcd6598f5c`

## Transform classification

- `build_virtual_slot_streams`: **REORDER→ADD** — REORDER→ADD (1:1 beatmap order, no collapse)
- `compose_chapter_prose`: **ADD** — ADD (additive path when repeated STORY/REFLECTION/TEACHER_DOCTRINE)
- `slot_map_first_of_type`: **DROP** — DROP removed on additive path
- `_dedupe_paragraphs`: **DEDUPE** — DEDUPE bypassed for authored repeatable slots
- `_first_or_join`: **DEDUPE** — DEDUPE bypassed; collapsed path moved to build_virtual_slot_streams_collapsed
- `_shape_integration`: **TRUNCATE** — TRUNCATE skipped on additive path (INTEGRATION verbatim)
- `clean_for_delivery`: **DEDUPE** — DEDUPE book-wide paragraph dedupe (unchanged; post-render)
- `register_output_strengthen`: **ADD/DROP** — ADD/DROP inject lines only post-render (unchanged)

## Duplicate guard (burnout ch2)

Baseline slots 3 and 7 both carried `COMPOSITE_DOCTRINE v02` (violation).
After patch: `[]`

## Slot-by-slot word deltas

| idx | type | source_id | authored | after_compose | after_render |
|---:|---|---|---:|---:|---:|
| 1 | HOOK | HOOK v32 | 90 | 90 | 90 |
| 2 | STORY | TURNING_POINT v06 | 150 | 150 | 150 |
| 3 | REFLECTION | COMPOSITE_DOCTRINE v02 | 268 | 268 | 268 |
| 4 | EXERCISE | EXERCISE v09 | 31 | 31 | 31 |
| 5 | STORY | STORY v04 | 51 | 51 | 51 |
| 6 | TEACHER_DOCTRINE | COMPOSITE_DOCTRINE v08 | 352 | 352 | 352 |
| 7 | REFLECTION | COMPOSITE_DOCTRINE v01 | 259 | 259 | 259 |
| 8 | EXERCISE | EXERCISE v01 | 30 | 30 | 0 |
| 9 | STORY | STORY v15 | 48 | 48 | 48 |
| 10 | INTEGRATION | INTEGRATION v12 | 117 | 117 | 117 |

## Before/after word counts

- Baseline render (artifact): 1114 words
- Patched compose path: 1428 words
- Patched full render: 1403 words
