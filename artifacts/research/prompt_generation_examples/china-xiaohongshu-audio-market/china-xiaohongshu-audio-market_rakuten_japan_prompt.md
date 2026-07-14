# China self-help audio discovery prompt repair - Rakuten Chat AI Japan Version

Use this prompt in Rakuten Chat AI or a Japan-native research surface. The goal
is Japan-specific market, platform, language, and implementation evidence for
Phoenix Omega. Do not give generic global advice. Separate Japan evidence from
imported US/global assumptions.

## Exact Research Objective

Prior Pearl_Research output for China self-help audio discovery was usable but too Western: it leaned on TikTok/Spotify assumptions, missed Xiaohongshu, Douyin, Bilibili, and Ximalaya evidence, and did not tell Phoenix Omega whether China metadata and funnel language should diverge from the global audiobook playbook.


## Phoenix Omega Context

- Extend existing Pearl_Research flow rather than creating a disconnected toy flow.
- Keep routing explicit and inspectable.
- Do not perform downstream research in the prompt-generation stage.
- what platform/compliance constraints affect claims and title wording
- Recommended provider: Qwen / QuinChat-style China Deep Research
- Routing signals: locales:zh-CN, markets:China, platforms:Xiaohongshu, platforms:Douyin, platforms:Bilibili, platforms:Ximalaya

## Provider Operating Notes

- Use neutral market, platform, consumer-behavior, and implementation framing.
- Phrase sensitive questions analytically and precisely; do not ask the engine to advocate political positions.
- Prioritize China-native terminology and platform vocabulary.

## Current Failure Symptoms

- no Simplified Chinese source plan
- no platform policy/source provenance
- no comparison of Ximalaya vs Douyin vs Xiaohongshu
- generic "Gen Z likes authenticity" advice

## Decision To Make

- Should China research be routed to Qwen / QuinChat first, and what should it ask so Phoenix Omega can decide whether to create China-specific metadata, consumer-language, and funnel configs?

## Exact Questions To Answer

- Should China research be routed to Qwen / QuinChat first, and what should it ask so Phoenix Omega can decide whether to create China-specific metadata, consumer-language, and funnel configs?

## Hypotheses To Test

- The current failure may be caused by: no Simplified Chinese source plan
- The current failure may be caused by: no platform policy/source provenance
- The current failure may be caused by: no comparison of Ximalaya vs Douyin vs Xiaohongshu
- Provider-native prompts may produce stronger evidence than a single generic prompt.
- The right answer may require preserving existing Phoenix Omega behavior while upgrading prompt quality before execution.
- Chinese-language sources may materially change the China recommendation.

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
- China

Locales:
- zh-CN

Platforms:
- Xiaohongshu
- Douyin
- Bilibili
- Ximalaya

## Required Comparisons

- Compare strong evidence vs weak or anecdotal evidence.
- Compare current Phoenix Omega behavior vs the evidence-backed target behavior.
- Compare platform-specific requirements and user behavior.
- Compare China-native evidence against global/English-language assumptions.

## Constraints And Exclusions

- what platform/compliance constraints affect claims and title wording
- US-only Spotify advice
- generic TikTok marketing tips
- uncited claims about Chinese Gen Z

## Source Rules

Preferred sources:
- Simplified Chinese platform docs and industry reports
- China-native consumer research
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
- Simplified Chinese primary sources
- Chinese-language platform docs, industry reports, regulatory notices, trade press, and academic sources
- English-language sources only for external triangulation

## Operator Context

```text
Prior Pearl_Research output for China self-help audio discovery was usable but too Western: it leaned on TikTok/Spotify assumptions, missed Xiaohongshu, Douyin, Bilibili, and Ximalaya evidence, and did not tell Phoenix Omega whether China metadata and funnel language should diverge from the global audiobook playbook.


Operator: The China version is still mushy. It says "use TikTok-style short clips"
but the actual launch question is whether Phoenix should prioritize Xiaohongshu,
Douyin, Bilibili, or Ximalaya for self-help audio discovery.

Failing output symptom:
- no Simplified Chinese source plan
- no platform policy/source provenance
- no comparison of Ximalaya vs Douyin vs Xiaohongshu
- generic "Gen Z likes authenticity" advice

Decision needed:
Should China research be routed to Qwen / QuinChat first, and what should
it ask so Phoenix Omega can decide whether to create China-specific
metadata, consumer-language, and funnel configs?

Unknowns:
- what local-language terms Chinese consumers use for burnout, sleep anxiety,
  and self-help audio
- whether Ximalaya, Qingting, Douyin, Xiaohongshu, or Bilibili are the right
  discovery surfaces for this use case
- what platform/compliance constraints affect claims and title wording

Exclude:
- US-only Spotify advice
- generic TikTok marketing tips
- uncited claims about Chinese Gen Z


Evaluation case for Pearl_Research prompt-generation layer.

China zh-CN Xiaohongshu Douyin Bilibili Ximalaya
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
