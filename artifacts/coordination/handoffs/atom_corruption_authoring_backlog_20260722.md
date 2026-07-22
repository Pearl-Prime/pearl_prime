# Handoff — Atom Authoring Backlog (English-source corpus defect, 2026-07-22)

STARTUP_RECEIPT:
- AGENT=Pearl_QA (running as Claude Sonnet 5 in this session)
- LANE=atom-authoring-backlog (Prompt 2, follow-on to Prompt 1's
  `artifacts/qa/atom_corruption_scope_20260722.{tsv,md}`)
- STATUS=INVESTIGATION COMPLETE — read-only against `atoms/**`, no content
  authored or fixed in this lane.

## What this is

Prompt 1 scanned all 5,279 `atoms/**/locales/zh-TW/CANONICAL.txt` files and
found 1,850 corrupted, of which **650 have an equally corrupted or empty
English source** (`en_source_status == EN_ALSO_CORRUPTED`). This is upstream
of translation entirely — the English atom itself was never authored (or was
overwritten with LLM chat leakage), so no amount of re-translating zh-TW
fixes it, and every locale sourced from these 650 atoms either has no real
content or will inherit the same corruption once translated.

This lane turns that 650-row subset into a clean, prioritized authoring
backlog: `artifacts/qa/atom_authoring_backlog_20260722.tsv` (650 rows + header).

**No English content was authored, rewritten, or fixed in this lane.** That is
explicitly out of scope — it belongs to Pearl_Writer (operator-reviewed prose
authoring), not QA/localization. This lane only diagnoses and prioritizes.

## Scope re-verified

Re-filtered `artifacts/qa/atom_corruption_scope_20260722.tsv` for
`en_source_status == EN_ALSO_CORRUPTED`: **650 rows**, confirmed matching
Prompt 1's reported figure. Breakdown by `defect_class`:

| defect_class | count | % of 650 |
|---|---:|---:|
| EMPTY_STUB | 490 | 75.4% |
| META_COMMENTARY | 101 | 15.5% |
| UNTRANSLATED_ENGLISH | 45 | 6.9% |
| UNCLEAR_MIXED | 14 | 2.2% |

## Sample verification (method + honest confidence)

Hand-read the actual English `CANONICAL.txt` for ~15 files sampled across all
four defect classes (systematic stride sampling within each class, not
random — every Nth row by class, small classes read in full or near-full:
6/490 EMPTY_STUB, 5/101 META_COMMENTARY, 6/45 UNTRANSLATED_ENGLISH, 6/14
UNCLEAR_MIXED considered). This is **not** a statistically powered sample of
650; treat the confidence levels below as directional, not exhaustive.

- **EMPTY_STUB — HIGH confidence, genuinely TRULY_EMPTY.** Every sample
  showed the same systemic pattern: odd-numbered variant slots (`v01`, `v03`,
  `v05`) carry a full metadata header (`path:`, `BAND:`, `SEMANTIC_FAMILY:`,
  `IDENTITY_STAGE:`) followed by **zero body text**, and the even-numbered
  slot that should follow (`v02`, `v04`) appears as an orphaned bare label
  with no `##` header and no metadata at all — e.g.
  `atoms/first_responders/financial_anxiety/spiral/CANONICAL.txt`,
  `atoms/educators/burnout/watcher/CANONICAL.txt`,
  `atoms/healthcare_rns/imposter_syndrome/shame/CANONICAL.txt`. Some files in
  this class also carry a literal placeholder string,
  `[Integration content for <persona> × <topic>]`
  (e.g. `atoms/healthcare_rns/financial_anxiety/INTEGRATION/CANONICAL.txt`).
  This is unambiguous: nobody wrote this content. Confirmed genuinely unusable
  — not just short or differently formatted.

- **META_COMMENTARY — MEDIUM confidence, mixed.** Two distinct sub-patterns
  found, both worth flagging separately before dispatch:
  1. Confirmed genuine raw chat-completion leakage on the **zh-TW** side (the
     mega-commit contamination Prompt 1 already root-caused) — but in at
     least one sampled case
     (`atoms/corporate_managers/anchored/anxiety_false_alarm/CANONICAL.txt`),
     the **English source itself is fully clean, well-authored content**
     (RECOGNITION → MECHANISM_PROOF → TURNING_POINT → EMBODIMENT, all
     variants present and coherent). This looks like a **false positive** in
     the `en_source_status` classification for this row — flagged in the
     backlog for a second look, not treated as confirmed-corrupted.
  2. A recurring **templated/duplicate-label pattern** in `REFLECTION`-type
     atoms across multiple unrelated persona pools (confirmed in
     `atoms/nyc_executives/compassion_fatigue/REFLECTION/CANONICAL.txt` and
     `atoms/gen_alpha_students/compassion_fatigue/REFLECTION/CANONICAL.txt`):
     a second write-pass reuses variant labels already used earlier in the
     same file (e.g. `## REFLECTION v16` appears twice) and fills them with a
     near-identical paragraph template, swapping only a trigger noun-phrase
     per persona (`"before the board"` / `"before the exam"` /
     `"the quarter close"`). This is a genuine authoring-quality defect
     (mechanical slot-substitution, not distinct authored voice) but it is
     **not** raw LLM refusal/chat junk in the way META_COMMENTARY's name
     implies — it reads as legitimate-looking prose on a skim. Recommend this
     sub-pattern get a dedicated pass rather than being bundled with clear-cut
     chat-leakage files.

- **UNTRANSLATED_ENGLISH — MEDIUM-HIGH confidence.** Samples showed the same
  empty-block signature as EMPTY_STUB co-occurring in the same file
  (`atoms/educators/burnout/watcher/CANONICAL.txt`), consistent with the
  scanner's documented overlap-priority rule (META > EMPTY > UNTRANSLATED >
  UNCLEAR) picking a different dominant label for files with mixed defects.
  Practically: treat as real authoring gaps.

- **UNCLEAR_MIXED — LOW confidence, by design.** Prompt 1's own doc already
  flags this bucket as not cleanly resolved. Carried into the backlog as
  `P3_NEEDS_REVIEW`, not prioritized by locale count.

**No MISFILED cases found** in the sample — no instance where content existed
at a nearby/differently-named path instead of being genuinely missing.

## Other-locale cross-reference (who's waiting on each English fix)

Using Prompt 1's `other_locales_affected` column (checked for the full 1,850,
not re-derived here):

| priority | rows | meaning |
|---|---:|---|
| P0_MULTI_LOCALE_BLOCKED | 31 | ja-JP **and** zh-CN both show the same corruption at this path — fixing English unblocks 3 locales at once (en, ja-JP, zh-CN, plus zh-TW translation) |
| P1_ONE_LOCALE_BLOCKED | 172 | one other locale (ja-JP or zh-CN) independently shows the same corruption at this path |
| P2_ZHTW_ONLY | 433 | no other-locale file exists at this path yet, or the other-locale file that exists looks clean (`PRESENT_CLEAN`) — fixing English still matters for zh-TW + future locale expansion, just not blocking an already-corrupted sibling today |
| P3_NEEDS_REVIEW | 14 | `UNCLEAR_MIXED` — defect itself not cleanly established, review before prioritizing |

203 of 650 rows (31%) have at least one other locale independently blocked on
the same English fix (P0+P1) — this is the subset where fixing English pays
off across the whole multi-locale program immediately, not just zh-TW.
ko-KR/zh-HK/zh-SG are not named as waiting on any row here because Prompt 1
found too little file coverage at these paths (2-8%) to confirm the pattern
for those locales either way — absence from the backlog is a coverage gap,
not a clean bill of health.

## Root cause (from Prompt 1 — not re-derived here)

Traced by git blame to three incidents, ~2 months apart:
1. **`85cd624e95`** (PR #500, 2026-04-20) — unreviewed 4,667-file backup/sync
   commit landed raw LLM chat-completion text directly into `CANONICAL.txt`
   paths.
2. **`d2d79c4e93`** (2026-04-24) — an owner-override "recover CJK
   translations" commit self-reported ~100% coverage but left 69% of its own
   touched files untranslated or empty, with no validation gate catching the
   shortfall before merge.
3. **`0d1cf1520d` + `0ac28088fc`** (PRs #1590/#1623, 2026-06-15) — a header-
   repair script explicitly labeled "do-NOT-merge" in its own commit subject
   was merged anyway, over-matched and corrupted bodies, and the same-day
   "restore" left every one of its touched files empty rather than actually
   recovering content.

These four commits account for 1,827/1,850 (98.8%) of the full flagged
population; the 650-row `EN_ALSO_CORRUPTED` subset in this backlog inherits
that same attribution (see `origin_commit` column).

## Persona pools most affected (top 10 by row count in the backlog)

`first_responders` (121), `gen_alpha_students` (96), `corporate_managers`
(78), `gen_x_sandwich` (57), `tech_finance_burnout` (52), `entrepreneurs`
(51), `working_parents` (40), `millennial_women_professionals` (39),
`gen_z_professionals` (39), `healthcare_rns` (37).

## Recommendation — track as its own initiative, separate from zh-TW translation

**This is a corpus-wide content-integrity gap, not a zh-TW translation
defect, and should not be folded into the zh-TW translation program's PR or
branch.** Rationale:

- It affects the English atom bank directly — the same 650 gaps will surface
  in every current and future locale sourced from these atoms (§ above: 203
  already confirmed waiting in ja-JP/zh-CN).
- The fix is **authoring**, not translation. A translator (human or Qwen)
  re-running against an empty stub or a chat-leakage file ships the same
  emptiness or junk in the target language — Prompt 1 already demonstrated
  this is exactly what happened in commit `d2d79c4e93`.
- Ownership: **Pearl_Writer** (operator-reviewed English prose authoring),
  working from `artifacts/qa/atom_authoring_backlog_20260722.tsv` as the
  queue. Not Pearl_QA/localization (this lane), not any `translate-*` agent.
  Per repo convention (`docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md`, Cursor/
  Claude split doc), this is Claude-authored prose work requiring operator
  review before it ships — the same discipline as
  `atom-authoring-queue_2026-07-21.md`'s single-cell authoring pass, scaled
  to a backlog.
- Suggested sequencing: start with the 31 `P0_MULTI_LOCALE_BLOCKED` rows
  (fixes 3+ locales per atom authored), then the 172 `P1` rows, review the 14
  `P3_NEEDS_REVIEW` rows by hand before queuing them, and treat the 433 `P2`
  rows as the long tail. Re-run Prompt 1's scanner after any authoring wave
  to confirm the fix actually resolved the flagged block (not just silenced
  the phrase-match heuristic).

## Deliverables

- `artifacts/qa/atom_authoring_backlog_20260722.tsv` — 650 rows + header.
  Columns: `path, persona_pool, topic, atom_label, defect_class, priority,
  locales_waiting_on_en_fix, other_locale_signal, origin_commit`.
- This handoff.

## CLOSEOUT_RECEIPT

- Backlog: `artifacts/qa/atom_authoring_backlog_20260722.tsv`, 650 rows.
  By defect type: EMPTY_STUB 490, META_COMMENTARY 101, UNTRANSLATED_ENGLISH
  45, UNCLEAR_MIXED 14. By priority: P0_MULTI_LOCALE_BLOCKED 31,
  P1_ONE_LOCALE_BLOCKED 172, P2_ZHTW_ONLY 433, P3_NEEDS_REVIEW 14.
- Locales affected (named): ja-JP and/or zh-CN independently corrupted at the
  same path for 203/650 rows (P0+P1). ko-KR/zh-HK/zh-SG not confirmed either
  way — insufficient file coverage at these paths per Prompt 1.
- Handoff doc: `artifacts/coordination/handoffs/atom_corruption_authoring_backlog_20260722.md`
  (this file).
- Recommendation: track as a **separate initiative from the zh-TW translation
  program**, owned by **Pearl_Writer** (operator-reviewed English authoring),
  queued from the backlog TSV, sequenced P0 → P1 → P3 (reviewed) → P2.
- No files under `atoms/**` were read-modified; this lane is output-only
  against `artifacts/`.

Signal token: `ATOM_AUTHORING_BACKLOG_LOGGED_650`
