# Adaptive Chapter-Count & F1 Register-Repetition — Analysis (2026-06-15)

**Author:** Pearl_Prime · **Project:** proj_pearl_prime_bestseller_rebase_20260425
(composer-frontier thread) · **Extends:** `COMPOSER_FRONTIER_FIX_SPEC_20260614.md`

**Thesis (operator):** *fewer chapters for shorter books* is the primary lever for F1
register-repetition. **Verdict: confirmed and quantified.** Honoring the already-ratified
per-format `compact_chapter_subset` cuts F1 by 37–65% and roughly halves word-overshoot, via a
two-line bug fix. Evidence: [`../../qa/duration_ladder_subset_proof_20260615/INDEX.md`](../../qa/duration_ladder_subset_proof_20260615/INDEX.md).

---

## 1. F1 root-cause — quantified

### 1a. What F1 measures
`register_gate._detect_f1_templated_paragraphs`: pairwise Jaccard ≥ 0.55 over paragraphs of
≥ 3 sentences, **across all chapters**. Comparison cost is O(paragraphs²); the **finding count**
is the number of near-duplicate *clusters*. Cluster size 2 = `WARN`, 3+ = `FAIL`. **F1 never
produces a `HARD_FAIL` severity → it never gates the verdict** (the verdict is F2-only).

### 1b. Two independent axes drive F1
From the published 8-tier ladder (chapters pinned at 12, words growing 7×):

| tier | words | F1 | cluster sizes (size:count) | max cross-ch span |
|------|------:|---:|---|---:|
| micro_book_15 | 7193 | 14 | 2:12, 3:1, 5:1 | 5 |
| short_book_30 | 10561 | 30 | 2:25, 3:1, 4:2, 5:1, 7:1 | 8 |
| one_hour_book | 12780 | 34 | 2:27, 3:1, 4:2, 5:2, 6:1, 9:1 | 11 |
| standard_book | 22155 | 57 | 2:50, 3:1, 4:2, 5:3, 6:1 | 11 |
| extended_book_2h | 22283 | 54 | 2:47, 3:1, 4:2, 5:3, 6:1 | 11 |
| deep_book_4h | 35077 | 111 | 2:101, 4:3, 5:4, 6:1, **14:1** | 11 |
| deep_book_6h | 51709 | 191 | 2:175, 4:6, **10:1, 13:1, 14:2** | 11 |

- **Axis 1 — length** (this table): F1 14→191 as words grow at fixed 12 chapters. Length adds
  paragraphs → more clusters. (The brief's "14→191" is this axis, **not** chapter count.)
- **Axis 2 — chapter count** (the proof run, fixed word target): F1 falls 37–65% when chapters
  drop 12→5/8. Fewer chapters = fewer cross-chapter recurrences of the same scaffolding.

The lever in this session attacks **Axis 2**. (Lever B — see §4 — attacks the scaffolding
itself, helping both axes.)

### 1c. Which scaffolding drives the clusters (deep_book_6h, largest clusters)
F1 is a **true positive** — real cross-chapter scaffolding, not gate noise. The biggest clusters:

| size | chapters | family | excerpt |
|---:|---|---|---|
| 14 | **all 12** | HOOK / opening | "The task is open. You have been looking at it for forty minutes…" |
| 14 | 1,5,6,7,8 | EXERCISE framing | "Just thirty seconds. Not to fix anything…" |
| 13 | 1,5,6,7,8 | EXERCISE framing | "Now, I want you to notice something. Notice what came up first…" |
| 10 | 1,5,6,7,8 | TEACHER_DOCTRINE prefix | "This is The Unspoken. Notice. Do not analyze…" |
| 6 | 2,3,6,7,8,9 | doctrine closer | "You are not on the way to becoming. You are already here…" |
| 6 | 2,4,6,7,10,12 | inter-chapter transition | "Same body. Different door. Watch what changes." |

Families: **HOOK openings, EXERCISE/practice framing, TEACHER_DOCTRINE prefixes/closers,
inter-chapter transitions/bridges** — exactly the elements named in
`COMPOSER_FRONTIER_FIX_SPEC` DEFECT 1 (verbatim cross-chapter bridges), DEFECT 2 (doctrine-tail
orphans), DEFECT 3 (HOOK stubs). Each chapter is a fresh opportunity for these to recur ⇒
chapter count is a structural multiplier on F1.

---

## 2. Book-structure analysis — chapter-count × duration tier

### Current (broken) behavior
`apply_knobs` sets `per_chapter = word_target / chapter_count`. With chapters pinned at 12, the
short tiers divide a small target across 12 chapters; atoms have minimum render sizes, so each
chapter overshoots its tiny per-slot budget and the book overshoots badly (micro +60%).

### Proposed (fixed) behavior — the proof
Honoring the declared subset gives fewer, richer chapters: `per_chapter` rises, atoms fit their
budget, the book lands closer to range, and cross-chapter scaffolding recurs fewer times.

| format | before | after | F1 | overshoot |
|--------|:--:|:--:|:--:|:--:|
| compact_book_5ch_15min | 12ch/7106w | 5ch/5396w | 17 → **6** | +58% → **+20%** |
| compact_book_5ch_20min | 12ch/8138w | 5ch/7494w | 17 → **9** | +48% → **+36%** |
| compact_book_8ch_30min | 12ch/10751w | 8ch/9352w | 35 → **22** | +43% → **+25%** |

**Residual:** even 5 chapters overshoot the tightest band (5ch_15min still +20%) — the atom
floor sets a practical minimum book length. Closing that last gap is a depth-budget / atom-trim
question, not a chapter-count one. Logged, not solved here.

---

## 3. Structure universality & subsettability (15 topic spines)

- **Positions are NOT universal:** only **2/12** chapter positions share a role across all 15
  topics (ch1=`recognition`, ch12=`integration`); the other 10 vary. So the per-format subset
  is topic-blind by *position*, and the *roles* it keeps differ by topic.
- **But every topic subsets coherently:** at the 5ch positions `[1,4,7,10,12]` and the 8ch
  positions `[1,3,4,6,7,9,10,12]`, **all 15 topics yield fully distinct roles** (5/5 and 8/8),
  always spanning `recognition → … → integration`. No topic collapses to duplicate beats.

**Implication:** per-format positional subsetting is **correct-enough to ship for every topic**
(an internally coherent compressed arc), which is why the bug fix is safe beyond anxiety.
Choosing *the optimal* beats per topic (e.g. always keep that topic's load-bearing practice
beat) is an **optimization** = a per-topic subset = a **new vocabulary axis** beyond per-format.
That contradicts PR-D-SPINE-01 (per-format; rejected per-topic P2) + TEMPLATE-UNIVERSAL-01
(chapter_count per-format) ⇒ deferred to a drafted cap amendment (§5), **not** required for the
fix.

---

## 4. Atom analysis — does the catalog support "deep"?

Source: `scripts/inventory/atom_coverage_audit.py` → `artifacts/inventory/atom_coverage_report.md`.

- **Live catalog = 4 topics × 13 personas = 52 combos, 100% complete** (anxiety,
  financial_anxiety, sleep_anxiety, social_anxiety). The other 11 spines exist but are not in the
  live persona×topic catalog yet.
- Banks are healthy (~20 variants/slot per the pilot findings). **Atom depth supports fewer,
  richer chapters** — fewer chapters draw *more* atoms per slot, well within bank depth.
- **EXERCISE is the one thin slot** (render logs show EXERCISE→`library_34` fallbacks;
  `gen_z_professionals × financial_anxiety` EXERCISE bank is the known shortage,
  `COMPOSER_FRONTIER_FIX_SPEC` DEFECT 5). **Fewer chapters *relieve* this** — fewer EXERCISE
  slots to fill — so SHORT&DEEP is *strictly better* for EXERCISE-thin cells.
- **`midlife_women`:** atoms complete, but **zero `master_arcs`** → excluded from the
  arc/angle/catalog path (spine-path render still works; not catalog-buildable until arcs land).

---

## 5. THE MATRIX — SHORT&DEEP / SHORT&FAST / FULL-ONLY at short tiers

Discriminators tested: (i) arc subsettability — **uniform PASS** (§3); (ii) atom depth —
**uniform PASS** for the 52 live combos (§4). Neither is a discriminator, so the structural
recommendation is uniform; the tag below is therefore driven by the **F1/Lever-B state**, which
is the real gate on SHORT&FAST.

| classification | which cells | why |
|---|---|---|
| **SHORT & DEEP** (recommended) | **all 52 live** persona × {anxiety, financial_anxiety, sleep_anxiety, social_anxiety} at micro/short/one-hour tiers | arc subsets cleanly; atoms deep enough; cuts F1 37–65% **now**, no composer change. EXERCISE-thin cells benefit most. |
| **SHORT & FAST** (not recommended yet) | none, until Lever B | keeping 12 thin chapters holds F1 high (proven: 12ch = 2–3× the F1 of the subset). Only revisit per-cell **after** the bridge workstream lands scaffolding variety. |
| **FULL-ONLY** | none structurally forced | every live topic compresses coherently. (Caveat: `midlife_women` is arc-path-excluded for *all* tiers until master_arcs exist — orthogonal to chapter count.) |

**Bottom line:** at short tiers, **SHORT&DEEP wins everywhere in the live catalog.** SHORT&FAST
is a Lever-B-gated future option, not a current shipping choice. The remaining decision is a
**product** one (does the operator want the *default* short tiers — micro/short/one-hour — to
ship fewer chapters, or keep them 12-thin and route short-duration requests to the `compact_*`
formats?) — see the spec extension and the open decision in the closeout. This decision is
**in-envelope either way** (per-format), so it needs operator product sign-off, not Architect
ratification.

---

## 6. Two-lever F1 framing (for the spec)

- **Lever A — fewer chapters (this session, SHIPPED):** the 2-line subset fix. Cuts F1 (Axis 2)
  + word-overshoot + F7. Does **not** flip the gate (F2-driven).
- **Lever B — scaffolding variety (bridge workstream `ws_bridge_transition_system_20260416`):**
  make HOOK/doctrine/transition/bridge text vary by chapter so repeats stop clustering. Cuts F1
  on **both** axes and is the prerequisite for any future SHORT&FAST cell. **Spec it; do not edit
  the bridge banks here.**
- **Gate PASS is a third lane:** F2 (atom-label corruption + teacher-wrapper templates) owned by
  **#1601** + atom-repair. Neither Lever A nor B flips HARD_FAIL alone.
