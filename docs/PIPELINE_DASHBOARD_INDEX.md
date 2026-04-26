# Pipeline Dashboard Index

**Last updated:** 2026-04-27

Single-page operator-facing index for everything in the repo. Each row is a link plus a one-line description. Browse in under 30 seconds; click into any linked doc for the actual content. No content is duplicated here.

> Authority: Pearl_Architect. Closes G1 in `FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md` (dashboard subsystem entry point). Owner of dashboard subsystem = Pearl_Brand (per DASH-02; see [PEARL_ARCHITECT_STATE](PEARL_ARCHITECT_STATE.md)).

## Table of contents

1. [System overview](#1-system-overview)
2. [Canonical authority docs](#2-canonical-authority-docs)
3. [Architecture](#3-architecture)
4. [Audit + canonical maps](#4-audit--canonical-maps)
5. [Pipeline matrix + inventory](#5-pipeline-matrix--inventory)
6. [Coordination state](#6-coordination-state)
7. [Brand surfaces](#7-brand-surfaces)
8. [Manga catalog](#8-manga-catalog)
9. [Manga production](#9-manga-production)
10. [Pearl Prime](#10-pearl-prime)
11. [Pearl News](#11-pearl-news)
12. [Audiobook + Podcast + Video + TTS](#12-audiobook--podcast--video--tts)
13. [Marketing](#13-marketing)
14. [Integrations](#14-integrations)
15. [CI / governance](#15-ci--governance)
16. [Open PRs](#16-open-prs)
17. [Audit tooling](#17-audit-tooling)
18. [Active workstream gaps](#18-active-workstream-gaps)

---

## 1. System overview

| Link | Description |
| --- | --- |
| [PLAIN_ENGLISH_SYSTEM_OVERVIEW](PLAIN_ENGLISH_SYSTEM_OVERVIEW.md) | Plain-English narrative of what the whole system does |
| [SYSTEMS_V4](SYSTEMS_V4.md) | V4 systems map — pipelines, layers, modes |

## 2. Canonical authority docs

Source: [`SUBSYSTEM_AUTHORITY_MAP.tsv`](../artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv). Each subsystem has one or more authority specs; this is the live list.

| Subsystem | Authority docs | Owner |
| --- | --- | --- |
| core_pipeline | [PHOENIX_ARC_FIRST_CANONICAL_SPEC](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md), [PHOENIX_V4_5_WRITER_SPEC](../specs/PHOENIX_V4_5_WRITER_SPEC.md) | Pearl_Prime |
| pearl_prime | [PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC](PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md), [PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC](PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md) | Pearl_Prime |
| teacher_mode | [SYSTEMS_V4](SYSTEMS_V4.md), [PHOENIX_V4_5_WRITER_SPEC](../specs/PHOENIX_V4_5_WRITER_SPEC.md) | Pearl_Editor |
| manga_pipeline | [AI_MANGA_PIPELINE_SUMMARY](../specs/AI_MANGA_PIPELINE_SUMMARY.md), [MANGA_IMPLEMENTATION_OUTLINE](MANGA_IMPLEMENTATION_OUTLINE.md) | Pearl_Dev |
| pearl_news | [PEARL_NEWS_WRITER_SPEC](PEARL_NEWS_WRITER_SPEC.md), [PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE](research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md) | Pearl_News |
| translation | [localization quality_contracts README](../config/localization/quality_contracts/README.md), [DOCS_INDEX](DOCS_INDEX.md) | Pearl_Localization |
| video_pipeline | [scripts/video/README](../scripts/video/README.md), [VIDEO_PIPELINE_SPEC](VIDEO_PIPELINE_SPEC.md) | Pearl_Video |
| ei_v2 | `phoenix_v4/quality/ei_v2/`, [DOCS_INDEX](DOCS_INDEX.md) | Pearl_Research |
| trend_feeds | [TREND_FEED_INTEGRATION_STRATEGY](TREND_FEED_INTEGRATION_STRATEGY.md), `scripts/feeds/` | Pearl_Int |
| brand_admin | [OLD_CHAT_AND_HOME_PROMOTION_SPEC](OLD_CHAT_AND_HOME_PROMOTION_SPEC.md), [BRAND_ADMIN_CANONICAL_PACKAGE](../BRAND_ADMIN_CANONICAL_PACKAGE.md) | Pearl_Prez |
| ite | `phoenix_v4/manga/ite_pipeline.py`, [DOCS_INDEX](DOCS_INDEX.md) | Pearl_Dev |
| integrations | [INTEGRATION_CREDENTIALS_REGISTRY](INTEGRATION_CREDENTIALS_REGISTRY.md), `skills/pearl-int/SKILL.md` | Pearl_Int |
| pearl_devops | [GITHUB_OPERATIONS_FRAMEWORK](GITHUB_OPERATIONS_FRAMEWORK.md), [GITHUB_GOVERNANCE](GITHUB_GOVERNANCE.md), [BRANCH_PROTECTION_REQUIREMENTS](BRANCH_PROTECTION_REQUIREMENTS.md), [CLAUDE.md](../CLAUDE.md) | Pearl_DevOps |
| audiobook_pipeline | [AUDIOBOOK_OPS_MANUAL](AUDIOBOOK_OPS_MANUAL.md), [AUDIOBOOK_PIPELINE_SPEC](AUDIOBOOK_PIPELINE_SPEC.md) | Pearl_Dev |
| marketing | [OLD_CHAT_AND_HOME_PROMOTION_SPEC](OLD_CHAT_AND_HOME_PROMOTION_SPEC.md), `marketing_deep_research/` | Pearl_Marketing |
| podcast_pipeline | [PODCAST_PIPELINE_INTEGRATION_SPEC](PODCAST_PIPELINE_INTEGRATION_SPEC.md), `pearl_news/research/podcast/` | Pearl_Prime |
| dashboard | [PEARL_ARCHITECT_STATE](PEARL_ARCHITECT_STATE.md) (DASH-02), [BRAND_ADMIN_CANONICAL_PACKAGE](../BRAND_ADMIN_CANONICAL_PACKAGE.md) | Pearl_Brand |

## 3. Architecture

| Link | Description |
| --- | --- |
| [FULL_REPO_ARCHITECTURE_MAP_2026-04-26](FULL_REPO_ARCHITECTURE_MAP_2026-04-26.md) | Whole-repo architecture map produced by Pearl_Architect |
| [PEARL_ARCHITECT_STATE](PEARL_ARCHITECT_STATE.md) | Pearl_Architect live state (DASH-02, BR-CANON-01, etc.) |
| [PEARL_PM_STATE](PEARL_PM_STATE.md) | Pearl_PM live state (active projects, workstreams) |
| [AGENT_FILE_PERSISTENCE_PROTOCOL](AGENT_FILE_PERSISTENCE_PROTOCOL.md) | File persistence enforcement contract |

## 4. Audit + canonical maps

| Link | Description |
| --- | --- |
| [FULL_REPO_SYSTEM_AUDIT_2026-04-26](FULL_REPO_SYSTEM_AUDIT_2026-04-26.md) | Full audit of all subsystems and pipelines |
| [FULL_REPO_CANONICAL_SYSTEM_MAP_2026-04-26](FULL_REPO_CANONICAL_SYSTEM_MAP_2026-04-26.md) | Canonical system map keyed to authority docs |
| [FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26](FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md) | Deprecation & deletion plan (PR ladder D1, D2, ..., PR 6 = this dashboard) |
| [FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26](FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md) | Gap inventory G1-G5, N1-N3 with execution ladder |
| ⚠️ `specs/NEXT_PHASE_EXECUTION_SPEC_2026-04-27.md` | Referenced as G1 spec authority; **file not present yet — operator should create or this row should be relabelled to point at the gap plan ladder above** |

## 5. Pipeline matrix + inventory

| Link | Description |
| --- | --- |
| [pipeline_matrix 2026-04-27](../artifacts/inventory/full_repo_pipeline_matrix_2026-04-27.csv) | Live pipeline matrix (CSV) — every pipeline + its entrypoint, callers, configs |
| [pipeline_matrix 2026-04-26](../artifacts/inventory/full_repo_pipeline_matrix_2026-04-26.csv) | Previous snapshot (for diffing) |
| [doc_status_matrix 2026-04-27](../artifacts/inventory/full_repo_doc_status_matrix_2026-04-27.csv.gz) | Per-doc status (canonical / superseded / orphan) |
| [doc_status_matrix 2026-04-26](../artifacts/inventory/full_repo_doc_status_matrix_2026-04-26.csv.gz) | Previous snapshot |
| [file_inventory 2026-04-26](../artifacts/inventory/full_repo_file_inventory_2026-04-26.csv.gz) | Every tracked file with size, type, last_touched |
| [git_history_index 2026-04-26](../artifacts/inventory/full_repo_git_history_index_2026-04-26.csv) | Per-file commit history index |
| [audit_baseline 2026-04-26](../artifacts/inventory/full_repo_audit_baseline_2026-04-26.md) | Narrative audit baseline |

## 6. Coordination state

| Link | Description |
| --- | --- |
| [ACTIVE_PROJECTS.tsv](../artifacts/coordination/ACTIVE_PROJECTS.tsv) | Current projects under active work |
| [ACTIVE_WORKSTREAMS.tsv](../artifacts/coordination/ACTIVE_WORKSTREAMS.tsv) | In-flight workstreams (note: schema-malformed rows tracked in GAP-G3) |
| [SUBSYSTEM_AUTHORITY_MAP.tsv](../artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv) | Subsystem → authority docs + owner agent |
| [PEARL_PM_STATE](PEARL_PM_STATE.md) | PM agent's persistent state |

## 7. Brand surfaces

| Link | Description |
| --- | --- |
| [BRAND_ADMIN_CANONICAL_PACKAGE](../BRAND_ADMIN_CANONICAL_PACKAGE.md) | Canonical brand admin package (top of repo) |
| [canonical_brand_list.yaml](../config/manga/canonical_brand_list.yaml) | Manga-side canonical brand registry (Path X — separate from book brands) |
| [brand_registry.yaml](../config/brand_registry.yaml) | Book-pipeline brand registry |
| [brand_admin.html](../brand_admin.html) | Brand admin entry HTML (root) |
| [brand_admin_weekly_os.html](../brand_admin_weekly_os.html) | Brand admin weekly OS dashboard |
| [brand-wizard-app](../brand-wizard-app/) | Brand wizard app source (React/Cloudflare Pages) |
| [brand-wizard-app/public/brand_admin.html](../brand-wizard-app/public/brand_admin.html) | Static admin page served by brand-wizard-app |

## 8. Manga catalog

| Link | Description |
| --- | --- |
| [GENRE_PORTFOLIO_PLAN](GENRE_PORTFOLIO_PLAN.md) | Cross-locale genre portfolio plan |
| [CJK_CATALOG_PLAN](CJK_CATALOG_PLAN.md) | CJK catalog plan (CN/JP/KR/TW + others) |
| [US_CATALOG_PLAN](US_CATALOG_PLAN.md) | US catalog plan |
| [MANGA_CATALOG_RECONCILIATION_SPEC](../specs/MANGA_CATALOG_RECONCILIATION_SPEC.md) | Reconciliation spec (per-brand × per-genre allocations) |
| [manga_brand_series_plan.yaml](../config/manga/manga_brand_series_plan.yaml) | Series plan config |
| [scripts/manga/build_manga_catalog.py](../scripts/manga/build_manga_catalog.py) | Catalog generator |
| [scripts/catalog/dump_manga_series_plan_json.py](../scripts/catalog/dump_manga_series_plan_json.py) | Series plan JSON dumper |

## 9. Manga production

| Link | Description |
| --- | --- |
| [artifacts/manga/chapter_scripts/](../artifacts/manga/chapter_scripts/) | Chapter scripts (per-episode) |
| [artifacts/manga/panel_prompts/](../artifacts/manga/panel_prompts/) | Panel prompt JSON / per-episode |
| [scripts/manga/queue_panel_renders.py](../scripts/manga/queue_panel_renders.py) | Queue panel renders to ComfyUI |
| [scripts/manga/build_thumbnail_review_grid.py](../scripts/manga/build_thumbnail_review_grid.py) | Build thumbnail review grid for rendered panels |
| [scripts/manga/build_pre_render_script_preview.py](../scripts/manga/build_pre_render_script_preview.py) | Pre-render script preview |
| [scripts/manga/run_chapter_production.py](../scripts/manga/run_chapter_production.py) | End-to-end chapter production |
| [scripts/manga/run_chapter_visual.py](../scripts/manga/run_chapter_visual.py) | Visual-only chapter run |
| [MECHA_EP001_PEARL_STAR_RUNBOOK_2026-04-27](MECHA_EP001_PEARL_STAR_RUNBOOK_2026-04-27.md) | Pearl Star runbook for mecha ep_001 35-panel render |

## 10. Pearl Prime

| Link | Description |
| --- | --- |
| [PEARL_PRIME_BOOK_SYSTEM_CANONICAL](PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md) | Canonical doc for Pearl Prime book system |
| [PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC](PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md) | Bestseller writing overlay |
| [PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC](PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md) | Whole-workflow hardening spec |
| [PEARL_PRIME_RELEASE_CONTRACT](PEARL_PRIME_RELEASE_CONTRACT.md) | Release contract |
| [scripts/atom_writing/run_writing_campaign.py](../scripts/atom_writing/run_writing_campaign.py) | Atom-writing campaign runner |
| [scripts/catalog/generate_full_catalog.py](../scripts/catalog/generate_full_catalog.py) | Full catalog generation |
| [scripts/pearl_prime_multilingual/build_review_pack.py](../scripts/pearl_prime_multilingual/build_review_pack.py) | Multilingual review pack builder |
| [scripts/pearl_prime_multilingual/assemble_full_catalog_qa.py](../scripts/pearl_prime_multilingual/assemble_full_catalog_qa.py) | Locale-parameterized full-catalog QA |
| [scripts/pearl_prime_en_us/assemble_first_100_qa.py](../scripts/pearl_prime_en_us/assemble_first_100_qa.py) | EN-US first-100 QA assembler |

## 11. Pearl News

| Link | Description |
| --- | --- |
| [PEARL_NEWS_WRITER_SPEC](PEARL_NEWS_WRITER_SPEC.md) | Pearl News writer spec |
| [PEARL_NEWS_CONTRACT](PEARL_NEWS_CONTRACT.md) | Output contract |
| [PEARL_NEWS_ARCHITECTURE_SPEC](PEARL_NEWS_ARCHITECTURE_SPEC.md) | Architecture |
| [PEARL_NEWS_LLM_ROUTING](PEARL_NEWS_LLM_ROUTING.md) | LLM tier routing for News |
| [PEARL_NEWS_OPTION_B_RUNBOOK](PEARL_NEWS_OPTION_B_RUNBOOK.md) | Option-B runbook |
| [scripts/pearl_news/run_daily_news_cycle.py](../scripts/pearl_news/run_daily_news_cycle.py) | Daily news cycle runner |
| Live site: <https://pearlnewsuna.org> | Production deployment |

## 12. Audiobook + Podcast + Video + TTS

| Link | Description |
| --- | --- |
| [AUDIOBOOK_OPS_MANUAL](AUDIOBOOK_OPS_MANUAL.md) | Operator manual |
| [AUDIOBOOK_PIPELINE_SPEC](AUDIOBOOK_PIPELINE_SPEC.md) | Pipeline spec |
| [AUDIOBOOK_PIPELINE_COMPLETE_GUIDE](AUDIOBOOK_PIPELINE_COMPLETE_GUIDE.md) | Complete guide |
| [AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN](AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md) | Locale + catalog marketing plan (4th canonical doc post PR #686) |
| [scripts/audiobook/generate_showcase_bundle.py](../scripts/audiobook/generate_showcase_bundle.py) | Showcase bundle generator |
| [scripts/audiobook_script/run_regression.py](../scripts/audiobook_script/run_regression.py) | Audiobook script regression |
| [PODCAST_PIPELINE_COMPLETE_GUIDE](PODCAST_PIPELINE_COMPLETE_GUIDE.md) | Podcast complete guide |
| [PODCAST_PIPELINE_INTEGRATION_SPEC](PODCAST_PIPELINE_INTEGRATION_SPEC.md) | Podcast integration spec |
| [scripts/podcast/run_podcast_pipeline.py](../scripts/podcast/run_podcast_pipeline.py) | Podcast pipeline entry |
| [scripts/podcast/render_podcast_audio.py](../scripts/podcast/render_podcast_audio.py) | Podcast audio render |
| [VIDEO_PIPELINE_SPEC](VIDEO_PIPELINE_SPEC.md) | Video pipeline spec |
| [VIDEO_PIPELINE_COMPLETE_GUIDE](VIDEO_PIPELINE_COMPLETE_GUIDE.md) | Video complete guide |
| [scripts/video/README](../scripts/video/README.md) | Video pipeline README |
| [scripts/video/orchestrate_book_to_video.py](../scripts/video/orchestrate_book_to_video.py) | Book → video orchestration |
| [scripts/video/render_audiobook.py](../scripts/video/render_audiobook.py) | Audiobook video render |
| [scripts/video/render_videos.py](../scripts/video/render_videos.py) | Video render |
| [scripts/audio/generate_presenter_audio.py](../scripts/audio/generate_presenter_audio.py) | Presenter TTS (CosyVoice / ElevenLabs) |
| [scripts/audio/generate_teacher_showcase_audio.py](../scripts/audio/generate_teacher_showcase_audio.py) | Teacher-showcase TTS |
| ⚠️ `scripts/tts/` | No dedicated `scripts/tts/` dir — TTS lives under `scripts/audio/` and inside video pipeline. Operator: confirm if a top-level `scripts/tts/` should be created |

## 13. Marketing

| Link | Description |
| --- | --- |
| [funnel/](../funnel/) | Funnel system (landing pages, freebies) |
| [somatic_exercise_freebee_apps/](../somatic_exercise_freebee_apps/) | Somatic exercise freebie apps |
| [marketing_deep_research/](../marketing_deep_research/) | Marketing deep research outputs |
| ⚠️ `platform_marketing/` | Planned per `SUBSYSTEM_AUTHORITY_MAP.tsv` row 17; directory does not yet exist — operator decision required |

## 14. Integrations

| Link | Description |
| --- | --- |
| [INTEGRATION_CREDENTIALS_REGISTRY](INTEGRATION_CREDENTIALS_REGISTRY.md) | All credentials documented (read this first) |
| [scripts/ci/check_integration_env.py](../scripts/ci/check_integration_env.py) | Verify required env vars |
| [scripts/ci/integration_env_registry.py](../scripts/ci/integration_env_registry.py) | Single source of truth for env-var names |
| [scripts/ci/load_integration_env_from_keychain.py](../scripts/ci/load_integration_env_from_keychain.py) | Load env from macOS Keychain |
| [scripts/integrations/](../scripts/integrations/) | Integration shell helpers (Slack, Discord, WhatsApp, etc.) |
| Pearl Star endpoints | `COMFYUI_URL` (manga panel render), `COSYVOICE_URL` (CJK TTS), `GEMMA_BASE_URL` (English unattended LLM) — synthesis under integrations registry |

## 15. CI / governance

| Link | Description |
| --- | --- |
| [.github/workflows/](../.github/workflows/) | All 74 workflow files |
| [llm-policy-enforcement.yml](../.github/workflows/llm-policy-enforcement.yml) | Tier-policy gate (blocks paid LLM API keys) |
| [llm-callers-audit.yml](../.github/workflows/llm-callers-audit.yml) | Continuous LLM caller audit |
| [github-governance-check.yml](../.github/workflows/github-governance-check.yml) | PR governance review (mass-deletion, scope) |
| [docs-ci.yml](../.github/workflows/docs-ci.yml) | Docs governance CI |
| [scripts/ci/pr_governance_review.py](../scripts/ci/pr_governance_review.py) | PR governance review (Pearl_PM + Pearl_Architect gate) |
| [scripts/ci/check_docs_governance.py](../scripts/ci/check_docs_governance.py) | DOCS_INDEX governance enforcer |
| [scripts/ci/audit_llm_callers.py](../scripts/ci/audit_llm_callers.py) | LLM caller auditor |
| [scripts/ci/preflight_push.sh](../scripts/ci/preflight_push.sh) | Pre-push preflight |
| [scripts/git/push_guard.py](../scripts/git/push_guard.py) | Push-guard |
| [scripts/git/pre_merge_check.sh](../scripts/git/pre_merge_check.sh) | Pre-merge governance check |
| [scripts/git/health_check.sh](../scripts/git/health_check.sh) | Hourly repo health check |
| [GITHUB_OPERATIONS_FRAMEWORK](GITHUB_OPERATIONS_FRAMEWORK.md) | Ops framework |
| [GITHUB_GOVERNANCE](GITHUB_GOVERNANCE.md) | Governance policy |
| [BRANCH_PROTECTION_REQUIREMENTS](BRANCH_PROTECTION_REQUIREMENTS.md) | Branch protection rules |
| [GITHUB_GOVERNANCE_INCIDENT_RUNBOOK](GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md) | Incident runbook |

## 16. Open PRs

| Link | Description |
| --- | --- |
| <https://github.com/Ahjan108/phoenix_omega_v4.8/pulls> | All open PRs (live `gh pr list` URL) |

## 17. Audit tooling

| Link | Description |
| --- | --- |
| [scripts/audit/build_full_repo_inventory.py](../scripts/audit/build_full_repo_inventory.py) | Full file inventory generator |
| [scripts/audit/build_git_history_index.py](../scripts/audit/build_git_history_index.py) | Per-file git history index |
| [scripts/audit/classify_doc_status.py](../scripts/audit/classify_doc_status.py) | Doc status classifier (canonical / superseded / orphan) |
| [scripts/audit/build_pipeline_matrix.py](../scripts/audit/build_pipeline_matrix.py) | Pipeline matrix builder (AST-based import-counter) |
| [scripts/audit/remote_commit_review.py](../scripts/audit/remote_commit_review.py) | Remote commit review tooling |

## 18. Active workstream gaps

Source: [`FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md`](FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md). Status as of 2026-04-27.

| Gap | Subsystem | Description | Status |
| --- | --- | --- | --- |
| GAP-G1 | DevOps | `pr_governance_review.py` not wired to GitHub workflow | open — only manual via `pre_merge_check.sh` |
| GAP-G2 | PM | `PEARL_PM_STATE.md` last_verified 2026-04-10 (16+ days stale); 5 active projects but only 1 referenced | open |
| GAP-G3 | PM | 7 schema-malformed rows in `ACTIVE_WORKSTREAMS.tsv` (4×14-field + 3×16-field) | open |
| GAP-G4 | Architect | `dashboard` subsystem absent from authority map; no entry point existed | **closed** by this doc + DASH-02 (PR #709) |
| GAP-G5 | Architect | `Pearl_DevOps` subsystem absent from authority map; owns 72+ CI workflows | open |
| GAP-N1 | News | Pearl News v5.4 interactive sidebar — PR #592 open | partial |
| GAP-N2 | News | (see gap plan) | open |
| GAP-N3 | News | (see gap plan) | open |

---

**Maintenance:** any new subsystem, pipeline, or canonical spec must add a row here. Add in the matching section, keep one-line descriptions, link by relative repo path. Run `PYTHONPATH=. python3 scripts/ci/check_docs_governance.py --check-inventory` after any edit.
