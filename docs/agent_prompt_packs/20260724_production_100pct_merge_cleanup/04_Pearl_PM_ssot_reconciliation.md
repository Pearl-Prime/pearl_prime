# EXECUTE — Lane 04 (Pearl_PM × Pearl_Architect): Coordination SSOT reconciliation

This is an execution prompt, not a planning request. End state: **PROGRAM_STATE.md,
ACTIVE_PROJECTS.tsv, ACTIVE_WORKSTREAMS.tsv, SUBSYSTEM_AUTHORITY_MAP.tsv, and
DOCS_INDEX.md all reconciled to 2026-07-24 truth and MERGED** (single docs PR).

## Contract (in-band)
- STARTUP_RECEIPT: branch, HEAD SHA, `git status --short | head`, `gh auth status`,
  `git fetch origin && git log origin/main -1 --oneline`.
- Wait for Lane 02's `PIPER100-L02-MAIN-GREEN` before merging; author immediately.
  Fold in Lane 01's merge ledger before finalizing (poll the dispatcher).
- Every SHA/PR/status you write into the SSOT is a CLAIM you must have re-verified
  live this session (`gh pr view`, `git log origin/main`). The SSOT's value is that
  it is TRUE — a stale-but-confident row is worse than no row.
- These are HOT governance files (serial-lane rule): take this lane solo, branch
  fresh off origin/main immediately before push, rebase-and-retry on conflict rather
  than force.
- Reuse-first: EDIT the canonical files in place. Do not create any new state doc,
  registry, or parallel index. The pack's SYSTEMS_STATE_2026-07-24.md is your source
  material, not a new SSOT — it stays a dated snapshot.
- Preflight + merge rules as standard (push_guard, preflight_push, pre_merge_check,
  governance review; squash-merge pre-authorized when green).
- Layer-honest: use the repo's own vocabulary in every status you write
  (structurally clear / authored candidate / system working / bestseller register;
  manga ABSENT→…→PROVEN-AT-BAR). Never write "done" for a gate-PASS.

## Authority reads
`docs/PROGRAM_STATE.md` (full), `docs/PEARL_ARCHITECT_STATE.md` (§cap entries),
`artifacts/coordination/ACTIVE_PROJECTS.tsv`, `ACTIVE_WORKSTREAMS.tsv`,
`SUBSYSTEM_AUTHORITY_MAP.tsv`, `docs/DOCS_INDEX.md`, and this pack's
`SYSTEMS_STATE_2026-07-24.md`. DISCOVERY REPORT: list every drift you will fix
(expected ≥ the five below) with provenance, BEFORE editing.

## Known drifts to fix (verify, then correct)
1. **ACTIVE_PROJECTS.tsv** — add rows for the 4 orphan project_ids referenced by
   workstreams: `PRJ-JAPAN-MANGA-ONLY-CATALOG-V1`, `PRJ-PEARL-PRIME-Q-GATES`,
   `proj_integrations_20260719`, `proj_manga_100pct_certification_20260703`
   (derive owner/status from their workstream rows + handoffs; if a project is
   actually dead, mark its workstreams superseded instead — don't invent life).
2. **SUBSYSTEM_AUTHORITY_MAP.tsv** — add the missing `social_media` row (owner per
   PROGRAM_STATE's social-atom-bank section; authority doc = the vibe-schema spec
   from cap `SOCIAL-ATOM-BANK-VIBE-01`).
3. **ACTIVE_WORKSTREAMS.tsv** — status-refresh only rows you can verify: mark
   completed what Lane 01's ledger + merged PRs prove (e.g. zh-TW program rows,
   manga pilot rows); mark superseded the #55/#131-era rows. Do NOT touch rows you
   can't verify — note them in a "needs owner review" list in the PR body.
4. **PROGRAM_STATE.md** — new "LAST VERIFIED 2026-07-24 @ <origin/main SHA>" pass:
   fold in (a) #234 supersession of #131/#231/#235, (b) manga pilot 3 cells/37 eps
   EXECUTED-REAL on main (#275), (c) zh-TW quality program COMPLETE, (d) brand-wizard
   regression + Lane 05 outcome, (e) main-green + branch-protection outcome from
   Lane 02, (f) the open-PR truth table replaced by Lane 01's end state, (g) purge
   the ex-#5237/#5206 stale numbers it already flags.
5. **DOCS_INDEX.md** — refresh (last update 2026-06-17): add the 07-22→24 handoffs,
   the two July prompt packs (20260723 waystream, 20260724 this one), the manga
   re-audit, PR #199's CI-gate doctrine. Judge staleness by authority+refs, not
   git-dates (mega-commit reset dates on 468/518 docs).
6. **Known-good anchors** — append (never rewrite) new anchors to CLAUDE.md's
   anchor section + the memory mirror if warranted by this wave (e.g. manga pilot
   verification SHA, CI-green SHA from Lane 02).

## Closeout
```
CLOSEOUT_RECEIPT: PIPER100-L04-DONE
pr: <#, squash SHA>
drifts_fixed: <numbered list matching discovery report>
rows_added/updated: <counts per file>
needs_owner_review: <unverifiable workstream rows>
program_state_verified_at: <origin/main SHA>
NEXT_ACTION: <...>
```
Append a dated note to this pack's INDEX.md.
