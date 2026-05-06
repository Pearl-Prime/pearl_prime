# Pearl_Architect State

Last verified: 2026-05-05  
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
