# Local Repo Recovery Audit — 2026-05-08

## 1) Pre-recovery state
- Main worktree: `/Users/ahjan/phoenix_omega`
- HEAD: `f7c8915cc52e456664ed4cb44329e459241d6b30`
- origin/main: `f7c8915cc52e456664ed4cb44329e459241d6b30`
- Pre-recovery dirty entry count: **1116**
- index.lock holder: none (no open lock process)
- Worktree inventory captured in `worktree_list.txt` and `worktree_dirs.txt`.

## 2) Classification table (Phase 2)
- lfs_smudge_drift: **971**
- genuine_local_patch: **3**
- cascade_deletion: **52**
- genuine_new_file: **4**
- needs_review: **29**
- needs_review_untracked: **24**
- ignored: **33**

## 3) Backup inventory (Phase 3)
- Backup root: `/tmp/phoenix_omega_recovery_2026-05-08/`
- patches: **32**
- files: **26**
- new_files: **4**
- needs_review: **56**
- Total backup files: **118**

## 4) Recovery actions taken (Phase 4)
1. Attempted `git checkout origin/main -- .` after lock cleanup; git-lfs pointer/clean-filter errors blocked full completion.
2. Executed forced restore with filters disabled: `GIT_LFS_SKIP_SMUDGE=1 GIT_LFS_SKIP_CLEAN=1 git reset --hard origin/main`.
3. Captured post-recovery status to `status_post.txt`.
4. Attempted `git lfs pull`; command returned index update error and was documented (non-blocking per runbook).

## 5) Post-recovery state
- Post-recovery dirty entry count: **61**
- Remaining entries are `?? .claude/worktrees/...` style untracked directories (worktree artifacts), not tracked-file modifications/deletions.
- LFS pull: attempted; failed with `Error updating the Git index` (see `.git/lfs/logs/20260508T182030.048876.log`).

## 6) Wave A file location report (Phase 5)
- `artifacts/qa/ci_hygiene_fixes_2026-05-08.md`
  - `/Users/ahjan/phoenix_omega/artifacts/qa/ci_hygiene_fixes_2026-05-08.md` (size=10123, mtime=2026-05-08 13:04:20, sanity=exists)
  - `/tmp/phoenix_omega_recovery_2026-05-08/new_files/artifacts/qa/ci_hygiene_fixes_2026-05-08.md` (size=10123, mtime=2026-05-08 13:04:20, sanity=exists)
- `artifacts/qa/cosyvoice2_reference_voice_audit_2026-05-08.tsv`
  - `/Users/ahjan/phoenix_omega/artifacts/qa/cosyvoice2_reference_voice_audit_2026-05-08.tsv` (size=2706, mtime=2026-05-08 11:15:22, sanity=exists)
  - `/Users/ahjan/phoenix_omega_cosyvoice_audit_wt/artifacts/qa/cosyvoice2_reference_voice_audit_2026-05-08.tsv` (size=2706, mtime=2026-05-08 11:16:04, sanity=exists)
  - `/tmp/phoenix_omega_recovery_2026-05-08/new_files/artifacts/qa/cosyvoice2_reference_voice_audit_2026-05-08.tsv` (size=2706, mtime=2026-05-08 11:15:22, sanity=exists)
- `artifacts/qa/overlay_enforcement_phase_1_impl_2026-05-08.md`
  - `/Users/ahjan/phoenix_omega/artifacts/qa/overlay_enforcement_phase_1_impl_2026-05-08.md` (size=4419, mtime=2026-05-08 13:03:02, sanity=exists)
  - `/tmp/phoenix_omega_recovery_2026-05-08/new_files/artifacts/qa/overlay_enforcement_phase_1_impl_2026-05-08.md` (size=4419, mtime=2026-05-08 13:03:02, sanity=exists)
- `artifacts/video/teacher_30s_v1/ahjan/script_en_US.yaml`
  - `/Users/ahjan/phoenix_omega/artifacts/video/teacher_30s_v1/ahjan/script_en_US.yaml` (size=2054, mtime=2026-05-08 11:22:21, sanity=yaml_ok)
  - `/tmp/phoenix_omega_recovery_2026-05-08/needs_review/artifacts/video/teacher_30s_v1/ahjan/script_en_US.yaml` (size=2054, mtime=2026-05-08 11:22:21, sanity=yaml_ok)
- `artifacts/video/teacher_30s_v1/joshin/script_ja_JP.yaml`
  - `/Users/ahjan/phoenix_omega/artifacts/video/teacher_30s_v1/joshin/script_ja_JP.yaml` (size=2078, mtime=2026-05-08 11:22:22, sanity=yaml_ok)
  - `/tmp/phoenix_omega_recovery_2026-05-08/needs_review/artifacts/video/teacher_30s_v1/joshin/script_ja_JP.yaml` (size=2078, mtime=2026-05-08 11:22:22, sanity=yaml_ok)
- `artifacts/video/teacher_30s_v1/junko/script_ja_JP.yaml`
  - `/Users/ahjan/phoenix_omega/artifacts/video/teacher_30s_v1/junko/script_ja_JP.yaml` (size=1973, mtime=2026-05-08 11:22:22, sanity=yaml_ok)
  - `/tmp/phoenix_omega_recovery_2026-05-08/needs_review/artifacts/video/teacher_30s_v1/junko/script_ja_JP.yaml` (size=1973, mtime=2026-05-08 11:22:22, sanity=yaml_ok)
- `artifacts/video/teacher_30s_v1/maat/script_en_US.yaml`
  - `/Users/ahjan/phoenix_omega/artifacts/video/teacher_30s_v1/maat/script_en_US.yaml` (size=2030, mtime=2026-05-08 11:22:21, sanity=yaml_ok)
  - `/tmp/phoenix_omega_recovery_2026-05-08/needs_review/artifacts/video/teacher_30s_v1/maat/script_en_US.yaml` (size=2030, mtime=2026-05-08 11:22:21, sanity=yaml_ok)
- `artifacts/video/teacher_30s_v1/master_feung/script_zh_CN.yaml`
  - `/Users/ahjan/phoenix_omega/artifacts/video/teacher_30s_v1/master_feung/script_zh_CN.yaml` (size=1979, mtime=2026-05-08 11:22:22, sanity=yaml_ok)
  - `/tmp/phoenix_omega_recovery_2026-05-08/needs_review/artifacts/video/teacher_30s_v1/master_feung/script_zh_CN.yaml` (size=1979, mtime=2026-05-08 11:22:22, sanity=yaml_ok)
- `artifacts/video/teacher_30s_v1/master_sha/script_en_US.yaml`
  - `/Users/ahjan/phoenix_omega/artifacts/video/teacher_30s_v1/master_sha/script_en_US.yaml` (size=1984, mtime=2026-05-08 11:22:21, sanity=yaml_ok)
  - `/tmp/phoenix_omega_recovery_2026-05-08/needs_review/artifacts/video/teacher_30s_v1/master_sha/script_en_US.yaml` (size=1984, mtime=2026-05-08 11:22:21, sanity=yaml_ok)
- `artifacts/video/teacher_30s_v1/master_wu/script_zh_TW.yaml`
  - `/Users/ahjan/phoenix_omega/artifacts/video/teacher_30s_v1/master_wu/script_zh_TW.yaml` (size=1947, mtime=2026-05-08 11:22:22, sanity=yaml_ok)
  - `/tmp/phoenix_omega_recovery_2026-05-08/needs_review/artifacts/video/teacher_30s_v1/master_wu/script_zh_TW.yaml` (size=1947, mtime=2026-05-08 11:22:22, sanity=yaml_ok)
- `artifacts/video/teacher_30s_v1/miki/script_ja_JP.yaml`
  - `/Users/ahjan/phoenix_omega/artifacts/video/teacher_30s_v1/miki/script_ja_JP.yaml` (size=1942, mtime=2026-05-08 11:22:22, sanity=yaml_ok)
  - `/tmp/phoenix_omega_recovery_2026-05-08/needs_review/artifacts/video/teacher_30s_v1/miki/script_ja_JP.yaml` (size=1942, mtime=2026-05-08 11:22:22, sanity=yaml_ok)
- `artifacts/video/teacher_30s_v1/omote/script_ja_JP.yaml`
  - `/Users/ahjan/phoenix_omega/artifacts/video/teacher_30s_v1/omote/script_ja_JP.yaml` (size=2064, mtime=2026-05-08 11:22:21, sanity=yaml_ok)
  - `/tmp/phoenix_omega_recovery_2026-05-08/needs_review/artifacts/video/teacher_30s_v1/omote/script_ja_JP.yaml` (size=2064, mtime=2026-05-08 11:22:21, sanity=yaml_ok)
- `artifacts/video/teacher_30s_v1/pamela_fellows/script_en_US.yaml`
  - `/Users/ahjan/phoenix_omega/artifacts/video/teacher_30s_v1/pamela_fellows/script_en_US.yaml` (size=1927, mtime=2026-05-08 11:22:23, sanity=yaml_ok)
  - `/tmp/phoenix_omega_recovery_2026-05-08/needs_review/artifacts/video/teacher_30s_v1/pamela_fellows/script_en_US.yaml` (size=1927, mtime=2026-05-08 11:22:23, sanity=yaml_ok)
- `artifacts/video/teacher_30s_v1/ra/script_en_US.yaml`
  - `/Users/ahjan/phoenix_omega/artifacts/video/teacher_30s_v1/ra/script_en_US.yaml` (size=2022, mtime=2026-05-08 11:22:21, sanity=yaml_ok)
  - `/tmp/phoenix_omega_recovery_2026-05-08/needs_review/artifacts/video/teacher_30s_v1/ra/script_en_US.yaml` (size=2022, mtime=2026-05-08 11:22:21, sanity=yaml_ok)
- `artifacts/video/teacher_30s_v1/sai_ma/script_en_US.yaml`
  - `/Users/ahjan/phoenix_omega/artifacts/video/teacher_30s_v1/sai_ma/script_en_US.yaml` (size=2017, mtime=2026-05-08 11:22:21, sanity=yaml_ok)
  - `/tmp/phoenix_omega_recovery_2026-05-08/needs_review/artifacts/video/teacher_30s_v1/sai_ma/script_en_US.yaml` (size=2017, mtime=2026-05-08 11:22:21, sanity=yaml_ok)
- `config/quality/refrain_allowlist.yaml`
  - `/Users/ahjan/phoenix_omega/config/quality/refrain_allowlist.yaml` (size=14157, mtime=2026-05-08 18:19:08, sanity=yaml_ok)
  - `/Users/ahjan/phoenix_omega_30s_amendment_wt/config/quality/refrain_allowlist.yaml` (size=14157, mtime=2026-05-08 12:48:36, sanity=yaml_ok)
  - `/Users/ahjan/phoenix_omega_catalog_v2_isolation_wt/config/quality/refrain_allowlist.yaml` (size=14157, mtime=2026-05-08 12:01:36, sanity=yaml_ok)
  - `/Users/ahjan/phoenix_omega_cosyvoice_audit_wt/config/quality/refrain_allowlist.yaml` (size=14157, mtime=2026-05-08 11:55:26, sanity=yaml_ok)
  - `/Users/ahjan/phoenix_omega_feature_audit_wt/config/quality/refrain_allowlist.yaml` (size=14157, mtime=2026-05-08 14:32:11, sanity=yaml_ok)
  - `/Users/ahjan/phoenix_omega_handoff_pr959_wt/config/quality/refrain_allowlist.yaml` (size=14157, mtime=2026-05-08 16:35:50, sanity=yaml_ok)
  - `/Users/ahjan/phoenix_omega_lettering_v2_wt/config/quality/refrain_allowlist.yaml` (size=14157, mtime=2026-05-08 02:56:45, sanity=yaml_ok)
  - `/Users/ahjan/phoenix_omega_loc_30s_batch_wt/config/quality/refrain_allowlist.yaml` (size=14157, mtime=2026-05-08 11:50:01, sanity=yaml_ok)
  - `/Users/ahjan/phoenix_omega_phase_c_isolation_wt/config/quality/refrain_allowlist.yaml` (size=14157, mtime=2026-05-08 11:56:04, sanity=yaml_ok)
  - `/Users/ahjan/phoenix_omega_qi_foundation_recon_wt/config/quality/refrain_allowlist.yaml` (size=14157, mtime=2026-05-08 11:28:50, sanity=yaml_ok)
  - `/tmp/phoenix_omega_recovery_2026-05-08/patches/config__quality__refrain_allowlist.yaml.patch` (size=15609, mtime=2026-05-08 17:48:24, sanity=patch_present)
- `phoenix_v4/quality/book_quality_gate.py`
  - `/Users/ahjan/phoenix_omega/phoenix_v4/quality/book_quality_gate.py` (size=9016, mtime=2026-05-08 18:19:10, sanity=exists)
  - `/Users/ahjan/phoenix_omega_30s_amendment_wt/phoenix_v4/quality/book_quality_gate.py` (size=9016, mtime=2026-05-08 12:51:29, sanity=exists)
  - `/Users/ahjan/phoenix_omega_catalog_v2_isolation_wt/phoenix_v4/quality/book_quality_gate.py` (size=9016, mtime=2026-05-08 12:04:28, sanity=exists)
  - `/Users/ahjan/phoenix_omega_cosyvoice_audit_wt/phoenix_v4/quality/book_quality_gate.py` (size=9016, mtime=2026-05-08 11:59:39, sanity=exists)
  - `/Users/ahjan/phoenix_omega_feature_audit_wt/phoenix_v4/quality/book_quality_gate.py` (size=9016, mtime=2026-05-08 14:33:45, sanity=exists)
  - `/Users/ahjan/phoenix_omega_handoff_pr959_wt/phoenix_v4/quality/book_quality_gate.py` (size=9016, mtime=2026-05-08 16:38:27, sanity=exists)
  - `/Users/ahjan/phoenix_omega_lettering_v2_wt/phoenix_v4/quality/book_quality_gate.py` (size=9016, mtime=2026-05-08 02:58:36, sanity=exists)
  - `/Users/ahjan/phoenix_omega_loc_30s_batch_wt/phoenix_v4/quality/book_quality_gate.py` (size=9016, mtime=2026-05-08 11:53:57, sanity=exists)
  - `/Users/ahjan/phoenix_omega_maat_prose_wt/phoenix_v4/quality/book_quality_gate.py` (size=8395, mtime=2026-05-08 02:42:18, sanity=exists)
  - `/Users/ahjan/phoenix_omega_operator_decisions_ratification_wt/phoenix_v4/quality/book_quality_gate.py` (size=9016, mtime=2026-05-08 16:58:35, sanity=exists)
  - `/Users/ahjan/phoenix_omega_pearl_github_wt/phoenix_v4/quality/book_quality_gate.py` (size=7091, mtime=2026-05-07 14:41:25, sanity=exists)
  - `/Users/ahjan/phoenix_omega_pearl_star_install_prep_wt/phoenix_v4/quality/book_quality_gate.py` (size=7091, mtime=2026-05-07 21:57:12, sanity=exists)
  - `/Users/ahjan/phoenix_omega_phase_c_isolation_wt/phoenix_v4/quality/book_quality_gate.py` (size=9016, mtime=2026-05-08 11:57:56, sanity=exists)
  - `/Users/ahjan/phoenix_omega_qi_foundation_recon_wt/phoenix_v4/quality/book_quality_gate.py` (size=9016, mtime=2026-05-08 11:28:51, sanity=exists)
  - `/tmp/phoenix_omega_recovery_2026-05-08/patches/phoenix_v4__quality__book_quality_gate.py.patch` (size=11838, mtime=2026-05-08 17:48:28, sanity=patch_present)
- `scripts/ci/audit_llm_callers.py`
  - `/Users/ahjan/phoenix_omega/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 11:28:17, sanity=exists)
  - `/Users/ahjan/phoenix_omega_30s_amendment_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 12:51:30, sanity=exists)
  - `/Users/ahjan/phoenix_omega_catalog_v2_isolation_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 12:04:32, sanity=exists)
  - `/Users/ahjan/phoenix_omega_cosyvoice_audit_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 11:59:44, sanity=exists)
  - `/Users/ahjan/phoenix_omega_envfixes_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 13:58:01, sanity=exists)
  - `/Users/ahjan/phoenix_omega_feature_audit_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 14:33:46, sanity=exists)
  - `/Users/ahjan/phoenix_omega_genre_lora_skip_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-07 20:56:29, sanity=exists)
  - `/Users/ahjan/phoenix_omega_handoff_pr959_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 16:38:30, sanity=exists)
  - `/Users/ahjan/phoenix_omega_lettering_v2_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 02:58:44, sanity=exists)
  - `/Users/ahjan/phoenix_omega_loc_30s_batch_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 11:54:04, sanity=exists)
  - `/Users/ahjan/phoenix_omega_maat_prose_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 02:42:18, sanity=exists)
  - `/Users/ahjan/phoenix_omega_operator_decisions_ratification_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 16:58:39, sanity=exists)
  - `/Users/ahjan/phoenix_omega_pearl_github_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-07 14:41:28, sanity=exists)
  - `/Users/ahjan/phoenix_omega_pearl_star_install_prep_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-07 21:57:14, sanity=exists)
  - `/Users/ahjan/phoenix_omega_phase_c_isolation_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 11:57:57, sanity=exists)
  - `/Users/ahjan/phoenix_omega_qi_foundation_recon_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 02:42:18, sanity=exists)
  - `/Users/ahjan/phoenix_omega_session_debrief_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 13:26:20, sanity=exists)
  - `/Users/ahjan/phoenix_omega_style_review_wt/scripts/ci/audit_llm_callers.py` (size=6140, mtime=2026-05-08 11:52:23, sanity=exists)
- `scripts/ci/pr_governance_review.py`
  - `/Users/ahjan/phoenix_omega/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 11:28:17, sanity=exists)
  - `/Users/ahjan/phoenix_omega_30s_amendment_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 12:51:30, sanity=exists)
  - `/Users/ahjan/phoenix_omega_catalog_v2_isolation_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 12:04:32, sanity=exists)
  - `/Users/ahjan/phoenix_omega_cosyvoice_audit_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 11:59:44, sanity=exists)
  - `/Users/ahjan/phoenix_omega_envfixes_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 13:58:01, sanity=exists)
  - `/Users/ahjan/phoenix_omega_feature_audit_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 14:33:47, sanity=exists)
  - `/Users/ahjan/phoenix_omega_genre_lora_skip_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-07 20:56:29, sanity=exists)
  - `/Users/ahjan/phoenix_omega_handoff_pr959_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 16:38:31, sanity=exists)
  - `/Users/ahjan/phoenix_omega_lettering_v2_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 02:58:46, sanity=exists)
  - `/Users/ahjan/phoenix_omega_loc_30s_batch_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 11:54:05, sanity=exists)
  - `/Users/ahjan/phoenix_omega_maat_prose_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 02:42:18, sanity=exists)
  - `/Users/ahjan/phoenix_omega_operator_decisions_ratification_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 16:58:39, sanity=exists)
  - `/Users/ahjan/phoenix_omega_pearl_github_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-07 14:41:28, sanity=exists)
  - `/Users/ahjan/phoenix_omega_pearl_star_install_prep_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-07 21:57:14, sanity=exists)
  - `/Users/ahjan/phoenix_omega_phase_c_isolation_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 11:57:58, sanity=exists)
  - `/Users/ahjan/phoenix_omega_qi_foundation_recon_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 02:42:18, sanity=exists)
  - `/Users/ahjan/phoenix_omega_session_debrief_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 13:26:20, sanity=exists)
  - `/Users/ahjan/phoenix_omega_style_review_wt/scripts/ci/pr_governance_review.py` (size=13111, mtime=2026-05-08 11:52:23, sanity=exists)
- `tests/ci/test_audit_llm_callers_roots.py`
  - `/Users/ahjan/phoenix_omega/tests/ci/test_audit_llm_callers_roots.py` (size=3376, mtime=2026-05-08 11:10:28, sanity=exists)
  - `/tmp/phoenix_omega_recovery_2026-05-08/needs_review/tests/ci/test_audit_llm_callers_roots.py` (size=3376, mtime=2026-05-08 11:10:28, sanity=exists)
- `tests/ci/test_pr_governance_review_fallback.py`
  - `/Users/ahjan/phoenix_omega/tests/ci/test_pr_governance_review_fallback.py` (size=3955, mtime=2026-05-08 11:04:10, sanity=exists)
  - `/tmp/phoenix_omega_recovery_2026-05-08/needs_review/tests/ci/test_pr_governance_review_fallback.py` (size=3955, mtime=2026-05-08 11:04:10, sanity=exists)
- `tests/quality/test_overlay_enforcement.py`
  - `/Users/ahjan/phoenix_omega/tests/quality/test_overlay_enforcement.py` (size=7764, mtime=2026-05-08 11:06:33, sanity=exists)
  - `/tmp/phoenix_omega_recovery_2026-05-08/new_files/tests/quality/test_overlay_enforcement.py` (size=7764, mtime=2026-05-08 11:06:33, sanity=exists)

## 7) Recommended next step
- Use `wave_a_locations.tsv` as the source-of-truth map for recovery PR planning.
- Prefer promoting Wave A new YAML/TSV/MD assets from backup paths under `/tmp/phoenix_omega_recovery_2026-05-08/new_files/` where present.
- For modified source files (`book_quality_gate.py`, `refrain_allowlist.yaml`, CI scripts), consume patch artifacts under `/tmp/phoenix_omega_recovery_2026-05-08/patches/` and apply in a clean implementation branch.
- If full binary parity is required, resolve the local git-lfs index issue separately before doing any LFS-heavy local runs in `/Users/ahjan/phoenix_omega`.
