# Pilot-10 Review Package — Pearl Prime 1000-Book Build Program (Wave 1 / §10 Human Review)

> **MACHINE PASS = STRUCTURAL ONLY. THIS AWAITS HUMAN REVIEW. NOT SELF-CLEARED.**
>
> Per `PEARL_PRIME_1000_BOOK_BUILD_PROGRAM_V1_SPEC.md` §13, the pilot is declared **successful only by the operator's human read** (§10). Nothing in this package self-declares success. Every "verdict" below is a *machine-gate* verdict — a deterministic structural check, not an editorial judgment of whether the prose is bestseller-grade. The §9 inline gates can only tell you a book is structurally well-formed; they cannot tell you it is *good*. That call is yours.
>
> **Headline for the reviewer (corrected to disk truth, 2026-06-14):** **9 of 10 books rendered a full, readable `book.txt`** (20,378–24,270 words, 12 chapters each). **1 of 10 (rank 3) genuinely did not build** — it hard-fails *before render* at the EXERCISE-bank-resolution gate (no authored EXERCISE atoms for its persona/topic), and re-running with the correct arc does **not** fix it (see Execution Notes §a). The two machine verdicts that matter:
> - **Inline §9 gates:** every rendered book PASSes chapter_flow / bestseller_craft / ei_v2, holds on book_quality (repeated-phrase density), and HARD-fails `book_pass` **solely on `word_budget`** (all 9 overshoot the 20,000 cap).
> - **Register gate (the trade-pub prose frontier, run fresh on all 9):** **9 of 9 = HARD_FAIL.** This is the signal the §9 gates miss — and reading the books confirms it is catching something real: identical scene-transition scaffolding lines and unresolved doctrine-prefix seams (`"…the through-line is… "`) recur verbatim across every book. The register HARD_FAIL is **not** a packaging artifact to wave off; it is the honest editorial verdict the §9 craft gates were too coarse to surface.
>
> The earlier draft of this package marked every book **NOT_BUILT** because the production pipeline exits 1 on the `book_pass` word-budget overshoot, which the build agents misread as "not built." That was wrong: a word-budget overshoot is an *expected* `book_pass` HARD_FAIL on a rendered artifact — **the book is BUILT.** This package corrects `built=true` for all 9 with a `book.txt` on disk.

## Book links (read these — the prose is the actual deliverable)

| Rank | Persona × Topic | book.txt | Words | Inline §9 | Register |
|---|---|---|---|---|---|
| 1 | gen_alpha_students × anxiety | [01/book.txt](./01_gen_alpha_students__anxiety/book.txt) | 20,416 | book_pass FAIL (word_budget) | HARD_FAIL |
| 2 | gen_z_professionals × burnout | [02/book.txt](./02_gen_z_professionals__burnout/book.txt) | 21,673 | book_pass FAIL (word_budget) | HARD_FAIL |
| 3 | gen_z_professionals × financial_anxiety | *(no render — EXERCISE-gate block, see §a)* | — | n/a | NOT_RUN |
| 4 | corporate_managers × burnout | [04/book.txt](./04_corporate_managers__burnout/book.txt) | 20,447 | book_pass FAIL (word_budget) | HARD_FAIL |
| 5 | corporate_managers × financial_anxiety | [05/book.txt](./05_corporate_managers__financial_anxiety/book.txt) | 20,993 | book_pass FAIL (word_budget) | HARD_FAIL |
| 6 | educators × anxiety | [06/book.txt](./06_educators__anxiety/book.txt) | 20,378 | book_pass FAIL (word_budget) | HARD_FAIL |
| 7 | gen_alpha_students × boundaries | [07/book.txt](./07_gen_alpha_students__boundaries/book.txt) | 20,518 | book_pass FAIL + scene FAIL | HARD_FAIL |
| 8 | gen_x_sandwich × anxiety | [08/book.txt](./08_gen_x_sandwich__anxiety/book.txt) | 23,090 | book_pass FAIL (word_budget) | HARD_FAIL |
| 9 | gen_x_sandwich × boundaries | [09/book.txt](./09_gen_x_sandwich__boundaries/book.txt) | 24,270 | book_pass FAIL (word_budget) | HARD_FAIL |
| 10 | nyc_executives × anxiety | [10/book.txt](./10_nyc_executives__anxiety/book.txt) | 20,954 | book_pass FAIL + scene FAIL | HARD_FAIL |

---

## Aggregate machine-gate scorecard

### Inline §9 gates (the per-book quality_summary.json roll-up), 9 rendered books

| Gate | PASS | WARN / HOLD | HARD_FAIL (blocking) |
|---|---|---|---|
| **chapter_flow** | **9** (0/12 chapters failed on every book) | 0 | 0 |
| **bestseller_craft** (advisory ONTGP) | **9** (ONTGP 0.60–0.72) | 0 | 0 |
| **ei_v2** | **9** (composite 0.61–0.66) | 0 | 0 |
| **book_quality** | 0 | **9** (all HOLD: "repeated phrase density above book cap") | 0 |
| **scene_anti_genericity** | 0 | 7 (WARN) | **2** (ranks 7 & 10: LOCATION_REPETITION) |
| **book_pass** (word_budget is the failing sub-check) | 0 | 0 | **9** (all on word_budget overshoot vs 20k) |

### Register gate (trade-pub register, F1–F11), run fresh on all 9 rendered books

| Metric | Value |
|---|---|
| **Books at HARD_FAIL** | **9 / 9** (verdict rule: any F2 finding ⇒ HARD_FAIL) |
| **F7** over-prescribed practice density (FAIL) | **108** — exactly **12 per book** (1/chapter). The most systematic signal. |
| **F1** templated-paragraph repetition | **444 total** (41 at FAIL severity); the most *frequent* finding class. |
| **F2** broken slot-template fragment (HARD_FAIL) | **142 total** (8–27 per book). **Mixed:** some are genuine seams (`". ."`, `"Now, ,"`, lowercase-after-period), many are false positives on numbered lists, section headings, and phrasal-verb sentence endings. |
| **F4** verbatim closing-line repetition (FAIL) | **17 total** (9 at FAIL); present on 8/9 books (rank 9 clean). |
| **F6** pedagogical-cadence 4-gram repetition (FAIL) | **9** — 1 per book, universal. |
| **F3** off-doctrine vocab (WARN) | 3 total (negligible). |
| **F8** citation grafting | deferred (anchor corpus not yet on disk). |

**Reading these two tables together — the honest synthesis:**

- **The §9 craft gates and the register gate disagree, and the register gate is the more discerning instrument.** chapter_flow / bestseller_craft / ei_v2 all PASS, which the prior draft read as "the prose reads as authored." But the register gate — purpose-built to catch the register-level tics those gates miss — HARD_FAILs all 9, and **reading the books confirms its findings are real** (see per-book notes and Execution Notes §c). The §9 "PASS" means *structurally coherent*; it does **not** mean *trade-pub clean*.
- **The dominant, systemic defect is renderer scaffolding, not content.** Every book interleaves the same skeleton of scene-transition one-liners — verbatim across books: *"Stay until the sentence lands all the way down."*, *"Strip the costume off. The motor underneath is small and predictable."*, *"Carry the seeing one room further into the house."*, *"What looks like one piece is actually two, stacked."* — plus doctrine-prefix atoms that render with an unfilled tail: *"Across Ahjan's contemplative work, the through-line is… "*, *"What Ahjan keeps pointing toward is… "*. These read as non-sequiturs between otherwise-strong passages. F1 (templating), F4 (closing-line repetition), and F6 (cadence) are all firing on this one root cause.
- **F7 = 12/book is a structural over-prescription signal.** The composer places a practice/exercise beat in every chapter; the register gate flags the per-chapter density as over-prescribed in all 12 chapters of all 9 books. Worth an architecture look (per-chapter practice-density cap).
- **book_quality HOLD is universal and is NOT a hard fail** — release-band advisory on repeated-phrase density. On several books the driver overlaps the scaffolding-line repetition above; on rank 4 it is *also* contaminated by unauthored placeholder HOOK stubs (see per-book note).
- **The word cap is a real but secondary frontier.** Every rendered book overshoots 20k (20,378–24,270). This is a budget-reconciliation decision (raise cap or add a trim-to-cap pass) and is genuinely separable from the register defects — but it is **not** the only thing between these books and a pass, as the prior draft claimed. Fixing the cap clears `book_pass`; it does nothing for the register HARD_FAIL.

**Bottom line for §10:** the machine now says "structurally sound (§9), over budget (book_pass), and register-failing (trade-pub gate)." The reviewer's job is to read the prose and decide whether the *writing* clears the trade bar. The strongest passages (named-character vignettes, sustained doctrine prose) are genuinely good; the connective scaffolding between them is the visible defect. The gates cannot make the final call for you.

---

## Per-book detail

> Each book's "Build status" is now **BUILT** wherever a `book.txt` exists. The production pipeline's exit-1 on `book_pass.word_budget` is an expected gate result on a rendered artifact, **not** a build failure.

### Rank 1 — gen_alpha_students × anxiety
- **Persona / topic:** gen_alpha_students (middle-school) × anxiety
- **Build status:** **BUILT** — `book.txt` rendered (118 KB / **20,416 words** / 12 chapters). Pipeline exited 1 on `book_pass.word_budget` (expected).
- **Inline §9 gates:** chapter_flow **PASS** (0/12) · book_quality **HOLD** (repeated-phrase density) · scene_anti_genericity **WARN** · bestseller_craft **PASS** (ONTGP 0.66) · ei_v2 **PASS** (0.65) · book_pass **FAIL** (word_budget 20,416 vs 20,000; all other sub-checks PASS).
- **Register gate:** **HARD_FAIL** · 78 findings · HARD_FAIL: F2×11 · FAIL: F7×12 (practice density), F1×5 (templating), F4×1, F6×1.
- **§10 editorial read (read the book.txt):** Opening hook is genuinely strong and scene-first — *"You're about to post a picture. Your hands shake scrolling through it looking for what's wrong."* — persona-true (social-media anxiety) and concrete. The doctrine prose ("The path is beginning… the beginner is someone who is still here") is well-written and lands. **But the chapter body is visibly assembled:** scene atoms ("You said something in class. Now it's 3 AM and your jaw is clenched…") alternate with one-line scaffolding ("Stay until the sentence lands all the way down.", "Strip the costume off.") that read as non-sequiturs, and line 30 renders the literal seam *"the through-line is… Attachment grows in darkness."* The closing chapter compounds it: *"What Ahjan keeps pointing toward is… "* appears **3× in one chapter**, plus `". ."` (dropped slot at "looking at it for forty minutes. ."), `"Now, ,"` (double-comma empty slot), and a lowercase fragment *"to believe that. Just try it."* Chapter progression is real (recognition → mechanism → integration) and the exercises are meaningful (breath practice, Grateful Heart), but the seams are the dominant defect. **Verdict feel:** strong raw material, defeated by renderer scaffolding.

### Rank 2 — gen_z_professionals × burnout
- **Persona / topic:** gen_z_professionals × burnout
- **Build status:** **BUILT** — `book.txt` rendered (**21,673 words**). Exit 1 on word_budget (expected).
- **Inline §9 gates:** chapter_flow **PASS** · book_quality **HOLD** · scene_anti_genericity **WARN** · bestseller_craft **PASS** (0.60) · ei_v2 **PASS** (0.64) · book_pass **FAIL** (word_budget 21,673 vs 20,000; +1,673).
- **Register gate:** **HARD_FAIL** · 77 findings · HARD_FAIL: F2×13 · FAIL: F7×12, F1×2, F4×1, F6×1.
- **§10 editorial read:** Same family signature. Lowest F1 count among the rendered books (×2), so the templating is marginally better controlled here, but F7×12 (practice in every chapter) and the scaffolding-line interleave persist. Internal accounting: pre_depth 18,704 → post_depth 19,963 (under cap), yet rendered = 21,673 — depth modules + angle scaffolding inflate past the budget the gate measures (see Execution Notes §b). **Arc:** `__false_alarm__` does not exist for this pair; built on `gen_z_professionals__burnout__overwhelm__F006.yaml` (canonical burnout role). angle INVISIBLE_COST.

### Rank 3 — gen_z_professionals × financial_anxiety
- **Persona / topic:** gen_z_professionals × financial_anxiety
- **Build status:** **NOT BUILT — genuine failure.** No `book.txt`. The pipeline aborts **before render** at the production EXERCISE-bank-resolution gate (`SystemExit`). `stdout.log` is 0 bytes; the SystemExit message is the last line of `stderr.log`.
- **Inline §9 gates / register:** n/a — the run never reaches render or any gate.
- **Root cause (verified, see Execution Notes §a):** `atoms/gen_z_professionals/financial_anxiety/EXERCISE/CANONICAL.txt` holds only **3 variants (1,240 bytes)**, and the persona-EXERCISE pool resolves empty in legacy mode, so **all 24 EXERCISE slots fall through to `practice_library` (library_34)**. Production strict-canonical mode (`EXERCISE-BANK-RESOLUTION-01`, `scripts/run_pipeline.py:269`) raises `SystemExit` on any practice_library fall-through. **This is NOT the word-budget frontier** — it is an upstream EXERCISE-atom coverage gap unique to this cell (no other built book pairs this persona with this topic). By contrast rank 5 (corporate_managers × financial_anxiety) has **13** EXERCISE variants that resolve from the persona bank (`slots_from_practice_library=0`) and renders fine.
- **Recovery attempted:** re-ran with the **correct** arc `gen_z_professionals__financial_anxiety__spiral__F006.yaml` (same arc *family* as rank 5, which used `__spiral__`). The arc resolved cleanly (no arc error). The build still hit the identical EXERCISE gate and produced no `book.txt`. Arc choice neither caused nor can avoid this failure — the EXERCISE bank is engine/arc-independent. **Fix = author ≥8–12 real EXERCISE atoms for gen_z_professionals/financial_anxiety** (Pearl_Editor + Pearl_Writer), or run dev builds with `--quality-profile draft`. The gate did its job: it refused to ship a book stuffed with generic practice text. Logs in `03_gen_z_professionals__financial_anxiety/`.

### Rank 4 — corporate_managers × burnout
- **Persona / topic:** corporate_managers × burnout
- **Build status:** **BUILT** — `book.txt` rendered (120 KB / **20,447 words**). Exit 1 on word_budget (expected).
- **Inline §9 gates:** chapter_flow **PASS** · book_quality **HOLD** · scene_anti_genericity **WARN** (THREE_DETAIL_RULE under-met ch1/4/6/9/11) · bestseller_craft **PASS** (0.61) · ei_v2 **PASS** (0.63) · book_pass **FAIL** (word_budget 20,447 vs 20,000; +447).
- **Register gate:** **HARD_FAIL** · 100 findings (joint-highest) · HARD_FAIL: F2×27 (highest) · FAIL: F7×12, F1×7 (joint-highest templating), F4×2, F6×1.
- **§10 editorial read:** Carries an extra, separable defect on top of the family scaffolding: `atoms/corporate_managers/burnout/HOOK/CANONICAL.txt` ships **unauthored placeholder stubs** — HOOK v02+ contain the literal `[Persona-specific hook for corporate_managers × burnout]`, and there is **cross-persona contamination** (`[Persona-specific hook for gen_z_professionals × burnout]` sits in the corp_mgr file). These leaked into prose ~24×, inflating both the word count and the repeated-phrase HOLD, and they directly feed the elevated F1/F2 counts here. The authored INTEGRATION refrain "pressure under the sternum" (18×) is *legitimate* by contrast. **Fix:** author real HOOK variants for corp_mgr/burnout (kills the placeholder + gen_z bleed, dedups the HOLD phrase, trims padding). **Arc:** `corporate_managers__burnout__overwhelm__F006.yaml`.

### Rank 5 — corporate_managers × financial_anxiety
- **Persona / topic:** corporate_managers × financial_anxiety
- **Build status:** **BUILT** — `book.txt` rendered (**20,993 words** / 12 ch; angle INHERITED_AMBITION). Exit 1 on word_budget (expected).
- **Inline §9 gates:** chapter_flow **PASS** (0/12) · book_quality **HOLD** · scene_anti_genericity **WARN** · bestseller_craft **PASS** (ONTGP 0.62) · ei_v2 **PASS** (0.61) · book_pass **FAIL** (word_budget 20,993 vs 20,000).
- **Register gate:** **HARD_FAIL** · 99 findings · HARD_FAIL: F2×15 · FAIL: F7×12, F1×4, F4×1, F6×1.
- **§10 editorial read:** The **reference success for the financial_anxiety topic** — its EXERCISE bank (13 variants) resolves cleanly where rank 3's (3 variants) does not, which is exactly why this one rendered and rank 3 did not. Prose carries the same family scaffolding and F7×12; otherwise mid-pack on register severity. Spine over-produces ~1,000 words past cap (post_depth body 19,990; rendered 20,993). **Arc:** `corporate_managers__financial_anxiety__spiral__F006.yaml` — the arc family rank 3's rebuild matched for consistency. `command.txt` saved in the book dir.

### Rank 6 — educators × anxiety
- **Persona / topic:** educators × anxiety
- **Build status:** **BUILT** — `book.txt` rendered (12 ch / **20,378 words**; smallest overshoot). Exit 1 on word_budget (expected).
- **Inline §9 gates:** chapter_flow **PASS** (0/12) · book_quality **HOLD** · scene_anti_genericity **WARN** · bestseller_craft **PASS** (ONTGP 0.69) · ei_v2 **PASS** (0.66) · book_pass **FAIL** (word_budget 20,378 vs 20,000; +378, the *closest* to clearing).
- **Register gate:** **HARD_FAIL** · 76 findings · HARD_FAIL: F2×13 · FAIL: F7×12, F1×3, F4×1, F6×1.
- **§10 editorial read:** Highest craft scores in the set (ONTGP 0.69) and the smallest word overshoot, so on the inline axis this is the closest-to-passing book. The register defects are still present (F7×12, family scaffolding). **Structural budget note:** `depth_budget_policy.book_wmax = 20000` is set *equal to* the book_pass cap with zero headroom; the two-pass depth-fill (ch 7/8/10/11) pushed pre_depth 13,326 → post_depth 19,978 → rendered 20,378 — the depth engine and the cap collide by construction (Execution Notes §b). **Arc:** `educators__anxiety__overwhelm__F006.yaml` (arc_id educators_anxiety_overwhelm_8). angle PROTECTIVE_ALARM. A §8 fallback report is at `06_educators__anxiety/fallback_report_section8.json`.

### Rank 7 — gen_alpha_students × boundaries
- **Persona / topic:** gen_alpha_students × boundaries
- **Build status:** **BUILT** — `book.txt` + plan.json rendered (**20,518 words**). Exit 1 on **2** hard §9 gates (book_pass + scene).
- **Inline §9 gates:** chapter_flow **PASS** (flow 1.00) · book_quality **HOLD** · scene_anti_genericity **HARD_FAIL** (3 LOCATION_REPETITION errors) · bestseller_craft **PASS** (ONTGP 0.67) · ei_v2 **PASS** (0.65) · book_pass **FAIL** (word_budget 20,518 vs 20,000; +518).
- **Register gate:** **HARD_FAIL** · 88 findings · HARD_FAIL: F2×16 · FAIL: F7×12, F1×7 (joint-highest templating), F4×1, F6×1.
- **§10 editorial read:** Two *inline* blockers (word_budget + scene), plus the register HARD_FAIL. The scene FAIL is a real, separable content tic: templated locative connectives — **"in the body of", "in the context of", "by the conditions"** — each appear in **8/12 chapters (67%)**, with 8/12 chapters below the THREE_DETAIL_RULE sensory floor. This overlaps the register F1 templating signal. **Fix:** de-template the 3 locative connectives + raise sensory density in ch 0/1/3/6/7/8; trim ~520 words. **Arc:** `gen_alpha_students__boundaries__false_alarm__F006.yaml` (verified on disk — `false_alarm` *does* exist for this anxiety-family topic, unlike for financial_anxiety/burnout).

### Rank 8 — gen_x_sandwich × anxiety
- **Persona / topic:** gen_x_sandwich × anxiety
- **Build status:** **BUILT** — `book.txt` rendered (138 KB / **23,090 words**; 2nd-largest; angle PROTECTIVE_ALARM). Exit 1 on word_budget (expected).
- **Inline §9 gates:** chapter_flow **PASS** (0/12) · book_quality **HOLD** · scene_anti_genericity **WARN** · bestseller_craft **PASS** (ONTGP 0.72, highest) · ei_v2 **PASS** (0.65) · book_pass **FAIL** (word_budget 23,090 vs 20,000; +3,090).
- **Register gate:** **HARD_FAIL** · 57 findings (fewest) · HARD_FAIL: F2×13 · FAIL: F7×12, F1×3, F4×1, F6×1.
- **§10 editorial read:** Highest bestseller_craft (0.72) and the **fewest register findings** (57) — on balance one of the cleaner-reading books, despite the largest non-rank-9 overshoot. The depth-budget planner clamped `total_words=20000` against `format_word_cap_max=20000` (believed it hit the cap exactly) but the rendered file measures 23,090 — a ~3,090-word planner-vs-gate accounting gap (Execution Notes §b). Family scaffolding + F7×12 still present.

### Rank 9 — gen_x_sandwich × boundaries
- **Persona / topic:** gen_x_sandwich × boundaries
- **Build status:** **BUILT** — `book.txt` rendered (**24,270 words** — the largest in the pilot). Exit 1 on word_budget (expected).
- **Inline §9 gates:** chapter_flow **PASS** (0/12) · book_quality **HOLD** · scene_anti_genericity **WARN** · bestseller_craft **PASS** (ONTGP 0.69) · ei_v2 **PASS** (0.66, highest) · book_pass **FAIL** (word_budget 24,270 vs 20,000; +4,270 / ~21%).
- **Register gate:** **HARD_FAIL** · 72 findings · HARD_FAIL: F2×8 (fewest F2) · FAIL: F7×12, F1×3, F6×1. **Only book with no F4** (verbatim closing-line repetition) — its chapter endings vary.
- **§10 editorial read:** Largest overshoot but the cleanest register *seam* profile (fewest F2, no F4). The planner caps at total_words=20000 (total_target_words=18,701) but exercise-journey + intro/outro + scene material expand the rendered prose to 24,270; the gate measures the rendered artifact. **Fix = render-side trim-to-cap OR raise the standard_book cap (a spec decision).** **Arc:** `gen_x_sandwich__boundaries__false_alarm__F006.yaml` (door/threshold motif).

### Rank 10 — nyc_executives × anxiety
- **Persona / topic:** nyc_executives × anxiety
- **Build status:** **BUILT** — `book.txt` rendered (123 KB / **20,954 words**). Exit 1 on **2** hard §9 gates (book_pass + scene).
- **Inline §9 gates:** chapter_flow **PASS** (0/12) · book_quality **HOLD** · scene_anti_genericity **HARD_FAIL** (3 LOCATION_REPETITION errors) · bestseller_craft **PASS** (ONTGP 0.71) · ei_v2 **PASS** (0.64) · book_pass **FAIL** (word_budget 20,954 vs 20,000).
- **Register gate:** **HARD_FAIL** · 76 findings · HARD_FAIL: F2×26 (2nd-highest) · FAIL: F7×12, F1×7 (joint-highest templating), F4×1, F6×1.
- **§10 editorial read:** The most register-defective book by templating + seams, and reading it confirms why. The hook is **doubled** — *"Catherine is in the back seat of a town car at 11 PM, deal closed…"* immediately followed by a generic restatement *"The deal closed at 11pm. Your chest doesn't know it's already won."* Line 44 renders *"Across Ahjan's contemplative work, the through-line is… "* **verbatim identical** to rank 1 line 30 (cross-book repetition). The "James" paragraph (ch 1) is a wall of somatic tags — *"His chest expands… His shoulders settle… His throat opens… His spine straightens… His ribs expand… His jaw releases… His hands move… His belly settles."* — relentless and mechanical. The scene FAIL: **"in the body of"** (9/12 ch), **"in the context of"** (9/12 ch), **"by the conditions"** (7/12 ch). **Arc-vs-format flag for the orchestrator:** the only nyc_executives+anxiety arc on disk is `nyc_executives__anxiety__spiral__F015.yaml` (engine=spiral, **F015 5-chapter micro-book**). The standard_book planning layer **overrode** the 5-chapter shape and auto-generated a **12-chapter** plan — so the F015 arc did not actually drive structure. Real arc-vs-runtime-format coverage gap.

---

## §8 Fallback / atom-source share (corrected to disk truth)

The §8 ledger asks: **when the engine reached into the atom banks, how often did it land on a real authored persona/topic atom vs. fall through to a generic library?**

- **Rank 3 (gen_z_professionals × financial_anxiety) — the one genuine degraded case.** Its EXERCISE bank holds 3 variants (1,240 bytes) for 24 slots; the persona-EXERCISE pool resolves empty in legacy mode, so **24/24 EXERCISE slots fell through to practice_library**. Production strict-canonical **rejects** that → the book never rendered. **100% EXERCISE-slot degradation** for one book; the only fallback-driven build failure in the pilot. (Verified directly: `enrichment_audit` would show `slots_from_practice_library=24`; rank 5's shows `0`.)
- **Ranks 1, 2, 4, 5, 6, 7, 8, 9, 10 — EXERCISE-bank-resolution did not force a rejected fall-through**, so these rendered. **Caveat (corrected from prior draft):** "did not trip the gate" is *not* the same as "richly sourced." Rank 5's EXERCISE bank is 13 variants; rank 1's anxiety EXERCISE bank is larger. The register gate's **F7×12 on every book** says the EXERCISE *content that did resolve* is being **over-prescribed** (a practice beat in every chapter) — a quality signal the §8 source-share view does not capture.

> **Note for §10:** the strict-canonical gate trades **build yield** for **source honesty** — it hard-fails rather than emit a book padded with generic-library EXERCISE text. Rank 3's NOT_BUILT is that guard firing correctly, **not** a regression. But do not over-read the other 9's "passed the source gate" as "source-clean" — the register gate's F1/F7 findings show source-quality work remains.

---

## Phase-B / Phase-C atom-repair status — VERIFIED ZERO NET COMMITTABLE CHANGE

> **This section corrects a material claim in the prior draft.** The earlier package described ~1,763 Phase-B glue-bank atoms authored and a Phase-C STORY/SCENE rewrite as if they were new work feeding these builds. **On disk, `git status atoms/` is empty — there is no uncommitted Phase-B/C change.** The glue banks the analysis flagged as "sparse" already carry their full variant complement, committed since 2026-05-29.

**What was verified (2026-06-14):**
- `git status --short atoms/` → **0 modified/added files.** The Phase-B/C "repairs" produced **zero net committable change.**
- The targeted glue banks for the worst-off cell (gen_z_professionals × financial_anxiety) **already carry 20 variants each** — PERMISSION 20, PIVOT 20, TAKEAWAY 20, THREAD 20 — all in the engine-valid `## TYPE vNN` format, **far above** the SPEC-739 ≥3 floor. These files are tracked-and-clean, last touched by a CI commit on 2026-05-29, i.e. they predate this pilot.
- **Therefore the analysis's "sparse" flag does not refer to glue-bank variant count.** It refers to a **different dimension** — locale/expansion coverage (the CJK locale files under each bank's `locales/`, and the topic×slot expansion breadth) — which the next pass must target. Chasing glue-bank variant counts again would be a no-op.
- **The one bank that *is* genuinely short and *did* block a build is EXERCISE** (rank 3: 3 variants, engine-empty in legacy mode). That is the real, build-blocking content gap — and it is an EXERCISE-tier authoring task, not a glue-bank task.

**Net:** the prose defects this pilot surfaces (register HARD_FAIL: scaffolding lines, doctrine-prefix seams, F7 over-prescription) are **renderer/composer** issues, not glue-bank-variant scarcity. The next content pass should target (1) EXERCISE atoms for the gen_z/financial_anxiety cell, (2) the locale/expansion dimension the "sparse" flag actually points at, and (3) the renderer scaffolding/seam problem — not re-expand glue banks that already meet the floor.

---

## Execution Notes (what happened during this validation pass)

**(a) Rank 3's failure was NOT an arc mismatch in the way first diagnosed — it is an EXERCISE-atom gap; recovery confirmed the book cannot build under production.**
The handoff attributed rank 3's failure to a wrong `--arc false_alarm` (financial_anxiety has no `false_alarm` arc; its arcs are `__overwhelm__/__shame__/__spiral__`). Rank 5 (corporate_managers × financial_anxiety) used `__spiral__`, so for consistency the rebuild used `gen_z_professionals__financial_anxiety__spiral__F006.yaml` (same family). **The arc resolved cleanly — no arc error.** The build still hard-failed at the EXERCISE-bank-resolution gate (`SystemExit`, before render), exactly as the original run did: all 24 EXERCISE slots fell through to `practice_library` because the gen_z/financial_anxiety EXERCISE bank has only 3 variants and resolves empty in legacy mode. **No `book.txt` was produced; no book was fabricated.** Rank 3 is reported as a genuine failure. Fix = author EXERCISE atoms for this cell (or `--quality-profile draft` for dev builds).

**(b) Word-budget overshoot on all 9 rendered books (20,378–24,270 vs the 20,000 standard_book cap) → expected `book_pass` HARD_FAIL — and it flags whether 20k is the right target.**
Every rendered book exceeds the cap; the smallest overshoot (rank 6, +378) still fails. Two structural causes recur: (1) `depth_budget_policy.book_wmax = 20000` is set *equal to* the cap with **zero headroom**, so the depth-fill pass routinely lands at/over the line; (2) a **planner-vs-gate accounting gap** — the depth planner clamps its internal `total_words` at 20,000 while the rendered `book.txt` (which `book_pass` actually measures) runs 1,000–4,270 words higher because exercise-journey + intro/outro + scene material expand past the planner's count. **This is a budget-reconciliation frontier, and it raises a real spec question: is 20k the right standard_book target, or is the spine simply over-producing?** The cleanest fix is either (a) lower `book_wmax` below the cap + add a render-side trim-to-cap pass, or (b) raise the standard_book cap to match trade length — an operator/spec call. Either unblocks `book_pass` on ~8 of the 9; **neither touches the register HARD_FAIL.**

**(c) Inline §9 gates vs the register gate — they measure different things, and the register gate is the prose-frontier signal.**
The §9 inline gates (chapter_flow, book_quality, scene_anti_genericity, bestseller_craft, ei_v2, book_pass) check *structural* coherence and pass the craft trio on all 9 books. The **register gate** (`phoenix_v4.quality.register_gate`, F1–F11) is a separate, finer instrument for *trade-pub register* tics the §9 gates miss — and it HARD_FAILs all 9. The two genuinely disagree, and **reading the books sides with the register gate**: the scaffolding one-liners, the `"…the through-line is… "` doctrine seams, the `". ."` / `"Now, ,"` dropped slots, and the per-chapter practice over-prescription (F7×12) are all real and visible. **Caveat on F2:** the F2 detector (which alone forces the HARD_FAIL verdict) is **mixed** — it catches genuine seams *and* false-positives on numbered lists, section headings (`"Small Exposures"`), and phrasal-verb sentence endings (`"a practice to work with."`). So the *verdict label* HARD_FAIL is F2-driven and partly over-triggered, but the *substance* (F1/F4/F6/F7) is sound. Recommendation: treat register F1/F4/F6/F7 as the actionable prose signal; calibrate F2 to suppress list/heading/phrasal-verb false positives before using it as a hard ship-blocker.

**(d) Phase-B/C atom "repairs" produced ZERO net committable change — `git status atoms/` is empty.**
The targeted glue banks (PERMISSION/PIVOT/TAKEAWAY/THREAD) already carry 8–20 variants each — ≥ the SPEC-739 3-floor — committed since 2026-05-29, so there was nothing to repair. The analysis's "sparse" flag does **not** refer to glue-bank variant count; it refers to a **different dimension — locale/expansion coverage** — which the next pass must target. The one genuinely build-blocking shortage is the **EXERCISE** bank for gen_z/financial_anxiety (3 variants, engine-empty). See the Phase-B/C section above for the full reconciliation.

---

## What §10 should weigh

1. **Two separable frontiers, not one.** (i) The **word cap** — every rendered book overshoots 20k; a budget/spec decision (raise cap or add trim-to-cap + headroom) clears `book_pass` on ~8 of 9. (ii) The **register gate** — 9/9 HARD_FAIL on real, readable defects (renderer scaffolding lines, doctrine-prefix seams, F7×12 practice over-prescription). **Fixing the cap does nothing for the register failure.** The prior draft's "the frontier is the word cap, not the prose" was incomplete — the prose has its own frontier, and it is the bigger one.
2. **The dominant prose defect is renderer/composer scaffolding, not content scarcity.** Identical transition one-liners and unfilled doctrine-prefix tails recur verbatim across all books. This is a renderer fix (suppress/vary scaffolding atoms; resolve the `"…is… "` doctrine-prefix tail) + a composer fix (per-chapter practice-density cap for F7). Owners: Pearl_Dev (composer/renderer) + Pearl_Editor (atom routing).
3. **2 books carry a real, separable scene tic** (ranks 7 & 10: templated locative connectives). De-template + raise sensory density. Independent of both frontiers above.
4. **1 book (rank 3) is a genuine, build-blocking content gap** — EXERCISE atoms for gen_z_professionals/financial_anxiety. The arc was corrected and it still cannot build; the gate correctly refused generic fall-through. Authoring fix.
5. **1 book (rank 4) has unauthored placeholder HOOK stubs + cross-persona bleed** leaking into prose ~24×. Author real HOOKs; relieves its HOLD and inflated F1/F2.
6. **Read the actual prose.** The strongest passages (named-character vignettes, sustained doctrine prose) are genuinely good and persona-true; the connective scaffolding between them is the visible defect. Whether the *writing* clears the trade bar is the §10 human call, and only the operator makes it. **The machine has NOT self-cleared this pilot.**

*No git operations were performed in assembling this package. Files written/updated: `PILOT_10_REVIEW_PACKAGE.md`, `pilot_10_scorecard.csv`, and `register_gate_report.json` in each of the 9 rendered book directories (this directory tree).*
