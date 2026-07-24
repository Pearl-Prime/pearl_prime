# EXECUTE — Lane 04 — Research: enduring main characters per genre + market-data currency refresh

**AGENT:** Pearl_Research · **SUBSYSTEM:** manga_pipeline · **WAVE:** 1

## EXECUTION CONTRACT (binding, in-band)
- EXECUTE end-to-end; terminal = signal token or ONE BLOCKER (evidence + pushed work +
  NEXT_ACTION). STARTUP_RECEIPT / CLOSEOUT_RECEIPT bracket the work.
- Re-verify premises live; check the `agent/manga-research-currency-verify` branch lineage and
  `artifacts/qa/manga_research_currency_audit_2026-07-22.md` before starting part B — if a
  sibling already refreshed the rankings, reconcile and skip that part.
- DISCOVERY REPORT before writes. Reuse-first: EXTENDS bible §5 sections,
  `main_character_interaction_grammar_by_genre.md`, `popular_genre_ranking_2026-05-02.md` —
  edit-in-place addenda, no parallel docs.
- Substrate: plumbing pattern; explicit paths; staged-diff gate; preflight before push.
- **Hot-file order:** `docs/research/manga_craft/index.md` is serialized 05 → 04 → 07 (INDEX
  hot-file map). Do not edit index.md until the dispatcher confirms Lane 05's index commit is on
  main; re-read it immediately before your edit and grep for duplicate numbering after (known
  prior collision class).
- Landing: MERGED (checks read + named) or BLOCKED. Cleanup ledger + handoff
  `artifacts/coordination/handoffs/manga_process_uplift_lane04_2026-07-24.md`.
- PROVENANCE: research=THIS LANE; documents=`GENRE_PORTFOLIO_PLAN.md`, manga_craft bibles;
  builds_on=`popular_genre_ranking_2026-05-02.md`,
  `marketing_grounded_per_genre_allocation_2026-05-13.md`,
  `main_character_interaction_grammar_by_genre.md`; inventory=EXTENDS.

## READ FIRST
`docs/research/manga_craft/main_character_interaction_grammar_by_genre.md`, 3 bibles' §5
(protagonist sections), `artifacts/research/popular_genre_ranking_2026-05-02.md`,
`artifacts/research/marketing_grounded_per_genre_allocation_2026-05-13.md`,
`docs/GENRE_PORTFOLIO_PLAN.md` (per-brand allocation), `config/manga/brand_genre_allocation.yaml`
consumers (`grep -rl brand_genre_allocation scripts/ phoenix_v4/`).

## MISSION — PART A: enduring-protagonist study (the operator's ask, currently distributed/thin)
For each canonical genre family: who are the genre's most enduring/beloved main characters
(≥3 named exemplars from commercially proven series), and WHY — extract with citations:
1. **Trait architecture:** core want vs need, competence/vulnerability mix, moral clarity vs
   ambiguity norms for the genre, comedic/serious register.
2. **Endurance mechanics:** what lets the MC carry 100+ episodes (renewable goal structure,
   relationship engine, escalating capability ladder, episodic-vs-serial identity).
3. **Reader-bond devices:** POV interiority conventions, catchphrase/visual-token anchoring,
   failure cadence (how often the MC loses, per genre).
4. **Anti-patterns:** documented reasons MCs fail/get dropped in the genre.
5. **Wellness-embed note:** how a self-help/teacher-vessel payload rides THIS genre's MC without
   breaking genre contract (cross-ref `manga_mode_vessels.yaml` + `teacher_apparatus_per_genre.md`).

Deliverables A:
- `artifacts/research/manga_mc_endurance_study_2026-07-24.md` (per-family sections, sourced,
  confidence-rated).
- **Machine-usable distillation:** `config/manga/mc_endurance_checklists.yaml` — per family:
  `must_have[]`, `should_have[]`, `anti_patterns[]`, `endurance_mechanics[]`, each item one
  testable sentence with a `source:` anchor into the study. This file is Lane 07's input — keep
  keys stable and document the schema in a header comment. Mark `status: unwired` in the header
  (Lane 07 wires it; `check_manga_wiring.py` requires the marker until then).
- Bible §5 addenda ONLY where the study adds named exemplars a bible lacks (dated addendum lines).

## MISSION — PART B: market-data currency refresh (verify, not redo)
`popular_genre_ranking` + `marketing_grounded_per_genre_allocation` are pinned to 2024–2025 data.
1. Refresh top-line rankings with the newest public data (Oricon 2026 interim, Circana/ICv2 2026
   reporting where public, platform annual reports). Add a dated **2026 refresh addendum** to each
   doc — never rewrite the originals.
2. **Verdict line:** does any 2026 movement change the per-brand allocation in
   `GENRE_PORTFOLIO_PLAN.md`? Expected: no structural change — if a genre moved enough to shift a
   brand's mix, DO NOT edit the plan; surface it as Q-MPU-05 in your closeout with the evidence
   (allocation changes are operator-tier brand decisions).
3. Confirm the allocation chain still holds live: `GENRE_PORTFOLIO_PLAN.md` →
   `locale_genre_allocations.yaml` → series-plan generators (name the consumer scripts + a spot
   check that fresh series plans match allocation percentages).

## SMOKE → PILOT → SCALE
Part A smoke: 1 family incl. YAML checklist; pilot: +4; scale: all families. Part B is one pass.
Commit at checkpoints.

## WRITE SCOPE
`artifacts/research/manga_mc_endurance_study_2026-07-24.md`,
`config/manga/mc_endurance_checklists.yaml` (NEW-ARTIFACT-JUSTIFIED: machine-readable MC
checklist absent; add registry row in same PR), bible §5 addendum lines, dated addenda to the two
market docs, `docs/research/manga_craft/index.md` (serialized — see contract), handoff.
**OUT OF SCOPE:** `GENRE_PORTFOLIO_PLAN.md` allocation numbers (operator-tier), pacing yaml,
excellence-gate config (Lane 07).

## SIGNAL
`manga-mc-endurance-research-merged=<full merge SHA>`
