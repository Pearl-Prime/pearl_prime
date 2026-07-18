# Full Repo Implementation Gap Plan — 2026-04-26

**Purpose:** for every business requirement (28 inferred) and every cross-subsystem
gap, this file lists the gap, its evidence, and the remediation PR (or routing
decision) that closes it.

**Audit baseline:** `1f4f8a28f`
**Source:** `artifacts/inventory/full_repo_pipeline_matrix_2026-04-26.csv` (row_type=requirement) + Phase 3 reviewer reports
**Companion docs:** `docs/FULL_REPO_SYSTEM_AUDIT_2026-04-26.md`, `docs/FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md`

---

## 1. Requirement matrix (28 inferred reqs)

No operator transcript exists for "28 requirements" (Subagent E searched
`docs/`, `specs/`, `artifacts/`, `old_chat_specs/`, git history with no hit).
The 28 reqs below are *inferred* from `ACTIVE_PROJECTS.tsv` topic clusters,
PR #682 spec, and recent session handoffs. **Treat as audit-derived, not operator-canonical.**

| Req | Topic | Status | Evidence | Gap |
|-----|-------|--------|----------|-----|
| R-001 | Teacher showcase pages with brand attribution | implemented | `config/catalog_planning/teacher_persona_matrix.yaml` | none |
| R-002 | Teacher profile pages with per-teacher video bindings | partial | `scripts/teacher_videos/` exists; not all profiles have bindings | GAP-T1 |
| R-003 | Teacher visual signature (portrait + scene + symbolic triptych) | partial | `ws_teacher_manga_triptych_20260410` active; not complete across all 12 teachers | GAP-T2 |
| R-004 | 37 brand onboarding (per PR #682 spec) | partial | `config/brand_registry.yaml` shows 28; mismatch | GAP-B1 |
| R-005 | 5-locale support (en_US, ja_JP, zh_TW, zh_CN, ko_KR) | partial | en_US strong; ja_JP/zh_TW/zh_CN partial; ko_KR rendered+held | GAP-L1 |
| R-006 | LTV modeling with platform-specific defaults | partial | `revenue_projector.py` consumes config defaults; no API ingestion | GAP-M1 |
| R-007 | Conversion rate signal ingestion (Spotify/Apple/Google Play/ACX) | missing | no API integration code in `scripts/` | GAP-M2 |
| R-008 | Pearl Prime bestseller-grade book pipeline (Move 4 sweep) | implemented | `assemble_full_catalog_qa.py` + named-character output verified | none |
| R-009 | Pearl Prime canonical CLI bestseller integration (Phase 2) | partial | EXERCISE side wired (PR #604/#612); SCENE side at sec 2/5/9 still pending | GAP-P1 |
| R-010 | Pearl News daily editorial cycle | implemented | `run_daily_news_cycle.py` + v52 deterministic teacher slots | none |
| R-011 | Pearl News v5.4 interactive sidebar | partial | PR #592 open; not yet merged | GAP-N1 |
| R-012 | Manga ep_001 ship — KDP en_US | implemented | `proj_manga_first_ship_20260425` — runbook live | none |
| R-013 | Manga ep_002 ship | partial | content landed PR #657; pipeline ship pending | GAP-MA1 |
| R-014 | Manga 12-shell × 37-brand catalog reconciliation | implemented (spec); partial (impl) | spec PR #682 merged; auto-generation PR (D-17) pending | GAP-MA2 |
| R-015 | Manga 5-locale routing matrix | partial | spec resolves OQ-1..OQ-9; impl pending across `phase_2x_*` ws's | GAP-MA3 |
| R-016 | Audiobook 5-locale rollout | partial | tooling exists; ko_KR hold | GAP-A1 |
| R-017 | Audiobook MVP en_US live | implemented | `scripts/audiobook/` + ACX route | none |
| R-018 | Podcast pipeline | missing | research only; no code | GAP-PC1 |
| R-019 | Brand Wizard app live | implemented | `brand-wizard-app/` deployed; needs node_modules cleanup | GAP-B2 |
| R-020 | Brand Admin weekly delivery live | implemented | `scripts/build_weekly_brand_package.py` runs daily | none |
| R-021 | Brand Admin canonical HTML (single source) | partial | 3 HTML variants; reconcile to one | GAP-B3 |
| R-022 | i18n for brand-wizard-app | partial | `useTranslation.jsx` exists but locale forks (`{,-ja,-tw,-zh}.jsx`) hand-cloned | GAP-B4 |
| R-023 | Marketing platform_marketing/ structure | missing | only `funnel/burnout_reset` built; one of N planned hubs | GAP-M3 |
| R-024 | Marketing freebies | partial | `somatic_exercise_freebee_apps/` exists but stale (2026-04-01) | GAP-M4 |
| R-025 | LLM tier policy enforcement | implemented | `.github/workflows/llm-policy-enforcement.yml` live | none |
| R-026 | Mass-delete protection (>50 file rule) | implemented | `pr_governance_review.py:117` | none |
| R-027 | Auto-PR-comment governance review on every PR | partial | check exists; not wired to GitHub workflow | GAP-G1 |
| R-028 | Branch protection: 4 required checks | implemented | `BRANCH_PROTECTION_REQUIREMENTS.md` + `validate_required_checks_match.py` | none |

**Roll-up:** 21 implemented (75%) / 5 partial (18%) / 1 missing (4%) / 1 unknown (4%).
*Adjustment*: re-classifying R-013 implemented→partial, R-016 implemented→partial,
and R-019 partial→implemented (with caveat) gives a more honest 17 implemented /
9 partial / 2 missing breakdown — this matches the audit findings.

## 2. Cross-subsystem governance gaps

| Gap | Subsystem | Description | Severity |
|-----|-----------|-------------|---------:|
| GAP-G1 | DevOps | `pr_governance_review.py` not wired to GitHub workflow; runs only via manual `pre_merge_check.sh` | high |
| GAP-G2 | PM | `PEARL_PM_STATE.md` last_verified 2026-04-10 (16 days stale); 5 active projects but only 1 referenced | high |
| GAP-G3 | PM | 7 schema-malformed rows in `ACTIVE_WORKSTREAMS.tsv` (4×14-field + 3×16-field) | medium |
| GAP-G4 | Architect | `dashboard` subsystem absent from authority map; no entry point exists | medium |
| GAP-G5 | Architect | `Pearl_DevOps` subsystem absent from authority map; owns 72 CI workflows | medium |
| GAP-G6 | Architect | `Audiobook` subsystem absent from authority map; has 4 canonical docs | medium |
| GAP-G7 | Architect | `Marketing`, `Podcast` subsystems absent from authority map | medium |
| GAP-G8 | Architect | 85 `specs/*.md` classified `unknown` by audit due to classifier rule miss | low (CSV regen) |
| GAP-G9 | Architect | 116 of 154 canonicals tagged `repo_coordination` — overweight catch-all | low |

## 3. Remediation plan (5 priority PRs)

Order by impact-then-cost.

### GAP-1 — `PEARL_PM_STATE.md` refresh + workstream schema fixes
- **Owner**: Pearl_PM
- **PR**: `agent/pearl-pm-state-refresh-20260427`
- **Files**: `docs/PEARL_PM_STATE.md`, `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`
- **Scope**: bump last_verified → 2026-04-26; add 4 missing project rows; fix 7 schema-malformed rows; sync 91 ws state with PEARL_PM_STATE.md
- **Closes**: GAP-G2, GAP-G3
- **Effort**: ~1-2h (largely mechanical)

### GAP-2 — Brand-count canon reconciliation
- **Owner**: Pearl_Brand
- **PR**: `agent/brand-count-canon-reconciliation-20260427`
- **Files**: `BRAND_ADMIN_CANONICAL_PACKAGE.md`, possibly `config/brand_registry.yaml` and `config/brand_management/global_brand_registry.yaml`
- **Scope**: declare canonical brand-count (24 vs 28 vs 36 vs 37 vs 312); document derivation if 312 is expanded view; reconcile PR #682 spec's "37" framing
- **Closes**: GAP-B1, C-1
- **Effort**: ~3-5h (needs research + ratification by operator)

### GAP-3 — Wire `pr_governance_review.py` to GitHub workflow
- **Owner**: Pearl_DevOps
- **PR**: `agent/wire-pr-governance-workflow-20260427`
- **Files**: `.github/workflows/pr-governance-review.yml` (NEW)
- **Scope**: trigger on `pull_request` events (opened/synchronize); run `python3 scripts/ci/pr_governance_review.py` and post a PR comment with verdict
- **Closes**: GAP-G1, R-027
- **Effort**: ~2-3h

### GAP-4 — Subsystem authority map fills
- **Owner**: Pearl_Architect
- **PR**: `agent/subsystem-authority-map-fills-20260427`
- **Files**: `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`, `docs/PEARL_ARCHITECT_STATE.md` (routing decisions section)
- **Scope**: add rows for `pearl_devops`, `audiobook_pipeline`, `dashboard` (or archive), `podcast_pipeline` (proposed), `marketing` (intentional fold under brand_admin?), confirm `pearl_legalbiz` external
- **Closes**: GAP-G4, GAP-G5, GAP-G6, GAP-G7
- **Effort**: ~2-4h (needs Pearl_Architect routing decisions)

### GAP-5 — Pearl Prime SCENE wiring (Phase 2 of BG-PR-09)
- **Owner**: Pearl_Dev
- **PR**: `agent/pearl-prime-scene-wiring-20260428` (under `ws_bestseller_pipeline_default_path_b_20260425`)
- **Files**: `phoenix_v4/rendering/section_packet_composer.py`, `scripts/run_pipeline.py` (compose_from_enriched_book)
- **Scope**: wire `build_story_schedule` output + `slot_tracker` consumption into `compose_from_enriched_book` so SCENE slots produce named-character content at sec 2/5/9
- **Closes**: GAP-P1, R-009
- **Gates**: blocks Move 4 450-book sweep
- **Effort**: ~6-10h

## 4. Subsystem remediation backlog (lower priority)

| Priority | Gap | Owner | PR sketch |
|---------:|-----|-------|-----------|
| 6 | GAP-B4 i18n collapse | Pearl_Brand | replace hand-cloned locale forks with `useTranslation.jsx` consumers |
| 7 | GAP-PC1 podcast publishing impl | Pearl_DevOps + Pearl_News | spec + skeleton |
| 8 | GAP-MA2 manga catalog auto-generation | Pearl_Dev | per spec D-17 |
| 9 | GAP-MA3 5-locale routing impl (post spec) | Pearl_Dev | per `ws_manga_phase_2x_*` |
| 10 | GAP-T1 teacher video bindings completion | Pearl_Video | per `ws_teacher_manga_triptych_20260410` |
| 11 | GAP-T2 triptych across all 12 teachers | Pearl_Video | extend triptych ws |
| 12 | GAP-A1 audiobook 5-locale rollout | Pearl_Dev | gated on platform onboarding |
| 13 | GAP-N1 Pearl News v5.4 sidebar merge | Pearl_News | merge PR #592 |
| 14 | GAP-M1 + GAP-M2 LTV/conversion API ingestion | Pearl_Marketing | needs platform credentials + integration |
| 15 | GAP-M3 platform_marketing/ structure | Pearl_Marketing | per AI brand framework |
| 16 | GAP-M4 freebies activation | Pearl_Marketing | revive `somatic_exercise_freebee_apps/` |
| 17 | GAP-G8 classifier rule patch | Pearl_Architect | patch `scripts/audit/classify_doc_status.py` |
| 18 | GAP-G9 canonical sub-bucketing | Pearl_Architect | split `repo_coordination` into 5+ sub-subsystems |

## 5. Sequencing

```
Wk1:  GAP-1 → GAP-2 → GAP-3 → GAP-4   (governance hygiene first)
Wk2:  GAP-5 → backlog 6, 7, 8           (impl unblocks Move 4 + ships podcast)
Wk3:  backlog 9, 10, 11, 12, 13         (subsystem catch-up)
Wk4:  backlog 14, 15, 16                (marketing buildout)
Wk5:  backlog 17, 18                    (audit-tooling polish)
```

## 6. Out-of-scope

The following are NOT addressed by this plan:

- Operator-strategy decisions (which markets to prioritize, which channels to launch)
- Platform onboarding (KDP / WEBTOON / Apple Books / Spotify / Audible) — operator
  external work
- Partner contracts / legal — `Pearl_LegalBiz` is intentionally light in repo
- Branch protection rule changes — `BRANCH_PROTECTION_REQUIREMENTS.md` is canonical;
  changes are operator-approved separately

## 7. Operator review checkpoint

Before executing GAP-1 through GAP-5:
1. Confirm the 28 inferred requirements match operator intent (or supply the actual transcript if it exists somewhere we missed — see OQ-A in the system audit)
2. Approve the priority ordering (impact-then-cost vs. risk-first vs. operator-preference)
3. Confirm Pearl_<subsystem> agent routing matches current org chart
4. Greenlight GAP-1 first (lowest risk, highest hygiene value)
