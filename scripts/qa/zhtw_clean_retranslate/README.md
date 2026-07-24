# zh-TW EN_CLEAN_ZH_CORRUPTED retranslation — working tools

Supports the lane: discard corrupted zh-TW `CANONICAL.txt` bodies and
retranslate fresh from the clean EN sibling, for rows in
`artifacts/qa/atom_corruption_scope_20260722.tsv` where
`en_source_status == EN_CLEAN_ZH_CORRUPTED`.

## Files

- `triage.py` — re-derives per-file status against the current tree. Usage:
  `python3 triage.py artifacts/qa/atom_corruption_scope_20260722.tsv OUT.tsv`.
  Output columns: `zh_path, en_path, triage, n_en_blocks, n_zh_blocks`.
  `triage == CLEAN_FALSE_POSITIVE` means the file is already a good, structurally
  matching translation — do NOT touch it (the original scope-report heuristic
  flagged it, but on block-level re-inspection it's fine). Any other value is a
  real defect (`HEADER_MISMATCH`, `DUPLICATE_HEADERS`, `BAD_BLOCKS:n/m`) and
  needs a fresh translation.
- `triage_remaining_20260722.tsv` — a snapshot triage run from 2026-07-22
  against a fresh `origin/main` worktree. 1200 total EN_CLEAN_ZH_CORRUPTED rows,
  133 of which are `CLEAN_FALSE_POSITIVE` (already fine, skip). Re-run
  `triage.py` before resuming — this snapshot goes stale as files are fixed.
- `emit.py` — given an EN source path + an ordered list of translated block
  bodies (one string per `## HEADER` block, in file order) + an output path,
  writes a new zh-TW file that is byte-identical to the EN source in structure
  (headers, `compression_family:`/metadata fields, blank lines, `---` fences)
  except for the translated body text. Handles both known block layouts:
  - Pattern A/B (fenced): `header / --- / [metadata or blank] / --- / BODY / --- /`
  - Pattern C (COMPRESSION-style): `header / [optional "field: value" line] / BODY / --- / --- / --- /`
  Usage (single file): `python3 emit.py spec.json` where spec.json is
  `{"en_path":..., "out_path":..., "translations": [...]}`.
- `emit_batch.py` — same as `emit.py` but takes a JSON array of specs.
  Usage: `python3 emit_batch.py batch.json <repo_root>`.
- `validate.py` — per-file gate: header-ID parity with EN source, no leftover
  English/meta-commentary phrases, CJK ratio >= 0.5 per block, and Simplified-
  character contamination (opencc `s2t` diff intersected with
  non-Big5-encodable chars, to skip known merge-collision false positives like
  台/吃/游/群/床). Usage: `python3 validate.py <en_path> <zh_path>`.

## Workflow used so far (batches 1-4, 43 files, see git log on this branch)

1. Run `triage.py` to get the current defect list, filter out
   `CLEAN_FALSE_POSITIVE`.
2. Pick a batch (5-20 files is a reasonable single-pass size given each block
   needs a genuine hand-composed translation, not a mechanical transform).
3. Read each EN source, compose natural Taiwan Traditional Chinese translations
   per block (glossary: `config/localization/quality_contracts/glossary.yaml`;
   register notes: `config/localization/quality_contracts/MARKET_VOICE_BRIEF.md`).
4. Write a JSON spec (list of `{en_path, out_path, translations}`), run
   `emit_batch.py` to materialize the files.
5. Run `validate.py` on every changed file; fix any FAIL before committing.
6. `git add` only the changed `locales/zh-TW/CANONICAL.txt` files (never
   `git add -A` — this repo has large pre-existing unrelated LFS-pointer diff
   noise in `git status`). Commit with a batch-numbered message. Push after
   every batch — do not let uncommitted work accumulate across a session
   boundary.

## Known false-positive caveat (inherited from Prompt 1's scope report)

`atom_corruption_scope_20260722.tsv` classifies at file level by *presence* of
any bad block, not majority vote. Re-running `triage.py`'s own block-level
check (`CLEAN_FALSE_POSITIVE`) is more reliable — 133/1200 rows in the
2026-07-22 snapshot are already-clean files that should NOT be overwritten.
