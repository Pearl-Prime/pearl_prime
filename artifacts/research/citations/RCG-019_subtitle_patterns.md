# RCG-019 — Subtitle pattern effectiveness (LOW)

**Audit ref:** `RESEARCH_AUDIT_2026_03_30.md` section A item 19
**Source file:** `omega/title_entropy/subtitle_patterns.yaml`
**Claim:** Subtitle pattern rules — no citation for effectiveness claims
**Research query:** audiobook subtitle conversion A/B testing academic OR industry

---

## Claim analysis

The `subtitle_patterns.yaml` file defines structural title/subtitle templates and brand preferences (scenario_direct, three_part, micro_promise, etc.). The audit flags that no evidence is cited for the effectiveness of these patterns — i.e., no A/B test data, conversion studies, or academic research validates that these specific patterns perform better than alternatives.

## Research findings

### Title/subtitle optimization — industry

1. **No publicly available A/B test** on audiobook subtitle patterns was found. Amazon, Audible, and major audiobook publishers do not publish conversion data by subtitle format.

2. **KDP and Audible metadata guidelines** prescribe character limits and prohibited practices (keyword stuffing) but do not recommend specific subtitle structural patterns.

3. **Self-publishing practitioner blogs** (e.g., Kindlepreneur, Reedsy, Written Word Media) discuss subtitle best practices (clarity, benefit-driven, keyword inclusion) based on anecdotal experience, not controlled studies.

### Title optimization — academic

4. **Berger, J. & Packard, G. (2022).** "Using Natural Language Processing to Understand People and Culture." *American Psychologist*, 77(4), 525-537. Demonstrates NLP analysis of language patterns in consumer behavior but does not address book subtitle effectiveness.

5. **Chevalier, J. A. & Mayzlin, D. (2006).** "The Effect of Word of Mouth on Sales: Online Book Reviews." *Journal of Marketing Research*, 43(3), 345-354. Studies book sales drivers (reviews, ratings) but not subtitle patterns.

6. **No academic study** was found specifically testing audiobook or book subtitle structural patterns against conversion metrics.

### Assessment

The subtitle patterns in the YAML represent **internal craft conventions** — editorial heuristics about what makes an effective subtitle for self-help audiobooks. These are reasonable working templates but have no external empirical validation.

## Verdict

**NEEDS_PRIMARY_SOURCE** — No external evidence (academic or industry) validates the specific subtitle patterns. The patterns are internal heuristics. This is expected for a LOW-severity item — subtitle pattern effectiveness would require proprietary A/B test data to validate.

## Recommendation

Label patterns as heuristic:
```yaml
_source:
  note: "Internal craft convention — no external A/B data. Patterns are editorial heuristics, not empirically validated."
  date: "2026-04-01"
```
Do not describe these patterns as "proven" or "optimized" in customer-facing contexts without owned test data.

## Citations

```yaml
_source:
  note: "NEEDS_PRIMARY_SOURCE — no public A/B data on audiobook subtitle patterns. Treat as internal heuristic."
  date: "2026-04-01"
```
