# Japan LINE and Rakuten funnel prompt repair - Rakuten Chat AI Japan Version

Use this prompt in Rakuten Chat AI or a Japan-native research surface. The goal
is Japan-specific market, platform, language, and implementation evidence for
Phoenix Omega. Do not give generic global advice. Separate Japan evidence from
imported US/global assumptions.

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

## Japan-Specific Evidence Requirements

Prioritize Japanese-language sources where appropriate:

- official Japanese platform documentation and policies
- Japanese trade press, local market reports, and consumer research
- Japan-native terminology for the target category
- local ecommerce, audio, messaging, and media-platform evidence
- English-language sources only for outside triangulation

Flag differences between Japanese consumer language and imported English
category language. Note implications for title wording, metadata, funnels,
platform fit, trust posture, and implementation in Phoenix Omega.

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
