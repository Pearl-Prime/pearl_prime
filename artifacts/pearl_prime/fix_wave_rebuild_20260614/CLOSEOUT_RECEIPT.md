# CLOSEOUT RECEIPT — Composer Frontier Fix Wave

- **Date:** 2026-06-14
- **PR:** [#1587](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1587) — `agent/pearl-prime-composer-frontier-wave-20260614`
- **Commit:** `10d26fb3330c0e2bed296cbbffe196d9f5a0aa14` (parent = `e69fc6a6568aa68c033679c898db681899627b3d` == origin/main)
- **Spec:** `artifacts/analysis/pearl_prime_priorities/COMPOSER_FRONTIER_FIX_SPEC_20260614.md`
- **STATUS:** **Fixes applied + rebuild-proven (partial). AWAITING operator review. NOT merged (DO-NOT-MERGE).**
- **Verdict:** **mostly-proven (gaps listed)** — every targeted *regression-class* defect is proven 0 in the rebuilt prose; the gate-clearing claims (word_budget pass, register verdict flip) are honestly NOT met and are out of this wave's scope.

This receipt was written by the CLOSEOUT/completeness-critic agent. Every count below was **independently re-derived from the on-disk files** (`grep`/`md5`/`pytest`/`git show`), not copied from the lane or verify receipts.

---

## 1. Per-fix: file:line changed + test

| Defect | File:line (current = PR commit) | Test |
|---|---|---|
| **D1** cross-book bridge repetition (arc-role → bank wiring + per-thesis fallback pools + bridge_memory dedup) | `phoenix_v4/rendering/chapter_composer.py:132` (`_ARC_ROLE_TO_EMOTIONAL_JOB`), `:143` (`_resolve_emotional_job`), `:1921` (`_FALLBACK_THREAD_KEYWORD_POOLS`), `:1973` (`_fallback_thread`) | `tests/test_composer_frontier_laneA.py` (10) |
| **D2** template-tail truncation orphans (sentence-bounded furniture cap) | `phoenix_v4/rendering/golden_chapter_synthesis.py:1352` (`_match_is_sentence_bounded`), `:1383` (`_limit_case_insensitive_phrase_occurrences`), `:1439` (`_SCENE_FURNITURE_SIGNATURES`), `:1464` (`dedupe_scene_furniture_book`) | `tests/test_composer_frontier_laneB.py` (8) |
| **D4** cross-persona registry bleed (persona-aware chokepoint + placeholder reject) | `phoenix_v4/planning/enrichment_select.py:569` (`_REGISTRY_PERSONA_LABEL_ALIASES`), `:578` (`_REGISTRY_PLACEHOLDER_RE`), `:606` (`_registry_persona_matches`), `:637` (`_registry_type_lists` persona param), `:1501/:1529/:3000` (placeholder reject) | `tests/test_composer_frontier_laneC.py` (15) |
| **D5** broadened bracketed-stub placeholder detection (composer) | `phoenix_v4/rendering/chapter_composer.py:54` (`_PLACEHOLDER_BRACKET_RE`), `:64` (`_is_placeholder_text`) | `tests/test_composer_frontier_laneA.py` (placeholder cases) |
| **D6 fix A** word_budget ceiling reconcile to SSOT | `config/format_selection/format_registry.yaml:149` `word_range:[9000,22000]`, `:151` `cap_word_target:22000` — **NO-OP: already on origin/main** (commit `8236c5e3c` #1550) | n/a (config) |
| **D7 content** corrupted CANONICAL.txt header repair (prepend `## `) | `scripts/fix/repair_atom_canonical_headers.py` (new) + **1617** `atoms/**/CANONICAL.txt` | parse-verified (no pytest) |
| **D7 guard** bare-header parse + fail-closed delivery backstop | `phoenix_v4/planning/registry_resolver.py:221/:227/:230` (`_is_bare_block_header`); `phoenix_v4/rendering/book_renderer.py:122` (`_BARE_ATOM_ID_LINE_RE`), `:142` (`_scrub_inline_leaked_slot_markers`), `:714/:751` (`delivery_contract_gate`) | `tests/test_composer_frontier_laneG.py` (8) |
| **D5/D6** EXERCISE bank shortage (book#3 pre-render abort) | `atoms/gen_z_professionals/financial_anxiety/EXERCISE/CANONICAL.txt` (+10 practice-shaped variants) | parse/filter-verified |

PR file composition (independently verified `git diff --name-status origin/main 10d26fb3`): **1695 files = 73 added + 1622 modified + 0 deleted.** Mass-deletion governance **PASSES** (the 13,725 "deletions" in the PR API are line-level bare-header → `## `-prefix rewrites, not file removals).

---

## 2. Before/after proof per defect — ACTUAL counts I verified on disk

Baselines: `artifacts/pearl_prime/pilot_10/{03,04,06,02}_*/book.txt`. Rebuilds: `…/fix_wave_rebuild_20260614/{book3,hook,bridge}/book.txt`.
book3 = gen_z_professionals × financial_anxiety · hook = corporate_managers × burnout(overwhelm) · bridge = educators × anxiety(overwhelm).

### a) Leaked atom-id labels — `^[A-Z_]+ v\d+$` standalone lines  → **PROVEN (0)**
- **Population baseline (decisive):** across all 9 rendered pilot books, exactly **8** leaked-label lines: book02=2, book07=4, book08=2 (Lane G's "8/8" claim **exactly reproduced**).
- **Rebuilds:** book3 = **0**, hook = **0**, bridge = **0** (both strict token regex and broad `^[A-Z_]+ v\d+$`).
- **Source proof:** smoking-gun atom `atoms/gen_z_professionals/burnout/INTEGRATION/CANONICAL.txt` now has **0 bare headers / 28 `## `-prefixed**. Inert top-section stubs (`[Integration content for …]`) confirmed **0** in rendered prose (parser-dropped).
- Register cross-check: **0** register findings (of 90/104/104) mention leaked/atom-id/bare-label in any of the 3 rebuilds.
- Note: book3's PROOF.md reported "baseline 8 → 0" for *this book*; book3's own baseline had **no book.txt** (aborted), so the "8" is the population total. Same fix, correct outcome, slightly loose attribution.

### b) Verbatim cross-book bridges — `What remains is the moment after the alarm fires`  → **PROVEN (catastrophic repeat killed)**
- **bridge baseline:** **10×** within one book (byte-identical). **Rebuild:** **1×**. Max within-book repeat of any `What remains is …` line dropped 10 → **2**.
- **book3:** topic N/A (financial_anxiety) — 0 in both, not regressed.
- Residual generic fallback `What remains is the next ordinary moment …` = **2** in every rebuild (5-option pool exhausted over 11 boundaries). Within the per-book baseline band; the strict "no bridge repeats > 1×" bar is **NOT** met. The byte-identical-scaffolding signature is killed; perfect uniqueness is not achieved.
- Cross-book distinctness: the 3 rebuilt `book.txt` have **distinct md5s** → no byte-identical scaffolding across books.

### c) Truncation orphan — `sternum. still bracing.`  → **PROVEN (0)**
- Baselines: book04 = **16**, bridge/book06 = **20**, book3 baseline aborted. **Rebuilds: 0 / 0 / 0.**
- Correct full form `sternum. That is the part still bracing` present **19 (book3) / 22 (bridge) / 15 (hook)**. Orphan replaced by the complete sentence everywhere.
- Also clean in all 3 rebuilds: unresolved `{slot}` braces = 0, `[TODO/TBD/TKTK/placeholder/draft]` = 0.

### d) Cross-persona HOOK bleed — `hook for gen_z_professionals` in a non-gen_z book  → **PROVEN (0)**
- **hook (corporate_managers) baseline:** **12** foreign `[Persona-specific hook for gen_z_professionals × burnout]`. **Rebuild: 0.** Total HOOK stubs 24 → 12 (the 12 removed are exactly the foreign ones).

### e) HOOK placeholder stubs (own-persona) — `[Persona-specific hook for <own> × <own>]`  → **NOT FIXED (unchanged)**
- **hook:** own-persona stubs **12 → 12**. **book3:** **12** own-persona stubs (baseline aborted, so no before-count; all 12 are `gen_z_professionals × financial_anxiety`). bridge: 0 in both.
- Root cause (DATA, out of scope): HOOK banks hold literal `[Persona-specific hook for …]` bodies for v02-v30 (only v01 has prose). The selection path `_try_persona_content` returns `atom['content']` with no placeholder check and bypasses the composer HOOK guard. Composer regexes match the stub in unit tests but are not applied on this path. Needs HOOK-bank authoring + a guard at the selection site. Tracked: task_9e941ac7 (author), task_efcc17e0 (guard).

### f) word_budget  → **NOT PASSING (overshoot)**
- Disk SSOT confirmed: `format_registry.yaml:149 word_range:[9000,22000]`, `:151 cap_word_target:22000`; matches `platform_duration_profiles.yaml T5_standard words:22000`. format_registry is **clean vs origin/main** (D6 fix A already landed via #1550).
- `book_pass_report.json` word_budget **status = FAIL** in all 3: book3=**22709**, hook=**22848**, bridge=**24098** — all > 22000.
- The PROVE blurb's "ceiling 24000" is a **misstatement**, contradicted by disk and by the verify agents. Correct ceiling = **22000**. Rebuilds got *longer* (more real prose after removing stubs / restoring STORY atoms), not shorter. The real remaining work is D6 fix B (run_pipeline.py budget/render accounting) + fix C (gen_x_sandwich depth over-fill) — both OUT OF SCOPE, deferred.

### g) book#3 BUILDS + EXERCISE resolves  → **PROVEN (builds), partial (gates)**
- Baseline `pilot_10/03_*/`: only `stderr.log` + empty `stdout.log`, **no book.txt** (aborted on EXERCISE-BANK-RESOLUTION-01). **Rebuild:** `book3/book.txt` = **133,822 B / 22,709 words / 12 chapters**, `slots_from_practice_library == 0` (EXERCISE now fills from the 10 new persona variants).
- Caveat: to build, the verify agent had to repair an **in-flight blocker the lane fix itself introduced** — the lane-fix STORY file `atoms/gen_z_professionals/financial_anxiety/spiral/CANONICAL.txt` shipped with 10 EMPTY stub blocks (no `path:`) → `validate_canonical_atom_file` rejected the whole file → NO_STORY_POOL hard-abort. Repaired (corruption removal, 0 content authored) and **the repaired file IS in the PR** (`1 insertion, 22 deletions`). Same 10-stub corruption is latent in sibling `*/financial_anxiety/spiral/` files (task_040db495).

### register_gate verdict  → **NOT FLIPPED (still HARD_FAIL)**
- All 3 rebuilds: **verdict = HARD_FAIL**. Severity breakdown (independently extracted): the HARD_FAIL is driven **solely by F2** (broken-slot grammar heuristics): book3 **10**, bridge **6**, hook **20** HARD_FAIL-severity findings. All other families (F1 templated-cluster 55/71/61, F7 practice-density 12/12/12, F12/F13/F4/F6) are WARN/FAIL and do **not** drive the verdict.
- **0** of the F2 findings are leaked-label findings → the DEFECT-7 register concern (leaked `^TOKEN vN$`) is genuinely cleared; the residual HARD_FAIL is from independent atom-prose seams + the unfixed HOOK stubs, not from anything this wave claimed to fully fix. Per spec dispatch note, the register verdict only clears when the config half (teacher_wrapper_templates ellipsis/dangling-prep + register_gate F2.C false-positive split) ALSO lands — out of this wave's file ownership.

---

## 3. Composer test-suite result — REGRESSION? **NO**

- **Independently re-ran** the 4 new lane suites: `pytest tests/test_composer_frontier_lane{A,B,C,G}.py` → **41 passed in 12.39s** (laneA 10, laneB 8, laneC 15, laneG 8). Reproduced.
- Verify-agent full scope (reported, not re-run here): **339 passed / 0 failed / 3 skipped** across 27 composer/rendering/manga/video modules.
- Pre-existing, unrelated: `tests/test_llm_callback.py` fails at **collection** (`ModuleNotFoundError: tests.test_ei_v2`, missing `tests/__init__.py`) — environmental, last touched by CI scan #1387, not part of this wave. The known slow integration test `test_spine_pipeline_integration.py::test_spine_gates_hard_records_production_policy` is a pre-existing known-fail (DEFECT 6 / "Books spine-default gate failure"), excluded from Core CI.
- **No regressions attributable to the wave.**

---

## 4. Duration-session coordination note (format_registry.yaml)

- `config/format_selection/format_registry.yaml` is a **NO-OP this wave** — `word_range:[9000,22000]` + `cap_word_target:22000` already on origin/main via `8236c5e3c` (#1550, DURATION-DERIVATION-01 §5; OPD-logged, operator-flagged for the 55→147 min customer-facing duration change) and #1572. It is **byte-identical to origin/main** in the PR (not in the stage set).
- This ceiling is the **operator-ratified magnitude decision** and exactly matches the SSOT `platform_duration_profiles.yaml T5_standard words:22000`. The spec's "24000" was an illustrative headroom figure against a stale 20k baseline — deliberately NOT applied (would re-open the two-SSOT divergence D6 was fighting).
- Only open PR touching this area is **#1575** ([DO-NOT-MERGE] Pearl_Research duration-per-platform handoff) — docs/handoff only, **no format_registry code change, no conflict**.
- Forward note: any render-headroom raise above 22000 is a **fresh operator magnitude decision** against the live DURATION-DERIVATION-01 anchor, and is the lever D6 fix B/C would need.

---

## 5. Cross-lane flags (open, for the operator / follow-on lanes)

1. **DEFECT 5 HOOK stubs (DATA gap, unfixed):** ~406 `[Persona-specific hook for …]` stub bodies across 14 HOOK CANONICAL.txt (corporate_managers, first_responders, gen_alpha_students, gen_x_sandwich, gen_z_professionals, healthcare_rns, working_parents × {burnout, financial_anxiety}). Needs (a) HOOK-bank authoring/deletion and (b) a placeholder reject at `enrichment_select._try_persona_content` (regexes exist but aren't applied on that selection path). Tasks: task_9e941ac7, task_efcc17e0.
2. **DEFECT 5 mirror guards (defense-in-depth, not yet broadened):** `golden_chapter_synthesis.py:45 _PLACEHOLDER_LINE`, `section_packet_composer.py:144 _strip_placeholders`, `qa/validate_pre_intro.py:32 PLACEHOLDER_PATTERNS` still match only `{..}`/named forms, not `[… persona-specific …]` square-bracket prose stubs.
3. **DEFECT 6 fix B/C (deferred, the real word_budget frontier):** `scripts/run_pipeline.py` budgets to post-depth words PRE-render then render adds +400…+4,270 words with no book-level ceiling clamp; gen_x_sandwich books #8/#9 over-fill at PRE-depth (23k/24k). Both out of this wave's file ownership.
4. **DEFECT 7 config half (deferred):** `config/catalog_planning/teacher_wrapper_templates.yaml` (ellipsis/dangling-prep tail) + `phoenix_v4/quality/register_gate.py` F2.C lowercase-noun-start false-positive split. Register verdict will not flip until these land alongside the content repair + guard.
5. **Latent STORY-stub corruption (build blocker, sibling files):** the 10-empty-stub pattern is latent in `*/financial_anxiety/spiral/` and `gen_z/burnout/{overwhelm,watcher}/` engine-bank files. Task: task_040db495.
6. **Auto-backup mutates atom files (infra hazard):** the hourly auto-backup commit (`5445e27c7` etc.) re-corrupts atom headers tree-wide. On disk RIGHT NOW, `atoms/corporate_managers/burnout/overwhelm/CANONICAL.txt` again has 10 bare headers — **but the PR commit `10d26fb3` (parent origin/main) carries the repaired version (0 bare / 38 `## `), so the PR is unaffected.** Task: task_b8fe6104.
7. **push_guard blocks on file count (intrinsic scope, not a hazard):** 1695 > `PUSH_GUARD_MAX_FILES` default 1000. NOT a deletion/size issue (0 deletions, 21.96 MB, max single file 0.14 MB). Operator may raise the cap if accepting the DEFECT-7 content-repair scope. Push itself succeeded; no force/bypass used.

---

## 6. STATUS & NEXT_ACTION

**STATUS:** Fixes applied + rebuild-proven (partial). The regression-class composer defects (leaked atom-id labels, catastrophic verbatim cross-book bridge, truncation orphans, cross-persona HOOK bleed, book#3 pre-render abort) are **proven eliminated** in the rebuilt prose with verified before/after counts. The gate-clearing outcomes (word_budget pass, register HARD_FAIL → not-HARD_FAIL) are **honestly NOT achieved** and are documented as out-of-scope (DATA gaps + run_pipeline accounting + register config half). **PR #1587 is OPEN, DO-NOT-MERGE, awaiting operator review.** Composer test suite: **no regression.**

**NEXT_ACTION:**
1. **Operator reviews** the before/after evidence in this receipt + the 3 PROOF.md files; accepts the DEFECT-7 content-repair scope (raise `PUSH_GUARD_MAX_FILES` for this merge) → **merge #1587**.
2. **Re-run the 10-book pilot** on merged main to confirm the wave lifts the gates at population scale (expect: 0 label leaks, 0 truncation orphans, 0 cross-persona bleed, book#3 builds; word_budget + register still red until the deferred lanes land).
3. Land the deferred lanes (HOOK-bank authoring + selection-path guard; run_pipeline word-budget clamp / depth over-fill; register config half) → re-pilot.
4. **Only then proceed to the 25-book wave.**
