# Main harvest report (report-only)

- Started: `2026-03-30T02:34:39Z`
- Repo: `/Users/ahjan/phoenix_omega`
- Run label: `post-S0-S8-PR78-89-20260330`
- Mode: `online_live`
- Merge target: `origin/main`

## Policy

Do not merge any codex/* convergence branch directly to main. Cut a clean agent/* branch from origin/main and transplant only the listed files.

## Pearl Prime governed PR slices

### pearl_prime_pr1: Runtime identity + location truth

- **Classification:** `satisfied_on_main`
- **Note:** Governed paths resolved on `origin/main` via S0–S8 and related work; convergence tip stale vs main (no transplant 2026-03-30).
- **Source (material):** `codex/state-convergence-20260328`
- **Target:** `origin/main`
- **Recommended clean branch:** `agent/pearl-prime-runtime-truth`
- **Spec:** `docs/PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md §5 PR 1`
- **Files (governed list):**
  - `scripts/run_pipeline.py`
  - `phoenix_v4/planning/catalog_planner.py`
  - `phoenix_v4/rendering/book_renderer.py`
  - `config/localization/render_location_profiles.yaml`
  - `tests/test_book_renderer.py`
  - `tests/test_book_renderer_location_fallbacks.py`
  - `tests/test_topic_identity_resolution.py`
- **Still divergent vs origin/main (per-path diff):** *(none — satisfied on main as of 2026-03-30)*
- **Required tests:**
  - `PYTHONPATH=. python3 -m pytest tests/test_topic_identity_resolution.py tests/test_book_renderer_location_fallbacks.py tests/test_book_renderer.py tests/test_location_passthrough.py -q`

### pearl_prime_pr2: Bestseller composition + editorial runtime

- **Classification:** `already_on_main`
- **Note:** No diff vs origin/main for listed paths on source ref (verify manually if main advanced partially).
- **Source (material):** `codex/state-convergence-20260328`
- **Target:** `origin/main`
- **Recommended clean branch:** `agent/pearl-prime-bestseller-runtime`
- **Spec:** `docs/PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md §5 PR 2`
- **Blocking dependencies:**
  - Branch from agent/pearl-prime-runtime-truth (PR 1 head) or from updated origin/main after PR 1 merges; do not open standalone from main while PR 1 would conflict on book_renderer.py (per recovery spec §5 PR 2).
- **Files (governed list):**
  - `phoenix_v4/rendering/chapter_composer.py`
  - `phoenix_v4/rendering/book_renderer.py`
  - `phoenix_v4/quality/chapter_flow_gate.py`
  - `phoenix_v4/qa/bestseller_editor.py`
  - `phoenix_v4/planning/slot_resolver.py`
  - `phoenix_v4/planning/assembly_compiler.py`
  - `tests/test_chapter_composer.py`
  - `tests/test_chapter_flow_gate.py`
- **Required tests:**
  - `PYTHONPATH=. python3 -m pytest tests/test_chapter_composer.py tests/test_chapter_flow_gate.py tests/test_book_renderer.py -q`

### pearl_prime_pr3: Governing Pearl Prime recovery docs

- **Classification:** `satisfied_on_main`
- **Note:** All four governed docs newer/more complete on `origin/main` than stale convergence tip; `DOCS_INDEX` links present (2026-03-30).
- **Source (material):** `codex/state-convergence-20260328`
- **Target:** `origin/main`
- **Recommended clean branch:** `agent/pearl-prime-recovery-docs`
- **Spec:** `docs/PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md §5 PR 3`
- **Blocking dependencies:**
  - Prefer origin/main after PR 2 merges (or stack on PR 2 head if cleaner).
- **Files (governed list):**
  - `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md`
  - `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`
  - `docs/PEARL_PRIME_SALVAGE_AUDIT_2026_03_29.md`
  - `docs/DOCS_INDEX.md`
- **Still divergent vs origin/main (per-path diff):** *(none — satisfied on main as of 2026-03-30)*
- **Required tests:**
  - `PYTHONPATH=. python3 scripts/ci/check_docs_governance.py`

## Codex branch candidates

- **`codex/main-autobackup-20260320-2124`** (`codex/main-autobackup-20260320-2124`): `archived` — Disposition `archive` (2026-03-30): autobackup snapshot; no governed merge target. Row added to `docs/BRANCH_DISPOSITION_2026_03_20.md`. Remote not present at triage.
  - commits ahead of origin/main: `2`
  - diff sample (first 40 paths, symmetric):
    - `.gitignore`
    - `CLAUDE.md`
    - `artifacts/backup_qwen_forks_err.log`
    - `brand-admin-wordpress.html.local-backup`
    - `docs/BRANCH_CLEANUP_2026_03_21.md`
    - `docs/COLAB_AND_BROWSER_VERIFICATION_RUNBOOK.md`
    - `docs/DOCS_INDEX.md`
    - `docs/MESSAGING_CHANNELS_LOCAL_SETUP.md`
    - `docs/WORDPRESS_LOCAL_SETUP.md`
    - `scripts/integrations/check_messaging_channels_local.sh`
    - …

- **`codex/main-autobackup-20260322-112842`** (`codex/main-autobackup-20260322-112842`): `archived` — Disposition `archive` (2026-03-30): autobackup snapshot; cherry-pick later if product needs. Row in disposition doc. Remote not present at triage.
  - commits ahead of origin/main: `22`
  - diff sample (first 40 paths, symmetric):
    - `ASIAN_MARKET_EXPANSION_WRITERS_SPEC.md`
    - `CONTENT_PRODUCTION_PLAN_13K_BOOKS.md`
    - `PHOENIX_OMEGA_GO_TO_MARKET_PLAN.md`
    - `PhoenixControl/PhoenixControl.xcodeproj/project.xcworkspace/contents.xcworkspacedata`
    - `PhoenixControl/PhoenixControl.xcodeproj/project.xcworkspace/xcuserdata/ahjan.xcuserdatad/UserInterfaceState.xcuserstate`
    - `PhoenixControl/PhoenixControl.xcodeproj/xcuserdata/ahjan.xcuserdatad/xcschemes/xcschememanagement.plist`
    - `ahjan_pic.png`
    - `artifacts/backup_qwen_forks_err.log`
    - `artifacts/ei_v2/ei_v1_v2_comparison.json`
    - `artifacts/ei_v2/ei_v1_v2_summary.txt`
    - …

- **`codex/main-salvage-20260323-153043`** (`codex/main-salvage-20260323-153043`): `archived` — Disposition `archive` (2026-03-30): salvage snapshot; teacher-bank work superseded by S6/S7 on `main`. Row in disposition doc. Remote not present at triage.
  - commits ahead of origin/main: `15`
  - diff sample (first 40 paths, symmetric):
    - `.github/pull_request_template.md`
    - `.github/workflows/docs-ci.yml`
    - `.gitignore`
    - `GEN_Z_PROFESSIONALS_ATOMS_COMPLETION_REPORT.md`
    - `PHOENIX_OMEGA_GO_TO_MARKET_PLAN.md`
    - `PhoenixControl/Models/TeacherStatus.swift`
    - `PhoenixControl/Services/ScriptRunner.swift`
    - `PhoenixControl/Views/TeacherView.swift`
    - `SOURCE_OF_TRUTH/teacher_banks/adi_da/approved_atoms/EXERCISE/adi_da_EXERCISE_000.yaml`
    - `SOURCE_OF_TRUTH/teacher_banks/adi_da/approved_atoms/EXERCISE/adi_da_EXERCISE_001.yaml`
    - …

- **`codex/marketing-brand-alias-resolution`** (`codex/marketing-brand-alias-resolution`): `archived` — Disposition `archive` (2026-03-30): marketing integration snapshot; not governed by active spec. Row in disposition doc. Remote deleted after triage (Pearl_GitHub 2026-03-30).
  - commits ahead of origin/main: `6`
  - diff sample (first 40 paths, symmetric):
    - `.github/workflows/bestseller-scrape-weekly.yml`
    - `.github/workflows/kdp-pipeline.yml`
    - `.github/workflows/trend-scrape-daily.yml`
    - `Sai_Maa1.png`
    - `artifacts/backup_qwen_forks_err.log`
    - `artifacts/books_qa/test_missing.txt`
    - `artifacts/ei_v2/marketing_integration.log`
    - `artifacts/freebies/index.jsonl`
    - `artifacts/ops/platform_health_scorecard_2026-03-04.json`
    - `artifacts/research/deepseek_bestseller_plan_2026_03_23.md`
    - …

- **`codex/runtime-consolidation`** (`codex/runtime-consolidation`): `keep_open` — Disposition `keep-open`: keep for audit/review; no wholesale merge.
  - disposition doc: `keep-open`
  - commits ahead of origin/main: `199`
  - diff sample (first 40 paths, symmetric):
    - `.augment-guidelines`
    - `.cursor/plans/pearl_prime_book-quality_fixes_c190b664.plan.md`
    - `.cursorrules`
    - `.env.example`
    - `.githooks/pre-push`
    - `.github/CODEOWNERS`
    - `.github/ISSUE_TEMPLATE/audit-gap.yml`
    - `.github/copilot-instructions.md`
    - `.github/pull_request_template.md`
    - `.github/workflows/audiobook-regression.yml`
    - …

- **`codex/state-convergence-20260328`** (`codex/state-convergence-20260328`): `superseded` — Both governed PR slices (PR1 runtime-truth, PR3 recovery-docs) confirmed satisfied on `origin/main`; no remaining transplant targets. Disposition `superseded` (2026-03-30). **Do not delete remote** — audit reference (see `codex/runtime-consolidation` pattern).
  - commits ahead of origin/main: `42`
  - diff sample (first 40 paths, symmetric):
    - `.github/workflows/audiobook-regression.yml`
    - `.github/workflows/brand-guards.yml`
    - `.github/workflows/catalog-book-pipeline.yml`
    - `.github/workflows/ei-v2-learning.yml`
    - `.github/workflows/marketing-briefs-and-proposals.yml`
    - `.github/workflows/marketing_continuous.yml`
    - `.github/workflows/max-quality-catalog.yml`
    - `.github/workflows/release-gates.yml`
    - `.github/workflows/simulation-10k.yml`
    - `.~lock.PHOENIX_OMEGA_INVESTOR_DD.xlsx#`
    - …

## Auxiliary items

- **Source/bank repair lane (not a branch cherry-pick)** (`pearl_prime_followup_source_repair`) — `completed`
  - S0–S8 workstream completed; closeout receipt at `artifacts/source_bank_repair/CLOSEOUT_RECEIPT.md` (PR #88 on `main`).

- **Bestseller 100 signoff evidence (narrow artifact)** (`bestseller_100_signoff_branch`) — `already_on_main`
  - Salvage audit: `origin/agent/bestseller-100-signoff-clean` carries signoff evidence only. If the signoff markdown is not on `origin/main`, open a narrow PR from a clean `agent/*` branch—do not merge the agent branch wholesale.
  - *Note:* If the signoff ref is missing locally, fetch origin before relying on divergence fields.

