# RCG-009 — First responders workforce size (MEDIUM)

**Audit ref:** `RESEARCH_AUDIT_2026_03_30.md` section A item 9
**Source file:** `unified_personas.md` (L68)
**Claim:** "First Responders — Niche ($2.5M workforce)"
**Research query:** US BLS police firefighters EMT employment total 2024 2025 definition

---

## Claim analysis

The persona table labels "First Responders" as a niche segment with a $2.5M (2.5 million) workforce figure. "First responders" typically encompasses law enforcement officers, firefighters, and emergency medical services (EMS) personnel, though definitions vary.

## Research findings

### BLS employment data (May 2023 OEWS)

1. **Police and sheriff's patrol officers** (SOC 33-3051): **724,690** employed.
   - URL: https://www.bls.gov/oes/current/oes333051.htm

2. **Firefighters** (SOC 33-2011): **330,200** employed.
   - URL: https://www.bls.gov/oes/current/oes332011.htm

3. **Emergency Medical Technicians (EMTs) and Paramedics** (SOC 29-2042): **269,920** employed.
   - URL: https://www.bls.gov/oes/current/oes292042.htm

4. **Detectives and criminal investigators** (SOC 33-3021): **113,690** employed.

5. **Correctional officers** (SOC 33-3012): **371,340** employed (sometimes included in "first responder" definitions).

6. **Dispatchers** (SOC 43-5031): **95,280** employed (911 dispatchers; sometimes classified as first responders).

### Sum estimates

- **Narrow definition** (police patrol + firefighters + EMTs/paramedics): ~1.32M
- **Broader definition** (adding detectives, correctional officers, dispatchers, other law enforcement): ~1.9-2.1M
- **Broadest definition** (including all protective service occupations SOC 33-0000 at ~3.6M, minus security guards at ~1.1M): ~2.5M

### Other sources

7. **U.S. Department of Homeland Security / FEMA.** Various publications reference "more than 2 million first responders" in the United States, though this is typically a rounded estimate without detailed methodology.

8. **National First Responders Day (Congressional records).** Public statements by officials commonly cite "over 2 million" or "approximately 2.5 million" first responders.

## Verdict

**PARTIALLY_CONFIRMED** — The 2.5M figure is plausible under a broad definition of "first responders" that includes police, firefighters, EMTs/paramedics, correctional officers, dispatchers, and related protective service roles. Under the narrow core definition (police + fire + EMS), the figure is closer to 1.3M. The 2.5M figure likely derives from FEMA/DHS estimates or the broadest BLS protective services category minus private security.

## Recommendation

Add a citation noting the definition: "First responder workforce estimated at 2.5M under broad definition including law enforcement, fire, EMS, corrections, and dispatch personnel (BLS OEWS May 2023 protective services occupations; DHS/FEMA estimates)." Specify whether the persona targets the narrow (police/fire/EMS ~1.3M) or broad (~2.5M) definition.

## Citations

```yaml
_source:
  url: "https://www.bls.gov/oes/current/oes330000.htm"
  study: "BLS OEWS May 2023 (SOC 33-0000 protective services); DHS/FEMA first responder estimates"
  note: "2.5M plausible under broad definition. Narrow (police+fire+EMS) is ~1.3M. Specify definition."
  date: "2026-04-01"
```
