# Prompt Pack — Brand Wizard end-to-end verification + two fixes (2026-07-19)

**Program goal:** Verify — with real executed evidence, not dispatch/keystroke — that the
brand wizard correctly (1) creates a brand YAML and connects it to a brand on activation,
(2) assigns that brand to the RIGHT global market (JP vs zh-CN vs zh-TW vs zh-SG — same
language, different markets), (3) puts teacher-chosen brands into teacher mode, enforces
one-teacher-per-global-market, and falls a second claimant back to the teacher's GENERAL
doctrine atoms (teachings without the name) instead of the named atoms, (4) opens the Brand
Director operations page for the exact brand the wizard created, and (5) shows ONLY real
downloadable assets — never phantom/planned books. Where a behavior is broken or missing,
land the scoped fix (offline-substrate; GitHub 403); where it is correct, land executed proof.

**Router live-truth anchor (2026-07-19):**
- `git fetch origin` + `gh` = **BLOCKED — GitHub 403 account suspension** (standing).
- Best local anchor: `origin/main` = `9e9b9e606791590337cd7d0f2fb425def2e6f760`.
- Working tree = shared dirty checkout on `codex/realist-social-samples-20260718`.
- Disk ~7 GiB free → NO new worktrees, NO full checkouts; plumbing commits only.
- CF deploy caveat (`reference_brand_wizard_cf_deploy`): CF Pages deploys via GitHub Actions;
  local tokens auth-fail on Pages REST — and GH Actions is itself blocked by the 403. So all
  verification runs against a LOCAL served build or the already-live CF URL (read-only); any
  fix lands offline-substrate for later replay-deploy. Do not attempt a live CF deploy this pack.

**Source request:** operator asked to verify the brand-wizard → YAML → brand-market assignment
chain, teacher-mode + per-market teacher uniqueness + named-vs-doctrine-atom fallback, correct
brand-director-page routing, and to STOP showing planned-but-not-created books as available.

## Ground truth (router discovery, 2026-07-19 — every claim re-verified by each lane)

| Behavior | Live state | Real paths |
|---|---|---|
| Wizard → YAML → brand assignment | BUILT | `server/routes/brand_onboarding.py` (`POST /api/v1/onboarding/submit`); writes `submissions/<date>/<brand_id>__<email>.yaml` + `roster_assignments.yaml` |
| Locale wizards | `wizard.html`, `wizard-ja.html`, `wizard-tw.html`, `wizard-zh.html` all EXIST (TW exists — operator belief "no TW wizard" is a delta to reconcile) | `brand-wizard-app/` |
| Global-market registry | 39×14 brand×lane; per-lane teacher imprint names for ja_JP/zh_TW/zh_HK/zh_CN/zh_SG | `config/brand_management/global_brand_registry_unified.yaml`; `config/brand_management/teacher_brand_map.yaml` |
| Market CAPTURE correctness (SG/CN/TW) at wizard entry → endpoint `lane` | UNVERIFIED (the operator's stated need) | wizard html + brand_onboarding.py `lane` field |
| Teacher mode in pipeline | BUILT | `scripts/run_pipeline.py` (`teacher_mode`, `teacher_id`, OPD-137 doctrine preamble) |
| One teacher per market (exclusivity) | BUILT (ledger) | `submissions/teacher_claims.yaml`, keyed `<lane>__<teacher_tid>` |
| Named vs generalized (doctrine, no-name) atoms | mechanism BUILT | `phoenix_v4/rendering/teacher_wrapper.py` modes `named`/`generalized`/`composite` |
| Second-claimant → generalized routing | UNVERIFIED (operator's core "verify it's there") | onboarding claim path → pipeline teacher_mode + wrapper mode selection |
| Brand Director page opens for right brand | UNVERIFIED | `brand-wizard-app/brand_directors.html` → `/src/main-brand-directors.jsx`; `config/brand_management/brand_director_assignments.yaml` |
| Phantom planned books shown as available | BUG (fail-open `_is_catalog_bearing`) | `brand_onboarding.py` `_is_catalog_bearing`; brand-directors React data source |

## Inventory

| # | File | Agent | Lane | Wave | Depends on (signal) |
|---|---|---|---|---|---|
| 00 | `00_MASTER_DISPATCH_PROMPT.md` | Pearl_PM | dispatcher | — | — |
| 01 | `01_Pearl_Int_wizard_yaml_market_assignment.md` | Pearl_Int + Pearl_Prez | verify YAML→brand + global-market capture (SG/CN/TW/JP); fix market mis-capture if broken | 1 | — |
| 02 | `02_Pearl_Editor_teacher_mode_exclusivity_doctrine_fallback.md` | Pearl_Editor + Pearl_Dev | verify teacher-mode + one-per-market exclusivity + named→generalized doctrine fallback with a 2-book executed proof | 1 | — |
| 03 | `03_Pearl_Brand_director_page_and_phantom_books.md` | Pearl_Brand + Pearl_Dev | verify Brand Director page opens for the right brand; FIX phantom-planned-books (show only real downloadable) | 1 | — |
| 06 | `06_Pearl_PM_synthesis_state_sync.md` | Pearl_PM | synthesize verdicts, correct stale premises at source, SSOT/registry sync, replay runbook | 4 | 01+02+03 signals |

**Prompt count:** 5 (1 dispatcher + 3 lanes + 1 synthesis).

## Wave order

- **Wave 1** — 01, 02, 03 run in PARALLEL (independent subsystems, no shared hot files — see collision map).
- **Wave 4** — 06 synthesis (sole writer of coordination hot files; runs after all three lane signals exist).

There is no wave-0 preservation lane here (unlike the lean pack) because these lanes create
their OWN evidence and commit it to the offline branch as they go; but each lane's FIRST act is
still to confirm it is not about to clobber untracked value in its write scope.

## Hot-file / collision map (verified: lanes are disjoint)

- Lane 01 writes: `submissions/**` test artifacts (gitignored PII path — keep test data synthetic), wizard html + `brand_onboarding.py` (ONLY if fixing market capture), lane evidence.
- Lane 02 writes: `phoenix_v4/rendering/teacher_wrapper.py` / onboarding claim routing (ONLY if fixing the generalized-fallback), teacher proof renders, lane evidence.
- Lane 03 writes: `brand-wizard-app/src/main-brand-directors.jsx` + `brand_onboarding.py` `_is_catalog_bearing` (the phantom-books fix), lane evidence.
- **`server/routes/brand_onboarding.py` is touched by BOTH 01 (market) and 03 (`_is_catalog_bearing`).** This is the one real overlap → serialize via the offline-branch commit slot (dispatcher grants; a lane rebases onto the other's commit before its own). Different functions, so no logical conflict, only commit-ordering.
- `config/brand_management/*.yaml` registries — READ-only in all lanes except 06 (which may append coordination notes). No lane rewrites the registry.
- Flagship/teacher goldens and `atoms/gen_z_professionals/anxiety/**` — untouchable.

## Landing contract (offline-substrate; GitHub 403)

- Offline branch `pearlstar_offline/brand-wizard-verify-20260719` (based on `9e9b9e6067…`),
  plumbing commits, explicit paths, diff-stat gate. Ledger row in
  `artifacts/coordination/pearlstar_offline/LEDGER.tsv`.
- Verify-only findings still LAND: evidence dir + handoff committed offline. A lane that proves
  a behavior correct is DONE (evidence + handoff); a lane that finds a bug lands the fix
  (offline) or BLOCKED with the exact gap spec. No lane ends at "analyzed, report later."
- Browser/served-UI verification MUST show a visible observed output (screenshot/DOM/served
  response), never dispatch-only (`docs/COLAB_AND_BROWSER_VERIFICATION_RUNBOOK.md`, §7).

## Required signal tokens

- `bw-yaml-market-verified=<full-sha>` (01) — plus `bw-market-fix-landed=<sha>` if a fix was needed
- `bw-teacher-exclusivity-doctrine-verified=<full-sha>` (02) — plus 2-book proof paths
- `bw-director-page-and-books-fixed=<full-sha>` (03)
- `bw-verify-closeout=<full-sha>` (06)

## Acceptance-layer honesty

Report each behavior on the six-layer manga-style taxonomy adapted here: CONFIG-EXISTS
(registry/route present) → CODE-WIRED (path reachable) → EXECUTED-REAL (a real submission /
rendered book / loaded page byte-verified) → PROVEN (operator confirms). A route existing is
CODE-WIRED, not "working." Only a byte-verified submission/render/page load is EXECUTED-REAL.
Do not report "verified" without an executed artifact.

## Status

- 2026-07-19: pack authored by router; dispatched by Pearl_PM.
- Wave 1 COMPLETE (offline `pearlstar_offline/brand-wizard-verify-20260719`):
  - `bw-yaml-market-verified=d796e3fac58e962fb2b0a039922201cbac1cdcda` (+ `bw-market-fix-landed` same) — zh_CN/zh_SG capture FIXED; TW wizard EXECUTED-REAL PASS
  - `bw-teacher-exclusivity-doctrine-verified=9f8a857e6dcdc5fb15e98eab8df4856cf6a5d391` — exclusivity 409 EXECUTED; onboarding→generalized ABSENT; pipeline generalized FIXED + mini A/B proof (full spine chord BLOCKED)
  - `bw-director-page-and-books-fixed=9756ebbc8890f7e9fb656ee54d1fee7238d5c454` — fail-closed catalog bearing + ops_url→real-asset handoff
- Offline tip: `9f8a857e6dcdc5fb15e98eab8df4856cf6a5d391`
- Wave 4 (06 synthesis): **LANDED-OFFLINE**
  - `bw-verify-closeout=<see artifacts/coordination/handoffs/brand_wizard_06_synthesis_2026-07-19.md and CLOSEOUT_RECEIPT for the exact landing SHA>`
  - Synthesis doc: `artifacts/qa/brand_wizard_verification_synthesis_2026-07-19.md` (behavior→verdict→evidence table; operator-belief reconciliation; follow-ons)
  - SSOT synced: `docs/PROGRAM_STATE.md` §"2026-07-19 Brand wizard onboarding" (no `origin/main` SHA bump — nothing merged); `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (+7 rows: 3 lanes + lane06 + 3 follow-ons); `artifacts/coordination/operator_decisions_log.tsv` (+3 rows: `OPD-BW-01`/`02`/`03`); `artifacts/coordination/pearlstar_offline/LEDGER.tsv` (brand-wizard rows `replay_status=pending`)
  - Replay+deploy runbook: `docs/runbooks/BRAND_WIZARD_GITHUB_RETURN_REPLAY_2026-07-19.md`
  - GitHub re-checked live at synthesis: still 403 account-suspended — no push/PR/deploy attempted
- **Final offline tip:** `<see bw-verify-closeout signal above>`
