# WORLDWIDE-CATALOG-GO-LIVE-V1 — Program Spec (operator-readable)

**Status:** proposed (pending operator approval of phase plan and Q1–Q5)  
**PROJECT_ID:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1  
**Last updated:** 2026-05-08  
**Owner:** Pearl_PM  
**Ratified cap:** `docs/PEARL_ARCHITECT_STATE.md` → **WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01**

---

## Purpose

One **durable program record** for worldwide production go-live planning across **catalog, dashboards, brand-admin delivery, author coverage, marketing velocity, spine CLI performance, executive visibility, command-UI alignment, and worktree hygiene** — so remediation fans out from a **single gap matrix**, not ad-hoc sessions.

## Scope (operator request)

- **37 manga brands** × **4 locales** (`en_US`, `ja_JP`, `zh_TW`, `zh_CN`) **as stated** — must be reconciled with **Path X** separation (book pipeline vs manga pipeline) already documented in `BRAND_ADMIN_CANONICAL_PACKAGE.md` and `docs/PEARL_ARCHITECT_STATE.md`.

## Non-scope

- No code, config edits, or merges as part of **this** packet (audit + program scaffolding only).

## Authority (read order for implementers)

See the cap entry — includes: `docs/SESSION_UNITY_PROTOCOL.md`; `docs/PEARL_PM_STATE.md`; `docs/PEARL_ARCHITECT_STATE.md`; `docs/DOCS_INDEX.md`; `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md`; `specs/PHOENIX_V4_5_WRITER_SPEC.md`; `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md`; `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`; `BRAND_ADMIN_CANONICAL_PACKAGE.md`; `docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md`.

## Deliverables (already landed by this packet)

| Artifact | Path |
|----------|------|
| Per-surface gap matrix + phased roadmap + Q1–Q5 | `artifacts/qa/go_live_readiness_audit_2026-05-08.md` |
| Architect cap | `docs/PEARL_ARCHITECT_STATE.md` |
| Program + workstreams | `artifacts/coordination/ACTIVE_PROJECTS.tsv`, `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` |
| Operator spec (this file) | `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md` |

## Phase plan (summary)

1. **Phase 1 — Visibility unlock:** Surfaces **2, 6, 8** (dashboard truth, executive view, marketing SSOT).  
2. **Phase 2 — Active-brand wiring:** Surfaces **3, 4, 7, 9**.  
3. **Phase 3 — Catalog completion:** Surfaces **1, 5** (catalog + authors).  
4. **Phase 4 — Production go-live:** Surface **10** plus cross-cutting hygiene and monitoring.

**Production go-live** is defined **only** by **Phase 4 exit criteria** in the audit Markdown.

## Operator decisions required

Questions **Q1–Q5** are listed verbatim at the **end** of `artifacts/qa/go_live_readiness_audit_2026-05-08.md`.

## Handoff

After operator answers **Q1–Q5**, Pearl_PM routes **Phase 1** implementation prompts against the **`ws_worldwide_gl_*`** rows opened for this project.

---

## AMENDMENT-2026-05-08-PRIORITIES

Operator decisions ratified as the activation gate for `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01`.

### Q1-Q5 (verbatim)

- Q1 = yes (phase order: visibility -> wiring -> catalog -> go-live)
- Q2 priorities:
  - P0 = Surface 1 (Catalog planning), Surface 4 (Active/inactive brands), Surface 6 (Marketing volume SSOT)  [all 3 RED surfaces]
  - P1 = Surface 2 (Brand dashboard), Surface 8 (Executive dashboard)
  - P2 = Surface 3 (Weekly packaging), Surface 5 (Author/bio), Surface 7 (Spine/CLI perf), Surface 9 (Command UI <-> CLI), Surface 10 (Disk/worktrees)
- Q3 = commit A1 (Pearl_Localization 12 scripts) + A2 (Pearl_Int CosyVoice2 audit TSV) + A5 (Pearl_Dev overlay Phase 1) + Pearl_DevOps CI hygiene (5 files); abandon A6 + stale drafts/contaminated worktree leftovers
- Q4 = brand_wizard YAML confirmed as canonical SSOT for active/inactive brand classification
- Q5 = Weekly cadence: Monday, both email + file delivery

### Per-surface priority lock

| Surface | Name | Priority |
|---|---|---|
| Surface 1 | Catalog planning | P0 |
| Surface 2 | Brand dashboard | P1 |
| Surface 3 | Weekly packaging | P2 |
| Surface 4 | Active/inactive brands | P0 |
| Surface 5 | Author/bio | P2 |
| Surface 6 | Marketing volume SSOT | P0 |
| Surface 7 | Spine/CLI perf | P2 |
| Surface 8 | Executive dashboard | P1 |
| Surface 9 | Command UI <-> CLI | P2 |
| Surface 10 | Disk/worktrees | P2 |

---

## Phase 1 P0 progress (2026-05-10)

Doc-only snapshot mirroring the architect cap entry `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 — AMENDMENT — 2026-05-10` in `docs/PEARL_ARCHITECT_STATE.md`. No new operator decisions; this section anchors the operator-readable spec to the same `main` HEAD so downstream readers do not have to cross-reference the architect log to know "what shipped, what is queued."

**`main` HEAD anchor:** `e25bd63e8a20f1c13fa4285ccfe1be095523546a` (2026-05-10).

### Phase 1 P0 status matrix

| Surface | Name | Tier | Status | PRs (merged) |
|---|---|---|---|---|
| Surface 4 | Active/inactive brand classifier (brand_wizard YAML SSOT) | P0 | merged | #972 (classifier) |
| Surface 6 | Marketing volume SSOT (discovery + V1 spec + YAML baseline) | P0 | merged | #976 (discovery + spec), #984 (`config/marketing/weekly_volumes_per_brand.yaml` V1) |
| Surface 1 | Catalog planning (Pearl Prime feature/knob axes) | P0 | substantively shipped | #986 (P0-1 structural variation + stable signature), #974 (P0-2 angle_registry alignment), #978 (P0-3 explicit `angle_id` per row) |
| Surface 2 | Brand dashboard (active brand panel) | P1 | partial — first consumer merged | #977 (active panel consumer of Surface 4 SSOT) |
| Surface 8 | Executive dashboard | P1 | queued | — |
| Surface 3 | Weekly packaging | P2 | queued | — |
| Surface 5 | Author/bio | P2 | queued | — |
| Surface 7 | Spine/CLI perf | P2 | queued | — |
| Surface 9 | Command UI ↔ CLI | P2 | queued | — |
| Surface 10 | Disk/worktrees | P2 | queued | — |

### Closeout summary

- **Surface 4 (active-brand SSOT)** — classifier + first dashboard consumer merged. SSOT layer closed; further consumers (`brand_admin.html`, Pearl Prime / full-catalog generators) landed under the 2026-05-09 wave (see architect cap for per-PR SHAs).
- **Surface 6 (marketing volume SSOT)** — discovery + V1 spec (`docs/specs/MARKETING_VOLUME_SSOT_V1_SPEC.md`) + V1 YAML baseline (37 brands × 6 surfaces) merged. Consumer wiring (Surfaces 2/3/8) is the next P1/P2 hop per spec §5 #4.
- **Surface 1 (catalog planning)** — Pearl Prime feature/knob P0-1/2/3 trio merged via the **`FEATURE-KNOB-CATALOG-VARIATION-V1-01`** cap. Catalog rows now carry explicit `angle_id` + structural variation axes + stable signature.
- **Surface 2 (brand dashboard)** — first slice (active panel) shipped early as part of the Surface 4 fan-out; broader Surface 2 ws (locale grids, podcast row, piece-level status) remains queued at P1.
- **Surfaces 3 / 5 / 7 / 8 / 9 / 10** — queued at P1/P2 per **AMENDMENT-2026-05-08-PRIORITIES**. No re-prioritization; this section does not move tiers.

### Anti-drift

- Phase 1 P0 is **substantively complete** at the SSOT/spec layer for Surfaces 1/4/6. Any session claiming "Phase 1 incomplete" must reference an unmerged P0 PR or a missing P0 ws row (none currently outstanding per this snapshot).
- Production go-live remains defined **only** by **Phase 4 exit criteria** in `artifacts/qa/go_live_readiness_audit_2026-05-08.md`. P0 SSOT closure does **not** itself constitute go-live.
- Any P-tier reassignment still requires a separate AMENDMENT (per AMENDMENT-2026-05-08-PRIORITIES anti-drift).

### Handoff

Pearl_PM may now route P1 prompts (Surface 2 broader binding + Surface 8 executive dashboard) against `ws_worldwide_gl_s02_*` and `ws_worldwide_gl_s08_*` without further architect ratification. P0 ws rows (`ws_worldwide_gl_s01_*`, `ws_worldwide_gl_s04_*`, `ws_worldwide_gl_s06_*`) may be flipped from `runnable`/`active` to `done` in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` at Pearl_PM's discretion.

Authority cross-ref: `docs/PEARL_ARCHITECT_STATE.md` → `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 — AMENDMENT — 2026-05-10`.

---

## §AMENDMENT-2026-05-10-PHASE-1-P0-COMPLETE

Operator-readable mirror of `docs/PEARL_ARCHITECT_STATE.md` → **WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 — AMENDMENT-2026-05-10-PHASE-1-P0-COMPLETE**. Ratifies **Phase 1 P0 = 100% complete** and opens **Phase 2**.

### 1. Phase 1 P0 100% complete

- **Visual signoff:** Operator **`PHASE_1_P0_VISUAL_SIGNOFF_PASS`** — **5 / 5** renders **PASS** tied to **PR #1020** batch-runner activation.
- **PNG evidence (repo-relative):** `artifacts/manga/activation_smoke_2026-05-10/smoke_junko_animagine_ja/smoke_junko_animagine_ja.png`; `.../smoke_miki_qwen_ja/smoke_miki_qwen_ja.png`; `.../smoke_feung_animagine_zh/smoke_feung_animagine_zh.png`; `.../smoke_joshin_flux_en/smoke_joshin_flux_en.png`; `.../smoke_ahjan_flux_en/smoke_ahjan_flux_en.png` (see `artifacts/qa/batch_runner_activation_smoke_2026-05-10.md` on **PR #1020**).
- **Anti-drift gate:** ≥ **1** operator-validated real dual-path batch (Pearl Star + RunComfy), per **AMENDMENT-2026-05-08-PRIORITIES**.
- **Wave duration:** **2026-05-08 → 2026-05-10** (~**2** days).
- **Merged PR count (window):** **63** PRs merged on `merged:2026-05-08..2026-05-10` (**≥ 35** program threshold).

**Verbatim binding claim:** **Phase 1 P0 is 100% complete** for **`PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1`**.

### 2. Phase 2 entry criteria

Phase 1 P0 milestone closed; CI baseline mostly green (Phase 2.6 in flight); Pearl Star + RunComfy dual-path exercised; image batch runner **dry-run + live** modes available.

### 3. Phase 2 scope

Image polish (remove baked-in text; consistency; voice fidelity; lettering stays pipeline-owned); **37 × 3 × 5** catalog matrix; **6–12** authors/brand; dashboard main-character + cover panels; full-queue activation after polish (**~19.3d → ~6–10d** dual-path).

### 4. Anti-drift

**“Phase 1 P0 is 100% complete”** cannot be downgraded without a new operator **AMENDMENT**. Phase 2 `ws_*` rows are **runnable** but **not** auto-spawned without operator authorization. Catalog master plan = Pearl_PM + Pearl_Marketing.

### 5. Action items (named `ws_*`)

`ws_phase_2_negative_prompt_text_removal_20260510` (Pearl_Dev); `ws_phase_2_worldwide_catalog_plan_v1_20260510` (Pearl_PM + Pearl_Marketing); `ws_phase_2_dashboard_manga_character_display_20260510` (Pearl_Brand); `ws_phase_2_full_queue_activation_20260510` (Pearl_Dev / Pearl_Conductor v3).

**Authority cross-ref (supersedes gate text):** parent architect cap **AMENDMENT-2026-05-10-PHASE-1-P0-COMPLETE** closes the prior “no 100% until real batch” hold on **Phase 1 P0** once this spec section ships on `main`.
