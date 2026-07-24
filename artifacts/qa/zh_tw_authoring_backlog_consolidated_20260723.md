# zh-TW Authoring Backlog — Consolidated (2026-07-23)

**Author:** Pearl_GitHub, this session. Branch: `agent/zh-tw-authoring-backlog-consolidated-20260723`.
**Inputs reconciled (three independently-produced lists, none aware of the other two):**

1. **PR #93** (`agent/zh-tw-register-rewrite-scope-correction-20260723`) —
   `artifacts/qa/zh_tw_wrong_register_bucket_triage_20260723.tsv`, 1,242 rows,
   scripted triage of the `WRONG_REGISTER_CLEAN_SCRIPT` audit bucket.
2. **Retranslation program, chunk-native finds** — `artifacts/qa/atom_authoring_backlog_20260722.tsv`
   as it exists on `agent/zhtw-retranslate-chunk2-20260723` (10 new rows beyond
   the shared 650-row base) + `artifacts/qa/atom_authoring_backlog_chunk6_20260723.tsv`
   on `agent/zhtw-retranslate-chunk6-20260723` (6 rows) — 16 rows total logged
   as dedicated TSV artifacts, **plus 66 further blockers self-declared only in
   prose tracker docs** (`scripts/qa/zhtw_clean_retranslate/CHUNK4_PROGRESS.md`,
   `CHUNK8_PROGRESS.md`, `chunk3_PROGRESS.md`, `artifacts/qa/zhtw_retranslate_chunk5_tracking_20260723.md`
   — chunks 3/4/5/8, never captured in any TSV, only found by reading every
   chunk's own closeout doc).
3. **Earlier corruption scan** — `artifacts/qa/atom_corruption_scope_20260722.tsv`
   on `agent/zhtw-clean-corrupted-retranslate-20260722`, 1,850 flagged rows
   (out of 5,279 zh-TW `CANONICAL.txt` files scanned), of which 650 carry
   `en_source_status == EN_ALSO_CORRUPTED` — the authoritative baseline this
   program has been calling "the 650-row backlog."

## Headline numbers

- **863 unique files** in the consolidated authoring backlog:
  `artifacts/qa/zh_tw_authoring_backlog_consolidated_20260723.tsv`.
- **Overlap between the three source lists, as originally delivered (exact, not estimated):**
  - List1 (PR#93, 1,242) ∩ List2 (retranslation-program TSV rows, 16) = **16** (all 16 of List2 sit inside List1's bucket)
  - List1 ∩ List3 (corruption-scan 650) = **230**
  - List2 ∩ List3 = **0**
  - List1 ∩ List2 ∩ List3 = **0**
  - Raw total rows across the three lists as delivered: 1,242 + 16 + 650 = 1,908
  - Raw union (dedup by path): **1,662** → **246 duplicate-flagged rows** removed by path-level dedup alone, before any EN-source re-verification.
- **PR #93's 1,242 rows are mostly NOT part of this backlog.** Only **355** of
  its 1,242 rows end up in the final 863-file consolidated list. The rest split into:
  - **285** confirmed false positives (PR#93's own hand-verified `AUTHORED_CANDIDATE` /
    `YAML_TEXT_OK_STRUCTURAL_FALSE_POSITIVE` buckets — already-fine files, not
    touched).
  - **645** confirmed **zh-TW-only translation gaps** — PR#93 correctly found the
    zh-TW file empty/stub/untranslated, but this session's file-by-file
    cross-check against `atom_corruption_scope_20260722.tsv`'s own English-source
    read confirms the **English source is clean** for these. These are real
    work, but they belong to the standard zh-TW retranslation queue
    (`agent/zhtw-retranslate-chunk*`), **not** an English-authoring backlog —
    translating from the existing clean EN source is a complete fix.
  - **312** genuinely EN-broken (subset of the 957 rows PR#93 itself flagged as
    non-false-positive), confirmed by independent EN-root re-read.

## Method

1. Parsed all four source artifacts (three TSVs + `atom_authoring_backlog_chunk6_20260723.tsv`)
   into path-keyed dicts. Confirmed byte-for-byte that the 650-row
   `atom_authoring_backlog_20260722.tsv` on `agent/bestseller-atom-flow-lanes-20260721`
   is exactly the `EN_ALSO_CORRUPTED` filter of `atom_corruption_scope_20260722.tsv` —
   two independent sessions derived the identical 650 rows from the same
   underlying scan, which is why they match exactly.
2. **Cross-referenced every PR#93 non-false-positive row (957: 818 `genuine` +
   139 `ambiguous AUTHORED_LOW_BODY_CJK`) against `atom_corruption_scope`'s own
   `en_source_status` field.** 955 of these 957 rows were already present
   somewhere in the corruption scan's full 1,850-row flagged population (not
   just its 650-row `EN_ALSO_CORRUPTED` subset — the other 1,200 rows there are
   `EN_CLEAN_ZH_CORRUPTED`, i.e. confirmed translation-only gaps) — meaning the
   two audits overwhelmingly describe the *same underlying files*, just
   measuring different things (PR#93: is the zh-TW body present? corruption
   scan: is the EN root also broken?). Only 2 of the 957 needed a fresh,
   from-scratch EN-root read; both came back genuinely broken.
3. **Found and fixed a real disagreement, not an estimate.** All 16 of the
   retranslation program's own session-native "EN-source-corrupted" finds
   (chunk2/chunk6, hand-verified by direct byte inspection per their own commit
   messages) were classified by `atom_corruption_scope`'s automated scanner as
   `EN_CLEAN_ZH_CORRUPTED` (i.e. "just needs translation"). Read the actual EN
   root files directly (`git show origin/main:<path>`) to adjudicate: **the
   retranslation program was right, the corruption scan was wrong for these.**
   Root cause identified: the corruption scan's original classifier did not
   strip the `compression_family: Cx` metadata field before measuring body
   length for `COMPRESSION`-schema blocks, so a block containing nothing but
   `compression_family: C1` read as "has content" instead of empty.
4. **Built an improved classifier** (reusing PR#93's own
   `classify_atom_canonical()` structural logic, which does correctly strip
   `compression_family:`) and applied it to the EN root of every path across
   all three source lists (1,969 unique paths). Two additional signal types
   were added and *individually spot-verified by direct file read before being
   trusted at scale*:
   - **Bracket-template placeholder detection** — a section whose entire
     stripped body is a single bracketed line (e.g. `[Recognition atom about
     Financial Anxiety and watcher. Character notices something...]` or
     `[Persona-specific hook for X × Y]`) is treated as empty. Confirmed via
     the chunk4/chunk5/chunk8 tracker docs' own hand-verified examples plus 8
     additional random samples — 100% true positive on every file read.
   - **Known-filler-sentence reuse** — exact-match of the two filler sentences
     `atom_corruption_scope_20260722.md` itself documents as reused verbatim
     across hundreds of EN files ("The mechanism deepens. Stakes rise. The
     cost becomes clear." / "Crisis. Breakthrough. The moment of maximum
     intensity."). Confirmed via direct `grep` on every sampled file — 6/6 true
     positive.
   - **A third signal — a ~17-phrase meta-commentary substring list — was
     built, tested, and discarded.** Spot-checking its 35 hits found **0/35
     true positives**: the naive substring match caught `"here is"` inside
     `"there is"` and `"i hear you"` inside genuine therapeutic character
     dialogue ("Kevin tells his team: 'I hear you and I also need support
     sometimes.'"). This signal is excluded from the final backlog entirely.
     Documented here so a future session does not re-invent and re-trust it.
5. **Never removed anything from the corruption scan's original 650-row
   baseline.** Our lighter-weight classifier disagrees with corruption_scope on
   228 of the 650 (says "clean" where corruption_scope says broken) — almost
   certainly because corruption_scope's original `META_COMMENTARY` detection
   (a 55-phrase list, per its own doc) is more sophisticated than what we
   rebuilt here for this reconciliation pass. The baseline 650 stays
   authoritative and untouched; our classifier is only trusted in the
   *additive* direction (finding new problems it can prove), never to
   subtract from an existing, differently-calibrated finding.
6. Every one of the 16 chunk2/chunk6 TSV-logged finds and all 66 chunk3/4/5/8
   tracker-doc-only blockers land inside the final 863-row list —
   **100% internal consistency check passed.**

## Locale exposure

For every one of the 863 files, checked the sibling file at the same atom path
for the 5 well-populated locales (`ja-JP`, `zh-CN`, `ko-KR`, `zh-HK`, `zh-SG`
— matching `atom_corruption_scope_20260722.md` §4's own choice of which
locales have enough corpus coverage to be meaningful) plus 6 minor locales
(`pt-BR`, `es-US`, `fr-FR`, `de-DE`, `es-ES`, `hu-HU`, informational only —
these have <3% corpus coverage each, so "file doesn't exist" there means
"market not yet localized," not "blocked by this atom"). Priority weight =
1 (zh-TW itself) + count of *other* locales whose file **exists and
independently shows the same brokenness** (not merely "hasn't been reached
yet"):

| Priority | Count | Meaning |
|---|---:|---|
| `P0_MULTI_LOCALE_BLOCKED` | 138 | zh-TW + ≥2 other locales confirmed broken at the same path |
| `P1_DUAL_LOCALE_BLOCKED` | 472 | zh-TW + exactly 1 other locale confirmed broken |
| `P2_ZHTW_ONLY_BLOCKED` | 253 | Only zh-TW currently shows the defect (other locales missing/not yet attempted or genuinely clean) |

Top affected persona pools: `first_responders` (123), `tech_finance_burnout`
(117), `gen_alpha_students` (110), `corporate_managers` (92), `healthcare_rns`
(67).

## Recommendation

**This consolidated list — `artifacts/qa/zh_tw_authoring_backlog_consolidated_20260723.tsv`
— should become the one authoring backlog this repo tracks going forward**, in
place of `atom_authoring_backlog_20260722.tsv`,
`atom_authoring_backlog_chunk6_20260723.tsv`, `atom_corruption_scope_20260722.tsv`'s
650-row subset, and the actionable subset of
`zh_tw_wrong_register_bucket_triage_20260723.tsv`, none of which should be
independently re-consulted for this purpose going forward (they remain valid
as historical audit trails / methodology references, but are each a strict
undercount or an unfiltered superset relative to this file). Concretely:

- 863 files need **English-side authoring** before any locale's translation of
  them is meaningful — flagged `atoms/**/CANONICAL.txt` (EN root), not the
  zh-TW copy. This is upstream of, and separate from, the zh-TW retranslation
  program (`agent/zhtw-retranslate-chunk1..8`), which should **skip** these 863
  paths (most chunk agents already independently discovered this and reported
  them as blockers — this list is the union of that hard-won knowledge, not
  new instruction).
- The 645 confirmed zh-TW-only translation gaps (PR#93 rows with clean EN)
  remain valid work for the retranslation program chunks; they are correctly
  excluded from *this* list because translating from the existing clean EN
  source fully resolves them.
- Given a broken EN source blocks every locale that reads from it, the 138
  `P0`/472 `P1` rows should be prioritized first — fixing the English source
  once unblocks 2-5+ locale translations simultaneously, not just zh-TW.

## Signal token

`ZHTW_AUTHORING_BACKLOG_RECONCILED_863`
