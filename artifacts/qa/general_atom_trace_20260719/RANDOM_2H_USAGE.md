# Random 2hr book + atom trace

```bash
PYTHONPATH=. python3 scripts/qa/run_random_2h_book_with_trace.py
PYTHONPATH=. python3 scripts/qa/run_random_2h_book_with_trace.py --seed 7
PYTHONPATH=. python3 scripts/qa/run_random_2h_book_with_trace.py --list-candidates
PYTHONPATH=. python3 scripts/qa/run_random_2h_book_with_trace.py --dry-run --seed 42
```

Picks a random viable persona×topic, renders `--runtime-format extended_book_2h` with the production four-piece chord, then writes `human_atom_trace.txt` beside `book.txt`.

## Smoke (2026-07-19)

- Seed `7` → `gen_z_professionals × anxiety` (comparison / F006)
- Render dir: `artifacts/qa/random_2h_books/random_2h_20260719_gen_z_professionals__anxiety__7/`
- Book words: 20974; slots: 144; resolved: 96; unresolved: 48 (honest `<unresolved:…>`)
- Trace HOOK: `atoms/gen_z_professionals/anxiety/HOOK/CANONICAL.txt:722` — “You sent it.”

Note: dirty `codex/*` branches with locale-threading drift can break `run_pipeline` before SPA/book exist. Run from `origin/main` / `offline/general-atom-trace-20260719` lineage (or restore matching `story_planner.py`).
