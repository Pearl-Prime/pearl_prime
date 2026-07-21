# Manga Mode Plumbing Closeout

- live source audit found `mode` already present in `run_one_book`, `emit_series_setup`, and story architecture.
- verifier=`scripts/manga/verify_manga_mode_plumbing.py`
- verifier fails when internal or handoff vessel beats disappear.
- CI-safe unit proof passes with both internal and handoff vessels.
- blocker: actual repo vessel config proof was not executed in the full checkout.
- manga-teacher-mode=partial
- manga-music-mode=partial
- emit-mode-plumbing=green
- overall-manga-green=NOT_PROVEN
