# Word-count calibration fix — pilot report

**Branch:** `agent/word-count-calibration`  
**Subsystem:** `core_pipeline` (enrichment + depth + beatmap audit + optional packet cap)  
**Authority:** `config/format_selection/format_registry.yaml`; `config/depth/depth_module_map.yaml`

## Summary

- **Task A (short tiers):** Enrichment now loads `word_range` from the format registry, tightens multi-variant stacking for micro/short runtimes (`_max_extra_chunks_for_format`), applies per-slot book budget (including a final truncate so stacked bodies cannot exceed remaining book max), and caps **depth pass** additions so totals stay ≤ `word_range[1]` for every runtime that declares a range.
- **Task B (deep_book_6h):** For `deep_book_6h`, persona HOOK/SCENE/STORY pools merge **all personas** that have the same topic (primary first, deduped). Depth pass uses larger per-chunk caps, **three** priority sweeps per chapter, a lower deficit floor (55 vs 100), alternates seeds per round, and respects the registry **max** so totals stay in `[min, max]`.

## Before (RESULTS_V2 — `book.txt` `wc -w`)

Source: `artifacts/pilots/duration_matrix/RESULTS_V2.md` @ `main` snapshot in that doc.

| Topic | Format | Registry max | Actual (V2) | deep_book_6h min | Actual 6h (V2) |
|-------|--------|--------------|-------------|------------------|----------------|
| grief | micro_book_15 | 3000 | 4135 | 52000 | 39902 |
| anxiety | micro_book_15 | 3000 | 3583 | 52000 | 42080 |
| somatic_healing | micro_book_15 | 3000 | 6102 | 52000 | 26655 |

## After (enrichment + depth — `EnrichedBook.total_words`)

Measured with the same spine/knob/beatmap/enrichment/depth path as the pipeline core (seed `cal_report`), not `run_pipeline.py` full `book.txt` render.

| Topic | Format | Registry range | Actual words | Micro ≤ max? | 6h ≥ 41600 & ≤ 58000? |
|-------|--------|----------------|-------------|--------------|------------------------|
| grief | micro_book_15 | 2500–3000 | 3000 | yes | — |
| grief | deep_book_6h | 52000–58000 | 58000 | — | yes |
| anxiety | micro_book_15 | 2500–3000 | 2620 | yes | — |
| anxiety | deep_book_6h | 52000–58000 | 58000 | — | yes |
| somatic_healing | micro_book_15 | 2500–3000 | 3000 | yes | — |
| somatic_healing | deep_book_6h | 52000–58000 | 58000 | — | yes |

## Tests

- `tests/test_enrichment_select.py::test_short_format_does_not_exceed_word_range_max`
- `tests/test_enrichment_select.py::test_deep_book_6h_exceeds_40k_words`
- `tests/test_section_packet_composer.py::test_packet_word_cap_truncates_stacked_packet`

## Optional full spine verification

```bash
cd /Users/ahjan/phoenix_omega && export PYTHONPATH=.
for topic in grief anxiety somatic_healing; do
  for fmt in micro_book_15 deep_book_6h; do
    python3 scripts/run_pipeline.py --pipeline-mode spine \
      --runtime-format "$fmt" --topic "$topic" \
      --arc config/source_of_truth/master_arcs/gen_z_professionals__${topic}__*__F006.yaml \
      --no-job-check --quality-profile draft \
      --render-dir "artifacts/pilots/calibration_fix/${topic}/${fmt}"
  done
done
```

Then confirm `wc -w` on each `book.txt` against `format_registry.yaml` for the same format.
