# Duration matrix scaling delta (format-aware enrichment + depth deficit fix)

## Root cause (pre-change)

- Beatmap assigned **different `target_words` per slot** by `runtime_format`, but `select_enrichment` filled **one** registry / persona / teacher body per slot, so **actual body length was identical** across extended/deep tiers.
- `apply_depth_pass` updated `deficit` with `deficit -= added_w` only. New depth slots also carried `target_words`, so **remaining deficit vs chapter targets was wrong**, and the pass could stop early with the same depth stack across formats.

## Changes

1. **`phoenix_v4/planning/enrichment_select.py`** — After the primary waterfall pick, **stack additional distinct variants** from the same registry section and/or additional atoms from the same persona/teacher pool when `slot.target_words` exceeds the primary word count. Chunk budget scales with **`runtime_format` and per-slot `target_words`** (`slots_format_scaled` in `enrichment_audit`).
2. **`apply_depth_pass`** — After each depth append, recompute  
   `deficit = sum(slot.target_words) - chapter.total_words`.
3. **`phoenix_v4/planning/beatmap_compile.py`** — Add `runtime_format` to each slot's `atom_selection_criteria`.
4. **`phoenix_v4/rendering/section_packet_composer.py`** — Honor `beatmap_slot["target_words"]`; optional `supplemental_enrichment_blocks` and `beatmap_slot["supplemental_enrichment_blocks"]` (merged with Pearl_Writer expansion on main).
5. **`scripts/pilot/run_duration_matrix_pilot.py`** — Added at repo root (was referenced by the pilot spec).

## `book.txt` word counts — before vs after (3×3 long-form cells)

**Before** (plateau; same count for 2h/4h/6h per topic):

| Topic | extended_book_2h | deep_book_4h | deep_book_6h |
|-------|------------------:|-------------:|-------------:|
| grief | 10,749 | 10,749 | 10,749 |
| anxiety | 11,563 | 11,563 | 11,563 |
| somatic_healing | 6,884 | 6,884 | 6,884 |

**After** (`wc -w` on spine `--render-book`, persona `gen_z_professionals`, draft, 2026-04-12):

| Topic | extended_book_2h | deep_book_4h | deep_book_6h |
|-------|------------------:|-------------:|-------------:|
| grief | 21,760 | 31,049 | 39,902 |
| anxiety | 23,891 | 35,389 | 41,929 |
| somatic_healing | 18,754 | 24,209 | 26,655 |

All nine cells are **distinct**; 2h < 4h < 6h per topic.

## Verification

```bash
cd /Users/ahjan/phoenix_omega && PYTHONPATH=. python3 scripts/pilot/run_duration_matrix_pilot.py
```

## Tests

- `tests/test_enrichment_select.py::test_runtime_format_scales_enriched_word_count`
- `tests/test_section_packet_composer.py::test_beatmap_target_words_override_and_supplements`
