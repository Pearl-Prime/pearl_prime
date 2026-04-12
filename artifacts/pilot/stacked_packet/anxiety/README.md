# Legacy template packet pilot — anxiety

## Parameters

- topic: anxiety
- persona: gen_z_professionals
- teacher: ahjan
- runtime_format: standard_book
- seed: legacy_packet_pilot_v1
- legacy_library: v2_somatic

## Outputs

- `book.txt` — stitched section packets
- `section_packet_audit.json` — per-section sources and warnings
- `word_budget.json` — beatmap/enrichment budget plus packet totals

## Note

Legacy scaffold hits depend on `config/templates/legacy_template_index.yaml` and extracted
trees. Use `--legacy-library v2_somatic` when `template_expand2/_extracted/qaudiobook_template_v2_somatic/sections_somatic_v2/`
is present (12×10×5 somatic YAML). Sparse V4 bootstrap trees only light a few slots.

## Measured (from this run)

- Total words (packets): 14397
- Sections: 102
- Average words/section: 141.1
- Sections with legacy scaffold text: 51
- Bridge inserts (chapter starts >1): 0
- Under beatmap target_words: 75
- Thin sections (<200 words): 82
- Sections >=400 words: 7
