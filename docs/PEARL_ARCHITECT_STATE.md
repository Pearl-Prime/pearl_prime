# Pearl_Architect State

Last verified: 2026-04-26  
Owner: Pearl_Architect

## Purpose

This file is the fast resume point for architecture routing and drift prevention in Phoenix Omega.

It answers:

- what the canonical architecture anchors are
- how Pearl_Architect differs from Pearl_PM
- what common routing failures look like
- what sources should be consulted first when a task is ambiguous

## Core Distinction

- **Pearl_PM = where work should continue**
- **Pearl_Architect = where work belongs**

Pearl_PM resolves overlap, active workstreams, project fit, and handoffs.  
Pearl_Architect resolves subsystem ownership, governing docs, required repo sources, and architecture drift risk.

## Canonical Architecture Anchors

When routing a task, start here:

1. [docs/SYSTEMS_V4.md](./SYSTEMS_V4.md) — systems-level overview
2. [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) — sole system architecture authority
3. [docs/DOCS_INDEX.md](./DOCS_INDEX.md) — authoritative navigation map
4. [docs/OWNERSHIP_MATRIX.md](./OWNERSHIP_MATRIX.md) — repo and path-family ownership boundaries
5. [artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv](../artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv) — subsystem shortcut map

## Common Drift Patterns

Reject or reroute proposals when they:

- invent a parallel UI or onboarding surface instead of updating the governed bundle
- invent generic SaaS flows where governed brand, funnel, or registry structures already exist
- introduce a new workbook, doc, or spec when a canonical file already exists
- treat historical salvage or old chat notes as current truth
- mix GitHub/repo-health work into non-GitHub lanes
- present planned or inferred business claims as if they were verified repo truth

## Current Routing Truth

- **Arc-First remains sole architecture authority.** If a proposal conflicts with Arc-First, Arc-First wins.
- **DOCS_INDEX is the canonical navigation layer.** If a task cannot be routed from there, Pearl_Architect must surface the gap.
- **SUBSYSTEM_AUTHORITY_MAP is a shortcut, not a replacement for DOCS_INDEX.**
- **Qwen-Agent / LM Studio retired operator patterns are historical only unless a new governing doc explicitly revives them.**
- **Existing workstream wins for execution; authority-doc fit wins for subsystem routing.**

## High-Value First Reads By Task Shape

| Task shape | Start here |
|-----------|------------|
| System architecture / pipeline | `docs/SYSTEMS_V4.md`, `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md` |
| GitHub / repo health | `docs/GITHUB_OPERATIONS_FRAMEWORK.md`, `docs/OWNERSHIP_MATRIX.md` |
| Presentation / onboarding / UI translation | `docs/DOCS_INDEX.md`, subsystem authority, existing HTML/UI files |
| Content / prompts / messaging | subsystem authority, writer specs, current live docs/assets |
| Recovery / overlap / salvage | `docs/PEARL_PM_STATE.md`, `ACTIVE_PROJECTS.tsv`, `ACTIVE_WORKSTREAMS.tsv` |

## Next Actions

1. Keep `SUBSYSTEM_AUTHORITY_MAP.tsv` aligned with live authority docs.
2. Surface gaps when a recurring task cannot be routed cleanly from the current architecture docs.
3. Block generic or duplicate architecture before implementation starts.
4. Keep Pearl_Architect docs aligned with `SESSION_UNITY_PROTOCOL.md`.

## Architect routing decisions

### BG-PR-08 — Bestseller-grade book arc validation (closed-not-needed)

**Status:** **closed-not-needed** (Option B, 2026-03-31).  
**Rationale:** No single in-repo spec named `validate_book_emotion_arc` / `BookArcResult`; arc validation is **distributed** across existing loaders and validators (e.g. `arc_loader`, `validate_arc_alignment`, `validate_compiled_plan`, `emotion_arc_validator.validate_emotion_arc`). Further consolidation is optional engineering polish, not a blocking architecture gap.

### BG-PR-09 — Move 3 Path A retired; hybrid Option (c) chosen for bestseller catalog smoke + Path B spec drafting

**Status:** **Path A retired; hybrid Option (c) ratified** (2026-04-26).  
**Context:** `proj_pearl_prime_bestseller_rebase_20260425` opened Move 3 Path A as a "wrapper-only tactical fix": edit `scripts/pearl_prime_multilingual/assemble_full_catalog_qa.py` to invoke `scripts/pilot/run_legacy_template_packet_pilot.py` per book instead of `scripts/run_pipeline.py --pipeline-mode spine`. Pearl_Dev's discovery (this conversation, post-PR #661 close-out) found the premise invalidated: the wrapper at lines 195-219 already invokes `run_pipeline.py` with the canonical Path B flag set (`--topic, --persona, --arc, --teacher, --seed, --out, --atoms-model, --atoms-root, --locale, --pipeline-mode spine, --render-book, --render-dir, --quality-profile, --no-job-check, --no-generate-freebies` plus optional `--angle, --series, --installment` — 16 wrapper-required CLI surfaces total). The pilot has only 8 argparse flags and explicitly declares itself "Side pipeline — does not change run_pipeline defaults" (line 5 docstring). Replacing the canonical wrapper invocation with the side-pipeline pilot would regress: multi-locale support (`--locale`), arc selection (`--arc`), render aggregation (`quality_summary.json` schema → `section_packet_audit.json`), `--quality-profile {production|draft|debug|flagship}`, catalog metadata (`--angle, --series, --installment`), and would force opinionated `--legacy-library v2_somatic` + `--exercise-journeys` on all 450 books across all locales. It would also contradict `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md:570-577` which declares `run_pipeline.py --pipeline-mode spine` as the canonical bestseller CLI.

**Architectural problem the wrapper edit was trying to solve:** the canonical CLI's spine-pipeline path does NOT currently invoke `attach_exercise_journeys` (`phoenix_v4/planning/enrichment_select.py:2027`) + `build_story_schedule` (`phoenix_v4/planning/story_planner.py:353`) + `compose_section_packet(story_schedule=…, slot_tracker=…)` (`phoenix_v4/rendering/section_packet_composer.py:243`). The Move 2 session reproduced the pilot end-to-end and proved those three calls produce bestseller-grade output (`story_plan:HARDSHIP:story_0:{recognition,mechanism_proof,turning_point}:overwhelm:vXX` at sec 2/5/9; `journey_intro:{awareness,regulation}` at sec 4/8; named characters Marcus/Priya/Elena/Jordan in prose; zero `library_34` fallback). The catalog wrapper currently produces non-bestseller-grade output because the canonical CLI doesn't wire those three calls.

**Three options surveyed:**

- **Option (a) — Temporary parallel pilot-using smoke wrapper.** New `scripts/pearl_prime_multilingual/bestseller_smoke_qa.py` (NOT the canonical wrapper); single-persona/single-topic smoke verification; canonical wrapper untouched. *Pros:* tactical, fast, respects Arc-First. *Cons:* doesn't solve root cause; wrapper-drift risk.
- **Option (b) — Path B spec + implementation only.** Author `docs/PEARL_PRIME_BESTSELLER_PIPELINE_DEFAULT_SPEC.md`; port the three integration calls into `run_pipeline.py` behind a `--bestseller-pipeline` flag. *Pros:* canonical, single CLI, long-term clean. *Cons:* gated on closing two prerequisite ws's (`ws_spine_flow_bridges_20260413` last touched 2026-04-14; `ws_bridge_transition_system_20260416` last touched 2026-04-16 — both ≥10 days stale); blocks Move 4 (`ws_catalog_quality_analysis_20260410` 450-book sweep) until Path B lands; risk of indefinite delay.
- **Option (c) — Hybrid: parallel smoke wrapper now + Path B spec drafting in parallel + Path B implementation gated.** Combines (a) + (b). Smoke wrapper unblocks Move 4's bestseller-grade evidence loop immediately; spec authoring proceeds in parallel (Pearl_Architect-only, NOT gated on the stale prereq ws's); implementation deferred until spec lands AND prereqs close. Sunset clause: smoke wrapper retires when Path B lands.

**Decision: Option (c) — Hybrid.** Rationale: (i) prereq ws's are ≥10 days stale → pure Option (b) risks indefinite Move 4 block; (ii) Move 4 has zero evidence on `origin/main` → Pearl_Research + Pearl_Prime are blocked NOW; (iii) the Move 2 session reproduction independently proved the pilot produces bestseller-grade output → smoke wrapper has a known-working backbone; (iv) Path B is canonically correct per Arc-First (`PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md:570-577`) → spec authoring should NOT be deferred merely because implementation is gated; (v) parallel-wrapper-drift risk mitigated by an explicit single-persona/single-topic smoke scope + a hard-coded sunset clause in the smoke wrapper's ws `next_action`; (vi) spec authoring is Pearl_Architect-only (no code, no prereq dependency) and can begin immediately.

**Anti-drift check (`Common Drift Patterns` above):** Authoring `docs/PEARL_PRIME_BESTSELLER_PIPELINE_DEFAULT_SPEC.md` is genuinely new (no existing canonical for `--bestseller-pipeline` flag semantics) and SUPPLEMENTS rather than DUPLICATES `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (which declares the canonical CLI but does not specify the `--bestseller-pipeline` flag's three integration call ports). Not drift. The smoke wrapper is single-purpose with sunset; not a parallel-UI invention.

**Gate dependencies:**

- Smoke wrapper (`ws_bestseller_smoke_wrapper_20260425`, Pearl_Dev): no prereqs; trigger = Pearl_PM ws creation.
- Spec drafting (`ws_bestseller_pipeline_default_spec_20260425`, Pearl_Architect follow-up session): no prereqs; trigger = Pearl_PM ws creation.
- Path B implementation (`ws_bestseller_pipeline_default_path_b_20260425`, Pearl_Dev): gated on spec landing AND `ws_spine_flow_bridges_20260413` closure AND `ws_bridge_transition_system_20260416` closure.
- Smoke wrapper sunset: triggered by Path B implementation landing.

**Handoffs:**

- Pearl_PM (PRIMARY, immediate): cancel `ws_bestseller_pipeline_default_path_a_20260425` (status=cancelled, rationale citing this entry); open three new ws's per Option (c); update `proj_pearl_prime_bestseller_rebase_20260425` `open_questions` (remove Path A premise; replace with Path B prereq + spec-authoring open) + `next_action` (route to smoke + spec + gated implementation).
- Pearl_Architect (FOLLOW-UP SESSION, decoupled): draft `docs/PEARL_PRIME_BESTSELLER_PIPELINE_DEFAULT_SPEC.md` under `ws_bestseller_pipeline_default_spec_20260425` once Pearl_PM opens it. Spec scope: `--bestseller-pipeline` flag semantics on `run_pipeline.py`; the three integration call ports; slot grid contract (sec 2/5/9 = STORY from engine bank; sec 4/8 = `journey_intro` EXERCISE); audit-signal contract (`section_packet_audit.json` schema for bestseller-grade output). MUST NOT contradict `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md:570-577`; supplement by specifying HOW the canonical CLI achieves bestseller-grade output.
- Pearl_Dev (IMMEDIATE): build `scripts/pearl_prime_multilingual/bestseller_smoke_qa.py` under `ws_bestseller_smoke_wrapper_20260425`. Single-persona/single-topic smoke (NOT multi-locale, NOT 450-book sweep). Output: bestseller-grade audit signal evidence on a single sample.
- Pearl_Dev (GATED): implement Path B under `ws_bestseller_pipeline_default_path_b_20260425` once spec + prereqs land.
- Pearl_Research + Pearl_Prime (Move 4 RE-SCOPE): Move 4's "450-book bestseller-grade sweep" deliverable is split into (i) immediate single-sample bestseller-grade evidence via the smoke wrapper, and (ii) full 450-book sweep gated on Path B implementation landing. Update `ws_catalog_quality_analysis_20260410` accordingly.

**Update 2026-04-26 (Pearl_Dev runtime verification — Option (c) PARTIALLY downgraded):**

PR #604 (`be8f5dc8538bb4153b71143fc57fc2618a28f53b` "feat(pilot-parity): port 7 pilot-only features into spine path") wired the EXERCISE-side integration call (`attach_exercise_journeys` at [`scripts/run_pipeline.py:617-619`](../scripts/run_pipeline.py)) plus the flag at `:1546-1549`. PR #612 (`e40f1b74fddeed8565442027ad3928ef9d81f8c8` "fix(enrichment): additive-only + EXERCISE rule + hard-fail on missing atoms") made `additive_enrichment` the only mode at [`enrichment_select.py:281-285`](../phoenix_v4/planning/enrichment_select.py). Both verified.

**However:** runtime verification of the wrapper-flag-add (Pearl_Dev session, 2026-04-26) showed PR #604 wired the *enrichment* side of `build_story_schedule` but the *composer* consumption is missing. `compose_from_enriched_book` (canonical CLI) does not read the `story_schedule` + `slot_tracker` the way the pilot's `compose_section_packet(story_schedule=…, slot_tracker=…)` does. Evidence: catalog wrapper run with `--exercise-journeys` produces journey-aware EXERCISE slots ✓ (12 entries in `enrichment_audit.json` `exercise_journeys` key; thesis-aligned `body_scan_v1` + `extended_exhale_v2` etc.; canary PASS exit 0; 36/36 tests PASS) but SCENE slots at sec 2/5/9 still show generic `persona_atom+registry` content (`SCENE v04`/`SCENE v18`) with **zero named-character (Marcus/Priya/Elena/Jordan/Sam/Alex) hits in `book.txt`** and zero `story_schedule` / `story_plan:HARDSHIP` / `book_tracker` keys in the audit JSON.

**Option (c) downgrade is PARTIAL, not full:**
- `ws_bestseller_smoke_wrapper_20260425`: still NOT needed (additive default + canonical wrapper produces partial bestseller-grade output via flag-add).
- `ws_bestseller_pipeline_default_spec_20260425`: still NOT needed (no new governing flag; wiring only — the bestseller-grade contract is already in `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md:570-577`).
- **`ws_bestseller_pipeline_default_path_b_20260425`: STILL NEEDED** — scoped to wiring `build_story_schedule` output + `slot_tracker` consumption into `compose_from_enriched_book` for SCENE slots at sec 2/5/9. Pearl_Dev-owned, no spec dependency, no prereq ws gating. Single-PR scope; pattern-mirror is the pilot's `compose_section_packet` call site at [`phoenix_v4/rendering/section_packet_composer.py:243`](../phoenix_v4/rendering/section_packet_composer.py).

**Two phases:**
- **Phase 1** (this conversation): wrapper passes `--exercise-journeys`; EXERCISE slots journey-aware; canary PASS; 36/36 tests PASS; 1 of 3 integration call sites wired into canonical CLI consumption.
- **Phase 2** (follow-up Pearl_Dev under new `ws_bestseller_pipeline_default_path_b_20260425`): wire `build_story_schedule` + `slot_tracker` into `compose_from_enriched_book` so SCENE slots produce named-character content. Move 4 (`ws_catalog_quality_analysis_20260410` 450-book sweep) gated on Phase 2 landing.

**Pearl_PM hard gate:** do NOT open `ws_bestseller_smoke_wrapper_20260425` or `ws_bestseller_pipeline_default_spec_20260425`. DO open `ws_bestseller_pipeline_default_path_b_20260425` (Pearl_Dev, no prereqs, no spec). Close `ws_bestseller_pipeline_default_path_a_20260425` status=completed with Phase-1 framing after the sibling Pearl_Dev wrapper-flag PR lands.

**No new governing spec introduced; the previously-projected `PEARL_PRIME_BESTSELLER_PIPELINE_DEFAULT_SPEC.md` remains retired (Phase 2 is wiring-only follow-up; the bestseller contract is already in `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`).**
