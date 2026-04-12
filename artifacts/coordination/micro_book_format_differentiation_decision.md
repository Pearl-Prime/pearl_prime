# Micro-book format differentiation — architect decision draft

**Date:** 2026-04-12  
**Owner decision:** pending (Pearl_PM / product owner)  
**Blocked implementation:** `micro_book_20` reader-facing differentiation until one option is approved.

## Authority review

| Source | Finding |
|--------|---------|
| `config/format_selection/format_registry.yaml` | `micro_book_15` and `micro_book_20` differ only in `duration_minutes` (15 vs 20), `word_range` ([2500, 4500] vs [3000, 5500]), and default chapter count is the same (5). No structural or pedagogical delta is declared. |
| `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md` | Format is a compile input; arc governs pacing and reflection sequence. No SKU-level prose contract for 15 vs 20 minutes. |
| `specs/PHOENIX_V4_5_WRITER_SPEC.md` | Uses the umbrella term **micro_book** for several gates (e.g. misfire tax, integration modes); it does not split requirements between 15- and 20-minute runtime SKUs. |
| `config/governance/system_registry.yaml` | No entries defining micro-book reader experience tiers. |

**Conclusion:** This is an **authority gap**: commerce exposes two SKUs with duration/word targets but no specified differentiated reader experience.

## Options (choose one)

### Option A — Deeper reflection prompts

**Definition:** `micro_book_20` = `micro_book_15` spine + **one additional reflection prompt per chapter**, placed at **end-of-chapter** (INTEGRATION-adjacent or explicit REFLECTION block per Writer Spec §7).

**Pros:** Clear listener-visible difference; aligns with “extra five minutes” as contemplation space; minimal change to HOOK/STORY/SCENE counts.  
**Cons:** Requires reflection prompt authoring or template pool per persona × topic; EI/duration gates must allow slightly higher teaching density.

### Option B — Additional story depth per chapter

**Definition:** `micro_book_20` = `micro_book_15` + **one extra story-depth section per chapter** (e.g. second STORY or extended SCENE beat within format k-table), bounded by `word_range`.

**Pros:** Differentiation is narrative/show-not-tell; fits users who buy “longer” for more immersion.  
**Cons:** Stronger load on atom pools and bestseller craft gates; compile/beatmap changes per format.

### Option C — Collapse SKUs

**Definition:** Retain a single micro SKU (e.g. `micro_book_15` only); map `micro_book_20` catalog entries to that runtime or deprecate the ID with a migration note.

**Pros:** No false differentiation; simpler registry and QA.  
**Cons:** Catalog/marketing cleanup; any listings that promise “20 minutes” must be reconciled.

## Pearl_Architect recommendation

**Prefer Option A** until atom pool depth is audited for Option B: end-of-chapter reflection is easy to explain to listeners, matches the duration delta without doubling narrative load, and stays compatible with existing “micro_book” Writer Spec language.

**If** commercial promises already position the 20-minute SKU as “more stories,” revisit **Option B** after a pool coverage check.

---

**Next step:** Owner selects A, B, or C → Pearl_Dev implements under workstream `ws_micro_book_differentiation_20260412`.
