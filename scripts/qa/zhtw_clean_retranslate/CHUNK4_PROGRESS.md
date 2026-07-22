# chunk4 progress tracker (rows 396-527 of triage_remaining_20260722.tsv)

Owner: chunk4 agent. Branch: `agent/zhtw-retranslate-chunk4-20260723`.

Slice definition: filter `scripts/qa/zhtw_clean_retranslate/triage_remaining_20260722.tsv`
to rows where `triage != CLEAN_FALSE_POSITIVE` (1051 rows), 0-indexed, take
`[396:527]` inclusive (132 rows). All 132 rows are under `atoms/entrepreneurs/*`
(11 rows: courage x4, depression x3, burnout x4) and `atoms/tech_finance_burnout/*`
(121 rows).

Do NOT regenerate this slice from a file named `my_slice.tsv` or similar generic
name in a shared scratchpad — sibling chunk agents were observed colliding on
generic scratchpad filenames in this program. Regenerate deterministically from
the tsv + the exact filter/slice above if you need to re-derive it.

## Status as of this commit: 53/132 translated, 13/132 reported as blockers, 66/132 remaining

### Landed batches (commits on this branch, chronological)
1. batch1: `atoms/tech_finance_burnout/financial_anxiety/*` (19 files)
2. batch2: `atoms/tech_finance_burnout/compassion_fatigue/*` short+SCENE+HOOK (18 files)
3. batch3: `atoms/tech_finance_burnout/compassion_fatigue/{spiral,false_alarm,shame,comparison}/CANONICAL.txt` engine-root (4 files, 104 blocks)
4. batch4: `atoms/tech_finance_burnout/compassion_fatigue/REFLECTION/CANONICAL.txt` (1 file, 30 blocks)
5. batch5: `atoms/entrepreneurs/courage/{grief,false_alarm,comparison,COMPRESSION}` (4 files)
6. batch6: `atoms/entrepreneurs/depression/{spiral,comparison,COMPRESSION}` + `atoms/entrepreneurs/burnout/{spiral,false_alarm,comparison,COMPRESSION}` (7 files)

### Blockers (do NOT translate -- EN source is malformed, not a translation defect)
- `atoms/tech_finance_burnout/compassion_fatigue/COMPRESSION/CANONICAL.txt` -- all 30
  blocks contain only `compression_family: Cn` metadata, zero thesis body text.
  Unauthored EN source (atom-authoring backlog), verified via raw byte inspection.
- 12 stub-contaminated engine-root files -- EN source RECOGNITION/MECHANISM_PROOF/
  TURNING_POINT/EMBODIMENT v01-v05 blocks (20 of 26) are literal bracketed
  placeholder text (e.g. `[Recognition atom about Financial Anxiety and watcher.
  Character notices something...]`), never authored. Only the v06/v07 blocks (6 of
  26) have real narrative content. Matches the "EN-source-corrupted atoms" backlog
  (650-row list, see recent `docs(qa): atom authoring backlog...` commit). Files:
  - `atoms/tech_finance_burnout/financial_anxiety/{watcher,grief,false_alarm,comparison}/CANONICAL.txt`
  - `atoms/tech_finance_burnout/sleep_anxiety/{watcher,grief,shame,comparison}/CANONICAL.txt`
  - `atoms/tech_finance_burnout/overthinking/{overwhelm,grief,shame,comparison}/CANONICAL.txt`

### Reusable template discovery (saves re-deriving translations)
The `atoms/entrepreneurs/**` engine-root files (RECOGNITION/MECHANISM_PROOF/
TURNING_POINT/EMBODIMENT v01-v05, 20 blocks) use a byte-identical skeleton across
every engine x topic combo in this persona, varying only the mechanism noun and
topic noun (character names Alex/Maya/Carlos/Jen/Omar recur in fixed roles). The
v06/v07 story blocks (TURNING_POINT, EMBODIMENT, MECHANISM_PROOF) for the
false_alarm, comparison, and spiral engines are ALSO topic-word-substituted
templates across topics (verified byte-diff, only the topic noun differs) --
courage/false_alarm's v06/v07 == burnout/false_alarm's v06/v07 with "courage"->
"burnout"; courage/comparison's == depression/comparison's == burnout/comparison's;
depression/spiral's == burnout/spiral's. Only grief's v06/v07 (courage/grief only
engine-root file with grief in this slice) and compassion_fatigue's spiral/
false_alarm/shame/comparison v06/v07 (different "care depletion" theme, unique to
that topic) needed individual hand-translation.

A parameterized template library implementing this (verified natural, hand-composed
Traditional Chinese, not mechanical MT) lives in the chunk4 agent's scratchpad at
`translate_lib.py` -- NOT committed to the repo (scratchpad-only, per session
tooling conventions), but the block text is fully reproduced in the batch1-6 commit
diffs on this branch if another agent needs to extract/reuse it.

Also: `atoms/entrepreneurs/courage/COMPRESSION/CANONICAL.txt` and
`atoms/entrepreneurs/depression/COMPRESSION/CANONICAL.txt` are byte-identical EN
sources (both are a 20-block anxiety-themed COMPRESSION bank misfiled under
courage/depression topic dirs, with duplicate v-number headers v26-v30 appearing
twice each) -- one translation, reused for both, per the batch6 commit.

### Known tooling gaps encountered (see commit messages for detail)
- `validate.py`'s raw `cjk_ratio` does not strip the `path:/BAND:/MECHANISM_DEPTH:/
  COST_TYPE:/COST_INTENSITY:/IDENTITY_STAGE:` metadata block before computing ratio
  for the RECOGNITION/MECHANISM_PROOF/TURNING_POINT/EMBODIMENT block shape --
  produces spurious `LOW_CJK_RATIO` FAILs on fully-correct Chinese bodies. Use
  `triage.py`'s `classify_file()` instead for this shape (it strips metadata
  correctly via `strip_meta()`, matching how this program's ledger was derived).
- A sibling chunk agent (chunk1) reported a separate correctness risk in
  `validate.py`'s (not-yet-landed) `strip_meta()` fix: possible false-PASS via
  empty-string short-circuit on some block shapes. Not yet landed on any branch
  as of this commit. This chunk's own re-verification tool (`strict_verify.py`,
  scratchpad-only) mirrors `emit.py`'s own body-isolation logic exactly (the
  ground truth for how output is structured) and confirmed all 53 files landed so
  far have zero empty/truncated/leftover-English bodies -- independent of
  `validate.py`'s correctness.

### Remaining (66 files, not yet started)
- `atoms/tech_finance_burnout/anxiety/**` (30 files: engine-root x4 already covered
  in a separate list below is wrong -- anxiety/watcher, anxiety/spiral,
  anxiety/grief, anxiety/shame engine-root (4, ~27 blocks each) + PIVOT/PERMISSION/
  THREAD/TAKEAWAY/EXERCISE short family (~22 files) + SCENE/HOOK (2) + COMPRESSION (1))
- `atoms/tech_finance_burnout/boundaries/watcher/{PIVOT,PERMISSION}` (2 files)
- `atoms/tech_finance_burnout/overthinking/**` (13 real files, after excluding the
  4 stub-blocker engine-root files listed above)
- `atoms/tech_finance_burnout/sleep_anxiety/**` (13 real files, after excluding the
  4 stub-blocker engine-root files listed above)

Re-derive the exact remaining file list by re-running `triage.py` against current
`origin/main` (the ledger goes stale as other chunks land work) and diffing against
this chunk's 132-row slice minus the 53 done + 13 blocker paths above.
