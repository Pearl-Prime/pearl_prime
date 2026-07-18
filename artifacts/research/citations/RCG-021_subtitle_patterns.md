# RCG-021 — Subtitle / title pattern effectiveness (`omega/title_entropy/subtitle_patterns.yaml`)

**Audit:** `artifacts/research/RESEARCH_AUDIT_2026_03_30.md` §A item 19 (LOW).  
**Dev spec mapping:** `docs/RESEARCH_CITATION_GAP_DEV_SPEC.md` Batch 3 **RCG-019** (same claim).  
**Tooling:** Claude-in-Chrome MCP was **not** available in this session; findings use **web search + public pages** only (deep-research skill fallback).

## Claim in repo

`subtitle_patterns.yaml` defines structural **title/subtitle templates** and brand preferences. The audit flags **no citation for effectiveness** (i.e. no evidence that a given template lifts conversion).

## What the file actually asserts

The YAML is **templating** (scenario_direct, three_part, micro_promise, etc.) and brand weighting — it does **not** state numeric conversion lifts or A/B outcomes [internal file review]. Any “effectiveness” risk is **implicit** (templates chosen for catalog coherence), not a published claim.

## External evidence (limited)

Public, **non-peer-reviewed** industry content discusses title/subtitle testing and genre heuristics; none located in this pass is a **controlled A/B** on **audiobook subtitles** specifically:

1. **Title/subtitle A/B testing (general book marketing)** — practitioner framing of split testing for titles; not audiobook-specific or Phoenix-internal [1].  
2. **KDP title/subtitle craft (conversion framing)** — blog guidance on click/sale framing; not empirical A/B disclosure tied to audiobook [2].  
3. **Audiobook marketing / discoverability (2025–2026)** — market overview (e.g. growth, metadata); **does not** validate specific subtitle pattern formulas [3].

## Conclusion (for YAML / migration)

- **Verified:** No strong **external** study was found in this 10-minute pass that **validates** the repo’s exact template strings for **audiobook** conversion.  
- **Recommendation:** Treat current patterns as **internal / craft convention** unless product runs owned A/B tests. Optional `_source: { note: "heuristic template — no external A/B cited", url: "" }` on blocks if adopting §6 `_source` convention.  
- **Downstream:** Do not describe these templates in customer-facing copy as “proven by industry A/B” without new evidence.

## Sources

[1] https://authornexusai.com/which-book-title-will-captivate-your-audience-the-most-using-a-b-testing/ — Author Nexus AI, title A/B testing overview (general).  
[2] https://kdpgenius.com/en/blog/06-title-subtitle — KDP Genius, title/subtitle craft (general KDP).  
[3] https://narrationbox.com/blog/5-proven-audiobook-marketing-strategies-2025-2026 — Narration Box, audiobook marketing trends (not subtitle A/B results for repo patterns).
