# F1 cross-chapter depth-dedup — independent verification (2026-06-15)

**Fix:** `phoenix_v4/planning/enrichment_select.py` — `ws_f1_depth_dedup_20260615`
(task_48b619ed). **Verifier:** Pearl_Dev (Lever-B out-of-scope follow-up).
**Complements:** Lever-B composer half — `../leverB_20260615/INDEX.md` (PR #1621,
within-slot bridge) + `../../analysis/pearl_prime_priorities/ADAPTIVE_CHAPTER_COUNT_AND_F1_20260615.md` §4.
**Sibling proof (env-flag toggle):** `../f1_depth_dedup_20260615/` (gen_proof.py + SUMMARY_after_fix.json).

---

## TL;DR

The depth pass (`enrichment_select.apply_depth_pass`) re-read atom CANONICAL
blocks **per chapter** using a PER-CHAPTER exact-match `book_seen_bodies` set, so
the same atom body was re-injected across all 12 chapters — the bulk of the
full-12 F1 mass. The fix makes the registry **book-wide AND fuzzy** (Jaccard ≥
0.55, mirroring the register-gate F1 detector) and rotates the depth selector to
an unused sibling ARC block / variant instead of re-stamping.

**Result — deep_book_6h F1 drops 228 → 121 (−107, −47%)**, holding composer /
register_gate / atoms / seed identical across arms. The headline "materially
fewer F1 clusters at full-12" target is **met**. The win is concentrated in the
broad depth re-injection mass (size-2 clusters 207 → 112).

**Honest residual:** the four *named* big clusters the brief called out —
HOOK "The task is open" (14→13), EXERCISE "Just thirty seconds" (12),
"Now, I want you to notice" (10), doctrine "This is The Unspoken" (9) — **persist
essentially untouched**. See "Injector attribution" below: these are NOT depth-pass
re-injections; they enter downstream of `apply_depth_pass`, OUT of this file's scope.

## Method (rigorous true-baseline A/B)

Cell: **gen_z_professionals × anxiety (teacher=ahjan), seed=leverB_baseline**
(the gen_z×anxiety atoms are clean on the working tree — verified 0 dirty — so the
numbers are comparable to ⑤'s leverB authority baseline).

- **prefix** arm = `origin/main` pre-fix `enrichment_select` loaded via an importlib
  shim (`render_one.py`, materialized with `git show` — no working-tree mutation).
- **fixed** arm = working-tree `enrichment_select` (the fix + the two concurrent
  refinements: tunable `PHOENIX_DEPTH_DEDUP_THRESHOLD` + base-content pre-seeding).
- **Everything else identical** across arms (composer, register_gate, atoms, seed),
  so the F1 delta is attributable purely to the `enrichment_select.py` change.

This is stronger than the sibling `gen_proof.py` env-flag baseline, whose
`PHOENIX_DEPTH_DEDUP_FUZZY=0` arm is *fix-with-fuzzy-off* (book-wide registry +
sibling rotation), NOT the legacy per-chapter behaviour. The prefix arm here
reproduces the genuine origin/main baseline (deep F1 = 228 ≈ ⑤'s 224).

Build: `run_all.sh` → `compose_from_enriched_book(quality_profile="draft")`;
scored with `register_gate.evaluate_register(quality_profile="production")`.
Deterministic; NO paid LLM (CLAUDE.md tier policy).

## Before / After — full-12 tiers

| tier | words (pre→fix) | F1 (pre→fix) | Δ F1 | 'task is open' | verdict |
|------|:--:|:--:|:--:|:--:|:--|
| standard_book | 23597 → 23597 | 66 → 66 | **0** | 3 → 3 | HARD_FAIL |
| extended_book_2h | 26148 → 26206 | 72 → 67 | **−5** | 3 → 3 | HARD_FAIL |
| deep_book_6h | 59449 → 61097 | **228 → 121** | **−107 (−47%)** | 15 → 13 | HARD_FAIL |

deep_book_6h F1 cluster-size histogram:
- prefix: `{2:207, 3:12, 4:4, 7:1, 9:1, 10:1, 12:1, 14:1}`
- fixed:  `{2:112, 3:2, 4:2, 6:1, 9:1, 10:1, 12:1, 13:1}`

The −107 is almost entirely the size-2 near-duplicate pairs (207→112) plus
size-3/4 (12→2, 4→2) — the broad cross-chapter depth re-injection the fix targets.
Book is NOT thinned (words +1648; the regression test
`test_depth_dedup_preserves_book_completeness` asserts deep stays >40k words).

Short tiers (standard/extended) barely move because their depth pass does little
cross-chapter re-injection (only ~3 HOOK occurrences vs deep's 15); their F1 is
dominated by other small clusters the depth dedup doesn't own.

## The fix (what it changes)

- `apply_depth_pass`: PER-CHAPTER `_chapter_seen_bodies` dict → ONE book-wide
  `_SeenBodies()` registry shared across all chapters/rounds/passes. **This is the
  core fix** — the per-chapter set never saw what earlier chapters used.
- `_SeenBodies`: set-compatible (`x in reg`, `reg.add(x)` unchanged) + a fuzzy
  layer (`note`/`seen_similar`, Jaccard ≥ threshold) mirroring `register_gate`'s F1
  detector. Bodies < 30 tokens are exempt (short transitions may repeat).
- `_load_depth_content` (+ `_pick_canonical_block_per_section` `reject` predicate):
  every depth source-type (teacher_atom / persona_atom / registry / template /
  phoenix_standard / exercise_atom / exercise_bridge) now rotates deterministically
  off already-used bodies to an unused sibling, falling back to the original pick
  only if every sibling is used (completeness > strict no-repeat).
- Feature-flagged: `PHOENIX_DEPTH_DEDUP_FUZZY=0` → exact-only; `PHOENIX_DEPTH_DEDUP_THRESHOLD` → tune.

## Injector attribution — why the named clusters persist

`diag_hook_injector.py` (fixed code, deep_book_6h) traces the HOOK phrase per stage:

```
base slots (post-select):  'The task is open' ×3
depth slots (post-depth):  'The task is open' ×49      <- depth DOES inject it, heavily
composed prose:            'The task is open' ×13      <- clean_for_delivery cuts 49->13
```

The HOOK **is depth-injected** (3→49 in slots) — NOT composer-injected. But the 13
final occurrences are **12 byte-identical paragraphs** + 1 longer variant (Jaccard
0.71), all from a **single atom**: `atoms/gen_z_professionals/anxiety/HOOK/CANONICAL.txt`.

A book-wide **exact**-match dedup alone would catch 12 identical copies — so this
HOOK injection path **bypasses `_book_seen_bodies` entirely**. It is NOT the
`_pick_canonical_block_per_section` / `_load_depth_content` selector path the fix
instruments (the fix's `_already_used` is never consulted for these re-stamps).
`clean_for_delivery._dedup_repeated_blocks` collapses the 49 slot-copies to ~1 per
chapter, but it is **chapter-scoped + exact**, so the cross-chapter identical copies
survive into prose and fire the size-13 F1 cluster.

**Bottom line:** the task's headline (deep F1 ↓ from 224) is met by deduping the
broad depth re-injection **mass** (the size-2 pairs). The four *named* clusters
(HOOK / "Just thirty seconds" / "Now, I want you to notice" / "This is The Unspoken")
ride a **separate re-stamp path** outside the selectors the fix — and the task's own
prescribed fix-direction ("rotate `_pick_canonical_block_per_section` by book-level
usage") — instrument. The prescribed fix was implemented faithfully; the named HOOK
simply enters by a different door than the diagnosis assumed.

## Verdict note

All tiers stay `HARD_FAIL`. Per ⑤/register_gate, the verdict is **F2-only**
(`_aggregate_verdict`; F1 never reaches HARD_FAIL severity). This is an F1 /
prose-quality lever, not a gate-flip — halving deep F1 is a real craft win but
does not by itself flip the verdict (F2 is owned by atom-repair / #1601).

## NEXT_ACTION

**Ship this fix** — it is a verified, regression-free −47% deep-tier F1 reduction
that faithfully implements the brief's prescribed fix-direction for the depth
SELECTOR layer. It is not sufficient on its own to make the *named* HOOK cluster
disappear, but that target belongs to a different code path:

**Follow-on (close the named-cluster residual):** route the HOOK / persona-atom
**re-stamp path** in `apply_depth_pass` through the same `_already_used` /
`_book_seen_bodies` gate the selector paths use — the 12 copies are byte-identical,
so even non-fuzzy exact dedup suffices once the path is wired. *Alternatively*,
promote `clean_for_delivery._dedup_repeated_blocks` from chapter-scoped to
cross-chapter for byte-identical blocks. Proven locus:
`atoms/gen_z_professionals/anxiety/HOOK/CANONICAL.txt` re-stamped 49× into depth
slots → 13× in prose (`diag_hook_injector.py`). This is a **distinct path** from
this PR's selectors; `enrichment_select.py` is being actively edited by the
#1590 atom-header-repair session — coordinate before touching it again.

## Files

- Fix: `phoenix_v4/planning/enrichment_select.py`
- Regression test: `tests/test_enrichment_depth_dedup_f1.py` (9 tests, all green)
- This proof: `render_one.py`, `aggregate.py`, `run_all.sh`, `diag_hook_injector.py`,
  `SUMMARY.json`, `{prefix,fixed}/<tier>/{book.txt,score.json}`
- Sibling env-flag proof: `../f1_depth_dedup_20260615/gen_proof.py` + `SUMMARY_after_fix.json`
