# Pearl Prime SCENE Wiring — Handoff Context for Pearl_Dev

> ## ⚠️ SUPERSEDED 2026-04-27
>
> **This handoff doc is based on a stale BG-PR-09 framing.** PR #669 (`cbfbe14c39`, merged 2026-04-26 03:16) had ALREADY landed the canonical-CLI's SCENE wiring before this doc was authored, but via a different architectural path (upstream substitution in `enrichment_select.py:907` after `beatmap_compile.py` slot-grid edit, NOT the predicted port of `compose_section_packet` into `compose_from_enriched_book`).
>
> **No wiring PR is needed.** Phase 2 is closed-as-completed-by-PR-#669.
>
> See `docs/PEARL_ARCHITECT_STATE.md` BG-PR-09 cap entry (2026-04-27) for the full discovery + verification (12 named-character hits + 72 `story_plan/HARDSHIP` audit JSON matches + 36/36 tests + canary PASS, all reproduced on `origin/main` HEAD `99a926a9b7` with zero code changes).
>
> **Doc retained for archaeological reference** — shows what the BG-PR-09 framing predicted vs what PR #669 actually shipped. Do NOT use as a current execution brief.

---

(Original handoff content below — superseded.)

**Decision**: 1b approved 2026-04-27 (downgraded from 1a). Pearl Prime SCENE wiring (BG-PR-09 Phase 2) is approved but routed to a **fresh focused Pearl_Dev session** rather than spawned as a subagent in the audit-followup session, due to subtle pipeline-regression risk.

**Workstream**: `ws_bestseller_pipeline_default_path_b_20260425`
**Project**: `proj_pearl_prime_bestseller_rebase_20260425`
**Status**: ready to start (no prereq ws gating; no spec drafting required — wiring-only follow-up per BG-PR-09 update 2026-04-26)

---

## What's broken

Pearl Prime catalog wrapper currently produces **partial bestseller-grade output**:

- ✅ EXERCISE slots at sec 4/8 produce journey-aware named-character content (PR #604 wired `attach_exercise_journeys` into the canonical CLI; verified by 12-entry `enrichment_audit.json` `exercise_journeys` key + thesis-aligned `body_scan_v1` + `extended_exhale_v2` etc.; canary PASS exit 0; 36/36 tests PASS)
- ❌ SCENE slots at sec 2/5/9 produce generic content (`SCENE v04` / `SCENE v18`) with **zero named-character (Marcus/Priya/Elena/Jordan/Sam/Alex) hits** in `book.txt` and **zero `story_schedule` / `story_plan:HARDSHIP` / `book_tracker` keys** in the audit JSON

Result: Move 4's 450-book bestseller-grade catalog sweep is **gated** on this fix. `ws_catalog_quality_analysis_20260410` cannot proceed end-to-end.

## What needs to land

Wire `build_story_schedule` output + `slot_tracker` consumption into `compose_from_enriched_book` so SCENE slots at sec 2/5/9 produce named-character content matching the pilot's `compose_section_packet(story_schedule=…, slot_tracker=…)` pattern.

## Pattern-mirror

The pilot's working call site is:
- `phoenix_v4/rendering/section_packet_composer.py:243` — `compose_section_packet(story_schedule=…, slot_tracker=…)`

The canonical CLI's broken call site is:
- `scripts/run_pipeline.py` — `compose_from_enriched_book` (does not currently read `story_schedule` + `slot_tracker` the way pilot's `compose_section_packet` does)

Pearl_Dev's job: port the pilot's call signature into `compose_from_enriched_book` so the canonical CLI matches pilot output for SCENE slots.

## Authority docs (read in order)

1. `docs/PEARL_ARCHITECT_STATE.md` — BG-PR-09 entry + 2026-04-26 update (full background on Move 3 Path A retirement + Phase 1/Phase 2 split + decision rationale)
2. `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md:570-577` — canonical CLI declaration (`run_pipeline.py --pipeline-mode spine`); the bestseller contract Pearl_Dev wires
3. `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md` — workflow hardening context
4. `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md` — sole architecture authority
5. `phoenix_v4/rendering/section_packet_composer.py:243` — pilot's working `compose_section_packet` signature (the pattern-mirror)
6. `phoenix_v4/planning/story_planner.py:353` — `build_story_schedule` (whose output needs to flow through)
7. `scripts/run_pipeline.py` — canonical CLI's `compose_from_enriched_book` (the wiring target)

## Verification criteria

After landing, the catalog wrapper should produce:

- `book.txt` containing named characters (Marcus / Priya / Elena / Jordan / Sam / Alex) at sec 2/5/9
- `section_packet_audit.json` containing `story_schedule` + `story_plan:HARDSHIP:story_0:{recognition,mechanism_proof,turning_point}:overwhelm:vXX` + `book_tracker` keys
- All 36/36 existing tests still PASS
- Canary build still exits 0
- A new test specifically validating named-character SCENE slot output (Pearl_Dev should add)

## What's NOT in scope

- New spec authoring (no new governing flag; bestseller contract is already in `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md:570-577`)
- Path A wrapper-edit work (retired per BG-PR-09; do not revive)
- Move 5 story_atoms enhancements (rolling-optional per PR #672; not gated on Phase 2)

## Closeout

After Pearl_Dev's PR lands:

1. Update `ws_bestseller_pipeline_default_path_b_20260425` status: completed
2. Update BG-PR-09 entry in `docs/PEARL_ARCHITECT_STATE.md`: Phase 2 done; Move 4 unblocked
3. Pearl_Research + Pearl_Prime can run the 450-book sweep under `ws_catalog_quality_analysis_20260410`
4. `proj_pearl_prime_bestseller_rebase_20260425` status remains active (Move 5 Phase 2+ rolling-optional)

## Estimate

Pearl_Dev focused session: 6-10h (read context + implement + add test + verify + push + CI + merge).

No prereq ws gating. No spec drafting required. Single focused PR.
