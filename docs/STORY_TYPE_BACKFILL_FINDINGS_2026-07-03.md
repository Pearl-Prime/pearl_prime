# Story-Type Backfill — findings (Phase 3)

**Author:** Pearl_Architect · **Date:** 2026-07-03 · deterministic, no LLM
**Scope:** `docs/STORY_TYPE_ENFORCEMENT_SCOPE_2026-07-03.md` Phase 3 (#4596). Tool: `scripts/atom_writing/classify_story_types.py`.

## What ran
Classified and tagged all **218 persona STORY pools** (`atoms/<persona>/<topic>/STORY/CANONICAL.txt`, 3,746 story variants) with a deterministic `story_type` per `docs/STORY_TYPES_AND_STRUCTURES.md`, injected into each block's metadata:
```
STORY_TYPE: <type>
STORY_TYPE_SOURCE: heuristic_v1   # machine-classified, reviewable/overridable
```
The CANONICAL.txt parser ignores unknown meta keys, so the tags are format-safe (parse-sweep clean, block counts preserved) and forward-compatible. The linter's CANONICAL path now **consumes** the tag (§7 conformance + §3 naming apply to pools).

## The distribution (the honest finding)

| story_type | variants | share |
|---|---|---|
| character_study | 3,226 | **86%** |
| atmospheric | 516 | 14% |
| direct_teaching | 4 | 0% |
| parable / recognition_exchange | 0 | 0% |

**Two real gaps, now measured and enforceable (not just recalled):**
1. **Naming debt = 2,938 atoms.** Of 3,226 character_study atoms, only **288 are NAMED**; **2,938 are unnamed** ("She/He") → each raises `CHARACTER_STUDY_UNNAMED` (WARN). This is the exact worklist for the naming authoring the whole thread pointed to — now a countable CI signal, not a memory.
2. **Near-zero type variety.** The catalog is ~86% one type. `docs/STORY_TYPES_AND_STRUCTURES.md` §9 targets 2–3 distinct types per book; most books will raise `LOW_STORY_TYPE_VARIETY` (WARN). The parable / recognition_exchange / direct_teaching types are essentially unused catalog-wide.

## Honest caveats
- `STORY_TYPE_SOURCE: heuristic_v1` — these are **machine tags, not human-reviewed**. character_study is the structural default for third-person character vignettes (which is most of the corpus); an author pass may re-type some (e.g. sensory-only openers → atmospheric).
- Conformance is **clean** on the pools (character_study/atmospheric are valid types; pools carry no story_origin, so the composite/principle rules don't trigger) — the gate stays green. The naming/variety signals are **WARN, report-only** — they do not block.

## What this changes
The story-quality gaps that were narrative claims across #4592/#4594/#4595/#4596 are now **numbers a gate can watch**: 2,938 unnamed character studies + near-zero variety. The remaining work is the **naming/individuation authoring** lane (Pearl_Writer / Claude-writes) — add named protagonists to the deep-but-unnamed character studies — measured down by re-running the linter.

## Reproduce
```bash
PYTHONPATH=. python3 scripts/atom_writing/classify_story_types.py            # dry-run distribution
PYTHONPATH=. python3 phoenix_v4/quality/story_atom_lint.py \
  --path atoms/corporate_managers/burnout/STORY/CANONICAL.txt --json-out /tmp/x.json  # see CHARACTER_STUDY_UNNAMED
```
