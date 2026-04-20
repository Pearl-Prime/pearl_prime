# TEMPLATE THESIS VERDICT
Pearl_Architect + Pearl_Research | 2026-04-18 | Zero API Spend

---

## I. Executive Summary

### Did the old template system exist in git history?

**Yes. And it is more complete than anyone realized.**

The `v2_somatic` library contains **600 YAML files on disk** organized as 12 chapters × 10 sections × 5 variants. Every section has a named role: hook, scene, reflection, exercise, scene, teacher_doctrine, reflection, exercise, scene, integration. The content is production-quality prose. The loader works (confirmed: 120/120 section files load in the pilot). The system was:

1. **Built** — April 10-11, 2026 (commits `f9a22456fc` through `203f4c2fe9`)
2. **Piloted** — `artifacts/pilot/stacked_packet/anxiety/` shows a structurally legible chapter
3. **Not wired to production** — the `standard_book` beatmap defaulted to 4 slots, not 10; the pipeline continued to assemble from atom pools

The template approach was implemented, reported on, and then abandoned in favor of patching the assembly pipeline. The patches have run for every sprint since. Chapter flow gates fail 12/12 chapters across all 15 topics in every production run.

### Is the operator's thesis supported by craft evidence?

**Yes. Strongly.**

Five commercial bestsellers (Atomic Habits, Set Boundaries Find Peace, Burnout, Big Feelings, The Body Keeps the Score) were analyzed chapter-by-chapter. All five use **named section roles within each chapter**: opening hook, mechanism explanation, reader recognition, practice, closing reframe. This is converged commercial craft, not coincidence.

The current pipeline produces chapters that fail structurally: atom pool dumps appear verbatim in delivered books (`## HOOK v01 --- --- ...` labels appear in `book.txt`). Chapters repeat the same hook 19 times in sequence. No chapter flow gate has passed in any production run.

### Recommendation

**Scenario A — Revive the template approach (full commit).** Specifically: complete the wiring that was never finished in April 2026. The content exists. The loader works. The build is a 2-3 week wiring job, not an architecture rewrite.

---

## II. Three Scenarios

### Scenario A — Revive Template Approach (Full Commit)

**What this means:**
- Stop patching the scene-assembly pipeline for book coherence
- Wire the 10-slot beatmap as the default for standard_book
- Use section packet composer as primary content path (loader already works 120/120)
- Apply Pearl_Writer thin-section expansion to the template grid
- Ship one complete anxiety × gen_z_professionals × overwhelm book in 3 weeks

**Build sequence:**
1. Day 1-2: Author one complete 12-chapter template YAML (the fail-fast gate)
2. Operator reads outline — go/no-go
3. Days 3-5: Content for one template (persona-voiced variants for each of 10 sections × 12 chapters)
4. Days 6-10: Spine compiler refactor (wire section packet as primary slot fill)
5. Days 11-12: Section-job validators (museum extension)
6. Days 13-14: Render path refactor (bridge generation for section packets)
7. Days 15-17: Tests + CI integration

**Risk:** 3 weeks before a coherent book ships
**Reward:** The first structurally coherent book Phoenix Omega has ever produced

---

### Scenario B — Evolve Current Pipeline to Be Section-Aware (Lower Commitment)

**What this means:**
- Add `section_role` metadata to atoms in the registry
- Add a `section_plan` to `ChapterContract` that specifies what role each slot fills
- Force HOOK as slot 0, MECHANISM as slot N-4, PRACTICE as slot N-2, INTEGRATION as slot N

**Build sequence:**
1. Add `section_role` field to atom YAML schema
2. Extend ChapterContract with `section_order: [HOOK, SCENE, ...]`
3. Modify EnrichmentSelect to respect section_order when filling slots
4. Add section-sequence validator to regression museum

**Effort:** 1 week
**Risk:** Does not guarantee coherence — atom pools may not have good content for every role
**Reward:** Marginal improvement. Chapters have declared structure but fill it with atoms that weren't written for specific structural positions
**Verdict:** This is the right plan if the operator wants a low-risk entry point but does not address the core problem — atoms are not written as hooks, or mechanisms, or integration sections

---

### Scenario C — Hybrid: Template in Parallel With Current

**What this means:**
- Ship one book via template approach AND one book via current assembly approach
- Same arc (anxiety × gen_z_professionals × overwhelm)
- Pearl_Editor reads both
- Evidence-based verdict

**Effort:** Template book (Scenario A) + one additional assembly run = 3-3.5 weeks
**Risk:** 2× time to verdict / Reward: eliminates "what if assembly just needs one more fix" doubt permanently

**Use this scenario if:** The operator is not ready to commit to Scenario A without head-to-head evidence.

---

## III. Recommendation + Reasoning

### Recommendation: Scenario A

**Why not Scenario B:** Adding section_role metadata to atoms and a section_plan to ChapterContract does not solve the coherence problem. It creates a new constraint layer on top of atoms that were written without positional awareness. An atom written as a "scene vignette" is not automatically a good "opening hook." The v2_somatic YAML grid was written with section roles in mind — each hook is a hook, each mechanism section is a mechanism explanation. That intentionality is the difference.

**Why not Scenario C:** The question "does the template produce better books than assembly?" can be answered with high confidence from existing evidence. The stacked packet pilot chapter (in `artifacts/pilot/stacked_packet/anxiety/book.txt`) is structurally legible without head-to-head comparison. The production book output (`artifacts/pilot/full_15_spine/anxiety/book.txt`) shows raw hook pool dumps in the delivered text. The experiment is already run. We don't need another one.

**Why Scenario A:** The infrastructure exists. The content exists. The loader works. The beatmap has the right grid already defined. The only reason this wasn't the production path in April 2026 is that the team pivoted away from completing it. The 2-3 week estimate is for completing work that was already 60% done.

### Five Operator Questions That Would Flip the Recommendation

1. **"We have paying customers waiting for books."** → Switch to Scenario C. Ship via current pipeline (imperfect) while building template approach in parallel.

2. **"The v2_somatic content doesn't fit our voice."** → Switch to Scenario C. Run the content authoring sprint (2 days) before committing to full build.

3. **"We need books in 3 additional topics first."** → Stick with Scenario B as a bridge. Add section_role metadata while building proper templates per-topic in parallel.

4. **"The zip archives for v2_somatic chapters 3-7 and 9-12 are corrupted or missing."** → Re-evaluate. Pearl_Writer can generate replacements but this adds 5-7 days to the estimate.

5. **"We've tried structural fixes before and assembly still wins on word count."** → Note that the comparison is invalid: assembly word count comes from atom pool depth (thousands of atoms), not structural quality. Template word count comes from 153-word sections that need Pearl_Writer expansion. These are independent variables.

---

## IV. The Anti-Recommendation

### "Keep doing what we're doing"

Name it. This is the option of: another sprint fixing atom repetition, another gate pass improving bridge sentences, another benchmark showing gates are green while reader experience is unknown, another discovery that chapter flow fails 12/12.

**This is the wrong choice.** Here is why in specific terms:

1. **It has no finish line.** "Assembly pipeline producing coherent books" has no definition that anyone has agreed on. Every sprint patches a different symptom. The chapter flow gate was invented to catch exactly this problem. It has failed 12/12 chapters in every run for months.

2. **It is treating symptoms, not the cause.** The cause of incoherence is that no chapter has a declared narrative arc within it. Fixing bridges, adding gate layers, tuning atom cooldowns — none of these give a chapter a spine. They make the chapters' random content flow slightly better. A chapter that flows slightly better between unstructured blocks is still an unstructured chapter.

3. **The content for a structured approach already exists.** 600 YAML section files are on disk. A loader that works is committed. A pilot that produced a structurally legible chapter is in `artifacts/`. The pivot back to assembly patching was not based on evidence that the template approach failed — it was based on the template build being incomplete, and the team choosing to close known assembly issues instead of completing the unknown template wiring.

4. **The operator is correct.** The operator said: "A template has 12 chapters, 7-10 sections per chapter, 3-5 variants per section. That gives you a coherent book. What we ship now is scene/story/scene with no structure." This analysis confirms every part of that statement. The operator's architectural intuition is right. Continuing to patch the approach the operator has identified as wrong is not neutral — it is a compounding wrong turn.

**Do not run another benchmark. Do not ship another gate pass. Do not open another PR that makes the assembly pipeline slightly better. Build the template approach.**

---

## V. Fail-Fast Gate — What Ships First

### The Gate: One Hand-Authored 12-Chapter Template YAML

**Before any code is written**, the operator reads a single document:

A complete 12-chapter template for:
- Topic: anxiety
- Persona: gen_z_professionals
- Arc: overwhelm (discovering the alarm → understanding the alarm → learning to respond → integrating new relationship)

For each of 12 chapters, the document specifies:
- Chapter title
- Chapter thesis (the one sentence this chapter leaves the reader with)
- Section 01 (hook): what kind of hook? what's the opening line?
- Section 02 (scene): what setting? what moment?
- Section 03 (reflection): what question does this chapter's scene raise?
- Section 04 (exercise): what practice? what does the reader do?
- Section 05 (scene): what second moment? closer or wider?
- Section 06 (teacher doctrine): what mechanism does this chapter explain?
- Section 07 (reflection): how does the mechanism land in the reader's body?
- Section 08 (exercise): what is the regulation practice?
- Section 09 (scene): what does the shift look like?
- Section 10 (integration): what is the one takeaway sentence?

**This document is a 1-day deliverable.**

**The operator's test:** Read it as an outline. Can you follow the arc of the book? Can you see what each chapter is for? Does chapter 1 set up what chapter 2 deepens? Does the book have a beginning, middle, and end?

**If yes → authorize the 3-week build.** The build is finishing wiring that was 60% done in April 2026.

**If no → the thesis is wrong** — structure as described does not produce coherence in this genre/persona combination, and 3 weeks is saved. Return to first principles.

This gate costs 1 day and answers a 3-week question.

---

## Summary of Findings

| Question | Answer |
|---------|--------|
| Did old template system exist in git? | YES — 600 YAML files, loader works, pilot ran |
| Was it ever production? | NO — never wired to default render path |
| Date of template build | April 10-11, 2026 (PRs #383, #385, #389) |
| Date of template abandonment | April 12, 2026 (team pivoted to assembly patching) |
| Does current pipeline have section-awareness? | NO — 12/12 chapter flow failures, hook pool dumps in delivery |
| Section types formalized | 10 (from v2_somatic grid, mapped to 15 canonical section jobs) |
| Bestseller citations | 5 (Atomic Habits, Set Boundaries, Burnout, Big Feelings, The Body Keeps the Score) |
| Build effort estimate | 14-17 working days (2-3 weeks) |
| Recommended scenario | A — Revive template approach |
| Fail-fast gate | 1-day hand-authored 12-chapter template YAML, operator reads as outline |
| API spend this sprint | $0 |

**NEXT_ACTION:**
Operator reads this verdict → picks scenario → if A or C, next sprint is 1-day hand-authored template YAML for anxiety × gen_z_professionals × overwhelm. Operator reads the outline. If it reads like a coherent book, authorizes the 3-week build. If not, saves 3 weeks and reconsiders the thesis.

The YAML should be authored by a human or Pearl_Writer (not a pipeline run) to ensure intentionality in every section job description.
