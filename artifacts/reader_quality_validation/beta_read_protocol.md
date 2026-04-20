# Beta-Read Protocol
## Operator-Owned: Reader Response Validation

**Purpose:** Ground-truth the Pearl_Editor verdict with 5 actual humans from the target persona before committing to any architectural change.

**Recruiter note:** This protocol is operator-owned and runs outside GitHub Actions. Estimated timeline: 1 week to collect, 1 day to analyze.

---

## Participant Profile

**Recruit 5 humans matching ALL of:**
- Age 24-35
- Professional role (full-time employment, any sector)
- Self-identifies as experiencing anxiety or stress related to work/performance
- Regular reader (≥1 book per quarter)
- NOT currently in treatment or crisis (informed consent)

**Recruitment channels:** Personal network, Slack communities (e.g. product/design Slacks, startup communities), LinkedIn outreach, Twitter/X. Offer: gift card ($20-30) or charitable donation of their choice.

---

## The Read

Send Chapter 1 only: `artifacts/qa/_scratch_pp_ahjan_genz_anxiety/standard_book/book.txt`, lines 1-46 (Chapter 1 text up to but not including "Chapter 2").

**IMPORTANT:** Strip the following before sending — these are rendering artifacts that would contaminate the test:
- Do NOT send if the raw Python dict `{'intro':` appears in the chapter. If Chapter 5 or 6 is used in any variant test, strip that block manually first.
- Do NOT send any "---" barrage block that runs more than 100 words.

Presentation: plain text email or PDF. No branding. No title other than a generic working title like "Untitled Self-Help Book — Anxiety."

Reading time: approximately 5-8 minutes.

---

## Survey (run immediately after reading)

Use Google Form, Tally.so, or Typeform. 5 scored questions + 1 open question.

**Q1 (Likert 1-5):** "How much do you want to read the next chapter?"
- 1 = I definitely don't / 5 = I definitely do

**Q2 (Text, optional):** "Did any sentence feel generic — like it could be from any self-help book? If so, paste it here."
*(This surfaces the spiritual epigraph problem, karma yoga corpus, and repeated exercises without priming.)*

**Q3 (Text, optional):** "Was there a line you'd screenshot or share with a friend? If so, paste it."
*(This validates memorable lines vs. gate predictions.)*

**Q4 (Likert 1-5):** "Did you learn something specific about anxiety — or did you just feel generally encouraged?"
- 1 = Just general encouragement / 5 = Learned something specific

**Q5 (Likert 1-5):** "If this were a real book and the sample ended here, would you buy it?"
- 1 = Definitely not / 5 = Definitely yes

**Q6 (Open):** "What one thing would make you more likely to read the whole book?"

---

## Scoring Thresholds

| Avg Q1 | Interpretation | Action |
|--------|---------------|--------|
| ≥ 4.0  | Real reader pull-through — pipeline produces viable books | Scenario A: ship & instrument |
| 3.0–3.9 | Mid-range — specific fixes needed | Scenario C: targeted fixes |
| 2.5–2.9 | Weak — structural problems confirmed | Scenario C/D: assess depth |
| < 2.5  | Pipeline produces prose but not books | Scenario D: rethink assembly |

| Avg Q5 | Interpretation |
|--------|---------------|
| ≥ 3.5 | Sample converts — first chapter is buy-worthy |
| 2.5–3.4 | Marginal — needs opening chapter surgery |
| < 2.5 | First chapter kills the conversion |

---

## Analysis After Collection

1. Tabulate Q1 and Q5 averages.
2. Collect Q2 responses — any sentence flagged by ≥3/5 readers is a confirmed slop passage.
3. Collect Q3 responses — any sentence cited by ≥2/5 readers is a confirmed quotable.
4. Cross-reference Q3 responses against `pearl_editor_markup.md` "Memorable lines" findings. Agreement = editorial judgment validated.
5. Q6 open responses: code for themes (author voice, clarity, exercises, story, specificity).
6. Feed findings into `DECISION_MATRIX.md` — confirm or revise Scenario selection.

---

## Operator Dispatch

1. Prepare clean chapter 1 text (strip rendering artifacts per above).
2. Create form in Tally.so or Google Forms using Q1-Q6 above.
3. Recruit 5 participants via personal network or community posting.
4. Set deadline: 7 days from send.
5. Analyze within 48 hours of last response.
6. Report back to Pearl_PM with average Q1, average Q5, confirmed quotables, confirmed slop passages, and top Q6 theme.

**Estimated total operator time:** 3-4 hours (setup + outreach + analysis).
