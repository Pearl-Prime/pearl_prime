# chunk8 progress tracker (rows 924-end of filtered triage_remaining_20260722.tsv)

Owner: chunk8 agent. Branch: `agent/zhtw-retranslate-chunk8-20260723`.

Slice definition: filter `scripts/qa/zhtw_clean_retranslate/triage_remaining_20260722.tsv`
to rows where `triage != CLEAN_FALSE_POSITIVE` (1051 rows), 0-indexed, take
`[924:end]` inclusive (127 rows).

Do NOT regenerate this slice from a generic scratchpad filename (e.g. `my_slice.tsv`)
-- sibling chunk agents were observed colliding on generic scratchpad filenames in
this program. Regenerate deterministically from the tsv + the exact filter/slice
above if you need to re-derive it. This file (checked into the repo, not
scratchpad) is the durable record.

## Status as of this commit: 37/127 translated + verified, 18/127 EN-source blockers, 14/127 already fixed by sibling PR #68, 58/127 remaining

### Pre-work triage (both checks required — origin/main alone is not enough)

1. Re-ran `triage.py`'s block-level logic against **current `origin/main`**: all
   127 rows in this slice still showed real defects (0 already clean on main).
2. Cross-checked against the sibling **`agent/zhtw-clean-corrupted-retranslate-20260722`**
   branch tip (PR #68, 8 batches landed there but not yet merged to main) — found
   **14 files already fixed there** (not visible from origin/main alone, since that
   PR is unmerged). Skipped these to avoid duplicate/conflicting work; they will
   reconcile naturally when PR #68 merges. See "Already fixed by sibling PR #68"
   below.

### Blockers (do NOT translate -- EN source is malformed, not a translation defect)

18 `COMPRESSION`-engine files where the EN source has literally **no body prose** --
just `## COMPRESSION vNN | slug` headers with a bare `compression_family: Cx` line
and zero sentence content (verified via `emit.py`'s own body-slot extraction logic,
not just eyeballing -- the "body" that `emit.py` would replace is the
`compression_family: Cx` line itself, because there is nothing else in the block).
The zh-TW sibling for each of these is byte-identical to the EN source (never
translated because there was nothing to translate). Translating these would mean
inventing content from the slug names alone, which is explicitly out of scope --
report as a blocker instead. Matches the reference "EN-source-corrupted atoms"
authoring backlog documented elsewhere in this program.

Files:
- `atoms/working_parents/courage/COMPRESSION/CANONICAL.txt`
- `atoms/working_parents/depression/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/compassion_fatigue/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/anxiety/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/boundaries/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/financial_stress/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/grief/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/self_worth/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/courage/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/depression/COMPRESSION/CANONICAL.txt`
- `atoms/gen_z_professionals/compassion_fatigue/COMPRESSION/CANONICAL.txt`
- `atoms/gen_z_professionals/anxiety/COMPRESSION/CANONICAL.txt`
- `atoms/gen_z_professionals/boundaries/COMPRESSION/CANONICAL.txt`
- `atoms/gen_z_professionals/financial_stress/COMPRESSION/CANONICAL.txt`
- `atoms/gen_z_professionals/grief/COMPRESSION/CANONICAL.txt`
- `atoms/gen_z_professionals/self_worth/COMPRESSION/CANONICAL.txt`
- `atoms/gen_z_professionals/courage/COMPRESSION/CANONICAL.txt`
- `atoms/gen_z_professionals/depression/COMPRESSION/CANONICAL.txt`

### Already fixed by sibling PR #68 (skipped, no duplicate work)

14 `COMPRESSION` files, already genuinely translated on
`agent/zhtw-clean-corrupted-retranslate-20260722` (batches 7-8) but not yet merged
to `origin/main`:

- `atoms/gen_x_sandwich/financial_anxiety/COMPRESSION/CANONICAL.txt`
- `atoms/gen_x_sandwich/sleep_anxiety/COMPRESSION/CANONICAL.txt`
- `atoms/gen_x_sandwich/overthinking/COMPRESSION/CANONICAL.txt`
- `atoms/gen_x_sandwich/somatic_healing/COMPRESSION/CANONICAL.txt`
- `atoms/gen_x_sandwich/social_anxiety/COMPRESSION/CANONICAL.txt`
- `atoms/gen_x_sandwich/imposter_syndrome/COMPRESSION/CANONICAL.txt`
- `atoms/gen_x_sandwich/burnout/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/financial_anxiety/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/sleep_anxiety/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/overthinking/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/somatic_healing/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/social_anxiety/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/imposter_syndrome/COMPRESSION/CANONICAL.txt`
- `atoms/gen_alpha_students/burnout/COMPRESSION/CANONICAL.txt`

### Landed batches (commits on this branch, chronological)

1. batch1 (12 files): `working_parents/{burnout,courage,depression}` 3-block
   COMPRESSION/TAKEAWAY/EXERCISE/PERMISSION/PIVOT/THREAD engines.
2. batch2 (10 files): `gen_z_professionals`/`gen_z_student` 4-block COMPRESSION +
   `working_parents` `courage`/`depression` 4-block SCENE (template variables
   `{transit_line}`/`{weather_detail}`/`{street_name}` preserved verbatim).
3. batch3 (5 files): `gen_z_professionals/sleep_anxiety` 5-block COMPRESSION +
   `gen_z_student` `boundaries`/`burnout`/`depression`/`imposter_syndrome`
   6-block COMPRESSION.
4. batch4 (4 files): `gen_z_student` `overthinking`/`self_worth`/`sleep_anxiety`/
   `social_anxiety` 6-block COMPRESSION.
5. batch5 (2 files): `gen_alpha_students/overthinking` PERMISSION (20-block) +
   `gen_alpha_students/compassion_fatigue` INTEGRATION (25-block, YAML-style
   `mode:`/`reframe_type:`/`weight:`/`carry_line:`/`note:` metadata preserved
   verbatim, manually verified intact post-`emit.py`).
6. batch6 (2 files): `gen_alpha_students/self_worth` INTEGRATION (25-block) +
   `working_parents/depression` INTEGRATION (25-block, first-person prose v01-07
   + templated body-landed/cost-visible/question-open/someone-else/still-here
   v08-25).
7. batch7 (1 file): `gen_z_professionals/grief` REFLECTION (25-block, single-fence
   F1-F5 family/voice_mode/mechanism_emphasis metadata for v01-v29 odd-numbered +
   templated "mechanism I want to name" pattern for v16-v25; duplicate header
   numbers -- v17/19/21/23/25 appear twice -- preserved exactly as authored in the
   EN source, not "fixed").
8. batch8 (1 file): `gen_x_sandwich/courage` COMPRESSION (30-block, boundaries-
   themed compressions with recurring "courage isn't the absence of the cost
   calculation" boilerplate closer).

### validate.py bug + re-verification (2026-07-23, post-closeout correction)

Sibling chunk1 agent found and fixed a real bug in `validate.py`'s `strip_meta()`
(commit `87d66cbb58` on `agent/zhtw-clean-corrupted-retranslate-20260722`): the old
regex assumed every block has a `---`-fenced metadata section, which (a) left
untranslated EN metadata lines inside the CJK-ratio window on metadata-heavy blocks
(false-FAIL on good translations), and (b) silently discarded the actual translated
body to `""` on blocks with no metadata section -- which then false-**PASSED** via
`cjk_ratio`'s empty-string short-circuit (`cr == 1.0` when trimmed string is empty).
That second direction is the dangerous one: a validator saying PASS on a blank body.

Re-verified all 37 already-committed files on this branch against the fixed
validator (`validate.py` @ `87d66cbb58`):
- **37/37 PASS** under the fixed validator.
- Explicitly checked all 279 individual blocks across the 37 files for empty/
  near-empty translated bodies (the specific "false-PASS via empty string" risk) --
  **zero** found. No file on this branch was silently false-passed by the old bug.
- The 2 cases previously documented in the session closeout as validator false
  positives under the *old* buggy validator both **now PASS cleanly** under the
  fixed one, confirming the original manual reasoning was correct and no content
  fix was needed:
  - `atoms/gen_alpha_students/compassion_fatigue/INTEGRATION/locales/zh-TW/CANONICAL.txt`
  - `atoms/gen_z_professionals/grief/REFLECTION/locales/zh-TW/CANONICAL.txt`

### Remaining (58 files, not done this session)

All in the heaviest tier (26-33 blocks/file, long narrative SCENE/RECOGNITION-style
prose or long COMPRESSION sets):

- `atoms/gen_x_sandwich/boundaries/overwhelm/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/boundaries/overwhelm/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/boundaries/spiral/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/boundaries/spiral/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/burnout/comparison/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/burnout/comparison/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/burnout/false_alarm/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/burnout/false_alarm/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/burnout/shame/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/burnout/shame/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/burnout/spiral/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/burnout/spiral/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/compassion_fatigue/comparison/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/compassion_fatigue/comparison/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/compassion_fatigue/false_alarm/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/compassion_fatigue/false_alarm/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/compassion_fatigue/shame/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/compassion_fatigue/shame/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/compassion_fatigue/spiral/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/compassion_fatigue/spiral/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/courage/comparison/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/courage/comparison/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/courage/grief/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/courage/grief/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/courage/overwhelm/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/courage/overwhelm/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/courage/watcher/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/courage/watcher/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/somatic_healing/false_alarm/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/somatic_healing/false_alarm/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/somatic_healing/spiral/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/somatic_healing/spiral/CANONICAL.txt blocks)
- `atoms/working_parents/burnout/comparison/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/burnout/comparison/CANONICAL.txt blocks)
- `atoms/working_parents/burnout/spiral/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/burnout/spiral/CANONICAL.txt blocks)
- `atoms/working_parents/courage/comparison/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/courage/comparison/CANONICAL.txt blocks)
- `atoms/working_parents/courage/grief/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/courage/grief/CANONICAL.txt blocks)
- `atoms/working_parents/courage/overwhelm/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/courage/overwhelm/CANONICAL.txt blocks)
- `atoms/working_parents/courage/watcher/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/courage/watcher/CANONICAL.txt blocks)
- `atoms/working_parents/depression/comparison/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/depression/comparison/CANONICAL.txt blocks)
- `atoms/working_parents/depression/false_alarm/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/depression/false_alarm/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/compassion_fatigue/grief/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/compassion_fatigue/grief/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/depression/grief/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/depression/grief/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/depression/overwhelm/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/depression/overwhelm/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/grief/grief/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/grief/grief/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/self_worth/comparison/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/self_worth/comparison/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/anxiety/comparison/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/anxiety/comparison/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/anxiety/grief/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/anxiety/grief/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/anxiety/spiral/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/anxiety/spiral/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/courage/shame/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/courage/shame/CANONICAL.txt blocks)
- `atoms/working_parents/courage/false_alarm/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/courage/false_alarm/CANONICAL.txt blocks)
- `atoms/working_parents/courage/shame/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/courage/shame/CANONICAL.txt blocks)
- `atoms/working_parents/courage/spiral/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/courage/spiral/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/anxiety/grief/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/anxiety/grief/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/anxiety/overwhelm/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/anxiety/overwhelm/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/anxiety/shame/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/anxiety/shame/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/anxiety/spiral/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/anxiety/spiral/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/courage/shame/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/courage/shame/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/burnout/HOOK/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/burnout/HOOK/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/financial_anxiety/HOOK/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/financial_anxiety/HOOK/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/social_anxiety/REFLECTION/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/social_anxiety/REFLECTION/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/boundaries/COMPRESSION/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/boundaries/COMPRESSION/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/compassion_fatigue/COMPRESSION/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/compassion_fatigue/COMPRESSION/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/depression/COMPRESSION/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/depression/COMPRESSION/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/financial_anxiety/HOOK/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/financial_anxiety/HOOK/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/financial_stress/COMPRESSION/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/financial_stress/COMPRESSION/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/grief/COMPRESSION/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/grief/COMPRESSION/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/self_worth/COMPRESSION/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/self_worth/COMPRESSION/CANONICAL.txt blocks)
- `atoms/gen_z_professionals/financial_anxiety/HOOK/locales/zh-TW/CANONICAL.txt` (atoms/gen_z_professionals/financial_anxiety/HOOK/CANONICAL.txt blocks)
- `atoms/working_parents/courage/HOOK/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/courage/HOOK/CANONICAL.txt blocks)
- `atoms/working_parents/courage/REFLECTION/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/courage/REFLECTION/CANONICAL.txt blocks)
- `atoms/working_parents/depression/REFLECTION/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/depression/REFLECTION/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/burnout/HOOK/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/burnout/HOOK/CANONICAL.txt blocks)
- `atoms/gen_z_professionals/financial_anxiety/spiral/locales/zh-TW/CANONICAL.txt` (atoms/gen_z_professionals/financial_anxiety/spiral/CANONICAL.txt blocks)
- `atoms/working_parents/burnout/HOOK/locales/zh-TW/CANONICAL.txt` (atoms/working_parents/burnout/HOOK/CANONICAL.txt blocks)

