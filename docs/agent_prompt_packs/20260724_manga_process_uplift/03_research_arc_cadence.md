# EXECUTE — Lane 03 — Research: per-genre arc cadence (empirical, sourced)

**AGENT:** Pearl_Research · **SUBSYSTEM:** manga_pipeline · **WAVE:** 1

## EXECUTION CONTRACT (binding, in-band)
- EXECUTE end-to-end; terminal = signal token or ONE BLOCKER (evidence + pushed work +
  NEXT_ACTION). STARTUP_RECEIPT / CLOSEOUT_RECEIPT bracket the work.
- Re-verify premises live; search `artifacts/research/` + open PRs for an existing arc-cadence
  study first — already-done = SUCCESS-reconcile.
- DISCOVERY REPORT before writes. Reuse-first: EXTENDS `manga_pacing_by_genre.yaml` (canonical,
  edit in place) and craft-bible §7 sections; does NOT create a parallel pacing registry.
- Substrate: plumbing pattern; explicit paths; staged-diff gate; preflight before push.
- Landing: MERGED (checks read + named) or BLOCKED. Cleanup ledger + handoff
  `artifacts/coordination/handoffs/manga_process_uplift_lane03_2026-07-24.md`.
- PROVENANCE: research=THIS LANE; documents=`docs/research/manga_craft/index.md` §7 table,
  `specs/ARC_AUTHORING_PLAYBOOK.md`; builds_on=`manga_pacing_by_genre.yaml` (canonical registry
  row `manga_pacing_by_genre` if present — verify), craft bibles; inventory=EXTENDS.

## READ FIRST
`config/manga/manga_pacing_by_genre.yaml` (structure: 22 genre families + alias map; your new
block must follow its conventions), `docs/research/manga_craft/index.md` (the §7 "48-Volume
Shape" summary table — the assertions you are grounding), 2–3 full bibles' §7 (e.g.
`webtoon_vertical_romance.md`, `seinen_psychological.md`, `iyashikei_minimalism.md`),
`artifacts/research/manga_genre_writing_styles_2026_04_04.md` (pacing chapters),
`docs/specs/MANGA_ARC_STORYBOARD_CONTRACT.md` (`genre_cadence` field — your output feeds it).

## MISSION
The craft bibles assert arc shapes per genre; no artifact grounds them in named-series evidence.
Produce the **empirical arc-cadence study**: for each of the ~22 pacing genre families, from ≥3
named successful series each (use each family's existing `reference_corpus[]` list first, top up
where thin), derive with citations (fan-wiki chapter/arc indexes, publisher volume breakdowns,
platform episode listings are acceptable sources — cite title + URL + access date):

1. **Arc length distribution:** typical episodes/chapters per major arc (min/median/max), and
   volume-boundary alignment (do arcs close at volume/season edges?).
2. **Cadence pattern:** fixed cadence vs escalating arc lengths vs seasonal cycles; mid-arc
   mini-climax spacing; cliff/hook placement relative to arc position.
3. **Serialization unit mapping:** print-volume genres (arc↔volumes) vs webtoon genres
   (arc↔episode-season, note ~25-ep season convention where confirmed).
4. **First-100-episodes shape:** for long-runners in the corpus, what actually happens across
   the first ~100 episodes/chapters (how many arcs, where the first major status-quo shift lands)
   — this directly parameterizes the Lane 06 100-episode master-plan contract.

**Deliverables:**
- `artifacts/research/manga_arc_cadence_study_2026-07-24.md` — per-family sections + a single
  roll-up table; confidence rating per family; sources footer.
- **`arc_cadence` block added to each family in `config/manga/manga_pacing_by_genre.yaml`:**
  `episodes_per_arc_range`, `arc_pattern` (fixed|escalating|seasonal_cycle), `season_unit`
  (episodes per season/volume where applicable), `first_major_shift_by` (episode number),
  `arc_cadence_confidence`, `arc_cadence_sources[]`. Keep YAML valid; do not disturb existing
  keys; run any pacing-yaml consumer tests you find (`grep -rl manga_pacing_by_genre tests/ scripts/`).
- **Craft-bible §7 corrections ONLY where research contradicts an assertion** — dated one-line
  correction with citation, never silent rewrites. List every correction in the closeout.
- Where a family's evidence is thin (<3 series), the block still lands with
  `arc_cadence_confidence: low` and a named follow-up in the handoff — no silent gaps.

## SMOKE → PILOT → SCALE
Smoke: 1 family (battle) end-to-end incl. YAML block + validation. Pilot: +4 (romance, healing,
workplace, webtoon-drama). Scale: all families. Commit at each checkpoint.

## WRITE SCOPE
`artifacts/research/manga_arc_cadence_study_2026-07-24.md`,
`config/manga/manga_pacing_by_genre.yaml`, craft-bible §7 correction lines, handoff.
**OUT OF SCOPE:** `manga_craft/index.md` (hot file — request the index correction via dispatcher
if the summary table needs it), arc-storyboard schema (Lane 06), any story authoring.

## DO NOT
- Do not invent numbers where sources are thin — mark low-confidence instead.
- Do not change `words_per_page_range`/existing pacing keys — additive block only.
- Do not touch the MDLG-08 deviation gate thresholds.

## SIGNAL
`manga-arc-cadence-research-merged=<full merge SHA>`
