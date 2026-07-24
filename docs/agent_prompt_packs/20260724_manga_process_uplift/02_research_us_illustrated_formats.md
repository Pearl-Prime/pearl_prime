# EXECUTE — Lane 02 — Research: US illustrated self-help book formats

**AGENT:** Pearl_Research · **SUBSYSTEM:** manga_pipeline (US illustrated lane) · **WAVE:** 1

## EXECUTION CONTRACT (binding, in-band)
- EXECUTE end-to-end; turn ends only on the signal token or ONE concrete BLOCKER (evidence +
  pushed work + NEXT_ACTION). STARTUP_RECEIPT first; CLOSEOUT_RECEIPT last.
- Re-verify every premise live before acting; already-done = SUCCESS-reconcile (search
  `artifacts/research/` and open PRs for a US-illustrated format study first).
- DISCOVERY REPORT before writes. Reuse-first: this lane EXTENDS
  `artifacts/research/western_illustrated_styles_2026_04_04.md` and `docs/US_CATALOG_PLAN.md`;
  it does not fork a parallel strategy doc. New artifact carries `NEW-ARTIFACT-JUSTIFIED:
  dedicated US illustrated-self-help category study absent (confirmed 2026-07-24 inventory)`.
- Substrate: plumbing pattern off `origin/main^{tree}`; explicit paths; staged-diff gate;
  preflight (`push_guard.py` + `preflight_push.sh`) before push.
- Landing: MERGED (checks read + named) or BLOCKED. Cleanup ledger + handoff
  `artifacts/coordination/handoffs/manga_process_uplift_lane02_2026-07-24.md`.
- PROVENANCE: research=THIS LANE (creates it); documents=`docs/US_CATALOG_PLAN.md`;
  builds_on=`western_illustrated_styles_2026_04_04.md`, `us_illustrated_pilot_cells.yaml`;
  inventory=EXTENDS.

## READ FIRST
`docs/US_CATALOG_PLAN.md` (dual-path strategy — manga-aisle B&W vs mainstream self-help
illustrated), `artifacts/research/western_illustrated_styles_2026_04_04.md`,
`artifacts/qa/US_ILLUSTRATED_SELF_HELP_PILOT_2026-07-08.md`,
`config/manga/us_illustrated_pilot_cells.yaml`, `config/manga/western_cartoon_styles.yaml`,
`artifacts/research/popular_genre_ranking_2026-05-02.md` (sourcing style to match).

## MISSION
Produce the missing category study for **US-market illustrated self-help books** — the format
parameters for `direct_self_help_illustrated` are currently ASSERTED in config, not researched.
Web-research (WebSearch/WebFetch; cite every load-bearing claim with source + date) and deliver:

1. **Comp-title corpus (≥15 titles):** e.g. illustrated-trade self-help & adjacent (The Boy, the
   Mole…; Big Panda & Tiny Dragon; Everything Is F*cked-style illustrated editions; graphic-
   medicine crossovers; gift/inspiration category leaders). For each: page count, trim size,
   art:text ratio (estimate: full-page art / spot art / text-dominant), word count class, price
   band, B&W vs color, publisher category shelving.
2. **Format norms table:** typical page-count bands (gift 96–160? trade 192–256? — derive, don't
   assume), words-per-page bands, art density per page, chapter/section structure conventions.
3. **Market signal:** category sales evidence (Circana/BookScan public reporting, bestseller-list
   presence, publisher list activity), price/format correlation with sales rank where derivable.
4. **Recommendation block:** for each of the 5 pilot cells in `us_illustrated_pilot_cells.yaml`,
   recommended page count, art:text ratio, trim, color mode, words/page — with the comp evidence
   line-cited. Explicitly mark confidence per row (high/med/low).
5. **Config feed-through:** update `config/manga/us_illustrated_pilot_cells.yaml` (or its format
   sidecar if the schema demands one) with the researched parameters, marked
   `source: <research doc anchor>` — parameters flip from asserted → RESEARCHED. Update
   `docs/US_CATALOG_PLAN.md` with a dated §addendum pointing at the study (edit in place; no fork).

**Deliverable doc:** `artifacts/research/us_illustrated_self_help_format_study_2026-07-24.md`
(match the sourced-claim rigor of `popular_genre_ranking_2026-05-02.md`; confidence ratings per
section; sources footer).

## SMOKE → PILOT → SCALE
Smoke: 3 comp titles fully parameterized → sanity-check the table schema. Pilot: 8. Scale: ≥15 +
norms + recommendations. Checkpoint the doc after each stage (commit locally each stage so value
is never lost).

## WRITE SCOPE
`artifacts/research/us_illustrated_self_help_format_study_2026-07-24.md`,
`config/manga/us_illustrated_pilot_cells.yaml`, `docs/US_CATALOG_PLAN.md` (§addendum only),
handoff. **OUT OF SCOPE:** manga pacing yaml, craft bibles, series plans, any prose authoring.

## DO NOT
- Do not paste paywalled text; summarize with citation. Max one short quote per source.
- Do not let the illustrated lane inherit manga episode framing — it is a BOOK format (Q-MPU-03);
  flag any planning-contract implications for Lane 06 in your handoff instead of speccing them.
- Do not touch `manga_pacing_by_genre.yaml` (Lane 03's file).

## SIGNAL
`us-illustrated-format-research-merged=<full merge SHA>`
