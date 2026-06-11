# Pearl Prime — Atom Coverage + EXERCISE Schema-Lift Phase A Launch Tracker

## §A. Banner

- **Authored:** 2026-06-11 (UTC), **iter 1** (initial)
- **Owner:** Pearl_PM
- **Program:** Pearl Prime atom coverage + EXERCISE schema lift (the content+structural side of Phase A en-US catalog launch)
- **Sibling tracker (different program; do not confuse):** [`storefront_v1_phase_a_tracker.md`](./storefront_v1_phase_a_tracker.md) (Pearl Prime Storefront V1; landed at PR #1448 + #1481)
- **Cadence:**
  - **DAILY** until 3-PR merge cascade clears (#1485 / #1486 / #1488)
  - **WEEKLY** once child ws's begin executing
  - **DAILY** again during pre-launch QA (A1-A6 verification + CI guard PASS confirmation + Move 4 verdict recompute)
- **One-line summary:** 3-PR stack ready for operator merge (any order on parents; #1488 auto-rebases). 8 child ws's queued (status=proposed). 20 Q-Atom-* awaiting operator answers. Phase A launch gate = **ALL Tier P0 + P1 atom cells filled + A1-A6 verified + CI guard PASS + ONE-PATH-V1-01 D4 + D8 runtime asserts landed**.

---

## §B. Spec stack snapshot (3 PRs + cap entries)

| PR | SHA | Owner | Cap entry | Files | PR status | Cap status |
|---|---|---|---|---|---|---|
| [#1485](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1485) | `19ca18344` | Pearl_Architect | `ATOM-100PCT-COVERAGE-SSOT-V1-01` | 9 | OPEN, MERGEABLE | PROPOSAL — awaiting 16 Q-Atom-* answers |
| [#1486](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1486) | `771e714e8` | Pearl_Architect | `EXERCISE-COMPONENT-SCHEMA-LIFT-01` | 5 | OPEN, MERGEABLE | ratified |
| [#1488](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1488) | `0fa6a3b2e` | Pearl_Architect (AMENDMENT) | (cross-link; amends #1485 SSOT + appends A1-A6 to #1486 cap entry) | 3 | OPEN, MERGEABLE; STACKED on #1485 + #1486 | — |

**Total impact when all 3 merge:** 17 files; 1 new canonical SSOT + 1 new cap entry + 1 schema bump (v1→v2) + 8 new ws rows + 20,803-row gap matrix + per-format variant policy + A1-A6 acceptance checklist.

---

## §C. 3-PR MERGE QUEUE (replaces ad-hoc operator memory)

| # | PR | Stack position | Mergeable | CI | Reviews | Gating-on | Recommended order |
|---|---|---|---|---|---|---|---|
| 1 | [#1485](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1485) SSOT | base | YES | 6 PASS / 2 FAIL (`scan` + `Workers Builds` — known OPD-153 noise; `Verify governance` is the only ruleset-required check) | 0 | Operator answers to 16 Q-Atom-SSOT-* | MERGE 1st **OR** 2nd (siblings — either order; #1488 auto-rebases) |
| 2 | [#1486](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1486) schema lift | sibling | YES | 10 PASS / 1 FAIL (`Workers Builds`) | 1 | Operator confirming schema-lift defaults (no new Q-Atom-* — cap is ratified; Pearl_Dev ws's queued) | MERGE 1st **OR** 2nd |
| 3 | [#1488](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1488) AMENDMENT | stacked | YES | 9 PASS / 2 FAIL (same noise) | 1 | Rebases clean against either #1485 or #1486 merging first; operator answers 4 Q-Atom-AMEND-* | MERGE 3rd (last in stack) |

**Net mergeability:** all 3 are MERGEABLE today; only known-noise CI checks are failing (Workers Builds is OPD-153; `scan` is the no-binary-blobs scan and is also known-noisy on doc-only PRs).

**Fastest merge sequence:** operator answers 20 Q-Atom-* (or sends *"go with recommended defaults unless I flag"*) → all 3 PRs can merge same session in order (1485, 1486, 1488) or with #1488 last after either parent.

---

## §D. OPERATOR-DECISION-PENDING MATRIX (20 Q-Atom-*)

> **BATCH RATIFIED 2026-06-11** via AMENDMENT-RATIFICATION PR — **20 of 20 RESOLVED**. Logged as OPD-20260611-001 through OPD-20260611-020 in [`operator_decisions_log.tsv`](./operator_decisions_log.tsv). One operator override: `Q-Atom-LOCALE-SCOPE-01` = (b) top-3 vs recommended (c) en-US only.

### Group A: SSOT atom coverage (PR #1485 §12 — 16 questions)

> Per `feedback_operator_proxy_routing`: when answered, log each to [`artifacts/coordination/operator_decisions_log.tsv`](./operator_decisions_log.tsv) per the OPD-XXX schema.

| # | Q-ID | Question (1 line) | Recommended default | Decision | Logged-at |
|---|---|---|---|---|---|
| 1 | `Q-Atom-PERSONA-SCOPE-01` | Persona enumeration — 14 keep / retire near-empty / staged | (a) keep all 14 + backfill | **(a)** | OPD-20260611-001 |
| 2 | `Q-Atom-LOCALE-SCOPE-01` | Locale ceiling — all 13 / top-3 / en-US only / +EU | (c) en-US only for Phase A | **(b) **OVERRIDE**** | OPD-20260611-002 |
| 3 | `Q-Atom-LOCALE-PHASE-01` | Locale sequencing | (a) en-US → ja-JP → zh-TW → zh-CN → ko-KR | **(a)** | OPD-20260611-003 |
| 4 | `Q-Atom-VARIANT-CEILING-01` | Variant ceiling | (a) ≥3 floor + ≤5 ceiling per SPEC-739-THRESHOLD-01 | **(a)** | OPD-20260611-004 |
| 5 | `Q-Atom-PERSONA-KEYED-FALLBACK-01` | Tier P1 personas without TEACHER_DOCTRINE | (a) BLOCK catalog runs until backfilled | **(a)** | OPD-20260611-005 |
| 6 | `Q-Atom-STORY-BANK-EXPANSION-01` | Named-character bestseller bank target | (b) ≥3 named characters per P×T cell | **(b)** | OPD-20260611-006 |
| 7 | `Q-Atom-TEACHER-BANK-SCOPE-01` | Teacher-bank coverage | (a) all 13 teachers × all 15 topics complete | **(a)** | OPD-20260611-007 |
| 8 | `Q-Atom-PRIORITY-PERSONAS-01` | Tier P0 priority personas (5-6 for Phase A) | gen_z_professionals + corporate_managers + working_parents + first_responders + healthcare_rns + gen_x_sandwich | **6-persona list** | OPD-20260611-008 |
| 9 | `Q-Atom-PRIORITY-TOPICS-01` | Tier P0 priority topics (5-6 for Phase A) | anxiety + overthinking + burnout + boundaries + self_worth + depression | **6-topic list** | OPD-20260611-009 |
| 10 | `Q-Atom-EXERCISE-BANK-RESOLUTION-01` | Strict-canonical Tier P0 + gratitude promotion | (a) confirm strict-canonical; gratitude separate | **(a)** | OPD-20260611-010 |
| 11 | `Q-Atom-MASTER-ARC-INTERACTION-01` | Atom requirements independent of arc chapter_count | (a) confirm independence | **(a)** | OPD-20260611-011 |
| 12 | `Q-Atom-CI-GUARD-SEVERITY-01` | CI guard severity | (a) HARD FAIL on Tier P0 missing | **(a)** | OPD-20260611-012 |
| 13 | `Q-Atom-SSOT-UPDATE-CADENCE-01` | §9 gap matrix update protocol | (a) every atom-authoring ws PR auto-updates | **(a)** | OPD-20260611-013 |
| 14 | `Q-Atom-DE-DE-FR-FR-01` | de-DE / fr-FR locale gap | (a) defer per AMENDMENT-2026-06-04.2 top-3 | **(a)** | OPD-20260611-014 |
| 15 | `Q-Atom-ONE-PATH-SPEC-FILE-01` | SSOT sequencing vs ONE-PATH-V1-01 ratification | (a) wait for ONE-PATH ratification; pair-cycle | **(a)** | OPD-20260611-015 |
| 16 | `Q-Atom-DIRECTIVE-9-VS-CAP-16-01` | 9 atom types (directive) vs 16 (ONE-PATH-V1-01 D8) | (a) accept §3 routing-class split; 9 SSOT scope | **(a)** | OPD-20260611-016 |
| — | `Q-Atom-LEGACY-ATOM-TYPES-01` | 7 legacy slot-types beyond directive 9 | (a) track under ONE-PATH-V1-01 alone | **(a)** | OPD-20260611-016 |

**Note:** SSOT §12 lists 16 explicit Q-Atom-* + LEGACY-ATOM-TYPES-01 as a 17th (pair-voted with DIRECTIVE-9-VS-CAP-16-01). The directive cited 16 from SSOT §12; the 17th is the pair-vote dependency.

### Group B: AMENDMENT (PR #1488 §17 — 4 questions)

| # | Q-ID | Question (1 line) | Recommended default | Decision | Logged-at |
|---|---|---|---|---|---|
| 17 | `Q-Atom-SLOT-07-PRIORITY-01` | slot_07 supply backfill priority | (a) breath_regulation first (ab_tady_37 covers it) | **(a)** | OPD-20260611-017 |
| 18 | `Q-Atom-AUDIT-PASS-THRESHOLD-01` | Preservation audit pass threshold | (a) ≥99% items zero-loss | **(a)** | OPD-20260611-018 |
| 19 | `Q-Atom-INCLUDE-PEARL-PM-ITER-3-01` | Phase A tracker iter 3 in AMENDMENT PR? | (b) defer to Pearl_PM's own iter session (THIS TRACKER closes that loop) | **(b)** | OPD-20260611-019 |
| 20 | `Q-Atom-INCLUDE-SLOT-07-BACKFILL-WS-01` | Include optional slot_07 supply backfill ws? | (a) YES — already included in #1488 | **(a)** | OPD-20260611-020 |

**Decision-pending state:** **0 of 20 PENDING** (20 RESOLVED 2026-06-11 via AMENDMENT-RATIFICATION PR; 1 operator override on `Q-Atom-LOCALE-SCOPE-01`).

**~~Fastest unblock~~ COMPLETED 2026-06-11:** operator one-line acceptance with 1 override → all 20 resolved → 3 PRs unblocked for merge.

---

## §E. WORKSTREAM CASCADE (8 child ws's with dependencies)

### Dependency tree

```
PR #1485 MERGE ───┬─── ws_pearl_editor_atom_100pct_tier_p0_persona_keyed_20260606
                  │       (Pearl_Editor; Tier P0 = 105 rows; ~125 hr)
                  │
                  ├─── ws_pearl_writer_atom_100pct_tier_p0_engine_atoms_20260606
                  │       (Pearl_Writer; Tier P0 + P1 = 548 rows; ~665 hr)
                  │
                  ├─── ws_pearl_dev_atom_100pct_ci_guard_20260606
                  │       (Pearl_Dev; scripts/ci/check_atom_100pct_coverage.py +
                  │        runtime variant-floor assert at registry_resolver.py:604)
                  │
                  └─── ws_pearl_localization_atom_100pct_tier_p2_ja_jp_20260606
                          (Pearl_Localization; Tier P2 = 803 rows; ~982 hr)
                          ─── HARD-gated on en-US Tier P0 + P1 = 0 in gap matrix

PR #1486 MERGE ───┬─── ws_pearl_dev_practice_ingest_components_lift_20260610
                  │       (Pearl_Dev; ingest fix + ab_tady_37 source branch;
                  │        272 v1 rows → 311 v2 rows; A1 + A2 verifiable post-merge)
                  │
                  └─── ws_pearl_dev_renderer_practice_components_consume_20260610
                          (Pearl_Dev; renderer reads structured components;
                          A4 + A5 verifiable post-merge)
                          ─── HARD-gated on ingest ws merging first

PR #1488 MERGE + ↑ both Pearl_Dev schema ws's
                  → ws_pearl_editor_exercise_preservation_audit_20260611
                          (Pearl_Editor; A1-A6 end-to-end verification with
                          per-item evidence; produces
                          artifacts/qa/exercise_preservation_audit_<UTC>.{md,tsv})

Operator answers Q-Atom-SLOT-07-PRIORITY-01
                  → ws_pearl_editor_slot_07_practice_supply_backfill_20260611
                          (Pearl_Editor + Pearl_Writer; 11 content_types × ≥8
                          items = 88 items minimum; staged per priority)
                          ─── HARD-gated on PR #1486 + 2 Pearl_Dev ws's merged
```

### Per-ws table

| # | ws_id | Owner | Status | Blockers | Acceptance ref | Est. hr | Tier |
|---|---|---|---|---|---|---|---|
| 1 | `ws_pearl_editor_atom_100pct_tier_p0_persona_keyed_20260606` | Pearl_Editor | proposed | PR #1485 merge + Q-Atom-PRIORITY-PERSONAS-01 + Q-Atom-PRIORITY-TOPICS-01 | SSOT §16 Phase A (P0=0) | ~125 | P0 |
| 2 | `ws_pearl_writer_atom_100pct_tier_p0_engine_atoms_20260606` | Pearl_Writer | proposed | PR #1485 merge | SSOT §16 Phase A (P0+P1=0) | ~665 | P0+P1 |
| 3 | `ws_pearl_localization_atom_100pct_tier_p2_ja_jp_20260606` | Pearl_Localization | proposed | en-US Tier P0+P1 = 0 in gap matrix | SSOT §16 Phase B | ~982 | P2 |
| 4 | `ws_pearl_dev_atom_100pct_ci_guard_20260606` | Pearl_Dev | proposed | PR #1485 merge + Q-Atom-CI-GUARD-SEVERITY-01 | SSOT §14 + §16 (CI guard PASS gate) | ~10-15 LoC × 2 PRs | P0 |
| 5 | `ws_pearl_dev_practice_ingest_components_lift_20260610` | Pearl_Dev | proposed | PR #1486 merge | A1 + A2 | ~80-120 LoC | P0 |
| 6 | `ws_pearl_dev_renderer_practice_components_consume_20260610` | Pearl_Dev | proposed | ws #5 merged | A4 + A5 | ~50-80 LoC | P0 |
| 7 | `ws_pearl_editor_exercise_preservation_audit_20260611` | Pearl_Editor | proposed | ws #5 + ws #6 merged | A1-A6 | TBD | P0 |
| 8 | `ws_pearl_editor_slot_07_practice_supply_backfill_20260611` | Pearl_Editor + Pearl_Writer | proposed | PR #1486 + ws #5 + ws #6 merged + Q-Atom-SLOT-07-PRIORITY-01 | A6 | TBD (staged) | P1 |

---

## §F. PHASE A PRE-LAUNCH GATE MATRIX

Required for **Phase A en-US catalog launch declaration** under `CATALOG-800-PER-BRAND-01` + `PEARL-PRIME-ONE-PATH-V1-01`:

| # | Gate | Owning ws | Current state | Evidence path |
|---|---|---|---|---|
| G1 | **Tier P0 atom cells** (105 rows → 0) | ws #1 (Editor) + ws #2 (Writer) + ws #4 (Dev CI guard) | not-started | `artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv` (re-run after each ws PR) |
| G2 | **Tier P1 atom cells** (548 rows → 0) | ws #1 + ws #2 (continue past P0) | not-started | same TSV |
| G3 | **A1-A6 acceptance criteria PASS** | ws #7 (Pearl_Editor preservation audit) | not-started | `artifacts/qa/exercise_preservation_audit_<UTC>.{md,tsv}` |
| G4 | **`scripts/ci/check_atom_100pct_coverage.py` PASS on main** | ws #4 (Pearl_Dev CI guard) | not-started | `.github/workflows/atom_100pct_coverage.yml` runs nightly + on PRs |
| G5 | **ONE-PATH-V1-01 D4 + D8 runtime asserts landed** | (cross-ref ONE-PATH-V1-01 cap; not in this 8-ws scope) | not-started | `phoenix_v4/planning/registry_resolver.py:519-607` (variant-floor) + atom-resolver entry at `:415-462` (PersonaAtomCoverageError); cross-link `ws_pearl_dev_one_path_phase_2_runtime_gates_20260606` |
| G6 | **EXERCISE schema-lift cascade complete** | ws #5 + ws #6 + ws #7 + ws #8 (slot_07 backfill optional) | not-started | A1-A6 evidence + 311-row store + (when ws #8 lands) slot_07 supply |
| G7 | **`component_variant_by_format` dry-run PASS per format** | ws #6 (renderer) tests | not-started | A5 evidence; `tests/rendering/test_practice_components_render.py` |
| G8 | **Move 4 verdict recompute under production-profile** | cross-ref ONE-PATH-V1-01 P0-C action item | not-started | `artifacts/qa/move4_recompute_<UTC>.md` (post-Phase-2 ws lands) |
| G9 | **`CATALOG-800-PER-BRAND-01` high-confidence catalog artifact produced** | cross-ref Pearl_Research + Pearl_Marketing existing ws (out of this 8-ws scope) | not-started | `artifacts/catalog/full_catalog_high_confidence_<UTC>.csv` |

**Status legend:** `not-started` / `in-progress` / `verified` / `failed`.

**Net gate state:** **9 of 9 not-started** (no PR or ws has merged yet; cascade hasn't begun).

---

## §G. CRITICAL PATH (the bottleneck right now)

### Bottleneck identification — **UPDATED 2026-06-11 post-RATIFICATION**

| Layer | State | Bottleneck? |
|---|---|---|
| ~~20 Q-Atom-*~~ | **0 of 20 PENDING (20 RESOLVED 2026-06-11)** | ~~bottleneck~~ **RESOLVED** |
| **3 PRs (#1485, #1486, #1488) + AMENDMENT-RATIFICATION PR + tracker PR #1489** | all MERGEABLE; ruleset-required `Verify governance` PASS; only OPD-153 known-noise failing | **YES — the new bottleneck.** Operator merge action required. |
| 8 ws's | all `proposed`; **4 immediately-unblocked** on first parent PR merge | Not yet — gated on PR merges |
| Pearl_Dev / Editor / Writer / Localization capacity | available; no concurrent in-flight on this scope | Not blocking |

### POST-RATIFICATION CASCADE READY

The 4 immediately-unblocked ws's dispatch the moment the first parent PR merges:

1. `ws_pearl_editor_atom_100pct_tier_p0_persona_keyed_20260606` (Tier P0; gated on #1485 merge)
2. `ws_pearl_writer_atom_100pct_tier_p0_engine_atoms_20260606` (Tier P0+P1; gated on #1485 merge)
3. `ws_pearl_dev_atom_100pct_ci_guard_20260606` (CI guard; gated on #1485 merge)
4. `ws_pearl_dev_practice_ingest_components_lift_20260610` (ingest; gated on #1486 merge)

Subsequent ws dispatches per dependency tree (see §E):
- `ws_pearl_dev_renderer_practice_components_consume_20260610` (#6) → on ws #5 merge
- `ws_pearl_editor_exercise_preservation_audit_20260611` (#7) → on ws #5 + #6 both merged
- `ws_pearl_localization_atom_100pct_tier_p2_ja_jp_20260606` (#3) → on en-US Tier P0 + P1 = 0
- `ws_pearl_editor_slot_07_practice_supply_backfill_20260611` (#8) → on ws #5 + #6 merged (Q-Atom-SLOT-07-PRIORITY-01 answered)

### Recommended merge sequence (fastest path through cascade)

1. **AMENDMENT-RATIFICATION PR** (this session; small atomic; merge first to flip cap status → ACTIVE)
2. **#1485 SSOT** (any order with #1486)
3. **#1486 schema lift** (any order with #1485)
4. **#1488 AMENDMENT** (third; auto-rebases against parents)
5. **#1489 tracker** (any order; small atomic; merges independent of cascade)

Or batch-merge all 5 in any order — they're all designed to be independent or auto-rebasing.

---

## §H. ITER-2 TRIGGER CONDITIONS

Iter 2 fires on **any one** of the following:

| Trigger | Action |
|---|---|
| Any of #1485 / #1486 / #1488 merges | Same-day iter 2 — capture merge SHA + cascade update + flip §F gate state per evidence |
| Any of 20 Q-Atom-* is answered | Same-day iter 2 — log to OPD log + update §D row + downstream §E ws blocker re-eval |
| Any child ws PR merges | Same-day iter 2 — flip ws status from `proposed → in_progress → completed` + downstream blockers updated + §F gate state advanced if evidence path produced |
| 48 hours elapsed with no motion | Iter 2 — explicit no-motion surface in §G + recommended unblock path |
| **Default catch-all:** operator one-line *"go with recommended defaults"* | Iter 2 — log all 20 decisions in one batch + dispatch the 4 immediately-unblocked ws's |

---

## §I. CROSS-REFERENCES + ANCHORS

### PRs
- PR #1485: https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1485
- PR #1486: https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1486
- PR #1488: https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1488

### Spec + summary
- SSOT: `docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md` (lands with PR #1485)
- AMENDMENT §17: same file, §17 (lands with PR #1488)
- Operator-facing summary: `artifacts/qa/pearl_prime_atom_100pct_summary_20260606.md` (lands with PR #1485)
- Gap matrix TSV: `artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv` (20,803 rows; lands with PR #1485)

### Cap entries (all in `docs/PEARL_ARCHITECT_STATE.md`)
- `ATOM-100PCT-COVERAGE-SSOT-V1-01` (PR #1485; PROPOSAL)
- `EXERCISE-COMPONENT-SCHEMA-LIFT-01` (PR #1486; ratified; A1-A6 added via PR #1488)
- `PEARL-PRIME-ONE-PATH-V1-01` (existing; PROPOSAL — paired Q-OP-* cycle with this tracker)
- `CATALOG-800-PER-BRAND-01` (existing; Phase A gate authority)
- `EXERCISE-BANK-RESOLUTION-01` (existing; orthogonal — production-profile strict-canonical)

### 8 ws row IDs (all in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`)
1. `ws_pearl_editor_atom_100pct_tier_p0_persona_keyed_20260606`
2. `ws_pearl_writer_atom_100pct_tier_p0_engine_atoms_20260606`
3. `ws_pearl_localization_atom_100pct_tier_p2_ja_jp_20260606`
4. `ws_pearl_dev_atom_100pct_ci_guard_20260606`
5. `ws_pearl_dev_practice_ingest_components_lift_20260610`
6. `ws_pearl_dev_renderer_practice_components_consume_20260610`
7. `ws_pearl_editor_exercise_preservation_audit_20260611`
8. `ws_pearl_editor_slot_07_practice_supply_backfill_20260611`

### Decision log
- `artifacts/coordination/operator_decisions_log.tsv` (next slot per preflight: OPD-155)

### Sibling tracker (different program)
- `artifacts/coordination/storefront_v1_phase_a_tracker.md` — Pearl Prime Storefront V1 program; landed at PR #1448 (iter 1) + #1481 (iter 2). **Do not confuse** — different scope; runs in parallel.

---

*Iter 1 banner. Tracker becomes the single pane for the Pearl Prime atom-coverage + EXERCISE schema-lift cascade until Phase A en-US catalog launch declared.*
