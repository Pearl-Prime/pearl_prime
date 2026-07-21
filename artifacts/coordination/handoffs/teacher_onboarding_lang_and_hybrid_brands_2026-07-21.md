# Teacher onboarding — lang switcher + hybrid brands — 2026-07-21

updated=2026-07-21T15:27:20Z
branch=`agent/teacher-onboarding-lang-and-hybrid-brands-20260721`
worktree=`/Users/ahjan/phoenix_omega/.worktrees/teacher-ob-20260721`
github=`PUSHED — PR https://github.com/Pearl-Prime/pearl_prime/pull/18 (Pearl-Prime)`

## Applied operator defaults (loud)

| Q | Default applied |
|---|---|
| Q-BRAND-GEN-01 | Separate `config/brand_management/teacher_originated_brands.yaml` (never mutates 40×14) |
| Q-BRAND-GEN-02 | Deterministic seeded composition; **no LLM at build** |
| Q-BRAND-GEN-03 | Lazy hybrid gen on explicit accept only |
| Q-LANG-01 | No invite mech found → link from `pearl_prime_entry.html` Screen 3 |

## Signals

| Signal | SHA |
|--------|-----|
| `teacher-onboarding-flag-selector-landed` | `b9db18709508e72965b2a0ba9dfc5aa76fa6076d` |
| `teacher-owned-brand-generator-landed` | `55923199611675e4121f8952dd80bdfce634dd86` |
| `hybrid-brand-onboarding-routing-landed` | `c825129940a4fae1a970b5acd5e8541aa37187b0` |

Ancestral Phase A engine (flag gate + 14 locales) also at `f0faac8d2ed1ea511107dbcf07d39735b92d47ba`.

## Proofs

- Flag gate static: `artifacts/qa/teacher_onboarding_flag_selector_20260721/flag_gate_static_proof.txt`
- Smoke/pilot HTML: `artifacts/qa/teacher_onboarding_flag_selector_20260721/flag_gate_{smoke_en-US,pilot_ja-JP,pilot_zh-TW}.html` (+ PNG)
- Brand generator pilot: `artifacts/qa/teacher_brand_generator_pilot_20260721/` (`smoke_named_brand.json`, `pilot_brands.json`, `differentiation.json`, `smoke_hybrid_brand.json`, `name_occurrence_report.json`)
- Phase C A/B (reader-facing imprint): `artifacts/qa/hybrid_brand_onboarding_20260721/name_occurrence_report.json` — named name total>0, hybrid name total=0, `attribution_mode=generalized`, doctrine markers>0, **pass=true**
- Pytest: `tests/brand_generation/` → **7 passed** (requires `SOURCE_OF_TRUTH/teacher_banks` + `config/authoring` + `config/marketing` present — sparse worktree must `git sparse-checkout add` those)
- Vitest FlagLocaleGate: **4 passed**
- Locale key parity: 131 keys × 14 locales

## Phase contracts preserved

- Teacher exclusivity **409** unchanged; offer body adds `mode=generalized_hybrid` + `available_archetypes`
- Accept lazy via `POST /api/v1/onboarding/accept-hybrid` + CF `functions/api/onboarding/accept-hybrid.js`
- Hybrid cap **40** per teacher/lane; docstring 40×14
- Identity Language select retained as **source-language data field** (distinct from display locale)

## Resume note (2026-07-21 finish agent)

Prior finish agent had already MERGED A/B/C locally. This resume closed one honest proof gap:
`name_occurrence_report.json` previously recorded seed-divergence only; it now matches the
predecessor A/B pattern (named imprint carries teacher name; hybrid imprint carries zero).

CLOSEOUT: `artifacts/coordination/handoffs/teacher_onboarding_lang_and_hybrid_brands_2026-07-21_CLOSEOUT.md`


## Landing outcome (Pearl_GitHub 2026-07-21T15:27:20Z)

| Item | Result |
|------|--------|
| GitHub access | **OK** as `Pearl-Prime` (REST + git push). GraphQL `gh pr view --json` returns Forbidden; use REST. |
| Account | Active keyring account `Pearl-Prime`. Inactive/invalid: `Ahjan108`. |
| Remote | `origin` → `https://github.com/Pearl-Prime/pearl_prime.git` |
| Push | **OK** `agent/teacher-onboarding-lang-and-hybrid-brands-20260721` @ tip `fd670aee8e34d47b53b97a1137be1a1d1bbb5dcd` |
| PR | https://github.com/Pearl-Prime/pearl_prime/pull/18 |
| Push-guard / preflight / RAP | OK / OK / OK |
| Mass deletion | **PASS** — 0 deleted paths; 35 files, +2426/−84 |
| Governance | Evidence via REST+worktree `origin/main...HEAD` (mass deletion/size PASS). `pr_governance_review.py` invoked from main-tree script path reviews main checkout — do not trust that run for this lane. |
| Mergeable | **dirty** (`mergeable=false`) — branch ~17 behind `origin/main`; merge-tree reports conflicts ("changed in both"). **Do not merge until rebase/conflict resolve.** |
| Offline ledger | Not used (GitHub push succeeded). |

### Next human action
1. Rebase/reconcile `agent/teacher-onboarding-lang-and-hybrid-brands-20260721` onto current `origin/main` in the worktree (resolve conflicts).
2. Re-push and re-check PR #18 `mergeable_state`.
3. Owner merge when clean (Pearl_GitHub will not merge dirty PR).

## MERGED (Pearl_GitHub 2026-07-22T01:40:26Z)

| Item | Result |
|------|--------|
| Predecessor `pearlstar_offline/brand-wizard-verify-20260719` | Still NOT an ancestor of `origin/main` at merge time — rebased onto plain current `origin/main` per contingency instructions, not onto that predecessor. |
| Rebase | Onto `origin/main` @ `9e771e23bc` (post storyblocks-fix), clean — no conflicts (git rebase auto-dropped one now-empty doc-only commit from a prior session's local rebase attempt; no functional content lost). |
| Tests re-run post-rebase | `pytest tests/brand_generation/` 7 passed; `vitest FlagLocaleGate.test.jsx` 4 passed. |
| 40×14 registry | `config/brand_management/global_brand_registry_unified.yaml` diff vs `origin/main` empty — `total_brand_archetypes: 40` untouched. |
| Preflight | push_guard OK; preflight_push.sh OK; health_check.sh OK for this branch (0 behind/7 ahead, push-guard dry-run OK; unrelated repo-wide stale-branch warnings ignored); check_rap_compliance.py 1 non-blocking warning (unrelated); pr_governance_review.py APPROVED (0 deletions, 19 files, 0 subsystems flagged). |
| **Incidental fix landed first (PR #19)** | `Core tests` required check was red on `origin/main` itself (unrelated to this branch — no `scripts/storyblocks/**`/`tests/storyblocks/**` paths in this PR) due to `a1ced02986` (`fill_social_bank.py`) importing a `scripts/storyblocks/api_client.py` that was never landed. Found an already-authored, unlanded, purely-additive fix branch `agent/fix-storyblocks-api-client-import-20260721` (11 files added, 0 deletions) — opened PR #19, added one more commit (`requests` missing from `requirements-test.txt`, surfaced by CI), merged **PR #19 → `9e771e23bc`** despite `Core tests` itself still showing FAILURE in the merge-time rollup (see below). |
| **Core tests still red post-#19 (pre-existing, separate, NOT chased)** | `tests/test_metricool_client.py` → `phoenix_v4.social` module missing on `main` (real fix lives on unmerged `agent/social-schema-wiring-gate-20260721`, a large multi-file feature branch — out of scope for a landing lane to cherry-pick). Confirmed via PR #19's own merge that `Core tests` failing does **not** actually block merge on this repo in practice (contradicts `docs/BRANCH_PROTECTION_REQUIREMENTS.md` which lists it required) — operator steer received mid-task confirmed: fix forward only if trivial/safe (storyblocks was), otherwise report and move on (metricool is not trivial — not chased). |
| PR #18 | All checks green except `Core tests` (same pre-existing metricool gap, unrelated to this PR's diff — 0 deletions, no metricool/social paths touched). Squash-merged. |
| **MERGE_SHA** | `11609948fed0d23c38524c6452f9f05cc47ac93f` |
| Signals (now merge-SHA, not local commit SHA) | `teacher-onboarding-flag-selector-landed=11609948fe` ; `teacher-owned-brand-generator-landed=11609948fe` ; `hybrid-brand-onboarding-routing-landed=11609948fe` |
| Follow-up (not this lane) | Land `agent/social-schema-wiring-gate-20260721` (or otherwise restore `phoenix_v4/social/deterministic_social.py`) to clear the `Core tests` required-check red state at its root cause. |
