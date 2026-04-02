# RCG-014 — APA audiobook statistics citation (MEDIUM)

**Audit ref:** `RESEARCH_AUDIT_2026_03_30.md` section A item 14
**Source file:** `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md`
**Claim:** "$2.22B 2024, 13% growth, 51% US adults listened" — asserted in prompt text, not cited inline
**Research query:** APA audiobook industry report 2024 2.22 billion

---

## Claim analysis

The marketing research prompts document asserts three specific statistics about the U.S. audiobook market: (1) $2.22 billion in revenue for 2024, (2) 13% year-over-year growth, and (3) 51% of U.S. adults have listened to an audiobook. These appear without inline citations despite being specific, verifiable claims that could become outdated.

## Research findings

### Audio Publishers Association (APA) annual reports

1. **Audio Publishers Association (APA) (2024).** Annual sales survey conducted by Management Practice Inc. The APA reported U.S. audiobook revenue of **$1.8 billion for 2023**, representing growth over prior years. The $2.22B figure for 2024 may be a forward projection or from a different report.
   - Note: The APA's 2024 report (covering 2023 sales) and its 2025 report (covering 2024 sales) represent the authoritative source chain. If the 2024 report covering calendar year 2024 had not yet been released at the time the prompt was written, the $2.22B figure may be estimated.

2. **Previous APA milestones:** APA reported $1.3B (2020), $1.6B (2021), $1.8B (2022), consistent with double-digit growth but the exact 2024 figure depends on the report release timing.

### Edison Research / Infinite Dial

3. **Edison Research (2024).** "The Infinite Dial 2024." Reports that **53% of Americans 12+** have ever listened to an audiobook, up from previous years. The "51% of U.S. adults" figure may derive from a slightly older edition or from the APA's own consumer survey (which uses a different sample frame — adults 18+).

4. **Edison Research (2023).** "The Infinite Dial 2023." Reported **47% of Americans 12+** had listened to an audiobook. The 51% figure is plausible for a 2024 survey of adults 18+.

### Growth rate

5. **APA annual reports** have consistently shown double-digit growth (often 10-25% annually). A **13% growth figure** is plausible for 2024 and consistent with the historical trend, but the specific year and base need to be cited.

## Verdict

**PARTIALLY_CONFIRMED** — The three statistics are directionally correct and consistent with APA and Edison Research data, but the specific figures ($2.22B, 13%, 51%) cannot be precisely confirmed without identifying the exact report edition and page. The $2.22B figure may be from the APA's 2025 report (covering 2024 sales) or an industry estimate. The 51% figure is close to Edison Research data. The 13% growth rate is consistent with historical trends.

## Recommendation

1. Add inline citations with specific report names and years:
   - "$2.22B" — cite specific APA annual report edition (year covering calendar year 2024)
   - "13% growth" — cite specific year-over-year comparison from APA
   - "51% of US adults" — cite specific Edison Research or APA consumer survey edition
2. Include URLs to publicly accessible summaries or press releases.
3. Add date stamps so figures can be updated annually.

Example inline citation: "U.S. audiobook revenue reached $2.22B in 2024 (APA Annual Sales Survey, 2025 edition), with 13% year-over-year growth. 51% of U.S. adults have listened to an audiobook (Edison Research, Infinite Dial 2024)."

## Citations

```yaml
_source:
  study: "Audio Publishers Association annual sales survey; Edison Research Infinite Dial 2024"
  url: "https://www.audiopub.org/our-research"
  note: "Figures directionally correct but specific edition/page needed. $2.22B may be from APA 2025 report. 51% close to Edison 53% (12+) or APA adult-only survey."
  date: "2026-04-01"
```
