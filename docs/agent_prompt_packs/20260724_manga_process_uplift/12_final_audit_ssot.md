# EXECUTE — Lane 12 — Final audit + SSOT update

**AGENT:** Pearl_PM · **SUBSYSTEM:** manga_pipeline + repo coordination · **WAVE:** 4

## GATE CHECK
Run only after every other lane is terminal (signal emitted, or BLOCKED with pushed work +
handoff). The dispatcher hands you the lane→signal table; re-verify EVERY signal against live
origin/main yourself (`git log origin/main --oneline | head -40`, PR pages) — relayed prose is
not a signal surface.

## EXECUTION CONTRACT (binding, in-band)
- EXECUTE end-to-end; terminal = signal token or ONE BLOCKER. STARTUP_RECEIPT / CLOSEOUT_RECEIPT.
- You are the serial owner of hot coordination files for this pass: `docs/PROGRAM_STATE.md`,
  `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`, `CANONICAL_ARTIFACTS_REGISTRY.tsv`,
  `docs/DOCS_INDEX.md`. One PR, plumbing pattern, explicit paths, staged-diff gate, preflight.
- Landing: MERGED or BLOCKED. Cleanup ledger + handoff
  `artifacts/coordination/handoffs/manga_process_uplift_lane12_2026-07-24.md`.

## MISSION
1. **Verify, don't collect:** for each of lanes 01–11, byte-verify the deliverable exists on
   origin/main (spot-open files, run one validator per code lane: e.g.
   `python3 scripts/ci/check_manga_series_master_plan.py <golden>`,
   `python3 scripts/manga/validate_story_excellence.py <pilot ep>`); record PASS/FAIL per lane.
   A lane whose signal exists but whose artifact fails verification is reported BROKEN, loudly.
2. **Registry + index:** land the requested registry rows (master-plan contract, checklists yaml,
   mc checklists, demand-rollup schema, 3 skills) in `CANONICAL_ARTIFACTS_REGISTRY.tsv`; DOCS_INDEX
   rows for the new specs/skills; close/update the pack's workstream rows in
   `ACTIVE_WORKSTREAMS.tsv`.
3. **PROGRAM_STATE manga row update** — the drift-critical part. Rewrite the Manga row to
   reflect post-pack truth with acceptance layers named per deliverable: research=RESEARCHED
   (list the 3 studies), contracts/gates=SPECCED/CODE-WIRED, pilot=<the layer Lane 11 actually
   emitted>, bubble-v2/storyboard-gate=on-main-per-Lane-01, R3 audit discrepancy=resolved-with-
   pointer. State explicitly: **PROVEN-AT-BAR still NO** — blind-10 scorecards remain the M6
   blocker; name the 2 pilot episodes as candidates. Update the "Next manga blocker" line to the
   true post-pack order (expected: blind-10 judging + M5 bank fill for the pilot series + master-
   plan scale-out wave; re-derive from what actually landed).
4. **False-premise sweep (§11 corollary):** any doc/memory-visible source still carrying a
   premise this pack disproved (e.g. "vessels unwired", "no arc-cadence data", "fixed 12-ep
   arcs") gets a dated correction or superseded banner — list every correction in the closeout.
5. **Enforcement-promotion check (§14):** confirm each fixed drift class got its gate (checklist
   mutation tests, master-plan validator, storyboard consumption regression). Any lesson living
   only in prose → file it as a named follow-up with owner.

## CLOSEOUT
```
CLOSEOUT_RECEIPT
AGENT: Pearl_PM (final audit)
COMMIT_SHA: <full SHA of the coordination PR>
LANE_VERDICTS: <12 rows: lane / signal / byte-verified PASS|FAIL|BLOCKED>
ACCEPTANCE_LAYERS: <per deliverable, honest>
CORRECTIONS: <false-premise fixes landed>
FOLLOW_UPS: <named, with owner: blind-10 judging (M6), bank fill (M5), master-plan scale-out, Q-MPU ratifications outstanding>
NEXT_ACTION: <one line for the operator>
manga-process-uplift-audited=<full merge SHA>
```
