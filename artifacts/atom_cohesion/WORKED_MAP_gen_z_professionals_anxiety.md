# WORKED_MAP — gen_z_professionals × anxiety

**Author:** Pearl_Editor · **Chunk A of 5** · **Date:** 2026-06-16
**Method:** hand-judged atom→atom adjacency over the **real** rendered slot-sequence, cross-checked against the cluster's `editorial_report.json` / `chapter_flow_report.json` findings and an EI v2 `emotion_arc_validator` reading. READ-ONLY; no atom edits.
**Ground-truth render:** `artifacts/pearl_prime/standard_book/ahjan_gen_z_professionals_anxiety_en_US_20260518T011019Z/` (standard_book, spine pipeline, 12 ch).

---

## 1. Cluster atom inventory (variant counts, `## ` headers)

Read across **all** slot types present in `atoms/gen_z_professionals/anxiety/`:

| Slot type | Variants | Latent cohesion tag carried | Notes |
|---|---:|---|---|
| HOOK | 88 | — none | richest bank; opening-move varies wildly (scene / aphorism / direct-address) |
| SCENE | 82 | — none | |
| PIVOT | 49 | — none | |
| REFLECTION | 44 | **`family: F1-F5`** (29 files) | family = de-dup label, NOT transition tag |
| STORY | 43 | — none | (+ angle sub-banks below) |
| INTEGRATION | 35 | — none | contains position-presupposing openers ("Seven chapters in…") |
| COMPRESSION | 30 | **`compression_family: C1-C5`** (30 files) | family = de-dup label, NOT transition tag |
| EXERCISE | 30 | — none | |
| PERMISSION | 20 | — none | |
| TAKEAWAY | 20 | — none | |
| THREAD | 20 | — none | |
| TEACHER_DOCTRINE | 5 | — none | abstract/aphoristic register (clash risk) |
| PERMISSION_GRANT | 1 | — none | |
| ANGLE sub-banks: comparison / false_alarm / grief / overwhelm / shame / spiral / watcher | 26-28 each | — none | STORY angle pools |
| ANGLE_DEFINITION / ANGLE_CALLBACK / TEACHER_DOCTRINE_INTRO | (ENGINE/dir) | — none | |
| **Total** | **660** | only 2 of 22 dirs tagged | **20 of 22 slot dirs carry NO cohesion metadata at all** |

**Key inventory finding:** the only pre-existing "family" metadata is `compression_family` (COMPRESSION only) and `family` (REFLECTION only). Both are **repetition-decay** labels (single-use per book), not adjacency/transition labels, and the other 20 slot types are tag-naked. So the selector has *nothing* to reason about flow with even where tags exist. (Inventory via header grep, not the stale gap_matrix TSV; consistent with `scripts/inventory/atom_coverage_audit.py`.)

---

## 2. Real chapter-1 slot sequence (from the selection trace)

From `selected_content_variants.json` (ch1), in render order:

| # | slot_type | atom_id | words | rendered at |
|---:|---|---|---:|---|
| 1 | HOOK | `HOOK v32` | 107 | book.txt:3 |
| 2 | STORY | `…recognition:overwhelm:v03` | 92 | (Priya scene fragments) |
| 3 | REFLECTION | `REFLECTION v17` | 330 | |
| 4 | EXERCISE | `ahjan_EXERCISE_003_mined` | 87 | book.txt:27 |
| 5 | STORY | `…mechanism_proof:overwhelm:v05` | 81 | |
| 6 | TEACHER_DOCTRINE | `TEACHER_DOCTRINE v01` | 297 | book.txt:10 |
| 7 | REFLECTION | `REFLECTION v31` | 281 | |
| 8 | EXERCISE | `ahjan_EXERCISE_013_mined` | 90 | |
| 9 | STORY | `…turning_point:overwhelm:v08` | 130 | book.txt:33-35 |
| 10 | INTEGRATION | `INTEGRATION v29` | 283 | book.txt:31 ("Seven chapters in…") |

> Note the renderer interleaves the wrapper/compression furniture, so on the page the order around lines 3-15 reads HOOK → COMPRESSION-furniture → **broken wrapper tail** → TEACHER_DOCTRINE → REFLECTION fragments. The seams analyzed below are the ones a reader actually hits.

---

## 3. Adjacency verdicts (FLOW vs JAR), with excerpts

Legend: ✅ FLOW (smooth hand-off) · ⚠️ SOFT-JAR (register/temperature wobble) · ❌ HARD-JAR (reader-visible gear-grind).

### §A — ❌ HARD-JAR: COMPRESSION → (broken wrapper) → TEACHER_DOCTRINE  `book.txt:6→8→10`
```
6 | The calendar says productive. Your body is running something else entirely.   ← COMPRESSION: tight present-2nd-person, somatic
8 | In Ahjan's framework, the path begins with.                                   ← WRAPPER TAIL: dangling-prep fragment (no closing move)
10| Attachment grows in darkness. When you look directly at what you hold tight…  ← TEACHER_DOCTRINE: abstract 3rd-person aphorism
```
**Why it jars:** three registers collide in 5 lines with no transition. Closing move of (6) is a punchy somatic declarative; opening move of (10) is a contemplative universal aphorism — the reader is yanked from *their own chest at 10pm* to *a metaphysics of attachment* with a broken sentence (8) wedged between. Emotional temperature: (6) cool-activated → (10) detached-neutral, a flat seam where the reader expected the doctrine to *land on* the body the compression just named.
**Cross-check:** `editorial_report.json` ch2+ `hook_friction: FAIL`; `chapter_flow_report.json` `monotone_pacing` + transition findings; the wrapper tail recurs **8×** book-wide. **This is the fully-worked JAR pair in SCHEMA.md §7.2.**

### §B — ✅ FLOW: STORY(turning_point) → INTEGRATION body  `book.txt:33→35`
```
33| The pattern is this. The 2 a.m. spiral was never about the Slack message…    ← STORY/INTEGRATION: 2nd-person, naming the mechanism
35| What changes at this point is the relationship. You stop negotiating with the alarm…  ← continuation, same register
```
**Why it flows:** opening move of (35) — "**What changes at this point** is…" — is a *continuation move* that explicitly picks up the thread (35) inherits from (33)'s "The pattern is this." Same person (2nd), same tense (present), same register (intimate-analytic), monotonically rising valence (recognition → agency). The hand-off is seamless. **This is the fully-worked FLOW pair in SCHEMA.md §7.1.**

### §C — ❌ HARD-JAR: STORY(turning_point) ch1 slot 9 ↔ INTEGRATION `v29` ch1 slot 10  (position mismatch)
`INTEGRATION v29` opens "**Seven chapters in**, I want you to notice what has quietly shifted" — selected into **chapter 1**. Its opening move presupposes mid-book position; placed at the front it is incoherent regardless of what precedes it. Pure isolation artifact (thesis-overlap ranked it #1; opening-move never gated vs chapter index). The atom's *body* would FLOW from §B's run — but its *opener* HARD-JARs with book position.

### §D — ⚠️ SOFT-JAR: REFLECTION → EXERCISE  `book.txt:13-25 → 27`
The REFLECTION block ("The mechanism I want to name is hypervigilance…") is dense clinical-explanatory; the EXERCISE ("Notice a thought that repeats itself…") shifts abruptly to imperative-instructional with no bridging cue. Same person (2nd), compatible temperature, but the *move* jumps explain→instruct without a permission/transition beat. Tolerable but choppy; a one-line bridge or a closing-move=`invites_practice` tag on the REFLECTION would smooth it.

### §E — ✅ FLOW: HOOK v32 → STORY(recognition)  `book.txt:3 → Priya scene`
HOOK v32 closes on the body ("waiting for the catch"); the recognition STORY opens on a concrete scene of the same felt state. Opening-move(scene) lands the abstract recognition the HOOK raised — register shifts (direct-address → 3rd-person vignette) but *purposefully*, which reads as craft, not whiplash, because the emotional temperature is continuous and the vignette is *evidence for* the hook's claim. (Contrast §A, where the register shift carries no such payoff.)

---

## 4. Pattern extracted (feeds SCHEMA.md)

The hand-judgments reduce to a small set of **adjacency predictors**:

1. **Opening-move ↔ preceding closing-move compatibility** is the dominant signal. FLOW pairs share a *continuation* relationship (closing="names pattern" → opening="what changes / continues"); JAR pairs put an *independent-start* or *position-presupposing* opener after an unrelated close (§A, §C).
2. **Register continuity** — intimate-2nd-person ↔ abstract-aphorism is the worst clash in this cluster (§A); intimate ↔ scene-vignette is *fine* when emotionally continuous (§E). So register is a **soft compatibility matrix**, not a hard equality.
3. **Emotional-temperature continuity** — flat/whiplash seams read worse than monotonic ones; this is exactly what `emotion_arc_validator`'s valence trajectory already scores (post-render). Bring it forward.
4. **Position-validity** — some openers ("Seven chapters in") are only legal in a sub-range of chapters (§C). A `position_affinity` tag gates this.
5. **Completeness of closing move** — a closing move that is a broken/dangling fragment (the wrapper tail, §A line 8) can never be a valid predecessor; it must be flagged so it is never a hand-off point.

These five become the per-atom tags + the pairwise compatibility rules in **SCHEMA.md**.

---

## 5. EI v2 cross-check (emotion_arc_validator)

Running the cluster book mentally through `emotion_arc_validator.validate_emotion_arc` (lexicon mode, `emotion_arc_validator.py:112`): chapter 1's valence trajectory is **non-monotonic** — the COMPRESSION→DOCTRINE seam (§A) drops to detached-neutral (DOCTRINE has near-zero valence words) between two activated passages, and the `valence_variance` low-flatness check (`:198-201`) is the same monotonicity the live `ei_v2_report.json` already flags ×12. The validator's `_ROLE_VALENCE_EXPECTATIONS` (`:82-87`) confirms an INTEGRATION-role atom is *expected to end positive* (agency) — `INTEGRATION v29` does, but its **opener** is the defect, which a valence model alone won't catch: that is why SCHEMA.md adds an explicit `opening_move` tag rather than relying on valence alone.

**Takeaway for the schema:** EI v2 already owns (a) the **pairwise text-vs-text** scorer (`cross_encoder_reranker`) and (b) the **cross-chapter valence trajectory** (`emotion_arc_validator`). The schema's job is to give those two consumers *structured per-atom tags* (opening/closing-move, register, temperature, position) so the adjacency decision can be made **at selection time** instead of detected after render.
