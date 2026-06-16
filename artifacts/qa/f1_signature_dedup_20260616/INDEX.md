# F1-signature delivery-layer dedup — eliminates the named HOOK/EXERCISE/doctrine clusters (2026-06-16)

**Fix:** `phoenix_v4/rendering/book_renderer.py::_dedup_paragraphs_book_wide`
(`ws_f1_signature_dedup_20260616`). **Follow-on to PR #1632** (enrichment depth-dedup):
closes the residual the #1632 closeout flagged as out-of-scope.

---

## Problem #1632 left

PR #1632 (book-wide fuzzy depth-dedup in `enrichment_select`) cut deep_book_6h F1
228→121 but left the *named* clusters that `diag_hook_injector.py` traced to a
re-stamp path bypassing `_book_seen_bodies`: HOOK **"The task is open"** (×13),
EXERCISE **"Now, I want you to notice"** (×12). Both are **short, dense,
multi-sentence** signatures (24 w / 4 sent / 135 ch and 28 w / 5 sent / 144 ch) that:

1. **escape the book-wide dedupe's 30-word floor** (`_dedup_paragraphs_book_wide`
   exempts < `min_words`=30), and
2. **vary by a trailing clause** (so the exact-fingerprint dedupe misses them; the
   HOOK has 2 distinct fingerprints, the EXERCISE 10).

So they survive `clean_for_delivery` and fire a large F1 cluster.

## Fix

A scoped **F1-signature** pass inside `_dedup_paragraphs_book_wide`, run before the
word-floor exemption, mirroring register_gate's F1 detector:

- **eligibility:** `< 45` words **and** `>= 90` chars **and** `>= 3` sentences — the
  short-dense-multi-sentence "signature" class (hooks / exercises / doctrines). Bulk
  SCENE/STORY content (>= 45 words) is never touched.
- **fuzzy keep=1:** Jaccard `>= 0.55` (== `register_gate.F1_SIMILARITY_THRESHOLD`) so
  trailing-clause variants collapse too.
- toggle: `PHOENIX_F1_SIGNATURE_DEDUPE=0` restores prior behavior.

This is the **delivery-layer backstop**; the root-cause depth re-stamp (rotate the
HOOK across its 88 variants in `apply_depth_pass`) remains a separate enrichment_select
follow-on, but it is co-edited by the live #1590 atom-repair session.

## Before / After — full-12 tiers (gen_z_professionals × anxiety × ahjan, seed leverB_baseline)

True-pre-fix-vs-fixed A/B chain (origin/main → #1632 → +signature dedup), all else identical:

| tier | F1: origin/main → #1632 → **+sig** | "task is open" | "now…notice" | F1_sizes (+sig) |
|------|:--:|:--:|:--:|:--|
| standard_book | 66 → 66 → **54** | 13→13→**1** | — | `{2:54}` |
| extended_book_2h | 72 → 67 → **56** | 3→3→**1** | — | `{2:56}` |
| deep_book_6h | 228 → 121 → **93** | 15→13→**1** | 12→12→**2** | `{2:90, 3:2, 6:1}` |

**deep_book_6h: the size-13 "task is open" cluster and the size-12 "now I want you to
notice" cluster are GONE.** Every F1 cluster on standard/extended is now size-2 (WARN).
The largest remaining deep cluster is **size-6 "Same body. Different door."** — the
`chapter_composer._bridge_within_slot` within-slot bridge (a DIFFERENT subsystem,
leverB / PR #1621), not this fix's scope.

No thinning: deep 59,159 w (>40k floor); standard 23,102 w; extended 25,721 w (all
within ~2% of the #1632 render). Verdict stays HARD_FAIL (F2-only; F1 never gates).

## Tests

`tests/test_book_renderer_f1_signature_dedup.py` (7): identical-collapse, fuzzy
trailing-clause-variant collapse, short-beat NOT removed (no over-removal), bulk
content untouched, flag-off, predicate classification, chapter-heading preservation.
Plus regression-clean: `test_book_renderer*` (25) + `test_book_renderer_dedup` +
`test_book_renderer_clean_for_delivery` (28) + enrichment depth-dedup (9).

## Files

- Fix: `phoenix_v4/rendering/book_renderer.py`
- Test: `tests/test_book_renderer_f1_signature_dedup.py`
- Proof: `SUMMARY.json`, `fixed/<tier>/{book.txt,score.json}`, render harness
  `../f1_depth_dedup_verify_20260615/render_one.py`
