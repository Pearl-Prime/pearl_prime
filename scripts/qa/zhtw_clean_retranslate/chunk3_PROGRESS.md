# zh-TW retranslate chunk3 — progress tracker

Assigned slice: rows [264, 395] (0-indexed, inclusive) of the
`triage.py`-filtered (non-CLEAN_FALSE_POSITIVE, non-header) row list from
`scripts/qa/zhtw_clean_retranslate/triage_remaining_20260722.tsv` as of 2026-07-22.
132 files total. Branch: `agent/zhtw-retranslate-chunk3-20260723`.

## Validator correctness note (2026-07-23)

A sibling chunk agent found a real bug in `scripts/qa/zhtw_clean_retranslate/validate.py`:
`strip_meta()`/`cjk_ratio()` did not mirror `emit.py`'s own body-isolation logic, causing
(a) a false-PASS when a translated body is accidentally empty (empty string short-circuits
cjk_ratio to 1.0), and (b) false-FAILs on metadata-heavy blocks (mode:/carry_line:/family:/
BAND:/MECHANISM_DEPTH:/etc-style story-atom headers) where the real body is short but correct.
A canonical fix had not landed on `agent/zhtw-clean-corrupted-retranslate-20260722` as of this
commit, so this chunk built its own corrected validator
(mirrors `emit.py replace_body()`'s exact body-region extraction) and re-verified every file
already committed in this chunk against it — all passed (see below). All files from this point
forward in this chunk are validated with the corrected logic.

## URGENT re-verification vs TRUE-fixed validator (2026-07-23, coordinator instruction)

Coordinator flagged a REGRESSION in the intermediate fix (`45350ec8c7`): it used
`len(dash_idx)==3` to detect the rare 3-fence-no-closing shape, but the STANDARD
2-fence-pair shape (used by most RECOGNITION/MECHANISM_PROOF/TURNING_POINT/EMBODIMENT
blocks corpus-wide) also has exactly 3 dashes — so `45350ec8c7` silently false-passed
empty bodies. Truly fixed in `4b37c8bd5078b7b6f04f23ff702fade84a619524` on
`origin/agent/zhtw-clean-corrupted-retranslate-20260722` (shape detected from actual
content, not dash count, plus an explicit `EMPTY_OR_NEAR_EMPTY_BODY` check).

Confirmed this chunk's own `validate_fixed.py`/`emit_lib.py` never had the buggy
`len(dash_idx)==3` branch — `strip_meta()` always used "body between the last two
dashes" for the standard shape, matching the corrected behavior for that shape by
construction. But per coordinator instruction, re-verified all 42 already-committed
files by extracting EN (from `origin/main`) + ZH (from this branch's git objects) and
running them through the ACTUAL corrected `validate.py` module
(`4b37c8bd5078b7b6f04f23ff702fade84a619524`), not just this chunk's own validator.

**Result of first pass (against branch tip `b7dde14c9dc480e31003e28e6371f1b5975d1aff`):**
55 problems flagged across 5 files. Investigated each:

- `atoms/educators/courage/spiral` — `TURNING_POINT v01`, `EMBODIMENT v01`:
  `LOW_CJK_RATIO=0.00`. Checked EN source: these blocks contain ONLY
  `CALLBACK_ID:`/`CALLBACK_PHASE:` metadata, no prose body at all, in the EN source
  itself. **Benign** — legitimate EN-source-empty placeholder, correctly preserved
  empty in translation (matches this chunk's own CALLBACK_ID-only allowlist carve-out).
  No action needed.
- `atoms/educators/courage/shame` — same two headers, same cause, same verdict:
  **benign**, EN source itself has no prose in these two blocks.
- `atoms/first_responders/financial_anxiety/HOOK`, `atoms/first_responders/burnout/HOOK`
  — `HOOK v06`-`v30` (25 each): **benign**, confirmed previously as genuine EN-source
  stub placeholders (literal unauthored hook text), deliberately preserved verbatim per
  the EN-source-blocker policy. Already documented below as PARTIAL.
- `atoms/first_responders/courage/COMPRESSION` — `COMPRESSION v13`:
  `LOW_CJK_RATIO=0.00`. **GENUINE BUG, found and fixed for real.** Root cause: the EN
  source's `COMPRESSION v13` is the LAST block in the file and is missing its closing
  `---` fence (malformed/truncated EN source — confirmed via `git show` line count,
  `v13` ends the file with no trailing dash, unlike `v01`-`v12` which all close
  correctly). My original emit pass placed the already-correct Chinese translation in
  the wrong delimiter slot (the blank metadata region between the first two dashes)
  and left the raw English prose duplicated, untranslated, below it. Rebuilt the block
  to match the sibling `v01`-`v12` shape (`header/---/blank/---/BODY/---`), keeping the
  same already-correct Chinese translation and removing the duplicated English. No new
  content invented — same translation, correct placement. Fixed in commit
  `358373baa3b39a9c008f2d6567abe61bdf1e8d02`, pushed to this branch. Header/block count
  unchanged (13/13).
- Swept all 42 other files for the same "last block missing closing fence" EN-source
  shape (via header-tail scan against `origin/main`) — `first_responders/courage/COMPRESSION`
  was the ONLY file with this defect. No other files affected.

**Result of second pass (against branch tip `358373baa3b39a9c008f2d6567abe61bdf1e8d02`,
post-fix):** 54 problems remain, all in the two confirmed-benign categories above
(2+2 CALLBACK_ID-only empty blocks, 25+25 HOOK-stub placeholders). Zero genuine
failures remain. All 42 files are now re-verified clean against the TRUE corrected
validator.

**RECONCILIATION FLAG (coordinator, 2026-07-23):** chunk1 independently found the same
`validate.py` bug and pushed a canonical fix to `agent/zhtw-clean-corrupted-retranslate-20260722`
(commits `87d66cbb58` "repair validate.py strip_meta false-pass/false-fail bug" and `45350ec8c7`
"validate.py strip_meta() doesn't handle 3-fence block shape"). This chunk's
`scripts/qa/zhtw_clean_retranslate/validate_fixed.py` was built independently and is NOT
confirmed byte-identical to chunk1's fix — both target the same emit.py-mirroring issue but
may differ in edge-case handling (e.g. this chunk's version has an explicit CALLBACK_ID-only
allowlist carve-out; unclear if chunk1's does too). **A future consolidation pass must diff
the two and reconcile to one canonical validator** — do not assume they are identical or that
either one is sufficient without comparing. This chunk continues using its own
`validate_fixed.py` for the remainder of its slice per coordinator instruction, since both are
expected to converge on equivalent-enough logic for this chunk's own re-verification purposes.

## Status: 42 translated (2 partial) + 4 blocked / 132 total in slice

### Done (real hand-composed zh-TW translation, header/block parity verified, fixed-validator PASS)

- [x] `atoms/educators/self_worth/shame/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/educators/courage/INTEGRATION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/educators/courage/spiral/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/educators/courage/shame/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/educators/depression/watcher/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/educators/depression/overwhelm/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/educators/depression/grief/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/educators/depression/shame/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/financial_anxiety/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/compassion_fatigue/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/anxiety/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/sleep_anxiety/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/boundaries/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/somatic_healing/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/financial_stress/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/social_anxiety/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/grief/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/imposter_syndrome/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/self_worth/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/courage/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/depression/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/burnout/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/financial_anxiety/HOOK/locales/zh-TW/CANONICAL.txt`
  - PARTIAL: only v01-v05 (5/30) have real EN content, hand-translated. v06-v30 (25/30) are literal unauthored placeholder stubs in the EN source itself ("[Persona-specific hook for first_responders x financial_anxiety]") -- preserved verbatim, not invented.
- [x] `atoms/first_responders/burnout/HOOK/locales/zh-TW/CANONICAL.txt`
  - PARTIAL: only v01-v05 and v31-v33 (8/33) have real EN content, hand-translated. v06-v30 (25/33) are literal unauthored placeholder stubs in the EN source itself ("[Persona-specific hook for first_responders x burnout]") -- preserved verbatim, not invented.
- [x] `atoms/first_responders/overthinking/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/overthinking/INTEGRATION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/sleep_anxiety/INTEGRATION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/first_responders/imposter_syndrome/REFLECTION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/midlife_women/self_worth/REFLECTION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/midlife_women/financial_stress/REFLECTION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/midlife_women/depression/REFLECTION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/entrepreneurs/anchored/financial_anxiety/false_alarm/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/entrepreneurs/anchored/anxiety/watcher/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/entrepreneurs/anchored/anxiety/overwhelm/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/entrepreneurs/financial_anxiety/watcher/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/entrepreneurs/financial_anxiety/false_alarm/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/entrepreneurs/financial_anxiety/comparison/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/entrepreneurs/financial_anxiety/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/entrepreneurs/compassion_fatigue/spiral/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/entrepreneurs/compassion_fatigue/false_alarm/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/entrepreneurs/compassion_fatigue/comparison/locales/zh-TW/CANONICAL.txt`
- [x] `atoms/entrepreneurs/compassion_fatigue/COMPRESSION/locales/zh-TW/CANONICAL.txt`

### Blocked (EN source itself is malformed — empty body, nothing to translate)

- [BLOCKED] `atoms/educators/grief/COMPRESSION/locales/zh-TW/CANONICAL.txt`
  - EN source malformed: all 30 COMPRESSION blocks are empty (only compression_family: metadata, zero body text) in origin/main EN CANONICAL.txt. Nothing to translate; zh-TW mirrors EN byte-for-byte already. Needs atom-authoring pass on EN source first, not a translation fix.
- [BLOCKED] `atoms/educators/self_worth/COMPRESSION/locales/zh-TW/CANONICAL.txt`
  - Same as above: EN source COMPRESSION blocks are empty (metadata-only).
- [BLOCKED] `atoms/educators/courage/COMPRESSION/locales/zh-TW/CANONICAL.txt`
  - Same as above: EN source COMPRESSION blocks are empty (metadata-only).
- [BLOCKED] `atoms/educators/depression/COMPRESSION/locales/zh-TW/CANONICAL.txt`
  - Same as above: EN source COMPRESSION blocks are empty (metadata-only).

### Remaining (not yet started)

- [ ] `atoms/entrepreneurs/anxiety/watcher/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anxiety/grief/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anxiety/false_alarm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anxiety/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anxiety/comparison/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/financial_anxiety/comparison/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/compassion_fatigue/spiral/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/compassion_fatigue/shame/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/compassion_fatigue/comparison/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/anxiety/spiral/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/anxiety/grief/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/anxiety/false_alarm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/anxiety/comparison/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/sleep_anxiety/watcher/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/sleep_anxiety/shame/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/sleep_anxiety/comparison/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/overthinking/grief/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/boundaries/spiral/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/somatic_healing/spiral/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/somatic_healing/grief/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/somatic_healing/false_alarm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/financial_stress/watcher/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/financial_stress/spiral/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/financial_stress/grief/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/financial_stress/shame/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/social_anxiety/overwhelm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/social_anxiety/spiral/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/grief/comparison/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/imposter_syndrome/watcher/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/imposter_syndrome/overwhelm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/imposter_syndrome/spiral/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/imposter_syndrome/false_alarm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/courage/overwhelm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/depression/false_alarm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/depression/shame/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/anchored/burnout/shame/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/sleep_anxiety/watcher/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/sleep_anxiety/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/sleep_anxiety/comparison/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/overthinking/overwhelm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/overthinking/grief/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/overthinking/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/overthinking/comparison/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/boundaries/watcher/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/boundaries/spiral/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/boundaries/grief/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/boundaries/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/somatic_healing/spiral/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/somatic_healing/grief/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/somatic_healing/false_alarm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/somatic_healing/shame/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/somatic_healing/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/somatic_healing/comparison/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/financial_stress/watcher/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/financial_stress/overwhelm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/financial_stress/spiral/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/financial_stress/grief/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/financial_stress/false_alarm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/financial_stress/shame/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/financial_stress/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/financial_stress/comparison/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/social_anxiety/watcher/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/social_anxiety/overwhelm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/social_anxiety/spiral/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/social_anxiety/grief/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/social_anxiety/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/grief/INTEGRATION/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/grief/overwhelm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/grief/false_alarm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/grief/shame/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/grief/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/grief/comparison/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/imposter_syndrome/watcher/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/imposter_syndrome/spiral/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/imposter_syndrome/grief/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/imposter_syndrome/false_alarm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/imposter_syndrome/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/imposter_syndrome/REFLECTION/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/self_worth/watcher/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/self_worth/overwhelm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/self_worth/spiral/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/self_worth/grief/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/self_worth/false_alarm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/self_worth/COMPRESSION/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/courage/overwhelm/locales/zh-TW/CANONICAL.txt`
- [ ] `atoms/entrepreneurs/courage/spiral/locales/zh-TW/CANONICAL.txt`

Remaining count: 86

## Session close note (2026-07-23, session 2)

This session ended after 42 real translations (2 partial,
see notes above) + 4 blocked (46/132 accounted).
The remaining files are genuine, substantial hand-translation work (most are
13-31 blocks of narrative story-atom prose, grounding-exercise prose, or
first-person reflective essay prose, same register/quality bar as the files
above) — not yet started, not mechanically stubbed. A follow-up session/agent
should:
1. Re-run `triage.py` against current `origin/main` before resuming (other
   chunk agents may have advanced independently).
2. Continue through the remaining list above, using `emit_lib.py` (Pattern
   A/C body-isolation) + `validate_fixed.py` (NOT the original `validate.py`,
   which has the metadata-isolation bug documented above — see also the
   RECONCILIATION FLAG above re: chunk1's independent fix).
3. Commit via the same private-GIT_INDEX_FILE plumbing pattern, batching
   every 1-3 files given most remaining files are large (13-31 blocks).
4. Watch for known non-defect validator flags that are fine to accept after
   eyeballing the flagged block:
   (a) `LOW_CJK_RATIO` on blocks with heavy machine-readable metadata
       (mode:/carry_line:/family:/BAND:/MECHANISM_DEPTH:/etc.) relative to a
       short-but-correct translated body.
   (b) CALLBACK_ID/CALLBACK_PHASE-only blocks with zero narrative body in the
       EN source (seen in `courage/spiral`, `courage/shame`,
       `depression/watcher`) — preserve verbatim untranslated.
   (c) Literal `[Persona-specific hook for <persona> x <topic>]` placeholder
       stub text repeated across many HOOK-file block variants (seen in
       `first_responders/financial_anxiety/HOOK` 25/30 blocks,
       `first_responders/burnout/HOOK` 25/33 blocks) — this is a genuine
       EN-source authoring gap, not corruption. Translate only the blocks with
       real content, preserve the bracket placeholder verbatim for the rest,
       and flag the file as PARTIAL (see examples above) rather than skipping
       it entirely or inventing narrative content for the stub slots. Check
       every HOOK-shaped file in the remaining list for this pattern before
       assuming all its blocks need full narrative translation.
5. The 4 blocked files (`educators/{grief,self_worth,courage,depression}/
   COMPRESSION`) need EN-source authoring (all COMPRESSION blocks are empty
   in the EN CANONICAL.txt itself), not translation — flag to the atom-
   authoring backlog, do not attempt to translate placeholder/empty content.
6. `entrepreneurs/{topic}/{mechanism}` and `entrepreneurs/anchored/{topic}/
   {mechanism}` files are NOT uniformly template-generated — some topics use a
   highly schematic 5-character skeleton ("<Name> experiences the core
   recognition of <mechanism> in the context of <topic>...", identical body
   text across ALL mechanisms within that topic, verified via `diff`); others
   have full specific narrative content unique per character/mechanism, just
   like the non-anchored files. CONFIRMED this session: `financial_anxiety` and
   `compassion_fatigue` topics use the schematic template (verified across
   watcher/false_alarm/comparison/spiral mechanisms — RECOGNITION through
   EMBODIMENT v01-05, 20 blocks, are byte-identical apart from the mechanism/
   topic name substitution). `anxiety` topic (non-anchored) does NOT — each
   mechanism (watcher, overwhelm, grief, false_alarm, comparison) has unique
   narrative. Files with 26 blocks in a schematic-topic dir also carry 6
   mechanism-specific TURNING_POINT/EMBODIMENT/MECHANISM_PROOF v06/v07
   extension blocks that are NOT part of the reusable template — these recur
   verbatim (name-swapped) across the SAME mechanism in different topics
   though (e.g. the "watcher" v06/v07 extension text is identical whether the
   topic is financial_anxiety, depression, courage, self_worth, etc. — only
   the character name and topic noun change). Still: read each file's first
   block before assuming a shortcut applies; do not extrapolate from one
   sample file to an entire directory without spot-checking.

