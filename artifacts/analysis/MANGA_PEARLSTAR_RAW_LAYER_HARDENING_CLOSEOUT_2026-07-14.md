# Manga Pearl Star Raw Layer Hardening Closeout

- base_sha=`b507f3029e2aa7e5d9adfdb258b16d17910dc4fe`
- contract=`config/manga/raw_v5_layer_contract.yaml`
- implementation=`scripts/manga/raw_v5_layer_contract.py`
- prompt contract adds one-role-per-layer positive clauses and explicit contamination negatives.
- telemetry emitted: `raw_layer_role_confidence`, `contamination_suspected`, `candidate_layer_for_subject`.
- contaminated raw layers remain non-certified and selected-component fallback is preserved.
- blocker: no live Pearl Star regeneration was possible in this runtime.
- raw-v5-layer-roles=partial
- pearlstar-layer-contracts=green
- selected-component-fallback=preserved
- overall-manga-green=NOT_PROVEN
