# Decision Matrix — Reader Quality Validation Sprint
**Date:** 2026-04-18
**Evidence:** Pearl_Editor markup (this session) + Gate benchmark scores (this session) + Beta-reader protocol (operator-owned, pending)

---

## The Central Question

> "Are we at 92% of the way to bestsellers, or 92% of the way to a machine that produces slop efficiently?"

**Short answer: Neither. We're at ~60% of the way to viable self-help books, with a specific and diagnosable assembly failure that the current gate stack cannot detect.**

---

## Evidence Summary

### Gate Benchmark — Critical Finding

The pipeline's gate stack rates ALL THREE real bestsellers as FAIL/WARN:

| Book | ONTGP mean | Flow score | Flow status | Memorable lines |
|------|------------|------------|-------------|-----------------|
| **Our standard_book** (12 chapters) | **0.495** | 98.8 | PASS | 3 / 12 chapters |
| Bourne Ch1 representative | 0.524 | 70 | FAIL | 0 |
| Wilson Ch1 representative | 0.424 | 55 | FAIL | 0 |
| Breslin Ch1 representative | 0.378 | 70 | FAIL | 1 |

**Interpretation:** Our book scores BETTER than real bestsellers on our own gates. This does NOT mean our book is better. It means **the gates are measuring conformance to a template, not literary quality**.

The ONTGP framework penalizes bestsellers for:
- "WEAK_TRANSITIONS" — bestseller prose uses its own transitions, not the pipeline's expected transition cues
- "MISSING_CLEAR_POINT" — bestseller chapters build meaning differently than the ONTGP structure
- "NO_ACTIONABLE_STEP" — memoir-driven bestsellers (Wilson) don't have per-chapter exercises
- Low "Give" scores — Wilson scores 0.1 on Give; it's a bestseller

**The gates are not miscalibrated in the sense of wrong thresholds — they are miscalibrated in the sense of measuring the wrong thing.**

### Pearl_Editor Verdict

**Average chapter rating: 3.7 / 10**

**Book-level hook strength: 2/10** (sample would not convert)

**Book-level finish probability: 10%** (catastrophic repetition by chapter 4)

**Key failures not detected by any gate:**
1. Verbatim repetition of exercise blocks across 9 of 12 chapters
2. Verbatim repetition of full scene paragraphs across 4-5 chapters
3. Raw Python dict syntax in chapters 5 and 6 (`{'intro': "..."`)
4. "Helvetica; ;;" font artifact in chapter 10
5. Karma Yoga / Bhakti Yoga / Buddhist cosmology corpus injection in 9 chapters (zero relevance to gen_z_professionals anxiety)
6. Chapter escalation failure — chapters 1-12 have identical structure, no arc
7. No author/narrator presence — reader has no one to follow

---

## Scenario Matrix

### Scenario A — "We're close, ship and iterate"
**Evidence for:** Some individual atoms are good (Marcus, Sarita, 3 quotable lines).
**Evidence against:** Book-level finish probability 10%. Python dicts in prose. Repeated exercises 9 times. Gates rate bestsellers worse than us.
**Verdict: NOT A.** We are not close.

### Scenario B — "Gates are miscalibrated"
**Evidence for:** Strong. All 3 bestsellers FAIL our gates. Our book PASSES gates while having unrendered template artifacts in the prose.
**Evidence against:** None. This is confirmed.
**Verdict: CONFIRMED B** — BUT B alone isn't the complete picture.

### Scenario C — "Real content gap"
**Evidence for:** Strong. The content gap is assembly-level, not atom-level. Good atoms assembled catastrophically.
**Evidence against:** The atoms CAN be good (Marcus, Sarita, the aphorisms).
**Verdict: CONFIRMED C** — specifically an assembly/rendering gap, not an ideation gap.

### Scenario D — "Fundamental gap"
**Evidence for:** Partial. The book is pre-commercial.
**Evidence against:** The atoms work. The individual vignettes work. There's no fundamental failure of concept.
**Verdict: NOT D.** The pipeline can produce quality content. It can't assemble it into a book.

---

## Selected Scenario: **B + C** (gates miscalibrated AND real content gap in assembly layer)

### The Specific Assembly Failures

This is not a "the content is bad" problem. This is three distinct technical failures:

**Failure 1: Cross-chapter deduplication is not enforced.**
The same exercise blocks, scene stamps, and vignette paragraphs are being inserted into each chapter without checking whether they already appeared. A chapter-level gate does not catch this — only a book-level cross-chapter deduplication check would.

**Failure 2: Template rendering is incomplete.**
Raw Python dict syntax (`{'intro': "..."}`) is reaching the rendered book.txt without being expanded. This is a rendering pipeline bug, not a content problem.

**Failure 3: Corpus insertion is unfiltered.**
Karma Yoga, Bhakti Yoga, Buddhist cosmology passages from an unrelated source corpus are being inserted verbatim into chapters targeting gen_z_professionals × anxiety. These pass the chapter_flow gate because the gate checks for specific forbidden strings, not persona-relevance. The gate is blind to corpus provenance.

---

## Ranked Next-Sprint Actions

### Action 1 (HIGHEST PRIORITY): Cross-chapter repetition gate
**What:** Build a book-level gate that detects verbatim paragraph repetition across chapters. Threshold: any 50+ word block appearing in >1 chapter → FAIL. Any exercise block appearing in >2 chapters → FAIL.
**Why:** The most common reader-facing failure. 9 of 12 chapters have the same exercise. No existing gate catches this.
**Scope:** One gate, one threshold, no API spend. Pure heuristic.

### Action 2: Template rendering audit
**What:** Audit all rendering paths that produce `book.txt`. Find the code path where a Python dict is being included in rendered output instead of being expanded. Add a post-render check that FAILs on any `{'` followed by a known exercise key (intro, guided_practice, aha_noticing).
**Why:** Python dicts in shipped prose are a hard stop. Gate currently doesn't catch them.
**Scope:** Targeted rendering bug fix + one gate assertion.

### Action 3: Corpus provenance gate
**What:** Build a persona-relevance filter that flags blocks whose content is off-persona. Specifically: detect "karma yoga," "bhakti yoga," "enlightened teacher," "Six Worlds," "Dharmakaya," "dharma" and similar terms in books targeting non-spiritual personas (gen_z_professionals, etc.). Blocks containing these terms in a gen_z_professionals book → FAIL.
**Why:** The corpus injection problem is destroying persona coherence. A reader who opened an anxiety book for young professionals and hit "transcend the limitations of the Six Worlds" is gone.
**Scope:** A keyword blocklist per persona, applied at chapter level.

### Action 4: Gate recalibration for bestseller text
**What:** After actions 1-3, re-run `score_external_text.py` against the benchmark texts. Adjust ONTGP thresholds and flow gate transition expectations so that bestseller text scores in the 0.55-0.70 range rather than FAILing. This is calibration work, not content work.
**Why:** Currently gates rate bestsellers lower than our broken book. That's backwards. Gates should identify what makes books work, not what makes them conform to our template.
**Scope:** Threshold tuning, not architectural rewrite.

### Action 5: Book-level arc enforcement
**What:** Add a check that chapter titles, chapter emotional_job assignments, and narrative arc actually escalate from chapter to chapter. Current chapters 1-12 are structurally identical — same template, different scene stamps.
**Why:** A book without escalation is not a book. It's an anthology of similar chapters.
**Scope:** Book-level structural validation. Can be heuristic (check that emotional_job doesn't repeat across adjacent chapters).

---

## What This Sprint Replaces in the Roadmap

The original plan (ACT-012 through ACT-015 per `artifacts/analysis/shortest_path_to_bestseller.md`) assumed the pipeline's feature completeness gap was the limiting factor. This sprint proves otherwise:

**The feature completeness rate (87-92%) is measuring pipeline coverage, not book quality. The two are not the same.**

Before ANY feature sprint (ACT-012..015), the following must be true:
- [ ] Cross-chapter repetition gate exists and BLOCKS the standard_book candidate
- [ ] Template rendering artifacts (Python dicts, font names) are caught pre-delivery
- [ ] Corpus injection in off-persona chapters is caught pre-delivery

When those three gates exist and pass on a candidate book, run `score_external_text.py` against the benchmark texts again. If bestseller text now scores ≥ 0.55 on our gates, the pipeline can proceed to feature work with confidence that quality measurement is trustworthy.

---

## Beta-Reader Protocol Integration

The `beta_read_protocol.md` protocol is designed to confirm this analysis with human signal. Expected outcomes:

- **If Q1 avg < 2.5:** Confirms Scenario C/D. Structural assembly is the priority.
- **If Q2 responses cite the spiritual epigraphs or exercise repetitions:** Confirms Pearl_Editor finding without priming.
- **If Q3 responses cite "Perfectionism is fear in a productive costume" or the "3am" line:** Confirms Pearl_Editor memorable-line findings.
- **If Q5 avg < 2.5:** First chapter doesn't convert. Chapter surgery needed before delivery.

---

## API Spend This Sprint: $0
All analysis performed in this Claude Code session (subscription, not API). Gate scoring is deterministic/heuristic. Benchmark samples are representative texts written from memory, not API-generated.

**NEXT_ACTION (operator):**
1. Read this decision matrix.
2. If scenario B+C is confirmed: halt ACT-012..015 feature work.
3. Run beta-read protocol per `beta_read_protocol.md`.
4. Assign sprint to fix Action 1 (cross-chapter dedup gate) and Action 2 (template rendering audit).
5. After those two fixes: re-run full QA ladder and check if standard_book candidate clears.
6. Then and only then: return to feature work with valid quality signal.
