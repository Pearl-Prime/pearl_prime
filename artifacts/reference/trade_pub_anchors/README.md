# Trade-Pub Anchor Corpus — Operator Step-by-Step Guide

**What this is:** the gold-standard register comparator for Pearl Prime books. Every Pearl Prime book is targeting the prose register of trade-published bestsellers in the somatic / therapy / mind-body category. Without anchors on disk, "would this sit next to van der Kolk?" is a vibe check. With anchors, it becomes measurable — the register gate (`docs/PEARL_PRIME_REGISTER_GATE_SPEC.md`) compares rendered books against these reference passages.

**Why we need YOUR picks** (not generated examples): the register comparator only works if the anchors are real, trade-pub-published prose YOU consider exemplary. Generated anchors would teach the system to imitate generated content. Real anchors teach it to reach.

**Your task:** ~10-15 minutes. Pick 1-2 passages from each book below. Paste verbatim into the matching `.md` file. Commit. That's it.

---

## How to do this in 10 minutes flat

### Step 1 — Open the four anchor-template files in this directory

Each file is named for one trade-pub author + book. The file already has the right shape — you just fill in the prose blocks.

```
artifacts/reference/trade_pub_anchors/
  README.md                          ← you're reading this
  van_der_kolk__body_keeps_score.md  ← Bessel van der Kolk
  levine__waking_the_tiger.md        ← Peter Levine
  mate__myth_of_normal.md            ← Gabor Maté
  foo__what_my_bones_know.md         ← Stephanie Foo
```

### Step 2 — For each book, find 1-2 passages you consider exemplary

**What "exemplary" means here:**
- A 1-3 paragraph passage that demonstrates the prose register Pearl Prime should match
- NOT the most quotable line (we have a memorable_lines gate for that)
- NOT the most informational summary
- The kind of passage where the AUTHOR'S VOICE is unmistakably present — somatic, specific, embodied, restrained
- Pick passages that surface a MECHANISM (anxiety / trauma / dysregulation / freeze response / vagal tone / etc.) in their authored register

**Where to find them:**
- Your physical copies if you own them
- Your ebook reader (Kindle / Apple Books) — search by chapter, highlight
- Goodreads quotes pages have many but pick from the prose you've actually read
- Audiobook bookmarks / Audible

**Length per passage:** ~80-300 words. Long enough to demonstrate cadence. Short enough to be a discrete anchor.

### Step 3 — Paste verbatim into the matching file

Open `van_der_kolk__body_keeps_score.md` and replace the `<<<PASTE PASSAGE HERE>>>` blocks with the actual prose. The metadata wrapper (chapter, page, themes) gives the gate something to anchor against; just fill in what you know.

**Example** (this is illustrative; the actual passage you pick is yours):

```markdown
## Passage 1

**Chapter / location:** Chapter 4 — "Running for Your Life"
**Page reference:** approx p. 65 (Penguin paperback)
**Themes:** survival response, freeze, trauma physiology

> Trauma is not the story of what happened back then. It is the
> imprint that experience left in your body's tissues, your nervous
> system, your dreams. The body keeps the score. The mind moves on.
> The body holds on.

**Why this passage:** demonstrates van der Kolk's signature shift — naming the mechanism (somatic imprint) in declarative short-sentence cadence without explanation.
```

(That's NOT an actual van der Kolk passage — it's an illustrative shape. Replace with what YOU consider the right register from the actual book.)

### Step 4 — Commit your picks

Once all four files have at least one passage:

```bash
git add artifacts/reference/trade_pub_anchors/
git commit -m "feat(reference): trade-pub anchor corpus for register gate (operator picks)"
git push
```

Or just tell me you're done and I'll commit + push for you.

---

## What happens after you commit

The register gate's F8 detector (citation grafting; currently deferred) gets ungated. Future register-gate runs include a register-similarity score against these anchors. The 2026-05-18 calibration verdict's F8 finding moves from "advisory only" to "measurable."

Beyond F8: the anchor corpus becomes the calibration baseline for any future register-related work. Voice classifier training, prose-quality rubrics, "would this sit next to" comparisons — they all key off these files.

---

## Operator tips for picking well

1. **Don't overthink it.** Your first instinct is right. The book you actually love is the right one to pick from.

2. **Pick the passage that made you UNDERLINE it** when you read the book. That's the one.

3. **Mix it up.** Pick passages from DIFFERENT chapters / different points in each book — opening / mid-arc / close. The gate will train against variety, not one beat per author.

4. **No need to type — copy-paste.** If you have ebook versions, the copy-paste is fastest. If only physical, OCR works (point your phone camera at the page).

5. **Skip a book if you can't honestly say "this is the register I want."** Better to have 3 strong anchor files than 4 with one weak one.

---

## Time check

This task is genuinely 10-15 minutes. If it takes longer, you're overthinking. Pick fast, paste, commit. The register gate doesn't need perfect anchors; it needs YOUR honest taste. That's the irreplaceable part.

---

## Cross-references

- Register gate spec: `docs/PEARL_PRIME_REGISTER_GATE_SPEC.md` §3.8 (F8 detector — what these anchors enable)
- Scorecard: `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` Layer 4 (anchors also seed system-level benchmark calibration)
- Calibration verdict: `artifacts/qa/ACCEPTANCE_VERDICT_2hr_ahjan_genz_anxiety_2026-05-18.md` §7 (the "trade-pub register" comparator currently anchored only by author names)
