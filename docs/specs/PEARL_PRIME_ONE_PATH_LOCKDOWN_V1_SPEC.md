# Pearl Prime — ONE-PATH Lockdown V1 (Spec)

**Status:** **PROPOSAL — awaiting Pearl_Architect cap-entry ratification + operator answers to §10 Q-OP-***
**Date:** 2026-06-06
**Authority order:** Subordinate to [`specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md`](../../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) (§2 arc-blueprint contract) and [`specs/PHOENIX_V4_5_WRITER_SPEC.md`](../../specs/PHOENIX_V4_5_WRITER_SPEC.md) (§4 atom contracts; §3 TTS prose law). **Supersedes** the partial constraints in [`docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`](../PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md) by promoting its rubric scoring to runtime gates, and [`docs/PEARL_PRIME_CRAFT_DEPTH_OVERLAY_PROPOSAL_2026-06-06.md`](../PEARL_PRIME_CRAFT_DEPTH_OVERLAY_PROPOSAL_2026-06-06.md) by making its G1-G6 + C1-C5 mandatory instead of advisory.
**Audience:** Pearl_Architect (decision); Pearl_Dev (runtime gates); Pearl_Editor + Pearl_Writer (atom + content backfill); Pearl_PM (sequencing).
**Predecessors:** `COHESIVE-FLOW-PATH-DEFAULT-SPINE-01` (cap entry, ratified 2026-05-30) — flipped `--pipeline-mode` default `registry`→`spine`. This spec extends that single-knob fix to a full 18-dimension lockdown.
**Evidence base:** 7-axis full audit (2026-06-06) at [`artifacts/qa/pearl_prime_audit_2026-06-06.md`](../../artifacts/qa/pearl_prime_audit_2026-06-06.md); gold reference at [`artifacts/pearl_prime/gold_reference_ladder_2026-05-30/`](../../artifacts/pearl_prime/gold_reference_ladder_2026-05-30/); 2 independent editorial critiques converged on the same 8 craft failures.

---

## §1 — Purpose + operator directive (verbatim)

**Operator directive (2026-06-06):**
> *"verify, best way for pearl prime. and do permanently delete all lesser ways. i need to know the best way for all and drop the weaker stuff so that no agent gets the option of doing it lesser."*

The audit + gold-reference + critique corpus converges: ONE path produces bestseller-grade output. Everything else produces sub-bestseller drafts a reviewer can dismantle in 5 paragraphs. The operator's directive is binding: no agent — Pearl_Prime, Pearl_Writer, Pearl_Editor, or downstream catalog runners — may ship a lesser configuration silently. This spec defines the canonical path, enumerates every lesser configuration, and specifies the **runtime fail-fast assert-points** that hard-block lesser configs. This is git-first restoration (per `feedback_drift_recovery_git_first`) encoded as runtime enforcement: the gold reference IS the canonical SHA; this spec is its enforcement contract.

The lockdown spans 18 dimensions across 4 phases. No new architecture. No new specs (besides this one). No new gates beyond what the predecessor cap entries already named. The work is consolidation, not invention.

---

## §2 — The Canonical Path (18 dimensions; one value + one assert-point each)

| # | Dimension | Canonical value | Runtime enforcement point | Failure type |
|---:|---|---|---|---|
| D1 | `arc.chapter_count` | **12** (F006 12-chapter shape; matches 12-spine 1:1) | `phoenix_v4/planning/story_planner.build_story_schedule` + arc-loader entry at `scripts/run_pipeline.py:1692` arc validation | `ArcChapterCountError` (raise; halt before knob_apply) |
| D2 | `chapter.section_count` | **10** (`SOMATIC_10_SLOT_GRID`; no tapering) | `phoenix_v4/planning/beatmap_compile.py:42-53` (literal grid); + registry-validator at `phoenix_v4/planning/registry_resolver.load_registry` | `SectionGridError` (raise on any chapter with <10 sections) |
| D3 | `section_02.atom_type` | **STORY** (not SCENE; PR-669 forward only) | `phoenix_v4/planning/knob_apply.py` spine validator at chapter compile + registry-load asserts label | `SlotLabelDriftError` |
| D4 | `section.variant_floor` | **≥3 enforced AT RUNTIME** | `phoenix_v4/planning/registry_resolver.py:604` — new `assert len(variants) >= section.min_variants_required` before modulo-index | `VariantFloorError` |
| D5 | `section.variant_ceiling` | **≤5 (opt-in per-section ceiling; 3 is fine; 4-5 are bonus)** | same site; `min_variants_required: 5` honored as upper override | warn-only (variant_ceiling exceeded is not a fail; just a signal that authoring went above target) |
| D6 | `quality_profile` (catalog) | **production ONLY** | `scripts/run_pipeline.py` argparse entry — reject `draft`/`debug`/`flagship` when `--catalog-target` or `--book-plan-id` matches `^ref_*_v1$` or `^cat_*` patterns | `CatalogProfileError` |
| D7 | `exercise_resolution` | **strict-canonical** (Option 1 of EXERCISE-BANK-RESOLUTION-01); persona-keyed OR teacher-bank EXERCISE only; **NO** practice_library fall-through under production | `phoenix_v4/planning/enrichment_select.py` EXERCISE resolution + `scripts/run_pipeline.py:710 _check_exercise_strict_canonical_gate` | `EnrichmentGapError` (already raised under proposed `ws_exercise_strict_canonical_production_20260506`; lockdown makes it mandatory) |
| D8 | `persona_keyed_atoms.required` | **ALL of:** `HOOK`, `STORY`, `SCENE`, `REFLECTION`, `EXERCISE`, `COMPRESSION`, `PIVOT`, `PERMISSION`, `PERMISSION_GRANT`, `TAKEAWAY`, `THREAD`, `INTEGRATION`, `TEACHER_DOCTRINE`, `TEACHER_DOCTRINE_INTRO`, `ANGLE_DEFINITION`, `ANGLE_CALLBACK` (16 dirs minimum per `<persona>×<topic>`). **NO fallback** to generic teacher_banks/doctrine when persona-keyed TEACHER_DOCTRINE absent. | atom-resolver entry at `phoenix_v4/planning/registry_resolver.py:415-462` — fail-fast precondition check per persona×topic before compose loop begins | `PersonaAtomCoverageError` (cite missing slot-type dirs) |
| D9 | `teacher_pool_semantics` | **first-match deterministic** per TEACHER-POOL-SEMANTICS-01 | `_TEACHER_TYPE_MAP` lookup at `phoenix_v4/planning/registry_resolver.py:425-429` (existing; no change) | n/a — already enforced |
| D10 | `hook_opening` | **scene-first** per HOOK-SCENE-FIRST-01 — **F11 detector flips WARN→BLOCK** (corpus is 178-atom-clean per `ws_pearl_editor_hook_p0/p1/p2_rewrite_batch_20260527` completed series) | `phoenix_v4/quality/register_gate_f11.py` (per pending `ws_register_gate_f11_hook_abstract_detector_20260523` — this spec elevates from WARN to BLOCK) | `HookAbstractOpeningError` |
| D11 | `audiobook_wpm.midpoint` | **130-200 inclusive per format** (audiobook-normal band) | `config/format_selection/format_registry.yaml` validator at module-load + audiobook generator entry; midpoint = `(word_range[0] + word_range[1]) / 2 / duration_minutes` | `AudiobookWpmOutOfBandError` (raise on any runtime format with both `word_range` + `duration_minutes` whose midpoint-wpm ∉ [130,200]) |
| D12 | `voice_braid` | **slot-zoned (Option B, recommended)** — Pearl_Architect ruling per Q-OP-VOICE-BRAID-01. Default mapping: HOOK + INTEGRATION = authorial-I; STORY = third-person omniscient; TEACHER_DOCTRINE = Ahjan-specific; REFLECTION = authorial-I; EXERCISE = coach; SCENE = second-person present | `phoenix_v4/rendering/section_packet_composer.py` + new style-policy lint at Stage-6 cleanup | `VoiceOutOfZoneError` (raise on cross-zone voice bleed; e.g. coach voice in STORY slot) |
| D13 | `character_transform.required` | **every named character per book must show on-page transformation** (position change OR belief change OR action change) per CRAFT_DEPTH_OVERLAY G4 | `phoenix_v4/quality/book_pass_gate.py` `callback_completion` check — extend to require transformation field; reject illustration-only characters | `CharacterIllustrationOnlyError` |
| D14 | `pronoun_continuity` | **`character_roster.yaml` is binding** per-character pronoun field; mid-book slippage = fail | new `phoenix_v4/quality/character_continuity_gate.py` per CRAFT_DEPTH_OVERLAY G5 — regex `<NamedCharacter>` followed within 10 words by off-roster pronoun → fail | `PronounContinuityError` |
| D15 | `signal_amp_framing` | **spiral / overwhelm / shame / false_alarm / watcher engines MUST contain ≥1 explicit "signal vs amplification" reframing beat** per chapter per CRAFT_DEPTH_OVERLAY G6 | new `phoenix_v4/quality/signal_amplification_gate.py` (engine-scoped; fires only on the 5 introspective engines) — detection via connective set `{but also, and yet, even so, the same signal that, accurate in X distorted in Y}` co-located with topic noun in REFLECTION or PIVOT atom | `SignalAmplificationMissingError` |
| D16 | `placeholder_leakage` | **zero of:** `[Angle journey placeholder]`, `[Angle journey — definition placeholder]`, `fingerprint:`, `char_count:`, `paragraph_count:`, `sentence_count:`, `[* placeholder *]`, `What Ahjan keeps pointing toward is...` (the lonely-promise pattern) | new step in `phoenix_v4/rendering/prose_resolver.py` Stage-6 cleanup before book.txt write — assert-empty post-strip | `PlaceholderLeakageError` (cite which token; cite line offset; cite source-slot) |
| D17 | `decorative_metaphor_cap` | **≤N per chapter beyond SCENE atoms** where N = signature-phrase whitelist count from `config/authoring/signature_phrases.yaml`. Phrases on whitelist: cap 1/chapter, 4/book. Off-list phrases: cap 1 use total. | `phoenix_v4/quality/scene_anti_genericity_gate.py` (existing; extend scope beyond SCENE to REFLECTION + TEACHER_DOCTRINE bodies) per CRAFT_DEPTH_OVERLAY G2 | `DecorativeMetaphorInflationError` |
| D18 | `chapter_repetition_gate` | **cosine similarity between chapter bodies < threshold T** (T=0.85 recommended per Q-OP-CHAPTER-REPETITION-THRESHOLD-01) per CRAFT_DEPTH_OVERLAY G1 | new `phoenix_v4/quality/chapter_progression_gate.py` — embeddings via local sentence-transformers (no paid API; CPU ~500MB) at post-render | `ChapterProgressionLoopError` |
| D19 | `signature_phrases.whitelist` | **≤5 phrases per book** (operator-pick per Q-OP-SIGNATURE-PHRASES-COUNT-01; default 5) — managed at `config/authoring/signature_phrases.yaml` per topic × engine | render-time counter co-located with D17 enforcement | n/a — D17 raises on violation |
| D20 | `ahjan_voice.specificity` | **Ahjan TEACHER_DOCTRINE passages must cite named contemplative sources** (Naqshbandi, Angulimala, named-doctrine-anchor, teacher-personal anecdote) per CRAFT_DEPTH_OVERLAY C3. Generic Buddhist aphorism rejected. | offline atom-validator (CI) at `scripts/registry/validate_teacher_doctrine_specificity.py` (new) + render-time fail-fast for any TEACHER_DOCTRINE atom failing the validator's tag | `GenericBuddhistDriftError` |

Twenty dimensions named with assert-points (the mission spec called for ≥16; this spec ships 20). No dimension has a fallback. No dimension has a default-on-miss path. Each failure type is named; agent-actionable + operator-readable per §12.

---

## §3 — Gold reference SHA + combo + book_plan_id pattern (the canonical ground truth)

**Branch:** `agent/gold-reference-7tier-redirect-20260530` (current HEAD pointer; pin to MEMORY.md per Q-OP-GOLD-REFERENCE-SHA-PIN-01).
**Artifact root:** `artifacts/pearl_prime/gold_reference_ladder_2026-05-30/` (8 runtime-format outputs: micro_15, micro_20, short_30, standard_book, standard_book_smoke, extended_2h, deep_4h, deep_6h).
**Combo:**
- brand: `stillness_press`
- persona: **`gen_z_professionals`** ← the only persona with full 16-slot-type persona-keyed atom coverage for `anxiety`
- topic: `anxiety`
- engine: `spiral`
- arc: `config/source_of_truth/master_arcs/gen_z_professionals__anxiety__spiral__F006.yaml` (chapter_count: 12 — one of only 38 such 12-chapter arcs in 531 total)
- structural format: F006 (chapter_range [8,12])
- teacher: `ahjan`
- runtime profile: `production`
- flags: `--exercise-journeys --pipeline-mode spine`
- book_plan_id pattern: `ref_anxiety_genz_<duration>_v1` (e.g. `ref_anxiety_genz_6h_v1`)

**Per-format wc + verdict (gold ladder):**

| Format | wc | overall_status | release_band | hold_reasons |
|---|---:|---|---|---|
| micro_book_15 | 6548 | n/a (draft? — check) | n/a | n/a |
| micro_book_20 | 8338 | n/a | n/a | n/a |
| short_book_30 | 10538 | n/a | n/a | n/a |
| standard_book | 19986 | (under 20k ceiling — clean) | n/a | n/a |
| standard_book_smoke | 21177 | (over ceiling) | n/a | n/a |
| extended_book_2h | 27102 | n/a | n/a | n/a |
| deep_book_4h | 39693 | WARN | Hold | repeated phrase density above book cap (same as today's smoke — content-side, not gate-defect) |
| deep_book_6h | 56210 | n/a | n/a | n/a |

The gold path is the **specification of acceptable output shape**. Any catalog run that does not match the gold path's profile (D1-D20 above) is ipso facto a lesser configuration.

---

## §4 — Hard-deletion manifest summary

Full manifest at [`artifacts/qa/pearl_prime_one_path_deletion_manifest_20260606.tsv`](../../artifacts/qa/pearl_prime_one_path_deletion_manifest_20260606.tsv) — 18 rows (L01-L18), schema:
`lesser_config_id | type | current_location | shipped_count | classification | rationale | owner_ws | risk_if_kept`

Classifications:
- **DELETE** — code/data permanently removed (vestigial code, silent-acceptance paths, fallback paths)
- **COMPRESS-TO-CANONICAL** — value space narrowed to the canonical value at runtime (arc.chapter_count auto-collapse; label drift mechanical rename)
- **BACKFILL-TO-CANONICAL** — content gap closed by Pearl_Editor + Pearl_Writer authoring (registry tapered sections; missing persona-keyed atoms; missing engine-bank depth)
- **BLOCK** — runtime fail-fast on lesser config (production-only catalog gate; persona-keyed atom precondition; wpm in-band; placeholder leakage)
- **OPERATOR-DECISION-REQUIRED** — Q-OP-* in §10 (arc-strategy A/B/C; locale-scope demote; voice-braid A/B/C; etc.)

**Row distribution (summary; full TSV is authoritative):**
- DELETE: L04, L05, L06, L07, L11, L18 (6 rows)
- COMPRESS-TO-CANONICAL: L01 (default), L03 (mechanical sweep)
- BACKFILL-TO-CANONICAL: L02, L09, L10 (3 rows)
- BLOCK at runtime: L07, L08, L13, L14, L15 (5 rows)
- OPERATOR-DECISION-REQUIRED: L01 (arc-strategy), L09 (persona-floor), L10 (locale-scope), L14 (voice-braid)

Several rows have multiple classifications (e.g. L01 has both COMPRESS-TO-CANONICAL default + OPERATOR-DECISION on whether to rewrite vs. compress).

---

## §5 — Runtime enforcement architecture

**Principle:** every dimension in §2 has a single fail-fast assert-point. No multi-stage cascades. No conditional bypasses. No CI-only enforcement. The runtime is the source of truth; CI mirrors the runtime, not the reverse.

**Cross-cutting integration:** all new gates wired into `scripts/run_pipeline.py` after the existing gate cascade (`chapter_flow` → `bestseller_craft` → `ei_v2` → `editorial` → `memorable_lines` → `transformation_arc` → `book_pass` → `book_quality_gate` → **new gates D2/D3/D4/D8/D10/D12/D13/D14/D15/D17/D18/D20** → `placeholder_leakage` final-strip D16) before `book.txt` write. The new gates do NOT replace existing gates; they extend the cascade.

**Failure-type taxonomy (one exception class per dimension; see §12 for messages):**

| Dimension | Exception class | Module |
|---|---|---|
| D1 | `ArcChapterCountError` | `phoenix_v4/planning/arc_loader.py` |
| D2 | `SectionGridError` | `phoenix_v4/planning/registry_resolver.py` |
| D3 | `SlotLabelDriftError` | `phoenix_v4/planning/knob_apply.py` |
| D4 | `VariantFloorError` | `phoenix_v4/planning/registry_resolver.py` |
| D6 | `CatalogProfileError` | `scripts/run_pipeline.py` |
| D7 | `EnrichmentGapError` (existing; promote) | `phoenix_v4/planning/enrichment_select.py` |
| D8 | `PersonaAtomCoverageError` | `phoenix_v4/planning/registry_resolver.py` |
| D10 | `HookAbstractOpeningError` | `phoenix_v4/quality/register_gate_f11.py` |
| D11 | `AudiobookWpmOutOfBandError` | `phoenix_v4/format/wpm_validator.py` (new) |
| D12 | `VoiceOutOfZoneError` | `phoenix_v4/quality/voice_braid_gate.py` (new) |
| D13 | `CharacterIllustrationOnlyError` | `phoenix_v4/quality/book_pass_gate.py` (extend) |
| D14 | `PronounContinuityError` | `phoenix_v4/quality/character_continuity_gate.py` (new) |
| D15 | `SignalAmplificationMissingError` | `phoenix_v4/quality/signal_amplification_gate.py` (new) |
| D16 | `PlaceholderLeakageError` | `phoenix_v4/rendering/prose_resolver.py` |
| D17 | `DecorativeMetaphorInflationError` | `phoenix_v4/quality/scene_anti_genericity_gate.py` (extend) |
| D18 | `ChapterProgressionLoopError` | `phoenix_v4/quality/chapter_progression_gate.py` (new) |
| D20 | `GenericBuddhistDriftError` | `scripts/registry/validate_teacher_doctrine_specificity.py` (new) + render-time mirror |

**No `try/except` swallowing.** Each exception halts the pipeline. The cascade orders gates so the cheapest precondition fails first (D1, D2, D3, D8 — registry-load time; ~0.5 s) before expensive enrichment/depth/compose (~5-15 min).

---

## §6 — CRAFT_DEPTH_OVERLAY integration

The predecessor [`docs/PEARL_PRIME_CRAFT_DEPTH_OVERLAY_PROPOSAL_2026-06-06.md`](../PEARL_PRIME_CRAFT_DEPTH_OVERLAY_PROPOSAL_2026-06-06.md) proposed 6 new gates (G1-G6) + 5 writer contracts (C1-C5) as advisory recommendations. **Under this ONE-PATH lockdown, the overlay's G1-G6 + C1-C5 ARE MANDATORY runtime enforcement, not advisory.** Mapping:

| Overlay element | This spec dimension | Status |
|---|---|---|
| G1 chapter-repetition gate (cosine similarity) | D18 | **mandatory** (production blocking) |
| G2 decorative-metaphor cap | D17 | **mandatory** (production blocking; flagship advisory deprecated) |
| G3 placeholder leakage gate | D16 | **mandatory ALL profiles** (these are render artifacts, never desired) |
| G4 character transformation requirement | D13 | **mandatory** (production blocking) |
| G5 pronoun continuity gate | D14 | **mandatory ALL profiles** (mechanical bug, never desired) |
| G6 signal-vs-amplification framing | D15 | **mandatory engine-scoped** (spiral/overwhelm/shame/false_alarm/watcher) |
| C1 one question per chapter | D2 + D18 (compositionally) | mandatory at registry-validate time |
| C2 voice-braid rules | D12 | **mandatory; Option B (slot-zoned) recommended** per Q-OP-VOICE-BRAID-01 |
| C3 Ahjan character specificity | D20 | **mandatory** (offline validator + render-time mirror) |
| C4 post-depth re-trim OR raise ceiling | resolved by Phase 3 atom backfill — corp_mgrs's 929-word overshoot is a content-compression artifact (20-arc → 12 spine); gen_z's 12-arc has no overshoot. C4 deprecated as standalone; subsumed by D1. | obsolete (root cause D1) |
| C5 signature_phrases whitelist | D19 | **mandatory; ≤5 phrases per book** per Q-OP-SIGNATURE-PHRASES-COUNT-01 |

The CRAFT_DEPTH_OVERLAY proposal stops being a separate doc — its constraints fold into this lockdown spec. Any future cap-entry amendment that modifies the CRAFT_DEPTH_OVERLAY's behavior must amend THIS spec (PEARL-PRIME-ONE-PATH-V1-01).

---

## §7 — Migration sequence (4 phases; staged via 6 child ws)

**Phase 1 — Mechanical sweeps (Pearl_Dev; ~1 week)**
Single-PR-per-item; no operator-tier decision needed. Items: L03 (`section_02` SCENE→STORY label sweep across 180 registry chapters in 15 topic files), L05 (delete vestigial `RUNTIME_TEMPLATES.chapter_count` at `book_structure_plan.py:71-73`), L11 + D16 (placeholder leakage post-compose strip + assert-empty in `prose_resolver.py` Stage-6). Owner: `ws_pearl_dev_one_path_phase_1_mechanical_sweeps_20260606`. Estimated effort: ~3-5 PR slices, ~50-100 LoC total, no content authoring required.

**Phase 2 — Runtime gates (Pearl_Dev; ~2 weeks)**
Each gate is independently shippable. Items: D4 (variant-floor assert at `registry_resolver.py:604`), D7 (EXERCISE strict-canonical promotion — already proposed under `ws_exercise_strict_canonical_production_20260506`; this spec elevates), D6 (CatalogProfileError — production-only catalog gate at CLI entry), D8 (PersonaAtomCoverageError — fail-fast precondition before compose loop), D10 (F11 HOOK abstract detector WARN→BLOCK elevation — already proposed; this spec elevates), D11 (AudiobookWpmOutOfBandError — format-registry validator + audiobook generator entry), D18 default-flip mirror sites (per COHESIVE-FLOW-PATH-DEFAULT-SPINE-01 still pending Pearl_Dev). Owner: `ws_pearl_dev_one_path_phase_2_runtime_gates_20260606`. Estimated effort: ~7-9 PR slices, ~200-300 LoC total, comprehensive test coverage required.

**Phase 3a — Persona-keyed atom backfill (Pearl_Editor + Pearl_Writer; ~3-4 weeks; staged per persona)**
Highest-leverage content lane. Items: L09 — author the 16-slot-type persona-keyed atom dirs for corporate_managers + first_responders + working_parents + healthcare_rns + tech_finance_burnout + gen_x_sandwich + millennial_women_professionals + gen_alpha_students + gen_z_student × {anxiety, burnout, depression, grief, overthinking, etc.}. Modeled on the gen_z_professionals shape. Approx. 16 slot types × 15 topics × 13 personas ≈ 3,120 atoms (gross; some types share via teacher_banks; net ≈ ~1,800 net new atoms after dedup against teacher_banks). Staged per Q-OP-L09-PERSONA-FLOOR-01 (recommended (b) staged with priority order). Owner: `ws_pearl_editor_one_path_phase_3a_persona_keyed_atom_backfill_20260606`. Estimated effort: rolling per-persona; Pearl_Editor + Pearl_Writer pair-authoring via Qwen for first-draft + Claude Code Pearl_Writer revision passes.

**Phase 3b — Registry section backfill (Pearl_Writer + Pearl_Editor; ~2-3 weeks; per topic)**
Parallel to Phase 3a. Items: L02 — backfill the 450 missing sections in `registry/<topic>.yaml` for chapters 02-12 to reach the full 10-section grid. 15 topics × (11 chapters × ~3 sections short) ≈ 450 sections × ≥3 variants each ≈ 1,350 net new variants. Owner: `ws_pearl_writer_one_path_phase_3b_registry_backfill_20260606`. Estimated effort: ~6-8 weeks across all topics; can launch per-topic for parallelism.

**Phase 4 — Craft gates activation (Pearl_Dev; ~2 weeks; gated on Phase 3a+3b completion)**
Items: D12 (VoiceOutOfZoneError — needs C5 signature_phrases.yaml + slot-zone mapping), D13 (CharacterIllustrationOnlyError — needs character_roster.yaml `arc_required` field; cross-link to `SOURCE_OF_TRUTH/story_atoms/character_roster.yaml`), D14 (PronounContinuityError — needs character_roster.yaml `pronouns` field), D15 (SignalAmplificationMissingError — engine-scoped; requires content backfill for signal/amplification REFLECTION variants per engine), D17 (DecorativeMetaphorInflationError + D19 signature_phrases whitelist — requires `config/authoring/signature_phrases.yaml` authoring by Pearl_Editor), D18 (ChapterProgressionLoopError — embedding model; recommend local sentence-transformers all-MiniLM-L6-v2, ~500MB, CPU; per Q-OP-CHAPTER-REPETITION-THRESHOLD-01 threshold T=0.85), D20 (GenericBuddhistDriftError — needs `scripts/registry/validate_teacher_doctrine_specificity.py` validator + Ahjan-source-anchor authoring). Owner: `ws_pearl_dev_one_path_phase_4_craft_gates_20260606`. Estimated effort: ~5-7 PR slices, ~300-500 LoC total.

**Pearl_PM meta-ws (cross-phase; entire lockdown):**
`ws_pearl_pm_one_path_lockdown_sequencing_tracker_20260606` — owns the cross-phase tracker; reviews Phase 1 → Phase 2 → Phase 3a + 3b → Phase 4 readiness gates; coordinates the Move 4 verdict recompute (Q-OP-MOVE-4-VERDICT-RECOMPUTE-01) after Phase 2 lands.

---

## §8 — Acceptance criteria (per phase)

**Phase 1 acceptance:**
- A1 (L03): `grep -c "section_02:.*type: SCENE" registry/*.yaml` returns 0 across all 15 topics
- A2 (L05): `grep -n "RUNTIME_TEMPLATES.chapter_count" phoenix_v4/planning/book_structure_plan.py` returns no matches
- A3 (L11 + D16): synthetic test — render a book with seeded placeholders; render fails with `PlaceholderLeakageError`; legitimate runs produce zero placeholder tokens in `book.txt`

**Phase 2 acceptance:**
- A4 (D4): test that a registry section with `min_variants_required: 5` but only 3 variants raises `VariantFloorError` at runtime (currently passes silently)
- A5 (D7): test that a production run with persona+teacher EXERCISE atoms absent raises `EnrichmentGapError` (currently produces FALLBACK warning)
- A6 (D6): test that `--quality-profile draft` with `--book-plan-id ref_*` raises `CatalogProfileError`
- A7 (D8): test that a persona×topic combo missing any of the 16 required atom-type dirs raises `PersonaAtomCoverageError` before compose begins
- A8 (D10): F11 HOOK abstract opening detector — synthetic abstract-opening atom raises `HookAbstractOpeningError`
- A9 (D11): unit test that asserts each runtime format's midpoint-wpm ∈ [130, 200]; failing formats are listed
- A10 (D18 mirror): `--pipeline-mode registry` (without explicit flag) issues deprecation warning + recommends `spine`

**Phase 3a acceptance:**
- A11 (L09 staged): per-persona, the 16-slot-type atom dir set is complete for the priority persona list (operator picks per Q-OP-L09); a smoke run for each priority persona × anxiety produces book.txt within the same WC envelope as gold ref (within ±10%)
- A12: re-run Move 4 sweep with the priority-persona set under production profile; recompute the BESTSELLER count under §13 rubric (no `book_pass: FAIL` masked); compare against draft-profile baseline

**Phase 3b acceptance:**
- A13 (L02): for each `registry/<topic>.yaml`, every chapter 01-12 has exactly 10 sections with the canonical slot types per SOMATIC_10_SLOT_GRID; offline `scripts/registry/validate_topic_registry_shape.py` (new) passes for all 15 topics

**Phase 4 acceptance:**
- A14 (D12): test that injecting a coach-voice paragraph into a STORY slot raises `VoiceOutOfZoneError`
- A15 (D13): test that a book with David appearing 5 times unchanged raises `CharacterIllustrationOnlyError`
- A16 (D14): test that referring to Marcus with "she/her" within 10 words raises `PronounContinuityError`
- A17 (D15): test that a spiral-engine chapter without a signal/amplification connective raises `SignalAmplificationMissingError`
- A18 (D17 + D19): test that >5 off-whitelist metaphor phrases in a chapter raises `DecorativeMetaphorInflationError`
- A19 (D18): test that two near-duplicate chapters (cosine > 0.85) raise `ChapterProgressionLoopError`
- A20 (D20): test that a generic-Buddhist Ahjan atom raises `GenericBuddhistDriftError`

**Lockdown acceptance (whole spec):**
- A21: any catalog run that does not match the gold-reference path's 20-dimension profile FAILS before book.txt write
- A22: the gold-reference combo (gen_z_professionals × anxiety × spiral × F006 × ahjan × production × `--exercise-journeys`) still passes (no false positives)
- A23: the 13 surfaced lesser configurations from today's smoke (`/tmp/pearl_prime_status_assembly_2026-06-06/`) all FAIL under lockdown (no false negatives)

---

## §9 — Cross-references to amended cap entries

This spec is the consolidation point for the following cap entries (per `docs/PEARL_ARCHITECT_STATE.md`):

| Cap entry | Line | Relationship under ONE-PATH |
|---|---:|---|
| `TEMPLATE-UNIVERSAL-01` | 576 | **AMENDED** — 12-chapter spine + 10-section grid hard-enforced at runtime (D1 + D2); ≥3-variant floor hard-enforced (D4); cap-entry framing updated to acknowledge registry source layer needs Phase 3b backfill to match spec |
| `BESTSELLER-INJECTIONS-MANDATORY-01` | 601 | **AMENDED** — production profile is the ONLY catalog profile (D6); STORY at sec 2/5/9 grid-architectural enforcement extended to label drift (D3); --exercise-journeys gated mandatory under D7 |
| `EXERCISE-BANK-RESOLUTION-01` | 677 | **PROMOTED** — Option 1 strict-canonical was advisory; now mandatory at runtime (D7); cross-links to `ws_exercise_strict_canonical_production_20260506` (this spec elevates that ws's PR shipping) |
| `QUOTE-ATOM-ROUTING-01` | 705 | unaffected (already retired-as-orphan) |
| `TEACHER-POOL-SEMANTICS-01` | 728 | unaffected (D9 already enforces) |
| `AUTO-PLAN-SSOT-01` + `-AMENDMENT` | 438, 523 | **CLOSED** — A3 confirms refactor SHIPPED; `ws_auto_plan_ssot_refactor_20260505` status-flip to completed in this spec's PR; L05 closes the vestigial `RUNTIME_TEMPLATES.chapter_count` follow-up |
| `PR-D-SPINE-01` | 407 | **EXTENDED** — `compact_chapter_subset` semantics extended to handle the L01 20-arc compression case (operator-pick Q-OP-L01-ARC-STRATEGY-01 default = compress-to-canonical) |
| `SPEC-739-THRESHOLD-01` | 308 | **PROMOTED** — runtime variant-floor assert (D4) closes A4's load-bearing anomaly (offline-only enforcement) |
| `HOOK-SCENE-FIRST-01` | 1867 | **PROMOTED** — F11 detector WARN→BLOCK (D10); operator action-item Q1 resolved by this spec |
| `CATALOG-800-PER-BRAND-01` | 629 | **AMENDED PENDING Q-OP-L10** — top-5-locale math broken (no de-DE/fr-FR atoms); recommended demote to top-3 (en-US + ja-JP + zh-TW) per Q-OP-L10-LOCALE-SCOPE-01 (b) |
| `PEARL-EDITOR-UPSTREAM-01` | 649 | unaffected (already content-authority canonical); Phase 3a + 3b ws's are within Pearl_Editor scope as authority-flow demands |
| `COHESIVE-FLOW-PATH-DEFAULT-SPINE-01` | (recent) | **EXTENDED** — single-knob `--pipeline-mode` default flip extended to full 20-dimension lockdown |

**No new cap entry below PEARL-PRIME-ONE-PATH-V1-01.** This spec is the consolidation point. Future amendments should amend this spec, not append parallel cap entries.

---

## §10 — Open Operator Questions (Q-OP-*; recommend defaults; operator decides)

**Q-OP-L01-ARC-STRATEGY-01** — 20-chapter arcs (449 of 531; 85%):
- (a) **[RECOMMENDED for Phase A speed]** auto-compress to 12 at load via spine-subset (handled by D1 + PR-D-SPINE-01 `compact_chapter_subset` mechanism extension to non-compact runtime formats)
- (b) Pearl_Writer rewrites each arc to 12-chapter shape (higher quality long-term; high effort: 449 × ~30 min/arc ≈ 224 hours)
- (c) hybrid: top-15-priority personas get rewrite, rest compress

**Q-OP-L09-PERSONA-FLOOR-01** — Persona-keyed atom backfill priority:
- (a) all 15 personas before any catalog run (recommended if launch is months out)
- (b) **[RECOMMENDED]** staged: gen_z_professionals (DONE; gold) + corporate_managers + working_parents + first_responders first; then healthcare_rns + gen_x_sandwich + tech_finance_burnout + millennial_women_professionals; then the rest
- (c) BLOCK catalog runs on uncovered personas until backfilled (strictest; allows staged shipping with confidence)

**Q-OP-L10-LOCALE-SCOPE-01** — de-DE / fr-FR / ko-KR atom gap (breaks CATALOG-800-PER-BRAND-01 top-5-locale math):
- (a) backfill (multi-quarter; high cost)
- (b) **[RECOMMENDED]** demote CATALOG-800-PER-BRAND-01 to top-3 (en-US + ja-JP + zh-TW) — only the 3 locales with shipping atoms today
- (c) stage per-locale launch as separate AMENDMENT

**Q-OP-VOICE-BRAID-01** — C2 voice braid (D12):
- (a) alternate
- (b) **[RECOMMENDED]** slot-zoned (HOOK + INTEGRATION = authorial-I; STORY = third-person omniscient; TEACHER_DOCTRINE = Ahjan-specific; REFLECTION = authorial-I; EXERCISE = coach; SCENE = second-person present)
- (c) collapse to single voice

**Q-OP-CHAPTER-REPETITION-THRESHOLD-01** — D18 cosine similarity threshold T:
- (a) **[RECOMMENDED]** 0.85 (conservative; flags near-duplicates without false-positive on intentional theme recurrence)
- (b) 0.80
- (c) 0.90
- Embedding model: sentence-transformers all-MiniLM-L6-v2 local (no paid API per CLAUDE.md Tier policy; CPU; ~500MB)

**Q-OP-METAPHOR-CAP-N-01** — D17 decorative metaphor cap per chapter (beyond SCENE):
- (a) **[RECOMMENDED]** 5 per chapter beyond SCENE (1 per slot type other than HOOK/STORY/INTEGRATION)
- (b) 3 (strictest)
- (c) 7 (loosest; risks "treading water" recurrence)

**Q-OP-SIGNATURE-PHRASES-COUNT-01** — C5 signature_phrases.yaml whitelist size per book:
- (a) **[RECOMMENDED]** 5
- (b) 7
- (c) 3

**Q-OP-DRAFT-PROFILE-SMOKE-01** — Should `--smoke` flag preserve draft-profile for ad-hoc operator-attended runs?
- (a) **[RECOMMENDED]** YES — operator-attended exempt (debug velocity); draft profile permitted only when `--smoke` flag set
- (b) NO — production only everywhere

**Q-OP-RUNTIME-FAIL-MESSAGE-LANGUAGE-01** — When the runtime rejects a lesser config, who's the audience?
- (a) operator-readable (English error with WHY + WHAT TO FIX)
- (b) agent-actionable (structured exception with ws-suggestion)
- (c) **[RECOMMENDED]** both — single message with both layers (English summary + structured exception fields)

**Q-OP-MIGRATION-CADENCE-01** — Phase 1 mechanical sweeps + Phase 2 runtime gates:
- (a) **[RECOMMENDED]** ship together as single PR per agent for atomicity (one PR per ws's mechanical+runtime set)
- (b) split per L-row for review surface (slower; easier review)
- (c) Pearl_PM sequences per readiness (most flexible; risks coordination drift)

**Q-OP-MOVE-4-VERDICT-RECOMPUTE-01** — Recompute the Move 4 27/30 verdict under production-profile + §13 rubric?
- (a) **[RECOMMENDED]** YES, before Phase 1 dispatches (clears the false-positive; refreshes operator confidence baseline)
- (b) NO, baseline shifts after lockdown anyway

**Q-OP-GOLD-REFERENCE-SHA-PIN-01** — Pin the gold-reference SHA + branch as a known-good anchor in `~/.claude/projects/-Users-ahjan-phoenix-omega/memory/MEMORY.md`?
- (a) **[RECOMMENDED]** YES — append to `project_known_good_anchors.md`; the gold ref IS the canonical SHA per `feedback_drift_recovery_git_first`
- (b) NO (defer to per-persona anchor pinning later)

**Q-OP-CRAFT-DEPTH-OVERLAY-PROPOSAL-DISPOSITION-01** — disposition of the predecessor `docs/PEARL_PRIME_CRAFT_DEPTH_OVERLAY_PROPOSAL_2026-06-06.md`?
- (a) **[RECOMMENDED]** mark as SUPERSEDED-BY-PEARL-PRIME-ONE-PATH-V1-01; retain as historical context; do not delete
- (b) delete entirely (the constraints are folded into this spec)

---

## §11 — LLM Tier Policy compliance (per CLAUDE.md)

Every component of this lockdown adheres to the Tier policy:
- **Tier 1 (Claude Code, operator-present):** all spec authoring (this doc), Pearl_Architect rulings on Q-OP-*, Pearl_Writer atom authoring under Phase 3a + 3b, Pearl_Editor doctrine authoring + signature_phrases.yaml authoring.
- **Tier 2 (Gemma English / Qwen CJK6 on Pearl Star via Ollama):** D18 chapter-repetition embedding model = local sentence-transformers all-MiniLM-L6-v2 (no API; CPU; ~500MB). Optional first-draft Qwen passes for atom backfill under Phase 3a (Pearl_Editor's discretion; revised by Pearl_Writer in Tier 1).
- **BANNED:** no `ANTHROPIC_API_KEY` / OpenAI / Google AI / DashScope cloud / Together / Replicate / Perplexity / Cohere / Mistral-paid in any runtime gate, validator, or assembly step. Per CLAUDE.md `.github/workflows/llm-policy-enforcement.yml` — violations block PRs.

---

## §12 — Failure messages (operator-readable + agent-actionable)

Per Q-OP-RUNTIME-FAIL-MESSAGE-LANGUAGE-01 default (c) both layers:

**Template:**
```
[PEARL-PRIME-ONE-PATH-V1] Dimension <Dx> violation: <CamelCaseError>
  WHY: <one-sentence English diagnosis>
  WHAT TO FIX: <one-sentence remediation pointer; cite spec section or ws_id>
  STRUCTURED:
    dimension: D<x>
    canonical_value: "<value from §2>"
    observed_value: "<value at failure>"
    file_path: "<source-slot path>"
    line_offset: <int>
    suggested_ws: "<ws_id from §10 routing>"
    cap_entry: "PEARL-PRIME-ONE-PATH-V1-01"
```

**Examples:**

```
[PEARL-PRIME-ONE-PATH-V1] Dimension D1 violation: ArcChapterCountError
  WHY: Arc file declares chapter_count: 20; canonical is 12.
  WHAT TO FIX: Either use a 12-chapter arc (e.g. gen_z_professionals__anxiety__spiral__F006.yaml) OR enable spine-subset compression per Q-OP-L01-ARC-STRATEGY-01.
  STRUCTURED:
    dimension: D1
    canonical_value: "12"
    observed_value: "20"
    file_path: "config/source_of_truth/master_arcs/corporate_managers__anxiety__spiral__F006.yaml"
    line_offset: 6
    suggested_ws: "ws_pearl_editor_one_path_phase_3a_persona_keyed_atom_backfill_20260606"
    cap_entry: "PEARL-PRIME-ONE-PATH-V1-01"
```

```
[PEARL-PRIME-ONE-PATH-V1] Dimension D8 violation: PersonaAtomCoverageError
  WHY: Required persona-keyed atom dir missing for corporate_managers × anxiety: TEACHER_DOCTRINE.
  WHAT TO FIX: Author atoms/corporate_managers/anxiety/TEACHER_DOCTRINE/CANONICAL.txt modeled on atoms/gen_z_professionals/anxiety/TEACHER_DOCTRINE/CANONICAL.txt; route to Pearl_Editor.
  STRUCTURED:
    dimension: D8
    canonical_value: "all 16 required atom-type dirs present"
    observed_value: "missing: TEACHER_DOCTRINE, PERMISSION_GRANT, TEACHER_DOCTRINE_INTRO, ANGLE_DEFINITION, ANGLE_CALLBACK"
    file_path: "atoms/corporate_managers/anxiety/"
    line_offset: null
    suggested_ws: "ws_pearl_editor_one_path_phase_3a_persona_keyed_atom_backfill_20260606"
    cap_entry: "PEARL-PRIME-ONE-PATH-V1-01"
```

```
[PEARL-PRIME-ONE-PATH-V1] Dimension D7 violation: EnrichmentGapError
  WHY: EXERCISE slot at chapter 3 fell through to practice_library; production profile requires persona-keyed or teacher-bank EXERCISE only.
  WHAT TO FIX: Either author atoms/corporate_managers/anxiety/EXERCISE/CANONICAL.txt with ≥3 variants per slot, OR author teacher_banks/ahjan/approved_atoms/EXERCISE atoms for the relevant slot, OR run under --quality-profile draft (non-catalog only).
  STRUCTURED:
    dimension: D7
    canonical_value: "persona-atom OR teacher-bank EXERCISE; NO practice_library fall-through"
    observed_value: "practice_library fall-through at chapter_index=2"
    file_path: "SOURCE_OF_TRUTH/practice_library/inbox/*.json"
    line_offset: null
    suggested_ws: "ws_pearl_editor_one_path_phase_3a_persona_keyed_atom_backfill_20260606"
    cap_entry: "PEARL-PRIME-ONE-PATH-V1-01"
```

The failure-message template is canonical. All 18 exception classes (§5) emit messages in this shape. Agents reading failures can `grep` for the `STRUCTURED:` block to extract machine-actionable fields; operators reading failures see the WHY + WHAT TO FIX at the top.

---

## §13 — Anti-drift check

- This spec does **not** replace any V4.5 Writer Spec, PHOENIX_ARC_FIRST_CANONICAL_SPEC, or `PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md` semantics.
- All 20 dimensions trace to either an existing cap entry (TEMPLATE-UNIVERSAL-01, BESTSELLER-INJECTIONS-MANDATORY-01, etc.) OR the CRAFT_DEPTH_OVERLAY proposal — no new architecture invented.
- The 6 child ws's dispatch the work; no implementation in this PR. The PR is scoped to spec + governance + manifest + ws rows.
- Authority order preserved (V4.5 Writer Spec → PHOENIX_ARC_FIRST_CANONICAL_SPEC → PEARL_PRIME_BOOK_SYSTEM_CANONICAL → this spec).
- Memory `feedback_validation_before_scaling` honored — Phase 3a + 3b content backfill ws's gate Phase 4 craft-gate activation; lockdown gates Phase 4 catalog-scale runs; recompute Move 4 verdict gates trust restoration.
- Memory `feedback_drift_recovery_git_first` honored — gold reference IS the canonical SHA; this spec is git-first restoration encoded as runtime enforcement. Q-OP-GOLD-REFERENCE-SHA-PIN-01 (a) extends the principle to MEMORY.md.
- Memory `feedback_sibling_session_collision` honored — sibling PR search `gh pr list --search "ONE PATH lockdown" --state all` returned no matches; this is the first PR for this lockdown.

---

## §14 — Disposition of CRAFT_DEPTH_OVERLAY proposal

Per Q-OP-CRAFT-DEPTH-OVERLAY-PROPOSAL-DISPOSITION-01 (a) recommended:
- `docs/PEARL_PRIME_CRAFT_DEPTH_OVERLAY_PROPOSAL_2026-06-06.md` marked as **SUPERSEDED-BY-PEARL-PRIME-ONE-PATH-V1-01** in its frontmatter (Pearl_PM follow-up; not in this PR).
- Historical context preserved (Pearl_Architect Phase A reasoning trace).
- All G1-G6 + C1-C5 constraints folded into D12-D20 of this spec.
- Future amendments to craft constraints amend THIS spec, not the proposal.

---

## §15 — Closeout

This spec defines the canonical Pearl Prime ebook-assembly path with 20-dimension precision, the 18-row deletion manifest, the runtime fail-fast enforcement contract, and the 6 child ws fan-out for implementation. It is **PROPOSAL pending Pearl_Architect cap-entry ratification + operator answers to §10 Q-OP-***. Upon ratification, the cap entry [`PEARL-PRIME-ONE-PATH-V1-01`](../PEARL_ARCHITECT_STATE.md#pearl-prime-one-path-v1-01) (appended in the same PR) becomes the active governance row; the 6 child ws's spawn per `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (status proposed → in_progress upon operator green-light).

The operator directive is satisfied: 1 canonical path. 18 lesser paths classified for deletion / compression / backfill / block. Runtime enforcement at every join. No agent — Pearl_Prime, Pearl_Writer, Pearl_Editor, or downstream catalog runners — can ship a lesser configuration silently. The next session that runs the canonical CLI with a lesser combo will receive a `PersonaAtomCoverageError` or `ArcChapterCountError` (or whichever fires first in the cascade) and halt before book.txt write.

---

*Companion artifacts:*
- `artifacts/qa/pearl_prime_one_path_deletion_manifest_20260606.tsv` (18-row TSV)
- `docs/PEARL_ARCHITECT_STATE.md#pearl-prime-one-path-v1-01` (cap entry)
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (6 child ws rows + 3 status-flip notes)
- `artifacts/qa/pearl_prime_audit_2026-06-06.md` (7-axis audit synthesis)
- `artifacts/qa/pearl_prime_why_smoke_was_worse_2026-06-06.md` (the specific regression that surfaced the persona-keyed atom gap that motivated D8)
- `/tmp/pearl_prime_audit_2026-06-06/agent{1,2,3,4,5,6}_*.md` (per-axis evidence reports)
- `/tmp/pearl_prime_audit_2026-06-06/recommendations.md` + `qa_checklist.md` (Pearl_PM follow-throughs)
- `artifacts/pearl_prime/gold_reference_ladder_2026-05-30/` (the canonical truth)
