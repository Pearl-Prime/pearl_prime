# Session Handoff — 2026-05-27 V5.1 → ep_002 cascade

**Date:** 2026-05-27 (handoff written end of day)
**Owner:** Pearl_PM (closing agent)
**Scope:** V5.1 Milestone A acceptance → ep_002 preparation cascade → 9 operator decisions → 7 PRs (5 merged, 2 open, 1 spawn-task pending re-dispatch)
**Predecessor handoff:** docs/SESSION_HANDOFF_2026_05_04.md (V5 spec ship) + the V5.1 catalog rollout plan docs/MANGA_V5_CATALOG_ROLLOUT_PLAN.md
**Next session start point:** §10 "Next session bootstrap"

---

## 1. Session arc — what happened

The session opened with operator visual review of 35 V5.1 ep_001 composites (`artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v51_qwen/ep_001/*.png`) and ended mid-merge-cascade for the two PRs that unblock ep_002 V5.1 render dispatch.

High-level arc:

1. **Milestone A ACCEPTED** — operator verdict on 35 V5.1 ep_001 composites: Q1 ≥31/35 shippable PASS, Q2 Mira identity consistent PASS, Q3 iyashikei aesthetic PASS, Q4 L0 environmentals real PASS. V5.1 2-stage decompose architecture (base Qwen-Image render → Image-to-Layers) empirically validated at full episode scale.
2. **5-PR merge cascade** — V5.1 catalog plan + Step 0 beatsheet extraction + Step 1+ generator + ep_002 beatsheet draft + housekeeping cascade-renumber. All merged in dependency order with regression check post-#1310.
3. **Three post-cascade closeouts** — (a) fal.ai credential staging (operator-tier; pending), (b) ep_002 scene_inventory authoring (8 new scenes, MERGED via #1324), (c) beatsheet narrative review surface (checklist authored; OPEN items partially resolved by subsequent decisions).
4. **OPD-154 authority principle ratified** — operator elevated the b17/b22 lock from OPD-149's archetype DEFINE to a general principle: panel descriptions beat chapter_script writer-notes when they conflict. PR #1331 opened.
5. **Pose library extension** — Pearl_Author dispatched; PR #1333 opened with 14 new mira_aoki + 3 new dr_morimoto poses. **Last mechanical gate before ep_002 V5.1 render.**
6. **CI blockage discovered** — both #1331 and #1333 hit a flaky failure on `tests/unit/brand/test_build_admin_packets.py::test_build_zip_from_tsv` — a regression from PR #1326 (per-platform download route, OPD-145 split-at-build) that doesn't `mkdir(parents=True)` before opening a per-platform zip. Pearl_Dev was dispatched to fix; agent KILLED mid-flight (worktree-add died, partial state remains). Needs re-dispatch.

---

## 2. Merge cascade — 5 PRs in dependency order

All 5 merged with Pearl_GitHub safety rules (no force-push, no squash that loses history, CI green confirmed before merge, ep_001 round-trip regression check at the Step 1+ gate).

| # | PR | Merge SHA | Scope |
|---|----|-----------|-------|
| 1 | #1290 | `22326acea` | V5.1 catalog rollout plan v1.0 (docs/MANGA_V5_CATALOG_ROLLOUT_PLAN.md) |
| 2 | #1307 | `8794601a7` | Milestone C Step 0: reverse-extracted ep_001 beatsheet from 35 YAMLs; design notes; schema |
| 3 | #1310 | `f992eef0b` | Milestone C Step 1+: continuity_state generator + 2 archetype DEFINEs + multi-character extension; STRICT round-trip 42/42 PASS on ep_001 |
| 4 | #1316 | `cd65f7c2c` | ep_002 beatsheet draft (32 beats; Mira + Dr. Morimoto multi-char) |
| 5 | #1322 | `c2e83b378` | Housekeeping cascade-renumber (OPDs 145-151 → 147-153) + PR template cascade-prevention checkbox + fal.ai credential staging docs + Workers Builds tech debt log |

**Mid-cascade safety gate:** ep_001 round-trip 42/42 PASS verified on fresh main after #1310 merged (operator-required). Confirms multi-character extension preserves V1 single-character byte-clean round-trip.

---

## 3. Post-cascade follow-ups — 3 merged, 2 pending

| # | PR | Merge SHA | Scope |
|---|----|-----------|-------|
| 6 | #1324 | `be988aa82` | ep_002 scene_inventory: 8 new scenes (street_sidewalk + 7 office_*), iyashikei-in-office defense rigorous |
| 7 | #1325 | `15b46e37a` | Preflight OPD-max hint (prevents future OPD-numbering collisions at authoring time, not just review time) |
| 8 | #1331 | **OPEN** | OPD-154 + b17/b22 additive citation + ws_ep002_v51_pose_library_extension_20260527 opened + parent project updated. **Blocked on flaky #1326 regression.** |
| 9 | #1333 | **OPEN** | Pose library extension: 14 new mira poses + 3 new dr_morimoto poses (PuLID-ready). **Blocked on same flaky #1326 regression. Last mechanical gate before ep_002 V5.1 render.** |

---

## 4. OPD decisions — 9 new OPDs (8 on main, 1 pending #1331)

| OPD | Date | Topic | Status |
|-----|------|-------|--------|
| OPD-145 | 2026-05-26 | (operator's parallel work) ws_per_platform_download_route split-at-build vs slice — split chosen | on main (from #1323) |
| OPD-146 | 2026-05-24 | Milestone C OPEN-3: tension_override field added to schema (was OPD-144 pre-renumber) | on main (from #1310) |
| OPD-147 | 2026-05-26 | V5.1 Milestone A ACCEPTED (was OPD-145 pre-renumber) | on main (re-added via #1322) |
| OPD-148 | 2026-05-26 | ep_002 candidate archetype #1: elevator_interior_micro_tension DOWNGRADE to character_face_micro_tension (was OPD-146 pre-renumber) | on main |
| OPD-149 | 2026-05-26 | ep_002 candidate archetype #2: secondary_character_face_close DEFINE — joint workstream with multi-character extension (was OPD-147 pre-renumber) | on main |
| OPD-150 | 2026-05-26 | ep_002 candidate archetype #3: typographic_caption_card DEFINE in META cluster (was OPD-148 pre-renumber) | on main |
| OPD-151 | 2026-05-26 | Milestone H §7.1 fal.ai smoke test approved — BLOCKED on Phoenix credential setup (was OPD-149 pre-renumber) | on main |
| OPD-152 | 2026-05-26 | CI cascade pattern: PR template checkbox for planner/composer signal changes (was OPD-150 pre-renumber) | on main |
| OPD-153 | 2026-05-27 | Workers Builds: pearl-prime — accepted technical debt (was OPD-151 pre-renumber) | on main |
| **OPD-154** | **2026-05-27** | **Authority hierarchy: panel descriptions > chapter_script writer-notes when they conflict — applies beyond just b17/b22** | **pending PR #1331** |

**Why the cascade-renumber:** my session's branch authored OPDs 145-151 in parallel with main's #1323 (which used OPD-145 for split-at-build) and main's #1310 renumber (which moved my OPD-144 tension_override to OPD-146). When merging #1322 housekeeping, my OPDs 145-151 collided with main's 145+146 — resolved by shifting mine to 147-153 (+ OPD-154 added later). 65 OPD references across 9 files (beatsheet, generator, tests, design notes, iyashikei configs, PR template, fal.ai docs) were updated to match. **Future collisions prevented by PR #1325's preflight OPD-max hint** — it prints the next available OPD before any commit.

---

## 5. Architectural confirmations — what V5.1 proves

### 5.1 V5.1 2-stage architecture works at episode scale

Base Qwen-Image render → Qwen-Image-Layered Image-to-Layers decompose produces shippable manga panels for the iyashikei-genre stillness_press series. Operator verdict on 35 ep_001 composites:

- **Q1 (≥31/35 shippable):** PASS
- **Q2 (Mira identity consistent across panels):** PASS — "all 3 perfect" on character_quiet_face panels 003/023/031; the face-distance tool's flag of 7 panels above threshold was false-positive detector noise on hand/cup archetypes (not real drift)
- **Q3 (iyashikei aesthetic preserved):** PASS — V5.1 ep001_004 matches V3.1 painterly feel
- **Q4 (L0 environmentals real recognizable scenes):** PASS — 022, 035
- **Bonus:** V4→V5 architectural pivot confirmed worth it (V5.1 shows Mira's hand properly placed where V4 had floating subject)

### 5.2 Continuity-state generator works

Pearl_Author skill (continuity_state_generator.py) deterministically produces 35 panel YAMLs from a beatsheet. STRICT round-trip on ep_001 = byte-clean (zero EXACT / ENUM / NUMERIC / STRUCTURAL divergences) per Milestone C exit criterion. 42 tests pass.

### 5.3 Multi-character generator extension works

ep_002 introduces Dr. Morimoto as a second `stage_character`. The generator extension:
- Adds `subject_actor` field (parametrized on-frame focal character)
- Adds 2 new archetypes: `secondary_character_face_close` (SOMATIC cluster, requires subject_actor) + `typographic_caption_card` (META cluster, suppresses all characters)
- Preserves V1 single-character behavior exactly — ep_001 round-trip stays byte-clean (proven by explicit regression guard `test_ep_001_round_trip_still_passes_after_multi_char_extension`)

### 5.4 Known-good architecture anchors

Add to `~/.claude/projects/.../memory/MEMORY.md` `project_known_good_anchors.md`:
- **Manga V5.1 2-stage decompose:** validated at ep_001 35-panel scale on 2026-05-26 per OPD-147 Milestone A ACCEPTED.
- **continuity_state generator:** STRICT round-trip byte-clean on ep_001 (PR #1310, commit `5d6bd57f6`).
- **Multi-character extension:** ep_001 single-char path preserved post-extension (PR #1310, regression test in place).
- **2 new archetypes live:** secondary_character_face_close (SOMATIC) + typographic_caption_card (META) per OPDs 149+150.
- **Cascade-prevention pattern:** OPD-152 PR template checkbox + #1325 preflight OPD-max hint.

---

## 6. Artifacts created this session

### 6.1 Operator-facing review surfaces (local-only; not in main)

- `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/continuity_state/ep_002/_BEATSHEET_NARRATIVE_REVIEW_CHECKLIST.md` — 6-section operator review checklist for ep_002 beatsheet (32 beats); OPEN-A-H scenes + OPEN-7-A multi-char + OPEN-9 Dr. Morimoto CU conflict + OPEN-10 prop_evolution_enum + OPEN-11 poses + OPEN-12 dusk temporal.
- Status update by OPD-154: **OPEN-9 RESOLVED.** OPEN-A-H resolved by #1324 scene_inventory merge. OPEN-11 resolving via #1333 pose library merge. OPEN-7-A resolved by #1310 multi-char extension. OPEN-10 + OPEN-12 remain — non-blocking warnings only.

### 6.2 On-main deliverables (merged)

- `docs/MANGA_V5_CATALOG_ROLLOUT_PLAN.md` — V5.1 milestone structure (A→H) + 800-series target arithmetic
- `docs/MANGA_V5_COMPUTE_SCALING_OPTIONS.md` — Milestone H scoping; top-3 options ranked
- `docs/PEARL_ARCHITECT_BRIEF_EP002_CANDIDATE_ARCHETYPES.md` — 532-line brief that produced OPDs 148/149/150
- `docs/PEARL_AUTHOR_BEATSHEET_DESIGN_NOTES.md` — Pearl_Author design notes for the continuity_state generator
- `docs/specs/MANGA_BEATSHEET_SCHEMA.yaml` — beatsheet schema with tension_override field
- `scripts/manga/continuity_state_generator.py` — 1567-line deterministic generator with 10 H-rules + 4-category field classification + multi-char extension
- `scripts/manga/diff_continuity_state.py` — round-trip harness
- `scripts/manga/morning_check_v51_ep001.sh` — overnight dispatch resilience tool (OPD-141)
- `scripts/manga/tests/test_continuity_state_generator.py` — 42 tests; round-trip + multi-char regression + archetype dispatch
- `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/continuity_state/ep_001/_extracted_beatsheet.yaml` — ground-truth ep_001 beatsheet
- `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/continuity_state/ep_002/_extracted_beatsheet.yaml` — 32-beat ep_002 beatsheet
- `config/source_of_truth/manga_profiles/series/stillness_en_01.scene_inventory.yaml` — 13 scenes (5 original + 8 new via #1324)
- `config/manga/panel_templates/iyashikei.yaml` + `iyashikei.scene_context.yaml` — extended with 2 new archetypes
- `docs/runbooks/PEARL_INT_FAL_AI_SETUP_2026-05-27.md` — 139-line operator runbook for fal.ai credential setup
- `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §12a — fal.ai entry
- `scripts/ci/integration_env_registry.py` — FAL_KEY registered (entry 121)
- `.github/pull_request_template.md` — planner/composer-signal cascade-prevention checkbox (OPD-152)
- `scripts/ci/preflight_push.sh` — OPD-max hint (PR #1325)

### 6.3 Pending on-PR deliverables

- **PR #1331** — `artifacts/coordination/operator_decisions_log.tsv` OPD-154 row; `_extracted_beatsheet.yaml` b17 + b22 additive OPD-154 citation; `ACTIVE_WORKSTREAMS.tsv` new ws row; `ACTIVE_PROJECTS.tsv` parent project update.
- **PR #1333** — `config/source_of_truth/manga_profiles/series/stillness_en_01.character_pose_inventory.yaml` extended: 12 → 26 mira_aoki poses + new dr_morimoto block (3 poses). 238 insertions, 0 deletions (pure append). ep_001 round-trip 42/42 PASS preserved.

---

## 7. Pending operator-tier tasks

### 7.1 fal.ai credential setup (~5 min, gate for OPD-151 Milestone H §7.1 smoke test)

Runbook: `docs/runbooks/PEARL_INT_FAL_AI_SETUP_2026-05-27.md`. Steps 1-3:

1. fal.ai sign-in at https://fal.ai/login (Google OAuth recommended; Phoenix Cloudflare workspace account)
2. Generate API key at https://fal.ai/dashboard/keys; label `phoenix-omega-milestone-h-smoke`; **copy immediately** (shown once)
3. Add to Keychain:
   ```bash
   security add-generic-password -s phoenix-omega -a FAL_KEY -w '<paste-key>' -U
   ```

Once done, Pearl_Int picks up Steps 4-5 (loader verify + auth-only API ping) and logs OPD-154→OPD-155 (next slot) marking credential provisioned. After that, the §7.1 smoke test can run unattended.

**Pearl_Int security boundary:** cannot enter passwords, cannot copy keys from portal. Operator must do those.

### 7.2 ep_002 beatsheet narrative review — remaining items

Checklist at `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/continuity_state/ep_002/_BEATSHEET_NARRATIVE_REVIEW_CHECKLIST.md` (local; not on main).

- ✅ §1 narrative arc (operator pass)
- ✅ §2 scene transitions (9 transitions across 32 beats)
- ✅ §3 character beats — Dr. Morimoto CU conflict RESOLVED by OPD-154
- ⏳ §4 prop continuity — operator review pending
- ⏳ §5 OPEN-10 prop_evolution_enum `worn_at_neck` — Phase-2 spec edit (`MANGA_CONTINUITY_STATE_SPEC §2`); non-blocking warning
- ⏳ §5 OPEN-12 `dusk` temporal — confirm in enum or alias to `evening`; non-blocking

These do NOT gate ep_002 V5.1 dispatch — generator surfaces them as warnings, not errors.

### 7.3 Workers Builds Cloudflare cleanup (per OPD-153, optional)

Per OPD-153 + Pearl_Int audit `artifacts/audits/workers_builds_pearl_prime_audit_2026-04-27.md`:

1. Navigate https://dash.cloudflare.com/0fe2f0679b00fb8a5c3ce830f4144c98/workers/services/view/pearl-prime/production/settings
2. Disconnect GitHub build watcher
3. Confirm next PR's check list has no `Workers Builds: pearl-prime` entry

Until done, the failing check remains accepted noise (non-blocking per branch protection ruleset 13451138 which requires only `Verify governance`).

---

## 8. Known issues + open threads

### 8.1 ⚠️ PR #1326 regression in `scripts/brand/build_admin_packets.py` (active blocker)

`tests/unit/brand/test_build_admin_packets.py::test_build_zip_from_tsv` fails on CI runners ~50% of the time. Root cause: `build_platform_zips_for_brand` opens a zipfile at `<pkg_base>/<brand>/<week>/<platform>/<file>.zip` without `mkdir(parents=True)` on the platform subdirectory. Passes locally due to test ordering leaving the dir from previous runs.

**Fix:** one-line `zip_out.parent.mkdir(parents=True, exist_ok=True)` before the `with zipfile.ZipFile(zip_out, "w", ...)`.

**Current blockage:** PR #1331 + PR #1333 are both red on this flake. Reruns triggered (might pass without fix). Pearl_Dev fix agent (`ac65f68291f5c2da4`) was dispatched but **KILLED mid-flight** ("Worktree-add died mid-flight; the registered worktree is already removed but the dir remains with partial contents"). Re-dispatch needed.

### 8.2 ⚠️ `git worktree add --no-checkout` is a footgun in this repo

Discovered during PR #1331 commit. The `--no-checkout` pattern creates an index with 56,893 entries but a working tree with only the few checked-out paths. When you `git add` with backslash continuations (multi-line shell), staging captures the un-materialized paths as deletions — would result in a catastrophic mass-deletion commit.

**Workaround:** use full-checkout worktree, OR `git add -- <path>` one at a time and verify with `git diff --staged --name-only` after each add (count should match expectation).

**Pattern reference:** memory entry `feedback_worktree_no_checkout_poison.md` documents this for the broader case (origin/main tracks `.claude/worktrees/**`). Even with sparse-checkout cone-mode and reconcile, the multi-line `git add` shell pattern was the trigger for this session's near-miss.

### 8.3 Test_build_zip_from_tsv flakiness pattern

Same SHA on main (`bd772dcd`) produced 3 different CI conclusions: success, failure, skipped. Not just sometimes-passing — sometimes-skipping. Suggests pytest-xdist worker order or fixture race. The mkdir fix removes the failure mode entirely; the skipped runs are a separate observation worth noting in the fix PR.

### 8.4 Pearl_Author scope conflict resolved inline

Pearl_Author's dispatched pose-library brief named `medium_seated_across_table` for dr_morimoto b16 (operator's brief). Beatsheet uses `medium_seated_at_table_facing`. Pearl_Author aligned to beatsheet name (validator invariant 2 in `MANGA_LAYER_RENDER_CONTRACT_SPEC §6.3.A` requires beatsheet pose_id → pose library presence). Documented in PR #1333 body. **Pearl_Editor follow-up:** confirm naming convention preference and reconcile in a small editorial pass.

### 8.5 Pearl_Editor follow-up: chapter_script writer-note refinement

Per OPD-154's tail rationale: refine `artifacts/manga/chapter_scripts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_002.yaml` writer-note for Dr. Morimoto from "never close-up" to "never empathic close-up; observational CUs OK" to encode OPD-154's principle at the source and prevent future re-litigation. Low priority. Separate ws.

---

## 9. The merge-cascade pattern — operationalized

Operator's "Option B" directive from this session (rebase + merge in dependency order, no partial-merge state to track) is a reusable pattern. Reference path:

1. Confirm all PRs in cascade are ready (CI green or known-flaky)
2. Identify hot files that will conflict (this session: `operator_decisions_log.tsv`, `_extracted_beatsheet.yaml`, generator code with OPD comments)
3. For each PR in order:
   - Pull latest origin/main into branch
   - Resolve conflicts deterministically (take main for OPD log when not adding new entries; manual edit for generator code references)
   - Re-run preflight + tests
   - Push, wait CI, merge with `--merge` strategy (no squash, no force-push)
4. Mid-cascade safety gate: after a code-change PR (this session: #1310 generator), run regression check against fresh main BEFORE proceeding to next PR
5. Post-cascade: if some PRs had renumbered IDs (this session: OPD-145→147), explicitly recover the lost entry in a housekeeping PR (OPD-147 Milestone A re-added via #1322)

The pattern landed in 5+3 PRs over ~6 hours with one regression check (42/42 PASS) and zero rollbacks. Memory entry `feedback_serial_lane_hot_governance_file.md` already captures the hot-file serialization principle; this session's cascade is a concrete instance.

---

## 10. Next session bootstrap

### 10.1 Read first

1. **This handoff** (you're here)
2. `CLAUDE.md` — project rules; the Pearl_GitHub entry; banned-paid-LLM policy
3. `docs/SESSION_UNITY_PROTOCOL.md` — STARTUP_RECEIPT / CLOSEOUT_RECEIPT pattern
4. `docs/MANGA_V5_CATALOG_ROLLOUT_PLAN.md` — V5.1 rollout milestones (A→H)
5. `docs/PEARL_ARCHITECT_STATE.md` MANGA-LAYERED-PIPELINE-V2-01 cap entry (line ~799-829)
6. `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` — V2 PRIMARY authority for V5.1 work
7. `artifacts/coordination/operator_decisions_log.tsv` — last 10 OPDs (currently 144-153 on main; 154 pending #1331)
8. `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` — `ws_ep002_v51_pose_library_extension_20260527` (PR #1333) is the last mechanical gate

### 10.2 Do first (in priority order)

1. **Re-dispatch Pearl_Dev #1326 regression fix** (~10 min) — agent was killed; the fix is still needed. Use a regular worktree (NOT `--no-checkout`). Reference: PR scope = 1 file (`scripts/brand/build_admin_packets.py`), 1 line addition (`zip_out.parent.mkdir(parents=True, exist_ok=True)`), test_build_admin_packets.py should be 100% pass on clean tmpdir after.
2. **Merge Pearl_Dev fix PR** once CI green — eliminates flakiness for all future PRs.
3. **Re-trigger CI on #1331 + #1333** (or rebase onto fresh main if needed) — Core tests should now pass deterministically.
4. **Merge #1331** — OPD-154 + b17/b22 citation + ws + project updates land.
5. **Merge #1333** — pose library extension lands. **ep_002 V5.1 dispatch is now fully unblocked.**
6. **(Operator) fal.ai keychain entry** (~5 min) — Steps 1-3 of fal.ai runbook. Unblocks OPD-151 Milestone H §7.1 smoke test.
7. **(Operator)** approve V5.1 ep_002 render dispatch on Pearl Star.

### 10.3 Open Q's for operator

- Does Pearl_Author's `medium_seated_at_table_facing` (matched to beatsheet) or `medium_seated_across_table` (brief original) become the canonical dr_morimoto b16 pose name? Pearl_Editor follow-up.
- OPEN-10 `prop_evolution_enum` extension for `worn_at_neck` (jade_pendant state transition): Phase-2 spec edit or accept as informational warning?
- OPEN-12 temporal `dusk`: add to enum, or alias to `evening`?
- Workers Builds Cloudflare cleanup (per OPD-153): operator tackle now, or stay in accepted-noise mode?

---

## 11. Quick-reference SHA table

| Artifact | SHA / PR# | Date |
|----------|-----------|------|
| V5.1 catalog plan | `22326acea` (#1290) | 2026-05-22 |
| Step 0 beatsheet extraction | `8794601a7` (#1307) | 2026-05-24 |
| Step 1+ generator + multi-char + 2 archetype DEFINEs | `f992eef0b` (#1310) | 2026-05-26 |
| ep_002 beatsheet draft | `cd65f7c2c` (#1316) | 2026-05-27 |
| Cascade-renumber housekeeping | `c2e83b378` (#1322) | 2026-05-27 |
| ep_002 scene_inventory (8 scenes) | `be988aa82` (#1324) | 2026-05-27 |
| Preflight OPD-max hint | `15b46e37a` (#1325) | 2026-05-27 |
| OPD-154 authority + b17/b22 + ws + project | **#1331 OPEN** (commit `4ee70de2e`) | 2026-05-27 |
| Pose library extension (14 mira + 3 dr_morimoto) | **#1333 OPEN** (commit `ce20b23d6`) | 2026-05-27 |
| Pearl_Dev #1326 regression fix | **NOT YET** (agent killed; re-dispatch needed) | — |

---

## 12. Memory updates to consider

Add to `~/.claude/projects/-Users-ahjan-phoenix-omega/memory/MEMORY.md`:

- **project_v51_2stage_validated** — V5.1 2-stage decompose architecture empirically validated at ep_001 35-panel scale on 2026-05-26 per OPD-147 Milestone A ACCEPTED. Reference: `composed_v51_qwen/ep_001/*.png`, MANGA_V5_CATALOG_ROLLOUT_PLAN §Milestone-A, this handoff.
- **feedback_test_zip_from_tsv_flake** — `tests/unit/brand/test_build_admin_packets.py::test_build_zip_from_tsv` flake pattern (introduced by PR #1326; fixed once Pearl_Dev mkdir fix lands). If you see flaky-skip behavior on this test, rerun or wait for the fix PR.
- **feedback_merge_cascade_pattern** — Option B rebase-in-dependency-order pattern; mid-cascade safety gate after code changes; explicit recovery of lost OPDs via housekeeping PR. This session = concrete instance.
- **project_v51_unblocked_for_ep002** (after #1331 + #1333 merge): all operator-tier gates closed for ep_002 V5.1 dispatch. Operator's remaining work = approve render trigger.

---

**End of handoff.** Operator review surface (this file + OPD log + beatsheet) opens with `open docs/SESSION_HANDOFF_2026_05_27_V51_EP002_CASCADE.md`.
