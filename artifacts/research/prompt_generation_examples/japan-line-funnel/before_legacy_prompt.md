# Legacy Pearl_Research Prompt Preview: japan_line_funnel

This is the old direct research prompt shape assembled by `scripts/research/run_research.py` before the new brief/compiler layer.

## System

```text
You are a platform strategist for distribution and discovery (Pearl News plane).

Interpret raw signals for how titles, packaging, and channel behavior should shift for Gen Z vs Gen Alpha. When asked for structured output, obey the YAML schema in the YAML-only pass (/no_think).
```

## User Task

```text
Dimension 5.1 — Platform fit and packaging.

Use /think. From the raw data, infer which surfaces (short video, community, search, email) matter most and why.

Raw data:
Session notes:
The previous output was plausible but thin. It mixed US email funnel logic
into Japan, assumed generic "mobile-first" behavior, and did not prove
the LINE cadence or Rakuten/Amazon JP split with Japanese sources.

Failing output:
- no Japanese-language source requirement
- no LINE Official Account / LIFF / rich menu evidence
- no Rakuten Kobo vs Amazon JP vs Audible Japan comparison
- no language/register guidance for self-help funnel copy

Decision:
Should the Japan lane use Rakuten Chat AI / Japan-native deep research
before Phoenix changes config/funnel/line_jp/oa_brand_registry.yaml and
downstream metadata rules?

Missing evidence:
- current LINE OA read/click behavior
- Japanese self-help/audiobook discovery terms
- platform policy constraints and metadata norms
- what not to import from US email funnels

Do not include generic global advice. Surface contradictions and open risks.


---

Dimension 5.2 — Discovery and title angles.

Use /think. Propose discovery hypotheses and title-angle directions strictly grounded in the data.

Raw data:
Session notes:
The previous output was plausible but thin. It mixed US email funnel logic
into Japan, assumed generic "mobile-first" behavior, and did not prove
the LINE cadence or Rakuten/Amazon JP split with Japanese sources.

Failing output:
- no Japanese-language source requirement
- no LINE Official Account / LIFF / rich menu evidence
- no Rakuten Kobo vs Amazon JP vs Audible Japan comparison
- no language/register guidance for self-help funnel copy

Decision:
Should the Japan lane use Rakuten Chat AI / Japan-native deep research
before Phoenix changes config/funnel/line_jp/oa_brand_registry.yaml and
downstream metadata rules?

Missing evidence:
- current LINE OA read/click behavior
- Japanese self-help/audiobook discovery terms
- platform policy constraints and metadata norms
- what not to import from US email funnels

Do not include generic global advice. Surface contradictions and open risks.

```

## YAML Pass Instruction

```text
Using only the following analysis, output a single valid YAML object. No thinking, no markdown fences, only YAML.

Schema:
primary_surfaces: ["string"]
packaging_moves: ["string"]
discovery_hypotheses: ["string"]
title_angle_candidates: ["string"]

Analysis to convert to YAML:
{{ANALYSIS_SUMMARY}}
```
