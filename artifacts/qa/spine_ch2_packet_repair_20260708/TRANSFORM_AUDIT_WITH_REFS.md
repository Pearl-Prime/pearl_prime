# Spine Ch2 Transform Audit (file:line refs)

**Repro:** burnout / corporate_managers / standard_book / seed 4242 / chapter 2  
**Git SHA:** `8939c676db272fb7e9420f7f7488f6fcd6598f5c` (uncommitted patch on working tree)

## Transform classification

| Stage | Class | Before (broken) | After (patched) | File:line |
|---|---|---|---|---|
| `build_virtual_slot_streams` | **REORDER + DROP** | Type-bucketed slots into fixed canonical order (`HOOK→REFLECTION→STORY→COMPRESSION→TEACHER_DOCTRINE…`); repeated STORY/REFLECTION/TEACHER_DOCTRINE collapsed via `_first_or_join` → `_dedupe_paragraphs` | **ADD**: 1:1 beatmap order; one prose entry per slot; no collapse | `golden_chapter_synthesis.py:852-910` |
| `_first_or_join` / `_dedupe_paragraphs` | **DEDUPE** | Prefix/suffix paragraph dedupe dropped repeated authored packets | Bypassed on spine path; legacy retained in `build_virtual_slot_streams_collapsed` | `golden_chapter_synthesis.py:611-667`, `761-800`, `913+` |
| TEACHER_DOCTRINE routing | **REPLACE/DROP** | Doctrine silently folded into COMPRESSION (`compression = join(compression, doctrine)`) then dropped from compose slot_map | Doctrine emitted as own slot; no COMPRESSION fold | `golden_chapter_synthesis.py:913-917` (removed from active path) |
| `compose_chapter_prose` slot_map | **DROP** | `slot_map[st]` kept first-of-type only for STORY/REFLECTION/TEACHER_DOCTRINE | Additive path when repeated types detected | `chapter_composer.py:2949-3030` |
| `compose_additive_chapter_prose` | **ADD** | N/A | Append every packet in slot order; arc_thesis append-only | `chapter_composer.py:2962-2988` |
| `_trim_reflection` | **TRUNCATE** (legacy path) | Was capping sentences (fixed earlier) | Full reflection preserved on additive path | `chapter_composer.py:2205-2224` |
| `_shape_integration` | **TRUNCATE** (legacy path) | 60-word cap on integration sentences | Skipped on additive path (INTEGRATION verbatim) | `chapter_composer.py:2582-2605` |
| `enrichment_select` duplicate guard | **DROP** (bug) | Slots 3+7 both `COMPOSITE_DOCTRINE v02` (intra-chapter reuse allowed) | `_chapter_used_doctrine_source_ids` blocks reuse; slot 7 rerouted to `v01` | `enrichment_select.py:883-908`, `2381`, `2637-2638`, `971` |
| `pick_doctrine_atom_by_id` | **REPLACE** | Intra-chapter re-pick always allowed when `target == current` | LRU fallback when id already stamped this chapter | `doctrine_rotation.py:170-303` |
| `clean_for_delivery` | **DEDUPE** (post-render) | Book-wide paragraph dedupe unchanged | Unchanged — post-render only | `book_renderer.py:810+` |
| `register_output_strengthen` | **ADD/DROP** (post-render) | destack / cap density / suppress cadence | Unchanged — post-render only | `register_output_strengthen.py:196`, `552`, `957` |

## Duplicate guard verdict (burnout Ch2)

| Slot | Before | After |
|---:|---|---|
| 3 REFLECTION | `COMPOSITE_DOCTRINE v02` | `COMPOSITE_DOCTRINE v02` |
| 7 REFLECTION | `COMPOSITE_DOCTRINE v02` (**violation**) | `COMPOSITE_DOCTRINE v01` (**guard PASS**) |

`chapter_duplicate_doctrine_source_violations(ch2.slots) == []`

## Authored packet preservation (word deltas)

| idx | type | source_id | authored | compose | render | notes |
|---:|---|---|---:|---:|---:|---|
| 1 | HOOK | HOOK v32 | 90 | 90 | 90 | preserved |
| 2 | STORY | TURNING_POINT v06 | 150 | 150 | 150 | was collapsed before |
| 3 | REFLECTION | COMPOSITE_DOCTRINE v02 | 268 | 268 | 268 | was merged/deduped before |
| 4 | EXERCISE | EXERCISE v09 | 31 | 31 | 31 | preserved |
| 5 | STORY | STORY v04 | 51 | 51 | 51 | was dropped before |
| 6 | TEACHER_DOCTRINE | COMPOSITE_DOCTRINE v08 | 352 | 352 | 352 | was routed to COMPRESSION |
| 7 | REFLECTION | COMPOSITE_DOCTRINE v01 | 259 | 259 | 259 | rerouted from duplicate v02 |
| 8 | EXERCISE | EXERCISE v01 | 30 | 30 | 0 | exercise governance cap=1 drops 2nd EXERCISE at render (pre-existing) |
| 9 | STORY | STORY v15 | 48 | 48 | 48 | was dropped before |
| 10 | INTEGRATION | INTEGRATION v12 | 117 | 117 | 117 | preserved |

**Word totals:** baseline render 1114 → patched compose 1428 → patched render 1403 (+289 vs baseline)
