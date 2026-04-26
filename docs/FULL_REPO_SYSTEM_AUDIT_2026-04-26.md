# Full Repo System Audit — 2026-04-26

**Audit owner:** Pearl_Architect (lead) + Pearl_PM (coordination)
**Branch:** `agent/full-repo-reconciliation-20260426`
**Baseline SHA:** `1f4f8a28fc0e09163b4a88653074114c337ca1ea` (origin/main HEAD)
**Spec:** `specs/FULL_REPO_RECONCILIATION_EXECUTION_SPEC.md` (PR-1 of this audit)
**Companion docs:**
- `docs/FULL_REPO_CANONICAL_SYSTEM_MAP_2026-04-26.md`
- `docs/PLAIN_ENGLISH_SYSTEM_OVERVIEW.md`
- `docs/FULL_REPO_ARCHITECTURE_MAP_2026-04-26.md`
- `docs/FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md`
- `docs/FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md`

**Inventory CSVs (PR-3):**
- `artifacts/inventory/full_repo_file_inventory_2026-04-26.csv` (42,257 rows)
- `artifacts/inventory/full_repo_git_history_index_2026-04-26.csv` (2,006 commits + 11 PRs)
- `artifacts/inventory/full_repo_doc_status_matrix_2026-04-26.csv` (19,879 rows)
- `artifacts/inventory/full_repo_pipeline_matrix_2026-04-26.csv` (1,053 rows)

---

## 1. Why this audit exists — banned failure mode

PR #680 (manga pipeline audit, merged 2026-04-26 00:43 UTC) used **narrow filename
patterns** (`docs/MANGA_*.md`) and missed five load-bearing strategic docs. PR #682
(catalog reconciliation), PR #684 (docx→md migration), PR #685 (coordination
backfill), and PR #686 (audiobook docs rename) all stem from that miss.

**This audit bans narrow-pattern enumeration as the audit method.** Every classifier
here uses `git ls-files` + `git log --all` + `git grep` for full coverage.

### Strategic-miss test — PASSED

All 5 PR #680 misses appear in `full_repo_doc_status_matrix_2026-04-26.csv`:

| Path | Lines | classification | subsystem |
|------|------:|----------------|-----------|
| `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` | 303 | canonical | manga_pipeline |
| `docs/CJK_CATALOG_PLAN.md` | 300 | canonical | manga_pipeline |
| `docs/GENRE_PORTFOLIO_PLAN.md` | 563 | canonical | manga_pipeline |
| `docs/US_CATALOG_PLAN.md` | 279 | canonical | manga_pipeline |
| `docs/MANGA_MODE_STRATEGY.md` (.docx + .md) | 342 | canonical | manga_pipeline |

## 2. Repo scale snapshot

42,257 tracked files across 60+ top-level areas. Top concentrations:

| Area | Files | % | Notes |
|------|------:|--:|-------|
| `atoms/` | 17,090 | 40.5% | Pearl Prime + manga registry entries |
| `brand-wizard-app/` | 7,872 | 18.6% | **88.7% (6,984) is committed `node_modules/`** — see §6 deletion |
| `artifacts/` | 4,679 | 11.1% | generated outputs + coordination + research |
| `config/` | 3,650 | 8.6% | brand registry, locale registry, gates, etc. |
| `SOURCE_OF_TRUTH/` | 3,177 | 7.5% | teacher banks, story atoms |
| `template_expand2/` | 1,012 | 2.4% | teacher template fixtures |
| `image_bank/` | 841 | 2.0% | brand portrait sets (~9% of target) |
| `teachers/` | 590 | 1.4% | per-teacher pages/profiles |
| `pearl_news/` | 503 | 1.2% | editorial pipeline |
| `scripts/` | 455 | 1.1% | runnable entry points |
| `docs/` | 301 | 0.7% | canonical authority docs |
| (49 other areas) | 2,087 | 4.9% | |

87% of all 2,006 captured commits are from April 2026 — recent rapid iteration.
Top authors: Nihala (Ma'at) 1,399 (70%); Ahjan108 576 (29%); github-actions[bot] 29.

## 3. Subsystem health scorecard

Synthesized from Phase 3 reports.

| Subsystem | Pipelines (live) | Canonical docs | Orphans | Last touched | Verdict |
|-----------|------------------|----------------|---------|--------------|---------|
| Pearl_Prime | 1 (multilingual catalog) | 6 | low | 2026-04-25 | **strong** but `pearl_prime/` package is stub; real impl in `scripts/pearl_prime_multilingual/` |
| Pearl_News | 1 (daily editorial) | 4 | 24 (likely false-positives) | 2026-04-23 | **medium** — `pearl_news copy/` 7 real dead; orphan FP-rate needs runtime check |
| Pearl_Manga | 3 (visual / lettering / webtoon) | 12 | 45 (in `phoenix_v4/manga/`) | 2026-04-25 | **strong but bloated** — biggest single dead-code cluster |
| Pearl_Brand | 2 (Wizard + Admin weekly) | 5 | low (in code) | 2026-04-26 | **fractured canon** — brand counts: 24/28/36/37/312 mismatch across configs |
| Pearl_Marketing | 0 | 2 | n/a | 2026-04-01 (cold) | **weak** — no `platform_marketing/` exists; freebies stale |
| Pearl_DevOps | 11 cataloged of 72 CI workflows | 4 | n/a | 2026-04-26 | **strong governance**, but **subsystem absent from `SUBSYSTEM_AUTHORITY_MAP.tsv`** |
| Pearl_LegalBiz | n/a | 0 | n/a | n/a | **light by design** — no contracts in repo (correct) |
| Audiobook | 1 (MVP) | 4 | low | 2026-04-26 | **partial** — 5-locale rollout pending; ko_KR hold |
| Podcast | 0 (proposed) | 1 (research) | n/a | n/a | **missing impl** — research only |

## 4. Cross-subsystem conflicts surfaced

| # | Conflict | Resolution proposed |
|---|----------|---------------------|
| C-1 | Brand-count canon: `config/brand_registry.yaml` (28) vs `config/brand_management/global_brand_registry.yaml` (312) vs PR #682 spec ("37 brands") | Pearl_Brand session; canonicalize on one source; reconcile spec |
| C-2 | `docs/MANGA_MODE_STRATEGY.docx` (legacy) + `.md` (PR #684 migration) both committed | PR D1 candidate: archive `.docx` |
| C-3 | `pearl_news/` (live) + `pearl_news copy/` (PR #245 accidental restore, 7 dead .py files) | PR D1 candidate |
| C-4 | Triple-maintained brand-admin HTML: root `brand_admin.html`, `brand_admin_weekly_os.html`, `brand-wizard-app/public/brand_admin.html` | Pearl_Brand session; pick canonical |
| C-5 | Hand-cloned locale forks: `BrandWizard{,-ja,-tw,-zh}.jsx` + `main{,-ja,-tw,-zh}.jsx` despite `useTranslation.jsx` existing | Pearl_Brand i18n collapse PR |
| C-6 | 85 `specs/*.md` files all classified `unknown` despite being subsystem authority — classifier rule miss | Patch `classify_doc_status.py` rule (post-merge follow-up) |
| C-7 | 116 of 154 canonicals tagged `repo_coordination` — overweight catch-all | Sub-bucket into `audiobook`, `video_pipeline`, `podcast_pipeline` etc. |
| C-8 | `dashboard` subsystem: missing from `SUBSYSTEM_AUTHORITY_MAP.tsv` AND no pipeline entry point exists | Pearl_Architect routing decision |
| C-9 | Pearl_DevOps subsystem identity unresolved (absent from authority map) | Pearl_Architect routing decision |
| C-10 | `MANGA_MODE_STRATEGY.docx` and `.md` both classified canonical | Mark `.docx` superseded |

## 5. Governance state

✅ **Working**:
- `.github/workflows/llm-policy-enforcement.yml` — banned paid LLM API enforcement live
- `scripts/git/push_guard.py` — push-time integrity check
- `scripts/ci/preflight_push.sh` — pre-push validation
- `scripts/ci/audit_llm_callers.py` — LLM tier policy audit
- `docs/BRANCH_PROTECTION_REQUIREMENTS.md` — exact 4-check requirement
- `validate_required_checks_match.py` — job-name match enforcement

⚠️ **Partial**:
- Mass-delete check (>50 file rule) exists in `scripts/ci/pr_governance_review.py:117`
  but is **manual-only** via `pre_merge_check.sh`. CLAUDE.md describes auto-PR-comment
  governance; that wiring is the missing piece.
- `pr_governance_review.py` exists but no GitHub workflow invokes it on PR open

❌ **Missing or stale**:
- `docs/PEARL_PM_STATE.md` last_verified 2026-04-10 (16 days stale); 5 active projects
  in `ACTIVE_PROJECTS.tsv` but only 1 referenced in PEARL_PM_STATE.md
- `docs/DOCS_INDEX.md` referenced in spec but state unverified; check
- 7 schema-malformed rows confirmed in `ACTIVE_WORKSTREAMS.tsv`:
  - 4×14-field: `ws_spine_pipeline_wiring`, `ws_pr_triage_20260412`, `ws_manga_weekly_rollout`, `ws_cjk_atom_translation_qwen25`
  - 3×16-field: `ws_source_bank_repair`, `ws_branch_cleanup`, `ws_tts_provider_hardening`

## 6. Dead code clusters (high-confidence deletion candidates)

Detail in `docs/FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md`. Summary:

| Cluster | Count | Verdict |
|---------|------:|---------|
| `brand-wizard-app/node_modules/` (committed) | 6,984 | **PR D1**: gitignore + remove |
| `phoenix_v4/manga/` orphan subset | 45 | needs runtime check; biggest dead-code cluster |
| `phoenix_v4/` (other) orphan subset | 108 | needs runtime check |
| `pearl_news copy/` (PR #245 restore) | 7 | **PR D1**: clearly safe |
| `pearl_news/pipeline/` (cross-package imports) | 24 | likely false-positive; needs runtime grep |
| `del_files/`, `del_location_plan/`, `del_intake_planner/`, `del_exta_stories/`, `deli/`, `delf/` | 8+ | **PR D1**: deletion artifacts |
| `files-4/` | 1+ | **PR D1**: duplicate validation |
| `dashboard/` (no entry point) | n/a | needs Pearl_Architect routing |

## 7. Implementation gaps

Detail in `docs/FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md`. Summary of 28
inferred requirements:

- 21 implemented (75%)
- 5 partial (18%) — teacher visual signature; teacher video binding; conversion tracking; Pearl News; audiobook 5-locale
- 1 missing (4%) — podcast publishing
- 1 unknown (4%) — podcast system status

Priority remediation order:
1. Brand-count canon reconciliation (Pearl_Brand)
2. PEARL_PM_STATE.md refresh (Pearl_PM)
3. ACTIVE_WORKSTREAMS.tsv schema fixes (Pearl_PM)
4. Wire pr_governance_review.py into CI (Pearl_DevOps)
5. Podcast publishing impl (Pearl_DevOps + Pearl_News)

## 8. Open questions

| OQ | Question | Status |
|----|----------|--------|
| OQ-A | Does a "28 requirements" transcript exist somewhere not found by the audit? | unresolved; Subagent E searched docs/, specs/, artifacts/, old_chat_specs/, git history with no hit |
| OQ-B | Are the 153 phoenix_v4/ orphans truly dead, or imported via dynamic loading (importlib, getattr)? | needs runtime check |
| OQ-C | dashboard subsystem missing from authority map; pipeline_matrix shows no entry point | unresolved; Pearl_Architect routing |
| OQ-D | Pearl_DevOps subsystem absent from authority map | unresolved; Pearl_Architect routing |
| OQ-E | brand-count canon: 24 vs 28 vs 36 vs 37 vs 312 — which is canonical? | unresolved; Pearl_Brand session |
| OQ-F | 7 schema-malformed rows in ACTIVE_WORKSTREAMS.tsv; impact on automated coordination? | known; Pearl_PM cleanup pending |
| OQ-G | line_count=0 anomaly for `MANGA_MODE_STRATEGY.md` in CSV but file is 342 lines on disk — Subagent C classifier bug | known; corrects in next CSV regeneration |
| OQ-H | 85 `specs/*.md` classified `unknown` — classifier rule miss | known; patch in classify_doc_status.py post-merge |

## 9. Recommended PR sequence after this audit lands

(See `FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md` and `FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md` for full lists.)

| PR | Type | Owner | Scope |
|----|------|-------|-------|
| D1 | deletion | Pearl_GitHub | gitignore + remove `brand-wizard-app/node_modules/` (6,984 files); pearl_news copy/ (7); del_*/ clusters |
| D2 | deletion | Pearl_GitHub | dashboard/ archive OR clarify routing |
| D3 | deletion | Pearl_GitHub | phoenix_v4/ orphans (gated on runtime FP check) |
| GAP-1 | remediation | Pearl_PM | PEARL_PM_STATE.md refresh + 7 schema fixes |
| GAP-2 | remediation | Pearl_Brand | brand-count canon reconciliation |
| GAP-3 | remediation | Pearl_DevOps | wire pr_governance_review.py to GitHub workflow |
| GAP-4 | remediation | Pearl_DevOps + Pearl_News | podcast publishing impl spec + skeleton |
| DOC-1 | doc fix | Pearl_Architect | classifier rule patch (specs/*.md, repo_coordination split) |

## 10. Subagent provenance (Phase 1 + Phase 3)

Phase 1 subagents (parallel, ~30-90 min each): Subagent A inventory, B git history,
C doc canonicality, D pipeline + code, E business reqs.

Phase 3 reviewers (consolidated 9 → 3 for context efficiency): code+pipelines,
docs+governance, brand+content. Per-reviewer reports preserved in PR-3 artifacts.

All work performed under Tier 1 (Claude Code, operator-present). Zero paid LLM API
calls per `.github/workflows/llm-policy-enforcement.yml`.
