# Atom Cohesion — Chunk: Adjacency selector + dwell craft gate

**Status:** GATED, post-flip AND post-composer-lane. Fire when (a) first R2 EPUB batch ships AND (b) OPD-20260629-002 (#3110/#3123) has landed.
**Lane:** Atom Cohesion (chunked plan A–F). Sequenced AFTER the thesis de-templating chunk.
**Authored:** 2026-06-30. Persisted from session for durability; scheduled via Jul 1 runbook backlog.

---

```
ROLE: Pearl_Dev. /Users/ahjan/phoenix_omega. GPU-free, NO paid LLM. STAGE a PR. Atom Cohesion lane.

=== GATE (STOP if unmet) ===
- DO NOT FIRE until BOTH: (a) flip first-EPUB-batch shipped (freeze lifted), AND (b) the OPD-20260629-002
  composer lane PRs (#3110/#3123) touching enrichment_select.py have LANDED — you cannot edit that file in
  parallel with them. If #3110/#3123 still open, STAND DOWN and report "serialized behind composer lane."
- Prompt 1 (thesis de-templating) should have landed first — the adjacency penalty needs varied pools to pick
  from. If Prompt 1 not landed, run against current pools but note the limitation.

=== PROBLEM ===
The selector picks each chapter's atoms (bridge/scene-anchor/thesis) without looking at the PREVIOUS chapter's
selections → within-book repetition (1281 MEDIUM in the sweep). And chapters sit side-by-side rather than
building on each other (the operator's #1 craft concern: integration-pacing / dwell).

=== READ FIRST ===
- artifacts/atom_cohesion/SELECTOR_DIAGNOSIS.md (the existing diagnosis — build on it).
- phoenix_v4/planning/enrichment_select.py + variation_selector.py (the selection path).
- phoenix_v4/quality/register_gate.py (dwell/F13 — composer-lane-owned; see deconfliction) +
  register_output_strengthen.py.
- artifacts/qa/plan_scale_qa_sweep_20260630/ repetition detector (reuse it as the before/after measure).
- Project memory [Integration-pacing priority] (dwell-beat craft gate + pin in OVERLAY_SPEC),
  [Atom cohesion chunked plan], [#1590 CANONICAL over-match regression] (selector changes are regression-prone).

=== MISSION ===
Make the selector adjacency-aware (anti-within-book repetition) and add a dwell/integration-pacing craft check
so chapters integrate prior material. Deterministic; no LLM.

=== DELIVERABLES ===
1. Adjacency penalty in the selector: when choosing a chapter's atoms, penalize candidates too similar
   (token/semantic overlap) to the previous chapter(s)' selected fragments. Prefer adding this to
   variation_selector.py / a new selector helper to MINIMIZE enrichment_select.py edits (composer-lane overlap).
2. Dwell / integration-pacing craft gate: a check that flags chapters which restart vs build on prior material.
   If it belongs in register_gate.py (composer-lane resource), COORDINATE with OPD-20260629-002 — add it as a
   separate gate module they review, do NOT double-edit register_gate.py.
3. Validate: rebuild a 12-ch book; repetition census drops vs 20260630 baseline; register still PASS; no
   CANONICAL over-match regression (run the relevant tests — see [#1590] memory).
4. Pin the dwell-beat requirement in the overlay spec per [Integration-pacing priority].

=== DECONFLICTION (HARD) ===
- enrichment_select.py + register_gate.py are OPD-20260629-002's live resources. Serialize behind their landed
  PRs; isolate your changes to variation_selector.py / a new module wherever possible; coordinate any shared-file
  edit. `gh pr list --search "enrichment_select OR register_gate OR adjacency OR cohesion" --state all`.

=== DO NOT ===
- Do NOT edit enrichment_select.py or register_gate.py in parallel with the composer lane.
- Do NOT use paid/GPU LLM. Do NOT git add -A. Do NOT ship a selector change without the regression tests green.

=== DISCOVERY REPORT (before coding) ===
Where the adjacency penalty plugs in (and how it avoids the composer-lane files); the similarity metric;
the dwell-gate placement + coordination plan with OPD-20260629-002; your before/after repetition measure.

=== GOLDEN BRANCH + PR ===
Branch agent/adjacency-cohesion-selector-<date> off origin/main. push-guard + preflight + check_rap_compliance.

=== CLOSEOUT_RECEIPT ===
STATUS · full SHA · PR# · adjacency penalty location + metric · dwell gate placement + composer-lane coordination
· repetition census before→after · register PASS maintained · regression tests green (incl. CANONICAL over-match)
· overlay spec pinned · DECISIONS + alt · NEXT_ACTION.
```
