# Cohesive-Flow 12×10×5 — Architecture & Drift Audit (read-only)

**Auditor:** Pearl_Architect (read-only architecture audit; NO renderer/atom/config edits — this artifact is the only change)
**Date:** 2026-05-29
**Scope:** Verify the operator's assertion that the COHESIVE-FLOW book structure ("12 chapters × 10 sections × 5 variations per section, with bestseller elements + stories + exercises injected on top") that "used to work" has DRIFTED to a 9-slot bestseller beat, and that this is why 15-minute books are still great while 6-hour books got bad.
**Method:** Read in full — `phoenix_v4/planning/beatmap_compile.py`, `phoenix_v4/planning/story_planner.py`, `phoenix_v4/planning/variation_selector.py`, `phoenix_v4/planning/enrichment_select.py` (story routing + depth pass), `phoenix_v4/planning/injection_resolver.py` (BookSlotTracker), `scripts/run_pipeline.py` (`_run_spine_pipeline_mode`), `phoenix_v4/rendering/golden_chapter_synthesis.py` (`_bucket_slots`), `config/format_selection/format_registry.yaml`, `config/plans/*.yaml`, `config/practice/assembly_components.yaml`, `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md`, `artifacts/catalog/pearl_prime_book_script_catalogs/README.md`, and the forensic `docs/diagnostics/OPD-142_STORY_SCHEDULE_REGRESSION_FORENSIC_2026-05-21.md`. Git `log`/`show` used for drift commits. Builds on `artifacts/qa/PEARL_PRIME_CH1_CONSTRUCTION_AUDIT.md` and `artifacts/qa/D1_EXERCISE_REPEAT_COUNT_INVESTIGATION.md` — **and corrects one material error in the former.**

> ## BLUF (bottom line up front)
> The operator is **substantially right**, and a prior audit was wrong on the key point. **12×10×5 is REAL, is the documented canonical contract, and is wired into live code** — it is the SOMATIC 10-slot somatic grid (`beatmap_compile.py:42`, PR #395) consumed by the **spine** path, with 5 story variants per arc-position (`story_atoms/.../v01..v05`). The prior CH1 audit's claim that "there is **no** `SOMATIC_10_SLOT_GRID` anywhere in the render path" is **FALSE** — it was reading the **legacy/registry** path (the 9-slot bestseller beat in `config/plans/*.yaml`), which is the **code default** but **not** the canonical contract. The structure did not *evaporate*; the system has **two divergent paths** and the canonical 12×10×5 spine path is gated behind a flag the catalog batch runner does not pass. The Priya "1 story / 3 places / 1 chapter" mechanism is real, was broken by PR #1248 (2026-05-20), and has since been **restored** on current main (`enrichment_select.py:1713`). The 6h-degrades symptom is the **depth pass** stacking ~35 DEPTH atoms into a chapter's STORY/REFLECTION buckets (`enrichment_select.py:3135-3141`), which 15-min books never trigger.

---

## THE TWO PATHS (this is the whole story)

| | **Spine path** (canonical per spec) | **Legacy / registry path** (code default) |
|---|---|---|
| Selected by | `--pipeline-mode spine` | `--pipeline-mode registry` (the **argparse default**, `run_pipeline.py:1604`) |
| Structure source | `compile_beatmap()` → **`SOMATIC_10_SLOT_GRID`** (10 sections) | `config/plans/*.yaml` `bestseller_beat_order` → **9-slot beat** |
| Per-chapter sections | **10** (HOOK, STORY, REFLECTION, EXERCISE, STORY, TEACHER_DOCTRINE, REFLECTION, EXERCISE, STORY, INTEGRATION) | **9** (HOOK, SCENE, STORY, PIVOT, REFLECTION, EXERCISE, TAKEAWAY, INTEGRATION, THREAD) |
| STORY variants | **5** per arc-position (`story_atoms/{persona}/anchored/{topic}/{engine}/{arc}/micro/v01..v05`) | 20–88 `## STORY vNN` blocks in `atoms/{persona}/{topic}/STORY/CANONICAL.txt` |
| Named-character threading | **YES** — `build_story_schedule()` (Priya at sec 2/5/9) | No (per-slot independent picks) |
| Entry point | `run_pipeline.py:507 _run_spine_pipeline_mode` → `:624 compile_beatmap` | `run_pipeline.py:3524 render_book` → `assembly_compiler.compile_plan` |

The operator's "12×10×5 cohesive flow with injections" = the **spine path**. The prior audit's "9-slot beat / 20–88 variations" = the **legacy path**. **Both descriptions are accurate — of different paths.** The catalog SSOT declares the spine path canonical (`README.md:37` `pipeline_route = scripts/run_pipeline.py --pipeline-mode spine`; `PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:15-20`), but the code default and the QA batch runner route to legacy (see Q2/Q5).

---

## Q1 — Does 12×10×5 exist / did it drift? — **VERDICT: CONFIRMED (it exists; it drifted by path-divergence, not deletion)**

### 12×10×5 is a real, named, documented contract
- **Canonical doc:** `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:57-58` — "**10 sections** per chapter" + "**≥ 3 variants** per section (target 5 where authored …; selected deterministically by seed)". §2 ties chapter count to the runtime format (standard_book = 10 chapters; the historical 12 is F006 "Nervous System Ladder" arcs).
- **Catalog lock:** every Pearl Prime catalog row stores the literal `section_plan_id = pearl_prime_12x10x5` and `variant_pool_size = 5` (`artifacts/catalog/pearl_prime_book_script_catalogs/README.md:33,65-66`; generator `scripts/catalog/generate_pearl_prime_book_script_catalog.py:21,824,866`). README:40-44: "**12 chapters × 10 sections × 5 variants per section** (1 of 5 selected at render time by deterministic seed). Bestseller overlay is render-time injection."

### The 10-section grid exists in live code (the prior audit was wrong here)
- `phoenix_v4/planning/beatmap_compile.py:42-53` — **`SOMATIC_10_SLOT_GRID`** is a real constant: `[HOOK, STORY, REFLECTION, EXERCISE, STORY, TEACHER_DOCTRINE, REFLECTION, EXERCISE, STORY, INTEGRATION]` = sections 1–10.
- It is **applied**: `resolve_slot_definitions()` (`:344-345`) returns `list(SOMATIC_10_SLOT_GRID)` for every format in `SOMATIC_FULL_RUNTIME_FORMATS = {standard_book, extended_book_2h, deep_book_4h, deep_book_6h}` (`:37-39`). `compile_beatmap()` builds 10 `BeatmapSlot`s per chapter for those formats (`:473-541`) and tags `somatic_section_index` 1..10 (`:520`, `SLOT_TO_SOMATIC_INDEX :84-95`). The audit field `somatic_ten_slot_grid` is emitted true for these formats (`:666`).
- It is **on the ship path**: `run_pipeline.py:_run_spine_pipeline_mode` calls `compile_beatmap` at `:624`, feeds the beatmap to `select_enrichment` (`:665`), then `compose_from_enriched_book` (`:756`). So the 10-section grid IS in the spine render path. **`artifacts/qa/PEARL_PRIME_CH1_CONSTRUCTION_AUDIT.md:85` ("There is **no** `SOMATIC_10_SLOT_GRID` constant anywhere in the render path") is FALSE** — that audit traced the legacy reference plans, not `compile_beatmap`.
- **5 variations is real on the STORY axis:** `story_atoms/millennial_women_professionals/anchored/anxiety/watcher/{recognition,mechanism_proof,turning_point,embodiment}/micro/` each hold exactly **v01..v05** (verified: 5 files per arc-position; 126 story-atom files for that persona×topic). The prior audit's "20–88 variations" counted the `## STORY vNN` blocks inside the **legacy** `atoms/.../STORY/CANONICAL.txt` (HOOK=88, STORY≈43) — a different artifact on a different path.

### Smoking-gun drift commits
| What | Commit | PR | Meaning |
|---|---|---|---|
| 10-slot somatic grid **introduced** | `d448b9b16` (`049a486b0`/`dd4a48946` squashed) | **#395** ("feat: 10-slot somatic beatmap for standard_book and deep formats", 2026-04-12) | This is when 12×10×5 became live code. Added `SOMATIC_10_SLOT_GRID`, `SOMATIC_WORD_BUDGET`, `resolve_slot_definitions`. |
| STORY wired at sec 2/5/9 + story_schedule routing | `cbfbe14c3` | **#669** (2026-04-26) | The "**working**" state per OPD-142: named characters (Marcus/Priya/Jordan/Sam/Zoë), same-character × 3 beats per chapter. |
| 9-slot bestseller beat (legacy plans) | `e8f49bf1a`/`b03d988c3` | **#448** ("integrate clean bestseller candidate stack") | When `config/plans/*.yaml` got `bestseller_beat_order: [HOOK, SCENE, STORY, PIVOT, REFLECTION, EXERCISE, TAKEAWAY, INTEGRATION, THREAD]` (`anxiety_gen_z_professionals_6h.yaml:46`). This is the legacy-path 9-slot the prior audit described. |

**There is no commit that deleted 12×10×5.** The "drift" is structural divergence: the canonical 10-section spine and the legacy 9-section beat coexist, and which one ships depends entirely on `--pipeline-mode` (Q2/Q5). The most consequential drift is the **default**: `PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:29-48` flags it explicitly — spec says spine is mandatory, but `run_pipeline.py:1604` argparse default is `registry`. **Agents/runners that omit the flag silently get the legacy 9-slot path.**

**Nuance (do not overclaim):** even on the spine path the 10 *sections* are not 10 distinct rendered blocks. `_bucket_slots` (`golden_chapter_synthesis.py:636-668`) buckets by slot **type**, so the 3 STORY sections (2/5/9), 2 EXERCISE (4/8), and 2 REFLECTION (3/7) collapse into one stream per type via `_first_or_join` (`:671-710`), then `compose_chapter_prose` reorders into argued flow. So the spine renders ~7 *type-streams* from 10 *authored sections*. The 10-section grid governs **selection breadth and story-arc placement**, not 10 literally separate rendered chunks. This is by design, not drift.

---

## Q2 — Why 15-min good, 6-hour bad? — **VERDICT: CONFIRMED (different structures + a depth-stacking divergence)**

The 15-min and 6-hour books **do not use the same structure scaled** — they diverge twice.

### Divergence 1 — 15-min is NOT even on the 10-slot grid
- `micro_book_15` is **excluded** from `SOMATIC_FULL_RUNTIME_FORMATS` (`beatmap_compile.py:37-39` lists only standard_book/extended_book_2h/deep_book_4h/deep_book_6h). So a 15-min book compiles via the **legacy candidate path** in `compile_beatmap` (`:543-648`, the `else` branch) — ~5 chapters (`format_registry.yaml:98`), a short ~5-slot beat, **no depth pass**. Few chapters, full atoms, no stacking → it reads clean. (The catalog default runtime is `standard_book`, `generate_pearl_prime_book_script_catalog.py:88`; 15-min is a separate compact format.)

### Divergence 2 — 6-hour adds depth-stacking that degrades cohesion
- `deep_book_6h` **is** on the 10-slot grid (20 chapters, `format_registry.yaml:134`). It reaches its 50–72k word target by running **`apply_depth_pass`** (`run_pipeline.py:715`; `enrichment_select.py:3105`). The pass appends `DEPTH_*` slots which `_bucket_slots` routes into the STORY/REFLECTION/EXERCISE streams (`golden_chapter_synthesis.py:649-661`).
- **The degradation is documented in the code itself.** `enrichment_select.py:3135-3141`: *"Three rounds × 2 passes × ~6 module hits stacked ~35 depth atoms into Ch1's STORY+REFLECTION buckets, producing the '8 tableaus in a row' operator complaint."* `deep_book_6h` runs `depth_rounds = 2` (`:3141`) vs `1` for every other format. **This is the precise file:line where 6h cohesion diverges:** the same 10-section grid, but long runtime piles 35 depth atoms into a few buckets, and the within-slot bridges (`build_virtual_slot_streams` / `_bridge_within_slot`) only paper over so much.
- **Corroborating churn:** an entire PR series (OPD-109 Phase 1–4: #1212, #1228, #1230, #1233, #1242, #1243; OPD-118 #1244) targets exactly `deep_book_6h` "type-block" / "8 tableaus" cohesion — within-slot bridges, atom-bucket dedup, persona pool rotation, cross-pass aggregate-then-bridge. The 6h-degrades problem is a known, actively-patched hotspot; 15-min never enters this code because it has no depth pass.

### Compounding factor — the legacy default + the (now-fixed) EXERCISE lean
- If a 6h book runs via the **legacy** path (the code default; see Q5), it gets the 9-slot beat AND — until 2026-05-29 — the `quick_repeat` lean truncated EXERCISE guidance to 3 sentences from the 3rd exercise-chapter on (`D1_EXERCISE_REPEAT_COUNT_INVESTIGATION.md`). On a 20-chapter book that hit ~18 chapters; on a 5-chapter 15-min book it rarely fired. **This lean is now disabled** (`config/practice/assembly_components.yaml:25-43`, operator directive 2026-05-29, "no exercise may ever be leaned/truncated") — so that specific 6h degradation is already remediated on this branch. The depth-stacking (Divergence 2) is the residual, structural cause.

**Net:** 15-min good because it's a short, depth-free legacy-candidate render; 6h bad because long runtime triggers `apply_depth_pass` stacking + (legacy default) the 9-slot beat. Not "the same structure scaled" — genuinely different render shapes.

---

## Q3 — "1 story in 3 places across 1 chapter / Priya" — **VERDICT: CONFIRMED (real, spine-only, broke in PR #1248, restored on current main)**

This mechanism is `phoenix_v4/planning/story_planner.py` and it literally uses **Priya** as its worked example.

- **The mechanism:** `build_story_schedule()` (`:424`) selects N_PER_PHASE (default 3) full-arc character stories per book phase. A "full arch story" = one character's journey `recognition → mechanism_proof → turning_point → embodiment` (`:8-9, :50-55`). `_schedule_phase` (`:383-417`) docstring: *"**One story per chapter. Arc positions spread across the three SCENE slots.**"* The 3 arc positions are placed at `SCENE_SECTION_INDICES = (2, 5, 9)` (`:68`) **within one chapter** (`:403-415`). So one named character (e.g. Priya) is introduced at section 2 (recognition), developed at section 5 (mechanism_proof), and resolved at section 9 (turning_point, or embodiment in a phase-final chapter) — **exactly "1 story / 3 places / 1 chapter."**
- **Priya is in the source:** `story_planner.py:17` — *"v03 of recognition is Priya, but v03 of mechanism_proof may be Nadia."* The planner scans atoms for the first named character (`:150` NER pass), groups by character across arc positions (`_index_by_character :230-233`), and selects characters with deepest coverage (`:464-472`), borrowing best-fit atoms for missing positions (`:21-23`).
- **It is ACTIVE on the spine path:** wired in `enrichment_select.py:1626` (`build_story_schedule`) and consumed at `:1714` — `if stype in ("SCENE","STORY") and _sec_idx in SCENE_SECTION_INDICES:` injects `_story_schedule.get(...)` with `source = "story_plan"`. Story atoms exist for the live persona (`story_atoms/gen_z_professionals/anchored/anxiety/` = 74 files; `millennial_women_professionals` = 126). Personas without `anchored` coverage fall through to the generic STORY waterfall (`enrichment_select.py:1705` comment).
- **It DRIFTED and was RESTORED** (the operator's "used to work" intuition is precisely correct here). Per `docs/diagnostics/OPD-142_STORY_SCHEDULE_REGRESSION_FORENSIC_2026-05-21.md`:
  - **Working:** PR #669 (`cbfbe14c3`, 2026-04-26) — verified named characters Marcus/Priya/Jordan/Sam/Zoë, same-character × 3 beats per chapter.
  - **Broke:** PR **#1248** (`639f273fb`, 2026-05-20, "OPD-116/117 Phase B — angle journey"). `patch_beatmap_angle_journey` inserts ANGLE_DEFINITION/ANGLE_CALLBACK at list-index 1, shifting STORY slots from list positions (1,4,8) to (2,5,9). The routing guard used `_sec_idx = slot_i + 1` → STORY slots became {3,6,10} ∉ {2,5,9} → the schedule was BUILT (31 entries) but **never CONSUMED** → STORY slots fell through to the generic persona waterfall → **three different characters per chapter, wrong arc positions, a 7-word broken atom.** This is the operator's "it drifted."
  - **Restored:** the OPD-142 one-line fix **is applied on current main** — `enrichment_select.py:1713`: `_sec_idx = getattr(slot, "somatic_section_index", 0) or (slot_i + 1)` (keys off the preserved somatic index, not list position). PR #1275 (Holistic v2 Phase B) also added hard-mode same-character continuity to `build_story_schedule`. **So Priya-threading is live today on the spine path.** (Caveat: only on `--pipeline-mode spine`; the legacy default path has no story_schedule.)

---

## Q4 — Can 15-min books be strung together for longer books? — **VERDICT: REFUTED as currently designed; FEASIBLE only as a net-new build (NOT recommended over restoring the spine grid)**

- **No concatenation mechanism exists.** There is no `compose_from_books` / `stitch` / `assemble_book_from_units` in `phoenix_v4/` or `scripts/`. The architecture deliberately produces length by **(a) more chapters** (more `(chapter, section)` seed coordinates) and **(b) the depth pass** — never by concatenating finished short books. `scripts/compose_cohesive_chapter_from_plan.py` composes **one** cohesive chapter (`hook → scene → bridge → teaching → bridge → story → bridge → exercise → integration`, docstring `:5-6`) and is **not** imported by any ship path (confirmed by the prior audit and re-verified — no import edge from `run_pipeline`/`compose_from_enriched_book`).
- **Why stringing 15-min units would give a disjointed 6h book, not a coherent one:**
  1. **Arc collapse.** A 15-min book is a self-contained 4-phase micro-arc (HARDSHIP→HELP→HEALING→HOPE compressed into ~5 chapters via `compact_chapter_subset`, `format_registry.yaml:186`). Twenty-four of them concatenated = 24 mini-resolutions, not one 6h transformation arc. The phase model (`PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:68-79`) assumes a single arc spanning the whole book.
  2. **Story-thread collapse.** `build_story_schedule` shares `book_used_paths` across phases so a reader meets **12 distinct characters** across one book (`story_planner.py:458-461`). Concatenated 15-min units would repeat the same handful of characters every ~5 chapters (each unit re-seeds), destroying the named-character continuity Q3 just confirmed.
  3. **Uniqueness collapse.** `BookSlotTracker` (`injection_resolver.py:45-73`) enforces no-repeat **within one book**. Stitched units would each restart their tracker → heavy cross-unit atom repetition → worse anti-spam (Q5) and visible "the same exercise again" seams.
- **What it would take (if ever pursued):** a new book-level composer that (i) plans ONE 4-phase arc across all chapters, (ii) runs a single `build_story_schedule` and a single `BookSlotTracker` over the full chapter set, (iii) renders cohesion bridges across unit seams. That is **functionally identical to just running the existing spine pipeline at a long runtime** — i.e. the spine 10-slot grid already *is* "the good short-book engine, scaled with one arc + one tracker." **Recommendation: do not build a concatenator. The higher-leverage move is to restore/repair the spine 12×10×5 path (Q1/Restoration) so long books inherit the 15-min book's cohesion natively.**

---

## Q5 — Anti-spam / cross-book uniqueness — **VERDICT: CONFIRMED (three independent layers; 5-variant spine still has a vast combinatorial space; 20–88 legacy is wider per-slot but that is not the binding constraint)**

Three layers guarantee 925×4 books are not duplicates:

1. **Book-level structural variation** — `phoenix_v4/planning/variation_selector.py`. Selects `book_structure_id × journey_shape_id × motif_id × section_reorder_mode × reframe_profile_id × chapter_archetypes`, keyed by `sha256(seed|topic|persona|angle|arc|installment)` (`:33-43`). Distinct knob pools: 6 × 5 × 6 × 4 × 4 = **2,880 base structural combos** *before* chapter_archetypes/angle/arc/persona/topic/seed multiply it. Explicit anti-clustering: **hard cap** `ANTI_CLUSTER_COMBO_MAX_SHARE = 0.15` (`:21` — no combo may exceed 15% of a wave; `:233-247` rotates motif then reframe to escape an over-used combo) + **soft penalty** `SOFT_PENALTY_PER_USE = 0.7` (`:23`, least-used preference). Emits a per-book `variation_signature` (`:280-293`).
2. **Per-slot variant selection (within-book no-repeat + family spread)** — `injection_resolver.py BookSlotTracker.pick` (`:75-`): hard-excludes already-used `variant_id`s (`:98-102`) and prefers the least-used `collision_family` (`:108-`), with deterministic SHA tiebreak. One tracker per book → no slot repeats a variant inside a book.
3. **Deterministic-by-seed cross-book selection** — `assembly_compiler._deterministic_select` (legacy, `:659`: `sha256(f"{seed}:ch{ci}:slot{si}")`) and `registry_resolver._deterministic_index` (spine). Catalog rows lock `selection_strategy = deterministic_by_seed` (`README.md:68`). Different `(brand, topic, persona, locale)` → different seed → different selections; identical inputs → reproducible (so re-runs don't churn).

**5 variants vs 20–88 — which is better anti-spam?** Per-slot, 20–88 (legacy STORY/HOOK CANONICAL blocks) is a wider pool than 5 (spine story_atoms). **But per-slot pool size is NOT the binding uniqueness constraint** — the **book-level structural combinatorics (Layer 1, ~2,880 base × archetypes × angle × persona × topic) and the deterministic seed (Layer 3)** are. With 12 chapters × ~10 sections each drawing 1-of-(≥3..5) variants under a no-repeat tracker, plus 2,880+ structural shapes, the realized per-book fingerprint space dwarfs 925 (en_US ready rows = 1,056; full 4-locale ≈ 4×). **Uniqueness holds at scale on both paths.** The spine's 5-variant STORY pool is a *cohesion* feature (curated named-character arcs), not an anti-spam weakness — Layer 1+3 carry uniqueness. The canonical floor is "≥3 variants, target 5" (`PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:58`), and the wider 20–88 legacy pool is an *incidental* property of the old CANONICAL.txt files, not a designed anti-spam requirement.

**One caveat to verify before scale:** Layer 1 (`variation_selector`) is invoked in the variation/knob path; confirm the **spine** catalog batch actually threads `select_variation_knobs` per row (not just per-slot selection), or two books that share `(structure defaults, topic, persona)` and differ only by brand could be structurally close. Layer 3's seed still differentiates them, but Layer 1's anti-cluster cap is the explicit spam guard and should be confirmed wired on the spine batch driver.

---

## SUMMARY VERDICTS

| # | Question | Verdict | One-line |
|---|----------|---------|----------|
| 1 | Does 12×10×5 exist / did it drift? | **CONFIRMED** | Real & live as `SOMATIC_10_SLOT_GRID` (PR #395) on the spine path with 5 story variants; "drift" = path-divergence (spine vs legacy 9-slot) + the registry **default**, NOT deletion. Prior CH1 audit's "no grid in render path" is FALSE. |
| 2 | Why 15-min good, 6-hour bad? | **CONFIRMED** | Different structures: 15-min = depth-free legacy-candidate (~5 ch); 6h = 10-slot grid + `apply_depth_pass` stacking ~35 DEPTH atoms into STORY/REFLECTION buckets (`enrichment_select.py:3135-3141`, "8 tableaus in a row"). |
| 3 | "1 story / 3 places / 1 chapter / Priya" | **CONFIRMED** | `build_story_schedule` places one character's recognition/mechanism_proof/turning_point at sec 2/5/9 in one chapter; Priya is the source example; broke in PR #1248, **restored on main** (`enrichment_select.py:1713`). Spine-only. |
| 4 | String 15-min units into long books? | **REFUTED (as designed); feasible only as net-new build** | No concatenator exists; stitching collapses the single arc, named-character continuity, and within-book no-repeat → disjointed. Equivalent-but-better path is restoring the spine grid. |
| 5 | Anti-spam / uniqueness at scale | **CONFIRMED** | Three layers (book-structural anti-cluster 15% cap; per-slot no-repeat tracker; seed determinism). 2,880+ structural combos × seed ≫ 925×4. 5-variant spine is a cohesion feature, not a spam risk; per-slot pool size isn't the binding constraint. |

**The drift commit (Q1):** the structure was **introduced** by PR **#395** (`d448b9b16`) and never deleted; the operative "drift" is (a) the **default-mode** spec↔code gap (`run_pipeline.py:1604` defaults to `registry`, bypassing the 12×10×5 spine — `PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:29-48`) and (b) the Priya-threading regression in PR **#1248** (`639f273fb`), now fixed on main.

---

## RESTORATION PLAN (PLAN ONLY — do NOT implement; big change, needs operator sign-off)

Goal: make the canonical **12×10×5 cohesive-flow spine** (10-section grid + injections + Priya-threading) the **actual** ship path for the 925×4 batch, so long books inherit the 15-min book's cohesion instead of degrading. Ordered by leverage.

**Step 1 (HIGHEST LEVERAGE) — Route the catalog batch through the spine path.**
The catalog SSOT says spine (`README.md:37`), but `scripts/run_max_quality_catalog.py:149-166` invokes `run_pipeline.py` **without `--pipeline-mode spine`** → it silently runs the legacy 9-slot path. Add `--pipeline-mode spine` to that runner (and any other catalog/batch driver). This single change flips the 925-batch from the 9-slot legacy beat to the 10-section 12×10×5 grid **with no renderer change**. *Risk: LOW (one flag); but re-runs the full quality-gate suite — validate gate pass-rate on a 5-book canary first.*

**Step 2 — Flip the code default (close the spec↔code drift).**
Execute the already-routed workstream `ws_pipeline_mode_default_flip_to_spine_20260518`: change the argparse default `registry → spine` at `run_pipeline.py:1604` (+ the mirror sites `:1763, :1951, :2295` per the canonical doc) + add a regression test asserting the default at import. *Risk: MEDIUM — any caller relying on the implicit legacy default changes behavior; audit all `run_pipeline.py` callers first.*

**Step 3 — Tame the 6h depth-stacking (the actual cohesion fix for long books).**
The 6h-degrades root cause is `apply_depth_pass` piling ~35 DEPTH atoms into STORY/REFLECTION buckets (`enrichment_select.py:3135-3141`). Options (operator picks): (a) cap DEPTH atoms per slot-bucket per chapter (hard ceiling on tableaus-in-a-row); (b) prefer reaching word target via **more chapters** (raise `chapter_count_default`) over depth-stacking existing chapters; (c) route DEPTH content into *new* interstitial sections rather than appending into the 3 STORY / 2 REFLECTION buckets. Build on the OPD-109 within-slot-bridge work already merged. *Risk: MEDIUM-HIGH — affects word-target attainment; gate on `deep_book_6h` word-floor (50k) + chapter_flow_gate.*

**Step 4 — Confirm Priya-threading survives at every long runtime.**
The OPD-142 fix is on main (`enrichment_select.py:1713`) but its tests (`tests/unit/planning/test_story_schedule_routing_opd142.py`, OPD-142 §5) should be confirmed present/green for `deep_book_6h × angle_id` so the angle-journey path can never silently re-break the schedule. Ensure `story_atoms/{persona}/anchored/{topic}/` coverage exists for every catalog persona×topic (today only gen_z_professionals & millennial_women_professionals × anxiety verified) — personas without coverage get the generic waterfall, i.e. **no Priya-threading**. *Risk: LOW (tests + content audit); but the content-coverage gap is the real limiter on how many of the 925 actually get named-character arcs.*

**Step 5 — Confirm book-level anti-cluster (Layer 1) is wired on the spine batch.**
Verify `select_variation_knobs` (variation_selector) runs per catalog row on the spine driver so the 15%-of-wave combo cap actually applies at 925×4 scale (Q5 caveat). *Risk: LOW (verification).*

### Interaction with the in-flight lean-disable fix
The EXERCISE/STORY lean-disable (`config/practice/assembly_components.yaml:25-43`, operator directive 2026-05-29; branch `agent/disable-exercise-story-lean-20260529`) is **complementary and already landed on this branch** — it removes the legacy `quick_repeat` truncation that was a *second* 6h degradation. It does **not** address the depth-stacking (Step 3) or path-default (Steps 1–2). Sequence: the lean fix can ship independently now; Steps 1–2 should land *together* (flipping default without routing the batch, or vice-versa, leaves a mixed state); Step 3 should follow on a canary because it changes word-target dynamics that the lean fix also nudges upward (full exercises = more words).

---

## Corrections to prior audits (for the record)
1. `PEARL_PRIME_CH1_CONSTRUCTION_AUDIT.md:85` — "no `SOMATIC_10_SLOT_GRID` … in the render path" is **FALSE**. The grid is at `beatmap_compile.py:42`, applied for SOMATIC_FULL_RUNTIME_FORMATS, and reached via `run_pipeline.py:624` on the spine path. The audit traced only the legacy reference plans.
2. `PEARL_PRIME_CH1_CONSTRUCTION_AUDIT.md` MODEL-POINT-1 verdict "REFUTED (every number is wrong)" — **partially wrong**. On the *spine* path the operator's numbers are *substantially right*: 10 sections (grid), 5 variants (story_atoms v01-v05). They are wrong only for the *legacy* path. The correct framing is "path-dependent," not "REFUTED."
3. The "1 deterministic pick per slot" the prior audit confirmed is correct on both paths; what it missed is the **named-character story_schedule** (Priya) layered on top of the spine STORY slots.

---
*Read-only architecture audit. No renderer / atom / config files were modified. This artifact is the only change. No paid-LLM callers introduced or invoked.*
