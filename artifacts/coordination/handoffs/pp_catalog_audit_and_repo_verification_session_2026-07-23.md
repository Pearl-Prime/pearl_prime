# Session Handoff — Pearl Prime Catalog Audit + Repo Production Verification

**Date:** 2026-07-23
**Agent:** Claude Code session (acting as Piper → Pearl_PM/general-purpose executor across the session)
**Anchor at close:** `origin/main` = `a3bcd69e3d15410093c4ccb4823f7f39e7a4697d`
**Status:** Catalog audit COMPLETE (merged). Repo verification COMPLETE (all 31 gates confirmed green on true `origin/main`; 2 real governance gaps found, 1 has an open fix PR). Recommended fixes are NOT yet implemented — this session was audit + verification only, no code/atom/config changes.

---

## 1. What was asked, in order (the session evolved through three requests)

1. **`/piper` invocation** — operator asked (voice-transcribed, informal) for a "robust testing" of the Pearl Prime book planner + assembly pipeline: look at existing catalog plans across the whole US-market catalog (all brands, ~800 books/brand), and audit what assembly would do with those plans — explicitly **without assembling/rendering anything**. Questions to answer: is a bestseller contract created before catalog approval; is Pearl_Editor entering the process at the right point; is cohesive flow/enrichment real at catalog scale; is EI v2 genuinely wired in; is the catalog's revenue/access mix deliberate or accidental.
2. **Per the `piper` skill's contract** (author prompts, never execute), the response was a 6-lane read-only audit prompt pack + Pearl_PM dispatcher, committed and PR'd (**PR #215**, still open — see §6).
3. **Operator: "no prompts, i want you to execute 100% production for repo verification, audit, and recommend how to fix."** This shifted the mandate from prompt-authoring to direct execution. Mid-execution, discovered that **another concurrent process/session had already picked up the pack from PR #215 and run all 6 lanes to completion** (see §3) — this session's own 4 parallel verification agents corroborated those merged findings independently rather than duplicating the work. This session then additionally ran the actual **production-readiness gate suite** (`scripts/run_production_readiness_gates.py`, 31 conditions) for repo verification proper.

---

## 2. What actually shipped (merged, verifiable via `git log origin/main`)

| PR | Title | Merge SHA | Status |
|---|---|---|---|
| #221 | Lane A — catalog plan inventory (en_US, all 40 brand archetypes) | `46d971d642cc4076d065a2466be9e55fb3f940cb` | MERGED |
| #222 | Lane B — Pearl_Editor content-authority sequencing audit | `cfa68a3454aecd2722dfb365d1bb8c4af194cd16` | MERGED |
| #227 | Lane C — catalog-scale assembly-readiness prediction | `a7933a689421cdc507ed32cff1443e9e0ad23839` | MERGED |
| #218 | Lane D — marketing/revenue-mix audit | `5a23ce384039e59f031bcb775a5a1269587ff848` | MERGED |
| #220 | Lane E — EI v2 integration-gap audit + wiring proposal | `848c726c66a6cf82696d6810acd6ce91605a0488` | MERGED |
| #230 | Lane F — synthesis (also appended a `docs/PROGRAM_STATE.md` section) | `7f4dc39efdda9ce8e2d85c2ae23be79d45123361` | MERGED |
| #233 | Dispatcher handoff | `a08a50b59e18af71441cc98e83d23d6e942c8dfe` | MERGED |
| #215 | The original prompt pack (docs only — now superseded by execution above) | — | **still OPEN, mergeable** |

**All six lane PRs + dispatcher handoff are docs/audit-only diffs — zero atoms, zero config, zero pipeline code changed anywhere in this program.**

Canonical evidence root: `artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/` (six subdirectories, one per lane, each with `REPORT.md` + `evidence/`). Read `lane_f_synthesis/REPORT.md` first — it is the single-document answer to every question the operator asked, with citations into the other five.

---

## 3. Catalog audit — headline findings (full detail in Lane F's `REPORT.md`)

**One root cause wears five faces: nothing gates catalog admission or content/atom selection on any signal — not content-authority, not craft quality, not revenue. Admission and volume are governed purely by build-order/backfill-timing accident.**

- **True catalog size: 32,401 planned en_US books across 40 brand archetypes** — not the 1,519 listings / 26 brands / 2,187 files `docs/PROGRAM_STATE.md` stated before this audit (~15x stale; corrected in the same doc now, see the "Catalog plan + assembly readiness audit (2026-07-23)" section at `docs/PROGRAM_STATE.md:304`).
- **37 of 40 brands genuinely sit at ~800–845 books each** — the operator's original "800/brand" framing is empirically closer to true than the ratified `CATALOG-800-PER-BRAND-01` cap's "system-wide-only" claim (2026-05-06). Flagged as **Q-CATALOG-AUDIT-04** (stale-cap-record correction, not a system-behavior change).
- **Catalog-wide assembly-readiness census (657 distinct persona×topic×engine cells, all 32,401 books, not a sample):**
  - 1.4% (465 books) predict **BOUND** (both atom bank + character bank present) — and even that's a precondition, not a guarantee (one BOUND cell was live-rescored in the prior 07-22 audit and still failed `chapter_flow`).
  - 70.6% (22,885 books) predict **UNBOUND-thin** but tuple-viability PASS — capped at `structurally clear only` (Layer 1), no character through-line.
  - 27.9% (9,051 books) fail the tuple-viability preflight outright — closer to `path broken` than `structurally clear`.
  - 7 of 13 personas (53.7% of the whole catalog, including `corporate_managers`, the largest single persona) have **zero** character bank at all. `corporate_managers` is also the single worst persona on tuple-viability failure rate (32.5%).
- **Content-authority (story_atoms/teacher_banks) enters the pipeline only at render time, as a soft-skip lookup.** `scripts/catalog/gen_plan_skeletons.py` (the catalog-plan admission generator) has **zero** references to `story_atoms`/`research_fit`/`CANONICAL` — a cell is admitted to the catalog purely on arc-file presence, never on whether it has authored character content. `PEARL-EDITOR-UPSTREAM-01` answers an ownership question, not this pipeline-stage question (Lane B, working title for the gap: `PEARL-EDITOR-PLAN-TIME-GATE-01`, carried forward as **Q-CATALOG-AUDIT-01**).
- **Revenue/access mix is accident, not design.** A real, well-researched revenue-strategy doc exists (`docs/GLOBAL_PERSONA_MARKETING_PLAN.md`, ranks `first_responders` as market-gap #4, tied for highest opportunity score) — but zero code reads it. `first_responders` sits at ~5% the plan density of the 8 core personas purely from build-order (a dated "P0/P1 backfill 2026-04-29" that never got full fan-out). Carried forward as **Q-CATALOG-AUDIT-02**.
- **EI v2 "not wired to planners" was partly stale.** It has one live production plan-time hard-gate (`apply_bestseller_beat_order_gate`, `enforce_bestseller_beat_order: true` in production config) and one fully-built-but-never-armed render-time hard-gate (`DimensionGateBlockError` — `enforce_dimension_gates` defaults `False`, never flipped `True` in `scripts/run_pipeline.py`). The one function purpose-built to route EI v2 into planner atom-selection (`hybrid_select_slot_production()`) has **zero callers anywhere in the repo**. A real architecture spec for wiring this properly (`docs/specs/EI_V2_STRENGTHENED_ARCHITECTURE_SPEC.md`, 2026-06-11, status DESIGN) has sat unratified for 6 weeks. Carried forward as **Q-CATALOG-AUDIT-03**.

**Prioritized fix roadmap (10 items, full detail + recommended defaults in Lane F §"Prioritized fix roadmap" + §"Cap-entry candidates"):**

Executable-default (no ratification needed):
1. `docs/PROGRAM_STATE.md` catalog-number refresh — **partially done** (Lane F's own append)
2. Re-run series-plan-emission for 3 arc-orphaned brands (`qi_foundation`/`body_memory`/`still_forest`, ~92% orphaned each)
3. **Author `story_atoms` for `corporate_managers` first** — single highest-leverage content-authoring investment
4. Investigate `NO_BINDING`/`BAND_DEFICIT` cluster on 4 topics (burnout, imposter_syndrome, overthinking, sleep_anxiety — each >50% preflight-fail)
5. Fix the 8-cell `gen_z_student` engine-resolution mismatch
6. Arm `enforce_dimension_gates=True` at the one production render call site — **only after a dry-run sweep** (could retroactively fail currently-shipping books)

Operator-tier (needs ratification before implementation — each has a recommended default written up in Lane F):
7. **Q-CATALOG-AUDIT-01** — plan-time content-authority gate. Recommended default: (b) flag-only, not hard-block.
8. **Q-CATALOG-AUDIT-02** — wire the revenue-research doc into selection, with an access-floor guarantee. Recommended default: (A) wire it, scoped small, ratified before merge.
9. **Q-CATALOG-AUDIT-03** — ratify or reject `EI_V2_STRENGTHENED_ARCHITECTURE_SPEC.md` before any further EI v2 wiring lane.
10. **Q-CATALOG-AUDIT-04** — re-ratify `CATALOG-800-PER-BRAND-01` to match empirical reality.

---

## 4. Repo production verification — this session's own work (not from the merged pack)

Ran `scripts/run_production_readiness_gates.py` (31 conditions). **First run (from this session's checked-out branch, `agent/bestseller-atom-flow-lanes-20260721`, which was 170 commits behind `origin/main`) showed 4 false failures** (gates 21, 27, 28, 32). Re-verified all four from a clean detached worktree at true `origin/main` — **all four pass genuinely; the failures were 100% checkout-staleness artifacts**, not real defects:

| Gate | Stale-branch result | True `origin/main` result |
|---|---|---|
| 21 — manga render-progress bytes | FAIL (2 schema mismatches) | PASS (3 files checked) |
| 27 — data dictionary | FAIL | PASS (213 documented, 0 orphans) |
| 28 — flagship CH1 golden parity | FAIL (byte mismatch) | PASS, byte-identical |
| 32 — capability regression | FAIL (5 "removed" scripts) | PASS (0 regressions) |

**Process gap worth fixing:** the gate script does not verify its own checkout is current against `origin/main` before reporting — any agent running it from a stale branch gets false failures with no warning. Cheap fix: add a `git fetch && git diff --quiet origin/main` precheck (warn, don't block) at the top of `scripts/run_production_readiness_gates.py`.

**Two real, current gaps, confirmed independently via the GitHub API / Actions (not affected by branch staleness):**

1. **`main` has no branch protection and no rulesets** — `gh api repos/Pearl-Prime/pearl_prime/branches/main/protection` → 404 "Branch not protected"; `gh api repos/Pearl-Prime/pearl_prime/rulesets` → `[]`. CLAUDE.md states "PRs with BLOCKED status cannot be merged (enforced by GitHub ruleset)" — **this enforcement does not exist at the platform level today.** Every merge gate in this repo's governance model is convention-only.
2. **`Core tests` and `parse-sweep` required checks are red on `main` itself right now**, for a single, precise reason (verified via `gh run view <run_id> --log-failed` on the latest `main`-branch run, `29998507158`, 2026-07-23T10:13Z): `tests/unit/planning/test_canonical_atom_parse_sweep_guard.py::test_parse_sweep_is_green_tree_wide` fails on exactly 4 files with mangled stub content — `atoms/corporate_managers/compassion_fatigue/{grief,overwhelm,watcher}/locales/zh-CN/CANONICAL.txt` + `atoms/entrepreneurs/compassion_fatigue/watcher/locales/zh-CN/CANONICAL.txt` (the "PR #1590 failure class" the check script itself names). `pytest -x` stops there; 4,543 other tests pass, 22 skip, 1 xfail. **An open fix already exists: PR #131** ("fix(atoms): author real zh-CN prose for compassion_fatigue stub blocks"), state OPEN, mergeable status UNKNOWN as of this session's close.

---

## 5. Recommended next actions, in priority order

1. **Merge PR #131** — unblocks `Core tests`/`parse-sweep` for every PR in the repo. Cheapest, highest-blast-radius fix available; not authored by this session.
2. **Configure branch protection / a ruleset on `main`** requiring the passing status checks (Drift detectors, Governance review, Verify governance, Release gates, EI V2 gates, Core tests, parse-sweep, etc.) before merge is allowed. This makes CLAUDE.md's documented governance model actually true at the platform level. Operator/repo-admin action — needs GitHub admin permissions this session did not attempt to use.
3. **Decide Q-CATALOG-AUDIT-01 through -04** (see §3) — each has a recommended default already written up in `lane_f_synthesis/REPORT.md`; ratifying them is a Pearl_Architect cap-entry action, not a coding task.
4. **Once #3's Q-01 is decided:** start the `corporate_managers` `story_atoms` authoring lane (fix-roadmap item 3) — this is the single highest-leverage executable-default follow-up per the audit.
5. **Optional, low-cost:** add the `origin/main` freshness precheck to `run_production_readiness_gates.py` (§4) so this session's false-failure trap doesn't repeat for the next agent.
6. **Housekeeping:** PR #215 (the original prompt pack) is superseded by the executed lanes — consider closing it with a comment pointing to PR #230, or leave it as a historical record of the authored prompts. Not urgent either way.

---

## 6. What this session did NOT do

- No atoms, config, or pipeline code were changed anywhere. Every artifact produced (this session and the concurrently-executed pack) is a markdown report or a `docs/PROGRAM_STATE.md` append.
- No book was rendered or assembled by this session's own agents (the production-readiness gate suite's gate 30 does render a flagship chapter as part of its own check — that's the gate script's existing behavior, not something this session added).
- Branch protection was **not** configured — flagged as a recommendation, not actioned (requires repo-admin GitHub permissions).
- PR #131 was **not** merged by this session — flagged as the top recommendation, not actioned.
- Locale catalogs beyond en_US, manga/audiobook/music catalog axes — entirely unaudited (explicitly out of scope for all six lanes).

---

## 7. File/path index for the next session

- **Start here:** `artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_f_synthesis/REPORT.md`
- Per-lane detail: `artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_{a,b,c,d,e}_*/REPORT.md` (+ each lane's `evidence/`)
- Dispatcher handoff (six-lane execution log, corrections made mid-dispatch): `artifacts/coordination/handoffs/pp-catalog-audit-dispatcher_2026-07-23.md`
- Original prompt pack (now historical/superseded): `docs/agent_prompt_packs/20260723_pearl_prime_catalog_plan_assembly_readiness_audit/`
- `docs/PROGRAM_STATE.md:304` — the appended "Catalog plan + assembly readiness audit (2026-07-23)" section
- Governance/architecture ratification target: `docs/PEARL_ARCHITECT_STATE.md` (Q-CATALOG-AUDIT-01 through -04 need cap entries)
- EI v2 wiring spec awaiting ratification: `docs/specs/EI_V2_STRENGTHENED_ARCHITECTURE_SPEC.md`
- Revenue-strategy doc that needs wiring: `docs/GLOBAL_PERSONA_MARKETING_PLAN.md` + `config/catalog_planning/market_topic_fit.yaml`
- Open fix for Core tests/parse-sweep: PR #131
- This session's now-superseded prompt-pack PR: #215

---

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Claude Code session (Piper -> direct executor)
TASK:           Pearl Prime catalog plan+assembly audit (verification of concurrently-executed pack) + repo production-readiness verification
COMMIT_SHA:     see table in §2 (six lane PRs + dispatcher handoff, all merged); this handoff itself not yet committed as of writing
FILES_WRITTEN:  this file; docs/agent_prompt_packs/20260723_pearl_prime_catalog_plan_assembly_readiness_audit/** (PR #215, still open)
FILES_READ:     artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md; all 6 lane REPORT.md files (§2); docs/PROGRAM_STATE.md; docs/PEARL_ARCHITECT_STATE.md (relevant caps); scripts/run_production_readiness_gates.py + 4 individual gate scripts; PR #131 / #215 metadata via gh
PROVENANCE:     research: pearl_prime_pipeline_audit_20260722 (baseline); lane_a-f reports (this session's own 4 parallel corroboration agents + the already-merged official lanes) | documents: PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md, CLAUDE.md governance sections | builds_on: pearl_prime_pipeline_audit_20260722, the 6-lane pack this session authored earlier | inventory: EXTENDS (zero functions changed; this session added verification/documentation only)
STATUS:         completed (audit + verification); recommended fixes NOT implemented (see §5/§6)
HANDOFF_TO:     operator (for Q-CATALOG-AUDIT-01..04 ratification + branch-protection config) and next engineering session (for PR #131 merge + corporate_managers story_atoms authoring)
NEXT_ACTION:    Merge PR #131 first (unblocks CI baseline for everything else); then decide Q-CATALOG-AUDIT-01..04; then start corporate_managers story_atoms authoring lane.
```
