# China self-help audio discovery prompt repair - Gemini Deep Research Version

Use Gemini Deep Research for broad synthesis, multi-source triangulation, and
high-signal decision support. Do not give generic advice. Do not produce a
surface overview. The goal is a decision-grade research report for Phoenix
Omega.

## Exact Research Objective

Prior Pearl_Research output for China self-help audio discovery was usable but too Western: it leaned on TikTok/Spotify assumptions, missed Xiaohongshu, Douyin, Bilibili, and Ximalaya evidence, and did not tell Phoenix Omega whether China metadata and funnel language should diverge from the global audiobook playbook.


## Business And System Context

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

## Failure Symptoms

- no Simplified Chinese source plan
- no platform policy/source provenance
- no comparison of Ximalaya vs Douyin vs Xiaohongshu
- generic "Gen Z likes authenticity" advice

## Decision The Operator Needs To Make

- Should China research be routed to Qwen / QuinChat first, and what should it ask so Phoenix Omega can decide whether to create China-specific metadata, consumer-language, and funnel configs?

## Questions Gemini Must Answer

- Should China research be routed to Qwen / QuinChat first, and what should it ask so Phoenix Omega can decide whether to create China-specific metadata, consumer-language, and funnel configs?

## Hypotheses To Test

- The current failure may be caused by: no Simplified Chinese source plan
- The current failure may be caused by: no platform policy/source provenance
- The current failure may be caused by: no comparison of Ximalaya vs Douyin vs Xiaohongshu
- Provider-native prompts may produce stronger evidence than a single generic prompt.
- The right answer may require preserving existing Phoenix Omega behavior while upgrading prompt quality before execution.
- Chinese-language sources may materially change the China recommendation.

## Required Comparisons

- Compare strong evidence vs weak or anecdotal evidence.
- Compare current Phoenix Omega behavior vs the evidence-backed target behavior.
- Compare platform-specific requirements and user behavior.
- Compare China-native evidence against global/English-language assumptions.

## Evidence Standards And Source Rules

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

Triangulate across primary sources, official platform documentation, current
market reports, credible trade publications, academic/industry research, and
high-signal practitioner evidence. Search beyond the obvious first-page
sources. Distinguish strong evidence, weak evidence, outdated evidence, and
inference.

## Markets, Locales, And Platforms

Markets:
- China

Locales:
- zh-CN

Platforms:
- Xiaohongshu
- Douyin
- Bilibili
- Ximalaya

## Constraints

- what platform/compliance constraints affect claims and title wording
- US-only Spotify advice
- generic TikTok marketing tips
- uncited claims about Chinese Gen Z

## Context From The Messy Session

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

Make the report decision-oriented. Explicitly surface contradictions,
tradeoffs, and uncertainty.
