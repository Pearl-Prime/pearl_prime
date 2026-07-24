# Manga Structural Composition MVP — V1 Spec

**Status:** SPECCED (gt30d C01 · 2026-07-22)  
**Keepers:** I042  
**Owner:** Pearl_Architect (Claude) → Cursor D06 implements smoke/pilot only  
**Acceptance layer for this doc:** SPECCED — not CODE-WIRED, not EXECUTED-REAL, not PROVEN-AT-BAR

## 0. Purpose

Define the minimum structural-composition contract so manga panels can be checked for
**support surfaces, contact regions, support edges, and relation-specific geometry**
before claiming layered assembly quality.

Cite: manga vision-conformance doctrine
(`artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md`,
`docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md` if present),
`MANGA_LAYER_RENDER_CONTRACT_SPEC` / V5 layered architecture. Do **not** present
text-to-image single-shot pages as layered panels.

## 1. Six-layer honesty

Any status claim for this MVP must name one of:
`ABSENT → RESEARCHED → SPECCED → CONFIG-EXISTS → CODE-WIRED → EXECUTED-REAL → PROVEN-AT-BAR`.

This document reaches **SPECCED** only.

## 2. MVP objects

| Object | Meaning | MVP requirement |
|---|---|---|
| support_surface | Stable plane a figure/object rests on | Required for standing/sitting poses |
| contact_region | Region where two entities touch | Required when relation implies contact |
| support_edge | Edge used for lean/brace | Required for lean/brace relations |
| relation_check | Named geometric predicate | Fail closed in pilot if predicate missing |

## 3. Acceptance for Cursor D06 (smoke → pilot)

### Smoke
- Module or script can load a panel manifest and report missing MVP objects as structured errors.
- No claim of EXECUTED-REAL.

### Pilot
- One series/episode authored story (≥6 panels) runs the checker.
- INTERIM layers labeled `provenance: INTERIM`; never presented as final art.
- Byte/stub gates remain enforced (`check_render_progress_bytes`, `check_manga_story_authored`).

### Out of scope for MVP
- Full PassB reading-graph (see C02).
- Catalog-scale render.
- Blind PROVEN-AT-BAR judgment.

## 4. Cursor-may-implement checklist

1. [ ] Add checker under `scripts/manga/` (reuse assemble/bank paths; no parallel render stack).
2. [ ] Smoke on one synthetic panel JSON.
3. [ ] Pilot on one authored episode; stop on systemic failure.
4. [ ] CLOSEOUT names acceptance layer honestly.
5. [ ] Do not edit RENDER_PROGRESS bytes to pass gates.

## 5. Signal

`gt30d-c01-spec-terminal` when this file lands on a branch/main or LANDED-OFFLINE.
