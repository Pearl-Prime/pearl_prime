# {{PROMPT_TITLE}} - Qwen / QuinChat China Version

Use this prompt in a Qwen or QuinChat-style China research engine. The goal is
China-native market, platform, consumer, and implementation evidence for
Phoenix Omega. Do not give generic Western advice. Do not answer from memory
alone.

Frame the task as neutral market and implementation research. Use analytically
precise language. For sensitive or regulatory topics, ask for evidence,
constraints, market behavior, official rules, and source disagreement rather
than advocacy or opinion.

## Exact Research Objective

{{RESEARCH_OBJECTIVE}}

## Phoenix Omega Context

{{SYSTEM_CONTEXT}}

## Provider Operating Notes

{{PROVIDER_STYLE_NOTES}}

## Current Failure Symptoms

{{FAILURE_SYMPTOMS}}

## Decision To Make

{{DECISION_TO_MAKE}}

## Exact Questions To Answer

{{EXACT_QUESTIONS}}

## Hypotheses To Test

{{HYPOTHESES_TO_TEST}}

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

{{MARKETS_LOCALES_PLATFORMS}}

## Required Comparisons

{{REQUIRED_COMPARISONS}}

## Constraints And Exclusions

{{CONSTRAINTS_AND_EXCLUSIONS}}

## Source Rules

{{SOURCE_RULES}}

## Operator Context

```text
{{RAW_CONTEXT_EXCERPT}}
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
