# Global social media pipeline research prompt repair - Qwen / QuinChat China Version

Use this prompt in a Qwen or QuinChat-style China research engine. The goal is
China-native market, platform, consumer, and implementation evidence for
Phoenix Omega. Do not give generic Western advice. Do not answer from memory
alone.

Frame the task as neutral market and implementation research. Use analytically
precise language. For sensitive or regulatory topics, ask for evidence,
constraints, market behavior, official rules, and source disagreement rather
than advocacy or opinion.

## Exact Research Objective

Phoenix Omega needs a global deep-research prompt to decide how to build a reusable book-to-social pipeline across YouTube Shorts, Instagram, TikTok, Pinterest, and email without overfitting to one platform.


## Phoenix Omega Context

- Extend existing Pearl_Research flow rather than creating a disconnected toy flow.
- Keep routing explicit and inspectable.
- Do not perform downstream research in the prompt-generation stage.
- what should be excluded from automation because it needs human review
- Recommended provider: Gemini Deep Research
- Routing signals: locales:en-US, markets:Global

## Provider Operating Notes

- Prioritize broad synthesis and multi-source triangulation.
- Look for contradictions across high-authority and niche sources.
- Return decision-oriented synthesis, not a source dump.

## Current Failure Symptoms

- no decision framework for which platforms get which content shapes
- no evidence-backed cadence or asset-sizing recommendations
- no comparison between educational clips, quote cards, carousel posts, freebie captures, and email proof-loop reuse
- no source-quality rules

## Decision To Make

- What should Phoenix Omega automate first: extraction, captions, image generation, video assembly, scheduling, or analytics feedback?

## Exact Questions To Answer

- What should Phoenix Omega automate first: extraction, captions, image generation, video assembly, scheduling, or analytics feedback?

## Hypotheses To Test

- The current failure may be caused by: no decision framework for which platforms get which content shapes
- The current failure may be caused by: no evidence-backed cadence or asset-sizing recommendations
- The current failure may be caused by: no comparison between educational clips, quote cards, carousel posts, freebie captures, and email proof-loop reuse
- Provider-native prompts may produce stronger evidence than a single generic prompt.
- The right answer may require preserving existing Phoenix Omega behavior while upgrading prompt quality before execution.

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
- Global

Locales:
- en-US

Platforms:
- YouTube Shorts
- Instagram
- TikTok
- Pinterest
- Email

## Required Comparisons

- Compare strong evidence vs weak or anecdotal evidence.
- Compare current Phoenix Omega behavior vs the evidence-backed target behavior.
- Compare platform-specific requirements and user behavior.

## Constraints And Exclusions

- what should be excluded from automation because it needs human review
- single-platform hacks
- generic content marketing advice

## Source Rules

Preferred sources:
- official platform docs
- credible creator economy reports
- current benchmark studies with methods
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
- English-language primary sources
- Local-language sources when the market context calls for them

## Operator Context

```text
Phoenix Omega needs a global deep-research prompt to decide how to build a reusable book-to-social pipeline across YouTube Shorts, Instagram, TikTok, Pinterest, and email without overfitting to one platform.


Messy session:
Pearl_Research came back with a decent but shallow summary: "repurpose
book content into social posts." That is not enough for implementation.

What is broken:
- no decision framework for which platforms get which content shapes
- no evidence-backed cadence or asset-sizing recommendations
- no comparison between educational clips, quote cards, carousel posts,
  freebie captures, and email proof-loop reuse
- no source-quality rules

Decision needed:
What should Phoenix Omega automate first: extraction, captions, image
generation, video assembly, scheduling, or analytics feedback?

Unknowns:
- what current platform mechanics matter in 2026
- which formats lead to owned-list capture instead of vanity engagement
- what should be excluded from automation because it needs human review

Good output should include implementation implications for Phoenix Omega,
tables, recommended action, open risks, and provenance.


Evaluation case for Pearl_Research prompt-generation layer.

Global en-US YouTube Shorts Instagram TikTok Pinterest Email
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
