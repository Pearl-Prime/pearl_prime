# PEARL_PRIME_1000_BOOK_BUILD_PROGRAM_V1_SPEC

**Status:** v1 — program spec for scaling Pearl Prime toward 1,000 cohesive books
**Effective:** 2026-06-14
**Authority inputs:**
- `artifacts/analysis/PEARL_PRIME_THESIS_PLAN_VIEW_IDEA.md`
- `artifacts/analysis/pearl_prime_analysis/pearl_prime_atom_analysis_pack.md`
- `artifacts/analysis/pearl_prime_priorities/best_current_100_build_list.md`
- `artifacts/analysis/pearl_prime_priorities/fix_first_roadmap.md`
**Primary system docs this spec aligns with:**
- `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md`
- `docs/BOOK_PLANNING_SYSTEM_SPEC.md`
- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`
- `docs/BESTSELLER_STRUCTURES.md`
- `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md`

**Operating system + materialized deliverables:** `docs/specs/PEARL_PRIME_100_TO_1000_BESTSELLER_BUILD_PROGRAM.md` (active slate, Wave 1, fix-first queue, pilot set + run plan, gated fan-out). **Wave-1 execution:** `docs/specs/PEARL_PRIME_WAVE_1_EXECUTION_SPEC.md`.

**Canonical authority this spec ROUTES INTO (cite, do not duplicate — reuse-not-greenfield):**
- **Craft / chapter standard:** `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (canonical CLI §570–577); **dwell-beat craft gate + one-author/wrapper voice doctrine — PR #1527 (MERGED)** for integration-pacing; planner `phoenix_v4/planning/chapter_planner.py`.
- **Live quality gates (§9 uses THESE; no new gate):** `phoenix_v4/quality/chapter_flow_gate.py`, `phoenix_v4/quality/book_quality_gate.py`, `phoenix_v4/qa/scene_anti_genericity_gate.py`, `phoenix_v4/qa/bestseller_editor.py`, `phoenix_v4/quality/bestseller_craft_gate.py`, EI v2 `phoenix_v4/quality/ei_v2/` (+ the #1516/#1517 strengthening and the EI P0 build #1578).
- **Runtime (§8 / Phase D):** canonical bestseller CLI (overlay §570–577); spine-default enabler **PR #1536 (OPEN)**; pilot runner `scripts/pilot/run_spine_pipeline.py`; output validator `scripts/qa/validate_spine_output.py`.

Registered in the Canonical Artifacts Registry as `pearl_prime_build_program` (`artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv`).

---

## §1 — Objective

Build a Pearl Prime production program that can eventually support **1,000 cohesive books** where:

- each chapter has meaningful forward motion
- each book has a clear emotional and practical arc
- output passes structural and quality gates
- top candidates survive human/editorial review at a true trade-quality bar

This spec governs **how to scale**, not just how to render one acceptable book.

## §2 — Core thesis

The system's main bottleneck is **not** lack of theory or lack of variety. The main bottleneck is the interaction of:

- uneven atom-bank quality
- weak `STORY` / `SCENE` depth in some persona-topic clusters
- weak glue-slot banks: `PERMISSION`, `PIVOT`, `TAKEAWAY`, `THREAD`
- fallback-heavy runtime behavior
- partial drift between documented doctrine and live runtime defaults

Therefore, Pearl Prime must optimize for:

1. chapter architecture
2. source-bank strength
3. continuity glue
4. controlled fallback
5. corpus-level validation

## §3 — Non-goals

This program does **not** aim to:

- make all persona-topic combinations equally strong at once
- use machine gates as the only proof of bestseller quality
- scale to 1,000 before proving a strong 10-book and 100-book set
- solve quality primarily through additional prose doctrine docs

## §4 — Operating principle

The governing rule is:

**focus -> repair -> deepen -> validate -> scale**

Not:

**widen -> fallback -> gate-pass -> declare done**

## §5 — Program phases

### Phase A — Build from strength

Use the strongest current persona-topic pairs first.

- Input: `best_current_100_build_list`
- Rule: early production waves should come from `build_now` and strongest `build_soon` candidates
- Constraint: preserve diversity across personas and topics; avoid one-cluster domination

### Phase B — Repair recurring leverage gaps

Before expanding the slate, repair recurring weak banks that affect many books.

Current recurring priority classes:

- `PERMISSION`
- `PIVOT`
- `TAKEAWAY`
- `THREAD`

Current top personas for these recurring repairs:

- `first_responders`
- `entrepreneurs`
- `healthcare_rns`

### Phase C — Deepen bestseller lift banks

For the strongest candidate books, deepen:

- `STORY`
- `SCENE`

This is where most of the true bestseller lift comes from.

### Phase D — Reduce runtime degradation

Tighten the pipeline so output quality depends less on weak defaults or fallback behavior.

Targets:

- reduce `legacy_uniform` dependence
- reduce hidden fallback share
- prefer spine-mode truth in real production book paths
- expose fallback usage in artifacts/reports

### Phase E — Validate by corpus

Promotion happens by wave, not by anecdote:

1. 10-book pilot
2. 25-book wave
3. 100-book proven slate
4. only then scale toward 1,000

## §6 — Book selection standard

A book is eligible for early production if it has:

- strong build score from current atom inventory
- healthy `STORY` depth
- healthy `SCENE` depth
- low sparse-unit debt
- enough slot coverage to sustain chapter motion
- no major dependency on weak recurring glue banks unless those banks are already in the repair queue

**Operationalized for Wave 1 (PEARL_PRIME_100_TO_1000_BESTSELLER_BUILD_PROGRAM §6):** the eligibility filter is `readiness_band == build_now` AND `scene_blocks >= 30` AND `sparse_unit_count == 0` (zero unrepaired-glue dependency). This excludes `gen_z_professionals / anxiety` (sparse=1 in `PERMISSION_GRANT`) from Wave 1 and the pilot until fix-first item #19 lands.

## §7 — Chapter quality standard

Authority for the craft bar below: `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` + the **dwell-beat / integration-pacing** craft gate from **PR #1527** (a REFLECTION / somatic-pause beat after each teaching beat *before* the next; cap on new insights per section). This spec cites that gate; it does not redefine it. Atom completeness must not stand in for authored cohesion.

A production-worthy chapter must:

- **Orient** into a recognizable lived state
- **Name** a real mechanism
- **Turn** understanding in a meaningful direction
- **Give** something actionable or metabolizable
- **Pull** forward or close with consequence

A chapter should feel like:

- one dominant chapter role
- one arguable thesis
- one coherent emotional movement
- one meaningful payoff

A chapter must **not** feel like a stitched slot checklist.

## §8 — Runtime standard

Canonical runtime = the bestseller CLI (overlay §570–577: spine mode + strict quality profile + `--exercise-journeys`); the 10-book pilot tool is `scripts/pilot/run_spine_pipeline.py`, validated by `scripts/qa/validate_spine_output.py`. Spine-as-production-default is enabled by **PR #1536** (Phase D).

Production book runs should prefer the canonical spine path and track:

- fallback usage by slot and chapter
- source share by teacher/persona/registry/practice/fallback path
- degraded canonical parsing cases
- chapter-level flow/craft/editorial failures

Any production path that silently relies on fallback should be treated as degraded, even if the book still renders.

## §9 — Acceptance standard

Machine acceptance requires passing the existing gate stack (no new gate is built; §9 uses these live files), at minimum:

- chapter flow — `phoenix_v4/quality/chapter_flow_gate.py`
- book quality gate — `phoenix_v4/quality/book_quality_gate.py`
- scene anti-genericity — `phoenix_v4/qa/scene_anti_genericity_gate.py`
- bestseller craft / editor — `phoenix_v4/quality/bestseller_craft_gate.py`, `phoenix_v4/qa/bestseller_editor.py`
- EI v2 (rigorous-evaluation track) — `phoenix_v4/quality/ei_v2/`
- register / ship-readiness (wired by PR #1536) — `phoenix_v4/quality/register_gate.py`, `phoenix_v4/quality/ship_readiness_aggregator.py`

Production books are expected to HARD_FAIL this strict stack today (register_gate HARD_FAIL; ei_v2 ≈0.53; `book_pass` fails the >20000-word ceiling though `book.txt` still renders) — that failure is the **signal** that trade-pub register is the real frontier, not a bug to mask. The pilot runs strict gates and reports honestly; only *tests* of the entrypoint use `--quality-profile=draft`.

But gate pass is only **structural acceptance**. Final acceptance for a serious bestseller candidate requires human/editorial confirmation that:

- chapter progression feels real
- stories are vivid enough
- repetition is controlled
- middle-book energy does not flatten
- endings land without generic uplift

## §10 — Fix-first roadmap standard

Repairs are prioritized by:

1. number of top-100 books affected
2. recurrence across many topics for one persona
3. whether the weak bank is a glue bank or core story bank
4. whether the affected book is already near-buildable

This means recurring persona-slot programs usually outrank one-off repairs.

## §11 — Deliverables

The program should continuously maintain:

- active top-100 build slate
- recurring bank repair roadmap
- per-wave book list
- per-wave repair queue
- fallback usage evidence
- corpus-level editorial review results
- promotion/block decisions per wave

## §12 — Definition of done

Pearl Prime is **not done** when it merely has:

- a large catalog
- good docs
- passing gates
- one or two strong books

It is done enough to scale only when:

- the 10-book pilot is strong under human review
- the 25-book wave holds quality without collapse
- the 100-book slate is built mainly from strong clusters, not fallback illusion
- recurring weak glue banks have been repaired in priority personas
- `STORY` / `SCENE` depth is strong in top families
- fallback reliance is measured and controlled

## §13 — Immediate execution order

The next concrete sequence is:

1. use the current top-100 build list as the candidate pool
2. define Wave 1 from the strongest 25 books
3. take the top items from the fix-first roadmap
4. repair those banks before widening Wave 1
5. run a 10-book proof set with human review
6. promote only the clusters that hold quality repeatedly

---

## Bottom line

Pearl Prime reaches 1,000 cohesive books **by scaling from proven strong clusters**, not by trying to make every cluster equally strong at once.

The winning formula is:

**strong source banks + chapter architecture + continuity glue + reduced fallback + corpus validation**