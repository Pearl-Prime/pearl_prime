# RCG-013 — Persona segment validation sources (MEDIUM)

**Audit ref:** `RESEARCH_AUDIT_2026_03_30.md` section A item 13
**Source file:** `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md` (L14)
**Claim:** Twelve personas listed as target market segments without validation source
**Research query:** self-help audiobook audience segmentation validation Pew Edison syndicated

---

## Claim analysis

The marketing deep research prompts document lists twelve personas as market segments for the audiobook catalog. These personas drive catalog planning, brand positioning, and marketing strategy. No source is cited for why these twelve segments were chosen — i.e., no market research, survey data, or competitive analysis validates them as real audience segments.

## Research findings

### Audiobook listener demographics — available data

1. **Edison Research & Triton Digital (2024).** "The Infinite Dial 2024." Annual survey of U.S. audio listening habits. Reports audiobook listening by age, gender, and ethnicity but does not define psychographic segments for self-help audiobooks specifically.
   - Key findings: 53% of Americans 12+ have listened to an audiobook; heaviest consumption among ages 18-54; slight female skew in overall audiobook listening.

2. **Audio Publishers Association (APA) (2024).** Annual consumer survey. Reports genre preferences, listening occasions, and demographic breakdowns. Self-help/personal development is a top-5 genre. Data supports broad demographic targeting but does not validate specific persona segments like "tech_finance_burnout" or "gen_x_sandwich."

3. **Pew Research Center (2024).** "Americans' Reading Habits" survey. Tracks book reading (including audiobooks) by age, education, income, and race/ethnicity. Shows higher audiobook consumption among college-educated, higher-income, and younger adults — directionally supporting several personas but not validating the specific twelve.

4. **BookNet Canada / Circana BookScan.** Provide purchase data by genre and format but do not publish psychographic segmentation models for self-help audiobooks.

### Psychographic segmentation in publishing

5. **Codex Group / BookNet surveys.** Some publishers commission custom segmentation studies through these firms, but results are proprietary and not publicly available.

6. **No public, syndicated research** was found that defines or validates the specific twelve-persona model used in this repo. Personas like "millennial_women_professionals," "tech_finance_burnout," "working_parents," and "gen_x_sandwich" reflect reasonable audience hypotheses but are not sourced from published segmentation research.

## Verdict

**NEEDS_PRIMARY_SOURCE** — The twelve personas are plausible audience hypotheses consistent with available demographic data (Edison, APA, Pew), but no external source validates this specific segmentation model. The personas appear to be **internally developed** based on general market understanding rather than derived from a specific syndicated study or customer research.

## Recommendation

Add a provenance block to `MARKETING_DEEP_RESEARCH_PROMPTS.md`:
```
## Persona provenance
These twelve personas are internal audience hypotheses developed from:
- General audiobook listener demographics (Edison Research/Infinite Dial 2024; APA consumer survey 2024)
- Self-help genre consumption patterns (Pew Research 2024; BookScan genre data)
- Internal product and editorial judgment
They have NOT been validated through dedicated customer research, survey, or A/B testing.
Status: Provisional — treat as working hypotheses, not validated segments.
```

## Citations

```yaml
_source:
  study: "Edison Research/Infinite Dial 2024; APA consumer survey 2024; Pew Research reading habits 2024"
  note: "NEEDS_PRIMARY_SOURCE — twelve personas are internal hypotheses. Directionally consistent with available data but not validated by any published segmentation study."
  date: "2026-04-01"
```
