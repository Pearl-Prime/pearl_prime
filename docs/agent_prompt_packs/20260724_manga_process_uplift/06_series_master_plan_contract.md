# EXECUTE — Lane 06 — Series Master Plan contract (100-episode, genre-cadence arcs, mode-arcs)

**AGENT:** Pearl_Architect (spec) + Pearl_Dev (schema/validator) · **SUBSYSTEM:** manga_pipeline · **WAVE:** 2

## GATE CHECK (verifiable, not narrative)
Proceed only when `manga-arc-cadence-research-merged=<sha>` exists on a durable surface (merged
PR / PROGRAM_STATE / dispatcher log). Verify:
`git log origin/main --oneline -- config/manga/manga_pacing_by_genre.yaml | head -3` shows the
arc_cadence commit. If absent → report gate-unmet to dispatcher and STOP (this is the one lane
where building without the research would encode the exact fixed-12 assumption the operator asked
us to research away).

## EXECUTION CONTRACT (binding, in-band)
- EXECUTE end-to-end; terminal = signal token or ONE BLOCKER (evidence + pushed work +
  NEXT_ACTION). STARTUP_RECEIPT / CLOSEOUT_RECEIPT bracket the work.
- Re-verify premises live; PR #295's arc plans and the `20260723_manga_48ep_3catalog_series`
  pack are the live 48-ep program — this lane WRAPS it, never forks or invalidates it.
- DISCOVERY REPORT before writes. Reuse-first: EXTENDS `MANGA_ARC_STORYBOARD_CONTRACT.md` +
  `arc_storyboard_plan.schema.json` + the 48ep pack's `ASSIGNMENT_MATRIX.tsv` conventions.
- Substrate: plumbing pattern; explicit paths; staged-diff gate; preflight before push.
- Landing: MERGED (checks read + named) or BLOCKED. Cleanup ledger + handoff
  `artifacts/coordination/handoffs/manga_process_uplift_lane06_2026-07-24.md`.
- PROVENANCE: research=`manga_arc_cadence_study_2026-07-24.md` (+ pacing yaml arc_cadence,
  bible §7); documents=`MANGA_ARC_STORYBOARD_CONTRACT.md`, `GENRE_PORTFOLIO_PLAN.md`,
  `MANGA_MODE_STRATEGY.md`, `manga_mode_vessels.yaml`; builds_on=`manga_arc_storyboard`
  contract + 48ep program artifacts; inventory=EXTENDS (48-ep plans remain valid inputs).

## READ FIRST
`docs/specs/MANGA_ARC_STORYBOARD_CONTRACT.md`, `schemas/manga/arc_storyboard_plan.schema.json`,
`docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/` (INDEX + ASSIGNMENT_MATRIX.tsv +
one arc plan from PR #295's `arc_plans/` if merged — else from the PR branch, read-only),
`config/manga/manga_pacing_by_genre.yaml` (arc_cadence blocks), `config/manga/manga_mode_vessels.yaml`,
`docs/research/manga_craft/teacher_apparatus_per_genre.md`, `docs/specs/MUSIC_MODE_MANGA_V1_SPEC.md`,
`schemas/manga/series_plan.schema.json`, `phoenix_v4/manga/series/story_architect.py` (inputs it
takes: series/arc/genre/topic/mode/chapter — your plan must resolve to these).

## MISSION
Author the **Series Master Plan** layer: a per-series 100-episode plan that sits ABOVE the
existing per-arc storyboards and BELOW the series_plan listing.

1. **Spec:** `docs/specs/MANGA_SERIES_MASTER_PLAN_CONTRACT.md` — v1.0. Contents:
   - **Arc segmentation is genre-derived:** number + lengths of arcs over eps 1–100 come from the
     genre's `arc_cadence` block (episodes_per_arc_range, arc_pattern, first_major_shift_by) —
     NEVER a fixed 12. The 48-ep program's existing 4×12 plans map onto this as "near-term
     detailed window" (see §migration).
   - **Per-arc block:** arc_id, episode span, arc premise/promise, status-quo shift, MC change
     vector (consumes Lane 04 checklist keys), **self_help_topic** (from the brand's topic set),
     **mode_arc** — teacher-mode: the arc-level teaching (vessel + what the teaching resolves to
     across the arc, teacher NEVER named per `check_manga_story_authored`); music-mode: arc-level
     musical motif per `MUSIC_MODE_MANGA_V1_SPEC`; regular: explicit none.
   - **Episode-plan pass (the operator's second pass):** per episode within an arc — logline,
     genre-pleasure beat, self_help_topic beat, hook/cliff position, checklist refs. This is the
     input `story_architect` + the storyboarder consume.
   - **Marketing/genre conformance self-check section:** each master plan carries a filled
     checklist: genre contract (bible §1), cadence conformance (pacing yaml), MC endurance
     (mc_endurance_checklists), mode-arc coherence. Machine-checkable fields, not prose vibes.
   - **§Migration:** how a 48-ep plan upgrades to a 100-ep master plan (eps 1–48 = existing arcs
     verbatim; 49–100 outline-level per Q-MPU-01 ruling: flagship-first, ratified 2026-07-24).
     Existing plans stay valid — inventory EXTENDS, never REDUCED. **Absorb PR #295's 20 arc
     plans as rework inputs (Q-MPU-02 ruling: REWORK, never merge #295):** fetch
     `claude/manga-12ep-arc-authoring-egnwqf` read-only, migrate its `arc_plans/` +
     `arc_plans_all_genres/` content into master-plan-conformant artifacts for the flagship-first
     wave (source-credited), landing via THIS lane's PR. Do not close #295 (dispatcher does,
     after Lanes 05+06 signals exist).
   - **§US-illustrated addendum (Q-MPU-03 ruling: BOTH frames, ratified 2026-07-24):** the
     illustrated lane gets (a) a BOOK-format master-plan variant (chapters/page-count/art-ratio,
     parameterized by Lane 02's study — if `us-illustrated-format-research-merged` not yet
     emitted, mark numbers PENDING-LANE-02 rather than inventing them) AND (b) a
     serialized-episode variant for illustrated content that ships as a series (webtoon-style
     illustrated self-help). Routing rule: the series_plan `format`/`master_format` field decides
     the frame — spell the mapping out in the addendum.
2. **Schema:** `schemas/manga/series_master_plan.schema.json` — versioned, required fields per
   the spec, `acceptance_layer` enum like the arc-storyboard schema. Cross-refs validated:
   genre must exist in pacing yaml; arc spans must tile 1..100 without gaps/overlaps; mode fields
   XOR per vessels config.
3. **Validator:** `scripts/ci/check_manga_series_master_plan.py` — schema + cross-ref checks +
   cadence conformance (arc lengths within genre range ±tolerance from pacing yaml) +
   stub-marker lint (reuse `check_manga_story_authored` primitives) + teacher-name scan. Wire as
   an ADVISORY gate in `scripts/run_production_readiness_gates.py` (next free number, re-derive
   live). Tests: fixture master plan PASS + 4 mutation fixtures FAIL (bad tiling, off-cadence,
   teacher named, stub markers) — mutation-tested per agent_brief §14.
4. **One golden example:** author `artifacts/manga/series_master_plans/<flagship series>.master_plan.yaml`
   for ONE en_US flagship (pick the series with the deepest existing artifacts —
   `stillness_press…the_alarm_is_lying` unless discovery says otherwise), upgrading its existing
   arc plans per §migration. Validator PASS required. Label honestly: SPECCED+CODE-WIRED with one
   EXECUTED-REAL example; craft grade = authored candidate at most.

## WRITE SCOPE
The 4 deliverables above + registry rows (`manga_series_master_plan_contract`, schema, validator)
in `CANONICAL_ARTIFACTS_REGISTRY.tsv` via dispatcher request, handoff. **OUT OF SCOPE:**
authoring master plans at scale (Lane 11 pilots one; scale is a follow-on program),
`story_architect.py` code changes, pacing yaml. PR #295's branch is a read-only absorb-source —
never push to it, never merge it, never close it (dispatcher closes it).

## DO NOT
- No fixed-12 anywhere; every cadence number traces to the pacing yaml.
- Do not invalidate or rewrite the 48-ep program's artifacts.
- Do not mark the gate required — advisory until Lane 11 proves the loop.

## SIGNAL
`manga-series-master-plan-contract-merged=<full merge SHA>`
