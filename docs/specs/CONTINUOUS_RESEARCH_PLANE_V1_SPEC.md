# Continuous Research Plane — V1 Spec

**Status:** SPECCED (gt30d Wave-B C01 · 2026-07-22)  
**Keepers:** I015  
**Reuse:** `scripts/research/research_prompt_builder.py`, `docs/research/PEARL_RESEARCH_PROMPT_GENERATION_LAYER.md`

## Purpose
Turn one-shot research briefs into a **scheduled cadence** (weekly/nightly) that emits prompt packs / digests without inventing a parallel research stack.

## Cadence (default)
| Slot | Owner | Output |
|---|---|---|
| Weekly | Pearl_Research | refreshed prompt pack under `docs/agent_prompt_packs/` or `artifacts/research/` |
| On-demand | operator | single `research_prompt_builder` run |

## Cursor-may-implement
1. Thin scheduler stub / runbook (GitHub Actions optional; prefer PearlStar if unattended).
2. No paid LLM APIs in unattended path (Tier-2 Gemma/Qwen only if automated).

## Signal
`gt30d-wb-c01-spec-terminal`
