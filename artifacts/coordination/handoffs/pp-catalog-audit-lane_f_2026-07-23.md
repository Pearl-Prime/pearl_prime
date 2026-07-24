# Pearl Prime Catalog Plan + Assembly Readiness Audit — Operator Handoff (2026-07-23)

This is the final handoff for a six-lane audit (Lanes A-F) answering the operator's questions about the Pearl
Prime en_US catalog: what's planned, whether Pearl_Editor content-authority enters the process at the right
point, whether plan+assembly is actually working at catalog scale, whether the persona/revenue mix is
deliberate, and whether EI v2 is genuinely wired in. **Every lane in this pack (A through F) is read-only —
zero atoms, config files, or pipeline code were changed. This is research and documentation only.**

Full synthesis report (all citations, full tables, cross-axis analysis):
`artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_f_synthesis/REPORT.md`

## Quick answers

1. **"What's the plan for the US market, across all brands?"** 32,401 book-plan files across 40 brand
   archetypes — not the 1,519/26-brand figure `docs/PROGRAM_STATE.md` currently states (stale ~15x). 37 of 40
   brands genuinely have ~800-845 books each. 3 brands have a broken series-plan import (not deliberate).
2. **"Is Pearl_Editor getting in the process at the right point?"** No — content-authority (story_atoms
   coverage) is only checked at render time, as a soft-skip that never blocks anything. Catalog admission never
   checks it at all.
3. **"Is our plan and assembly working, catalog-wide?"** Not remotely: 98.6% of the planned catalog is either
   capped at `structurally clear only` (Layer 1, no character bank — 70.6%) or predicted to fail the render
   preflight outright (27.9%). Only 1.4% even has the precondition for Layer 2 — and that's not a guarantee.
4. **"Are we making the majority of books to make money, with a spread to help — on purpose?"** Accident, not
   design. A real revenue-strategy document exists but is wired into zero production code. The actual mix is
   shaped by which persona/brand got built out first, not by any revenue or access decision.
5. **"Is EI v2 genuinely in the system?"** Partially. One real hard-gate is live (beat-order, plan-time); one
   fully-built hard-gate is disarmed (dimension gates, render-time); the one function built to feed EI v2 into
   plan-time atom selection has zero production callers.

## The one connecting thread

All five findings trace to the same root cause: **nothing in the production pipeline gates catalog admission
or atom selection on any signal at all — not content-authority, not craft quality, not revenue.** What ships is
purely a function of build-order/backfill timing. Fixing any one axis in isolation (e.g., arming the EI v2
render gate) would not change this pattern on its own.

## What needs your decision (not self-ratified by this pack)

- **Q-CATALOG-AUDIT-01** — should catalog admission flag (or withhold) cells with no story_atoms coverage?
  Recommended default: flag-only for now (withhold would currently shrink the catalog to ~9 admissible cells).
- **Q-CATALOG-AUDIT-02** — should the existing revenue-potential research get wired into book selection, with
  a floor guaranteeing under-served personas (e.g., first_responders) aren't just build-order accidents?
  Recommended default: yes, scoped small, with confidence tagging.
- **Q-CATALOG-AUDIT-03** — `docs/specs/EI_V2_STRENGTHENED_ARCHITECTURE_SPEC.md` has sat unratified 6 weeks.
  Recommended default: resolve its §13 open questions and ratify/reject before any further EI v2 wiring lane.
- **Q-CATALOG-AUDIT-04** — the ratified `CATALOG-800-PER-BRAND-01` cap (per-brand 800 is NOT the target) now
  contradicts the live catalog (39/40 brands do have ~800/brand). Recommended default: re-ratify to match
  reality; this is a documentation-accuracy fix, not a request to change target volume.

## Single highest-leverage next step

If only one follow-up lane should launch next: **author story_atoms for `corporate_managers`** — it's the
largest persona (3,743 planned books), has the worst tuple-viability failure rate (32.5%), and has zero
character bank today. This is a content-authoring lane (Pearl_Editor/Pearl_Writer), not a code change, and does
not require any of the four decisions above to start.

## What this pack did not cover

Locales beyond en_US; any live render/parity verification (everything here is static-analysis prediction,
except the 2026-07-22 pipeline audit's 3 previously-live-rescored samples, which this pack cites); manga,
audiobook, and music catalog axes.

## Signals

`lane-a-plan-inventory-merged=46d971d642cc4076d065a2466be9e55fb3f940cb`
`lane-b-editor-sequencing-merged=cfa68a3454aecd2722dfb365d1bb8c4af194cd16`
`lane-c-assembly-readiness-merged=a7933a689421cdc507ed32cff1443e9e0ad23839`
`lane-d-marketing-mix-merged=5a23ce384039e59f031bcb775a5a1269587ff848`
`lane-e-ei-v2-gap-merged=848c726c66a6cf82696d6810acd6ce91605a0488`
`lane-f-synthesis-merged=<filled at merge>`
