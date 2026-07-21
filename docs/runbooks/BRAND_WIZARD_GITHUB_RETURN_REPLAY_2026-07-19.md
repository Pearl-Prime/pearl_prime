# Brand Wizard verification pack — GitHub return replay + deploy runbook (2026-07-19)

**Status:** PARKED
**Wake signal:** `github-suspension-lifted`
**Do not execute while `git fetch origin` / `gh` still return 403.**
**Doctrine:** **replay-1-branch** — verify the offline branch end-to-end as ONE PR before any deploy.

## Why this exists

All brand-wizard verification work (3 verify+fix lanes + this synthesis) landed on
`pearlstar_offline/brand-wizard-verify-20260719` because `git fetch origin` and `gh api user` both
return `403` ("Your account was suspended") — confirmed live at pack start and re-confirmed live at
this synthesis. Nothing in this pack is on `origin/main`. The CF Pages deploy for the wizard/director
fixes is itself gated on GitHub Actions, which is blocked by the same 403 — so deploy cannot happen
until GitHub returns, even though the code fix is done and evidence-backed offline today.

## Durable surfaces to replay

| Surface | Path / ref | Notes |
|---|---|---|
| Offline branch | `pearlstar_offline/brand-wizard-verify-20260719` | sole durable git surface this pack |
| Offline tip (at synthesis) | `9f8a857e6dcdc5fb15e98eab8df4856cf6a5d391` | lane02 handoff+heartbeat commit |
| Synthesis/closeout tip | `<this lane's landing SHA — see handoff/CLOSEOUT_RECEIPT>` | plumbing commit, this turn |
| Lane signals | `bw-yaml-market-verified=d796e3fac58e962fb2b0a039922201cbac1cdcda`; `bw-teacher-exclusivity-doctrine-verified=9f8a857e6dcdc5fb15e98eab8df4856cf6a5d391`; `bw-director-page-and-books-fixed=9756ebbc8890f7e9fb656ee54d1fee7238d5c454` | verify each still resolves on the offline branch after fetch |
| LEDGER | `artifacts/coordination/pearlstar_offline/LEDGER.tsv` | brand-wizard rows; `replay_status=pending` until this runbook executes |
| Synthesis doc | `artifacts/qa/brand_wizard_verification_synthesis_2026-07-19.md` | behavior→verdict→evidence table; PR body source |
| Pack INDEX | `docs/agent_prompt_packs/20260719_brand_wizard_verify/INDEX.md` | ground-truth table + wave status |

### Coherent PR slice (this pack is small enough for ONE PR)

Unlike larger packs, the three lanes here are disjoint-but-related fixes to the same subsystem
(brand onboarding/wizard/director) with only one real file overlap (`server/routes/brand_onboarding.py`,
already serialized offline — lane 03's `_is_catalog_bearing` fix, then lane 01 never touched that
file). Recommend **ONE PR** covering the full offline branch, not split by lane:

- `brand-wizard-app/src/BrandWizard-zh.jsx` (lane 01 — market capture fix)
- `server/routes/brand_onboarding.py` + `brand-wizard-app/src/brandDirectorRoster.js` +
  `brand-wizard-app/src/brandDirectorAvailability.js` + `BrandDirectorDashboard.jsx` +
  `functions/api/onboarding/assignments.js` (lane 03 — phantom-books + director-page fix)
- `phoenix_v4/rendering/teacher_wrapper.py` + `phoenix_v4/planning/enrichment_select.py` +
  `scripts/run_pipeline.py` + `phoenix_v4/rendering/section_packet_composer.py` +
  `config/catalog_planning/teacher_wrapper_templates.yaml` (lane 02 — doctrine-attribution wiring)
- `tests/brand_wizard/test_catalog_bearing_and_ops_url.py` (+ updated `test_pages_assignment_lookup.py`)
- Coordination docs: this runbook, the synthesis doc, PROGRAM_STATE subsection, ACTIVE_WORKSTREAMS
  rows, OPD rows, LEDGER rows, pack INDEX, all handoffs + heartbeats

If `origin/main` has drifted far enough by wake time that a single clean cherry-pick/replay fails,
fall back to splitting by lane (01 client-only / 02 pipeline-only / 03 server+react) using the file
lists above — each lane's own commit on the offline branch is already scoped to exactly those files.

## Exact steps (on wake)

1. **Verify GitHub restored**
   ```bash
   git fetch origin
   # expect a successful fetch — NOT 403 account-suspended
   git rev-parse origin/main
   gh api user   # expect your login, not a 403 JSON error
   ```

2. **Reconcile live `origin/main`**
   - Record the new tip (pack anchor was `9e9b9e606791590337cd7d0f2fb425def2e6f760`; it will have
     moved).
   - Re-check `server/routes/brand_onboarding.py` for drift on `origin/main` since the pack anchor —
     if it changed materially, re-apply lane 03's `_is_catalog_bearing` fail-closed logic and lane
     01's (none — lane 01 never touched this file) by hand rather than assuming a clean apply.

3. **Fetch the durable offline tip**
   ```bash
   git fetch pearlstar_offline
   git rev-parse pearlstar_offline/brand-wizard-verify-20260719
   git log --oneline pearlstar_offline/brand-wizard-verify-20260719 -10
   ```
   Confirm the three lane signal SHAs (`d796e3fac5…`, `9f8a857e6d…`, `9756ebbc88…`) and this
   synthesis lane's landing SHA are all present in that history.

4. **Branch + replay**
   ```bash
   git fetch origin
   git checkout -b agent/brand-wizard-verify-replay-20260719 origin/main
   # Cherry-pick or path-limited apply of the file lists above from
   # pearlstar_offline/brand-wizard-verify-20260719, resolving any drift by hand.
   PYTHONPATH=. python3 scripts/git/push_guard.py
   scripts/ci/preflight_push.sh
   bash scripts/git/health_check.sh
   ```

5. **Pre-push regression**
   ```bash
   PYTHONPATH=. python3 -m pytest tests/brand_wizard/test_catalog_bearing_and_ops_url.py -q
   PYTHONPATH=. python3 -m pytest tests/test_pages_assignment_lookup.py -q
   ```
   Both must be green before push (they were 10/10 + green offline).

6. **Push + ONE PR**
   ```bash
   git push -u origin HEAD
   gh pr create --title "fix(brand-wizard): market-capture zh_CN/zh_SG + phantom-books fail-closed + doctrine-attribution wiring" \
     --body "$(cat artifacts/qa/brand_wizard_verification_synthesis_2026-07-19.md)"
   ```

7. **Governance before merge**
   ```bash
   bash scripts/git/pre_merge_check.sh <PR_NUMBER>
   python3 scripts/ci/pr_governance_review.py
   gh pr diff <PR_NUMBER> --stat | tail -1
   # If deletions > 50 → STOP; ask owner (mass-deletion rule, CLAUDE.md rule 0)
   ```
   If either blocks, do NOT merge — fix or ask the owner.

8. **Required checks green → merge → record merge SHA**
   Update `LEDGER.tsv` brand-wizard rows: `replay_status=merged:<sha>`. Update
   `docs/PROGRAM_STATE.md` "Brand wizard onboarding" subsection to note the merge and (only now)
   it is safe to bump the section's own status — **still do not** retroactively bump the file's top
   "LAST VERIFIED origin/main SHA" line unless a full fresh verification pass is done separately.

9. **THEN — CF Pages deploy (wizard/director fixes only; separate step, GH Actions-gated)**
   The CF Pages deploy for `brand-wizard-app/` is triggered via GitHub Actions (per
   `docs/agent_prompt_packs/20260719_brand_wizard_verify/INDEX.md` CF deploy caveat: local tokens
   auth-fail on the Pages REST API directly). It cannot run until step 6–8 have merged AND GitHub
   Actions itself is unblocked (same 403 lift covers both).
   ```bash
   # After merge, trigger (or wait for) the CF Pages GH Actions workflow for brand-wizard-app/.
   # Do NOT attempt a direct `wrangler pages deploy` with local tokens — documented auth-fail.
   ```

10. **Verify-live step (mandatory before declaring deploy done)**
    - Load the live CF Pages URL for `wizard-zh.html` with `?market=cn` and `?market=sg` — confirm
      distinct captured brands (mirrors `MARKET_CAPTURE_MATRIX.md` postfix rows), not a re-run of
      the pre-fix `en_us` collapse.
    - Load the live `brand_directors.html` → click into a zero-asset brand and an asset-bearing
      brand — confirm the Ops link goes to `brand_handoff_dashboard.html`, not `brand_admin.html`,
      and the zero-asset brand shows "No titles available yet", not phantom counts.
    - Screenshot both and attach to the merge PR or a follow-up verify-live note. Per
      `docs/COLAB_AND_BROWSER_VERIFICATION_RUNBOOK.md` §7, dispatch-only claims are not acceptable —
      a visible observed output is required.

## Explicit non-actions (until wake)

- No `git push origin`
- No `gh pr create` / `gh pr merge`
- No CF Pages / wrangler deploy with local tokens
- No PROGRAM_STATE status flip to "on main" / "deployed" on offline-only value
- No re-opening the 3 lane fixes as if unverified — they are EXECUTED-REAL/FIXED offline; replay is
  a git-mechanics + deploy step, not a re-verification step (re-run the regression tests in step 5
  as a safety check, not a re-discovery)

## Follow-on lanes to fold into the same PR wave (if not yet separately dispatched)

1. Wire onboarding 409 `teacher_claimed` → generalized-doctrine offer (currently ABSENT).
2. Full spine-chord A/B production proof for `master_feung` after persona/coverage alignment
   (currently BLOCKED).
3. Sibling-surface phantom-book audit: `brand_admin.html` direct open, storefront, GHL feed, exec
   dashboard (currently un-audited by this pack).

## Owner

Pearl_PM / Pearl_GitHub on wake. Resume surface: this file +
`artifacts/coordination/handoffs/brand_wizard_06_synthesis_2026-07-19.md`.
