# Lever B — Cross-Chapter Scaffolding Variety (2026-06-15)

**Author:** Pearl_Dev · **Project:** proj_pearl_prime_bestseller_rebase_20260425
(composer-frontier thread, ws_bridge_transition_system_20260416)
**Complements:** Lever A (`../duration_ladder_subset_proof_20260615/INDEX.md`, PRs #1610/#1612)
**Spec:** `../../analysis/pearl_prime_priorities/ADAPTIVE_CHAPTER_COUNT_AND_F1_20260615.md` §4 (Lever B);
`../../analysis/pearl_prime_priorities/COMPOSER_FRONTIER_FIX_SPEC_20260614.md` (DEFECT 1/3).

---

## TL;DR

Lever B's **composer-engine** half (data-driven bridge bank + per-chapter rotation + bridge_memory
dedup + book-distinct seeding) **was already merged** on `origin/main` via the OPD-109 fleet
(PRs #1212/#1217/#1226/#1227/#1228/#1230/#1233/#1243) + **#1589** (engine) + **#1596** (deferred lanes).
The inter-chapter thread-forward F1 cluster the brief named ("What remains is the moment after the
alarm fires…") is **GONE on current main** — verified 0 occurrences in fresh full-12 renders.

This session found and fixed **one remaining composer-owned cluster** (`_bridge_within_slot`
shape-bucket degeneracy) and **surfaced a hard scope boundary**: at full-12, **99.6% of the residual
F1 is generated OUTSIDE the Lever-B WRITE_SCOPE** — by the depth-pass atom re-injection in
`enrichment_select.py` and HOOK/exercise/doctrine re-stamping in `golden_chapter_synthesis.py`.

## Root cause of the in-scope cluster (FIXED)

`chapter_composer.py::_bridge_within_slot` chose its shape bucket via
`shape_idx = atom_pair_index % len(shape_names)`. STORY has **3** shape buckets, so every atom_pair
divisible by 3 (the live build emits the first within-slot bridge of each STORY stack at pairs
9/21/30/36 — all ≡ 0 mod 3) landed on `shape_names[0]` = `contrast_lift` **in every chapter**. The
`(book_count, seed_rank)` sort could not break the cross-chapter tie hard enough, so
`"Same body. Different door. Watch what changes."` recurred **8× book-wide** in deep_book_6h.

**Fix (all in `chapter_composer.py`, in-scope):**
1. Fold `chapter_index` into the bucket choice — `(chapter_index + atom_pair_index) % len(shapes)` —
   so the same atom_pair no longer pins to one bucket across chapters.
2. When a rotation state is present, **widen the candidate pool to all shape buckets** for the slot
   (deduped by text) so book-level dedup has headroom to reach a still-unused sibling-bucket variant.
3. Make book-level no-repeat a **HARD preference**: restrict to `book_count == 0` variants whenever
   any remain, before the least-used-first sort.

The legacy seed-only path (no rotation state) is byte-identical to before — pool-widening engages
only when a `WithinSlotRotationState` exists.

## Before / After — full-12 tiers (gen_z_professionals × anxiety, ahjan)

Build: `scripts/pilot/run_spine_pipeline.py --format <tier> --seed leverB_baseline`
(deterministic; `compose_from_enriched_book(quality_profile="draft")`; no paid LLM).
Scored with `phoenix_v4.quality.register_gate.evaluate_register`. **Both variants built on the
identical `origin/main` (a4021381c) composer — only the Lever-B edit toggled** — so the delta is
attributable purely to this change (NOT to #1596, which is already on main and lifts the absolute
numbers vs the brief's stale-snapshot table).

| tier | chapters | words | F1 clusters (origin/main → +Lever-B) | verdict |
|------|:--:|:--:|:--:|:--|
| standard_book | 12 | 23.5k | 61 → 61 | HARD_FAIL |
| extended_book_2h | 12 | 26.1k | 67 → 67 | HARD_FAIL |
| deep_book_6h | 12 | 59.5k | 224 → 224 | HARD_FAIL |

**In-scope cluster, deep_book_6h:** `"Same body. Different door."` raw count **8 → 6**; the **size-8
within-slot F1 cluster is eliminated** (gone from the cluster-size histogram); the within-slot bridges
now draw evenly across all 3 STORY shape buckets. Book-level F1 is unchanged because that one cluster
is 1 of 224 (see attribution below). (`SUMMARY.json` has the full per-tier finding breakdown.)

## Why book-level F1 barely moves — the scope boundary (SURFACED, NOT fixed)

F1-cluster emitter attribution, deep_book_6h (224 clusters on origin/main):

| emitter | clusters | in Lever-B WRITE_SCOPE? |
|---|--:|:--:|
| `chapter_composer._bridge_within_slot` (STORY within-slot bridge) | **1** | ✅ yes — fixed here |
| depth-pass atom re-injection / HOOK·EXERCISE·doctrine re-stamp | **223** | ❌ no |
| | **= 0.4% in-scope** | |

The dominant full-12 clusters are **not** composer bridges:

| cluster | size | source | emitter (verified by trace) |
|---|--:|---|---|
| "The task is open…" (HOOK v02) | 14 (all 12 ch) | `atoms/.../HOOK/CANONICAL.txt` v02 | depth-pass re-read → **`enrichment_select.py`** (15× in prose, **0× in enriched slots & plan**) |
| "Just thirty seconds…" / "Now, I want you to notice…" | 12 / 10 | EXERCISE atom + `component_templates.yaml` | enrichment EXERCISE selection / depth |
| "This is The Unspoken…" | 9 | doctrine atom | depth re-read |
| "Same body. Different door…" | 8→6 | `within_slot_bridge_families.yaml` | **`chapter_composer._bridge_within_slot`** ← the in-scope one |

Trace method: monkeypatched the emitting functions during a live `compose_from_enriched_book` run and
counted occurrences in `book_plan.json` (enrichment plan) vs `enriched.chapters[].slots[]` vs final
composed prose. The HOOK/EXERCISE/doctrine strings are **0× in the plan and enriched slots but 15×/12×/
9× in composed prose** → injected by the depth pass (`enrichment_select.apply_depth_pass` /
`golden_chapter_synthesis` HOOK aggregation), which re-selects the **same** atom CANONICAL block across
chapters. That is a **selector-dedup** defect in `enrichment_select.py` — explicitly OUT of the Lever-B
WRITE_SCOPE, and `enrichment_select.py` is adjacent to a concurrently-running #1601 pipeline.

## Verdict note

All tiers stay `HARD_FAIL` — the register verdict is **F2-only** (`register_gate._aggregate_verdict`;
F1 never reaches HARD_FAIL severity). Lever B is an **F1/prose-quality** lever, not a gate-flip
(per ADAPTIVE_CHAPTER_COUNT_AND_F1 §6, Lane C = F2 owned by #1601 + atom-repair).

## NEXT_ACTION (to actually move full-12 F1 / unblock SHORT&FAST)

The headline deliverable ("materially fewer F1 clusters at full-12 → unblock the 12-thin SHORT&FAST
cells") requires a **depth-pass cross-chapter atom-dedup** in `enrichment_select.py`
(`_load_depth_content` / `apply_depth_pass`): the `book_seen_bodies` exact-match dedup is defeated by
per-chapter trailing-clause variation, so the same HOOK/STORY/REFLECTION block (e.g. HOOK v02) is
re-injected across all 12 chapters. That file is OUT of this session's WRITE_SCOPE (and adjacent to the
live #1601 re-pilot). Recommend a dedicated `enrichment_select.py` depth-dedup task, gated to not
collide with #1601. The in-scope composer fix here is a correct, regression-free prerequisite (the
within-slot bridge layer is now clean), but it is not sufficient on its own.

## Files

- Fix: `phoenix_v4/rendering/chapter_composer.py` (`_bridge_within_slot`)
- Regression: `tests/test_bridge_transition_system.py`
  (`test_within_slot_bridge_no_cross_chapter_repeat_on_degenerate_pairs`,
  `test_within_slot_legacy_seed_only_path_is_deterministic`)
- Renders: `baseline/<tier>/book.txt`, `after_fix/<tier>/book.txt`
- Data: `SUMMARY.json`
