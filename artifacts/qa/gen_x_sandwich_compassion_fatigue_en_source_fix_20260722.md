# gen_x_sandwich / compassion_fatigue — EN source defect fix (2026-07-22)

Closes the EN-source-authoring backlog items raised in
`artifacts/qa/zh_cn_wave1_shard_01_skips.md` (skips 3–6, PR #106) for:

- `atoms/gen_x_sandwich/compassion_fatigue/watcher/CANONICAL.txt`
- `atoms/gen_x_sandwich/compassion_fatigue/overwhelm/CANONICAL.txt`
- `atoms/gen_x_sandwich/compassion_fatigue/grief/CANONICAL.txt`
- `atoms/gen_x_sandwich/compassion_fatigue/INTEGRATION/CANONICAL.txt`

## Investigation

Confirmed both defect classes described in the shard-01 skip report are still
present on `origin/main` as of this fix:

1. **Orphan-body variants (watcher, overwhelm, grief).** The
   `RECOGNITION`/`MECHANISM_PROOF`/`TURNING_POINT`/`EMBODIMENT` v01/v03/v05
   blocks each have a real `## SHAPE vNN` header and real frontmatter
   (`path:`, `BAND:`, `SEMANTIC_FAMILY:`, `IDENTITY_STAGE:`), but the body was
   a bare orphan line naming the *next* variant (e.g. the v01 block's body was
   literally the text `RECOGNITION v02`) instead of authored prose. 10 of the
   ~22 variants per file had no translatable content. The `v06+`
   band_fill/capacity_fill variants later in each file were already real and
   translation-ready — untouched here.
   - Same orphan-body pattern reproduces (unfixed) in
     `atoms/millennial_women_professionals/compassion_fatigue/watcher/CANONICAL.txt`
     and its already-shipped `locales/zh-CN/CANONICAL.txt`, where the orphan
     text was carried through into the "translated" file verbatim rather than
     flagged — i.e. this defect class is systemic across personas, not unique
     to gen_x_sandwich. Flagging for a follow-up audit; out of scope for this
     fix, which is scoped to the 4 files blocking shard 01/PR #106.

2. **Duplicate header IDs (INTEGRATION only).** `## INTEGRATION v05`, `v06`,
   and `v07` each appeared twice: once as a mostly-empty legacy-schema stub
   (`integration_mode`/`reframe_type` frontmatter, v02/v04/v06 bodies fully
   empty) and again as fully-authored real content in a newer schema
   (`mode`/`reframe_type`/`weight`/`carry_line`). `structural_validator.py`'s
   `duplicate_header_ids` check fails unconditionally on this regardless of
   source vs. candidate parity, so no zh-CN candidate could ever pass.

## Fix

- watcher/overwhelm/grief: authored real 1–3 sentence body prose for all 10
  orphan-body variants per file, in-voice with the persona (gen_x
  "sandwich generation" caregiver) and matching each block's existing
  `path:` slug, `BAND`, `SEMANTIC_FAMILY`, and `IDENTITY_STAGE` — metadata
  left untouched, only the placeholder body text replaced.
- INTEGRATION: authored real bodies for the legacy schema's empty v02/v04/v06
  stubs (kept the `integration_mode`/`reframe_type` schema and mother/
  boundaries narrative thread already established by the surrounding v01/
  v03/v05/v07 blocks), then renumbered the newer-schema block from
  `v05–v25` to `v08–v28` to eliminate the ID collision. No prose was deleted;
  total variant count grew from 25 (with 3 duplicate IDs + 3 empty stubs) to
  28 unique, fully-authored variants.

Verified with `structural_validator.parse_blocks()` against all 4 files:
33/33/33/28 unique header IDs, zero duplicates, zero empty bodies, zero
orphan-line bodies remaining.

## Still open (not fixed here — flagging for follow-up)

- `ja-JP` and `zh-TW` locale mirrors of these 4 files structurally mirror the
  old (defective) EN source 1:1, including the INTEGRATION duplicate-ID
  layout and the orphan-body placeholder text (left untranslated in-place).
  They now need re-sync against the corrected EN source — INTEGRATION's
  renumbering plus new prose in all 4 files needs locale-native translation
  by `translate-ja` / `translate-zh-tw`. Not attempted here (outside EN-source
  scope and this session's language competence).
- The orphan-body defect class is systemic beyond gen_x_sandwich (see
  millennial_women_professionals example above); a full cross-persona sweep
  of `compassion_fatigue/{watcher,overwhelm,grief}` and sibling shapes using
  the same `SEMANTIC_FAMILY` schema is recommended as a separate backlog item.
