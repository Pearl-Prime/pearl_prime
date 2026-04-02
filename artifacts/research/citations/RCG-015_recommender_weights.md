# RCG-015 — Recommender scoring weights provenance (MEDIUM)

**Audit ref:** `RESEARCH_AUDIT_2026_03_30.md` section A item 15
**Source file:** `config/recommender/` (scoring weights if present)
**Claim:** Scoring weights provenance — hand-tuned vs. evidence-based: unable to verify (no citation system in config)
**Research query:** recommendation system hybrid weights calibration A/B benchmark

---

## Claim analysis

The audit flags that recommender configuration files under `config/recommender/` may contain scoring weights (for content recommendation, catalog ordering, or persona matching) without any documentation of whether those weights are derived from A/B testing, published recommendation system research, or hand-tuned internal estimates.

## Research findings

### Recommender system weight calibration — academic

1. **Koren, Y., Bell, R., & Volinsky, C. (2009).** "Matrix Factorization Techniques for Recommender Systems." *Computer*, 42(8), 30-37. IEEE. Foundational paper on collaborative filtering weights — demonstrates that weight calibration in recommender systems requires iterative optimization against real user interaction data.

2. **Burke, R. (2002).** "Hybrid Recommender Systems: Survey and Experiments." *User Modeling and User-Adapted Interaction*, 12(4), 331-370. Reviews hybrid recommender architectures where multiple signal types (collaborative, content-based, knowledge-based) are combined via weighted schemes. Weight selection is identified as a key design decision requiring empirical tuning.

3. **Rendle, S. (2010).** "Factorization Machines." *Proceedings of the IEEE International Conference on Data Mining (ICDM)*, 995-1000. Describes learned weight systems for feature interactions in recommendation — weights are optimized through training, not manually set.

### Industry practice

4. **Netflix Technology Blog, Spotify Engineering Blog, Amazon Science publications** consistently describe weight calibration as an empirical, data-driven process involving A/B testing and online learning. No major recommender system relies on manually set, un-documented weights in production.

5. **For early-stage or content-first systems** (like a book/audiobook catalog without large user interaction datasets), **hand-tuned weights based on editorial judgment** are a common starting point. This is a legitimate engineering practice but should be documented as such.

### Assessment

Without inspecting the specific YAML files (which the audit notes may or may not contain weights), the concern is about **provenance documentation**, not about the weights being wrong. If the system is pre-launch or has limited user data, hand-tuned weights are expected. The issue is that they are not labeled as such.

## Verdict

**NEEDS_PRIMARY_SOURCE** — This is a documentation gap rather than a factual claim to verify. If weights exist in `config/recommender/`, they need provenance labels indicating whether they are:
- Hand-tuned editorial defaults (acceptable for early-stage systems)
- Derived from A/B testing (cite the test IDs and dates)
- Based on published research (cite the papers)
- Optimized through model training (cite the training run)

## Recommendation

For each weight block in `config/recommender/*.yaml`, add:
```yaml
_source:
  note: "Internal calibration — editorial default. No A/B test data. Review with user interaction data when available."
  date: "2026-04-01"
```
Or, if weights are research-based:
```yaml
_source:
  study: "[Paper/method name]"
  note: "Weight derived from [method]. Last calibrated [date]."
```

## Citations

```yaml
_source:
  study: "Koren et al. 2009, IEEE Computer 42(8); Burke 2002, UMUAI 12(4)"
  note: "NEEDS_PRIMARY_SOURCE — recommender weights need provenance labels. Hand-tuned defaults are acceptable for early-stage but must be documented."
  date: "2026-04-01"
```
