# Pearl_Architect State

Last verified: 2026-05-10  
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

### BR-CANON-01 — Brand-count canon = 37 per PR #682 spec (decision 7c approved 2026-04-27) — REFRAMED BY PATH X

**Status:** **ratified, then reframed by Path X (2026-04-27).** This entry's "37 is canonical for ALL brand counting" framing is **superseded** by the Path X cap entry below: **37 governs MANGA only; 24 archetypes × 13 lanes = 312 governs the BOOK pipeline; both are legitimate canons on different axes.** Keep this entry for archaeology; route to the Path X cap entry for current truth.

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

### BR-CANON-01 update — 312 = expanded view of 37 (decision 3a approved 2026-04-27) — SUPERSEDED BY PATH X

**Status:** **superseded by Path X (2026-04-27)** — see BR-CANON-01 Path X cap entry below.

**Update to BR-CANON-01 above:** operator decision 3a approved 2026-04-27 originally framed:

**312 entries in `config/brand_management/global_brand_registry.yaml` are the EXPANDED VIEW** of 37 brands × ~8.4 lane derivatives (24 archetypes × 13 lanes ≈ 312, derivable from the 37-row seed). NOT a separate registry.

**Pearl_Brand reconciliation pattern (originally proposed) under `ws_brand_count_canon_reconciliation_20260427`:**

1. **Authoritative source**: `config/brand_registry.yaml` (currently 28 rows; expand to 37 per PR #682 spec)
2. **Derived view**: `config/brand_management/global_brand_registry.yaml` (re-derive 312 from the 37-row seed via deterministic generator)
3. **Cross-doc updates**: `BRAND_ADMIN_CANONICAL_PACKAGE.md` aligns to 37
4. **Generator script** (NEW): `scripts/brand_management/derive_global_registry.py` reads the 37-row seed + the 24×13 archetype × lane matrix and emits 312 entries; runs in CI to detect drift

**Pearl_Brand handoff is now unblocked**: operator inputs to BR-CANON-01 + DASH-02 give Pearl_Brand everything needed to start.

**Why superseded:** Pearl_Brand re-investigated 2026-04-27 and surfaced that the 3a framing ("312 is the expanded view of 37") is mathematically tidy (24 × 13 = 312; 37 × 8.4 ≈ 312) but architecturally misleading. The 24 in `config/brand_management/global_brand_registry.yaml` are *spiritual archetypes* (inner_light_press / contemplative + karma yoga; etc.) whereas the 37 in `docs/GENRE_PORTFOLIO_PLAN.md` are *manga genre/demographic brands* (stillness_press iyashikei josei; cognitive_clarity seinen psychological; etc.). They are not the same axis. Operator surfaced the framing question and chose **Path X — keep them distinct** (decision Q1 = yes distinct, Q4 = split BRAND_ADMIN_CANONICAL_PACKAGE into book + manga sections, Q2/Q3 N/A).

### BR-CANON-01 Path X cap entry — 37 = MANGA canon; 24×13=312 = BOOK pipeline; both legitimate (decision Path X approved 2026-04-27)

**Status:** **ratified — Path X separation** (operator decision 2026-04-27).

**Decision:** **Manga and book pipelines ARE intentionally distinct.** No convergence. No shared registry. The two canons govern different content, different distribution channels, and different revenue tiers:

| Pipeline | Canonical brand count | Authoritative registry | Owner |
|---|---:|---|---|
| **Book** (Pearl_Prime) | 24 archetypes × 13 lanes = **312** | `config/brand_registry.yaml` (28-row seed) → `config/brand_management/global_brand_registry.yaml` (312 derived) | Pearl_Prime |
| **Manga** (Pearl_Brand) | **37** brands | `config/manga/canonical_brand_list.yaml` (NEW under this entry) | Pearl_Brand |

The 37 are genre × demographic × wellness-anchor brands derived from market analysis (`docs/GENRE_PORTFOLIO_PLAN.md`); they govern the manga catalog reconciliation (`specs/MANGA_CATALOG_RECONCILIATION_SPEC.md`, PR #682). They are NOT a subset, superset, or transform of the 24 spiritual archetypes that govern Pearl_Prime's book pipeline.

**Operator decisions 2026-04-27:**

- Q1: yes, distinct (manga and book brand canons are intentionally separate)
- Q4: split `BRAND_ADMIN_CANONICAL_PACKAGE.md` into a book section (24 × 90 = 2,160) and a new manga section (37, with cross-links to `config/manga/canonical_brand_list.yaml` and the manga reconciliation spec)
- Q2/Q3: not applicable under Path X (no convergence; no merged registry)

**Anti-drift check:** Path X rejects the 3a framing's implicit pressure to make 312 = 37 × N for some N. That math holds (37 × 8.4 ≈ 312) but it is a coincidence; the underlying axes (spiritual archetype × locale lane vs. genre × demographic × wellness anchor) are distinct. Forcing convergence would require redesigning either the book pipeline's archetypes or the manga pipeline's genre allocation. Operator chose to preserve both.

**Action items (this PR):**

1. **NEW:** `config/manga/canonical_brand_list.yaml` — 37 manga brands enumerated from `docs/GENRE_PORTFOLIO_PLAN.md` ##### headers; each entry has `tier` (flagship/core/niche), `demographic` (josei/seinen/shonen/shojo/manhwa), `primary_topic`, `secondary_topics`, `notes`.
2. **EDIT:** `BRAND_ADMIN_CANONICAL_PACKAGE.md` — split into a book section (24 × 90 = 2,160) and a new manga section (37, with cross-links to `config/manga/canonical_brand_list.yaml` and `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md`); note Pearl_Brand also owns dashboard surfaces per DASH-02.
3. **EDIT:** this state doc — mark the 3a "expanded view" entry SUPERSEDED; add this Path X cap entry.
4. **DEFERRED:** `scripts/manga/derive_manga_lane_table.py` — manga lane semantics are NOT the book pipeline's 24×13 (manga distribution channels align differently). Pearl_Brand surfaces this as an open question rather than sketching speculative lane primitives. Open Question documented in `BRAND_ADMIN_CANONICAL_PACKAGE.md` manga section.

**Files NOT modified under Path X (load-bearing book-pipeline canon):**

- `config/brand_registry.yaml` (28-row Pearl_Prime book registry — UNCHANGED)
- `config/brand_management/global_brand_registry.yaml` (312-entry book × locale matrix — UNCHANGED)
- `scripts/brand_management/generate_global_registry.py` (book-side generator — UNCHANGED)

**Handoffs:**

- Pearl_Brand (THIS PR): land the canonical list + doc edits; surface the manga lane semantics open question; do NOT touch book-pipeline files.
- Pearl_Prime: no action — book pipeline registry continues unchanged.
- Pearl_PM: close `ws_brand_count_canon_reconciliation_20260427` after this PR merges; the original convergence framing is retired in favor of Path X separation.
- Pearl_Brand (FOLLOW-UP, operator-gated): once manga lane semantics are decided (genre × demographic × distribution-channel? × locale?), open a sibling ws to author `scripts/manga/derive_manga_lane_table.py` and any downstream manga lane table consumers.

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

### SPEC-739-THRESHOLD-01 — Variant coverage threshold = 3 floor; 5 = optional expansion (decision 2026-04-28)

**Status:** **ratified** (operator decision 2026-04-28).

**Context:** PR #178 (commit `4725390b29bf5cee81874c811d4f86ad627952fb`, merged 2026-04-01) and sibling PRs #174 (healthcare_rns + first_responders, 124 files), #176 (tech_finance_burnout + gen_alpha_students, 716 files), #177 (gen_x_sandwich + working_parents, 124 files), #178 (entrepreneurs + millennial_women_professionals, 128 files) established a 3-variant persona-voiced authoring tradition across 8 personas × 16 topics × 4 slots ≈ 1,092 files between 2026-04-01 and 2026-04-02 — replacing auto-generated 20-variant template content (originally seeded by PR #138, 588 files across 12 personas) with curated 3-variant slots in the `--- variant: vNN` format. Spec #739 (`specs/SPEC_5_VARIANTS_AND_BESTSELLER_BEAT_WIRING.md`, landed 2026-04-27 in PR #743) declared a ≥5-variant gate without reconciling against this established tradition. Phase 1 validator (PR #743) + Phase 1.5 format fix (PR #746) faithfully reported the contradiction as **1,168 "gaps"** in `artifacts/qa/variant_coverage_gap_2026-04-27.md` (63 registry sections + 1,105 atom tuples). On inspection these were design-tradition artifacts, not coverage gaps — 477 of the atom tuples (have=3: 454 + have=4: 23) represented curated production content already meeting the established floor.

**Framing nuance (recorded so future-you doesn't redo the analysis):** The original task brief described "Sibling PRs #138/#174/#176/#177 followed the same 3-variant authoring tradition." PR #138's commit message actually says "All 588 files created with 20 variants each" — it was the *auto-generated baseline* that PRs #174/#176/#177/#178 *replaced* with 3-variant curated content for 8 personas. The remaining 4 personas (educators, gen_z_professionals, corporate_managers, healthcare_rns gap-fill) are largely still on the 20-variant baseline from PR #138. The "3 = production floor" framing holds because (a) the curated 3-variant content is the lowest count of authored production-grade material and (b) personas still on the 20-variant baseline are 20 ≥ 3 = comfortably above the floor. Lowering the floor to 3 unblocks the 8 rewritten personas while leaving headroom for the 4 not-yet-rewritten personas to be rewritten at 3 in the future without failing the gate.

**Decision:** Lower spec #739 threshold to 3. Frame as production floor, not quality ceiling. Preserve 5 as optional future expansion target via per-section `min_variants_required: 5` override in `registry/<topic>.yaml` (already in use at `registry/grief.yaml` chapter_01 section_10 INTEGRATION + chapter_12 section_07 INTEGRATION; the validator's `check_registry` line 153 honors per-section overrides verbatim — `need = int(section.get("min_variants_required") or min_variants)`). The 477-tuple swing in the gap report is the load-bearing evidence that the threshold (not the authoring backlog) was the dominant variable in the contradiction.

**Verified gap-count delta (this PR's regenerated `artifacts/qa/variant_coverage_gap_2026-04-28.md`):**

| Axis | BEFORE (threshold ≥5) | AFTER (threshold ≥3) | Delta |
|---|---:|---:|---|
| Registry sections passing | 1,287 | 1,287 | unchanged (per-section overrides preserve authoring intent) |
| Registry sections failing | 63 | 63 | unchanged (all are have=1 grief sections that fail at need=3 too) |
| Atom tuples passing | 1,205 | 1,682 | +477 (have=3: 454 + have=4: 23) — the curated authoring tradition |
| Atom tuples failing — below_threshold | 587 | 110 | -477 (have=0: 10 + have=1: 97 + have=2: 3 remain as real Phase 2 backlog) |
| Atom tuples failing — missing_file | 518 | 518 | unchanged (TEACHER_DOCTRINE-dominated; structural — see followup below) |
| **Total gaps reported** | **1,168** | **691** | **-477 (-41% raw)** |
| Real gaps (excluding scope-deferred missing_file) | 650 | 173 | -477 (-73%) |
| Threshold-axis gaps (excluding missing_file + grief have=1 registry rows) | 587 | 110 | -477 (-81%) |

**mwp-specific delta (anchor sample):** BEFORE 89 atom gaps (74 below_threshold = 67 have=3 + 7 have=1; 15 missing_file TEACHER_DOCTRINE). AFTER 22 atom gaps (7 have=1 below_threshold + 15 missing_file TEACHER_DOCTRINE). The 67 have=3 tuples flip from "gap" to "passing" — exactly what the threshold flip predicts.

**Anti-drift check:** Aligning with the established 2026-04-01 authoring tradition is anti-drift. Preserving the spec at ≥5 would have been the drift — it would have either (a) pressured Phase 2 authoring sessions to overwrite curated 3-variant persona-voiced content with auto-generated 5-variant slop, or (b) left the validator perpetually red on intentional production content. The spec retains its historical filename for stable cross-references; the threshold value is now the load-bearing field, not the filename.

**Out of scope for this PR (deferred handoffs):**

1. **TEACHER_DOCTRINE missing-file gaps (518 tuples repo-wide; 15 mwp-specific).** The validator currently flags `atoms/<persona>/<topic>/TEACHER_DOCTRINE/CANONICAL.txt` as missing whenever the file does not exist. By design, TEACHER_DOCTRINE content lives in `teacher_banks/<teacher>/doctrine/` rather than the persona × topic atom tree (the doctrine is teacher-keyed, not persona-keyed; see `docs/SYSTEMS_V4.md` teacher mode and `SOURCE_OF_TRUTH/teacher_banks/`). The validator flagging is structural, not a Phase 2 authoring task. **Followup ws (NOT spawned by this PR):** Pearl_Dev to add teacher_banks-awareness to `check_atoms` so TEACHER_DOCTRINE either resolves to the teacher bank's doctrine path or is excluded from the (persona × topic × section_type) axis. Pearl_PM to open `ws_spec_739_validator_teacher_banks_awareness_20260428` (or rename per Pearl_PM convention) when this work is scheduled. Until then, the 518 missing_file gaps remain in the report as known structural artifacts.

2. **Spec filename rename (`SPEC_5_VARIANTS_AND_BESTSELLER_BEAT_WIRING.md` → `SPEC_3_VARIANTS_AND_BESTSELLER_BEAT_WIRING.md`).** Touches too many cross-references (handoff docs, ws rows, PR descriptions, this cap entry). Spec §1 now carries a one-line historical-filename note acknowledging the threshold was reconciled while the filename was preserved for stable references. Filename rename is NOT scheduled.

3. **5-as-optional-expansion path scheduling.** This cap entry confirms the 5-ceiling is available via per-section `min_variants_required: 5` override (already used at 2 grief INTEGRATION sections). When/whether to opt more sections into the 5-ceiling is a separate decision per topic/persona; not scheduled by this entry.

4. **Phase 2 authoring scope-shrink execution.** With the threshold reconciled, `ws_spec_739_phase_2_persona_atom_authoring_20260427`'s scope drops from "~4,200-atom ceiling" to "110 below-threshold tuples" (real Phase 2 backlog). Pearl_PM to update the ws's `task` and `next_action` columns post-PR-merge to reflect the new scope. NOT done in this PR.

5. **Format reconciliation `## TYPE vNN` vs `--- variant: vNN`.** Phase 1.5 (PR #746) made the validator format-agnostic. Reconciling the two header conventions to a single canonical form is a separate Pearl_Architect routing decision; untouched by this PR.

**Resolves:** `ws_spec_739_arch_min_variants_review_20260427` (the proposed Pearl_Architect ws asking "lift `registry/grief.yaml` `min_variants_required: 3` → 5 vs accept per-section minimum?"). Decision: **accept the per-section minimum** as legitimate. The registry-side per-section overrides (61 grief sections at need=3, 29 grief sections at need=5) are intentional authoring decisions, not "set assuming 5" drift; they remain unchanged. Pearl_PM should mark this ws as **resolved-by SPEC-739-THRESHOLD-01** when updating the workstream TSV.

**Handoffs:**
- Pearl_PM (PRIMARY, post-merge): backfill `ws_spec_739_threshold_reconciliation_20260428` row in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (status=completed; cite this PR + this cap entry); update `ws_spec_739_phase_2_persona_atom_authoring_20260427` `task` + `next_action` to reflect the 110-tuple scope shrink; mark `ws_spec_739_arch_min_variants_review_20260427` as resolved-by-SPEC-739-THRESHOLD-01; open `ws_spec_739_validator_teacher_banks_awareness_20260428` for the TEACHER_DOCTRINE structural followup (Pearl_Dev, no prereqs).
- Pearl_Dev (FOLLOWUP, NOT this PR): TEACHER_DOCTRINE teacher_banks-awareness in `scripts/registry/validate_variant_coverage.py` `check_atoms` per item 1 above.
- Pearl_Editor + Pearl_Writer (FOLLOWUP, NOT this PR): Phase 2 authoring against the 110 below-threshold tuples in `artifacts/qa/variant_coverage_gap_2026-04-28.md` once Pearl_PM updates the Phase 2 ws.

### SPEC-739-VALIDATOR-MULTISOURCE-01 — Validator alt-source awareness (TEACHER_DOCTRINE + EXERCISE per spec §4.5); other 9 section types deferred (decision 2026-04-28)

**Status:** **ratified** (operator decision 2026-04-28).

**Context:** SPEC-739-THRESHOLD-01 cap entry surfaced TEACHER_DOCTRINE missing-file phantom gaps as a deferred Pearl_Dev followup. Investigation under `ws_spec_739_validator_teacher_banks_awareness_20260428` confirmed that `scripts/registry/validate_variant_coverage.py` measured only ONE of the spec-canonical content sources for atom resolution. `specs/PHOENIX_V4_5_WRITER_SPEC.md` §4.5 declares EXERCISE has THREE sources: `atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt` → `teacher_banks/<teacher>/approved_atoms/EXERCISE/*.yaml` → `SOURCE_OF_TRUTH/practice_library/store/practice_items.jsonl`. TEACHER_DOCTRINE has zero `atoms/<persona>/<topic>/TEACHER_DOCTRINE/CANONICAL.txt` files repo-wide by design — the pipeline pulls TEACHER_DOCTRINE from `teacher_banks/<teacher>/doctrine/` (verified via `phoenix_v4/planning/injection_resolver.py` runtime reads + `phoenix_v4/rendering/prose_resolver.py` Stage-6 docstring). Empirical evidence shows the same multi-source pattern in pipeline runtime for STORY/HOOK/REFLECTION/INTEGRATION/COMPRESSION/PIVOT/PERMISSION/TAKEAWAY/THREAD via `teacher_banks/<teacher>/approved_atoms/<TYPE>/` (200 atoms per type per teacher across 13 teachers), but the spec only formalizes it for EXERCISE.

**Decision:** Implement validator awareness for the **two spec-codified cases** (TEACHER_DOCTRINE via `teacher_banks/<teacher>/doctrine/`; EXERCISE per spec §4.5 three-source rule). **Defer** the other 9 section types as a separate Pearl_Architect routing question — extending validator awareness there is *pipeline-canonical* via `prose_resolver.py` but *spec-uncodified*, and broadening validator semantics without spec authority would be drift.

**Effect on gap report (verified empirically against `origin/main` at e0dd7c08ef):**

| Metric | BEFORE (e0dd7c08ef) | AFTER (this PR) | Delta |
|---|---:|---:|---|
| atom_passed | 1,682 | 1,921 | +239 |
| - via persona-atom canonical | 1,682 | 1,682 | unchanged |
| - via alt source: `teacher_banks/doctrine` | 0 | 210 | +210 (TEACHER_DOCTRINE phantom gaps eliminated) |
| - via alt source: `teacher_banks/approved_atoms/EXERCISE` | 0 | 29 | +29 (EXERCISE phantom gaps eliminated) |
| atom_gaps total | 628 | 389 | −239 |
| - below_threshold | 110 | 110 | unchanged (real Phase 2 backlog) |
| - missing_file | 518 | 279 | −239 (deferred 9 section types remain at ~29-32 each) |
| **total gaps reported** | **691** | **452** | **−239 (−35%)** |

**mwp anchor:** BEFORE 22 (7 below_threshold + 15 missing_file all TEACHER_DOCTRINE). AFTER 7 (7 below_threshold + 0 missing_file) — every mwp missing-file tuple was TEACHER_DOCTRINE; all resolve via `teacher_banks/doctrine`.

**Scope-discipline anchor:** A regression test (`test_other_section_types_remain_persona_atom_only_per_scope`) explicitly seeds `teacher_banks/<teacher>/approved_atoms/<TYPE>/` for HOOK / STORY / REFLECTION / INTEGRATION / COMPRESSION / PIVOT / PERMISSION / TAKEAWAY / THREAD and asserts the validator does NOT silently broaden multi-source awareness to those types. Future Pearl_Architect routing decision required to extend (or hold).

**Anti-drift check:** Implementing the spec's explicit §4.5 EXERCISE three-source rule + TEACHER_DOCTRINE's by-design teacher_banks resolution is anti-drift (validator now matches what spec + pipeline already declare). Extending to the other 9 section types without spec authority WOULD be drift; correctly deferred.

**Open routing question (NOT decided this PR):** Should validator multi-source awareness extend to STORY/HOOK/REFLECTION/INTEGRATION/COMPRESSION/PIVOT/PERMISSION/TAKEAWAY/THREAD via `teacher_banks/<teacher>/approved_atoms/<TYPE>/` per `prose_resolver.py` pipeline-canonical Stage-6 sources? Pros: gap report becomes pipeline-accurate; remaining 279 missing_file gaps resolve. Cons: dilutes the persona-voiced authoring requirement (spec §3.1 R-1 mandates persona-specific variants at production floor); broadens validator semantics beyond spec authority. Pearl_Architect to rule when scheduled.

**Resolves:** `ws_spec_739_validator_teacher_banks_awareness_20260428` (proposed by SPEC-739-THRESHOLD-01 cap entry as a Pearl_Dev followup for the 518 missing_file tuples). Decision: **partial resolution** — TEACHER_DOCTRINE + EXERCISE done; other 9 section types deferred as named open routing question above. Pearl_PM should mark this ws as **completed** when updating the workstream TSV (the 279 still-missing tuples are not this ws's responsibility — they're scope-deferred to the open routing question's eventual ws).

**Handoffs:**
- Pearl_PM (post-merge): mark `ws_spec_739_validator_teacher_banks_awareness_20260428` as **completed** in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (cite this PR + this cap entry); update the proj `next_action` to reflect that the gap-report numbers are now `691 → 452 (−35%)` for the canonical reference.
- Pearl_Architect (FUTURE, when scheduled): rule on extending validator multi-source awareness to the other 9 section types per the open routing question above. Open `ws_spec_739_validator_alt_source_extension_<DATE>` if the answer is yes.
- Pearl_Editor + Pearl_Writer (Phase 2 restart, separate session): the corrected gap report at `artifacts/qa/variant_coverage_gap_2026-04-28.md` is now pipeline-accurate for TEACHER_DOCTRINE + EXERCISE; remaining 110 below_threshold tuples are the real Phase 2 backlog. Hero persona = `millennial_women_professionals` (7 mwp gaps total post-fix).

### MASTER-CATALOG-01 — `PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md` declared not-needed; route to existing canon (decision approved 2026-05-05)

**Status:** **closed-not-needed** (Option (ii), 2026-05-05).
**Context:** Audit handoff `docs/PHOENIX_OMEGA_AUDIT_HANDOFF_2026-05-04.md` (persisted via PR #875) §1 row 9 + §5.1 P0 #2 listed `docs/PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md` as a missing anchor cited in the audit's Phase 5 storefront pathway. Three options surfaced: (i) author the doc, (ii) re-route Phase 5 to existing canonical docs, or (iii) declare obsolete.
**Decision:** **Option (ii) — re-route.** A unified "master catalog plan" anchor would *drift from* `BR-CANON-01 Path X` (37 = manga canon; 24 archetypes × 13 lanes = 312 = book pipeline; both legitimate on different axes). Manga and book pipelines are intentionally distinct; a single unifying plan-doc would re-introduce the pre-Path-X conflation that Path X explicitly retired. The audit was authored before Path X landed; its "missing master plan" framing is a pre-Path-X artifact. The Phase 5 storefront pathway references the per-axis canon already on origin/main:
- **Manga axis:** `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` + `docs/CJK_CATALOG_PLAN.md` + `docs/US_CATALOG_PLAN.md` (per-locale)
- **Book axis:** `docs/GENRE_PORTFOLIO_PLAN.md` (canonical strategic) + book script catalogs (4 locales × 13 brands)
- **Cross-axis index:** `docs/DOCS_INDEX.md` (the navigation layer; not a plan doc)
Rejected (i) because it would author drift; rejected (iii) because the underlying Phase 5 pathway IS active and routed to existing canon.
**Anti-drift check:** Re-routing to existing canon is anti-drift. Option (i) would have created a parallel plan-doc duplicating `GENRE_PORTFOLIO_PLAN.md` + `MANGA_FULL_CATALOG_PLAN.md` content, exactly the kind of "introduce a new spec when a canonical file already exists" pattern this doc's `Common Drift Patterns` section flags.
**Action items:**
1. Pearl_GitHub (`ws_docs_index_refresh_20260505`): when refreshing `docs/DOCS_INDEX.md`, add a routing note that the audit's `PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md` reference is closed-not-needed under MASTER-CATALOG-01 and link to the per-axis canon above.
2. Pearl_PM: close `ws_master_catalog_plan_authoring_20260505` status=closed-not-needed citing this entry.
**Handoffs:**
- Pearl_GitHub → `ws_docs_index_refresh_20260505` → trigger = audit-handoff persistence PR #875 merged.
- Pearl_PM → `ws_master_catalog_plan_authoring_20260505` → trigger = this cap-entry PR merged; close-out only.

### PR-D-SPINE-01 — Compact-format spine = declarative subset of 12-chapter spine via `compact_chapter_subset` (P3-refined; decision approved 2026-05-05)

**Status:** **ratified — declarative-P3 implementation already shipped in PR #865** (operator decision 2026-05-05).
**Context:** `artifacts/handoff/PR_D_HANDOFF_2026-05-04.md` (persisted via PR #877) §3 surfaced four paths for the compact-format spine architecture: P1 (synthesize spine from format spec's `beat_sheet` — ~50 lines, single source of truth = format spec, risk = thin synthesized scaffolding), P2 (author 3 new compact spine YAMLs via Pearl_Writer follow-up — crosses engineering/content line, slowest), P3 (subset 12-chapter spine to N chapters at `apply_knob` time — ~15-30 lines, brittle if hand-coded), abandon. PR #865 (still blocked under BRAND1-COMBINED-PR-01 below) ships a **declarative refinement of P3**: `compact_chapter_subset: [1, 4, 7, 10, 12]` etc. is added to each compact format block in `config/format_selection/format_registry.yaml`; `_load_compact_chapter_subset` in `phoenix_v4/planning/knob_apply.py` reads the list and returns subsetted, renumbered `SpineChapter` objects from the full topic spine. Three tests pin the contract (`test_load_spine_compact_8ch_30min_subsets_to_8` etc.; verified passing in Pearl_PM 2026-05-04 session).
**Decision:** **P3-declarative.** The brittleness the handoff flagged for P3 (auto-mapping `phase → chapter range` is fragile) is mitigated by **operator hand-curation of the subset list per format**: each compact format's `compact_chapter_subset` is a small explicit list; the operator can re-curate if a particular spine chapter's role doesn't match the compact narrative. P1 is rejected because synthesizing from `beat_sheet` discards the spine-author's curation work. P2 is rejected as cost-disproportionate for the thin compact-format coverage and as crossing engineering/content lines mid-cycle. Abandon is rejected — #858 already shipped W1+W2+W4 wiring; backing out is wasteful.
**Anti-drift check:** Declarative subset config in `format_registry.yaml` extends an existing canon; no new spec authored. The `_load_compact_chapter_subset` reader is a single ~30-line helper in `knob_apply.py`, not a parallel pipeline. Format spec remains the single source of truth for compact format contract; spine YAMLs remain the single source of truth for chapter content.
**Action items:**
1. Pearl_Dev (after BRAND1-COMBINED-PR-01 split lands): the W1+W2+W4 wiring is on origin/main via #858. The W3a (`SOMATIC_FULL_RUNTIME_FORMATS` extension), W3c (declarative subset implementation), W3d (`ARC_BEATS` extension), and W4 (runtime_policies in `book_quality_gate.yaml`) all currently live in #865's branch — fold these into the PR-Beta split per BRAND1-COMBINED-PR-01.
2. Pearl_Dev: under `ws_pr_d_wires_resume_20260505`, run W5/W6 smoke against `gen_z_professionals × anxiety × {compact_book_5ch_15min, compact_book_8ch_30min}` once PR-Beta lands. Iteration cap = 2 per memory `feedback_validation_before_scaling`.
**Handoffs:**
- Pearl_Dev → `ws_pr_d_wires_resume_20260505` → trigger = BRAND1-COMBINED-PR-01 PR-Beta merged (chapter_count fix + spine subset on origin/main).
- Pearl_PM → `ws_pr_d_spine_arch_pick_20260505` → trigger = this cap-entry PR merged; close as resolved-by-PR-D-SPINE-01.

### COVER-REGISTRY-01 — `config/authoring/author_cover_art_registry.yaml` is book-pipeline-only (not retired); manga has no registry (decision approved 2026-05-05)

**Status:** **ratified** (Option (a) with reframe, 2026-05-05).
**Context:** Pearl_PM 2026-05-04 finish-out session surfaced a file-level conflict between PR #880 (Pearl Star image-gen canonical bundle) and the brand-1 PR stack (#865 + #867). The Pearl Star handoff `docs/HANDOFF_PEARL_STAR_IMAGE_PIPELINE_2026-05-04.md` §3 listed `config/authoring/author_cover_art_registry.yaml` as a deletion candidate alongside the rest of the static-PNG manga cover-art system; brand-1 PR #865 added 12 stillness_press author entries + 8 brand palette tokens to that same file. Pearl_PM excluded the deletion from PR #880 per Q-B and routed the long-term decision here. Three options were on the table: (a) coexist (two cover systems in parallel), (b) retire the YAML and re-land brand-1's 12 entries elsewhere, (c) retire the new EI manga-author system instead.
**Decision:** **Option (a) — coexist, with explicit reframe.** Path X (BR-CANON-01 Path X cap entry) already established that manga and book pipelines are intentionally distinct on the brand-count axis; the cover-art axis is the same shape. Specifically:
- **Manga side:** EI character-authors at `config/authoring/manga_authors/`. Cover art is **unique per book** — Pearl Star FLUX renders imagery + PIL composites typography. **No registry, no shared bases.** Spec authority: `specs/MANGA_AUTHOR_AND_COVER_ART_CANONICAL_SPEC.md` (in PR #880).
- **Book side (KDP audiobooks):** Pen-name authors at `config/authoring/pen_name_teacher_profiles.yaml` + `config/author_registry.yaml`. Cover art uses **4 base slots per author + deterministic SHA256 per-book composition** (PIL-only, FLUX bases generated once per author). Spec authority: `docs/authoring/AUTHOR_COVER_ART_SPEC.md` (committed in #865 as part of brand-1 phase 1). `config/authoring/author_cover_art_registry.yaml` is the runtime registry for the 4-slot system; it stays.
The Pearl Star handoff §3 listed the YAML as a deletion candidate because it conflated "old MANGA static-PNG cover art" with "all static-PNG cover art." Brand-1 explicitly notes (handoff §11 #4): "Treating manga authors and pen-name authors as the same class — they're separate." The two systems share neither a registry nor a generator; the only collision was the filename `author_cover_art_registry.yaml` which now belongs to the BOOK pipeline only. Rejected (b) because re-landing brand-1's content elsewhere is churn for no architectural gain. Rejected (c) because the Pearl Star EI author-cover system has clear spec authority and is needed for the manga lane.
**Anti-drift check:** This decision **clarifies** path-family ownership rather than introducing new files: zero new specs, zero new configs. It corrects a deletion-list scope error in the Pearl Star handoff. The new `MANGA_AUTHOR_AND_COVER_ART_CANONICAL_SPEC.md` retains authority over the manga axis; `AUTHOR_COVER_ART_SPEC.md` (book axis, in #865) retains authority over the book axis; both systems have non-overlapping config paths.
**Action items:**
1. Pearl_GitHub (PR #880 reviewer): merge PR #880 as currently shaped — the deletion of `config/authoring/author_cover_art_registry.yaml` is correctly NOT in the bundle.
2. Pearl_Brand: edit `specs/MANGA_AUTHOR_AND_COVER_ART_CANONICAL_SPEC.md` (in PR #880, before merge OR follow-up doc PR after merge) to remove `config/authoring/author_cover_art_registry.yaml + dependent scripts (old; deletion candidates)` from the "Replaces" front-matter. Replace with: "the static-PNG manga cover-art system is retired on the manga side only; the book-side `author_cover_art_registry.yaml` remains active under `docs/authoring/AUTHOR_COVER_ART_SPEC.md`." This is a small spec edit, not new spec authoring.
3. Pearl_PM: close `ws_pearl_star_brand1_cover_registry_routing_20260505` status=resolved-by-COVER-REGISTRY-01 citing this entry.
**Handoffs:**
- Pearl_GitHub → PR #880 merge (operator approval per receipt E5).
- Pearl_Brand → small spec-edit ws (Pearl_PM to open `ws_manga_cover_spec_replaces_clause_edit_20260505` if the edit is deferred to a follow-up PR; or Pearl_GitHub edits in PR #880 directly).
- Pearl_PM → `ws_pearl_star_brand1_cover_registry_routing_20260505` → trigger = this cap-entry PR merged; close as resolved.

### AUTO-PLAN-SSOT-01 — Canonical chapter_count = `format_registry.yaml`; refactor `book_structure_plan.FORMAT_CHAPTER_COUNTS` to read from registry (decision approved 2026-05-05)

**Status:** **ratified — long-term refactor (Option (b)); stopgap (NOTE comment + dual-update) acceptable for current cycle** (operator decision 2026-05-05).
**Context:** `artifacts/handoff/HANDOFF_bestseller_smoke_post_852_856_2026-05-04.md` (on origin/main via PR #858 squash `f052d38d5e`) §Finding 1 named the SSoT violation: `phoenix_v4/planning/book_structure_plan.py:18 FORMAT_CHAPTER_COUNTS` is a hardcoded dict that duplicates `chapter_count_default` declared in `config/format_selection/format_registry.yaml`. The format-selector path at `phoenix_v4/planning/format_selector.py:153` already reads from the registry; the auto-plan path does not. PR #856 added the `compact_book_*` registry declarations without wiring `book_structure_plan` to read them, so the auto-plan's fallback `FORMAT_CHAPTER_COUNTS.get(runtime_format, 10)` returned 10 chapters instead of the registry-declared 8 — the failure that produced REJECT in the bestseller smoke.
**Decision:** **Option (b) — `format_registry.yaml` is the canonical home for chapter_count_default.** `book_structure_plan.FORMAT_CHAPTER_COUNTS` should be refactored to either (i) read at module-import time from the registry, or (ii) be eliminated in favor of a registry-aware helper. Either form prevents the same regression on the next format added. Rejected option (a) leave-as-is: dual-update discipline failed once (#856) and will fail again. Rejected putting chapter_count in `book_structure_plan.py`: that's a runtime planning module, not a config; format declarations belong in `format_registry.yaml` per existing structure.

The interim stopgap landed in PR #865 (still blocked) is acceptable for this cycle:
- Adds `compact_book_*` entries to `FORMAT_CHAPTER_COUNTS` (matches registry's `chapter_count_default`)
- Adds an explicit NOTE comment naming the duplication, the format-selector single-source path, and "BOTH must be updated together when adding a new runtime format. Eliminating the duplication … is tracked as a follow-up refactor"
The NOTE comment is the right interim contract: it documents the drift risk explicitly. The follow-up refactor is the ratification target; that's what this cap entry tracks.

**Anti-drift check:** No new spec authored. The decision aligns auto-plan with format-selector: both read `chapter_count_default` from the same registry. Reduces (does not introduce) duplication.
**Action items:**
1. Pearl_Dev (follow-up after BRAND1-COMBINED-PR-01 PR-Beta lands, which carries the stopgap): open a small refactor PR replacing `FORMAT_CHAPTER_COUNTS` with a registry-aware helper. ~30-50 lines. Single owner: `book_structure_plan.py`. Test pin: assert that adding a new runtime format to `format_registry.yaml` flows through to auto-plan without editing `book_structure_plan.py`.
2. Pearl_PM: close `ws_auto_plan_ssot_routing_20260505` status=resolved-by-AUTO-PLAN-SSOT-01 once the refactor PR lands. The interim stopgap is part of BRAND1-COMBINED-PR-01 PR-Beta; the refactor is a separate ws.
**Handoffs:**
- Pearl_Dev → `ws_auto_plan_ssot_refactor_20260505` (NEW; Pearl_PM to open) → trigger = BRAND1-COMBINED-PR-01 PR-Beta merged.
- Pearl_PM → `ws_auto_plan_ssot_routing_20260505` → trigger = this cap-entry PR merged; close as resolved (refactor work tracked under the new ws).

### BRAND1-COMBINED-PR-01 — Close #865 + #867; split into 3 clean PRs off `origin/main` (decision approved 2026-05-05)

**Status:** **ratified — Option (c) split differently, with specific 3-PR shape** (operator decision 2026-05-05).
**Context:** Pearl_PM 2026-05-04 finish-out session attempted the Q-A directive's strip + rebase path on PR #865 (brand-1 phase 1, registry plumbing) and PR #867 (brand-1 phase 2, 48 author bundle YAMLs stacked on #865). Two structural blockers surfaced: (1) **#865 alone fails CI** because `tests/test_registry_plan_runtime_format.py` invokes `scripts/run_pipeline.py` and the pipeline rejects per Writer Spec §23.9 ("no assets directory for author_id=lena_thorne") — registries reference 12 brand-1 authors whose `assets/authors/{id}/` directories live in #867, not #865. (2) **#867 is CONFLICTING** after #865's rebase, locked at sibling worktree `unruffled-robinson-25197f`, and its diff vs current `origin/main` shows 153 files changed including 61 file deletions (over `CLAUDE.md` rule 0 threshold of 50) — most of those are stale `.claude/worktrees/*` deletions plus retroactive deletions of `tests/test_cover_d1_immediate_fixes.py` (#855), `tests/test_pearl_news_sidebar_v52.py` (#853), and other already-merged work the branch was based off pre-merge. Cherry-picking #867's commits onto rebased #865 produced conflicts on tangled history.

In addition, PR #865 has scope-creeped well past brand-1 phase 1's 7-file charter: its 24-file rebased diff covers four distinct workstreams — (i) brand-1 author registries + spec doc (the original charter), (ii) PR-D residual wiring (chapter_count fix in `book_structure_plan.py` + spine subset in `format_registry.yaml` + `knob_apply.py` + `chapter_flow_gate.py`), (iii) `gen_z_professionals × anxiety` atom backfill (3 CANONICAL.txt files), (iv) 3 PR_E/G/H bestseller smoke QA artifacts.

Four options were considered:
- (a) keep stacked: blocked on Writer Spec §23.9 (registries-without-assets); also #865 still carries 3 unrelated workstreams in scope.
- (b) collapse #865 + #867 into one combined PR off main: 153 file changes including 61 deletions tripping rule 0; spurious `.claude/worktrees/*` artifacts; cross-workstream creep persists.
- (c) split differently: separate PRs aligned to actual workstreams.
- (d) close both and re-author from scratch: wasteful (working content exists).

**Decision:** **Option (c) split differently into THREE clean PRs off `origin/main`** (`f052d38d5e` post-#858):

**PR-Alpha — brand-1 author system atomic.** The brand-1 phase 1 + phase 2 unit per the brand-1 handoff's "the two PRs together" framing. Files (~62):
- `config/author_registry.yaml` (12 stillness_press entries)
- `config/authoring/author_cover_art_registry.yaml` (12 entries + 8 palette tokens — the file COVER-REGISTRY-01 ratifies as book-pipeline-canonical)
- `config/authors/author_voice_profiles.yaml` (12 voice profiles)
- `config/brand_author_assignments.yaml` (12-author pool + topic-affinity rules)
- `docs/authoring/AUTHOR_COVER_ART_SPEC.md` (NEW — book-pipeline cover-art authority per COVER-REGISTRY-01)
- `scripts/catalog_visibility/distribute_brand1_to_authors.py` (NEW)
- `artifacts/catalog/brand1_author_distribution_en_US.csv` (192 rows)
- `assets/authors/{12 author_ids}/{bio,why_this_book,authority_position,audiobook_pre_intro}.yaml` × 12 = 48 YAMLs
- `docs/handoffs/2026-05-04_brand1_author_system_handoff.md` (handoff doc)
Resolves Writer Spec §23.9: registries and assets land atomically.

**PR-Beta — PR-D residual wiring + auto-plan SSoT stopgap.** Per PR-D-SPINE-01 + AUTO-PLAN-SSOT-01. Files (~10):
- `config/format_selection/format_registry.yaml` (`compact_chapter_subset` declarations on 3 compact formats)
- `phoenix_v4/planning/knob_apply.py` (`_load_compact_chapter_subset` + extended `load_spine` signature)
- `phoenix_v4/planning/book_structure_plan.py` (`FORMAT_CHAPTER_COUNTS` augmented + NOTE comment per AUTO-PLAN-SSOT-01 stopgap)
- `phoenix_v4/quality/chapter_flow_gate.py` (compact runtime classification)
- `config/quality/per_format_chapter_flow_requirements.yaml` (compact rules)
- `config/quality/book_quality_gate.yaml` (`runtime_policies` for compact, if not already on main from #858)
- `config/spines/anxiety_spine.yaml` (any tweaks)
- `registry/anxiety.yaml` (any tweaks)
- 4 test files: `tests/test_chapter_flow_gate.py`, `tests/test_enrichment_select.py` (adds), `tests/test_generate_book_plan.py`, `tests/test_knob_apply.py`
This PR-Beta is the pipeline-side residual; it gates the AUTO-PLAN-SSOT-01 long-term refactor (separate Pearl_Dev follow-up ws).

**PR-Gamma — gen_z×anxiety atom backfill.** Per bestseller smoke handoff §Finding 2. Files (~3):
- `atoms/gen_z_professionals/anxiety/HOOK/CANONICAL.txt`
- `atoms/gen_z_professionals/anxiety/INTEGRATION/CANONICAL.txt`
- `atoms/gen_z_professionals/anxiety/PIVOT/CANONICAL.txt`
Optional: minor test additions if any existing test pins these paths.

**Out-of-scope** (not in any of the three PRs): the 3 PR_E/G/H bestseller smoke QA artifacts (`artifacts/qa/bestseller_smoke_post_pr_{e,g,h}_2026-05-04.md`). These are evidence, not deliverables. They can land as part of the W5/W6 smoke re-run under `ws_bestseller_smoke_re_run_20260505` after PR-Beta + PR-Gamma merge, OR be omitted entirely if the re-run produces fresh equivalent artifacts.

Rejected (a) for the §23.9 violation. Rejected (b) for the rule-0 trip + worktree artifact pollution. Rejected (d) for being wasteful — Pearl_Dev cherry-picks the already-authored content into the three new branches.

**Anti-drift check:** No new specs authored. Three PRs, each scoped to a single workstream, each landing atomically per its own integration contract. Brand-1 phase-1+phase-2 atomic landing satisfies Writer Spec §23.9. PR-D residual wiring honors PR-D-SPINE-01's declarative-P3 ratification. Atom backfill honors bestseller smoke handoff Finding 2's content-only scope.
**Action items:**
1. **Pearl_Dev** (PRIMARY, IMMEDIATE) — open the three clean PRs from `origin/main`:
   - branch a: `agent/brand1-author-system-atomic-20260505` for PR-Alpha. Cherry-pick from #865 + #867. Verify `lena_thorne` assets exist before opening. Run gates including `gh pr view --json files` deletion check (expect 0 deletions).
   - branch b: `agent/pr-d-residual-wiring-20260505` for PR-Beta. Cherry-pick the relevant 10 files from rebased #865's branch (`agent/brand1-author-system-phase1` at `c459e217db`). Re-run the 3 `test_load_spine_compact_*` tests locally; verify pass.
   - branch c: `agent/atom-backfill-gen-z-anxiety-20260505` for PR-Gamma. Cherry-pick the 3 atoms.
   - All three independent of each other — Pearl_Dev opens in parallel.
2. **Pearl_PM** (after Pearl_Dev opens the three PRs):
   - close PR #865 status=superseded by PR-Alpha/Beta/Gamma trio; comment linking this cap entry.
   - close PR #867 status=superseded by PR-Alpha; comment linking this cap entry.
   - close `ws_brand1_phase1_phase2_combined_pr_routing_20260505` status=resolved-by-BRAND1-COMBINED-PR-01.
   - open three new ws's: `ws_brand1_author_system_atomic_pr_20260505`, `ws_pr_d_residual_wiring_pr_20260505`, `ws_atom_backfill_gen_z_anxiety_pr_20260505`. Each with Pearl_Dev as owner, blocker=needs-CI-pass, next_owner=Pearl_GitHub.
**Handoffs:**
- Pearl_Dev → 3 new ws's (above) → trigger = this cap-entry PR merged.
- Pearl_PM → close #865, close #867, close `ws_brand1_phase1_phase2_combined_pr_routing_20260505`, open 3 new ws's → trigger = Pearl_Dev opens the three replacement PRs.
- Pearl_GitHub → review/merge the 3 replacement PRs in normal cadence (no special ordering; all three independent).

### AUTO-PLAN-SSOT-01-AMENDMENT — chapter_count divergence adjudication for 16 of 20 formats (decision approved 2026-05-06)

**Status:** **ratified — supplements AUTO-PLAN-SSOT-01** (2026-05-06).
**Context:** Pearl_Dev STOP 2026-05-06 under `ws_auto_plan_ssot_refactor_20260505` surfaced that the original AUTO-PLAN-SSOT-01 cap entry (2026-05-05) assumed `config/format_selection/format_registry.yaml` carried `chapter_count_default` for every format the Python `phoenix_v4/planning/book_structure_plan.FORMAT_CHAPTER_COUNTS` dict covers, AND that values agreed where both existed. Neither was true: of 20 keys in the Python dict, **only 4 match the registry** (`micro_book_15`, `compact_book_5ch_15min`, `compact_book_5ch_20min`, `compact_book_8ch_30min`); **10 are missing from the registry entirely** (Group A); **6 have divergent values** (Group B). A naive swap of FORMAT_CHAPTER_COUNTS for a registry read would have lost 10 formats' counts (falling through to the dict's `.get(..., 10)` default) and silently changed runtime behavior for 6 others. Beyond AUTO-PLAN-SSOT-01's "30-50 line refactor" scope.

A third Python source — `RUNTIME_TEMPLATES` at `book_structure_plan.py:62-65` — also exists, with `chapter_count` keys that differ AGAIN from FORMAT_CHAPTER_COUNTS (`short_book_30`: 6 here vs 8 there; `deep_book_6h`: 12 here vs 20 there). RUNTIME_TEMPLATES is consumed at line 120 only for `tier`/`exercise_cap` data; its embedded `chapter_count` field is vestigial in the auto-plan path. Out of scope for this amendment; flagged for follow-up cleanup.

**Decision:** Group A backfilled from Python mechanically (Python is the only source). Group B adjudicated per format below; the receipt's default tie-breaker — **prefer Python (matches current runtime behavior); flag for bestseller smoke verification** — applies to all 6, because the evidence is that Python was set later (PR ACT-011 / BSG-011 "Book plan generator", commit 2026-04-14) than the registry values (PR #252 PR-#245-incident restore, 2026-03-30; subsequent PR #409 word_range calibration, 2026-04-09), AND no spec text in `PHOENIX_V4_5_WRITER_SPEC.md` / `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` declares chapter_count for any of the divergent formats. Python is the de-facto runtime SSoT; making registry SSoT means writing Python's values into the registry and deleting the duplicate Python constant. Format_selector's existing registry-read path (`format_selector._chapter_count_and_word_range:149-165`) applies persona/structural clamping AFTER reading `chapter_count_default` from the registry, so backfilling Python's values into the registry preserves both auto-plan and format-selector behavior.

**Group A — 10 MISSING from registry, mechanical backfill** (write the Python value as `chapter_count_default` in `config/format_selection/format_registry.yaml:runtime_formats`):

| Format | Backfill value |
|---|---:|
| `five_min_practice` | 5 |
| `pocket_guide` | 6 |
| `ten_things_to_do` | 8 |
| `symptom_to_action_atlas` | 8 |
| `daily_text_audio_companion` | 10 |
| `crisis_cards` | 6 |
| `weekly_challenge_pack` | 8 |
| `faq_audiobook` | 8 |
| `myth_vs_mechanism` | 8 |
| `protocol_library` | 10 |

For each Group A format, the registry currently has no entry under `runtime_formats:`; Pearl_Dev adds a minimal entry with at least `chapter_count_default` set. `word_range` and other fields can be filled at the operator's discretion or left absent (registry's other consumers like `format_selector` already handle missing optional fields with sensible fallbacks: `word_range: [9000, 11000]` per `format_selector.py:154`).

**Group B — 6 DIVERGENT, ruling preserves Python value** (write the Python value as `chapter_count_default`, overwriting the existing registry value):

| Format | Registry (current) | Python (current) | Ruling | Evidence |
|---|---:|---:|---:|---|
| `micro_book_20` | 5 | 6 | **6** | Registry from PR #252 (incident restore) → #409; Python from BSG-011 (later, deliberate). Tie-breaker: Python. |
| `short_book_30` | 7 | 8 | **8** | Same. Note `RUNTIME_TEMPLATES[short_book_30].chapter_count = 6` exists for tier/exercise_cap context only; not the auto-plan value. |
| `standard_book` | 12 | 10 | **10** | Same. **Most consequential** — `standard_book` is the default canonical book runtime. `RUNTIME_TEMPLATES[standard_book].chapter_count = 12` (matches registry) but again is tier/exercise_cap context, not auto-plan. Auto-plan currently produces 10-chapter `standard_book` outputs; preserve. |
| `extended_book_2h` | 15 | 14 | **14** | Same. |
| `deep_book_4h` | 20 | 16 | **16** | Same. |
| `deep_book_6h` | 24 | 20 | **20** | Same. `RUNTIME_TEMPLATES[deep_book_6h].chapter_count = 12` is anomalous (third value); not the auto-plan value. |

**Anti-drift check:** No new spec authored. Registry becomes SSoT for `chapter_count_default`; Python's `FORMAT_CHAPTER_COUNTS` constant is removed in the follow-up Pearl_Dev refactor PR. The 6 Group B rulings preserve current runtime behavior; if any of these turns out to be a regression vs intended bestseller-grade output, the bestseller-smoke run under `ws_pr_d_wires_resume_20260505` will surface it (and the registry value can be edited deliberately). The `RUNTIME_TEMPLATES.chapter_count` vestigial field is left untouched (separate cleanup, low priority).

**Action items:**
1. Pearl_Dev (`ws_auto_plan_ssot_refactor_20260505`): edit `config/format_selection/format_registry.yaml` under `runtime_formats:` — add 10 Group A entries with `chapter_count_default` (Group A table values); update 6 Group B entries' `chapter_count_default` to the Group B ruling values. One config commit.
2. Pearl_Dev (same PR): remove `FORMAT_CHAPTER_COUNTS` dict from `phoenix_v4/planning/book_structure_plan.py`; replace the `n_chapters = chapter_count or FORMAT_CHAPTER_COUNTS.get(runtime_format, 10)` lookup at line 511 with a registry-aware reader (mirror the `_load_compact_chapter_subset` pattern landed in PR-Beta `0142d88337`). The fallback default 10 is preserved as a last-resort guard, but post-Group-A backfill no known runtime format should hit it. One code commit. Tests in `tests/test_book_structure_plan.py` updated.
3. Pearl_Dev (same PR): bestseller smoke on `gen_z_professionals × anxiety` (per `HANDOFF_bestseller_smoke_post_852_856 §11`) at minimum; opportunistically run `millennial_women_professionals × anxiety` if low-cost — verify the 16 Group A+B rulings produced no regression beyond the literal value adjustments (e.g., chapter_count = 10 still produces standard_book; etc.).
4. Pearl_PM (post-merge): close `ws_auto_plan_ssot_refactor_20260505` with the merged SHA + cite this amendment.

**Out-of-scope for the refactor PR (separate follow-ups):**
- `RUNTIME_TEMPLATES.chapter_count` vestigial field cleanup. Low priority; touch when next editing `book_structure_plan.py` for unrelated reasons.
- Reconciling format_selector's persona/structural clamping with auto-plan's direct read. Currently auto-plan does NOT apply that clamping. If a future change wants the two paths to produce identical chapter counts under all conditions, it's a separate cap-entry-level decision (auto-plan would need persona/structural context at the lookup site).

**Handoffs:**
- Pearl_Dev → resume `ws_auto_plan_ssot_refactor_20260505`; refactor PR ~80-120 lines (larger than original AUTO-PLAN-SSOT-01's ~30-50 estimate; unavoidable given backfill scope).
- Pearl_PM → post-merge: close `ws_auto_plan_ssot_refactor_20260505` (cite this amendment + the merged refactor SHA); update `proj_pearl_prime_bestseller_rebase_20260425.next_action` to reflect SSoT consolidation complete.

### TEMPLATE-UNIVERSAL-01 — Universal template = 12-chapter spine × 10-section grid × 3-variation floor (5 optional ceiling); chapter_count is per-format (decision approved 2026-05-06)

**Status:** **ratified — Option (c) hybrid** (operator framing reconciled with shipped behavior, 2026-05-06).
**Context:** Operator architecture ask — "Pearl Prime uses 12-chapter × 10-section × 5-variation universally." On inspection three of those four numbers are universal-at-spine-layer, but `chapter_count` was already adjudicated per-format under AUTO-PLAN-SSOT-01-AMENDMENT (16 of 20 formats explicit values; range 5-20). A naive ratification of "12 chapters universal" would silently retire 16 format adjudications. Re-investigation surfaced that the operator's universality claim holds at the **spine/registry** layer (`registry_resolver.load_registry` docstring: "Create registry/{topic}.yaml with 12 chapters × 10 sections × 5 variants"; `phoenix_v4/planning/registry_resolver.py:117`) but NOT at the **auto-plan output** layer (per-format `chapter_count_default` from `format_registry.yaml`).
**Decision:** **Option (c) hybrid.** The 12 × 10 × 5 framing is canonical at the **spine/registry source-of-truth layer**; auto-plan **subsets** that source per format via PR-D-SPINE-01's `compact_chapter_subset` declarative mechanism. Concretely:

| Layer | Universal? | Authority | Mechanism |
|---|---|---|---|
| **Spine/registry** (per-topic source) | **Yes** — 12 chapters × 10 sections × ≥3 variants | `registry/<topic>.yaml`; `SOMATIC_10_SLOT_GRID` at `phoenix_v4/planning/beatmap_compile.py:42` | Topic registries are authored at 12×10×{≥3} per the resolver docstring contract |
| **Auto-plan output** (per-book) | **No** — `chapter_count` per format | `format_registry.yaml:runtime_formats[].chapter_count_default` | `book_structure_plan.get_format_chapter_count` at `phoenix_v4/planning/book_structure_plan.py:46` reads registry; subsets via `_load_compact_chapter_subset` at `phoenix_v4/planning/knob_apply.py` per PR-D-SPINE-01 |
| **Variations floor** | **Yes** — 3 floor (5 optional ceiling per-section) | SPEC-739-THRESHOLD-01 | `min_variants_required: 5` per-section override available where curated |

The 10-section grid is unambiguously universal: every format renders against `SOMATIC_10_SLOT_GRID` (HOOK / STORY / REFLECTION / EXERCISE / STORY / TEACHER_DOCTRINE / REFLECTION / EXERCISE / STORY / INTEGRATION). The 3-variation floor is universal per SPEC-739-THRESHOLD-01 (not 5; 5 is opt-in via per-section `min_variants_required`). The 12-chapter SPINE is the topic registry's source-of-truth shape; per-book chapter_count is the auto-plan's subset over that 12-chapter spine. Rejected (a) literal universality (would retire AUTO-PLAN-SSOT-01-AMENDMENT and silently force 12 chapters on micro_book_15/compact_book_*/etc.). Rejected (b) reframe-as-implemented-without-spine-acknowledgement (loses operator's correct intuition that the 12×10×5 numbers ARE the canonical source-of-truth shape).

**Anti-drift check:** No new spec authored. The hybrid recognition aligns with two already-ratified cap entries (AUTO-PLAN-SSOT-01 + AMENDMENT for chapter_count; SPEC-739-THRESHOLD-01 for variations floor) and with the existing spine architecture (12-chapter topic registry + per-format subset). Reframes operator's "universally" question as "at which layer?" — universal at spine, per-format at auto-plan.

**Action items:**
1. Pearl_Dev (`ws_template_universal_audit_20260506`): grep for any registry/<topic>.yaml topic that does NOT have 12 chapters × 10 sections; surface as content gap (Pearl_Editor + Pearl_Writer ws would follow). Audit-only scope; no code changes.
2. Pearl_GitHub (`ws_template_universal_docs_index_note_20260506`): when next refreshing `docs/DOCS_INDEX.md`, add a routing note that the universal template is "12-chapter spine source-of-truth + per-format auto-plan subset" (cite this entry + AUTO-PLAN-SSOT-01-AMENDMENT + PR-D-SPINE-01).
3. No spec edit. No code edit. AUTO-PLAN-SSOT-01-AMENDMENT's 16 format rulings stand.

**Handoffs:**
- Pearl_Dev → `ws_template_universal_audit_20260506` → trigger = this cap-entry PR merged.
- Pearl_GitHub → `ws_template_universal_docs_index_note_20260506` → trigger = next DOCS_INDEX refresh (low priority; piggyback).

### BESTSELLER-INJECTIONS-MANDATORY-01 — Bestseller injections mandatory for `--quality-profile production`; STORY at sec 2/5/9 architecturally mandatory across all profiles (decision approved 2026-05-06)

**Status:** **ratified — Option (a) profile-gated for non-grid injections; grid-architectural for STORY-at-SCENE** (2026-05-06).
**Context:** Operator architecture ask — "bestseller injections (named characters, story_plan/HARDSHIP at sec 2/5/9, journey_intro at sec 4/8, EI v2 gate, exercise_journeys) ALWAYS applied or gated on quality_profile?" Investigation surfaces that the question conflates two architecturally distinct injection mechanisms: (1) **grid-level injections** (sec 2/5/9 STORY slots producing `story_plan/HARDSHIP` named-character output via `phoenix_v4/planning/beatmap_compile.py:42 SOMATIC_10_SLOT_GRID` post-PR #669 SCENE→STORY swap) which run on every render regardless of profile, and (2) **flag-level injections** (`--exercise-journeys` controlling `attach_exercise_journeys` at `scripts/run_pipeline.py:619`; `--quality-profile production` enabling enrichment-gap hard-fail at `:568` and EI v2 gate blocking at `:269 _block_on_fail`) which are CLI-flag-gated.
**Decision:** **mandatory for production; grid-architectural for STORY**. The two mechanisms preserve distinct contracts:

| Injection | Mechanism | Always-on? | Citation |
|---|---|---|---|
| `story_plan/HARDSHIP` at sec 2/5/9 (named characters) | `SOMATIC_10_SLOT_GRID` STORY slots; engine bank via `persona_atoms["STORY"]`; `enrichment_select.py` waterfall | **YES — architecturally** (every render, every profile) | `phoenix_v4/planning/beatmap_compile.py:42-52`; BG-PR-09 closure entry above |
| `journey_intro:awareness/regulation` at sec 4/8 EXERCISE | `attach_exercise_journeys` via `--exercise-journeys` flag | **YES for production** (canonical CLI default; bestseller smoke gates on this) | `scripts/run_pipeline.py:619-621` |
| EI v2 gate | `quality_profile in {production, flagship}` | **YES for production** (blocking); flagship advisory; draft/debug skip | `scripts/run_pipeline.py:269-278 _block_on_fail` |
| Enrichment-gap hard-fail | `quality_profile == "production"` | **YES for production** | `scripts/run_pipeline.py:567-579` |
| Named-character story atoms (engine bank) | `atoms/<persona>/<topic>/<engine>/CANONICAL.txt` waterfall | **YES — content-dependent** (where present; per-persona content gap) | `enrichment_select.py:931-935` |

Rejected (b) "MANDATORY across all profiles" — would force production-grade gates on draft/debug runs which exist precisely to allow iteration without those gates. Rejected (c) "per-injection gating without overall posture" — already implemented; the question is what the canonical posture *is*, not whether per-injection gates exist. The canonical posture is: **`--quality-profile production` is the bestseller-grade contract**; the canonical CLI in `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` declares this. STORY-at-SCENE is grid-mandatory because the slot grid itself is the architecture (PR #669 made STORY the slot type at sec 2/5/9; non-architectural to opt out).

**Anti-drift check:** No new spec authored. The decision codifies what `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md:570-577` already declares (production CLI is canonical) and what BG-PR-09's PR #669 closure already shipped (grid-mandatory STORY at sec 2/5/9). Surfaces the architectural distinction (grid-level vs flag-level) so future-you doesn't accidentally route grid-level questions to flag-level mechanisms.

**Action items:**
1. Pearl_Dev (`ws_bestseller_injections_audit_20260506`): audit-only scope — verify the canonical CLI default in `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md:570-577` includes `--quality-profile production --exercise-journeys` (NOT optional). If the spec text does not declare this default explicitly, surface a 1-line spec edit (Pearl_Architect follow-up). No code changes from this audit.
2. Pearl_Editor + Pearl_Writer (FOLLOWUP, content-not-code): the named-character engine bank (`atoms/<persona>/<topic>/<engine>/CANONICAL.txt`) coverage is the dominant variable in whether grid-mandatory STORY at sec 2/5/9 produces named-character output. Per existing `proj_pearl_prime_bestseller_rebase_20260425.open_questions`, midlife_women has zero master_arcs; covered as separate routing under that project. Not opened here.
3. Pearl_GitHub: when refreshing `docs/DOCS_INDEX.md`, add a one-line routing note that "`--quality-profile production` is the canonical bestseller-grade CLI flag-set" pointing at `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md:570-577`.

**Handoffs:**
- Pearl_Dev → `ws_bestseller_injections_audit_20260506` → trigger = this cap-entry PR merged.
- Pearl_Editor + Pearl_Writer → ongoing engine-bank coverage authoring under existing per-persona ws's; no new ws opened by this entry.
- Pearl_GitHub → DOCS_INDEX routing note (low priority; piggyback).

### CATALOG-800-PER-BRAND-01 — 800 high-confidence configs is system-wide total (not per-brand); reframe operator ask + open data-artifact ws (decision approved 2026-05-06)

**Status:** **ratified — reframe-as-target with data-artifact follow-up** (2026-05-06).
**Context:** Operator architecture ask — "does the catalog planner generate 800 configs per brand from marketing research?" Anchor at `artifacts/research/full_content_audit.md:65` defines the 800 as **HIGH CONFIDENCE (market-validated) — Brand's primary topic + primary persona + proven format + top 5 locales (en-US, de-DE, ja-JP, ko-KR, fr-FR)** out of a 7,020,000-config theoretical maximum. Math from the anchor: 24 archetypes × ~4 primary topics × ~2.5 primary personas × ~3 proven formats × 5 top locales ≈ 720-1,080 → rounds to ~800 **system-wide**, NOT 800 per brand. The auto-memory entry for "800 high-confidence configs" already records this correctly (`Operator's '800 books per brand' = ~800 high-confidence catalog configs (brand×topic×persona×format×locale) per artifacts/research/full_content_audit.md:65. The $-makers tier.`). Current shipped catalog enumeration: `artifacts/catalog/brand1_author_distribution_en_US.csv` (192 rows = brand-1 × en_US only, single locale, single brand) via `scripts/catalog_visibility/distribute_brand1_to_authors.py`.
**Decision:** **ratify-as-target with reframe.** The 800 is the system-wide $-maker tier per the anchor; the planner does NOT today output 800 system-wide (it outputs 192 brand-1×en_US rows). Bridging the gap is a **data-artifact** ws, not a spec ws and not a code-architecture ws. Output target: `artifacts/catalog/high_confidence_catalog_v1.tsv` (or .csv) with columns `brand`, `topic`, `persona`, `format`, `locale`, `confidence_tier=high`, `source_evidence`. The Pearl_Research methodology already exists in the anchor doc (Part 2: cluster-based market viability scoring across 45 clusters); the ws operationalizes it across all 24 book archetypes (per BR-CANON-01 Path X — the manga axis is separately governed by `docs/GENRE_PORTFOLIO_PLAN.md` + per-locale plans).

Rejected (a) "ratify-as-implemented if 800/brand IS today's output" — it isn't (192 rows, single brand, single locale). Rejected (c) "descope" — the 800 tier is the canonical $-maker target per the anchor; descoping it would retire the anchor's load-bearing claim. The anchor stands; the planner needs to catch up via a Pearl_Research/Pearl_Marketing data-artifact ws.

**Anti-drift check:** No new spec authored. No new master plan doc (MASTER-CATALOG-01 closed-not-needed; the per-axis canon at `docs/GENRE_PORTFOLIO_PLAN.md` + `docs/CJK_CATALOG_PLAN.md` + `docs/US_CATALOG_PLAN.md` retains authority). The high-confidence catalog TSV is a **data-artifact** within the existing per-axis canon, NOT a parallel plan-doc. Operator's "800 per brand" framing is reframed in this entry's text + in memory; future operator asks reuse the system-wide framing.

**Action items:**
1. Pearl_Research + Pearl_Marketing (`ws_catalog_800_high_confidence_artifact_20260506`): operationalize the anchor's market-viability methodology (`artifacts/research/full_content_audit.md` Part 2) across all 24 book archetypes × primary topics × primary personas × proven formats × top 5 locales. Output: `artifacts/catalog/high_confidence_catalog_v1.tsv`. Method: walk `config/brand_registry.yaml` brand-by-brand; for each brand pull primary_topics + primary_personas; cross with proven formats per `format_registry.yaml`; emit one row per (brand × topic × persona × format × locale) tuple where confidence is high per the anchor's cluster scores. Iteration cap = 1 PR; no code changes (data only, optional small generator script).
2. Pearl_Dev (FOLLOWUP, separate ws if needed): if the data-artifact reveals the existing planner (`scripts/catalog_visibility/distribute_brand1_to_authors.py`) needs generalization beyond brand-1×en_US to consume the 800-row TSV, open `ws_catalog_planner_generalization_20260506` (Pearl_Dev). NOT opened here; gated on the artifact ws producing actionable evidence.
3. Pearl_GitHub: when next refreshing `docs/DOCS_INDEX.md`, add a routing note that "high-confidence catalog tier = ~800 system-wide per `artifacts/research/full_content_audit.md:65`" pointing at the artifact TSV (after it lands).

**Handoffs:**
- Pearl_Research + Pearl_Marketing → `ws_catalog_800_high_confidence_artifact_20260506` → trigger = this cap-entry PR merged.
- Pearl_Dev → optional `ws_catalog_planner_generalization_20260506` → trigger = artifact ws produces evidence requiring planner code changes.
- Pearl_GitHub → DOCS_INDEX routing note → trigger = artifact TSV lands.

### PEARL-EDITOR-UPSTREAM-01 — Pearl_Editor owns content authority for teacher_banks + atom authoring lanes; "upstream" = authority-flow not pipeline-stage (decision approved 2026-05-06)

**Status:** **ratified — Option (c) hybrid** (operator framing reframed as authority-flow, 2026-05-06).
**Context:** Operator architecture ask — "Pearl_Editor sits upstream of Pearl_Prime." `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` already records: `teacher_mode | docs/SYSTEMS_V4.md;specs/PHOENIX_V4_5_WRITER_SPEC.md | SOURCE_OF_TRUTH/teacher_banks/;config/authoring/pen_name_teacher_profiles.yaml | Pearl_Editor | active`. So Pearl_Editor IS the active authority owner of teacher_banks, which Pearl_Prime's render pipeline reads as overlay content (`phoenix_v4/planning/registry_resolver.py:51-67`). The "upstream" framing is correct as **authority-flow** (content authority precedes render consumption) but not as **pipeline-stage** (Pearl_Editor isn't a runtime pipeline step that fires before Pearl_Prime).
**Decision:** **Option (c) hybrid.** Pearl_Editor's authority scope:

| Authority | Status | Path | Spec |
|---|---|---|---|
| `teacher_banks/<teacher>/doctrine/` | **owned today** (existing) | `SOURCE_OF_TRUTH/teacher_banks/` | `docs/SYSTEMS_V4.md` teacher mode |
| `teacher_banks/<teacher>/approved_atoms/<TYPE>/` | **owned today** (existing) | same | `PHOENIX_V4_5_WRITER_SPEC §4.5` (EXERCISE three-source); SPEC-739-VALIDATOR-MULTISOURCE-01 ratified per-spec scope |
| `config/authoring/pen_name_teacher_profiles.yaml` | **owned today** (existing) | same | per SUBSYSTEM_AUTHORITY_MAP |
| `atoms/<persona>/<topic>/<TYPE>/CANONICAL.txt` (persona-keyed atoms) | **co-owned with Pearl_Writer** (existing practice via atom_gap_fill / story_cell_authoring lanes) | `atoms/` | `PHOENIX_V4_5_WRITER_SPEC §3` |
| `SOURCE_OF_TRUTH/musician_banks/<id>/` (NEW under MUSIC-MODE-V1-01 below) | **expand to own** (recommended this entry) | `SOURCE_OF_TRUTH/musician_banks/` | per MUSIC-MODE-V1-01 |

Pearl_Editor is the content-authority node; Pearl_Prime's render pipeline is the consumption node. "Upstream" reframes correctly as authority precedes render. **Pearl_Editor is NOT inserted as a runtime pipeline step** (which would require new pipeline architecture); the existing read-overlay mechanism in `registry_resolver.py:415-462` is the integration point and stays unchanged. Rejected (a) "ratify upstream as new runtime pipeline step" — would require new spec authoring (out-of-scope for cap entries) and a new pipeline stage; the existing overlay mechanism already produces the desired effect. Rejected (b) "ratify current scope without authority-flow reframe" — loses operator's correct intuition that content authority should precede render consumption.

**Anti-drift check:** No new spec authored. SUBSYSTEM_AUTHORITY_MAP row stays as-is for `teacher_mode`; this entry adds clarity on what "upstream" means architecturally without expanding Pearl_Editor's runtime role. The musician_banks expansion lands cleanly under MUSIC-MODE-V1-01 below (which routes ownership to Pearl_Editor consistent with this entry's authority-flow framing).

**Action items:**
1. Pearl_PM: add a `pearl_editor_scope` open question to `proj_pearl_prime_bestseller_rebase_20260425` capturing "should atoms/<persona>/* be promoted to a full Pearl_Editor authority row in SUBSYSTEM_AUTHORITY_MAP, or remain co-owned with Pearl_Writer via existing atom_gap_fill / story_cell_authoring practice?" — defer the formal decision until catalog 800 data-artifact (CATALOG-800-PER-BRAND-01) reveals scale-of-authoring-needed pressure.
2. Pearl_GitHub: when next refreshing `docs/DOCS_INDEX.md` or `docs/OWNERSHIP_MATRIX.md`, add a routing note that Pearl_Editor's authority is **content authority** (read-overlay model), not a runtime pipeline stage; cite this entry.
3. NO spec authored under this entry. NO subsystem authority map edit beyond MUSIC-MODE-V1-01's musician_banks row addition (covered there).

**Handoffs:**
- Pearl_PM → open-question add on `proj_pearl_prime_bestseller_rebase_20260425` → trigger = this cap-entry PR merged.
- Pearl_GitHub → DOCS_INDEX/OWNERSHIP_MATRIX routing note (low priority; piggyback) → trigger = next refresh.
- No Pearl_Dev ws opened by this entry.

### EXERCISE-BANK-RESOLUTION-01 — Strict-canonical EXERCISE for `--quality-profile production`; gratitude_practices content authoring is separate (decision approved 2026-05-06)

**Status:** **ratified — Option 1 (strict-canonical for production)** (operator decision 2026-05-06; PR #893 diagnosis merged).
**Context:** PR #893 (`agent/exercise-bank-diagnosis-20260506`, MERGED) authored `docs/EXERCISE_BANK_ENFORCEMENT_DIAGNOSIS_2026-05-06.md` (~209 lines, single-file diagnosis MD; no code/specs/configs touched). Findings:
- 37-somatic bank exists at `SOURCE_OF_TRUTH/practice_library/inbox/exercises_ab_tady_37_PRODUCTION_READY.json` (39 items with full 5-part `components`).
- 9-types bank exists for 8 of 9 types (`*_library_34_PRODUCTION_READY.json` × 8 = 272 items); `gratitude_practices` is **absent on disk** (content authoring gap).
- 5-part structure (`bridge + intro + description + aha + integration`) reaches the rendered book via `practice_library_loader.py` + `chapter_composer` (`/tmp/bestseller_smoke_ssot_refactor_genz/book.txt` verified).
- `library_34 FALLBACK` warning name is misleading: per spec §4.5 the practice_library IS the third source (`atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt` → `teacher_banks/<teacher>/approved_atoms/EXERCISE/*.yaml` → `practice_library`). Current behavior matches spec; the warning text drifts from spec.
- For `gen_z_professionals × anxiety` the persona-atom + teacher_banks EXERCISE sources are empty (#887 atom backfill explicitly deferred EXERCISE), so the third-source fall-through fires correctly per spec.

PR #893 surfaced three options: (1) **Strict-canonical EXERCISE for `production` profile** (~20-30 lines in `scripts/run_pipeline.py` raising `EnrichmentGapError` when EXERCISE falls through to practice_library; production must use persona-atom OR teacher_banks); (2) re-ingest practice_library with components preserved + collapse parallel paths (~50-100 lines, multi-file); (3) cosmetic log rename + audit `source_id` traceability (~15 lines). Diagnosis recommended (1).

**Decision:** **Option 1 — strict-canonical for `--quality-profile production`.** Reasoning: (i) honors operator intent that production books use **persona-keyed or teacher-keyed** EXERCISE content (where authoring quality is highest), reserving practice_library for non-production iteration; (ii) makes the existing `--quality-profile` posture (BESTSELLER-INJECTIONS-MANDATORY-01) consistent across EXERCISE alongside enrichment-gap hard-fail and EI v2 gate; (iii) surfaces #887's deferred EXERCISE atom backfill as a hard signal (production rejects until the atoms exist), forcing the content-gap to the foreground rather than masking it with practice_library fallback; (iv) the practice_library third-source remains valid for `--quality-profile draft/debug/flagship` so iteration is unblocked. Rejected (2): structural multi-file refactor is right long-term but is **out of this cap-entry's routing scope** (separate Pearl_Architect ruling needed if pursued). Rejected (3): cosmetic-only log rename doesn't change behavior; the log message reframe should ride along with Option 1's PR (free) but is not the load-bearing change.

**The 9th content type `gratitude_practices` is a CONTENT AUTHORING gap, NOT this entry's architectural concern.** Pearl_Editor + Pearl_Writer ws opened separately for the bank authoring; independent of the strict-canonical ruling.

**Anti-drift check:** No new spec authored. The strict-canonical mode is a **behavior tightening** of the existing `--quality-profile production` posture, not a new gate. The third-source practice_library remains spec-§4.5-canonical for non-production profiles. The misleading log message ("library_34 FALLBACK") is rewriteable in the same Pearl_Dev PR (free piggyback) to restore spec-text-fidelity. Surfaces #887's deferred EXERCISE atom gap as a forcing function.

**Action items:**
1. Pearl_Dev (`ws_exercise_strict_canonical_production_20260506`): edit `scripts/run_pipeline.py` to raise `EnrichmentGapError` when EXERCISE resolution falls through to `practice_library` AND `quality_profile == "production"`. Estimated ~20-30 lines per PR #893 diagnosis. Free piggyback: rewrite the misleading log warning at `phoenix_v4/exercises/practice_library_loader.py` from "EXERCISE FALLBACK: Using library_34" to "EXERCISE: Using practice_library per spec §4.5". Tests: pin the error path under production profile + the pass path under draft/debug/flagship.
2. Pearl_Editor + Pearl_Writer (`ws_gratitude_practices_authoring_20260506`): author the 9th content type bank `gratitude_practices_library_34_PRODUCTION_READY.json` mirroring the existing 8 types' schema (5-part components per item; ~34 items per content-bank precedent). Independent of Pearl_Dev's ruling; can ship in parallel.
3. Pearl_Editor + Pearl_Writer (FOLLOWUP, content-not-code): EXERCISE atom backfill for `gen_z_professionals × anxiety` (and other personas where production runs would now hard-fail). Per `proj_pearl_prime_bestseller_rebase_20260425.open_questions` master_arcs gap list. NOT opened by this entry; covered under existing project ws's.

**Handoffs:**
- Pearl_Dev → `ws_exercise_strict_canonical_production_20260506` → trigger = this cap-entry PR merged.
- Pearl_Editor + Pearl_Writer → `ws_gratitude_practices_authoring_20260506` → trigger = this cap-entry PR merged.
- Pearl_Editor + Pearl_Writer → ongoing EXERCISE atom backfill under existing per-persona ws's.

### QUOTE-ATOM-ROUTING-01 — Retire ~9 persona-keyed QUOTE atoms as orphan (no canonical slot grid entry); migrate content to TEACHER_DOCTRINE / REFLECTION / INTEGRATION (decision approved 2026-05-06)

**Status:** **ratified — Option (d) retire-as-orphan + content migration** (operator decision 2026-05-06; F3 deferred from PR #903).
**Context:** PR #903 atom-usage audit F3: `atoms/<persona>/<topic>/QUOTE/CANONICAL.txt` files exist (~9 affected — primarily ahjan-authored) but **no entry in `_TEACHER_TYPE_MAP`, no membership in `_PERSONA_OVERLAY_TYPES`, no membership in `_TEACHER_OVERLAY_TYPES`, and no QUOTE slot in `SOMATIC_10_SLOT_GRID`**. They never load. Re-investigation per TEMPLATE-UNIVERSAL-01: the canonical 10-section grid is HOOK / STORY / REFLECTION / EXERCISE / STORY / TEACHER_DOCTRINE / REFLECTION / EXERCISE / STORY / INTEGRATION — no QUOTE. Adding QUOTE to `_PERSONA_OVERLAY_TYPES` would not route the 9 atoms because no chapter section has `section_type=QUOTE`.

Four routing options were considered: (a) alias QUOTE → TEACHER_DOCTRINE in `_TEACHER_TYPE_MAP` (mirror F2's TEACHING fix; ~1 line); (b) alias QUOTE → PERMISSION; (c) introduce QUOTE as a new canonical 10-section grid entry (architectural — would require spec edit on `PHOENIX_V4_5_WRITER_SPEC.md` AND a new `SOMATIC_10_SLOT_GRID` slot, retiring or expanding the 10-section canon); (d) retire as orphan + migrate content.

**Decision:** **Option (d) — retire-as-orphan; Pearl_Editor migrates content.** Reasoning: (i) the 10-section grid is canonical per TEMPLATE-UNIVERSAL-01 (this batch); introducing an 11th slot type is architectural change requiring spec authority (out of this entry's scope); (ii) F2's TEACHING fix worked because `TEACHING/` lived in `teacher_banks/<teacher>/approved_atoms/` (teacher-keyed; aliasable as TEACHER_DOCTRINE alternate dir name) — F3's QUOTE atoms live in `atoms/<persona>/<topic>/QUOTE/` (persona-keyed; different shape; not aliasable as a teacher-bank alternate); (iii) aliasing persona-keyed QUOTE into the teacher overlay path would cross authority boundaries (Pearl_Editor's teacher_banks vs persona atoms co-owned with Pearl_Writer per PEARL-EDITOR-UPSTREAM-01); (iv) the 9 atoms appear to be a content-authoring experiment at a non-canonical slot type — Pearl_Editor reviews each atom and re-files content into TEACHER_DOCTRINE / REFLECTION / INTEGRATION (whichever fits) under the correct persona-keyed slot directory, OR retires individual atoms whose content doesn't fit anywhere canonical.

Rejected (a) and (b): both require aliasing persona-keyed atoms into teacher-overlay or other paths in `_TEACHER_TYPE_MAP`, which crosses authority boundaries (teacher-bank lookups don't read `atoms/<persona>/<topic>/`). Rejected (c): introducing QUOTE as 11th canonical slot is architectural, requires spec authority, and is disproportionate to 9 atoms.

**Anti-drift check:** No new spec authored. No new code shape. The retire-and-migrate path preserves the canonical 10-section grid (per TEMPLATE-UNIVERSAL-01) and respects authority boundaries (per PEARL-EDITOR-UPSTREAM-01). Cleanup is content authoring (Pearl_Editor's lane), not code.

**Action items:**
1. Pearl_Editor (`ws_quote_atom_orphan_migration_20260506`): inventory the ~9 `atoms/<persona>/<topic>/QUOTE/CANONICAL.txt` files (`find atoms -name CANONICAL.txt -path '*/QUOTE/*'`). For each: read content; pick best-fit canonical slot (TEACHER_DOCTRINE / REFLECTION / INTEGRATION typical for quote-style content); re-author at `atoms/<persona>/<topic>/<TARGET_SLOT>/CANONICAL.txt` (append to the existing variant list rather than overwrite); delete the source `QUOTE/` directory tree. Pearl_Writer pairs if content needs adaptation. Single-PR scope; no code changes.
2. Pearl_Dev (CLOSED-NOT-NEEDED; do not open ws): no `_TEACHER_TYPE_MAP` edit, no `_PERSONA_OVERLAY_TYPES` edit, no `SOMATIC_10_SLOT_GRID` edit. F3 closes via content migration only.
3. Pearl_PM: close `ws_quote_atom_routing_fix_20260506` (if pre-emptively opened) status=resolved-by-QUOTE-ATOM-ROUTING-01-as-content-migration.

**Handoffs:**
- Pearl_Editor + Pearl_Writer → `ws_quote_atom_orphan_migration_20260506` → trigger = this cap-entry PR merged.
- Pearl_Dev → no ws opened (closed-not-needed at the code layer).
- Pearl_PM → `ws_quote_atom_routing_fix_20260506` (if exists) → close as resolved.

### TEACHER-POOL-SEMANTICS-01 — `_TEACHER_TYPE_MAP` lookup is first-match (intentional, deterministic); F7 closes as designed; ahjan TEACHING reachability via Pearl_Editor migration (decision approved 2026-05-06)

**Status:** **ratified — Option (a) keep first-match; Pearl_Editor content migration unblocks ahjan TEACHING reachability** (operator decision 2026-05-06; F7 deferred from PR #903).
**Context:** PR #903 atom-usage audit F7: `_TEACHER_TYPE_MAP` lookup at `phoenix_v4/planning/registry_resolver.py:425-429`:

```python
atom_pool: list[dict] = []
for dir_name in _TEACHER_TYPE_MAP.get(sec_type, [sec_type]):
    atom_pool = teacher_atoms.get(dir_name, [])
    if atom_pool:
        break
```

Behavior is **first-match** (overwrites `atom_pool` each iteration; breaks on first non-empty match). Audit framed it as undocumented; framing was wrong — code is unambiguously first-match. F2 fix added `"TEACHING"` to `_TEACHER_TYPE_MAP["TEACHER_DOCTRINE"]` = `["COMPRESSION", "REFLECTION", "TEACHING"]`. For ahjan: if ahjan has any COMPRESSION atoms, those win; the ~100 TEACHING atoms remain effectively unreached at slot-lookup time UNLESS COMPRESSION + REFLECTION are both empty. Switching to union semantics would unlock the 100 TEACHING atoms but changes the seed→atom mapping (the modulo over a larger pool produces different deterministic selections), which would invalidate cached bestseller-grade book outputs (gen_z_professionals × anxiety etc. on origin/main per BG-PR-09 closure verification).

Three options were considered: (a) keep first-match (deterministic; F7 closes as intentional); (b) switch to union (more diversity but changes seed→atom mapping); (c) hybrid — first-match for production; union for draft/debug.

**Decision:** **Option (a) — keep first-match.** Reasoning: (i) deterministic seed→atom mapping is **load-bearing for render-cache stability** — every cached bestseller-grade book on origin/main was rendered against the first-match contract; switching to union would silently drift cached vs fresh-render outputs; (ii) the F2 fix's TEACHING addition serves as a **safety net** — when a teacher has no COMPRESSION/REFLECTION, the TEACHING dir is now reachable (which is the original ghost-atom failure F2 addressed); (iii) ahjan's ~100 TEACHING atoms unreachability under first-match is a **content-authoring problem at the wrong directory**, not a code-semantics problem — Pearl_Editor migrates the 100 atoms into COMPRESSION (or REFLECTION) preserving first-match preference and unlocking the content for bestseller-grade renders; (iv) introducing flag-gated hybrid (Option c) adds CLI surface for a problem solvable at the content layer; respects "smaller change wins" and Arc-First minimalism.

Rejected (b): union breaks render-cache determinism without operator-approved cache regeneration; the cost (re-render the bestseller-grade catalog) is disproportionate to the benefit (one teacher's ~100 atoms reachable in their original location). Rejected (c) hybrid: adds a flag for a content-layer problem; over-engineering.

The first-match contract is now **explicitly documented**: `_TEACHER_TYPE_MAP[<TYPE>] = [primary_dir, fallback_dir, ...]`; lookup returns the first non-empty pool. Adding aliases (like F2's "TEACHING") expands the **fallback chain**, not the **active pool**. Future contributors should treat the aliases as ordered preferences.

**Anti-drift check:** No new spec authored. The decision codifies the existing code's intent and writes the contract into the cap entry as load-bearing reference. The Pearl_Editor migration ws unblocks ahjan content reachability without any code change. Render-cache stability is preserved.

**Action items:**
1. Pearl_Editor + Pearl_Writer (`ws_ahjan_teaching_atoms_migration_20260506`): inventory ahjan's `SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/TEACHING/*.yaml` files. For each: re-file as `SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/COMPRESSION/<atom_id>.yaml` (or REFLECTION if content fit is better); delete source TEACHING/ tree after migration. Use first-match preference: COMPRESSION wins for teacher-doctrine voice; REFLECTION for reflective voice. Single-PR scope; no code changes.
2. Pearl_Dev (`ws_teacher_pool_semantics_doc_pin_20260506` — OPTIONAL, low priority): add a 5-line docstring above `_TEACHER_TYPE_MAP` at `phoenix_v4/planning/registry_resolver.py:58` documenting the first-match contract explicitly so a future maintainer doesn't switch it to union without operator approval. ~5-line doc patch; no behavior change. Free piggyback on any future `registry_resolver.py` edit; not urgent.
3. Pearl_Architect (FUTURE, deferred): if/when the operator approves a cache-regeneration pass for the bestseller-grade catalog, re-open this question for union-pool consideration — but not before. Not opened here.

**Handoffs:**
- Pearl_Editor + Pearl_Writer → `ws_ahjan_teaching_atoms_migration_20260506` → trigger = this cap-entry PR merged.
- Pearl_Dev → optional `ws_teacher_pool_semantics_doc_pin_20260506` (low priority; free piggyback).
- Pearl_Architect → no follow-up ws opened; reopen only on cache-regeneration approval.

### MUSIC-MODE-V1-01 — Pearl Prime music overlay V1 ratified-as-drafted; subsystem `music_mode` owner = Pearl_Editor (decision approved 2026-05-06)

**Status:** **ratified** (operator decision 2026-05-06; supersedes draft "RECOMMENDED 2026-05-06" on PR #902 head ref).
**Merge-order note:** This batch's coordination PR and PR #902 (`agent/music-mode-v1-implementation-20260506`) carry mutual draft text on this entry. If this batch's PR merges first, PR #902's rebase auto-resolves the duplicate header (this batch's "ratified" entry wins; PR #902's "recommended" draft is discarded by rebase). If PR #902 merges first, this batch's PR rebase replaces the "recommended" draft with this "ratified" entry in place. Either order is safe; operator merges in QA pass per the session's coordination notes.
**Context:** Pearl_Dev draft on PR #902 implemented Pearl Prime music overlay V1: two render variants (`with-lyrics`, `no-lyrics`); second-person intro and conclusion; per-chapter opening, closing, and one mid-chapter bestseller-beat block; one MusicGen companion prompt per book for brand-admin packaging. Discovery reference: `artifacts/qa/music_mode_discovery_2026-05-06.md` (PR #898 head when available). Implementation:
- New `SOURCE_OF_TRUTH/musician_banks/<id>/` mirrors `teacher_banks/` atom layout.
- `--music-mode` is **orthogonal** to `--pipeline-mode` (additive overlay).
- 6 new slot pool directory names under `approved_atoms/`: `LYRIC_OPENING`, `LYRIC_CLOSING`, `LYRIC_BESTSELLER_BEAT`, `MUSIC_REFLECTION_OPENING`, `MUSIC_REFLECTION_CLOSING`, `MUSIC_REFLECTION_BESTSELLER_BEAT`.
- V1 seeded for `gen_z_professionals × anxiety` test musician `test_artist_alpha`; survey schema at `artifacts/musician_survey/SURVEY_TEMPLATE.yaml`.
- Companion audio: V1 ships **prompt JSON** via `scripts/music/generate_book_companion_song.py`; MusicGen runnable path remains Colab-oriented (`scripts/music/musicgen_colab.py` / Pearl Star). WAV export deferred until a supported local/scheduled runner is pinned.

Pearl_Dev's draft requested ratification on four specific points; this entry rules each.

**Decision:** **ratify-as-drafted with ownership clarified.** Per-point rulings:

| # | Question | Ruling | Rationale |
|---|---|---|---|
| 1 | Option A (ride existing pipeline) vs Option B (net-new `music_pipeline` subsystem) | **Option A** | Path X precedent (BR-CANON-01 Path X) — additive overlays preferred over net-new subsystems where existing pipeline can absorb. Music slots are **additive post-render injections** on `book.txt`; `SOMATIC_10_SLOT_GRID` and enrichment slot plans untouched (per draft anti-drift check). |
| 2 | `musician_banks/` subsystem owner: Pearl_Music? Pearl_Prime sub-mode? new agent? | **`music_mode` subsystem; owner = Pearl_Editor** | Consistent with PEARL-EDITOR-UPSTREAM-01 (this batch) — Pearl_Editor owns content authority for all banks (teacher_banks today; expand to musician_banks under this entry). Avoids minting a net-new agent (Pearl_Music) for a content-authoring lane that fits the existing Pearl_Editor authority shape. |
| 3 | Survey schema canonical at `artifacts/musician_survey/SURVEY_TEMPLATE.yaml` | **Yes — confirmed canonical** | Schema lives in `artifacts/` (data layer), not in `specs/` or `config/`. Appropriate placement for a survey artifact template. |
| 4 | Six new slot type names per Arc-First | **Confirmed as-named** | `LYRIC_*` and `MUSIC_REFLECTION_*` are descriptive, lane-specific (no collision with `SOMATIC_10_SLOT_GRID` slot names), and grouped semantically (LYRIC for lyrical content; MUSIC_REFLECTION for reflective text on the music). Names align with Arc-First's "additive overlays use distinct namespaces" pattern. |

Anti-drift check (additive on draft's own check): The music-mode subsystem expands Pearl_Editor's content-authority scope (per PEARL-EDITOR-UPSTREAM-01). It does NOT introduce a runtime pipeline stage; the existing post-render injection mechanism is the integration point. No new spec authored — `MUSIC_MODE_V1.md` (if Pearl_Dev's PR carries one) is operational documentation, not spec authority; the `music_mode` subsystem's spec authority is `docs/SYSTEMS_V4.md` (extended via Pearl_Editor follow-up if/when needed). The 6 slot names extend `approved_atoms/` directory conventions; no collision with the canonical 10-section grid.

**Action items:**
1. Pearl_GitHub (PR #902 reviewer): merge PR #902 per operator approval. Nothing in this ratification changes the implementation shape; the "recommended" status flip to "ratified" is the only delta vs PR #902's draft.
2. Pearl_PM (`ws_music_mode_v1_pilot_20260506`): administer survey to musician #1 (real, non-test); receive YAML; route to Pearl_Editor for first real `musician_banks/<id>/` authoring. Iteration cap = 1 musician per ws (V1 scope).
3. Pearl_Editor + Pearl_Writer (`ws_musician_banks_first_real_artist_20260506`): per-musician atom expansion from real survey YAML. Authors the 6 slot pools (`LYRIC_OPENING`/`CLOSING`/`BESTSELLER_BEAT`, `MUSIC_REFLECTION_OPENING`/`CLOSING`/`BESTSELLER_BEAT`) at `SOURCE_OF_TRUTH/musician_banks/<id>/approved_atoms/<SLOT>/<atom_id>.yaml`. Content authoring; no code.
4. Pearl_Architect (this entry's effect): add `music_mode | docs/SYSTEMS_V4.md | SOURCE_OF_TRUTH/musician_banks/;artifacts/musician_survey/SURVEY_TEMPLATE.yaml | Pearl_Editor | active` row to `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`. NOT done in this PR (cap entries are routing-only); flagged as Pearl_GitHub follow-up under `ws_subsystem_authority_map_music_mode_row_20260506`.

**Handoffs:**
- Pearl_GitHub → PR #902 merge (operator approval) → trigger = this cap-entry PR + PR #902 both ready.
- Pearl_PM → `ws_music_mode_v1_pilot_20260506` → trigger = PR #902 merged.
- Pearl_Editor + Pearl_Writer → `ws_musician_banks_first_real_artist_20260506` → trigger = first real survey YAML received.
- Pearl_GitHub → `ws_subsystem_authority_map_music_mode_row_20260506` → trigger = this cap-entry PR merged (small TSV row addition).

### MANGA-LAYERED-PIPELINE-V2-01 — V2 manga pipeline scope = 5 implementation phases + cross-cutting items, sourced from CHARACTER_INDIVIDUATION_PIPELINE_SPEC + 2026-04-29 community audit + 2026-05-02 attractor research (decision approved 2026-05-07)

**Status:** **ratified — comprehensive 5-phase scope; supersedes the dev-session V2 stub at `docs/MANGA_LAYERED_PIPELINE_V2_SCOPE.md` from PR #923** (operator decision 2026-05-07).

**Context:** Brand-2 V1 ship at PR #923 (and brand-1 at PR #918 before it) ran through a primitive single-render-per-panel pipeline — no character lock, no register lock, no QA gate, heuristic bubble placement, locale text baked at compose-time. The dev session that shipped V1 also opened a thin V2 pointer doc citing only the 7-item version of the scope (~5-7 engineering days). The operator surfaced ~25-30 specific assets already researched + license-verified across `artifacts/research/comfyui_workflow_audit_2026-04-29.md` (Top-5 forks: PuLID-Flux-II, Mickmumpitz, Char-Creator-3.0, PuLID+OpenPose+Janus anime, Kontext+PuLID — plus the recommended composite target), `docs/COMMUNITY_ASSETS_AUDIT_2026-04-29.md` (base-model + LoRA + workflow inventory), `artifacts/research/community_lora_roster_2026-04-29.yaml` (mecha / dark_fantasy / fantasy_adventure / healing license-tiered roster), `artifacts/research/jp_cn_specific_finds_2026-04-29.md` (Qwen-Image-Edit-2511 + ColorManga + Multiple-Angles-LoRA + Qwen-Image-i2L + Manga Editor Desu! + animeoutlineV4 recurring-baseline), `docs/FORK_WRAP_BUILD_DECISIONS_2026-04-29.md` (per-asset call), `artifacts/research/license_risk_register_2026-04-29.md` (FLUX-dev / Pony / NoobAI / Illustrious / InstantID-AntelopeV2 BLOCKED), `artifacts/research/integration_effort_estimates_2026-04-29.md` (Top-5 ROI = ~3 days + ~$50; full Phase-1 fork = ~14 engineer-days), `artifacts/research/average_face_problem_eval_2026-05-02.md` (4-tier ROI ranking; Qwen-Image weakest attractor of commercial-clean bases), `artifacts/research/dashboard_22_failure_diagnosis_2026-05-02.md` (visual evidence of 22 stillness_press protagonists collapsing to one Gaussian-attractor face), `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` (the 5-stage hybrid spec — V2 PRIMARY authority), `artifacts/research/webtoon_compositing_lettering_2026-04-25.md` (lettering-layer 20% gap: no SVG masters, no Source Han Sans / Noto CJK installed, no auto-tail-to-mouth, no per-locale text manifest separation, no SFX-on-art layer), plus per-genre prompt + drawing-tradition + cross-genre-blending + brand-LoRA configs already on main. The dev's stub is correct in spirit but materially under-scoped against this corpus.

**Decision:** **5-phase implementation per the authority sources. ~4-5 weeks Pearl_Dev wall-clock + ~$50 RunPod compute + ~3 hr operator review distributed across phases.** Each phase delivers independently-verifiable value so ratification can be incremental. Total component count by source: ~25-30. Phase budgets are honest engineer-days (per `integration_effort_estimates_2026-04-29.md`), not aspirational.

**Phase A — Character individuation core (~1 week).** Implements the spec's Stages 2-3-5 plus the cookbook + drawing-tradition + forbidden-tokens wiring. (A1) Constraint solver — 200-400 LOC Python per spec §2.2 pseudocode (5 same-brand / 7 cross-brand thresholds); REJECT returns colliding axes for author iteration. (A2) Prompt builder reading `config/manga/character_design_template.yaml` instances + `genre_prompt_cookbook_v2.yaml` + `drawing_tradition_per_genre.yaml` + (NEW) `config/manga/forbidden_tokens_registry.yaml` (file does not exist yet on main; Phase A creates it); per-base-model token strategy per spec §2.3 (Animagine = booru tag style; Qwen-Image = natural-language prose; FLUX-schnell = front-loaded). Replaces ad-hoc `panel_prompts.json` authoring with deterministic builder. (A3) QA harness wired to `facenet-pytorch` (commercial-clean VGGFace2) + cosine pairwise face-distance gate (<0.4 fail / 0.4-0.55 borderline manual / ≥0.55 pass per spec §2.5). (A4) Operator content task: fill 12-axis YAML for the 12 named teacher characters per `brand_lora_plans.yaml` (~15 min each = ~3 hr operator). (A5) `cross_genre_blending_rules.yaml` consultation hook for series spanning genres.

**Phase B — Base models + face lock (~1 week).** Migrates off FLUX-dev (license-blocked per `license_risk_register_2026-04-29.md`); installs commercial-clean PuLID. (B1) Add Qwen-Image base (Apache 2.0; weakest attractor per `average_face_problem_eval_2026-05-02.md`) — primary base for character work + speech-bubble text rendering. (B2) Add Animagine XL 4.0 (RAIL++-M) — secondary base for shojo / iyashikei / healing register where the attractor matches desired register. (B3) Keep FLUX-schnell as 4-step-cfg-1.0-euler-simple fallback per the configuration brand-2 V1 ship landed; drop FLUX-dev entirely. (B4) Pearl Star install of `lldacing/ComfyUI_PuLID_Flux_ll` with `PulidFluxFaceNetLoader` (NOT the InsightFace path — that's blocked via AntelopeV2 NC). (B5) `cubiq/PuLID_ComfyUI` install for the SDXL/Animagine path. (B6) Generate canonical reference character sheet PNG per teacher (12 sheets; reuse `artifacts/manga/image_bank/stillness_press/character_model_sheets.json` for ahjan since the model-sheet shape is documented). (B7) Wire reference-image input pathway into the prompt compiler (FaceNet conditioning per panel). (B8) Optional: evaluate Qwen-Image-i2L (one-image-to-LoRA) — gates per-character LoRA cost from ~10 min compute to seconds; bench validate Alibaba's claim before bundling.

**Phase C — Manga register + genre LoRAs + lettering layer (~1 week).** Closes the V1 register-oscillation defect AND the V1 lettering gap surfaced in operator's V1 ship caveats. (C1) `animeoutlineV4` LoRA — universal anime/manga lineart helper recurring across every JP/CN tutorial per `jp_cn_specific_finds_2026-04-29.md`. (C2) `lineart-anime-redmond` (LineAniRedmond) — pair at 0.7-1.0 with genre LoRAs. (C3) Halftone LoRA — operator picks between `H4LFT0N3_XL` (Civitai 320439) and `sh-halftone-v3` (Civitai 1685881); both 🟡 and require Civitai 6-flag verification before fork. (C4) Install `chflame163/ComfyUI_LayerStyle` (MIT) for halftone post-processing layer. (C5) Optional `sketch2manga` for screentone (🟡, license-verify). (C6) Per-character LoRA training for named recurring cast only (12-14 LoRAs per `brand_lora_plans.yaml`; `ai-toolkit (ostris, MIT)` per `FORK_WRAP_BUILD_DECISIONS_2026-04-29.md`; ~10 min compute per LoRA on H100; supplements PuLID for series-level consistency over 12+ chapters). NOT 200+ catalog LoRAs — that's where `community_lora_roster` triage rules (Animagine covers fantasy_adventure + healing without LoRA; cross-test Super Robot Diffusion XL on Animagine for mecha; train Phoenix-native only on cross-test failure). (C7) Brand-style LoRAs — 12 brand-style LoRAs same pipeline. (C8) Lettering layer per `webtoon_compositing_lettering_2026-04-25.md` 20%-gap punch list: install Source Han Sans + Noto Sans CJK Traditional/Simplified/Korean + Japanese SFX font (operator's V1 ja-JP WEBTOON-Japan caveat); SVG master bubbles (PNG-only doesn't survive 2× downscale); auto-tail-to-mouth speaker geometry (requires character bbox detection); per-locale text manifest separation (V1 baked text into bubbled PNGs — V2 emits one panel render + N locale text manifests for compose-time overlay per PR #631 Decision 1's 50-99× multi-market saving).

**Phase D — Anatomical correction (~1.5 weeks; research + integration sequential).** The gap operator flagged that wasn't in any prior research artifact. (D-research, ~3-4 days, Pearl_Research): scan canonical hand-correction tooling — `BadHands_v3`, `negative_hand_neg`, `EasyNegative_Hand`, `hand_v1.0`, Detail Tweaker XL for hands; FLUX-native `flux-hand-fix` and Hand Correction LoRAs. Face-detail enhancement LoRAs. Eye-detail LoRAs. ADetailer / face-restoration post-processing as a non-LoRA alternative that may obviate per-feature LoRAs. License-verify each candidate per the audit's Civitai 6-flag pattern. (D-integration, ~3-4 days, Pearl_Dev): wire selected negatives into the prompt builder's negative-prompt slot; wire selected positive-side LoRAs into the workflow JSON's LoRA loader stack; smoke-test on brand-2 ep_001 panel reruns; visual diff vs current V1 hand+face quality ships as `artifacts/qa/v1_v2_hand_face_diff_<date>.md`.

**Phase E — V1→V2 re-render + comparison (~3 days).** (E1) Re-render brand-1 ep_001 (PR #918 panels) + brand-2 ep_001 (PR #923 panels) through V2 pipeline. (E2) QA harness gate run per Phase A3 + face-distance metric across catalog. (E3) WD-EVA02-large-tagger-v3 install + reverse-prompt verification on samples (commercial-default manga tagger per `jp_cn_specific_finds_2026-04-29.md` §Qwen-VL-as-QA — Qwen-VL misreports panel content on comics, not a substitute). (E4) R2 V2 prefix upload to a separate prefix `s3://phoenix-omega-artifacts/manga/<series>/ep_001/v2/` so V1↔V2 is a directory diff. (E5) Operator visual review + decision gate: V2 promotes to default, OR V1 stays on WEBTOON Canvas with V2 archived for comparison.

**Cross-cutting (any phase).** (CC1) Fork-evaluate `Manga Editor Desu!` (NegiTurkey / ネギかも, JP OSS featured on Gigazine per `jp_cn_specific_finds_2026-04-29.md` §3) — orchestration tool that may obviate rebuilding `queue_panel_renders.py`-style drivers. License is 🟡 (free + Pro tier; verify before commit). Phase 2 evaluation per `FORK_WRAP_BUILD_DECISIONS_2026-04-29.md` §1.4. (CC2) `WD-EVA02-large-tagger-v3` install for QA harness — community-default manga tagger; not Qwen-VL. (CC3) Forbidden-tokens enforcement at prompt-build time (Phase A creates `config/manga/forbidden_tokens_registry.yaml`; runtime enforcement in the builder). (CC4) Brand × genre portfolio allocation pre-render check via `config/manga/brand_genre_allocation.yaml`. (CC5) `config/manga/cross_genre_blending_rules.yaml` consultation for cross-genre series.

**Phased value delivery.** After Phase A: catalog distinctness deterministic — 70% identity consistency from prompt stack alone per `average_face_problem_eval_2026-05-02.md` Tier 1. After Phase B: ~90% identity consistency (PuLID + reference + base swap closes another 20%). After Phase C: bestseller-grade manga register + lettering layer (V1 ja-JP WEBTOON-Japan publish gate clears). After Phase D: anatomical defects (hands, faces) closed. After Phase E: V1→V2 promotion decided per visual comparison.

**Anti-drift check:** Builds atop `CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` as PRIMARY authority — does NOT duplicate it. Phases A2 + A3 reference spec §2.3 + §2.5 verbatim; Phase B4 references audit Top-5 #2 (PuLID-Flux-II) verbatim. Honors PR-D-SPINE-01 + AUTO-PLAN-SSOT-01 patterns (no duplicate sources of truth — `character_design_axes.yaml` + `character_design_template.yaml` + `forbidden_tokens_registry.yaml` + `genre_prompt_cookbook_v2.yaml` + `drawing_tradition_per_genre.yaml` are each single-source-of-truth for their slice). Honors COVER-REGISTRY-01 (manga panels render-side; cover work is separate). Honors `license_risk_register_2026-04-29.md` BLOCKED list (no FLUX-dev, no Pony, no Illustrious-XL standalone, no InsightFace AntelopeV2, no Studio Ghibli LoRAs). BR-CANON-01 Path X axis preserved (manga pipeline distinct from book pipeline). Memory `feedback_validation_before_scaling` honored: Phase E re-render gates V2 promotion to default — V2 does not auto-replace V1 on WEBTOON Canvas. Memory `feedback_cover_text_overlay_two_stage` honored: Phase C8's lettering layer enforces "FLUX renders imagery only; PIL/SVG composites text" architecturally for panels too, not just covers.

**Action items:**
1. Pearl_PM: open the 6 ws rows below in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (this PR does it inline — items here track downstream coordination after merge).
2. Pearl_Int: license-verify each Civitai page in the per-phase fork list before each phase opens (~1.5 hr per phase per `integration_effort_estimates_2026-04-29.md`); update `scripts/ci/integration_env_registry.py` if a new env var is needed (e.g., Civitai API token if any auto-download is gated).
3. Pearl_Editor: own A4 character_design YAML authoring per teacher, B6 reference character sheet review per teacher, C7 brand-style LoRA per-brand voice profile review.
4. Pearl_Research: own `ws_manga_v2_phase_d_anatomical_research_20260507`; gated only on operator-go.
5. Pearl_Dev: phase-by-phase implementation per the 5 phase ws's; sub-divide if a phase's blast radius justifies it.
6. Pearl_GitHub: when this PR merges, mark `docs/MANGA_LAYERED_PIPELINE_V2_SCOPE.md` (PR #923's stub doc, if merged by then) as SUPERSEDED-BY-MANGA-LAYERED-PIPELINE-V2-01 in a small follow-up doc edit OR retire it entirely; this cap entry is the canonical V2 scope going forward.

**Handoffs:**
- Pearl_PM → `ws_manga_v2_phase_a_individuation_20260507` → trigger = this cap-entry PR merged + operator-approved Phase A start.
- Pearl_PM → `ws_manga_v2_phase_b_base_models_pulid_20260507` → trigger = Phase A's constraint solver + prompt builder + QA harness landed on main.
- Pearl_PM → `ws_manga_v2_phase_c_register_genre_loras_20260507` → trigger = Phase B's PuLID + base models live on Pearl Star.
- Pearl_Research → `ws_manga_v2_phase_d_anatomical_research_20260507` → trigger = operator-approved Phase D research start (parallel to A/B/C OK; gates the integration ws).
- Pearl_Dev → `ws_manga_v2_phase_d_anatomical_integration_20260507` → trigger = Phase D research ws closes with vetted asset list.
- Pearl_Dev → `ws_manga_v2_phase_e_re_render_smoke_20260507` → trigger = Phases A+B+C+D all merged.
- Pearl_GitHub → `ws_manga_v2_supersede_dev_stub_20260507` (small follow-up doc edit) → trigger = PR #923 merged + this cap-entry PR merged.

### QI-FOUNDATION-CANONICAL-RECONCILIATION-01 — `qi_foundation` alias in `brand_lora_plans` vs canonical **`qi_foundation_cultivation`** (PR #940 D1; ratification **proposed** 2026-05-08)

**Status:** **proposed** (cap + audit artifact only — YAML execution deferred to Pearl_Dev follow-up PR).

**Context:** PR #940 scoping discrepancy **D1**: `config/manga/brand_lora_plans.yaml` references **`qi_foundation`** — `brand_suffixes` binds suffix **`qf`** at **line ~27**; **`character_loras.master_feung`** (**lines ~67–73**) uses **`trigger_word: "feung_qf"`** and **`style_ref: qi_foundation`**; **`brand_style_loras`** Block **~159–163** uses root key **`qi_foundation`** with **`style_qf`**. **`config/manga/canonical_brand_list.yaml`** has **no** `qi_foundation` key; the Path-X manga brand exists as **`qi_foundation_cultivation`** (**~288–293** under `brands:`). Adjacent **`config/manga/*.yaml`** files (`brand_genre_allocation.yaml`, `manga_brand_series_plan.yaml`, `character_brand_registry.yaml`, `japan_dual_track_config.yaml`, `brand_illustration_styles.yaml`) still key **`qi_foundation`** — second-order drift; catalog series plans already cite **`brand_id: qi_foundation_cultivation`**. Project routing: **`proj_manga_catalog_reconciliation_20260426`** (canonical 37-brand registry governance per ACTIVE_PROJECTS).

**Decision:** **Direction B.** Do **not** add a 38ᵗʰ **`qi_foundation`** row to `canonical_brand_list.yaml` (**Direction A rejected** — would duplicate **`qi_foundation_cultivation`** and break Path X **37 manga brands** invariant). **`brand_lora_plans`** is subordinate configuration; it must consume **canonical `brand_id` strings**. Pearl_Dev fixes by **replacing** **`qi_foundation`** keys/refs with **`qi_foundation_cultivation`**, **retaining `qf`**/`feung_qf`/`style_qf` as suffix/trigger convention, and **rebinding `master_feung`** to the canonical brand. Optional extended sweep: rename **`qi_foundation`** → **`qi_foundation_cultivation`** in other `config/manga/*.yaml` call sites to remove inner-field contradictions (e.g. `character_brand_registry` **`brand_id: qi_foundation`**).

**Anti-drift:** Target CI invariant: **every** `brand_suffixes` key **and** every `style_ref` / `brand_style_loras` root key that denotes a **manga canonical brand** must satisfy **key ∈ `canonical_brand_list.brands`**. **Staged enforcement** (Pearl_DevOps + Pearl_Dev): **Phase 1** — land this cap’s Pearl_Dev YAML fix + add a **fatal check** for reintroduction of alias **`qi_foundation`** where canonical expects **`qi_foundation_cultivation`** in LoRA/teaching-plane configs. **Phase 2** — expand to full key-set crosswalk (note: `brand_suffixes` today uses other abbreviated slugs vs canonical full names — full strict mode may require a one-time alias map or broader rename batch; track under `proj_manga_catalog_reconciliation_20260426`).

**Action items:**
1. **Pearl_Dev:** follow-up PR — edit **`config/manga/brand_lora_plans.yaml`** per Direction B; optionally batch the §2 `config/manga/` alias sweep in same or sequenced PR.
2. **Pearl_DevOps** (primary CI gate owner) **+ Pearl_Dev** (domain script assist): add **`ws_brand_suffix_canonical_ci_20260508`** — CI script + workflow job implementing Phase 1 (alias regression) then Phase 2 (full ⊂-check or approved alias map).

**Handoffs:**
- **Pearl_Dev** → YAML execution PR → trigger = merge of this cap PR.
- **Pearl_DevOps** → CI workstream above → trigger = after Pearl_Dev lands Phase-1 YAML (or in parallel if check is forward-compatible).

**Budget:** This PR = **docs-only** (~2 files, ~0 engineering risk). Follow-up Pearl_Dev YAML PR = **small** (single-file minimum; **medium** if full `config/manga/` alias sweep). CI Phase 1 = **~0.5–1 eng-day** (script + workflow); Phase 2 = **backlog sized** after alias inventory.

**Audit artifact:** `artifacts/qa/qi_foundation_canonical_reconciliation_2026-05-08.md`.
### WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 — Worldwide catalog production go-live program audit (operator-ratified 2026-05-08; **Phase 1 P0 complete** 2026-05-10)

**Status:** **ACTIVE** — **Phase 1 P0** closed per **AMENDMENT-2026-05-10-PHASE-1-P0-COMPLETE** + **PR #1022** (Phase 1 P0 closure / activation evidence chain on `main`); **Phase 2 V1.1** execution begins per **AMENDMENT-2026-05-11-V1-1-37-BRAND-ACTIVATION** (program continues Phases **2–4** toward go-live; **Phase 4** exit criteria remain the only go-live definition).

**Context:** Operator requested a **single durable program** for **worldwide production go-live** framed as **37 brands × 4 locales** across the Pearl Prime / brand-admin / dashboard / pipeline surfaces. Past work fragmented into point fixes. This program **freezes** an honest **10-surface** audit (catalog planning, brand dashboard, weekly admin packaging, active-brand classification, author/bio matrix, marketing weekly volumes, spine CLI performance, executive dashboard, command UI ↔ CLI alignment, worktree/disk inventory) so every remediation references **one** `PROJECT_ID` and **named workstreams**.

**Scope note (Path X):** `BRAND_ADMIN_CANONICAL_PACKAGE.md` **lines 13–20** separate **book** vs **manga** registries. The operator’s **“37 brands”** language matches **manga canon** (`config/manga/canonical_brand_list.yaml` — **37** `brands:` keys) but **does not** match Pearl Prime **book-script** catalogs documented as **12–19 brands per locale** (`artifacts/catalog/pearl_prime_book_script_catalogs/README.md` **lines 17–20, 104–111**). The program **does not** collapse those axes without an explicit operator amendment.

**Decision:** Adopt the **Phase 1→4 roadmap** in `artifacts/qa/go_live_readiness_audit_2026-05-08.md` §Phase B **pending** operator confirmation (Q1).

**Anti-drift:**

1. Any agent doing point work on a listed surface **must** reference the matching **`ws_worldwide_gl_*`** row in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (or amend the program).  
2. Any **new surface** requires a **program amendment** (cap entry `AMENDMENT` + audit MD revision).  
3. **Production go-live** is defined **only** by **Phase 4 exit criteria** in the audit Markdown — not by individual HTML polish or catalog partials.

**Action items:**

1. Operator: answer **Q1–Q5** verbatim at `artifacts/qa/go_live_readiness_audit_2026-05-08.md` §Phase D.  
2. Pearl_PM: after answers, **activate** Phase 1 workstreams (status → `active` / `ready`) per priority (Q2).  
3. Per-surface owner agents as named in **Phase A** of the audit Markdown (Pearl_Architect, Pearl_Brand, Pearl_Dev, Pearl_DevOps, Pearl_Marketing, Pearl_GitHub, Pearl_Editor+Pearl_Writer as cited per surface).

**Handoffs:**

- **Pearl_PM (PRIMARY):** owns program coherence + phase gates.  
- **Surface owners:** as listed per surface in the audit (`artifacts/qa/go_live_readiness_audit_2026-05-08.md`).  
- **Pearl_Architect:** Path X reconciliation if operator collapses book vs manga scope (requires **AMENDMENT**).

**Budget:** Tier 1 (operator-present) for **design + ratification + phase prompts**; Tier 2 acceptable for unattended **catalog/pipeline regeneration** tasks **after** SSOT locks.

**Pointers:** `artifacts/qa/go_live_readiness_audit_2026-05-08.md`; `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md`; `artifacts/coordination/ACTIVE_PROJECTS.tsv`; `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`.

#### AMENDMENT 2026-05-08-PRIORITIES

**Status transition:** `proposed` -> `active` (operator decisions are the activation gate).

**Decision:** Operator ratifies phase order + per-surface priorities + Wave A recovery scope + active-brand SSOT + weekly cadence per Q1-Q5 above.

**Operator decisions (verbatim):**

- Q1 = yes (phase order: visibility -> wiring -> catalog -> go-live)
- Q2 priorities:
  - P0 = Surface 1 (Catalog planning), Surface 4 (Active/inactive brands), Surface 6 (Marketing volume SSOT) [all 3 RED surfaces]
  - P1 = Surface 2 (Brand dashboard), Surface 8 (Executive dashboard)
  - P2 = Surface 3 (Weekly packaging), Surface 5 (Author/bio), Surface 7 (Spine/CLI perf), Surface 9 (Command UI <-> CLI), Surface 10 (Disk/worktrees)
- Q3 = commit A1 (Pearl_Localization 12 scripts) + A2 (Pearl_Int CosyVoice2 audit TSV) + A5 (Pearl_Dev overlay Phase 1) + Pearl_DevOps CI hygiene (5 files); abandon A6 + stale drafts/contaminated worktree leftovers
- Q4 = brand_wizard YAML confirmed as canonical SSOT for active/inactive brand classification
- Q5 = Weekly cadence: Monday, both email + file delivery

**Anti-drift:**

- any agent doing point work on a P0 surface must reference its `ws_worldwide_gl_s0X` row
- any P-tier reassignment requires a separate AMENDMENT
- "active brand" definition is brand_wizard YAML presence -- ANY override requires AMENDMENT
- weekly download cadence is Monday email+file -- change requires AMENDMENT

**Action items:** Phase 1 P0 ws rows (s01, s04, s06) advance to `status=runnable`; router fans out implementation prompts in next turn.

**Handoffs:** Pearl_PM owns program; per-surface implementation owners assigned in ws rows.

#### WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 — AMENDMENT — 2026-05-09 (Pearl_Conductor autonomous wave Phase 1 P0 progress)

Phase 1 P0 progress captured (no operator decisions required; this AMENDMENT is a state-snapshot record):

1. **Surface 4 — Active Brand SSOT** — substantively shipped:
   - PR #972 (`10ed203bd6`) — active/inactive classifier (brand_wizard YAML SSOT) landed
   - PR #977 (`5b455bbf19`) — brand_admin dashboard panel consumer
   - PR #982 (`509fad6d56`) — brand_admin.html active classifier consumer (gating + ordering)
   - PR #987 (`1e28f4378a`) — Pearl Prime + full-catalog generators consume active classifier (helper module + per-brand gating)
   - **Status:** Surface 4 SSOT closed; consumers in flight on multiple surfaces.

2. **Surface 2 — Brand Dashboard** — partial:
   - PR #977 panel ships; broader binding (locale grids, podcast row, piece-level status) remains under `ws_worldwide_gl_s02_brand_dashboard_20260508`.

3. **Surface 6 — Marketing Volume SSOT** — substantively shipped:
   - PR #976 (`f4a872b937`) — discovery + V1 spec (`docs/specs/MARKETING_VOLUME_SSOT_V1_SPEC.md`)
   - PR #984 (`4c89fe1f19`) — `config/marketing/weekly_volumes_per_brand.yaml` V1 baseline (37 brands × 6 surfaces; status=draft awaiting Table 6 ratification)
   - **Status:** SSOT YAML on disk; consumer wiring (Surfaces 2/3/8) is next per spec §5 #4.

4. **Cross-cutting Pearl Prime feature/knob progress:**
   - PR #974 (`a5eb025a0a`) — FEATURE-KNOB P0-2 angle_registry alignment
   - PR #978 (`95cdb3be6f`) — FEATURE-KNOB P0-3 explicit angle_id per row
   - PR #986 (`071f4ee21b`) — FEATURE-KNOB P0-1 structural variation axes + stable signature
   - **Status:** P0-1/P0-2/P0-3 trio complete; downstream consumption auditable.

5. **Music-mode integration progress** (cross-ref MUSIC-MODE-BRAND-INTEGRATION-V1-01):
   - PR #973 (`465b772186`) — cap ratified
   - PR #975 (`38c6596f95`) — AMENDMENT 2026-05-09 (Q1-Q4 ratified; 6 ws runnable)
   - PR #981 (`4a26d3b35f`) — `config/music/music_brand_registry.yaml` SSOT schema+seed
   - PR #983 (`144a5437e7`) — wizard step 1 mode selector + step 4 survey pane
   - **Status:** registry + wizard pane shipped; survey-save POST + live-embed routes + 100%-music-mode catalog generator remain (deferred to next operator round).

6. **Freebie/funnel cap parallel** (cross-ref MUSIC-MODE-FREEBIE-FUNNEL-V1-02):
   - PR #979 — cap proposed
   - PR #989 — AMENDMENT operator Q1-Q3 ratified; cap proposed→active

**No new operator decisions required by this AMENDMENT.** It captures the state of the program after the autonomous wave so subsequent sessions can pick up cleanly. Outstanding open questions in the parent cap remain unchanged. Anti-drift: any future agent picking up Phase 1 P0 work should consult this AMENDMENT block before re-prompting on Surfaces 4/6 or feature/knob P0 axes.

Authorization: Pearl_Conductor 2026-05-09 autonomous wave (operator pre-approved orchestration).

#### WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 — AMENDMENT — 2026-05-10 (Phase 1 P0 progress snapshot — per-surface completed/remaining matrix)

**Purpose:** State-snapshot record after Phase 1 P0 implementations landed on `main`. No new operator decisions. Anchors the program to `main` HEAD so subsequent sessions can resume from a known point without re-reading every prior PR.

**`main` HEAD anchor:** `e25bd63e8a20f1c13fa4285ccfe1be095523546a` (2026-05-10).

**Per-surface progress (P0 first, then P1/P2 queue):**

| Surface | Name | Tier | Status | Evidence |
|---|---|---|---|---|
| Surface 4 | Active/inactive brand classifier (brand_wizard YAML SSOT) | **P0** | **merged** | PR **#972** (`10ed203bd6`) — classifier landed; SSOT closed |
| Surface 6 | Marketing volume SSOT (discovery + V1 spec + YAML baseline) | **P0** | **merged** | PR **#976** (`f4a872b937`) — discovery + `docs/specs/MARKETING_VOLUME_SSOT_V1_SPEC.md`; PR **#984** (`4c89fe1f19`) — `config/marketing/weekly_volumes_per_brand.yaml` V1 baseline (37 brands × 6 surfaces) |
| Surface 1 | Catalog planning (Pearl Prime feature/knob axes) | **P0** | **substantively shipped (in flight on consumers)** | feat/knob trio merged: PR **#986** (`071f4ee21b`) P0-1 structural variation + stable signature; PR **#974** (`a5eb025a0a`) P0-2 angle_registry alignment; PR **#978** (`95cdb3be6f`) P0-3 explicit `angle_id` per row. Structural variation done; downstream catalog regen audits remain. |
| Surface 2 | Brand dashboard (active brand panel) | **P1** | **partial — first consumer merged** | PR **#977** (`5b455bbf19`) — brand_admin dashboard active-panel consumer of Surface 4 SSOT; broader binding (locale grids, podcast row, piece-level status) remains under `ws_worldwide_gl_s02_brand_dashboard_20260508` |
| Surface 8 | Executive dashboard | **P1** | **queued** | per AMENDMENT-2026-05-08-PRIORITIES; no PR landed |
| Surface 3 | Weekly packaging | **P2** | **queued** | per AMENDMENT-2026-05-08-PRIORITIES |
| Surface 5 | Author/bio | **P2** | **queued** | per AMENDMENT-2026-05-08-PRIORITIES |
| Surface 7 | Spine/CLI perf | **P2** | **queued** | per AMENDMENT-2026-05-08-PRIORITIES |
| Surface 9 | Command UI ↔ CLI | **P2** | **queued** | per AMENDMENT-2026-05-08-PRIORITIES |
| Surface 10 | Disk/worktrees | **P2** | **queued** | per AMENDMENT-2026-05-08-PRIORITIES |

**Phase 1 P0 closeout summary:**

- **Surface 4 (active-brand SSOT):** classifier merged in #972. First consumer merged in #977 (Surface 2 panel). Additional consumers landed under the 2026-05-09 wave (PRs #982, #987 for `brand_admin.html` + Pearl Prime / full-catalog generators; see prior amendment).
- **Surface 6 (marketing volume SSOT):** discovery + V1 spec merged in #976; YAML baseline merged in #984. Consumer wiring (Surfaces 2/3/8) is the next P1/P2 hop per `MARKETING_VOLUME_SSOT_V1_SPEC.md` §5 #4.
- **Surface 1 (catalog planning):** structural variation P0 trio (#986/#974/#978) merged. Catalog rows now carry explicit `angle_id` + structural axes + stable signature; downstream consumption is auditable.
- **Surface 2 (brand dashboard):** P1 — first slice (active panel consumer) shipped early as part of the Surface 4 fan-out; the broader Surface 2 ws remains queued for full P1 execution.
- **Surfaces 3/5/7/8/9/10:** queued at P1/P2 per the **AMENDMENT-2026-05-08-PRIORITIES** lock. No re-prioritization; this AMENDMENT does not move tiers.

**Completed `ws_worldwide_gl_*` lanes (P0):**

- `ws_worldwide_gl_s04_active_brand_classifier_20260508` — **closed** (PR #972 + downstream consumers)
- `ws_worldwide_gl_s06_marketing_volume_ssot_20260508` — **closed** at SSOT layer (PR #976 spec + PR #984 YAML); consumer-wiring follow-ups are P1/P2 per spec
- `ws_worldwide_gl_s01_catalog_planning_20260508` — **substantively closed** at the Pearl Prime feature/knob layer (PRs #986/#974/#978 via `FEATURE-KNOB-CATALOG-VARIATION-V1-01`); any catalog-generator consumption verification remains open

**Remaining `ws_worldwide_gl_*` lanes:**

- **P1:** `ws_worldwide_gl_s02_brand_dashboard_20260508` (broader binding beyond active panel); `ws_worldwide_gl_s08_executive_dashboard_20260508`
- **P2:** `ws_worldwide_gl_s03_weekly_packaging_20260508`; `ws_worldwide_gl_s05_author_bio_20260508`; `ws_worldwide_gl_s07_spine_cli_perf_20260508`; `ws_worldwide_gl_s09_command_ui_cli_20260508`; `ws_worldwide_gl_s10_disk_worktrees_20260508`

**Anti-drift:**

- Phase 1 P0 is **substantively complete** at the SSOT/spec layer for Surfaces 1/4/6. Any session claiming "Phase 1 incomplete" must reference an unmerged P0 PR or a missing P0 ws row (none currently outstanding per this snapshot).
- Production go-live remains defined **only** by **Phase 4 exit criteria** in `artifacts/qa/go_live_readiness_audit_2026-05-08.md`. P0 SSOT closure does **not** itself constitute go-live.
- Any P-tier reassignment still requires a separate AMENDMENT (per AMENDMENT-2026-05-08-PRIORITIES anti-drift).
- This AMENDMENT supersedes the 2026-05-09 AMENDMENT only on the **Phase 1 P0 status matrix**; the 2026-05-09 entry remains authoritative for music-mode + freebie/funnel cross-references and per-PR SHA evidence.

**Action items:** none new. Pearl_PM may now route P1 prompts (Surface 2 broader binding + Surface 8) against `ws_worldwide_gl_s02_*` and `ws_worldwide_gl_s08_*` without further architect ratification.

**Handoffs:** **Pearl_PM** — owns Phase 1 → Phase 2 transition decision (when to flip Phase 1 P0 from `runnable`/`active` to `done` in `ACTIVE_WORKSTREAMS.tsv`). **Surface owners** — unchanged from parent cap.

**Pointers:** parent cap `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` (above); prior `AMENDMENT — 2026-05-09`; `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md` (operator-readable mirror); `artifacts/qa/go_live_readiness_audit_2026-05-08.md`; `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`.

Authorization: Pearl_Architect 2026-05-10 doc-only progress amendment (operator pre-approved snapshot; no new decisions).

#### WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 — AMENDMENT — 2026-05-10 (Phase 1 P0 → Phase 2 transition)

**Status:** **Phase 1 P0 substantially complete** (program SSOT + first-wave consumers; **not** a Phase 4 go-live declaration).

**What landed on `main` for P0-class surfaces (this transition record):**

1. **Surface 1 — Catalog planning / Pearl Prime knobs:** angle registry alignment + explicit `angle_id` per row + structural variation axes + stable signature (**#974**, **#978**, **#986** via `FEATURE-KNOB-CATALOG-VARIATION-V1-01`).
2. **Surface 2 — Brand dashboard (P1-class surface; first slices shipped early):** active/inactive panel consumer (**#977**) + RunComfy monthly spend panel + read path (**#1005**). Broader locale grids / podcast row / piece-level status remain **P1** under `ws_worldwide_gl_s02_brand_dashboard_20260508`.
3. **Surface 4 — Active brand SSOT:** classifier (**#972**) + `brand_admin` dashboard consumer (**#977**) + `brand_admin.html` consumer (**#982**) + Pearl Prime + full-catalog generator consumers (**#987**) — **all live** on `main` per prior amendments + this wave.
4. **Surface 6 — Marketing volume SSOT:** discovery + binding spec (**#976**) + V1 YAML baseline (**#984**) — **SSOT authored**; consumer wiring remains **P1/P2** per `MARKETING_VOLUME_SSOT_V1_SPEC.md` §5.

**Surfaces 3 / 5 / 7 / 8 / 9 / 10:** unchanged queue posture vs **AMENDMENT-2026-05-08-PRIORITIES** — **P1/P2** (weekly packaging automation branch is **in flight on remote** per `ACTIVE_WORKSTREAMS.tsv`; not a program tier change).

**Phase 2 entry criteria (Pearl_PM routing gate — non-exhaustive):**

1. **Core tests green on `main`** after CI recovery cover-art WARN path is observed stable (**#1011** merged; Pearl_DevOps confirms green signal on required checks).
2. **Image generation queue active** only after **Pearl_Int Step 4** completes **Qwen-Image** rollout prerequisites on Pearl Star (operator telemetry: shard **08** ~**7%** at time of this AMENDMENT — **blocks** batch **ACTIVATION**, not doc/spec work).

**Anti-drift (hard):** Do **NOT** close **Phase 1** as **100% program-complete** (and do **not** treat Phase 4 go-live as satisfied) until **image generation produces ≥ 1 real operator-validated batch** on the chosen production path (Pearl Star lane and/or RunComfy paid lane per `IMG-RENDER-DUAL-PATH-V1-01`). Coordination-only “dry-run” or scaffold merges are **insufficient** for that bar.

**Pointers:** prior matrix AMENDMENT (same day, above); `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md`; `artifacts/qa/go_live_readiness_audit_2026-05-08.md` Phase 4 exit criteria; `docs/PEARL_PM_STATE.md` wave snapshot.

Authorization: Pearl_PM + Pearl_Architect joint transition bookkeeping 2026-05-10 (doc-only; no operator decision required).

#### WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 — AMENDMENT-2026-05-10-PHASE-1-P0-COMPLETE

**Authorization:** Operator **`PHASE_1_P0_VISUAL_SIGNOFF_PASS`** on **5 / 5** real renders executed under **PR #1020** batch-runner activation (dual-path Pearl Star + RunComfy). This amendment ratifies the parent cap **status → `complete`** at the **Phase 1 P0** boundary and opens **Phase 2** per **AMENDMENT-2026-05-08-PRIORITIES** anti-drift gate (real operator-validated batch).

**`main` HEAD anchor (doc authoring):** `3c35e9f64ced852555fe842152225efe26d4ff9a` (2026-05-10).

---

##### 1. PHASE 1 P0 100% COMPLETE

- **Visual signoff:** Operator confirmed **`PHASE_1_P0_VISUAL_SIGNOFF_PASS`** — **5 / 5** renders **PASS** (full-resolution review of real PNG outputs).
- **PNG evidence (repo-relative paths; PR #1020 smoke table):**
  1. `artifacts/manga/activation_smoke_2026-05-10/smoke_junko_animagine_ja/smoke_junko_animagine_ja.png`
  2. `artifacts/manga/activation_smoke_2026-05-10/smoke_miki_qwen_ja/smoke_miki_qwen_ja.png`
  3. `artifacts/manga/activation_smoke_2026-05-10/smoke_feung_animagine_zh/smoke_feung_animagine_zh.png`
  4. `artifacts/manga/activation_smoke_2026-05-10/smoke_joshin_flux_en/smoke_joshin_flux_en.png`
  5. `artifacts/manga/activation_smoke_2026-05-10/smoke_ahjan_flux_en/smoke_ahjan_flux_en.png`
- **Anti-drift gate satisfied:** ≥ **1** operator-validated **real** dual-path batch (Pearl Star + RunComfy) with machine-verified PNG signatures + logged hashes per `artifacts/qa/batch_runner_activation_smoke_2026-05-10.md` (**PR #1020**; file lands with runner merge).
- **Wave duration:** **2026-05-08 → 2026-05-10** (~**2** days) for the **WORLDWIDE** activation wave.
- **Total PRs merged (inclusive window):** `gh pr list --state merged --search merged:2026-05-08..2026-05-10` → **63** merged PRs on the tracked GitHub remote (**≥ 35** program wave threshold).

**Binding claim (verbatim):** **Phase 1 P0 is 100% complete** for **`PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1`** at the milestone boundary defined by **AMENDMENT-2026-05-08-PRIORITIES** + operator visual signoff + real-render evidence above.

---

##### 2. PHASE 2 ENTRY CRITERIA

1. **Phase 1 P0 milestone closed** — this AMENDMENT (operator visual signoff + anti-drift gate met).
2. **CI baseline mostly green** — Phase **1 + 2 + 2.5** delivered; **2.6** in flight per **PRJ-CI-BASELINE-RECOVERY-V1**; eventual elimination of **`--admin`** merge bypass remains an acceptance goal (`ws_ci_recovery_acceptance`).
3. **Pearl Star + RunComfy dual-path operational** — live dispatch exercised under **PR #1020** activation harness (`--activate` / `--live` modes; see `IMG-RENDER-DUAL-PATH-V1-01`).
4. **Image batch runner activated** — **dry-run** scaffold (**PR #995**) + **live** activation path (**PR #1020**) with replayable smoke plan.

---

##### 3. PHASE 2 SCOPE

- **Polish — image quality:** suppress **text / words** baked into raster renders (negative-prompt + workflow hygiene); character consistency; brand voice fidelity. Final lettering remains the dedicated **lettering pipeline** (not generative in-image text).
- **Catalog completion:** **Phoenix-counted cells = 259** — **222** = **37 × 3 × 2** (**ebook** + **manga**) regular worldwide + **37** Japan **manga-only** parallel (**37 × ja_JP × manga**; separate JP legal entity — see **AMENDMENT-2026-05-10-CELL-MATH-CORRECTION** + **JAPAN-MANGA-ONLY-CATALOG-V1-01**). **Audiobook** ships via **Google Play brand admin** (not a Phoenix cell). **Podcast** remains a **separate planning track**.
- **Author / teacher associations:** **6–12** authors per brand with bios.
- **Dashboard expansion:** main-character display **per manga series**; per-brand **cover art** panel.
- **Full queue activation (Pearl_Conductor v3):** **~19.3-day** unattended generation backlog → **~6–10 days** wall-clock at dual-path parallelism (Pearl Star + RunComfy), **after** Phase 2 P0 polish closes known image-defect classes (notably baked-in text).

---

##### 4. ANTI-DRIFT

- The claim **“Phase 1 P0 is 100% complete”** is **BINDING** for this program record — it **cannot** be downgraded or contradicted in coordination docs **without a new operator AMENDMENT** referencing this block.
- **Phase 2** workstreams enumerated in §5 are **queued** (`status=runnable` in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`); **no autonomous spawn / execution** without **separate operator authorization** (Pearl_Conductor policy unchanged).
- **Text baked into images** is **Phase 2 P0 polish** (**high priority**; operator-flagged defect on otherwise PASS renders).
- The **master catalog × locale × surface matrix** is a **Phase 2 strategic deliverable** (**Pearl_PM** + **Pearl_Marketing** scope; not guessed here).

---

##### 5. ACTION ITEMS (named `ws_*` — prompts not authored in this amendment)

| workstream_id | Primary owners | Intent |
|---|---|---|
| `ws_phase_2_negative_prompt_text_removal_20260510` | Pearl_Dev | Patch workflow JSONs to add **text / words / typography** to **negative prompts**; re-render for operator verification (lettering remains pipeline-owned). |
| `ws_phase_2_worldwide_catalog_plan_v1_20260510` | Pearl_PM + Pearl_Marketing | Author **37 × 3 × 5** coverage master plan (surfaces above) aligned to **Path X** + marketing SSOT. |
| `ws_phase_2_dashboard_manga_character_display_20260510` | Pearl_Brand | Add per-series **main character** panel + per-brand **cover art** panel on dashboards. |
| `ws_phase_2_full_queue_activation_20260510` | Pearl_Dev (Pearl_Conductor **v3**) | Fire **19.3-day** unattended generation backlog **after** Phase 2 P0 polish (text removal + related gates). |

**Supersedes-in-effect:** The prior same-day **“Do NOT close Phase 1 as 100% program-complete … until ≥ 1 real operator-validated batch”** hard note in **AMENDMENT — 2026-05-10 (Phase 1 P0 → Phase 2 transition)** is **closed satisfied** by operator **`PHASE_1_P0_VISUAL_SIGNOFF_PASS`** + evidence §1 above.

**Pointers:** `artifacts/qa/batch_runner_activation_smoke_2026-05-10.md` (**PR #1020**); prior **AMENDMENT — 2026-05-10** matrix + transition blocks; `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md` §**AMENDMENT-2026-05-10-PHASE-1-P0-COMPLETE**; `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`.

### FEATURE-KNOB-CATALOG-VARIATION-V1-01 — Structural variation + angle registry alignment + explicit angle_id per row (ratified 2026-05-08)

**Status:** **active** (operator authorized; ws rows runnable).

**Context:** PR #960 audit found dead vocab (angle_registry, recommender weights) + 12 cross-cutting findings; operator authorizes top-3 P0 remediations.

**Decision:** 3 Pearl_Dev workstreams open per the 3 P0 directions verbatim:

- P0-1: Serialize structural variation (angle_id, motif_id, book_structure_id, journey_shape_id, stable signature) on Pearl Prime full-catalog artifacts
- P0-2: Align CatalogPlanner angle resolution with `config/angles/angle_registry.yaml` (replace heuristic `_derive_angle` and `{topic}_general` defaults)
- P0-3: Add explicit `angle_id` per catalog row (deterministic registry join; narrative framing catalog-declared, not CLI/arc-defaulted)

**Anti-drift:**

- the 3 P0 workstreams are independent and must NOT be merged into a single mega-PR
- any new vocab axis added to `angle_registry.yaml` or motif registry requires AMENDMENT
- removing the heuristic `_derive_angle` path requires the registry-join path to be production-validated against an existing reference book

**Action items:** `ws_feat_knob_p0_1/2/3` `status=runnable`; router fans out implementation prompts in next turn.

**Handoffs:** Pearl_Dev owns implementation; Pearl_Architect ratifies completion when each ws lands.

### MUSIC-MODE-BRAND-INTEGRATION-V1-01 — Music mode as first-class brand archetype (brands 38+); wizard + musician survey; live routes (**active** 2026-05-09; Q1–Q4 ratified)

**Status:** **active** — operator answers to Q1–Q4 captured in [`specs/MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` §AMENDMENT-2026-05-09](specs/MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md#amendment-2026-05-09); six `ws_music_brand_*` rows advanced **`proposed` → `runnable`** in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`; project **`PRJ-MUSIC-MODE-BRAND-INTEGRATION-V1`**: **`proposed` → `active`** in `artifacts/coordination/ACTIVE_PROJECTS.tsv`.

**Context:** Operator directive: **music mode is not a bolt-on**. It is a **first-class brand archetype** with **new brands numbered 38+**, architecturally **separate** from canonical **Path X 37** (`config/manga/canonical_brand_list.yaml`). Each music-mode brand requires **brand wizard** plus **`musician_reflections_survey`**. The survey must expose a **single Save control at the bottom**; submissions **persist via backend** into **wizard YAML**, then **auto-advance** the wizard. The survey must be served as a **live route inside the wizard app** (same origin / wizard navigation) — **`file://` URLs are deprecated** for this flow. **Music-mode brand catalog = 100% music-mode books** (no composite teacher+music catalog row; no teacher-mode masquerading as music-mode). Registry SSOT for music-mode brands: **`config/music/music_brand_registry.yaml`** (new file path reserved; authoring lands under `ws_music_brand_registry_music_brand_registry_yaml_20260509`). **Freebie / funnel music-mode integration** is explicitly **out of scope** for V1 and is tracked only as a **follow-up cap** placeholder (`ws_music_brand_freebie_funnel_followup_cap_20260509`).

**Cross-reference:** **`MUSIC-MODE-V1-01`** (Pearl Prime overlay, `musician_banks/`, survey template artifact) remains the **rendering / atom-bank** authority. **This entry (`MUSIC-MODE-BRAND-INTEGRATION-V1-01`)** owns **brand identity + onboarding + catalog classification** for music-mode **brands 38+** without contaminating Path X 37.

**Decision (locked sections — ratification package):**

1. **Archetype + numbering:** Music mode = first-class archetype; brands **38+**; dedicated registry **`config/music/music_brand_registry.yaml`** (not merged into `canonical_brand_list.yaml`).
2. **Wizard flow:** **Step 1** — mode selector (includes music-mode path). **Step 4** — conditional **musician_reflections_survey** pane when music-mode is selected. Both steps run on the **live wizard HTTP route** (wizard app shell), **not** `file://`.
3. **Save mechanism:** **One** Save button at bottom → **POST** → persisted **wizard YAML** (backend / server route contract TBD in implementation PR) → **auto-advance** to next wizard step.
4. **Catalog rule:** Music-mode brand catalog rows are **100% music-mode** pipeline books only — **no** composite rows; **no** teacher-mode substitution.
5. **Registry architecture:** **Active** music-mode brand = **brand wizard YAML present** per **Q4 default** (same wizard YAML SSOT as worldwide program — see `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` active-brand note). **`music_brand_registry.yaml`** indexes / cross-walks wizard outputs; it does not invent parallel pen names without wizard backing.
6. **Compatibility:** Path X **37 canonical brands frozen**. Existing **`music_pipeline`** scripts and **`MUSIC-MODE-V1-01`** overlay tooling are **consumed unchanged**; this program adds **brand/admin + catalog** surfaces only unless an implementation ws explicitly extends pipeline flags (requires AMENDMENT).
7. **Anti-drift:** **No** `canonical_brand_list.yaml` contamination with music-only pseudo-brands. Survey answers **do not** live only in browser localStorage — **server-backed persistence** to wizard YAML. **`file://` embedding** for the survey is **rejected** (security + SSOT + CI reproducibility).
8. **Action items:** Six workstreams in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`: `ws_music_brand_wizard_step1_step4_survey_pane_20260509`; `ws_music_brand_survey_save_post_yaml_advance_20260509`; `ws_music_brand_registry_music_brand_registry_yaml_20260509`; `ws_music_brand_catalog_generator_100pct_music_mode_20260509`; `ws_music_brand_wizard_live_embed_routing_20260509`; `ws_music_brand_freebie_funnel_followup_cap_20260509`.
9. **Budget:** **Tier 1** (operator-present) for **design + ratification + Q-card**; **Tier 2** acceptable for unattended **catalog regeneration** runs **after** SSOT locks and operator Q1–Q4 answers (**locked 2026-05-09** via §AMENDMENT-2026-05-09).
10. **Status gate (closed 2026-05-09):** Operator **Q1–Q4** recorded as **defaults** in `docs/specs/MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` §16 + **§AMENDMENT-2026-05-09**. Pearl_Architect amendment session **`MUSIC-MODE-BRAND-INTEGRATION-V1-01-AMENDMENT`** executed — cap + project + six ws rows flipped per amendment §5 **STATUS TRANSITIONS**.

**Operator decision card (verbatim — answer in spec §16):**

- **Q1 — UX flow placement:** Confirm mode selector at **wizard step 1** (default), or name an alternative step index + rationale.
- **Q2 — `brand_id` slug rule:** Confirm **`<musician_handle>_music`** (default), or specify an alternate deterministic slug pattern + collision policy.
- **Q3 — Catalog volume tier default:** Confirm **800** baseline tier (default), or specify alternate tier / cap for first music-mode catalog slice.
- **Q4 — Inactive brand path:** Confirm **same brand_wizard YAML SSOT** marks inactive brands (default), or specify a secondary persisted store (requires AMENDMENT to this cap).

**Anti-drift check:** Does not duplicate `MUSIC-MODE-V1-01`; supplements with **brand/wizard/catalog** boundaries. Does not edit `canonical_brand_list.yaml` in this PR.

**Handoffs:** **Pearl_PM** — coordination cleanup picks up **this amendment PR** alongside in-flight implementation lanes; six `ws_music_brand_*` rows are now **`runnable`**. **Pearl_Dev + Pearl_Brand** — own wizard + routing + registry implementation fan-out (router prompts post-merge). **Pearl_Architect** — follow-up cap **`MUSIC-MODE-FREEBIE-FUNNEL-V1-02`** remains owned under `ws_music_brand_freebie_funnel_followup_cap_20260509` (doc-only; separate ratification).

**Pointers:** `docs/specs/MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md`; `artifacts/coordination/ACTIVE_PROJECTS.tsv` (`PRJ-MUSIC-MODE-BRAND-INTEGRATION-V1`); `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (six `ws_music_brand_*` rows); `artifacts/musician_survey/SURVEY_TEMPLATE.yaml` (schema reference); `docs/PEARL_ARCHITECT_STATE.md` (`MUSIC-MODE-V1-01`).

#### MUSIC-MODE-BRAND-INTEGRATION-V1-01 — AMENDMENT — 2026-05-09 (operator Q1–Q4 — binding defaults)

Operator decisions (**all defaults accepted**):

- **Q1** — mode selector at **brand wizard step 1** (first-class branch).
- **Q2** — music mode `brand_id` slug = **`<musician_handle>_music`**.
- **Q3** — catalog volume tier default = **800 baseline** (override via survey field `music_volume_tier`).
- **Q4** — inactive brand path = **same `brand_wizard` YAML SSOT as Path X** (`WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` alignment).

1. **UX FLOW (Q1=default):**
   - Mode selector at brand wizard step 1 with options: [Standard book brand] [Manga/illustrated brand] [Music mode brand] [Hybrid (advanced — reserved)]
   - Music mode flow inserts musician reflections survey as conditional Step 4 (live wizard pane, NOT file:// URL).
   - **Anti-drift:** any UX placement change (mid-wizard, end-of-wizard, popup) requires separate AMENDMENT.

2. **BRAND_ID SLUG (Q2=default):**
   - Music mode brand_id = `<musician_handle>_music` (e.g., ahjansam_music, junko_music).
   - **Anti-drift:** alternate naming patterns (vanity slug, numeric, etc.) require separate AMENDMENT.

3. **CATALOG VOLUME TIER (Q3=default):**
   - Default tier = 800 baseline (matches Path X canonical brand volume).
   - Override via survey field `music_volume_tier` ∈ {solo, standard, enterprise}; solo<800, standard=800, enterprise>800 (specific numeric ranges TBD by Pearl_Marketing in implementation).
   - **Anti-drift:** changing the default 800 baseline requires separate AMENDMENT.

4. **INACTIVE BRAND PATH (Q4=default):**
   - Music mode brand active/inactive classification follows the same brand_wizard YAML SSOT defined in WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 + ws_worldwide_gl_s04 classifier (PR #972).
   - Music mode brands MUST appear in `config/music/music_brand_registry.yaml` AND have a brand_wizard YAML at `brand-wizard-app/brands/<brand_id>.yaml` to be active.
   - **Anti-drift:** any music-mode-specific archive/retention rule (vs Path X) requires separate AMENDMENT.

5. **STATUS TRANSITIONS:**
   - Cap entry **MUSIC-MODE-BRAND-INTEGRATION-V1-01**: status **proposed → active**.
   - **6 ws rows**: **proposed → runnable** (per `ACTIVE_WORKSTREAMS.tsv` update).
   - **PRJ-MUSIC-MODE-BRAND-INTEGRATION-V1**: status **proposed → active**.
   - **Implementation ownership** (named, not authored here):
     - **a.** `ws_music_brand_wizard_step1_step4_survey_pane_20260509` → **Pearl_Brand**
     - **b.** `ws_music_brand_survey_save_post_yaml_advance_20260509` → **Pearl_Dev**
     - **c.** `ws_music_brand_registry_music_brand_registry_yaml_20260509` → **Pearl_Dev**
     - **d.** `ws_music_brand_catalog_generator_100pct_music_mode_20260509` → **Pearl_Dev**
     - **e.** `ws_music_brand_wizard_live_embed_routing_20260509` → **Pearl_Dev**
     - **f.** `ws_music_brand_freebie_funnel_followup_cap_20260509` → **Pearl_Architect** (authors separate cap **MUSIC-MODE-FREEBIE-FUNNEL-V1-02**)

### MUSIC-MODE-FREEBIE-FUNNEL-V1-02 — Music mode brand freebies + funnel (additive; proposed 2026-05-09; pending operator decision card)

**Status:** **proposed** — doc-only cap + spec + coordination; **no** code, **no** UI, **no** authored freebie assets in this PR. Normative inventory and deltas live in [`docs/specs/MUSIC_MODE_FREEBIE_FUNNEL_V1_SPEC.md`](./specs/MUSIC_MODE_FREEBIE_FUNNEL_V1_SPEC.md).

**Context:** Operator framing from `MUSIC-MODE-BRAND-INTEGRATION-V1-01` action item **f** / `ws_music_brand_freebie_funnel_followup_cap_20260509`: *the funnel and freebies we create should also have considerations for music mode* — companion songs as freebies, music previews, sample EPs, lyric videos, etc. This cap **does not** amend `MUSIC-MODE-BRAND-INTEGRATION-V1-01`; it **spins** the deferred freebie/funnel scope into its own program under **`PRJ-MUSIC-MODE-FREEBIE-FUNNEL-V1`**.

**Cross-reference:** Parent program **`PRJ-MUSIC-MODE-BRAND-INTEGRATION-V1`** + `MUSIC-MODE-BRAND-INTEGRATION-V1-01` (wizard, registry, catalog). Rendering overlay remains **`MUSIC-MODE-V1-01`**. Freebie system authority remains **`specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md`** + `config/freebies/*`.

**Decision (locked sections — ratification package):**

1. **SCOPE — Music mode brand freebies + funnel artifacts that differ from standard Pearl Prime brand freebies.** Covers **additive** music-native lead magnets and **funnel touchpoint deltas** for music-mode brands (38+), including operator examples: **companion song** as freebie, **music previews**, **sample EPs**, **lyric videos**, and related hooks. **Out of this cap’s PR:** implementation, funnel code changes, and Pearl_Marketing-authored templates (tracked under child workstreams).

2. **INVENTORY OF EXISTING FREEBIE/FUNNEL SURFACES (discovery).** Pearl_Architect discovery sweep (2026-05-09) documented in spec **§2**: `funnel/` (Flask proof-loop hub + README pointers into `config/freebies/*`); **`platform_marketing/`** path **not present** at repo root — marketing-adjacent surfaces mapped to `config/marketing/`, `docs/marketing/`, `scripts/marketing/`, `marketing_deep_research/`; `somatic_exercise_freebee_apps/` (HTML somatic tools); `config/freebies/` (`freebie_registry.yaml`, `funnel_proof_loop.yaml`, `freebie_to_book_map.yaml`, `freebie_selection_rules.yaml`, companion workbook YAML, etc.). For each bucket: **music-mode-aware today ≈ no**; spec records **where** music-mode freebie types would attach.

3. **PROPOSED MUSIC MODE FREEBIE TYPES (V1 candidate set — ≥5).** (a) Companion song download (free full track from upcoming album). (b) 30s preview clip (lyric snippet + audio). (c) Sample EP (3–5 tracks). (d) Lyric poster (PDF). (e) Behind-the-song interview (audio or text). Additional types **via Pearl_Marketing** after operator Q1.

4. **FUNNEL FLOW DELTA.** Music-mode brand funnel = **standard Pearl Prime / burnout-reset style funnel backbone** + **music-specific top-of-funnel hooks** (audio-first promise, track list, listening CTA). Spec **§4** lists what **stays shared** vs what **deltas** (hero, email E1–E5 tone, book vs album CTA, asset hosting).

5. **ANTI-DRIFT.** Music-mode freebies **SHALL NOT replace** standard Pearl Prime freebies for music-mode brands; they **extend** the freebie set. Music-mode freebie types are **additive** to existing freebie taxonomy (`freebie_registry.yaml` pattern per `PHOENIX_FREEBIE_SYSTEM_SPEC.md`). Implementation **MUST** consume **`brand_wizard` YAML** plus **`musician_reflections_survey`** persisted fields (same wizard YAML SSOT family as `MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` §3 — survey payload keyed/merged into wizard persistence; **not** hardcoded per-brand lists). **Catalog volume** Q3=800 baseline applies to **book catalog rows**, **not** freebie cadence; freebie cadence is **separate** (spec **§5**).

6. **ACTION ITEMS (named sub-workstreams — not authored here).** `ws_music_freebie_inventory_audit_20260509` (Pearl_Marketing); `ws_music_freebie_template_authoring_20260509` (Pearl_Marketing); `ws_music_freebie_funnel_wiring_20260509` (Pearl_Dev). Opened under **`PRJ-MUSIC-MODE-FREEBIE-FUNNEL-V1`** in `ACTIVE_WORKSTREAMS.tsv`.

7. **STATUS.** **`proposed`** pending operator **Q1–Q3** in `docs/specs/MUSIC_MODE_FREEBIE_FUNNEL_V1_SPEC.md` §16 (decision card). Pearl_Architect amendment flips to **active** when answers land.

**Operator decision card (verbatim — answer in spec §16):** see spec **§16 Q1–Q3** (freebie-type set approval; funnel delta breadth; implementation phasing).

**Anti-drift check:** Does not edit parent `MUSIC-MODE-BRAND-INTEGRATION-V1-01` entry. Does not imply Path X 37 changes. No paid API scope.

**Handoffs:** **Pearl_PM** — child ws statuses after operator Q-card. **Pearl_Marketing** — inventory + template authoring. **Pearl_Dev** — pipeline wiring to YAML SSOT. **Pearl_Architect** — amendment after Q1–Q3.

**Pointers:** `docs/specs/MUSIC_MODE_FREEBIE_FUNNEL_V1_SPEC.md`; `artifacts/coordination/ACTIVE_PROJECTS.tsv` (`PRJ-MUSIC-MODE-FREEBIE-FUNNEL-V1`); `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`; `ws_music_brand_freebie_funnel_followup_cap_20260509` (action item **f** — row marked **completed** after PR #979 lands; follow-up work under `PRJ-MUSIC-MODE-FREEBIE-FUNNEL-V1`).

### TEACHER-MANGA-30S-VIDEO-V1-01 — 12 teacher × manga 30-second video deliverables (**active**); adi_da deferred V1.1 (ratified 2026-05-08)

**Status:** **active** — operator answers to Q1–Q4 captured in [`docs/specs/TEACHER_MANGA_30S_VIDEO_V1_SPEC.md` §AMENDMENT-2026-05-08](../docs/specs/TEACHER_MANGA_30S_VIDEO_V1_SPEC.md); binding matrix edits in [`artifacts/qa/teacher_manga_30s_locale_brand_matrix_2026-05-08.tsv`](../artifacts/qa/teacher_manga_30s_locale_brand_matrix_2026-05-08.tsv).

**Context:** Operator request — a 30-second video per teacher, tied to that teacher's manga brand, with the SAME NARRATIVE MEANING as the teacher's audiobook chapter-1 sample (script meaning-matched, not verbatim). Teacher-as-MC experiences a struggle → release/resolution arc that mirrors the teacher's signature transformation. Style is primarily manga but with a deliberate spread of types — manga, fantasy, hybrid, and one experimental — to demonstrate market range while keeping teacher identity locked. Locale is the teacher's native locale per operator's matrix.

**Decision (V1 frozen):** **12 teachers × 1 video each = 12 ship deliverables.** **adi_da is deferred to V1.1** per operator **Q1 = (b)** — no manga brand binding in `brand_lora_plans.character_loras`; matrix row retained with **`deferred_v1_1`**. Wave A implementation prompts are **already in flight** — do **not** re-issue those prompts.

| Pillar | Lock |
|---|---|
| Story shape | HOOK (0–6s) → STRUGGLE (6–22s) → RELEASE (22–30s) — same DNA as the audiobook chapter-1 climax |
| Script-reuse rule | Meaning matches `artifacts/audiobook_samples/_prose/<teacher>_*_ch1.txt`; verbatim NOT required; 30s ≈ 65–80 EN words / locale-equivalent |
| Teacher-as-MC | Reuse `character_design` from `brand_lora_plans.yaml.character_loras.<teacher>`; NO new identity instances (**adi_da has none — deferred V1.1**). |
| Style spread (**Q2 locked**) | **6** `pure_manga` / **3** `manga_fantasy_hybrid` / **2** `cinematic_painterly_fantasy` / **1** `experimental` — distribution + per-teacher rationale in `artifacts/qa/teacher_manga_30s_locale_brand_matrix_2026-05-08.tsv`; **silent per-teacher style reassignment is forbidden** → requires separate AMENDMENT. |

**Verified brand bindings (12/12 confirmed against `config/manga/brand_lora_plans.yaml.brand_suffixes`) — pilot locked Q3:**

| Teacher → manga brand (suffix) | Locale | Style mode |
|---|---|---|
| ahjan → stillness_press (sp) | en-US | pure_manga |
| joshin → cognitive_clarity (cc) | ja-JP | pure_manga **(pilot — locked)** |
| miki → digital_ground (dg) | ja-JP | pure_manga |
| miyuki → relational_calm (rc) | ja-JP | pure_manga | (per OPD-111)
| junko → (new cosmic brand pending) | ja-JP | pure_manga | (per OPD-111 — channeling)
| omote → body_memory (bm) | ja-JP | pure_manga |
| master_wu → warrior_calm (wc) | zh-TW | pure_manga |
| master_feung → qi_foundation (qf) | zh-CN | manga_fantasy_hybrid |
| master_sha → sleep_restoration (sr) | en-US | manga_fantasy_hybrid |
| ra → solar_return (so) | en-US | manga_fantasy_hybrid |
| pamela_fellows → somatic_wisdom (sw) | en-US | cinematic_painterly_fantasy |
| sai_ma → devotion_path (dp) | en-US | cinematic_painterly_fantasy |
| maat → heart_balance (hb) | en-US | experimental |
| **(deferred V1.1)** adi_da → (**NONE**) | zh-TW | **deferred — see amendment §1 / matrix row** |

**Anti-drift check:** Identity-preserving by design. The 12-axis `character_design` from `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` is reused; style-spread varies wardrobe/setting/lighting/lineart-engine but NOT identity. **Any agent attempting to render adi_da under THIS cap MUST stop and request explicit V1.1 scoping** (brand/`character_design` binding). Per-teacher style overrides require AMENDMENT. Pilot identity (**joshin / cognitive_clarity / ja-JP**) is locked; operator-level re-pilot needs explicit instruction. No paid LLM/TTS APIs unattended (Tier 2 = CosyVoice2 + edge_tts free). No verbatim audiobook prose re-quote in social/video context (>15-word displacive copyright avoidance). Pearl Star Path A is the canonical render path per `docs/PEARL_STAR_IMAGE_GENERATION_PROTOCOL.md`.

**Discrepancies / prerequisite tracking (updated 2026-05-08):**

| ID | Discrepancy | Disposition |
|---|---|---|
| D1 | `qi_foundation` brand (master_feung's binding) vs `canonical_brand_list.yaml` | **Closed for V1 prerequisite purposes** via **PR #944** merged **`7e8009e78e`**; YAML reconciliation continues as **Wave A4** Pearl_Dev lane (not blocking cap activation). |
| D2 | maat audiobook prose anchor | **Closed** via **PR #943** merged **`54b759d603`** (`artifacts/audiobook_samples/_prose/maat_self_worth_ch1.txt`); maat matrix row **`ready`**. |
| D3 | adi_da unbound manga brand | **Tracked as V1.1 prerequisite** per **Q1 = (b)**; **does not block** V1 (12-active program). |

**Out of scope (this cap entry):**
1. Any render, any video file, any audio file (unless owned by downstream lanes).
2. Any code change to `phoenix_v4/` or `scripts/` or `config/video/*` params (Pearl_Dev PRs tracked under Wave A).
3. Editing `canonical_brand_list.yaml` / `brand_lora_plans.yaml` for adi_da (V1.1 cap entry when scheduled).
4. **Re-issuing** Pearl_Localization / Pearl_Int / Pearl_Editor / Pearl_Dev Wave A prompts (capture-only refs in amendment §7).

**Action items — Wave capture (already running; see amendment §7):**
- **A1** Pearl_Localization × **12** scripts → recovery PR pending
- **A2** Pearl_Int CosyVoice2 audit → recovery PR pending
- **A3** Pearl_Editor style review → **PR #953** (open)
- **A4** Pearl_Dev `qi_foundation` YAML reconciliation → **PR #952** (open)
- **A5** Pearl_Dev overlay enforcement Phase 1 → recovery PR pending
- **A6** Pearl_Dev `teacher_30s_vertical_v1` render preset → status unknown
- **A7** Pearl_GitHub merge train → **CLOSED (5 SHAs)**
- **B1** Pearl_Video **joshin** pilot → gated on **A1 + A2 (joshin row) + A6**

**Budget (Tier 2 unattended — free):** Pearl Star GPU ~6–12h active-teacher total; CosyVoice2 ~1h total; ffmpeg trivial; operator review scaled to 12. Paid spend 0.

**Handoffs:**
- **Pearl_PM** — coordination cleanup picks up **this amendment PR** alongside Wave A PRs pending.
- Any future operator change to locales (**Q4 locked**) → **requires AMENDMENT**.

**Resolves:** V1 operational scope freeze for 12 active teachers plus **1 deferred** matrix row (**13 rows preserved**).

#### TEACHER-MANGA-30S-VIDEO-V1-01 — AMENDMENT — 2026-05-08 (operator Q1–Q4 — binding)

Operator decisions (verbatim lock):

- **Q1 = (b)** — defer **adi_da** to **V1.1** (program ships **12**, not 13).
- **Q2 = approve** — lock **6 / 3 / 2 / 1** style spread **as proposed** in §6 table + matrix.
- **Q3 = joshin** — pilot **= joshin / cognitive_clarity / ja-JP**.
- **Q4 = none** — retain all **six** **en-US** defaults: **ahjan, pamela_fellows, master_sha, maat, ra, sai_ma**.

1. **ADI_DA deferral (Q1 = b):** Total V1 deliverables **12** (not 13). **adi_da** row **preserved** in matrix TSV with **`deferred_v1_1`**; rationale **"no manga brand binding in brand_lora_plans.character_loras; awaits brand assignment"**. **Anti-drift:** Any agent attempting to render **adi_da** against **this cap** MUST STOP and request **V1.1** scoping.

2. **Style-spread lock (Q2 = approve):**
   - **6** `pure_manga`: ahjan, joshin, miki, junko, omote, master_wu
   - **3** `manga_fantasy_hybrid`: master_feung, master_sha, ra
   - **2** `cinematic_painterly_fantasy`: pamela_fellows, sai_ma
   - **1** `experimental`: maat
   **Anti-drift:** Per-teacher style reassignment requires a **separate AMENDMENT** — agents MAY NOT silently re-allocate.

3. **Pilot teacher (Q3 = joshin):** Pilot **= joshin / cognitive_clarity / ja-JP**. **Wave B1** (`Pearl_Video` joshin pilot) consumes **Wave A1** joshin script **+ Wave A2** joshin reference voice **+ Wave A6** render preset convergence. **Anti-drift:** Pilot identity locked; operator-level **re-pilot** needs explicit instruction.

4. **Locale lock (Q4 = none):** **ja_JP:** joshin, miki, junko, omote · **zh_TW:** master_wu *(adi_da deferred → **single-teacher zh_TW** in V1)* · **zh_CN:** master_feung · **en_US:** ahjan, pamela_fellows, master_sha, maat, ra, sai_ma. **Anti-drift:** Locale overrides require future **AMENDMENT**.

5. **Prerequisite status:**
   - **D1** (`qi_foundation`): **Closed** by **PR #944** (merged **`7e8009e78e`**); follow-up YAML reconciliation **in flight** as **Wave A4**.
   - **D2** (maat audiobook prose): **Closed** by **PR #943** (merged **`54b759d603`**); **maat** row → **`ready`**.
   - **D3** (adi_da brand binding): **V1.1** prerequisite — **does not block** V1.

6. **Status transitions:** Cap **TEACHER-MANGA-30S-VIDEO-V1-01**: **`proposed` → `active`**. **`ws_teacher30s_scope_ratified`**: **`proposed` → `complete`**. **`ws_teacher30s_script_derivation`**, **`ws_teacher30s_render_pilot`**: **`proposed` → `in_progress`** (Wave A/B refs per §7).

7. **Wave A in-flight references (capture-only — DO NOT re-prompt):**
   - **A1** Pearl_Localization × 12 scripts → recovery PR pending
   - **A2** Pearl_Int CosyVoice2 audit → recovery PR pending
   - **A3** Pearl_Editor style review → **PR #953** (open)
   - **A4** Pearl_Dev `qi_foundation` YAML reconciliation → **PR #952** (open)
   - **A5** Pearl_Dev overlay enforcement Phase 1 → recovery PR pending
   - **A6** Pearl_Dev `teacher_30s_vertical_v1` render preset → status unknown
   - **A7** Pearl_GitHub merge train → **CLOSED (5 SHAs)**
   - **B1** Pearl_Video joshin pilot → gated on **A1 + A2 (joshin) + A6**


### PER-CHAPTER-OVERLAY-ENFORCEMENT-V1-01 — Per-chapter overlay rule enforcement scoped; unblocks YELLOW ITEM-2 (`your nervous system` allowlist removal) (decision ratified 2026-05-08)

**Status:** **ratified** (2026-05-08). Subsystem: `core_pipeline`. Project: PRJ-PEARL-PRIME-Q-GATES. Workstreams opened: `ws_per_chapter_overlay_enforcement_design_20260508` (status=proposed, Pearl_Architect), `ws_per_chapter_overlay_enforcement_impl_20260508` (status=proposed, Pearl_Dev — covers Phases 1/2/3).

**Context:** Sprint 1 YELLOW ITEM-1 (PR #941, SHA aed7d2a017) replaced the raw `ignored_prefixes` tuple in `_repeated_phrase_violations` with a YAML-backed `config/quality/refrain_allowlist.yaml` (43 entries: 36 `legitimate_motif` cap=18, 7 `doctrinal_attribution` cap=14). ITEM-1 closed the book-wide cap gap. ITEM-2 — removal of `"your nervous system"` from the allowlist — was deferred because the allowlist entry carries `todo: ITEM-2:remove-when-per-chapter-overlay-active`: removing it without overlay enforcement would cause spurious gate failures on any somatic book where the phrase is genuinely used as spine vocabulary. This cap ratifies the scope needed to make that removal safe.

**Problem the book-wide cap cannot solve:** A phrase appearing exactly twice per chapter in a 12-chapter book passes the book-wide cap of 18 (cap_per_chapter=2 handles the per-chapter density). What the book-wide cap alone cannot catch is structural: a refrain phrase absent from the climax chapters (arc discontinuity), an attribution phrase appearing in compression chapters (cognitive competition), or a fragment phrase clustering 5 times in a single chapter even if it is under the book-wide total. The per-chapter overlay enforcement closes these four structural gaps.

**Four overlay rule types (defined precisely in `docs/specs/PER_CHAPTER_OVERLAY_ENFORCEMENT_V1_SPEC.md §2`):**

1. **DENSITY_CEILING** — phrase appears ≤N times per chapter (default N=2 for `legitimate_motif`). Spec source: `BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md §6 Pacing Rules`. Reader failure mode: within-chapter mantra fatigue.

2. **PRESENCE_FLOOR** — phrase appears ≥1 time in each of the named structural chapter classes (`opening`=ch1, `mid`=ch4–8, `climax`=ch9–10). Spec source: `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (SOMATIC SLOT GRID). Reader failure mode: arc discontinuity.

3. **DRIFT_DETECTION** — chapter containing phrase ≥3 times triggers per-chapter violation independent of book-wide cap. Spec source: `BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md §2 Voice/Register`. Reader failure mode: phrase drift / audio defect perception.

4. **ABSENCE_GUARD** — phrase must NOT appear in named chapter classes (default for `doctrinal_attribution`: `compression_chapters`). Spec source: `PHOENIX_V4_5_WRITER_SPEC.md §4 TEACHER_DOCTRINE`. Reader failure mode: attribution overload in concept-dense sections.

**Composition rule:** `PASS = book_wide_cap_ok AND all_overlay_rules_ok`. Both gates are mandatory. The violation dict must include a `rule` key: `book_wide_cap` or `overlay:<rule_type>`.

**Critical distinction — cap_per_chapter vs overlay_rule:** `cap_per_chapter` is a numeric ceiling (integer) applied unconditionally to every chapter. `overlay_rule` is a structural rule type (enum) encoding structural assertions about phrase distribution across chapter architecture. They compose independently. An entry with `cap_per_chapter: 2` and `overlay_rule: presence_floor` simultaneously enforces "no more than 2 per chapter" (density) AND "must appear at least once in opening + mid + climax" (structure). These are documented separately in the violation dict.

**Extended YAML schema (new optional fields — back-compat; absence of `overlay_rule` defaults to `none`):**
```yaml
overlay_rule: none  # density_ceiling | presence_floor | drift_detection | absence_guard | none
overlay_param:
  N: 2
  structural_chapters: [opening, mid, climax]
  excluded_chapter_classes: []
```

**Per-entry overlay assignment summary (Phase 2 targets; full table in spec §6):**
- Group A entries 1–15 (core somatic instruction motifs): full-phrase entries → `presence_floor`; fragment entries → `none` (governed by parent).
- Group B entries 16–36 (sprint-1 scene-anchor motifs): root motif sentences → `presence_floor`; n-gram fragments → `drift_detection`. Entry 27 (`your nervous system`) → `drift_detection` (ITEM-2 target).
- Group C entries 37–43 (TEACHER_DOCTRINE attribution): all → `absence_guard(compression_chapters)`.

**Migration path (ITEM-2 unblock chain):**
- Phase 1: implement gate extension + extended YAML schema + tests; all current entries default to `overlay_rule: none` (zero behavior change); reference book (50,344-word deep_book_6h anxiety×gen_z, SHA 635e1a96bf) revalidated.
- Phase 2: per-entry `overlay_rule` assignment sweep PR; revalidate reference book end-to-end.
- Phase 3: remove `your nervous system` from allowlist; gate must catch it via `drift_detection` OR default book-wide cap >12; ITEM-2 closed when violation fires without the allowlist entry.

**Anti-drift rules:**
- No silent thresholds — every `overlay_param` must cite spec source.
- No removal from allowlist without regenerating ≥1 reference book end-to-end before merge.
- Overlay rule changes require end-to-end reference book rerun before PR merges.
- Gate must report which rule fired in violation dict (`book_wide_cap` or `overlay:<rule_type>`).
- `cap_per_chapter` (numeric) and `overlay_rule` (structural) are distinct; violation dict documents them separately.

**Anti-drift check (per Common Drift Patterns):** `docs/specs/PER_CHAPTER_OVERLAY_ENFORCEMENT_V1_SPEC.md` is genuinely new — no existing spec covers per-chapter overlay enforcement rules for the refrain allowlist. It SUPPLEMENTS `config/quality/refrain_allowlist.yaml` (which defines what is allowed) with an enforcement layer (how allowance is conditionally governed). It does NOT duplicate `BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md` or `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` — it cites them as spec sources for each rule's threshold values. The new YAML fields are additive and back-compatible (absence = `none` = no change). Not drift.

**Action items:**
1. Pearl_Dev (`ws_per_chapter_overlay_enforcement_impl_20260508`, Phase 1): implement gate extension + YAML schema + tests; separate PR after this cap-entry PR merges.
2. Pearl_Dev (Phase 2 sweep PR, gated on Phase 1 merge): assign `overlay_rule` per-entry per spec §6 table; revalidate reference book.
3. Pearl_Dev (Phase 3 PR, gated on Phase 2 merge): remove `your nervous system`; confirm gate catches it; ITEM-2 closed.
4. Pearl_PM: track `ws_per_chapter_overlay_enforcement_impl_20260508` through Phases 1/2/3.

**Handoffs:**
- Pearl_Dev → `ws_per_chapter_overlay_enforcement_impl_20260508` (Phase 1) → trigger = this cap-entry PR merged.
- Pearl_PM → update `ws_per_chapter_overlay_enforcement_impl_20260508` status through Phase 2 and Phase 3 → trigger = Phase 1 merged.
- Pearl_Architect → no follow-up routing needed; spec is self-contained; reopen only if a new structural rule type is proposed.

### IMG-RENDER-DUAL-PATH-V1-01 — Dual-path image generation: Pearl Star (Tier 2, free, canonical) + RunComfy ($10/month soft cap) + locale-first queue (ratified operator Q-IMG-1/2/3, 2026-05-09)

**Status:** **active** (operator authorization; OPERATOR DECISION CARD: NONE — binding immediately).

> **AMENDMENT-2026-06-03-RUNCOMFY-DEPRECATION-IN-PROGRESS:** Operator has decided to retire the RunComfy paid lane. Current balance ($20.48) is being burned on one-time high-value renders (character refs / ep_002 V5.1 / flagship parity / KDP covers / style probes) before account closure. Cap is **TEMPORARILY raised from $10 to $25** in 4 enforcement sites (`runcomfy_dispatch.py:88`, `runcomfy_cost_tracker.py:29`, `dispatchers/runcomfy_dispatcher.py:164`, `batch_runner.py:43`) to allow the burn. After closure, a follow-up PR restores `_COOLDOWN_USD = 10.0` and removes RunComfy from the dual-path entirely (Pearl Star becomes single-path canonical). Burn receipt: `artifacts/qa/runcomfy_burn_receipt_20260603.md` (forthcoming).

**PROJECT_ID:** `PRJ-DUAL-PATH-IMAGE-RENDER-V1`.  
**Subsystem:** `integrations` (primary RunComfy wiring); `manga_pipeline`; `brand_admin`; cross-cutting.  
**Spec:** [`docs/specs/IMG_RENDER_DUAL_PATH_V1_SPEC.md`](./specs/IMG_RENDER_DUAL_PATH_V1_SPEC.md).

**Authority / cross-links (do not supersede Arc-First; supplement catalog + integrations posture):**

- WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 and MANGA-LAYERED-PIPELINE-V2-01 anchors in `docs/PEARL_ARCHITECT_STATE.md` (existing caps).
- `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` — credential prose (RunComfy token staged per operator; Pearl_Int wiring extends registry in a separate workstream — **unchanged here**).
- `skills/pearl-int/references/manga_render_path_decision.md` — Pearl Star remains **Path A canonical** post-#921/#922; RunComfy was video_bank-scope historically; **this cap expands RunComfy to parallel image renders** without demoting Pearl Star.
- [`artifacts/qa/parallel_image_generation_plan_2026-05-09.md`](../artifacts/qa/parallel_image_generation_plan_2026-05-09.md) (PR #988) — default **within-locale asset-type ordering**.
- [`CLAUDE.md`](../CLAUDE.md) Tier 1 vs Tier 2 policy — Pearl Star = Tier 2 unattended; repo remains BANNED on paid cloud LLM keys in Tier-2 pipelines per existing enforcement.

**Operator decisions (verbatim lock):**

| ID | Decision |
|----|-----------|
| **Q-IMG-1** | **Locale-first queue:** prioritize `ja_JP`, `zh_TW`, `zh_CN` for brands that already have `en_US` assets (~18 brands × 3 missing locales = **54 brand-locale cells**) **before** zero-asset brand fills. |
| **Q-IMG-2** | **Within-cell asset ordering** follows **`parallel_image_generation_plan_2026-05-09.md` default** (PR #988; operator-approved). |
| **Q-IMG-3** | **Pearl Star has NO monthly spend cap.** Run unattended until drained or operator pauses. |
| **RunComfy budget** | **$10/month soft cap** after free-tier credits exhausted; Pearl Star unaffected. |

**1. Scope (summary)** — Dual-path image generation consumes the **same** ComfyUI-style workflow JSON templates (Animagine, FLUX, Qwen-Image, etc.). **Pearl Star** is the primary/canonical Tier-2 unattended path.**RunComfy** adds parallel paid capacity + locale-variant overflow. Renderer choice is environment-agnostic; divergence in workflow JSON bodies between paths is **forbidden** (see spec §7).

**2. Priority queue (Q-IMG-1 + Q-IMG-2)**

1. Locales **`ja_JP`, `zh_TW`, `zh_CN`** for brands with existing **`en_US`** coverage (54 cells framing).
2. Then **`en_US`** for **19 zero-asset brands**, only **after** the 18-brand locale-parity cohort reaches **≥80%** of its target asset-count threshold.
3. Then **non-`en_US`** fills for those zero-asset brands (final wave).
4. Within each brand-locale cell, **asset-type order** = PR #988 plan default (**Q-IMG-2**).

**3. Pearl Star path — Tier 2**

- Free; 24/7 unattended; single-GPU sequential per session (throughput posture per infra reality).
- **CosyVoice2 resident ~2.9 GiB** — image sessions must reserve headroom accordingly.
- **~19.3 days** wall-time estimate at saturated utilization for **100,605** images per PR #988 inventory framing (ordering does not change the count — **planning fidelity** datum only).
- **No monthly operator spend cap** — **Q-IMG-3**.

**4. RunComfy path — paid soft cap**

- Token: **`phoenix-omega` / `RUNCOMFY_API_TOKEN`** macOS Keychain generic-password (operator staged via `security add-generic-password` — Pearl_Int verifies read path only once wiring executes).
- **Free tier consumes first.** Soft cap (**$10/mo billed**) binds only on **metered/on-bill RunComfy spend after free exhaustion** (Pearl_Int normalizes semantics against actual vendor statements — see spec §4).
- **Soft-cap behavior:** at **$8 (80%)** → Pearl_Int emits **budget alert** (Slack/email/log per wiring); at **$10 (100%)** → RunComfy path **`COOLDOWN`**: dispatch **paused** until next calendar-month rollover.**Pearl Star continues.**
- **State file:** `artifacts/qa/runcomfy_monthly_spend.tsv` — columns **`date`** | **`dispatched_jobs_today`** | **`cumulative_month_spend_usd`** (append-only daily rows).

**5. Workflow + LoRA gate**

- Workflows authoritative under `scripts/image_generation/comfyui_workflows/` today; RunComfy must accept **those same JSONs** modulo environment validation (Pearl_Int audit ws).
- **Civitai 6-flag commercial gate** applies **uniformly** (see `skills/pearl-int/references/integration_registry.md`). **Banned LoRAs (e.g. Rent-only)** are blocked on **both** paths.

**6. Dispatch (Pearl_Dev — `ws_image_batch_generation_orchestration_20260509`)**

- Builds batches from §2 ordering; **Pearl Star + RunComfy** receive **parallel** eligible batches whenever `cumulative_month_spend_usd < 10`; else RunComfy arm holds **cooldown**.
- Telemetry: `artifacts/qa/image_batch_dispatch_log.tsv` — `timestamp`, `batch_id`, `brand`, `locale`, `asset_type`, `path` (`pearl_star`|`runcomfy`), **`spend_to_date_usd`**, `status`. Per-job **`wall_time`**, **`output_path`**, **`hash`** tracked in implementation artifacts (exact column extension allowed in Pearl_Dev PR — additive only vs this spec §6 skeleton).

**7. Anti-drift**

1. **`$10` RunComfy cap is constitutionally binding** absent operator **`AMENDMENT`** — no silent bypass branches.
2. **Pearl Star canonical-ness** survives per `manga_render_path_decision.md` — RunComfy is **additive capacity**, never a replacement canon.
3. **Identical workflow JSON** semantics across paths unless an **explicit AMENDMENT** cites vendor impossibility (then document divergence in Pearl_Int audit with operator sign-off).
4. **Locale-first queue is binding.** **Brand-before-locale inversion** requires **AMENDMENT**.
5. LoRA licensing gate uniformity across paths (**non-negotiable repeat**).

**8. Prerequisites + action items**

- **PREREQ:** Pearl_Int **Steps 3+4 — Animagine + Qwen-Image on Pearl Star** (operator-attended rollout in flight vs **PR #946** prep lineage).

| Workstream ID | Owner | Scope |
|---|---|---|
| `ws_runcomfy_pearl_int_wiring_20260509` | Pearl_Int | Keychain-backed API client; [`scripts/image_generation/runcomfy_dispatch.py`](../scripts/image_generation/runcomfy_dispatch.py); daily billing probe → `artifacts/qa/runcomfy_monthly_spend.tsv`; $8/$10 cap machine. |
| `ws_image_batch_generation_orchestration_20260509` | Pearl_Dev | Dual-path batch runner §6 — cost-aware parallelism + structured logs; queue reader §2. |
| `ws_parallel_plan_locale_first_priority_update_20260509` | Pearl_PM | Update **only** [`artifacts/qa/parallel_image_generation_plan_2026-05-09.md`](../artifacts/qa/parallel_image_generation_plan_2026-05-09.md) for locale-first + RunComfy parallel annotations (**separate ws / PR — not here**). |
| `ws_runcomfy_workflow_compatibility_audit_20260509` | Pearl_Int | Environment matrix vs Pearl Star workflows (nodes, loaders, LoRAs). |
| `ws_runcomfy_cost_alert_dashboard_20260509` | Pearl_Brand | Exec/brand dashboard — monthly RunComfy spend panel + threshold surfacing (**80% yellow posture** mirrored from Pearl_Int alerting). |

**Handoffs:**

- **Pearl_Int:** RunComfy wiring + compatibility audit (`RUNCOMFY_API_TOKEN` **must exist in Keychain before dispatch test PRs merge** — operator confirms staging receipt).
- **Pearl_Dev:** batch orchestrator with dual dispatcher + parity logging.
- **Pearl_PM:** parallel plan doc reorder annotations (coordinate with #988 lineage).
- **Pearl_Brand:** operational spend UX for operators reviewing soft-cap posture.

### CI-BASELINE-RECOVERY-V1-01 — CI baseline recovery: required-check root causes + phased recovery (Pearl_DevOps cap + spec 2026-05-09)

**Status:** **complete** — **AMENDMENT-20260527-CI-BASELINE-RECOVERY-COMPLETE** (Phase 4 acceptance PARTIAL; ruleset merge path without `--admin` restored).

#### CI-BASELINE-RECOVERY-V1-01 — AMENDMENT-20260527-CI-BASELINE-RECOVERY-COMPLETE

**Authorization:** Pearl_DevOps `ws_ci_recovery_acceptance` close-out **2026-05-27**.

**`main` HEAD anchor:** `15b46e37a29d5a6349e0d0cfa1a189f6ba1abc18` (PR #1325).

**Verdict:** **PARTIAL** (see `artifacts/qa/ci_baseline_recovery_v1_acceptance_20260527.md`).

**Binding outcomes:**

1. **Phase 1 (#997)** — `Verify governance` false positive on `bypass_actors` audit field: **fixed**; green on merge commits and current `main`.
2. **Phase 2 (#1006 policy + #1011 WARN)** — author `cover_art` gate **relax-to-warn** per AMENDMENT-2026-05-10: **landed**; **Core tests** **success** on `main` HEAD at acceptance time.
3. **Ruleset merge hygiene** — GitHub ruleset `13451138` requires **only** `Verify governance`; last **3** merged PRs (#1325, #1324, #1323) and last **15** sampled merges: **no** merge commit with failing `Verify governance` → **routine `--admin` for required-check bypass is no longer the default path**.
4. **OPD-152** — PR-template cascade-prevention checkbox for planner/composer signal + test assertion co-commit: **landed** (PR #1322 chain).
5. **OPD-153** — `Workers Builds: pearl-prime` reclassified as **accepted non-blocking noise**; operator dashboard disconnect remains optional (audit Path A1).
6. **PR #1325** — `preflight_push.sh` surfaces max OPD on `origin/main` to reduce numbering collisions.

**Deferred (not blocking this amendment):**

- **Release gates** still **failure** on `main` HEAD — continue under **`ws_ci_recovery_release_gates`** (Phase 3).
- **EI V2 gates** — not observed on acceptance HEAD (path-filter / trigger gap); address only if promotion to ruleset required.

**Project / workstream status:** `PRJ-CI-BASELINE-RECOVERY-V1` → **completed**; `ws_ci_recovery_acceptance` → **completed**; `ws_ci_recovery_release_gates` → **runnable** (Release gates green).

**Anti-drift:** Do not claim full yaml-contract green (`Core` + `Release` + `EI V2` + `Verify governance`) on `main` until Release gates Phase 3 evidence exists — this amendment closes the **ruleset / `--admin`** recovery goal only.

---

**Prior status (archived):** **proposed** — pending operator priority pick and answers to Q1–Q3 in `docs/specs/CI_BASELINE_RECOVERY_V1_SPEC.md` §16.

**Subsystem:** `pearl_devops` (primary); coordination with `Pearl_Editor` on cover art policy.

**Context:** `main` @ `465b772186f049fa3ce63453ccdc616bc5d98e23` exhibits failing **required** checks (**Core tests**, **Release gates** when path-filter triggers, **Verify governance**) driven by (1) production readiness **condition 18** / missing `assets/authors/cover_art/*_base.png` vs `config/authoring/author_cover_art_registry.yaml`, and (2) `verify_github_governance.py` **FORBIDDEN_PATTERNS** false positive on legitimate `bypass_actors` field references in `scripts/ci/check_branch_protection_ruleset.py` (scanner line **29**; `check_no_bypass_scripts` loop ~**141–165**). Routine PR merges currently require **`--admin`** to bypass branch protection — this cap scopes recovery so **`--admin` is no longer the default merge path**.

**Authority bundle:** `docs/GITHUB_OPERATIONS_FRAMEWORK.md`; `docs/GITHUB_GOVERNANCE.md`; `docs/BRANCH_PROTECTION_REQUIREMENTS.md`; `config/governance/required_checks.yaml`; `CLAUDE.md` rule 0 (mass deletion).

**Project / workstreams:** `PRJ-CI-BASELINE-RECOVERY-V1` in `artifacts/coordination/ACTIVE_PROJECTS.tsv`; `ws_ci_recovery_verify_governance_bypass`, `ws_ci_recovery_core_tests_cover_art`, `ws_ci_recovery_release_gates`, `ws_ci_recovery_acceptance` in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`.

**Canonical spec:** `docs/specs/CI_BASELINE_RECOVERY_V1_SPEC.md` (per-check URLs, phased plan, anti-drift, budget, operator decision card).

**Out of scope (this cap):** remediation code changes; edits to `required_checks.yaml` / live rulesets **before** fixes land and prove green on `main`.

**Anti-drift (summary):** Preserve all historical `--admin` audit trail; post-recovery reserve `--admin` for true emergencies; new required checks must prove green before promotion; cover-art gate should trend toward **warn-not-fail** for missing assets (Pearl_Editor follow-up) once operator selects option in §16 Q2.

**Action items:**
1. Operator: answer **Q1–Q3** in `docs/specs/CI_BASELINE_RECOVERY_V1_SPEC.md` §16 (verbatim card).
2. Pearl_DevOps: after ratification, execute **Phase 1** (`ws_ci_recovery_verify_governance_bypass`) then **Phase 2–4** per spec.
3. Pearl_PM: track statuses in coordination TSVs through acceptance.

### CI-BASELINE-RECOVERY-V1-01 — AMENDMENT (2026-05-10): Phase 2 ratified; cover_art gate Q2 = relax-to-warn

**Baseline:** Cap `CI-BASELINE-RECOVERY-V1-01` landed via merge **PR #980** (operator-approved recovery cap on `main`).

**Ratified Phase 2 posture:** Core tests recovery for production readiness **condition 18** (author cover art / `scripts/ci/check_author_cover_art.py` and its readiness integration) proceeds under **§16 Q2 option (B)**: treat missing registry-referenced `cover_art_base` PNGs under `assets/authors/cover_art/` as **WARN**, not **FAIL**, until assets are filled or policy is amended again. Aligns with the cap’s anti-drift note that cover-art gates should trend toward **warn-not-fail** once catalog posture is explicit.

**Scope of this amendment:** Documentation and coordination only. **No gate code change** in the amendment PR; the implementation PR that actually relaxes severity is a **follow-up**, tracked as **`ws_ci_recovery_phase_2_impl_20260510`** (runnable).

**Operator Q2:** **relax-to-warn** — pre-approved for this session under standing operator authority for `CI-BASELINE-RECOVERY-V1-01` (no additional authorization required).

**Execution order:** Phase 1 (Verify governance) remains first in the default sequence; Phase 2 implementation may proceed after Phase 1 green per spec §3 unless an incident reorder is separately recorded.

**Where recorded:** `docs/specs/CI_BASELINE_RECOVERY_V1_SPEC.md` — appended Phase 2 cover_art relaxation detail; `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` — `ws_ci_recovery_core_tests_cover_art` advanced to **runnable**, new **`ws_ci_recovery_phase_2_impl_20260510`** row **runnable**.

#### WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 — AMENDMENT-2026-05-10-CELL-MATH-CORRECTION (operator Gap #3 ratification)

**Authorization:** Operator clarification **2026-05-10** (Pearl_Architect doc-only propagation).

**Verbatim production facts (locked):**

- **Regular worldwide catalog:** **37 brands × 3 locales (`en_US`, `ja_JP`, `zh`) × 2 Phoenix surfaces (`ebook`, `manga`) = 222 cells.** Locale mix: **en_US** ebook-heavy with some manga; **ja_JP** higher manga % vs en_US; **zh** similar mix per market research.  
- **Audiobook:** **NOT** a Phoenix Omega cell. Each ebook script is the **script** for the audiobook; brand admin generates/list MP3 via **Google Play** dashboard for supported languages.  
- **Podcast:** **Separate planning track** — **not** counted in the **222** regular cells.  
- **Japan manga-only parallel catalog (NEW program):** **37 brands** with **IDENTICAL `brand_id` keys** to the regular 37 × **`ja_JP` locale** × **manga-only** surface = **37 cells**. **Separate Japanese company / legal entity.** Distribution: **Line Manga** (primary; PR #801 research lineage) **+ other JP manga platforms** (vs regular ja_JP lane → Google Play + Amazon, etc.). Same character/voice/brand narrative IDs; **different** storefront + financial entity.  
- **Total Phoenix-Omega-planned cells:** **222 + 37 = 259**.

**Anti-drift (hard):**

1. The **555** cell figure (PR #1023 + PR #1027 deck lineage) is **SUPERSEDED**; authoritative denominator is **259** until a future operator **AMENDMENT** changes it.  
2. **Audiobook generation is NEVER a Phoenix Omega cell** — future docs claiming otherwise are drift.  
3. Japan manga-only **`brand_id` set is IDENTICAL** to the regular 37 — adding net-new brand IDs requires an **AMENDMENT**.  
4. **Operator decision Gap #3 ratified:** authoritative production cell total is **259** (`authoritative-is-259`).

**Deliverable pointers:** `docs/specs/PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md`; `artifacts/catalog/worldwide_catalog_plan_{en_US,ja_JP,zh}_2026-05-10.tsv`; `brand-wizard-app/public/pearl_prime_v6-3-en.html`.

**Phase 2 catalog completion line (cross-edit):** The historical bullet that read “37 × 3 × 5 surfaces” in **AMENDMENT-2026-05-10-PHASE-1-P0-COMPLETE §3** is **superseded for cell math** by this amendment — Phoenix-counted worldwide cells are **ebook+manga = 222** plus **Japan manga-only = 37**.

---

#### WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 — AMENDMENT-2026-05-11-V1-1-37-BRAND-ACTIVATION (operator Q1–Q4 ratification; PR #1037 allocation stack)

**Authorization:** Operator decision card answers on **PR #1037** / `docs/specs/PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md` appendix + `docs/specs/MANGA_ONLY_BRAND_ALLOCATION_V1_SPEC.md` — **Pearl_Architect** doc-only ratification **2026-05-11** (Tier 1). **BINDING:** Q1–Q4 below cannot be reversed by downstream agents without a **separate operator AMENDMENT**. **37 Path X `brand_id` values** remain **frozen** (`config/manga/canonical_brand_list.yaml` — no edits in this wave).

**Operator decisions (verbatim):**

- **Q1** = **V1.1** (ship all **25** missing alongside existing **12**; single Phase 2 wave).
- **Q2** = **approve** (**5** series × **5** episodes per brand-locale-surface; default).
- **Q3** = **parallel-locales** (all **4** locales simultaneously per brand).
- **Q4** = **blocked_lora-first** (**zh_TW** + **zh_CN** `blocked_lora` cleanup before `blocked_score`).

---

##### 1. PHASE 2 V1.1 SCOPE (Q1=V1.1 single wave)

- All **37** Path X canonical brands ship in **V1.1** (**12** existing teacher brands + **25** missing manga-only/category brands).
- **V1.1** wave produces **200** **NEW** brand-locale-surface cells (**25** brands × **4** locales × **2** surfaces) **ON TOP OF** existing **12**-brand × **4**-locale × **2**-surface = **96** cells.
- **Total V1.1 cells: 296** (per **PR #1037** TSV row count: `artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv`).
- **V1.2 deferred:** **NOT** a deferred-brand pile; reserved for **surface expansion** (e.g., adding **video** to brands that currently have **ebook+manga**).
- **Anti-drift:** do **NOT** spawn **V1.2-deferred-brand** workstreams; if any agent surfaces “ship **25** brands later,” that violates **Q1=V1.1** ratification.

##### 2. BRAND VOLUMES (Q2=approve default 5×5)

- Default per brand-locale-surface: **5** series × **5** episodes = **25** content units.
- Total **V1.1** content units (excluding existing **12**): **200** cells × **25** units = **5,000** new content units.
- Plus existing **12** brands × **4** locales × **2** surfaces × **25** units = **2,400** (or already partially produced).
- **TOTAL V1.1 target: ~7,400** content units worldwide (**en_US** + **ja_JP** + **zh_TW** + **zh_CN** regular catalogs).
- **Note:** Japan-manga-only catalog (**37** cells, separate cap, parallel program) is **NOT** counted in **V1.1** worldwide totals; it runs as **`PRJ-JAPAN-MANGA-ONLY-CATALOG-V1`**.
- **Anti-drift:** per-brand volume override requires **AMENDMENT** (not silent edits to TSV).

##### 3. LOCALE PARALLELISM (Q3=parallel-locales)

- All **4** locales (**en_US**, **ja_JP**, **zh_TW**, **zh_CN**) generate **simultaneously** per brand.
- **Pearl Star** + **RunComfy** dual-path handles concurrent dispatch (per **IMG-RENDER-DUAL-PATH-V1-01** + **AMENDMENT-2026-05-10-PATH-BY-WORKFLOW**).
- **Cost expectation:** RunComfy **$10/mo** cap will be exercised more aggressively than serial-locale approach; **Pearl Star** handles overflow.
- **Anti-drift:** any agent that switches to **serial-locale** (**en-first**) without operator **AMENDMENT** violates **Q3**.
- **Pearl_Conductor v3** (when fired) **MUST** honor **parallel-locale** dispatch order.

##### 4. CLEANUP PRIORITY (Q4=blocked_lora-first)

**Pearl_Dev** priority order:

1. **zh_TW** + **zh_CN** `blocked_lora` rows (**~150** total per **PR #1035** audit).
2. **zh_TW** `blocked_score` rows (**160** per audit).
3. **ja_JP** `warrior_calm` tentpole mismatch (single-brand metadata fix).

**Rationale:** `blocked_lora` blocks **all** rendering for those rows; `blocked_score` blocks promotional metadata but **doesn't** gate renders.

**Anti-drift:** do **not** interleave `blocked_score` before `blocked_lora` unless operator **AMENDMENT**.

##### 5. STATUS TRANSITIONS

- Cap entry **WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01:** continues as **ACTIVE** (**Phase 1 P0** complete via **#1022**; **Phase 2** begins now).
- Workstreams ratified to **runnable** per **Q1**:
  - `ws_catalog_generator_extend_to_37_brands_20260511` → **runnable** (**Pearl_Dev**; the most critical-path ws).
  - `ws_zh_manga_blocked_lora_followup_20260511` → **runnable** (**Pearl_Dev**; per **Q4** priority).
  - `ws_zh_manga_blocked_score_followup_20260511` → **status=queued** (waits on `blocked_lora` completion).
- **NEW** workstreams opened by this **AMENDMENT**:
  - `ws_catalog_generator_v1_1_25_brand_authoring_20260511` → **runnable** (**Pearl_Marketing**; authors per-brand series themes for the **25** missing brands).
  - `ws_pearl_conductor_v3_full_queue_activation_20260511` → **status=queued_after_v1_1_authoring** (**Pearl_Dev**; fires unattended generation once **25**-brand themes authored + generator extended + `blocked_lora` cleared).
  - `ws_warrior_calm_ja_jp_tentpole_fix_20260511` → **status=queued** (**Pearl_Editor**; small metadata fix).

##### 6. ACTION ITEMS (named for next-router fan-out; not authored here)

| ID | Owner | Action |
|---|---|---|
| **a.** | **Pearl_Dev** | Extend catalog generator to **37** Path X brands (consume **PR #1037** TSV; mirror `music_mode_branch.py` pattern from **#1008**). |
| **b.** | **Pearl_Marketing** | Author per-brand series themes for the **25** missing brands (e.g., `healing_ground` series titles, workplace brands' topic anchors, romance brands' arc shapes). |
| **c.** | **Pearl_Dev** | Clear **zh_TW** + **zh_CN** `blocked_lora` rows (**~150** rows) — likely LoRA training or asset gating fix. |
| **d.** | **Pearl_Editor** | **ja_JP** `warrior_calm` tentpole metadata fix (single-brand). |
| **e.** | **Pearl_Dev** (after **a**+**b**+**c**): | **Pearl_Conductor v3** prompt — full-queue unattended generation against all **37** × **4** locales × **2** surfaces (estimated **5–10** days wall on **Pearl Star** + **RunComfy** under **$10** cap). **DO NOT** spawn / fire **v3** until **a**, **b**, and **c** are satisfied — this **AMENDMENT** is the gate. |
| **f.** | **Pearl_Brand** | Dashboard updates to surface **37**-brand status + **V1.1** progress per brand. |
| **g.** | **Pearl_Architect** | Closeout **AMENDMENT** once **V1.1** completes (target: **7,400** content units shipped; first end-to-end worldwide brand catalog ratified at **100%**). |

**Pointers:** **PR #1037** (allocation plan TSV); **PR #1035** (status diagnostic); **PR #1022** (Phase 1 P0 closure); **AMENDMENT-2026-05-10-PATH-BY-WORKFLOW** (dual-path routing); `docs/specs/MANGA_ONLY_BRAND_ALLOCATION_V1_SPEC.md`; `artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv`.

---

#### PER-CHAPTER-OVERLAY-ENFORCEMENT-V1-01 — AMENDMENT-2026-05-10-GAP-1-NERVOUS-SYSTEM-FOLLOWUP

**Operator decision (Gap #1):** Remove **`your nervous system`** from `refrain_allowlist` **after** overlay Phase 2 proves the gate catches it.

**Action:** Open follow-up workstream **`ws_phase_2_item_2_remove_nervous_system_after_overlay_proven_20260510`** (Pearl_Dev): demonstrate overlay catches the phrase via **test fixture**; **then** remove the allowlist entry in a subsequent PR (ITEM-2 chain).

---

#### PER-CHAPTER-OVERLAY-ENFORCEMENT-V1-01 — AMENDMENT-2026-05-10-GAP-2-IMPL-COMPLETE

**Operator decision (Gap #2):** Mark **`ws_per_chapter_overlay_enforcement_impl_20260508`** **complete** (was `proposed`).

**Evidence:** `phoenix_v4/quality/book_quality_gate.py` **`_overlay_violations`** (**lines 176–286**) — overlay rule kinds **`density_ceiling`**, **`drift_detection`**, **`presence_floor`**, **`absence_guard`** — plus **`_repeated_phrase_violations`** integration entrypoint (**from line 287**), i.e. the **~176–297** window Pearl_Architect cited for Phase 1–2 overlay enforcement landing on `main`.

---

#### PER-CHAPTER-OVERLAY-ENFORCEMENT-V1-01 — AMENDMENT-2026-05-10-GAP-4-CAP-BANNER-CLEANUP

**Operator decision (Gap #4):** **cleanup-now** — cap status banners drift from merged `main` reality.

**Action:** Open **`ws_phase_2_cap_status_banner_cleanup_20260510`** (Pearl_PM): pass through **all** cap entries’ status banners in `docs/PEARL_ARCHITECT_STATE.md` (and linked coordination surfaces) and reconcile with **merged `main`** reality; small Pearl_PM follow-up PR.

---

### JAPAN-MANGA-ONLY-CATALOG-V1-01 — Japan parallel manga-only catalog (BG-PR-09 house style)

**Status:** **proposed** — pending operator confirmation of legal/business decisions.

**PROJECT_ID:** `PRJ-JAPAN-MANGA-ONLY-CATALOG-V1`

**Context:** Operator clarified Japan operates **two** parallel catalogs: **(a)** regular worldwide catalog includes **`ja_JP`** variants on Google Play / Amazon / etc., and **(b)** a **Japan-only manga catalog** (37 brands × manga surface) distributed via a **separate Japanese company** contracting **Line Manga** + other JP manga platforms.

**Decision (architecture):**

- **37 `brand_id` values** are **IDENTICAL** to `config/manga/canonical_brand_list.yaml` — **no new brand IDs**.  
- **Surface scope:** **manga only** (no ebook, no podcast, no video) for this program cap.  
- **Distribution:** **Line Manga** primary (per PR #801 research lineage) + **other JP manga platforms TBD**.  
- **Legal entity:** **separate Japanese company** (operator-side corporate action; documented here only).  
- **Financial flow:** **separate** from regular Phoenix Omega economics (different platform rev-share + different brand-admin posting path).

**Anti-drift:**

1. **37 brand IDs IDENTICAL** to canonical list — net-new IDs require **AMENDMENT**.  
2. **Manga-only scope is BINDING** — adding ebook/podcast/video requires **AMENDMENT**.  
3. **Cross-catalog character/voice consistency:** characters **MUST** match regular per-brand `character_design` — drift = quality risk.  
4. **Separate legal entity is operator-side** — do **not** auto-create code assuming single-entity ownership.

**Action items (tracked as workstreams; not fully authored in this PR):**

| Workstream ID | Owner | Purpose |
|---|---|---|
| `ws_japan_manga_only_catalog_scoping_20260510` | Pearl_PM + Pearl_Marketing | Author per-brand manga catalog (37 × series/episode counts) for Japan manga-only program. |
| `ws_japan_manga_only_platform_contract_research_20260510` | Pearl_Research | Refresh PR #801 Line Manga research with Japan-manga-only terms. |
| `ws_japan_manga_only_legal_entity_decision_20260510` | Operator-side | Confirm separate Japanese company structure with counsel. |
| `ws_japan_manga_only_brand_admin_separation_20260510` | Pearl_Dev | Wizard / brand-admin path for Japan-manga-only (same vs separate Japanese-only wizard). |

**Operator decision card (Q1–Q4):**

1. **Q1:** Confirm **37 brand IDs identical** to regular catalog (vs different IDs for legal separation)?  
2. **Q2:** Manga volume per brand for Japan-manga-only — **same** as regular `ja_JP` manga %, **or higher** because the catalog is manga-dedicated?  
3. **Q3:** Brand admin separation — **same wizard** vs **separate Japanese-only wizard**?  
4. **Q4:** Timeline — **Phase 2 alongside V1.1 worldwide expansion**, **or Phase 3** after worldwide V1 ships?

**Authority:** This cap entry + `docs/specs/JAPAN_MANGA_ONLY_CATALOG_V1_SPEC.md` (detail).

---

### TEACHER-MODE-WRAPPER-SEMANTICS-01 — Teacher voice wraps persona+topic substance; never substitutes (decision approved 2026-05-17)

**Status:** **ratified-as-drafted** (operator approved 2026-05-17 per audit §7 reroute).

**Context:** [`artifacts/qa/persona_topic_yaml_specificity_audit_20260517.md`](../artifacts/qa/persona_topic_yaml_specificity_audit_20260517.md) §6 identified the primary root cause of operator-reported vague/generic books: the loader at [`phoenix_v4/planning/enrichment_select.py:982-1080`](../phoenix_v4/planning/enrichment_select.py) performs "additive stacking" (persona_atom → registry → teacher_atom, all three fire) without per-slot precedence rules. Result: teacher atoms fire on ~60/120 slots (~50%) and frequently override the substance of slots where persona+topic atoms should dominate. Smoking gun (audit §4): Chapter 1 opens with `ahjan_HOOK_011` ("Every person carries the capacity for awakening...") instead of [`registry/anxiety.yaml:25`](../registry/anxiety.yaml) ("You did everything they said to do. Your chest has not gotten the memo..."). The teacher voice substituted for the topic-specific somatic hook even though the HOOK slot's body should come from persona+registry. This cap entry locks the **substance vs voice** distinction and resolves the per-slot precedence ambiguity that TEACHER-POOL-SEMANTICS-01 left underspecified.

**Decision: Teacher banks are a VOICE layer that wraps the SUBSTANCE layer (persona × topic atoms + topic registry). Per-slot precedence is locked per the table below.**

**Per-slot precedence (locked):**

| Slot type | Body (substance) source — first match wins | Voice wrapper allowed? |
|---|---|---|
| HOOK | `atoms/<persona>/<topic>/HOOK/*` → `registry/<topic>.yaml` | ≤1 line teacher framing at opening only; teacher HOOK atoms fall back ONLY when persona+registry empty |
| SCENE (sec 2/5/9) | `atoms/<persona>/<topic>/<engine>/CANONICAL.txt` (engine-bank, named-character continuity per `SOURCE_OF_TRUTH/story_atoms/character_roster.yaml`) | ≤2 lines teacher framing at scene open/close; teacher SCENE atoms fall back ONLY when persona engine-bank empty |
| STORY | same as SCENE — persona engine-bank first | same wrapper rule as SCENE |
| COMPRESSION | `atoms/<persona>/<topic>/COMPRESSION/*` → `registry/<topic>.yaml` mechanism vocab | teacher voice for cadence only; never replaces mechanism vocabulary |
| PERMISSION | `atoms/<persona>/<topic>/PERMISSION/*` → `registry/<topic>.yaml` | teacher voice for cadence only |
| PIVOT | `atoms/<persona>/<topic>/PIVOT/*` → `registry/<topic>.yaml` | teacher voice for cadence only |
| TAKEAWAY | `atoms/<persona>/<topic>/TAKEAWAY/*` → `registry/<topic>.yaml` | teacher voice for cadence only |
| THREAD | `atoms/<persona>/<topic>/THREAD/*` → `registry/<topic>.yaml` | teacher voice for cadence only |
| TEACHER_DOCTRINE | `SOURCE_OF_TRUTH/teacher_banks/<teacher>/approved_atoms/TEACHER_DOCTRINE/*` (teacher OWNS this slot) | n/a |
| REFLECTION | `SOURCE_OF_TRUTH/teacher_banks/<teacher>/approved_atoms/REFLECTION/*` (teacher OWNS) | n/a |
| INTEGRATION | `SOURCE_OF_TRUTH/teacher_banks/<teacher>/approved_atoms/INTEGRATION/*` (teacher OWNS) | n/a |
| EXERCISE | per existing EXERCISE-BANK-RESOLUTION-01 (PR #912 strict-canonical) | n/a (locked separately) |
| QUOTE | per existing QUOTE-ATOM-ROUTING-01 (migrate to TEACHER_DOCTRINE / REFLECTION / INTEGRATION) | n/a (locked separately) |

**Story selection order for SCENE / STORY slots (sec 2/5/9 per BESTSELLER-INJECTIONS-MANDATORY-01):**
1. PRIMARY — `atoms/<persona>/<topic>/<engine>/CANONICAL.txt` (engine-bank, 2,584 files per [`phoenix_v4/planning/pool_index.py:7`](../phoenix_v4/planning/pool_index.py); proven 27/30 bestseller-grade in [`artifacts/qa/move4_2026_04_26/per_persona_topic_coverage.md`](../artifacts/qa/move4_2026_04_26/per_persona_topic_coverage.md))
2. WRAPPER — teacher voice ≤2 lines framing the scene open/close (cadence, register, gesture toward the body) — wraps the scene; does not replace the named-character continuity
3. FALLBACK ONLY — `SOURCE_OF_TRUTH/teacher_banks/<teacher>/approved_atoms/STORY/*` ONLY when the persona engine-bank pool is empty for the (`<persona>`, `<topic>`, `<engine>`) tuple

**Voice-wrapper rules (when teacher voice augments a substance slot):**
- **Scope:** framing only — opening or closing line of the slot, transition cadence — NEVER the body sentence(s) carrying mechanism vocabulary, named-character continuity, or somatic specificity
- **Line budget:** HOOK ≤1 wrapper line; SCENE/STORY ≤2 wrapper lines per scene; other substance slots cadence-only (no extra lines, just stylistic register)
- **Doctrine compliance:** wrapper honors `SOURCE_OF_TRUTH/teacher_banks/<teacher>/doctrine/doctrine.yaml` (tradition, tone, forbidden claims)
- **Mechanism-specificity preserved:** wrapper line must NOT contradict, soften, or generalize the topic-specific mechanism vocabulary from the substance source

**Anti-drift check:**
- SUPPLEMENTS TEACHER-POOL-SEMANTICS-01 (first-match deterministic but WHICH pool was unspecified — this cap resolves it)
- SUPPLEMENTS BESTSELLER-INJECTIONS-MANDATORY-01 (clarifies the injection content at sec 2/5/9 comes from persona engine-bank, not teacher banks)
- SUPPLEMENTS PEARL-EDITOR-UPSTREAM-01 (formalizes content-authority vs voice-authority layer separation)
- DOES NOT CONTRADICT EXERCISE-BANK-RESOLUTION-01 / QUOTE-ATOM-ROUTING-01 / BG-PR-09
- Retires unqualified "additive stacking" framing for substance slots: the loader still STACKS sources, but precedence per the table above selects the BODY; teacher contributions in substance slots are wrapper-only per the line-budget rule

**Handoffs (Pearl_PM opens these 3 ws's after merge; ws rows seeded by this PR in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`):**

- **Pearl_Dev (PRIMARY) — `ws_teacher_wrapper_semantics_impl_20260517`**: amend [`phoenix_v4/planning/enrichment_select.py:982-1080`](../phoenix_v4/planning/enrichment_select.py) per-slot waterfall to encode the precedence table above. For substance slots: persona+registry wins on body; teacher contributes wrapper line(s) within the line-budget rule. For voice slots (TEACHER_DOCTRINE / REFLECTION / INTEGRATION): teacher wins. Add test fixture `tests/test_teacher_wrapper_semantics.py` covering: (i) HOOK body sourced from persona+registry when both pools non-empty; (ii) teacher HOOK falls back ONLY when persona+registry empty; (iii) SCENE wrapper line-budget enforced; (iv) voice slots remain teacher-owned. ~50-100 lines including tests. Acceptance: re-run `--quality-profile production` for ahjan × gen_z_professionals × anxiety × standard_book; Chapter 1 opens with `registry/anxiety.yaml:25` somatic hook (not `ahjan_HOOK_011`); karma/Dharma/Buddha/enlightenment counts ≤ 2 each per chapter; `bestseller_craft.overall_score` ≥ 0.55.

- **Pearl_Dev (FOLLOW-UP) — `ws_enrichment_audit_section_packet_serialization_fix_20260517`**: fix the serialization type-bug at [`scripts/run_pipeline.py:1406`](../scripts/run_pipeline.py) so `enrichment_audit.json` includes the `story_schedule` key per audit §7.4. ~10 lines. Unblocks audit §7.2's story_schedule diagnosis ws.

- **Pearl_Editor + Pearl_Writer — `ws_ahjan_teacher_bank_framing_reauthor_20260517`** (replaces the audit's §7.1 ws at a NEW SMALLER scope per this cap entry's wrap-not-replace rule): re-author the ahjan teacher_bank HOOK/REFLECTION/COMPRESSION subset as anxiety-AWARE FRAMINGS (~12-15 wrapper-style atoms total — opening/closing lines in ahjan voice that gesture at the body, the felt sense, the moment). NOT full substantive essays — the substance comes from persona+topic atoms and `registry/anxiety.yaml`. Scope intentionally smaller than the audit's original §7.1 estimate because this cap routes substance to persona+topic and reserves teacher banks for voice. Gated on `ws_teacher_wrapper_semantics_impl_20260517` landing (semantics first, then re-author against locked rules).

**Authority:** This cap entry + the supplemented entries above + [`docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`](./PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md) §570-577 (canonical CLI) + [`specs/PHOENIX_V4_5_WRITER_SPEC.md`](../specs/PHOENIX_V4_5_WRITER_SPEC.md) §4 (three-source content rule).

---

### JOSHIN-SHINGON-KENJIN-ZEN-01 — Joshin recast to Shingon; new Kenjin Roshi (Sōtō Zen) carries existing Zen content (OPD-105 approved 2026-05-18)

**Decision-of-record:** [`artifacts/coordination/operator_decisions_log.tsv`](../artifacts/coordination/operator_decisions_log.tsv) OPD-20260518-105.

**Authority sources:**
- Plan: [`docs/migrations/JOSHIN_SHINGON_KENJIN_ZEN_MIGRATION_PLAN_2026-05-18.md`](./migrations/JOSHIN_SHINGON_KENJIN_ZEN_MIGRATION_PLAN_2026-05-18.md)
- Research foundation: [`docs/research/shingon_buddhism_research_2026-05-18.md`](./research/shingon_buddhism_research_2026-05-18.md)
- Joshin doctrine v3: [`SOURCE_OF_TRUTH/teacher_banks/joshin/doctrine/doctrine.yaml`](../SOURCE_OF_TRUTH/teacher_banks/joshin/doctrine/doctrine.yaml)
- Kenjin doctrine v1: [`SOURCE_OF_TRUTH/teacher_banks/kenjin/doctrine/doctrine.yaml`](../SOURCE_OF_TRUTH/teacher_banks/kenjin/doctrine/doctrine.yaml)

**What changed:**
- **Joshin (display_name: "Joshin"):** tradition recast to **Shingon Esoteric Buddhism (Kōyasan Shingon-shū, Kogi branch)**. Honorific = `ajari` (NOT roshi). Doctrine v3 grounds in sokushin-jōbutsu, sanmitsu, dual mandala, rokudai, honpushō. Signature practices: gohōgō recitation ("Namu Daishi Henjō Kongō"), susokukan, hokkai-jō-in mudrā + Kōmyō Shingon, gachirin-kan, Ajikan. Heart Sutra opening: "Bussetsu Maka Hannya Haramita Shingyō" (with Bussetsu prefix — Shingon form).
- **NEW teacher: `kenjin` (display_name: "Kenjin Roshi"):** Sōtō Zen Buddhism (Eihei-ji line). Male, late 50s, Japanese-American (Kyoto-born, Bay Area sangha). Honorific = `roshi`. Signature practices: shikantaza, kinhin, oryoki, koan inquiry. Heart Sutra opening: "Maka Hannya Haramita Shingyō" (no Bussetsu prefix — Zen form). 4 STORY atoms migrated from Joshin (canonical Zen-genre parables).
- **Cognitive Clarity / Clear Seeing Books brand:** wholesale-migrated from joshin to kenjin per OPD-105 operator decision #1 (Option C). 132 book_plans + 44 series_plans renamed (`cognitive_clarity__joshin__*` → `cognitive_clarity__kenjin__*`). 6 Zen-coded authors (Ada Park, Joel Crane, Hana Lee, Marcus Stone, Yuki Tanabe, Elliot Vane) wholesale-keep with Kenjin (operator decision #5). All catalog_planning routing tables (lane_assignments × 12 locales, brand_identity_system, teacher_brand_archetypes, brand_display_names, etc.) updated.
- **`still_forest` brand:** tradition rewritten from "Forest meditation / nature connection" (third-axis drift, neither Zen nor Shingon) to "Mount Kōya forest training, ajari-led contemplative stillness" (Shingon-grounded forest framing per operator decision #4). Applied across `config/brand_management/teacher_brand_map.yaml` + `global_brand_registry.yaml` (13 region instances).
- **Pearl_News scope:** Joshin's Pearl_News entry was already correctly Shingon (no change). Kenjin is NOT added to Pearl_News per OPD-105 explicit scope.

**Operator decisions (5 approved):**
1. (P0) Cognitive Clarity routing → **Option C** (wholesale to Kenjin; Joshin gets new Shingon brand in follow-up commission per migration plan §6.B)
2. (P1) Joshin's Shingon sub-school → **Kōyasan Shingon-shū (Kogi)**
3. (P1) Kenjin's identity → **Male, late 50s, Japanese-American (Bay Area), Sōtō Zen**
4. (P1) `still_forest` reconciliation → **Reconcile in same migration**
5. (P2) Clear Seeing Books 6-author roster → **Wholesale-keep with Kenjin**

**PRs (4-phase migration, stacked):**
- Phase 1: PR #1207 — Joshin Shingon doctrine + Kenjin teacher card (5 files)
- Phase 2: PR #1208 — Cognitive Clarity wholesale brand migration to Kenjin (204 files)
- Phase 3: PR #1209 — Joshin Zen-tell atom corrections + still_forest reconciliation (8 files)
- Phase 4: PR (this commit) — docs + tests + governance backfill

**Out of scope (follow-up commissions, per migration plan §6.B):**
1. Joshin Shingon-coded brand authoring (new brand name + identity + colophon + tagline + 6+ new Shingon-coded authors)
2. Joshin new Shingon atom authoring (12 STORY + 12 EXERCISE + 12 SCENE atoms grounded in research §3 / §6.3)
3. Visual asset re-render for Joshin (Shingon iconography)
4. Audiobook prose regen for `artifacts/audiobook_samples/_prose/joshin_anxiety_ch1.txt`
5. Pearl_Video pilot regeneration if `joshin / cognitive_clarity / ja-JP` pilot was Zen-coded

**Authority:** This cap entry + the four phase PRs (1207, 1208, 1209, this PR).

---

### JUNKO-CHANNELING-MIYUKI-CONTEMPLATIVE-01 — Junko stays channeling; new Miyuki (Japanese contemplative) carries former wabi-sabi atoms (OPD-111 approved 2026-05-19)

**Decision-of-record:** [`artifacts/coordination/operator_decisions_log.tsv`](../artifacts/coordination/operator_decisions_log.tsv) OPD-20260519-111.

**Authority sources:**
- Plan: [`docs/migrations/JUNKO_CHANNELING_MIYUKI_CONTEMPLATIVE_MIGRATION_PLAN_2026-05-19.md`](./migrations/JUNKO_CHANNELING_MIYUKI_CONTEMPLATIVE_MIGRATION_PLAN_2026-05-19.md)
- Junko doctrine v2 (unchanged — channeling-correct): [`SOURCE_OF_TRUTH/teacher_banks/junko/doctrine/doctrine.yaml`](../SOURCE_OF_TRUTH/teacher_banks/junko/doctrine/doctrine.yaml)
- Miyuki doctrine v1 (new): [`SOURCE_OF_TRUTH/teacher_banks/miyuki/doctrine/doctrine.yaml`](../SOURCE_OF_TRUTH/teacher_banks/miyuki/doctrine/doctrine.yaml)
- Junko intake: [`teachers/junko/junko_doctrine_notes.rtf`](../teachers/junko/junko_doctrine_notes.rtf) + [`teachers/junko/junko_yt.rtf`](../teachers/junko/junko_yt.rtf)

**What changed:**
- **Junko (display_name: "Channeler Junko"):** doctrine unchanged (channeling/light-language/cosmic guidance/ascended masters per intake). 152 contemplative atoms (Japanese contemplative + body-anchored + ganbaru voice; e.g., STORY_003 opened "In the Zen tradition, there is a story…") MIGRATED OUT to new teacher `miyuki`. 152 NEW channeling atoms authored from intake material in same combined Phase 2+3 PR.
- **NEW teacher: `miyuki` (display_name: "Miyuki"):** Japanese contemplative (lay-secular, wabi-sabi, ganbaru, mono no aware). Honorific = null (operator decision #3). Geographic anchor = Kyoto (operator decision #4). Female, late 40s. Doctrine v1 grounds in ganbaru-as-practice, mono no aware, ma, body-first recognition, secular dailiness, small arrivals not breakthroughs. Signature practices: body_noticing, breath_anchored_sitting, kitchen_table_dawn, ganbaru_walk. Inherits 152 atoms wholesale (renamed junko_* → miyuki_*).
- **Relational Calm / Bare Form Books brand:** wholesale-migrated from junko to miyuki across all 14 catalog_planning files, 6 manga config files, 9 manga_profiles, 2 brand_management files (13 zen_clarity locale instances), 2 publishing files, 15 scripts, 2 tests, 1 workflow. Wabi-sabi visual register inherited (junko awaits new cosmic visuals in Phase 5 deferred re-render commission).
- **Hybrid Option III for cosmic canonical topics (operator decision #2):** both teachers share contemplative topics (anxiety, social_anxiety, burnout, sleep_anxiety, relational_harmony, shame, etc.); differentiation is voice register (junko=channeling/cosmic; miyuki=Japanese contemplative/lay-secular), not topic. No new canonical topics added.
- **register_gate.py:** Junko forbidden_tokens populated (zen, zazen, ganbaru, mono no aware, kitchen table, etc.). Miyuki forbidden_tokens added (channel, light language, ascended master, shingon, etc.).
- **Pearl_News scope:** Junko's Pearl_News entry already correctly channeling (no change). Miyuki is NOT added to Pearl_News per OPD-111 explicit scope (operator decision #6 — matches OPD-105 Kenjin precedent; Pearl_Prime-only).
- **Voice ID:** Miyuki audiobook voice = `ja_f_mature_warm_01` (operator decision #7).

**Operator decisions (7 approved):**
1. (P0) Phase 2 + Phase 3 PR shape → **Combined PR** (~302 files; avoids atom-empty Junko window)
2. (P0) Cosmic canonical topics → **Hybrid Option III** (shared topics, voice differentiation; no new topics added)
3. (P1) Miyuki honorific → **null** (matches Junko/Maat/Miki)
4. (P1) Miyuki geographic anchor → **Kyoto** (matches wabi-sabi voice in atoms)
5. (P1) 3 sample channeling atoms in plan §4.4 → **Approved** (used VERBATIM as HOOK_001, STORY_001, PIVOT_001)
6. (P2) Add Miyuki to Pearl_News → **No** (Pearl_Prime-only; matches OPD-105 Kenjin precedent)
7. (P2) Voice ID for Miyuki audiobook → **`ja_f_mature_warm_01`**

**PRs (4-phase migration, stacked):**
- Phase 1: PR #1219 — Miyuki teacher card (15 files)
- Phase 2+3 combined: PR #1220 — atom migration (152) + new Junko channeling atoms (152) = 308 files
- Phase 4: PR (this commit) — catalog routing across catalog_planning + manga + brand_management + publishing + scripts + tests + workflow + docs + register_gate
- Phase 5: PR (next) — visual asset rename (no re-render)

**Out of scope (follow-up commissions, per migration plan §7.C):**
1. Junko cosmic-coded brand authoring (new brand name + identity + colophon + 4-6 new luminous-coded authors)
2. Junko visual asset re-render (cosmic register: luminous robes, light particles, hands-raised mudras, gold/blue palette)
3. Junko's new bestseller book in channeling voice ("The Receivers" working title; ~1-2 Pearl_Writer sessions)
4. Miyuki Pearl_News integration if operator reverses decision #6
5. Voice audit for Miyuki audiobook (CosyVoice2 reference clip confirmation)

**Authority:** This cap entry + the four phase PRs (1219, 1220, this PR, and the Phase 5 PR).

---

### HOOK-SCENE-FIRST-01 — HOOK + ANGLE_DEFINITION atoms must open scene-first (1 specific person + 1 specific situation + 1 specific body posture); philosophy may appear AFTER the scene, never before (OPD-144 ratified 2026-05-21)

**Status:** **ratified** (operator decision 2026-05-21; logged 2026-05-23 via PR #1292; cap entry authored via this PR).

**Context:** Operator 2026-05-21 comparison of two AUTHORED reference books in `artifacts/pipeline_examples/`:

- **Miki — scene-first opening** (`artifacts/pipeline_examples/miki/book_miki_imposter_syndrome_15min.txt:26`): *"Somewhere right now, a person is sitting in a bathroom stall at their new job, pressing their phone against their thigh so nobody hears the screen light up, breathing through their mouth because their nose is too congested from the silent crying they did in the car on the way here."* Contains (1) specific person ("a person… at their new job"), (2) specific situation ("sitting in a bathroom stall"), (3) specific body posture ("pressing their phone against their thigh… breathing through their mouth"). Reader recognition arrives in sentence 1.
- **Omote — philosophy-first opening** (`artifacts/pipeline_examples/omote/book_omote_sleep_anxiety_15min.txt:27`): *"Nightfall strips the surface away. This happens automatically, without consent and without ceremony. The lights go off. The room darkens. The sounds of the day recede — traffic, conversation, the hum of machines and obligations and schedules and the low buzz of perpetual performance. And in the sudden quiet, the interior speaks."* Abstract event; no specific person; no specific body posture. Concrete reader recognition arrives at paragraph 4 ("The email that went unanswered…"). Operator: *"The Omote book ch1 is not as good as the Miki book."*

Both are AUTHORED reference texts (not pipeline-generated output) under `artifacts/pipeline_examples/{teacher}/`. The diagnosis is about an authoring rule (which way to open a HOOK), not a pipeline bug. Operator decision of record: **OPD-144** in `artifacts/coordination/operator_decisions_log.tsv` (recovered from `old_chat_specs/Untitled 127.txt` L91-110, landed via PR #1292 commit `74a8c6fa5`). Affected atom paths per OPD-144: `atoms/*/*/HOOK/CANONICAL.txt` and `atoms/*/*/ANGLE_DEFINITION/CANONICAL.txt`.

**Decision:** **HOOK atom first paragraph MUST contain (1) one specific person, (2) one specific situation/setting, (3) one specific body posture.** Philosophical or abstract claims may appear AFTER the scene, never before. This is the binding authoring rule for:

| Atom type | Path glob | Scope of rule |
|---|---|---|
| `HOOK` | `atoms/<persona>/<topic>/HOOK/CANONICAL.txt` | First paragraph must be scene-first |
| `ANGLE_DEFINITION` | `atoms/<persona>/<topic>/ANGLE_DEFINITION/CANONICAL.txt` | First paragraph must be scene-first (per OPD-144 affected_paths) |

Reading-order rule: **scene first, philosophy second.** Binding for NEW authoring as of 2026-05-21. EXISTING atoms are reviewed under the Pearl_Editor brief addendum ws (see Action items §1) — atoms that violate the rule are tagged for rewrite queue but NOT rewritten in that ws; the rewrite queue is a separate downstream ws gated on the brief addendum landing.

**Anti-drift check:**

- Does NOT contradict `TEMPLATE-UNIVERSAL-01` — HOOK is one of the 10 sections in `SOMATIC_10_SLOT_GRID`; this is a within-section authoring constraint, supplemental to the 12-spine × 10-section × 3-floor universal structure; doesn't change shape.
- Does NOT contradict `BESTSELLER-INJECTIONS-MANDATORY-01` — HOOK is grid-architectural across all profiles per `SOMATIC_10_SLOT_GRID`; this entry tightens HOOK *content quality*, doesn't add or remove an injection.
- Does NOT contradict `EXERCISE-BANK-RESOLUTION-01` — EXERCISE-scoped, no overlap.
- Does NOT contradict `SPEC-739-THRESHOLD-01` / `SPEC-739-VALIDATOR-MULTISOURCE-01` — threshold is shape/count of variations; this is content quality within a variation.
- Does NOT contradict `BG-PR-09 Phase-2 closeout` — STORY-at-sec-2/5/9 grid swap, no HOOK overlap.
- REINFORCES `PEARL-EDITOR-UPSTREAM-01` — routes the brief addendum + corpus tagging to Pearl_Editor consistent with the authority-flow framing (content authority precedes render consumption).
- No new spec authored in this entry. The scene-first rule MAY amend `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` in a future ws gated on Pearl_Editor brief addendum landing (deferred — Open Question Q2 below).

**Empirical state:** Sample of 5 HOOK CANONICAL.txt files (out of 211 total HOOK atoms surveyed during discovery): `atoms/midlife_women/anxiety/HOOK/CANONICAL.txt`, `atoms/entrepreneurs/anxiety/HOOK/CANONICAL.txt`, `atoms/midlife_women/imposter_syndrome/HOOK/CANONICAL.txt`, `atoms/midlife_women/sleep_anxiety/HOOK/CANONICAL.txt`, `atoms/entrepreneurs/overthinking/HOOK/CANONICAL.txt`. Distribution: **4/5 scene-first, 1/5 philosophy-first.** The philosophy-first atom is `atoms/entrepreneurs/overthinking/HOOK/CANONICAL.txt:7`, opening with *"Your worth is your business. Your business is your worth. So every decision becomes a referendum on your value as a human."* The sample is too small to be authoritative across the full 211-atom corpus, but it confirms the problem is **real and present** (~20% philosophy-first in this random slice) — worth a brief addendum + a detector, not hypothetical. Full corpus tagging is Pearl_Editor's ws scope.

**F11 detector ID claim:** Operator chose F11 per OPD-144 (`phoenix_v4/quality/register_gate.py (F11 detector target)` in OPD-144 affected_paths). Grep verification confirms F11 is unclaimed:

```
$ grep -RIn 'F11\b\|register.gate.F11\|RG.F11' . --include='*.py' --include='*.yaml' --include='*.md'  (excluding worktrees + old_chat_specs)
(no output)
```

F1–F8 currently claimed in `phoenix_v4/quality/register_gate.py:10-17` (F8 deferred pending anchor corpus at `artifacts/reference/trade_pub_anchors/`). F9 and F10 are unclaimed gaps — operator chose F11 explicitly, leaving F9/F10 reserved for future detectors (cap entry records this empirically; not Pearl_Architect's decision to renumber).

**Action items:**

1. **Pearl_Editor (`ws_pearl_editor_hook_scene_first_brief_addendum_20260523`)** — author brief addendum codifying the scene-first HOOK + ANGLE_DEFINITION authoring rule per this cap entry; review existing `atoms/*/*/HOOK/CANONICAL.txt` corpus (211 files) AND existing `atoms/*/*/ANGLE_DEFINITION/CANONICAL.txt` corpus; tag philosophy-first atoms for rewrite queue (do NOT rewrite in this ws — queue only). Output: `docs/PEARL_EDITOR_BRIEF.md` addendum section + a tagging artifact (e.g., `artifacts/qa/HOOK_SCENE_FIRST_TAGGING_*.tsv` — Pearl_Editor's call on format). Iteration cap = 1 PR. No code edits.
2. **Pearl_Dev (`ws_pearl_dev_register_gate_f11_hook_abstract_detector_20260523`)** — implement register-gate **F11: HOOK atom first-paragraph abstract-opening detector**. Triggers on first paragraph lacking concrete-person + concrete-situation + concrete-body-posture signal. Surface as register-gate **WARN** (not HARD_FAIL) until brief-addendum corpus pass completes. Add F11 line to `phoenix_v4/quality/register_gate.py:10-17` docstring + implement detector function alongside F1-F7. Iteration cap = 1 PR. Soft dependency on Pearl_Editor's corpus tagging (informs detector's edge-case heuristics) but NOT a hard blocker — Pearl_Dev can implement against the cap-entry rule text alone.
3. **Pearl_PM** — route `ws_pearl_editor_hook_scene_first_brief_addendum_20260523` and `ws_pearl_dev_register_gate_f11_hook_abstract_detector_20260523` (both opened in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` via this PR) for execution.
4. **Pearl_Architect (deferred ws)** — if/when Pearl_Editor brief addendum lands and the corpus rewrite queue is non-trivial, open a follow-up cap entry / amendment considering whether the scene-first rule should be amended INTO `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` as a spec-level rule (not just brief-addendum). Open Question Q2 below.

**Handoffs:**

- Pearl_PM → routes `ws_pearl_editor_hook_scene_first_brief_addendum_20260523` + `ws_pearl_dev_register_gate_f11_hook_abstract_detector_20260523` → trigger = this cap-entry PR merged (which also requires PR #1292 to merge first, since this PR is stacked on PR #1292).
- Pearl_Editor → `ws_pearl_editor_hook_scene_first_brief_addendum_20260523` → independent execution after Pearl_PM routes.
- Pearl_Dev → `ws_pearl_dev_register_gate_f11_hook_abstract_detector_20260523` → soft dep on Pearl_Editor's corpus tagging; can start in parallel with Editor's review.

**Open questions (for future amendment, not decided here):**

- **Q1.** Should F11 eventually escalate from WARN to HARD_FAIL once the brief-addendum corpus pass completes and the philosophy-first atoms are rewritten? Cap entry leaves this OPEN for a future amendment. Pearl_Dev's V1 implementation: WARN-only.
- **Q2.** Should the scene-first rule be amended INTO `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` as spec-level (not just brief-addendum-level)? Cap entry leaves this OPEN; revisit after Pearl_Editor brief addendum lands.

**Authority:** This cap entry + OPD-144 (`artifacts/coordination/operator_decisions_log.tsv` row, landed via PR #1292) + this cap-entry PR.

---

### BR-CANON-02-GLOBAL-BRAND-IDENTITY — Operator-visible 37 = manga canon × cross-axis JOIN view (additive cap on Path X, decision ratified 2026-05-26)

**Status:** **ratified** (operator decision via PR #1305 ship + acknowledged in PR #1309 ws opening + load-bearing on main since commit `182c96582`).

**Context:** Operator framing 2026-05-24 in v2 dashboard spec: "Each brand is a global brand, not manga-only or book-only." PR #1305's `brand-wizard-app/public/brand_admin_v2.html` surfaces ~37 brands with `axes_present: [book, manga, music]` chips per card — a JOIN view over the 3 Path X axes. BR-CANON-01 Path X cap entry established that book / manga / music are intentionally distinct registries that DO NOT converge. The operator's v2 framing does not contradict Path X — it adds an **operator-visible JOIN view** above the 3 axes. This cap codifies the join without merging the registries.

Load-bearing evidence on `origin/main` (merge order 2026-05-26):

| Commit | PR | What landed |
|---|---|---|
| `c1fa2c8a2` | #1309 | Opened follow-up ws rows including this cap ws |
| `dbeb40e0b` | #1296 | `brand_index` + `_book_brand_rows` / `_manga_brand_rows` / `_music_brand_rows` |
| `182c96582` | #1305 | v2 picker + `axes_present` chips via `planned_volumes` |
| `03914d36c` | #1312 | 37-brand `artifacts/weekly_packages` stub seed (`2026-W22`) |

**Decision:** The operator-visible "global brand" set = **manga canonical list slots 1–37** (`config/manga/canonical_brand_list.yaml`), used as the picker canon for `brand_admin_v2.html` (`renderPicker` iterates `brand_index().manga`). Brand identity is shared across axes via the **`brand_id` key** when the same id exists in more than one registry (e.g., `stillness_press` on book + manga; `axes_present` materializes the join via `_axes_for_brand` in `server/routes/brand_admin_public.py`). The 3 registries remain authoritative for their respective content pipelines:

| Axis | Registry | Pipeline owner | Typical count |
|---|---|---|---|
| **Book** | `config/brand_registry.yaml` | Pearl_Prime | 26 active keys (locale variants may differ) |
| **Manga** | `config/manga/canonical_brand_list.yaml` | Pearl_Brand | **37** (operator picker canon) |
| **Music** | `config/music/music_brand_registry.yaml` | Pearl_Brand | 38+ (`id_space_start=38`; music-only slugs) |

The "global brand" is a **VIEW** (join + projection at endpoint-time), not a new registry:

- `_book_brand_rows()`, `_manga_brand_rows()`, `_music_brand_rows()` emit per-axis rows.
- `brand_index()` returns `{book, manga, music, counts}` without merging registries.
- `_axes_for_brand(brand_id)` computes which axes apply for a given `brand_id`.
- `planned_volumes` (v2 picker cards) exposes `axes_present: _axes_for_brand(brand_id)`.

No new YAML, no new join table, no `config/global_brand_registry.yaml`.

**Anti-drift check:**

- Path X separation **REMAINS BINDING**. BR-CANON-02 is **ADDITIVE** on BR-CANON-01 Path X — not a supersession.
- DO NOT introduce a persisted "global registry" file — the join is computed at endpoint-time.
- DO NOT modify any of the 3 source registries from a "global brand" framing.
- DO NOT rename `brand_id` values to enforce join keys — accept book-only locale variants (`*_en_us`), music-only slots 38+, and manga-only ids; `axes_present` reflects reality.
- DO NOT expand operator-visible canon beyond manga's 37 without a successor cap (**BR-CANON-03** or later amendment).

**Action items:** None directly. This cap ratifies what is already on main:

- `server/routes/brand_admin_public.py:brand_index` — computes the join (PR #1296, `dbeb40e0b`)
- `brand-wizard-app/public/brand_admin_v2.html` — renders `axes_present` chips (PR #1305, `182c96582`)
- `artifacts/weekly_packages/<brand>/2026-W22/` — 37 stub packages (PR #1312, `03914d36c`)

**Handoffs:**

- **Pearl_PM:** use **BR-CANON-02-GLOBAL-BRAND-IDENTITY** when routing any future "global brand" / "cross-axis" / "join" / "all brands view" ws's.
- **Pearl_Brand:** continues owning dashboard surfaces under **DASH-02**; BR-CANON-02 ratifies what v2 already does.
- **Pearl_Architect (FOLLOW-UP, operator-gated):** if operator later expands operator-visible canon beyond 37, open **BR-CANON-03** (or successor) specifying the new operator-visible canon — do NOT modify BR-CANON-02 in place.
- **Pearl_Editor + Pearl_Marketing:** `ws_planned_volumes_per_brand_backfill_20260526` backfills per-axis volume data; BR-CANON-02 does NOT gate that work.

**Cross-references:**

- **BR-CANON-01** + Path X update + Path X cap entry (this state doc) — foundation BR-CANON-02 builds on
- **MUSIC-MODE-BRAND-INTEGRATION-V1-01** (this state doc) — music axis (slot 38+); BR-CANON-02 surfaces music in the join when `music_brands` entries share `brand_id`
- **DASH-02** (this state doc) — Pearl_Brand ownership of the dashboard surface that materializes the join
- **WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01** (this state doc) — parent program; brand_dashboard + weekly_packaging surfaces
- **BRAND_ADMIN_CANONICAL_PACKAGE.md** — declares v2 canonical-weekly-work (cross-reference only; not amended by this cap)

---

#### WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 — AMENDMENT-2026-05-27-BRAND-ADMIN-V2-PHASE-1-P0-COMPLETE

**Authorization:** Brand-Admin-V2 sub-program **Phase 1 P0 100% complete**. Five constituent PRs landed on `main`, each gated through `Verify governance` (ruleset 13451138) + Core tests + Release gates + EI V2 gates. Operator-visible 37-brand picker now renders real planned-volume numbers across **book / manga / podcast / audiobook** axes; weekly-work dashboard surfaces per-platform downloads (KDP / WEBTOON / Spotify / Pearl News) with split-at-build per OPD-145.

**`main` HEAD anchor (doc authoring):** post-PR #1337 merge (planned-volumes backfill landed; HEAD advances with this AMENDMENT PR).

---

##### 1. PHASE 1 P0 100% COMPLETE — Brand-Admin-V2 sub-program

Sub-program scope = **operator-visible 37-brand × 4-axis × per-platform-download weekly-work dashboard**. All five constituent capabilities shipped:

| Capability | PR | Merge SHA | Authority |
|---|---|---|---|
| Live 3-axis brand index endpoint (book / manga / music) | #1296 | `dbeb40e0b` | `server/routes/brand_admin_public.py` |
| V2 weekly-work dashboard + picker (`brand_admin_v2.html`) | #1305 | `182c96582` | `BRAND_ADMIN_CANONICAL_PACKAGE.md` |
| Per-platform download route (OPD-145 split-at-build) | #1326 | `c7a645e44` | `scripts/brand/build_admin_packets.py` |
| Per-brand planned volumes backfill (37 brands × 3 axes) | #1337 | `e5cb4dc92` | `config/brand_admin/manga_canon_planned_volumes.yaml` |
| Mkdir-parent fix for split-at-build zip writer | #1334 | `d6bcaa5ac` | `scripts/brand/build_admin_packets.py:141` |

**Supporting cap entry:** `BR-CANON-02-GLOBAL-BRAND-IDENTITY` (this state doc) — additive JOIN cap declaring brand_id as cross-axis JOIN key while preserving Path X 37-manga + 24×13=312-book + 38+ music separation.

**Operator-visible deliverable:** http://127.0.0.1:8000 → `brand-wizard-app/public/brand_admin_v2.html` → 37-brand picker → click brand → per-week × per-platform downloads.

**Binding claim (verbatim):** **Brand-Admin-V2 Phase 1 P0 is 100% complete** for `PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1` at the milestone boundary defined by the 5 PRs above + planned-volumes backfill landing.

---

##### 2. PHASE 2 ENTRY CRITERIA (brand-admin-v2 sub-program)

1. **Phase 1 P0 milestone closed** — this AMENDMENT (5 PRs landed + planned-volumes coverage matrix).
2. **CI baseline clean for brand-admin sub-program** — `tests/test_brand_admin_v2_api.py` + `tests/unit/brand/test_build_admin_packets.py` green on `main` HEAD (verified post-#1334).
3. **Path X anti-drift held** — 37-manga canon unchanged; book pipeline (24×13=312) unchanged; music registry (38+) unchanged; brand_id JOIN materialized only at dashboard surface per `BR-CANON-02`.
4. **OPD-145 split-at-build pattern adopted** — per-platform ZIPs under `artifacts/weekly_packages/<brand>/<week>/<platform>/<brand>_<week>_<platform>.zip` per OPD-145 ratification.

---

##### 3. PHASE 2 SCOPE — Real-content build × 4 axes + cron wireup

Five **runnable** workstreams now opened (table §5). Sub-program Phase 2 P0 = move from **planned numbers** (configs only) to **real shippable content** flowing through each per-platform pipeline weekly. Cron wireup = Monday weekly job that re-generates per-brand × per-platform ZIPs against the latest content tree.

- **Book axis (KDP ebook):** Pearl_Prime bestseller pipeline → KDP EPUB output → packaged into `<brand>/<week>/kdp/<brand>_<week>_kdp.zip`
- **Manga axis (KDP paperback + WEBTOON):** Manga V2 layered render → KDP paperback PDF + WEBTOON vertical-scroll → packaged into `<brand>/<week>/kdp/` and `<brand>/<week>/webtoon/`
- **Podcast axis (Spotify):** Pearl_Audio podcast pipeline → MP3 + show notes → packaged into `<brand>/<week>/spotify/`
- **Audiobook axis (Audible / Spotify / Google Play):** Pearl_Audio audiobook pipeline → M4B + chapter markers → packaged into `<brand>/<week>/audible/` and `<brand>/<week>/google_play/`
- **Cron wireup:** GitHub Actions `weekly_package_writer.yml` (existing scaffold) → activate Monday 9am UTC schedule → re-run `scripts/brand/build_admin_packets.py` on the live content tree

---

##### 4. ANTI-DRIFT

- The claim **"Brand-Admin-V2 Phase 1 P0 is 100% complete"** is **BINDING** for this sub-program record — it **cannot** be downgraded or contradicted in coordination docs **without a new operator AMENDMENT** referencing this block.
- **Phase 2 workstreams** enumerated in §5 are **runnable** (`status=runnable` in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`); each requires operator authorization to spawn (Pearl_Conductor policy unchanged).
- **Path X 37-manga canon is FROZEN** at brand_id scope — Phase 2 real-content axes use the existing 37 brand_ids, do NOT add 38th manga brand, do NOT modify `config/manga/canonical_brand_list.yaml`.
- **Music brands (slot 38+)** remain wizard-onboarded only — no manual seeding into Phase 2 real-content backfill.
- **Per-platform ZIP semantics** = split-at-build per OPD-145; do NOT introduce slice-on-demand variant without separate AMENDMENT.

---

##### 5. ACTION ITEMS (named `ws_*` — prompts not authored in this amendment)

| workstream_id | Primary owners | Intent |
|---|---|---|
| `ws_brand_admin_v2_real_content_build_book_axis_20260527` | Pearl_Prime + Pearl_Dev | Wire Pearl_Prime bestseller output → KDP ebook EPUB → `<brand>/<week>/kdp/<brand>_<week>_kdp.zip` (37 manga-canon brands; weekly cadence) |
| `ws_brand_admin_v2_real_content_build_manga_axis_20260527` | Pearl_Author + Pearl_Dev (Manga V2) | Wire Manga V2 layered render → KDP paperback PDF + WEBTOON vertical-scroll → `<brand>/<week>/{kdp,webtoon}/` (37 manga-canon brands) |
| `ws_brand_admin_v2_real_content_build_podcast_axis_20260527` | Pearl_Audio + Pearl_Dev | Wire Pearl_Audio podcast → MP3 + show notes → `<brand>/<week>/spotify/` (37 manga-canon brands) |
| `ws_brand_admin_v2_real_content_build_audiobook_axis_20260527` | Pearl_Audio + Pearl_Dev | Wire Pearl_Audio audiobook → M4B + chapter markers → `<brand>/<week>/{audible,google_play}/` (37 manga-canon brands) |
| `ws_brand_admin_v2_weekly_cron_wireup_20260527` | Pearl_DevOps | Activate Monday 9am UTC `weekly_package_writer.yml` GitHub Actions schedule + verify per-brand × per-platform ZIPs regenerate against live content tree |

**Sequencing:** Real-content × 4 axes can run in parallel (independent content pipelines). Cron wireup is gated on at least 1 of the 4 axes landing (so the cron has real content to package).

**Pointers:** `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (5 new `runnable` ws rows below); `BRAND_ADMIN_CANONICAL_PACKAGE.md` (v2 canonical-weekly-work surface); `BR-CANON-02-GLOBAL-BRAND-IDENTITY` (this state doc — JOIN cap); `config/brand_admin/manga_canon_planned_volumes.yaml` (planned-volumes SSOT from #1337); `artifacts/brand_admin/planned_volumes_coverage_20260527.tsv` (coverage matrix evidence).

---

#### WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 — AMENDMENT-2026-05-27-BRAND-ADMIN-V2-PHASE-2-P0-COMPLETE

**Authorization:** Brand-Admin-V2 sub-program **Phase 2 P0 100% complete**. All 5 Phase 2 P0 workstreams (real-content build × 4 axes + weekly cron wireup) shipped end-to-end via 5 PRs in a single autonomous multi-agent session (2026-05-27). MVP scope: stillness_press brand × week 2026-W22. Total paid-API spend: **$0** (free Edge TTS for podcast; local CosyVoice2 for audiobook; reused existing V4 panels for manga; no RunComfy/ElevenLabs charges).

**`main` HEAD anchor (doc authoring):** post-PR #1349 merge (manga axis MVP landed; HEAD advances with this AMENDMENT PR).

---

##### 1. PHASE 2 P0 100% COMPLETE — Brand-Admin-V2 sub-program

All 5 Phase 2 P0 workstreams from AMENDMENT-2026-05-27 §5 shipped via 5 PRs:

| Capability | PR | Merge SHA | Authority |
|---|---|---|---|
| Book axis MVP (stillness_press 2026-W22 KDP EPUB; 1.5 MB, 11 chapters) | #1344 | `18c7b777c` | `scripts/release/build_epub.py` + manifest entry; **bonus: fixed packager bug** (`build_platform_zips_for_brand` was only writing manifest+README, missing deliverable files) |
| Podcast axis MVP (stillness_press 2026-W22 Spotify+Apple MP3; 55s, 887KB; free Edge TTS) | #1347 | `b6f873a82` | `scripts/podcast/render_simple_episode.py` (NEW) + Edge TTS fallback after ElevenLabs 401 |
| Audiobook axis MVP (stillness_press 2026-W22 Audible+Google Play M4B; 6.5min, 2.5MB; 3 chapter atoms; local CosyVoice2) | #1346 | `e50bbb649` | New `audible` + `google_play_audiobook` platform slugs; `audiobook` deliverable_type; ffmpeg-only M4B re-encode |
| Manga axis MVP (stillness_press 2026-W22 KDP PDF + WEBTOON PNG; 5.3MB PDF + 1080×68016 PNG; reused 35 V4 ep_001 panels) | #1349 | `89e924fae` | `scripts/brand/build_stillness_manga_2026w22.py` (NEW) + 4-axis composite manifest |
| Cron wireup (Monday 9am UTC weekly_package_writer.yml + auto-PR pattern; **bonus: fixed hidden heredoc/YAML bug** that had been silently breaking the workflow since PR #1251) | #1348 | `85d3fbb39` | `.github/workflows/weekly_package_writer.yml` |

**Composite manifest:** `artifacts/weekly_packages/stillness_press/2026-W22/manifest.json` now declares `package_type=book_axis_mvp+podcast_axis_mvp+audiobook_axis_mvp+manga_axis_mvp` with all 4 axes status=ready.

**Operator-visible deliverable:** http://127.0.0.1:8000 → `brand-wizard-app/public/brand_admin_v2.html` → stillness_press → 2026-W22 → 6 platform download cards (KDP / WEBTOON / Spotify / Apple Podcasts / Audible / Google Play) all non-null.

**Binding claim (verbatim):** **Brand-Admin-V2 Phase 2 P0 is 100% complete** for `PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1` at the milestone boundary defined by the 5 PRs above + composite-manifest end-to-end smoke pass.

---

##### 2. PHASE 3 ENTRY CRITERIA (brand-admin-v2 sub-program)

1. **Phase 2 P0 milestone closed** — this AMENDMENT (5 PRs landed + 4-axis composite live).
2. **CI baseline clean** — all required checks green on `main` HEAD; Workers Builds = OPD-153 noise (non-blocking).
3. **Cron operational** — `weekly_package_writer.yml` runs Monday 9am UTC; auto-PRs land in `agent/weekly-packages-YYYY-MM-DD` branches for operator review.
4. **HOOK-SCENE-FIRST-01 corpus pass complete** — 41 P0 (#1336) + 100 P1 (#1342) + 37 P2 (#1341) = **178 atoms rewritten scene-first**; F11 corpus at or near 0 WARN. Unblocks Open Question Q1 (F11 WARN → HARD_FAIL escalation; routed to Pearl_Architect).

---

##### 3. PHASE 3 SCOPE — Per-brand scale-out from 1 brand × 1 week → 37 brands × weekly cadence

Phase 2 P0 was MVP scope (1 brand, 1 week, 4 axes). Phase 3 P0 = horizontal scale-out:

- **Per-brand content build at scale:** apply the 4-axis pattern to all 37 manga-canon brands. Each axis has its own pipeline; Phase 3 work is brand-specific source content authoring (Pearl_Editor + Pearl_Marketing scope, not Pearl_Dev).
- **Cron stability:** verify Monday 9am UTC cron successfully opens auto-PR + content stays current week over week; eyeball auto-PR contents for the first 2-3 weeks.
- **Operator review of PR #1350** (cron-generated `weekly_packages_2026-05-25.tsv` PR with -555 lines / 0 +) — deferred to operator decision because large-deletion smell needs human eyeball.

Phase 3 P0 workstreams **NOT YET OPENED** — pending operator authorization on per-axis cadence + brand priority order. Recommendation: open `ws_brand_admin_v2_phase_3_p0_*` rows in a separate Pearl_PM cycle.

---

##### 4. ANTI-DRIFT

- The claim **"Brand-Admin-V2 Phase 2 P0 is 100% complete"** is **BINDING** for this sub-program record — cannot be downgraded without new operator AMENDMENT referencing this block.
- **Path X 37-manga canon FROZEN.**
- **Book pipeline 24×13=312 FROZEN.**
- **Music registry 38+ FROZEN.**
- **OPD-145 split-at-build semantics PRESERVED** — all 5 PRs adhered (no slice-on-demand variant introduced).
- **OPD-153 cascade-prevention HELD** — Workers Builds failures accepted as known noise; all merges used `--admin --squash --delete-branch` with required ruleset (`Verify governance`) green.
- **Tier 1 LLM policy ADHERED** — content authoring used Claude Code (operator-present session); paid APIs (ElevenLabs, RunComfy) gated by $5 cap; all axes shipped with $0 paid-API spend by falling back to free/local alternatives.

---

##### 5. OPERATOR ACTION ITEMS

1. **PR #1350** — cron-generated `weekly_packages_2026-05-25.tsv` PR (0 additions / 555 deletions). Operator decision needed: merge (legitimate regen) or close (data loss concern)? Recommend eyeball-review before merge.
2. **ELEVENLABS_API_KEY rotation** — Keychain key returned 401 invalid_api_key during podcast axis work. Rotate with: `security add-generic-password -s ELEVENLABS_API_KEY -a $USER -w <new_key>`. No blocker (podcast axis fell back to Edge TTS), but unblocks higher-quality TTS for future production.
3. **F11 WARN → HARD_FAIL escalation** (HOOK-SCENE-FIRST-01 Open Question Q1) — 178-atom corpus is now scene-first; F11 detector likely safe to promote from WARN to HARD_FAIL. Recommend Pearl_Architect ws to author the escalation.
4. **Phase 3 P0 dispatch** — per-brand scale-out from 1 brand → 37 brands. Awaits operator authorization on cadence + brand priority.

**Pointers:** `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (7 ws rows flipped completed in this PR + 1 new P2 row); `BRAND_ADMIN_CANONICAL_PACKAGE.md`; `artifacts/weekly_packages/stillness_press/2026-W22/manifest.json` (4-axis composite); prior `AMENDMENT-2026-05-27-BRAND-ADMIN-V2-PHASE-1-P0-COMPLETE` (this state doc).

---

### MANGA-RENDER-LINEAGE-01 — V4/V5 contract+continuity_state chain canonical for render; SpiritualTech VISUAL_AGENT prompt-planning superseded-for-layered (ratified 2026-05-29)

**Status:** **ratified** (operator decision 2026-05-29; this cap entry + [`docs/MANGA_RENDER_LINEAGE_DECISION_2026-05-29.md`](./MANGA_RENDER_LINEAGE_DECISION_2026-05-29.md)).

**Decision:** Two manga render lineages existed, sharing only `continuity_state`. **CANONICAL for render** = the V4/V5 contract + `continuity_state` chain (`contract_to_prompt_compiler` → `scripts/manga/render_v5_episode.py`, Qwen-Image-Layered — what AUTHORITY V5.1 runs and what `continuity_state_generator.py` scales). **SUPERSEDED for the layered-render approach** = SpiritualTech `VISUAL_AGENT` / `build_panel_prompts.py` prompt-planning (retained as experiment-of-record / non-layered fallback). **RETAINED** = `LETTERING_AGENT` + `LAYOUT_AGENT` (post-render text/composition; reconcile against V5 lettering-v2 PR #945). **Open impl item:** align any reused VISUAL_AGENT prompt logic to the Qwen natural-language-prose strategy (`docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` §2.3).

**How to apply:** route render-pipeline work through the V4/V5 contract + `continuity_state` chain; do NOT build new layered render on the SpiritualTech `panel_prompts.json` path.

**Authority:** this cap entry + `docs/MANGA_RENDER_LINEAGE_DECISION_2026-05-29.md` + `docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` (V5.1 render AUTHORITY).
---

### COHESIVE-FLOW-PATH-DEFAULT-SPINE-01 — Flip `--pipeline-mode` default `registry` → `spine` (operator Option A; ratified 2026-05-30)

**Status:** **ratified** (operator decision 2026-05-30; cap entry only — implementation deferred to Pearl_Dev).

**Context:** Read-only audit [PR #1379](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1379) + [`artifacts/qa/COHESIVE_FLOW_12x10x5_ARCHITECTURE_AUDIT.md`](../artifacts/qa/COHESIVE_FLOW_12x10x5_ARCHITECTURE_AUDIT.md) confirms **12×10×5 is real on the spine path** (`SOMATIC_10_SLOT_GRID`, PR #395) and that the operative drift is **path divergence**: spec + catalog SSOT declare spine canonical, but `scripts/run_pipeline.py` argparse default is `registry` (`:1604`), so agents and batch runners that omit `--pipeline-mode` silently ship the legacy 9-slot bestseller beat. [`docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md`](./PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md) **§1.1** already flags this as *"the most consequential spec↔code drift in Pearl Prime today"* and pre-schedules the fix workstream.

**Decision gate (operator pick on PR #1379 thread):**

| Option | Mechanism | Outcome |
|--------|-----------|---------|
| **A (ratified)** | Flip global argparse default `registry` → `spine` at `run_pipeline.py` (+ mirror sites) + regression test | **Closes silent fallback** for every caller that omits the flag |
| **B (rejected)** | Route catalog/batch drivers only (`run_max_quality_catalog.py` et al. pass `--pipeline-mode spine`) | Batch ships spine; **ad-hoc CLI and other callers still default to legacy** — mixed state, easy re-drift |
| **C (rejected)** | Keep code default `registry`; enforce spine only via docs / explicit operator discipline (§1.1 interim rule) | **Does not fix spec↔code drift**; agents continue to silently hit legacy when the flag is omitted |

**Decision:** **Option A.** Operator rationale: **avoid silent fallback to legacy** — the canonical 12×10×5 cohesive-flow spine (`SOMATIC_10_SLOT_GRID`, Priya `story_schedule` at sec 2/5/9, 5 story variants) must be the default ship path, not an opt-in flag behind a legacy default.

**Pearl_Dev implementation scope (NOT this cap PR — cite only):**

| Touch point | File:line | Change |
|-------------|-----------|--------|
| Primary argparse default | `scripts/run_pipeline.py:1604` | `default="registry"` → `default="spine"` |
| Mirror site 1 | `scripts/run_pipeline.py:1763` | same default flip |
| Mirror site 2 | `scripts/run_pipeline.py:1951` | same default flip |
| Mirror site 3 | `scripts/run_pipeline.py:2295` | same default flip |
| Regression test | new test module (Pearl_Dev's call) | assert `--pipeline-mode` default is `spine` at module import |

**Downstream workstream:** `ws_pipeline_mode_default_flip_to_spine_20260518` (Pearl_Dev; small PR; scheduled before catalog-scale production per §1.1). Complements audit restoration Step 1 (explicit `--pipeline-mode spine` on batch drivers) — Steps 1+2 should land together per audit interaction note; **this cap ratifies Step 2 (default flip)** as the binding architecture decision.

**Anti-drift check:**

- Does NOT implement code — cap entry only; no `run_pipeline.py` edits in the architect PR.
- Does NOT contradict `TEMPLATE-UNIVERSAL-01` — spine path *is* the 12-chapter spine × 10-section grid source-of-truth; flipping default aligns code with that cap.
- Does NOT close PR #1379 — audit artifact remains the forensic substrate; this entry ratifies the operator path-default pick against that audit.
- REINFORCES `PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md` §1.1 — removes the interim "MUST pass `--pipeline-mode spine` explicitly" burden once Pearl_Dev lands the ws.

**Action items:**

1. **Pearl_Dev (`ws_pipeline_mode_default_flip_to_spine_20260518`)** — implement the four default flips + import-time default regression test; audit all `run_pipeline.py` callers before merge (§1.1 risk: MEDIUM). Iteration cap = 1 PR.
2. **Pearl_Dev / Pearl_GitHub (follow-on, not gated on cap merge)** — restoration Step 1 from PR #1379 audit: add `--pipeline-mode spine` to `scripts/run_max_quality_catalog.py` and any other catalog/batch driver that omits the flag (LOW risk; canary 5-book gate pass-rate first).
3. **Pearl_PM** — ensure `ws_pipeline_mode_default_flip_to_spine_20260518` is routed in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` with trigger = this cap-entry PR merged (do not mark completed until Pearl_Dev PR merges).
4. **Pearl_Architect** — comment on PR #1379 when this cap PR merges: `Option A ratified — cap COHESIVE-FLOW-PATH-DEFAULT-SPINE-01 landed at <PR-link>`.

**Authority:** this cap entry + [PR #1379](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1379) + [`artifacts/qa/COHESIVE_FLOW_12x10x5_ARCHITECTURE_AUDIT.md`](../artifacts/qa/COHESIVE_FLOW_12x10x5_ARCHITECTURE_AUDIT.md) + [`docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md`](./PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md) §1.1.
