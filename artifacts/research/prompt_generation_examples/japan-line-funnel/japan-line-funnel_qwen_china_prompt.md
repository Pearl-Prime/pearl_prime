# Japan LINE and Rakuten funnel prompt repair - Qwen / QuinChat China Version

Use this prompt in a Qwen or QuinChat-style China research engine. The goal is
China-native market, platform, consumer, and implementation evidence for
Phoenix Omega. Do not give generic Western advice. Do not answer from memory
alone.

Frame the task as neutral market and implementation research. Use analytically
precise language. For sensitive or regulatory topics, ask for evidence,
constraints, market behavior, official rules, and source disagreement rather
than advocacy or opinion.

## Exact Research Objective

Pearl_Research needs a stronger Japan-native prompt before deciding how Phoenix Omega should update the Japan LINE freebie funnel, Rakuten Kobo positioning, and audiobook metadata assumptions.


## Phoenix Omega Context

- Extend existing Pearl_Research flow rather than creating a disconnected toy flow.
- Keep routing explicit and inspectable.
- Do not perform downstream research in the prompt-generation stage.
- platform policy constraints and metadata norms
- Do not include generic global advice. Surface contradictions and open risks.
- Recommended provider: Rakuten Chat AI / Japan-native Deep Research
- Routing signals: locales:ja-JP, markets:Japan, platforms:LINE, platforms:Rakuten, platforms:Rakuten Kobo, platforms:Audible Japan, platforms:Amazon JP

## Provider Operating Notes

- Use Japan-native market terminology and platform names.
- Separate imported global advice from Japan-specific evidence.
- Flag language/register and cultural-fit implications for Phoenix Omega.

## Current Failure Symptoms

- no Japanese-language source requirement
- no LINE Official Account / LIFF / rich menu evidence
- no Rakuten Kobo vs Amazon JP vs Audible Japan comparison
- no language/register guidance for self-help funnel copy

## Decision To Make

- Should the Japan lane use Rakuten Chat AI / Japan-native deep research before Phoenix changes config/funnel/line_jp/oa_brand_registry.yaml and downstream metadata rules?

## Exact Questions To Answer

- Should the Japan lane use Rakuten Chat AI / Japan-native deep research before Phoenix changes config/funnel/line_jp/oa_brand_registry.yaml and downstream metadata rules?

## Hypotheses To Test

- The current failure may be caused by: no Japanese-language source requirement
- The current failure may be caused by: no LINE Official Account / LIFF / rich menu evidence
- The current failure may be caused by: no Rakuten Kobo vs Amazon JP vs Audible Japan comparison
- Provider-native prompts may produce stronger evidence than a single generic prompt.
- The right answer may require preserving existing Phoenix Omega behavior while upgrading prompt quality before execution.
- Japanese-language sources may materially change the Japan recommendation.

## China-Specific Evidence Requirements

Prioritize Simplified Chinese sources where appropriate:

- official platform documentation and policies
- Chinese-language industry reports and trade press
- Chinese market data and consumer research
- platform-native evidence from relevant China platforms
- regulatory or official notices where relevant
- English-language sources only for outside triangulation

Explicitly separate mainland China evidence from Hong Kong, Taiwan, Singapore,
or global Chinese-language evidence when those differ.

## Markets, Locales, Platforms

Markets:
- Japan

Locales:
- ja-JP

Platforms:
- LINE
- Rakuten Kobo
- Audible Japan
- Amazon JP

## Required Comparisons

- Compare strong evidence vs weak or anecdotal evidence.
- Compare current Phoenix Omega behavior vs the evidence-backed target behavior.
- Compare platform-specific requirements and user behavior.
- Compare Japan-native evidence against imported US/global assumptions.

## Constraints And Exclusions

- platform policy constraints and metadata norms
- Do not include generic global advice. Surface contradictions and open risks.
- generic global funnel advice
- US-only email marketing benchmarks

## Source Rules

Preferred sources:
- Japanese-language platform docs
- Japanese market reports and trade press
- official platform documentation and policy pages
- primary market data, filings, or regulator publications
- credible industry reports and trade press
- academic or practitioner research with transparent methods

Acceptable sources:
- credible news analysis with named sources
- platform-native examples when clearly labeled as examples
- expert commentary only when triangulated against stronger sources

Weak sources:
- unsourced trend roundups
- affiliate SEO posts
- single-anecdote social media claims
- AI-generated summaries without source URLs

Source languages:
- Japanese-language primary sources
- Japanese market terminology, platform docs, trade press, and local consumer research
- English-language sources only for external triangulation

## Operator Context

```text
Pearl_Research needs a stronger Japan-native prompt before deciding how Phoenix Omega should update the Japan LINE freebie funnel, Rakuten Kobo positioning, and audiobook metadata assumptions.


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


Evaluation case for Pearl_Research prompt-generation layer.

Japan ja-JP LINE Rakuten Kobo Audible Japan Amazon JP
```

## Required Output

Return:

1. Executive summary
2. Direct answer to the operator's real question
3. Evidence-backed findings
4. Contradictions / ambiguities
5. Recommended action
6. Implementation implications for Phoenix Omega
7. Open risks
8. Provenance / sources

Surface contradictions, tradeoffs, and uncertainty. Include source titles,
URLs, publication dates when available, and note when a source is translated.
