# PROPOSED cap amendment — per-topic `compact_chapter_subset` (TEMPLATE-UNIVERSAL-01 / PR-D-SPINE-01)

**Status:** PROPOSED — awaiting **Pearl_Architect** ratification. **Do NOT self-install** (cap entries
are serialized on `docs/PEARL_ARCHITECT_STATE.md` per the hot-file lane discipline).
**Routed by:** Pearl_Prime, 2026-06-15 · **Project:** proj_pearl_prime_bestseller_rebase_20260425
**Evidence:** [`ADAPTIVE_CHAPTER_COUNT_AND_F1_20260615.md`](./ADAPTIVE_CHAPTER_COUNT_AND_F1_20260615.md) §3.

---

## Motivation

The ratified `compact_chapter_subset` (PR-D-SPINE-01) is **per-FORMAT** — one positional subset list
applied to every topic's spine. Empirically (analysis §3), only **2/12** chapter positions are
universal across the 15 topic spines (ch1=`recognition`, ch12=`integration`); the other 10 vary in
role. The current per-format subset is **coherent** for every topic (the 5ch `[1,4,7,10,12]` and 8ch
`[1,3,4,6,7,9,10,12]` positions yield 5/5 and 8/8 **distinct** roles in all 15 topics) — but it is
**topic-blind**, so the *specific* beats dropped differ by topic and may not be each topic's least
load-bearing ones (e.g. position 8 is modally `practical_interruption`, a core practice beat).

This is an **optimization, not a correctness fix** — per-format subsetting already ships coherent
compressed arcs (Lever A, PRs #1610/#1612). The amendment lets the spine author keep each topic's
load-bearing beat under compression.

## Why this needs an amendment (not self-installable)

PR-D-SPINE-01 explicitly ratified **per-format** subsets and **rejected per-topic compact spines (P2)**
as out-of-envelope. TEMPLATE-UNIVERSAL-01 makes chapter_count **per-format**. A per-topic subset is a
**new vocabulary axis** that extends both caps → Pearl_Architect ratification required.

## Proposed mechanism (additive, backward-compatible)

1. Format blocks in `config/format_selection/format_registry.yaml` MAY add an **optional**
   `compact_chapter_subset_by_topic` map keyed by topic id:
   ```yaml
   compact_book_8ch_30min:
     compact_chapter_subset: [1, 3, 4, 6, 7, 9, 10, 12]   # per-format default (unchanged, fallback)
     compact_chapter_subset_by_topic:                      # optional per-topic override
       grief:    [1, 2, 4, 6, 7, 9, 11, 12]                # keeps grief's relational_consequence beat
       courage:  [1, 3, 4, 6, 8, 9, 10, 12]
   ```
2. `phoenix_v4/planning/knob_apply.py::_load_compact_chapter_subset(runtime_format, repo_root)` gains a
   `topic: Optional[str] = None` param: when the format declares `compact_chapter_subset_by_topic` and
   it contains `topic`, return that list; **else fall back to the per-format `compact_chapter_subset`**
   (current behavior). `load_spine` (already has `topic`) passes it through; `compile_beatmap`'s re-load
   passes `shaped_spine.topic`. ~15 lines, single helper — no parallel pipeline.
3. **Invariant:** per-topic list length MUST equal the format's `chapter_count_default` (same gate that
   pins the per-format lists). Add a test mirroring `test_load_spine_compact_8ch_30min_subsets_to_8`.

## Backward-compatibility & anti-drift

- Zero behavior change where no `compact_chapter_subset_by_topic` is declared (every format today).
- Per-format remains the **default and fallback** — the amendment narrows, never replaces.
- Spine YAMLs remain the single source of truth for chapter content; format spec remains SSoT for the
  compact contract. Extends existing canon; no new spec, no new pipeline.
- **Atom-parse adjacency:** any change touching spine subsetting must keep the atoms-parse-sweep CI
  guard GREEN (the #1590→#1635 over-match lesson). Run it before merge.

## Risk: LOW (additive, opt-in, length-gated). Effort: ~½ day Pearl_Dev (helper + 1 test + curation).

## Ratification target — exact `PEARL_ARCHITECT_STATE.md` entry for Pearl_Architect to paste

> ### COMPACT-SUBSET-PER-TOPIC-01 — optional per-topic `compact_chapter_subset_by_topic` (extends PR-D-SPINE-01 + TEMPLATE-UNIVERSAL-01)
> **Status:** _pending operator/Architect decision_.
> **Decision:** per-format `compact_chapter_subset` MAY be overridden per topic via an optional
> `compact_chapter_subset_by_topic` map; per-format stays the default+fallback; length must equal
> `chapter_count_default`. `_load_compact_chapter_subset` gains a `topic` param.
> **Anti-drift:** additive, opt-in, length-gated; per-format default preserved; spine YAML stays content
> SSoT; atoms-parse-sweep guard must stay GREEN.
> **Action items:** Pearl_Dev implements helper+test+curation under a new ws once ratified.

**Next step:** Pearl_Architect reviews; if ratified, opens the cap entry + dispatches the Pearl_Dev ws
(serialized on the hot file). Until then, per-format subsetting (live) is the shipping behavior.
