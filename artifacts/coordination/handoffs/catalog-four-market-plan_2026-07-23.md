# Handoff — catalog-four-market-plan (2026-07-23)

**Lane:** `catalog-four-market-plan`
**Agent:** Pearl_GitHub
**Branch:** `agent/catalog-four-market-plan-20260723`
**Base:** `origin/main` @ `0ce62bca0533e3b919f42a668456b60f8d6f716e`

## What this lane did

Re-derived, live and independently, the per-locale catalog materialization state for all 14
registered markets, using `git ls-files` (tracked state only, not raw-disk `find`/`ls`, which is
inflated by untracked scratch in shared checkouts — see the audit doc Section 5 for why that
distinction mattered mid-session). This corrects/confirms a pasted operator closeout whose two
cited "delivered" commit SHAs do not resolve anywhere in this repo's history.

**Finding: the closeout's 4-market numeric table (ja_JP 269 manga plans / ko_KR 266 / zh_TW 274,
all three missing text plans; zh_HK neither) is accurate** once re-derived via `git ls-files`. Its
sourcing (the two commit SHAs) could not be verified and should not be repeated as fact — nothing
matching its claimed deliverable exists on `origin/main`, and no PR (`gh pr list --search`) proposes
one.

## Deliverables (this lane, audit + plan only — no content authored)

1. `docs/specs/CATALOG_FOUR_MARKET_COMPLETION_PLAN.md` — live 14-market table, governed
   ja_JP -> ko_KR -> zh_TW -> zh_HK sequencing, CI rule (cites existing
   `scripts/ci/check_title_language_conformance.py` gate 34 — no new script needed), explicit
   non-goals (does not lift the ko_KR `hold_pending_market_clearance` hold; does not author content).
2. `artifacts/qa/catalog_four_market_audit_20260723/SUMMARY.md` — full live-derivation evidence,
   command list, and the closeout diff table.
3. `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` — new row
   `ws_catalog_four_market_completion_plan_20260723` under the existing
   `proj_manga_catalog_reconciliation_20260426` project (did not create a new project).
4. `artifacts/coordination/ACTIVE_PROJECTS.tsv` — updated that project's `active_workstreams` and
   `next_action` columns to reference the new workstream.

## Key correction to internalize

- **Do not use raw `find`/`ls` counts against `config/source_of_truth/book_plans_*` or
  `manga_series_plans/*` as a materialization proxy in this repo right now** — multiple concurrent
  agent worktrees/sessions can leave large amounts of untracked scratch in shared checkouts (this
  session found ~32,000 untracked files under `book_plans_ja_jp` alone in the *shared* checkout at
  `/Users/ahjan/phoenix_omega`, versus 0 tracked). Always use `git ls-files` scoped to the branch
  you actually intend to report on, and always confirm you are operating in your own isolated
  worktree, not a shared checkout, before trusting `find`/`ls` output for anything.
- ja_JP/ko_KR/zh_TW's existing manga "plans" are auto-generated listing scaffolds
  (`title: TBD`), not authored stories — CONFIG-EXISTS layer only, sampled not exhaustively verified.

## Standing constraints carried forward (not resolved by this lane)

- ko_KR: `distribution_status: hold_pending_market_clearance` (D-18, Korea AI Act) — do not lift;
  operator/legal-tier call.
- zh_TW: ~15 open zh-TW-specific translation-QA PRs at audit time (#61/#62/#67/#68/#69/#72/#78/#80/
  #87/#88/#90/#91/#92/#93/#131) — any future zh_TW content-authoring stage of this plan must
  sequence behind those, not run in parallel against the same files.

## Next owner / next action

Stage 1 (ja_JP) content-authoring is the next concrete step, owned by a translation/content lane
(`translate-ja` / Pearl_Writer, Tier-1 per CLAUDE.md LLM Tier Policy) — not this lane, which is
audit + plan only. See `docs/specs/CATALOG_FOUR_MARKET_COMPLETION_PLAN.md` Section 6 for the
concrete next-actions list.

## Acceptance layer (name it honestly)

This lane produced an **authored plan + corrected audit** — RESEARCHED/SPECCED layer. It is not
progress on the underlying catalog (zero content authored, zero materialization counts changed).
