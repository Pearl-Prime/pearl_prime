# System Drift Audit — Full Report (Phoenix Omega)

**PROJECT_ID:** PRJ-SYSTEM-DRIFT-AUDIT-V1  
**Subsystem:** pearl_architect coordination (cross-cutting verification)  
**Audit date:** 2026-05-10  
**Baseline:** `origin/main` @ `515de6cb5e775595e3f32a64cd3dc1a5f36d8798`  
**Authority read:** `docs/SESSION_UNITY_PROTOCOL.md` (template + minimum read set); `CLAUDE.md` (Tier policy, preflight); `docs/DOCS_INDEX.md` (navigation, first ~120 lines); `artifacts/coordination/ACTIVE_PROJECTS.tsv`; `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (partial grep + targeted rows); `docs/PEARL_ARCHITECT_STATE.md` (targeted sections + full `###` cap inventory via grep).

**Alignment score (method):** Weighted rubric documented in §0 — **75%** overall.

**Drift inventory (session):** critical **0** | high **3** | medium **9** | low **6** | total **18**

---

## 0. Alignment rubric (how 75% was derived)

| Pillar | Weight | Evidence basis | Score |
|--------|--------|----------------|-------|
| Cap ↔ spec linkage | 25% | Most 2026 caps cite `docs/specs/*` or governing docs; a few older caps only in architect narrative | 85% |
| Spec ↔ implementation | 35% | Strong on registry + recent PR waves; partial on multi-phase gates (overlay ITEM-2; CI spec banner vs merged code) | 70% |
| Anti-drift / policy | 25% | `audit_llm_callers` clean; Path X 37; music registry separation; RunComfy cap in IMG spec; stale marketing GTM counts | 78% |
| Coordination truth | 15% | `ACTIVE_WORKSTREAMS` overlay ws `proposed` vs code; spec `main` anchors stale | 65% |

**Weighted:** 0.25×85 + 0.35×70 + 0.25×78 + 0.15×65 ≈ **75%**.

---

## 1. Methodology

### 1.1 What was read (Phase 1 foundation)

**Executed in full or substantial part:**

| Area | Scope | Notes |
|------|--------|------|
| `marketing_deep_research/` | All `*.md` | **2 files:** `README.md`, `deep-research-report.md` |
| `docs/MARKETING_*.md` glob | All matches | `docs/specs/MARKETING_VOLUME_SSOT_V1_SPEC.md`, `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md`, `docs/marketing_templates.md`, `docs/MARKETING_FREE_SOURCES.md` |
| `docs/CJK_CATALOG_PLAN.md` | First ~50 lines | Authority + genre-shell thesis |
| `docs/MANGA_GTM_PLAN.md` | First ~60 lines | **Drift:** still “24 brands” |
| `docs/specs/*.md` | **All 13** | Full paths enumerated Phase 3 |
| `docs/MANGA_LAYERED_PIPELINE_V2_SCOPE.md` | Exists at repo root | User asked `docs/specs/MANGA_LAYERED_PIPELINE_V2_SCOPE.md` — **actual:** `docs/MANGA_LAYERED_PIPELINE_V2_SCOPE.md` (path drift) |
| `docs/JAPAN_LINE_FREEBIE_FUNNEL_PLAN_2026-04-29.md` | Located | User path `docs/specs/JAPAN_*` — **actual:** `docs/JAPAN_LINE_FREEBIE_FUNNEL_PLAN_2026-04-29.md` |
| `artifacts/research/` | 2026-dated set via glob | **~45+** files (yaml/md); not every file body read end-to-end — **honesty gap:** spot-read + index for audit |
| `docs/PEARL_ARCHITECT_STATE.md` | Grep + line-targeted reads | Full cap list from `^###` grep; IMG + CI sections read `1336-1454` |

**Pearl Prime “specs” naming:** User listed `docs/specs/PEARL_PRIME_*_SPEC.md` — **no such glob**. Pearl Prime authority lives under `docs/PEARL_PRIME_*.md` and `specs/PHOENIX_*` per `docs/DOCS_INDEX.md:33-36`.

### 1.2 What was checked (Phases 3–7)

- **Existence:** key paths cited in caps/specs (`scripts/image_generation/runcomfy*.py`, `phoenix_v4/planning/book_structure_plan.py`, `config/music/music_brand_registry.yaml`, etc.).
- **Counts:** `canonical_brand_list` brands; `teacher_registry` keys; TSV line counts; `find specs` / `docs/specs` counts.
- **Policy:** `PYTHONPATH=. python3 scripts/ci/audit_llm_callers.py` → `violation_count: 0`.
- **Registry cross-walk:** sampled Path X id vs `music_brand_registry` anti-drift comments; weekly volumes brand key count **37**.
- **Coordination:** `ACTIVE_PROJECTS.tsv` full file read; `ACTIVE_WORKSTREAMS.tsv` grep for overlay + first page of rows.
- **Not executed exhaustively:** full pairwise YAML diff across 15 registries; every `specs/*.md` implementation line mapping; exhaustive orphan file enumeration across entire repo (see Appendix A honesty note).

---

## 2. Phase 1 — Foundation (operator intent — condensed)

### 2.1 `marketing_deep_research/deep-research-report.md` + README

**Intent captured:** establish research-backed positioning for Phoenix Omega product layers; README frames folder purpose.

### 2.2 Marketing + catalog plans

| Source | Binding intent |
|--------|----------------|
| `docs/CJK_CATALOG_PLAN.md` | CJK per-locale strategic canon; genre shell revenue thesis; ties to `docs/GENRE_PORTFOLIO_PLAN.md` |
| `docs/MANGA_GTM_PLAN.md` | Regional GTM tiers; **drift:** opening summary still **24 brands / 12 languages** (`docs/MANGA_GTM_PLAN.md:5`) vs Path X **37** brands |
| `docs/MARKETING_FREE_SOURCES.md` / templates / prompts | Operational marketing inputs (not fully line-audited this session) |

### 2.3 `docs/specs` operator packet (headlines)

| Spec | Intent |
|------|--------|
| `WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md` | 10-surface go-live program; Path X separation; Q1–Q5; phase table |
| `MARKETING_VOLUME_SSOT_V1_SPEC.md` | Brand×locale×surface SSOT contract; consumer join rules |
| `IMG_RENDER_DUAL_PATH_V1_SPEC.md` | Pearl Star + RunComfy; $10 soft cap; locale-first queue |
| `CI_BASELINE_RECOVERY_V1_SPEC.md` | Required-check recovery; phased ws; Q1–Q3 card |
| `MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` | 38+ music brands; wizard; survey; Path X read-only |
| `MUSIC_MODE_FREEBIE_FUNNEL_V1_SPEC.md` | Additive music freebies + funnel |
| `TEACHER_MANGA_30S_VIDEO_V1_SPEC.md` | 12 (or 13) vertical video deliverables |
| `PER_CHAPTER_OVERLAY_ENFORCEMENT_V1_SPEC.md` | Overlay rules + ITEM-2 allowlist removal |
| `IMAGE_ASSET_INVENTORY_V1_SPEC.md` | Inventory schema + `total_pngs` anchor |
| `DASHBOARD_ACTIVE_BRAND_PANEL_V1_SPEC.md` / `ACTIVE_BRAND_SSOT_V1_SPEC.md` / `ANGLE_REGISTRY_SSOT_V1_SPEC.md` | SSOT/dashboard/angle governance |
| `PEARL_CONDUCTOR_V2_TEMPLATE.md` | Orchestration / isolation PR discipline |

### 2.4 Research artifacts (2026)

Representative **binding themes:** individuation, webtoon compositing, license risk, RunComfy/community workflow audits, Japan LINE funnel research (`artifacts/research/japan_line_freebie_funnel_market_research_2026-04-29.md`, `japan_line_competitive_funnel_audit_2026-04-29.md`), dashboard failure diagnosis, anatomical correction audit.

**Gap:** Not every 2026 research file read verbatim — risk of uncaptured intent statements in unread files.

---

## 3. Phase 2 — Cap entry inventory

**Source:** `docs/PEARL_ARCHITECT_STATE.md` — `rg '^### [A-Z0-9]'` (41 headings; includes closed/superseded entries).

### 3.1 Cap table (primary IDs)

| cap_id | Declared status (from heading line / nearby prose) | Matching spec / authority doc | Spec? |
|--------|-----------------------------------------------------|----------------------------------|-------|
| BG-PR-08 | closed-not-needed | bestseller arc validation | partial (historical) |
| BG-PR-09 | completed-by-PR-669 / hybrid path | Path B / smoke narrative | narrative |
| BR-CANON-01 (+ Path X update) | ratified / Path X | `MANGA_CATALOG_RECONCILIATION_SPEC` / DOCS_INDEX | yes |
| DASH-01 / DASH-02 | active decisions | dashboard specs / ownership | partial |
| PHX-V4-ORPHAN-01 | closed | phoenix_v4 hygiene | narrative |
| SPEC-739-THRESHOLD-01 | ratified | `specs/PHOENIX_V4_5_WRITER_SPEC.md` | yes |
| SPEC-739-VALIDATOR-MULTISOURCE-01 | ratified | `specs/PHOENIX_V4_5_WRITER_SPEC.md` | yes |
| MASTER-CATALOG-01 | closed-not-needed | DOCS_INDEX routing | yes |
| PR-D-SPINE-01 | ratified | format registry + writer specs | yes |
| COVER-REGISTRY-01 | ratified | BRAND_ADMIN / registry | yes |
| AUTO-PLAN-SSOT-01 + AMENDMENT | approved | `config/format_selection/format_registry.yaml` + code | yes |
| TEMPLATE-UNIVERSAL-01 | approved | writer / overlay specs | yes |
| BESTSELLER-INJECTIONS-MANDATORY-01 | approved | `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` | yes |
| CATALOG-800-PER-BRAND-01 | approved | coordination + catalogs | partial |
| PEARL-EDITOR-UPSTREAM-01 | approved | authority flow docs | partial |
| EXERCISE-BANK-RESOLUTION-01 | approved | enrichment / writer spec | yes |
| QUOTE-ATOM-ROUTING-01 | approved | atom banks | partial |
| TEACHER-POOL-SEMANTICS-01 | approved | `specs/PHOENIX_V4_5_WRITER_SPEC.md` | yes |
| MUSIC-MODE-V1-01 | ratified | musician banks / overlay | partial |
| MANGA-LAYERED-PIPELINE-V2-01 | approved | `docs/MANGA_LAYERED_PIPELINE_V2_SCOPE.md` + research | yes |
| QI-FOUNDATION-CANONICAL-RECONCILIATION-01 | **proposed** | (pending reconciliation PR) | **no standalone spec** |
| WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 + AMENDMENTS | mixed: cap proposed; amendments describe merges | `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md` | yes |
| FEATURE-KNOB-CATALOG-VARIATION-V1-01 | ratified | catalog planner artifacts + PRs | partial |
| MUSIC-MODE-BRAND-INTEGRATION-V1-01 + AMENDMENT | active | `docs/specs/MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` | yes |
| MUSIC-MODE-FREEBIE-FUNNEL-V1-02 | proposed → active per coordination | `docs/specs/MUSIC_MODE_FREEBIE_FUNNEL_V1_SPEC.md` | yes |
| TEACHER-MANGA-30S-VIDEO-V1-01 + AMENDMENT | active | `docs/specs/TEACHER_MANGA_30S_VIDEO_V1_SPEC.md` | yes |
| PER-CHAPTER-OVERLAY-ENFORCEMENT-V1-01 | ratified | `docs/specs/PER_CHAPTER_OVERLAY_ENFORCEMENT_V1_SPEC.md` | yes |
| IMG-RENDER-DUAL-PATH-V1-01 | active | `docs/specs/IMG_RENDER_DUAL_PATH_V1_SPEC.md` | yes |
| CI-BASELINE-RECOVERY-V1-01 + AMENDMENT | **mixed** (see drift) | `docs/specs/CI_BASELINE_RECOVERY_V1_SPEC.md` | yes |

**Amendment count (WORLDWIDE):** **3** `#### WORLDWIDE-…AMENDMENT` headings found in grep (2026-05-09 twice + 2026-05-10 variants as recorded in architect file).

**Note:** User expected **IMG-RENDER-DUAL-PATH-V1-01 + AMENDMENT-2026-05-10** as separate cap line — **not present** as its own `####` cap heading; IMG anti-drift lives under the single `### IMG-RENDER…` block (`docs/PEARL_ARCHITECT_STATE.md:1336-1419`). **Gap vs operator checklist wording**, not necessarily a governance failure.

---

## 4. Phase 3 — Spec ↔ implementation matrix

### 4.1 `docs/specs/*.md` files (13) — implementation cross-check

| Spec path | Key implementation anchors | Exists on `main`? | Drift notes |
|-----------|-----------------------------|-------------------|-------------|
| `CI_BASELINE_RECOVERY_V1_SPEC.md` | `scripts/ci/verify_github_governance.py`; `scripts/ci/check_author_cover_art.py` | yes | Spec status text stale vs merges |
| `IMG_RENDER_DUAL_PATH_V1_SPEC.md` | `scripts/image_generation/runcomfy_dispatch.py`; `dispatchers/runcomfy_dispatcher.py`; workflows dir | yes | `runcomfy_monthly_spend.tsv` exists but minimal rows at audit |
| `IMAGE_ASSET_INVENTORY_V1_SPEC.md` | `artifacts/qa/image_asset_inventory_2026-05-09.tsv` | yes | Row count matches audit doc |
| `MARKETING_VOLUME_SSOT_V1_SPEC.md` | `config/marketing/weekly_volumes_per_brand.yaml` | yes | Documented schema deviations in YAML header comments `29-44` |
| `MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` | `config/music/music_brand_registry.yaml`; `brand-wizard-app/` | yes | |
| `MUSIC_MODE_FREEBIE_FUNNEL_V1_SPEC.md` | `funnel/`; `config/freebies/` | yes (per recent commits) | Not every funnel file opened |
| `TEACHER_MANGA_30S_VIDEO_V1_SPEC.md` | `config/video/render_params.yaml`; `format_specs.yaml` | yes | Operator Q-gates still in project row |
| `PER_CHAPTER_OVERLAY_ENFORCEMENT_V1_SPEC.md` | `phoenix_v4/quality/book_quality_gate.py`; `config/quality/refrain_allowlist.yaml` | yes | ITEM-2 incomplete |
| `WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md` | `scripts/brand/*`, `brand-wizard-app`, `ACTIVE_PROJECTS` | yes | Spec banner vs amendment content |
| `DASHBOARD_ACTIVE_BRAND_PANEL_V1_SPEC.md` | brand-admin / wizard HTML | partial check | |
| `ACTIVE_BRAND_SSOT_V1_SPEC.md` | active classifier commits **#972** lineage | partial | |
| `ANGLE_REGISTRY_SSOT_V1_SPEC.md` | angle registry + PR **#974** | partial | |
| `PEARL_CONDUCTOR_V2_TEMPLATE.md` | skills / orchestration | yes | Template, not executable |

### 4.2 Major code subsystems (governing spec mapping — summary)

| Subsystem dir | Primary governing specs (representative) |
|---------------|-------------------------------------------|
| `phoenix_v4/manga/` | `specs/AI_MANGA_PIPELINE_SUMMARY.md`; `docs/MANGA_IMPLEMENTATION_OUTLINE.md` |
| `phoenix_v4/quality/` | `specs/PHOENIX_V4_5_WRITER_SPEC.md`; `docs/specs/PER_CHAPTER_OVERLAY_ENFORCEMENT_V1_SPEC.md` |
| `phoenix_v4/planning/` | `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md`; AUTO-PLAN cap; `ANGLE_REGISTRY_SSOT_V1_SPEC.md` |
| `phoenix_v4/rendering/` | `specs/PHOENIX_V4_5_WRITER_SPEC.md`; `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` |
| `scripts/catalog/` | worldwide program; `FEATURE-KNOB` cap; `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` |
| `scripts/manga/` | manga implementation outline; reconciliation spec |
| `scripts/image_generation/` | `docs/specs/IMG_RENDER_DUAL_PATH_V1_SPEC.md`; `parallel_image_generation_plan_2026-05-09.md` |
| `scripts/brand/` | `ACTIVE_BRAND_SSOT_V1_SPEC.md`; worldwide program |
| `scripts/ci/` | `CI_BASELINE_RECOVERY_V1_SPEC.md`; `CLAUDE.md` |
| `scripts/video/` | `docs/VIDEO_PIPELINE_SPEC.md`; teacher 30s spec |
| `brand-wizard-app/` | music integration spec; worldwide surfaces |
| `funnel/` | freebie system specs; music freebie funnel spec |

**Silent addition check (sample):** New RunComfy modules trace to **IMG-RENDER-DUAL-PATH-V1-01** cap and spec — **no orphan** in this slice.

---

## 5. Phase 4 — Config registry consistency (pair / spot checks)

| Check | Result | Receipt |
|-------|--------|-----------|
| Path X brand count | **37** brands | `canonical_brand_list.yaml` parse |
| `weekly_volumes_per_brand.yaml` brand_targets keys | **37** | python parse session |
| Music registry ↔ Path X | Explicit “do not add music brands to canonical list” | `config/music/music_brand_registry.yaml:48-54` |
| `teacher_registry` vs Pearl Prime “12 teachers” framing | **13** teacher keys including `adi_da` | `config/teachers/teacher_registry.yaml` |
| Locales `en_US`, `ja_JP`, `zh_TW`, `zh_CN` | Present under `locale_registry` (hyphen keys `en-US` style in YAML) | `config/localization/locale_registry.yaml:20-79` |
| `qi_foundation` naming | Canonical list uses **`qi_foundation_cultivation`** | `config/manga/canonical_brand_list.yaml:288` |
| `refrain_allowlist` ITEM-2 | Phrase still present | `config/quality/refrain_allowlist.yaml:281` |

**Not fully verified:** cross-product of every `brand_id` across `brand_registry.yaml` × `canonical_brand_list.yaml` × `brand_author_assignments.yaml` × `character_brand_registry.yaml` × `brand_lora_plans.yaml` — **medium honesty gap**; recommend dedicated Pearl_Dev audit ws.

---

## 6. Phase 5 — Workstream / project completion

### 6.1 `ACTIVE_PROJECTS.tsv`

Read full file (11 project rows). **Examples:**

- **PRJ-DUAL-PATH-IMAGE-RENDER-V1** — `wired_dry_run` aligns with RunComfy client + batch scaffold narrative.
- **PRJ-CI-BASELINE-RECOVERY-V1** — `active` with Phase 1–2 merges noted — consistent with `git log`.
- **proj_teacher_manga_30s_video_v1_20260508** — `proposed` with explicit Q1–Q4 gates — consistent with spec §16 pattern.

### 6.2 Workstream evidence drift

| ws_id | TSV status | Evidence on `main` | Drift class |
|-------|------------|--------------------|-------------|
| `ws_per_chapter_overlay_enforcement_impl_20260508` | `proposed` | `overlay_rule` enforcement code in `book_quality_gate.py` | **high** — ws stale vs implementation |
| Worldwide `ws_worldwide_gl_s08_exec_dashboard_live_20260508` | likely queued | No executive dashboard completion in spec matrix | expected P1 gap |

**Full TSV:** 100+ rows — not every row reconciled to PR SHAs in this session.

---

## 7. Phase 6 — Anti-drift validation

| Rule | Verbatim source | Honored on `main`? | Severity if not |
|------|-----------------|-------------------|-----------------|
| Path X 37 brands | `canonical_brand_list` + caps | **yes** (count) | — |
| Music brands additive | `music_brand_registry.yaml` header | **yes** (structure + comments) | — |
| $10/mo RunComfy cap | `IMG_RENDER_DUAL_PATH_V1_SPEC.md` §4.B | **yes** in spec text; code present — **runtime enforcement** not fully proven in this read-only audit | **medium** (verification gap) |
| LLM Tier — no banned paid APIs | `CLAUDE.md` + workflow | **audit script 0 violations** | — |
| Teacher × brand bindings | `brand_lora_plans.yaml` / teacher specs | spot only | **medium** incomplete |
| Spec citations / phrase-density anchors | writer specs | not re-run line-by-line | **low** gap |
| `--admin` merges documented | governance docs | not audited per merge | **honesty gap** |

**Violations logged:**

1. **high — `rule_violation` / `inconsistency`:** CI spec claims cap-scoping “no remediation” while remediation merged — `docs/specs/CI_BASELINE_RECOVERY_V1_SPEC.md:10` vs `main` history.
2. **high — `inconsistency`:** Overlay enforcement ws `proposed` vs implemented gate code — `ACTIVE_WORKSTREAMS.tsv` vs `phoenix_v4/quality/book_quality_gate.py`.
3. **high — `missing_implementation`:** PER-CHAPTER ITEM-2 not done — `config/quality/refrain_allowlist.yaml:281`.
4. **medium — `inconsistency`:** WORLDWIDE spec status banner vs Phase 1 P0 section — `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md:3` vs `:87-114`.
5. **medium — `inconsistency`:** MANGA GTM brand count stale — `docs/MANGA_GTM_PLAN.md:5`.
6. **medium — `inconsistency`:** WORLDWIDE spec HEAD anchor stale — `:91` vs current `main`.
7. **medium — `rule_violation` risk:** Marketing YAML `status: draft` — `config/marketing/weekly_volumes_per_brand.yaml:50` vs consumer contracts expecting promotion discipline.
8. **low:** marketing_deep_research shallow vs “all subdirectories exhaustive read” instruction.

---

## 8. Phase 7 — Operator-framing verification

| Statement | Result | Receipt |
|-----------|--------|---------|
| 37 brands Path X | **PASS** | YAML parse |
| 12 teachers Pearl Prime | **PARTIAL** — registry has **13** teachers | `teacher_registry.yaml` |
| 6–12 authors per brand | **PARTIAL** — e.g. stillness_press shows **12** authors in pool comment | `config/brand_author_assignments.yaml:11-28` (not all brands counted) |
| Pearl Prime book + audiobook same script | **PARTIAL** — audiobook pipeline consumes book content but localized artifacts are separate paths | `docs/AUDIOBOOK_PIPELINE_SPEC.md:35-70` |
| Music mode = 38+; not part of 37 | **PASS** (design) | `music_brand_registry.yaml:27-28` |
| Locales en_US, ja_JP, zh_TW, zh_CN | **PASS** as program scope; **ko_KR** exists in broader locale registry | worldwide spec `17`; `locale_registry.yaml` beyond first 80 lines |
| Pearl Star = Path A canonical manga | **PASS** per IMG cap cross-link | `docs/PEARL_ARCHITECT_STATE.md:1346-1348` |
| RunComfy parallel + Qwen-Image primary post-amendment | **PARTIAL** — dual-path cap emphasizes **Pearl Star canonical** + RunComfy parallel; Qwen-Image is Pearl Star stack | IMG cap `1336-1375`; log **#1018** |
| Image inventory 6,528 PNGs | **PASS** at artifact time | TSV `wc -l` + audit md |
| 555 brand-locale-surface cells | **FAIL to verify** | no definition located on-repo |

---

## 9. Appendix A — Orphan files

**Method honesty:** No full-repo static analysis was run to classify every path without a spec reference.

**High-likelihood low-risk orphans:** historical chat exports under `de_chats_to_analyze/`, `old_chat_specs/`, binary archives — not governed by current caps.

**Recommendation:** run `scripts/observability/detect_changes.py` / inventory scanner ws if true orphan map is required.

---

## 10. Appendix B — Missing implementations / missing spec paths

| Item | Detail |
|------|--------|
| `docs/specs/PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md` | **Missing file** (user checklist; PR #1023 not fetched in-session) |
| `docs/specs/MANGA_LAYERED_PIPELINE_V2_SCOPE.md` | **Wrong path** — actual `docs/MANGA_LAYERED_PIPELINE_V2_SCOPE.md` |
| `docs/specs/JAPAN_LINE_FREEBIE_FUNNEL_PLAN_*.md` | **Wrong path** — actual `docs/JAPAN_LINE_FREEBIE_FUNNEL_PLAN_2026-04-29.md` |
| KDP/audiobook dedicated Comfy workflows | Plan flags gap | `artifacts/qa/parallel_image_generation_plan_2026-05-09.md:42` |

---

## 11. Appendix C — PR archaeology (`main`, since 2026-05-08)

**Method:** `git log origin/main --since='2026-05-08' --oneline` → **63** commits.

**Mapped sample (chronological head excerpt):**

| SHA (short) | PR | Cap / theme |
|-------------|-----|-------------|
| `515de6cb5` | #1022 | WORLDWIDE Phase 1 P0 doc completion |
| `ba2bac591` | #1020 | IMG batch ACTIVATION milestone |
| `40ac58fe4` | #1021 | CI deps httpx |
| `805f62947` | #1011 | CI cover_art WARN |
| `ff110894f` | #1010 | RunComfy API wiring |
| `1b479d2fa` | #1008 | Music catalog branch 100% |
| `d26fc3e93` | #988 | Image inventory + parallel plan |
| `d5a8775ba` | #992 | IMG cap land |
| `4c89fe1f1` | #984 | Marketing weekly volumes YAML |
| `144a5437e` | #983 | Music wizard steps |

**Full list:** see `git log` output in Pearl_Architect session logs / reproduce locally.

---

## 12. Findings roll-up (severity × category)

| id | category | sev | summary | primary receipt |
|----|----------|-----|---------|-----------------|
| F01 | inconsistency | high | CI spec banner vs merged remediation | `docs/specs/CI_BASELINE_RECOVERY_V1_SPEC.md:8-10` |
| F02 | inconsistency | high | Overlay ws stale vs code | `ACTIVE_WORKSTREAMS.tsv`; `book_quality_gate.py` |
| F03 | missing_implementation | high | ITEM-2 allowlist phrase persists | `refrain_allowlist.yaml:281` |
| F04 | inconsistency | medium | WORLDWIDE spec status vs amendment | `WORLDWIDE_CATALOG…SPEC.md:3` vs `:87-114` |
| F05 | inconsistency | medium | MANGA GTM brand count | `MANGA_GTM_PLAN.md:5` |
| F06 | inconsistency | medium | WORLDWIDE HEAD anchor stale | `WORLDWIDE…SPEC.md:91` |
| F07 | inconsistency | medium | QI cap still proposed | `PEARL_ARCHITECT_STATE.md:840` |
| F08 | inconsistency | medium | marketing YAML draft status | `weekly_volumes_per_brand.yaml:50` |
| F09 | inconsistency | medium | Teacher count framing vs registry | `teacher_registry.yaml` |
| F10 | inconsistency | medium | Weekly volumes locale deferral vs operator “cells” language | `weekly_volumes…yaml:40-44` |
| F11 | rule_violation | medium | RunComfy enforcement not runtime-proven | audit scope limitation |
| F12 | inconsistency | low | IMG cap lacks separate `#### AMENDMENT-2026-05-10` | architect file grep |
| F13 | inconsistency | low | marketing_deep_research small | glob |
| F14 | inconsistency | low | Research corp not fully read | methodology §1.1 |
| F15 | inconsistency | low | Registry full cross-matrix not built | Phase 4 |
| F16 | inconsistency | low | Appendix A orphans not enumerated | Appendix A |
| F17 | inconsistency | low | PR #1023 body not ingested | Phase 7 |
| F18 | inconsistency | low | PEARL_PRIME_WORLDWIDE spec file missing | Appendix B |

---

## 13. Closeout metadata (for operator receipt)

- **Total cap headings (`###`):** 41 (includes superseded/closed — see Phase 2)
- **`docs/specs` files:** 13  
- **Root `specs/*.md`:** 76  
- **Alignment:** **75%**  
**Final severity counts (authoritative):** critical **0**, high **3**, medium **9**, low **6** — total classified findings **18** (see §12 table).

**Top 3 critical gaps (operator-facing, despite no “critical” severity):**

1. **ITEM-2** still open (`refrain_allowlist.yaml:281`).  
2. **Coordination vs code** for overlay ws.  
3. **555 cells / PR #1023** trace missing.

---

*End of full report — Pearl_Architect 2026-05-10.*
