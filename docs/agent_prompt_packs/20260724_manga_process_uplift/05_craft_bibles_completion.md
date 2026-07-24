# EXECUTE — Lane 05 — Craft-bible completion: 3 stubs + wave-2 drawing-tradition backfill

**AGENT:** Pearl_Writer (Tier-1 Claude) · **SUBSYSTEM:** manga_pipeline · **WAVE:** 1.5

## EXECUTION CONTRACT (binding, in-band)
- EXECUTE end-to-end; terminal = signal token or ONE BLOCKER (evidence + pushed work +
  NEXT_ACTION). STARTUP_RECEIPT / CLOSEOUT_RECEIPT bracket the work.
- Re-verify premises live: PR #295 state (must still be unmerged per Q-MPU-02; if a sibling
  merged or closed it, STOP and reconcile with the dispatcher first) + PR search "craft bible" —
  if a sibling already filled a stub or landed wave-2 items, SUCCESS-reconcile, never re-author.
- DISCOVERY REPORT before writes. Reuse-first: bibles are canonical singletons — edit in place to
  the standard 10-section schema; SHA/line-pin §10 references to real research files.
- Substrate: plumbing pattern; explicit paths; staged-diff gate; preflight before push.
- **Hot-file order:** you are FIRST in the `docs/research/manga_craft/index.md` serial chain
  (05 → 04 → 07). Re-read index.md immediately before editing; after editing, grep for duplicate
  entry numbers (this exact collision happened 2026-07-24 with 5 concurrent agents).
- Landing: MERGED (checks read + named) or BLOCKED. Cleanup ledger + handoff
  `artifacts/coordination/handoffs/manga_process_uplift_lane05_2026-07-24.md`.
- PROVENANCE: research=`manga_genre_writing_styles_2026_04_04.md`, `manga_pacing_by_genre.yaml`
  reference corpora, genre_bestseller_dossiers; documents=`manga_craft/index.md` schema;
  builds_on=the 26 full bibles (format-match them); inventory=EXTENDS.

## READ FIRST
`docs/research/manga_craft/index.md` (10-section schema + summary tables), one strong full bible
as format template (`supernatural_mystery.md`), the 3 stubs (`isekai.md`,
`psychological_horror.md`, `school_coming_of_age.md`),
`docs/specs/MANGA_DRAWING_TRADITION_WAVE2_REIMPLEMENTATION_SPEC_20260721.md` (all 234 lines),
`artifacts/coordination/handoffs/session_cleanup_r2_manga_spec_handoff_2026-07-21.md` (item 3
landed `aad5cf2152`; items 1/2/4 open), `config/manga/genre_prompt_cookbook.yaml` +
`artifacts/research/per_genre_drawing_tradition_corpus_2026-05-02.yaml` (tradition source).

## MISSION
0. **Absorb PR #295's 10 craft bibles (operator ruling Q-MPU-02 = REWORK, 2026-07-24 — #295 is
   NEVER merged).** Fetch branch `claude/manga-12ep-arc-authoring-egnwqf` read-only; take its 11
   `docs/research/manga_craft/` files (10 bibles + index rows), verify each against the
   10-section structural bar, adapt where needed, and land them via THIS lane's PR with a
   source-credit line ("absorbed from #295 branch, reworked per Q-MPU-02"). If any bible
   duplicates one already on live main, reconcile (newer/deeper wins; state the choice). The
   #295 arc plans are NOT yours — Lane 06 absorbs those. Do not close #295 (dispatcher does,
   after both lanes' signals exist).
1. **Expand the 3 stub bibles** (~2 KB each) to the full 10-section schema (§1 Market Contract …
   §10 References) at the depth of the 26 full bibles (8–17 KB): market contract with named comps,
   quantified visual grammar (panels/page, words/page, silent-panel %, fill ratios), pacing,
   dialogue, character (feed Lane 04's exemplars if already merged — check the signal; otherwise
   note "MC exemplars pending Lane 04"), failure modes, 48-volume shape (+ note that Lane 03's
   `arc_cadence` block is the quantitative authority once merged), panel scaffolding fields,
   locale weighting, SHA-pinned references. Ground isekai in
   `manga_genre_writing_styles_2026_04_04.md` §Isekai; psychological_horror in the horror +
   seinen-psych chapters + horror dossier; school_coming_of_age in the school family pacing entry.
2. **Wave-2 re-implementation, open items 1/2/4** of
   `MANGA_DRAWING_TRADITION_WAVE2_REIMPLEMENTATION_SPEC_20260721.md` (item 3 already landed as
   `aad5cf2152` — do not redo): item 1 = upgrade the 6 `deferred_phase2` genres (mystery,
   supernatural_everyday, workplace, battle, sci_fi_cyberpunk, sports) to deep drawing-tradition
   blocks per the spec's field contract; items 2/4 per the spec text (re-read; the spec is the
   authority on their exact scope). Verify each item against live main first — the spec exists
   BECAUSE a prior session falsely reported this work done; byte-verify, then author.
3. **index.md update** (serialized, per contract): add/repair rows for the 3 expanded bibles;
   sequential numbering, zero duplicates, verified by grep.

## QUALITY BAR
Each expanded bible must pass the same structural check as the existing set: all 10 sections
present, quantified §2 (numbers, not adjectives), §10 pinned to real files (verify paths exist).
Run `python3 - <<'EOF'` structural self-check (sections present + min length) and paste results
in the closeout. Layer-honest label: RESEARCHED/SPECCED (these are research-craft docs, not code).

## SMOKE → PILOT → SCALE
Smoke: 1 stub (school_coming_of_age) fully expanded → self-check. Then the other 2. Then wave-2
items 1/2/4 as a second commit (or second PR if the first is large).

## WRITE SCOPE
`docs/research/manga_craft/{isekai,psychological_horror,school_coming_of_age}.md`, the 10
absorbed #295 bibles under `docs/research/manga_craft/`,
`docs/research/manga_craft/index.md` (serialized), wave-2 target files per the spec (expected:
`config/manga/genre_prompt_cookbook.yaml` tradition blocks / tradition corpus yaml — confirm from
the spec §item-1 contract), handoff. **OUT OF SCOPE:** the 26 full bibles (except nothing),
pacing yaml (Lane 03), mc checklists (Lane 04), story scripts.

## DO NOT
- Do not report a bible "done" on file-existence — the structural check is the bar.
- Do not weaken `check_manga_wiring.py` if a wave-2 config edit trips it — fix the consumer or
  the KNOWN_UNWIRED entry honestly.
- Qwen is never used for this lane's prose (Tier-1 policy; operator-reviewed craft docs).

## SIGNAL
`manga-craft-bibles-complete=<full merge SHA>` (last PR if split; list all SHAs in closeout).
