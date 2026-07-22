# chunk1 tracking (agent/zhtw-retranslate-chunk1-20260723)

Slice: rows [0, 131] (0-indexed, inclusive) of the filtered
`triage_remaining_20260722.tsv` list (CLEAN_FALSE_POSITIVE rows excluded,
original file order preserved). 132 files total.

- `done_files.txt` — 54 files genuinely hand-translated, `emit.py`-written,
  and validated PASS with the fixed `validate.py`
  (see `../validate.py` commit `87d66cbb58` on
  `agent/zhtw-clean-corrupted-retranslate-20260722`).
- `not_started_files.txt` — 59 files not yet touched this session; still
  need real translation.
- Blocked (19 files, not tracked in a separate list here — see the
  chunk1 branch commit log message on batch 1 and the CLOSEOUT_RECEIPT):
  EN source itself is malformed (stub placeholders or a structurally
  empty COMPRESSION body), so no meaning exists yet to translate. Not a
  translation defect — an upstream EN authoring gap.
