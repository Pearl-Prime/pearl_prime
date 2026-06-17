# Drift Sentinel — PoC run report

**Canonical Artifact Graph:** 409 nodes (docs/**/*.md), 130,131 TF-IDF features. Free/local, CPU, ~1s build.

**Similarity distribution (all artifact pairs):** median=0.016  p95=0.046  p99=0.088  max=0.465  → thresholds WARN≥0.28, BLOCK≥0.4 sit at the far tail (only 0.03% of pairs ≥ WARN).

## Demo 1 — latent drift the Sentinel finds in the repo *as it stands today*
The most-similar EXISTING doc pairs. High similarity = candidate duplicate / parallel / drifted artifacts that a graph would have flagged the moment the second one was written.

| sim | artifact A | artifact B |
|----:|------------|------------|
| ⛔ 0.465 | `docs/HANDOFF_PR1326_MKDIR_FIX_DISCOVERY_2026-06-11.md` | `docs/HANDOFF_PR1326_MKDIR_REDISCOVERY_SESSION2_2026-06-11.md` |
| ⛔ 0.446 | `docs/brand_admin/zh_HK_distribution_guide.md` | `docs/brand_admin/zh_TW_distribution_guide.md` |
| ⛔ 0.404 | `docs/MARKETING_FREE_SOURCES.md` | `docs/research/RESEARCH_FEED_SOURCES.md` |
| ⚠️ 0.388 | `docs/brand_admin/zh_HK_distribution_guide.md` | `docs/brand_admin/zh_SG_distribution_guide.md` |
| ⚠️ 0.385 | `docs/PR_B_VISUAL_IDENTITY_EXECUTION_CHECKLIST.md` | `docs/PR_B_VISUAL_IDENTITY_RUNBOOK.md` |
| ⚠️ 0.373 | `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` | `docs/MANGA_DRAWING_TRADITIONS_RESEARCH_2026-05-02.md` |
| ⚠️ 0.368 | `docs/ONBOARDING_PROOF_ASSET_PRODUCTION_BACKLOG.md` | `docs/ONBOARDING_PROOF_FIDELITY_UPGRADE_LANE.md` |
| ⚠️ 0.367 | `docs/brand_admin/zh_SG_distribution_guide.md` | `docs/brand_admin/zh_TW_distribution_guide.md` |
| ⚠️ 0.360 | `docs/CONTROL_PLANE_GO_NO_GO.md` | `docs/CONTROL_PLANE_RUNBOOK.md` |
| ⚠️ 0.354 | `docs/PEARL_NEWS_GITHUB_SCHEDULING.md` | `docs/PEARL_NEWS_OPTION_B_RUNBOOK.md` |
| ⚠️ 0.332 | `docs/email_sequences/README.md` | `docs/email_sequences/exercise-one-liners.md` |
| ⚠️ 0.316 | `docs/LOCAL_CREDENTIALS_INTAKE_RUNBOOK.md` | `docs/MESSAGING_CHANNELS_LOCAL_SETUP.md` |
| ⚠️ 0.312 | `docs/brand_admin/en_US_distribution_guide.md` | `docs/brand_admin/zh_SG_distribution_guide.md` |
| ⚠️ 0.312 | `docs/ONBOARDING_POST_MERGE_HYGIENE.md` | `docs/REPO_HYGIENE_AND_WORKTREE_CLEANUP.md` |
| ⚠️ 0.311 | `docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md` | `docs/TEACHER_MODE_SYSTEM_REFERENCE.md` |
| ⚠️ 0.308 | `docs/COMMUNITY_ASSETS_AUDIT_2026-04-29.md` | `docs/FORK_WRAP_BUILD_DECISIONS_2026-04-29.md` |
| ⚠️ 0.302 | `docs/BOOK_001_FREEZE.md` | `docs/BOOK_001_POST_MORTEM.md` |
| ⚠️ 0.301 | `docs/LOCAL_CREDENTIALS_INTAKE_RUNBOOK.md` | `docs/WORDPRESS_LOCAL_SETUP.md` |

## Demo 2 — live intercept: an agent is *about to write* a doc that already exists
Each case feeds the **body** of a REAL existing artifact (filename stripped — simulating an agent re-authoring it in their own words under a NEW name) against the full graph. A new locale/guide/spec that merely re-states existing canon is the single most common drift; the Sentinel catches it and points at what to reuse.

**Agent proposes:** `docs/brand_admin/zh_MO_distribution_guide.md` — *a 5th locale guide, hand-authored from scratch*
&nbsp;&nbsp;(its body = a re-authoring of the real `docs/brand_admin/zh_HK_distribution_guide.md`)
&nbsp;&nbsp;**Sentinel:** ⛔ BLOCK — nearest existing canonical:
&nbsp;&nbsp;&nbsp;&nbsp;`0.990` → `docs/brand_admin/zh_HK_distribution_guide.md`  ⟵ the original
&nbsp;&nbsp;&nbsp;&nbsp;`0.438` → `docs/brand_admin/zh_TW_distribution_guide.md`
&nbsp;&nbsp;&nbsp;&nbsp;`0.381` → `docs/brand_admin/zh_SG_distribution_guide.md`
&nbsp;&nbsp;💬 *“Wait — this is ~99% the same as `docs/brand_admin/zh_HK_distribution_guide.md` (already canonical). Reuse / extend it instead of greenfielding a new file.”*

**Agent proposes:** `docs/VISUAL_IDENTITY_EXECUTION_GUIDE.md` — *a 'new' visual-identity guide*
&nbsp;&nbsp;(its body = a re-authoring of the real `docs/PR_B_VISUAL_IDENTITY_RUNBOOK.md`)
&nbsp;&nbsp;**Sentinel:** ⛔ BLOCK — nearest existing canonical:
&nbsp;&nbsp;&nbsp;&nbsp;`0.986` → `docs/PR_B_VISUAL_IDENTITY_RUNBOOK.md`  ⟵ the original
&nbsp;&nbsp;&nbsp;&nbsp;`0.380` → `docs/PR_B_VISUAL_IDENTITY_EXECUTION_CHECKLIST.md`
&nbsp;&nbsp;&nbsp;&nbsp;`0.137` → `docs/BRAND_ADMIN_ONBOARDING_PAGES_SPEC.md`
&nbsp;&nbsp;💬 *“Wait — this is ~99% the same as `docs/PR_B_VISUAL_IDENTITY_RUNBOOK.md` (already canonical). Reuse / extend it instead of greenfielding a new file.”*

**Agent proposes:** `docs/CONTROL_PLANE_OPERATIONS_GUIDE.md` — *a parallel control-plane runbook*
&nbsp;&nbsp;(its body = a re-authoring of the real `docs/CONTROL_PLANE_RUNBOOK.md`)
&nbsp;&nbsp;**Sentinel:** ⛔ BLOCK — nearest existing canonical:
&nbsp;&nbsp;&nbsp;&nbsp;`0.986` → `docs/CONTROL_PLANE_RUNBOOK.md`  ⟵ the original
&nbsp;&nbsp;&nbsp;&nbsp;`0.342` → `docs/CONTROL_PLANE_GO_NO_GO.md`
&nbsp;&nbsp;&nbsp;&nbsp;`0.137` → `docs/PHOENIX_OMEGA_ERROR_STATE_UX_SPEC.md`
&nbsp;&nbsp;💬 *“Wait — this is ~99% the same as `docs/CONTROL_PLANE_RUNBOOK.md` (already canonical). Reuse / extend it instead of greenfielding a new file.”*

**Agent proposes:** `docs/REPO_GOVERNANCE_SOURCE_OF_TRUTH.md` — *a fresh governance source-of-truth*
&nbsp;&nbsp;(its body = a re-authoring of the real `docs/GITHUB_GOVERNANCE.md`)
&nbsp;&nbsp;**Sentinel:** ⛔ BLOCK — nearest existing canonical:
&nbsp;&nbsp;&nbsp;&nbsp;`0.992` → `docs/GITHUB_GOVERNANCE.md`  ⟵ the original
&nbsp;&nbsp;&nbsp;&nbsp;`0.266` → `docs/GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md`
&nbsp;&nbsp;&nbsp;&nbsp;`0.248` → `docs/BRANCH_PROTECTION_REQUIREMENTS.md`
&nbsp;&nbsp;💬 *“Wait — this is ~99% the same as `docs/GITHUB_GOVERNANCE.md` (already canonical). Reuse / extend it instead of greenfielding a new file.”*

## Demo 3 — control: a genuinely new artifact passes clean (no false alarm)
**Agent proposes:** `docs/QUANTUM_RIBBON_TELEMETRY_SPEC.md` (truly unrelated)
&nbsp;&nbsp;**Sentinel:** ✅ OK — nearest is only `0.045` (`docs/PEARL_PRIME_REGISTER_GATE_SPEC.md`). Below WARN → no false alarm; the agent proceeds.

---
*PoC uses TF-IDF cosine as a free/local stand-in for the production BGE-m3 embedder; the graph + gate logic is identical. Production adds: subsystem/owner/anchor-SHA edges, the inline PreToolUse hook tier, and the learning loop that promotes every confirmed catch into a sharper detector.*