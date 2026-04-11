# Legacy template packet pilot — anxiety

## Parameters

- topic: anxiety
- persona: gen_z_professionals
- teacher: ahjan
- runtime_format: standard_book
- seed: legacy_packet_pilot_v1
- legacy_library: v2_full

## Outputs

- `book.txt` — stitched section packets
- `section_packet_audit.json` — per-section sources and warnings
- `word_budget.json` — beatmap/enrichment budget plus packet totals

## Note

V4 template directories are not extracted in-repo; expect **zero** legacy YAML hits
unless `template_expand/_extracted/v2_full/` is populated.

## Measured (from this run)

- Total words (packets): 8412
- Sections: 102
- Average words/section: 82.5
- Sections with legacy scaffold text: 0
- Bridge inserts (chapter starts >1): 0
- Under beatmap target_words: 99
- Thin sections (<200 words): 94
- Sections >=400 words: 7
