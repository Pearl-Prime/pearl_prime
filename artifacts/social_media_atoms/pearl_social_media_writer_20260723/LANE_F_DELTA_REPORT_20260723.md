# Lane F — Delta Report (2026-07-23)

Agent: `pearl-social-media-writer` (Lane F, wave-2 atom expansion) · Continues
Lane A (research)/Lane C (repair pilot)/Lane D+E (assembler wiring, separate
worktree, not touched here).

Acceptance layer of everything below: **EXECUTED-REAL for the touched
cells/rows** (byte-verified in `SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl`,
local `check_social_post_variation.py` gate passing, hand-traced sample) —
**not** catalog-wide, and **not** `PROVEN-AT-BAR` (no blind-judged sample was
run this wave either). Six-layer taxonomy per
`docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md`.

Required citation source for all new/rewritten rows:
`artifacts/social_media_atoms/pearl_social_media_writer_20260723/deep_research_digest_20260723.md`
(Lane A digest — same file Lane C cited; re-used, not re-authored).

Script that made every change below (idempotent, re-runnable against a fresh
checkout for audit): `artifacts/social_media_atoms/pearl_social_media_writer_20260723/build_lane_f_expansion.py`.

---

## 1. Discovery — full-bank audit (not just the touched pilot slice)

Re-ran the family/persona/topic/broken-template audit across the entire
`evergreen_en_us_atoms.jsonl` (1,724 rows before this wave), not just Lane C's
touched cells:

- **Family coverage before**: `MICRO_STORY` (4), `CASE_PROOF` (4),
  `CAROUSEL_SLIDE` (12), `THREAD_UNIT` (8), `VIDEO_BEAT` (10) — confirmed all
  five new families existed ONLY for `(anxiety, burnout) x
  (corporate_managers, gen_z_professionals)`, exactly as Lane C's closeout
  stated.
- **Persona coverage before**: `corporate_managers` 559, `gen_z_professionals`
  559, `healthcare_rns` 540, `entrepreneurs` 22, `gen_x_sandwich` 22,
  `working_parents` 22. The three thin personas' 22 rows each covered
  **only the `burnout` topic**, and only the original 9 pre-2026-07-21
  families (no `anxiety` rows of any family existed for
  `entrepreneurs`/`gen_x_sandwich`/`working_parents` at all — a gap not
  previously named this explicitly).
- **Broken-template rows**: `grep -c "is not the whole story"` = 60 total in
  the file; 6 already repaired by Lane C (anxiety+burnout x
  corp/genz/healthcare_rns), confirming **54 broken `HOOK_COVER` rows**
  remained, spanning exactly 18 topics x 3 personas
  (`corporate_managers`/`gen_z_professionals`/`healthcare_rns`), all
  `variant_index: 1`.
- **Cross-persona verbatim duplication**: confirmed Lane C's own honest
  finding — `REFRAME`-02/-03 and `MECHANISM_EXPLAINER`-02/-03 for
  `anxiety`+`burnout` were still byte-identical across
  `corporate_managers`/`gen_z_professionals`/`healthcare_rns` (8 distinct
  duplicate clusters: {ME-02, ME-03, R-02, R-03} x {anxiety, burnout}).
- **Localization**: `apac_localization_atoms.jsonl` already has full 10-field
  `adapter_family` coverage for all 7 markets Lane C touched (`en-SG`,
  `ja-JP`, `ko-KR`, `zh-CN`, `zh-HK`, `zh-SG`, `zh-TW`); spot-checked every
  specific issue the native-speaker validation notes raised (Kakao Story
  defunct-name risk, MZ-generation staleness, 45%/67%/55%/21% stale
  percentages, XHS credential-pairing, HK intra-sentential code-switching,
  TW Threads-era register shift, SG two-register split) against the live
  rows — **all were already folded in by Lane C**; no residual
  percentage-figure or stale-claim strings found in a full grep pass. See
  §5 for the one gap that is real but unclosable this wave.
- **New defect noticed in passing (not fixed, out of this wave's scope)**:
  `EVG-ENUS-BURN-WKPR-HC-01` (`working_parents`, pre-existing row, not part
  of Lane C's or this wave's touched set) opens with `"working parents: the
  second shift starts..."` — a persona-address-style hook that reads as
  metadata leakage in the same spirit as (but not identical to) the
  `"is not the whole story"` pattern. `working_parents` was not one of the
  two personas this wave expanded (Lane C's note suggested
  `entrepreneurs`/`gen_x_sandwich` as candidates; `working_parents` remains
  fully untouched by both waves). Flagging for the next wave, not fixed here.

---

## 2. New family rows added (68 rows)

Personas `entrepreneurs` and `gen_x_sandwich` — previously **zero** rows in
any of the 5 new families, for any topic — now have full parity with the
`corporate_managers`/`gen_z_professionals` pilot cell structure across both
`anxiety` and `burnout`:

| Topic | Persona | MICRO_STORY | CASE_PROOF | CAROUSEL_SLIDE | THREAD_UNIT | VIDEO_BEAT | Total |
|---|---|---|---|---|---|---|---|
| burnout | entrepreneurs | 1 | 1 | 6 | 4 | 5 | 17 |
| burnout | gen_x_sandwich | 1 | 1 | 6 | 4 | 5 | 17 |
| anxiety | entrepreneurs | 1 | 1 | 6 | 4 | 5 | 17 |
| anxiety | gen_x_sandwich | 1 | 1 | 6 | 4 | 5 | 17 |

**68 new rows total.** Each is an authored sentence (not a template swap) in
the persona's established voice (`entrepreneurs` = founder/business-owner
framing, e.g. investor calls, runway, fundraising; `gen_x_sandwich` =
caring for two generations at once, e.g. calls to a parent vs. a child's
bedtime), citing Lane A's digest sections for the underlying structural
pattern (Anchor/Turn/Shift/Residue for `MICRO_STORY`, Problem-Mechanism-
Result for `CASE_PROOF`, open-loop carousel arc, Hook-Context-Position-
Invitation for `THREAD_UNIT`, the 5-beat video map for `VIDEO_BEAT`) — same
citation discipline Lane C used, not a new claim.

A same-family cross-persona near-duplicate was caught and fixed during this
wave's own self-QA (`EVG-ENUS-ANXI-ENTR-VB-04` vs `EVG-ENUS-ANXI-GXSW-VB-04`,
3-gram Jaccard 0.80 before rewrite, 0 after) — see §4.

---

## 3. Broken-template repair (54 → 0 for this pattern)

All 54 remaining `"{persona}: {clause} is not the whole story."` `HOOK_COVER`
rows (18 topics x `corporate_managers`/`gen_z_professionals`/`healthcare_rns`)
rewritten in place as real, persona-voiced sentences with no metadata
leakage. Topics repaired this wave: `addiction`, `adhd`, `body_image`,
`boundaries`, `compassion_fatigue`, `courage`, `depression`, `divorce`,
`financial_anxiety`, `grief`, `imposter_syndrome`, `money`, `overthinking`,
`relationship_anxiety`, `self_worth`, `shame`, `sleep_anxiety`,
`social_anxiety` — all 18 remaining topics from Lane C's closeout, all 3
personas each.

Example (`overthinking`, `gen_z_professionals`):
- **Before**: `"Gen Z professionals: thinking harder will create certainty is
  not the whole story."`
- **After**: `"You think you're one more replay away from certainty. You've
  replayed this fifty times already and it hasn't shown up yet."`

`grep -c "is not the whole story" SOURCE_OF_TRUTH/social_media_atoms/*.jsonl`
now returns 0 across all three bank files — this specific mail-merge pattern
is fully repaired bank-wide. (Other, unrelated broken-template shapes may
still exist and were not searched for beyond this named pattern.)

---

## 4. De-duplication (8 rows rewritten in touched cells + 1 self-caught)

For the `anxiety`+`burnout` x touched-persona cells, rewrote the
`gen_z_professionals` occurrence of each of the 8 verbatim-duplicate
clusters Lane C's closeout named (`REFRAME`-02/-03,
`MECHANISM_EXPLAINER`-02/-03, both topics) into a genuinely distinct sentence
carrying the same mechanism. Example:

- **Before** (identical across `corporate_managers`/`gen_z_professionals`/
  `healthcare_rns`): `"A useful reframe: your response makes sense, but it
  does not have to run the next hour. rest is a recovery input, not a
  reward for perfect output."`
- **After** (`gen_z_professionals` only): `"It's allowed to be exhausted and
  also allowed to stop mid-week, not just at the finish line. One real off
  hour counts as recovery input right now, not a reward you haven't earned
  yet."`

**Reported honestly**: only the `gen_z_professionals` occurrence was
rewritten per cluster (the mission's stated bar — "at least one occurrence")
— `corporate_managers` and `healthcare_rns` remain byte-identical to each
other in these 8 rows; that duplicate pair is not resolved this wave.

Additionally, this wave's own new-family authoring introduced one
cross-persona near-duplicate (`EVG-ENUS-ANXI-ENTR-VB-04` /
`EVG-ENUS-ANXI-GXSW-VB-04`, jaccard 0.80) — caught by a full pairwise scan of
the 68 new rows before handoff and rewritten distinctly (jaccard 0 after).

---

## 5. APAC localization — no new gap found or closed this wave

Re-read `NATIVE_SPEAKER_VALIDATION_20260723.md` in full and checked every
named issue against the live `apac_localization_atoms.jsonl` rows. Every
specific defect the six native-speaker subagents flagged in that document
was already folded in by Lane C (defunct product names removed, stale
percentages absent, MZ-generation/group-harmony framing corrected, XHS
credential-pairing added, HK intra-sentential code-switching corrected, TW
Threads-era register named, SG two-register split authored). **No action
taken this wave** — there was nothing left to close among the six markets
this repo has a native-speaker agent for.

**One real, unclosable gap remains, named honestly**: the Singapore
validation notes flag "no mention of Malay/Tamil/Eurasian audiences" as
missing — but there is no `translate-ms-sg`/`translate-ta-sg` (or
equivalent) native-speaker subagent available in this environment's agent
roster to author that content per this skill's discipline ("do not draft
market tone content yourself"). This is a structural gap for a future wave
once such an agent exists, not something this wave could close.

---

## 6. Self-QA

- `python3 scripts/ci/check_social_post_variation.py` → **PASS** (20 posts,
  2 brands, 2 surfaces, same-brand jaccard < 0.72, cross-brand < 0.90).
- `python3 scripts/ci/check_social_post_variation.py --inject-duplicates 3` →
  **FAIL as expected** (7 violations reported) — gate itself still catches
  real problems.
- Full-bank pairwise 3-gram-Jaccard scan restricted to the 68 new rows: 1
  near-duplicate found and fixed (see §4), 0 remaining.
- Full-bank scan of the 54 repaired `HOOK_COVER`-01 rows against their own
  `-02`/`-03` sibling variants (same persona+topic): 0 clashes.
- Hand-traced a fresh sample of 11 rows across all three categories
  (repaired hooks, dedup rewrites, new-family rows, spanning `entrepreneurs`,
  `gen_x_sandwich`, `corporate_managers`, `gen_z_professionals`,
  `healthcare_rns`): no doubled labels, no persona-slug leakage, no
  mail-merge fragments in any sampled row.
- All touched/added rows carry `review_status: draft_operator_review_required`
  — none self-marked `production_ready` or `reviewed_candidate`.

Note: running the gate required temporarily reading (not editing)
`phoenix_v4/social/deterministic_social.py` and five `config/` YAML files
that sit outside this worktree's sparse-checkout cone — these are the exact
files Lane E owns concurrently. They were read via `git show
origin/main:<path>`, used only to run the local CI check, and are untouched
in this branch's final diff (confirmed via `git status` before commit,
2 files only: the atom bank and this wave's build script).

---

## What this delta does NOT claim

- Not catalog-wide: `working_parents` remains at 22 rows (burnout-only, 9
  original families only) — fully untouched by this wave, same as Lane C
  left it.
- 18 more topics x 4 more personas (`corporate_managers`,
  `gen_z_professionals`, `healthcare_rns`, `working_parents`) still have zero
  rows in the 5 new families outside the original `anxiety`/`burnout` pilot
  cell.
- `corporate_managers`/`healthcare_rns` occurrences of the 8 dedup clusters
  in §4 remain byte-identical to each other (only the `gen_z_professionals`
  occurrence was rewritten).
- Not a claim of native/operator sign-off — every row is still
  `draft_operator_review_required`.
- Not a claim that the new-family rows are wired into the assembler —
  `phoenix_v4/social/deterministic_social.py` selection logic for
  `MICRO_STORY`/`CASE_PROOF`/`CAROUSEL_SLIDE`/`THREAD_UNIT`/`VIDEO_BEAT` was
  not inspected or modified this wave (Lane E's concurrent scope, a
  different worktree).
- The `EVG-ENUS-BURN-WKPR-HC-01` persona-address-style hook noticed in §1 is
  flagged, not fixed.
