# Manga Layered Default Integration Closeout

- base_sha=`b507f3029e2aa7e5d9adfdb258b16d17910dc4fe`
- implementation=`scripts/manga/integrate_real_v5_structural.py`
- tests=`18 passed` aggregate CI-safe suite
- production adapter discovers V5 panel roots, delegates to `assemble_real_v5_structural.py`, refuses `layer_00.png` authority, requires all four gates, and emits episode indexes.
- blocker: canonical `scripts/run_manga_pipeline.py` stage-boundary wiring was not executed against the full checkout; adapter is PR-ready but default call-path proof remains outstanding.
- manga-layered-default-integration=partial
- raw-v5-layer-roles=not-green
- selected-component-structural-assembly=green-for-proof
- overall-manga-green=NOT_PROVEN
