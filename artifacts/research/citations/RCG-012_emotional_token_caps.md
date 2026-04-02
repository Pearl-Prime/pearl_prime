# RCG-012 — Emotional token global caps rationale (MEDIUM)

**Audit ref:** `RESEARCH_AUDIT_2026_03_30.md` section A item 12
**Source file:** `config/catalog_planning/brand_archetype_registry.yaml` (L27-30)
**Claim:** `emotional_token_global_caps` — reset: 12, clarity: 18, calm: 24 — no rationale provided
**Research query:** audiobook marketing keyword density caps emotional language A/B OR competitor benchmark

---

## Claim analysis

The brand archetype registry YAML defines numeric caps on emotional tokens: "reset" capped at 12, "clarity" at 18, "calm" at 24. These caps presumably limit how many times these emotional keywords can appear in marketing copy, metadata, or content. No rationale, source, or methodology is provided for these specific numbers.

## Research findings

### Marketing keyword density — general

1. **SEO and keyword density best practices.** Industry-standard guidance (Moz, SEMrush, Yoast) suggests keyword density of 1-2% for web content to avoid keyword stuffing penalties. However, these guidelines apply to search engine optimization for web pages, not audiobook metadata or marketing copy specifically.

2. **Amazon KDP metadata guidelines.** Amazon limits subtitle length to 200 characters and has keyword fields with specific character limits. Amazon's content policy prohibits "keyword stuffing" in titles and descriptions but does not define numeric caps per emotional word.

3. **No published A/B test or competitor benchmark** was found that establishes specific numeric caps for emotional language tokens in audiobook marketing copy. The specific numbers (12, 18, 24) do not correspond to any publicly available research, platform policy, or industry standard.

### Emotional language in marketing — academic

4. **Berger, J. & Milkman, K. L. (2012).** "What Makes Online Content Viral?" *Journal of Marketing Research*, 49(2), 192-205. Found that content with high-arousal emotions (awe, anxiety, anger) is more likely to be shared, but does not address frequency caps or diminishing returns from specific word counts.

5. **Rocklage, M. D. & Fazio, R. H. (2020).** "The Enhancing Versus Backfiring Effects of Positive Emotion in Consumer Reviews." *Journal of Marketing Research*, 57(2), 332-352. Demonstrates that emotional language effectiveness depends on context and can backfire when perceived as inauthentic — supporting the concept of caps but not specific numeric values.

### Assessment

The caps appear to be **internal engineering defaults** — reasonable design decisions to prevent emotional keyword overuse, but not derived from external research. The graduated values (12 < 18 < 24) suggest an intentional hierarchy where "calm" is permitted more frequently than "reset," which could reflect brand voice priorities rather than empirical findings.

## Verdict

**NEEDS_PRIMARY_SOURCE** — The specific numeric caps (12, 18, 24) cannot be traced to any external research, A/B test, or platform policy. The concept of capping emotional language is reasonable and has indirect support in marketing literature (Rocklage & Fazio 2020), but the specific numbers are almost certainly **internal calibration values**.

## Recommendation

1. Add a `_source:` block to the YAML:
   ```yaml
   _source:
     note: "Internal calibration — no external A/B data. Caps reflect brand voice hierarchy. Review with conversion data when available."
     date: "2026-04-01"
   ```
2. If A/B testing is eventually conducted on these caps, document results and update the source.

## Citations

```yaml
_source:
  note: "NEEDS_PRIMARY_SOURCE — caps are internal engineering defaults. No external A/B or industry benchmark found. Concept supported by Rocklage & Fazio 2020 (emotional language backfire effects)."
  date: "2026-04-01"
```
