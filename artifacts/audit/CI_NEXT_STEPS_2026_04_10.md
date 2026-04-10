# CI Health — Next Steps

**Date:** 2026-04-10
**Project:** proj_state_convergence_20260328
**Source:** artifacts/audit/ci_failure_audit.md (PR #345, merged SHA abd48de1c1e5cd6917f48edfa723a910619db1f0)
**Author:** Pearl_PM + Pearl_GitHub
**Scope:** Post-merge CI state documentation and remaining issue plan. PLANNING ONLY — no code or content generated.

---

## Post-Merge CI State on Main

Verified after merge commit `abd48de1c1e5cd6917f48edfa723a910619db1f0` triggered on main:

| Check | Status | Required | Notes |
|-------|--------|----------|-------|
| Core tests | ✅ SUCCESS | Yes | **Fixed by PR #345** |
| GitHub governance check | ✅ SUCCESS | Yes | Unchanged — was passing |
| EI V2 gates | ✅ SUCCESS | Yes | Unchanged — was passing |
| Pages build and deployment | ✅ SUCCESS | No | Passing |
| Production failure alerts | ✅ SUCCESS | No | Passing |
| Release gates | ❌ FAILURE | Yes | gen_z_student content gap (see below) |
| Workers Builds: pearl-prime | ❌ FAILURE | Yes* | Cloudflare infra — unchanged |
| change-impact.yml | ❌ FAILURE | No | Not a required check |
| pearl-news-full-qa.yml | ❌ FAILURE | No | Not a required check |
| max-quality-catalog.yml | ❌ FAILURE | No | Not a required check |
| translate-bestseller-atoms.yml | ❌ FAILURE | No | Not a required check |

> *Workers Builds: pearl-prime is in the status check rollup but PRs can still be merged via `--admin`. See Issue 2 below.

---

## Fixed by PR #345

### Core Tests — `test_render_book_enforce_chapter_flow_raises`

**File fixed:** `phoenix_v4/rendering/book_renderer.py` (lines 758, 797)

**Root cause:** `chapter_flow_gate_report()` returned `"PASS"` when 0 chapters were extracted — vacuous truth (`"PASS" if failed == 0`). On Python 3.11 (CI environment), placeholder-only plans produce rendered text that `_extract_rendered_chapters` cannot parse, so `chapters = []`, `failed = 0`, and the gate returned PASS without raising `ChapterFlowGateError`.

**Fix:** Both branches now require `len(chapters) > 0` for PASS: `"PASS" if (failed == 0 and len(chapters) > 0)`. A book with zero extractable chapters always fails the gate.

**Verification:** 1368/1368 tests pass locally + CI confirms SUCCESS on main.

**Impact of the bug (before fix):** The chapter flow gate was silently accepting empty books — a real production safety issue, not just a test problem.

---

## Remaining Issues

### Issue 1: Release Gates — gen_z_student Content Gap

**TYPE:** Content gap — NOT a code bug

**CAUSE:** The Release gates rigorous system test (`test_non_story_atoms_for_all_books`) runs on push/schedule events only (`if: github.event_name != 'pull_request'`). It attempts to compile a gen_z_student book and fails because:
- `gen_z_student` has 0 atoms in 3 topics: `compassion_fatigue`, `financial_anxiety`, `financial_stress`
- Missing across 5 slot types: `HOOK`, `SCENE`, `REFLECTION`, `EXERCISE`, `INTEGRATION`
- Total: 15 missing (persona × topic × slot_type) combinations

**EFFECT:**
- Release gates FAILS on every push to main (but not on PRs — rigorous test skips for `pull_request` events)
- Cascading failure: Pearl Prime release evidence step (canary artifact) skips when rigorous test fails
- Makes Release gates noisy — hard to tell real regressions from content gaps

**FIX:** Generate missing gen_z_student atoms for the 3 zero-atom topics. Once atoms exist, the rigorous test will pass automatically — no code changes needed.

**WHO:** Pearl_Writer via Qwen on Pearl Star

**FILES:** `atoms/gen_z_student/{compassion_fatigue,financial_anxiety,financial_stress}/` — create directories and populate with atoms

**HOW MANY:** Minimum 21 atoms per topic × 3 topics = 63 atoms (parity with other canonical personas)

**PRIORITY:** P1 — doesn't block PR merges (rigorous test skips on pull_request events) but makes main push CI red on every merge

**CROSS-REFERENCE:** This is identical to P1 BLOCK 2 / Item B3 in `artifacts/audit/P1_NEXT_STEPS_2026_04_10.md`. Fixing the P1 BLOCK 2 gen_z_student items **also fixes this CI failure** — they are the same workstream.

**DO NOT:** Weaken the test, add skip conditions for gen_z_student, or lower the threshold. The gate is working correctly — it's detecting a real content gap.

---

### Issue 2: Workers Builds: pearl-prime (Cloudflare)

**TYPE:** Infrastructure — NOT a code bug

**CAUSE:** Cloudflare Workers build for `pearl-prime` service is failing. This is an external infrastructure dependency not controlled by repo code.

**EFFECT:**
- Every PR shows a FAIL in the status check rollup for `Workers Builds: pearl-prime`
- PRs cannot be merged via the standard UI or `gh pr merge` without `--admin` flag
- No functional impact on actual deployment (Workers build is separate from GitHub Actions CI)

**FIX OPTIONS (choose one):**
1. **Remove from required checks:** Repo Settings → Branches → Branch protection rules for `main` → uncheck `Workers Builds: pearl-prime` from required status checks. Immediate fix, no code needed.
2. **Fix Cloudflare config:** Repair the pearl-prime Workers build in Cloudflare dashboard. Requires Cloudflare account access and Workers troubleshooting.

**WHO:** Owner (repo settings, option 1) or Pearl_Int (Cloudflare config, option 2)

**PRIORITY:** P2 — workaround (`--admin`) is reliable; fix when convenient

**WORKAROUND:** Continue using `gh pr merge <number> --squash --admin` until resolved

---

### Issue 3: change-impact.yml

**TYPE:** Workflow configuration failure

**CAUSE:** Per ci_failure_audit.md — workflow is failing (not a required check)

**EFFECT:**
- Change impact analysis not running on PRs
- Drift detection and subsystem scope warnings are not being posted as PR comments
- Governance check may miss cross-subsystem scope violations

**FIX:** Triage the specific failure in `.github/workflows/change-impact.yml` — likely a missing dependency, secret, or path mismatch introduced during root directory cleanup (PR #339 removed many files)

**WHO:** Pearl_Dev

**PRIORITY:** P2 — not a required check, but loss of drift detection is a governance risk

---

### Issue 4: pearl-news-full-qa.yml

**TYPE:** Self-hosted runner / credentials failure

**CAUSE:** Pearl News full QA requires live API credentials and a self-hosted runner (Pearl Star). Fails in CI because the hosted runner environment doesn't have QWEN_API_KEY or DASHSCOPE_API_KEY available, or Pearl Star is offline.

**EFFECT:** Pearl News QA not running on PRs — language quality regressions could go undetected

**FIX:** Ensure Pearl Star self-hosted runner is registered and online, and secrets are configured for the workflow

**WHO:** Pearl_Int (runner setup) or Owner (secrets)

**PRIORITY:** P2 — Pearl News QA runs can be triggered manually when needed

---

### Issue 5: max-quality-catalog.yml

**TYPE:** Content / runtime failure

**CAUSE:** Catalog quality gate fails because it exercises the full assembly pipeline including gen_z_student persona — the same content gap as Issue 1 (or dependency on atoms/teacher banks that are incomplete)

**EFFECT:** Max quality catalog generation not running — no automated quality benchmark

**FIX:** Resolves automatically once gen_z_student atoms are written (same fix as Issue 1)

**WHO:** Pearl_Writer (content fix) — no code changes needed

**PRIORITY:** P2 — resolves as side effect of P1 BLOCK 2 work

---

### Issue 6: translate-bestseller-atoms.yml

**TYPE:** Self-hosted runner / Qwen API dependency

**CAUSE:** Translation pipeline requires Pearl Star (CJK6 self-hosted runner) with Qwen API access. Fails in hosted CI environment.

**EFFECT:** Bestseller atom translation not running automatically on PRs

**FIX:** Schedule as manual trigger or ensure Pearl Star runner is online for translation runs

**WHO:** Pearl_Int (runner registration)

**PRIORITY:** P3 — translation is a non-blocking enhancement; CJK content gap is documented separately

---

## Dependency Map

```
P1 BLOCK 2: gen_z_student atoms (Pearl_Writer)
  └─→ fixes Issue 1: Release gates rigorous test
  └─→ fixes Issue 5: max-quality-catalog (likely)

Issue 2: Workers Builds fix (Owner/Pearl_Int)
  └─→ removes --admin requirement for all future merges

Issue 3: change-impact fix (Pearl_Dev)
  └─→ restores drift detection on PRs

Issue 4: Pearl Star runner online (Pearl_Int)
  └─→ enables pearl-news-full-qa + translate-bestseller-atoms
  └─→ fixes Issue 6 as well
```

---

## Cross-Reference: ci_failure_audit.md ↔ P1 Health Report

The gen_z_student gap appears in both audit documents — same root cause viewed from two angles:

| Source | Observation | Impact |
|--------|------------|--------|
| `ci_failure_audit.md` | Release gates rigorous test fails: 15 missing (persona×topic×slot) combos for gen_z_student | CI red on main push |
| `P1_HEALTH_REPORT_2026_04_10.md` | gen_z_student has 143 atoms (lowest persona), 3 zero-atom topic combos | Assembly hard-fail for those combos |
| `P1_NEXT_STEPS_2026_04_10.md` — Item B3 | Fill gen_z_student: compassion_fatigue, financial_anxiety, financial_stress (~63 atoms) | Fixes both CI and assembly |

**One workstream fixes both:** `ws_atom_gap_fill_20260410` (pending) → Pearl_Writer → Item B3 in P1_NEXT_STEPS.

---

## What's Now Healthy on Main

| Check | Status | Notes |
|-------|--------|-------|
| Core tests (1368/1368) | ✅ GREEN | Fixed by PR #345 |
| EI V2 gates | ✅ GREEN | Stable |
| GitHub governance | ✅ GREEN | Stable |
| Pages deployment | ✅ GREEN | Stable |
| Production alerts | ✅ GREEN | Stable |

---

## Priority Order for Remaining Fixes

| Priority | Issue | Action | Who | Effort |
|----------|-------|--------|-----|--------|
| P1 | Issue 1 + 5: Release gates, catalog | Generate gen_z_student atoms (B3 in P1_NEXT_STEPS) | Pearl_Writer | ~30 min (63 atoms) |
| P2 | Issue 2: Workers Builds | Remove from required checks OR fix Cloudflare | Owner | ~15 min (option 1) |
| P2 | Issue 3: change-impact.yml | Triage + fix workflow | Pearl_Dev | ~1 hour |
| P2 | Issue 4 + 6: self-hosted runner | Register Pearl Star runner, configure secrets | Pearl_Int | ~1 hour |
| — | Issues 3–6 combined | All resolve when Pearl Star is online + runner registered | Pearl_Int | ~1 hour |
