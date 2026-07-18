# Full Repo Canonical System Map — 2026-04-26

**Purpose:** the single answer to "which doc is canonical for X?"

This file is the routing table for every subsystem, derived from the
`full_repo_doc_status_matrix_2026-04-26.csv` (where `classification=canonical`)
cross-referenced with `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`.

When a doc claims authority on a topic, look here first. If conflicts surface,
consult the conflict-resolution table at the bottom.

---

## 1. Subsystem → canonical doc mapping

### 1.1 Core Pipeline

| Topic | Canonical | Status |
|-------|-----------|--------|
| Architecture authority | `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md` | active |
| Writer overlay | `specs/PHOENIX_V4_5_WRITER_SPEC.md` | active |
| System overview | `docs/SYSTEMS_V4.md` | active |

### 1.2 Pearl Prime (books)

| Topic | Canonical | Status |
|-------|-----------|--------|
| Whole workflow hardening | `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md` | active |
| Bestseller writing overlay | `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` | active |
| Book system canonical | `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md` | active |
| Coverage + gap analysis | `docs/PEARL_PRIME_COVERAGE_GAP_ANALYSIS_2026-04-26.md` | open in PR #683 |
| Move 4 framework | `docs/PEARL_ARCHITECT_STATE.md` BG-PR-09 entry | active |

### 1.3 Pearl News

| Topic | Canonical | Status |
|-------|-----------|--------|
| Writer spec | `docs/PEARL_NEWS_WRITER_SPEC.md` | active |
| Qwen deep-research engine | `docs/research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md` | active |
| Daily render | `pearl_news/config/`, `pearl_news/prompts/` | active |

### 1.4 Manga Pipeline

| Topic | Canonical | Status |
|-------|-----------|--------|
| Pipeline summary | `specs/AI_MANGA_PIPELINE_SUMMARY.md` | active |
| Implementation outline | `docs/MANGA_IMPLEMENTATION_OUTLINE.md` | active |
| Catalog reconciliation | `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` | active (PR #682) |
| Strategic genre portfolio | `docs/GENRE_PORTFOLIO_PLAN.md` | active |
| CJK locale catalog | `docs/CJK_CATALOG_PLAN.md` | active |
| US locale catalog | `docs/US_CATALOG_PLAN.md` | active |
| Full catalog plan | `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` | RETIRED — to be auto-generated per spec D-17 |
| Mode strategy (business) | `docs/MANGA_MODE_STRATEGY.md` | active (PR #684 migration) |
| Mode strategy (legacy docx) | `docs/MANGA_MODE_STRATEGY.docx` | superseded by `.md`; schedule for archive |
| Phase 1 audit (don't trust as enumeration) | `docs/MANGA_PIPELINE_AUDIT_2026-04-26.md` | superseded for repo-wide enumeration; manga subset still valid |
| Series portfolio research | `docs/MANGA_SERIES_PORTFOLIO_RESEARCH.md` | active |

### 1.5 Brand (Wizard + Admin)

| Topic | Canonical | Status |
|-------|-----------|--------|
| Brand Admin canonical package | `BRAND_ADMIN_CANONICAL_PACKAGE.md` (root) | active |
| Old chat & home promotion spec | `docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md` | active |
| Brand registry (one-source) | **CONFLICTED** — `config/brand_registry.yaml` (28) vs `config/brand_management/global_brand_registry.yaml` (312) | **needs Pearl_Brand reconciliation** |
| Brand author assignments | `config/brand_author_assignments.yaml` | active |

### 1.6 Teacher Mode

| Topic | Canonical | Status |
|-------|-----------|--------|
| System overview | `docs/SYSTEMS_V4.md` | active |
| Writer spec | `specs/PHOENIX_V4_5_WRITER_SPEC.md` | active |
| Teacher banks | `SOURCE_OF_TRUTH/teacher_banks/` | active |
| Pen-name profiles | `config/authoring/pen_name_teacher_profiles.yaml` | active |

### 1.7 Translation / Localization

| Topic | Canonical | Status |
|-------|-----------|--------|
| Quality contracts README | `config/localization/quality_contracts/README.md` | active |
| Locale registry | `config/localization/locale_registry.yaml` | active |
| Quality contracts dir | `config/localization/quality_contracts/` | active |

### 1.8 Video Pipeline

| Topic | Canonical | Status |
|-------|-----------|--------|
| Video config + scripts README | `scripts/video/README.md` + `config/video/` | active |
| Render params | `config/video/render_params.yaml` | active |
| Audiobook style | `config/video/audiobook_style.yaml` | active |
| Cadence config | `config/release_velocity/video_cadence.yaml` | active |

### 1.9 EI v2 (quality module)

| Topic | Canonical | Status |
|-------|-----------|--------|
| Module location | `phoenix_v4/quality/ei_v2/` | active |
| Config | `config/quality/ei_v2_config.yaml` | active |

### 1.10 Trend Feeds

| Topic | Canonical | Status |
|-------|-----------|--------|
| Strategy doc | `docs/TREND_FEED_INTEGRATION_STRATEGY.md` | active |
| Budget guard | `scripts/feeds/budget_guard.py` | active |

### 1.11 Recommendations

| Topic | Canonical | Status |
|-------|-----------|--------|
| Scoring weights | `config/recommender/scoring_weights.yaml` | active |
| Hard gates | `config/recommender/hard_gates.yaml` | backlog |

### 1.12 ITE (manga ingestion-and-export)

| Topic | Canonical | Status |
|-------|-----------|--------|
| Pipeline | `phoenix_v4/manga/ite_pipeline.py` | active |
| Gate registry | `config/manga/gate_registry.yaml` | active |

### 1.13 Integrations

| Topic | Canonical | Status |
|-------|-----------|--------|
| Credentials registry | `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` | active |
| Pearl_Int skill | `skills/pearl-int/SKILL.md` | active |
| Env registry | `scripts/ci/integration_env_registry.py` | active |

### 1.14 Repo Coordination

| Topic | Canonical | Status |
|-------|-----------|--------|
| Active projects | `artifacts/coordination/ACTIVE_PROJECTS.tsv` | active (5 rows) |
| Active workstreams | `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` | active (~76 rows; 7 schema-malformed) |
| Subsystem authority map | `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` | active (14 rows) |
| Architecture routing | `docs/PEARL_ARCHITECT_STATE.md` | active (last verified 2026-04-26) |
| Project routing | `docs/PEARL_PM_STATE.md` | **stale** (last verified 2026-04-10) |
| Session unity | `docs/SESSION_UNITY_PROTOCOL.md` | active |
| Pearl_GitHub | `skills/pearl-github/SKILL.md` + `references/` | active |
| GitHub governance | `docs/GITHUB_GOVERNANCE.md` + `BRANCH_PROTECTION_REQUIREMENTS.md` | active |
| Agent file persistence | `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md` | active |

### 1.15 Subsystems WITHOUT canonical anchor (gaps)

| Subsystem | Gap | Recommended action |
|-----------|-----|---------------------|
| Pearl_DevOps | Absent from `SUBSYSTEM_AUTHORITY_MAP.tsv`; CI is owned but unattributed | Pearl_Architect: add `pearl_devops` row pointing at `.github/workflows/` + `scripts/ci/` |
| Dashboard | Authority map lists no entry; pipeline matrix has no entry point | Pearl_Architect: clarify routing OR archive |
| Audiobook | No `audiobook_pipeline` subsystem in authority map; has 4 canonical docs (per AUDIOBOOK_ rename PR #686) | Pearl_Architect: add `audiobook_pipeline` row |
| Podcast | No `podcast_pipeline` subsystem in authority map; only research dir exists | Pearl_Architect: add row OR mark as proposed |
| Marketing | No `marketing` subsystem in authority map | Pearl_Architect: clarify (folded under brand_admin?) |
| Pearl_LegalBiz | No subsystem in authority map (intentional?) | Pearl_Architect: confirm intentionally external |
| Pearl_Marketing | No subsystem in authority map | Pearl_Architect: ditto |

## 2. Cross-doc supersession chain

When a doc references a successor:

| Older | Successor | Why |
|-------|-----------|-----|
| `docs/MANGA_MODE_STRATEGY.docx` | `docs/MANGA_MODE_STRATEGY.md` | PR #684 migration; docx scheduled for archive |
| `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` (hand-edited) | auto-generated per `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` D-17 | hand-edited version retired |
| `docs/MANGA_PIPELINE_AUDIT_2026-04-26.md` (PR #680, narrow-pattern) | `docs/FULL_REPO_SYSTEM_AUDIT_2026-04-26.md` (this audit) | full enumeration replaces narrow pattern |
| `ws_bestseller_pipeline_default_path_a_20260425` (cancelled) | `ws_bestseller_pipeline_default_path_b_20260425` | per BG-PR-09 update |

## 3. Conflict resolution decisions

For each cross-subsystem conflict surfaced in `FULL_REPO_SYSTEM_AUDIT_2026-04-26.md` §4:

### C-1 — Brand count canon (24 vs 28 vs 36 vs 37 vs 312)

**Status:** unresolved; routes to Pearl_Brand reconciliation session
**Decision criteria:**
- Which file is loaded by `scripts/build_weekly_brand_package.py`?
- Which count does PR #682 spec rely on (37)?
- Are 312 entries (24 archetypes × 13 lanes) a derived/expanded view or a separate registry?
**Provisional canon:** `config/brand_management/global_brand_registry.yaml` (312) is the *expanded* view; `config/brand_registry.yaml` (28) is the *seed*. PR #682's 37 figure is aspirational. Pearl_Brand to ratify.

### C-2, C-3, C-4 — file conflicts

Routed to `FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md` PR D1.

### C-5 — Locale forks JSX

Routed to Pearl_Brand i18n collapse PR (in `FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md`).

### C-6, C-7 — classifier rule misses

Patch the audit script (`scripts/audit/classify_doc_status.py`) post-merge: add specs/ → canonical fast-path; split repo_coordination into sub-buckets.

### C-8, C-9 — missing subsystems

Routed to Pearl_Architect routing decisions in `docs/PEARL_ARCHITECT_STATE.md` (separate session).

### C-10 — MANGA_MODE_STRATEGY duplication

`.docx` marked superseded (deletion plan PR D1).

## 4. How to use this map

1. **Routing a task:** look up the subsystem; the canonical doc is the authority.
2. **Discovering a new doc:** check whether it conflicts with anything in §1; if yes,
   surface as a new C-N entry and route to Pearl_Architect.
3. **Authoring a new spec:** confirm no canonical exists for the topic; if one exists,
   amend rather than duplicate.
4. **Auditing canonicality drift:** re-run `scripts/audit/classify_doc_status.py`;
   compare against this map; report changes in §3.
