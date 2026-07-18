# Handoff — Lane 06 · Pearl_PM · Synthesis + SSOT sync + replay runbook (2026-07-19)

**Agent:** Pearl_PM
**STATUS:** completed (synthesis + source-correction + SSOT sync + replay runbook landed offline)
**Offline parent tip at land:** `9f8a857e6dcdc5fb15e98eab8df4856cf6a5d391`
**Shared tree:** `codex/realist-social-samples-20260718` (never switched)
**GitHub:** re-checked live this turn — still 403 account-suspended (`git fetch origin`, `gh api user`).

## Gate check

All three lane signals confirmed present on `pearlstar_offline/brand-wizard-verify-20260719` before
writing SSOT, re-verified against durable evidence (not relayed prose):

- `bw-yaml-market-verified=d796e3fac58e962fb2b0a039922201cbac1cdcda` (+ `bw-market-fix-landed` same)
- `bw-teacher-exclusivity-doctrine-verified=9f8a857e6dcdc5fb15e98eab8df4856cf6a5d391`
- `bw-director-page-and-books-fixed=9756ebbc8890f7e9fb656ee54d1fee7238d5c454`

## What this lane did

1. **Synthesis doc** — `artifacts/qa/brand_wizard_verification_synthesis_2026-07-19.md`: 11-row
   behavior→verdict→evidence table, plain-language answers to the 5 operator asks, operator-belief
   reconciliation ("no TW wizard" / "market code missing" / doctrine-fallback / atom sufficiency),
   fixed-vs-open summary, cheap re-proofs performed this turn, 3 named follow-ons.
2. **Source-corrected stale premises** — the pack's own `INDEX.md` ground-truth table already
   carried the "no TW wizard" / "market code missing" corrections from the dispatcher; this lane
   additionally promoted both corrections into `docs/PROGRAM_STATE.md` (the actual program SSOT,
   read before any doc that disagrees with it) so the correction is not stranded in a pack-scoped
   file only Pearl_PM sessions read.
3. **SSOT sync:**
   - `docs/PROGRAM_STATE.md` — new "2026-07-19 Brand wizard onboarding" subsection with the 9-row
     verdict table, belief corrections, follow-ons. **Did NOT bump the top "LAST VERIFIED
     origin/main SHA" line** — nothing merged to `origin/main`.
   - `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` — +7 rows (3 lane rows `landed_offline`
     /`landed_offline_partial`, 1 lane06 row, 3 `proposed` follow-on rows), schema-conformant
     (15 tab-separated columns matching header).
   - `artifacts/coordination/operator_decisions_log.tsv` — +3 rows (`OPD-BW-01` market-capture fix
     scope, `OPD-BW-02` doctrine-fallback verdict honesty, `OPD-BW-03` phantom-books real-asset-gate
     scope), write-time-computed IDs (unused `OPD-BW-*` prefix confirmed before use), binary-append
     preserving the file's existing `\n`-only line endings.
   - `artifacts/coordination/pearlstar_offline/LEDGER.tsv` — fixed the pre-existing malformed lane03
     row (was missing 3 trailing tab-separated columns) to `replay_status=pending`; added lane01 and
     lane02 rows, also `replay_status=pending`.
4. **Replay+deploy runbook** — `docs/runbooks/BRAND_WIZARD_GITHUB_RETURN_REPLAY_2026-07-19.md`:
   exact wake steps (fetch verify → branch/replay → regression tests → ONE PR → governance →
   merge → **then** the CF Pages GH-Actions-gated deploy → mandatory verify-live screenshot step
   per the browser-verification runbook). Explicit non-actions list. Follow-ons folded in.
5. **Pack INDEX status** — `docs/agent_prompt_packs/20260719_brand_wizard_verify/INDEX.md` Wave 4
   marked LANDED-OFFLINE with pointers to all synced artifacts.

## Landing mechanics

Plumbing commit onto the offline tip using an isolated `GIT_INDEX_FILE` seeded via `git read-tree`
from the offline tip's own tree, then `git add` of only the explicit new/changed paths (content read
from the shared working tree on disk), `git write-tree` + `git commit-tree` with the offline tip as
sole parent, then `git update-ref` — the checked-out `codex/realist-social-samples-20260718` branch
was never touched (no checkout, no `git add -A`, no worktree).

**Important divergence note:** `docs/PROGRAM_STATE.md` and
`artifacts/coordination/operator_decisions_log.tsv` on the shared working tree (based on
`codex/realist-social-samples-20260718` HEAD) had already diverged from the offline branch's own
copies of those same files (the offline branch descends from an older `origin/main` point,
`9e9b9e6067…`, and never inherited later main-lineage edits to those two files). To avoid smuggling
~150 lines of unrelated main-lineage drift into this offline branch, this lane extracted **only the
new brand-wizard content** (the new PROGRAM_STATE subsection; the 3 new OPD-BW rows) and applied it
on top of the **offline tip's own prior version** of each file, not the working-tree version. This
keeps the offline branch's diff scoped to exactly this pack's contribution.
`artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` had NOT diverged (byte-identical base on both sides
before this lane's edit), so its 7 new rows were applied directly from the working-tree copy.

## Evidence

`artifacts/qa/brand_wizard_verification_synthesis_2026-07-19.md` (this lane's primary output);
re-opened `MARKET_CAPTURE_MATRIX.md`, `name_occurrence_report.json`, `ops_url_fix_proof.json`,
`catalog_bearing_fail_closed.json` this turn as cheap re-proofs (see synthesis doc "Re-verification
performed this turn").

## Cleanup

- No worktrees created.
- No `git add -A` — every plumbing-commit path was explicit.
- Shared tree stayed on `codex/realist-social-samples-20260718`.
- No servers/processes started by this lane (coordination-class, no code executed).

## NEXT_ACTION

1. Operator/Pearl_GitHub: on `github-suspension-lifted`, execute
   `docs/runbooks/BRAND_WIZARD_GITHUB_RETURN_REPLAY_2026-07-19.md`.
2. Follow-on lane: wire onboarding 409 `teacher_claimed` → generalized-doctrine offer.
3. Follow-on lane: full spine-chord A/B production proof for `master_feung` after persona/coverage
   alignment.
4. Follow-on lane: sibling-surface phantom-book audit (`brand_admin.html` direct, storefront, GHL
   feed, exec dashboard).

## SIGNAL

`bw-verify-closeout=<see CLOSEOUT_RECEIPT for this turn's exact landing SHA>`
