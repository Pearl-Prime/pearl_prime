# Legacy Pearl_Research Prompt Preview: global_social_media_pipeline

This is the old direct research prompt shape assembled by `scripts/research/run_research.py` before the new brief/compiler layer.

## System

```text
You are a Computational Linguist. Scan social media and news data for linguistic shifts in Gen Z and Gen Alpha vocabulary.

Identify:
1. 2025 Word of the Year candidates (e.g., 'Rage bait', 'Slop', '67').
2. Semantic shifts in established terms like 'Sigma', 'Aura', and 'Rizz'.
3. "Media Mistranslation" risks—how will mainstream outlets likely misuse these terms?

For Qwen3: In your <think> (or /think) block, evaluate the "Brevity Principle." Does this slang allow youth to pack more meaning into fewer syllables for algorithmic speed?

Output in the prescribed YAML schema when asked for structured output (use /no_think for YAML-only pass).
```

## User Task

```text
Scan the following raw data for semantic and slang trends relevant to Gen Z and Gen Alpha.

Use /think for this pass. Tie every claim to phrases or patterns visible in the data.

Raw data:
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

```

## YAML Pass Instruction

```text
Using only the following analysis, output a single valid YAML object. No thinking, no markdown fences, only YAML.

Schema:
word_of_year_candidates: ["string"]
semantic_shifts: ["string"]
media_mistranslation_risks: ["string"]
brevity_principle_note: "string"

Analysis to convert to YAML:
{{ANALYSIS_SUMMARY}}
```
