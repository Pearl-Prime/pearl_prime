# RCG-017 — Brand archetype taxonomy sourcing (MEDIUM)

**Audit ref:** `RESEARCH_AUDIT_2026_03_30.md` section A item 17
**Source file:** `config/brand_registry.yaml`
**Claim:** Brand archetype definitions — no sourced basis for archetype taxonomy
**Research query:** brand archetype Jung Pearson applied publishing 2024

---

## Claim analysis

The brand registry YAML defines brand archetypes (e.g., Sage, Healer, Warrior, Explorer) used to classify and position audiobook brands. These archetype names and definitions echo established marketing frameworks but the YAML does not cite the theoretical or practical source of the taxonomy.

## Research findings

### Foundational archetype theory

1. **Jung, Carl G. (1959/1969).** *The Archetypes and the Collective Unconscious.* Collected Works, Vol. 9, Part 1. Princeton University Press. Jung's original theory of universal archetypes as recurring patterns in the collective unconscious. This is the theoretical root of all brand archetype frameworks.

2. **Campbell, Joseph (1949).** *The Hero with a Thousand Faces.* Pantheon Books. Extended Jungian archetypes into narrative structure (the monomyth/hero's journey), influential in brand storytelling.

### Brand archetype frameworks

3. **Mark, Margaret & Pearson, Carol S. (2001).** *The Hero and the Outlaw: Building Extraordinary Brands Through the Power of Archetypes.* New York: McGraw-Hill. ISBN: 978-0-071-36415-1. **This is the most widely cited brand archetype framework in marketing.** Defines 12 archetypes: Innocent, Explorer, Sage, Hero, Outlaw, Magician, Regular Guy/Gal, Lover, Jester, Caregiver, Creator, Ruler. Most brand archetype systems in practice derive from or adapt this framework.

4. **Pearson, Carol S. (1991).** *Awakening the Heroes Within: Twelve Archetypes to Help Us Find Ourselves and Transform Our World.* HarperOne. ISBN: 978-0-062-50678-9. Earlier Pearson work mapping 12 archetypes to personal development — bridges Jung to applied brand/marketing use.

### Application in publishing and content marketing

5. **Hartwell, M. & Chen, J. C. (2012).** *Archetypes in Branding: A Toolkit for Creatives and Strategists.* HOW Books/F+W Media. ISBN: 978-1-440-33506-1. Practical toolkit extending the Pearson framework to brand identity design, including publisher and content brands.

6. **No published study was found** applying brand archetypes specifically to audiobook or self-help publishing taxonomy. The repo's taxonomy appears to be an **internal adaptation** of the Mark & Pearson framework (or a similar 12-archetype model) tailored to the audiobook catalog's brand positioning needs.

## Verdict

**PARTIALLY_CONFIRMED** — The brand archetype taxonomy has clear theoretical roots in Jung (1959) and applied marketing roots in Mark & Pearson (2001). The specific archetype names and definitions in `brand_registry.yaml` appear to be an internal adaptation of these established frameworks. The framework itself is well-sourced; the specific application to audiobook brands is internal.

## Recommendation

Add a provenance comment to `config/brand_registry.yaml`:
```yaml
# Brand archetype taxonomy adapted from:
# - Jung, C. G. (1959). The Archetypes and the Collective Unconscious.
# - Mark, M. & Pearson, C. S. (2001). The Hero and the Outlaw. McGraw-Hill.
# Internal adaptation for audiobook brand positioning.
# Specific archetype-to-brand mappings are editorial decisions, not research-validated.
```

## Citations

```yaml
_source:
  study: "Jung 1959, Collected Works Vol 9; Mark & Pearson 2001, The Hero and the Outlaw, McGraw-Hill; Pearson 1991, Awakening the Heroes Within"
  note: "Framework well-sourced (Jung/Pearson tradition). Specific audiobook application is internal adaptation."
  date: "2026-04-01"
```
