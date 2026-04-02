# RCG-016 — Teacher profile audience assumptions (MEDIUM)

**Audit ref:** `RESEARCH_AUDIT_2026_03_30.md` section A item 16
**Source file:** `config/authoring/pen_name_teacher_profiles.yaml`
**Claim:** 480 author-slot/profile rows with persona definitions — no research citations for audience assumptions
**Research query:** audiobook listener demographics psychographics 2024 2026

---

## Claim analysis

The pen name teacher profiles YAML contains 480 rows defining author personas with audience targeting assumptions (e.g., who listens to what kind of content, what emotional needs they have, preferred tone and style). These audience assumptions drive content creation and positioning decisions but cite no research for the demographic and psychographic claims embedded in the profiles.

## Research findings

### Audiobook listener demographics

1. **Edison Research (2024).** "The Infinite Dial 2024." Key demographic findings:
   - 53% of Americans 12+ have ever listened to an audiobook
   - Monthly audiobook listening highest among ages 18-34 (35%) and 35-54 (30%)
   - Slight female skew in overall audiobook consumption
   - Higher consumption among college-educated and higher-income households

2. **Audio Publishers Association (APA) Consumer Survey (2024).** Reports:
   - Self-help/personal development is a top-5 audiobook genre
   - Listeners cite commuting, exercising, and relaxing as primary listening occasions
   - 60%+ of frequent listeners consume 3+ audiobooks per month

3. **Pew Research Center (2024).** "Book Reading in America":
   - 23% of U.S. adults reported listening to an audiobook in the past year (narrower definition than "ever listened")
   - Strongest among ages 18-49, college graduates, and those earning $75K+

### Psychographic data for self-help audiences

4. **Codex Group / BookNet Canada.** Conduct reader psychographic surveys but results are proprietary. No public data was found validating specific self-help audiobook listener psychographic segments.

5. **General psychographic frameworks** (e.g., VALS by Strategic Business Insights, Mintel consumer segments) provide broad lifestyle segmentation but none maps to the specific teacher-profile audience definitions in the YAML.

6. **No publicly available study** validates the specific audience assumptions embedded in 480 teacher profile rows. The assumptions appear to be **editorially constructed** based on genre knowledge and general demographic data rather than derived from a specific research study.

## Verdict

**NEEDS_PRIMARY_SOURCE** — The audience assumptions in the teacher profiles are reasonable editorial constructions consistent with available demographic data (Edison, APA, Pew), but they are not sourced from any specific research. With 480 rows making implicit audience claims, documenting representative examples' provenance is important for credibility.

## Recommendation

1. Add a header comment to the YAML file:
   ```yaml
   # Audience assumptions: internal editorial construction informed by
   # Edison Research Infinite Dial 2024, APA Consumer Survey 2024,
   # Pew Research 2024. Not validated by dedicated audience research.
   # Status: Provisional — update with listener data when available.
   ```
2. For representative rows (e.g., the top-level persona definitions), add `_source:` blocks.
3. Consider commissioning a listener survey to validate the most impactful audience assumptions.

## Citations

```yaml
_source:
  study: "Edison Research Infinite Dial 2024; APA Consumer Survey 2024; Pew Research 2024"
  note: "NEEDS_PRIMARY_SOURCE — 480 profile rows with audience assumptions. Editorially constructed, not research-validated. Add provenance header."
  date: "2026-04-01"
```
