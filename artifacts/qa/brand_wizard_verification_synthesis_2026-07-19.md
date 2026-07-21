# Brand Wizard Verification — Synthesis (Wave 4 / Lane 06) — 2026-07-19

**Agent:** Pearl_PM · **Pack:** `docs/agent_prompt_packs/20260719_brand_wizard_verify/`
**Offline branch:** `pearlstar_offline/brand-wizard-verify-20260719` (offline tip at synthesis start:
`9f8a857e6dcdc5fb15e98eab8df4856cf6a5d391`)
**Shared tree:** `codex/realist-social-samples-20260718` (never switched)
**GitHub:** re-checked live this turn — still **403 account-suspended** (`git fetch origin` and
`gh api user` both return `403` / "Your account was suspended"). No push/PR/deploy attempted.

This document is the single honest answer to the operator's five original questions. It supersedes
any prior chat-only summary. Every verdict below is re-verified against the durable evidence on
disk (byte-opened files, JSON assertions, matrix tables), not relayed prose from the lane agents.

## Behavior → verdict → evidence

| # | Behavior | Verdict (acceptance layer) | Evidence |
|---|---|---|---|
| 1 | Wizard activation → brand YAML → brand assignment | **EXECUTED-REAL** | `artifacts/qa/brand_wizard_yaml_market_verify_20260719/MARKET_CAPTURE_MATRIX.md` — real `matchBrand`/`appendBrandAssignmentToYAML` prod functions, real FastAPI server, byte-opened written YAMLs |
| 2 | Market-capture correctness — en_US | EXECUTED-REAL PASS | same matrix, row 1 (unaffected by fix; was already correct) |
| 3 | Market-capture correctness — ja_JP | EXECUTED-REAL PASS | same matrix, row 2 (already correct) |
| 4 | Market-capture correctness — zh_TW | EXECUTED-REAL PASS | same matrix, row 3 (already correct) |
| 5 | Market-capture correctness — zh_CN / zh_SG | **FIXED** (was FAIL, both collapsed to `en_us`; now PASS, distinct `stabilizer_zh_cn` / `stabilizer_zh_sg`) | same matrix, `results_prefix.json` (before) vs `results_postfix.json` (after); fix = `resolveOnboardingMarket()` added to `brand-wizard-app/src/BrandWizard-zh.jsx` |
| 6 | Teacher-mode + one-teacher-per-market exclusivity | **EXECUTED-REAL (simulated)** — second claim → HTTP 409 `teacher_claimed` | `artifacts/qa/brand_wizard_teacher_doctrine_verify_20260719/exclusivity_sim_result.json` |
| 7 | Named vs. generalized (no-name) doctrine-atom fallback — **onboarding route** | **ABSENT** — a rejected second claimant is NOT offered/routed to a generalized-doctrine brand; the ledger just 409s | same dir, `exclusivity_sim_result.json` + lane-02 handoff §"Routing verdict" |
| 8 | Named vs. generalized doctrine fallback — **pipeline mechanism** | **FIXED + mini EXECUTED-REAL proof** — `--teacher-attribution named\|generalized` wired end-to-end; Book A (named) = 2 name occurrences, Book B (generalized) = 0, both carry Taoist doctrine markers | `name_occurrence_report.json` (re-opened this turn, re-confirmed: `book_a_named.master_feung_name_count=2`, `book_b_generalized.master_feung_name_count=0`, both `taoist_doctrine_marker_count>0`); `wrapper_mode_smoke.json`; `book_a.txt`/`book_b.txt` |
| 9 | Full 2-book spine-chord production proof of named vs. generalized | **BLOCKED** — G-DEF4 persona/topic mismatch on `healthcare_rns`, and `master_feung` doctrine-atom coverage (12 of a wanted 20/slot) | lane-02 handoff §"Atom sufficiency"; `atom_gap_fill_report.json` (clone atoms made then rolled back — not used for the mini proof, not committed) |
| 10 | Brand Director page opens for the exact brand the wizard created | **EXECUTED-REAL** — `brand_directors.html` HTTP 200 (served, vite PID), per-brand `?brand=<id>` deep-link scoping proven for both a zero-asset brand (`optimizer_en_us`) and an asset-bearing brand (`stabilizer_en_us`) | `artifacts/qa/brand_wizard_director_page_verify_20260719/after/VISIBLE_PROOF_after.html`, `ops_url_fix_proof.json` (re-opened this turn) |
| 11 | Phantom (planned-but-not-created) books shown as available | **FIXED** — `_is_catalog_bearing` now fail-closed (unknown/empty index → False); ops deep-link retargeted from `brand_admin.html` (hardcoded UPLOADS counts) to `brand_handoff_dashboard.html` (real-asset only) | `before/phantom_books_optimizer_en_us.json` (KDP=6, GP=4 phantom counts pre-fix) vs `after/catalog_bearing_fail_closed.json` (re-opened this turn: `unknown_fail_closed=true`, `empty_index_fail_closed=true`, `non_buildable_hidden=true`, `buildable_shown=true`); regression `tests/brand_wizard/test_catalog_bearing_and_ops_url.py` 10/10 passed |

## Plain-language answers to what the operator asked

1. **"Does the wizard connect the YAML to the right brand?"** — Yes, and this was already working
   before today (`matchBrand`/`appendBrandAssignmentToYAML` byte-verified). No fix was needed here.

2. **"Does it assign the brand to the correct global market (JP vs zh-CN vs zh-TW vs zh-SG)?"** —
   Partially broken, now fixed. JP, TW, and en_US were always correct. The **Simplified-Chinese
   wizard (`wizard-zh.html`, which serves BOTH China and Singapore) had no code path reading the
   hub's `?market=` handoff at all** — every submission through it, whether meant for China or
   Singapore, silently fell through to the en_US brand. Fixed today by adding the same
   `resolveOnboardingMarket()` pattern the TW/JA wizards already had. Verified before/after with a
   real server + real written files: China and Singapore now land on two distinct real brands.

3. **"Is teacher mode + one-teacher-per-market + doctrine fallback real?"** — Teacher mode and the
   one-per-market exclusivity lock are real and proven (second claim gets a real 409). The
   **doctrine-fallback mechanism in the render pipeline is real and was just fixed/proven** with a
   small two-book test (named book has the teacher's name twice, generalized book has it zero
   times, both keep the teacher's actual doctrine content). What is **NOT** real yet: when a second
   teacher-claimant hits that 409 in the onboarding wizard itself, nothing currently offers them the
   generalized-doctrine brand — they just get rejected. And a full two-book production-quality proof
   at the normal quality bar is blocked today by a persona/topic mismatch and a thin atom pool for
   this teacher, not by the fallback mechanism itself.

4. **"Does the director page open for the right brand?"** — Yes, proven. Both a brand with zero
   real deliverable assets and a brand with a real delivery file load their correct, brand-scoped
   ops page.

5. **"Are phantom (not-yet-created) books gone?"** — Gone from the ops path the wizard/director
   flow actually uses today. The fix makes the "is this brand catalog-bearing" check fail closed
   and retargets the Ops deep-link to the dashboard that only shows real, downloadable assets. One
   sibling surface — `brand_admin.html` opened **directly** (not via the Ops link) — still shows the
   old hardcoded phantom counts; this was explicitly out of scope for this fix and is named as a
   follow-on below, not silently left broken.

## Operator-belief reconciliation (corrected at source)

- **"There is no TW wizard."** — **False, and already corrected at source** in
  `docs/agent_prompt_packs/20260719_brand_wizard_verify/INDEX.md` (ground-truth table + Wave-1
  status section) and now also recorded in `docs/PROGRAM_STATE.md` (this synthesis, below).
  `wizard-tw.html` exists, is wired with a working `resolveOnboardingMarket()`, and the hub already
  routes `zh_TW`/`zh_HK` to it correctly. The belief most likely originated from testing the
  *Simplified-Chinese* wizard (`wizard-zh.html`, a different, visually-similar file) and observing
  it silently produce en_US results — the real, adjacent bug this pack found and fixed.
- **"Market code is missing."** — **False.** The market registry, lane mapping, and per-wizard
  market-resolution mechanism (`resolveOnboardingMarket()`, `LANE_FROM_MARKET`) already existed for
  3 of 4 wizard variants. What was actually broken was narrower and more specific: one wizard file
  (`wizard-zh.html`) never called its market-resolution function at all, so its market **capture**
  (not the market **code**) silently no-opped to a hardcoded default. That capture gap is now fixed.
- **"Doctrine fallback is missing / unverified."** — **Partially true, now precisely scoped.** The
  wrapper-mode mechanism (`teacher_wrapper.py` named/generalized/composite) already existed as
  CONFIG-EXISTS/CODE-WIRED before today. What was actually missing: (a) the pipeline CLI flag to
  drive it end-to-end (`--teacher-attribution`) — now added and mini-proven; (b) any onboarding-side
  routing from a rejected second claim to the generalized brand — still genuinely absent, named as a
  follow-on, not fixed today.
- **"Atom sufficiency for master_feung doctrine."** — Doctrine atom pools (TEACHER_DOCTRINE +
  SCENE/HOOK) exist and are non-stub — sufficient for the mini mechanism proof (CONFIG-EXISTS →
  EXECUTED in the mini cell). They are **not** sufficient for a full production-quality spine
  render at this teacher's normal coverage bar (12 of a wanted 20 atoms/slot) — a real gap, not a
  belief to reconcile.

## What is fixed vs. still open (at a glance)

**Fixed and offline-preserved (not yet on `origin/main` — GitHub 403):**
- zh_CN/zh_SG market-capture collapse (`BrandWizard-zh.jsx`)
- Phantom-books fail-open catalog-bearing check + stale `brand_admin.html` ops deep-link
- Pipeline `--teacher-attribution` named/generalized wrapper wiring

**Proven correct, no fix needed:**
- YAML→brand assignment mechanism
- en_US / ja_JP / zh_TW market capture
- One-teacher-per-market exclusivity (409 on second claim)
- Brand Director page brand-scoped routing

**Still open (named as follow-ons, not silently dropped):**
- Onboarding-side 409 → generalized-doctrine-brand offer (currently ABSENT)
- Full 2-book production-quality spine-chord A/B proof for master_feung (BLOCKED: persona/topic + coverage)
- Sibling phantom-book surfaces: `brand_admin.html` direct open, storefront, GHL feed, exec dashboard (NOT audited this pack)

## Re-verification performed this turn (cheap re-proofs)

- Re-opened `MARKET_CAPTURE_MATRIX.md` — confirmed zh_CN/zh_SG rows read **PASS** in the postfix
  table, byte-distinct `stabilizer_zh_cn` / `stabilizer_zh_sg` brand IDs.
- Re-grepped `book_b.txt` for `feung` (case-insensitive) — the only hit is the file's own title
  line (`"... master_feung attribution=generalized"` — file metadata, not body content); confirmed
  `book_b.txt` is byte-identical to `book_b_generalized.txt`; doctrine markers present per
  `name_occurrence_report.json`.
- Re-opened `after/ops_url_fix_proof.json` and `after/catalog_bearing_fail_closed.json` — confirmed
  `ops_url` retarget to `brand_handoff_dashboard.html` and all four fail-closed assertions `true`.
- Re-ran `git fetch origin` and `gh api user` live — both still return HTTP 403 / account-suspended.
  No push/PR/deploy performed.

## Follow-on lanes to open (not started this wave)

1. **Wire wizard 409 `teacher_claimed` → composite/generalized doctrine offer** — add a response
   payload on second-claim rejection suggesting the generalized-attribution brand path (same
   `teacher_id`, `attribution_mode=generalized`); do not mutate the exclusivity ledger itself.
2. **Full spine-chord A/B production proof** for `master_feung` after persona/topic-registry
   alignment (avoid the `healthcare_rns` G-DEF4 mismatch) and either coverage-gate relaxation for
   modular short formats or +8 authored atoms/slot (no silent cloning for catalog ship).
3. **Sibling-surface phantom-book audit** — `brand_admin.html` opened directly, storefront,
   GHL feed, and exec dashboard may still share the old fail-open catalog-bearing pattern; audit and
   fix each surface independently of this pack's scope (director-page Ops-link path only).

## Provenance

- research: operator asks re-stated in `docs/agent_prompt_packs/20260719_brand_wizard_verify/INDEX.md` "Source request"
- documents: the 3 lane handoffs, the dispatcher handoff, this pack's INDEX.md ground-truth table
- builds_on: EXTENDS lane 01/02/03 evidence; no new code executed by this synthesis lane
- inventory: coordination-class only (no code/atoms/config changed by lane 06)
