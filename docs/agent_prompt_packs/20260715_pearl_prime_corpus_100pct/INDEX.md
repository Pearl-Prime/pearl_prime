# Pearl Prime Story/Transition/Cohesion Corpus 100pct Prompt Pack

## Program

- Goal: Drive the Pearl Prime story, transition, and atom-cohesion corpus workflow to proof-backed completion through safe micro-waves, starting from live origin/main truth and not from stale pasted notes.
- Source request: EXECUTE as Phoenix Omega Pearl_PM prompt router/dispatcher, using Router Operating Principles v4 from docs/agent_brief.txt.
- Router date: 2026-07-15.
- Live origin/main verified by router: `73e4a6fbb6322cdd9457494e3954d1286592ab20` (`Merge pull request #5636 from Ahjan108/codex/freebie-post-experience-capture-pr`).
- PROGRAM_STATE caveat: docs/PROGRAM_STATE.md still self-reports `LAST VERIFIED` at `d8532d2d43874051b90201bda8b07eab5c1ce817`; every lane must re-verify live `origin/main`.
- Prompt count: 9 prompt files total: 1 master dispatcher plus 8 lane prompts.
- Master dispatcher: `docs/agent_prompt_packs/20260715_pearl_prime_corpus_100pct/00_MASTER_DISPATCH_PROMPT.md`.

## Live Facts Verified By Router

- `#4644` is MERGED, merge commit `9fa288cd9e8610e7a2f0a4035a51da47f8356f70`, title `feat(composer): Phase 1 de-injection - glue OFF, TRANSITION consumer`.
- `#5162` is MERGED, merge commit `96be684e92489cd6657ae2c6eda0bdf7231155a9`, title `fix(composer): wire before_story TRANSITION into additive path (non-flagship, byte-neutral)`.
- `#4633` is MERGED, merge commit `d1d9d44c5f2746732cc632ccf094c0682a93ad4e`, title `feat(story): named 3-level story atoms - wave 1 (3 cells, 36 characters)`.
- `#4643` is OPEN, `mergeable=CONFLICTING`, checks red: parse-sweep, Core tests, Variant coverage gate, Schema & config validation. It must be reconciled or superseded, not merged as-is.
- `#5237` is OPEN, `mergeable=CONFLICTING`, checks red: parse-sweep, Schema & config validation, Core tests, Drift detectors, Release gates. It must not be blindly merged.
- `#5206` is OPEN, `mergeable=CONFLICTING`, only Workers Builds reported green. Treat as evidence-only/stale until re-derived.
- `PR #4643` file surface from live GitHub: two TRANSITION atom banks, book identity contracts, chapter thesis bank, and a de-injection/tissue spec.
- `PR #5237` file surface from live GitHub: atom cohesion evidence, corporate_managers/burnout atom edits, a `check_atom_cohesion.py` gate, and tests.
- Render glue production default is OFF through `phoenix_v4/rendering/render_glue.py`; explicit glue-off command must set `PHOENIX_ENABLE_RENDER_GLUE=0` or leave it unset.

## Wave Order

- Wave 0: `01_Pearl_PM_foundation_live_reconcile.md` - live facts, collision map, watchdog surface.
- Wave 1: `02_Pearl_Dev_transition_4643_supersede.md` - reconcile/land or supersede #4643 transition atom work from clean `origin/main`.
- Wave 2: `03_Pearl_QA_pilot_render_read_glue_off.md` - render-read the two pilot cells with transition glue OFF.
- Wave 3: `04_Pearl_Editor_atom_cohesion_stub_repair.md` - repair atom cohesion/stub/craft lane without merging dirty #5237.
- Wave 4A: `05_Pearl_Writer_story_atoms_scale_wave_a.md` - scale named STORY atoms only after pilot render-read passes.
- Wave 4B: `06_Pearl_Writer_transition_atoms_scale_wave_a.md` - scale TRANSITION atoms only after pilot render-read passes.
- Wave 5: `07_Pearl_Dev_production_gate_coverage_controller.md` - smoke -> pilot -> scale production proof waves; create next wave if coverage is not complete.
- Wave 6: `08_Pearl_PM_final_corpus_auditor.md` - final QA with exact production gates and honest catalog-scale claims.

## Lane Matrix

| Prompt | Agent | Lane | Owner | Substrate | Depends on | Output tag | Hot files |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 00 | Pearl_PM | master_dispatch | Pearl_PM | cloud chat + GitHub CLI | none | dispatcher closeout | reads all; implements none |
| 01 | Pearl_PM | corpus_foundation_live_reconcile_20260715 | Pearl_PM | clean cloud checkout + GitHub CLI | none | `corpus-foundation-ready=<sha>` | PM-only coordination files |
| 02 | Pearl_Dev | transition_4643_supersede_20260715 | Pearl_Dev | clean branch from origin/main | `corpus-foundation-ready` | `transition-pilot-reconciled=<sha>` | transition atom files; no hot coordination edits |
| 03 | Pearl_QA | pilot_render_read_glue_off_20260715 | Pearl_QA | clean branch + render runner | `transition-pilot-reconciled` | `pilot-glue-off-read-pass=<sha>` | proof artifacts only |
| 04 | Pearl_Editor | atom_cohesion_stub_repair_20260715 | Pearl_Editor + Pearl_Writer | clean branch + authoring + gates | `pilot-glue-off-read-pass` | `atom-cohesion-repair-a=<sha>` | scoped atom files; no hot coordination edits |
| 05 | Pearl_Writer | story_atoms_scale_wave_a_20260715 | Pearl_Writer | clean branch + authoring + gates | `pilot-glue-off-read-pass`; `atom-cohesion-repair-a` | `story-scale-wave-a=<sha>` | scoped STORY engine banks only |
| 06 | Pearl_Writer | transition_atoms_scale_wave_a_20260715 | Pearl_Writer | clean branch + authoring + gates | `pilot-glue-off-read-pass`; `atom-cohesion-repair-a` | `transition-scale-wave-a=<sha>` | scoped TRANSITION banks only |
| 07 | Pearl_Dev | production_gate_coverage_controller_20260715 | Pearl_Dev + Pearl_QA | build/test runner | story + transition scale signals | `corpus-production-gates-complete=<sha>` | proof artifacts; optional next-pack docs |
| 08 | Pearl_PM | final_corpus_auditor_20260715 | Pearl_PM | clean checkout + GitHub CLI | all launched lanes terminal | `pearl-prime-corpus-100pct-closeout=<sha>` | PROGRAM_STATE/ACTIVE_WORKSTREAMS only if warranted |

## Deconfliction

- `docs/PROGRAM_STATE.md`, `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`, `artifacts/coordination/operator_decisions_log.tsv`, `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv`, `docs/DOCS_INDEX.md`, and `docs/PEARL_ARCHITECT_STATE.md` are PM-serialized hot files. Non-PM lanes propose updates in handoff/PR body only.
- #4643 and #5237 are stale/conflicting source PRs. Agents may inspect their diffs and artifacts, but must create fresh branches from current `origin/main`.
- #5206 is evidence-only/stale. It may inform coverage gates only after live re-derivation.
- STORY scale and TRANSITION scale may run in parallel only after Wave 3, and only on disjoint file scopes chosen by the dispatcher.
- Locale atom lanes own locale subdirectories. This pack is en-US corpus-first unless the final coverage controller explicitly creates a separate localization follow-up.
- No lane may claim catalog-scale coverage unless the exact cells and gates are merged and listed in a proof root.

## Required Production Gates

- Live GitHub verification of #4644, #5162, #4633, #4643, #5237, and #5206 before dispatch.
- Transition consumer tests: `tests/unit/rendering/test_deinjection_phase1.py`, `tests/unit/rendering/test_composer_glue_off_default.py`, and targeted transition parser/select checks.
- Atom parse/stub gates: `scripts/ci/check_canonical_atom_parse_sweep.py`, `scripts/ci/check_canonical_atom_parse_sweep_baseline.txt`, and the cleanly-landed atom cohesion gate if promoted.
- Story gates: `tests/test_story_type_conformance.py`, `tests/unit/planning/test_story_picks.py`, `tests/unit/planning/test_opd142_story_schedule_routing.py`, `tests/unit/planning/test_opd143_story_slot_distinct_per_chapter.py`.
- Render proof: production spine renders with `PHOENIX_ENABLE_RENDER_GLUE=0`, `--pipeline-mode spine`, `--quality-profile production`, `--exercise-journeys`, and proof artifacts under `artifacts/qa/pearl_prime_corpus_*_20260715/`.
- Production readiness: `python3 scripts/run_production_readiness_gates.py` or a documented narrower gate set if full readiness is blocked by unrelated live-main red.
- Final audit: exact cells, files, PRs, merge SHAs, proof roots, and cleanup ledgers.

## Cleanup Requirements

Every lane must report:

- worktree removed or HOLD path/reason;
- local branch deleted or HOLD reason;
- remote branch deleted after merge or HOLD reason;
- scratch files removed;
- background jobs stopped or declared;
- temp credentials/logs redacted where relevant;
- handoff file path under `artifacts/coordination/handoffs/`;
- exact CLOSEOUT_RECEIPT signal token.

## Prompt-Pack Analysis And Fixes Applied

- More than three lanes required: v4 Prompt-Pack Mode used with a Pearl_PM dispatcher.
- Hot-file collision risk fixed by PM-only coordination edits.
- Dirty PR risk fixed by clean supersede lanes for #4643 and #5237.
- Giant-batch risk fixed by requiring smoke -> pilot -> scale in every lane.
- Watchdog risk fixed by polling/no-progress/max-window clauses in every lane.
- Stale-premise risk fixed by making every SHA/count/status a claim to re-verify.
- 100pct overclaim risk fixed by final auditor requiring merged proof roots before any catalog-scale statement.

## Final Status

- Status: prepared-local.
- Blockers: none for prompt-pack creation. Downstream execution may block on live PR conflicts, CI, production-path render failures, credentials, or operator Layer-4 read requirements.
- Next action: paste `00_MASTER_DISPATCH_PROMPT.md` into the lead cloud agent.
