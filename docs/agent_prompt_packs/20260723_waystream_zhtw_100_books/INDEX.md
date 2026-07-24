# Waystream zh-TW 100-Book QA Batch Prompt Pack

## Program

- **Goal:** Produce 100 real zh-TW EPUBs across the Waystream Sanctuary catalog
  (`config/source_of_truth/book_plans_en_us/way_stream_sanctuary__*.yaml`, 800 cells) as
  an explicit **QA / pipeline-capacity stress batch** — Waystream is normally treated as
  an en-US brand; this program does NOT ratify a commercial zh-TW Waystream launch. Real
  production gates run (no shortcuts), but output lands under a QA-labeled path, not the
  live brand_deliveries/GHL commercial-attach convention.
- **Source request:** Operator, 2026-07-23, via Piper: "make 100 zh-tw books of all sorts
  for waystream sanctuaries band in zh-tw, even though it's eng brand for qa, use pipeline."
- **Router date:** 2026-07-23
- **Live origin/main anchor:** `1f5217edb5` (re-verify at dispatch time — this program
  moved multiple PRs/hour on 2026-07-22/23; treat as stale on sight)
- **Prompt count:** 5 (00 dispatcher + 01 prereq + 02 smoke + 03 pilot + 04 scale,
  04 fans to 6 parallel batch instances)
- **Master dispatcher:** `00_MASTER_DISPATCH_PROMPT.md`

## Why this isn't a flat 100-way fan-out

A prior sibling lane already tried book #1 (PR #211, OPEN, docs-only): cell
`gen_z_professionals × overthinking × spiral` was correctly zh-TW-clean and
tuple-viable, but the production chord hard-failed on `EXERCISE-BANK-RESOLUTION-01`
— confirmed **cell-independent** (reproduced on a second unrelated cell). A code fix
exists (PR #223, OPEN) but is blocked from merging by an unrelated pre-existing
red-on-main issue (4 zh-CN stub files, fix is PR #131, OPEN). Even after #223 merges,
the same first cell hits a further, unfixed accent-planner supply gap
(`AUTHOR_DISCLOSURE`) before it produces a real EPUB. **Zero zh-TW Waystream books
currently complete the pipeline.** Dispatching 100 parallel builds today reproduces
100 identical failures. Sequence: unblock → prove one cell ships → pilot → scale.

## Wave Order

- **Wave 0:** Land the EXERCISE-classifier fix chain (`01`) — verify/merge #131, verify
  #223 goes green, merge #223. Gate: `exercise-classifier-fix-merged=<sha>`.
- **Wave 1 (smoke):** Ship ONE real zh-TW EPUB — the same cell PR #211 already scoped
  (`02`) — diagnosing/fixing whatever gate comes next (AUTHOR_DISCLOSURE accent supply,
  or others). This supersedes/closes PR #211. Gate: `zhtw-smoke-cell-shipped=<sha>`.
- **Wave 2 (pilot):** 9 more diverse cells, 1 PR, stratified across personas (`03`).
  Gate: `zhtw-pilot-10-shipped=<sha>`.
- **Wave 3 (scale):** 90 more cells across 6 parallel batch lanes (`04`, ~15 cells/PR,
  stratified ~7 cells per persona across all 14 personas) to reach 100 total.

## Lane Matrix

| Prompt | Agent | Lane | Owner | Substrate | Depends on | Output tags | Hot files |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | Pearl_GitHub | prereq-unblock | Pearl_GitHub | github_actions | none | `exercise-classifier-fix-merged=<sha>` | PR #131, PR #223 (review/merge only, no new code) |
| 02 | Pearl_Localization | smoke | Pearl_Localization | local + github_actions | 01 signal | `zhtw-smoke-cell-shipped=<sha>` | PR #211 (supersede/close), `phoenix_v4/planning/accent_planner*` if a real fix is needed |
| 03 | Pearl_Localization | pilot-10 | Pearl_Localization | local + github_actions | 02 signal | `zhtw-pilot-10-shipped=<sha>` | `artifacts/qa/waystream_zhtw_100_books_20260723/` |
| 04 | Pearl_Localization ×6 | scale-batch-{A..F} | Pearl_Localization | local + github_actions | 03 signal | `zhtw-scale-batch-{A..F}-shipped=<sha>` | same QA dir, disjoint cell lists per batch |

## Deconfliction

- **Open PRs checked (2026-07-23, `1f5217edb5`):** #211 (this program's own smoke
  precursor — supersede, don't duplicate), #223 (the fix this program depends on —
  land, don't re-author), #131 (unrelated stub fix gating #223 — land, don't
  re-diagnose), #93/#162 (zh-TW backlog reconciliation — read-only input, don't touch).
- **Active workstreams checked:** no existing ACTIVE_WORKSTREAMS.tsv row for a
  "100 zh-TW books" or "Waystream zh-TW" program as of this pack's authoring — Wave 0
  lane opens the row.
- **Shared files:** `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`,
  `docs/PROGRAM_STATE.md` — ONE serial actor at a time (append your row, don't rewrite
  others' rows); `phoenix_v4/planning/enrichment_select.py` /
  `phoenix_v4/planning/registry_resolver.py` — do not re-touch these in Waves 1-3, they
  belong to PR #223's already-landed fix.
- **Serialization rule:** Wave 0 must fully land (signal emitted, both PRs merged)
  before Wave 1 starts. Wave 1's smoke cell must ship (signal emitted) before Wave 2
  starts. Wave 2's pilot batch must ship before any Wave 3 batch starts. Wave 3's 6
  batch lanes are mutually independent (disjoint cell lists) and may run in parallel.

## Evidence Requirements

- **Tests:** existing test suites for #131/#223 must stay green; no new pipeline code
  is expected in Waves 1-3 (translation/authoring/QA-artifact work only) — if a lane
  discovers it needs a real code fix (like Wave 1 might, for the next gate after
  EXERCISE), treat that as its own narrowly-scoped PR, not an atom/translation change.
- **Proof roots:** `artifacts/qa/waystream_zhtw_100_books_20260723/<persona>__<topic>__<engine>/`
  per book — `assembly_trace.md`, `locale_fallback_report.json`,
  `enrichment_audit.json`, register_gate output, `TRACE_SUMMARY.md`.
- **PR/merge signals:** see Output tags column above — every wave emits a named,
  greppable signal on a durable surface (merged PR / PROGRAM_STATE), never prose.
- **Operator approvals:** none required to execute (QA framing is already the
  operator's own instruction) — but see 04's "commercial-attach" DO NOT; that step
  DOES need a fresh operator ask if anyone ever proposes it later.
- **Final audit:** a closing lane (end of Wave 3) tallies real shipped count vs. 100,
  lists any cells that never cleared gates, and updates `docs/PROGRAM_STATE.md`
  Localization section with the honest total (do not round up to "100" if fewer
  actually shipped clean).

## Cleanup Requirements

Every lane reports: worktree removed or HOLD path/reason; local branch deleted or HOLD
reason; remote branch deleted after merge or HOLD reason; scratch files removed;
background jobs stopped or declared; handoff file path
(`artifacts/coordination/handoffs/<lane_id>_2026-07-23.md`).

## Final Status

- Status: not yet dispatched
- Blockers: PR #131 → #223 merge chain must land before Wave 1 can start
- Next action: paste `00_MASTER_DISPATCH_PROMPT.md` into the lead agent
