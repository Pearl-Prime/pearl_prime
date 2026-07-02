# Deep-Content Output Verification — are the stories / scenes / exercises actually in the book?

> ## ⛔ CORRECTION (2026-07-03, later same day) — this document's headline conclusion is WRONG
>
> **This audit concluded "rich 3-layer story depth authored for only ~3 cells / 0.4%." That is FALSE.** It measured story depth by **roster-NAME presence** (grepping for Priya/Marcus…) and by counting `character_roster.yaml` files (3). That is the wrong proxy: depth ≠ named-roster.
>
> **Corrected ground truth (content-measured across all 218 STORY pools, `atoms/<persona>/<topic>/STORY/CANONICAL.txt`):**
> - **216 / 218 pools (99%) contain genuine deep 3-layer story content** (multi-sentence character arc + concrete scene + stakes) — 2,792 deep story variants catalog-wide. Depth is authored **across the whole catalog**, with **unnamed** "She/He" protagonists.
> - The name-grep found roster names in only 3 cells → the audit wrongly read "no depth" everywhere else. The deep stories were there; they just don't use proper names.
> - **These deep stories DO render to output post-#4591:** for gz×burnout, 15 of 23 pool variants render verbatim; 9 deep scene-paragraphs in the book.
> - **Real remaining items (all narrow, NOT "author depth from scratch"):** (1) **naming** — 196/218 pools use unnamed protagonists vs the spec's Kenji/Mara/Priya (22 named); (2) **shared-spine + noun-swap quality** — all cells share per-topic story spines persona-adapted by noun substitution, which sometimes misfires ("*The student loans had gone well*"); (3) story **independence/diversity** across personas of the same topic.
>
> Superseded by `CONTENT_HISTORY_FORENSICS_2026-07-03.md` (also corrected) and memory `project_story_depth_mismeasured`. The SCENE and EXERCISE findings below stand; only the STORY "3-cell / 0.4%" claim is retracted.

---

**Author:** Pearl_Architect (OUTPUT + per-cell DEPTH audit — read the rendered books, not the pool)
**Date:** 2026-07-03
**Builds on (do NOT re-run):** #4572 wiring verification (banks present + wired); #4591 cohesion restore (prose flows, ~4–7% F14).
**⚠️ Superseded on STORY-depth by the CORRECTION banner above — depth is 216/218 cells, not 3.**
**Question answered:** cohesion (fixed) is *does the prose flow*. This is the DIFFERENT axis — *are the 3-layer named-character STORIES, the reader-identification SCENES, and the multi-layer EXERCISES actually rendered in the book, per cell?*

---

## TL;DR — the operator's memory is correct, and the gap is AUTHORING, not wiring or a fold regression

- **The depth substrate IS documented, IS wired, and DOES render** — stories, scenes and exercises appear in the output books. Nothing was lost, and the #4591 cohesion fold buried **nothing** (verified).
- **BUT rich, cell-matched, individuated 3-layer character depth is authored for only 3 cells — all anxiety — = 0.4% of 784 arcs (~1.4% of the 218-cell SSOT).** Every other cell renders the STORY slot with **thin / generic / sometimes mismatched** story atoms.
- **Gap class: CATALOG-WIDE AUTHORING of cell-matched 3-layer stories/scenes** (Pearl_Writer / Claude-writes prose, per tier policy) — NOT a code fix, NOT a wiring loss, NOT a composer-selection bug (one minor provenance wrinkle noted below).

This is exactly `docs/...PEAK_REQUIREMENTS_SSOT` Appendix C **G5** ("named-character depth authored for ~3 anxiety rosters, <2% of cells"), now confirmed **at the OUTPUT level**.

---

## The three authored-depth cells (the entire individuated roster)

`SOURCE_OF_TRUTH/story_atoms/` contains exactly **3** character rosters, all anxiety:

| roster file | cell |
|---|---|
| `character_roster.yaml` | anxiety × gen_z_professionals × overwhelm |
| `character_roster_millennial_anxiety.yaml` | anxiety × millennial_* |
| `character_roster_working_parents_anxiety.yaml` | anxiety × working_parents |

`character_roster.yaml` = 22 individuated characters (Priya, Marcus, Maya, Aisha, Jordan, Tariq, Nadia, Sam…) with age / role / situation. **784 master-arc files exist; 3 have an authored roster = 0.4%.**

---

## Three-level verdict — DOCUMENTED / AUTHORED-PER-CELL / RENDERED (with quotes)

### Element 1 — 3-layer STORY (named person + stakes + resolution)

| | DOCUMENTED | AUTHORED-FOR-CELL | RENDERED-IN-OUTPUT |
|---|---|---|---|
| anxiety × gz × overwhelm (roster) | ✅ `HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md` | ✅ 22-char roster | ✅ **RICH** — 8 named chars, scene-embedded |
| burnout × gz × watcher (typical) | ✅ same | ❌ no roster | ⚠️ **THIN** — 3 name-drops, 0 scene-embedded |
| burnout × healthcare_rns × watcher | ✅ same | ❌ no roster | ⚠️ 0 named chars |

**RENDERED quote — anxiety roster cell (rich 3-layer):**
> Priya submits the project update at 11:47pm. It is thorough. She has checked it three times. The Slack confirmation appears immediately… She picks it up again. The update had a typo in the second paragraph. She already knows this.
>
> Marcus scrolls past the LinkedIn notification without opening it… Jess from his cohort got promoted to senior associate. They started the same month… he feels something that is not exactly jealousy and not exactly not jealousy.
>
> [Tariq] drove around the block twice before going inside. His roommate… asked if he was okay. Tariq said yeah, just needed some air… The doctor asks how he's sleeping. Tariq says fine… and the word lands wrong, and he can tell the doctor knows it landed wrong.

→ Named person + concrete scene + stakes + developing resolution. Bestseller-level.

**RENDERED quote — burnout cell (thin / MISMATCHED):**
> Marcus learned, on a Wednesday night, that the cost of closing the laptop was smaller than the cost of not closing it. The learning landed in his body, not in his head.

→ Named, but a compressed teaching abstraction, not a scene.

> Priya overhears a conversation in the break room. One of the **nurses** she thought was managing fine is talking… about cutting back hours.

→ **Provenance wrinkle:** "Priya" in the roster is a *product manager at a SaaS company*; here she is placed among **nurses** in a **gen_z_professionals** book — a generic/mis-sourced story atom with a roster name stapled on. Minor selection issue; the dominant gap is that no cell-matched story was authored to select instead.

**Cross-cell scan (name-in-concrete-scene paragraphs):** anxiety-roster = **4**; all four burnout cells = **0**.

### Element 2 — SCENE (reader-identification situation)

DOCUMENTED (`PEARL_PRIME_SCENE_WIRING_HANDOFF`) ✅ · RENDERED in **both** cells ✅ — chapters open on 2nd-person identification scenes:
> The all-hands started ten minutes ago. You are listening with one ear while you scan the agenda doc. Your camera is off. Your hand is on the mouse but not moving.

Second-person SCENE coverage is broad (not roster-gated). The gap is the **named-character** story layer, not the generic scene layer.

### Element 3 — multi-layer EXERCISE (intro → guide → aha → integration)

DOCUMENTED ✅ (`SOURCE_OF_TRUTH/exercises_v4/`: 11 types, intro + guided_practice + aha_noticing + integration) · WIRED ✅ (exercise-journeys) · RENDERED ✅ with intro + guided layers in **both** cells — NOT stubs:
> Now we're going to do a breath practice. This is a breath-based practice. You are not trying to breathe perfectly or deeply. You are giving your nervous system a rhythm it can follow…

Exercises render across cells (topic-agnostic by design — selected by function, not topic). Integration/affirmation content present ("I am enough, exactly as I am…"). **Exercises are NOT the primary depth gap.**

---

## #4591 cohesion-fold regression check — CLEAN

The fresh fold folds only standalone one-line inject paragraphs (bridges / practice-intros) into neighbors. Verified on the rendered output:
- **STORIES intact** — Priya/Marcus/Tariq are multi-sentence paragraphs, never in the inject set; they render whole after the fold.
- **EXERCISES intact** — the practice-intro folds *into* the exercise intro ("Now we're going to do a breath practice. This is a breath-based practice…"), preserving the layer, not burying it.
- **SCENES intact** — 2nd-person chapter-opening scenes unchanged.

No STORY / scene / exercise was suppressed by #4591.

---

## Gap class + the one closing lever

**Gap class = CATALOG-WIDE AUTHORING (Pearl_Writer / Claude-writes), not code.**

| candidate | verdict |
|---|---|
| wiring loss | ❌ ruled out (#4572; stories/scenes/exercises render) |
| composer selection/routing | ⚠️ minor only — one mis-sourced story atom (Priya/nurses); the composer *does* fill the slot |
| #4591 cohesion-fold regression | ❌ ruled out (verified above) |
| **catalog-wide authoring of cell-matched 3-layer depth** | ✅ **this** — authored for 3/784 cells |

**Depth count (honest):** ~**3 cells** (all anxiety) have rich authored 3-layer character depth; the remaining ~**781 arcs** render the STORY slot with generic/shared/mismatched atoms — cohesive (post-#4591) but shallow on named-character stories.

**The ONE lever:** author cell-matched 3-layer character rosters + story atoms (named person + stakes + resolution) per the `HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC`, catalog-wide (or per selected flagship cells first). This is the same **line-edit / depth-authoring lane** — prose authoring, operator-present, Tier-1 Claude-writes — widened from register to depth. NOT another gate, NOT a composer change.

---

## Reconciliation with the operator's memory

- "It was all documented" — **TRUE**: the story rubric, character-individuation spec, scene-wiring handoff, and exercises_v4 contract all exist.
- "The exemplars exist" — **TRUE**: the 3 anxiety rosters render genuinely deep, bestseller-level named-character stories (quoted above).
- "I keep not seeing it" — **TRUE and explained**: the deep 3-layer content was **authored for ~0.4% of cells**; every other book renders a wired-but-generic STORY slot. Wired ≠ authored-per-cell ≠ the rich version you remember. It was never a loss — it was never authored across the catalog.

## NEXT_ACTION

Depth-authoring lane (Pearl_Writer / Claude-writes), NOT a code fix:
1. **Flagship-first** — author cell-matched rosters + 3-layer story atoms for a handful of flagship cells; render + read to confirm bestseller-level depth carries to output.
2. **Then catalog-widen** — roll the authored-depth pattern across the 218-cell SSOT (or the shipping subset).
Minor code follow-up (separate, low priority): story-atom provenance guard so a mismatched-context story (Priya/nurses) can't be selected into an unrelated persona cell.

## Reproduce

```bash
# CI-ALLOWLIST: legacy-registry-ok — verification render, not a bestseller build (chord flags present below)
python3 scripts/run_pipeline.py --topic anxiety --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml \
  --pipeline-mode spine --quality-profile production --exercise-journeys \
  --no-job-check --skip-quality-gates --render-book --render-dir /tmp/anx
# then read /tmp/anx/book.txt for named-character stories (Priya/Marcus/Tariq)
```
