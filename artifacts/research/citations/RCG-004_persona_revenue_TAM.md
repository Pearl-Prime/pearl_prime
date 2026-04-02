# RCG-004 — Persona revenue TAM estimates (HIGH)

**Audit ref:** `RESEARCH_AUDIT_2026_03_30.md` section A item 4
**Source file:** `unified_personas.md` (L57-68 table)
**Claim:** Revenue estimates: `$130-165M`, `$80-120M`, `$60-100M`, `$70-100M`, `$165M+`, `$50-80M` — no methodology disclosed
**Research query:** audiobook self-help US TAM SAM methodology syndicated OR document internal model assumptions

---

## Claim analysis

The persona table in `unified_personas.md` assigns specific dollar-range revenue estimates to six persona segments (millennial_women_professionals, tech_finance_burnout, entrepreneurs, working_parents, gen_x_sandwich, corporate_managers). These ranges total roughly $555-730M in aggregate. No methodology, data sources, or assumptions are documented.

## Research findings

### U.S. audiobook market sizing

1. **Audio Publishers Association (APA) & Edison Research (2024).** Annual audiobook survey. Reports U.S. audiobook revenue at approximately **$2.0-2.2 billion** in 2024 (exact figure varies by source year). The self-help/personal development segment is typically 10-15% of the audiobook market.

2. **Grand View Research (2024).** "U.S. Audiobooks Market Size, Share & Trends Analysis Report." Estimates the U.S. audiobook market at approximately $5.4 billion by 2030 (broader definition including educational and business). Self-help is a leading genre but market share percentages vary.

3. **IBISWorld (2024).** Audiobook publishing market reports. Consistent with $1.8-2.2B U.S. audiobook market range.

### Self-help audiobook segment

4. **BookScan / Circana (2024).** Print + audio data shows self-help/self-improvement as a top-5 audiobook genre by revenue, but precise segment revenue figures are behind paywalls. Industry estimates suggest self-help audiobooks are roughly $200-350M of the U.S. audiobook market.

### Assessment of the persona revenue figures

If the total U.S. self-help audiobook market is ~$200-350M, then the persona table's aggregate of $555-730M **exceeds the entire U.S. self-help audiobook market** and likely represents a broader **total addressable market (TAM)** that includes:
- Print and ebook revenue in addition to audiobook
- Adjacent categories (wellness, business, mindfulness)
- Potential international reach

Without documented methodology, it is impossible to verify whether these figures represent:
- Pure audiobook revenue (unlikely given the totals)
- Multi-format revenue (print + digital + audio)
- TAM vs. SAM vs. SOM
- U.S.-only or global

## Verdict

**NEEDS_PRIMARY_SOURCE** — The revenue estimates cannot be verified or refuted because no methodology is disclosed. The aggregate ($555-730M) substantially exceeds the likely U.S. self-help audiobook market ($200-350M), suggesting either a broader TAM definition, multi-format inclusion, or aspirational figures. Without knowing the assumptions, these numbers risk misleading downstream catalog and investment decisions.

## Recommendation

1. **Add a methodology paragraph** to `unified_personas.md` explaining: market definition (audiobook-only vs multi-format), geography, data sources (syndicated reports, internal modeling), and year.
2. **If internal estimates**: Label explicitly as "provisional internal estimate — not independently validated" with an owner and date.
3. **If sourced from a syndicated report**: Cite the specific report, table, and page number.
4. Consider adding a `_source:` block to any companion YAML echoing these figures.

## Citations

```yaml
_source:
  study: "APA/Edison Research audiobook survey 2024; industry self-help audiobook segment ~$200-350M estimate"
  note: "NEEDS_PRIMARY_SOURCE — persona revenue ranges ($555-730M aggregate) exceed likely U.S. self-help audiobook market. Methodology undisclosed. Label as provisional or cite source."
  date: "2026-04-01"
```
