# Catalog 800 Autogenerator — V1 Spec

**Status:** SPECCED (gt30d Wave-B C03 · 2026-07-22)  
**Keepers:** I030  

## Purpose
Replace hand-edited high_confidence catalog configs with a deterministic generator for pilot cells — not a silent full-catalog rewrite.

## Constraints
- Smoke → pilot (≤10 cells) before scale
- Output must carry acceptance layer labels
- No public publish authorization from this spec

## Cursor-may-implement
1. Generator script + fixture pilot
2. Diff against existing high_confidence if present

## Signal
`gt30d-wb-c03-spec-terminal`
