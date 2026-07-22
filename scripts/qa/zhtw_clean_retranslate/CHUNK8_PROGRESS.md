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

## Status as of this commit: 62/127 translated + verified, 18/127 EN-source blockers, 14/127 already fixed by sibling PR #68, 33/127 remaining

### IMPORTANT: shared-worktree disk state is not trustworthy for re-verification

Discovered mid-session: `atoms/**/locales/zh-TW/CANONICAL.txt` files on disk in the
shared worktree (`/Users/ahjan/phoenix_omega_worktrees/zhtw-clean-retranslate-20260722`,
used concurrently by all 8 chunk agents) get silently overwritten by sibling agents'
concurrent `emit_batch.py` runs and `git checkout --` cleanups. A file validated PASS
immediately after `emit_batch.py` can show completely different (even truncated)
content minutes later if you re-read it from the live worktree disk path.

**Rule: always re-verify translated content by extracting from your own branch's
git objects (`git show refs/heads/agent/zhtw-retranslate-chunk8-20260723:<path>`
into a private scratch dir), never by re-reading the shared worktree disk state
after the fact.** Validating immediately post-`emit_batch.py` (before the commit)
is fine -- the risk window is between commit and *later* re-checks.

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
not just eyeballing). The zh-TW sibling for each of these is byte-identical to the
EN source. Translating these would mean inventing content from the slug names
alone -- explicitly out of scope. Report as a blocker instead.

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

### validate.py: two real bugs found and fixed this session (program-wide impact)

Both landed on `agent/zhtw-clean-corrupted-retranslate-20260722` (the shared
tooling branch used by all 8 chunk agents), not just chunk8:

1. `87d66cbb58` (chunk1): original `strip_meta()` regex silently discarded real
   content on some block shapes, false-PASSing via `cjk_ratio`'s empty-string
   short-circuit.
2. `45350ec8c7` (chunk1): follow-up fix for the 3-fence-no-closing-fence block
   shape, but used `len(dash_idx) == 3` as an *unconditional* signal for that
   shape. This is wrong -- the extremely common STANDARD 2-fence-pair shape
   (open/meta-body-split/close) also has exactly 3 dashes. **Every file using the
   standard shape -- the shape used by the vast majority of RECOGNITION/
   MECHANISM_PROOF/TURNING_POINT/EMBODIMENT engine-root blocks across this whole
   corpus -- was being silently mis-parsed as having an empty body, false-PASSing
   via the same cjk_ratio short-circuit the original 87d66cbb58 fix was trying to
   close.**
3. **`4b37c8bd50` (chunk8, this session):** fixed #2 by detecting the block shape
   from actual content (is there real non-blank text after the last dash) instead
   of dash count alone. Also added an explicit `EMPTY_OR_NEAR_EMPTY_BODY` check as
   defense in depth, since two real bugs in this file's own history both
   manifested as silent empty-body false-PASS via the same mechanism.

Discovered while hand-fixing `gen_x_sandwich/courage/shame` (see below) — that
file mixes both block shapes in the same file, which a pure dash-count check
cannot distinguish. Re-verified all 21 RECOGNITION-family files translated on
this branch (extracted from git objects, not the shared worktree disk) against
the corrected validator: **21/21 genuinely PASS with real non-empty bodies
confirmed per-block.** Sibling chunks relying on the pre-4b37c8bd50 validator for
this same very common engine family should re-verify.

### Known blocker: 3-fence emit.py shape — RESOLVED this session

`atoms/gen_x_sandwich/courage/shame/CANONICAL.txt` mixes the 3-fence-no-closing-
fence block layout (blocks 1-20: RECOGNITION/MECHANISM_PROOF/TURNING_POINT/
EMBODIMENT v01-05, unique content not shared with sibling engines -- Karen/Tom/
Maria/Bill/Diane characters) with the standard 2-fence-pair shape (blocks 21-27:
RECOGNITION v06 stub + the v06/v07 pattern set) in the SAME file. `emit.py` itself
has not been patched for the 3-fence shape (only `validate.py` has). Hand-fixed
per coordinator instruction: wrote a corrected body-isolation helper (mirrors the
validate.py fix -- detect shape per-block from content, not dash count) and
applied it directly instead of the standard `emit_batch.py` flow. Landed in
commit `c214330856`. Verified: header-ID parity exact (27/27), no stray English
leakage, all 27 blocks have real non-empty translated bodies.

### Landed batches (commits on this branch, chronological)

1. batch1 (12 files): `working_parents/{burnout,courage,depression}` 3-block
   COMPRESSION/TAKEAWAY/EXERCISE/PERMISSION/PIVOT/THREAD engines.
2. batch2 (10 files): `gen_z_professionals`/`gen_z_student` 4-block COMPRESSION +
   `working_parents` `courage`/`depression` 4-block SCENE.
3. batch3 (5 files): `gen_z_professionals/sleep_anxiety` 5-block COMPRESSION +
   `gen_z_student` `boundaries`/`burnout`/`depression`/`imposter_syndrome`
   6-block COMPRESSION.
4. batch4 (4 files): `gen_z_student` `overthinking`/`self_worth`/`sleep_anxiety`/
   `social_anxiety` 6-block COMPRESSION.
5. batch5 (2 files): `gen_alpha_students/overthinking` PERMISSION (20-block) +
   `gen_alpha_students/compassion_fatigue` INTEGRATION (25-block).
6. batch6 (2 files): `gen_alpha_students/self_worth` INTEGRATION (25-block) +
   `working_parents/depression` INTEGRATION (25-block).
7. batch7 (1 file): `gen_z_professionals/grief` REFLECTION (25-block, duplicate
   header numbers preserved exactly as authored in EN source).
8. batch8 (1 file): `gen_x_sandwich/courage` COMPRESSION (30-block).
9. batch9 (1 file): `gen_x_sandwich/boundaries/overwhelm` (26-block
   RECOGNITION-family engine-root file).
10. batch10 (7 files): `working_parents/courage` full RECOGNITION-family
    cluster (comparison/grief/overwhelm/watcher/false_alarm/shame/spiral) —
    discovered and diff-verified the cross-engine shared-20-block reuse pattern.
11. batch11 (4 files): `gen_x_sandwich/courage` cluster (comparison/grief/
    overwhelm/watcher; `shame` excluded here, handled separately).
12. batch12 (4 files): `gen_x_sandwich/burnout` cluster.
13. batch13 (4 files): `gen_x_sandwich/compassion_fatigue` cluster.
14. batch14 (1 file): `gen_x_sandwich/courage/shame` — hand-fixed 3-fence emit,
    full unique translation (does not share the template with its cluster).
15. batch15 (4 files): `working_parents/burnout` {comparison,spiral} +
    `working_parents/depression` {comparison,false_alarm} — confirmed shared-20
    reuse against the already-translated `working_parents/courage` set (same
    unfilled `{topic}/{engine}` EN template across all working_parents engine
    files for these characters).
16. docs commits: `scripts/qa/zhtw_clean_retranslate/CHUNK8_PROGRESS.md` updated
    3x to track state as work landed.

### Remaining (33 files, not done this session)


- `atoms/gen_x_sandwich/boundaries/spiral/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/boundaries/spiral/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/somatic_healing/false_alarm/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/somatic_healing/false_alarm/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/somatic_healing/spiral/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/somatic_healing/spiral/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/compassion_fatigue/grief/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/compassion_fatigue/grief/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/depression/grief/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/depression/grief/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/depression/overwhelm/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/depression/overwhelm/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/grief/grief/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/grief/grief/CANONICAL.txt blocks)
- `atoms/gen_alpha_students/self_worth/comparison/locales/zh-TW/CANONICAL.txt` (atoms/gen_alpha_students/self_worth/comparison/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/anxiety/comparison/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/anxiety/comparison/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/anxiety/grief/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/anxiety/grief/CANONICAL.txt blocks)
- `atoms/gen_x_sandwich/anxiety/spiral/locales/zh-TW/CANONICAL.txt` (atoms/gen_x_sandwich/anxiety/spiral/CANONICAL.txt blocks)
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


### Reuse-pattern hint for whoever continues this file

Before hand-translating any remaining `RECOGNITION`/`MECHANISM_PROOF`/
`TURNING_POINT`/`EMBODIMENT` engine-root file (`comparison`, `grief`, `overwhelm`,
`spiral`, `anxiety`/`shame` engines still remaining for `gen_x_sandwich/anxiety`,
`gen_x_sandwich/boundaries/spiral`, `gen_x_sandwich/somatic_healing`, and the
`gen_alpha_students` clusters), first `diff` it against any sibling engine file
already done for the same (persona, topic) pair -- a low diff-line count relative
to total file size (via `diff <(git show origin/main:A) <(git show origin/main:B)
| grep -c '^[<>]'`) indicates high reuse of the shared 20-block set, meaning only
the trailing 6-7 blocks need fresh translation. `atoms/gen_x_sandwich/boundaries/
spiral` vs `.../boundaries/overwhelm` (already translated) showed HIGHER
divergence (206 lines) than the courage/burnout/compassion_fatigue/depression
clusters in this same corpus, so it may need full translation rather than reuse --
verify before assuming. The `gen_alpha_students` anxiety/depression/grief clusters
(5 topics x up to 4 engines each) are untested for this pattern but worth checking
first given the file count.

The `HOOK`/`REFLECTION`/`COMPRESSION` remaining files (gen_alpha_students/burnout
HOOK, working_parents/courage HOOK+REFLECTION, etc.) are a DIFFERENT template
family, not part of this reuse pattern -- each needs its own check for internal
reuse (e.g. whether all `*_professionals/financial_anxiety/HOOK` files across
personas share a template) before assuming full one-off translation is required.

