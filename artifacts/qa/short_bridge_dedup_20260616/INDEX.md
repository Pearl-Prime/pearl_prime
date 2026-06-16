# Terse within-slot bridge re-stamp dedup (2026-06-16)

**Fix:** `phoenix_v4/rendering/book_renderer.py::_dedup_paragraphs_book_wide`
(`ws_short_bridge_dedup_20260616`). **Follow-on to PR #1644.** Eliminates the
residual size-5/6 **"Same body. Different door. Watch what changes."** F1 cluster.

---

## Root cause (instrument-proven, not a selection bug)

Instrumenting `_bridge_within_slot` across a real deep render (`_diag_bridge.py`,
276 STORY bridge calls) showed the selector is **already optimal**: it draws
**49 distinct** bridge variants uniformly (TLS rotation state present on every
call). "Same body. Different door." is chosen ~6× — exactly the statistical mean
of **276 within-STORY bridge insertions ÷ 49 bank variants** (pigeonhole). So no
selector change can drop it below ~5-6; it is a **bank-capacity** limit, and the
49 variants are mutually similar (all `scene_vignette` "same/different/watch"
phrasings) so they also pair up under F1.

The re-stamp survives every existing dedupe: it is too short (< 30 words) for the
exact book-wide dedupe, too short (46 chars, < 90) for the #1644 fuzzy F1-signature
pass, and (3 short sentences) escapes the "< 3 sentences" beat exemption.

## Fix

A delivery-layer backstop in `_dedup_paragraphs_book_wide`: a paragraph that packs
**>= 3 sentences into < 90 chars** is a formulaic transition bridge, not narrative
prose (real 3-sentence paragraphs are far longer). Such terse multi-sentence EXACT
cross-chapter repeats are spurious bridge re-stamps → **EXACT keep=1**. Toggle
`PHOENIX_F1_SIGNATURE_DEDUPE=0`.

## Proof (deep_book_6h render; deterministic, no paid LLM)

`_dedup_paragraphs_book_wide` applied to the rendered manuscript (this IS what
`clean_for_delivery` does):

| | F1 | F1_sizes | "Same body" | words |
|---|--:|---|--:|--:|
| before | 93 | `{2:90, 3:2, 5:1}` | 5 | 59,193 |
| **after** | **92** | **`{2:90, 3:2}`** | **1** | 59,165 |

**The size-5 cluster is gone; the largest F1 cluster is now size-3.** Only **4**
paragraphs removed (the 4 surplus "Same body" re-stamps, −28 words) — **zero
collateral**, surgical. Cumulative deep histogram vs origin/main:
`{2:207,3:12,4:4,7,9,10,12,14}` → `{2:90, 3:2}` (no cluster > 3).

Verdict stays HARD_FAIL (F1 never gates; F2-only).

## Note — what was NOT shipped

A `chapter_composer._bridge_within_slot` cross-bucket **widening** was prototyped
(makes selection uniform/varied) but is **F1-neutral** (selection was already
optimal, per the instrument) and was dropped: `chapter_composer.py` had advanced on
origin/main (a `bridge_bank` fix) so the prototype sat on a stale base. The true
F1 lever for the bridge tail is **growing the STORY bridge bank** (49 → ~150
distinct variants), a separate data/content task. `book_renderer.py` is also being
concurrently extended (an uncommitted `_f1_longpara` backstop for the >= 45-word
class) — this fix was committed via object-DB plumbing off origin/main so it does
not touch that work.

## Files

- Fix: `phoenix_v4/rendering/book_renderer.py`
- Test: `tests/test_book_renderer_short_bridge_dedup.py` (5)
