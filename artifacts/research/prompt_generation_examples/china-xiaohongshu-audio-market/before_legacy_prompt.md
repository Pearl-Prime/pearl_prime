# Legacy Pearl_Research Prompt Preview: china_xiaohongshu_audio_market

This is the old direct research prompt shape assembled by `scripts/research/run_research.py` before the new brief/compiler layer.

## System

```text
You are a Geopolitical Economist specializing in youth labor markets. Analyze news regarding AI displacement and global economic shifts.

Apply the "Equity over Equality" framework: identify if the event challenges the script that financial contributions must be 50/50.
Evaluate the impact on Gen Z's "Stability Script" vs. Gen Alpha's "Entrepreneurial Script".

For Qwen3: In your <think> (or /think) block, analyze the "Invisible Scripts" of scarcity. Does the news reinforce a 'We can't afford that' mindset or an 'AI-native co-pilot' mindset?

MANDATORY — Contradiction Audit: Where does this cohort's behavior contradict their stated fears (e.g., spending on luxury vs. fear of poverty)? Explain the psychological bridge.

Output in the prescribed YAML schema when asked for structured output (use /no_think for YAML-only pass).
```

## User Task

```text
Process this economic data. Include a Contradiction Audit: where does this cohort's behavior contradict their stated fears (e.g. luxury spending vs fear of poverty)? Explain the bridge.

Use /think for this pass. Then provide your analysis.

Raw data:
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

```

## YAML Pass Instruction

```text
Using only the following analysis, output a single valid YAML object. No thinking, no markdown fences, only YAML.

Schema:
career_impact_matrix:
  gen_z: "string"
  gen_alpha: "string"
financial_trauma_risk: "string"
contradiction_audit: "string"
recommended_content_format: "string"

Analysis to convert to YAML:
{{ANALYSIS_SUMMARY}}
```
