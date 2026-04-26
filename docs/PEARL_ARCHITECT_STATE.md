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

### BR-CANON-01 — Brand-count canon = 37 per PR #682 spec (decision 7c approved 2026-04-27)

**Status:** **ratified** (operator decision 2026-04-27).
**Context:** Audit finding C-1 in `docs/FULL_REPO_SYSTEM_AUDIT_2026-04-26.md` surfaced a fractured brand-count canon — configs disagree:

- `config/brand_registry.yaml` — 28 brands
- `config/brand_management/global_brand_registry.yaml` — 312 entries (24 archetypes × 13 lanes)
- `BRAND_ADMIN_CANONICAL_PACKAGE.md` — 36
- `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` (PR #682) — **37** (load-bearing claim)

**Decision:** **37 is canonical** per the most recent governing spec (PR #682). Pearl_Brand reconciles `config/brand_registry.yaml` + `config/brand_management/global_brand_registry.yaml` + `BRAND_ADMIN_CANONICAL_PACKAGE.md` to 37 (with 312 framed as the *expanded view* = 37 brands × ~8.4 derivative variants/lanes, not a separate registry).

**Anti-drift check:** No new spec authored. The 37 figure already governs `MANGA_CATALOG_RECONCILIATION_SPEC.md`. Other docs are amended to match.

**Handoffs:**
- Pearl_Brand (PRIMARY) under `ws_brand_count_canon_reconciliation_20260427`: edit the 3 docs above to 37; document the derivation if 312 is the expanded view.
- Pearl_PM: this entry is ratification-only; no ws state-change beyond opening the Pearl_Brand ws (already done in `ACTIVE_WORKSTREAMS.tsv`).

### DASH-01 — Dashboard subsystem: revive, do not archive (decision 9b approved 2026-04-27)

**Status:** **active routing pending** (operator decision 2026-04-27).
**Context:** Audit finding C-8 surfaced the `dashboard/` subsystem as having no entry point + no row in `SUBSYSTEM_AUTHORITY_MAP.tsv`. Pipeline matrix shows it as `orphaned`.

**Decision:** **revive, not archive.** Pearl_Architect picks a canonical home from these candidates:

- **Pearl_News** — Pearl News v5.4 sidebar (PR #592) suggests dashboard work belongs here
- **Pearl_Brand** — Brand Admin weekly delivery has dashboard surfaces
- **Pearl_Prime** — book authoring dashboards exist
- **(new)** — register `dashboard` as its own subsystem with a distinct owner

**Recommendation (preliminary):** absorb into **Pearl_Brand** since the existing `brand_admin.html` + `brand-wizard-app/public/brand_admin.html` + `brand_admin_weekly_os.html` already provide dashboard surfaces. Final routing decision pending Pearl_Architect deep-dive under `ws_dashboard_subsystem_routing_20260427`.

**Handoffs:**
- Pearl_Architect (PRIMARY) under `ws_dashboard_subsystem_routing_20260427`: pick the canonical home; add the row to `SUBSYSTEM_AUTHORITY_MAP.tsv` with the chosen owner; document in this state doc as DASH-02 entry.
- Pearl_PM: open Pearl_Architect ws (already done).

### PHX-V4-ORPHAN-01 — phoenix_v4/ "153 orphans" deletion deferred / formally closed (decision 2c approved 2026-04-27)

**Status:** **closed-not-needed** (operator decision 2026-04-27).
**Context:** Audit (PR #702 `docs/FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md` PR D3 cluster) flagged 153 .py files in `phoenix_v4/` as orphans (`imported_by_count=0` AND `has_main=0`), suggested as deletion candidates pending runtime check.

**Verification done 2026-04-27 (Pearl_Architect spot-check):** sampled 30 of the 153 alleged orphans and ran a wider import-detection grep:

| Allegedly orphan | Actual ref count | Used by (sample) |
|---|---:|---|
| `phoenix_v4/content_banks/loader.py` | **61** | `tools/ci/run_narrative_gates.py` + 60 others |
| `phoenix_v4/content_banks/selector.py` | 26 | `tests/test_variation.py` + 25 others |
| `phoenix_v4/content_banks/session.py` | 6 | `server/routes/plaid_integration.py` + 5 others |
| `phoenix_v4/exercises/component_assembler.py` | 3 | `tests/test_exercise_component_assembler.py` + 2 others |
| `phoenix_v4/content_banks/quarantine.py` | 2 | `tests/test_doctrine_quarantine.py` + 1 other |

**Result: 30 of 30 sampled (100%) are FALSE POSITIVES.** Extrapolated to all 153: ~153 likely false positives, ~0 likely truly dead.

**Root cause of audit error:** Subagent D's import-counter in the original audit only matched the pattern `from phoenix_v4.X.Y import Z` and missed:

- `from .Y import Z` (relative imports within the package)
- `from phoenix_v4.X import Y` (package-level imports without specifying the submodule)
- pytest test discovery (auto-loads `test_*.py` without explicit import statement)
- CI script invocations (e.g., `tools/ci/run_narrative_gates.py` invokes via subprocess)

**Decision: defer / close PR D3 as not-needed.** No deletion. Cluster stays. The "153 orphans" was an audit-tooling artifact, not a real dead-code target.

**Anti-drift check:** Closing a deletion PR because it would have removed live code is the correct call. Re-running the same broken audit later would re-flag the same files; preventing that is the audit-tool patch backlog item below.

**Audit-tool patch backlog (Pearl_Architect follow-up):** `scripts/audit/build_pipeline_matrix.py` import-counter logic needs upgrade to AST-based or `pyflakes` / `vulture` integration, not pattern grep. Open as separate Pearl_Architect ws after operator agrees on tooling choice (overlaps with GAP-G8 classifier patch). Until that lands, treat any `phoenix_v4/`-related orphan output from the audit as suspect.

**Handoffs:**
- Pearl_PM: close `ws_phoenix_v4_orphan_runtime_check_20260427` (was proposed; never opened) — superseded by this entry.
- Pearl_Architect (FOLLOW-UP): open `ws_audit_import_counter_upgrade_20260427` if/when operator wants the audit-tool patch.
- Pearl_GitHub: cancel any draft PR D3 work (none in flight).

### DASH-02 — dashboard subsystem owner = Pearl_Brand (decision 2a approved 2026-04-27)

**Status:** **ratified** (operator decision 2026-04-27, follow-up to DASH-01).
**Context:** DASH-01 (above) reactivated the dashboard subsystem ("revive, not archive") but deferred the canonical-home decision to Pearl_Architect. Operator picked **Pearl_Brand** in the second decision round 2026-04-27.

**Rationale:**
- Pearl_Brand already owns the three live brand-admin HTML surfaces (`brand_admin.html`, `brand_admin_weekly_os.html`, `brand-wizard-app/public/brand_admin.html`)
- Triple-maintained HTML reconciliation (audit C-4) folds naturally under the same owner
- Brand Admin weekly delivery (`scripts/build_weekly_brand_package.py`, last touched 2026-04-26) is the most active dashboard touchpoint

**Action items:**
- Add row to `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`: `dashboard` subsystem, owner=Pearl_Brand, status=active
- Pearl_Brand absorbs `dashboard/` as part of `ws_brand_count_canon_reconciliation_20260427` OR opens a sibling ws (Pearl_Brand judgment)
- Triple HTML reconciliation can land under the same Pearl_Brand session (C-4 from audit)

**Anti-drift check:** Adding `dashboard` under Pearl_Brand (which already governs brand-admin surfaces) consolidates ownership, doesn't fragment it. Not drift.

### BR-CANON-01 update — 312 = expanded view of 37 (decision 3a approved 2026-04-27)

**Update to BR-CANON-01 above:** operator decision 3a approved 2026-04-27 confirms:

**312 entries in `config/brand_management/global_brand_registry.yaml` are the EXPANDED VIEW** of 37 brands × ~8.4 lane derivatives (24 archetypes × 13 lanes ≈ 312, derivable from the 37-row seed). NOT a separate registry.

**Pearl_Brand reconciliation pattern under `ws_brand_count_canon_reconciliation_20260427`:**

1. **Authoritative source**: `config/brand_registry.yaml` (currently 28 rows; expand to 37 per PR #682 spec)
2. **Derived view**: `config/brand_management/global_brand_registry.yaml` (re-derive 312 from the 37-row seed via deterministic generator)
3. **Cross-doc updates**: `BRAND_ADMIN_CANONICAL_PACKAGE.md` aligns to 37
4. **Generator script** (NEW): `scripts/brand_management/derive_global_registry.py` reads the 37-row seed + the 24×13 archetype × lane matrix and emits 312 entries; runs in CI to detect drift

**Pearl_Brand handoff is now unblocked**: operator inputs to BR-CANON-01 + DASH-02 give Pearl_Brand everything needed to start.

### BG-PR-09 — Phase 2 = COMPLETED-BY-PR-#669 (cap entry 2026-04-27)

**Status:** **closed-not-needed (Phase 2 NO-OP)** (operator decision 2026-04-27, follow-up to BG-PR-09 + the 2026-04-26 update + Path A closeout in `ws_bestseller_pipeline_default_path_a_20260425.next_action`).

**Discovery 2026-04-27:** Pearl_Dev session spawned to execute the SCENE wiring (decision 1b) STOPPED at Step 2 (Hard Stop Rule #3: "if compose_from_enriched_book has been modified since the BG-PR-09 entry was authored, STOP"). The wiring described in `docs/PEARL_PRIME_SCENE_WIRING_HANDOFF_2026-04-27.md` was based on a stale framing — PR #669 (`cbfbe14c39`, merged 2026-04-26 03:16) had already landed the canonical-CLI's SCENE wiring, but via a DIFFERENT architectural path than the handoff predicted:

| Predicted (handoff doc) | Actual (PR #669) |
|---|---|
| Port pilot's `compose_section_packet(story_schedule=…, slot_tracker=…)` into `compose_from_enriched_book` | Change `SOMATIC_10_SLOT_GRID` sec 2/5/9 from `SCENE` → `STORY` in `beatmap_compile.py`; extend waterfall in `enrichment_select.py:907` to handle STORY at SCENE_SECTION_INDICES; substitution happens UPSTREAM in enrichment, composer just renders `slot.content` |

Both architectural paths produce identical bestseller-grade output. PR #669 chose the upstream-substitution path; the canonical CLI is now correct.

**Verification reproduced 2026-04-27 (canonical CLI, no code changes against `origin/main` HEAD `99a926a9b7`):**

- `gen_z_professionals × anxiety` → `book.txt` shows **12 named-character hits** (Marcus=6, Priya=3, Jordan=1); `section_packet_audit.json` shows **72 `story_plan/HARDSHIP` source_id matches** at sec 2/5/9
- `millennial_women_professionals × anxiety` → `book.txt` shows 3 named-character hits (Elena from `watcher` engine bank); same 72 audit-JSON matches
- `pytest tests/test_pilot_feature_parity.py tests/test_book_qa_pipeline_integration.py tests/test_canary_integration.py`: **36/36 PASS** (6.54s)
- `scripts/canary/run_bestseller_canary.py`: exit 0, `overall_status=PASS`

**Decision: close BG-PR-09 Phase 2 as completed-by-PR-#669.** No new wiring PR needed. `ws_bestseller_pipeline_default_path_b_20260425` was never opened (per Path A's 2026-04-26 closeout text confirming it was unnecessary). Move 4 (`ws_catalog_quality_analysis_20260410` 450-book sweep) is unblocked architecturally; whatever coverage gap remains is now CONTENT (story_atoms anchored coverage for 13 personas without it), NOT wiring.

**Anti-drift check:** Recognizing that the handoff doc was based on a stale framing and closing the work as already-done is the correct call. Re-opening would risk double-wiring.

**Handoffs:**
- `docs/PEARL_PRIME_SCENE_WIRING_HANDOFF_2026-04-27.md` — marked SUPERSEDED in this PR; content preserved for archaeological reference.
- Pearl_Research + Pearl_Prime: Move 4 450-book sweep is architecturally unblocked. Coverage extends as Move 5 anchored content authoring lands per persona (gen_z covered today; 13 others queued).
- Pearl_PM: no ws state-change required (path_b ws never opened).

**Optional follow-up (NOT done in this PR; OQ-3 from Pearl_Dev report):** `enrichment_select.py:1216` could emit `story_schedule` as a top-level audit JSON key (currently only present per-slot via `source_id`). ~5-line patch. Not required for functionality; defer unless an audit consumer needs the top-level handle.
