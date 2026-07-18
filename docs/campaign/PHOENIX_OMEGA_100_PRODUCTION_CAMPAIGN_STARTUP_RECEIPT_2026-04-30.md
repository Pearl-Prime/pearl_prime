# Phoenix Omega — 100% Production Campaign STARTUP_RECEIPT

**Date:** 2026-04-30
**Operator:** Nihala (Ma'at)
**Agent:** Claude Code (Opus 4.7, Tier 1, operator-present)
**Brief:** "MASTER EXECUTION BRIEF — Phoenix Omega: Finish to 100% Production-Ready"
**Mode:** "do 100% with background agents… make assumptions, report them in QA"

This is the STARTUP_RECEIPT for the 7-phase production campaign + the
session-1 closeout. It documents the assumptions taken, the work landed,
and the blockers/decisions waiting on the operator.

---

## A. Predicates verified

| # | Predicate | Status |
|---|-----------|--------|
| 1 | Audit PR merged (`docs/PHOENIX_OMEGA_PRODUCTION_AUDIT_2026-04-29.md`) | ❌ **OPEN — PR #805** |
| 2 | Pathway PR merged (`docs/PATHWAY_TO_PRODUCTION_2026-04-29.md`) | ❌ **OPEN — same PR #805** |
| 3 | Cookbook PR (drift autopsy + per-genre cookbook) merged | ❌ **OPEN — PR #802 (1 of 2)** |
| 4 | Community-audit PR (Phase 1, 8 files) merged | ❌ **OPEN — PR #803** |
| 5 | LINE Japan funnel PR merged | ❌ **OPEN — PR #801** |
| 6 | Operator approves the 7-phase ladder | ⏳ **Pending operator** |
| 7 | Operator chooses labor model | ⏳ **Pending operator (assumed AI-only)** |

**Conclusion:** The brief explicitly says "All work below assumes the audit
PR has landed and its phase plan is the canonical ground truth." That
predicate is FALSE today. The brief's strict reading would block all
Phase 0 work until #805 / #802 / #803 / #801 land.

Per operator instruction "do 100%, make assumptions, report them in QA,"
Session 1 proceeded with the items that are independently actionable
(don't require the audit / cookbook / community-audit / LINE PRs as
*code* dependencies, only as *documentation* references).

---

## B. Phase 0 PR fan-out plan — Session 1 result

| ID | Description | Branch | PR | Status |
|---|---|---|---|---|
| P0.1 | stillness_press multi-genre migration | (in `agent/spec739-registry-grief-gaps` worktree, not this one) | — | ⏸️ **Skipped** — uncommitted in another worktree, must be picked up by that worktree's owning agent |
| P0.2 | Native locale templates (en_US/ja_JP/zh_TW/zh_CN) | (in operator's other worktree per brief) | — | ⏸️ **Skipped** — same reason as P0.1 |
| P0.3 | FLUX workflow schnell-mismatch fix | `claude/unruffled-robinson-25197f` | **#807** | ✅ **OPEN — ready for review** |
| P0.3-followup | LoRA plan base_model schnell→dev sweep | `agent/lora-plans-flux-base-model-sweep-20260430` | **#809** | ✅ **OPEN — ready for review** |
| P0.4 | warrior_calm tentpole resolution | `agent/warrior-calm-tentpole-coexist-20260430` | **#808** | ✅ **OPEN — ready for review (assumes H2=C)** |
| P0.5 | Pearl Prime catalog regen with native templates | — | — | ⏸️ **Blocked on P0.2** |
| P0.6 | Cookbook PR landing | (already exists as #802) | #802 | ⏸️ **Operator merge** — not for me to land someone else's open PR |
| P0.7 | Community-audit PR landing | (already exists as #803) | #803 | ⏸️ **Operator merge** — same |

### What landed in Session 1

3 PRs opened, all from `origin/main`, all push-guard + preflight green:

1. **PR #807** — `fix(comfyui): FLUX schnell-mismatch — swap to flux1-dev (P0.3)`
   - 4 workflow JSONs swapped from `flux1-schnell-fp8` (steps=20-24, cfg=4-4.5) to `flux1-dev-fp8` (steps=28, cfg=3.5, dpmpp_2m/karras)
   - Files: `config/comfyui_workflows/manga_covers/flux_character_portrait_template.json` (the one the brief explicitly names) + 3 sibling workflows (`flux_txt2img_manga.json`, `flux_img2img_manga.json`, `flux_ip_adapter_manga.json`) which the template's `_meta` says it's "aligned with"
   - `flux_video_bank.json` untouched (already correct schnell config)

2. **PR #808** — `fix(manga): warrior_calm tentpole — Option C (coexist) policy (P0.4)`
   - New `tentpole_divergence_policy` block in `config/manga/brand_genre_allocation.yaml`
   - Generator (`scripts/catalog/generate_manga_catalog.py:370`) consults policy → emits `intentional_portfolio_divergence` for documented-coexist brands instead of `tentpole_mismatch`
   - All 4 manga catalogs regenerated; `tentpole_mismatch=0` everywhere; `intentional_portfolio_divergence=2` in `ja_JP_manga_catalog.csv` (the 2 expected `warrior_calm_battle` rows)

3. **PR #809** — `fix(manga): brand_lora_plans base_model schnell→dev sweep (P0.3 follow-up)`
   - 14 per-LoRA `base_model: flux1-schnell-fp8` → `flux1-dev-fp8`
   - Aligns with PR #807 + the file's own `training_defaults.base_model: "FLUX.1-dev"` at line 9
   - Safe: all 14 LoRAs are `status: defined` (not yet trained)

---

## C. Phase exit criteria acknowledged

Yes. Phase N+1 will not start until Phase N's exit criteria are
operator-PASS.

---

## D. Cost envelope

Operator decision pending. Not inflated by Session 1 (3 zero-cost config
PRs, no API calls, no image renders).

---

## E. Calendar

Operator decision pending target completion date. AI-only path estimate
16-24 weeks per the brief stands.

---

## F. Hard rules acknowledged

| Rule | Status |
|---|---|
| No `--admin` merges | ✅ |
| No paid LLM/image API calls | ✅ (Session 1 used 0 LLM/image calls) |
| STARTUP_RECEIPT per PR | ✅ (each PR has full description + acceptance criteria) |
| CLOSEOUT_RECEIPT with full SHA + wc | ⏳ See section J below |
| Validation before scaling | ✅ (no scaling work in Session 1) |
| Honest receipts — no "mostly done" | ✅ |
| Branched from `origin/main` | ✅ (all 3 branches) |
| push-guard + preflight before push | ✅ (all 3 branches) |

---

## G. Out of scope for the entire campaign (re-confirmed)

- Migration to non-FLUX/non-Pony image gen
- Switch to a non-spine book pipeline
- New product surfaces beyond catalog/manga/audio/podcast/video
- Hire-decision-making on operator's behalf
- Anything that requires `--admin` merge

---

## H. Open questions for operator (BLOCKERS — please answer before next session)

These are now load-bearing. Each is repeated from the brief's STARTUP_RECEIPT
H block + my Session 1 assumption (which is what shipped if any).

### H1. P0.3 schnell-fix option

**Brief asked:** A (FLUX-dev steps=28 cfg=3.5) or B (schnell steps=4 cfg=1.0)?

**ASSUMED:** **A** — operator-present (Tier 1) prioritises quality over throughput; PR #807 implements this. The same Option A config was applied to the 3 sibling workflows + 14 LoRA base_model entries (PR #809).

**Override path:** if you actually want B, revert PRs #807 + #809 and we land schnell-correct configs (steps=4 cfg=1.0 sampler/scheduler euler/simple).

### H2. P0.4 warrior_calm tentpole

**Brief asked:** A (rebalance ja_JP allocation), B (re-author mono-genre as `warrior_calm_battle.yaml`), or C (coexist with documented divergence)?

**ASSUMED:** **C** — least invasive, smallest blast radius, and consistent with the file's existing line-8 comment "Per the plan §3 reconciliation (option C — Coexist)". PR #808 implements this. The 2 affected series rows are now tagged `intentional_portfolio_divergence` (a transparency tag, not a "decision pending" tag).

**Override path:** if you actually want A or B, revert PR #808 and we either rebalance the matrix (A) or re-author the mono-genre file (B).

### H3. P1.4 zh-locale brand migration

**Brief asked:** include 12 zh-locale brands in Phase 1, or defer to Phase 2?

**ASSUMED:** **defer to Phase 2** — global-west 11 brands are higher commercial priority per brief's own "defer if scope exceeds 2 weeks" guidance. NOT acted on; pending operator confirm.

### H4. P3 LINE Japan funnel architecture

**Brief asked:** full 12-brand orchestration, or hub model (3 master OAs + 9 sub-routed)?

**ASSUMED:** **hub model** — smaller blast radius, validates funnel mechanics before full orchestration. NOT acted on (Phase 3 not started); pending operator confirm.

### H5. P4 scale target

**Brief asked:** 800 books per `$-makers-tier` memory, or smaller initial wave (e.g., 200)?

**ASSUMED:** **start with 200, validate, then scale to 800** — consistent with the "validation before scaling" memory feedback and the brief's own P4.1 → P4.2 → P4.3 ladder. NOT acted on; pending operator confirm.

### H6. P5 storefront priority

**Brief asked:** en_US first then ja_JP (calendar-staggered) or both in parallel?

**ASSUMED:** **en_US first, ja_JP second** — JP has tax/banking prerequisites that need operator-side legal/finance work before submission. NOT acted on; pending operator confirm.

### H7. P6 ongoing operations

**Brief asked:** operator handles, or operator delegates to a hire?

**ASSUMED:** **operator handles** until labor model decided. NOT acted on; pending operator confirm.

---

## I. Additional blockers surfaced in Session 1

These are NEW (not in the brief's H block):

### I1. Prerequisite PRs not merged

The brief assumes PRs #805 (audit), #802 (cookbook), #803 (community-audit), #801 (LINE funnel) are merged. None are. **Recommended action:** operator review-merge in this order:

1. **#805** (audit) — gives the campaign its canonical ground truth document
2. **#802** (cookbook) — informs P2.1 prompt rewrites for the 8 known drift failures
3. **#803** (community-audit) — informs P2.3 LoRA reuse vs train decisions
4. **#801** (LINE funnel) — Phase 3 prerequisite

Until #805 lands, all references in PR descriptions to the audit's "drift autopsy" are forward-looking placeholders.

### I2. Worktree `agent/spec739-registry-grief-gaps` has uncommitted P0.1 work

The brief describes this worktree as containing the stillness_press multi-genre migration files (uncommitted). I am operating in a different worktree (`unruffled-robinson-25197f`). I cannot land P0.1 from here without disturbing the other worktree's work-in-progress. **Recommended action:** the agent owning the spec739 worktree should commit + open the P0.1 PR per brief's spec.

### I3. P0.2 native locale templates also in another worktree

Same situation as I2 — the brief described uncommitted changes in *the current worktree*, but `git status --short` of the `unruffled-robinson-25197f` worktree shows clean state. The native locale templates must be in a different worktree. **Recommended action:** locate the right worktree + commit there.

### I4. P0.3 smoke render comparison HTML

PR #807's acceptance criteria include "smoke test: regenerate 1 each of (mecha, dark_fantasy, fantasy_adventure, healing-control)" + "side-by-side comparison committed to `artifacts/qa/flux_workflow_fix_smoke_2026-04-30.md`". This requires RunComfy credentials + actual image generation. **Recommended action:** operator runs this validation step, or delegates to a worktree that has RunComfy credentials loaded.

---

## J. CLOSEOUT_RECEIPT — Session 1

```
SESSION 1 CLOSEOUT — 2026-04-30
================================

Branches created (all from origin/main):
  1. claude/unruffled-robinson-25197f               — PR #807 (P0.3 FLUX fix)
  2. agent/warrior-calm-tentpole-coexist-20260430   — PR #808 (P0.4 warrior_calm)
  3. agent/lora-plans-flux-base-model-sweep-20260430 — PR #809 (P0.3 LoRA sweep)
  4. docs/campaign-startup-receipt-20260430         — PR (this doc)

Commit SHAs:
  PR #807 — 1e27732db3 (fix(comfyui): FLUX workflow schnell-mismatch ...)
  PR #808 — 3714d5a10f (fix(manga): warrior_calm tentpole ...)
  PR #809 — 70db95c552 (fix(manga): brand_lora_plans base_model ...)
  PR (this) — pending push

Files modified across the 3 PRs:
  config/comfyui_workflows/manga_covers/flux_character_portrait_template.json
  scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json
  scripts/image_generation/comfyui_workflows/flux_img2img_manga.json
  scripts/image_generation/comfyui_workflows/flux_ip_adapter_manga.json
  config/manga/brand_genre_allocation.yaml
  scripts/catalog/generate_manga_catalog.py
  artifacts/catalog/manga/ja_JP_manga_catalog.csv
  artifacts/catalog/manga/manga_catalog_summary.json
  config/manga/brand_lora_plans.yaml

Total LoC: +104 / -50 (across the 3 fix PRs)

Gates:
  push_guard:        OK on every push
  preflight_push.sh: OK on every push
  --admin merges:    NONE used
  paid LLM/image API calls: ZERO

Phase 0 status:
  P0.1: skipped (other worktree)
  P0.2: skipped (other worktree)
  P0.3: PR #807 OPEN + PR #809 OPEN
  P0.4: PR #808 OPEN (assumes H2=C)
  P0.5: blocked on P0.2
  P0.6: existing PR #802 OPEN (operator merge)
  P0.7: existing PR #803 OPEN (operator merge)

Phase 0 EXIT CRITERIA standing:
  ❌ All 7 Phase 0 PRs merged to main → 0/7 (3 are now PRs awaiting review,
     2 are pre-existing PRs awaiting operator merge, 2 are in other worktrees)
  ❌ git status --short shows zero uncommitted files in working worktree → CLEAN locally
  ⏳ Last 14 days of CI ≥80% green → not measured this session
  ❌ Pearl Prime catalog ≥8,294 listing-ready rows → blocked on P0.2 + P0.5
  ✅ Workflow JSON fix in place — pending #807 merge
  ❌ Cookbook + community-audit research merged → #802 + #803 still OPEN
  ⏳ Operator signs off on Phase 0 closeout

NEXT_ACTION (operator):
  1. Review/merge PR #807 (FLUX workflow fix)
  2. Review/merge PR #808 (warrior_calm Option C — confirm H2 decision)
  3. Review/merge PR #809 (LoRA base_model sweep)
  4. Review/merge PR (this doc) — campaign STARTUP_RECEIPT
  5. Decide H1-H7 and update brief if any answer differs from my assumptions
  6. Merge prerequisite PRs in order: #805, #802, #803, #801
  7. Direct an agent in worktrees agent/spec739-registry-grief-gaps + (P0.2-bearing) to land P0.1 + P0.2
  8. Spawn next campaign session for P0.5 once P0.2 lands

NEXT_ACTION (agent, next session):
  1. Verify operator merge of #807 / #808 / #809
  2. Verify operator decisions on H1-H7
  3. If H2≠C: revert #808, land alternate
  4. If P0.2 has landed: kick off P0.5 (Pearl Prime catalog regen)
  5. If P0.1 has landed: begin Phase 1 — P1.1 global-west brand migration
     (parallelize 4 sub-agents, 3 brands each)
```
