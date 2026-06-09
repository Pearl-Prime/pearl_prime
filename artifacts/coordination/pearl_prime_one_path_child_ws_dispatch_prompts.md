# Pearl Prime ONE-PATH — 6 child ws dispatch prompts (pre-staged)

**Status:** READY-TO-FIRE — paste each prompt section verbatim into the relevant agent dispatch the moment PR #1473 (ONE-PATH lockdown V1) merges. All 13 Q-OP-* answers + Q-PRP-STOREFRONT-CONTENT-GATE-01 pre-baked per `artifacts/coordination/operator_decisions_log.tsv` rows OPD-20260606-001 through OPD-20260606-016.

**Sequencing:** per OPD-20260606-011 (Q-OP-MIGRATION-CADENCE-01 = (a) single-PR-per-ws atomic). Phase order: 1 → 2 → 3a + 3b parallel → 4. Pearl_PM meta-ws coordinates throughout.

**Cross-program contract:** every per-persona Phase 3a PR that lands triggers an automated SKU-join check per Q-PRP-STOREFRONT-CONTENT-GATE-01 — see `artifacts/coordination/storefront_v1_phase_a_tracker_iter_2_seed.md` §J.

---

## Prompt 1 — ws_pearl_dev_one_path_phase_1_mechanical_sweeps_20260606

```
PEARL_DEV — Phase 1 mechanical sweeps for PEARL-PRIME-ONE-PATH-V1-01 lockdown

You are Pearl_Dev for Phoenix Omega. Work in /Users/ahjan/phoenix_omega.
Operator present (Tier 1 OK). Emit STARTUP_RECEIPT / CLOSEOUT_RECEIPT.

MISSION: ship 3 mechanical sweeps as 3 separate PRs (per OPD-20260606-011 single-PR-per-ws-atomic):

PR 1.a — L03 section_02 SCENE→STORY label sweep
- Files: registry/{anxiety,boundaries,burnout,compassion_fatigue,courage,depression,
  financial_anxiety,financial_stress,grief,imposter_syndrome,overthinking,
  self_worth,sleep_anxiety,social_anxiety,somatic_healing}.yaml (15 topic files)
- Mechanical change: every chapter's section_02 type: SCENE → type: STORY
- Acceptance: grep -c "section_02:.*type: SCENE" registry/*.yaml returns 0
- Authority: docs/specs/PEARL_PRIME_ONE_PATH_LOCKDOWN_V1_SPEC.md §2 D3;
  artifacts/qa/pearl_prime_one_path_deletion_manifest_20260606.tsv L03

PR 1.b — L05 delete vestigial RUNTIME_TEMPLATES.chapter_count
- File: phoenix_v4/planning/book_structure_plan.py:71-73
- Mechanical change: remove `chapter_count` field from RUNTIME_TEMPLATES dict
  (retain tier + exercise_cap fields that ARE consumed)
- Acceptance: grep -n "RUNTIME_TEMPLATES.chapter_count" phoenix_v4/planning/book_structure_plan.py returns 0
- Authority: spec §2 D5; manifest L05; AUTO-PLAN-SSOT-01-AMENDMENT closure

PR 1.c — L11 + D16 placeholder leakage post-compose strip + assert-empty
- File: phoenix_v4/rendering/prose_resolver.py (Stage-6 cleanup)
- Add: regex strip of {`[Angle journey placeholder]`, `[Angle journey — definition placeholder]`,
  `fingerprint:`, `char_count:`, `paragraph_count:`, `sentence_count:`, `[* placeholder *]`,
  `What Ahjan keeps pointing toward is...` (lonely-promise pattern)}
- Add: assert-empty check post-strip; raise PlaceholderLeakageError if any token survives
- Acceptance: synthetic test fixture with seeded placeholders → render fails with
  PlaceholderLeakageError; legitimate run produces zero placeholder tokens
- Authority: spec §2 D16; manifest L11

ALL 3 PRs:
- Branch pattern: agent/pearl-dev-one-path-phase-1-{l03|l05|l11}-20260606
- Worktree from origin/main --no-checkout
- Per-PR test coverage (extend tests/test_one_path_phase_1.py)
- Sibling-PR check before push
- Reference cap entry PEARL-PRIME-ONE-PATH-V1-01 in body
- Do NOT merge; operator reviews per PR
```

---

## Prompt 2 — ws_pearl_dev_one_path_phase_2_runtime_gates_20260606

```
PEARL_DEV — Phase 2 runtime gates for PEARL-PRIME-ONE-PATH-V1-01 lockdown

You are Pearl_Dev for Phoenix Omega. Work in /Users/ahjan/phoenix_omega.
Operator present. Phase 1 mechanical sweeps must be MERGED before Phase 2 starts.

MISSION: ship 7 runtime gates as 7 separate PRs. Each gate = one exception class +
one assert-point per spec §5 + tests + cascade integration in scripts/run_pipeline.py.

Per-PR scope (in cascade-cost-order so cheap precondition checks fail first):

PR 2.a — D8 PersonaAtomCoverageError fail-fast precondition
  Site: phoenix_v4/planning/registry_resolver.py:415-462
  Pre-compose check: persona×topic must have all 16 required slot-type dirs
  (HOOK/STORY/SCENE/REFLECTION/EXERCISE/COMPRESSION/PIVOT/PERMISSION/
  PERMISSION_GRANT/TAKEAWAY/THREAD/INTEGRATION/TEACHER_DOCTRINE/
  TEACHER_DOCTRINE_INTRO/ANGLE_DEFINITION/ANGLE_CALLBACK)
  NO fallback to teacher_banks/doctrine if TEACHER_DOCTRINE absent
  Per spec §12 failure-message template (operator-readable + agent-actionable both layers)

PR 2.b — D4 VariantFloorError runtime assert
  Site: phoenix_v4/planning/registry_resolver.py:604 (before modulo-index)
  assert len(variants) >= section.min_variants_required
  ~5 line change + 1 test

PR 2.c — D1 ArcChapterCountError + auto-compress
  Site: phoenix_v4/planning/story_planner.build_story_schedule + arc-loader
  Per OPD-20260606-002 (a) auto-compress: if arc.chapter_count > spine chapter count,
  apply PR-D-SPINE-01 compact_chapter_subset mechanism (extended from compact_book_*
  formats to ALL runtime formats with non-12 chapter_count_default)
  Raise ArcChapterCountError only if arc declares a chapter_count incompatible
  with both spine + compatible_structural_formats range

PR 2.d — D7 EnrichmentGapError EXERCISE strict-canonical (promote existing
         ws_exercise_strict_canonical_production_20260506)
  Site: phoenix_v4/planning/enrichment_select.py + scripts/run_pipeline.py:710
  Production profile: practice_library fall-through → EnrichmentGapError (no warning)
  Per EXERCISE-BANK-RESOLUTION-01 Option 1 promotion under ONE-PATH

PR 2.e — D6 CatalogProfileError production-only catalog gate
  Site: scripts/run_pipeline.py argparse entry
  Per OPD-20260606-009 (a) --smoke flag exempt: reject --quality-profile draft/debug/flagship
  when (--catalog-target OR --book-plan-id matches ^ref_*_v1$ or ^cat_*) AND --smoke NOT set

PR 2.f — D10 F11 HOOK-abstract WARN→BLOCK elevation
  Site: phoenix_v4/quality/register_gate_f11.py (currently WARN; promote to raise)
  Per HOOK-SCENE-FIRST-01 Open Question Q1; 178-atom corpus is scene-first-clean
  per ws_pearl_editor_hook_p0/p1/p2_rewrite_batch_20260527 (3 completed ws's)

PR 2.g — D11 AudiobookWpmOutOfBandError format-registry validator
  New: phoenix_v4/format/wpm_validator.py
  At module-load: per runtime format with both word_range + duration_minutes,
  assert midpoint-wpm ∈ [130, 200]
  Currently failing: micro_book_15 (233), micro_book_20 (213), short_book_30 (200),
  standard_book (264), compact_book_5ch_15min (250), compact_book_5ch_20min (238),
  compact_book_8ch_30min (217), deep_book_4h (125 — marginally low)
  Follow-on Pearl_Architect ws to recalibrate failing format word_range ceilings
  OR shorten duration_minutes — that's a separate AMENDMENT, NOT this PR

PR 2.h — D18 --pipeline-mode default flip mirror sites
  Per COHESIVE-FLOW-PATH-DEFAULT-SPINE-01 ratified 2026-05-30 (already merged cap;
  this is the implementation)
  Sites: scripts/run_pipeline.py:1604, :1763, :1951 — flip default="registry" → "spine"
  Add regression test asserting default at module import

ALL 8 PRs (incl. cross-link 2.h to the existing
ws_pipeline_mode_default_flip_to_spine_20260518):
- Branch pattern: agent/pearl-dev-one-path-phase-2-{d8|d4|d1|d7|d6|d10|d11|d18}-20260606
- Per-PR test coverage
- Reference cap entry PEARL-PRIME-ONE-PATH-V1-01 in body
- Failure-message format strict per spec §12 template (both English + STRUCTURED layers)
- Sibling-PR check before push
- Do NOT merge; operator reviews per PR
- After PR 2.a merges + gen_z_professionals × anxiety smoke still passes: Phase 3 ws's
  unblocked
```

---

## Prompt 3 — ws_pearl_editor_one_path_phase_3a_persona_keyed_atom_backfill_20260606

```
PEARL_EDITOR + PEARL_WRITER — Phase 3a persona-keyed atom backfill (ROLLING)

You are Pearl_Editor (lead) + Pearl_Writer (revision). Work in /Users/ahjan/phoenix_omega.
Operator present. Phase 2 D8 (PersonaAtomCoverageError) must be MERGED for the runtime gate
to fire on missing atom dirs.

MISSION: author the 16 persona-keyed slot-type atom dirs for staged personas per
OPD-20260606-003 (b) priority order. Each persona × topic gets its own PR slice.

GOLD-REFERENCE TEMPLATE: atoms/gen_z_professionals/anxiety/* (16 slot-type dirs;
3-40 variants per dir; persona-keyed Ahjan voice in TEACHER_DOCTRINE/CANONICAL.txt:9
contains the "Slack at 9:47pm / footstep on street" carry_line that drives the
gold-reference book.txt opening).

PRIORITY ORDER (per OPD-20260606-003):
Wave 1 (3 personas, ~6 weeks total content authoring):
- corporate_managers × anxiety + boundaries + burnout (highest-revenue brand assignments)
- working_parents × somatic_healing + anxiety + burnout
- first_responders × anxiety + burnout + compassion_fatigue

Wave 2 (4 personas, ~8 weeks):
- healthcare_rns × compassion_fatigue + anxiety + burnout
- gen_x_sandwich × anxiety + grief + boundaries
- tech_finance_burnout × sleep_anxiety + boundaries + burnout
- millennial_women_professionals × anxiety + boundaries + grief

Wave 3 (5 personas, ~10 weeks):
- gen_alpha_students, gen_z_student, nyc_executives, educators × topic priorities TBD
- midlife_women BLOCKED on ws_midlife_women_arc_authoring_20260427 (zero arcs)

PER-PERSONA × PER-TOPIC PR SLICE:
- Author all 16 slot-type dirs at atoms/<persona>/<topic>/<TYPE>/CANONICAL.txt
- Modeled on atoms/gen_z_professionals/anxiety/<TYPE>/CANONICAL.txt structure
- Pair-authoring: Pearl_Editor authors first-draft (via Qwen Tier 2 acceptable for
  bulk text generation; Tier 1 review pass mandatory) + Pearl_Writer revision in Tier 1
- TEACHER_DOCTRINE atoms MUST cite named contemplative sources per spec §2 D20 + C3
  (Naqshbandi, Angulimala, named-doctrine-anchor, teacher-personal anecdote);
  generic Buddhist aphorism rejected
- After each persona × topic ships: CI smoke runs 7 runtime formats for that combo;
  if ≥1 format passes Q-PRP-STOREFRONT-CONTENT-GATE-01 criterion (book.txt within
  ±10% of gold-ref wc envelope + exit 0 production), append SKU row to
  config/storefront/sku_url_map.yaml + redeploy (mechanical per
  storefront_v1_phase_a_tracker iter 2 §J)

PR pattern: agent/pearl-editor-one-path-phase-3a-{persona}-{topic}-20260606
Per-PR scope: 16 dirs × ~5 variants each = ~80 atoms; ~25-40 atoms total accounting
  for engine-bank already-shipped overlap
Branch from origin/main; --no-checkout
Cross-link to ws_atom_gap_fill_20260410 for already-known gaps (17 P0 zero-atom combos)
Do NOT merge; operator reviews per PR
```

---

## Prompt 4 — ws_pearl_writer_one_path_phase_3b_registry_backfill_20260606

```
PEARL_WRITER + PEARL_EDITOR — Phase 3b registry section backfill (ROLLING)

You are Pearl_Writer (lead) + Pearl_Editor (review). Work in /Users/ahjan/phoenix_omega.
Operator present. Phase 2 D2 SectionGridError must be MERGED for the runtime gate
to fire on tapered chapters.

MISSION: backfill 450 missing sections in registry/<topic>.yaml chapters 02-12 to reach
the full 10-section grid per spec §2 D2. 15 topics × 11 chapters × ~3 sections short
≈ 450 sections × ≥3 variants each ≈ 1,350 net new variants.

PER-TOPIC PR SLICE:
- Topic order: anxiety + burnout + overthinking FIRST (highest-traffic per Move 4
  bestseller-grade list), then somatic_healing + boundaries + compassion_fatigue +
  grief + courage + depression + sleep_anxiety + financial_anxiety +
  financial_stress + imposter_syndrome + self_worth + social_anxiety
- For each topic file: chapter_02 needs +1 section, chapter_03 needs +2, chapters_04-12
  need +3 each (varies per per-A1 audit findings)
- All new sections honor SOMATIC_10_SLOT_GRID slot-type ordering
- All new sections meet ≥3 variant floor per SPEC-739-THRESHOLD-01 (some at min=5
  per per-section override)
- Author validator: scripts/registry/validate_topic_registry_shape.py (new) — offline
  pass for each topic: every chapter 01-12 has exactly 10 sections matching grid

PR pattern: agent/pearl-writer-one-path-phase-3b-{topic}-20260606
Per-PR scope: ~33 sections × ~4 variants = ~132 new atoms per topic
Branch from origin/main; --no-checkout
Cross-link to TEMPLATE-UNIVERSAL-01 cap entry (this work closes the "registry source
  layer needs Phase 3b backfill" deferred item from PEARL-PRIME-ONE-PATH-V1-01)
Do NOT merge; operator reviews per PR
```

---

## Prompt 5 — ws_pearl_dev_one_path_phase_4_craft_gates_20260606

```
PEARL_DEV — Phase 4 craft-gate activation for PEARL-PRIME-ONE-PATH-V1-01 lockdown

You are Pearl_Dev. Phase 3a + 3b must have landed for ≥3 personas before this Phase
fires (otherwise the craft gates raise on every existing combo with insufficient atoms).

MISSION: ship 8 craft gates as 8 separate PRs.

PR 4.a — D12 VoiceOutOfZoneError (slot-zoned voice braid per OPD-20260606-005 (b))
  New: phoenix_v4/quality/voice_braid_gate.py
  Style policy at Stage-6 cleanup: HOOK + INTEGRATION = authorial-I; STORY =
    third-person omniscient; TEACHER_DOCTRINE = Ahjan-specific; REFLECTION =
    authorial-I; EXERCISE = coach; SCENE = second-person present
  Lint: cross-zone voice bleed within a slot's rendered text → raise

PR 4.b — D13 CharacterIllustrationOnlyError
  Extend: phoenix_v4/quality/book_pass_gate.py callback_completion check
  Require: every named character (per character_roster.yaml) shows on-page
    transformation (position change OR belief change OR action change)
  Depends on: Pearl_Editor extending character_roster.yaml entries with
    arc_required field (separate sub-PR)

PR 4.c — D14 PronounContinuityError
  New: phoenix_v4/quality/character_continuity_gate.py
  Regex: <NamedCharacter> followed within 10 words by off-roster pronoun → raise
  Depends on: character_roster.yaml entries with pronouns field

PR 4.d — D15 SignalAmplificationMissingError (engine-scoped)
  New: phoenix_v4/quality/signal_amplification_gate.py
  Fires only on engines = {spiral, overwhelm, shame, false_alarm, watcher}
  Detection: connective set {but also, and yet, even so, the same signal that,
    accurate in X distorted in Y} co-located with topic noun in REFLECTION or
    PIVOT atom per chapter
  Depends on: Pearl_Editor authoring signal/amplification REFLECTION variants
    per engine in atoms/<persona>/<topic>/REFLECTION/CANONICAL.txt

PR 4.e — D17 DecorativeMetaphorInflationError + D19 signature_phrases whitelist
  Extend: phoenix_v4/quality/scene_anti_genericity_gate.py (scope beyond SCENE to
    REFLECTION + TEACHER_DOCTRINE)
  Per OPD-20260606-007 (a) N=5/chapter; per OPD-20260606-008 (a) whitelist=5/book
  Whitelist file: config/authoring/signature_phrases.yaml (Pearl_Editor authored;
    per topic × engine)

PR 4.f — D18 ChapterProgressionLoopError
  New: phoenix_v4/quality/chapter_progression_gate.py
  Per OPD-20260606-006 (a) cosine T=0.85 + sentence-transformers all-MiniLM-L6-v2 local
  Post-render gate; embedding via local CPU (~500MB; no paid API per CLAUDE.md Tier)
  Pip dep: sentence-transformers added to requirements (cross-link to CI workflow)

PR 4.g — D20 GenericBuddhistDriftError
  New: scripts/registry/validate_teacher_doctrine_specificity.py (offline)
  Plus: render-time mirror at phoenix_v4/quality/teacher_doctrine_specificity_gate.py
  Detection: TEACHER_DOCTRINE atom must cite at least one of {Naqshbandi, Angulimala,
    named-doctrine-anchor, teacher-personal anecdote}
  Depends on: Pearl_Editor authoring discipline (already encoded in Phase 3a prompt
    above)

PR 4.h — Final cascade integration in scripts/run_pipeline.py
  Wire new gates D12-D20 into the production-profile gate cascade after the existing
    chain (chapter_flow → bestseller_craft → ei_v2 → editorial → memorable_lines →
    transformation_arc → book_pass → book_quality_gate → D8 → D4 → D6 → D7 → D10 →
    D11 → D18 → D12 → D13 → D14 → D15 → D17 → D18 → D20 → D16 placeholder strip → book.txt write)
  Per OPD-20260606-010 (c) both-layer failure messages per spec §12 template

ALL 8 PRs:
- Branch pattern: agent/pearl-dev-one-path-phase-4-{d12|d13|d14|d15|d17|d18|d20|cascade}-20260606
- Per-PR test coverage
- Reference cap entry PEARL-PRIME-ONE-PATH-V1-01 in body
- Do NOT merge; operator reviews per PR
```

---

## Prompt 6 — ws_pearl_pm_one_path_lockdown_sequencing_tracker_20260606

```
PEARL_PM — ONE-PATH lockdown sequencing meta-ws (CROSS-PHASE)

You are Pearl_PM for Phoenix Omega. Work in /Users/ahjan/phoenix_omega.
Operator present. This ws spawns immediately after PR #1473 merges.

MISSION: cross-phase tracker for PEARL-PRIME-ONE-PATH-V1-01 lockdown. Owns the
sequencing gate readiness checks across Phase 1 → Phase 2 → Phase 3a + 3b parallel →
Phase 4. Plus 8 enumerated action items per cap entry PEARL-PRIME-ONE-PATH-V1-01 §7-§8:

1. Sequence the 5 implementation ws PRs per OPD-20260606-011 single-PR-per-ws-atomic
2. Status-flip ws_auto_plan_ssot_refactor_20260505 → completed (Audit A3 confirmed
   refactor SHIPPED; FORMAT_CHAPTER_COUNTS dict removed)
3. Scope-amend ws_register_gate_f11_hook_abstract_detector_20260523 to elevate
   F11 WARN→BLOCK per spec §2 D10 (cross-link to ws_pearl_dev_one_path_phase_2 PR 2.f)
4. Cross-link ws_exercise_strict_canonical_production_20260506 to spec §2 D7
5. After Phase 2 lands: dispatch Move 4 verdict recompute under production+§13 rubric
   per OPD-20260606-012 (a); refreshes operator confidence baseline; clears the
   false-positive that Move 4 ran under draft profile
6. Pin gold-reference SHA agent/gold-reference-7tier-redirect-20260530 + combo
   (gen_z_professionals × anxiety × spiral × F006 × ahjan × production ×
   --exercise-journeys × --pipeline-mode spine + 16 slot-type persona-keyed atom
   coverage + book_plan_id pattern ref_anxiety_genz_*_v1 + ladder at
   artifacts/pearl_prime/gold_reference_ladder_2026-05-30/) to
   ~/.claude/projects/-Users-ahjan-phoenix-omega/memory/MEMORY.md via
   project_known_good_anchors.md append per OPD-20260606-013 (a)
7. Mark docs/PEARL_PRIME_CRAFT_DEPTH_OVERLAY_PROPOSAL_2026-06-06.md frontmatter
   SUPERSEDED-BY-PEARL-PRIME-ONE-PATH-V1-01 per OPD-20260606-014 (a)
8. Pearl_GitHub routing: when next refreshing docs/DOCS_INDEX.md, add note
   "Pearl Prime canonical path = ONE-PATH-V1; lesser configurations fail-fast per
   the runtime cascade in spec §5"

CROSS-PROGRAM CONTRACT:
- Every per-persona Phase 3a PR merge triggers automated Q-PRP-STOREFRONT-CONTENT-GATE-01
  evaluation: CI runs 7-runtime smoke for the persona × topic; if smoke book.txt lands
  within ±10% of gold-ref envelope (per artifacts/coordination/storefront_v1_phase_a_tracker_iter_2_seed.md §J.1)
  AND exits 0 under production profile, append SKU row to config/storefront/sku_url_map.yaml
  AND redeploy storefront. NO operator approval per-SKU per OPD-20260606-016.

CADENCE:
- Daily tracker iter while merge cascade in progress
- Weekly tracker iter post-cascade through Phase 3 backfill
- Triggers iter dispatch on: any PR merge, any operator decision logged, 24h no-motion

Modify only: artifacts/coordination/storefront_v1_phase_a_tracker.md (iter doc) +
  artifacts/coordination/operator_decisions_log.tsv (log new OPDs as operator answers
  emerge); spawn child ws's per phase order; coordinate cross-program SKU expansion
Per OPD-20260606-011 single-PR-per-ws-atomic: each iter = single doc PR, no code
Do NOT merge; operator reviews each iter
```

---

## Sequencing summary

| Phase | Owner | Dispatch trigger | Estimated wall time |
|---|---|---|---|
| 1 | Pearl_Dev | PR #1473 merge | ~1 week (3 PRs) |
| 2 | Pearl_Dev | Phase 1 PR 1.a + 1.c merge (1.b standalone) | ~3 weeks (8 PRs) |
| 3a | Pearl_Editor + Pearl_Writer | Phase 2 PR 2.a merge | rolling per-persona; ~10-20 weeks across waves |
| 3b | Pearl_Writer + Pearl_Editor | Phase 2 PR 2.b merge (D4 floor) | rolling per-topic; ~6-12 weeks |
| 4 | Pearl_Dev | Phase 3a + 3b ≥3 persona × topic complete | ~3 weeks (8 PRs) |
| PM meta-ws | Pearl_PM | PR #1473 merge | cross-cutting |

Total to full lockdown + first full-catalog gen_z_professionals × all-topics expansion: ~16-20 weeks.

Storefront launch (Phase A): can fire AFTER #1448 → #1454 → #1450 → #1452 → #1453 cascade merges + ja-JP freebie ws lands + at least the 7-SKU en-US gen_z_professionals × anxiety subset passes §J.1 criterion. Estimated 1-2 weeks from operator green-light.
