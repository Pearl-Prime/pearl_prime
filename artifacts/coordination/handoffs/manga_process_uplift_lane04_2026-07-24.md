# Lane 04 Handoff — MC Endurance Research + Market Refresh (2026-07-24)

**Lane:** 04 of manga process uplift pack
(`docs/agent_prompt_packs/20260724_manga_process_uplift/04_research_mc_endurance_and_market_refresh.md`)
**Agent:** Pearl_Research · **PR:** #325 (`agent/manga-mc-endurance-research-20260724`)
**Signal (on merge):** `manga-mc-endurance-research-merged=<merge SHA>`

## Delivered

| Artifact | State |
|---|---|
| `artifacts/research/manga_mc_endurance_study_2026-07-24.md` | NEW — all 25 canonical families, ≥3 proven exemplars each, 5-section extraction, confidence-rated, sourced (2026-07-24 web pass + repo-pinned + [K] facts) |
| `config/manga/mc_endurance_checklists.yaml` | NEW — 25 families, 289 items, schema header, `status: unwired` (Lane 07 wires + flips) |
| Bible §5 dated addenda | 9 bibles: action_battle, dark_fantasy, iyashikei_minimalism, shojo_romance, workplace_drama, mecha, sci_fi_cyberpunk, psychological_thriller, josei_adult_memoir |
| `popular_genre_ranking_2026-05-02.md` | 2026 refresh addendum appended (Oricon 2026-H1, Circana 2026, AJPEA 2025, WBTN FY2025) — original untouched |
| `marketing_grounded_per_genre_allocation_2026-05-13.md` | 2026 refresh addendum + allocation-chain live confirmation appended |
| Registry row | `mc_endurance_checklists` in `CANONICAL_ARTIFACTS_REGISTRY.tsv` (NEW-ARTIFACT-JUSTIFIED) |
| `docs/research/manga_craft/index.md` | Cross-cutting research row (serialized behind Lane 05 per hot-file order) |

## Part B verdict (binding for this refresh)

**NO structural change** to `docs/GENRE_PORTFOLIO_PLAN.md` per-brand allocations from 2026
movement; **no Q-MPU-05 escalation.** Frieren/Apothecary 2026 performance *supports* the
healing-anchor bet; standing sports + fantasy_adventure underweight flags re-confirmed but
already on record (operator-tier). Allocation chain WIRED + LIVE (consumers named in the
allocation doc addendum; ja_JP fresh-plan spot check ≤5.8-pt deviation, explained by the
generator's documented blend weights).

## For Lane 07 (direct consumer)

- Key space = exactly the 25 `canonical_genre_list.yaml` ids =
  `story_excellence_gates.yaml::genre_core_evidence` keys. Stable; do not rename.
- Item schema: `{item, source}`; `source` anchors are
  `mc_endurance_study#<family>/<traits|endurance|bond|anti|wellness|exemplars>`.
- Flip `status: unwired` → wired in the same PR that adds the gate consumer.
- Per-family failure cadence is a genre signature (study §Cross-family synthesis item 2) —
  do NOT gate a global "MC must fail" rule.
- Completion-first families (essay, memoir, school, battle_internal, social_issue; single-run
  mecha/sci-fi) must not be gated for 100+ episode shapes (synthesis item 3).

## Findings / follow-ups (not actioned here)

1. **Untracked-authority gap:** `docs/research/manga_craft/main_character_interaction_grammar_by_genre.md`,
   `comedy_gag.md`, and `story_quality_gap_audit_modern_reader_worlds.md` exist in the shared
   checkout but are NOT on origin/main (same class as the known catalog tracked-vs-untracked
   gap). Lane 05's PR #323 lands `comedy.md` (index row 24, absorbed from #295), which
   supersedes the untracked `comedy_gag.md`; a follow-up should add the comedy endurance
   exemplars to that bible's §5 (Ryotsu/Kochikame 200 vols, Gintoki, Saiki — study §comedy
   has the full text). Same applies to the other Lane-05-landed bibles for families covered
   by this study (slice_of_life, food, family, procedural, essay, graphic_medicine,
   battle_internal, social_issue) — study §-sections are ready to cite. The
   interaction-grammar doc still needs a landing owner.
2. **Romance webtoon share correction:** the 39.4% figure in the 2025-era docs reads as a
   platform-specific share; cross-market 2025 romance share is ≈27.4% (#1 rank unchanged).
   Noted in the allocation addendum; no table rewrite performed (append-only rule).
3. **Locale-plan conformance knob:** if a future lane wants locale-exact allocation
   conformance in generated plans, the lever is `generate_catalog_plan_from_strategic.py`'s
   M2 70/30 blend + `DISTRIBUTION_WEIGHTS`, not the allocation YAML — operator-tier.

## Cleanup ledger

- Scratchpad work dir `…/scratchpad/lane04/` (session-local, auto-cleaned; nothing left in
  the shared checkout).
- No worktrees created; no branch switches; shared checkout untouched (plumbing commits via
  temp index off `origin/main^{tree}`).
- Temp refs: none beyond the lane branch. Old pre-re-root commit objects
  (668f1808e1, 11dc3898c5, eb88b9fd5c) are unreferenced and will GC.
- Branch `agent/manga-mc-endurance-research-20260724` — delete after merge.

## NEXT_ACTION

Lane 07 gate-check passes once BOTH `manga-mc-endurance-research-merged` +
`manga-craft-bibles-complete` signals exist. Lane 07 consumes the checklist YAML per the
schema header; this handoff's §For Lane 07 lists the binding constraints.
